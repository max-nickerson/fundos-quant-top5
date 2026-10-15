"""
Bitcoin em reais com tendência, no veículo mais barato (à vista numa corretora brasileira ou BIT na B3) e contra a manada local.

Tese de mesa: o bitcoin anda em ondas de meses (halving, liquidez global, ETF spot em 2024); seguir a média longa pega o miolo das ondas
e fica fora dos invernos de -70% (2018, 2022). O tamanho é por volatilidade (vol-alvo, teto 1x do PL) para o fundo não virar uma
aposta só. Dois detalhes de pessoa física pesam:
  1. Veículo: o BTC à vista em corretora brasileira (Binance/Mercado Bitcoin) tem ISENÇÃO de IR para vendas de até R$ 35 mil no mês
     (IN RFB 1.888/2019 e Lei 9.250/95, art. 22 — vale para o conjunto de criptoativos) — com R$ 20-50 mil quase todo mês fica isento;
     o ETF (QBTC11) paga 15% sempre. O futuro BIT da B3 (desde 17/04/2024) deixa a garantia no Tesouro Selic rendendo CDI e embute
     uma base em média ~4 pp a.a. ABAIXO do CDI (medida: BIT vs BTC-BRL, 2024-26) — segurar BTC pelo futuro é mais barato que à vista,
     mas paga 15% de IR. O contrato era de 0,1 BTC (R$ 35-60 mil) até 13/06/2025 e passou a 0,01 BTC (R$ 4-6 mil): só cabe depois.
     veiculo="spot" (escolhido por causa da isenção) ou "futuro" (BIT quando cabe em contratos inteiros, senão à vista).
  2. Contra a manada local: prêmio do BTC no Mercado Bitcoin sobre o BTC global x dólar acima do percentil 90 de 1 ano = euforia do
     varejo brasileiro pagando ágio -> zera (kimchi=True).
Preço: BTC-BRL do Mercado Bitcoin (diário até 2018, candle de 1h no horário do fechamento da B3 de 2019 a 10/2020) e da Binance BTCBRL
depois. Custos: 0,5% por lado no MB até 10/2020, 0,15% na Binance depois (taxa 0,1% + spread); BIT 0,05% por lado.
Dinheiro em BTC à vista não rende CDI. INICIO 2015-01-01, CORTE 2021-01-01.
"""
import numpy as np
import pandas as pd

import gl_comum as G
from gl_cripto_premio import BIT_MULT, bit_continuo

NOME = "Bitcoin em R$ com tendência (à vista isento ou BIT) e contra a manada local"
TESE = "BTC acima da média longa, tamanho por vol, à vista em corretora BR (isenção de R$ 35 mil/mês) ou BIT; sai com ágio local alto"
BENCHMARK = "CDI"
INICIO, CORTE = "2015-01-01", "2021-01-01"
REGIME = "nenhum"
CUSTO_TROCA = .002
PARAMS = {"ma": 100, "vol_alvo": .25, "kimchi": True, "veiculo": "spot"}   # maior IR dentro da amostra
GRADE = {"ma": [100, 200], "vol_alvo": [.25, .5], "kimchi": [False, True]}
VIZINHANCA = {"ma": (70, 140), "vol_alvo": (.18, .35)}
ISENCAO_MES = 35_000.0
BIT_CUSTO = .0005
INSTRUMENTOS = {"BTC à vista": {"onde": "Binance BR / Mercado Bitcoin", "ticker": "BTCBRL", "lote": "fração", "custo": "0,15% (0,5% MB pré-2020)"},
                "BIT": {"onde": "B3 (futuro)", "ticker": "BIT", "lote": "0,01 BTC desde 06/2025", "custo": "~0,05%"}}
APLICAVEL = True
MOTIVO = "BTC à vista é fracionário (qualquer valor); BIT só cabe para R$ 20 mil desde 06/2025."
ALAVANCAGENS = [1]
MOTIVO_ALAV = "Teto de 1x do PL em BTC (vol-alvo já define o tamanho); alavancar via BIT só faria sentido com vol-alvo maior."


