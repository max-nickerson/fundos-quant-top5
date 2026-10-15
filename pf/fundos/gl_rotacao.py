"""
Rotação de ETFs globais da B3 (em R$, sem remessa) com tendência e caixa em CDI.

Tese de mesa: o investidor brasileiro só deveria carregar risco lá fora quando ele PAGA mais que o CDI. Todo mês, entre ETFs da B3 que
dão S&P (IVVB11), Nasdaq (NASD11), China (XINA11), Europa (EURP11), mundo (ACWI11), ouro (GOLD11), prata (BSLV39) e cripto (HASH11),
compro os k que mais subiram em R$ nos últimos `janela` pregões, SÓ se o retorno em R$ superou o CDI do mesmo período (momento
absoluto) e o preço está acima da média de 200 dias; o resto fica no Tesouro Selic. Os negócios que pagam: ciclos longos de dólar forte
+ bolsa americana (2019-2021, 2024), ouro em alta com juro real caindo (2019-20, 2024-25) e as ondas do bitcoin (2020-21, 2023-24).
O que mata: virar do avesso em V (mar/2020, 2022) e o hurdle alto do CDI de 2022-2025.

Dados: preço de fechamento da B3 a partir do 20º pregão de cada ETF; antes da listagem, proxy = ETF dos EUA (Yahoo, ajustado) x PTAX
(HASH11 antes de 2021 = BTC-BRL do Mercado Bitcoin, 00h UTC). EURP11 foi deslistado em 12/2024 (sai do universo: posição liquidada).
Custo: meio spread do fechamento (mediana móvel, teto 1%) + emolumentos 0,03%; proxy pré-listagem paga 0,3% (BTC no MB: 1%). Lote 1 cota.
IR: ETF de renda variável na B3 = 15% sobre o ganho, sem isenção de R$ 20 mil (classe etf_b3); BDR (BSLV39) = 15% (classe acoes, sem
isenção para BDR). Corte OOS 2021-01-01 (dados desde 2012, com proxy).
"""
import numpy as np
import pandas as pd

import gl_comum as G

NOME = "Rotação de ETFs globais da B3 (tendência, caixa em CDI)"
TESE = "Compro os ETFs globais da B3 que mais subiram em R$ e bateram o CDI; senão fico no Tesouro Selic"
BENCHMARK = "CDI"
INICIO, CORTE = "2013-01-01", "2021-01-01"
REGIME = "nenhum"
CUSTO_TROCA = .002
PARAMS = {"janela": 126, "k": 2, "ma": 200}               # maior IR dentro da amostra (gl_escolhe.py)
GRADE = {"janela": [126, 252], "k": [2, 3], "ma": [100, 200]}
VIZINHANCA = {"janela": (90, 180), "ma": (150, 250)}
CLASSE_IR = "etf_b3"

UNIVERSO = {"IVVB11": "SPY", "NASD11": "QQQ", "XINA11": "MCHI", "EURP11": "IEUR", "ACWI11": "ACWI", "GOLD11": "GLD",
            "BSLV39": "SLV", "HASH11": "BTC"}
FIM_NEGOCIACAO = {"EURP11": "2024-12-19"}                     # deslistado (último pregão no COTAHIST)
INSTRUMENTOS = {t: {"onde": "B3 (Clear/Rico/XP/Inter)", "ticker": t, "lote": 1, "custo": "meio spread + 0,03%"} for t in UNIVERSO}
APLICAVEL = True
MOTIVO = "Tudo na B3, cotas inteiras de R$ 10-450; com R$ 20 mil cabem 2-3 ETFs sem distorção relevante."
ALAVANCAGENS = [1]
MOTIVO_ALAV = "ETF à vista; alavancar exigiria termo/margem de ações (custo ~CDI+3%) ou opções — não compensa para uma rotação."


def carrega():
    b = G.ler("b3_etf_bdr.parquet")
    b = b[b.ticker.isin(UNIVERSO)]
    c = G.ler("cripto_br.parquet")
    btc = c[(c.fonte == "MB") & (c.sym == "BTC-BRL") & (c.res == "1d")].set_index("data").fech
    btc.index = btc.index + pd.Timedelta(days=1)              # candle diário fecha 00h UTC do dia seguinte (21h de Brasília)
    return {"b3": b, "us": G.ler("us_etf_ajustado.parquet"), "btc_brl": btc}


