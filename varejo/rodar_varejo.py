"""
Versão pessoa física com R$ 20 mil: roda os 5 fundos de varejo e a carteira, com a mesma bateria de robustez do institucional, mais:
  - sensibilidade ao tamanho do capital (R$ 5 mil a R$ 1 milhão),
  - resultado depois do IR (15%) contra o CDI de varejo também depois do IR,
  - carteira de R$ 20 mil SEM alavancagem extra, cada fundo rodando com a SUA fatia do capital (lotes e custos mínimos pesam mais).

    python varejo/rodar_varejo.py [--rapido] [nome_do_fundo]
"""
import importlib
import importlib.util
import json
import sys
import types
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
sys.path.insert(0, str(AQUI.parent))          # comum, robustez, graficos e fundos/ institucionais

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

import comum as C  # noqa: E402
import graficos as G  # noqa: E402
import robustez as RB  # noqa: E402
import varejo as V  # noqa: E402

FUNDOS = ["variancia_varejo", "carry_moedas_varejo", "mineradoras_varejo", "rebal_ibovespa_varejo", "eurobonds_varejo"]
SAIDA = AQUI / "resultados"
CAPITAIS = [5_000, 10_000, 20_000, 50_000, 100_000, 1_000_000]
pd.set_option("display.width", 200)


def fmt(x):
    return x.round(2).to_string() if hasattr(x, "round") else str(x)


def com_capital(m, capital):
    """Visão do módulo com outro capital padrão (para a bateria de robustez rodar com a fatia certa)."""
    v = types.SimpleNamespace(**{k: getattr(m, k) for k in dir(m) if not k.startswith("__")})
    v.excesso = lambda d, **kw: m.excesso(d, **{"capital": capital, **kw})
    return v


def sensibilidade_capital(m, d):
    out = {}
    for c in CAPITAIS:
        try:
            r = RB.cota(m, m.excesso(d, capital=c))
            out[f"R$ {c:,.0f}".replace(",", ".")] = RB.ativo_aa(m, r)
        except Exception as ex:
            out[f"R$ {c:,.0f}"] = np.nan
            print("   capital", c, ex)
    return pd.Series(out, name="ativo OOS pp (antes do IR)")


def alavancagens(m, d, capital=V.CAPITAL):
    """Para cada alavancagem viável: ativo OOS, vol, pior queda, se quebrou. Se o módulo tiver relatorio_alavancagem(), usa os
    detalhes dele (chamadas de margem, alavancagem efetiva)."""
    out = {}
    for L in getattr(m, "ALAVANCAGENS", [1]):
        r = RB.cota(m, m.excesso(d, capital=capital, alavancagem=L))
        o = C.metricas(RB.oos(m, r), C.CDI)
        t = C.metricas(r, C.CDI)
        eq = (1 + r).cumprod()
        linha = {"ativo OOS pp": RB.ativo_aa(m, r), "ativo total pp": t["ativo a.a. pp"], "vol OOS %": o["vol a.a. %"],
                 "pior queda total %": t["pior queda %"], "quebrou": bool((eq < .05).any())}
        if hasattr(m, "relatorio_alavancagem"):
            try:
                linha.update(m.relatorio_alavancagem(d, alavancagem=L, capital=capital))
            except Exception as ex:
                print("   relatorio_alavancagem", L, ex)
        out[f"{L}x"] = linha
    return pd.DataFrame(out).T


def depois_do_ir(m, r):
    """Fundo e CDI de varejo, ambos com IR de 15%."""
    rl = V.apos_ir(r)
    cl = V.cdi_liquido().reindex(r.index).fillna(0)
    o = RB.oos(m, rl)
    return {"fundo líquido de IR a.a. %": C.anual(o), "CDI líquido de IR a.a. %": C.anual(cl.reindex(o.index)),
            "ativo líquido de IR pp": C.anual(o) - C.anual(cl.reindex(o.index))}, rl


def carrega_modulo(nome):
    """Fundos de varejo ficam em varejo/fundos/ (carregados pelo caminho para não confundir com fundos/ institucional)."""
    spec = importlib.util.spec_from_file_location(nome, AQUI / "fundos" / f"{nome}.py")
    m = importlib.util.module_from_spec(spec)
    sys.modules[nome] = m
    spec.loader.exec_module(m)
    return m


