"""
(5) ETF de cripto da B3 x futuro da B3, market-neutral: compro o ETF quando ele está barato contra o próprio futuro e vendo o futuro.

O que já foi testado (gl_cripto_premio): ETF contra o BTC/ETH à vista com ordem limitada — o ganho era a ALTA do cripto (beta). Aqui o
hedge é o FUTURO da mesma bolsa, no mesmo fechamento, em contratos inteiros: BIT (0,01 BTC, R$, desde 16/06/2025), ETR (0,25 ETH, cotado
em US$) e SOL (5 SOL, em US$), lançados em 16/06/2025. Antes disso o BIT tinha 0,1 BTC (R$ 35–60 mil): não cabe -> INICIO 2025-06-16.

Tese de mesa: o ETF (BITH11, ETHE11, SOLH11) é negociado por varejo e por UM formador; o futuro, por mesas e arbitradores. Em dia de
pânico/euforia o varejo vende/compra o ETF a mercado e o formador alarga o spread; a razão ETF/futuro sai da mediana. Quem compra o ETF
barato e vende o futuro trava a diferença; ela volta quando o formador reequilibra (cria/resgata cotas). Vendedor forçado: o varejo do ETF.
Sinal no fechamento de t: desvio = ln(meio do ETF / (ajuste do futuro x câmbio)) − mediana de 40 pregões (só passado); se desvio < −thr
compro o ETF na OFERTA DE VENDA do fechamento de t+1 e vendo N futuros (inteiros, nocional ≈ `peso` x capital) no ajuste de t+1; saio
(ETF na oferta de compra, futuro no ajuste) quando o desvio volta acima de −thr/3 ou após `max_dias`. Futuro contínuo: contrato mais
negociado da véspera (sem salto de rolagem). Custos: ETF 0,03% + spread real; futuro 0,05%/lado. ETR/SOL em US$: o P&L do futuro é
convertido pelo dólar do dia — sobra exposição cambial sobre o nocional (sem WDO, que é grande demais: US$ 10 mil); fica no P&L (ruído).
Preços não simultâneos: ajuste (~17h-18h) x leilão de fechamento do ETF (18h) — diferença de minutos; medido no caderno.
IR: ETF e futuro são renda variável comum (15%) e se compensam (IN RFB 1.585/2015) -> uma classe só (futuros_b3).
"""
import re

import numpy as np
import pandas as pd

import cr_comum as K
from gl_cripto_premio import bit_continuo

NOME = "ETF cripto B3 x futuro B3 (BITH11/ETHE11/SOLH11 x BIT/ETR/SOL), market-neutral"
TESE = "compro o ETF de cripto quando ele fecha barato contra o próprio futuro da B3 e vendo o futuro em contratos inteiros"
BENCHMARK = "CDI"
INICIO, CORTE = "2025-06-16", "2026-01-01"
REGIME = "nenhum"
CUSTO_TROCA = .0
CLASSE_IR = "futuros_b3"
PARAMS = {"thr": .005, "max_dias": 5, "peso": .3}   # maior IR no IS (todas negativas no IS de 6,5 meses)
GRADE = {"thr": [.005, .01, .015, .02], "max_dias": [3, 5, 10]}
VIZINHANCA = {"thr": (.007, .015), "max_dias": (3, 8), "peso": (.2, .33)}
PARES = {"BTC": ("BITH11", "BIT", .01, False), "ETH": ("ETHE11", "ETR", .25, True), "SOL": ("SOLH11", "SOL", 5.0, True)}
INSTRUMENTOS = [{"onde": "B3", "ticker": f"{e} x {f}", "lote": f"1 cota x {m} {a}", "custo": "ETF 0,03%+spread; futuro 0,05%/lado"}
                for a, (e, f, m, _) in PARES.items()]
APLICAVEL = True
MOTIVO = "tudo na B3 (conta única, garantia em Tesouro Selic); contratos de 0,01 BTC / 0,25 ETH / 5 SOL cabem em R$ 20 mil desde 06/2025"
ALAVANCAGENS = [1, 1.5]
MOTIVO_ALAV = "3 pares x 30% = 90% do PL em ETF; 1,5x só se os sinais não coincidirem (margem do futuro é pequena, o ETF é pago à vista)"
FUT_CUSTO = .0005


def carrega():
    b = pd.read_parquet(K.GC / "b3_etf_bdr.parquet")
    f = pd.read_parquet(K.GC / "futuros_b3.parquet")
    f = f[f.ticker.str.fullmatch(r"(BIT|ETR|SOL)[FGHJKMNQUVXZ]\d\d")]
    dol = pd.read_csv(K.GC / "dolar.csv", index_col=0, parse_dates=True)
    return {"etf": b[b.ticker.isin([v[0] for v in PARES.values()])], "fut": f, "dol": dol}


def _fx(d):
    x = d["dol"]
    s = x["dol_b3"].reindex(K.DIAS).fillna(x["brlx"].reindex(K.DIAS))
    return s.fillna(K.PTAX.reindex(K.DIAS)).ffill()


