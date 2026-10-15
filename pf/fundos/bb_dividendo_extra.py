"""
Dividendo/JCP extraordinário anunciado: reação lenta até a data-com — frente "pf2_b3".

Mesa: quando a companhia aprova um provento GRANDE (>= `limiar` do preço, várias vezes o normal), o comprador natural é o investidor de
renda (pessoa física, fundos de dividendos, previdência) que só age quando vê o número no aviso aos acionistas e quer estar na base
na data-com. Esse fluxo é previsível e concentrado entre a aprovação e a data-com (5–10 pregões em mediana). Para a PF, o DIVIDENDO é
isento (JCP paga 15% na fonte), então segurar até depois do ex não é neutro: com saida="com" vendo no fechamento da data-com (sem o
provento); com saida="ex" recebo o provento e vendo no dia ex (JCP líquido de 15%).
Dados: proventos da B3 (quant/fundos/dados/arb_proventos.parquet: valor por ação, tipo, última data-com) — 103
companhias pagadoras (blue chips/elétricas/bancos); data do sinal = data de APROVAÇÃO (o aviso sai no mesmo dia; executo no fechamento
seguinte). Rendimento = valor por ação / preço de fechamento do dia da aprovação (proventos com a mesma aprovação e data-com somados).
Regra: provento >= `limiar` do preço, data-com >= 2 pregões depois da aprovação -> compra no fechamento de t+1+lag, sai na data-com
(ou no dia ex). R$ `frac` x capital por evento.
IR: ações (vendas pequenas -> isento na maioria dos meses); o painel R soma o provento bruto no dia ex — para JCP desconto os 15% na fonte.
"""
import numpy as np
import pandas as pd
from pathlib import Path

import bb_base as BB

B, C, pf = BB.B, BB.C, BB.pf
DIAS = BB.DIAS

NOME = "Dividendo/JCP extraordinário anunciado (até a data-com)"
TESE = ("Compro a ação no dia seguinte à aprovação de um provento extraordinário (>= limiar do preço) e vendo na data-com para o investidor "
        "de renda que compra para estar na base; lote pequeno")
BENCHMARK = "CDI"
INICIO, CORTE = "2014-03-01", "2021-01-01"
REGIME = "nenhum"
CLASSE_IR = "acoes"
CUSTO_TROCA = .001
PARAMS = {"limiar": .02, "saida": "com", "frac": .20, "min_preg": 2}
GRADE = {"limiar": [.02, .03, .05], "saida": ["com", "ex"]}
VIZINHANCA = {"limiar": (.015, .03), "frac": (.12, .25)}
INSTRUMENTOS = [{"onde": "Clear/Rico/XP (corretagem zero)", "ticker": "pagadoras de provento extraordinário (103 companhias)",
                 "lote": "1 ação", "custo": "emolumentos 0,03% + meio spread real do fechamento + 0,2% no fracionário"}]
APLICAVEL = True
MOTIVO = "blue chips/elétricas; R$ 4 mil por evento com R$ 20 mil"
ALAVANCAGENS = [1]
MOTIVO_ALAV = "limitado pelo nº de eventos"
_CACHE = BB.Cache()
CLS = {"ON": "3", "PN": "4", "PNA": "5", "PNB": "6", "UNT": "11"}


def carrega():
    d = BB.acoes()
    d = {k: d[k] for k in ("P", "R", "V", "BID", "ASK", "HS")}
    d["DY"] = B.painel("dy")["dy"].reindex(columns=d["P"].columns)            # provento (Yahoo) já somado em R no dia ex
    a = pd.read_parquet(Path(__file__).resolve().parent.parent / "dados" / "auditoria" / "arb_proventos.parquet")
    num = lambda s: pd.to_numeric(s.astype(str).str.replace(".", "", regex=False).str.replace(",", ".", regex=False), errors="coerce")
    x = pd.DataFrame({"data": pd.to_datetime(a.dateApproval, dayfirst=True, errors="coerce"),
                      "com": pd.to_datetime(a.lastDatePriorEx, dayfirst=True, errors="coerce"),
                      "ticker": a.code4 + a.typeStock.map(CLS).fillna("?"),
                      "valor": num(a.valueCash) / num(a.quotedPerShares).replace(0, np.nan).fillna(1),
                      "tipo": a.corporateAction})
    x = x.dropna(subset=["data", "com", "valor"])
    x = x[(x.data >= "2013-06-01") & x.ticker.isin(d["P"].columns)].rename(columns={"data": "aprov"})
    x["data"] = x.aprov                                 # coluna de corte do truncamento (o sinal nunca é antes da aprovação)
    d["prov"] = x
    dv = x.copy()
    dv["data"] = dv.com                                 # tabela de proventos PAGOS (fato realizado) para refazer o retorno do dia ex
    d["divs"] = dv
    d["ipe"] = pd.read_parquet(BB.DADOS / "ipe_proventos.parquet")[["data", "raiz"]]   # entregas IPE/CVM sobre proventos
    return d


