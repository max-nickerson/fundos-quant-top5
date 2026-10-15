"""
Pânico cambial em emergente -> compro o EXPORTADOR com custo em moeda local (ADR) e vendo o país (ETF).

Tese de mesa: quando a moeda despenca (rand, peso mexicano, rupia, peso chileno/colombiano), o estrangeiro vende "o país" pelo ETF e
pelos ADRs sem separar quem perde de quem ganha. A mineradora de ouro sul-africana (GFI, HMY, SBSW, DRD), a Sasol (SSL), os aeroportos
mexicanos (ASR, PAC, OMAB: tarifa internacional em dólar, custo em pesos), as exportadoras de software indianas (INFY, WIT), a Ecopetrol
(EC) e a SQM vendem em dólar e pagam custo em moeda local: a desvalorização AUMENTA a margem em dólar. Compro a cesta de exportadores
da moeda que caiu e vendo o ETF do país no mesmo valor (fica o "exportador contra o doméstico"), seguro semanas.
Turquia (TRY): não há ADR exportador líquido (TKC é telecom doméstica) — fica fora. Argentina: na frente em_argentina.

Choque = moeda (moeda por US$) sobe mais que `z` desvios em 21 dias (desvio de 252 dias, só passado) — o mesmo critério para todas as
moedas (rand e rupia têm vols diferentes). FX do Yahoo: o "Close" do dia t é a cotação do início de t (usar t é defasado, não futuro).
PF: tudo na IBKR (fração na compra, inteiro na venda), conta margem quando há vendido; 40% do capital por moeda, até 100%.
"""
import numpy as np
import pandas as pd

import em_comum as E

NOME = "Pânico cambial EM: exportadores (ADR) contra o país (ETF) (IBKR)"
TESE = ("Quando o rand/peso/rupia cai > 2 desvios em 21 dias, compro os ADRs exportadores daquela moeda (custo local, receita em dólar) "
        "e vendo o ETF do país; saio em 3–6 semanas")
BENCHMARK = "CDI"
INICIO, CORTE = "2013-01-01", "2021-01-01"
REGIME = "nenhum"
CUSTO_TROCA = .001
CLASSE_IR = "exterior"
GRUPOS = {"ZAR=X": (["GFI", "HMY", "SBSW", "DRD", "SSL"], "EZA"), "MXN=X": (["ASR", "PAC", "OMAB"], "EWW"),
          "INR=X": (["INFY", "WIT"], "INDA"), "CLP=X": (["SQM"], "ECH"), "COP=X": (["EC"], None)}
PARAMS = {"z": 2.0, "dias": 42, "hedge": "pais", "peso": .40}   # escolhido no IS (maior IR IS)
GRADE = {"z": [1.5, 2.0, 2.5], "dias": [21, 42], "hedge": ["pais", "nenhum"]}
VIZINHANCA = {"z": (1.6, 2.5), "dias": (30, 60), "peso": (.3, .5)}
INSTRUMENTOS = ("IBKR: GFI, HMY, SBSW, DRD, SSL (África do Sul), ASR, PAC, OMAB (México), INFY, WIT (Índia), SQM (Chile), EC (Colômbia) "
                "comprados; EZA, EWW, INDA, ECH vendidos (ações inteiras, aluguel 0,3–0,5% a.a.); conta margem >= US$ 2.000.")
APLICAVEL = True
MOTIVO = "Operável (R$ 8 mil por moeda com 20k); perna vendida exige conta margem; Colômbia sem ETF vivo (só comprado)."
ALAVANCAGENS = [1, 1.5, 2]
MOTIVO_ALAV = "L multiplica o peso por moeda; choques simultâneos (2015, 2020) são cortados em 100% do capital por perna."


def carrega():
    tk = list(GRUPOS) + [a for g in GRUPOS.values() for a in g[0]] + [g[1] for g in GRUPOS.values() if g[1]]
    return E.seleciona(tk)


def _pesos(d, z, dias, hedge, peso):
    fx = d["raw"][list(GRUPOS)].ffill(limit=5)
    ch = np.log(fx / fx.shift(21))
    sd = np.log(fx).diff().rolling(252, min_periods=126).std() * np.sqrt(21)
    zz = ch / sd.shift(1)
    ent = (zz >= z)
    est = E.maquina(ent, pd.DataFrame(False, index=ent.index, columns=ent.columns), dias, espera=10)
    P = E.preco_usd(d)
    neg = E.negociou(d)
    cols = [a for g in GRUPOS.values() for a in g[0]] + sorted({g[1] for g in GRUPOS.values() if g[1]})
    W = pd.DataFrame(0.0, index=P.index, columns=cols)
    for m, (ex, pais) in GRUPOS.items():
        disp = P[ex].notna() & neg[ex].rolling(5, min_periods=1).max().astype(bool)
        w = disp.astype(float).div(disp.sum(axis=1).replace(0, np.nan), axis=0).fillna(0) * peso
        w = E.congela(w, pd.DataFrame({a: est[m] for a in ex}))
        W[ex] = W[ex] + w
        if hedge == "pais" and pais is not None:
            W[pais] = W[pais] - w.sum(axis=1).where(P[pais].notna(), 0)
    comprado = W.clip(lower=0).sum(axis=1)
    f = (1.0 / comprado).clip(upper=1).fillna(1)
    W = W.mul(f, axis=0)
    W = W.where(W.ne(W.shift(1)) | (W == 0)).ffill().fillna(0)
    return W, {}


excesso, classes_ir, posicoes, negocios = E.contrato(__import__(__name__))
