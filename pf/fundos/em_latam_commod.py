"""
"Petróleo em pânico" fora do Brasil: ADRs/ETFs andinos e colombianos x commodity (Ecopetrol x Brent, Southern Copper/Chile/Peru x
cobre, Buenaventura x ouro) — compro o ativo quando ele cai muito mais que a commodity num pânico e vendo a commodity no beta.

Tese de mesa (análogo do mh_petroleo, que sobreviveu no Brasil): EC é "Brent em dólar + risco Colômbia"; SCCO/ECH/EPU são "cobre +
risco país"; BVN é "ouro/prata + risco Peru". No pânico (resgate de fundo EM/LatAm, margem, eleição) o ativo cai mais do que a commodity
justifica: o resíduo contra a commodity despenca sem notícia própria. Compro o ativo, vendo o ETF da commodity na proporção do beta (só
fica a volta do desconto) e saio quando o resíduo volta a zero ou em 42 pregões. "Mercado" (opção da grade): só compra com pânico de
mercado (VIX no 1/5 mais alto do ano ou EEM 10% abaixo do topo de 63 dias) — separa venda forçada de notícia da empresa/país.

PF: tudo na IBKR — o hedge por micro futuro não cabe (1 MHG = 2.500 lb de cobre ~ US$ 12 mil; 1 MCL ~ US$ 6–8 mil > posição de US$ 1–2
mil); uso ETFs vendidos em ações inteiras: BNO (Brent), CPER (cobre; só 10 mil ações para alugar na IBKR em 15/10/2026), GLD (ouro).
Conta margem (US$ 2.000) para vender. 25% do capital por ativo, no máximo 2 ao mesmo tempo.
"""
import numpy as np
import pandas as pd

import em_comum as E

NOME = "Commodity em pânico LatAm: EC/SCCO/BVN/ECH/EPU x Brent/cobre/ouro (IBKR)"
TESE = ("Compro o ADR/ETF andino que caiu muito mais que a sua commodity num pânico (resíduo z <= −1,5/−2 e queda > 10–20%) e vendo o "
        "ETF da commodity no beta; saio quando o resíduo volta a zero")
BENCHMARK = "CDI"
INICIO, CORTE = "2013-01-01", "2021-01-01"
REGIME = "nenhum"
CUSTO_TROCA = .001
CLASSE_IR = "exterior"
MAPA = {"EC": "BNO", "SCCO": "CPER", "BVN": "GLD", "ECH": "CPER", "EPU": "CPER"}
PARAMS = {"z_in": 1.5, "queda": .20, "gatilho": "ativo", "jan": 21, "max_dias": 42, "peso": .25, "hedge": "commodity"}   # escolhido no IS (maior IR IS; todas as variantes negativas no IS)
GRADE = {"z_in": [1.5, 2.0], "queda": [.10, .20], "gatilho": ["ativo", "mercado"]}
VIZINHANCA = {"z_in": (1.2, 2.0), "queda": (.15, .27), "jan": (15, 30), "max_dias": (30, 63), "peso": (.18, .33)}
INSTRUMENTOS = ("IBKR: EC, SCCO, BVN (ADRs NYSE), ECH, EPU (ETFs) comprados com fração; BNO, CPER, GLD vendidos em ações inteiras "
                "(aluguel 0,3–0,5% a.a.). Conta margem >= US$ 2.000. Micro futuros (MCL/MHG/MGC) grandes demais para a posição.")
APLICAVEL = True
MOTIVO = ("Operável com R$ 20 mil (R$ 5 mil por ativo), mas o hedge em ETF vendido exige conta margem (US$ 2.000 parados durante o "
          "negócio) e o CPER tem pouco papel para alugar")
ALAVANCAGENS = [1, 1.5, 2]
MOTIVO_ALAV = "L multiplica o peso por ativo; 5x não (ativos de vol 35–50% + perna vendida)."
VARIANTES = {"sem hedge": {"hedge": "nenhum"}}


def carrega():
    return E.seleciona(list(MAPA) + sorted(set(MAPA.values())) + ["EEM", "^VIX"])


def _pesos(d, z_in, queda, gatilho, jan, max_dias, peso, hedge):
    P = E.preco_usd(d)
    neg = E.negociou(d)
    at = list(MAPA)
    R = P.pct_change(fill_method=None)
    rc = pd.DataFrame({a: R[MAPA[a]] for a in at})
    ra = R[at]
    beta = pd.DataFrame({a: (ra[a].rolling(252, min_periods=126).cov(rc[a]) / rc[a].rolling(252, min_periods=126).var()) for a in at}).clip(.2, 2)
    res = ra - beta.shift(1) * rc
    z = res.rolling(jan, min_periods=jan // 2).sum() / (res.rolling(252, min_periods=126).std() * np.sqrt(jan))
    dd = P[at] / P[at].rolling(63, min_periods=20).max() - 1
    ent = (z <= -z_in) & (dd <= -queda) & neg[at]
    if gatilho == "mercado":
        pan = E.panico_mercado(P["EEM"], d["raw"]["^VIX"])
        ent = ent & pan.to_numpy()[:, None]
    est = E.maquina(ent, z >= 0, max_dias, espera=5)
    est = E.limita_n(est, 2, -z)                                           # no máximo 2 ao mesmo tempo (maior desconto primeiro)
    W = est * peso
    W = W.where(W.ne(W.shift(1)) | (W == 0)).ffill().fillna(0)
    if hedge == "commodity":
        b = E.congela(beta.where(est > 0), est)
        for c in sorted(set(MAPA.values())):
            W[c] = -sum(W[a] * b[a] for a in at if MAPA[a] == c)
    return W, {}


excesso, classes_ir, posicoes, negocios = E.contrato(__import__(__name__))
