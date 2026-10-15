"""
Tesouro Prefixado x Focus — pessoa física no Tesouro Direto.

Tese de mesa: o Tesouro Prefixado (LTN) embute a Selic média esperada até o vencimento + um prêmio de risco. Em choques de RISCO
(2008, 2015, greve de 2018, PEC da transição 2022) o pré paga muito mais que a Selic que os economistas (Focus) esperam — o prêmio volta
quando o susto passa. Compro LTN de 1,5–3 anos no Tesouro Direto quando a taxa supera o CDI esperado pelo Focus em `thr` pp e vendo
de volta ao Tesouro quando o prêmio some. Filtro de mesa (opcional, escolhido no IS): não entrar quando o Focus está REVISANDO a Selic
para cima (choque de inflação/BC atrás da curva — aí o prêmio é falso: 2021, 2024).
Vantagem de pessoa física: o varejo compra no Tesouro Direto o mesmo risco do DI1 sem margem nem contrato de R$ 100 mil, com
recompra garantida; o custo é o spread de 0,12 pp de taxa (≈ 0,2–0,35% do PU em 1,5–3 anos).

Implementação:
  - CDI esperado: caminho da Selic interpolando a meta vigente e as medianas de fim de ano do Focus (coleta de t-1), composto até o
    vencimento do título (CDI = Selic - 0,10). Prêmio = taxa de venda da LTN - CDI esperado no mesmo prazo;
  - compra no PU de compra, marca/vende no PU de venda; custódia B3 0,20% a.a.; IR regressivo (_ir_extra acima de 15%);
  - 100% do capital no título quando ligado; vencimento travado até sair; rola a 6 meses do vencimento.
Dados: Tesouro Direto 2005+, Focus anual 2000+, Selic meta (SGS 432). Corte OOS 2021-01-01.
"""
import numpy as np
import pandas as pd

import _rf_comum as K

NOME = "Tesouro Prefixado x Focus (Tesouro Direto)"
TESE = ("Compro Tesouro Prefixado de 1,5–3 anos quando a taxa paga muito mais que a Selic esperada pelo Focus (prêmio de risco em "
        "pânico) e vendo de volta ao Tesouro quando o prêmio some; não entro quando o Focus revisa a Selic para cima")
BENCHMARK = "CDI"
INICIO, CORTE = "2007-01-01", "2021-01-01"
REGIME = "nenhum"
CUSTO_TROCA = 0.0
PARAMS = {"thr": 0.75, "prazo": 3.0, "filtro": 0}               # escolhidos no IS (maior IR 2007-2020; filtro empata e fica o simples)
GRADE = {"thr": [0.75, 1.5], "prazo": [1.5, 3.0], "filtro": [0, 1]}
VIZINHANCA = {"thr": (0.5, 1.25), "prazo": (2.0, 4.0)}
CLASSE_IR = "renda_fixa"
ALIQUOTAS = None
INSTRUMENTOS = [{"onde": "Tesouro Direto", "ticker": "Tesouro Prefixado 20XX (LTN)", "lote": "0,01 título (~R$ 7–9); mínimo R$ 30",
                 "custo": "spread compra/recompra 0,12 pp de taxa (≈ 0,2–0,35% do PU); custódia B3 0,20% a.a."}]
APLICAVEL = True
MOTIVO = "Tesouro Direto aceita R$ 30 e recompra todo dia útil."
ALAVANCAGENS = [1]
MOTIVO_ALAV = ("Tesouro Direto não aceita margem; a versão alavancada é o DI1 (fundo rf_di_copom), que poucas corretoras oferecem a PF.")
TIPO = "Tesouro Prefixado"
HORIZ = (0.25, 0.5, 1.0, 1.5, 2.0, 3.0, 4.0)


def carrega():
    return {"td": K.ler("tesouro_direto.parquet"), "focus": K.ler("focus_anual.parquet"), "selic": K.ler("selic_meta.csv")}


def _taxa_prazo(td, venc):
    tx = td["tx_venda"]
    pos = {c: i for i, c in enumerate(tx.columns)}
    X = tx.to_numpy()
    y = np.array([X[i, pos[v]] if pd.notna(v) else np.nan for i, v in enumerate(venc.to_numpy())])
    T = (pd.to_datetime(venc) - K.DIAS.to_series(index=K.DIAS)).dt.days / 365.25
    return pd.Series(y, index=K.DIAS), T


def premio(d, prazo):
    """Prêmio (pp) = taxa de venda da LTN de referência - CDI esperado (Focus) até o vencimento dela. Também devolve o vencimento."""
    td = K.tesouro(d, TIPO)
    venc = K.escolhe_vencimento(td, prazo)
    y, T = _taxa_prazo(td, venc)
    E = pd.concat({h: K.cdi_esperado(d, h) for h in HORIZ}, axis=1).to_numpy()
    hs = np.array(HORIZ)
    Tv = T.to_numpy()
    esp = np.array([np.interp(Tv[i], hs, E[i]) if np.isfinite(Tv[i]) and np.isfinite(E[i]).all() else np.nan for i in range(len(Tv))])
    return td, venc, y - esp, y, pd.Series(esp, index=K.DIAS)


def _sinal(d, thr, prazo, filtro):
    td, venc, pr, y, esp = premio(d, prazo)
    F = K.focus_anual(d, "Selic")
    prox = pd.Series([F.at[t, t.year + 1] if (t.year + 1) in F.columns else np.nan for t in K.DIAS], index=K.DIAS)
    revisa = (prox - prox.shift(21)) >= .25                    # Focus revisando a Selic do ano que vem para cima (>= 25 bps em 1 mês)
    on = np.zeros(len(pr), bool)
    st = False
    pv, rv = pr.to_numpy(), revisa.to_numpy()
    for t in range(len(pv)):
        if np.isfinite(pv[t]):
            if not st and pv[t] >= thr and not (filtro and rv[t]):
                st = True
            elif st and pv[t] <= 0:
                st = False
        on[t] = st
    return td, venc, pd.Series(on, index=K.DIAS), pr


def _livro(d, capital=20000, custo_mult=1, lag=0, thr=PARAMS["thr"], prazo=PARAMS["prazo"], filtro=PARAMS["filtro"]):
    td, venc, on, _ = _sinal(d, thr, prazo, filtro)
    alvo = K.alvo_de_vencimento(venc, on, list(td["pu_venda"].columns))
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
    td, venc, on, _ = _sinal(d, p["thr"], p["prazo"], p["filtro"])
    W = K.alvo_de_vencimento(venc, on, list(td["pu_venda"].columns))
    R = td["R"].sub(K.CDI, axis=0)
    W.columns = R.columns = [f"PRE{c:%Y-%m}" for c in R.columns]
    return W, R


def negocios(d, capital=20000, **params):
    p = {**PARAMS, **params}
    ng = _livro(d, capital, **p)["negocios"].copy()
    td, _, _, pr = _sinal(d, p["thr"], p["prazo"], p["filtro"])
    if len(ng):
        ng["taxa_entrada"] = [td["tx_compra"].at[i, a] for a, i in zip(ng.ativo, ng.entrada)]
        ng["premio_entrada"] = [pr.shift(1).get(i, np.nan) for i in ng.entrada]
        ng["taxa_saida"] = [td["tx_venda"].at[f, a] for a, f in zip(ng.ativo, ng.saida)]
        ng["ativo"] = [f"PRE{a:%Y-%m}" for a in ng.ativo]
    return ng
