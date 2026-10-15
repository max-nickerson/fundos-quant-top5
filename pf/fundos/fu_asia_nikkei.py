"""
Ásia com micro: Nikkei 225 Micro (OSE, via IBKR) — compra no pânico japonês com o iene subindo (desmonte do carry trade + chamada de
margem do varejo japonês), reversão de curto prazo ou tendência.

Tese de mesa ("panico_iene"): no Japão o varejo opera muito alavancado (信用取引, conta margem com liquidação em D+2) e o mundo financia
posições em iene (carry trade). Quando o Nikkei cai forte E o iene sobe ao mesmo tempo (ex.: 5/ago/2024, −12% num dia), quem estava
vendido em iene e comprado em ações japonesas é forçado a desmontar, e o varejo recebe chamada de margem para D+2 e vende a qualquer
preço. Esse é o vendedor forçado; compro 1 micro depois de uma queda de k desvios em 5 dias com o USD/JPY caindo (iene forte) e seguro H
dias. Até 2024 o BoJ comprava ETF nas quedas da manhã (comprador "de política" do outro lado) — parou em mar/2024.

Contratos (fontes: JPX "Nikkei 225 Micro Futures" — multiplicador ¥10, tick 5 pts = ¥50, lançado em 29/mai/2023; IBKR margens OSE,
out/2026: N225MC margem inicial ~¥63,5 mil ≈ 9-10% do nocional; taxas OSE ¥1,1 + ¥0,2 por contrato):
  - Nikkei 225 Micro: ¥10 x Nikkei (~67.700 pts = ¥677 mil ≈ US$ 4,5 mil ≈ R$ 25 mil): 1 contrato ≈ 1,25x R$ 20 mil, 0,5x R$ 50 mil;
  - custo por lado: comissão IBKR ~¥30 + taxas ¥1,3 + meio tick ¥25 = ¥57; 4 rolagens/ano;
  - Mini-KOSPI 200 (KRX, KRW 50.000 x KOSPI 200 ≈ 860 pts = KRW 43 mi ≈ R$ 170 mil): a IBKR dá acesso (Eurex/KRX Link e KRX direto,
    exceto residentes da Coreia/Japão/Índia), mas 1 contrato = 8,5x R$ 20 mil e 3,4x R$ 50 mil -> NÃO cabe; fora da grade.
    Mini Nikkei (¥100, ≈ R$ 250 mil) e CME NKD/NIY também não cabem.
Retorno do futuro: Nikkei (preço) + 1,8% a.a. de dividendos − juro do BoJ (BIS); nível do Yahoo (^N225) só para o nocional. Antes de
mai/2023 o micro é hipotético (mesmo subjacente; o mini existia, mas 10x maior).
"""
import numpy as np
import pandas as pd

import fu_comum as F

NOME = "Nikkei 225 Micro (OSE): pânico com iene forte (carry + margem do varejo)"
TESE = "Compra 1 micro Nikkei depois de queda forte com o iene subindo (desmonte do carry e chamada de margem do varejo japonês), segura H dias"
BENCHMARK = "CDI"
INICIO, CORTE = "2008-01-01", "2021-01-01"
REGIME = "nenhum"
CUSTO_TROCA = 0.0
CLASSE_IR = "exterior"
PARAMS = {"modo": "panico_iene", "k": 2.0, "H": 5}          # maior excesso IS da grade (todos negativos no IS)
GRADE = {"modo": ["panico_iene", "reversao", "tendencia"], "k": [1.5, 2.0], "H": [5, 10]}
VIZINHANCA = {"k": (1.25, 2.25), "H": (4, 15)}
LANCAMENTO = {"N225MC": "2023-05-29"}
TETO_ALAV = 2.5
DIV, CUSTO_JPY, MULT = .018, 57.0, 10.0
INSTRUMENTOS = [("IBKR/OSE", "N225MC", "¥10 x Nikkei (≈ R$ 25 mil)", "¥57/lado"), ("Tesouro Direto", "Tesouro Selic", "caixa", "0")]
APLICAVEL = True
MOTIVO = ("Nikkei Micro cabe (≈ 1,25x R$ 20 mil; margem ≈ R$ 2,5 mil na IBKR); Mini-KOSPI 200 (≈ R$ 170 mil) e mini Nikkei (≈ R$ 250 mil) "
          "não cabem. Micro só existe desde mai/2023: antes o resultado é hipotético.")
ALAVANCAGENS = [1, 2]
MOTIVO_ALAV = "1 contrato ≈ 1,25x com R$ 20 mil; 2x = 2-4 contratos (teto 2,5x o capital)."


def carrega():
    return {"idx": F.ler("indices.parquet")[["^N225"]], "fx": F.ler("fx.parquet")[["JPY=X"]], "bis": F.ler("bis.parquet")[["JP"]]}


def _contrato(d):
    def f():
        px = d["idx"]["^N225"].dropna()
        idx = pd.bdate_range(px.index.min(), px.index.max())
        p = F.nivel(px, idx)
        dias = pd.Series(idx, index=idx).diff().dt.days.fillna(1)
        r = p.pct_change(fill_method=None).fillna(0) + DIV * dias / 365 - F.juro_dia(d["bis"]["JP"], idx)
        return F.contrato(r, p, MULT, "JPY", idx, d["fx"], CUSTO_JPY, .10, rol=4), p
    return F.memo("nikkei", (d["idx"], d["fx"], d["bis"]), f)


def gera(d, capital=20000, regime=REGIME, alavancagem=1, modo="panico_iene", k=1.5, H=10):
    K, p = _contrato(d)
    if modo == "panico_iene":
        jpy = F.nivel(d["fx"]["JPY=X"], p.index)                       # ienes por dólar: cai quando o iene se valoriza
        r = np.log(p).diff()
        z = r.rolling(5).sum() / (r.rolling(252, min_periods=150).std() * np.sqrt(5))
        gat = (z <= -k) & (np.log(jpy).diff(5) < 0)
        lado = F.segura(gat.astype(float), H)
    else:
        lado = F.sinal_indice(p, modo, k, H)
    n = F.n_por_exposicao(K, capital, alavancagem).clip(lower=1)
    n = n.where(K["noc"] * n <= TETO_ALAV * alavancagem * capital, 0)
    return pd.DataFrame({"N225MC": (lado * n).fillna(0)}, index=K.index), {"N225MC": K}


F.montar(globals(), gera, carrega)
