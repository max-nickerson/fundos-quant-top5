"""
Roda a bateria de robustez dos fundos da frente global_cripto com R$ 20 mil e R$ 50 mil, calcula o resultado depois do IR por classe e
salva pf/resultados/global_cripto.pkl (lista de dicts: nome, excesso_20k, excesso_50k, metricas_20k, metricas_50k, ...).

    python pf/fundos/gl_rodar.py [--rapido] [gl_nome ...]
"""
import importlib
import pickle
import sys
import time
import types
from pathlib import Path

import numpy as np
import pandas as pd

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import gl_comum as G  # noqa: E402

import comum as C  # noqa: E402
import pf as P  # noqa: E402
import robustez as RB  # noqa: E402

FUNDOS = ["gl_rotacao", "gl_hedge_cdi", "gl_bdr_limite", "gl_spinoff", "gl_cripto_premio", "gl_cripto_tendencia", "gl_wsp"]
SAIDA = G.PF / "resultados" / "global_cripto.pkl"


def visao(m, capital):
    v = types.SimpleNamespace(**{k: getattr(m, k) for k in dir(m) if not k.startswith("__")})
    v.excesso = lambda d, **kw: m.excesso(d, **{"capital": capital, **kw})
    v.posicoes = lambda d, **kw: m.posicoes(d, **{"capital": capital, **kw})
    v.negocios = lambda d, **kw: m.negocios(d, **{"capital": capital, **kw})
    return v


def apos_ir(m, d, e, capital):
    """Cota depois do IR: P&L do ativo por classe (m.classes_ir) + caixa (o resto, CDI tributado como renda fixa)."""
    cl = m.classes_ir(d, capital=capital)
    tot = capital * (C.CDI.reindex(G.DIAS).fillna(0) + e.reindex(G.DIAS).fillna(0) - RB.DESPESAS / 252)
    cl = {k: v.reindex(G.DIAS).fillna(0) for k, v in cl.items()}
    cl["renda_fixa"] = tot - sum(cl.values())
    liq = P.apos_ir_por_classe(cl, capital) / capital
    imposto = (tot / capital - liq)
    return liq, imposto


def metricas(m, d, capital, n_leque, log):
    v = visao(m, capital)
    R = RB.bateria(v, d, n_leque=n_leque, log=log)
    oos = lambda x: x[x.index >= pd.Timestamp(m.CORTE)]
    liq, imp = apos_ir(m, d, R["e"], capital)
    liq = liq[liq.index >= pd.Timestamp(m.INICIO)]
    cdil = P.cdi_liquido().reindex(liq.index).fillna(0)
    a = RB.ativo(m, R["r"])
    ng = R["negocios"]
    o = ng[pd.to_datetime(ng["entrada"]) >= pd.Timestamp(m.CORTE)]
    out = {
        "OOS ativo pp (antes IR)": RB.ativo_aa(m, R["r"]),
        "IS ativo pp": RB.ativo_aa(m, R["r"], RB.ins),
        "OOS ativo pp (depois IR, vs CDI líquido)": C.anual(oos(liq)) - C.anual(oos(cdil)),
        "imposto a.a. % do PL (OOS)": oos(imp).sum() / max(len(oos(imp)) / 252, .5) * 100,
        "IR OOS (information ratio)": RB.ir(oos(a)),
        "vol OOS %": oos(R["e"]).std() * np.sqrt(252) * 100,
        "pior queda %": R["metricas"].loc["pior queda %", "fora da amostra"],
        "PBO %": R["resumo_grade"]["PBO %"],
        "% variantes batem OOS": R["resumo_grade"]["% variantes que batem o benchmark OOS"],
        "Sharpe defl. grade %": R["resumo_grade"]["Sharpe deflacionado (grade) %"],
        "P(bater) 1a %": R["mc"].loc["P(bater o benchmark) %", "1 ano(s)"],
        "P(bater) 3a %": R["mc"].loc["P(bater o benchmark) %", "3 ano(s)"],
        "leque p5": R["leque"]["ativo OOS pp"].quantile(.05) if len(R["leque"]) else np.nan,
        "leque mediana": R["leque"]["ativo OOS pp"].median() if len(R["leque"]) else np.nan,
        "leque p95": R["leque"]["ativo OOS pp"].quantile(.95) if len(R["leque"]) else np.nan,
        "custo 2x": R["custo"]["2x"], "custo 0x": R["custo"]["0x"],
        "exec t+2": R["atraso"]["t+2"], "exec t+3": R["atraso"]["t+3"],
        "truncamento passou": bool(R["truncamento"]["passou"].all()),
        "placebo p": R["placebo"]["p-valor (fração de placebos >= real)"],
        "sem 5 melhores": R["sem_maiores"].get("sem os 5 melhores", np.nan),
        "sem 10 melhores": R["sem_maiores"].get("sem os 10 melhores", np.nan),
        "walk-forward pp": R["wf_ativo"],
        "negócios OOS": len(o), "acerto OOS %": (o["contrib_pp"] > 0).mean() * 100 if len(o) else np.nan,
    }
    extras = {"melhores": o.nlargest(10, "contrib_pp"), "piores": o.nsmallest(10, "contrib_pp"),
              "por_ativo_oos": o.groupby("ativo")["contrib_pp"].agg(["sum", "count"]).sort_values("sum", ascending=False),
              "ano": R["ano"], "regime": R["regime"], "grade": R["grade"], "truncamento": R["truncamento"], "custo": R["custo"],
              "atraso": R["atraso"], "mc": R["mc"]}
    return R["e"], out, extras


