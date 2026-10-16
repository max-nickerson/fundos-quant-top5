"""
mx_rebal_pequeno — frente pf3_mecanismos. Mecanismos 3 (magnitude) + 4 (ser pequeno) aplicados ao rebalanceamento do Ibovespa
(rev_rebal_ibovespa: +1,0 pp, marginal) e, por extensão, à lição do bb_rebal_indices (SMLL/IBrX −2,4: "dinheiro passivo pequeno demais").

Inspiração: bb_dividendo_extra_aud (o efeito cresce com o tamanho do fluxo forçado) e b3_opa_leilao (a vantagem do pequeno está nos papéis
em que o institucional não monta posição).
Hipótese: o comprador forçado (fundo de índice/ETF) compra um valor proporcional ao valor de mercado do entrante; o impacto de preço é
esse valor dividido pelo giro do papel. O efeito deve aparecer nos entrantes de GIRO BAIXO (valor de mercado alto para o volume, a
demanda passiva vale muitos dias de volume) ou de ADV baixo (os menores entrantes, onde o arbitrador institucional não entra) — e sumir nos
entrantes líquidos, que o mercado antecipa sem custo.
Medidas (só dados até a decisão): giro = ADV60 / valor de mercado (ações emitidas do último ITR/FRE ENTREGUE à CVM x preço; todas as
classes da companhia somadas pelo CNPJ). Em cada revisão fico com a metade de menor giro ('giro'), a metade de menor ADV ('adv') ou todos.
Resto igual ao rev_rebal_ibovespa (regra da B3 reconstruída, compra `antes` pregões antes, vende no último pregão da carteira velha,
fracionário, sem hedge, 1/15 do capital por papel; vendas pequenas -> isento). Seleção e `antes` escolhidos só no IS pelo maior IR.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

import _mx_comum as X  # noqa: E402
import _ev_pf as M  # noqa: E402
import rev_rebal_ibovespa as RR  # noqa: E402

I = RR.I
BB, B, C, pf, DIAS = X.BB, X.B, X.C, X.pf, X.DIAS

NOME = "Rebalanceamento do Ibovespa só nos entrantes de giro baixo / pequenos (magnitude + tamanho)"
TESE = ("Compro no fracionário só os prováveis entrantes do Ibovespa em que a demanda passiva vale mais dias de volume (giro baixo) ou os "
        "menores, e vendo aos fundos de índice no último pregão da carteira velha")
BENCHMARK = "CDI"
INICIO, CORTE = RR.INICIO, RR.CORTE
REGIME = "nenhum"
CLASSE_IR = "acoes"
CUSTO_TROCA = .001
PARAMS = {"sel": "giro", "antes": 10}
GRADE = {"sel": ["todos", "giro", "adv"], "antes": [10, 21]}
VIZINHANCA = {"antes": (7, 14)}
INSTRUMENTOS = RR.INSTRUMENTOS
APLICAVEL = True
MOTIVO = RR.MOTIVO
ALAVANCAGENS = [1]
MOTIVO_ALAV = "exposição média pequena; o limite é o nº de entrantes"
_CACHE = {}


def carrega():
    d = RR.carrega()
    ae = B.ler("acoes_emitidas")
    mp = B.ler("mapa_cnpj")
    d["emit"] = ae.merge(mp, on="cnpj")[["data", "raiz", "acoes"]].groupby(["data", "raiz"]).acoes.max().reset_index()
    return d


def _pesos(d, antes, sel):
    p = I._painel(d)
    ev = I.eventos(d, int(antes))
    ev = ev[ev.s > 0]
    if sel != "todos" and len(ev):
        em = d["emit"].sort_values("data")
        keep = []
        for dec, g in ev.groupby("data"):
            adv = p["ADV"].reindex(columns=g.ticker).asof(dec) if len(p["ADV"]) else pd.Series(dtype=float)
            px = p["P"].reindex(columns=g.ticker).loc[:dec].ffill().iloc[-1]
            if sel == "giro":
                e = em[em.data <= dec].groupby("raiz").acoes.last()
                mcap = pd.Series({t: e.get(t[:4], np.nan) * px[t] for t in g.ticker})
                m = adv / mcap                                    # giro: menor = demanda passiva maior em dias de volume
            else:
                m = adv
            m = m.dropna()
            if not len(m):
                continue
            corte = m.median()
            keep += [(dec, t) for t in m.index[m <= corte]]
        ks = set(keep)
        ev = ev[[(a, b) in ks for a, b in zip(ev.data, ev.ticker)]]
    idx = DIAS[DIAS >= I.INICIO_DADOS]
    W = pd.DataFrame(0.0, index=idx, columns=sorted(ev.ticker.unique()))
    for dec, t in zip(ev.data, ev.ticker):
        i = idx.get_loc(dec)
        W.iloc[i:i + int(antes) - 1, W.columns.get_loc(t)] = 1.0 / I.N_MAX
    W = W.div(np.maximum(W.abs().sum(axis=1), 1), axis=0).reindex(DIAS).fillna(0)
    return M.antecipa_saida(W)


def _roda(d, capital=20000, custo_mult=1, lag=0, alavancagem=1, sel="giro", antes=10):
    key = (id(d), capital, custo_mult, lag, alavancagem, sel, int(antes))
    if key not in _CACHE:
        if len(_CACHE) > 24:
            _CACHE.clear()
        p = I._painel(d)
        W = _pesos(d, antes, sel)
        tk = list(W.columns)
        adv = p["ADV"].reindex(columns=tk)
        taxa = M.taxa_aluguel(adv, p["R"].reindex(columns=tk), p["P"].reindex(columns=tk))
        _CACHE[key] = (d, M.simula(W, p["P"].reindex(columns=tk), p["R"].reindex(columns=tk), adv, capital, custo_mult, lag, alavancagem,
                                   taxa=taxa, hedge=0.0, instrumento="bova", ibov=d["ibov"], custos="pf"), W)
    return _CACHE[key][1], _CACHE[key][2]


def excesso(d, capital=20000, custo_mult=1, lag=0, regime=REGIME, alavancagem=1, **params):
    e = _roda(d, capital, custo_mult, lag, alavancagem, **{**PARAMS, **params})[0]["excesso"]
    return C.aplica_regime(e, regime, CUSTO_TROCA * custo_mult)


def classes_ir(d, capital=20000, **params):
    return _roda(d, capital, **{**PARAMS, **params})[0]["classes"]


def posicoes(d, **params):
    kw = {**PARAMS, **params}
    p = I._painel(d)
    return M.posicoes_de(_pesos(d, kw["antes"], kw["sel"]), p["R"])


def negocios(d, capital=20000, **params):
    return M.negocios_de(_roda(d, capital, **{**PARAMS, **params})[0], capital)


if __name__ == "__main__":
    X.escolhe_is(sys.modules[__name__], carrega())
