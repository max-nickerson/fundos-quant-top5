"""
mx_fii_datacom — frente pf3_mecanismos. Mecanismo 1 (calendário obriga) + 3 (magnitude) aplicados ao bb_fii_datacom (OOS −2,0 pp).

Inspiração: bb_dividendo_extra_aud (o investidor de renda compra para estar na base na data-com; o edge cresce com o tamanho do provento).
Hipótese: no FII o comprador da data-com é o mesmo varejo de renda; se o mecanismo é o do dividendo extra, ele deve aparecer (i) perto
da data-com (k pequeno, a pista k = 3 / saída no ex = +4,1 OOS do caderno pf2_b3) e (ii) MAIS nos FIIs de maior rendimento mensal, não nos
de maior liquidez (o original comprava os 10 mais líquidos).
Regra decidida SÓ no IS (2017–2020): grade k x saída x seleção, escolhida pelo maior IR do IS (pf/fundos/_mx_comum.escolhe_is).
Seleção 'dy': os n FIIs líquidos (ADV >= adv_min) com maior rendimento do último informe mensal ENTREGUE à CVM até a decisão (entrega =
coluna 'entrega' do informe, ~45 dias depois do mês; o anúncio real sai antes — conservador) dividido pelo preço da decisão.
Data-com = último pregão do mês (calibração em bb_base). Execução, custos (meio spread real, sem fracionário), IR (FII 20% sobre todo o
excesso — conservador quando sai no ex com rendimento isento) iguais ao original.
"""
import numpy as np
import pandas as pd

import _mx_comum as X
import bb_fii_datacom as O

BB, B, C, pf, DIAS = X.BB, X.B, X.C, X.pf, X.DIAS

NOME = "FII na data-com só nos de maior rendimento (calendário + magnitude)"
TESE = ("O comprador da data-com do FII é o varejo de renda: compro os FIIs líquidos de MAIOR rendimento mensal k pregões antes do último "
        "pregão do mês e vendo para ele (data-com) ou recebo o rendimento isento (ex); regra escolhida no IS")
BENCHMARK = "CDI"
INICIO, CORTE = O.INICIO, O.CORTE
REGIME = "nenhum"
CLASSE_IR = "fii"
CUSTO_TROCA = .001
PARAMS = {"k": 5, "saida": "com", "sel": "dy", "n": 10, "adv_min": 1e6, "frac": .09}
GRADE = {"k": [3, 5, 10], "saida": ["com", "ex"], "sel": ["adv", "dy"]}
VIZINHANCA = {"n": (6, 14), "adv_min": (5e5, 2e6)}
INSTRUMENTOS = O.INSTRUMENTOS
APLICAVEL = True
MOTIVO = "FIIs líquidos, 1 cota mínima; 12 ciclos por ano"
ALAVANCAGENS = [1]
MOTIVO_ALAV = O.MOTIVO_ALAV
_CACHE = BB.Cache()


def carrega():
    return O.carrega()


def _dy(d):
    """Rendimento mensal conhecido em cada pregão (R$/cota do último informe entregue), DIAS x FII."""
    rd = d["rend"].dropna(subset=["entrega"])
    rd = rd[(rd.rend > 0) & (rd.rend < 50)]
    i = DIAS.searchsorted(pd.DatetimeIndex(rd.entrega))
    ok = i < len(DIAS)
    x = pd.DataFrame({"data": DIAS[i[ok]], "ticker": rd.ticker.values[ok], "rend": rd.rend.values[ok], "ref": rd.data.values[ok]})
    x = x.sort_values(["ref"]).groupby(["data", "ticker"]).rend.last().unstack()
    return x.reindex(index=DIAS, columns=d["P"].columns).ffill(limit=70)


def roda(d, capital=20000, custo_mult=1, lag=0, alavancagem=1, k=5, saida="com", sel="dy", n=10, adv_min=1e6, frac=.09):
    k, n = int(round(k)), int(round(n))
    key = (id(d), capital, custo_mult, lag, alavancagem, k, saida, sel, n, adv_min, round(frac, 4))

    def f():
        dd = dict(d)
        dd["R"], _ = BB.fii_retorno(d)
        P = d["P"].reindex(DIAS)
        adv = d["V"].reindex(DIAS).fillna(0).rolling(60, min_periods=20).mean()
        dy = (_dy(d) / P.ffill(limit=5)).where(lambda x: (x > 0) & (x < .05))
        mes = pd.Series(DIAS.to_period("M"), index=DIAS)
        ic = np.flatnonzero((mes != mes.shift(-1)).values)
        fim_dados = P.dropna(how="all").index.max()
        ev = []
        for i in ic:
            dec = i - k
            if dec < 60 or DIAS[dec] > fim_dados:
                continue
            a = adv.iloc[dec]
            ok = (a >= adv_min) & P.iloc[dec].notna()
            s = a[ok] if sel == "adv" else dy.iloc[dec][ok].dropna()
            s = s.nlargest(n)
            fim = i - 1 if saida == "com" else i
            ev += [(DIAS[dec], t, DIAS[fim], f"data-com {DIAS[i]:%Y-%m-%d} dy {dy.iat[dec, dy.columns.get_loc(t)] * 100:.2f}%") for t in s.index]
        ev = pd.DataFrame(ev, columns=["data", "ticker", "fim", "rotulo"])
        old = B.FRAC_EXTRA
        B.FRAC_EXTRA = 0.0
        try:
            res = BB.episodios(ev, dd, capital, None, frac * capital * alavancagem, custo_mult, lag, alavancagem)
        finally:
            B.FRAC_EXTRA = old
        res["negocios"] = BB.rotula(res["negocios"], ev)
        res["R"] = dd["R"]
        res["classes"] = {"fii": res["pnl"] - res["custo"], "_cdi_perdido": res["cdi_perdido"]}
        return res
    return _CACHE.get(key, f)


X.contrato(globals(), roda)

if __name__ == "__main__":
    import sys
    X.escolhe_is(sys.modules[__name__], carrega())
