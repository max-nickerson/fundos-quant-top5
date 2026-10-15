"""
Petróleo: PETR4/PRIO3 vs petróleo — versão PESSOA FÍSICA (R$ 20–50 mil), commodity como hedge da ação.

Sinal = C1 da pesquisa (quant/fundos/ideias_commodities.py::petroleo, notas em pesquisa/commodities.md), com os parâmetros da linha do
ranking final ({'jan': 63, 'z_in': 2.0, 'conj': 'brent+par'}): resíduo = (ação - CDI) - beta x (BNO em R$ sem hedge - CDI), beta de 1
ano em retornos de 5 dias (só passado, entre 0 e 3), z do resíduo acumulado, decisão semanal, entra |z| > z_in, sai em 0, stop |z| > 4
ou 120 dias; risco igual por par (vol-alvo 10%/raiz(n)); PRIO só desde 2016 (antes era penny stock); ação parada (> 30% dos dias sem
variação em 21 dias) fica fora. Diferenças para o original: (1) histerese do top 5 auditado (depois de stop/prazo o lado fica bloqueado
até o z voltar a 0 — no original reabria no mesmo dia, bug listado no DIARIO); (2) regime "nenhum" (o ranking usou "inv_risco_global",
regime genérico escolhido no IS — a auditoria mostrou que isso fabrica resultado); (3) BNO em R$ pela PTAX (original: BRL=X do Yahoo).

Execução PF (motor _rev_pares_pf.py, tamanho fixado na entrada):
  - PETR4/PRIO3 no fracionário da B3 (1 ação): comprada = dinheiro sai do CDI; vendida = aluguel BTC de PF (0,5% do volume por contrato
    na corretora + taxa ao doador: PETR4 0,5% a.a., PRIO3 1,5% a.a.), dinheiro da venda em Tesouro Selic (rende CDI). IR: vendas de ações
    no mês <= R$ 20 mil -> ganho ISENTO (com R$ 20 mil de capital quase todo mês fica abaixo) — edge que só a PF tem;
  - perna do petróleo: MCL (micro WTI, 100 barris, ~US$ 9,4 mil = R$ 47 mil em out/2026) em contratos inteiros se couber, senão BNO
    (ETF de Brent) na IBKR: vendido em cotas inteiras (Reg T: 50% + mínimo US$ 2.000 de patrimônio para vender a descoberto), comprado
    com fração. Na prática a perna de petróleo de um par é R$ 3–10 mil: o MCL NUNCA cabe com R$ 20–50 mil (só com 5x) -> BNO.
  - B3 tem minicontrato de WTI (100 barris, liquidação financeira) — mesmo tamanho do MCL, não resolve o lote (e a liquidez não foi
    verificada): https://www.b3.com.br/lumis/portal/file/fileDownload.jsp?fileId=8A828D2951C9C37701520D8E14423CD7
  - Não existe BDR de ETF de petróleo físico/futuro na B3 (só de petroleiras: BIYE39, BIEO39) — https://maisretorno.com/portal/biye39
  - Câmbio: o original hedgeia com "BNO em reais"; o vendido em BNO/MCL na IBKR hedgeia só o petróleo em dólar (o dinheiro da venda fica
    em dólar e anula o câmbio do nocional). Sobra beta x dólar no par. WDO (US$ 10 mil) não cabe na perna de R$ 3–10 mil.

Premissas corrigidas (out/2026), com fonte:
  - MCL: margem inicial IBKR US$ 1.625 (~17% do nocional; pf.CONTRATOS tinha 10%) — https://brokerchooser.com/best-brokers/lowest-margin-brokers-for-trading-micro-crude-oil-futures ;
    https://www.interactivebrokers.com/en/trading/margin-futures-fops.php ; MCL existe desde 12/07/2021 (VARIANTE "historico").
  - MCL custo por lado ~US$ 1,50 (IBKR US$ 0,25 + bolsa/regulatório ~US$ 0,70 + meio tick US$ 0,50); rola todo mês. Retorno do MCL =
    retorno do USO (ETF de futuros de WTI) - T-bill + 0,60% a.a. de taxa (proxy; o contínuo do Yahoo não é usado no P&L).
  - BNO: aluguel na IBKR não confirmado (arquivo de short não lido para BNO) -> 1,0% a.a. (conservador); meio spread 0,10%.
  - PETR4/PRIO3: emolumentos 0,03% + meio spread (pf.custo_b3, "liquida" + 0,2% do fracionário); aluguel PF como no brief.
"""
import importlib.util
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

