"""
Real tático (diferencial de juro real Brasil - EUA) em mini-dólar + compra do Brasil depois de pânico político/eleitoral.

Livro "juro": o real anda anos na direção do diferencial de juro REAL (Selic meta - IPCA esperado 12m do Focus) - (Fed funds - inflação
implícita 5 anos). Quando o diferencial está alto em relação aos últimos 5 anos (z > z_in), o carry real paga o risco e o estrangeiro entra:
vendo WDO (compro real). Quando está baixo (z < -z_in: 2011–14 Tombini, 2017–20 Selic a 2%), o real perde o suporte: compro WDO. Saio quando o z
volta a zero. Pesquisa anterior: JF6 "real tático" (vendido em real nov/2011–mai/2015 +17,5% do PL; vendido out/2017–jul/2020 +21,6%).
Livro "pânico": quando o Ibovespa cai >= `queda` em 5 pregões e o S&P NÃO caiu (> -2%) — pânico brasileiro (eleição, Joesley, greve dos
caminhoneiros, fura-teto, pacote fiscal) e não global —, compro Brasil por 42 pregões (BOVA11 no lote/fracionário com o capital à vista; ou WIN).
A regra decide os eventos (nada de lista escolhida a dedo): ver `negocios`.

PF: 1 WDO = US$ 10 mil (R$ 23 mil em 2014, ~R$ 50 mil em 2026). Com alvo de 1x o capital em dólar, R$ 20 mil arredonda para ZERO contrato
desde 2015 (o livro de juro some); R$ 50 mil dá 1 contrato. A variante "min1" opera sempre 1 contrato (com R$ 20 mil = 2,5x o capital em
dólar, vol ~35% a.a. só nesse livro). O caixa e a garantia ficam em Tesouro Selic (rendem CDI); a perna de BOVA11 sai do Tesouro.
Dados: DOL rolado da B3 desde 2019; antes, PTAX - (CDI - cupom), cupom = Fed funds + 1,07 pp (premissa do fundo de carry institucional).
"""
import numpy as np
import pandas as pd

import mh_base as B
import comum as C

NOME = "Real tático (juro real BR-EUA) em WDO + Brasil após pânico"
TESE = ("Vendo/compro mini-dólar quando o diferencial de juro real Brasil-EUA está extremo vs 5 anos; e compro Brasil (BOVA11/WIN) "
        "por 42 pregões depois de pânico brasileiro que não foi global")
BENCHMARK = "CDI"
INICIO, CORTE = "2014-01-01", "2021-01-01"
REGIME = "nenhum"
CUSTO_TROCA = .001
PARAMS = {"z_in": 1.0, "queda": .08, "livro": "juro", "noc": 1.0, "min1": False, "dias": 42, "veiculo": "bova", "peso_panico": 1.0}
GRADE = {"z_in": [.5, 1.0], "queda": [.05, .08], "livro": ["ambos", "juro", "panico"]}
VIZINHANCA = {"z_in": (.4, 1.5), "queda": (.04, .10), "dias": (21, 63)}
VARIANTES = {"livro de pânico sozinho (queda 5%)": {"livro": "panico", "queda": .05}, "ambos (queda 5%)": {"livro": "ambos", "queda": .05}, "juro com 1 contrato sempre (min1)": {"min1": True, "livro": "juro"}, "pânico via WIN": {"veiculo": "win", "livro": "panico"}}
APLICAVEL = True
MOTIVO = ("Pânico: aplicável com qualquer capital (BOVA11). Juro: só com R$ 50 mil (1 WDO ~ 1x o capital); com R$ 20 mil arredonda para 0 "
          "ou vira 2,5x o capital em dólar")
INSTRUMENTOS = ("B3 (Clear/Rico): WDO (US$ 10 mil, margem ~12% em Tesouro Selic, ~R$ 3,70 por contrato e lado com meio tick, rola todo mês); "
                "BOVA11 (cotas inteiras; lote/fracionário) ou WIN (R$ 0,20/ponto) no livro de pânico")
ALAVANCAGENS = [1, 1.5, 2, 5]
MOTIVO_ALAV = ("Futuros: alavancagem é só mais contrato (garantia em Tesouro Selic); 5x = 5 WDO com R$ 50 mil (vol ~70% a.a. no livro de juro) — "
               "viável em margem, mas a queda máxima mostra o risco; BOVA11 acima do capital via termo (CDI+4%)")


def carrega():
    d = B.seleciona(B.dados(), [])
    br = d["br"]
    for k, col in (("P", "bova_fech"), ("V", "bova_vol"), ("O", "bova_abre")):
        d[k] = br[[col]].rename(columns={col: "BOVA11"})
    d["R"] = br[["bova_fech"]].rename(columns={"bova_fech": "BOVA11"}).pct_change(fill_method=None)   # BOVA11 reinveste proventos
    return d


def _juro(d, z_in):
    selic = B.br(d, "selic_meta").ffill()
    ipca = B.br(d, "focus_ipca12m").ffill(limit=10)
    dff, bei = B.eua_ffill(d, "dff"), B.eua_ffill(d, "t5yie")
    x = (selic - ipca) - (dff - bei)
    z = (x - x.rolling(1260, min_periods=504).mean()) / x.rolling(1260, min_periods=504).std()
    zz = z.to_frame("x")
    compra_real = B.maquina(zz > z_in, zz <= 0, 10 ** 6)["x"]          # vendido em WDO
    vende_real = B.maquina(zz < -z_in, zz >= 0, 10 ** 6)["x"]          # comprado em WDO
    return vende_real - compra_real, z


def _panico(d, queda, dias):
    ib = B.br(d, "ibov").ffill(limit=5)
    spy = B.eua_ffill(d, "spy")
    r5, s5 = ib / ib.shift(5) - 1, spy / spy.shift(5) - 1
    ent = ((r5 <= -queda) & (s5 > -.02)).to_frame("x")
    return B.maquina(ent, ent & False, dias, espera=5)["x"]


def _livro(d, capital=20000, lag=0, custo_mult=1, alavancagem=1, z_in=1.0, queda=.06, livro="ambos", noc=1.0, min1=False, dias=42,
           veiculo="bova", peso_panico=1.0):
    fut, W = {}, None
    unit = B.futuros(d)["WDO"][1]
    if livro in ("ambos", "juro"):
        s, _ = _juro(d, z_in)
        alvo = s * noc
        if min1:
            alvo = np.sign(s) * np.maximum(noc, unit / capital * 1.01)
        fut["WDO"] = ("WDO", alvo)
    if livro in ("ambos", "panico"):
        p = _panico(d, queda, dias)
        if veiculo == "win":
            fut["WIN"] = ("WIN", p * peso_panico)
        else:
            W = (p * peso_panico).to_frame("BOVA11")
    return B.livro(capital, W, fut or None, d, lag=lag, custo_mult=custo_mult, alavancagem=alavancagem, classe_acoes="etf_b3")


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
    p = {**PARAMS, **params}
    r = B.padrao(__import__(__name__), d, capital, 0, 1, 1, params)
    s, z = _juro(d, p["z_in"])
    out = dict(r["diag"])
    out["juro: % dias com sinal"] = float((s != 0).mean() * 100)
    if "WDO" in r["pos"]:
        out["juro: % dias com sinal e 0 contrato"] = float(((s.shift(1) != 0) & (r["pos"]["WDO"] == 0)).mean() * 100)
    out["z juro hoje"] = float(z.dropna().iloc[-1])
    return out
