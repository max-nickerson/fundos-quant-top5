"""Junta as baterias da frente pf2_juros_fx -> pf/resultados/pf2_juros_fx.pkl e imprime a tabela do caderno."""
import pickle
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

AQUI = Path(__file__).resolve().parent.parent
BAT = AQUI / "resultados" / "bateria"
NOMES = ["jx_td_copom", "jx_renda_educa", "jx_lft_desagio", "jx_cdb_fgc", "jx_wdo_panico", "jx_weu_wdo", "jx_treasury_cdi", "jx_deb_evento"]
out, linhas = [], []
for n in NOMES:
    o = pickle.load(open(BAT / f"{n}.pkl", "rb"))
    R = o["R20"]
    mc = R["mc"]
    lin = {"fundo": n, "aplicável": o["APLICAVEL"], "OOS desde": o["CORTE"][:7], "20k pp": o["ativo20"], "20k IR pp": o["ativo_ir20"],
           "50k pp": o["ativo50"], "50k IR pp": o["ativo_ir50"], "IR": o["ir_oos20"], "PBO %": R["resumo_grade"]["PBO %"],
           "P(bater 3a) %": mc.loc["P(bater o benchmark) %", "3 ano(s)"], "leque P(>0) %": (R["leque"]["ativo OOS pp"] > 0).mean() * 100,
           "custo 2x": R["custo"].get("2x"), "t+2": R["atraso"].get("t+2"), "sem 10 melhores": R["sem_maiores"].get("sem os 10 melhores"),
           "truncamento": bool(R["truncamento"]["passou"].all())}
    linhas.append(lin)
    out.append({"nome": n, "NOME": o["NOME"], "excesso20": o["r20"] - __import__("comum").CDI.reindex(o["r20"].index),
                "excesso50": o["r50"] - __import__("comum").CDI.reindex(o["r50"].index), "metricas": lin, "negocios": R["negocios"]})
t = pd.DataFrame(linhas)
pickle.dump(out, open(AQUI / "resultados" / "pf2_juros_fx.pkl", "wb"))
pd.set_option("display.width", 250)
print(t.round(2).to_string())
if len(sys.argv) > 1:
    for n in sys.argv[1:]:
        ng = next(x["negocios"] for x in out if x["nome"] == n)
        print("\n==", n, len(ng))
        if len(ng):
            print(pd.concat([ng.nlargest(10, "contrib_pp"), ng.nsmallest(10, "contrib_pp")]).round(3).to_string())
