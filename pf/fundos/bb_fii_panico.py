"""
Pânico de FII: o varejo vende o FII que caiu muito em poucos dias — frente "pf2_b3".

Mesa: o cotista de FII é pessoa física; quando um FII cai forte em uma semana (notícia de inadimplência de um inquilino, corte de
rendimento, emissão abaixo do preço, "o FII X está derretendo" nas redes) o varejo vende sem olhar o valor patrimonial. Não há
institucional comprando FII pequeno; a PF com R$ 2 mil por FII é o comprador de liquidez. Diferente de rf_fii_infra (FI-Infra/FII de papel
com desconto ao VP mensal): aqui o gatilho é a VENDA forçada de curto prazo (queda relativa ao índice de FIIs em 5 pregões).
Sinal (só dados até t): retorno de 5 pregões do FII menos o do índice igual-ponderado dos FIIs líquidos < `queda`; ADV 60d >= R$ `adv_min`;
um negócio por FII a cada `hold` pregões. Compra no fechamento de t+1+lag, vende `hold` pregões depois. R$ `frac` x capital por FII.
Estudo de evento (FIIs ADV >= R$ 500 mil; excesso sobre o índice de FIIs, 20 pregões): IS 2017–2020 +0,6% (queda < −6%), +1,8% (< −10%);
2021–26 −0,9% / −3,2% (ciclo de alta de juros: o FII que caiu continuou caindo).
Obs.: o estudo acima ainda incluía ETFs (ESPECI CI); só com FIIs (informe CVM) o fundo dá IS +5,9 / OOS −1,0 pp (queda < −15%).
IR: CLASSE_IR = "fii" (20% sobre o excesso, conservador — o rendimento recebido é isento).
"""
import numpy as np
import pandas as pd

import bb_base as BB

B, C, pf = BB.B, BB.C, BB.pf
DIAS = BB.DIAS

NOME = "Pânico de FII (venda forçada do varejo)"
TESE = ("Compro o FII que caiu muito mais que o índice de FIIs em 5 pregões (venda de pânico do varejo, sem comprador institucional) e "
        "seguro hold pregões; R$ 2 mil por FII")
BENCHMARK = "CDI"
INICIO, CORTE = "2017-03-01", "2021-01-01"
REGIME = "nenhum"
CLASSE_IR = "fii"
CUSTO_TROCA = .001
PARAMS = {"queda": -.15, "hold": 21, "adv_min": 5e5, "frac": .10}
GRADE = {"queda": [-.06, -.10, -.15], "hold": [10, 21]}
VIZINHANCA = {"queda": (-.18, -.12), "hold": (15, 30), "adv_min": (3e5, 1e6)}
INSTRUMENTOS = [{"onde": "Clear/Rico/XP/Inter (corretagem zero)", "ticker": "FII com queda forte (XXXX11)", "lote": "1 cota",
                 "custo": "emolumentos 0,03% + meio spread real do fechamento"}]
APLICAVEL = True
MOTIVO = "FIIs com ADV >= R$ 500 mil; R$ 2 mil por FII com R$ 20 mil"
ALAVANCAGENS = [1]
MOTIVO_ALAV = "sem financiamento de FII no varejo"
_CACHE = BB.Cache()


def carrega():
    return BB.com_hs(BB.fiis())


def roda(d, capital=20000, custo_mult=1, lag=0, alavancagem=1, queda=-.10, hold=21, adv_min=5e5, frac=.10):
    hold = int(round(hold))
    key = (id(d), capital, custo_mult, lag, alavancagem, round(queda, 4), hold, adv_min, round(frac, 4))

    def f():
        dd = dict(d)
        R, _ = BB.fii_retorno(d)
        dd["R"] = R
        P = d["P"].reindex(DIAS)
        adv = d["V"].reindex(DIAS).fillna(0).rolling(60, min_periods=20).mean()
        liq = adv >= adv_min
        ix = R.where(liq.shift(1)).mean(axis=1).fillna(0)
        r5 = np.log1p(R.fillna(0)).rolling(5).sum().sub(np.log1p(ix).rolling(5).sum(), axis=0)
        sig = (r5 < np.log1p(queda)) & liq & P.notna()
        ii, jj = np.where(sig.values)
        ev, ult = [], {}
        for i, j in sorted(zip(ii, jj)):
            if DIAS[i] < pd.Timestamp(INICIO) or ult.get(j, -10 ** 6) > i - hold:
                continue
            ult[j] = i
            ev.append((DIAS[i], P.columns[j], f"queda 5d vs índice FII {np.expm1(r5.iat[i, j]) * 100:.1f}%"))
        ev = pd.DataFrame(ev, columns=["data", "ticker", "rotulo"])
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
    for kw in [{"queda": q, "hold": h} for q in GRADE["queda"] for h in GRADE["hold"]]:
        t = time.time()
        e = excesso(d, **kw)
        print(kw, "IS %.2f OOS %.2f (%.0fs)" % (C.anual(e[INICIO:CORTE]), C.anual(e[CORTE:]), time.time() - t), flush=True)
