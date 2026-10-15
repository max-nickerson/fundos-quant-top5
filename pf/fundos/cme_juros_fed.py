"""
Juros dos EUA pelo ciclo do Fed com Micro Treasury Yield (10Y e 2YY: US$ 10 por bp, 1 contrato ≈ R$ 55 por bp).

Negócio: "comprar o PU que vai subir". O Fed anda em ciclos longos e em passos de 25 bp; o mercado de 2 anos costuma precificar o ciclo
TARDE (no começo de 2022 a curva precificava 3 altas e vieram 17 passos de 25 bp; em 2019 e 2024 os cortes vieram mais e antes do que a
curva dizia no início). Quem paga: tesourarias e bancos que carregam títulos pelo carrego (compram yield alto por contabilidade, não por
visão), hedgers de hipoteca que precisam vender duration quando os juros sobem (convexidade negativa amplifica a tendência).
  - regra "ciclo": se o Fed funds efetivo subiu >= 25 bp nos últimos 6 meses -> COMPRADO em yield (vendido no título); caiu >= 25 bp ->
    VENDIDO em yield (comprado no título); senão zerado.
  - "ciclo_tend": idem, mas só se o yield do vencimento estiver do mesmo lado da sua média de `janela` pregões (o mercado confirma).
  - "precificado_tend": sem esperar o Fed — usa o 2 anos menos o Fed funds (o que o mercado precifica para 2 anos) + a tendência:
    2y − FF < −25 bp e yield abaixo da média -> vendido em yield; 2y − FF > +25 bp e acima da média -> comprado.
Carregamento: o futuro de yield embute o carrego do título — vendido em yield (comprado no título) ganha (yield − Fed funds)/duração por
ano; com curva invertida (2023) PAGA ~40 bp/ano no 2 anos. Isso entra no P&L.
Tamanho: n = arredonda(alvo x capital / vol anual de 1 contrato); 1 contrato do 2 anos ≈ R$ 4-6 mil de vol/ano (≈ 25% de R$ 20 mil).
"""
import numpy as np
import pandas as pd

import cme_comum as K

NOME = "Juros EUA pelo ciclo do Fed (micro yield 2Y/10Y)"
TESE = "Vendido no título (comprado em yield) quando o Fed sobe e comprado quando corta, confirmado pela tendência do próprio yield"
BENCHMARK = "CDI"
INICIO, CORTE = "2012-01-01", "2021-01-01"
REGIME = "nenhum"
CUSTO_TROCA = 0.0
PARAMS = {"tenor": "2YY", "regra": "ciclo_tend", "janela": 63, "alvo": .2}
GRADE = {"tenor": ["2YY", "10Y"], "regra": ["ciclo", "ciclo_tend", "precificado_tend"]}
VIZINHANCA = {"janela": (40, 100), "alvo": (.15, .3)}
CLASSE_IR = "exterior"
APLICAVEL = True
MOTIVO = ("opera com R$ 20 mil: margem ~US$ 300-400 por contrato; 1 contrato de 2 anos tem vol de ~25% do capital. Micro Treasury Yield "
          "tem pouca liquidez fora do vencimento corrente (rolagem mensal)")
INSTRUMENTOS = [("IBKR/CME", "2YY", "US$ 10/bp", "US$ 1,62/lado"), ("IBKR/CME", "10Y", "US$ 10/bp", "US$ 1,62/lado"),
                ("Tesouro Direto", "Tesouro Selic", "R$ ~150", "0")]
ALAVANCAGENS = [1, 1.5, 2]
MOTIVO_ALAV = "vol-alvo x 1/1,5/2; 5x = 4-5 contratos do 10 anos com R$ 20 mil: um dia como o CPI de jun/2022 (+30 bp) custa 30% do capital"


def gera(d, capital=20000, regime=REGIME, alavancagem=1, tenor="2YY", regra="ciclo_tend", janela=63, alvo=.2):
    idx = K.dias_us(d)
    Kd = K.contratos(d, [tenor], idx)
    p = d["precos"]
    ff = K.para(p["DFF"].dropna(), idx, soma=False).shift(1)            # Fed funds efetivo sai no dia seguinte (NY Fed, 9h)
    y = K.para(p[K.ESPEC[tenor]["yld"]].dropna(), idx, soma=False)
    y2 = K.para(p["DGS2"].dropna(), idx, soma=False)
    ciclo = ff - ff.shift(126)
    tend = np.sign(y - y.rolling(janela, min_periods=int(janela * .8)).mean())
    sinal = pd.Series(0.0, index=idx)
    alta, corte = ciclo >= .25, ciclo <= -.25
    if regra == "ciclo":
        sinal[alta], sinal[corte] = 1.0, -1.0
    elif regra == "ciclo_tend":
        sinal[alta & (tend > 0)], sinal[corte & (tend < 0)] = 1.0, -1.0
    else:
        prec = y2 - ff
        sinal[(prec > .25) & (tend > 0)], sinal[(prec < -.25) & (tend < 0)] = 1.0, -1.0
    v1 = K.vol_contrato_brl(Kd[tenor])
    n = np.floor(alvo * alavancagem * capital / v1 + .5).clip(upper=20).fillna(0)
    return pd.DataFrame({tenor: sinal * n}, index=idx), Kd


K.montar(globals(), gera)
