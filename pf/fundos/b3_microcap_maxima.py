"""
Micro caps perto da máxima de 52 semanas (e de vol baixa) — o que o institucional não consegue comprar.

Mesa: numa empresa pequena que entrega resultado, o preço sobe em degraus e passa meses perto da máxima do ano: o investidor ancora na
máxima ("já subiu demais"), a notícia se espalha devagar (pouca cobertura de analistas) e os fundos grandes não conseguem montar posição
num papel que gira R$ 100 mil-3 milhões/dia. Do outro lado, a micro cap que despenca raramente é "barganha": é empresa em crise
(recuperação judicial, aumento de capital, grupamento), que ninguém consegue vender a descoberto (sem aluguel) e que continua caindo —
o estudo da pesquisa mostrou que a reversão semanal em micro caps PERDE mesmo sem custo (ver b3_microcap_reversao).
Compro R$ 2,5 mil (20k) / R$ 6 mil (50k) de cada um dos `n` papéis do universo micro (ADV60 entre `adv_min` e `adv_max`, preço >= R$ 1,
negociou em >= 80% dos pregões, meio spread de fechamento <= 1,5%) mais perto da máxima de 252 pregões (sinal 'maxima'), ou com a melhor
combinação máxima + vol baixa ('maxima_vol') ou momento 12-1 ('momentum'). Revisão a cada `freq` pregões; quem ainda está no terço
superior do ranking fica (histerese: menos giro, menos spread e menos venda tributável).
Execução no fechamento de t+1 com o meio spread REAL e emolumentos; ações inteiras; dinheiro em ação não rende CDI.
IR: com giro mensal baixo, boa parte dos meses fica abaixo de R$ 20 mil de vendas (isento).
"""
import numpy as np
import pandas as pd

import b3_base as B

C, pf = B.C, B.pf

NOME = "Micro caps perto da máxima de 52 semanas (PF)"
TESE = ("Compro R$ 2-6 mil das micro caps (giro R$ 30 mil-3 mi/dia) mais perto da máxima do ano: notícia boa se espalha devagar onde não há "
        "analista nem fundo grande; as que despencam são crises sem vendedor a descoberto e continuam caindo")
BENCHMARK = "CDI"
INICIO, CORTE = "2015-03-01", "2021-01-01"
REGIME = "nenhum"
CUSTO_TROCA = .001
PARAMS = {"sinal": "maxima", "n": 8, "freq": 21, "adv_min": 3e4, "adv_max": 3e6, "manter": .33, "spread_max": .03, "por_papel": 2500.0}
GRADE = {"sinal": ["maxima", "maxima_vol", "momentum"], "freq": [21, 63], "adv_max": [3e6, 1e7]}
VIZINHANCA = {"n": (6, 12), "freq": (15, 42), "adv_max": (1.5e6, 6e6), "manter": (.2, .5), "spread_max": (.02, .05)}
INSTRUMENTOS = [{"onde": "Clear/Rico/XP/BTG (B3 à vista + fracionário)", "ticker": "micro caps (ADV R$ 30 mil-3 mi)", "lote": "1 ação",
                 "custo": "emolumentos 0,03% + meio spread real do fechamento + 0,2% na parte fracionária"}]
APLICAVEL = True
MOTIVO = "ações à vista em qualquer corretora; R$ 2-6 mil por papel cabem no volume diário (compra só se o volume do dia >= 10x a ordem)"
ALAVANCAGENS = [1]
MOTIVO_ALAV = "micro caps não servem de garantia e margem/termo custam CDI + 4-8% a.a.; o fundo é comprado à vista"
_RES = {}


def carrega():
    return B.dados_acoes()


def _score(d, sinal):
    P, R = d["P"], d["R"]
    lr = np.log1p(R.fillna(0).clip(-.9, 5))
    preco = np.exp(lr.cumsum())                                              # índice de preço ajustado (sem saltos de desdobramento)
    dist = np.log(preco / preco.rolling(252, min_periods=200).max())
    if sinal == "maxima":
        return dist
    if sinal == "momentum":
        return lr.rolling(231, min_periods=200).sum().shift(21)
    vol = lr.rolling(63, min_periods=40).std()
    return dist.rank(axis=1, pct=True) + (-vol).rank(axis=1, pct=True)


def roda(d, capital=20000, custo_mult=1, lag=0, sinal="maxima", n=8, freq=21, adv_min=3e4, adv_max=3e6, manter=.33, spread_max=.03,
         por_papel=2500.0, teto_vendas=None):
    k = (id(d), capital, custo_mult, lag, sinal, n, freq, adv_min, adv_max, manter, spread_max, por_papel, teto_vendas)
    if k in _RES:
        return _RES[k]
    P, V, HS = d["P"], d["V"], d["HS"]
    n, freq = int(n), int(freq)
    adv = V.fillna(0).rolling(60, min_periods=40).mean()
    pres = P.notna().rolling(60, min_periods=40).mean()
    hs = HS.where(P.notna()).rolling(10, min_periods=3).median()
    univ = (adv >= adv_min) & (adv <= adv_max) & (pres >= .8) & (P.ffill(limit=5) >= 1) & (hs <= spread_max / 2)
    s = _score(d, sinal).where(univ)
    pct = s.rank(axis=1, pct=True)
    rk = s.rank(axis=1, ascending=False, method="first")
    marca = pd.Series(np.arange(len(P)) % freq == 0, index=P.index) & (P.index >= pd.Timestamp(INICIO) - pd.Timedelta(days=40))
    tam = min(por_papel * capital / 20000, .95 * capital / n)
    alvo = ((rk <= n) & P.notna()).astype(float) * tam
    usados = alvo.columns[(alvo > 0).any()]
    alvo = alvo[usados].where(marca, np.nan, axis=0)
    mant = (pct >= 1 - manter)[usados].where(marca, False, axis=0)
    res = B.carteira_pf(alvo, d, capital, custo_mult, lag, teto_vendas=teto_vendas, manter=mant, apara=(2 * tam, tam))
    if len(_RES) > 64:
        _RES.clear()
    _RES[k] = res
    return res


def excesso(d, capital=20000, custo_mult=1, lag=0, regime=REGIME, alavancagem=1, **params):
    e = roda(d, capital, custo_mult, lag, **{**PARAMS, **params})["e"] * alavancagem
    return C.aplica_regime(e, regime, CUSTO_TROCA * custo_mult)


def classes_ir(d, capital=20000, **params):
    return B.classes_acoes(roda(d, capital, **{**PARAMS, **params}))


def posicoes(d, capital=20000, **params):
    W = roda(d, capital, **{**PARAMS, **params})["W"]
    return W, d["R"].reindex(index=B.DIAS, columns=W.columns).fillna(0).sub(B.CDI, axis=0)


def negocios(d, capital=20000, **params):
    return roda(d, capital, **{**PARAMS, **params})["negocios"]
