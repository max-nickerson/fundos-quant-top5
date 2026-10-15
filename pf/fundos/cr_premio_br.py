"""
(2) "Prêmio brasileiro" do bitcoin/ether: arbitragem entre corretoras brasileiras (Mercado Bitcoin x Binance BR) e triangular em R$.

Tese de mesa: o varejo brasileiro compra e vende cripto em R$ em livros rasos (Mercado Bitcoin: mediana de 1,5 BTC por hora). Em pânico
(FTX, nov/2022; LUNA, mai/2022) ou em euforia, o livro em R$ de uma corretora descola do outro: quem precisa sair vende a mercado onde tem
saldo. O arbitrador com ESTOQUE nas duas corretoras (BTC e R$ em cada) vende onde está caro e compra onde está barato no mesmo instante,
sem transferir nada (rebalanceia o estoque depois, por PIX e saque de cripto). Vendedor forçado: o varejo que só tem conta numa corretora.
Tamanho pequeno é vantagem (o livro raso só aceita lote pequeno).

O "prêmio brasileiro" contra o mundo (BTC-BRL / (BTCUSDT x dólar)) é medido no caderno: 0,6-0,7% em média = o custo de IOF/remessa que o
brasileiro evita comprando em R$ (e o ágio do USDT); fecha em 0,2-0,3% em 2025-26. Arbitrar contra o mundo exige conta offshore + câmbio
(IOF 1,1% / Res. BCB 521 trata stablecoin como câmbio) — não cabe. As versões testadas aqui são 100% domésticas:
  par="mb_bn":  MB BTC-BRL/ETH-BRL x Binance BTCBRL/ETHBRL (custos: MB 0,70% taker + 0,10% meio spread; Binance 0,10% + 0,05%).
  par="tri":    Binance BTCBRL x (BTCUSDT x USDTBRL), as três pernas na mesma corretora (0,10% + 0,03% por perna).
Sinal (candles de 1h, preço de fechamento = último negócio da hora; NÃO são ofertas simultâneas — conservador no custo): z = ln(A/B) −
mediana de 30 dias (só passado). Entra se |z| > thr (vende o caro, compra o barato), sai quando |z| < sai ou após `max_h` horas.
Executa no fechamento da hora SEGUINTE (t+1). Estoque: só `aloc` (25%) do capital fica nas corretoras (o resto no CDI); K por perna = 4K por ativo (BTC + R$ nas duas pontas). Custo do estoque:
o R$ parado nas corretoras não rende CDI; o BTC/ETH do estoque precisa de hedge (BIT/ETR vendido na B3) para não virar beta — cobro
CDI sobre o R$ parado e 4 pp a.a. sobre o estoque em cripto (base do BIT ≈ CDI − 4 pp, medida no gl_cripto_tendencia). Antes de 06/2025 o
BIT era de 0,1 BTC (não cabia): o hedge é uma aproximação nesse período (documentado). IR: classe cripto (isenção de R$ 35 mil/mês de
vendas — com giro alto o mês costuma passar de R$ 35 mil -> 15%).
"""
import numpy as np
import pandas as pd

import cr_comum as K

NOME = "Prêmio brasileiro: arbitragem MB x Binance BR e triangular em R$ (estoque nas duas pontas)"
TESE = "com BTC/ETH e R$ parados em duas corretoras, vendo onde o varejo pagou caro e compro onde vendeu barato, na mesma hora"
BENCHMARK = "CDI"
INICIO, CORTE = "2020-11-01", "2023-01-01"
REGIME = "nenhum"
CUSTO_TROCA = .0
CLASSE_IR = "cripto"
PARAMS = {"par": "mb_bn", "thr": .03, "sai": .0, "max_h": 72, "aloc": .25}   # maior IR no IS (todas negativas)
GRADE = {"par": ["mb_bn", "tri"], "thr": [.01, .015, .02, .03], "max_h": [24, 72]}
VIZINHANCA = {"aloc": (.15, .4), "thr": (.02, .04), "sai": (-.002, .003), "max_h": (36, 120)}
INSTRUMENTOS = [{"onde": "Mercado Bitcoin", "ticker": "BTC-BRL / ETH-BRL", "lote": "fração", "custo": "0,70% taker + spread"},
                {"onde": "Binance BR", "ticker": "BTCBRL / ETHBRL / BTCUSDT / USDTBRL", "lote": "fração", "custo": "0,10% + spread"},
                {"onde": "B3", "ticker": "BIT/ETR vendidos (hedge do estoque)", "lote": "0,01 BTC / 0,25 ETH", "custo": "~0,05%"}]
APLICAVEL = True
MOTIVO = ("contas em duas corretoras brasileiras (PF abre em minutos), frações de BTC/ETH; o hedge do estoque com BIT só cabe para R$ 20 mil "
          "desde 06/2025 (antes: estoque em beta ou só R$ 50 mil+)")
ALAVANCAGENS = [1]
MOTIVO_ALAV = "estoque tem de estar pago à vista nas duas corretoras; não há margem em corretora brasileira de cripto"
CUSTO = {"mb_bn": (.0080, .0015), "tri": (.0013, .0026)}              # (perna A, perna B) por lado: taxa + meio spread
CUSTO_ESTOQUE = .04
ATIVOS = ["BTC", "ETH"]


