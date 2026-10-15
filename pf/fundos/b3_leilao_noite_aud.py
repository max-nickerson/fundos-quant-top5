"""AUDITORIA (pf/pesquisa/auditoria_pf.md): igual a b3_leilao_noite.py, mas o custo por lado = emolumentos 0,03% + 1 bp de
derrapagem de leilão (ordem a mercado no call: o preço do COTAHIST nem sempre é o do leilão, prorrogação, desequilíbrio) = 8 bps ida e volta.
Cada bp por lado custa ~2,3 pp a.a. (o fundo vira negativo com 12 bps ida e volta).
"""
"""
Leilão de fechamento -> leilão de abertura: carregar a NOITE de ações líquidas que apanharam no dia (o "tug of war" B3).

Mesa: nas ações líquidas da B3 o retorno acontece de noite. De 2014 a 2026, comprar no leilão de fechamento e vender no leilão de
abertura rendeu +8 a +13 bps por noite em média, enquanto o pregão (abertura -> fechamento) PERDEU -5 a -10 bps: quem opera de dia
(day traders, mesas que zeram posição, algoritmos de execução que compram ao longo do dia) paga para ter liquidez intradiária e devolve no
fechamento; a notícia corporativa e o exterior entram na abertura. Depois de um dia de queda forte (retorno do papel <= -`limiar`
abaixo da média das ações líquidas), a noite seguinte é ainda melhor (+20 a +27 bps): quem foi stopado/zerado vendeu no pregão, e a
abertura devolve. Pessoa física com R$ 20-50 mil entra e sai nos LEILÕES (sem spread: o preço é único para todos), com corretagem zero;
pagando só emolumentos (0,03% por lado) o custo de ida e volta é ~6 bps — o institucional grande move o leilão; o pequeno não.
Regras: decisão no fechamento de t; compra no leilão de fechamento de t+1+lag (ordem a mercado no call de fechamento) e vende no leilão
de abertura do pregão seguinte. Universo: ADV60 >= `adv_min` (Ibovespa líquido). Até `n` papéis por noite, capital/n cada (ações
inteiras). Variante 'todos': carrega toda noite os `n` papéis mais líquidos (o prêmio de noite incondicional).
Retorno da noite = (1 + retorno total do dia seguinte) / (1 + retorno abertura->fechamento) - 1 (inclui o provento na data ex).
Dinheiro fora do CDI: o capital usado na noite (liquidação D+2 dos dois lados: na prática o dinheiro fica preso 1 dia útil por noite).
IR: swing trade (compra e venda em pregões diferentes) — vendas do mês muito acima de R$ 20 mil, então 15%.
"""
import numpy as np
import pandas as pd

import b3_base as B

C, pf = B.C, B.pf

NOME = "Noite nos leilões após queda forte (PF) — AUDITADA (8 bps ida e volta)"
SLIP = .0001                     # AUDITORIA: derrapagem por lado no leilão
TESE = ("Compro no leilão de fechamento as ações líquidas que caíram >= 2-4% abaixo do mercado no dia anterior e vendo no leilão de abertura: "
        "o prêmio da B3 está na noite (o pregão devolve), e é maior depois de vendas forçadas; no leilão o pequeno não paga spread")
BENCHMARK = "CDI"
INICIO, CORTE = "2014-06-01", "2021-01-01"
REGIME = "nenhum"
CUSTO_TROCA = .001
PARAMS = {"modo": "queda", "limiar": .03, "n": 4, "adv_min": 5e7}
GRADE = {"modo": ["queda", "todos"], "limiar": [.02, .04], "n": [2, 5]}
VIZINHANCA = {"limiar": (.015, .05), "n": (2, 8), "adv_min": (2e7, 1e8)}
INSTRUMENTOS = [{"onde": "Clear/Rico/XP/BTG (B3 à vista, ordens nos leilões de fechamento e abertura)", "ticker": "ações líquidas do Ibovespa",
                 "lote": "1 ação (fracionário também tem leilão) / 100", "custo": "emolumentos 0,03% por lado; sem spread (preço único do leilão)"}]
APLICAVEL = True
MOTIVO = "ordens a mercado no call de fechamento (16h55-17h) e de abertura (9h45-10h) em qualquer home broker; exige operar todo dia"
ALAVANCAGENS = [1, 1.5, 2]
MOTIVO_ALAV = ("as ações compradas no fechamento servem de garantia e a venda na abertura liquida em D+2 junto com a compra (o saldo fica "
               "negativo só intradiariamente); 2x = comprar o dobro do capital, possível com limite operacional da corretora")
