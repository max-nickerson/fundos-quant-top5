"""
Carry G10 com micro FX da CME (IBKR) — 1 contrato por perna, só a margem lá fora.

Negócio: todo fim de mês, compro o micro da moeda de MAIOR juro de política (BIS) e vendo o da de MENOR (pares em ordem: 1º x último,
2º x penúltimo). O futuro de moeda paga exatamente o diferencial de juros (paridade coberta): comprado em AUD/vendido em JPY ganha
juro australiano − juro japonês por ano, enquanto o câmbio não andar contra. Quem paga: hedgers e importadores que precisam vender a moeda
de juro alto a termo (exportador australiano, fundos japoneses que hedgeiam Treasury), e o "seguro" que o carry trader vende contra
crises (carry desmonta junto com o risco global).
  - regime "risco" (comum.regime_risco_global >= 2/3, checado todo dia): carry é venda de seguro contra crise — fica fora quando o
    VIX está alto/S&P abaixo da média de 200d/crédito piorando (desmonte de carry trade = fuga para iene e franco).
  - filtro_tend: só monta o par se o próprio par (long − short) não caiu nos últimos 3 meses (não pegar faca caindo — 2008, 2015 CHF).
  - dif_min: só monta o par se o diferencial de juros entre as duas pernas for >= dif_min p.p. (com diferencial pequeno o custo/risco
    não paga).
Tamanho: 1 contrato por perna (M6E = € 12.500 ≈ R$ 75 mil; M6A = A$ 10.000 ≈ R$ 37 mil; MJY = ¥ 1,25 mi ≈ R$ 43 mil): cada perna é
2-4x R$ 20 mil — não existe "contrato menor"; o risco é dado pela tabela de contratos, não por vol-alvo.
Dados: spot Yahoo (EURUSD=X...) + juros de política BIS (diários, vigentes na véspera) -> retorno do futuro sem salto de rolagem.
"""
import numpy as np
import pandas as pd

import cme_comum as K

NOME = "Carry G10 com micro FX (CME)"
TESE = "Comprado no micro da moeda de maior juro e vendido no de menor, 1 contrato por perna, fora quando o risco global vira"
BENCHMARK = "CDI"
INICIO, CORTE = "2012-01-01", "2021-01-01"
REGIME = "risco"
CUSTO_TROCA = 0.0
MOEDAS = ["M6E", "M6B", "M6A", "MCD", "MSF", "MJY"]
PARAMS = {"pernas": 2, "filtro_tend": False, "dif_min": 1.5}           # melhor excesso dentro da amostra (2012-2020)
GRADE = {"pernas": [2, 4], "filtro_tend": [False, True], "dif_min": [.5, 1.5]}
VIZINHANCA = {"dif_min": (.25, 2.0)}
CLASSE_IR = "exterior"
APLICAVEL = True
MOTIVO = ("opera com R$ 20 mil (margem de 2 micros FX ≈ US$ 500-900), mas cada perna tem nocional de 2-4x o capital: 1 par já dá vol de "
          "~15-30% do patrimônio. Micro FX tem pouca liquidez (spread 1-2 ticks); MJY é o micro de iene (¥ 1,25 mi), MSF franco.")
INSTRUMENTOS = [("IBKR/CME", "M6E", "€ 12.500", "US$ 0,40 + 2 ticks/lado"), ("IBKR/CME", "M6B", "£ 6.250", "idem"),
                ("IBKR/CME", "M6A", "A$ 10.000", "idem"), ("IBKR/CME", "MCD", "C$ 10.000", "idem"), ("IBKR/CME", "MSF", "CHF 12.500", "idem"),
                ("IBKR/CME", "MJY", "¥ 1.250.000", "idem"), ("Tesouro Direto", "Tesouro Selic", "R$ ~150", "0")]
ALAVANCAGENS = [1, 2]
MOTIVO_ALAV = ("alavancagem = contratos por perna (1 ou 2). 1,5x não existe (contrato inteiro); 5x = 5 contratos por perna ≈ 15-20x o "
               "capital em nocional: uma semana como jan/2015 (franco +20%) ou ago/2024 (iene +12%) quebra a conta")


def gera(d, capital=20000, regime=REGIME, alavancagem=1, pernas=2, filtro_tend=False, dif_min=1.5):
    idx = K.dias_us(d)
    Kd = K.contratos(d, MOEDAS, idx)
    juros = d["bis"].reindex(idx, method="ffill")
    dif = pd.DataFrame({m: juros[K.ESPEC[m]["bis"]] - juros["US"] for m in MOEDAS})
    cum = pd.DataFrame({m: np.log1p(Kd[m]["r"].fillna(0)).cumsum() for m in MOEDAS})
    mom = cum - cum.shift(63)
    fim = K.ultimo_do_mes(idx)
    N = pd.DataFrame(np.nan, index=idx, columns=MOEDAS)
    k = max(int(round(alavancagem)), 1)
    for i in np.where(fim)[0]:
        x = dif.iloc[i].dropna()
        if len(x) < 4:
            continue
        o = x.sort_values(ascending=False).index
        lin = pd.Series(0.0, index=MOEDAS)
        for j in range(pernas // 2):
            a, b = o[j], o[-1 - j]
            if x[a] - x[b] < dif_min:
                continue
            if filtro_tend and (mom.iloc[i][a] - mom.iloc[i][b]) < 0:
                continue
            lin[a], lin[b] = k, -k
        N.iloc[i] = lin.values
    N = N.ffill().fillna(0)
    if regime == "risco":
        N = N.mul(K.regime_risco(idx), axis=0)
    return N, Kd


K.montar(globals(), gera)
