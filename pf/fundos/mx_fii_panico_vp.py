"""
mx_fii_panico_vp — frente pf3_mecanismos. Mecanismo 2 (pânico + ÂNCORA) aplicado ao bb_fii_panico (OOS −1,0; limiares menores −5 a −12).

Inspiração: mh_petroleo (só compra PETR4 quando ela cai muito mais que o Brent em reais — a âncora diverge) e b3_opa_leilao (ação vs preço
da OPA). O caderno pf2_b3 já diagnosticou o motivo do fracasso do pânico de FII: "o que o varejo vende muitas vezes é crédito que
realmente piorou — sem a leitura da carteira do FII o sinal de preço não separa".
Hipótese: a carteira do FII (o valor patrimonial da cota, VP, informe mensal CVM — para FII de papel é a carteira de CRIs marcada) é a
âncora. Pânico com âncora = o preço caiu forte em 5 pregões (venda do varejo) MAS o VP não caiu (variação do VP nos 3 últimos informes
>= −2%) e a cota está abaixo de `pvp_max` x VP. Sem divergência (VP caindo junto) = crédito piorando = não compra.
Dados: VP = pl/cotas do último informe ENTREGUE à CVM até a decisão (coluna 'entrega'; ~45 dias de defasagem — a âncora é velha, o que é
conservador). Execução/custos/IR do original (compra no fechamento de t+1, segura `hold` pregões, meio spread real, FII 20%).
Regra (queda x pvp_max x segmento) escolhida só no IS (2017–2020) pelo maior IR. pvp_max = 9 equivale a "sem âncora de desconto"
(só o filtro de VP não cair).
"""
import numpy as np
import pandas as pd

import _mx_comum as X
import bb_fii_panico as O

BB, B, C, pf, DIAS = X.BB, X.B, X.C, X.pf, X.DIAS

NOME = "Pânico de FII com âncora no valor patrimonial (VP não caiu)"
TESE = ("Compro o FII que caiu forte em 5 pregões só quando a carteira (VP do informe CVM) não caiu e a cota está abaixo do VP: venda de "
        "pânico do varejo contra uma âncora que divergiu")
BENCHMARK = "CDI"
INICIO, CORTE = O.INICIO, O.CORTE
REGIME = "nenhum"
CLASSE_IR = "fii"
CUSTO_TROCA = .001
PARAMS = {"queda": -.10, "pvp_max": 9.0, "seg": "papel", "dvp_min": -.02, "hold": 21, "adv_min": 5e5, "frac": .10}
GRADE = {"queda": [-.06, -.10], "pvp_max": [.85, .95, 9.0], "seg": ["papel", "todos"]}
VIZINHANCA = {"queda": (-.13, -.08), "dvp_min": (-.04, -.01), "hold": (15, 30)}
INSTRUMENTOS = O.INSTRUMENTOS
APLICAVEL = True
MOTIVO = "FIIs com ADV >= R$ 500 mil; R$ 2 mil por FII com R$ 20 mil"
ALAVANCAGENS = [1]
MOTIVO_ALAV = O.MOTIVO_ALAV
_CACHE = BB.Cache()


def carrega():
    return O.carrega()


def _vp(d):
    """VP por cota, variação do VP em 3 informes e "é FII de papel", conhecidos em cada pregão (pela data de entrega), DIAS x FII."""
    rd = d["rend"].dropna(subset=["entrega"]).copy()
    rd = rd[(rd.cotas > 0) & (rd.pl > 0)]
    rd["vpc"] = rd.pl / rd.cotas
    rd = rd.sort_values(["ticker", "data"])
    rd["dvp"] = rd.groupby("ticker").vpc.pct_change(3)
    i = DIAS.searchsorted(pd.DatetimeIndex(rd.entrega))
    ok = i < len(DIAS)
    rd = rd[ok].assign(dia=DIAS[i[ok]])
    cols = d["P"].columns
    piv = lambda c: rd.groupby(["dia", "ticker"])[c].last().unstack().reindex(index=DIAS, columns=cols).ffill(limit=70)
    # FII de papel pelo segmento/mandato do último informe ENTREGUE (um conjunto fixo usaria informes futuros: falhava no truncamento)
    rd["papel"] = (rd.segmento.fillna("") + " " + rd.mandato.fillna("")).str.contains("tulos e Val").astype(float)
    return piv("vpc"), piv("dvp"), piv("papel").fillna(0) > 0


def roda(d, capital=20000, custo_mult=1, lag=0, alavancagem=1, queda=-.08, pvp_max=.95, seg="todos", dvp_min=-.02, hold=21,
         adv_min=5e5, frac=.10):
    hold = int(round(hold))
    key = (id(d), capital, custo_mult, lag, alavancagem, round(queda, 4), pvp_max, seg, dvp_min, hold, adv_min, round(frac, 4))

    def f():
        dd = dict(d)
        R, _ = BB.fii_retorno(d)
        dd["R"] = R
        P = d["P"].reindex(DIAS)
        adv = d["V"].reindex(DIAS).fillna(0).rolling(60, min_periods=20).mean()
        liq = adv >= adv_min
        ix = R.where(liq.shift(1)).mean(axis=1).fillna(0)
        r5 = np.log1p(R.fillna(0)).rolling(5).sum().sub(np.log1p(ix).rolling(5).sum(), axis=0)
        vpc, dvp, papel = _vp(d)
        pvp = P.ffill(limit=5) / vpc
        sig = (r5 < np.log1p(queda)) & liq & P.notna() & (pvp <= pvp_max) & (dvp >= dvp_min) & pvp.notna()
        if seg == "papel":
            sig = sig & papel
        ev, ult = [], {}
        for i, t in zip(*np.nonzero(sig.values)):
            tk = sig.columns[t]
            if i - ult.get(tk, -10 ** 6) < hold:
                continue
            ult[tk] = i
            ev.append((DIAS[i], tk, f"5d {np.expm1(r5.iat[i, t]) * 100:+.1f}% vs IFIX, P/VP {pvp.iat[i, t]:.2f}, VP 3m {dvp.iat[i, t] * 100:+.1f}%"))
        ev = pd.DataFrame(ev, columns=["data", "ticker", "rotulo"]).sort_values("data")
        old = B.FRAC_EXTRA
        B.FRAC_EXTRA = 0.0
        try:
            res = BB.episodios(ev, dd, capital, hold, frac * capital * alavancagem, custo_mult, lag, alavancagem, vol_min=10)
        finally:
            B.FRAC_EXTRA = old
        res["negocios"] = BB.rotula(res["negocios"], ev)
        res["R"] = R
        res["classes"] = {"fii": res["pnl"] - res["custo"], "_cdi_perdido": res["cdi_perdido"]}
        return res
    return _CACHE.get(key, f)


X.contrato(globals(), roda)

if __name__ == "__main__":
    import sys
    X.escolhe_is(sys.modules[__name__], carrega())
