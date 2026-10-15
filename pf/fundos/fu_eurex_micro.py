"""
Eurex micro (IBKR): Micro-Euro STOXX 50 (FSXE) e Micro-DAX (FDXS) — compra no pânico europeu, reversão de curto prazo ou tendência.

Tese de mesa ("panico"): a Europa tem o maior estoque do mundo de produtos estruturados de varejo sobre o Euro STOXX 50 (autocalls,
reverse convertibles com barreira). Os bancos emissores ficam VENDIDOS em gama perto das barreiras: numa queda forte eles vendem futuro
de índice para se hedgear, junto com os fundos de vol-alvo/CTAs que cortam risco quando o V2X dispara. Esse é o vendedor forçado; quem
compra 1 micro depois de uma queda de k desvios em 5 dias COM o V2X no decil de cima de 1 ano e segura H dias recebe o prêmio de liquidez.
"reversao" (sem filtro de medo, compra e vende os extremos) e "tendencia" (média de 200 dias) entram na grade como controle.

Contratos (Eurex, especificação "Public Contract Specifications for Futures Contracts", circular 025/21; IBKR, out/2026):
  - FSXE: EUR 1 x Euro STOXX 50 (~6.200 pts = EUR 6,2 mil ≈ R$ 38 mil); tick 0,5 pt = EUR 0,50; lançado em mar/2021.
  - FDXS: EUR 1 x DAX (~25.300 pts = EUR 25 mil ≈ R$ 160 mil = 8x R$ 20 mil, 3x R$ 50 mil): NÃO CABE (teto de 2,5x o capital) —
    fica na grade como "inst" só para registrar que nunca opera.
  - custo por lado: comissão IBKR Eurex ~EUR 0,35 + taxas Eurex ~EUR 0,25 + meio spread 1 tick (micro pouco líquido fora do horário
    europeu) = EUR 1,10 (FSXE) / EUR 1,60 (FDXS); margem ~8% do nocional (IBKR ~EUR 500 por FSXE); 4 rolagens/ano.
Retorno do futuro: DAX é índice de RETORNO TOTAL -> r = DAX − juro do BCE; Euro STOXX 50 é de preço -> r = SX5E + 3% a.a. de dividendos
(média 2007-2026) − juro do BCE (BIS). Nível (Yahoo) só para o nocional. Antes de mar/2021 o micro é hipotético (mesmo subjacente).
Com R$ 20 mil, 1 FSXE = 1,9x o capital: exposição mínima é 1 contrato.
"""
import numpy as np
import pandas as pd

import fu_comum as F

NOME = "Eurex micro (FSXE/FDXS): pânico europeu, reversão ou tendência"
TESE = "Compra 1 micro Euro STOXX 50 depois de queda forte com o V2X no topo (bancos vendidos em gama e vol-alvo vendendo), segura H dias"
BENCHMARK = "CDI"
INICIO, CORTE = "2008-01-01", "2021-01-01"
REGIME = "nenhum"
CUSTO_TROCA = 0.0
CLASSE_IR = "exterior"
PARAMS = {"modo": "panico", "k": 2.0, "H": 5, "inst": "FSXE"}          # maior excesso IS (2008-2020) da grade com FSXE
GRADE = {"modo": ["panico", "reversao", "tendencia"], "k": [1.5, 2.0], "H": [5, 10]}
# FDXS fora da grade: com o DAX > 12 mil desde 2017 (EUR 12 mil+ = 3-8x R$ 20 mil) não cabe; testado à parte (IS +6 a +7,5 pp no pânico
# com o DAX barato de 2008-2012, OOS = 0 porque nunca opera) — escolher FDXS no IS seria escolher um contrato que hoje não cabe.
VIZINHANCA = {"k": (1.25, 2.25), "H": (4, 15)}
LANCAMENTO = {"FSXE": "2021-03-22", "FDXS": "2021-03-22"}
TETO_ALAV = 2.5
ESPEC = {"FSXE": dict(nivel="^STOXX50E", div=.03, custo=1.10), "FDXS": dict(nivel="^GDAXI", div=0.0, custo=1.60)}
INSTRUMENTOS = [("IBKR/Eurex", "FSXE", "EUR 1 x SX5E (≈ R$ 38 mil)", "EUR 1,10/lado"), ("IBKR/Eurex", "FDXS", "EUR 1 x DAX (≈ R$ 160 mil)", "EUR 1,60/lado"),
                ("Tesouro Direto", "Tesouro Selic", "caixa", "0")]
APLICAVEL = True
MOTIVO = ("FSXE cabe (1 contrato ≈ 1,9x R$ 20 mil, 0,8x R$ 50 mil, margem ~R$ 3 mil na IBKR); FDXS não cabe (8x R$ 20 mil) e nunca opera. "
          "Micros da Eurex só existem desde mar/2021: antes disso o resultado é hipotético.")
ALAVANCAGENS = [1, 2]
MOTIVO_ALAV = "1 contrato já é ~2x com R$ 20 mil; 2x = até 2 contratos com R$ 50 mil (teto 2,5x o capital)."


def carrega():
    return {"idx": F.ler("indices.parquet")[["^STOXX50E", "^GDAXI"]], "v2x": F.ler("v2x.parquet"), "fx": F.ler("fx.parquet")[["EURUSD=X"]],
            "bis": F.ler("bis.parquet")[["XM"]]}


def _contrato(d, inst):
    def f():
        e = ESPEC[inst]
        px = d["idx"][e["nivel"]].dropna()
        idx = pd.bdate_range(px.index.min(), px.index.max())
        p = F.nivel(px, idx)
        dias = pd.Series(idx, index=idx).diff().dt.days.fillna(1)
        r = p.pct_change(fill_method=None).fillna(0) + e["div"] * dias / 365 - F.juro_dia(d["bis"]["XM"], idx)
        return F.contrato(r, p, 1.0, "EUR", idx, d["fx"], e["custo"], .08, rol=4), p
    return F.memo(("eurex", inst), (d["idx"], d["fx"], d["bis"]), f)


def gera(d, capital=20000, regime=REGIME, alavancagem=1, modo="panico", k=1.5, H=10, inst="FSXE"):
    K, p = _contrato(d, inst)
    lado = F.sinal_indice(p, modo, k, H, d["v2x"]["V2TX"])
    n = F.n_por_exposicao(K, capital, alavancagem).clip(lower=1)
    n = n.where(K["noc"] * n <= TETO_ALAV * alavancagem * capital, 0)            # 1 contrato grande demais -> não opera
    N = pd.DataFrame({inst: (lado * n).fillna(0)}, index=K.index)
    return N, {inst: K}


F.montar(globals(), gera, carrega)
