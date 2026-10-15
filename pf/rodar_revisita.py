"""
Frente "revisita": roda a bateria de robustez de cada fundo PF (pf/fundos/rev_*.py) com R$ 20 mil e R$ 50 mil.

    python pf/rodar_revisita.py rev_carry_moedas [rev_opa ...] [--rapido]   # um ou mais fundos -> pf/resultados/revisita/<nome>.pkl
    python pf/rodar_revisita.py --juntar                                    # junta tudo em pf/resultados/revisita.pkl

Cada pkl por fundo é um dict: nome, NOME, aplicavel, motivo, instrumentos, excesso_20k, excesso_50k (Series diárias antes do IR),
excesso_ir_20k/50k (depois do IR, sobre o CDI líquido), metricas_20k/50k (dict resumo), bateria_20k/50k (resumo da bateria),
alavancagem_20k/50k (DataFrame), negocios_20k (DataFrame), texto (saída impressa).
"""
import importlib.util
import io
import pickle
import sys
import time
import types
from contextlib import redirect_stdout
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parent))
sys.path.insert(0, str(AQUI))
sys.path.insert(0, str(AQUI / "fundos"))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

import comum as C  # noqa: E402
import pf  # noqa: E402
import robustez as RB  # noqa: E402

SAIDA = AQUI / "resultados" / "revisita"
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
    if hasattr(m, "posicoes"):
        v.posicoes = lambda d, **kw: m.posicoes(d, **{"capital": capital, **kw}) if "capital" in m.posicoes.__code__.co_varnames else m.posicoes(d, **kw)
    if hasattr(m, "negocios"):
        v.negocios = lambda d, **kw: m.negocios(d, **{"capital": capital, **kw}) if "capital" in m.negocios.__code__.co_varnames else m.negocios(d, **kw)
    return v


def depois_do_ir(m0, d, capital, e):
    """Excesso diário depois do IR sobre o CDI líquido + checagem de consistência das classes com o excesso antes do IR."""
    cls = {k: v.reindex(C.DIAS).fillna(0) for k, v in m0.classes_ir(d, capital=capital).items()}
    perd = cls.pop("_cdi_perdido", pd.Series(0.0, index=C.DIAS))
    bruto = (sum(cls.values()) - perd) / capital
    e = e.reindex(C.DIAS).fillna(0)
    dif = float((bruto - e).abs().sum() / max(e.abs().sum(), 1e-12))
    liq = (pf.apos_ir_por_classe(cls, capital) - .85 * perd) / capital
    # excesso depois do IR: fundo (CDI líquido + P&L líquido) contra o CDI líquido
    return liq, dif, {k: float(v[v.index >= "2000"].sum()) for k, v in cls.items()}


