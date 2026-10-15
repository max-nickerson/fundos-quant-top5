"""
Fato relevante fora de balanço em large caps, com o beta vendido (ou comprado) em mini-índice (WIN) inteiro.

Tese de mesa: no Brasil o mercado SUBREAGE a notícia relevante (estudo de eventos da pesquisa anterior: o que reage forte continua). Aqui o
evento é o FATO RELEVANTE que NÃO é balanço (M&A, venda de ativo, guidance, troca de CEO, reestruturação, acordo, multa) — o PEAD de
resultado e os insiders/follow-on ficam para a frente b3_acoes. Se a ação reagiu >= `thr` acima (abaixo) do Ibovespa entre o fechamento
anterior à entrega e o fechamento do pregão seguinte, compro (vendo, com aluguel de PF) no fechamento do outro dia e seguro `dias` pregões.
O que a PF ganha aqui é poder operar o evento em large cap (aluguel barato) e travar o beta no mini-índice: o WIN só sai do zero quando a
exposição líquida chega a meio contrato (~R$ 10–20 mil) — com R$ 20 mil quase nunca, com R$ 50 mil às vezes. Universo: ADV 60d >= R$ 50 mi
e preço >= R$ 5 (aluguel 1% a.a. + 0,5% por contrato). Até 5 eventos simultâneos de 20% do capital.
"""
import numpy as np
import pandas as pd

import mh_base as B
import comum as C

NOME = "Fato relevante (não-balanço) em large caps, beta em WIN"
TESE = ("Sigo a reação a fato relevante que não é balanço em large caps (comprado se a ação subiu >= thr vs Ibovespa, vendido com aluguel "
        "PF se caiu) por N pregões, com o beta líquido travado em mini-índice inteiro")
BENCHMARK = "CDI"
INICIO, CORTE = "2015-01-01", "2021-01-01"
REGIME = "nenhum"
CUSTO_TROCA = .001
PARAMS = {"thr": .05, "dias": 40, "hedge": "win", "lado": "ambos", "max_ev": 5, "peso": .2}
GRADE = {"thr": [.03, .05], "dias": [20, 40], "hedge": ["win", "nenhum"]}
VIZINHANCA = {"thr": (.025, .07), "dias": (10, 50)}
VARIANTES = {"só comprado": {"lado": "compra"}, "só vendido": {"lado": "venda"}, "contra a reação (reverte)": {"sentido": "reverte"}}
APLICAVEL = True
MOTIVO = ("Aplicável: large caps no fracionário e aluguel PF barato; o hedge WIN arredonda para 0 com R$ 20 mil (exposição líquida < meio "
          "contrato) e funciona em parte com R$ 50 mil")
INSTRUMENTOS = ("B3 (Clear/Rico): ações com ADV >= R$ 50 mi no fracionário, 20% do capital por evento, vendido via BTC de PF (0,5% por contrato "
                "+ ~1% a.a.); WIN no beta líquido (R$ 0,20/ponto, margem ~15% em Tesouro Selic); sinal = FR na CVM (data de entrega)")
ALAVANCAGENS = [1, 1.5, 2]
MOTIVO_ALAV = "Até 2x (5 eventos x 40%); 5x estoura a garantia do aluguel e concentra em 1–2 eventos"


def carrega():
    return B.dados()


