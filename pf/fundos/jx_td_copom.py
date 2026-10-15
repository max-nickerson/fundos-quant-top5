"""
Tesouro Direto depois de uma abertura forte de taxa, com regime do Copom — "o Tesouro é o comprador de última instância do varejo".

Tese de mesa: quando a curva abre forte em poucas semanas (stop de tesourarias e de fundos multimercado, resgates de fundos de renda fixa,
estrangeiro desmontando NTN-B), quem vende é VENDEDOR FORÇADO (limite de VaR/stop, cota caindo); o prêmio costuma devolver parte em
1–3 meses. O PF compra no Tesouro Direto o mesmo título, sem book, ao PU de compra publicado (spread de 0,12 pp de taxa — o custo real
do varejo), e revende ao próprio Tesouro quando quiser. O regime do Copom separa o pânico do choque de fundamento: com o BC SUBINDO juro
a abertura é informação (2013, 2015, 2021, 2024: a taxa seguiu abrindo); com o BC parado ou cortando, é prêmio (2018 greve, 2020 Covid,
2022 PEC, dez/2024 pacote fiscal — este último já com o BC subindo, por isso o filtro corta).
O dono pediu também a variante "vender a NTN-B depois de um fechamento forte e recomprar": ela é a mesma regra ao contrário sobre quem
JÁ carrega o título (exposição quase sempre ligada = beta de duration) — rodada como variante no caderno, não na grade.

Implementação:
  - título: Tesouro Prefixado (LTN) de ~3 anos ou Tesouro IPCA+ (NTN-B principal) de ~10 anos — o vencimento mais perto do prazo, travado;
  - sinal (fechamento de t, taxa de venda do Tesouro Direto da manhã): taxa subiu >= `thr` pp em 21 pregões; regime: a última decisão do
    Copom não foi de alta (`filtro`=1); entra em t+1 no PU de compra;
  - saída: a taxa devolveu metade do choque (taxa <= taxa da entrada - thr/2) ou `dias` pregões; vende no PU de venda;
  - 100% do capital no título; custódia B3 0,20% a.a.; IR regressivo (22,5% até 180 dias -> quase todos os negócios pagam 22,5%).
Dados: Tesouro Direto 2005+, Selic meta (BCB). Corte OOS 2021-01-01.
"""
import numpy as np
import pandas as pd

import _rf_comum as K
import jx_comum as J

NOME = "Tesouro Direto após abertura forte de taxa (regime Copom)"
TESE = ("Compro Tesouro Prefixado/IPCA+ no Tesouro Direto depois que a taxa abre forte em 1 mês (vendedor forçado) se o Copom não está "
        "subindo juro; vendo de volta ao Tesouro quando metade do choque devolve")
BENCHMARK = "CDI"
INICIO, CORTE = "2008-01-01", "2021-01-01"
REGIME = "nenhum"
CUSTO_TROCA = 0.0
PARAMS = {"tipo": "Tesouro IPCA+", "thr": 0.5, "filtro": 1, "dias": 63, "modo": "abertura"}   # maior IS (2008-2020)
GRADE = {"tipo": ["Tesouro Prefixado", "Tesouro IPCA+"], "thr": [0.5, 0.8], "filtro": [0, 1]}
VIZINHANCA = {"thr": (0.35, 0.7), "dias": (42, 90)}
PRAZO = {"Tesouro Prefixado": 3.0, "Tesouro IPCA+": 10.0}
CLASSE_IR = "renda_fixa"
INSTRUMENTOS = [{"onde": "Tesouro Direto", "ticker": "Tesouro Prefixado ~3 anos / Tesouro IPCA+ ~10 anos", "lote": "0,01 título; mínimo R$ 30",
                 "custo": "spread compra/recompra 0,12 pp de taxa (~0,3% do PU no pré de 3 anos, ~1% no IPCA+ de 10 anos); custódia 0,20% a.a."}]
APLICAVEL = True
MOTIVO = "Tesouro Direto: qualquer valor, recompra diária garantida (exceto quando o Tesouro suspende o mercado em volatilidade extrema)."
ALAVANCAGENS = [1]
MOTIVO_ALAV = "Tesouro Direto não aceita alavancagem; o equivalente alavancado seria DI1/DAP (contratos de R$ 100 mil de face)."
VARIANTES = {"variante 'vende após fechamento forte e recompra' (IPCA+)": {"modo": "rally", "tipo": "Tesouro IPCA+"},
             "variante 'vende após fechamento forte e recompra' (pré)": {"modo": "rally", "tipo": "Tesouro Prefixado"}}


