"""
Prêmio de volatilidade com beta neutro (SVXY + SH) — conta em dólar v2 (pf.conta_usd). Livro IDÊNTICO a varejo/fundos/variancia_varejo.py
(simulação diária da conta na IBKR: SVXY comprado com frações, hedge de beta com SH comprado — ou SPY vendido em ações inteiras —,
vol-alvo 8% do FUNDO, teto de choque calibrado em fev/2018, regime risco_global do institucional, banda de rebalanceio 50%,
comissão IBKR Pro tiered mín. US$ 0,35, chamada de margem e quebra).

O que muda (conta v2): a conta da IBKR tem o tamanho do SLEEVE (exterior = sleeve/capital), o saldo mora lá (sem a remessa diluída de
ida e volta do varejo), o caixa parado em SGOV e o saldo hedgeado com WDO inteiro (pf.conta_usd). O livro é passado à conta_usd em EXCESSO
DO T-BILL: P&L da conta simulada − T-bill (líquido do SGOV) sobre o patrimônio nominal (a conta_usd devolve esse T-bill sobre o saldo).
Com sleeve < US$ 2.000 a conta é "cash" (sem margem): SVXY + SH tem que caber no saldo — o livro encolhe (o simulador faz isso).
Referência (varejo antigo, 30% fora): −2,1 pp sem hedge, +0,7 pp com hedge teórico.
IR: dict da conta_usd ('exterior' 15% ao ano; 'futuros_b3' = hedge WDO 15% mensal; 'cdi_perdido').
"""
import importlib.util
import sys
from pathlib import Path

import numpy as np
import pandas as pd

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import _util as U  # noqa: E402
import _v2_comum as V2  # noqa: E402

C, pf = U.C, U.pf
for _p in (str(U.RAIZ), str(U.RAIZ / "varejo")):
    if _p not in sys.path:
        sys.path.append(_p)
_spec = importlib.util.spec_from_file_location("_variancia_varejo_base", U.RAIZ / "varejo" / "fundos" / "variancia_varejo.py")
VV = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(VV)

CONTA_USD_V2 = True
NOME = "Prêmio de vol beta neutro (SVXY + SH) — conta em dólar v2 (SGOV, hedge WDO)"
TESE = ("Vende vol do S&P comprando SVXY (−0,5x futuro de VIX de 30 dias) com hedge de beta em SH, vol-alvo 8% e fora no risco global; "
        "o dinheiro mora na IBKR em SGOV, hedgeado com WDO")
BENCHMARK, INICIO, CORTE, REGIME, CUSTO_TROCA = "CDI", VV.INICIO, VV.CORTE, VV.REGIME, 0.0
PARAMS = {"veiculo": "svxy", "teto": .4, "hedge_sp": "sh", "banda": .5}
GRADE = {"veiculo": ["svxy", "svix"], "teto": [.25, .4]}
VIZINHANCA = {"teto": (.25, .5), "banda": (.25, .75)}
INSTRUMENTOS = VV.INSTRUMENTOS + " Hedge cambial: WDO (B3) vendido sobre o saldo da IBKR; caixa lá fora em SGOV."
APLICAVEL = True
MOTIVO = "SVXY e SH com frações na IBKR cabem em qualquer sleeve; VXM/opções XSP não (ver variancia_varejo/rev_variancia)."
ALAVANCAGENS = [1, 1.5, 2]
MOTIVO_ALAV = ("alavancagem multiplica o alvo de vol (SVXY + SH) dentro do MESMO sleeve: acima do saldo exige conta margem (>= US$ 2 mil) "
               "e Reg T; 5x descartado (fev/2018 a 5x = −21% do capital, ver variancia_varejo)")
SLEEVES = V2.SLEEVES
_CACHE = {}


def carrega():
    return VV.carrega()


def _sim(d, capital, sleeve_brl, custo_mult, lag, regime, alavancagem, veiculo, teto, hedge_sp, banda):
    k = (id(d["etf"]), len(d["etf"]), capital, sleeve_brl, custo_mult, lag, regime, alavancagem, veiculo, round(teto, 6), hedge_sp, round(banda, 6))
    if k in _CACHE:
        return _CACHE[k]
    reg = regime if regime in ("risco_global", "nenhum", None) else "nenhum"
    f = sleeve_brl / capital / max(alavancagem, 1)            # o simulador multiplica o "exterior" pela alavancagem: o sleeve fica fixo
    sim = VV._simula(d, veiculo, teto, hedge_sp, f, banda, capital, custo_mult, lag, reg, alavancagem)
    S = VV._series(d, veiculo)
    cal = sim["r_conta"].index
    B = sleeve_brl / VV.V.PTAX.reindex(cal, method="ffill").bfill()
    tb = S["tb"].reindex(cal).fillna(0)
    sim["pnl_usd"] = (sim["r_conta"] - (tb - V2.SGOV / 252)) * B
    if len(_CACHE) > 80:
        _CACHE.clear()
    _CACHE[k] = sim
    return sim


def _roda(d, capital, sleeve_brl, hedge, custo_mult, lag, regime, alavancagem, params):
    p = {**PARAMS, **params}
    sl = V2.sleeve(capital, sleeve_brl)
    sim = _sim(d, capital, sl, custo_mult, lag, regime, alavancagem, p["veiculo"], p["teto"], p["hedge_sp"], p["banda"])
    ex, cls = V2.fecha(sim["pnl_usd"], sl, capital, hedge, custo_mult)
    if regime not in ("risco_global", "nenhum", None):
        ex = C.aplica_regime(ex, regime, .001 * custo_mult)
    return ex, cls, sim


def excesso(d, capital=20000, custo_mult=1, lag=0, regime=REGIME, alavancagem=1, sleeve_brl=None, hedge="inteiro", **params):
    return _roda(d, capital, sleeve_brl, hedge, custo_mult, lag, regime, alavancagem, params)[0]


def classes_ir(d, capital=20000, regime=REGIME, alavancagem=1, sleeve_brl=None, hedge="inteiro", **params):
    return _roda(d, capital, sleeve_brl, hedge, 1, 0, regime, alavancagem, params)[1]


def posicoes(d, capital=20000, **params):
    p = {**PARAMS, **params}
    return VV.posicoes(d, veiculo=p["veiculo"], teto=p["teto"])


def negocios(d, capital=20000, sleeve_brl=None, hedge="inteiro", **params):
    """Um negócio por mês por perna: veículo (vendido em vol) e hedge S&P (SH/SPY), em pp do capital (P&L em R$ pela PTAX)."""
    p = {**PARAMS, **params}
    ex, cls, sim = _roda(d, capital, sleeve_brl, hedge, 1, 0, REGIME, 1, params)
    cal = sim["pnl"].index
    C_usd = capital / VV.V.PTAX.reindex(cal, method="ffill").bfill()
    m = sim["pnl"].mul(C_usd, axis=0)                                             # US$ por perna
    m["hedge S&P"] = m.pop("SH") + m.pop("SPY")
    m = m.mul(VV.V.PTAX.reindex(cal, method="ffill").bfill(), axis=0) / capital   # fração do capital
    m = m.groupby(m.index.to_period("M")).sum()
    lin = []
    for per, row in m.iterrows():
        for a, v in row.items():
            if v != 0:
                lin.append({"ativo": a, "lado": -1 if a == p["veiculo"] else 1, "entrada": per.start_time, "saida": per.end_time.normalize(),
                            "dias": 21, "retorno_%": np.nan, "contrib_pp": v * 100})
    return pd.DataFrame(lin)
