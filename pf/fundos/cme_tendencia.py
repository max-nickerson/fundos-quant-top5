"""
Tendência multiativos com micros da CME — vol-alvo REALISTA com contratos inteiros.

Negócio: toda sexta, para cada micro (S&P, Nasdaq, Russell, ouro, prata, cobre, petróleo, euro, iene, yield de 10 anos), olho o retorno
em excesso dos últimos `janela` pregões dividido pela vol: positivo = comprado, negativo = vendido. Quem paga a tendência: quem ajusta
devagar — hedgers de commodity que rolam hedge por calendário, bancos centrais que sobem juros em passos de 25 bp, fundos de pensão que
rebalanceiam trimestralmente, investidor que entra depois de ler a notícia. É o "seguro de crise" barato: 2008, 2014 (petróleo), 2022
(juros e ações).
Tamanho (o ponto desta frente): com R$ 20 mil, 1 MES ≈ R$ 200 mil de nocional (10x o capital, vol ~R$ 30 mil/ano). Aloco contrato por
contrato, na ordem da força do sinal, enquanto a vol ex-ante da carteira (vol de 1 contrato em R$ x correlação de 1 ano) couber em
`alvo` x capital. Na prática R$ 20 mil compra 1-3 contratos dos micros PEQUENOS (1OZ, MCL, micro FX, 10Y, M2K) — é um fundo de tendência
concentrado, não diversificado. R$ 50 mil já carrega 3-6 posições.
Retornos: ETF - T-bill (+ taxa do ETF), moedas = spot + diferencial BIS, yield = FRED + carregamento (sem salto de rolagem).
"""
import numpy as np
import pandas as pd

import cme_comum as K

NOME = "Tendência multiativos com micros (CME)"
TESE = "Segue a tendência de 12 micros com contratos inteiros: compra o que sobe e vende o que cai, vol-alvo do patrimônio"
BENCHMARK = "CDI"
INICIO, CORTE = "2012-01-01", "2021-01-01"
REGIME = "nenhum"
CUSTO_TROCA = 0.0
UNIVERSO = ["MES", "MNQ", "M2K", "MGC", "1OZ", "SIL", "MHG", "MCL", "M6E", "MJY", "10Y"]
PARAMS = {"janela": 252, "alvo": .25}
GRADE = {"janela": [63, 126, 252], "alvo": [.15, .25]}
VIZINHANCA = {"janela": (150, 300), "alvo": (.18, .32)}
CLASSE_IR = "exterior"
APLICAVEL = True
MOTIVO = ("opera, mas com R$ 20 mil a carteira cabe só 1-3 contratos dos micros pequenos (1OZ, MCL, micro FX, 10Y, M2K): MES/MNQ/MGC/SIL "
          "sozinhos têm vol anual de 50-250% do capital e o algoritmo não os compra")
INSTRUMENTOS = [("IBKR/CME", a, f"x{K.ESPEC[a]['mult']}", f"US$ {K.custo_lado(a):.2f}/lado (comissão+meio spread)") for a in UNIVERSO]
ALAVANCAGENS = [1, 1.5, 2]
MOTIVO_ALAV = "alavancagem = vol-alvo x 1, 1,5, 2 (25%-50% do patrimônio); 5x = 125% de vol anual -> chamada de margem/quebra provável"


def gera(d, capital=20000, regime=REGIME, alavancagem=1, janela=252, alvo=.25):
    idx = K.dias_us(d)
    Kd = K.contratos(d, UNIVERSO, idx)
    R = pd.DataFrame({a: Kd[a]["r"] for a in UNIVERSO})
    V1 = pd.DataFrame({a: K.vol_contrato_brl(Kd[a]) for a in UNIVERSO})
    vol = R.rolling(63, min_periods=40).std() * np.sqrt(252)
    score = (np.log1p(R.fillna(0)).rolling(janela, min_periods=int(janela * .8)).sum() / (vol * np.sqrt(janela / 252)))
    score = score.where(R.rolling(janela).count() >= janela * .8)
    sexta = pd.Series(idx.to_period("W"), index=idx)
    sexta = sexta.ne(sexta.shift(-1)).values
    N = pd.DataFrame(np.nan, index=idx, columns=UNIVERSO)
    Rv = R.fillna(0).values
    orc = alvo * alavancagem * capital
    for i in np.where(sexta)[0]:
        if i < 260:
            continue
        s, v = score.iloc[i].fillna(0).values, V1.iloc[i].values
        with np.errstate(invalid="ignore", divide="ignore"):
            c = np.nan_to_num(np.corrcoef(Rv[i - 251:i + 1].T))
        np.fill_diagonal(c, 1)
        N.iloc[i] = K.inteiros_gulosos(s, v, c, orc, maxn=10)
    return N.ffill().fillna(0), Kd


K.montar(globals(), gera)