import _util as U  # noqa: E402
import _rev_pares_pf as PP  # noqa: E402

C, pf = U.C, U.pf

_spec = importlib.util.spec_from_file_location("_min_top5_p", U.RAIZ / "fundos" / "mineradoras.py")
M = importlib.util.module_from_spec(_spec)           # só as peças genéricas: beta, z, semana, histerese
_spec.loader.exec_module(M)

NOME = "Petróleo: PETR4/PRIO3 vs petróleo (PF: fracionário B3 + BNO/MCL na IBKR)"
TESE = ("A ação de petroleira é petróleo em reais + risco da empresa: quando PETR4/PRIO3 ficam para trás do Brent x dólar, compro a ação "
        "no fracionário (isenta até R$ 20 mil de vendas/mês) e vendo petróleo (BNO na IBKR; MCL se coubesse); quando andam demais, o inverso.")
BENCHMARK = "CDI"
INICIO, CORTE = "2012-01-01", "2021-01-01"
REGIME = "nenhum"
CUSTO_TROCA = .001
PARAMS = {"jan": 63, "z_in": 2.0, "alvo": .10, "conj": "brent+par"}
GRADE = {"jan": [63, 126], "z_in": [1.0, 1.5, 2.0], "conj": ["brent", "brent+par"]}
VIZINHANCA = {"jan": (45, 90), "z_in": (1.5, 2.5), "alvo": (.07, .14)}
RANKING = ["C1 Petróleo: PETR4/PRIO3 vs Brent em R$"]

ACOES = {"PETR4": "PETR4.SA", "PRIO3": "PRIO3.SA"}
PARES = {"PETR4 x BNO": ("PETR4", "BNO"), "PRIO3 x BNO": ("PRIO3", "BNO"), "PRIO3 x PETR4": ("PRIO3", "PETR4")}
CONJ = {"brent": ["PETR4 x BNO", "PRIO3 x BNO"], "brent+par": ["PETR4 x BNO", "PRIO3 x BNO", "PRIO3 x PETR4"], "petr": ["PETR4 x BNO"]}
INI = {"PRIO3 x BNO": "2016-01-01", "PRIO3 x PETR4": "2016-01-01"}
ROTAS = {"auto": "MCL|BNO", "so_etf": "BNO", "so_futuro": "MCL", "historico": "MCL|BNO"}
MCL = {"mult": 100.0, "margem": .17, "custo": 1.50, "rolagens": 12, "taxa_etf": .0060, "desde": "2021-07-12"}
ALUG = {"PETR4": .005, "PRIO3": .015, "BNO": .01}

INSTRUMENTOS = ("B3 (Clear/Rico/XP/BTG): PETR4 e PRIO3 no fracionário (1 ação, emolumentos 0,03% + spread), venda via aluguel BTC "
                "(0,5% do volume por contrato + 0,5–1,5% a.a. ao doador); IBKR: BNO (ETF de Brent, ~US$ 30–40/cota; vendido em cotas "
                "inteiras, Reg T 50% + mínimo US$ 2.000) ou MCL (micro WTI, 100 barris ~US$ 9,4 mil, margem ~US$ 1.625) se coubesse. "
                "Caixa em Tesouro Selic.")
APLICAVEL = True
MOTIVO = ("Operável no varejo: as ações cabem no fracionário (isenção de R$ 20 mil/mês) e o hedge de petróleo vai em BNO na IBKR; o MCL "
          "(R$ ~35–47 mil de nocional) é 4–10x a perna de petróleo de um par e não cabe. O custo fixo de ter conta margem na IBKR (US$ 2.000 "
          "parados para poder vender BNO) pesa muito em R$ 20 mil.")
ALAVANCAGENS = [1, 1.5, 2, 5]
MOTIVO_ALAV = ("1x a 2x: ações compradas são pagas à vista com o caixa (teto de 95% do capital fora do CDI); 5x roda só porque o motor "
               "recusa abrir o par quando o caixa não dá — a alavancagem efetiva fica bem abaixo de 5x (ver 'nocional bruto' no diagnóstico).")
