"""
Roda a bateria de robustez (robustez.bateria) em cada fundo da frente deriv_b3 com capital fixo de R$ 20 mil e R$ 50 mil,
calcula o resultado depois do IR por classe (pf.apos_ir_por_classe, benchmark = CDI depois de 15%) e salva:
  pf/resultados/deriv_b3/<fundo>.pkl  (um por fundo)   e   pf/resultados/deriv_b3.pkl (lista de dicts, todos os fundos)

  python db3_rodar.py                 # todos
  python db3_rodar.py db3_put_selic   # um
  python db3_rodar.py --junta         # só junta os .pkl por fundo
"""
import importlib
import pickle
import sys
import time
import types

import numpy as np
import pandas as pd

import db3_base as B
import comum as C
import pf as P
import robustez as RB

FUNDOS = ["db3_put_selic", "db3_trava_bova", "db3_wdo_carry", "db3_agro_ccm", "db3_win_regime", "db3_cc_isenta", "db3_base_win"]
SAIDA = B.PF / "resultados"
N_LEQUE = 30


def amarra(m, capital):
    """Módulo 'falso' com excesso/posicoes/negocios presos ao capital (a robustez chama m.excesso(d, **params))."""
    ns = types.SimpleNamespace(**{k: getattr(m, k) for k in dir(m) if not k.startswith("__")})
    ns.excesso = lambda d, **kw: m.excesso(d, capital=capital, **kw)
    ns.posicoes = lambda d, **kw: m.posicoes(d, capital=capital, **kw)
    ns.negocios = lambda d, **kw: m.negocios(d, capital=capital, **kw)
    return ns


def apos_ir(m, d, capital):
    """Excesso diário depois do IR, sobre o CDI depois do IR. '_cdi_perdido' = CDI que o dinheiro aplicado fora do CDI deixou de ganhar
    (também pagaria 15%)."""
    cl = dict(m.classes_ir(d, capital=capital))
    perd = cl.pop("_cdi_perdido", pd.Series(0.0, index=B.DIAS)).reindex(B.DIAS).fillna(0)
    liq = P.apos_ir_por_classe(cl, capital)
    return (liq - .85 * perd) / capital


def resumo(m, d, R, capital):
    ini, corte = pd.Timestamp(m.INICIO), pd.Timestamp(m.CORTE)
    e = R["e"][R["e"].index >= ini]
    r = R["r"]
    o = r[r.index >= corte]
    cdi_o = C.CDI.reindex(o.index).fillna(0)
    e_ir = apos_ir(m, d, capital)
    cdl = P.cdi_liquido()
    r_ir = (cdl + e_ir - RB.DESPESAS / 252)[lambda x: x.index >= corte]
    cdl_o = cdl.reindex(r_ir.index)
    a = o - cdi_o
    neg = R["negocios"]
    no = neg[pd.to_datetime(neg["entrada"]) >= corte] if len(neg) else neg
    lq = R["leque"]["ativo OOS pp"] if len(R["leque"]) else pd.Series(dtype=float)
    met = {
        "capital": capital,
        "OOS fundo a.a. %": C.anual(o), "OOS CDI a.a. %": C.anual(cdi_o), "OOS ativo pp": C.anual(o) - C.anual(cdi_o),
        "IS ativo pp": RB.ativo_aa(m, r, RB.ins),
        "OOS fundo após IR a.a. %": C.anual(r_ir), "OOS CDI após IR a.a. %": C.anual(cdl_o), "OOS ativo após IR pp": C.anual(r_ir) - C.anual(cdl_o),
        "IR (info ratio) OOS": RB.ir(a), "vol OOS %": o.std() * np.sqrt(252) * 100,
        "pior queda OOS %": C.metricas(o, C.CDI)["pior queda %"], "pior queda total %": C.metricas(r, C.CDI)["pior queda %"],
        "PBO %": R["resumo_grade"]["PBO %"], "% variantes batem OOS": R["resumo_grade"]["% variantes que batem o benchmark OOS"],
        "Sharpe defl. grade %": R["resumo_grade"]["Sharpe deflacionado (grade) %"],
        "P(bater) 1a %": R["mc"].loc["P(bater o benchmark) %", "1 ano(s)"], "P(bater) 3a %": R["mc"].loc["P(bater o benchmark) %", "3 ano(s)"],
        "leque p5": lq.quantile(.05) if len(lq) else np.nan, "leque mediana": lq.median() if len(lq) else np.nan,
        "leque p95": lq.quantile(.95) if len(lq) else np.nan,
        "custo 2x pp": R["custo"].get("2x"), "custo 0x pp": R["custo"].get("0x"), "t+2 pp": R["atraso"].get("t+2"), "t+3 pp": R["atraso"].get("t+3"),
        "truncamento passou": bool(R["truncamento"]["passou"].all()), "placebo p": R["placebo"]["p-valor (fração de placebos >= real)"],
        "walk-forward pp": R["wf_ativo"], "negócios OOS": len(no),
        "acerto OOS %": (no["contrib_pp"] > 0).mean() * 100 if len(no) else np.nan,
        "dias com posição OOS %": (e[e.index >= corte] != 0).mean() * 100,
    }
    return met, e_ir


