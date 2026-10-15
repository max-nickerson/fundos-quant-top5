"""
Exportadoras (SUZB3/FIBR3/KLBN11/VALE3) que ficaram para trás do dólar, com hedge de dólar em mini-dólar (WDO) e de bolsa em mini-índice (WIN).

Tese de mesa: a receita da Suzano/Klabin/Vale é em dólar e o custo em real — quando o dólar sobe o lucro em reais sobe NA HORA, mas a ação
reage com atraso (o analista só revisa a estimativa no trimestre seguinte, o estrangeiro que vende Brasil vende tudo junto). Quando a ação
fica muito abaixo do que o dólar e o Ibovespa explicariam (resíduo de 2 fatores, beta de 1 ano), compro a ação e vendo dólar (WDO) e
Ibovespa (WIN) nas proporções dos betas: fico só com a volta do resíduo. Saio quando o resíduo volta a zero ou em 63 pregões. Só comprado
(alugar exportadora para vender custa 0,5% por contrato e o resíduo dela tem tendência de alta nos ciclos de dólar — C8 da pesquisa
anterior mostrou que a "exportadora com hedge" como fator não tem alfa; aqui é só o desvio de curto prazo).

A pergunta do dono — "1 WDO = US$ 10 mil: com R$ 50 mil cabe?": o hedge pedido é beta_dólar (~0,3–0,8) x posição (R$ 7–17 mil por nome com
R$ 50 mil) = R$ 2–14 mil de dólar, contra R$ 25–55 mil de 1 WDO. O arredondamento dá 0 contrato quase sempre com R$ 20 mil e às vezes 1
contrato com R$ 50 mil (aí o hedge fica 2–5x maior que o pedido = aposta vendida em dólar). Ver `diagnostico`.
FIBR3 (Fibria, até a fusão com a Suzano em jan/2019) entra para não haver viés de sobrevivência; SUZB3 só a partir da migração (nov/2017).
"""
import numpy as np
import pandas as pd

import mh_base as B
import comum as C

NOME = "Exportadoras atrasadas vs dólar, hedge WDO+WIN"
TESE = ("Compro SUZB3/KLBN11/VALE3 quando a ação ficou muito abaixo do que o dólar e o Ibovespa explicam e vendo WDO e WIN nos betas; "
        "saio quando o resíduo zera")
BENCHMARK = "CDI"
INICIO, CORTE = "2015-01-01", "2021-01-01"
REGIME = "nenhum"
CUSTO_TROCA = .001
PARAMS = {"z_in": 2.0, "jan": 42, "hedge": "wdo+win", "max_dias": 63, "peso": 1 / 3}
GRADE = {"z_in": [1.5, 2.0], "jan": [42, 63], "hedge": ["wdo+win", "nenhum"]}
VIZINHANCA = {"z_in": (1.25, 2.5), "jan": (30, 90), "max_dias": (42, 90)}
VARIANTES = {"só WIN": {"hedge": "win"}, "só WDO": {"hedge": "wdo"}}
ATIVOS = ("SUZB3", "FIBR3", "KLBN11", "VALE3")
APLICAVEL = True
MOTIVO = ("Aplicável nas ações (fracionário); o hedge não cabe: com R$ 20 mil o WDO arredonda para zero (fundo vira ação comprada com "
          "hedge parcial de WIN), com R$ 50 mil o WDO sai em 0 ou 1 contrato (1 = hedge 2–5x maior que o pedido)")
INSTRUMENTOS = ("B3 (Clear/Rico): SUZB3/KLBN11/VALE3 no fracionário, 1/3 do capital por nome; WDO (US$ 10 mil, margem ~12%, R$ 1,20 + "
                "meio tick por lado, rola todo mês) e WIN (R$ 0,20/ponto, margem ~15%) vendidos; garantia em Tesouro Selic")
ALAVANCAGENS = [1, 1.5, 2]
MOTIVO_ALAV = "Até 2x (termo a CDI+4% nas ações); 5x não: 3 ações de vol 30–40% a 5x e os contratos arredondados viram aposta direcional"


def carrega():
    return B.seleciona(B.dados(), list(ATIVOS))


def _livro(d, capital=20000, lag=0, custo_mult=1, alavancagem=1, z_in=2.0, jan=63, hedge="wdo+win", max_dias=63, peso=1 / 3):
    P, R, ADV = B.acoes(d)
    fut = B.futuros(d)
    cdi = C.CDI.reindex(B.DIAS).fillna(0)
    X = pd.DataFrame({"usd": fut["WDO"][0], "ibov": fut["WIN"][0]})
    tk = [t for t in ATIVOS if t in R.columns]
    ex = R[tk].sub(cdi, axis=0)
    bet = {t: B.beta_rolante(ex[t], X, lim=(-.5, 2.5)) for t in tk}
    bu = pd.DataFrame({t: bet[t]["usd"] for t in tk})
    bi = pd.DataFrame({t: bet[t]["ibov"] for t in tk})
    res = ex - bu * X["usd"].to_numpy()[:, None] - bi * X["ibov"].to_numpy()[:, None]
    z = res.rolling(jan).sum() / (res.rolling(252, min_periods=126).std() * np.sqrt(jan))
    ent = (z <= -z_in) & (ADV[tk] >= 10e6) & R[tk].notna()
    pos = B.maquina(ent, z >= 0, max_dias, espera=5)
    W = pos * peso
    f = {}
    if hedge in ("wdo+win", "wdo"):
        f["WDO"] = ("WDO", -(W * B.congela(bu, pos)).sum(axis=1))
    if hedge in ("wdo+win", "win"):
        f["WIN"] = ("WIN", -(W * B.congela(bi, pos)).sum(axis=1))
    return B.livro(capital, W, f or None, d, lag=lag, custo_mult=custo_mult, alavancagem=alavancagem)


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
    """Quanto hedge foi pedido x quanto coube em contratos inteiros (dias com posição em ação)."""
    r = B.padrao(__import__(__name__), d, capital, 0, 1, 1, params)
    out = dict(r["diag"])
    W = r["W"]
    acoes = [c for c in W.columns if c in ATIVOS]
    em_pos = W[acoes].abs().sum(axis=1) > 0
    for k in ("WDO", "WIN"):
        if k in r["pos"]:
            n = r["pos"][k][em_pos.shift(1, fill_value=False)]
            out[f"{k}: % dos dias em posição com 0 contrato"] = float((n == 0).mean() * 100) if len(n) else np.nan
    return out
