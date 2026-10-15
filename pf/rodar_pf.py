"""
Rodada PF (R$ 20–50 mil, todas as contas como um fundo, caixa em CDI).

    python pf/rodar_pf.py lista                 # lista os fundos encontrados em pf/fundos/
    python pf/rodar_pf.py um <arquivo>          # bateria completa de um fundo -> pf/resultados/bateria/<arquivo>.pkl
    python pf/rodar_pf.py todos [n_proc]        # todos os fundos em paralelo
    python pf/rodar_pf.py ranking               # junta as baterias, ranqueia, salva pf/resultados/ranking_pf.csv
    python pf/rodar_pf.py top5 [a b c d e]      # dossiê dos 5 (painéis) + carteira de R$ 20 mil e R$ 50 mil, com alavancagem
"""
import importlib.util
import pickle
import subprocess
import sys
import time
import types
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
sys.path.insert(0, str(AQUI / "fundos"))                 # módulos auxiliares das frentes (b3_base, db3_base, ...)
sys.path.insert(0, str(AQUI.parent))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

import comum as C  # noqa: E402
import graficos as G  # noqa: E402
import pf  # noqa: E402
import robustez as RB  # noqa: E402

FUNDOS_DIR, RES = AQUI / "fundos", AQUI / "resultados"
BAT = RES / "bateria"
pd.set_option("display.width", 250)


def carrega_modulo(arquivo):
    nome = Path(arquivo).stem
    spec = importlib.util.spec_from_file_location(nome, FUNDOS_DIR / f"{nome}.py")
    m = importlib.util.module_from_spec(spec)
    sys.modules[nome] = m
    spec.loader.exec_module(m)
    return m


def lista():
    out = []
    for p in sorted(FUNDOS_DIR.glob("*.py")):
        if p.stem.startswith("_") or any(x in p.stem for x in ("rodar", "_base", "_comum", "_util")):
            continue
        txt = p.read_text(encoding="utf-8", errors="ignore")
        if "excesso" in txt and "\nNOME" in txt and "\nPARAMS" in txt:
            out.append(p.stem)
    return out


def com_capital(m, capital):
    v = types.SimpleNamespace(**{k: getattr(m, k) for k in dir(m) if not k.startswith("__")})
    v.excesso = lambda d, **kw: m.excesso(d, **{"capital": capital, **kw})
    if hasattr(m, "posicoes"):
        v.posicoes = lambda d, **kw: m.posicoes(d, **{**({"capital": capital} if "capital" in m.posicoes.__code__.co_varnames else {}), **kw})
    if hasattr(m, "negocios"):
        v.negocios = lambda d, **kw: m.negocios(d, **{**({"capital": capital} if "capital" in m.negocios.__code__.co_varnames else {}), **kw})
    return v


def aliquota(m):
    """Alíquota sobre o ganho além do CDI, pela CLASSE_IR declarada no fundo (padrão 15%). Isentos: 0%."""
    return {"isento": 0.0, "acoes_isentas": 0.0, "day_trade": .20}.get(getattr(m, "CLASSE_IR", "exterior"), .15)


def apos_ir(m, d, capital, r):
    """Regra única e conservadora (as funções classes_ir das frentes usam unidades diferentes):
    cota depois do IR = CDI depois de 15% + excesso sobre o CDI depois da alíquota da classe (anual, com compensação de prejuízo)."""
    cdi_l = pf.cdi_liquido().reindex(r.index).fillna(0)
    ex = (r - C.CDI.reindex(r.index).fillna(0))
    pnl = pf.apos_ir_por_classe({"x": ex * capital}, capital, {"x": aliquota(m)})
    return cdi_l + pnl.reindex(r.index).fillna(0) / capital


def _apos_ir_antigo(m, d, capital, r):
    """Cota depois do IR: usa classes_ir() do fundo se existir; senão CLASSE_IR (padrão 'exterior'/15%) sobre o ganho do fundo além do CDI;
    o CDI do caixa paga 15% como no benchmark."""
    cdi_l = pf.cdi_liquido().reindex(r.index).fillna(0)
    if hasattr(m, "classes_ir"):
        try:
            cls = m.classes_ir(d, capital=capital)
            pnl = pf.apos_ir_por_classe(cls, capital)
            return cdi_l + pnl.reindex(r.index).fillna(0) / capital
        except Exception as ex:
            print("   classes_ir falhou:", ex)
    al = {"isento": 0, "acoes_isentas": 0}.get(getattr(m, "CLASSE_IR", "exterior"), .15)
    ex = (r - C.CDI.reindex(r.index).fillna(0))
    pnl = pf.apos_ir_por_classe({"x": ex * capital}, capital, {"x": al})
    return cdi_l + pnl.reindex(r.index).fillna(0) / capital