def carrega():
    c = G.ler("cripto_br.parquet")
    f = G.ler("futuros_b3.parquet")
    return {"cripto": c, "bit": f[f.ticker.str.startswith("BIT")], "dolar": G.ler("dolar.csv")}


def _btc(d):
    c = d["cripto"]
    mb1d = c[(c.fonte == "MB") & (c.sym == "BTC-BRL") & (c.res == "1d")].set_index("data").fech
    mb1d.index = mb1d.index + pd.Timedelta(days=1)            # candle diário fecha 00h UTC do dia seguinte (21h de Brasília)
    a = G.no_calendario(mb1d, 3)
    b = G.cripto_no_fech_b3(c, "MB", "BTC-BRL")
    bn = G.cripto_no_fech_b3(c, "BN", "BTCBRL")
    r = bn.pct_change(fill_method=None)
    r = r.where(bn.notna() & bn.shift(1).notna(), b.pct_change(fill_method=None))
    r = r.where(r.notna() | (b.notna() & b.shift(1).notna()), a.pct_change(fill_method=None))
    custo = pd.Series(np.where(G.DIAS < pd.Timestamp("2020-10-13"), .005, .0015), index=G.DIAS)
    nivel = (1 + r.fillna(0)).cumprod().where(r.notna().cumsum() > 0)
    preco = bn.fillna(b).fillna(a)
    return nivel, custo, preco


def premio_local(d):
    """Ágio do BTC no Mercado Bitcoin sobre BTCUSDT (Binance) x dólar, no horário do fechamento da B3 (2019+) ou diário (2017-18)."""
    c = d["cripto"]
    dol = d["dolar"]
    fx = dol["dol_b3"].reindex(G.DIAS).fillna(dol["brlx"].reindex(G.DIAS)).ffill(limit=3)
    h = np.log(G.cripto_no_fech_b3(c, "MB", "BTC-BRL") / (G.cripto_no_fech_b3(c, "BN", "BTCUSDT") * fx))
    m1 = c[(c.fonte == "MB") & (c.sym == "BTC-BRL") & (c.res == "1d")].set_index("data").fech
    u1 = c[(c.fonte == "BN") & (c.sym == "BTCUSDT") & (c.res == "1h")].set_index("data").fech
    u1 = u1[u1.index.hour == 23]
    u1.index = u1.index.normalize()
    dia = np.log(m1 / (u1.reindex(m1.index) * dol["brlx"].reindex(m1.index).ffill()))   # 00h UTC; dólar do Yahoo do mesmo dia
    dia.index = dia.index + pd.Timedelta(days=1)
    return h.fillna(G.no_calendario(dia, 3))


def _alvo(d, ma, vol_alvo, kimchi):
    nivel, custo, preco = _btc(d)
    tend = G.tendencia(nivel, ma)
    vol = np.log(nivel).diff().rolling(63, min_periods=40).std() * np.sqrt(252)
    w = (tend * (vol_alvo / vol).clip(upper=1)).fillna(0)
    if kimchi:
        pr = premio_local(d)
        teto = pr.rolling(252, min_periods=120).quantile(.9)
        w = w.where(~(pr > teto), 0)
    return w, nivel, custo, preco