def roda(nome, n_leque=30, log=print):
    m = importlib.import_module(nome)
    t0 = time.time()
    d = m.carrega()
    res = {"nome": nome, "titulo": m.NOME, "tese": m.TESE, "aplicavel": m.APLICAVEL, "motivo": m.MOTIVO, "inicio": m.INICIO,
           "corte": m.CORTE, "params": m.PARAMS, "regime": m.REGIME}
    for cap in P.CAPITAIS:
        k = f"{cap // 1000}k"
        log(f"== {nome} R$ {cap:,.0f}")
        e, met, ext = metricas(m, d, cap, n_leque, log)
        res[f"excesso_{k}"], res[f"metricas_{k}"], res[f"extras_{k}"] = e, met, ext
        for a in getattr(m, "ALAVANCAGENS", [1]):
            if a == 1:
                continue
            ea = m.excesso(d, capital=cap, alavancagem=a)
            ra = RB.cota(m, ea)
            met[f"alav {a}x OOS pp"] = RB.ativo_aa(m, ra)
            met[f"alav {a}x pior queda %"] = C.metricas(RB.oos(m, ra), C.CDI)["pior queda %"]
        log(pd.Series({a: (round(b, 2) if isinstance(b, (float, np.floating)) else b) for a, b in met.items()}).to_string())
    log(f"   {nome}: {time.time() - t0:.0f}s")
    return res


def junta():
    """Junta as partes (_gc_<nome>.pkl, rodadas em paralelo) em global_cripto.pkl."""
    rs = [pickle.load(open(SAIDA.parent / f"_gc_{f}.pkl", "rb")) for f in FUNDOS if (SAIDA.parent / f"_gc_{f}.pkl").exists()]
    pickle.dump(rs, open(SAIDA, "wb"))
    print("salvo", SAIDA, [r["nome"] for r in rs])


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    n = 12 if "--rapido" in sys.argv else 30
    if "--junta" in sys.argv:
        junta()
        sys.exit()
    if "--parte" in sys.argv:
        for f in args:
            pickle.dump(roda(f, n), open(SAIDA.parent / f"_gc_{f}.pkl", "wb"))
        sys.exit()
    nomes = args or FUNDOS
    antigos = []
    if SAIDA.exists():
        antigos = [r for r in pickle.load(open(SAIDA, "rb")) if r["nome"] not in nomes]
    novos = [roda(f, n) for f in nomes]
    ordem = {f: i for i, f in enumerate(FUNDOS)}
    tudo = sorted(antigos + novos, key=lambda r: ordem.get(r["nome"], 99))
    SAIDA.parent.mkdir(exist_ok=True)
    pickle.dump(tudo, open(SAIDA, "wb"))
    print("salvo", SAIDA, [r["nome"] for r in tudo])
