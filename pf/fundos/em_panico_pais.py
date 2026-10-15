"""
Pânico de país: compro o ETF de país (IBKR) depois de queda > X% em poucas semanas — o vendedor forçado é o resgate do ETF.

Tese de mesa: quando um país despenca em semanas (eleição, câmbio, sanção, crise de crédito), o estrangeiro de varejo resgata o ETF
(TUR, EWZ, ARGT, EZA...) e o market maker/AP vende a cesta local para entregar o resgate — vende sem olhar preço, no pior momento. O
comprador natural (local, fundo de valor) chega devagar. PF compra pequeno (R$ 5 mil por país = US$ ~900, fração na IBKR), segura
semanas e sai. O que separa "vendedor forçado" de "notícia que muda o país": não sei separar com regra (Rússia 2022 é a cauda) — por
isso a perna sintética da Rússia (abaixo) fica sempre ligada.

Sobrevivência (crítico): RSX/ERUS (Rússia) foram congelados em 03/2022 e não existem no Yahoo. Uma regra "compra após −15/−25% em 21–42
dias" teria comprado a Rússia em 24–25/02/2022 (MOEX −33% em rublos em 24/02, rublo −10%; RSX já vinha −30% desde o meio de fevereiro).
Lançamos uma perda SINTÉTICA de 90% do peso por país em 04/03/2022 (negociação suspensa; liquidação com valor residual ~zero). Os ganhos
da Rússia em 2014–15 (que também existiriam) NÃO entram: o viés é conservador. EGPT/NGE/PAK também sumiram (estão fora da lista pedida).

Execução PF: ETF comprado na IBKR (fração; US$ 0,35 mín. por ordem), meio spread por ETF x (vol21/vol252, 1–3x — o spread abre no
pânico); dinheiro na IBKR só durante o negócio (remessa com IOF 1,1% + spread na ida e 0,38% + spread na volta, câmbio aberto: o
patrimônio na IBKR fica em dólar). Hedge opcional: EEM vendido no beta (exige conta margem, US$ 2.000 mínimos parados).
"""
import numpy as np
import pandas as pd

import em_comum as E
import comum as C

NOME = "Pânico de país: ETF após queda forte em semanas (IBKR)"
TESE = ("Compro o ETF de país que caiu > 15% em 21 pregões (resgates forçam o AP a vender a cesta); 25% do capital por país, saio em "
        "semanas; Rússia 2022 entra como perda sintética")
BENCHMARK = "CDI"
INICIO, CORTE = "2012-01-01", "2021-01-01"
REGIME = "nenhum"
CUSTO_TROCA = .001
CLASSE_IR = "exterior"
PAISES = ["TUR", "EWZ", "ARGT", "EZA", "EWW", "ECH", "EPU", "INDA", "EIDO", "VNM", "KSA"]
PARAMS = {"queda": .15, "jan": 21, "dias": 42, "hedge": "nenhum", "peso": .25, "russia": True}   # escolhido no IS (maior IR IS da grade)
GRADE = {"queda": [.15, .20, .25], "jan": [21, 42], "dias": [21, 42], "hedge": ["nenhum", "EEM"]}
VIZINHANCA = {"queda": (.12, .20), "jan": (15, 50), "dias": (15, 63), "peso": (.18, .33)}
INSTRUMENTOS = ("IBKR: ETFs de país TUR, EWZ, ARGT, EZA, EWW, ECH, EPU, INDA, EIDO, VNM, KSA (compra fracionária, US$ 0,0035/ação, mín. "
                "US$ 0,35); hedge opcional EEM vendido (ações inteiras, aluguel ~0,25% a.a., conta margem >= US$ 2.000). Alternativa B3: "
                "BEWZ39/BEWW39/BEEM39 (BDRs de ETF) — negociam em menos da metade dos pregões, spread largo: não usados. Caixa em Tesouro Selic.")
APLICAVEL = True
MOTIVO = ("Operável: 25% do capital por país = R$ 5 mil (20k) / R$ 12,5 mil (50k), fração na IBKR; o custo fixo é a remessa (IOF) por "
          "negócio. Sem hedge cambial (1 WDO = US$ 10 mil > posição).")
