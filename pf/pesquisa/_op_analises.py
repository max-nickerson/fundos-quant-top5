"""Frente pf2_opcoes: junta as baterias (pf/resultados/bateria/op_*.pkl) em pf/resultados/pf2_opcoes.pkl e imprime as análises do caderno
(wheel x ação, carteira com/sem hedge, calibração da CPM, liquidez de IDI/DOL/WDO, negócios). Uso: python pf/pesquisa/_op_analises.py"""
import pickle
import sys
from pathlib import Path

import numpy as np
import pandas as pd

PF = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(PF.parent), str(PF), str(PF / "fundos")]
import comum as C  # noqa: E402
import pf as P  # noqa: E402
import robustez as RB  # noqa: E402
import op_base as O  # noqa: E402

pd.set_option("display.width", 250)
FUNDOS = ["op_travas_multi", "op_eventos", "op_wheel", "op_xsp_cboe", "op_vix_hedge", "op_dolar", "op_copom", "op_aluguel"]
BAT = PF / "resultados" / "bateria"


def resumo():
    out, tab = [], []
    for n in FUNDOS:
        o = pickle.load(open(BAT / f"{n}.pkl", "rb"))
        R = o["R20"]
        mm = type("M", (), {"CORTE": o["CORTE"], "BENCHMARK": "CDI"})
        met = {"ativo20": o["ativo20"], "ativo50": o["ativo50"], "ativo_ir20": o["ativo_ir20"], "ativo_ir50": o["ativo_ir50"],
               "IR_oos20": o["ir_oos20"], "IR_oos50": o["ir_oos50"], "PBO": R["resumo_grade"]["PBO %"],
               "P_bater_3a": R["mc"].loc["P(bater o benchmark) %", "3 ano(s)"], "custo2x": R["custo"]["2x"], "t+2": R["atraso"]["t+2"],
               "sem10": R["sem_maiores"]["sem os 10 melhores"], "truncamento_ok": bool(R["truncamento"]["passou"].all()),
               "leque_p5": R["leque"]["ativo OOS pp"].quantile(.05), "leque_med": R["leque"]["ativo OOS pp"].median(),
               "vol_oos": R["metricas"]["fora da amostra"]["vol a.a. %"], "dd_oos": R["metricas"]["fora da amostra"]["pior queda %"],
               "ativo_IS": R["metricas"]["dentro da amostra"]["ativo a.a. pp"], "placebo_p": R["placebo"]["p-valor (fração de placebos >= real)"]}
        out.append({"nome": n, "NOME": o["NOME"], "APLICAVEL": o["APLICAVEL"], "CORTE": o["CORTE"], "PARAMS": o["PARAMS"],
                    "excesso20": o["r20"] - C.CDI.reindex(o["r20"].index), "excesso50": o["r50"] - C.CDI.reindex(o["r50"].index), "metricas": met})
        tab.append({"fundo": n, **{k: (round(v, 2) if isinstance(v, float) else v) for k, v in met.items()}})
    pickle.dump(out, open(PF / "resultados" / "pf2_opcoes.pkl", "wb"))
    t = pd.DataFrame(tab).set_index("fundo")
    print(t.to_string())
    return t


def negocios_extremos():
    for n in FUNDOS:
        o = pickle.load(open(BAT / f"{n}.pkl", "rb"))
        ng = o["R20"]["negocios"]
        cols = [c for c in ["ativo", "lado", "entrada", "saida", "evento", "strikes", "K", "serie", "contratos", "lotes", "pnl_rs", "contrib_pp"] if c in ng]
        print(f"\n== {n}: {len(ng)} negócios; por ativo (pp):", ng.groupby("ativo").contrib_pp.sum().round(1).sort_values().to_dict())
        print("melhores:\n", ng.nlargest(10, "contrib_pp")[cols].round(2).to_string(index=False))
        print("piores:\n", ng.nsmallest(10, "contrib_pp")[cols].round(2).to_string(index=False))