def _simula(d, capital, custo_mult, lag, thr, max_dias, peso, alavancagem=1):
    e = d["etf"]
    piv = lambda c: e.pivot_table(index="data", columns="ticker", values=c, aggfunc="last").reindex(K.DIAS)
    F, BI, AS, NG = piv("fech"), piv("oferta_compra"), piv("oferta_venda"), piv("negocios")
    fx = _fx(d)
    ini = K.DIAS.searchsorted(pd.Timestamp(INICIO))
    T = len(K.DIAS)
    out_pnl, out_E, out_R, neg = {}, {}, {}, []
    cdi = K.CDI_D.values
    for a, (etf, pre, mult, usd) in PARES.items():
        ff = d["fut"][d["fut"].ticker.str.startswith(pre)]
        if etf not in F or not len(ff):
            out_pnl[a], out_E[a], out_R[a] = pd.Series(0.0, index=K.DIAS), pd.Series(0.0, index=K.DIAS), pd.Series(0.0, index=K.DIAS)
            continue
        rf, nivel = bit_continuo(ff)
        X = fx if usd else pd.Series(1.0, index=K.DIAS)
        p, bi, ask, ng = F[etf], BI[etf], AS[etf], NG[etf].fillna(0)
        ok_q = (bi > 0) & (ask >= bi) & ((ask - bi) / ask < .02)
        meio = ((bi + ask) / 2).where(ok_q, p)
        justo = nivel * X
        q = np.log(meio / justo).where((ng > 0) & (justo > 0))
        dev = (q - q.rolling(40, min_periods=15).median().shift(1)).values
        hs = ((ask - bi) / (ask + bi)).where(ok_q).fillna(.004).clip(.0002, .02).values
        pv, nv, rv, Xv = p.ffill().values, nivel.ffill().values, rf.fillna(0).values, X.ffill().values
        pnl, E = np.zeros(T), np.zeros(T)
        sh = 1 + lag
        i = ini
        while i < T - sh:
            if not (np.isfinite(dev[i]) and dev[i] < -thr):
                i += 1
                continue
            k = i + sh                                                     # execução
            if not (np.isfinite(nv[k]) and pv[k] > 0 and ng.iloc[k] > 0):
                i += 1
                continue
            noc1 = mult * nv[k] * Xv[k]
            N = np.floor(peso * alavancagem * capital / noc1)
            if N < 1:
                i += 1
                continue
            n = np.floor(N * noc1 / pv[k])
            px_in = pv[k] * (1 + hs[k])
            acc = n * (pv[k] - px_in) - n * px_in * K.pf.B3_EMOL * custo_mult - N * noc1 * FUT_CUSTO * custo_mult
            pnl[k] += acc
            E[k] = n * pv[k]
            j = k + 1
            sai = None
            while j < T:
                dp = n * (pv[j] - pv[j - 1]) - N * mult * nv[j - 1] * rv[j] * Xv[j] - n * pv[j - 1] * cdi[j]
                pnl[j] += dp
                acc += dp
                dec = j - sh
                if dec >= k and ((np.isfinite(dev[dec]) and dev[dec] > -thr / 3) or dec - k >= max_dias):
                    c = n * pv[j] * (hs[j] + K.pf.B3_EMOL) * custo_mult + N * mult * nv[j] * Xv[j] * FUT_CUSTO * custo_mult
                    pnl[j] -= c
                    acc -= c
                    sai = j
                    break
                E[j] = n * pv[j]
                j += 1
            neg.append({"ativo": f"{etf}x{pre}", "lado": 1, "entrada": K.DIAS[k], "saida": K.DIAS[sai if sai else T - 1],
                        "dias": (sai if sai else T - 1) - k, "desvio_entrada_%": dev[i] * 100,
                        "retorno_%": acc / (n * px_in) * 100 if n else np.nan, "contrib_pp": acc / capital * 100})
            i = (sai if sai else T) + 1 - sh
        out_pnl[a], out_E[a] = pd.Series(pnl, index=K.DIAS), pd.Series(E, index=K.DIAS)
        out_R[a] = (p.ffill().pct_change(fill_method=None) - rf * (X / X.shift(1)).fillna(1)).fillna(0)
    return pd.DataFrame(out_pnl), pd.DataFrame(out_E), pd.DataFrame(out_R), pd.DataFrame(neg)


def excesso(d, capital=20000, custo_mult=1, lag=0, regime=REGIME, alavancagem=1, **params):
    p = {**PARAMS, **params}
    pnl, _, _, _ = _simula(d, capital, custo_mult, lag, p["thr"], int(p["max_dias"]), p["peso"], alavancagem)
    return K.C.aplica_regime(pnl.sum(axis=1) / capital, regime, CUSTO_TROCA * custo_mult)


def classes_ir(d, capital=20000, **params):
    p = {**PARAMS, **params}
    pnl, E, _, _ = _simula(d, capital, 1, 0, p["thr"], int(p["max_dias"]), p["peso"])
    perd = (E.shift(1).fillna(0) * K.CDI_D.values[:, None]).sum(axis=1)
    return {"futuros_b3": pnl.sum(axis=1) + perd, "_cdi_perdido": perd}


def posicoes(d, capital=20000, **params):
    p = {**PARAMS, **params}
    _, E, R, _ = _simula(d, capital, 1, 0, p["thr"], int(p["max_dias"]), p["peso"])
    return (E / capital).shift(-1).fillna(0), R.sub(K.CDI_D, axis=0)


def negocios(d, capital=20000, **params):
    p = {**PARAMS, **params}
    ng = _simula(d, capital, 1, 0, p["thr"], int(p["max_dias"]), p["peso"])[3]
    cols = ["ativo", "lado", "entrada", "saida", "dias", "retorno_%", "contrib_pp", "desvio_entrada_%"]
    return ng[cols] if len(ng) else pd.DataFrame(columns=cols)


if __name__ == "__main__":
    d = carrega()
    e = excesso(d)
    print(e[e.index >= INICIO].groupby(e[e.index >= INICIO].index.to_period("Q")).sum() * 100)
    n = negocios(d)
    print(len(n), n.groupby("ativo").contrib_pp.agg(["sum", "count"]))
    print(n.sort_values("contrib_pp").to_string())
