"""
Tesouro IPCA+ de valor — pessoa física no Tesouro Direto.

Tese de mesa: o juro real neutro brasileiro fica em 4,5–6%. Quando o Tesouro IPCA+ longo paga IPCA + 6,5–7% o mercado está cobrando
prêmio fiscal/político que historicamente foi devolvido em 6–24 meses (2008, 2013, 2015, 2022). Compro o título no Tesouro Direto e
vendo de volta ao Tesouro (recompra diária GARANTIDA, sem depender de contraparte) quando a taxa fecha `gap` pp.
Vantagem de pessoa física: o Tesouro Direto é o único lugar onde um varejista compra NTN-B principal de 20 anos com R$ 30, sem book,
com o Tesouro como comprador de última instância no pânico (quando o institucional não acha comprador para DAP longo).

Implementação:
  - preços REAIS de varejo: compra no PU de compra da manhã, marca e vende no PU de venda (recompra) — o spread de 0,12 pp de taxa
    (≈ 1,2% do PU no 2035, ≈ 2,3% no 2045) é o custo de entrada; custódia B3 0,20% a.a. (cobrada na venda desde 2025; mesma conta);
  - sinal: taxa de venda (resgate) do Tesouro IPCA+ (principal) com prazo mais perto de `prazo` anos; entra com taxa >= `entrada`,
    sai com taxa <= entrada - gap; o vencimento fica TRAVADO até a saída (rola a 6 meses do vencimento);
  - 100% do capital no título quando ligado (não há alavancagem no Tesouro Direto); fora disso, CDI;
  - IR: tabela regressiva (22,5% até 180 dias ... 15% acima de 720 dias) sobre o ganho de cada venda — `_ir_extra` leva a parte acima de 15%.
Dados: Tesouro Direto (taxas e PUs de compra/venda 2005+), corte OOS 2021-01-01.
Premissas corrigidas (fonte): custódia B3 0,20% a.a. para títulos não-Selic, sem isenção (b3.com.br, tarifas do Tesouro Direto);
spread de recompra 0,12 pp em IPCA+/Prefixado (medido no próprio arquivo do Tesouro: mediana 2017–2026 = 0,12 pp).
"""
import numpy as np
import pandas as pd

import _rf_comum as K

NOME = "Tesouro IPCA+ de valor (Tesouro Direto)"
TESE = ("Compro Tesouro IPCA+ longo quando o juro real passa de ~6,5% (prêmio fiscal) e vendo de volta ao Tesouro quando a taxa fecha; "
        "recompra diária garantida e títulos de R$ 30 são vantagem do varejo")
BENCHMARK = "CDI"
INICIO, CORTE = "2007-01-01", "2021-01-01"
REGIME = "nenhum"
CUSTO_TROCA = 0.0
PARAMS = {"entrada": 7.0, "gap": 1.25, "prazo": 20}            # escolhidos no IS (maior IR 2007-2020 na GRADE)
GRADE = {"entrada": [6.0, 6.5, 7.0], "gap": [0.75, 1.25], "prazo": [10, 20]}
VIZINHANCA = {"entrada": (6.5, 7.5), "gap": (0.9, 1.6), "prazo": (14, 26)}
CLASSE_IR = "renda_fixa"
ALIQUOTAS = None
INSTRUMENTOS = [{"onde": "Tesouro Direto (qualquer corretora; XP/Rico/Clear/Inter/Nubank sem taxa)", "ticker": "Tesouro IPCA+ 20XX (NTN-B principal)",
                 "lote": "0,01 título (~R$ 20–40); mínimo R$ 30", "custo": "spread compra/recompra 0,12 pp de taxa (≈ duration x 0,12%); custódia B3 0,20% a.a."}]
APLICAVEL = True
MOTIVO = "Tesouro Direto aceita R$ 30 e recompra todo dia útil; o capital inteiro cabe em um título."
ALAVANCAGENS = [1]
MOTIVO_ALAV = ("Tesouro Direto não aceita margem; alavancar exigiria DAP (contrato de ~R$ 4–5 mil de DV01 alto, poucos varejistas operam) "
               "— fora do escopo de um fundo de varejo honesto.")
TIPO = "Tesouro IPCA+"


def carrega():
    return {"td": K.ler("tesouro_direto.parquet")}


def _sinal(d, entrada, gap, prazo):
    td = K.tesouro(d, TIPO)
    venc = K.escolhe_vencimento(td, prazo)
    pos = {c: i for i, c in enumerate(td["tx_venda"].columns)}
    X = td["tx_venda"].to_numpy()
    y = pd.Series([X[i, pos[v]] if pd.notna(v) else np.nan for i, v in enumerate(venc.to_numpy())], index=K.DIAS)
    on = np.zeros(len(y), bool)
    estado = False
    yv = y.to_numpy()
    for t in range(len(yv)):
        if np.isnan(yv[t]):
            on[t] = estado
            continue
        if not estado and yv[t] >= entrada:
            estado = True
        elif estado and yv[t] <= entrada - gap:
            estado = False
        on[t] = estado
    return td, venc, pd.Series(on, index=K.DIAS), y


def _livro(d, capital=20000, custo_mult=1, lag=0, entrada=PARAMS["entrada"], gap=PARAMS["gap"], prazo=PARAMS["prazo"]):
    td, venc, on, _ = _sinal(d, entrada, gap, prazo)
    cols = list(td["pu_venda"].columns)
    alvo = K.alvo_de_vencimento(venc, on, cols)
    ce = (td["pu_compra"] / td["pu_venda"] - 1).clip(lower=0)
    return K.livro(alvo, td["R"], capital, lag, custo_ent=ce, custo_mult=custo_mult, lote=td["pu_compra"] * .01,
                   negocia=td["obs"], vivo=td["vivo"], custodia=K.CUSTODIA_TD, regressivo=True)


def excesso(d, capital=20000, custo_mult=1, lag=0, regime=REGIME, alavancagem=1, **params):
    p = {**PARAMS, **params}
    e = _livro(d, capital, custo_mult, lag, **p)["e"]
    return K.C.aplica_regime(e, regime, CUSTO_TROCA * custo_mult)


def classes_ir(d, capital=20000, **params):
    return K.classes_de_livro(_livro(d, capital, **{**PARAMS, **params}), capital, CLASSE_IR)


def posicoes(d, **params):
    p = {**PARAMS, **params}
    td, venc, on, _ = _sinal(d, p["entrada"], p["gap"], p["prazo"])
    W = K.alvo_de_vencimento(venc, on, list(td["pu_venda"].columns))
    R = td["R"].sub(K.CDI, axis=0)
    W.columns = R.columns = [f"IPCA+{c:%Y}" for c in R.columns]
    return W, R


def negocios(d, capital=20000, **params):
    p = {**PARAMS, **params}
    L = _livro(d, capital, **p)
    ng = L["negocios"].copy()
    td, _, _, y = _sinal(d, p["entrada"], p["gap"], p["prazo"])
    if len(ng):
        ng["taxa_entrada"] = [td["tx_compra"].at[i, a] for a, i in zip(ng.ativo, ng.entrada)]
        ng["taxa_saida"] = [td["tx_venda"].at[f, a] if f in td["tx_venda"].index else np.nan for a, f in zip(ng.ativo, ng.saida)]
        ng["ativo"] = [f"IPCA+{a:%Y}" for a in ng.ativo]
    return ng