VARIANTES = {"só PETR4 x petróleo": {"conj": "petr"}, "petróleo só em BNO": {"rota": "so_etf"},
             "petróleo só em MCL (par sem contrato inteiro não abre)": {"rota": "so_futuro"},
             "histórico (MCL só desde jul/2021)": {"rota": "historico"}, "sem o par PRIO3 x PETR4": {"conj": "brent"}}
EXEC = {"rota": "auto", "hedge_fx": "nenhum", "financia": "caixa"}


# ---------------------------------------------------------------- dados
def carrega():
    y = pd.read_parquet(U.FD / "y_comm.parquet")[list(ACOES.values())]
    e = pd.read_parquet(U.FD / "y_etf.parquet")[["BNO", "USO"]]
    n = pd.read_parquet(U.FD / "y_idx.parquet")[["CL=F", "BZ=F"]]
    tira = lambda x: x[~x.index.duplicated(keep="last")]
    return {"acoes": tira(y).rename(columns={v: k for k, v in ACOES.items()}), "etf": tira(e), "niveis": tira(n), "tb": C.TB_US,
            "cupom": C.ler("carry_moedas/cupom_frc.csv")["cupom_frc_aa_pct"]}


_CACHE = {}


def _chave(d, *a):
    return (id(d), len(d["acoes"]), d["acoes"].index.max(), len(d["etf"]), d["etf"].index.max()) + a


def _precos(d):
    A = d["acoes"].reindex(C.DIAS).ffill(limit=5)
    E = d["etf"].apply(PP.no_calendario)
    return A, E


def _r_acao(A, tk):
    r = A[tk].pct_change(fill_method=None)
    ok = r.notna() & ~((r == 0).astype(float).rolling(21, min_periods=10).mean().shift(1) > .3)   # ação parada = ilíquida
    return M._limpa(r).where(ok)


def _sinais(d, jan, z_in, alvo, conj):
    k = _chave(d, "s", jan, round(z_in, 6), round(alvo, 6), conj)
    if k in _CACHE:
        return _CACHE[k]
    A, E = _precos(d)
    cdi = C.CDI.reindex(C.DIAS).fillna(0)
    fxr = pf.PTAX.pct_change(fill_method=None).reindex(C.DIAS).fillna(0)
    rb = M._limpa(E["BNO"].pct_change(fill_method=None))
    ex = {"PETR4": _r_acao(A, "PETR4") - cdi, "PRIO3": _r_acao(A, "PRIO3") - cdi, "BNO": (1 + rb) * (1 + fxr) - 1 - cdi}
    R, B = {}, {}
    for kk in CONJ[conj]:
        a, h = PARES[kk]
        B[kk] = M._beta(ex[a], ex[h])
        R[kk] = ex[a] - B[kk] * ex[h]
        if kk in INI:
            R[kk] = R[kk].where(R[kk].index >= INI[kk])
    R = pd.DataFrame(R).reindex(C.DIAS)
    R = R.where(R.notna().cumsum() > 0)
    B = pd.DataFrame(B).reindex(C.DIAS)
    S, Mo = M._histerese(M._semanal(M._zscore(R, jan)), z_in)
    v = R.rolling(63, min_periods=40).std().shift(1) * np.sqrt(252)
    W = (S * (alvo / np.sqrt(R.shape[1])) / v).replace([np.inf, -np.inf], 0).fillna(0).clip(-2, 2).where(S != 0, 0)
    out = (np.sign(W), W.abs(), B, R, Mo)
    if len(_CACHE) > 60:
        _CACHE.clear()
    _CACHE[k] = out
    return out