def bateria_um(nome, n_leque=30):
    t0 = time.time()
    m0 = carrega_modulo(nome)
    d = m0.carrega()
    out = {"nome": nome, "NOME": m0.NOME, "TESE": getattr(m0, "TESE", ""), "APLICAVEL": getattr(m0, "APLICAVEL", True),
           "MOTIVO": getattr(m0, "MOTIVO", ""), "INSTRUMENTOS": getattr(m0, "INSTRUMENTOS", ""), "CORTE": m0.CORTE, "INICIO": m0.INICIO,
           "BENCHMARK": m0.BENCHMARK, "PARAMS": m0.PARAMS, "REGIME": getattr(m0, "REGIME", "nenhum")}
    for cap in pf.CAPITAIS:
        m = com_capital(m0, cap)
        if cap == 20_000:
            R = RB.bateria(m, d, n_leque, log=lambda *a: None)
            out["R20"] = {k: v for k, v in R.items() if k not in ("curvas_leque", "curvas_grade")}
            out["curvas_leque"] = pd.DataFrame(R["curvas_leque"])
            out["curvas_grade"] = pd.DataFrame(R["curvas_grade"])
            r = R["r"]
        else:
            r = RB.cota(m, m.excesso(d))
        ri = apos_ir(m0, d, cap, r)
        o = RB.oos(m, r)
        out[f"r{cap // 1000}"] = r
        out[f"ri{cap // 1000}"] = ri
        out[f"ativo{cap // 1000}"] = RB.ativo_aa(m, r)
        oi, ci = RB.oos(m, ri), RB.oos(m, pf.cdi_liquido().reindex(r.index).fillna(0))
        out[f"ativo_ir{cap // 1000}"] = C.anual(oi) - C.anual(ci)
        out[f"ir_oos{cap // 1000}"] = RB.ir(RB.oos(m, RB.ativo(m, r)))
    alav = {}
    for L in getattr(m0, "ALAVANCAGENS", [1]):
        for cap in pf.CAPITAIS:
            try:
                r = RB.cota(m0, m0.excesso(d, capital=cap, alavancagem=L))
                eq = (1 + r).cumprod()
                alav[(f"{L}x", cap)] = {"ativo OOS pp": RB.ativo_aa(m0, r), "vol OOS %": C.metricas(RB.oos(m0, r), C.CDI)["vol a.a. %"],
                                        "pior queda %": C.metricas(r, C.CDI)["pior queda %"], "quebrou": bool((eq < .05).any())}
            except Exception as ex:
                alav[(f"{L}x", cap)] = {"erro": str(ex)[:80]}
    out["alav"] = pd.DataFrame(alav).T
    out["seg"] = time.time() - t0
    BAT.mkdir(parents=True, exist_ok=True)
    pickle.dump(out, open(BAT / f"{nome}.pkl", "wb"))
    o = out["R20"]["metricas"]["fora da amostra"]
    print(f"{nome}: OOS {o['retorno a.a. %']:.1f}% vs CDI {o['benchmark a.a. %']:.1f}% | ativo 20k {out['ativo20']:+.2f} / 50k {out['ativo50']:+.2f} pp"
          f" | depois do IR 20k {out['ativo_ir20']:+.2f} | IR {out['ir_oos20']:.2f} | PBO {out['R20']['resumo_grade']['PBO %']:.0f}% | {out['seg']:.0f}s", flush=True)
    return out


