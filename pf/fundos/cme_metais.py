"""
Ouro, prata e cobre com micros da CME: pares de razão (prata x ouro, cobre x ouro) e sazonalidade do ouro.

Negócios:
  - "ouro_prata": a razão ouro/prata oscila em torno de uma média (prata = ouro com beta industrial). Quando a razão está > `entrada`
    desvios acima da média de 1 ano, compro prata (SIL, 1.000 oz) e vendo ouro (1OZ x h, mesmo nocional); abaixo, o contrário; saio
    quando volta a |z| < 0,5. Quem paga: fluxo de ETF/varejo em prata (exagera nas pontas) e produtores de prata como subproduto
    (oferta inelástica) — a razão volta porque o mesmo comprador marginal (banco central/ETF de ouro x indústria) não segura o desvio.
  - "cobre_ouro": cobre/ouro = termômetro de crescimento x medo. Desvio extremo (z) da razão costuma reverter quando o pânico passa
    (cobre vendido por CTAs/hedge de mineradoras) — MHG (2.500 lb) x 1OZ x h.
  - "sazonal_ouro": comprado em 1OZ de agosto a fevereiro (temporada de casamentos/festivais na Índia + compras antes do Ano Novo Chinês;
    joalheria é ~45% da demanda física), zerado de março a julho.
Tamanho: nº de pares = arredonda(alvo x capital / vol de 1 par em R$), por 63 dias. 1 par de prata = US$ 55-60 mil por perna (≈ 15x
R$ 20 mil) -> com R$ 20-50 mil o fundo de prata NÃO opera (nº de pares = 0); cobre/ouro (US$ 16 mil por perna) só com vol-alvo alta;
o sazonal com 1OZ (US$ 4 mil) cabe em qualquer conta.
Retornos: GLD/SLV/CPER − T-bill + taxa do ETF (sem salto de rolagem); nível GC=F/SI=F/HG=F só para tamanho.
"""
import numpy as np
import pandas as pd

import cme_comum as K

NOME = "Metais com micros: pares de razão e sazonalidade do ouro"
TESE = "Reversão da razão ouro/prata ou cobre/ouro com micros (perna de ouro em 1OZ) e ouro comprado na temporada de demanda física"
BENCHMARK = "CDI"
INICIO, CORTE = "2012-01-01", "2021-01-01"
REGIME = "nenhum"
CUSTO_TROCA = 0.0
INSTS = ["SIL", "MHG", "1OZ"]
PARAMS = {"modo": "sazonal_ouro", "entrada": 2.0, "alvo": .15}          # melhor excesso IS (2012-2020) da grade
GRADE = {"modo": ["ouro_prata", "cobre_ouro", "sazonal_ouro"], "entrada": [1.5, 2.0], "alvo": [.15, .25]}
VIZINHANCA = {"entrada": (1.25, 2.5), "alvo": (.12, .3)}
CLASSE_IR = "exterior"
APLICAVEL = True
MOTIVO = ("pares de prata não cabem (1 SIL ≈ US$ 56 mil = 15x R$ 20 mil: vol de 1 par > 100% do capital); cobre x ouro só com R$ 50 mil "
          "e vol-alvo alta; o sazonal com 1-OUNCE GOLD (1OZ, desde jan/2023, ≈ US$ 4 mil) opera com R$ 20 mil")
INSTRUMENTOS = [("IBKR/COMEX", "SIL", "1.000 oz", "US$ 5,85/lado"), ("IBKR/COMEX", "MHG", "2.500 lb", "US$ 2,10/lado"),
                ("IBKR/COMEX", "1OZ", "1 oz", "US$ 1,35/lado"), ("Tesouro Direto", "Tesouro Selic", "R$ ~150", "0")]
ALAVANCAGENS = [1, 1.5, 2]
MOTIVO_ALAV = "alavancagem = vol-alvo x 1/1,5/2; 5x não faz sentido (1OZ x 5 = 1x o capital em ouro já é ~5x a vol-alvo de 25%)"


def gera(d, capital=20000, regime=REGIME, alavancagem=1, modo="sazonal_ouro", entrada=2.0, alvo=.15):
    idx = K.dias_us(d)
    Kd = K.contratos(d, INSTS, idx)
    N = pd.DataFrame(0.0, index=idx, columns=INSTS)
    orc = alvo * alavancagem * capital
    fx = K.PTAX_FULL.reindex(idx, method="ffill")
    ouro = Kd["1OZ"]
    if modo == "sazonal_ouro":
        mes = idx.month
        on = pd.Series(np.isin(mes, [8, 9, 10, 11, 12, 1, 2]).astype(float), index=idx)
        on = on.shift(-2).fillna(0)        # calendário conhecido: decido em t a posição que rende 2 pregões depois (execução t+1)
        v1 = K.vol_contrato_brl(ouro)
        n = np.floor(orc / v1 + .5).clip(upper=20)
        N["1OZ"] = (n * on).fillna(0)
        return N, Kd
    a = "SIL" if modo == "ouro_prata" else "MHG"
    A = Kd[a]
    h = (A["noc"] / ouro["noc"]).round().clip(lower=1)            # 1OZ por contrato de A (mesmo nocional)
    ra, ro = A["r"], ouro["r"]
    razao = np.log(K.para(d["precos"][K.ESPEC[a]["nivel"]].dropna(), idx, soma=False) /
                   K.para(d["precos"]["GC=F"].dropna(), idx, soma=False))
    z = (razao - razao.rolling(252, min_periods=200).mean()) / razao.rolling(252, min_periods=200).std()
    # sinal da razão "metal / ouro": z muito alto -> vende metal/compra ouro; muito baixo -> compra metal/vende ouro
    lado = pd.Series(np.nan, index=idx)
    lado[z > entrada], lado[z < -entrada], lado[z.abs() < .5] = -1.0, 1.0, 0.0
    lado = lado.ffill().fillna(0)
    par = A["noc"].shift(1) * ra - h.shift(1) * ouro["noc"].shift(1) * ro          # P&L em US$ de 1 par (comprado na razão)
    vol_par = par.rolling(63, min_periods=40).std() * np.sqrt(252) * fx
    n = np.floor(orc / vol_par + .5).clip(upper=10).fillna(0)
    N[a] = lado * n
    N["1OZ"] = -lado * n * h
    return N.fillna(0), Kd


K.montar(globals(), gera)