def resumo(m, m0, d, R, capital, e_ir):
    o = R["metricas"]["fora da amostra"]
    oos = lambda s: s[s.index >= pd.Timestamp(m0.CORTE)]
    r_ir = CDI_LIQ.reindex(e_ir.index).fillna(0) + e_ir - RB.DESPESAS / 252
    ativo_ir = C.anual(oos(r_ir)) - C.anual(oos(CDI_LIQ))
    lq = R["leque"]["ativo OOS pp"] if len(R["leque"]) else pd.Series(dtype=float)
    ng = R["negocios"]
    return {"fundo OOS a.a. %": o["retorno a.a. %"], "CDI OOS a.a. %": o["benchmark a.a. %"], "ativo OOS pp": o["ativo a.a. pp"],
            "ativo OOS depois do IR pp": ativo_ir, "IR (inf. ratio) OOS": o["IR vs bench"], "vol OOS %": o["vol a.a. %"],
            "pior queda OOS %": o["pior queda %"], "ativo IS pp": R["metricas"]["dentro da amostra"]["ativo a.a. pp"],
            "PBO %": R["resumo_grade"]["PBO %"], "% variantes > CDI": R["resumo_grade"]["% variantes que batem o benchmark OOS"],
            "P(bater) 3a %": R["mc"].loc["P(bater o benchmark) %", "3 ano(s)"],
            "leque p5": lq.quantile(.05) if len(lq) else np.nan, "leque mediana": lq.median() if len(lq) else np.nan,
            "leque p95": lq.quantile(.95) if len(lq) else np.nan,
            "custo 2x pp": R["custo"].get("2x", np.nan), "t+2 pp": R["atraso"].get("t+2", np.nan),
            "truncamento passou": bool(R["truncamento"]["passou"].all()), "placebo p": R["placebo"]["p-valor (fração de placebos >= real)"],
            "walk-forward pp": R["wf_ativo"], "negócios": len(ng), "negócios OOS": int((pd.to_datetime(ng["entrada"]) >= pd.Timestamp(m0.CORTE)).sum()) if len(ng) else 0,
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


def roda(nome, n_leque=60):
    m0 = carrega_modulo(nome)
    d = m0.carrega()
    res = {"nome": nome, "NOME": m0.NOME, "aplicavel": m0.APLICAVEL, "motivo": m0.MOTIVO, "instrumentos": m0.INSTRUMENTOS,
           "ranking": getattr(m0, "RANKING", []), "tese": m0.TESE, "corte": m0.CORTE}
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
        res[f"metricas_{k}"] = {**resumo(m, m0, d, R, cap, e_ir), "dif classes x excesso": dif}
        res[f"classes_{k}"] = tot_cls
        res[f"bateria_{k}"] = {kk: R[kk] for kk in ("metricas", "ano", "grade", "resumo_grade", "custo", "atraso", "mc", "truncamento", "placebo",
                                                    "por_ativo", "sem_maiores", "sem_ativo", "regime", "wf_ativo")}
        res[f"leque_{k}"] = R["leque"]
        res[f"negocios_{k}"] = R["negocios"]
        res[f"alavancagem_{k}"] = alavancagens(m0, d, cap)
        # variantes extras que o módulo quiser reportar (ex.: livros diferentes, rotas diferentes) -> ativo OOS antes do IR
        if hasattr(m0, "VARIANTES"):
            vv = {}
            for rot, kw in m0.VARIANTES.items():
                try:
                    vv[rot] = RB.ativo_aa(m0, RB.cota(m0, m0.excesso(d, capital=cap, **kw)))
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
    L = [f"=== {res['NOME']} ({res['nome']}) | aplicável: {res['aplicavel']} | {res['motivo']}", f"instrumentos: {res['instrumentos']}"]
    for k in ("20k", "50k"):
        mt = res[f"metricas_{k}"]
        L.append(f"-- R$ {k}: " + " | ".join(f"{a}: {b:.2f}" if isinstance(b, float) else f"{a}: {b}" for a, b in mt.items()))
        L.append("   alavancagem:\n" + res[f"alavancagem_{k}"].round(2).to_string())
        if f"variantes_{k}" in res:
            L.append("   variantes: " + str({a: (round(b, 2) if isinstance(b, float) else b) for a, b in res[f"variantes_{k}"].items()}))
        L.append("   classes IR (P&L total R$): " + str({a: round(b) for a, b in res[f"classes_{k}"].items()}))
    b = res["bateria_20k"]
    L.append("-- R$ 20k: custo\n" + b["custo"].round(2).to_string() + "\n-- atraso\n" + b["atraso"].round(2).to_string())
    L.append("-- truncamento\n" + b["truncamento"].to_string())
    L.append("-- grade (20k)\n" + b["grade"].round(2).to_string())
    L.append("-- ano a ano (20k)\n" + b["ano"].round(2).to_string())
    ng = res["negocios_20k"]
    if len(ng):
        L.append("-- 10 melhores negócios (20k)\n" + ng.nlargest(10, "contrib_pp").round(3).to_string(index=False)[:3500])
        L.append("-- 10 piores negócios (20k)\n" + ng.nsmallest(10, "contrib_pp").round(3).to_string(index=False)[:3500])
    L.append("-- por ativo (20k)\n" + b["por_ativo"].head(12).round(3).to_string())
    L.append("-- concentração (20k)\n" + b["sem_maiores"].round(2).to_string())
    return "\n".join(L)


def juntar():
    out = [pickle.load(open(p, "rb")) for p in sorted(SAIDA.glob("rev_*.pkl"))]
    pickle.dump(out, open(AQUI / "resultados" / "revisita.pkl", "wb"))
    tab = pd.DataFrame({r["nome"]: {**{f"{a} 20k": b for a, b in r["metricas_20k"].items()},
                                    **{f"{a} 50k": b for a, b in r["metricas_50k"].items()}} for r in out}).T
    print(tab[[c for c in tab.columns if any(s in c for s in ("ativo OOS pp", "depois do IR", "IR (inf", "PBO", "P(bater"))]].round(2).to_string())
    return out


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if "--juntar" in sys.argv:
        juntar()
    else:
        for a in args:
            roda(a, 20 if "--rapido" in sys.argv else 60)
