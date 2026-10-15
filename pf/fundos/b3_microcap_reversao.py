"""
Reversão semanal em small/micro caps ilíquidas — o "formador de liquidez" que o institucional não consegue ser.

Mesa: em papéis com giro de R$ 30 mil a R$ 3 milhões/dia, quem precisa vender rápido (fundo com resgate, pessoa física em pânico, chamada
de margem) empurra o preço para baixo numa semana sem notícia; não há formador de mercado nem fundo grande para absorver (um fundo de
R$ 500 milhões não consegue montar R$ 5 milhões num papel que gira R$ 300 mil/dia). Quem é pequeno compra R$ 1–3 mil do perdedor da
semana e devolve a liquidez quando o preço volta. O custo é real: pago o meio spread do fechamento (melhor oferta de venda do COTAHIST)
na entrada e na saída, e só compro se o volume do dia for >= 10x a minha ordem.

Sinal (fechamento de t): retorno total de `janela` pregões; universo = ADV60 entre `adv_min` e `adv_max`, preço >= R$ 1, negociou em
>= 80% dos últimos 60 pregões, spread de fechamento <= `spread_max`; compra os `n` maiores perdedores (abaixo de -`queda_min`),
R$ capital/n por papel (teto R$ 3 mil para 20k... ver `por_papel`), revisão a cada `freq` pregões; quem continua na lista fica.
Execução no fechamento de t+1 (+lag). Dinheiro aplicado em ações não rende CDI (excesso = retorno do papel - CDI).
IR: swing trade de ações; meses com vendas <= R$ 20 mil isentos (raro aqui: o giro é semanal).
"""
import numpy as np
import pandas as pd

import b3_base as B

C, pf = B.C, B.pf

NOME = "Reversão semanal em micro caps ilíquidas (PF)"
TESE = ("Compro R$ 1-3 mil dos maiores perdedores da semana entre papéis que giram R$ 30 mil-3 mi/dia: vendedores forçados sem contraparte "
        "institucional derrubam o preço além do valor; o pequeno fornece liquidez e devolve quando o preço volta")
BENCHMARK = "CDI"
INICIO, CORTE = "2014-06-01", "2021-01-01"
REGIME = "nenhum"
CUSTO_TROCA = .001
PARAMS = {"janela": 5, "freq": 5, "n": 8, "adv_min": 3e4, "adv_max": 3e6, "queda_min": .05, "spread_max": .03, "por_papel": 2500.0}
GRADE = {"janela": [5, 10], "freq": [5, 10], "adv_max": [3e6, 2e7], "queda_min": [.05, .10]}
VIZINHANCA = {"janela": (4, 15), "freq": (4, 15), "n": (5, 12), "adv_max": (1e6, 1e7), "queda_min": (.03, .12), "spread_max": (.02, .05)}
INSTRUMENTOS = [{"onde": "Clear/Rico/XP/BTG (B3 à vista + fracionário)", "ticker": "small/micro caps (ADV R$ 30 mil-3 mi)", "lote": "1 ação (fracionário) / 100",
                 "custo": "emolumentos 0,03% + meio spread real do fechamento + 0,2% na parte fracionária"}]
APLICAVEL = True
MOTIVO = "ações à vista em qualquer corretora de varejo; ordens limitadas de R$ 1-3 mil; capacidade limitada pelo volume dos papéis (é o edge)"
ALAVANCAGENS = [1]
MOTIVO_ALAV = ("ações ilíquidas não servem de garantia relevante e conta margem/termo custam CDI + 4-8% a.a.; alavancar transformaria um "
               "edge de poucos pontos em prejuízo e aumentaria o impacto nos papéis")
_RES = {}


def carrega():
    return B.dados_acoes()


def _sinal(d, janela, adv_min, adv_max, queda_min, spread_max, n, freq):
    P, R, V, HS = d["P"], d["R"], d["V"], d["HS"]
    r = np.exp(np.log1p(R.fillna(0).clip(-.9, 5)).rolling(janela).sum()) - 1
    adv = V.fillna(0).rolling(60, min_periods=40).mean()
    pres = P.notna().rolling(60, min_periods=40).mean()
    hs = HS.where(P.notna()).rolling(10, min_periods=3).median()
    univ = (adv >= adv_min) & (adv <= adv_max) & (pres >= .8) & (P.ffill(limit=5) >= 1) & (hs <= spread_max / 2) & P.notna()
    s = (-r).where(univ & (r <= -queda_min))
    rk = s.rank(axis=1, ascending=False, method="first")
    sel = (rk <= n)
    marca = np.zeros(len(P), bool)
    marca[::max(int(freq), 1)] = True
    return sel, pd.Series(marca, index=P.index)


def roda(d, capital=20000, custo_mult=1, lag=0, janela=5, freq=5, n=8, adv_min=3e4, adv_max=3e6, queda_min=.05, spread_max=.03,
         por_papel=2500.0, teto_vendas=None):
    k = (id(d), capital, custo_mult, lag, janela, freq, n, adv_min, adv_max, queda_min, spread_max, por_papel, teto_vendas)
    if k in _RES:
        return _RES[k]
    sel, marca = _sinal(d, int(janela), adv_min, adv_max, queda_min, spread_max, int(n), int(freq))
    tam = min(por_papel * capital / 20000, .95 * capital / n)            # R$ 2,5 mil com 20k; R$ 6,2 mil com 50k (n=8)
    alvo = (sel.astype(float) * tam).where(marca, np.nan, axis=0)
    alvo = alvo.loc[:, sel.any()]

    res = B.carteira_pf(alvo, d, capital, custo_mult, lag, teto_vendas=teto_vendas)
    if len(_RES) > 64:
        _RES.clear()
    _RES[k] = res
    return res


def excesso(d, capital=20000, custo_mult=1, lag=0, regime=REGIME, alavancagem=1, **params):
    p = {**PARAMS, **params}
    e = roda(d, capital, custo_mult, lag, **p)["e"] * alavancagem
    return C.aplica_regime(e, regime, CUSTO_TROCA * custo_mult)


def classes_ir(d, capital=20000, **params):
    return B.classes_acoes(roda(d, capital, **{**PARAMS, **params}))


def posicoes(d, capital=20000, **params):
    res = roda(d, capital, **{**PARAMS, **params})
    W = res["W"]
    R = d["R"].reindex(index=B.DIAS, columns=W.columns).fillna(0).sub(B.CDI, axis=0)
    return W, R


def negocios(d, capital=20000, **params):
    return roda(d, capital, **{**PARAMS, **params})["negocios"]
