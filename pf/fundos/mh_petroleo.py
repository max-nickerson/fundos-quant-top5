"""
Petróleo em pânico: PETR4/PRIO3 x petróleo (MCL na CME) — pessoa física com R$ 20–50 mil.

Tese de mesa: PETR4 é "Brent em reais + risco Petrobras". Em pânico (venda forçada de estrangeiro, margem, resgate de fundo) a ação cai muito
mais do que o petróleo em reais justificaria: o resíduo contra o petróleo despenca sem notícia de governança. Compro a ação no fracionário e
vendo o petróleo na proporção do beta (micro WTI, MCL, 100 barris) para ficar só com a volta do desconto; saio quando o resíduo volta a zero
ou em 42 pregões. NÃO opero o lado vendido (a pesquisa anterior mostrou que vender PETR4/PRIO "cara" perde: PRIO é compounder e a
reprecificação de governança da PETR4 não reverte). Referência: C1 da frente commodities (comprado em 23/03/2020: +63% em 23 dias).
"Regime" com sentido econômico: o gatilho `mercado` só compra quando há pânico de mercado (VIX no 1/5 mais alto do último ano ou
Ibovespa 10% abaixo do topo de 63 dias) — separa venda forçada (reverte) de notícia da empresa (não reverte).

Premissas PF (ver mh_base): PETR4/PRIO3 em ações inteiras (fracionário), custo de varejo; MCL na IBKR com só a margem lá (perde CDI, IOF
1,1% + spread na remessa). O MCL só existe desde 12/07/2021: antes disso a perna é hipotética (mesmo tamanho, retorno do BNO - T-bill).
Na prática 1 MCL (~R$ 35–50 mil de nocional com o Brent a US$ 65–90) é maior que o hedge pedido (beta ~0,5 x R$ 10–25 mil): com R$ 20 mil
o arredondamento dá ZERO contratos quase sempre; com R$ 50 mil dá 1 contrato quando o petróleo está barato (mar/2020: Brent a US$ 25).
"""
import numpy as np
import pandas as pd

import mh_base as B
import comum as C

NOME = "Petróleo em pânico: PETR4/PRIO3 x MCL"
TESE = ("Compro PETR4/PRIO3 no fracionário quando a ação cai muito mais que o petróleo em reais num pânico de mercado e vendo micro WTI "
        "(MCL) na proporção do beta; saio quando o resíduo volta a zero")
BENCHMARK = "CDI"
INICIO, CORTE = "2015-01-01", "2021-01-01"
REGIME = "nenhum"
CUSTO_TROCA = .001
PARAMS = {"z_in": 1.5, "queda": .10, "gatilho": "acao", "hedge": "mcl", "jan": 21, "max_dias": 42, "peso": .5}
GRADE = {"z_in": [1.5, 2.0], "queda": [.10, .20], "gatilho": ["acao", "mercado"]}
VIZINHANCA = {"z_in": (1.25, 2.5), "queda": (.08, .25), "jan": (15, 30), "max_dias": (30, 63)}
VARIANTES = {"sem hedge": {"hedge": "nenhum"}, "só PETR4": {"universo": ("PETR4",)}}
ATIVOS = ("PETR4", "PRIO3")
APLICAVEL = True
MOTIVO = ("Aplicável: PETR4/PRIO3 no fracionário com qualquer capital; o hedge em MCL só sai do zero com R$ 50 mil e petróleo barato "
          "(com R$ 20 mil o fundo é, na prática, PETR4/PRIO3 comprado sem hedge nos pânicos)")
INSTRUMENTOS = ("B3 (Clear/Rico, corretagem zero): PETR4/PRIO3 (lote 100, fracionário PETR4F 1 ação), até 50% do capital por nome; "
                "IBKR: MCL (CME micro WTI, 100 barris, margem ~US$ 600–1.000, US$ 0,85 por lado), só a margem remetida (IOF 1,1%); "
                "caixa em Tesouro Selic/LFTS11")
ALAVANCAGENS = [1, 1.5, 2]
MOTIVO_ALAV = ("1,5x e 2x só fazem sentido como 'mais ação no pânico' (termo a CDI+4%); 5x não: a posição já é 100% em 2 ações de vol 40–60% "
               "e a perna de MCL arredondada pode virar 2–3 contratos")


def carrega():
    return B.seleciona(B.dados(), list(ATIVOS))


def _sinais(d, z_in, queda, gatilho, jan, max_dias, universo=ATIVOS):
    P, R, ADV = B.acoes(d)
    cdi = C.CDI.reindex(B.DIAS).fillna(0)
    oil = (1 + B.ret_eua(d, "bno")) * (1 + B.PTAX.pct_change(fill_method=None).fillna(0)) - 1 - cdi   # Brent em R$, excesso
    tk = [t for t in universo if t in R.columns]
    ex = R[tk].sub(cdi, axis=0)
    beta = pd.DataFrame({t: B.beta_rolante(ex[t], oil.to_frame("oil"), lim=(.2, 2))["oil"] for t in tk})
    res = ex - beta.mul(oil, axis=0)
    z = res.rolling(jan).sum() / (res.rolling(252, min_periods=126).std() * np.sqrt(jan))
    I = (1 + R[tk].fillna(0)).cumprod()
    dd = I / I.rolling(63, min_periods=20).max() - 1
    liq = ADV[tk] >= 10e6
    ent = (z <= -z_in) & (dd <= -queda) & liq & R[tk].notna()
    if gatilho == "mercado":
        vix = B.eua_ffill(d, "vix")
        ibov = B.br(d, "ibov").ffill(limit=5)
        panico = (vix >= vix.rolling(252, min_periods=126).quantile(.8)) | (ibov / ibov.rolling(63, min_periods=20).max() - 1 <= -.10)
        ent = ent & panico.to_numpy()[:, None]
    sai = z >= 0
    pos = B.maquina(ent, sai, max_dias)
    return pos, beta, z


def _livro(d, capital=20000, lag=0, custo_mult=1, alavancagem=1, z_in=2.0, queda=.15, gatilho="mercado", hedge="mcl", jan=21,
           max_dias=42, peso=.5, universo=ATIVOS):
    pos, beta, _ = _sinais(d, z_in, queda, gatilho, jan, max_dias, universo)
    W = pos * peso
    fut = {"MCL": ("MCL", -(W * B.congela(beta, pos)).sum(axis=1))} if hedge == "mcl" else None
    return B.livro(capital, W, fut, d, lag=lag, custo_mult=custo_mult, alavancagem=alavancagem,
                   taxa_aluguel={"PETR4": .005, "PRIO3": .01})


def excesso(d, capital=20000, custo_mult=1, lag=0, regime=REGIME, alavancagem=1, **params):
    e = B.padrao(__import__(__name__), d, capital, lag, custo_mult, alavancagem, params)["e"]
    return C.aplica_regime(e, regime, CUSTO_TROCA * custo_mult)


def classes_ir(d, capital=20000, **params):
    return B.padrao(__import__(__name__), d, capital, 0, 1, 1, params)["classes"]


def posicoes(d, capital=20000, **params):
    r = B.padrao(__import__(__name__), d, capital, 0, 1, 1, params)
    return r["W"], r["Rx"]


def negocios(d, capital=20000, **params):
    return B.negocios_de(B.padrao(__import__(__name__), d, capital, 0, 1, 1, params), capital)


def diagnostico(d, capital=20000, **params):
    r = B.padrao(__import__(__name__), d, capital, 0, 1, 1, params)
    return r["diag"]