_RES = {}


def carrega():
    return B.painel("P", "R", "O", "V")


def roda(d, capital=20000, custo_mult=1, lag=0, modo="queda", limiar=.03, n=4, adv_min=5e7, alavancagem=1.0):
    key = (id(d), capital, custo_mult, lag, modo, limiar, n, adv_min, alavancagem)
    if key in _RES:
        return _RES[key]
    P, R, O, V = d["P"], d["R"], d["O"], d["V"]
    cols = [c for c in P.columns if c[-1] in "345678" or c.endswith("11")]
    P, R, O, V = P[cols], R[cols], O[cols], V[cols]
    n = int(n)
    adv = V.fillna(0).rolling(60, min_periods=40).mean()
    liq = (adv >= adv_min) & P.notna()
    dia = (P / O - 1).where(O > 0)
    noite = ((1 + R) / (1 + dia) - 1).where(O > 0)
    rel = R.sub(R.where(liq).mean(axis=1), axis=0)
    if modo == "queda":
        s = (-rel).where(liq & (rel <= -limiar))
    else:
        s = adv.where(liq)
    rk = s.rank(axis=1, ascending=False, method="first")
    sel = (rk <= n)                                                       # decidido em t
    sh = 1 + lag
    compra = sel.shift(sh).fillna(False).astype(bool) & P.notna()        # leilão de fechamento de t+1+lag
    # ações inteiras: capital*alav/n por papel ao preço do fechamento da compra
    tam = capital * alavancagem / n
    qtd = np.floor(tam / P).where(compra, 0).fillna(0)
    val = qtd * P                                                          # R$ comprados no fechamento
    no = noite.shift(-1)                                                   # noite que começa no fechamento de hoje
    ok = no.notna()
    val = val.where(ok, 0)
    g = (val * no).fillna(0)
    custo = val * 2 * (B.EMOL + SLIP) * custo_mult                                  # leilão: sem spread; emolumentos nas duas pontas
    # P&L entra no dia da venda (abertura do pregão seguinte)
    pnl = (g - custo).sum(axis=1).shift(1).fillna(0)
    usado = val.sum(axis=1).shift(1).fillna(0)
    cdi_p = usado * C.CDI.reindex(P.index).fillna(0)
    e = (pnl - cdi_p) / capital
    W = (val / capital)
    W = W.shift(-sh).fillna(0)                                             # peso "decidido em t" para o motor comum (desloca 1+lag)
    m = val > 0
    ii, jj = np.nonzero(m.values)
    idx = P.index
    ng = pd.DataFrame({"ativo": np.array(cols)[jj], "lado": 1, "entrada": idx[ii], "saida": idx[np.minimum(ii + 1, len(idx) - 1)], "dias": 1,
                       "retorno_%": (no.values[ii, jj] - 2 * (B.EMOL + SLIP) * custo_mult) * 100,
                       "contrib_pp": (g.values[ii, jj] - custo.values[ii, jj]) / capital * 100, "valor": val.values[ii, jj]})
    res = {"e": e.reindex(B.DIAS).fillna(0), "pnl": (pnl - 0).reindex(B.DIAS).fillna(0), "cdi_perdido": cdi_p.reindex(B.DIAS).fillna(0),
           "W": W, "noite": noite, "negocios": ng, "vendas": usado}
    if len(_RES) > 64:
        _RES.clear()
    _RES[key] = res
    return res


def excesso(d, capital=20000, custo_mult=1, lag=0, regime=REGIME, alavancagem=1, **params):
    e = roda(d, capital, custo_mult, lag, alavancagem=alavancagem, **{**PARAMS, **params})["e"]
    return C.aplica_regime(e, regime, CUSTO_TROCA * custo_mult)


def classes_ir(d, capital=20000, **params):
    res = roda(d, capital, **{**PARAMS, **params})
    return {"acoes": res["pnl"], "_cdi_perdido": res["cdi_perdido"]}          # vendas >> R$ 20 mil/mês: tributado


def posicoes(d, capital=20000, **params):
    res = roda(d, capital, **{**PARAMS, **params})
    W = res["W"].loc[:, (res["W"] != 0).any()]
    return W, res["noite"][W.columns].reindex(B.DIAS).fillna(0).sub(B.CDI, axis=0)


def negocios(d, capital=20000, **params):
    return roda(d, capital, **{**PARAMS, **params})["negocios"]
