"""
Micro Euro STOXX 50 (FSXE, Eurex) no pânico europeu — conta em dólar v2 (pf.conta_usd). Sinal e contratos IDÊNTICOS a fu_eurex_micro.py
(compra 1 FSXE depois de queda de k desvios em 5 dias com o V2X no decil de cima de 1 ano; segura H dias).

O que muda: a margem MORA na IBKR (saldo em US$ comprando SGOV; a margem da Eurex em EUR é coberta pela conta multimoeda — premissa:
o saldo fica em US$/SGOV e a IBKR empresta EUR contra ele; o custo de converter só o P&L em EUR é desprezível), só a 1ª remessa paga IOF
e o saldo pode ser hedgeado com WDO. Sleeve "margem" = R$ 5 mil (margem ~8% de 1 FSXE ≈ R$ 3 mil, folga ~1,6x). Se a margem exigida
passar de 90% do saldo do 1º pregão do mês, corta contratos até caber (sem look-ahead). 50k: R$ 7,5 mil (até 2 FSXE em 2021, SX5E ~3.500).
P&L de 1 contrato: (SX5E + 3% a.a. de dividendos − juro do BCE) x nocional (fu_comum), convertido para US$ pela PTAX/EURUSD do dia.
IR: dict da conta_usd ('exterior' 15% ao ano; 'futuros_b3' = hedge WDO 15% mensal; 'cdi_perdido').
"""
import importlib.util
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _util as U  # noqa: E402
import _v2_comum as V2  # noqa: E402
import fu_comum as F  # noqa: E402

C, pf = U.C, U.pf
_spec = importlib.util.spec_from_file_location("_fu_eurex_micro_base", Path(__file__).resolve().parent / "fu_eurex_micro.py")
B = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(B)

CONTA_USD_V2 = True
NOME = "Micro Euro STOXX 50 no pânico — conta em dólar v2 (só a margem fora, SGOV, hedge WDO)"
TESE = B.TESE + "; a margem mora na IBKR em SGOV e o saldo é hedgeado com WDO"
BENCHMARK, INICIO, CORTE, REGIME, CUSTO_TROCA = "CDI", B.INICIO, B.CORTE, B.REGIME, 0.0
PARAMS, GRADE, VIZINHANCA = dict(B.PARAMS), dict(B.GRADE), dict(B.VIZINHANCA)
INSTRUMENTOS = B.INSTRUMENTOS + [("B3", "WDO (hedge do saldo)", "US$ 10 mil", "R$ 6/mês por contrato")]
APLICAVEL, MOTIVO = True, B.MOTIVO
ALAVANCAGENS, MOTIVO_ALAV = B.ALAVANCAGENS, B.MOTIVO_ALAV
LANCAMENTO = B.LANCAMENTO
SLEEVES = V2.SLEEVES
SLEEVE_MARGEM = {20000: 5000, 50000: 7500}
FOLGA_MARGEM = .9


def carrega():
    return B.carrega()


def _N(d, capital, regime, alavancagem, params):
    p = {**PARAMS, **params}
    regime = p.pop("regime", regime)
    N, Kd = B.gera(d, capital=capital, regime=regime, alavancagem=alavancagem, **p)
    N = N.copy().fillna(0)
    N[N.index < pd.Timestamp(INICIO)] = 0
    for a in N.columns:
        if a in LANCAMENTO:
            N.loc[(N.index >= pd.Timestamp(CORTE)) & (N.index < pd.Timestamp(LANCAMENTO[a])), a] = 0
    return N, Kd


def livro_usd(d, capital, sleeve_brl, custo_mult=1, lag=0, regime=REGIME, alavancagem=1, **params):
    N, Kd = _N(d, capital, regime, alavancagem, params)
    idx = N.index
    usd = F.nivel(F.PTAX_FULL, idx)                                     # R$ por US$
    mg = sum(N[a].abs() * Kd[a]["margem"].reindex(idx).ffill().fillna(0) for a in N.columns) / usd
    fator = (FOLGA_MARGEM * V2.usd_conta_mes(sleeve_brl, idx) / mg.where(mg > 0)).clip(upper=1).fillna(1)
    N = np.trunc(N.mul(fator, axis=0))                                  # corta contratos (inteiros) até a margem caber
    Nx = N.shift(1 + lag).fillna(0)
    pnl = pd.Series(0.0, index=idx)
    por = {}
    for a in N.columns:
        k = Kd[a].reindex(idx)
        pa = Nx[a].shift(1).fillna(0) * k["pc"].fillna(0)
        giro = Nx[a].diff().abs().fillna(Nx[a].abs()) + Nx[a].abs() * k["rol"].fillna(0) * 2 / 252
        ca = giro * k["custo"].ffill().fillna(0) * custo_mult
        por[a] = pa - ca                                                 # R$
        pnl += (pa - ca) / usd
    return pnl, Nx, por, Kd


def _roda(d, capital, sleeve_brl, hedge, custo_mult, lag, regime, alavancagem, params):
    sl = V2.sleeve(capital, sleeve_brl)
    pnl, Nx, por, Kd = livro_usd(d, capital, sl, custo_mult, lag, regime, alavancagem, **params)
    ex, cls = V2.fecha(pnl, sl, capital, hedge, custo_mult)
    return ex, cls, Nx, por, Kd


def excesso(d, capital=20000, custo_mult=1, lag=0, regime=REGIME, alavancagem=1, sleeve_brl=None, hedge="inteiro", **params):
    return _roda(d, capital, sleeve_brl, hedge, custo_mult, lag, regime, alavancagem, params)[0]


def classes_ir(d, capital=20000, regime=REGIME, alavancagem=1, sleeve_brl=None, hedge="inteiro", **params):
    return _roda(d, capital, sleeve_brl, hedge, 1, 0, regime, alavancagem, params)[1]


def posicoes(d, capital=20000, **params):
    N, Kd = _N(d, capital, REGIME, 1, params)
    return F.posicoes_de(N, Kd, capital)


def negocios(d, capital=20000, sleeve_brl=None, hedge="inteiro", **params):
    ex, cls, Nx, por, Kd = _roda(d, capital, sleeve_brl, hedge, 1, 0, REGIME, 1, params)
    return F.negocios_de({"Nx": Nx, "por_ativo": por}, Kd, capital)
