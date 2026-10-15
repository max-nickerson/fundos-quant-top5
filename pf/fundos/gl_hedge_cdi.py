"""
S&P e crédito americano pela B3 SEM pagar o carrego do dólar: ETF com hedge para CDI (SPXR11/HYBR11) e dólar só quando ele está subindo.

Tese de mesa: quem compra IVVB11 compra duas coisas — o prêmio da bolsa americana (S&P - T-bill) e o dólar contra o real. O dólar à vista,
com CDI de 10-15% e T-bill de 0-5%, custa ~8 pp a.a. de carrego; só compensa quando o real está se desvalorizando (crise, fiscal, eleição).
O fundo carrega o prêmio de ações (e o spread de high yield) "por cima do CDI" via ETF quanto/hedgeado e só troca para o IVVB11 (dólar
aberto) quando o dólar está acima da sua média de `ma_fx` pregões (o hedge vira hedge de cauda do Brasil). Bolsa americana abaixo da média
de `ma` pregões: Tesouro Selic. HY (HYBR11, 70% HY EUA + 30% soberano BR com hedge em mini dólar) só com crédito em tendência (HYG/IEF).

Instrumentos e proxies:
  - SPXR11 (It Now S&P 500 Futures Quanto BRL, Itaú, 0,25% a.a., B3 desde 19/12/2024): proxy antes = CDI + (SPY - T-bill) - 0,25% a.a.
    - 1,5% a.a. de base/rolagem do futuro quanto (com 0,5% o proxy rendia 1,2 pp a.a. a mais que o SPXR11 real em 2025-26;
    correlação semanal 0,99 — valida_proxy()).
  - HYBR11 (Nu, 0,30% a.a., desde 17/09/2025 — NÃO está no COTAHIST local): proxy o período todo = CDI + (HYG - T-bill) - 0,30% - 1,5%;
    custo de negociação 0,5% por lado (ETF pequeno, PL ~R$ 15 mi). Resultado da perna de HY é teórico.
  - IVVB11 (S&P sem hedge, desde 2014). Antes disso, SPY x PTAX.
Custos: meio spread do fechamento (mediana móvel, teto 1%) + 0,03%. IR: ETF na B3 15% (classe etf_b3; ETF de renda fixa como HYBR11
paga 15% na venda, sem come-cotas). Corte OOS 2021-01-01.
"""
import numpy as np
import pandas as pd

import gl_comum as G

NOME = "S&P/HY com hedge para CDI na B3 (dólar só em tendência)"
TESE = "Carrego o prêmio da bolsa e do HY americano por cima do CDI via ETF quanto; dólar aberto (IVVB11) só quando ele sobe"
BENCHMARK = "CDI"
INICIO, CORTE = "2013-01-01", "2021-01-01"
REGIME = "nenhum"
CUSTO_TROCA = .002
PARAMS = {"ma": 200, "ma_fx": 126, "hy": 0.0}
GRADE = {"ma": [100, 200], "ma_fx": [63, 126], "hy": [0.0, 0.5]}
VIZINHANCA = {"ma": (150, 250), "ma_fx": (80, 170)}
FEE = {"SPXR11": .0025, "HYBR11": .003}
BASE_QUANTO = .015                       # base/rolagem do hedge (a.a.): calibrado no desvio do proxy vs SPXR11 real (12/2024-10/2026)
INSTRUMENTOS = {"SPXR11": {"onde": "B3", "ticker": "SPXR11", "lote": 1, "custo": "meio spread + 0,03%"},
                "IVVB11": {"onde": "B3", "ticker": "IVVB11", "lote": 1, "custo": "meio spread + 0,03%"},
                "HYBR11": {"onde": "B3", "ticker": "HYBR11", "lote": 1, "custo": "0,5% (estimado)"}}
APLICAVEL = True
MOTIVO = "Tudo na B3 em cotas de R$ 10-450; SPXR11 tem R$ ~10 mi/dia. HYBR11 existe mas é pequeno (perna de HY teórica)."
ALAVANCAGENS = [1]
MOTIVO_ALAV = "Alavancagem barata do mesmo risco é o WSP (fundo gl_wsp); aqui fica 1x."


def carrega():
    b = G.ler("b3_etf_bdr.parquet")
    return {"b3": b[b.ticker.isin(["SPXR11", "IVVB11", "SPXH11"])], "us": G.ler("us_etf_ajustado.parquet")}