ALAVANCAGENS = [1, 1.5, 2]
MOTIVO_ALAV = "L multiplica o peso por país (25% -> 37,5%/50%); acima do patrimônio a IBKR financia (T-bill + 1,5%). 5x não: 4 países = 500% em ETFs de vol 30–60%."
RUSSIA = ("2022-02-25", "2022-03-04", -.90)      # entrada (execução), suspensão, perda sintética do valor


def carrega():
    return E.seleciona(PAISES + ["EEM"])


def _pesos(d, queda, jan, dias, hedge, peso):
    P = E.preco_usd(d)[PAISES]
    neg = E.negociou(d)[PAISES]
    dd = P / P.rolling(jan, min_periods=jan // 2).max() - 1
    ent = (dd <= -queda) & neg
    est = E.maquina(ent, pd.DataFrame(False, index=P.index, columns=PAISES), dias, espera=10)
    W = est * peso
    W = E.limita(W, 1.0)
    if hedge == "EEM":
        r = P.pct_change(fill_method=None)
        rm = E.preco_usd(d)["EEM"].pct_change(fill_method=None)
        b = pd.DataFrame({c: r[c].rolling(252, min_periods=126).cov(rm) / rm.rolling(252, min_periods=126).var() for c in PAISES}).clip(0, 2)
        b = E.congela(b, est)
        W["EEM"] = -(W[PAISES] * b).sum(axis=1)
    return W


def _russia_ativa(d):
    return d["raw"].index.max() >= pd.Timestamp(RUSSIA[1])


def _roda(d, capital, custo_mult, lag, alavancagem, queda, jan, dias, hedge, peso, russia=True):
    W = _pesos(d, queda, jan, dias, hedge, peso)
    res = E.livro(d, W, capital, lag, custo_mult, alavancagem)
    if russia and _russia_ativa(d):
        perda = pd.Series(0.0, index=E.DIAS)
        dia = E.DIAS[E.DIAS.searchsorted(pd.Timestamp(RUSSIA[1]))]
        perda[dia] = RUSSIA[2] * peso * alavancagem * capital
        res["e"] = res["e"] + perda / capital
        res["classes"]["exterior"] = res["classes"]["exterior"] + perda
        res["russia"] = perda
    return res


def excesso(d, capital=20000, custo_mult=1, lag=0, regime=REGIME, alavancagem=1, queda=PARAMS["queda"], jan=PARAMS["jan"],
            dias=PARAMS["dias"], hedge=PARAMS["hedge"], peso=PARAMS["peso"], russia=PARAMS["russia"]):
    e = _roda(d, capital, custo_mult, lag, alavancagem, queda, jan, dias, hedge, peso, russia)["e"]
    return C.aplica_regime(e, regime, CUSTO_TROCA * custo_mult)


def classes_ir(d, capital=20000, **kw):
    p = {**PARAMS, **kw}
    return _roda(d, capital, 1, 0, 1, p["queda"], p["jan"], p["dias"], p["hedge"], p["peso"], p["russia"])["classes"]


def posicoes(d, capital=20000, **kw):
    p = {**PARAMS, **kw}
    return E.posicoes_de(_roda(d, capital, 1, 0, 1, p["queda"], p["jan"], p["dias"], p["hedge"], p["peso"], False), capital)


def negocios(d, capital=20000, **kw):
    p = {**PARAMS, **kw}
    res = _roda(d, capital, 1, 0, 1, p["queda"], p["jan"], p["dias"], p["hedge"], p["peso"], p["russia"])
    ng = E.negocios_de(res, capital)
    if "russia" in res:
        ng = pd.concat([ng, pd.DataFrame([{"ativo": "RSX* (sintético)", "lado": 1, "entrada": pd.Timestamp(RUSSIA[0]),
                                           "saida": pd.Timestamp(RUSSIA[1]), "dias": 5, "retorno_%": RUSSIA[2] * 100,
                                           "contrib_pp": float(res["russia"].sum() / capital * 100)}])], ignore_index=True)
    return ng
