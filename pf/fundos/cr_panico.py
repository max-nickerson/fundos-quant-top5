"""
(3) Pânico cripto: comprar depois de queda de 15%+ em 24h (liquidação em cascata dos alavancados) e vender em dias — o "leilão" da cripto.

Tese de mesa: a queda de 15-30% em 24h em cripto quase nunca é notícia de fluxo de caixa; é a cascata de liquidações dos perpétuos (o
vendedor forçado: a corretora fecha a posição do alavancado a mercado, sem olhar preço). Quando a cascata acaba, o livro reabre acima.
É o mesmo negócio do leilão de fechamento após queda forte na B3 (+5,7 pp na rodada 1): ser o comprador de quem é obrigado a vender.
Tamanho pequeno: o PF compra em R$ na corretora brasileira (Binance BR/MB), frações, com ISENÇÃO de IR até R$ 35 mil de vendas no mês.

Implementação (candles de 1h da Binance, ~85 pares USDT INCLUSIVE os que morreram — LUNA, FTT, SRM...; preço em R$ = USDT x USDTBRL):
  - universo ponto no tempo: `universo`="btceth" (só BTC e ETH) ou "top20" (20 maiores por volume em US$ dos 30 dias anteriores);
  - sinal no fechamento da hora t: retorno de 24h <= −queda; compra no fechamento da hora seguinte (t+1); `lag` adia 24h por unidade;
  - segura `dias` dias e vende; uma posição por moeda; peso `peso` do capital por posição (máx. 1/peso posições);
  - custos por lado: BTC/ETH 0,15% (taxa 0,10% + spread, par em R$); altcoins 0,35% (R$->USDT 0,10% + taxa 0,10% + spread 0,15%);
  - moeda deslistada/sem preço: sai no último preço (LUNA mai/2022 entra com a perda inteira até a deslistagem).
O dinheiro em cripto não rende CDI. Alfa vs BTC reportado à parte (regressão do excesso contra o BTC em R$).
"""
import numpy as np
import pandas as pd

import cr_comum as K

NOME = "Pânico cripto: compra após queda de 15%+ em 24h (liquidações), vende em dias"
TESE = "compro em R$ a moeda que caiu 15%+ em 24h por liquidação de alavancados e vendo dias depois; isento até R$ 35 mil/mês"
BENCHMARK = "CDI"
INICIO, CORTE = "2018-01-01", "2023-01-01"
REGIME = "nenhum"
CUSTO_TROCA = .0
CLASSE_IR = "cripto"
PARAMS = {"queda": .20, "dias": 2, "universo": "btceth", "peso": .2}   # maior IR no IS (top20 .20/2 é o 2º: ver caderno)
GRADE = {"queda": [.10, .15, .20], "dias": [2, 5, 10], "universo": ["btceth", "top20"]}
VIZINHANCA = {"queda": (.12, .20), "dias": (3, 8), "peso": (.15, .25)}
INSTRUMENTOS = [{"onde": "Binance BR / Mercado Bitcoin", "ticker": "BTCBRL, ETHBRL, <alt>USDT via USDTBRL", "lote": "fração",
                 "custo": "0,15% (BTC/ETH) / 0,35% (alts) por lado"}]
APLICAVEL = True
MOTIVO = "à vista em corretora brasileira, frações; ordem a mercado na hora seguinte ao sinal (alerta de preço no celular)"
ALAVANCAGENS = [1]
MOTIVO_ALAV = "corretora brasileira não dá margem (a Binance cortou margem a brasileiros em 10/2026); 1/peso posições já usam o PL"
TOPN = 20


def carrega():
    x = K.ler("binance_1h.parquet")
    return {"h": x.set_index("t")}


def _paineis(d):
    x = d["h"].reset_index()
    P = K.painel_1h("fech", {"h": x})
    V = K.painel_1h("vol_usd", {"h": x})
    P = P.reindex(pd.date_range(P.index[0], P.index[-1], freq="h"))
    V = V.reindex(P.index)
    P = K.mata_saltos(P.where(P > 0))
    return P, V


def _simula(d, capital, custo_mult, lag, queda, dias, universo, peso, alavancagem=1):
    P, V = _paineis(d)
    cols = list(P.columns)
    R = P / P.shift(1) - 1
    r24 = P / P.shift(24) - 1
    if universo == "btceth":
        eleg = pd.DataFrame(False, index=P.index, columns=cols)
        eleg[["BTC", "ETH"]] = True
    else:
        vol30 = V.fillna(0).rolling(720, min_periods=240).sum()
        eleg = vol30.rank(axis=1, ascending=False) <= TOPN
    sig = (r24 <= -queda) & eleg & P.notna()
    S = sig.values
    T, N = S.shape
    W = np.zeros((T, N))
    fim = np.full(N, -1)
    H = int(round(dias * 24))
    maxpos = int(round(1 / peso))
    abertas = []
    for i in np.where(S.any(axis=1))[0]:
        abertas = [j for j in abertas if fim[j] > i]
        for j in np.where(S[i])[0]:
            if fim[j] > i or len(abertas) >= maxpos:
                continue
            fim[j] = i + H
            W[i:min(i + H, T), j] = peso * alavancagem
            abertas.append(j)
    W = pd.DataFrame(W, index=P.index, columns=cols)
    custo = pd.Series({c: (.0015 if c in ("BTC", "ETH") else .0035) for c in cols})
    fxr = K.fx_horario(P.index)
    fxr = fxr / fxr.shift(1) - 1
    M = K.motor(W, R, capital, custo, lag_passos=1 + 24 * lag, custo_mult=custo_mult, fx_r=fxr)
    M["R"] = R
    return M


def excesso(d, capital=20000, custo_mult=1, lag=0, regime=REGIME, alavancagem=1, **params):
    p = {**PARAMS, **params}
    M = _simula(d, capital, custo_mult, lag, p["queda"], p["dias"], p["universo"], p["peso"], alavancagem)
    e, _ = K.excesso_spot(M, capital)
    e = e.where(e.index >= pd.Timestamp(INICIO), 0)
    return K.C.aplica_regime(e, regime, CUSTO_TROCA * custo_mult)


def _ativos(M):
    return [c for c in M["E"].columns if (M["E"][c] != 0).any()]


def posicoes(d, capital=20000, **params):
    p = {**PARAMS, **params}
    M = _simula(d, capital, 1, 0, p["queda"], p["dias"], p["universo"], p["peso"])
    a = _ativos(M)
    return K.W_com_vendas(M["V"][a], M["R"][a], capital)


def negocios(d, capital=20000, **params):
    p = {**PARAMS, **params}
    M = _simula(d, capital, 1, 0, p["queda"], p["dias"], p["universo"], p["peso"])
    a = _ativos(M)
    return K.negocios_blocos(M["E"][a], M["pnl"][a], capital, M["R"][a])


if __name__ == "__main__":
    import time
    t0 = time.time()
    d = carrega()
    e = excesso(d)
    print(time.time() - t0)
    print(e.groupby(e.index.year).sum() * 100)
    n = negocios(d)
    print(len(n), n.sort_values("contrib_pp").tail(5).to_string(), n.sort_values("contrib_pp").head(5).to_string())
