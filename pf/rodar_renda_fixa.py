"""
Frente "renda_fixa": roda a bateria de robustez de cada fundo PF de renda fixa (pf/fundos/rf_*.py) com R$ 20 mil e R$ 50 mil.

    python pf/rodar_renda_fixa.py rf_ipca_valor [rf_pre_focus ...] [--rapido]   -> pf/resultados/renda_fixa/<nome>.pkl e .txt
    python pf/rodar_renda_fixa.py --grade rf_ipca_valor                          -> só a grade IS/OOS (para escolher PARAMS no IS)
    python pf/rodar_renda_fixa.py --juntar                                       -> pf/resultados/renda_fixa.pkl (lista de dicts)

Mesmo formato da frente "revisita" (pf/rodar_revisita.py), com duas diferenças de IR:
  - classes_ir pode trazer "_ir_extra" (IR regressivo da renda fixa acima de 15%, R$, na data da venda), descontado depois do IR;
  - o módulo pode definir ALIQUOTAS (ex.: {"fii_ganho": .20} — ganho de capital em FII paga 20%), repassado a pf.apos_ir_por_classe.
"""
import importlib.util
import io
import itertools
import pickle
import sys
import time
import types
from contextlib import redirect_stdout
from pathlib import Path

AQUI = Path(__file__).resolve().parent
for _p in (str(AQUI.parent), str(AQUI), str(AQUI / "fundos")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

import comum as C  # noqa: E402
import pf  # noqa: E402
import robustez as RB  # noqa: E402

SAIDA = AQUI / "resultados" / "renda_fixa"
sys.stdout.reconfigure(encoding="utf-8")
pd.set_option("display.width", 220)
CDI_LIQ = pf.cdi_liquido()


def carrega_modulo(nome):
    spec = importlib.util.spec_from_file_location(nome, AQUI / "fundos" / f"{nome}.py")
    m = importlib.util.module_from_spec(spec)
    sys.modules[nome] = m
    spec.loader.exec_module(m)
    return m


def com_capital(m, capital):
    v = types.SimpleNamespace(**{k: getattr(m, k) for k in dir(m) if not k.startswith("__")})
    v.excesso = lambda d, **kw: m.excesso(d, **{"capital": capital, **kw})
    v.negocios = lambda d, **kw: m.negocios(d, **{"capital": capital, **kw})
    return v


def depois_do_ir(m0, d, capital, e, **params):
    """Excesso diário depois do IR sobre o CDI líquido + checagem de consistência das classes com o excesso antes do IR."""
    cls = {k: v.reindex(C.DIAS).fillna(0) for k, v in m0.classes_ir(d, capital=capital, **params).items()}
    perd = cls.get("_cdi_perdido", pd.Series(0.0, index=C.DIAS))
    irx = cls.get("_ir_extra", pd.Series(0.0, index=C.DIAS))
    reais = {k: v for k, v in cls.items() if not k.startswith("_")}
    bruto = (sum(reais.values()) - perd) / capital
    e = e.reindex(C.DIAS).fillna(0)
    dif = float((bruto - e).abs().sum() / max(e.abs().sum(), 1e-12))
    liq = (pf.apos_ir_por_classe(reais, capital, getattr(m0, "ALIQUOTAS", None)) - .85 * perd - irx) / capital
    tot = {k: float(v[v.index >= m0.INICIO].sum()) for k, v in cls.items()}
    return liq, dif, tot


def oos(m0, s):
    return s[s.index >= pd.Timestamp(m0.CORTE)]


def ativo_ir(m0, e_ir):
    r = CDI_LIQ.reindex(e_ir.index).fillna(0) + e_ir - RB.DESPESAS / 252
    r = r[r.index >= pd.Timestamp(m0.INICIO)]
    return C.anual(oos(m0, r)) - C.anual(oos(m0, CDI_LIQ.reindex(r.index)))


def resumo(m0, R, e_ir):
    o = R["metricas"]["fora da amostra"]
    lq = R["leque"]["ativo OOS pp"] if len(R["leque"]) else pd.Series(dtype=float)
    ng = R["negocios"]
    return {"fundo OOS a.a. %": o["retorno a.a. %"], "CDI OOS a.a. %": o["benchmark a.a. %"], "ativo OOS pp": o["ativo a.a. pp"],
            "ativo OOS depois do IR pp": ativo_ir(m0, e_ir), "IR (inf. ratio) OOS": o["IR vs bench"], "vol OOS %": o["vol a.a. %"],
            "pior queda OOS %": o["pior queda %"], "ativo IS pp": R["metricas"]["dentro da amostra"]["ativo a.a. pp"],
            "PBO %": R["resumo_grade"]["PBO %"], "% variantes > CDI": R["resumo_grade"]["% variantes que batem o benchmark OOS"],
            "P(bater) 3a %": R["mc"].loc["P(bater o benchmark) %", "3 ano(s)"],
            "leque p5": lq.quantile(.05) if len(lq) else np.nan, "leque mediana": lq.median() if len(lq) else np.nan,
            "leque p95": lq.quantile(.95) if len(lq) else np.nan,
            "custo 2x pp": R["custo"].get("2x", np.nan), "t+2 pp": R["atraso"].get("t+2", np.nan),
            "truncamento passou": bool(R["truncamento"]["passou"].all()), "placebo p": R["placebo"]["p-valor (fração de placebos >= real)"],
            "walk-forward pp": R["wf_ativo"], "negócios": len(ng),
            "negócios OOS": int((pd.to_datetime(ng["entrada"]) >= pd.Timestamp(m0.CORTE)).sum()) if len(ng) else 0,
            "sem 10 melhores pp": R["sem_maiores"].get("sem os 10 melhores", np.nan)}


def alavancagens(m0, d, capital):
    out = {}
    for L in getattr(m0, "ALAVANCAGENS", [1]):
        try:
            r = RB.cota(m0, m0.excesso(d, capital=capital, alavancagem=L))
            t = C.metricas(r, C.CDI)
            out[f"{L}x"] = {"ativo OOS pp": RB.ativo_aa(m0, r), "vol OOS %": C.metricas(RB.oos(m0, r), C.CDI)["vol a.a. %"],
                            "pior queda total %": t["pior queda %"], "quebrou": bool(((1 + r).cumprod() < .05).any())}
        except Exception as ex:
            out[f"{L}x"] = {"erro": str(ex)[:200]}
    return pd.DataFrame(out).T


def grade(nome, capital=20000):
    """Grade IS/OOS antes e depois do IR (para escolher PARAMS só pelo IS: maior IR do excesso no IS)."""
    m0 = carrega_modulo(nome)
    d = m0.carrega()
    lin = []
    for v in itertools.product(*m0.GRADE.values()):
        p = {**m0.PARAMS, **dict(zip(m0.GRADE, v))}
        e = m0.excesso(d, capital=capital, **p)
        r = RB.cota(m0, e)
        a = RB.ativo(m0, r)
        lin.append({**dict(zip(m0.GRADE, v)), "IS pp": RB.ativo_aa(m0, r, RB.ins), "IR IS": RB.ir(RB.ins(m0, a)),
                    "OOS pp": RB.ativo_aa(m0, r), "IR OOS": RB.ir(RB.oos(m0, a))})
    t = pd.DataFrame(lin).sort_values("IR IS", ascending=False)
    print(t.round(2).to_string(index=False))
    return t


def roda(nome, n_leque=60):
    m0 = carrega_modulo(nome)
    d = m0.carrega()
    res = {"nome": nome, "NOME": m0.NOME, "aplicavel": m0.APLICAVEL, "motivo": m0.MOTIVO, "instrumentos": m0.INSTRUMENTOS,
           "tese": m0.TESE, "corte": m0.CORTE, "params": m0.PARAMS}
    buf = io.StringIO()
    for cap in pf.CAPITAIS:
        k = f"{cap // 1000}k"
        t0 = time.time()
        m = com_capital(m0, cap)
        with redirect_stdout(buf):
            R = RB.bateria(m, d, n_leque)
        e_ir, dif, tot_cls = depois_do_ir(m0, d, cap, R["e"])
        res[f"excesso_{k}"] = R["e"]
        res[f"excesso_ir_{k}"] = e_ir
        res[f"metricas_{k}"] = {**resumo(m0, R, e_ir), "dif classes x excesso": dif}
        res[f"classes_{k}"] = tot_cls
        res[f"bateria_{k}"] = {kk: R[kk] for kk in ("metricas", "ano", "grade", "resumo_grade", "custo", "atraso", "mc", "truncamento", "placebo",
                                                    "por_ativo", "sem_maiores", "sem_ativo", "regime", "wf_ativo")}
        res[f"leque_{k}"] = R["leque"]
        res[f"negocios_{k}"] = R["negocios"]
        res[f"alavancagem_{k}"] = alavancagens(m0, d, cap)
        if hasattr(m0, "VARIANTES"):
            vv = {}
            for rot, kw in m0.VARIANTES.items():
                try:
                    e = m0.excesso(d, capital=cap, **kw)
                    eir = depois_do_ir(m0, d, cap, e, **{a: b for a, b in kw.items() if a in m0.PARAMS})[0]
                    vv[rot] = (round(RB.ativo_aa(m0, RB.cota(m0, e)), 2), round(ativo_ir(m0, eir), 2))
                except Exception as ex:
                    vv[rot] = f"erro {ex}"[:150]
            res[f"variantes_{k}"] = vv
        print(f"[{nome} {k}] {time.time() - t0:.0f}s", flush=True)
    res["texto"] = texto(res)
    SAIDA.mkdir(parents=True, exist_ok=True)
    pickle.dump(res, open(SAIDA / f"{nome}.pkl", "wb"))
    (SAIDA / f"{nome}.txt").write_text(res["texto"], encoding="utf-8")
    print(res["texto"])
    return res


def texto(res):
    L = [f"=== {res['NOME']} ({res['nome']}) | aplicável: {res['aplicavel']} | {res['motivo']}", f"params: {res['params']}",
         f"instrumentos: {res['instrumentos']}"]
    for k in ("20k", "50k"):
        mt = res[f"metricas_{k}"]
        L.append(f"-- R$ {k}: " + " | ".join(f"{a}: {b:.2f}" if isinstance(b, float) else f"{a}: {b}" for a, b in mt.items()))
        L.append("   alavancagem:\n" + res[f"alavancagem_{k}"].round(2).to_string())
        if f"variantes_{k}" in res:
            L.append("   variantes (antes, depois do IR): " + str(res[f"variantes_{k}"]))
        L.append("   classes IR (P&L total R$): " + str({a: round(b) for a, b in res[f"classes_{k}"].items()}))
    b = res["bateria_20k"]
    L.append("-- resumo grade\n" + str({a: (round(v, 2) if isinstance(v, float) else v) for a, v in b["resumo_grade"].items()}))
    L.append("-- R$ 20k: custo\n" + b["custo"].round(2).to_string() + "\n-- atraso\n" + b["atraso"].round(2).to_string())
    L.append("-- truncamento\n" + b["truncamento"].to_string())
    L.append("-- placebo\n" + str({a: round(v, 3) for a, v in b["placebo"].items()}))
    L.append("-- Monte Carlo\n" + b["mc"].round(2).to_string())
    L.append("-- grade (20k)\n" + b["grade"].round(2).to_string())
    L.append("-- ano a ano (20k)\n" + b["ano"].round(2).to_string())
    ng = res["negocios_20k"]
    if len(ng):
        L.append("-- 10 melhores negócios (20k)\n" + ng.nlargest(10, "contrib_pp").round(3).to_string(index=False)[:4000])
        L.append("-- 10 piores negócios (20k)\n" + ng.nsmallest(10, "contrib_pp").round(3).to_string(index=False)[:4000])
    L.append("-- por ativo (20k)\n" + b["por_ativo"].head(15).round(3).to_string())
    L.append("-- concentração (20k)\n" + b["sem_maiores"].round(2).to_string())
    return "\n".join(L)


def juntar():
    out = [pickle.load(open(p, "rb")) for p in sorted(SAIDA.glob("rf_*.pkl"))]
    pickle.dump(out, open(AQUI / "resultados" / "renda_fixa.pkl", "wb"))
    tab = pd.DataFrame({r["nome"]: {**{f"{a} 20k": b for a, b in r["metricas_20k"].items()},
                                    **{f"{a} 50k": b for a, b in r["metricas_50k"].items()}} for r in out}).T
    cols = [c for c in tab.columns if any(s in c for s in ("ativo OOS pp", "depois do IR", "IR (inf", "PBO", "P(bater"))]
    print(tab[cols].round(2).to_string())
    return out


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if "--juntar" in sys.argv:
        juntar()
    elif "--grade" in sys.argv:
        for a in args:
            grade(a)
    else:
        for a in args:
            roda(a, 20 if "--rapido" in sys.argv else 60)