def carrega():
    c = pd.read_parquet(K.GC / "cripto_br.parquet")
    c = c[c.res == "1h"].copy()
    c["fecha"] = c.data + pd.Timedelta(hours=1)
    P = c.pivot_table(index="fecha", columns=["fonte", "sym"], values="fech", aggfunc="last").sort_index()
    P.columns = [f"{a}_{b}" for a, b in P.columns]
    return {"px": P[P.index >= "2020-10-01"]}


def _pernas(d, par):
    P = d["px"]
    if par == "mb_bn":
        return {"BTC": (P["MB_BTC-BRL"], P["BN_BTCBRL"]), "ETH": (P["MB_ETH-BRL"], P["BN_ETHBRL"])}
    return {"BTC": (P["BN_BTCBRL"], P["BN_BTCUSDT"] * P["BN_USDTBRL"]), "ETH": (P["BN_ETHBRL"], P["BN_ETHUSDT"] * P["BN_USDTBRL"])}


def _simula(d, capital, custo_mult, lag, par, thr, sai, max_h, alavancagem=1, aloc=.25):
    pern = _pernas(d, par)
    idx = d["px"].index
    k = capital * aloc * alavancagem / len(ATIVOS) / 4                               # R$ por perna
    ca, cb = CUSTO[par]
    sh = 1 + 24 * lag
    E, PNL, RR = {}, {}, {}
    for a, (A, B) in pern.items():
        A, B = A.reindex(idx), B.reindex(idx)
        s = np.log(A / B)
        z = (s - s.rolling(720, min_periods=240).median().shift(1)).values
        ok = np.isfinite(z)
        T = len(idx)
        x = np.zeros(T)
        h = 0
        for i in range(1, T):
            x[i] = x[i - 1]
            if not ok[i]:
                continue
            if x[i] != 0:
                h += 1
                if abs(z[i]) < sai or np.sign(z[i]) == x[i] or h >= max_h:
                    x[i], h = 0, 0                                         # fechou (ou inverteu, ou prazo)
            if x[i] == 0 and abs(z[i]) > thr:
                x[i], h = -np.sign(z[i]), 0                                # z>0: A caro -> vende A (x=-1), compra B
        X = pd.Series(x, index=idx).shift(sh).fillna(0)                   # executa no fechamento da hora t+1(+24 lag)
        rA, rB = A / A.shift(1) - 1, B / B.shift(1) - 1
        r = (rA - rB)
        X = X.where(r.notna() | (X == 0), 0)
        X0 = X.shift(1).fillna(0)
        cus = (X - X0).abs() * k * (ca + cb + .0005) * custo_mult           # + 0,05% de rebalanceamento do estoque (saque/PIX)
        E[a], PNL[a], RR[a] = X * k, X0 * r.fillna(0) * k - cus, r
    E, PNL, RR = pd.DataFrame(E), pd.DataFrame(PNL), pd.DataFrame(RR)
    estoque = pd.Series(capital * aloc * alavancagem, index=K.DIAS) * (pd.Series(K.DIAS, index=K.DIAS) >= idx[0])   # 4K por ativo, sempre
    # metade do estoque é R$ parado (sem CDI); metade é cripto com hedge vendido no BIT/ETR (rende a base ≈ CDI − 4 pp)
    return {"E": E, "pnl": PNL, "r": RR, "carrego": estoque / 2 * K.CDI_D + estoque / 2 * CUSTO_ESTOQUE / 252}


def excesso(d, capital=20000, custo_mult=1, lag=0, regime=REGIME, alavancagem=1, **params):
    p = {**PARAMS, **params}
    x = _simula(d, capital, custo_mult, lag, p["par"], p["thr"], p["sai"], int(p["max_h"]), alavancagem, p["aloc"])
    e = (K.para_dias(x["pnl"].sum(axis=1)) - x["carrego"]) / capital
    e = e.where(e.index >= pd.Timestamp(INICIO), 0)
    return K.C.aplica_regime(e.fillna(0), regime, CUSTO_TROCA * custo_mult)


def posicoes(d, capital=20000, **params):
    p = {**PARAMS, **params}
    x = _simula(d, capital, 1, 0, p["par"], p["thr"], p["sai"], int(p["max_h"]), 1, p["aloc"])
    giro = x["E"].diff().abs().fillna(0)               # cada abertura/fechamento vende K de cripto numa das corretoras
    W, R = K.W_com_vendas(x["E"].abs(), x["r"], capital)
    v = giro.sum(axis=1).groupby(K.balde(giro.index)).sum().reindex(K.DIAS).fillna(0) / capital
    par = np.arange(len(K.DIAS)) % 2 == 0
    W["_vendas_a"], W["_vendas_b"] = np.where(par, v, 0), np.where(~par, v, 0)
    return W, R


def negocios(d, capital=20000, **params):
    p = {**PARAMS, **params}
    x = _simula(d, capital, 1, 0, p["par"], p["thr"], p["sai"], int(p["max_h"]), 1, p["aloc"])
    return K.negocios_blocos(x["E"], x["pnl"], capital, x["r"])


def premio_global():
    """Prêmio do BTC em R$ (MB e Binance BR) sobre BTCUSDT x PTAX/dólar, por dia, e o USDT em R$ sobre o dólar (para o caderno)."""
    import gl_cripto_premio as GP
    return GP.kimchi()


if __name__ == "__main__":
    d = carrega()
    e = excesso(d)
    print(e.groupby(e.index.year).sum() * 100)
    n = negocios(d)
    print(len(n), n.sort_values("contrib_pp").tail(5), n.sort_values("contrib_pp").head(5))
