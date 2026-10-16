"""Frente pf3_internacional_B: tabelas capital x sleeve x hedge e resumo das baterias dos 5 fundos *_v2 (conta em dólar v2)."""
import pickle
import sys
from pathlib import Path

PF = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(PF / "fundos"), str(PF), str(PF.parent)]
import importlib  # noqa: E402

import pandas as pd  # noqa: E402

import _v2_comum as V2  # noqa: E402

FUNDOS = ["mineradoras_v2", "variancia_v2", "credito_em_v2", "carry_g10_v2", "eurex_panico_v2"]
pd.set_option("display.width", 250)
tabs, res = [], []
for n in FUNDOS:
    m = importlib.import_module(n)
    d = m.carrega()
    extra = {k: [v] for k, v in getattr(m, "SLEEVE_MARGEM", {}).items()}
    t = V2.tabela(m, d, extra=extra)
    t.insert(0, "fundo", n)
    tabs.append(t)
    o = pickle.load(open(PF / "resultados" / "bateria" / f"{n}.pkl", "rb"))
    R = o["R20"]
    res.append({"fundo": n, "ativo 20k": o["ativo20"], "ativo 50k": o["ativo50"], "IR 20k": o["ativo_ir20"], "IR 50k": o["ativo_ir50"],
                "IR OOS": o["ir_oos20"], "PBO %": R["resumo_grade"]["PBO %"], "P(bater 3a) %": R["mc"].loc["P(bater o benchmark) %", "3 ano(s)"],
                "custo 2x": R["custo"]["2x"], "t+2": R["atraso"]["t+2"], "sem 10 melhores": R["sem_maiores"]["sem os 10 melhores"],
                "walk-forward": R["wf_ativo"], "placebo p": R["placebo"]["p-valor (fração de placebos >= real)"],
                "truncamento ok": bool(R["truncamento"]["passou"].all())})
    print(n, "ok", flush=True)
T = pd.concat(tabs, ignore_index=True)
T.to_csv(PF / "resultados" / "pf3_internacional_B_tabela.csv", index=False, encoding="utf-8-sig")
S = pd.DataFrame(res)
S.to_csv(PF / "resultados" / "pf3_internacional_B_baterias.csv", index=False, encoding="utf-8-sig")
pickle.dump({"tabela": T, "baterias": S}, open(PF / "resultados" / "pf3_internacional_B.pkl", "wb"))
print(T.round(2).to_string())
print(S.round(2).to_string())
