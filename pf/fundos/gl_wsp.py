"""
S&P 500 sem remessa: micro futuro de S&P da B3 (WSP) com a garantia no Tesouro Selic, completado com SPXR11 quando o contrato não cabe.

Tese de mesa: o WSP (US$ 2,50 x índice, liquidado em R$; B3) dá o prêmio da bolsa americana SOBRE o CDI: o futuro embute o juro
americano, a margem fica em Tesouro Selic rendendo CDI e o câmbio só incide sobre o ajuste diário (não sobre o principal). É o jeito
mais barato de ter S&P para quem está no Brasil: sem IOF de remessa, sem taxa de ETF, sem carrego do dólar. O fundo fica comprado
quando o S&P está acima da média de `ma` pregões (regime de risco global testado no IS e descartado), com tamanho por
volatilidade (vol-alvo, teto 2x do PL), rebalanceado no fim de cada mês. O problema é o tamanho: 1 WSP ~ US$ 19-20 mil ~ R$ 95-100 mil = 5x um PL de R$ 20 mil. Então
os contratos INTEIROS que cabem (piso de alvo/nocional) vão no WSP e o resto em SPXR11 (ETF quanto do Itaú, 0,25% a.a., B3 desde
12/2024; proxy antes = CDI + S&P - T-bill - 1,5% a.a., ver gl_hedge_cdi). Com R$ 20 mil e 1x, nunca cabe 1 WSP (só SPXR11);
com R$ 50 mil cabe 1 contrato quando o alvo passa de ~2x.

Dados: ajuste diário do WSP no boletim BVBG.086 (B3), 2023-2026, contrato mais negociado da véspera (sem salto de rolagem);
antes de 2023, futuro sintético = SPY (retorno total) - T-bill (validação contra o WSP real no caderno). P&L em R$ = Δpontos x 2,5 x PTAX.
Custos WSP: R$ 2,50 por contrato por lado (emolumentos + meio tick de 0,25 pt) + rolagem trimestral (2 lados). Margem ~15% do
nocional em Tesouro Selic (rende CDI: o excesso é só o ajuste). IR: futuros 15% (futuros_b3), SPXR11 15% (etf_b3).
INICIO 2013-01-01, CORTE 2021-01-01 (OOS 2021-22 ainda com futuro sintético; real desde 2023).
"""
import numpy as np
import pandas as pd

import gl_comum as G
from gl_cripto_premio import bit_continuo as _continuo   # mesmo método: contrato mais negociado da véspera

NOME = "S&P 500 via WSP (B3) + SPXR11, tendência e vol-alvo, sem remessa"
TESE = "Comprado em S&P pelo micro futuro da B3 (margem no Tesouro Selic) quando a tendência e o risco global deixam; resto em SPXR11"
BENCHMARK = "CDI"
INICIO, CORTE = "2013-01-01", "2021-01-01"
REGIME = "nenhum"                  # no IS: nenhum (IR 0,60) > risco_global (0,47); a tendência já tira o fundo das quedas longas
CUSTO_TROCA = .001
PARAMS = {"ma": 200, "vol_alvo": .20}                 # maior IR dentro da amostra
GRADE = {"ma": [100, 200], "vol_alvo": [.10, .15, .20]}
VIZINHANCA = {"ma": (150, 250), "vol_alvo": (.15, .25)}
MULT, CUSTO_CT, TETO = 2.5, 2.5, 2.0
FEE_SPXR, BASE_QUANTO = .0025, .015
INSTRUMENTOS = {"WSP": {"onde": "B3 (futuro)", "ticker": "WSP", "lote": "1 contrato = US$ 2,50 x S&P (~R$ 100 mil)", "custo": "R$ 2,50/lado"},
                "SPXR11": {"onde": "B3", "ticker": "SPXR11", "lote": 1, "custo": "meio spread + 0,03%"}}
APLICAVEL = True
MOTIVO = ("Aplicável, mas com R$ 20 mil o WSP (≈ R$ 100 mil de nocional) não cabe a 1x: a exposição vai toda para o SPXR11; "
          "com R$ 50 mil, 1 WSP entra quando o alvo passa de ~2x (alavancagem 2x).")
ALAVANCAGENS = [1, 2, 5]
MOTIVO_ALAV = "2x e 5x são viáveis via WSP com margem ~15% em Tesouro Selic; com R$ 20 mil, 5x = 1 WSP (pior queda grande)."


def carrega():
    f = G.ler("futuros_b3.parquet")
    b = G.ler("b3_etf_bdr.parquet")
    return {"wsp": f[f.ticker.str.startswith("WSP")], "spxr": b[b.ticker == "SPXR11"], "us": G.ler("us_etf_ajustado.parquet")[["SPY"]]}


def _series(d):
    spy = G.no_calendario(d["us"]["SPY"])
    r_sint = (spy.pct_change(fill_method=None) - G.TB).fillna(0)             # futuro "justo": S&P total - T-bill
    nivel_sint = G.no_calendario(G.C._US["sp500"])                          # pontos = nível do S&P 500 (para o nocional)
    r_real, nivel_real = _continuo(d["wsp"]) if len(d["wsp"]) else (pd.Series(np.nan, index=G.DIAS),) * 2
    ok = r_real.notna() & nivel_real.notna()
    r = r_real.where(ok, r_sint)
    pts = nivel_real.where(nivel_real.notna(), nivel_sint)
    # SPXR11 real desde a listagem; antes, quanto sintético
    b = d["spxr"]
    real = G.pivo(b, "fech", ["SPXR11"])["SPXR11"]
    quanto = (1 + G.CDI.fillna(0) + spy.pct_change(fill_method=None).fillna(0) - G.TB - (FEE_SPXR + BASE_QUANTO) / 252).cumprod()
    niv_etf, ok_etf = G.emenda(real, quanto.where(spy.notna()))
    hs = G.meio_spread(G.pivo(b, "oferta_compra", ["SPXR11"])["SPXR11"], G.pivo(b, "oferta_venda", ["SPXR11"])["SPXR11"],
                       teto=.01).where(ok_etf, .002) + G.B3_EMOL
    return r, pts, niv_etf, hs, spy