def roda(nome, capitais=P.CAPITAIS, n_leque=N_LEQUE):
    m = importlib.import_module(nome)
    t0 = time.time()
    d = m.carrega()
    print(f"== {nome}: {m.NOME} (dados {time.time() - t0:.0f}s)", flush=True)
    out = {"nome": nome, "titulo": m.NOME, "tese": m.TESE, "aplicavel": m.APLICAVEL, "motivo": m.MOTIVO, "instrumentos": m.INSTRUMENTOS,
           "alavancagens": m.ALAVANCAGENS, "motivo_alav": m.MOTIVO_ALAV, "params": m.PARAMS, "corte": m.CORTE, "inicio": m.INICIO}
    for cap in capitais:
        mm = amarra(m, cap)
        R = RB.bateria(mm, d, n_leque=n_leque, log=lambda s: print("  ", cap, s, flush=True))
        met, e_ir = resumo(mm, d, R, cap)
        k = f"{cap // 1000}k"
        out[f"excesso {k}"] = R["e"]
        out[f"excesso após IR {k}"] = e_ir
        out[f"metricas {k}"] = met
        out[f"grade {k}"] = R["grade"]
        out[f"custo {k}"], out[f"atraso {k}"] = R["custo"], R["atraso"]
        out[f"negocios {k}"] = R["negocios"]
        out[f"por_ativo {k}"] = R["por_ativo"]
        out[f"sem_maiores {k}"] = R["sem_maiores"]
        out[f"ano {k}"] = R["ano"]
        out[f"truncamento {k}"] = R["truncamento"]
        out[f"regime {k}"] = R["regime"]
        out[f"mc {k}"] = R["mc"]
        out[f"leque {k}"] = R["leque"]
        out[f"placebo {k}"] = R["placebo"]
        print(pd.Series({k: round(v, 2) if isinstance(v, (float, np.floating)) else v for k, v in met.items()}).to_string(), flush=True)
    (SAIDA / "deriv_b3").mkdir(parents=True, exist_ok=True)
    with open(SAIDA / "deriv_b3" / f"{nome}.pkl", "wb") as f:
        pickle.dump(out, f)
    B.limpa_cache()
    return out


def junta():
    res = []
    for n in FUNDOS:
        p = SAIDA / "deriv_b3" / f"{n}.pkl"
        if p.exists():
            with open(p, "rb") as f:
                res.append(pickle.load(f))
    with open(SAIDA / "deriv_b3.pkl", "wb") as f:
        pickle.dump(res, f)
    linhas = []
    for x in res:
        for k in ("20k", "50k"):
            mt = x.get(f"metricas {k}")
            if mt:
                linhas.append({"fundo": x["nome"], "capital": k, **{c: mt[c] for c in (
                    "OOS fundo a.a. %", "OOS CDI a.a. %", "OOS ativo pp", "OOS fundo após IR a.a. %", "OOS CDI após IR a.a. %",
                    "OOS ativo após IR pp", "IR (info ratio) OOS", "PBO %", "P(bater) 3a %", "custo 2x pp", "t+2 pp", "truncamento passou",
                    "pior queda OOS %", "IS ativo pp")}})
    t = pd.DataFrame(linhas)
    print(t.round(2).to_string())
    return res


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if "--junta" not in sys.argv:
        for n in args or FUNDOS:
            roda(n)
    junta()
