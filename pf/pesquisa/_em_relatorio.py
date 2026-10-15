"""Junta as baterias da frente pf2_emergentes -> pf/resultados/pf2_emergentes.pkl + tabelas para o caderno (imprime em markdown)."""
import pickle
import sys
from pathlib import Path

PF = Path(__file__).resolve().parent.parent
for p in (str(PF.parent), str(PF), str(PF / "fundos")):
    sys.path.insert(0, p)
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

import comum as C  # noqa: E402
import em_comum as E  # noqa: E402
import robustez as RB  # noqa: E402
import rodar_pf as RP  # noqa: E402

FUNDOS = ["em_argentina", "em_panico_pais", "em_eleicoes", "em_china_adr_hk", "em_india_adr", "em_latam_commod", "em_fx_exportadoras",
          "em_fronteira"]


def decomp(m, d, cap):
    """Decomposição do excesso OOS (pp a.a.): ativos (P&L dos papéis com custos de negociação), remessa, câmbio do saldo, CDI perdido,
    hedge WDO, extra (Rússia sintética)."""
    if m.__name__ == "em_panico_pais":
        res = m._roda(d, cap, 1, 0, 1, *[m.PARAMS[k] for k in ("queda", "jan", "dias", "hedge", "peso")], m.PARAMS["russia"])
    else:
        res = E.roda(m, d, cap)
    o = lambda s: s[s.index >= pd.Timestamp(m.CORTE)]
    anos = len(o(res["e"])) / 252
    f = lambda s: float(o(s.reindex(E.DIAS).fillna(0)).sum() / cap * 100 / anos)
    return {"papéis": f(E.pf.usd_para_br(res["ativo_brl"].sum(axis=1))), "remessa": -f(res["remessa"]), "câmbio do saldo": f(res["cambio"]),
            "CDI perdido": -f(res["classes"]["_cdi_perdido"]), "WDO": f(res.get("wdo", pd.Series(0.0, index=E.DIAS))),
            "Rússia sint.": f(res["russia"]) if "russia" in res else 0.0, "saldo IBKR médio R$": float(o(res["saldo"]).mean())}


def main():
    linhas, saida, neg = [], [], {}
    for n in FUNDOS:
        o = pickle.load(open(PF / "resultados" / "bateria" / f"{n}.pkl", "rb"))
        m = RP.carrega_modulo(n)
        d = m.carrega()
        R = o["R20"]
        mc = R["mc"]
        e20 = o["r20"] - C.CDI.reindex(o["r20"].index).fillna(0)
        e50 = o["r50"] - C.CDI.reindex(o["r50"].index).fillna(0)
        ba = E.beta_alfa(e20, m.CORTE)
        dec20, dec50 = decomp(m, d, 20_000), decomp(m, d, 50_000)
        lq = R["leque"]["ativo OOS pp"]
        met = {"OOS desde": m.CORTE[:7], "ativo 20k pp": o["ativo20"], "ativo 50k pp": o["ativo50"], "depois IR 20k pp": o["ativo_ir20"],
               "depois IR 50k pp": o["ativo_ir50"], "IR OOS": o["ir_oos20"], "PBO %": R["resumo_grade"]["PBO %"],
               "P(bater 3a) %": mc.loc["P(bater o benchmark) %", "3 ano(s)"], "sem 10 melhores": R["sem_maiores"]["sem os 10 melhores"],
               "custo 2x": R["custo"]["2x"], "custo 0x": R["custo"]["0x"], "t+2": R["atraso"]["t+2"], "leque p5": lq.quantile(.05),
               "leque mediana": lq.median(), "placebo p": R["placebo"]["p-valor (fração de placebos >= real)"],
               "excesso bruto OOS (placebo real)": R["placebo"]["excesso bruto OOS real pp"],
               "truncamento ok": bool(R["truncamento"]["passou"].all()), "beta EEM": ba["beta EEM"], "alfa EEM pp": ba["alfa a.a. pp"],
               "negócios OOS": int((pd.to_datetime(R["negocios"].entrada) >= pd.Timestamp(m.CORTE)).sum()),
               **{f"20k {k}": v for k, v in dec20.items()}, **{f"50k {k}": v for k, v in dec50.items()}}
        linhas.append({"arquivo": n, "fundo": o["NOME"], **met})
        saida.append({"nome": n, "NOME": o["NOME"], "excesso_20k": e20, "excesso_50k": e50, "metricas": met, "PARAMS": o["PARAMS"]})
        neg[n] = R["negocios"]
    t = pd.DataFrame(linhas).set_index("arquivo")
    pickle.dump(saida, open(PF / "resultados" / "pf2_emergentes.pkl", "wb"))
    pd.set_option("display.width", 300)
    print(t.drop(columns=["fundo"]).round(2).T.to_markdown())
    for n, ng in neg.items():
        ng = ng.copy()
        ng["entrada"] = pd.to_datetime(ng["entrada"]).dt.date
        ng["saida"] = pd.to_datetime(ng["saida"]).dt.date
        cols = ["ativo", "lado", "entrada", "saida", "dias", "retorno_%", "contrib_pp"]
        print(f"\n### {n} — 10 melhores\n")
        print(ng.nlargest(10, "contrib_pp")[cols].round(2).to_markdown(index=False))
        print(f"\n### {n} — 10 piores\n")
        print(ng.nsmallest(10, "contrib_pp")[cols].round(2).to_markdown(index=False))
    # liquidez da fronteira
    X = E.yahoo()
    L = []
    for t_ in ["VNM", "VNAM", "AFK", "KSA", "QAT", "UAE", "KWT", "EPU", "ARGT", "ECNS", "EPHE", "THD", "GREK", "TUR", "EIDO", "EZA", "FRDM"]:
        c, v = X.get(f"Close|{t_}"), X.get(f"Volume|{t_}")
        if c is None:
            continue
        s = (c * v).dropna()
        L.append({"ETF": t_, "desde": c.first_valid_index().date(), "volume médio 252d US$ mi": s.iloc[-252:].mean() / 1e6,
                  "pregões sem negócio 252d": int((v.iloc[-252:] <= 0).sum())})
    for t_ in E.MORTOS:
        L.append({"ETF": t_, "desde": "sem dado (deslistado/fechado)", "volume médio 252d US$ mi": np.nan, "pregões sem negócio 252d": np.nan})
    print("\n### liquidez\n")
    print(pd.DataFrame(L).round(2).to_markdown(index=False))


if __name__ == "__main__":
    main()
