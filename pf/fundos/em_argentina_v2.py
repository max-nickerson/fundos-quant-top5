"""
Argentina no pânico v2: mesmo sinal e mesmos custos de IBKR de em_argentina (cesta de YPF/GGAL/BMA/PAM/CEPU após queda > 20% em 21
pregões, 50% do livro, 63 pregões), mas com a CONTA EM DÓLAR v2 (pf.conta_usd): o livro é do tamanho do sleeve que mora na IBKR, o caixa
parado fica em T-bill, só a 1ª remessa paga IOF e o câmbio do sleeve é hedgeado com WDO (contratos inteiros).
Na rodada PF2 os papéis davam +10,9 pp e a conta antiga comia −8,3 (remessa −2,2, câmbio −3,1, CDI perdido −3,0). Beta: ARGT/EEM.
"""
import pandas as pd

import comum as C
import em_comum as E
import em_argentina as O
import pf3a_comum as A

CONTA_USD_V2 = True
NOME = "Argentina no pânico v2: cesta de ADRs (conta em dólar v2)"
TESE = O.TESE + "; sleeve permanente na IBKR em T-bill, câmbio hedgeado com WDO"
BENCHMARK = "CDI"
INICIO, CORTE = O.INICIO, O.CORTE
REGIME = "nenhum"
CUSTO_TROCA = .001
CLASSE_IR = "exterior"
ADRS = O.ADRS
PARAMS = dict(O.PARAMS)
GRADE = dict(O.GRADE)
VIZINHANCA = dict(O.VIZINHANCA)
SLEEVES = A.SLEEVES
INSTRUMENTOS = O.INSTRUMENTOS + " Caixa parado em SGOV/BIL; B3: WDO vendido como hedge do sleeve."
APLICAVEL = True
MOTIVO = "Operável em conta cash: 50% do sleeve na cesta (R$ 2,5–18,75 mil). Sem remessa por negócio."
ALAVANCAGENS = [1, 1.5, 2]
MOTIVO_ALAV = O.MOTIVO_ALAV


def carrega():
    return O.carrega()


_CACHE = {}


def _roda(d, capital, custo_mult, lag, alavancagem, sleeve_brl, hedge, **p):
    sl = A.sleeve_padrao(capital, sleeve_brl)
    k = (id(d), len(d["raw"]), d["raw"].index[-1], capital, custo_mult, lag, alavancagem, sl, hedge, tuple(sorted(p.items())))
    if k in _CACHE:
        return _CACHE[k]
    W, _ = O._pesos(d, **p)
    res = E.livro(d, W, sl, lag, custo_mult, alavancagem, hedge_fx="nenhum")
    usd = A.usd_de_ext(res["classes"]["exterior"], res["cambio"], res["remessa"])
    e, cls = A.conta(usd, sl, capital, hedge, custo_mult)
    out = {"e": e, "classes": cls, "res": res, "usd": usd, "sl": sl}
    if len(_CACHE) > 60:
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
    W, R = E.posicoes_de(o["res"], o["sl"])
    return W * o["sl"] / capital, R


def negocios(d, capital=20000, sleeve_brl=None, hedge="inteiro", **kw):
    o = _roda(d, capital, 1, 0, 1, sleeve_brl, hedge, **_p(kw))
    return A.reescala_negocios(E.negocios_de(o["res"], o["sl"]), o["sl"], capital)
