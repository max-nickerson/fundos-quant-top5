"""
Carry G10 com micro FX da CME — conta em dólar v2 (pf.conta_usd). Sinal e contratos IDÊNTICOS a cme_carry_g10.py.

O que muda: a margem MORA na IBKR (não volta todo mês com IOF), o caixa parado compra SGOV (T-bill − 0,10%), só a 1ª remessa paga IOF +
spread e o saldo pode ser hedgeado vendendo WDO na B3 (contratos inteiros). Aqui o sleeve que vai para fora é só a MARGEM necessária:
  - margem de 1 par de micros FX ≈ US$ 500–900 (2,5–3,5% de € 12,5 mil/A$ 10 mil/¥ 1,25 mi) — R$ 5 mil (≈ US$ 900) cobre 1 par com
    folga; "margem" = R$ 5 mil (20k) / R$ 5 mil (50k: 1 par, alavancagem 1). Se a margem exigida passar de 90% do saldo do mês, o livro
    é cortado (contratos inteiros) até caber (não opera sem margem — sem look-ahead: usa o saldo do 1º pregão do mês).
  - P&L dos futuros em US$ (excesso do T-bill por construção: spot + diferencial de juros BIS) e custos IBKR em US$ (cme_comum).
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
import cme_comum as K  # noqa: E402

C, pf = U.C, U.pf
_spec = importlib.util.spec_from_file_location("_cme_carry_g10_base", Path(__file__).resolve().parent / "cme_carry_g10.py")
B = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(B)

CONTA_USD_V2 = True
NOME = "Carry G10 micro FX — conta em dólar v2 (só a margem fora, SGOV, hedge WDO)"
TESE = B.TESE + "; a margem mora na IBKR em SGOV e o saldo é hedgeado com WDO"
BENCHMARK, INICIO, CORTE, REGIME, CUSTO_TROCA = "CDI", B.INICIO, B.CORTE, B.REGIME, 0.0
PARAMS, GRADE, VIZINHANCA = dict(B.PARAMS), dict(B.GRADE), dict(B.VIZINHANCA)
MOEDAS = B.MOEDAS
INSTRUMENTOS = B.INSTRUMENTOS + [("B3", "WDO (hedge do saldo)", "US$ 10 mil", "R$ 6/mês por contrato")]
APLICAVEL, MOTIVO = True, B.MOTIVO
ALAVANCAGENS, MOTIVO_ALAV = B.ALAVANCAGENS, B.MOTIVO_ALAV
SLEEVES = V2.SLEEVES
SLEEVE_MARGEM = {20000: 5000, 50000: 5000}
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
        if a in K.LANCAMENTO:
            N.loc[(N.index >= pd.Timestamp(CORTE)) & (N.index < pd.Timestamp(K.LANCAMENTO[a])), a] = 0
    return N, Kd


def livro_usd(d, capital, sleeve_brl, custo_mult=1, lag=0, regime=REGIME, alavancagem=1, **params):
    """P&L diário em US$ (calendário dos EUA) dos micros, já com custos; posição zerada se a margem não cabe no saldo do mês."""
    N, Kd = _N(d, capital, regime, alavancagem, params)
    idx = N.index
    mg = sum(N[a].abs() * Kd[a]["margem"].reindex(idx).ffill().fillna(0) for a in N.columns)
    fator = (FOLGA_MARGEM * V2.usd_conta_mes(sleeve_brl, idx) / mg.where(mg > 0)).clip(upper=1).fillna(1)
    N = np.trunc(N.mul(fator, axis=0))                                  # corta contratos (inteiros) até a margem caber
    Nx = N.shift(1 + lag).fillna(0)
    pnl = pd.Series(0.0, index=idx)
    por = {}
    for a in N.columns:
        k = Kd[a]
        pa = Nx[a].shift(1).fillna(0) * k["pc"].reindex(idx).fillna(0)
        ca = (Nx[a].diff().abs().fillna(Nx[a].abs()) + Nx[a].abs() * K.ESPEC[a]["rol"] * 2 / 252) * K.custo_lado(a) * custo_mult
        por[a] = pa - ca
        pnl += pa - ca
    return pnl, Nx, por, Kd, N


def _roda(d, capital, sleeve_brl, hedge, custo_mult, lag, regime, alavancagem, params):
    sl = V2.sleeve(capital, sleeve_brl)
    pnl, Nx, por, Kd, N = livro_usd(d, capital, sl, custo_mult, lag, regime, alavancagem, **params)
    ex, cls = V2.fecha(pnl, sl, capital, hedge, custo_mult)
    return ex, cls, Nx, por, Kd, N


def excesso(d, capital=20000, custo_mult=1, lag=0, regime=REGIME, alavancagem=1, sleeve_brl=None, hedge="inteiro", **params):
    return _roda(d, capital, sleeve_brl, hedge, custo_mult, lag, regime, alavancagem, params)[0]


def classes_ir(d, capital=20000, regime=REGIME, alavancagem=1, sleeve_brl=None, hedge="inteiro", **params):
    return _roda(d, capital, sleeve_brl, hedge, 1, 0, regime, alavancagem, params)[1]


def posicoes(d, capital=20000, **params):
    N, Kd = _N(d, capital, REGIME, 1, params)
    return K.posicoes_de(N, Kd, capital)


def negocios(d, capital=20000, sleeve_brl=None, hedge="inteiro", **params):
    ex, cls, Nx, por, Kd, N = _roda(d, capital, sleeve_brl, hedge, 1, 0, REGIME, 1, params)
    fx = K.PTAX_FULL.reindex(Nx.index, method="ffill")
    L = {"Nx": Nx, "por_ativo": {a: v * fx for a, v in por.items()}}
    return K.negocios_de(L, Kd, capital)
