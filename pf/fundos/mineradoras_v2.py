"""
Mineradoras vs metal — conta em dólar v2 (pf.conta_usd). Sinal = institucional auditado (fundos/mineradoras.py, via rev_mineradoras.py):
resíduo "mineradora − beta x metal", z do resíduo acumulado (semanal), entra |z| > z_in, sai na média, stop/prazo, risco igual por par.

Execução (motor de pares PF, pf/fundos/_rev_pares_pf.py, sem alterá-lo):
  - TODAS as pernas na IBKR em ETF/ação (rota padrão "so_etf": GDX/GDXJ/SIL/COPX/FCX/VALE/BHP/RIO x GLD/SLV/CPER); compra com fração,
    VENDA EM AÇÕES INTEIRAS, aluguel do arquivo público de short da IBKR (0,25–0,63% a.a.), comissão US$ 0,0035/ação mín. US$ 0,35,
    Reg T 50% e mínimo de US$ 2.000 de patrimônio para vender a descoberto (par não abre se a conta não tiver isso);
  - tamanho do par pelo risco do FUNDO (vol-alvo 10%/raiz(n) x capital total), mas o dinheiro exigido (Reg T) tem que caber em 95% do
    SLEEVE (no motor: teto de caixa = 0,95 x sleeve / capital) — se não cabe, o par não abre ("não coube");
  - a conta da IBKR do motor (custo_conta_exterior) é DESLIGADA aqui (substituída durante a chamada por zero) e o livro em US$ vai para a
    pf.conta_usd: saldo mora lá em SGOV, só a 1ª remessa paga IOF, hedge com WDO inteiro.
  - P&L em excesso do T-bill: ações compradas ocupam caixa que renderia SGOV -> subtrai T-bill x valor comprado (a venda a descoberto
    não rende juro em conta < US$ 100 mil: o caixa da venda fica parado, conservador).
Variante "auto": perna do ouro em 1OZ (1 oz) quando arredonda para >= 1 contrato.
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
import _rev_pares_pf as PP  # noqa: E402

C, pf = U.C, U.pf
_spec = importlib.util.spec_from_file_location("_rev_mineradoras_base", Path(__file__).resolve().parent / "rev_mineradoras.py")
R = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(R)

CONTA_USD_V2 = True
NOME = "Mineradoras vs metal — conta em dólar v2 (ETFs/ações na IBKR, venda em ações inteiras, SGOV, hedge WDO)"
TESE = ("Mineradora é opção alavancada no metal: compro a mineradora que ficou para trás do metal e vendo o metal (ETF) e vice-versa; "
        "o dinheiro mora na IBKR em SGOV, hedgeado com WDO.")
BENCHMARK, INICIO, CORTE, REGIME, CUSTO_TROCA = "CDI", R.INICIO, R.CORTE, "nenhum", R.CUSTO_TROCA
PARAMS = {"jan": 63, "z_in": 1.0, "alvo": .10, "pares": "todos", "rota": "so_etf", "financia": "caixa"}
GRADE = {"jan": [63, 126], "z_in": [1.0, 2.0]}
VIZINHANCA = {"jan": (45, 90), "z_in": (.75, 1.5), "alvo": (.07, .14)}
INSTRUMENTOS = R.INSTRUMENTOS + " Hedge cambial: WDO (B3, US$ 10 mil, inteiro) vendido sobre o saldo da IBKR."
APLICAVEL = True
MOTIVO = ("Operável na IBKR com ações inteiras na ponta vendida; com sleeve < ~R$ 11 mil (US$ 2 mil) não há venda a descoberto (Reg T) e "
          "metade dos negócios não abre.")
ALAVANCAGENS = [1, 1.5, 2]
MOTIVO_ALAV = R.MOTIVO_ALAV
SLEEVES = V2.SLEEVES
_CACHE = {}


def carrega():
    return R.carrega()


def _motor(d, capital, sleeve_brl, custo_mult, lag, alavancagem, jan, z_in, alvo, pares, rota, financia="caixa"):
    k = (id(d), len(d["precos_limpos"]), d["precos_limpos"].index.max(), capital, sleeve_brl, custo_mult, lag, alavancagem, jan,
         round(z_in, 6), round(alvo, 6), pares, rota, financia)
    if k in _CACHE:
        return _CACHE[k]
    S, Wa, B, Rr, Mo = R._sinais(d, jan, z_in, alvo, pares)
    zero = lambda exig, folga=1.5, revisa="M": (pd.Series(0.0, index=C.DIAS), pd.Series(0.0, index=C.DIAS))
    orig_conta, orig_teto = pf.custo_conta_exterior, PP.TETO_CAIXA
    try:
        pf.custo_conta_exterior, PP.TETO_CAIXA = zero, .95 * sleeve_brl / capital
        res = PP.motor(S, Wa, B, R._pernas(pares, rota), R._instrumentos(d, rota), capital, alavancagem, lag, custo_mult, False,
                       "nenhum", d["cupom"], financia)
    finally:
        pf.custo_conta_exterior, PP.TETO_CAIXA = orig_conta, orig_teto
    # P&L em US$ em excesso do T-bill
    ptax = pf.PTAX.reindex(C.DIAS).ffill().bfill()
    ib = [c for c in res["Q"].columns if c.split("@")[0] not in R.FUT]
    longos = (res["nocional"][ib] * (res["Q"][ib] > 0)).sum(axis=1)               # R$ comprados na IBKR no fechamento
    tb = PP.no_calendario(C.TB_US).fillna(0)
    pnl_usd = res["classes"]["exterior"] / ptax - (longos / ptax).shift(1).fillna(0) * tb
    res["pnl_usd"] = pnl_usd
    if len(_CACHE) > 60:
        _CACHE.clear()
    _CACHE[k] = res
    return res


def _roda(d, capital, sleeve_brl, hedge, custo_mult, lag, alavancagem, params):
    p = {**PARAMS, **params}
    sl = V2.sleeve(capital, sleeve_brl)
    res = _motor(d, capital, sl, custo_mult, lag, alavancagem, p["jan"], p["z_in"], p["alvo"], p["pares"], p["rota"], p["financia"])
    ex, cls = V2.fecha(res["pnl_usd"], sl, capital, hedge, custo_mult)
    return ex, cls, res


def excesso(d, capital=20000, custo_mult=1, lag=0, regime=REGIME, alavancagem=1, sleeve_brl=None, hedge="inteiro", **params):
    ex = _roda(d, capital, sleeve_brl, hedge, custo_mult, lag, alavancagem, params)[0]
    return C.aplica_regime(ex, regime, CUSTO_TROCA * custo_mult)


def classes_ir(d, capital=20000, alavancagem=1, sleeve_brl=None, hedge="inteiro", **params):
    params.pop("regime", None)
    return _roda(d, capital, sleeve_brl, hedge, 1, 0, alavancagem, params)[1]


def posicoes(d, capital=20000, **params):
    p = {**PARAMS, **params}
    return R.posicoes(d, capital, p["jan"], p["z_in"], p["alvo"], p["pares"])


def negocios(d, capital=20000, sleeve_brl=None, hedge="inteiro", **params):
    return PP.tabela_negocios(_roda(d, capital, sleeve_brl, hedge, 1, 0, 1, params)[2])


def diagnostico(d, capital=20000, sleeve_brl=None, **params):
    res = _roda(d, capital, sleeve_brl, "inteiro", 1, 0, 1, params)[2]
    ng = PP.tabela_negocios(res)
    nc = pd.DataFrame(res["naocoube"], columns=["par", "data"])
    o = lambda x: x[x.index >= CORTE]
    return {"negocios OOS": int((pd.to_datetime(ng["entrada"]) >= CORTE).sum()), "nao coube OOS": int((nc["data"] >= CORTE).sum()),
            "exigido medio OOS R$": round(float(o(res["exigido"]).mean())),
            "nocional bruto medio OOS / capital": round(float(o(res["nocional"]).sum(axis=1).mean() / capital), 2),
            "P&L livro OOS US$/ano": round(float(o(res["pnl_usd"]).sum() / (len(o(res["pnl_usd"])) / 252)))}
