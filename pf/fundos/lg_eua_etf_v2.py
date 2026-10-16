"""
Noite após queda forte em ETFs dos EUA v2: mesmo sinal e custos de lg_eua_etf (28 ETFs de ações dos EUA; compra no leilão de fechamento
(MOC) quem caiu >= 2% no dia, vende no leilão de abertura (MOO); até 3 noites por dia; comissão IBKR + 1 bp de derrapagem), mas com a
CONTA EM DÓLAR v2 (pf.conta_usd): o sleeve mora na IBKR em T-bill (SGOV) e é hedgeado com WDO; só a 1ª remessa paga IOF.
Tamanho por noite = sleeve x L / n. Conta: girar o mesmo dinheiro toda noite numa conta CASH esbarra na liquidação (o caixa da venda
na abertura só liquida em D+1 -> comprar de novo no fechamento com caixa não liquidado e vender antes da liquidação é "good faith
violation"). Com conta margem (US$ 2 mil, sleeve >= R$ 11 mil) dá para usar o sleeve inteiro; abaixo disso usamos METADE do sleeve por
noite (alternância de caixa liquidado). Juros de margem só acima do sleeve (L > 1): T-bill + 1,5% por noite.
"""
import numpy as np
import pandas as pd

import comum as C
import lg_comum as L
import lg_eua_etf as O
import pf3a_comum as A

CONTA_USD_V2 = True
NOME = "Noite após queda forte — ETFs dos EUA v2 (MOC->MOO, conta em dólar v2)"
TESE = O.TESE + "; sleeve permanente na IBKR em T-bill, câmbio hedgeado com WDO"
BENCHMARK = "CDI"
INICIO, CORTE = O.INICIO, O.CORTE
REGIME = "nenhum"
CUSTO_TROCA = .001
CLASSE_IR = "exterior"
PARAMS = dict(O.PARAMS)
GRADE = dict(O.GRADE)
VIZINHANCA = dict(O.VIZINHANCA)
SLEEVES = A.SLEEVES
INSTRUMENTOS = O.INSTRUMENTOS
APLICAVEL = True
MOTIVO = ("MOC até 15h50 ET e MOO no dia seguinte (à mão ou API IBKR). Sleeve < R$ 11 mil: conta cash, metade do sleeve por noite. "
          "Decide com o preço das 15h50 (o sinal usa o fechamento -> ver t+2).")
ALAVANCAGENS = [1, 1.5, 2]
MOTIVO_ALAV = O.MOTIVO_ALAV + " (exige conta margem: sleeve >= R$ 11 mil)"
_CACHE = {}


def carrega():
    return O.carrega()


def _roda(d, capital, custo_mult, lag, alavancagem, sleeve_brl, hedge, universo, modo, limiar, n):
    sl = A.sleeve_padrao(capital, sleeve_brl)
    k = (id(d), capital, custo_mult, lag, alavancagem, sl, hedge, universo, modo, limiar, n)
    if k in _CACHE and _CACHE[k]["d"] is d:
        return _CACHE[k]
    base = sl if A.tem_margem(sl) else sl * .5
    tick = O.ETF if universo == "etf" else L.lista("sp100")
    g = L.grupo(d, "eua", tick)
    liq = L.adv_usd(g, "USD") >= 1e7
    sc = L.score_queda(g, limiar, modo, liq)
    res = L.noites([{"g": g, "mkt": "US", "score": sc}], base, int(n), lag, custo_mult, alavancagem)
    noc = res["nocional"]
    tb = C.TB_US.dropna()
    tb = tb.reindex(tb.index.union(noc.index)).ffill().reindex(noc.index).fillna(0)
    emprestado = (noc - sl).clip(lower=0)
    juros = L.para_b3(emprestado * (tb * 252 + L.MARGEM_SPREAD) / 360 * custo_mult)
    usd = ((res["pnl"] - juros).reindex(A.DIAS).fillna(0)) / A.PTAX
    e, cls = A.conta(usd, sl, capital, hedge, custo_mult)
    out = {"e": e, "classes": cls, "res": res, "usd": usd, "sl": sl, "base": base, "d": d}
    if len(_CACHE) > 48:
        _CACHE.clear()
    _CACHE[k] = out
    return out


def _p(kw):
    return {**PARAMS, **{k: v for k, v in kw.items() if k in PARAMS}}


def excesso(d, capital=20000, custo_mult=1, lag=0, regime=REGIME, alavancagem=1, sleeve_brl=None, hedge="inteiro", **kw):
    e = _roda(d, capital, custo_mult, lag, alavancagem, sleeve_brl, hedge, **_p(kw))["e"]
    return C.aplica_regime(e, regime, CUSTO_TROCA * custo_mult)


def classes_ir(d, capital=20000, sleeve_brl=None, hedge="inteiro", **kw):
    return _roda(d, capital, 1, 0, 1, sleeve_brl, hedge, **_p(kw))["classes"]


def posicoes(d, capital=20000, sleeve_brl=None, hedge="inteiro", **kw):
    o = _roda(d, capital, 1, 0, 1, sleeve_brl, hedge, **_p(kw))
    return o["res"]["W"] * o["base"] / capital, o["res"]["R"]


def negocios(d, capital=20000, sleeve_brl=None, hedge="inteiro", **kw):
    o = _roda(d, capital, 1, 0, 1, sleeve_brl, hedge, **_p(kw))
    return A.reescala_negocios(o["res"]["negocios"], o["base"], capital)