def _instrumentos(d, rota):
    A, E = _precos(d)
    tb = PP.no_calendario(d["tb"]).fillna(0)
    inst = {"PETR4": {"tipo": "b3", "P": A["PETR4"], "aluguel": ALUG["PETR4"], "liquidez": "liquida"},
            "PRIO3": {"tipo": "b3", "P": A["PRIO3"], "aluguel": ALUG["PRIO3"], "liquidez": "liquida"},
            "BNO": {"tipo": "ibkr", "P": E["BNO"], "spread": .001, "aluguel": ALUG["BNO"]}}
    cont = PP.no_calendario(d["niveis"]["CL=F"])
    if rota == "historico":
        cont = cont.where(cont.index >= MCL["desde"])
    rx = M._limpa(E["USO"].pct_change(fill_method=None)) - tb + MCL["taxa_etf"] / 252
    inst["MCL"] = {"tipo": "fut", "cont": cont, "rx": rx, "mult": MCL["mult"], "margem": MCL["margem"], "custo": MCL["custo"],
                   "rolagens": MCL["rolagens"]}
    return inst


def _pernas(conj, rota):
    out = {}
    for kk in CONJ[conj]:
        a, h = PARES[kk]
        out[kk] = [("A", a, None), ("H", ROTAS[rota] if h == "BNO" else h, 1.0)]
    return out


def _roda(d, capital, custo_mult, lag, alavancagem, jan, z_in, alvo, conj, validacao=False, **ex):
    ex = {**EXEC, **ex}
    k = _chave(d, "m", capital, custo_mult, lag, alavancagem, jan, round(z_in, 6), round(alvo, 6), conj, validacao, tuple(sorted(ex.items())))
    if k in _CACHE:
        return _CACHE[k]
    S, Wa, B, R, Mo = _sinais(d, jan, z_in, alvo, conj)
    res = PP.motor(S, Wa, B, _pernas(conj, ex["rota"]), _instrumentos(d, ex["rota"]), capital, alavancagem, lag, custo_mult, validacao,
                   ex["hedge_fx"], d["cupom"], ex["financia"])
    if len(_CACHE) > 60:
        _CACHE.clear()
    _CACHE[k] = res
    return res


# ---------------------------------------------------------------- contrato
def excesso(d, capital=20000, custo_mult=1, lag=0, regime=REGIME, alavancagem=1, jan=PARAMS["jan"], z_in=PARAMS["z_in"],
            alvo=PARAMS["alvo"], conj=PARAMS["conj"], validacao=False, **ex):
    res = _roda(d, capital, custo_mult, lag, alavancagem, jan, z_in, alvo, conj, validacao, **ex)
    return C.aplica_regime(res["e"], regime, CUSTO_TROCA * custo_mult)


def classes_ir(d, capital=20000, jan=PARAMS["jan"], z_in=PARAMS["z_in"], alvo=PARAMS["alvo"], conj=PARAMS["conj"], **ex):
    return _roda(d, capital, 1, 0, 1, jan, z_in, alvo, conj, **ex)["classes"]


def posicoes(d, capital=20000, jan=PARAMS["jan"], z_in=PARAMS["z_in"], alvo=PARAMS["alvo"], conj=PARAMS["conj"]):
    S, Wa, B, R, Mo = _sinais(d, jan, z_in, alvo, conj)
    return S * Wa, R


def negocios(d, capital=20000, jan=PARAMS["jan"], z_in=PARAMS["z_in"], alvo=PARAMS["alvo"], conj=PARAMS["conj"], lag=0, **ex):
    return PP.tabela_negocios(_roda(d, capital, 1, lag, 1, jan, z_in, alvo, conj, **ex))


def diagnostico(d, capital=20000, **kw):
    p = {**PARAMS, **{k: v for k, v in kw.items() if k in PARAMS}}
    ex = {k: v for k, v in kw.items() if k not in PARAMS}
    res = _roda(d, capital, 1, 0, 1, p["jan"], p["z_in"], p["alvo"], p["conj"], **ex)
    ng = PP.tabela_negocios(res)
    nc = pd.DataFrame(res["naocoube"], columns=["par", "data"])
    o = lambda s: s[s.index >= CORTE]
    cl = res["classes"]
    return {"negocios por rota": ng.groupby("rota").size().to_dict(), "nao coube por par": nc.groupby("par").size().to_dict(),
            "saldo IBKR medio OOS R$": round(float(o(res["saldo"]).mean())) if hasattr(res["saldo"], "mean") else 0,
            "nocional bruto medio OOS / capital": round(float(o(res["nocional"]).sum(axis=1).mean() / capital), 2),
            "P&L acoes isentas x tributaveis R$": (round(float(cl["acoes_isentas"].sum())), round(float(cl["acoes"].sum())))}