def carrega():
    return {"td": J.ler("td.parquet"), "selic": J.selic()}


def _sinal(d, tipo, thr, filtro, dias, modo):
    td = K.tesouro(d, tipo)
    venc = K.escolhe_vencimento(td, PRAZO[tipo])
    pos = {c: i for i, c in enumerate(td["tx_venda"].columns)}
    X = td["tx_venda"].to_numpy()
    vv = venc.to_numpy()
    # taxa do vencimento de referência hoje e há 21 pregões (do MESMO vencimento — sem salto de troca de referência)
    y = np.array([X[i, pos[v]] if pd.notna(v) else np.nan for i, v in enumerate(vv)])
    y21 = np.array([X[i - 21, pos[v]] if (pd.notna(v) and i >= 21) else np.nan for i, v in enumerate(vv)])
    dy = y - y21
    cic = J.ciclo_copom(d).to_numpy()
    on = np.zeros(len(y), bool)
    est, t0, ref = False, 0, np.nan
    for t in range(len(y)):
        if modo == "abertura":
            if est and ((np.isfinite(y[t]) and y[t] <= ref - thr / 2) or t - t0 >= dias):
                est = False
            elif not est and np.isfinite(dy[t]) and dy[t] >= thr and (not filtro or cic[t] <= 0):
                est, t0, ref = True, t, y[t]
            on[t] = est
        else:            # "rally": carrego sempre; vendo por `dias` pregões depois de um fechamento >= thr em 21 pregões
            if est and t - t0 >= dias:
                est = False
            elif not est and np.isfinite(dy[t]) and dy[t] <= -thr and (not filtro or cic[t] >= 0):
                est, t0 = True, t
            on[t] = not est
    on = pd.Series(on, index=K.DIAS) & venc.notna()
    return td, venc, on, pd.Series(dy, index=K.DIAS)


def _livro(d, capital=20000, custo_mult=1, lag=0, **p):
    td, venc, on, _ = _sinal(d, p["tipo"], p["thr"], p["filtro"], int(p["dias"]), p["modo"])
    cols = list(td["pu_venda"].columns)
    alvo = K.alvo_de_vencimento(venc, on, cols)
    ce = (td["pu_compra"] / td["pu_venda"] - 1).clip(lower=0)
    return K.livro(alvo, td["R"], capital, lag, custo_ent=ce, custo_mult=custo_mult, lote=td["pu_compra"] * .01,
                   negocia=td["obs"], vivo=td["vivo"], custodia=K.CUSTODIA_TD, regressivo=True)


def excesso(d, capital=20000, custo_mult=1, lag=0, regime=REGIME, alavancagem=1, **params):
    e = _livro(d, capital, custo_mult, lag, **{**PARAMS, **params})["e"]
    return K.C.aplica_regime(e, regime, CUSTO_TROCA * custo_mult)


def classes_ir(d, capital=20000, **params):
    return K.classes_de_livro(_livro(d, capital, **{**PARAMS, **params}), capital, CLASSE_IR)


def posicoes(d, **params):
    p = {**PARAMS, **params}
    td, venc, on, _ = _sinal(d, p["tipo"], p["thr"], p["filtro"], int(p["dias"]), p["modo"])
    W = K.alvo_de_vencimento(venc, on, list(td["pu_venda"].columns))
    R = td["R"].sub(K.CDI, axis=0)
    W.columns = R.columns = [f"{p['tipo'][8:11]}{c:%Y%m}" for c in R.columns]
    return W, R


def negocios(d, capital=20000, **params):
    p = {**PARAMS, **params}
    ng = _livro(d, capital, **p)["negocios"].copy()
    td = K.tesouro(d, p["tipo"])
    if len(ng):
        ng["taxa_entrada"] = [td["tx_compra"].at[i, a] for a, i in zip(ng.ativo, ng.entrada)]
        ng["taxa_saida"] = [td["tx_venda"].at[f, a] for a, f in zip(ng.ativo, ng.saida)]
        ng["ativo"] = [f"{p['tipo'][8:11]}{a:%Y%m}" for a in ng.ativo]
    return ng
