"""
Carry do real via mini-dólar: VENDIDO em WDO com a garantia em Tesouro Selic — o "carry trade" acessível à pessoa física.

Tese de mesa: o dólar futuro negocia acima do à vista pelo diferencial CDI − cupom cambial (pontos a termo). Quem vende o futuro e
deixa a garantia em Selic recebe esse diferencial (8–11% a.a. em 2022–2026) se o real não se desvalorizar mais que isso. É o mesmo
prêmio da perna BRL do fundo de carry de moedas: o estrangeiro e o exportador compram dólar futuro para se proteger (hedge) e pagam o
diferencial a quem fornece o hedge. Risco: o real cai junto com todo ativo de risco (Covid 2020: +45% no dólar). Por isso o sinal só
fica ligado quando:
  (a) VIX abaixo do percentil 80 de 1 ano (apetite a risco global — o carry desmonta quando o VIX dispara);
  (b) juro real ex-ante (Selic meta − IPCA 12m esperado pelo Focus) acima de um piso: carry alto em termos reais atrai o fluxo que
      sustenta o real; com juro real baixo (2020–21) o diferencial não paga a vol do câmbio;
  (c) CFTC: os especuladores alavancados (TFF, leveraged funds) no real da CME estão AUMENTANDO a posição comprada em real (acima da
      média de 26 semanas). A pesquisa mostrou que o contrarian CFTC não funciona — o especulador lotado está certo; aqui ele só confirma.

Implementação: WDO (US$ 10 mil; 1 ponto = R$ 10), contrato de vencimento mais próximo rolado 3 pregões antes do vencimento (1º dia útil
do mês), P&L pela variação do ajuste do MESMO contrato (sem salto de rolagem). Contratos inteiros: n = max(1, arred(capital x alav /
nocional)) quando ligado — 1 contrato = R$ 50–60 mil de nocional, ou seja, 2,5–3x o capital de R$ 20 mil (não existe micro-dólar
na B3). Custo R$ 4/contrato/lado + rolagem mensal (2 lados). Margem B3 ~R$ 4–6 mil/contrato em Selic. IR: "futuros_b3" (15%).
Dados: futuros B3 2019+ (quant/dados/futuros.parquet, deduplicado aqui: havia linhas repetidas e linhas sem ajuste) -> corte 2023.
"""
import numpy as np
import pandas as pd

import db3_base as B

NOME = "Carry do real vendido em mini-dólar (WDO) com filtro de risco"
TESE = "Vendo WDO (recebo CDI − cupom cambial) com garantia em Selic, só com VIX calmo, juro real alto e especuladores aumentando o real"
BENCHMARK = "CDI"
INICIO, CORTE = "2019-03-01", "2023-01-01"
REGIME, CUSTO_TROCA = "nenhum", 0.0
PARAMS = {"vix": False, "juro_real_min": 4.0, "cftc": False, "vix_q": .8}      # melhor IR no IS (2019–2022) da GRADE
GRADE = {"vix": [False, True], "juro_real_min": [0.0, 4.0], "cftc": [False, True]}
VIZINHANCA = {"juro_real_min": (2.5, 5.5), "vix_q": (.7, .9)}
CLASSE_IR = "futuros_b3"
MULT, CUSTO_LADO = 10.0, 4.0
INSTRUMENTOS = [{"onde": "B3", "ticker": "WDO (mini-dólar, vencimento mais próximo)", "lote": "1 contrato = US$ 10 mil",
                 "custo": "R$ 4/contrato/lado + rolagem mensal"},
                {"onde": "Tesouro Direto / B3", "ticker": "Tesouro Selic (garantia ~R$ 5 mil/contrato)", "lote": "R$ ~170", "custo": "igual ao benchmark"}]
APLICAVEL = True
MOTIVO = ("Cabe em margem (R$ 4–6 mil), mas 1 WDO = R$ 50–60 mil de nocional: com R$ 20 mil é 2,5–3x de alavancagem (vol ~35–45% a.a.; "
          "um choque como mar/2020 levaria 40–50% do capital). Com R$ 50 mil, 1 contrato ≈ 1x. Não há micro-dólar na B3.")
