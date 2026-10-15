"""
Roda a bateria de robustez dos fundos da frente micro_cme com R$ 20 mil e R$ 50 mil e salva pf/resultados/micro_cme.pkl.

    python pf/fundos/cme_rodar.py                 # todos (~30-40 min)
    python pf/fundos/cme_rodar.py cme_vxm         # um só (salva pf/resultados/micro_cme_<fundo>.pkl; o .pkl da frente junta todos)
"""
import importlib
import pickle
import sys
import time
import types
from pathlib import Path

import numpy as np
import pandas as pd

import cme_comum as K
import comum as C
import pf
import robustez as RB

FUNDOS = ["cme_carry_g10", "cme_tendencia", "cme_vxm", "cme_metais", "cme_cripto", "cme_sazonal", "cme_juros_fed"]
OUT = K.PF / "resultados"


def ligado(m, capital):
    """Módulo com excesso/posicoes/negocios fixados no capital (a bateria chama m.excesso(d, ...))."""
    w = types.SimpleNamespace(**{k: getattr(m, k) for k in dir(m) if not k.startswith("__")})
    w.excesso = lambda d, **kw: m.excesso(d, capital=capital, **kw)
    w.posicoes = lambda d, **kw: m.posicoes(d, capital=capital, **kw)
    w.negocios = lambda d, **kw: m.negocios(d, capital=capital, **kw)
    return w


def resumo(m, d, capital, n_leque=60):
    w = ligado(m, capital)
    R = RB.bateria(w, d, n_leque=n_leque, log=lambda s: print(f"   [{m.__name__} {capital/1000:.0f}k]{s}", flush=True))
    e = R["e"]
    # depois do IR: P&L dos futuros 15% ao ano (com compensação), CDI do caixa 15%; comparado ao CDI líquido
    ex_ir = K.apos_ir(m.classes_ir(d, capital=capital), capital)
    cdil = pf.cdi_liquido()
    r_ir = (cdil + ex_ir - RB.DESPESAS / 252)[lambda x: x.index >= pd.Timestamp(m.INICIO)]
    oos_ir = C.anual(RB.oos(m, r_ir)) - C.anual(RB.oos(m, cdil.reindex(r_ir.index)))
    ins_ir = C.anual(RB.ins(m, r_ir)) - C.anual(RB.ins(m, cdil.reindex(r_ir.index)))
    mt = R["metricas"]
    ng = R["negocios"]
    o = ng[pd.to_datetime(ng["entrada"]) >= pd.Timestamp(m.CORTE)]
    alav = {}
    for a in getattr(m, "ALAVANCAGENS", [1]):
        x = RB.cota(m, m.excesso(d, capital=capital, alavancagem=a))
        alav[a] = {"OOS pp": RB.ativo_aa(m, x), "pior queda %": C.metricas(RB.oos(m, x), C.CDI)["pior queda %"]}
    return {
        "excesso": e, "excesso_ir": ex_ir,
        "OOS pp": mt.loc["ativo a.a. pp", "fora da amostra"], "IS pp": mt.loc["ativo a.a. pp", "dentro da amostra"],
        "OOS pp depois IR": oos_ir, "IS pp depois IR": ins_ir,
        "IR OOS": mt.loc["IR vs bench", "fora da amostra"], "vol OOS %": mt.loc["vol a.a. %", "fora da amostra"],
        "pior queda OOS %": mt.loc["pior queda %", "fora da amostra"], "Sharpe OOS": mt.loc["Sharpe", "fora da amostra"],
        "ano": R["ano"], "PBO %": R["resumo_grade"]["PBO %"], "resumo_grade": R["resumo_grade"], "grade": R["grade"],
        "P(bater 3a) %": R["mc"].loc["P(bater o benchmark) %", "3 ano(s)"], "mc": R["mc"],
        "leque": R["leque"]["ativo OOS pp"].describe(percentiles=[.05, .5, .95]) if len(R["leque"]) else None,
        "custo": R["custo"], "atraso": R["atraso"], "truncamento": R["truncamento"], "placebo": R["placebo"],
        "melhores": o.nlargest(10, "contrib_pp"), "piores": o.nsmallest(10, "contrib_pp"), "por_ativo": R["por_ativo"],
        "sem_maiores": R["sem_maiores"], "sem_ativo": R["sem_ativo"], "regime": R["regime"], "wf_ativo": R["wf_ativo"],
        "n_negocios_oos": len(o), "alavancagem": alav,
        "saldo_ibkr_medio": m.livro_completo(d, capital=capital)[0]["saldo"].pipe(lambda s: s[s.index >= pd.Timestamp(m.CORTE)]).mean(),
    }


def roda(nome, n_leque=60):
    m = importlib.import_module(nome)
    d = K.carrega()
    t0 = time.time()
    out = {"nome": m.NOME, "modulo": nome, "tese": m.TESE, "aplicavel": m.APLICAVEL, "motivo": m.MOTIVO, "params": m.PARAMS,
           "regime": m.REGIME, "inicio": m.INICIO, "corte": m.CORTE}
    for cap in pf.CAPITAIS:
        out[f"{cap // 1000}k"] = resumo(m, d, cap, n_leque)
    out["excesso 20k"], out["excesso 50k"] = out["20k"]["excesso"], out["50k"]["excesso"]
    out["metricas"] = {k: {c: out[k][c] for c in ("OOS pp", "OOS pp depois IR", "IR OOS", "PBO %", "P(bater 3a) %")} for k in ("20k", "50k")}
    print(f"{nome}: {time.time() - t0:.0f}s", out["metricas"], flush=True)
    with open(OUT / f"micro_cme_{nome}.pkl", "wb") as f:
        pickle.dump(out, f)
    return out


def junta():
    lst = [pickle.load(open(OUT / f"micro_cme_{n}.pkl", "rb")) for n in FUNDOS if (OUT / f"micro_cme_{n}.pkl").exists()]
    with open(OUT / "micro_cme.pkl", "wb") as f:
        pickle.dump(lst, f)
    return lst


if __name__ == "__main__":
    alvo = sys.argv[1:] or FUNDOS
    for n in alvo:
        if n != "junta":
            roda(n)
    junta()
