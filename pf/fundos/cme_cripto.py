"""
Micro bitcoin / micro ether da CME (MBT = 0,1 BTC; MET = 0,1 ETH): tendência pagando a base, com filtro de euforia da base.

Negócio: cripto não tem fluxo de caixa; o preço anda por ondas de entrada de dinheiro novo (varejo, ETFs desde 2024, tesourarias) que
duram semanas/meses — tendência é o efeito mais documentado. Com futuro, quem está comprado PAGA a base (contango de 5-15% a.a.; >25%
nas euforias de 2021): o lado vendido é o "banco" que financia o comprado alavancado. Então:
  - comprado quando o retorno de `janela` dias é positivo, MAS só se a base anualizada estiver abaixo de `base_max` (base muito alta =
    alavancagem de varejo no topo e carregamento caro);
  - lado="ls": vendido quando a tendência é negativa (o vendido RECEBE a base).
Tamanho: contratos inteiros com vol-alvo (`alvo` x capital). MBT ≈ US$ 8 mil (≈ R$ 44 mil, vol 50% -> R$ 22 mil/ano = 110% de R$ 20 mil)
-> com R$ 20 mil, na prática só MET (≈ US$ 240, vol 70% -> R$ 900/ano por contrato: dá para dosar).
"Fim de semana": o CME fecha sábado/domingo; o movimento do fim de semana entra na segunda (o spot do Yahoo agrega isso). Não há
retorno extra em operar o gap (testado na pesquisa anterior: arbitragem de base cripto zerava com margem e contraparte).
Retorno do futuro = spot − base anualizada (Binance trimestral + 1 p.p.; 5% a.a. antes de ago/2020). Margem ~40% (CME + IBKR).
"""
import numpy as np
import pandas as pd

import cme_comum as K

NOME = "Micro BTC/ETH: tendência pagando a base"
TESE = "Comprado em MET/MBT quando a tendência é de alta e a base não está eufórica; vendido (recebendo a base) na tendência de baixa"
BENCHMARK = "CDI"
INICIO, CORTE = "2018-03-01", "2023-01-01"
REGIME = "nenhum"
CUSTO_TROCA = 0.0
INSTS = ["MBT", "MET"]
PARAMS = {"janela": 50, "lado": "long", "alvo": .2, "base_max": .25}
GRADE = {"janela": [20, 50, 100], "lado": ["long", "ls"]}
VIZINHANCA = {"janela": (35, 80), "alvo": (.15, .3), "base_max": (.15, .4)}
CLASSE_IR = "exterior"
FOLGA = 2.0
APLICAVEL = True
MOTIVO = ("opera com R$ 20 mil só via MET (0,1 ETH ≈ US$ 240); MBT (0,1 BTC ≈ US$ 8 mil) entra só quando a vol cabe (R$ 50 mil+). "
          "Margem de cripto ~40% do nocional, fins de semana sem negociação no CME")
INSTRUMENTOS = [("IBKR/CME", "MBT", "0,1 BTC", "US$ 3,50/lado"), ("IBKR/CME", "MET", "0,1 ETH", "US$ 0,75/lado"),
                ("Tesouro Direto", "Tesouro Selic", "R$ ~150", "0")]
ALAVANCAGENS = [1, 1.5, 2]
MOTIVO_ALAV = "vol-alvo x 1/1,5/2 (20-40%); 5x = 100% de vol anual em cripto -> quedas de 60-80% do patrimônio (2018, 2022)"


def gera(d, capital=20000, regime=REGIME, alavancagem=1, janela=50, lado="long", alvo=.2, base_max=.25):
    idx = K.dias_us(d)
    Kd = K.contratos(d, INSTS, idx)
    N = pd.DataFrame(0.0, index=idx, columns=INSTS)
    orc = alvo * alavancagem * capital
    R = pd.DataFrame({a: Kd[a]["r"] for a in INSTS})
    V1 = pd.DataFrame({a: K.vol_contrato_brl(Kd[a]) for a in INSTS})
    tend = np.log1p(R.fillna(0)).rolling(janela, min_periods=janela).sum()
    base = pd.DataFrame({a: K.base_cripto(d, K.ESPEC[a]["spot"][:3], idx) for a in INSTS})
    sinal = np.sign(tend)
    sinal = sinal.where(~((sinal > 0) & (base > base_max)), 0)
    if lado == "long":
        sinal = sinal.clip(lower=0)
    sexta = pd.Series(idx.to_period("W"), index=idx)
    sexta = sexta.ne(sexta.shift(-1)).values
    Rv = R.fillna(0).values
    for i in np.where(sexta)[0]:
        if i < 60 or not np.isfinite(V1.iloc[i].values).any():
            continue
        c = np.corrcoef(Rv[max(i - 251, 0):i + 1].T)
        N.iloc[i] = K.inteiros_gulosos(sinal.iloc[i].fillna(0).values, V1.iloc[i].values, np.nan_to_num(c), orc, maxn=40)
    N.loc[~sexta] = np.nan
    return N.ffill().fillna(0), Kd


K.montar(globals(), gera)