def _simula(d, ma, vol_alvo, kimchi, veiculo, capital, custo_mult=1, lag=0):
    w, nivel, custo, preco = _alvo(d, ma, vol_alvo, kimchi)
    wt = w.shift(1 + lag).fillna(0).values                       # executa no fechamento de t+1+lag
    r = nivel.pct_change(fill_method=None).fillna(0).values
    cdi = G.CDI.reindex(G.DIAS).fillna(0).values
    cv = custo.values * custo_mult
    usa_fut = np.zeros(len(G.DIAS), bool)
    n_fut = np.zeros(len(G.DIAS))
    if veiculo == "futuro":
        rf, niv_f = bit_continuo(d["bit"])
        noc1 = (niv_f * pd.Series([BIT_MULT(t) for t in G.DIAS], index=G.DIAS)).values
        rf = rf.values
    T = len(G.DIAS)
    v = np.zeros(T)                                              # valor em BTC à vista (R$) no fim do dia
    pnl_s, cus_s, car_s, pnl_f, cus_f, vendas = (np.zeros(T) for _ in range(6))
    nf = 0.0
    for i in range(1, T):
        v_ant = v[i - 1] * (1 + r[i])
        pnl_s[i] = v[i - 1] * r[i]
        car_s[i] = -v[i - 1] * cdi[i]
        if veiculo == "futuro" and nf != 0 and rf[i] == rf[i]:
            pnl_f[i] = nf * noc1[i - 1] * rf[i]
        alvo = wt[i] * capital
        fut_ok = veiculo == "futuro" and noc1[i] == noc1[i] and round(alvo / noc1[i]) >= 1
        if fut_ok:
            n_novo = float(round(alvo / noc1[i]))
            if n_novo != nf:
                cus_f[i] = abs(n_novo - nf) * noc1[i] * BIT_CUSTO * custo_mult
            nf = n_novo
            alvo_s = 0.0
        else:
            if nf:
                cus_f[i] = abs(nf) * (noc1[i] if noc1[i] == noc1[i] else 0) * BIT_CUSTO * custo_mult
            nf = 0.0
            alvo_s = alvo
        n_fut[i] = nf
        usa_fut[i] = fut_ok
        if alvo_s == 0 or abs(v_ant - alvo_s) > .25 * alvo_s:
            cus_s[i] = abs(alvo_s - v_ant) * cv[i]
            if alvo_s < v_ant:
                vendas[i] = v_ant - alvo_s
            v[i] = alvo_s
        else:
            v[i] = v_ant
    s = lambda a: pd.Series(a, index=G.DIAS)
    return dict(pnl_s=s(pnl_s), cus_s=s(cus_s), car_s=s(car_s), pnl_f=s(pnl_f), cus_f=s(cus_f), vendas=s(vendas), v=s(v),
                nf=s(n_fut), w=w, nivel=nivel)


def excesso(d, capital=20000, custo_mult=1, lag=0, regime=REGIME, alavancagem=1, **params):
    p = {**PARAMS, **params}
    x = _simula(d, p["ma"], p["vol_alvo"], p["kimchi"], p["veiculo"], capital, custo_mult, lag)
    e = (x["pnl_s"] - x["cus_s"] + x["car_s"] + x["pnl_f"] - x["cus_f"]) / capital
    return G.C.aplica_regime(e, regime, CUSTO_TROCA * custo_mult)


def classes_ir(d, capital=20000, **params):
    """Cripto à vista: mês com vendas <= R$ 35 mil é isento; acima, 15% (aproximação: P&L do mês inteiro vai para a classe do mês)."""
    p = {**PARAMS, **params}
    x = _simula(d, p["ma"], p["vol_alvo"], p["kimchi"], p["veiculo"], capital)
    m = x["pnl_s"] - x["cus_s"]
    mes = G.DIAS.to_period("M")
    isento_mes = x["vendas"].groupby(mes).transform("sum") <= ISENCAO_MES
    return {"isento": m.where(isento_mes, 0), "cripto": m.where(~isento_mes, 0), "futuros_b3": x["pnl_f"] - x["cus_f"]}


def posicoes(d, capital=20000, **params):
    p = {**PARAMS, **params}
    w, nivel, _, _ = _alvo(d, p["ma"], p["vol_alvo"], p["kimchi"])
    return w.to_frame("BTC"), nivel.pct_change(fill_method=None).fillna(0).sub(G.CDI.fillna(0)).to_frame("BTC")


def negocios(d, capital=20000, **params):
    p = {**PARAMS, **params}
    x = _simula(d, p["ma"], p["vol_alvo"], p["kimchi"], p["veiculo"], capital)
    n = pd.DataFrame({"BTC": (x["v"] > 0).astype(float) + (x["nf"] > 0).astype(float)})
    c = ((x["pnl_s"] - x["cus_s"] + x["car_s"] + x["pnl_f"] - x["cus_f"]) / capital).to_frame("BTC")
    return G.negocios_de(n.clip(upper=1), c, x["nivel"].to_frame("BTC"))