def _eventos(d, thr, lado, sentido="segue"):
    P, R, ADV = B.acoes(d)
    rib = B.futuros(d)["WIN"][0] + C.CDI.reindex(B.DIAS).fillna(0)
    ev = d["eventos"]
    dia = lambda s: B.DIAS.searchsorted(pd.DatetimeIndex(pd.to_datetime(s)).normalize())
    fr = ev[ev.tipo == "FR"].copy()
    itr = ev[ev.tipo == "ITR"].copy()
    fr["i"], itr["i"] = dia(fr.data), dia(itr.data)
    fr = fr[fr.i < len(B.DIAS) - 2]
    # tira FR com ITR/DFP da mesma empresa de 2 pregões antes até o dia da decisão (é balanço)
    perto = fr.merge(itr[["ticker", "i"]], on="ticker", suffixes=("", "_r"))
    perto = perto[(perto.i_r >= perto.i - 2) & (perto.i_r <= perto.i + 1)][["ticker", "i"]].drop_duplicates()   # só ITR já entregue na decisão (t0+1)
    fr = fr.merge(perto, on=["ticker", "i"], how="left", indicator=True)
    fr = fr[fr._merge == "left_only"].drop(columns="_merge").drop_duplicates(["ticker", "i"])
    fr = fr[fr.ticker.isin(R.columns)]
    Rv, ib = R.fillna(0).to_numpy(), rib.to_numpy()
    cols = {t: j for j, t in enumerate(R.columns)}
    adv, px, nn = ADV.to_numpy(), P.ffill(limit=5).to_numpy(), R.notna().to_numpy()
    out = []
    for t, i in zip(fr.ticker, fr.i):
        j = cols[t]
        if i < 1 or i + 1 >= len(B.DIAS) or not (nn[i, j] and nn[i + 1, j]):
            continue
        if adv[i - 1, j] < 50e6 or px[i - 1, j] < 5:
            continue
        reac = (1 + Rv[i, j]) * (1 + Rv[i + 1, j]) - (1 + ib[i]) * (1 + ib[i + 1])
        s = (np.sign(reac) if abs(reac) >= thr else 0) * (1 if sentido == "segue" else -1)
        if s == 0 or (lado == "compra" and s < 0) or (lado == "venda" and s > 0):
            continue
        out.append((i + 1, t, s, reac))                                 # decide no fechamento de t0+1
    return pd.DataFrame(out, columns=["i", "ticker", "lado", "reacao"]).sort_values(["i", "ticker"], kind="mergesort")   # ordem estável (truncamento)


def _livro(d, capital=20000, lag=0, custo_mult=1, alavancagem=1, thr=.05, dias=20, hedge="win", lado="ambos", max_ev=5, peso=.2,
           sentido="segue"):
    P, R, ADV = B.acoes(d)
    ev = _eventos(d, thr, lado, sentido)
    T = len(B.DIAS)
    tk = sorted(ev.ticker.unique())
    col = {t: j for j, t in enumerate(tk)}
    W = np.zeros((T, len(tk)))
    fim_de = []                                                           # (fim, ticker)
    for i, t, s in zip(ev.i, ev.ticker, ev.lado):
        fim_de = [(f, x) for f, x in fim_de if f > i]
        if len(fim_de) >= max_ev or any(x == t for _, x in fim_de):
            continue
        f = min(i + dias, T)
        W[i:f, col[t]] = s * peso
        fim_de.append((f, t))
    W = pd.DataFrame(W, index=B.DIAS, columns=tk)
    fut = None
    if hedge == "win":
        rw = B.futuros(d)["WIN"][0]
        cdi = C.CDI.reindex(B.DIAS).fillna(0)
        bi = pd.DataFrame({t: B.beta_rolante(R[t] - cdi, rw.to_frame("w"), lim=(.3, 2))["w"] for t in tk})
        fut = {"WIN": ("WIN", -(W * B.congela(bi, W)).sum(axis=1))}
    return B.livro(capital, W, fut, d, lag=lag, custo_mult=custo_mult, alavancagem=alavancagem, taxa_aluguel={t: .01 for t in tk})


def excesso(d, capital=20000, custo_mult=1, lag=0, regime=REGIME, alavancagem=1, **params):
    e = B.padrao(__import__(__name__), d, capital, lag, custo_mult, alavancagem, params)["e"]
    return C.aplica_regime(e, regime, CUSTO_TROCA * custo_mult)


def classes_ir(d, capital=20000, **params):
    return B.padrao(__import__(__name__), d, capital, 0, 1, 1, params)["classes"]


def posicoes(d, capital=20000, **params):
    r = B.padrao(__import__(__name__), d, capital, 0, 1, 1, params)
    return r["W"], r["Rx"]


def negocios(d, capital=20000, **params):
    return B.negocios_de(B.padrao(__import__(__name__), d, capital, 0, 1, 1, params), capital)


def diagnostico(d, capital=20000, **params):
    p = {**PARAMS, **params}
    r = B.padrao(__import__(__name__), d, capital, 0, 1, 1, params)
    ev = _eventos(d, p["thr"], p["lado"], p.get("sentido", "segue"))
    out = dict(r["diag"])
    out["eventos elegíveis"] = len(ev)
    out["eventos/ano"] = float(len(ev) / (len(B.DIAS) / 252))
    if "WIN" in r["pos"]:
        acoes = [c for c in r["W"].columns if c != "WIN"]
        liq = r["W"][acoes].sum(axis=1).shift(1).abs() > 0
        out["WIN: % dias com exposição e 0 contrato"] = float((r["pos"]["WIN"][liq] == 0).mean() * 100)
    return out
