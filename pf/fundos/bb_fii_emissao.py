"""
Emissão de cotas de FII: comprar a cota quando ACABA o período de negociação do direito de preferência — frente "pf2_b3".

Mesa: na oferta de cotas com direito de preferência, durante o período de preferência o mercado da cota fica pressionado: quem
recebeu o direito e não quer/pode subscrever vende o direito (o arbitrador compra o direito e VENDE a cota para travar), o cotista
que quer subscrever vende cota para levantar caixa, e o preço da emissão (normalmente perto do VP) vira teto. Quando o direito para de
negociar a pressão acaba. O direito em si NÃO é barato (estudo: comprado no 1º pregão o direito perde ~25% em mediana até o último
pregão; travado contra a cota perde 0,1–0,4% do nocional; meio spread mediano 2,6–4,7%) — o edge está na COTA depois do período.
Estudo de evento (FII subjacente menos o índice igual-ponderado de FIIs, do 1º pregão após o fim do direito até +20 pregões):
IS 2014–2020 +1,2% (92 ofertas), 2021–26 +1,3% (121). Comprador forçado: o arbitrador que vendeu a cota recompra/zera e o cotista
que vendeu volta.
Sinal causal (só dados até t): o direito (COTAHIST CODBDI 12, ESPECI DIR, ticker XXXX12) negociou ontem e NÃO negociou hoje, depois de
>= `min_preg` pregões seguidos (os direitos de FII negociam em pregões consecutivos: 1.192 de 1.206 intervalos são de 1 pregão) ->
compro a cota XXXX11 no fechamento de t+1+lag, seguro `hold` pregões. R$ `frac` x capital por oferta.
IR: CLASSE_IR = "fii" (20% sobre o excesso, conservador — o rendimento recebido é isento).
"""
import numpy as np
import pandas as pd

import bb_base as BB

B, C, pf = BB.B, BB.C, BB.pf
DIAS = BB.DIAS

NOME = "FII depois do fim do direito de preferência (emissão)"
TESE = ("Compro a cota do FII no pregão seguinte ao último dia de negociação do direito de preferência da emissão: acaba a venda do "
        "arbitrador/cotista que pressionava a cota; seguro hold pregões")
BENCHMARK = "CDI"
INICIO, CORTE = "2015-01-01", "2021-01-01"
REGIME = "nenhum"
CLASSE_IR = "fii"
CUSTO_TROCA = .001
PARAMS = {"hold": 21, "min_preg": 3, "adv_min": 2e5, "frac": .15}
GRADE = {"hold": [10, 21, 42], "min_preg": [3, 5]}
VIZINHANCA = {"hold": (15, 30), "frac": (.10, .20), "adv_min": (1e5, 5e5)}
INSTRUMENTOS = [{"onde": "Clear/Rico/XP/Inter (corretagem zero)", "ticker": "cota do FII emissor (XXXX11)", "lote": "1 cota",
                 "custo": "emolumentos 0,03% + meio spread real do fechamento"}]
APLICAVEL = True
MOTIVO = "FIIs com emissão em andamento; R$ 3 mil por oferta com R$ 20 mil; ~15–25 ofertas com direito negociado por ano"
ALAVANCAGENS = [1]
MOTIVO_ALAV = "sem financiamento de FII no varejo"
_CACHE = BB.Cache()


def carrega():
    d = BB.com_hs(BB.fiis())
    dr = pd.read_parquet(BB.DADOS / "fii_direitos.parquet")
    d["direitos"] = dr[dr.especi.str.startswith("DIR")][["data", "ticker", "fech", "volume", "negocios"]].copy()
    return d


def roda(d, capital=20000, custo_mult=1, lag=0, alavancagem=1, hold=21, min_preg=3, adv_min=2e5, frac=.15):
    hold, min_preg = int(round(hold)), int(round(min_preg))
    key = (id(d), capital, custo_mult, lag, alavancagem, hold, min_preg, adv_min, round(frac, 4))

    def f():
        dd = dict(d)
        R, _ = BB.fii_retorno(d)
        dd["R"] = R
        P = d["P"].reindex(DIAS)
        fim_dados = P.dropna(how="all").index.max()
        adv = d["V"].reindex(DIAS).fillna(0).rolling(60, min_periods=20).mean()
        dr = d["direitos"]
        ev = []
        for t, g in dr.groupby("ticker"):
            u = t[:4] + "11"
            if u not in P:
                continue
            i = np.unique(DIAS.searchsorted(pd.DatetimeIndex(g.data)))
            # sequências de pregões consecutivos; o fim é detectado no 1º pregão sem negócio (t), só se t está nos dados
            seq_ini = 0
            for k in range(len(i)):
                ultimo = k == len(i) - 1 or i[k + 1] != i[k] + 1
                if not ultimo:
                    continue
                n = k - seq_ini + 1
                dec = i[k] + 1
                if n >= min_preg and dec < len(DIAS) and DIAS[dec] <= fim_dados and adv[u].iloc[dec] >= adv_min:
                    ev.append((DIAS[dec], u, f"fim do direito {t} ({n} pregões)"))
                seq_ini = k + 1
        ev = pd.DataFrame(ev, columns=["data", "ticker", "rotulo"]).sort_values("data")
        old = B.FRAC_EXTRA
        B.FRAC_EXTRA = 0.0
        try:
            res = BB.episodios(ev, dd, capital, hold, frac * capital * alavancagem, custo_mult, lag, alavancagem)
        finally:
            B.FRAC_EXTRA = old
        res["negocios"] = BB.rotula(res["negocios"], ev)
        res["R"] = R
        return res
    return _CACHE.get(key, f)


def excesso(d, capital=20000, custo_mult=1, lag=0, regime=REGIME, alavancagem=1, **params):
    e = roda(d, capital, custo_mult, lag, alavancagem, **{**PARAMS, **params})["e"]
    return C.aplica_regime(e, regime, CUSTO_TROCA * custo_mult)


def classes_ir(d, capital=20000, **params):
    r = roda(d, capital, **{**PARAMS, **params})
    return {"fii": (r["pnl"] - r["custo"]), "_cdi_perdido": r["cdi_perdido"]}


def posicoes(d, capital=20000, **params):
    r = roda(d, capital, **{**PARAMS, **params})
    W = r["W"]
    return W, r["R"].reindex(index=DIAS, columns=W.columns).fillna(0).sub(BB.CDI, axis=0)


def negocios(d, capital=20000, **params):
    return roda(d, capital, **{**PARAMS, **params})["negocios"]


if __name__ == "__main__":
    import time
    d = carrega()
    for kw in [{"hold": h, "min_preg": m} for h in GRADE["hold"] for m in GRADE["min_preg"]]:
        t = time.time()
        e = excesso(d, **kw)
        print(kw, "IS %.2f OOS %.2f (%.0fs)" % (C.anual(e[INICIO:CORTE]), C.anual(e[CORTE:]), time.time() - t), flush=True)
    print(negocios(d).sort_values("contrib_pp").tail(5).to_string())
