"""
AUDITORIA (pf/pesquisa/auditoria_pf.md) de b3_ofertas_varejo.py — mesmo contrato, duas correções de realismo:
  1) rateio do varejo nas ofertas ICVM 400 que estrearam em alta: 15% do pedido (e não 30%). Nas ofertas quentes de 2020–21 a pessoa
     física sem lock-up recebeu tipicamente 5–20% do pedido (anúncios de encerramento/rateio); o original usava 30%;
  2) custo do pedido bloqueado: a corretora bloqueia o PEDIDO inteiro (não só a alocação) entre a reserva e a liquidação (~5 pregões)
     em TODA oferta pedida -> CDI perdido sobre min(pedido, 25% do capital) x 5 pregões por oferta.
"""
import numpy as np
import pandas as pd

import b3_ofertas_varejo as O
from b3_ofertas_varejo import (B, C, pf, TESE, BENCHMARK, INICIO, CORTE, REGIME, CUSTO_TROCA, GRADE, VIZINHANCA, INSTRUMENTOS,  # noqa: F401
                               APLICAVEL, MOTIVO, ALAVANCAGENS, MOTIVO_ALAV, carrega)

NOME = "Ofertas de ações pela tranche de varejo (PF) — AUDITADA (rateio 15% + pedido bloqueado)"
PARAMS = {**O.PARAMS, "rateio": .15}
DIAS_BLOQ = 5


def _bloqueio(d, capital, pedido):
    """CDI perdido (R$/dia) pelo pedido bloqueado nos DIAS_BLOQ pregões antes do 1º pregão de cada oferta pedida."""
    x = min(pedido * capital / 20000, .25 * capital)
    out = pd.Series(0.0, index=B.DIAS)
    cdi = C.CDI.reindex(B.DIAS).fillna(0)
    for dt in d["ofertas"].data:
        i = B.DIAS.searchsorted(dt)
        sl = slice(max(i - DIAS_BLOQ, 0), i)
        out.iloc[sl] += x * cdi.iloc[sl].values
    return out


def excesso(d, capital=20000, custo_mult=1, lag=0, regime=REGIME, alavancagem=1, **params):
    p = {**PARAMS, **params}
    e = O.roda(d, capital, custo_mult, lag, **p)["e"] * alavancagem - _bloqueio(d, capital, p["pedido"]) / capital
    return C.aplica_regime(e, regime, CUSTO_TROCA * custo_mult)


def classes_ir(d, capital=20000, **params):
    p = {**PARAMS, **params}
    cls = B.classes_acoes(O.roda(d, capital, **p))
    cls["_cdi_perdido"] = cls.get("_cdi_perdido", 0) + _bloqueio(d, capital, p["pedido"])
    return cls


def posicoes(d, capital=20000, **params):
    return O.posicoes(d, capital, **{**PARAMS, **params})


def negocios(d, capital=20000, **params):
    return O.negocios(d, capital, **{**PARAMS, **params})
