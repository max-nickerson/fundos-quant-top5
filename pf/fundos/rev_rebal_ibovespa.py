"""
E7 Rebalanceamento do Ibovespa — versão pessoa física (R$ 20–50 mil), frente "revisita".

Mesa: a cada quadrimestre (carteiras de jan/mai/set) os fundos de índice e ETFs (BOVA11 etc.) compram os entrantes no fechamento do
último pregão da carteira velha. Reconstruímos a regra da B3 só com dados até a data (fundos/rebal_ibovespa.py: índice de
negociabilidade 12m, presença >= 95%, preço >= R$ 1, 85% acumulado), compramos os prováveis entrantes 10 pregões antes e vendemos no
fechamento do último pregão da carteira velha — quem compra de nós é o fundo passivo.

Rota PF (Clear/Rico/Inter, corretagem zero): ~4 entrantes por revisão, 1/15 do capital cada (R$ 1,3 mil com R$ 20 mil -> FRACIONÁRIO, ticker
XXXX3F); resto em Tesouro Selic. Edges de capital pequeno:
  - VENDAS ≤ R$ 20 mil no mês => ganho ISENTO de IR (IN RFB 1.585/2015 art. 59): com R$ 20 mil a saída de cada revisão vende ~R$ 5–8 mil;
    com R$ 50 mil ~R$ 13–20 mil — quase todos os meses ficam isentos;
  - lote pequeno não move o preço de mid cap (o institucional pagava 20–80 bps de impacto).
Hedge: o institucional vende Ibovespa 1:1. Na PF 1 WIN ≈ R$ 41 mil (2x o capital) e a exposição média é ~R$ 5 mil -> arredonda para ZERO
(20k e 50k); BOVA11 alugado custa 0,5% por contrato + 0,88% a.a. (B3, 30/12/2025) -> fica como VARIANTE. Fundo escolhido: SEM hedge.
Execução t+1 (decide 10 pregões antes, executa no fechamento seguinte), ações inteiras, custos de varejo (motor _ev_pf).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _util as U  # noqa: E402

C, pf = U.C, U.pf
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

import _ev_pf as M  # noqa: E402
from fundos import rebal_ibovespa as I  # noqa: E402  (institucional, fundos-quant-top5/fundos)

NOME = "E7 Rebalanceamento do Ibovespa (PF)"
TESE = ("Compro no fracionário os prováveis entrantes do Ibovespa (regra da B3 reconstruída só com dados até a data) 10 pregões antes da "
        "troca e vendo no fechamento do último pregão da carteira velha para os fundos passivos; com R$ 20–50 mil as vendas do mês ficam "
        "abaixo de R$ 20 mil e o ganho é isento de IR")
BENCHMARK = "CDI"
INICIO, CORTE = "2014-06-01", "2021-01-01"
REGIME = "nenhum"          # evento de calendário com pressão de fluxo mecânica: não há regime de mercado com sentido econômico
CUSTO_TROCA = .001
PARAMS = {"antes": 10, "lado": "compra", "hedge": "nenhum"}
GRADE = {"antes": [10, 21, 42], "lado": ["ambos", "compra"]}
VIZINHANCA = {"antes": (7, 14)}
RANKING = ["E7 Rebalanceamento do Ibovespa"]
INSTRUMENTOS = ("Clear/Rico/Inter (corretagem zero): entrantes prováveis no fracionário (XXXX3F, 1 ação mínima; lote de 100 no padrão), "
                "1/15 do capital por papel; caixa em Tesouro Selic/LFTS11. Variantes de hedge: WIN (R$ 0,20 x pontos ≈ R$ 41 mil, margem em "
                "Tesouro Selic) ou BOVA11 vendido via aluguel (0,5% por contrato + 0,88% a.a. ao doador + B3 20% da taxa)")
APLICAVEL = True
MOTIVO = ("Aplicável: mid caps no fracionário com corretagem zero; posição média ~R$ 5 mil com R$ 20 mil; vendas por revisão < R$ 20 mil "
          "-> isento de IR. Sem hedge (WIN não cabe; BOVA11 alugado come o ativo)")
ALAVANCAGENS = [1, 1.5, 2, 5]
MOTIVO_ALAV = ("A exposição média é ~27% do capital (máx. ~70%): 1,5x e 2x cabem no próprio capital (sem financiamento); 5x passa do "
               "capital nas revisões com 5+ entrantes e o excedente paga termo a CDI + 4% a.a. (premissa: termo de mid cap em lote fracionário "
               "depende da corretora aceitar)")
VARIANTES = {"hedge WIN inteiro": {"hedge": "win"}, "hedge BOVA11 alugado": {"hedge": "bova"},
             "livro ambos (vende saintes via aluguel)": {"lado": "ambos"},
             "custos institucionais, sem arredondamento, hedge contínuo (validação)": {"custos": "inst", "hedge": "inst"}}


def carrega():
    d = I.carrega()
    d["ibov"] = pd.read_csv(U.RAIZ / "varejo" / "dados" / "rebal_ibovespa" / "ibov.csv", index_col=0, parse_dates=True)["ibov_pts"]
    return d


def _hedge(h):
    return {"nenhum": (0.0, "bova"), "bova": (1.0, "bova"), "win": (1.0, "win"), "inst": (1.0, "inst")}[h]


def _roda(d, capital=20000, custo_mult=1, lag=0, alavancagem=1, antes=PARAMS["antes"], lado=PARAMS["lado"], hedge=PARAMS["hedge"],
          custos="pf"):
    capital = 1e9 if custos == "inst" else capital            # validação: capital enorme, custos institucionais
    p = I._painel(d)
    W = M.antecipa_saida(I._pesos(d, int(antes), lado))         # saída no último PREGÃO da carteira velha (31/12 não tem pregão)
    tk = list(W.columns)
    adv = p["ADV"].reindex(columns=tk)
    if custos == "inst":
        taxa = I.aluguel_acao(adv.reindex(C.DIAS).ffill())
    else:
        taxa = M.taxa_aluguel(adv, p["R"].reindex(columns=tk), p["P"].reindex(columns=tk))   # saintes: modelo B3, sem prêmio de evento
    hf, ins = _hedge(hedge)
    return M.simula(W, p["P"].reindex(columns=tk), p["R"].reindex(columns=tk), adv, capital, custo_mult, lag, alavancagem, taxa=taxa,
                    hedge=hf, instrumento=ins, ibov=d["ibov"], custos=custos)


def excesso(d, capital=20000, custo_mult=1, lag=0, regime=REGIME, alavancagem=1, **params):
    kw = {**PARAMS, **params}
    e = _roda(d, capital, custo_mult, lag, alavancagem, **kw)["excesso"]
    return C.aplica_regime(e, regime, CUSTO_TROCA * custo_mult)


def classes_ir(d, capital=20000, **params):
    return _roda(d, capital, **{**PARAMS, **params})["classes"]


def posicoes(d, **params):
    kw = {**PARAMS, **params}
    p = I._painel(d)
    W = M.antecipa_saida(I._pesos(d, int(kw["antes"]), kw["lado"]))
    return M.posicoes_de(W, p["R"])


def negocios(d, capital=20000, **params):
    res = _roda(d, capital, **{**PARAMS, **params})
    ng = M.negocios_de(res, capital)
    return ng


if __name__ == "__main__":
    import time
    d = carrega()
    for kw in ({}, {"capital": 50000}, {"hedge": "win", "capital": 50000}, {"hedge": "bova"}, {"lado": "ambos"},
               {"custos": "inst", "hedge": "inst"}):
        t = time.time()
        e = excesso(d, **kw)
        print(kw, "IS %.2f OOS %.2f (%.1fs)" % (C.anual(e[INICIO:CORTE]), C.anual(e[CORTE:]), time.time() - t))
    e0 = I.excesso(d)
    print("institucional IS %.2f OOS %.2f" % (C.anual(e0[INICIO:CORTE]), C.anual(e0[CORTE:])))