def roda_fundo(nome, n_leque, capital=V.CAPITAL):
    m0 = carrega_modulo(nome)
    print(f"\n{'=' * 100}\n>>> {m0.NOME} (R$ {capital:,.0f})\n{'aplicável' if m0.APLICAVEL else 'NÃO aplicável'}: {m0.MOTIVO}\n"
          f"instrumentos: {m0.INSTRUMENTOS}")
    d = m0.carrega()
    m = com_capital(m0, capital)
    R = RB.bateria(m, d, n_leque)
    R["capital"] = sensibilidade_capital(m0, d)
    R["ir"], R["r_ir"] = depois_do_ir(m, R["r"])
    R["alav"] = alavancagens(m0, d, capital)
    o = R["metricas"]["fora da amostra"]
    print(fmt(R["metricas"]))
    print("\n-- robustez: " + ", ".join(f"{k}: {v:.1f}" for k, v in R["resumo_grade"].items()))
    lq = R["leque"]["ativo OOS pp"]
    print(f"-- leque: p5 {lq.quantile(.05):+.1f} | mediana {lq.median():+.1f} | p95 {lq.quantile(.95):+.1f} | P(>0) {(lq > 0).mean() * 100:.0f}%")
    print("-- custo\n" + fmt(R["custo"]) + "\n-- atraso\n" + fmt(R["atraso"]) + "\n-- Monte Carlo\n" + fmt(R["mc"]))
    print("-- look-ahead (truncamento)\n" + R["truncamento"].to_string() + "\n-- placebo " + str({k: round(v, 3) for k, v in R["placebo"].items()}))
    ng = R["negocios"]
    print("-- melhores negócios\n" + ng.nlargest(8, "contrib_pp").round(2).to_string(index=False)[:2500])
    print("-- piores negócios\n" + ng.nsmallest(8, "contrib_pp").round(2).to_string(index=False)[:2500])
    print("-- quem trouxe o retorno\n" + fmt(R["por_ativo"].head(10)) + "\n-- concentração\n" + fmt(R["sem_maiores"]))
    print("-- regime\n" + fmt(R["regime"]) + f"\n-- walk-forward: {R['wf_ativo']:+.2f} pp")
    print("-- tamanho do capital (ativo OOS antes do IR, pp)\n" + fmt(R["capital"]))
    print(f"-- alavancagem ({getattr(m0, 'MOTIVO_ALAV', '')})\n" + R["alav"].to_string())
    print("-- depois do IR (15% nos dois lados)\n" + "\n".join(f"   {k}: {v:.2f}" for k, v in R["ir"].items()))
    p = SAIDA / nome
    p.mkdir(parents=True, exist_ok=True)
    R["metricas"].round(4).to_csv(p / "metricas.csv")
    R["ano"].round(4).to_csv(p / "ativo_por_ano.csv")
    R["grade"].round(4).to_csv(p / "grade_variantes.csv")
    R["leque"].round(4).to_csv(p / "leque_parametros.csv", index=False)
    pd.concat([R["custo"], R["atraso"]]).round(4).to_csv(p / "custo_e_atraso.csv")
    R["mc"].round(4).to_csv(p / "monte_carlo.csv")
    R["truncamento"].to_csv(p / "teste_lookahead_truncamento.csv")
    ng.sort_values("contrib_pp", ascending=False).to_csv(p / "negocios.csv", index=False)
    R["por_ativo"].round(4).to_csv(p / "contribuicao_por_ativo.csv")
    pd.concat([R["sem_maiores"], R["sem_ativo"]]).round(4).to_csv(p / "concentracao.csv")
    R["regime"].round(4).to_csv(p / "regime_ligado_desligado.csv")
    R["capital"].round(4).to_csv(p / "sensibilidade_capital.csv")
    R["alav"].to_csv(p / "alavancagem.csv")
    json.dump({**{k: float(v) for k, v in R["resumo_grade"].items()}, **R["placebo"], **R["ir"], "walk-forward ativo OOS pp": float(R["wf_ativo"]),
               "aplicavel": bool(m0.APLICAVEL), "motivo": m0.MOTIVO, "instrumentos": m0.INSTRUMENTOS},
              open(p / "resumo.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    pd.DataFrame({"fundo": R["r"], "fundo_apos_ir": R["r_ir"]}).to_csv(p / "cota_diaria.csv")
    G.painel(m, R, SAIDA / f"{nome}.png")
    return m0, d, R


def carteira(res, L=1):
    """R$ 20 mil divididos pelo inverso da vol do IS de cada fundo aplicável; cada fundo roda com a SUA fatia e com a alavancagem L
    (ou a maior viável abaixo de L para aquele fundo)."""
    ok = {k: v for k, v in res.items() if v[0].APLICAVEL}
    E0 = pd.DataFrame({k: R["r"] - C.CDI.reindex(R["r"].index) for k, (m, d, R) in ok.items()})
    cortes = {k: pd.Timestamp(m.CORTE) for k, (m, d, R) in ok.items()}
    vol = pd.Series({k: E0[k][(E0.index < cortes[k]) & E0[k].notna()].std() for k in E0})
    w = (1 / vol) / (1 / vol).sum()
    Lf = {k: max([x for x in getattr(m, "ALAVANCAGENS", [1]) if x <= L] or [1]) for k, (m, d, R) in ok.items()}
    fatias = {k: RB.cota(com_capital(m, V.CAPITAL * w[k]), m.excesso(d, capital=V.CAPITAL * w[k], alavancagem=Lf[k])) for k, (m, d, R) in ok.items()}
    E = pd.DataFrame({k: s - C.CDI.reindex(s.index) for k, s in fatias.items()}).fillna(0)
    r = C.CDI.reindex(E.index) + E @ w
    corte = max(cortes.values())
    mm = types.SimpleNamespace(BENCHMARK="CDI", CORTE=str(corte.date()), INICIO=str(E.index[0].date()))
    tab = pd.DataFrame({"total": C.metricas(r, C.CDI), "fora da amostra": C.metricas(RB.oos(mm, r), C.CDI)})
    rng = np.random.default_rng(0)
    leque = {i: C.CDI.reindex(E.index) + E @ pd.Series(rng.dirichlet(w.values * 20), index=w.index) for i in range(200)}
    sem = {f"sem {ok[k][0].NOME}": RB.ativo_aa(mm, C.CDI.reindex(E.index) + E.drop(columns=k) @ (w.drop(k) / w.drop(k).sum())) for k in w.index}
    mc, cam = RB.monte_carlo(mm, r)
    ir, r_ir = depois_do_ir(mm, r)
    ano = r.groupby(r.index.year).apply(lambda x: ((1 + x).prod() - (1 + C.CDI.reindex(x.index)).prod()) * 100)
    corr = E[E.index >= corte].corr()
    corr.columns = corr.index = [ok[k][0].NOME for k in corr.columns]
    return {"L": Lf, "r": r, "r_ir": r_ir, "pesos": w, "reais": (w * V.CAPITAL).round(0), "metricas": tab, "leque_pesos": leque, "sem_fundo": pd.Series(sem),
            "mc": mc, "mc_caminhos": cam, "ir": ir, "ano": ano, "corr": corr, "corte": corte,
            "fundos": {ok[k][0].NOME: fatias[k] for k in ok}}


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    n = 20 if "--rapido" in sys.argv else 60
    res = {nome: roda_fundo(nome, n) for nome in (args or FUNDOS)}
    if not args:
        tab_L = {}
        for L in (1.5, 2, 5):
            RcL = carteira(res, L)
            o = RcL["metricas"]["fora da amostra"]
            eq = (1 + RcL["r"]).cumprod()
            tab_L[f"{L}x"] = {"alavancagem por fundo": str(RcL["L"]), "OOS a.a. %": o["retorno a.a. %"], "ativo OOS pp": o["ativo a.a. pp"],
                              "vol %": o["vol a.a. %"], "pior queda total %": RcL["metricas"].loc["pior queda %", "total"],
                              "ativo líquido de IR pp": RcL["ir"]["ativo líquido de IR pp"], "quebrou": bool((eq < .05).any())}
        tab_L = pd.DataFrame(tab_L).T
        print("-- carteira com alavancagem")
        print(tab_L.to_string())
        Rc = carteira(res)
        print(f"\n{'=' * 100}\nCARTEIRA DE R$ 20 MIL (sem alavancagem extra)\nR$ por fundo:\n" + fmt(Rc["reais"]))
        print(fmt(Rc["metricas"]) + "\n-- depois do IR\n" + "\n".join(f"   {k}: {v:.2f}" for k, v in Rc["ir"].items()))
        print("-- sem cada fundo\n" + fmt(Rc["sem_fundo"]) + "\n-- Monte Carlo\n" + fmt(Rc["mc"]) + "\n-- correlação OOS\n" + fmt(Rc["corr"]))
        p = SAIDA / "carteira"
        p.mkdir(parents=True, exist_ok=True)
        Rc["metricas"].round(4).to_csv(p / "metricas.csv")
        tab_L.to_csv(p / "alavancagem.csv")
        Rc["reais"].to_csv(p / "reais_por_fundo.csv")
        Rc["mc"].round(4).to_csv(p / "monte_carlo.csv")
        Rc["sem_fundo"].round(4).to_csv(p / "sem_cada_fundo.csv")
        json.dump(Rc["ir"], open(p / "depois_do_ir.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        pd.DataFrame({"carteira": Rc["r"], "carteira_apos_ir": Rc["r_ir"]}).to_csv(p / "cota_diaria.csv")
        Rc["metricas"] = Rc["metricas"].assign(**{"dentro da amostra": Rc["metricas"]["total"]})
        G.carteira(Rc, SAIDA / "carteira.png")
    print("\nArquivos em", SAIDA)