def _precos(d):
    b = d["b3"]
    fech = G.pivo(b, "fech")
    neg = G.pivo(b, "negocios").fillna(0) > 0
    bid, ask = G.pivo(b, "oferta_compra"), G.pivo(b, "oferta_venda")
    us = d["us"]
    ptax = G.PTAX
    niv, ok, cus = {}, {}, {}
    for t, u in UNIVERSO.items():
        proxy = G.no_calendario(d["btc_brl"]) if u == "BTC" else G.no_calendario(us[u]) * ptax
        real = fech[t] if t in fech else pd.Series(np.nan, index=G.DIAS)
        if t in FIM_NEGOCIACAO:
            real = real[real.index <= FIM_NEGOCIACAO[t]].reindex(G.DIAS)
            proxy = proxy.where(proxy.index <= FIM_NEGOCIACAO[t])
        niv[t], ok[t] = G.emenda(real, proxy)
        hs = G.meio_spread(bid.get(t, real * np.nan), ask.get(t, real * np.nan), teto=.01) if t in bid else real * np.nan
        pre = .01 if u == "BTC" else .003                      # BTC no Mercado Bitcoin antes de 2021: ~1% (taxa + spread)
        cus[t] = hs.where(ok[t], pre).fillna(pre) + G.B3_EMOL
        neg_t = neg[t] if t in neg else pd.Series(False, index=G.DIAS)
        ok[t] = neg_t.where(ok[t], niv[t].notna())             # negociável: real com negócio no dia, ou proxy existente
    return pd.DataFrame(niv), pd.DataFrame(ok), pd.DataFrame(cus)


def _pesos(d, janela, k, ma):
    Pn, ok, _ = _precos(d)
    cdi_acum = (1 + G.CDI.fillna(0)).cumprod()
    mom = Pn / Pn.shift(janela) - 1
    hurdle = cdi_acum / cdi_acum.shift(janela) - 1
    tend = G.tendencia(Pn, ma)
    ele = mom.gt(hurdle, axis=0) & (tend > 0)
    rank = mom.where(ele).rank(axis=1, ascending=False)
    sel = (rank <= k).astype(float)
    vol = np.log(Pn).diff().rolling(63, min_periods=40).std()
    iv = (1 / vol).where(sel > 0)
    W = iv.div(iv.sum(axis=1), axis=0).fillna(0) * sel.sum(axis=1).clip(upper=k).div(k, axis=0).values[:, None]
    W = W.where(Pn.notna(), 0)
    for t, fim in FIM_NEGOCIACAO.items():                     # sai antes da deslistagem
        W.loc[W.index >= pd.Timestamp(fim) - pd.Timedelta(days=10), t] = 0
    return G.mensal(W), Pn, ok


def _roda(d, capital, custo_mult, lag, janela, k, ma):
    W, Pn, ok = _pesos(d, janela, k, ma)
    _, _, cus = _precos(d)
    ex = G.executa(W, Pn, capital, cus, lag=lag, custo_mult=custo_mult, negocia=ok)
    return ex, W, Pn


def excesso(d, capital=20000, custo_mult=1, lag=0, regime=REGIME, alavancagem=1, **params):
    p = {**PARAMS, **params}
    ex, _, _ = _roda(d, capital / alavancagem if alavancagem else capital, custo_mult, lag, p["janela"], p["k"], p["ma"])
    e = G.excesso_de(ex, capital / alavancagem) * alavancagem
    return G.C.aplica_regime(e, regime, CUSTO_TROCA * custo_mult)


def classes_ir(d, capital=20000, **params):
    p = {**PARAMS, **params}
    ex, _, _ = _roda(d, capital, 1, 0, p["janela"], p["k"], p["ma"])
    m = ex["pnl"] - ex["custo"] - ex["aluguel"]
    return {"etf_b3": m.drop(columns=["BSLV39"]).sum(axis=1), "acoes": m["BSLV39"]}


def posicoes(d, capital=20000, **params):
    p = {**PARAMS, **params}
    W, Pn, _ = _pesos(d, p["janela"], p["k"], p["ma"])
    return W, Pn.pct_change(fill_method=None).fillna(0).sub(G.CDI, axis=0)


def negocios(d, capital=20000, **params):
    p = {**PARAMS, **params}
    ex, _, Pn = _roda(d, capital, 1, 0, p["janela"], p["k"], p["ma"])
    return G.negocios_de(ex["n"], G.contrib_ativo(ex, capital), Pn)