def ranking():
    L = []
    for p in sorted(BAT.glob("*.pkl")):
        o = pickle.load(open(p, "rb"))
        txt = (FUNDOS_DIR / f"{o['nome']}.py").read_text(encoding="utf-8", errors="ignore")
        cls = next((l.split("=")[1].strip().strip("\"'") for l in txt.splitlines() if l.startswith("CLASSE_IR")), "exterior")
        mm = types.SimpleNamespace(CLASSE_IR=cls, CORTE=o["CORTE"], BENCHMARK="CDI")
        for cap in pf.CAPITAIS:
            r = o[f"r{cap // 1000}"]
            ri = apos_ir(mm, None, cap, r)
            o[f"ativo_ir{cap // 1000}"] = C.anual(RB.oos(mm, ri)) - C.anual(RB.oos(mm, pf.cdi_liquido().reindex(r.index).fillna(0)))
        R = o["R20"]
        rg, mc, lq = R["resumo_grade"], R["mc"], R["leque"]["ativo OOS pp"]
        dsr = next((v for k, v in rg.items() if k.startswith("Sharpe deflacionado (1")), np.nan)
        L.append({"arquivo": o["nome"], "fundo": o["NOME"], "aplicável": o["APLICAVEL"], "OOS desde": o["CORTE"][:7],
                  "ativo 20k pp": o["ativo20"], "ativo 50k pp": o["ativo50"], "depois do IR 20k pp": o["ativo_ir20"], "depois do IR 50k pp": o["ativo_ir50"],
                  "IR OOS": o["ir_oos20"], "PBO %": rg["PBO %"], "Sharpe defl. %": dsr, "P(bater 3a) %": mc.loc["P(bater o benchmark) %", "3 ano(s)"],
                  "leque p5": lq.quantile(.05), "leque P(>0) %": (lq > 0).mean() * 100, "custo 2x": R["custo"].get("2x"), "exec t+2": R["atraso"].get("t+2"),
                  "walk-forward": R["wf_ativo"], "sem 10 melhores": R["sem_maiores"].get("sem os 10 melhores"),
                  "placebo p": R["placebo"]["p-valor (fração de placebos >= real)"], "truncamento ok": bool(R["truncamento"]["passou"].all())})
    t = pd.DataFrame(L)
    t["aplicável"] = t["aplicável"].map(lambda v: v if isinstance(v, (bool, np.bool_)) else not str(v).strip().lower().startswith(("false", "nao", "não", "no")))
    ok = (t["aplicável"].astype(bool) & t["truncamento ok"].astype(bool)).astype(float)
    pos = (t["depois do IR 20k pp"] > 0).astype(float)
    rob = ((t["custo 2x"] > 0).astype(float) + (t["exec t+2"] > 0).astype(float) + (t["sem 10 melhores"] > 0).astype(float)) / 3
    t["nota"] = ok * (.20 * t["IR OOS"].fillna(-9).rank(pct=True) + .20 * t["P(bater 3a) %"].fillna(0) / 100 + .15 * t["leque P(>0) %"].fillna(0) / 100
                      + pos * (.15 * (1 - t["PBO %"].fillna(50) / 100) + .15 * rob + .15 * t["Sharpe defl. %"].fillna(0) / 100)) * 100
    t = t.sort_values("nota", ascending=False).reset_index(drop=True)
    t.index += 1
    t.to_csv(RES / "ranking_pf.csv", encoding="utf-8-sig")
    print(t.drop(columns=["arquivo"]).round(2).to_string())
    return t