ALAVANCAGENS = [1, 2]
MOTIVO_ALAV = ("Mínimo = 1 contrato (≈ 2,7x em R$ 20 mil, ≈ 1,1x em R$ 50 mil); 2x só em R$ 50 mil (2 contratos). 5x = 4–5 contratos: um "
               "movimento de 20% do dólar zera o capital.")


def carrega():
    y = B.yahoo_idx(("^VIX",))
    return {"wdo": B.futuros(["WDO"]), "vix": y["^VIX"].dropna().to_frame("vix"), "selic": B.selic_meta().to_frame(),
            "ipca": B.focus_ipca12m().to_frame(), "cftc": B.cftc("BRAZILIAN REAL").to_frame("liq")}


def _serie(d):
    return B.memo("wdo_sr", d["wdo"], lambda: B.serie_rolada(d["wdo"], B.vencimento_wdo, antes=3))


def sinal(d, vix=True, juro_real_min=4.0, cftc=False, vix_q=.8):
    """Liga/desliga decidido no fechamento de t com dados até t (VIX de t-1: fecha depois da B3; Focus com 3 pregões de defasagem)."""
    on = pd.Series(True, index=B.DIAS)
    if vix:
        v = d["vix"]["vix"]
        ok = (v < v.rolling(252, min_periods=120).quantile(vix_q)).astype(float).reindex(B.DIAS, method="ffill").shift(1)
        on &= ok.fillna(0) > 0
    if juro_real_min is not None and juro_real_min > -50:
        sel = d["selic"].iloc[:, 0].reindex(B.DIAS, method="ffill")
        ip = d["ipca"]["ipca12m"].reindex(B.DIAS, method="ffill").shift(3)
        on &= ((sel - ip) > juro_real_min).fillna(False)
    if cftc:
        c = d["cftc"]["liq"]
        ok = (c > c.rolling(26, min_periods=13).mean()).astype(float)
        ok = ok.reindex(B.DIAS.union(ok.index)).ffill().reindex(B.DIAS)
        on &= ok.fillna(0) > 0
    return on


def _livro(d, capital, lag, custo_mult, alavancagem, p):
    sr = _serie(d)
    noc = (sr.ajuste * MULT).ffill(limit=5)                           # dia sem ajuste (feriado só na B3) não zera a posição
    on = sinal(d, p["vix"], p["juro_real_min"], p["cftc"], p["vix_q"]) & noc.notna()
    n = -(np.maximum(1, np.round(capital * alavancagem / noc))).where(on, 0).fillna(0)
    pnl, ne, custo = B.livro_futuro(n, sr, MULT, CUSTO_LADO, lag, custo_mult)
    return pnl, ne, noc, sr


def excesso(d, capital=20000, custo_mult=1, lag=0, regime=REGIME, alavancagem=1, **params):
    pnl, *_ = _livro(d, capital, lag, custo_mult, alavancagem, {**PARAMS, **params})
    return B.fecha(pnl / capital, regime, CUSTO_TROCA, custo_mult)


def classes_ir(d, capital=20000, **params):
    pnl, *_ = _livro(d, capital, 0, 1, 1, {**PARAMS, **params})
    return {CLASSE_IR: pnl}


def posicoes(d, capital=20000, **params):
    pnl, ne, noc, sr = _livro(d, capital, 0, 0, 1, {**PARAMS, **params})
    ret = sr.dP / sr.ajuste.shift(1)                                   # contrato de ontem: ajuste(t-1) e variação até t
    return B.wr_futuro(ne, noc.ffill(), ret, capital, "WDO")


def negocios(d, capital=20000, **params):
    pnl, ne, noc, sr = _livro(d, capital, 0, 1, 1, {**PARAMS, **params})
    return B.negocios_df(B.blocos(ne, pnl, "WDO", capital, ne.abs() * noc, quebra=sr.ticker.ffill()), capital)   # 1 negócio por contrato
