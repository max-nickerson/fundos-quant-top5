"""
Frente PF2 "fluxo global" — junta as baterias (pf/resultados/bateria/fg_*.pkl, geradas por `python pf/rodar_pf.py um fg_<nome>`),
roda as VARIANTES de cada fundo (IS/OOS com R$ 20 mil) e grava:
  - pf/resultados/pf2_fluxo_global.pkl  (lista de dicts: nome, excesso 20k, excesso 50k, métricas)
  - pf/pesquisa/pf2_fluxo_global_tabelas.md  (tabelas, variantes e 10 melhores/piores negócios de cada fundo — anexo do caderno)
    python pf/fundos/fg_rodar.py
"""
import importlib
import pickle
import sys
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")
AQUI = Path(__file__).resolve().parent
PF = AQUI.parent
sys.path[:0] = [str(AQUI), str(PF), str(PF.parent)]
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

import comum as C  # noqa: E402
import robustez as RB  # noqa: E402

FUNDOS = ["fg_fim_mes", "fg_indices_exclusao", "fg_taxloss", "fg_russell", "fg_dividendo_b3", "fg_merger_arb", "fg_ipo_quiet",
          "fg_spinoff_pequeno"]


def f(x, d=2):
    try:
        return f"{float(x):+.{d}f}"
    except Exception:                                                     # noqa: BLE001
        return "n/d"


def main():
    res, md = [], ["# PF2 fluxo global — tabelas geradas (anexo de pf2_fluxo_global.md)", ""]
    linhas = []
    for nome in FUNDOS:
        o = pickle.load(open(PF / "resultados" / "bateria" / f"{nome}.pkl", "rb"))
        R = o["R20"]
        rg, mc = R["resumo_grade"], R["mc"]
        cdi = C.CDI
        m = {"aplicável": o["APLICAVEL"], "OOS desde": o["CORTE"][:7], "ativo 20k pp": o["ativo20"], "ativo 50k pp": o["ativo50"],
             "depois do IR 20k pp": o["ativo_ir20"], "depois do IR 50k pp": o["ativo_ir50"], "IR OOS": o["ir_oos20"], "PBO %": rg["PBO %"],
             "P(bater 3a) %": mc.loc["P(bater o benchmark) %", "3 ano(s)"], "sem 10 melhores": R["sem_maiores"].get("sem os 10 melhores"),
             "custo 0x": R["custo"].get("0x"), "custo 2x": R["custo"].get("2x"), "exec t+2": R["atraso"].get("t+2"), "walk-forward": R["wf_ativo"],
             "leque p5": R["leque"]["ativo OOS pp"].quantile(.05), "leque mediana": R["leque"]["ativo OOS pp"].median(),
             "placebo p": R["placebo"]["p-valor (fração de placebos >= real)"], "truncamento ok": bool(R["truncamento"]["passou"].all())}
        res.append({"nome": nome, "NOME": o["NOME"], "excesso_20k": o["r20"] - cdi.reindex(o["r20"].index), "excesso_50k": o["r50"] - cdi.reindex(o["r50"].index),
                    "metricas": m, "PARAMS": o["PARAMS"], "metricas_tabela": R["metricas"]})
        linhas.append({"fundo": nome, **m})
        # variantes
        M = importlib.import_module(nome)
        d = M.carrega()
        var = []
        for k, v in {"(fundo)": {}, **getattr(M, "VARIANTES", {})}.items():
            try:
                r = RB.cota(M, M.excesso(d, **{**M.PARAMS, **v}))
                var.append({"variante": k, "IS pp": RB.ativo_aa(M, r, RB.ins), "OOS pp": RB.ativo_aa(M, r)})
            except Exception as ex:                                       # noqa: BLE001
                var.append({"variante": k, "IS pp": np.nan, "OOS pp": np.nan, "erro": str(ex)[:60]})
        ng = R["negocios"].copy()
        cols = [c for c in ["ativo", "lado", "entrada", "saida", "dias", "retorno_%", "ret_menos_hedge_%", "dividendo_%", "contrib_pp"] if c in ng]
        ng_ev = ng[~ng.ativo.astype(str).str.startswith("hedge")]
        md += [f"## {o['NOME']} (`{nome}`)", "", f"PARAMS (escolhidos no IS): `{o['PARAMS']}`", "",
               "| métrica | valor |", "|---|---|"] + [f"| {k} | {f(v) if isinstance(v, (float, np.floating)) else v} |" for k, v in m.items()] + [""]
        md += ["**Variantes (ativo sobre o CDI, R$ 20 mil, pp a.a.)**", "", pd.DataFrame(var).round(2).to_markdown(index=False), ""]
        if len(ng_ev):
            oos = ng_ev[pd.to_datetime(ng_ev.entrada) >= o["CORTE"]]
            extra = ""
            if "ret_menos_hedge_%" in ng_ev:
                extra = (f"; retorno médio por negócio menos o hedge: IS {ng_ev[pd.to_datetime(ng_ev.entrada) < o['CORTE']]['ret_menos_hedge_%'].mean():+.2f}%"
                         f" / OOS {oos['ret_menos_hedge_%'].mean():+.2f}%")
            md += [f"Negócios: {len(ng_ev)} ({len(oos)} no OOS); acerto OOS {(oos.contrib_pp > 0).mean() * 100:.0f}%{extra}.", "",
                   "**10 melhores negócios**", "", ng_ev.nlargest(10, "contrib_pp")[cols].round(2).to_markdown(index=False), "",
                   "**10 piores negócios**", "", ng_ev.nsmallest(10, "contrib_pp")[cols].round(2).to_markdown(index=False), ""]
        ano = R["ano"] if isinstance(R.get("ano"), pd.Series) else None
        if ano is not None:
            md += ["**Excesso sobre o CDI por ano (pp)**: " + ", ".join(f"{int(a)}: {v:+.1f}" for a, v in ano.items() if np.isfinite(v)), ""]
        print(nome, "ok", flush=True)
    t = pd.DataFrame(linhas).set_index("fundo")
    md = md[:2] + ["## Resumo", "", t.round(2).to_markdown(), ""] + md[2:]
    pickle.dump(res, open(PF / "resultados" / "pf2_fluxo_global.pkl", "wb"))
    (PF / "pesquisa" / "pf2_fluxo_global_tabelas.md").write_text("\n".join(md), encoding="utf-8")
    print(t.round(2).to_string())


if __name__ == "__main__":
    main()
