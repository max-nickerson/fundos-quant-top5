"""
Mini-dólar (WDO) depois de pânico cambial: VENDO dólar (compro real) por algumas semanas depois de uma alta forte e rápida do dólar.

Tese de mesa: altas de 2–3 desvios do dólar em 2 semanas no Brasil são, em geral, fluxo FORÇADO — stop de quem carregava real (carry),
estrangeiro desmontando bolsa/NTN-B (resgates de fundos EM), importador/empresa com dívida em dólar comprando hedge às pressas, overhedge
de bancos. O BC reage (leilões de linha/swap cambial, discurso) e o diferencial de juro passa a pagar mais a quem vende o dólar futuro.
É o oposto do carry "sempre vendido" já reprovado (db3_wdo_carry: beta de 'comprado em real'): aqui fico zerado 90% do tempo e só
forneço liquidez DEPOIS do vendedor forçado; o carry (CDI - cupom) só entra como bônus durante a janela.
Filtro opcional: pânico GLOBAL (VIX acima do seu percentil 90 de 1 ano) tende a continuar (2008, mar/2020) -> não entro.

Implementação:
  - sinal no fechamento de t (PTAX de t): retorno do dólar em 10 pregões / (vol diária de 63 pregões até t-10 x raiz(10)) >= `z`;
  - posição: vendido em WDO por `dias` pregões a partir de t+1 (+lag); ajuste diário = retorno em excesso do futuro (DOL rolado da B3
    desde 2019; antes, sintético PTAX - (CDI - cupom)); rolagem no 1º dia útil do mês (2 lados);
  - tamanho: contratos inteiros para 1x o capital em dólar, mínimo 1 (WDO = US$ 10 mil ~ R$ 50–55 mil: com R$ 20 mil é ~2,5x o capital
    durante a janela; com R$ 50 mil, ~1x). Garantia (~12% do nocional) em Tesouro Selic, rende CDI;
  - custo R$ 3,70 por contrato e lado (emolumentos ~R$ 1,20 + meio tick de 0,5 ponto = R$ 5 x 1/2... ver mh_base: R$ 3,70) x custo_mult;
  - IR: futuros B3 15% (apuração mensal com compensação).
Dados: PTAX (BCB) 2008+, DOL B3 2019+, Fed funds (FRED), VIX. Corte OOS 2021-01-01.
"""
import numpy as np
import pandas as pd

import jx_comum as J

NOME = "Mini-dólar vendido após pânico cambial (vendedor forçado)"
TESE = ("Vendo WDO (compro real) por 2–4 semanas depois que o dólar sobe >= 2 desvios em 10 pregões (stop de carry, resgates EM, hedge às "
        "pressas), fora de pânico global; zerado no resto do tempo")
BENCHMARK = "CDI"
INICIO, CORTE = "2008-06-01", "2021-01-01"
REGIME = "nenhum"
CUSTO_TROCA = 0.0
PARAMS = {"z": 2.0, "dias": 21, "filtro": "vix", "noc": 1.0, "minimo": 1}
GRADE = {"z": [2.0, 2.5], "dias": [10, 21], "filtro": ["nenhum", "vix"]}
VIZINHANCA = {"z": (1.7, 2.7), "dias": (8, 30)}
CLASSE_IR = "futuros_b3"
CUSTO_WDO = 3.70
INSTRUMENTOS = [{"onde": "B3 (Clear/Rico/XP/BTG)", "ticker": "WDO (mini-dólar, vencimento mais curto)", "lote": "1 contrato = US$ 10 mil",
                 "custo": "R$ 3,70 por contrato e lado (emolumentos + meio tick); margem ~12% em Tesouro Selic"}]
APLICAVEL = True
MOTIVO = ("Com R$ 50 mil, 1 WDO ~ 1x o capital. Com R$ 20 mil, 1 contrato = ~2,5x o capital em dólar durante a janela (não há "
          "micro-dólar na B3) — aplicável, mas o risco por negócio é ~2,5x maior.")
ALAVANCAGENS = [1, 2]
MOTIVO_ALAV = "2x = 2 contratos por R$ de capital; 5x com R$ 20 mil = 5 WDO (~R$ 270 mil de nocional) — um +10% no dólar leva 135% do capital."


def carrega():
    return {"mkt": J.mercado()}


def _sinal(d, z, dias, filtro):
    px = J.PTAX
    r = np.log(px).diff()
    vol = r.rolling(63, min_periods=40).std().shift(10)
    s10 = np.log(px / px.shift(10))
    zz = s10 / (vol * np.sqrt(10))
    entra = zz >= z
    if filtro == "vix":
        v = J.serie(d, "vix")
        p90 = v.rolling(252, min_periods=120).quantile(.9)
        entra &= ~(v > p90)
    # só dias com PTAX/dados do próprio dia (o corte de truncamento apaga o futuro)
    fim = d["mkt"].index.max()
    entra &= pd.Series(J.DIAS <= fim, index=J.DIAS)
    on = J.maquina(entra, pd.Series(False, index=J.DIAS), int(dias))
    return on, zz


def _livro(d, capital=20000, custo_mult=1, lag=0, alavancagem=1, z=PARAMS["z"], dias=PARAMS["dias"], filtro=PARAMS["filtro"],
           noc=PARAMS["noc"], minimo=PARAMS["minimo"]):
    on, zz = _sinal(d, z, dias, filtro)
    r, noc1 = J.wdo(d)
    alvo = -on.astype(float) * noc * alavancagem * capital
    n = J.contratos_inteiros(alvo, noc1, minimo=minimo * max(1, int(round(alavancagem))) if minimo else 0)
    L = J.futuro_livro(n, r, noc1, CUSTO_WDO, capital, lag, custo_mult, roll_mask=J.primeiro_util_do_mes())
    L["on"], L["zz"] = on, zz
    return L


def excesso(d, capital=20000, custo_mult=1, lag=0, regime=REGIME, alavancagem=1, **params):
    L = _livro(d, capital, custo_mult, lag, alavancagem, **{**PARAMS, **params})
    return J.C.aplica_regime(L["e"], regime, CUSTO_TROCA * custo_mult)


def classes_ir(d, capital=20000, **params):
    L = _livro(d, capital, **{**PARAMS, **params})
    return {CLASSE_IR: L["pnl"]}


def posicoes(d, capital=20000, **params):
    p = {**PARAMS, **params}
    L = _livro(d, capital, **p)
    r, noc1 = J.wdo(d)
    W = pd.DataFrame({"WDO": (L["pos"].shift(-1 - 0).fillna(0) * noc1 / capital)}).fillna(0)
    return W, pd.DataFrame({"WDO": r})


def negocios(d, capital=20000, **params):
    p = {**PARAMS, **params}
    L = _livro(d, capital, **p)
    ng = J.negocios_de_estado(L["on"], L["e"], "WDO vendido", lado=-1)
    if len(ng):
        ng["z_entrada"] = [L["zz"].get(a, np.nan) for a in ng.entrada]
        ng["ptax_entrada"] = [J.PTAX.get(a, np.nan) for a in ng.entrada]
        ng["ptax_saida"] = [J.PTAX.get(b, np.nan) for b in ng.saida]
        ng["contratos"] = [L["pos"].shift(-1).get(a, np.nan) for a in ng.entrada]
    return ng