def _alvo(d, ma, vol_alvo):
    r, pts, niv_etf, hs, spy = _series(d)
    tend = G.tendencia(spy, ma)
    vol = r.rolling(63, min_periods=40).std() * np.sqrt(252)
    return G.mensal((tend * (vol_alvo / vol).clip(upper=TETO)).fillna(0).to_frame("w"))["w"], r, pts, niv_etf, hs   # rebalanceio mensal


def _simula(d, ma, vol_alvo, capital, custo_mult=1, lag=0, regime=REGIME, alav=1.0):
    w, r, pts, niv_etf, hs = _alvo(d, ma, vol_alvo)
    if regime == "risco_global":                             # regime de mercado aplicado nos PESOS (decisão t-1, como comum.aplica_regime)
        s = G.C.regime_risco_global().reindex(G.DIAS).ffill().fillna(1.0).shift(1).fillna(1.0)
        w = w * s
    w = w * alav
    fx = G.PTAX.values
    noc1 = (pts * MULT * G.PTAX).values
    wt = w.shift(1 + lag).fillna(0).values
    rv = r.fillna(0).values
    T = len(G.DIAS)
    n = np.zeros(T)
    pnl_f, cus_f = np.zeros(T), np.zeros(T)
    trim = pd.Series(G.DIAS.to_period("Q"), index=G.DIAS)
    rola = (trim != trim.shift(-1)).values                      # último pregão do trimestre: rola (2 lados)
    for i in range(1, T):
        pnl_f[i] = n[i - 1] * noc1[i - 1] * rv[i] if noc1[i - 1] == noc1[i - 1] else 0
        x = wt[i] * capital / noc1[i] if noc1[i] > 0 else 0
        k = n[i - 1] if (n[i - 1] > 0 and n[i - 1] - .2 <= x < n[i - 1] + 1.2) else np.floor(x)   # histerese: não fica entrando e saindo
        n[i] = k
        cus_f[i] = (abs(k - n[i - 1]) + (2 * k if rola[i] else 0)) * CUSTO_CT * custo_mult
    resto = pd.Series(wt * capital - n * np.nan_to_num(noc1), index=G.DIAS).clip(lower=0) / capital
    W = pd.DataFrame({"SPXR11": resto}).shift(-1 - lag).fillna(0)      # executa() aplica o atraso de novo
    ex = G.executa(W, niv_etf.to_frame("SPXR11"), capital, hs.to_frame("SPXR11"), lag=lag, custo_mult=custo_mult)
    s = lambda a: pd.Series(a, index=G.DIAS)
    return s(pnl_f), s(cus_f), ex, s(n), w


def excesso(d, capital=20000, custo_mult=1, lag=0, regime=REGIME, alavancagem=1, **params):
    p = {**PARAMS, **params}
    pf_, cf, ex, _, _ = _simula(d, p["ma"], p["vol_alvo"], capital, custo_mult, lag, regime, alavancagem)
    e = (pf_ - cf) / capital + G.excesso_de(ex, capital)
    return e if regime in ("risco_global", "nenhum", None) else G.C.aplica_regime(e, regime, CUSTO_TROCA * custo_mult)


def classes_ir(d, capital=20000, **params):
    p = {**PARAMS, **params}
    pf_, cf, ex, _, _ = _simula(d, p["ma"], p["vol_alvo"], capital)
    return {"futuros_b3": pf_ - cf, "etf_b3": G.pnl_classe(ex)}


def posicoes(d, capital=20000, **params):
    p = {**PARAMS, **params}
    w, r, _, _, _ = _alvo(d, p["ma"], p["vol_alvo"])
    return w.to_frame("S&P"), r.fillna(0).to_frame("S&P")


def negocios(d, capital=20000, **params):
    p = {**PARAMS, **params}
    pf_, cf, ex, n, w = _simula(d, p["ma"], p["vol_alvo"], capital)
    pos = pd.DataFrame({"WSP": n, "SPXR11": ex["n"]["SPXR11"]})
    c = pd.DataFrame({"WSP": (pf_ - cf) / capital, "SPXR11": G.contrib_ativo(ex, capital)["SPXR11"]})
    r, pts, niv_etf, _, _ = _series(d)
    preco = pd.DataFrame({"WSP": (1 + r.fillna(0)).cumprod(), "SPXR11": niv_etf})
    return G.negocios_de(pos, c, preco)


def valida(d):
    """WSP real (2023+) contra o futuro sintético (SPY - T-bill): correlação diária/semanal e retorno a.a."""
    spy = G.no_calendario(d["us"]["SPY"])
    r_sint = (spy.pct_change(fill_method=None) - G.TB)
    r_real, _ = _continuo(d["wsp"])
    x = pd.DataFrame({"real": r_real, "sint": r_sint}).dropna()
    w = x.resample("W-FRI").apply(lambda s: (1 + s).prod() - 1)
    return {"corr diária": x.corr().iloc[0, 1], "corr semanal": w.corr().iloc[0, 1], "real a.a. %": G.C.anual(x["real"]),
            "sintético a.a. %": G.C.anual(x["sint"]), "dias": len(x)}