def roda(d, capital=20000, custo_mult=1, lag=0, alavancagem=1, limiar=.02, saida="com", frac=.20, min_preg=2):
    key = (id(d), capital, custo_mult, lag, alavancagem, round(limiar, 4), saida, round(frac, 4), min_preg)

    def f():
        P = d["P"].reindex(DIAS).ffill(limit=5)
        pv = d["prov"].copy()
        pv["jcp"] = pv.tipo.str.contains("JRS") * pv.valor
        g = pv.groupby(["aprov", "ticker", "com"]).agg(valor=("valor", "sum"), jcp=("jcp", "sum")).reset_index()
        # a "data de aprovação" da B3 nem sempre é a divulgação (BBSE3: aprovação 17/12/2021, comunicado na CVM só em 07/02/2022, com o
        # valor) -> o sinal é a 1ª entrega na CVM sobre proventos da companhia entre aprovação - 3 dias e a data-com (sem entrega: descarta)
        ip = d["ipe"].sort_values("data")
        g["raiz"] = g.ticker.str[:4]
        g["ini"] = g.aprov - pd.Timedelta(days=3)
        g = pd.merge_asof(g.sort_values("ini"), ip.rename(columns={"data": "ent"}), left_on="ini", right_on="ent", by="raiz",
                          direction="forward")
        g = g[g.ent.notna() & (g.ent <= g.com)]
        g["data"] = np.maximum(g.ent, g.aprov)
        i = DIAS.searchsorted(g.data)
        ic = DIAS.searchsorted(g.com)
        ok = i < len(DIAS)
        g, i, ic = g[ok], i[ok], ic[ok]
        g["y"] = [g.valor.iloc[k] / P[t].iloc[i[k]] if P[t].iloc[i[k]] > 0 else np.nan for k, t in enumerate(g.ticker)]
        sel = (g.y >= limiar) & (g.y < .5) & (ic - i >= min_preg)
        g, ic = g[sel.values], ic[sel.values]
        # a data-com é conhecida na entrada: a ordem de venda vai para o fechamento da data-com (ou do dia ex) mesmo com atraso na entrada
        fim = (ic - 1 if saida == "com" else ic) - lag
        ev = pd.DataFrame({"data": DIAS[DIAS.searchsorted(g.data)], "ticker": g.ticker.values, "fim": DIAS[np.minimum(fim, len(DIAS) - 1)],
                           "rotulo": [f"{'JCP' if j > 0 else 'dividendo'} {y * 100:.1f}% (com {c:%Y-%m-%d})" for j, y, c in zip(g.jcp, g.y, g.com)]})
        dd = dict(d)
        # dia ex: o painel R depende do Yahoo, que PERDE proventos de várias pagadoras (ALPA3 nov/2025, QUAL3 out/2019: queda ex sem o
        # provento) -> no 1º dia ex de cada provento da B3 troco o provento do Yahoo pelo da B3: R - dy_Yahoo + provento líquido/P_com
        # (JCP: 85%); o ajuste de desdobramento/bonificação do painel fica (CMIG 29/04/2022: bonificação no mesmo dia ex)
        R = d["R"].copy()
        dv = d["divs"].copy()
        dv["jcp"] = dv.tipo.str.contains("JRS") * dv.valor
        allp = dv.assign(liq=dv.valor - .15 * dv.jcp).groupby(["ticker", "com"]).liq.sum().reset_index()
        Pr = d["P"].reindex(DIAS)
        DY = d["DY"].reindex(DIAS)
        for t, c, v in zip(allp.ticker, allp.com, allp.liq):
            k = DIAS.searchsorted(c)
            if t not in R or k + 1 >= len(DIAS) or DIAS[k] != c:
                continue
            p0, p1 = Pr[t].iat[k], Pr[t].iat[k + 1]
            if p0 > 0 and p1 > 0 and v / p0 < .5:
                j = R.columns.get_loc(t)
                R.iat[k + 1, j] = R.iat[k + 1, j] - np.nan_to_num(DY[t].iat[k + 1]) + v / p0
        dd["R"] = R
        res = BB.episodios(ev, dd, capital, None, frac * capital * alavancagem, custo_mult, lag, alavancagem)
        res["negocios"] = BB.rotula(res["negocios"], ev)
        res["R"] = dd["R"]
        return res
    return _CACHE.get(key, f)


def excesso(d, capital=20000, custo_mult=1, lag=0, regime=REGIME, alavancagem=1, **params):
    e = roda(d, capital, custo_mult, lag, alavancagem, **{**PARAMS, **params})["e"]
    return C.aplica_regime(e, regime, CUSTO_TROCA * custo_mult)


def classes_ir(d, capital=20000, **params):
    return B.classes_acoes(roda(d, capital, **{**PARAMS, **params}))


def posicoes(d, capital=20000, **params):
    r = roda(d, capital, **{**PARAMS, **params})
    W = r["W"]
    return W, r["R"].reindex(index=DIAS, columns=W.columns).fillna(0).sub(BB.CDI, axis=0)


def negocios(d, capital=20000, **params):
    return roda(d, capital, **{**PARAMS, **params})["negocios"]


if __name__ == "__main__":
    import time
    d = carrega()
    for kw in [{"limiar": l, "saida": s} for l in GRADE["limiar"] for s in GRADE["saida"]]:
        t = time.time()
        e = excesso(d, **kw)
        print(kw, "IS %.2f OOS %.2f (%.0fs) n=%d" % (C.anual(e[INICIO:CORTE]), C.anual(e[CORTE:]), time.time() - t, len(negocios(d, **kw))), flush=True)
    ng = negocios(d)
    print(ng.sort_values("contrib_pp").iloc[list(range(4)) + list(range(-4, 0))].to_string())