def _precos(d):
    b = d["b3"]
    tk = ["SPXR11", "IVVB11"]
    fech, neg = G.pivo(b, "fech", tk), G.pivo(b, "negocios", tk).fillna(0) > 0
    bid, ask = G.pivo(b, "oferta_compra", tk), G.pivo(b, "oferta_venda", tk)
    us = d["us"]
    r_spy = G.no_calendario(us["SPY"]).pct_change(fill_method=None).fillna(0)
    r_hyg = G.no_calendario(us["HYG"]).pct_change(fill_method=None).fillna(0)
    cdi, tb = G.CDI.fillna(0), G.TB
    quanto = lambda r, fee: (1 + cdi + r - tb - (fee + BASE_QUANTO) / 252).cumprod().where(r.index >= r.ne(0).idxmax())
    niv, ok, cus = {}, {}, {}
    niv["SPXR11"], ok["SPXR11"] = G.emenda(fech["SPXR11"], quanto(r_spy, FEE["SPXR11"]))
    niv["IVVB11"], ok["IVVB11"] = G.emenda(fech["IVVB11"], G.no_calendario(us["SPY"]) * G.PTAX)
    niv["HYBR11"], ok["HYBR11"] = quanto(r_hyg, FEE["HYBR11"]), pd.Series(False, index=G.DIAS)
    for t in ("SPXR11", "IVVB11"):
        cus[t] = G.meio_spread(bid[t], ask[t], teto=.01).where(ok[t], .002).fillna(.002) + G.B3_EMOL
        ok[t] = neg[t].where(ok[t], True)
    cus["HYBR11"], ok["HYBR11"] = pd.Series(.005, index=G.DIAS), niv["HYBR11"].notna()
    return pd.DataFrame(niv), pd.DataFrame(ok), pd.DataFrame(cus), us


def _pesos(d, ma, ma_fx, hy):
    Pn, ok, cus, us = _precos(d)
    spx = G.no_calendario(us["SPY"])
    acoes = G.tendencia(spx, ma)
    dolar = G.tendencia(G.PTAX, ma_fx)
    q = np.log(G.no_calendario(us["HYG"]) / G.no_calendario(us["IEF"]))
    credito = G.tendencia(np.exp(q), 100)
    w_eq = 1 - hy
    W = pd.DataFrame(0.0, index=G.DIAS, columns=Pn.columns)
    W["IVVB11"] = w_eq * acoes * dolar
    W["SPXR11"] = w_eq * acoes * (1 - dolar)
    W["HYBR11"] = hy * credito
    return G.mensal(W.where(Pn.notna(), 0)), Pn, ok, cus


def _roda(d, capital, custo_mult, lag, ma, ma_fx, hy):
    W, Pn, ok, cus = _pesos(d, ma, ma_fx, hy)
    return G.executa(W, Pn, capital, cus, lag=lag, custo_mult=custo_mult, negocia=ok), W, Pn


def excesso(d, capital=20000, custo_mult=1, lag=0, regime=REGIME, alavancagem=1, **params):
    p = {**PARAMS, **params}
    ex, _, _ = _roda(d, capital, custo_mult, lag, p["ma"], p["ma_fx"], p["hy"])
    return G.C.aplica_regime(G.excesso_de(ex, capital), regime, CUSTO_TROCA * custo_mult)


def classes_ir(d, capital=20000, **params):
    p = {**PARAMS, **params}
    ex, _, _ = _roda(d, capital, 1, 0, p["ma"], p["ma_fx"], p["hy"])
    return {"etf_b3": G.pnl_classe(ex)}


def posicoes(d, capital=20000, **params):
    p = {**PARAMS, **params}
    W, Pn, _, _ = _pesos(d, p["ma"], p["ma_fx"], p["hy"])
    return W, Pn.pct_change(fill_method=None).fillna(0).sub(G.CDI, axis=0)


def negocios(d, capital=20000, **params):
    p = {**PARAMS, **params}
    ex, _, Pn = _roda(d, capital, 1, 0, p["ma"], p["ma_fx"], p["hy"])
    return G.negocios_de(ex["n"], G.contrib_ativo(ex, capital), Pn)


def valida_proxy(d):
    """Desvio do proxy quanto contra o SPXR11 real (desde a listagem): correlação diária e diferença de retorno a.a."""
    b = d["b3"]
    real = G.pivo(b, "fech")["SPXR11"]
    us = d["us"]
    r_spy = G.no_calendario(us["SPY"]).pct_change(fill_method=None).fillna(0)
    prox = G.CDI.fillna(0) + r_spy - G.TB - (FEE["SPXR11"] + BASE_QUANTO) / 252
    rr = real.pct_change(fill_method=None)
    x = pd.DataFrame({"real": rr, "proxy": prox}).dropna().iloc[20:]
    w = x.resample("W-FRI").apply(lambda s: (1 + s).prod() - 1)
    return {"corr diária": x.corr().iloc[0, 1], "corr semanal": w.corr().iloc[0, 1],
            "real a.a. %": G.C.anual(x["real"]), "proxy a.a. %": G.C.anual(x["proxy"]), "dias": len(x)}
