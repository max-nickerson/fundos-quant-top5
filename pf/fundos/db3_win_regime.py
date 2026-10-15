"""
Mini-índice (WIN), 1 contrato: tendência ou reversão de curto prazo com filtro de regime (VIX), garantia em Tesouro Selic.

Tese de mesa: o Ibovespa é dominado por fluxo estrangeiro, que entra e sai em ondas (meses) — tendência; e o varejo/tesouraria
reagem demais a choques de poucos dias (fiscal, Petrobras, eleição) — reversão de 5 dias. O WIN é o único jeito de o pequeno ficar
VENDIDO no índice sem alugar ações: 0,2 x Ibovespa por contrato (R$ 20–40 mil), margem ~R$ 2–4 mil em Selic, IR 15% em swing.
Regime: com o VIX acima do percentil 80 de 1 ano (aversão a risco global) NÃO fico comprado — é quando o estrangeiro vende.

Implementação: preço do WIN aproximado pelo Ibovespa (^BVSP, índice de retorno total): o futuro rende Ibovespa − CDI por dia
(F = Ibov x (1+CDI)^T, sem dividendos a descontar porque o índice já os reinveste), então o P&L de n contratos = n x 0,2 x Ibov(t−1) x
(r_ibov − CDI). Sem salto de rolagem (a série é o próprio índice); a rolagem é cobrada como custo: 2 lados por contrato nos vencimentos
(quarta-feira mais próxima do dia 15 dos meses pares). Custo R$ 1,10/contrato/lado (emolumentos + meio tick de 5 pontos).
Contratos inteiros: n = max(1, arred(capital x alav / (0,2 x Ibov))) quando há sinal. Dados 2005+, corte 2021.
Ressalva: o ^BVSP fecha no leilão de fechamento; o ajuste do WIN é calculado no mesmo horário — diferença pequena, sem viés de direção.
"""
import numpy as np
import pandas as pd

import db3_base as B

NOME = "Mini-índice WIN 1 contrato: tendência/reversão com regime VIX"
TESE = "1 WIN comprado/vendido conforme a tendência (média móvel) ou reversão de 5 dias do Ibovespa; sem compra com VIX alto"
BENCHMARK = "CDI"
INICIO, CORTE = "2010-01-01", "2021-01-01"
REGIME, CUSTO_TROCA = "nenhum", 0.0
PARAMS = {"modo": "reversao", "janela": 200, "vix": False, "z": 1.0}      # maior IR no IS (2010–2020) da GRADE
GRADE = {"modo": ["tend_ls", "tend_lf", "reversao"], "janela": [50, 200], "vix": [False, True]}
VIZINHANCA = {"janela": (140, 260), "z": (.7, 1.5)}
CLASSE_IR = "futuros_b3"
MULT, CUSTO_LADO = .2, 1.10
INSTRUMENTOS = [{"onde": "B3", "ticker": "WIN (mini-Ibovespa, vencimento par mais próximo)", "lote": "1 contrato = 0,2 x Ibovespa",
                 "custo": "R$ 1,10/contrato/lado + rolagem bimestral"},
                {"onde": "Tesouro Direto / B3", "ticker": "Tesouro Selic (margem ~R$ 2–4 mil)", "lote": "R$ ~170", "custo": "igual ao benchmark"}]
APLICAVEL = True
MOTIVO = "Cabe: 1 WIN = R$ 13–41 mil de nocional (0,7–2x com R$ 20 mil; 0,3–0,8x com R$ 50 mil), margem ~10% em Selic."
ALAVANCAGENS = [1, 1.5, 2]
MOTIVO_ALAV = "1 contrato já é 1–2x em R$ 20 mil; 2 contratos em R$ 50 mil ≈ 1,6x. 5x = vol de ~100% a.a.: não."


def venc_win(ano):
    out = []
    for m in (2, 4, 6, 8, 10, 12):
        alvo = pd.Timestamp(ano, m, 15)
        qs = pd.date_range(alvo - pd.Timedelta(days=6), alvo + pd.Timedelta(days=6), freq="W-WED")
        q = min(qs, key=lambda x: abs((x - alvo).days))
        x = B.DIAS[B.DIAS >= q]
        out.append(x[0] if len(x) else q)
    return out


VENC = pd.DatetimeIndex(sorted(v for a in range(2005, 2028) for v in venc_win(a)))


def carrega():
    y = B.yahoo_idx(("^BVSP", "^VIX"))
    return {"ibov": y["^BVSP"].dropna().to_frame("ibov"), "vix": y["^VIX"].dropna().to_frame("vix")}


def _livro(d, capital, lag, custo_mult, alavancagem, p):
    ib = d["ibov"]["ibov"].reindex(B.DIAS).ffill(limit=5)
    r = ib.pct_change(fill_method=None).fillna(0)
    jan = int(p["janela"])
    if p["modo"] in ("tend_ls", "tend_lf"):
        mm = ib.rolling(jan, min_periods=int(jan * .8)).mean()
        sig = np.sign(ib - mm).fillna(0)
        if p["modo"] == "tend_lf":
            sig = sig.clip(lower=0)
    else:                                                    # reversão: movimento de 5 dias > z desvios -> aposta contra, por 5 dias
        vol = r.rolling(jan, min_periods=int(jan * .8)).std() * np.sqrt(5)
        r5 = ib / ib.shift(5) - 1
        gat = (-np.sign(r5)).where(r5.abs() > p["z"] * vol, 0).fillna(0)
        sig = gat.replace(0, np.nan).ffill(limit=4).fillna(0)
    if p["vix"]:
        v = d["vix"]["vix"]
        alto = (v > v.rolling(252, min_periods=120).quantile(.8)).astype(float).reindex(B.DIAS, method="ffill").shift(1).fillna(0) > 0
        sig = sig.where(~(alto & (sig > 0)), 0)
    noc1 = MULT * ib
    n = (sig * np.maximum(1, np.round(capital * alavancagem / noc1))).where(ib.notna(), 0).fillna(0)
    ne = n.shift(1 + lag).fillna(0)
    bruto = ne.shift(1).fillna(0) * noc1.shift(1) * (r - B.CDI)
    rola = pd.Series(B.DIAS.isin(VENC), index=B.DIAS).shift(-2, fill_value=False)       # rola 2 pregões antes do vencimento
    giro = ne.diff().abs().fillna(ne.abs()) + 2 * ne.abs() * rola
    pnl = bruto.fillna(0) - giro * CUSTO_LADO * custo_mult
    return pnl, ne, noc1, r - B.CDI


def excesso(d, capital=20000, custo_mult=1, lag=0, regime=REGIME, alavancagem=1, **params):
    pnl, *_ = _livro(d, capital, lag, custo_mult, alavancagem, {**PARAMS, **params})
    return B.fecha(pnl / capital, regime, CUSTO_TROCA, custo_mult)


def classes_ir(d, capital=20000, **params):
    pnl, *_ = _livro(d, capital, 0, 1, 1, {**PARAMS, **params})
    return {CLASSE_IR: pnl}


def posicoes(d, capital=20000, **params):
    pnl, ne, noc, ret = _livro(d, capital, 0, 0, 1, {**PARAMS, **params})
    return B.wr_futuro(ne, noc.ffill(), ret, capital, "WIN")


def negocios(d, capital=20000, **params):
    pnl, ne, noc, _ = _livro(d, capital, 0, 1, 1, {**PARAMS, **params})
    return B.negocios_df(B.blocos(ne, pnl, "WIN", capital, ne.abs() * noc), capital)
