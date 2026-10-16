"""
mx_crise_dividendo — frente pf3_mecanismos. Mecanismo 2 (pânico + ÂNCORA) aplicado à crise corporativa (rev_crise: contrarian −15% a.a.
na pesquisa institucional; continuação vendida +0,5 pp) e ao pânico sem âncora em geral.

Inspiração: b3_opa_leilao / mh_petroleo — a queda só é comprável quando há um preço de referência que o pânico ignorou.
Hipótese: um provento JÁ DECLARADO (aviso entregue na CVM, valor e data-com conhecidos) é uma âncora de caixa: quem compra até a data-com
recebe esse valor. Quando a ação desaba (>= `queda` abaixo do mercado em 5 pregões) com um provento grande ainda por vir, o vendedor está
vendendo também o dinheiro já aprovado — o investidor de renda (mesmo comprador forçado do bb_dividendo_extra) volta até a data-com.
Sem âncora (rev_crise contrarian) a queda continua.
Regra: universo e sinal de provento do vencedor (bb_dividendo_extra_aud: proventos B3 de todas as pagadoras, sinal = 1ª entrega na CVM,
ADV >= R$ 5 mi). Em cada pregão t, para cada ação com provento declarado e data-com >= t+2 cujo valor total / preço de t >= `y_min`: se
o retorno de 5 pregões menos a média das ações líquidas <= −`queda`, compra no fechamento de t+1 e vende no fechamento da data-com (sem
receber o provento — mesma saída do vencedor). Um negócio por provento. R$ `frac` x capital por evento. IR: ações.
Regra (queda x y_min) escolhida só no IS (2014–2020) pelo maior IR.
"""
import numpy as np
import pandas as pd

import _mx_comum as X
import bb_dividendo_extra_aud as A

BB, B, C, pf, DIAS = X.BB, X.B, X.C, X.pf, X.DIAS

NOME = "Queda forte com provento declarado pendente (pânico + âncora de caixa)"
TESE = ("Compro a ação que caiu forte contra o mercado quando há um provento já aprovado (âncora de caixa) com data-com à frente; vendo na "
        "data-com ao investidor de renda")
BENCHMARK = "CDI"
INICIO, CORTE = A.INICIO, A.CORTE
REGIME = "nenhum"
CLASSE_IR = "acoes"
CUSTO_TROCA = .001
PARAMS = {"queda": .05, "y_min": .01, "frac": .20, "adv_min": 5.0}
GRADE = {"queda": [.05, .08, .12], "y_min": [.01, .03]}
VIZINHANCA = {"queda": (.04, .07), "y_min": (.007, .02), "frac": (.12, .25)}
INSTRUMENTOS = A.INSTRUMENTOS
APLICAVEL = True
MOTIVO = "pagadoras com ADV >= R$ 5 mi; poucos eventos por ano"
ALAVANCAGENS = [1]
MOTIVO_ALAV = "limitado pelo nº de eventos"
_CACHE = BB.Cache()


def carrega():
    d = A.carrega()
    a = BB.acoes()
    d["V"] = a["V"]
    return d


def _proventos(d, adv_min):
    """Proventos declarados: (sinal, ticker, com, valor total). Sinal = max(aprovação, 1ª entrega IPE em [aprov-3d, com])."""
    dd = A._filtra(d, adv_min)
    pv = dd["prov"]
    g = pv.groupby(["aprov", "ticker", "com"]).valor.sum().reset_index()
    ip = dd["ipe"].sort_values("data")
    g["raiz"] = g.ticker.str[:4]
    g["ini"] = g.aprov - pd.Timedelta(days=3)
    g = pd.merge_asof(g.sort_values("ini"), ip.rename(columns={"data": "ent"}), left_on="ini", right_on="ent", by="raiz", direction="forward")
    g = g[g.ent.notna() & (g.ent <= g.com)]
    g["sinal"] = np.maximum(g.ent, g.aprov)
    return g[["sinal", "ticker", "com", "valor"]]


def roda(d, capital=20000, custo_mult=1, lag=0, alavancagem=1, queda=.05, y_min=.01, frac=.20, adv_min=5.0):
    key = (id(d), capital, custo_mult, lag, alavancagem, round(queda, 4), round(y_min, 4), round(frac, 4), adv_min)

    def f():
        P = d["P"].reindex(DIAS).ffill(limit=5)
        R = d["R"].reindex(DIAS)
        adv = d["V"].reindex(DIAS).fillna(0).rolling(60, min_periods=20).mean()
        liq = adv >= 5e6
        mk = R.where(liq).mean(axis=1).fillna(0)
        r5 = np.log1p(R.fillna(0)).rolling(5).sum().sub(np.log1p(mk).rolling(5).sum(), axis=0)
        g = _proventos(d, adv_min)
        fim_dados = d["P"].dropna(how="all").index.max()
        ev = []
        for s, t, c, v in zip(g.sinal, g.ticker, g.com, g.valor):
            if t not in P:
                continue
            i0, ic = DIAS.searchsorted(s), DIAS.searchsorted(c)
            for i in range(i0, ic - 1):                       # compra em i+1 <= data-com - 1
                if DIAS[i] > fim_dados:
                    break
                p = P[t].iat[i]
                if p > 0 and v / p >= y_min and v / p < .5 and r5[t].iat[i] <= np.log1p(-queda):
                    ev.append((DIAS[i], t, DIAS[ic - 1], f"queda 5d {np.expm1(r5[t].iat[i]) * 100:+.1f}% com provento {v / p * 100:.1f}% (com {c:%Y-%m-%d})"))
                    break
        ev = pd.DataFrame(ev, columns=["data", "ticker", "fim", "rotulo"])
        if len(ev):
            ev["fim"] = ev["fim"] - pd.to_timedelta(0, "D")
            ev["fim"] = [DIAS[max(DIAS.searchsorted(x) - lag, 0)] for x in ev.fim]
        res = BB.episodios(ev, d, capital, None, frac * capital * alavancagem, custo_mult, lag, alavancagem)
        res["negocios"] = BB.rotula(res["negocios"], ev)
        return res
    return _CACHE.get(key, f)


X.contrato(globals(), roda)

if __name__ == "__main__":
    import sys
    X.escolhe_is(sys.modules[__name__], carrega())
