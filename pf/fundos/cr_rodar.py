"""
Frente pf2_cripto: junta as baterias (pf/resultados/bateria/cr_*.pkl, geradas por `python pf/rodar_pf.py um cr_<x>`), calcula o alfa vs BTC,
roda os diagnósticos do caderno e salva pf/resultados/pf2_cripto.pkl.
    python pf/fundos/cr_rodar.py
"""
import importlib
import pickle
import sys
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")
AQUI = Path(__file__).resolve().parent
for p in (str(AQUI), str(AQUI.parent), str(AQUI.parent.parent)):
    if p not in sys.path:
        sys.path.insert(0, p)
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

import cr_comum as K  # noqa: E402
import robustez as RB  # noqa: E402

FUNDOS = ["cr_funding", "cr_premio_br", "cr_panico", "cr_fds", "cr_etf_futuro", "cr_alts", "cr_eventos", "cr_staking"]
BAT = AQUI.parent / "resultados" / "bateria"
pd.set_option("display.width", 250)


def oos_pp(m, e):
    r = RB.cota(m, e.reindex(K.DIAS).fillna(0))
    return RB.ativo_aa(m, r)


def resumo():
    L, saida = [], []
    for n in FUNDOS:
        o = pickle.load(open(BAT / f"{n}.pkl", "rb"))
        R = o["R20"]
        e20 = o["r20"] - K.CDI.reindex(o["r20"].index).fillna(0)
        e50 = o["r50"] - K.CDI.reindex(o["r50"].index).fillna(0)
        a, b = K.alfa_vs_btc(e20, o["CORTE"])
        ng = R["negocios"]
        o_ng = ng[pd.to_datetime(ng.entrada) >= pd.Timestamp(o["CORTE"])].sort_values("contrib_pp")
        lin = {"fundo": n, "aplicável": o["APLICAVEL"], "OOS desde": o["CORTE"][:7],
               "20k antes IR": o["ativo20"], "20k depois IR": o["ativo_ir20"], "50k antes IR": o["ativo50"], "50k depois IR": o["ativo_ir50"],
               "IR": o["ir_oos20"], "PBO %": R["resumo_grade"]["PBO %"],
               "P(bater 3a) %": R["mc"].loc["P(bater o benchmark) %", "3 ano(s)"],
               "sem 10 melhores": R["sem_maiores"].get("sem os 10 melhores"), "custo 2x": R["custo"].get("2x"), "t+2": R["atraso"].get("t+2"),
               "leque p5": R["leque"]["ativo OOS pp"].quantile(.05), "trunc ok": bool(R["truncamento"]["passou"].all()),
               "alfa vs BTC pp": a, "beta BTC": b, "vol OOS %": R["metricas"].loc["vol a.a. %", "fora da amostra"],
               "pior queda %": R["metricas"].loc["pior queda %", "total"], "negócios OOS": len(o_ng)}
        L.append(lin)
        saida.append({"nome": n, "NOME": o["NOME"], "excesso_20k": e20, "excesso_50k": e50, "metricas": lin,
                      "melhores": o_ng.tail(10), "piores": o_ng.head(10), "por_ativo": R["por_ativo"], "ano": R["ano"]})
    t = pd.DataFrame(L).set_index("fundo")
    print(t.round(2).to_string())
    return t, saida


