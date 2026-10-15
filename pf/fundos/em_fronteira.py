"""
Fronteira e EM pequenos: o ETF americano descolado da bolsa local (VNM x VN30, TUR x BIST100, EIDO x JCI, EWM x KLCI, EZA x Top40).

Tese de mesa: o que ainda tem dado e liquidez na fronteira é pouco (ver o caderno: NGE, EGPT, PAK, FM, GXG/ICOL, RSX/ERUS morreram; VNM,
KSA, QAT, UAE, KWT, AFK vivem, com volume de US$ 0,5–30 mi/dia). Nesses ETFs a cesta é ilíquida e o AP cobra caro para criar/resgatar:
quando o americano resgata em pânico, o ETF negocia ABAIXO da cesta local (desconto ao NAV) por dias. O NAV histórico não é gratuito;
o substituto é a bolsa local em dólar (índice local / moeda). Se o ETF cai muito mais que a bolsa local, compro o ETF e espero o
desconto fechar (ou a bolsa local cair até ele — aí perco).
HONESTIDADE DE FUSO: a bolsa local fecha horas antes de NY; o sinal usa o fechamento local de t e o do ETF de t; a compra é no
fechamento do ETF de t+1 (depois de a bolsa local ter negociado t+1): o pedaço que é só fuso já passou.
FX do Yahoo: "Close" de t = cotação do início de t (defasada, não futura); dias com salto x10/÷10 (IDR, VND) e picos de 25% no
VN30 são descartados contra o último valor aceito (só passado).

PF: ETF na IBKR (fração), 30% do capital por ETF, no máximo 2; hedge opcional EEM vendido (beta).
"""
import numpy as np
import pandas as pd

import em_comum as E

NOME = "Fronteira/EM pequeno: ETF dos EUA com desconto contra a bolsa local (IBKR)"
TESE = ("Quando o ETF americano (VNM, TUR, EIDO, EWM, EZA) cai muito mais que a bolsa local em dólar, compro o ETF (resgate forçado cria "
        "desconto à cesta) e saio quando o desvio fecha ou em 10 dias")
BENCHMARK = "CDI"
INICIO, CORTE = "2013-01-01", "2021-01-01"
REGIME = "nenhum"
CUSTO_TROCA = .001
CLASSE_IR = "exterior"
PARES = {"VNM": ("E1VFVN30.VN", "VND=X"), "TUR": ("XU100.IS", "TRY=X"), "EIDO": ("^JKSE", "IDR=X"), "EWM": ("^KLSE", "MYR=X"),
         "EZA": ("^JN0U.JO", "ZAR=X")}
PARAMS = {"z_in": 2.5, "jan": 20, "hedge": "nenhum", "max_dias": 10, "peso": .30}   # escolhido no IS (maior IR IS; todas negativas no IS)
GRADE = {"z_in": [2.0, 2.5], "jan": [20, 60], "hedge": ["nenhum", "EEM"]}
VIZINHANCA = {"z_in": (2.1, 3.0), "jan": (12, 45), "max_dias": (5, 20), "peso": (.2, .4)}
INSTRUMENTOS = "IBKR: VNM, TUR, EIDO, EWM, EZA (fração); hedge opcional EEM vendido. Índices locais e moedas só como DADO."
APLICAVEL = True
MOTIVO = "Operável (R$ 6 mil por ETF com 20k); ETFs com US$ 5–100 mi/dia de volume — nosso tamanho é irrelevante para a liquidez."
ALAVANCAGENS = [1, 1.5, 2]
MOTIVO_ALAV = "L multiplica o peso por ETF (30% -> 45%/60%), no máximo 2 ETFs."


def carrega():
    tk = list(PARES) + [v[0] for v in PARES.values()] + [v[1] for v in PARES.values()] + ["EEM"]
    return E.seleciona(tk)


def desvio(d):
    R = d["raw"]
    out = {}
    for e, (ix, fx) in PARES.items():
        f = E.limpa_saltos(R[fx].dropna(), .25).reindex(R.index).ffill(limit=5)          # IDR/VND do Yahoo têm dias x10/÷10
        li = E.limpa_saltos(R[ix].dropna(), .15).reindex(R.index)                       # VN30: limite diário de 7%; picos de 25% são erro
        loc = (li / f).ffill(limit=3)
        ok = R[e].notna() & li.notna()
        out[e] = (np.log(R[e]) - np.log(loc)).where(ok)
    return pd.DataFrame(out)


def _pesos(d, z_in, jan, hedge, max_dias, peso):
    g = desvio(d)
    z = (g - g.rolling(jan, min_periods=jan // 2).mean().shift(1)) / g.rolling(126, min_periods=60).std().shift(1)
    neg = E.negociou(d)[list(PARES)]
    est = E.maquina((z <= -z_in) & neg, z >= 0, max_dias, espera=2)
    est = E.limita_n(est, 2, -z)
    W = est * peso
    if hedge == "EEM":
        P = E.preco_usd(d)
        r = P.pct_change(fill_method=None)
        rm = r["EEM"]
        b = pd.DataFrame({c: r[c].rolling(252, min_periods=126).cov(rm) / rm.rolling(252, min_periods=126).var() for c in PARES}).clip(0, 2)
        b = E.congela(b.where(est > 0), est)
        W["EEM"] = -(W[list(PARES)] * b).sum(axis=1)
    return W, {}


excesso, classes_ir, posicoes, negocios = E.contrato(__import__(__name__))