def top5(nomes):
    res = {n: pickle.load(open(BAT / f"{n}.pkl", "rb")) for n in nomes}
    mods = {n: carrega_modulo(n) for n in nomes}
    dados = {n: mods[n].carrega() for n in nomes}
    for k, n in enumerate(nomes, 1):
        R = dict(res[n]["R20"])
        R["curvas_leque"] = {c: s for c, s in res[n]["curvas_leque"].items()}
        R["curvas_grade"] = {c: s for c, s in res[n]["curvas_grade"].items()}
        G.painel(com_capital(mods[n], 20_000), R, RES / f"top{k}_{n}.png")
    saida = {}
    for cap in pf.CAPITAIS:
        E0 = pd.DataFrame({n: res[n][f"r{cap // 1000}"] - C.CDI.reindex(res[n][f"r{cap // 1000}"].index) for n in nomes})
        cortes = {n: pd.Timestamp(res[n]["CORTE"]) for n in nomes}
        vol = pd.Series({n: E0[n][(E0.index < cortes[n]) & E0[n].notna()].std() for n in nomes})
        w = (1 / vol) / (1 / vol).sum()
        for L in (1, 1.5, 2, 5):
            fat = {}
            for n in nomes:
                m = mods[n]
                Ln = max([x for x in getattr(m, "ALAVANCAGENS", [1]) if x <= L] or [1])
                fat[n] = RB.cota(m, m.excesso(dados[n], capital=cap * w[n], alavancagem=Ln))
            E = pd.DataFrame({n: s - C.CDI.reindex(s.index) for n, s in fat.items()}).fillna(0)
            r = C.CDI.reindex(E.index) + E @ w
            corte = max(cortes.values())
            mm = types.SimpleNamespace(BENCHMARK="CDI", CORTE=str(corte.date()), INICIO=str(E.index[0].date()))
            ri = pf.cdi_liquido().reindex(r.index).fillna(0) + sum(
                (apos_ir(mods[n], dados[n], cap * w[n], fat[n]) - pf.cdi_liquido().reindex(fat[n].index).fillna(0)).reindex(r.index).fillna(0) * w[n] for n in nomes)
            o = C.metricas(RB.oos(mm, r), C.CDI)
            ci = RB.oos(mm, pf.cdi_liquido().reindex(r.index).fillna(0))
            saida[(cap, L)] = {"reais por fundo": {n: round(cap * w[n]) for n in nomes}, "OOS a.a. %": o["retorno a.a. %"], "CDI %": o["benchmark a.a. %"],
                               "ativo OOS pp": o["ativo a.a. pp"], "depois do IR pp": C.anual(RB.oos(mm, ri)) - C.anual(ci), "Sharpe": o["Sharpe"],
                               "vol %": o["vol a.a. %"], "pior queda total %": C.metricas(r, C.CDI)["pior queda %"], "quebrou": bool(((1 + r).cumprod() < .05).any())}
            if L == 1:
                mc, cam = RB.monte_carlo(mm, r)
                rng = np.random.default_rng(0)
                leque = {i: C.CDI.reindex(E.index) + E @ pd.Series(rng.dirichlet(w.values * 20), index=w.index) for i in range(200)}
                sem = {f"sem {res[n]['NOME']}": RB.ativo_aa(mm, C.CDI.reindex(E.index) + E.drop(columns=n) @ (w.drop(n) / w.drop(n).sum())) for n in nomes}
                ano = r.groupby(r.index.year).apply(lambda x: ((1 + x).prod() - (1 + C.CDI.reindex(x.index)).prod()) * 100)
                corr = E[E.index >= corte].corr()
                corr.columns = corr.index = [res[n]["NOME"][:30] for n in corr.columns]
                tab = pd.DataFrame({"total": C.metricas(r, C.CDI), "fora da amostra": o})
                Rc = {"r": r, "metricas": tab.assign(**{"dentro da amostra": tab["total"]}), "leque_pesos": leque, "corr": corr, "mc": mc, "mc_caminhos": cam,
                      "ano": ano, "corte": corte, "sem_fundo": pd.Series(sem), "fundos": {res[n]["NOME"]: fat[n] for n in nomes}}
                G.carteira(Rc, RES / f"carteira_{cap // 1000}k.png")
                mc.to_csv(RES / f"carteira_{cap // 1000}k_monte_carlo.csv")
                pd.Series(sem).to_csv(RES / f"carteira_{cap // 1000}k_sem_cada_fundo.csv")
    tab = pd.DataFrame(saida).T
    tab.index.names = ["capital", "alavancagem"]
    tab.to_csv(RES / "carteira_pf.csv", encoding="utf-8-sig")
    print(tab.to_string())


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "lista"
    if cmd == "lista":
        print("\n".join(lista()))
    elif cmd == "um":
        bateria_um(sys.argv[2])
    elif cmd == "todos":
        n = int(sys.argv[2]) if len(sys.argv) > 2 and sys.argv[2].isdigit() else 4
        feitos = {p.stem for p in BAT.glob("*.pkl")} if "--faltantes" in sys.argv else set()
        fila, rodando = [f for f in lista() if f not in feitos], []
        while fila or rodando:
            while fila and len(rodando) < n:
                f = fila.pop(0)
                rodando.append((f, subprocess.Popen([sys.executable, "-W", "ignore", __file__, "um", f])))
            time.sleep(5)
            rodando = [(f, p) for f, p in rodando if p.poll() is None]
    elif cmd == "ranking":
        ranking()
    elif cmd == "top5":
        top5(sys.argv[2:] or list(ranking()["arquivo"][:5]))