def diag():
    out = {}
    imp = lambda n: importlib.import_module(n)
    # (1) funding: decomposição OOS (R$ 20 mil) e sem contraparte
    m = imp("cr_funding")
    d = m.carrega()
    x = m._simula(d, 20000, 1, 0, **m.PARAMS)
    pnl = K.para_dias(x["pnl"].sum(axis=1))
    comp = pd.DataFrame({"carry líquido de custos": pnl, "conta exterior (CDI+câmbio+IOF)": -x["conta"], "contraparte": -x["contraparte"]})
    out["funding_decomp"] = (comp.groupby(comp.index.year).sum() / 20000 * 100).loc[2020:]
    out["funding_sem_contraparte_pp"] = oos_pp(m, m.excesso(d, contraparte=0))
    fu = d["fund"]
    out["funding_aa_por_ano"] = (fu.groupby(fu.index.year).mean() * 365 * 100).loc[2020:]
    # (2) prêmio brasileiro
    m = imp("cr_premio_br")
    k = m.premio_global()
    k = k[k.index >= "2019-01-01"]
    out["kimchi_ano"] = k.groupby(k.index.year).agg(["mean", "std"]).round(2)
    fx = K.PTAX.pct_change(fill_method=None) * 100
    btc = K.btc_brl_dia() * 100
    z = pd.concat([k["MB"], fx.rename("dólar %"), btc.rename("BTC %")], axis=1).dropna()
    z["Δprêmio"] = z["MB"].diff()
    out["kimchi_quando"] = {"corr Δprêmio x dólar": z["Δprêmio"].corr(z["dólar %"]), "corr Δprêmio x BTC": z["Δprêmio"].corr(z["BTC %"]),
                            "prêmio médio em dias de BTC <= -8%": z.loc[z["BTC %"] <= -8, "MB"].mean(),
                            "prêmio médio em dias de dólar >= +1,5%": z.loc[z["dólar %"] >= 1.5, "MB"].mean(), "prêmio médio": z["MB"].mean()}
    d = m.carrega()
    pern = m._pernas(d, "mb_bn")
    zz = {}
    for a, (A, B) in pern.items():
        s = np.log(A / B)
        zh = (s - s.rolling(720, min_periods=240).median().shift(1)).abs()
        zz[a] = pd.DataFrame({f">{t:.0%}": (zh > t).groupby(zh.index.year).sum() for t in (.01, .02, .03)})
    out["premio_horas"] = pd.concat(zz)
    # (3) pânico: top20 e alfa
    m = imp("cr_panico")
    d = m.carrega()
    v = {}
    for nome, p in {"btceth .20/2d (PARAMS)": {}, "top20 .20/2d": {"universo": "top20"}, "top20 .15/2d": {"universo": "top20", "queda": .15},
                    "btceth .15/5d": {"queda": .15, "dias": 5}}.items():
        e = m.excesso(d, **p)
        ng = m.negocios(d, **p)
        o = ng[pd.to_datetime(ng.entrada) >= pd.Timestamp(m.CORTE)]
        v[nome] = {"OOS pp": oos_pp(m, e), "alfa vs BTC": K.alfa_vs_btc(e, m.CORTE)[0], "beta": K.alfa_vs_btc(e, m.CORTE)[1],
                   "negócios OOS": len(o), "acerto %": (o.contrib_pp > 0).mean() * 100,
                   "sem 10 melhores pp": oos_pp(m, e) - o.nlargest(10, "contrib_pp").contrib_pp.sum() / (len(e[e.index >= m.CORTE]) / 252)}
    out["panico_variantes"] = pd.DataFrame(v).T
    # (4) fim de semana: retorno médio por janela (bruto, sem custo), BTC e ETH, IS x OOS
    m = imp("cr_fds")
    d = m.carrega()
    P = K.painel_1h("fech", {"h": d["h"].reset_index()})[["BTC", "ETH"]]
    P = P.reindex(pd.date_range(P.index[0], P.index[-1], freq="h"))
    r = np.log(P / P.shift(1))
    w = {}
    for modo in ["fds", "noite", "eua", "asia"]:
        j = pd.Series(m.janela(P.index, modo), index=P.index)
        for per, msk in {"IS 2018-22": (P.index >= "2018-01-01") & (P.index < "2023-01-01"), "OOS 2023-26": P.index >= "2023-01-01"}.items():
            rr = r[j & msk]
            w[(modo, per)] = {"BTC % por ano na janela": rr["BTC"].sum() / (msk.sum() / 8760) * 100,
                              "ETH % por ano na janela": rr["ETH"].sum() / (msk.sum() / 8760) * 100, "% do tempo": j[msk].mean() * 100}
    out["janelas"] = pd.DataFrame(w).T
    # (5) ETF x futuro: o desvio volta em 1 pregão?
    m = imp("cr_etf_futuro")
    d = m.carrega()
    ng = m.negocios(d)
    out["etf_fut_por_par"] = ng.groupby("ativo").agg(n=("contrib_pp", "size"), soma_pp=("contrib_pp", "sum"),
                                                      desvio_medio=("desvio_entrada_%", "mean"), ret_medio=("retorno_%", "mean"))
    # (6) alts: versões
    m = imp("cr_alts")
    d = m.carrega()
    v = {}
    for nome, p in {"mom 28 sem hedge (PARAMS)": {}, "mom 28 hedge BTC": {"hedge": "btc"}, "rev 7 sem hedge": {"modo": "rev", "janela": 7},
                    "rev 7 hedge BTC": {"modo": "rev", "janela": 7, "hedge": "btc"}}.items():
        e = m.excesso(d, **p)
        a, b = K.alfa_vs_btc(e, m.CORTE)
        v[nome] = {"OOS pp": oos_pp(m, e), "alfa vs BTC": a, "beta": b}
    out["alts_variantes"] = pd.DataFrame(v).T
    # (7) eventos: sensibilidade ao financiamento extra e por ano
    m = imp("cr_eventos")
    d = m.carrega()
    v = {}
    for nome, p in {"venda 30d (PARAMS)": {}, "venda +30% a.a. de custo extra": {"fin": .30}, "venda +100% a.a.": {"fin": 1.0},
                    "venda 10d": {"h": 10}, "venda 60d": {"h": 60}, "compra 30d": {"modo": "compra"}, "halving 30d": {"modo": "halving"}}.items():
        e = m.excesso(d, **p)
        a, b = K.alfa_vs_btc(e, m.CORTE)
        v[nome] = {"OOS pp": oos_pp(m, e), "alfa vs BTC": a, "beta": b}
    out["eventos_variantes"] = pd.DataFrame(v).T
    M = m._simula(d, 20000, 1, 0, **{k: v_ for k, v_ in m.PARAMS.items()})
    conc = (M["E"] != 0).sum(axis=1)
    out["eventos_concorrencia"] = conc.groupby(conc.index.year).agg(["mean", "max"])
    out["eventos_ano"] = pickle.load(open(BAT / "cr_eventos.pkl", "rb"))["R20"]["ano"]
    # (8) staking
    m = imp("cr_staking")
    d = m.carrega()
    v = {}
    for nome, p in {"neutro (PARAMS)": {}, "neutro sem contraparte": {"contraparte": 0}, "beta (ETH em staking, BR)": {"modo": "beta"}}.items():
        e = m.excesso(d, **p)
        a, b = K.alfa_vs_btc(e, m.CORTE)
        v[nome] = {"OOS pp": oos_pp(m, e), "alfa vs BTC": a, "beta": b}
    out["staking_variantes"] = pd.DataFrame(v).T
    apy = d["apy"]["apy"]
    out["staking_apy_ano"] = apy.groupby(apy.index.year).mean()
    for k_, v_ in out.items():
        print(f"\n### {k_}\n{v_ if not isinstance(v_, pd.DataFrame) else v_.round(2).to_string()}")
    return out


if __name__ == "__main__":
    t, saida = resumo()
    dg = diag()
    pickle.dump(saida, open(AQUI.parent / "resultados" / "pf2_cripto.pkl", "wb"))                 # lista de dicts (contrato da rodada)
    pickle.dump({"tabela": t, "diagnosticos": dg}, open(AQUI.parent / "resultados" / "pf2_cripto_diag.pkl", "wb"))
    md = []
    for s in saida:
        md.append(f"\n#### {s['nome']} — 10 melhores negócios OOS\n\n" + s["melhores"].iloc[::-1].round(2).to_markdown(index=False))
        md.append(f"\n\n#### {s['nome']} — 10 piores negócios OOS\n\n" + s["piores"].round(2).to_markdown(index=False) + "\n")
    (AQUI.parent / "resultados" / "pf2_cripto" / "negocios.md").write_text("\n".join(md), encoding="utf-8")
