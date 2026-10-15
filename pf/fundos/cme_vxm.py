"""
VXM vendido (mini futuro de VIX da Cboe, US$ 100 x VIX) com regime de contango/VVIX e stop — conta pequena.

Negócio: vendo o futuro de VIX de 1 (ou 2) meses quando a curva está em CONTANGO (VX2 > VX1 > VIX à vista) e o VVIX (vol da vol) não está
em alerta. O futuro de VIX embute um prêmio: quem compra (hedgers de carteira, ETNs como VXX/UVXY que rolam todo dia comprando o 2º
vencimento, mesas vendidas em opção que precisam de vega) paga mais do que o VIX que se realiza no vencimento; o futuro "desce a curva"
até o VIX à vista. Vender esse seguro paga ~1-1,5 ponto de VIX por mês em mercado calmo e perde 10-20 pontos em uma semana de crise
(fev/2018, mar/2020, ago/2024) — por isso: (1) só vendo com contango (curva invertida = crise em curso); (2) VVIX abaixo do percentil 80 de
1 ano; (3) stop: se o contrato segurado subir > stop em 5 pregões, saio e fico 10 pregões de fora.
Tamanho: contratos = piso(perda_max x capital / choque), choque = 10 pontos (1º venc.) ou 7 (2º venc.) x US$ 100 x PTAX — o tamanho é
dado pela perda que aceito numa semana de crise, não pela vol (que é baixa justamente antes da crise).
Resultado da escolha no IS (2012-2020): os filtros de contango/VVIX/stop PIORARAM o excesso (saem depois do pico e perdem a descida
da curva, que é onde o prêmio é maior) -> REGIME "nenhum" (sempre vendido no 1º vencimento). Ver pf/pesquisa/micro_cme.md.
Dados: ajustes diários de TODOS os vencimentos VX (Cboe CFE) — o P&L é do próprio contrato segurado até 5 pregões antes do vencimento
(sem salto de rolagem). VXM existe desde ago/2020; antes, VX/10 (hipotético). Custo US$ 5,5 por lado + rolagem mensal real.
"""
import numpy as np
import pandas as pd

import cme_comum as K

NOME = "VXM vendido (prêmio do futuro de VIX)"
TESE = "Vende o mini futuro de VIX quando a curva está em contango e o VVIX calmo; stop de 5 dias; tamanho pela perda numa crise"
BENCHMARK = "CDI"
INICIO, CORTE = "2012-01-01", "2021-01-01"
REGIME = "nenhum"                     # escolhido no IS junto com a grade (ver GRADE): o filtro de contango/VVIX PIORA o IS
CUSTO_TROCA = 0.0
PARAMS = {"venc": 1, "perda_max": .4, "cmin": 0.0, "stop": .2}            # melhor excesso IS (2012-2020) da grade abaixo
GRADE = {"regime": ["nenhum", "contango", "contango_vvix"], "venc": [1, 2], "perda_max": [.25, .4]}
VIZINHANCA = {"perda_max": (.3, .5)}
CLASSE_IR = "exterior"
FOLGA = 2.0                                       # VIX dobra a margem numa crise: saldo-alvo 2x o maior mês anterior
APLICAVEL = True
MOTIVO = ("opera com R$ 20 mil: 1 VXM ≈ US$ 1.700-2.000 de nocional, margem ~US$ 800 (≈ R$ 4 mil); 1 contrato = R$ 550 por ponto de VIX "
          "-> 1-2 contratos com R$ 20 mil, 2-5 com R$ 50 mil. VXM tem pouca liquidez (spread de 1-2 ticks = US$ 5-10)")
INSTRUMENTOS = [("IBKR/Cboe CFE", "VXM", "US$ 100 x VIX", "US$ 5,5/lado (comissão + ~1 tick)"),
                ("Tesouro Direto", "Tesouro Selic", "R$ ~150", "0")]
ALAVANCAGENS = [1, 1.5, 2]
MOTIVO_ALAV = ("alavancagem multiplica perda_max (30% -> 45%/60% do capital num choque de 7-10 pontos de VIX); 5x = perder 150% do "
               "capital num fev/2018 -> quebra")


def gera(d, capital=20000, regime=REGIME, alavancagem=1, venc=1, perda_max=.4, cmin=0.0, stop=.2):
    idx = K.dias_us(d)
    Kd = K.contratos(d, ["VXM"], idx, venc_ordem=venc)
    k = Kd["VXM"]
    p = d["precos"]
    vix = K.para(p["^VIX"].dropna(), idx, soma=False)
    vvix = K.para(p["^VVIX"].dropna(), idx, soma=False)
    on = pd.Series(1.0, index=idx)
    if regime in ("contango", "contango_vvix"):
        on = ((k["vx2"] / k["vx1"] - 1 >= cmin) & (k["vx1"] > vix)).astype(float)
        if regime == "contango_vvix":
            on = on * (vvix < vvix.rolling(252, min_periods=120).quantile(.8))
        # stop: contrato segurado subiu > stop em 5 pregões -> fora por 10 pregões
        alta5 = k["pc"].rolling(5).sum() / k["noc"].shift(5) > stop
        fora = alta5.astype(float).rolling(10, min_periods=1).max().fillna(0)
        on = on * (1 - fora)
    choque = 10.0 if venc == 1 else 7.0
    fx = K.PTAX_FULL.reindex(idx, method="ffill")
    n = np.floor(perda_max * alavancagem * capital / (choque * 100 * fx))
    N = pd.DataFrame({"VXM": -(n * on).fillna(0)}, index=idx)
    return N, Kd


K.montar(globals(), gera)
