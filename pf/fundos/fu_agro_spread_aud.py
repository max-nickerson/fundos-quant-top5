"""
fu_agro_spread — AUDITADA (pf/pesquisa/auditoria_pf2.md). Mesma regra (CCM: vendido no setembro, comprado no março seguinte, mar-ago),
com duas correções de execução:
  1) o CCM março+1 NÃO negocia no começo de março (0 negócios nos 5 primeiros pregões de março em 2018-2025; 49% dos dias de março com
     negócio): o ajuste de entrada é teórico (curva da B3). Só entra depois do 1º pregão da janela em que o H+1 negociou >= 5 contratos
     (volume do boletim B3, quant/fundos/dados/b3_futuros_agro.parquet, conhecido no fechamento de t);
  2) custo por perna por lado: H+1 (ilíquido) = emolumentos R$ 1,50 + meio spread de R$ 0,20/saca (R$ 90) = R$ 91,50; U (líquido,
     milhares de contratos/dia) = R$ 1,50 + R$ 0,03/saca = R$ 15. Sem bid/ask histórico do boletim: hipótese conservadora, citada.
"""
import numpy as np
import pandas as pd

import fu_agro_spread as O
import fu_comum as F

NOME = "Agro B3: spread de milho set x mar+1 — AUDITADA (entra só com o H+1 negociando; meio spread R$ 0,20/saca no H+1)"
TESE = O.TESE
BENCHMARK = O.BENCHMARK
INICIO, CORTE = O.INICIO, O.CORTE
REGIME = O.REGIME
CUSTO_TROCA = O.CUSTO_TROCA
CLASSE_IR = O.CLASSE_IR
PARAMS = dict(O.PARAMS)
GRADE = dict(O.GRADE)
VIZINHANCA = {}
PAR = O.PAR
INSTRUMENTOS = O.INSTRUMENTOS
APLICAVEL = True
MOTIVO = O.MOTIVO
ALAVANCAGENS = [1, 2]
MOTIVO_ALAV = O.MOTIVO_ALAV
MIN_CONTR = 5
CUSTO_LONGO, CUSTO_CURTO = 91.5, 15.0          # R$ por contrato por lado (perna ilíquida / líquida), só no CCM
BRUTO = F.PF.parent.parent / "fundos" / "dados" / "b3_futuros_agro.parquet"


def carrega():
    v = pd.read_parquet(BRUTO, columns=["date", "ticker", "FinInstrmQty"])
    v = v[v.ticker.str[:3].isin(list(PAR))].groupby(["date", "ticker"]).FinInstrmQty.max().unstack().fillna(0)
    return {"agro": F.ler("agro_b3.parquet"), "vol": v}


def gera(d, capital=20000, regime=REGIME, alavancagem=1, produto="todos", lado=1):
    N, K = O.gera(d, capital=capital, regime=regime, alavancagem=alavancagem, produto=produto, lado=lado)
    prods = list(PAR) if produto == "todos" else [produto]
    vol = d["vol"]
    for pr in prods:
        if pr != "CCM":
            continue
        tko = O._pernas(d, pr)["outra"][1].reindex(N.index)
        q = pd.Series([vol.at[t, c] if (t in vol.index and c in vol.columns) else 0.0 for t, c in zip(N.index, tko)], index=N.index)
        on = N[f"{pr}_hedge"] != 0
        bloco = (on & ~on.shift(1, fill_value=False)).cumsum()             # recomeça a contagem a cada janela
        ja = ((q >= MIN_CONTR) & on).groupby(bloco).cummax()
        N[f"{pr}_hedge"] = N[f"{pr}_hedge"].where(ja, 0.0)
        N[f"{pr}_outra"] = N[f"{pr}_outra"].where(ja, 0.0)
        K[f"{pr}_outra"] = K[f"{pr}_outra"].assign(custo=CUSTO_LONGO)     # H+1
        K[f"{pr}_hedge"] = K[f"{pr}_hedge"].assign(custo=CUSTO_CURTO)     # U
    return N, K


F.montar(globals(), gera, carrega)

_neg_pernas = negocios                                     # noqa: F821


def negocios(d, capital=20000, **params):
    ng = _neg_pernas(d, capital=capital, **params)
    if ng.empty:
        return ng
    ng = ng.assign(prod=ng.ativo.str[:3])
    g = ng.groupby(["prod", "entrada"], as_index=False).agg(saida=("saida", "max"), dias=("dias", "max"), contratos=("contratos", "max"),
                                                             retorno_=("retorno_%", "sum"), contrib_pp=("contrib_pp", "sum"))
    g["ativo"] = g["prod"] + " spread"
    g["lado"] = int(params.get("lado", PARAMS["lado"]))
    return g.rename(columns={"retorno_": "retorno_%"})[["ativo", "lado", "entrada", "saida", "dias", "contratos", "retorno_%", "contrib_pp"]]