def wheel_vs_acao():
    import op_wheel as W
    d = W.carrega()
    print("\n== wheel x comprar e segurar (mesmos papéis, pesos iguais, excesso sobre o CDI)")
    for nomes in ("3", "6"):
        pnl, _ = W._livro(d, 20000, {**W.PARAMS, "nomes": nomes}, 0, 1)
        e = sum(pnl.values()) / 20000
        opc = sum(v for k, v in pnl.items() if k.endswith("_opc")) / 20000
        ac = sum(v for k, v in pnl.items() if k.endswith("_acao")) / 20000
        cdi = C.CDI.reindex(O.DIAS).fillna(0)
        R = d["R"][W.NOMES[nomes]].copy()
        R.loc[R.index < "2018-01-01", "VALE"] = np.nan                     # mesmo universo do wheel
        bh = R.mean(axis=1).fillna(0) - cdi
        for nome, a, b in (("IS", "2014-03-01", "2020-12-31"), ("OOS", "2021-01-01", "2026-12-31")):
            x, y = e[a:b], bh[a:b]
            beta = np.cov(x, y)[0, 1] / y.var()
            print(f"  {nomes} papéis {nome}: wheel {x.mean() * 25200:+.1f} pp (opções {opc[a:b].mean() * 25200:+.1f}, ações {ac[a:b].mean() * 25200:+.1f}) | "
                  f"ação {y.mean() * 25200:+.1f} pp | beta {beta:.2f} | alfa (wheel − beta x ação) {(x - beta * y).mean() * 25200:+.1f} pp | "
                  f"tempo com ação {(sum(v for k, v in pnl.items() if k.endswith('_acao'))[a:b] != 0).mean() * 100:.0f}% dos dias")
        if nomes == "3":
            cls = {"opcoes_b3": opc * 20000, "isento": ac * 20000}
            ri = pf_ir(cls, 20000)
            o = ri["2021":].mean() * 25200
            print(f"  depois do IR com a perna em ações ISENTA (vendas <= R$ 20 mil/mês): excesso OOS {o:+.1f} pp antes de descontar o CDI líquido")


def pf_ir(cls, cap):
    return P.apos_ir_por_classe(cls, cap) / cap


def hedge_carteira():
    import op_vix_hedge as V
    d = V.carrega()
    print("\n== carteira BOVA11 (R$ 20 mil) com e sem hedge (retorno total, queda máxima)")
    rb = C.R_IBOV.reindex(O.DIAS).fillna(0)
    for ini in ("2019-06-01", "2021-01-01"):
        lin = {}
        for nome, kw in (("sem hedge", None), ("trava VIX sempre", {"hedge": "vix_cs", "gatilho": "sempre"}),
                         ("trava VIX vol baixa", {"hedge": "vix_cs", "gatilho": "vol_baixa"}), ("put BOVA vol baixa", {"hedge": "put", "gatilho": "vol_baixa"}),
                         ("put BOVA sempre", {"hedge": "put", "gatilho": "sempre"}), ("collar sempre", {"hedge": "collar", "gatilho": "sempre"})):
            h = V.excesso(d, **kw) if kw else 0
            r = (rb + h)[ini:]
            eq = (1 + r).cumprod()
            lin[nome] = {"retorno a.a. %": ((eq.iloc[-1]) ** (252 / len(eq)) - 1) * 100, "queda máx %": (eq / eq.cummax() - 1).min() * 100,
                         "mar/2020 %": ((1 + r["2020-02-15":"2020-03-31"]).prod() - 1) * 100 if ini < "2020" else np.nan}
        print(f"  desde {ini}:\n", pd.DataFrame(lin).T.round(1).to_string())


def copom_calibracao():
    import op_copom as M
    d = M.carrega()
    c, cp = d["cpm"], d["copom"]
    cp = cp.assign(mes=[f"{M.LETRA[x.month - 1]}{x.year % 100:02d}" for x in cp.data]).drop_duplicates("mes").set_index("mes")
    L = []
    for (dia, m), g in c.groupby(["data", "mes"]):
        if m in cp.index and cp.at[m, "data"] > dia:
            for _, z in g.iterrows():
                L.append({"preco": z.preco, "ganhou": z.bp == cp.at[m, "delta"], "ano": dia.year})
    r = pd.DataFrame(L)
    r["faixa"] = pd.cut(r.preco, [0, 5, 10, 25, 50, 75, 90, 100])
    print("\n== CPM: preço (probabilidade implícita) x frequência real, 2020–2026 (dias baixados)")
    print(r.groupby("faixa", observed=True).agg(n=("ganhou", "size"), preco_medio=("preco", "mean"), acerto_pct=("ganhou", lambda x: x.mean() * 100)).round(1).to_string())


def liquidez_pr():
    t = pd.read_parquet(O.DADOS / "pr_opcoes.parquet")
    t = t[t.ticker.str.len() > 6]
    t["raiz"] = t.ticker.str[:3]
    neg = t.RglrTraddCtrcts.fillna(0) > 0
    g = t.assign(neg=neg, oferta=t.BestBidPric.notna() & t.BestAskPric.notna(), ctr=t.RglrTraddCtrcts.where(neg)).groupby("raiz")
    print("\n== opções de juros/dólar no BVBG.086 (2º–4º pregões do mês, 2018–2026)")
    print(pd.DataFrame({"dias": g.data.nunique(), "séries negociadas/dia": g.neg.sum() / g.data.nunique(),
                        "com bid e ask no fechamento/dia": g.oferta.sum() / g.data.nunique(), "contratos medianos por série negociada": g.ctr.median()}).round(1).to_string())


if __name__ == "__main__":
    resumo()
    negocios_extremos()
    wheel_vs_acao()
    hedge_carteira()
    copom_calibracao()
    liquidez_pr()
