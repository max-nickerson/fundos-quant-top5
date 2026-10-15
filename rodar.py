"""
Roda os 5 fundos e a carteira combinada, imprime os resultados e salva tudo em resultados/.

    python rodar.py                 # tudo (leva alguns minutos)
    python rodar.py --rapido        # leque com 20 sorteios em vez de 60
    python rodar.py carry_moedas    # só um fundo (sem a carteira)
"""
import importlib
import json
import sys
import types
from pathlib import Path

import numpy as np
import pandas as pd

import comum as C
import graficos as G
import robustez as RB

FUNDOS = ["variancia", "carry_moedas", "mineradoras", "rebal_ibovespa", "eurobonds"]
SAIDA = Path(__file__).resolve().parent / "resultados"
pd.set_option("display.width", 200)
pd.set_option("display.max_columns", 20)


def fmt(x):
    return x.round(2).to_string() if hasattr(x, "round") else str(x)


def salva(nome, R):
    p = SAIDA / nome
    p.mkdir(parents=True, exist_ok=True)
    R["metricas"].round(4).to_csv(p / "metricas.csv")
    R["ano"].round(4).to_csv(p / "ativo_por_ano.csv")
    R["grade"].round(4).to_csv(p / "grade_variantes.csv")
    R["leque"].round(4).to_csv(p / "leque_parametros.csv", index=False)
    pd.concat([R["custo"], R["atraso"]]).round(4).to_csv(p / "custo_e_atraso.csv")
    R["mc"].round(4).to_csv(p / "monte_carlo.csv")
    R["truncamento"].to_csv(p / "teste_lookahead_truncamento.csv")
    R["negocios"].sort_values("contrib_pp", ascending=False).to_csv(p / "negocios.csv", index=False)
    R["por_ativo"].round(4).to_csv(p / "contribuicao_por_ativo.csv")
    pd.concat([R["sem_maiores"], R["sem_ativo"]]).round(4).to_csv(p / "concentracao.csv")
    R["regime"].round(4).to_csv(p / "regime_ligado_desligado.csv")
    R["wf_escolhas"].to_csv(p / "walk_forward_escolhas.csv")
    pd.DataFrame({"fundo": R["r"], "excesso_sobre_cdi": R["e"].reindex(R["r"].index)}).to_csv(p / "cota_diaria.csv")
    json.dump({**{k: float(v) for k, v in R["resumo_grade"].items()}, **R["placebo"], "walk-forward ativo OOS pp": float(R["wf_ativo"])}, open(p / "resumo.json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)


def imprime(m, R):
    o = R["metricas"]
    print(f"\n{'=' * 100}\n{m.NOME}\n{m.TESE}\nbenchmark {m.BENCHMARK} | fora da amostra desde {m.CORTE} | parâmetros {m.PARAMS} | regime {m.REGIME}")
    print("\n-- métricas\n" + fmt(o))
    print("\n-- grade original / PBO / Sharpe deflacionado\n" + "\n".join(f"   {k}: {v:.1f}" for k, v in R["resumo_grade"].items()))
    lq = R["leque"]["ativo OOS pp"]
    print(f"\n-- leque de parâmetros ({len(lq)} sorteios): ativo OOS p5 {lq.quantile(.05):+.1f} | mediana {lq.median():+.1f} | p95 {lq.quantile(.95):+.1f} pp"
          f" | P(>0) {(lq > 0).mean() * 100:.0f}%")
    print("\n-- custo (ativo OOS pp)\n" + fmt(R["custo"]) + "\n-- atraso de execução (ativo OOS pp)\n" + fmt(R["atraso"]))
    print("\n-- Monte Carlo (excesso sobre o benchmark, bootstrap em blocos do fora da amostra)\n" + fmt(R["mc"]))
    print("\n-- look-ahead: truncamento\n" + R["truncamento"].to_string())
    print("-- look-ahead: placebo\n" + "\n".join(f"   {k}: {v:.3f}" for k, v in R["placebo"].items()))
    ng = R["negocios"]
    cols = [c for c in ["ativo", "lado", "entrada", "saida", "dias", "retorno_%", "contrib_pp"] if c in ng]
    print("\n-- 10 melhores negócios\n" + ng.nlargest(10, "contrib_pp")[cols].round(2).to_string(index=False))
    print("-- 10 piores negócios\n" + ng.nsmallest(10, "contrib_pp")[cols].round(2).to_string(index=False))
    print("\n-- quem trouxe o retorno (soma por ativo, pp)\n" + fmt(R["por_ativo"].head(12)))
    print("\n-- concentração (ativo OOS sem os maiores negócios, pp)\n" + fmt(R["sem_maiores"]))
    print("-- variação do excesso bruto OOS ao tirar cada ativo (pp)\n" + fmt(R["sem_ativo"]))
    print("\n-- regime ligado x desligado\n" + fmt(R["regime"]))
    print(f"\n-- walk-forward (re-escolhe a variante todo ano só com o passado): ativo OOS {R['wf_ativo']:+.2f} pp a.a.\n" + R["wf_escolhas"].to_string())


def carteira(res, n=200, seed=0):
    """Pesos pelo inverso da vol de cada fundo no SEU período de calibração; alavancagem para vol 6% calibrada antes do último corte."""
    E = pd.DataFrame({k: R["r"] - C.CDI.reindex(R["r"].index) for k, (m, R) in res.items()})
    cortes = {k: pd.Timestamp(m.CORTE) for k, (m, R) in res.items()}
    corte = max(cortes.values())
    vol = pd.Series({k: E[k][(E.index < cortes[k]) & E[k].notna()].std() for k in E})
    w = (1 / vol) / (1 / vol).sum()
    E = E.fillna(0)
    alav = lambda pesos: .06 / ((E[E.index < corte] @ pesos).std() * np.sqrt(252))   # vol-alvo 6% medida antes do corte
    lev = alav(w)
    ret = lambda pesos: C.CDI.reindex(E.index) + (E @ pesos) * alav(pesos)       # toda variação de pesos é re-alavancada para os mesmos 6%
    r = ret(w)
    m = types.SimpleNamespace(BENCHMARK="CDI", CORTE=str(corte.date()), INICIO=str(E.index[0].date()))
    rng = np.random.default_rng(seed)
    leque_pesos = {i: ret(pd.Series(rng.dirichlet(w.values * 20), index=w.index)) for i in range(n)}
    sem = {}
    for k in w.index:
        w2 = w.drop(k) / w.drop(k).sum()
        sem[f"sem {res[k][0].NOME}"] = RB.ativo_aa(m, ret(w2.reindex(w.index).fillna(0)))
    mc, cam = RB.monte_carlo(m, r)
    b = C.CDI
    tab = pd.DataFrame({"total": C.metricas(r, b), "dentro da amostra": C.metricas(RB.ins(m, r), b), "fora da amostra": C.metricas(RB.oos(m, r), b)})
    ano = r.groupby(r.index.year).apply(lambda x: ((1 + x).prod() - (1 + b.reindex(x.index)).prod()) * 100)
    corr = E[E.index >= corte].corr()
    corr.columns = corr.index = [res[k][0].NOME for k in corr.columns]
    return {"r": r, "pesos": (w * lev), "alavancagem": lev, "metricas": tab, "ano": ano, "corr": corr, "leque_pesos": leque_pesos,
            "sem_fundo": pd.Series(sem), "mc": mc, "mc_caminhos": cam, "corte": corte,
            "fundos": {res[k][0].NOME: res[k][1]["r"] for k in res}}


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    n_leque = 20 if "--rapido" in sys.argv else 60
    nomes = args or FUNDOS
    res = {}
    for nome in nomes:
        m = importlib.import_module(f"fundos.{nome}")
        print(f"\n>>> {m.NOME}: carregando dados e rodando a bateria de robustez")
        d = m.carrega()
        R = RB.bateria(m, d, n_leque)
        imprime(m, R)
        salva(nome, R)
        G.painel(m, R, SAIDA / f"{nome}.png")
        res[nome] = (m, R)
    tr = RB.teste_truncamento_regimes()
    print("\n-- look-ahead nos regimes (dados comuns cortados em T)\n" + tr.to_string())
    SAIDA.mkdir(exist_ok=True)
    tr.to_csv(SAIDA / "teste_lookahead_regimes.csv")
    if not args:
        Rc = carteira(res)
        print(f"\n{'=' * 100}\nCARTEIRA DOS 5 (alavancagem {Rc['alavancagem']:.2f}x)\npesos (fração do PL):\n" + fmt(Rc["pesos"]))
        print("\n-- métricas\n" + fmt(Rc["metricas"]) + "\n\n-- correlação OOS\n" + fmt(Rc["corr"]))
        print("\n-- sem cada fundo (ativo OOS pp)\n" + fmt(Rc["sem_fundo"]) + "\n\n-- Monte Carlo\n" + fmt(Rc["mc"]))
        lp = pd.Series({k: RB.ativo_aa(types.SimpleNamespace(BENCHMARK="CDI", CORTE=str(Rc["corte"].date())), v) for k, v in Rc["leque_pesos"].items()})
        print(f"-- pesos sorteados ({len(lp)}x): ativo OOS p5 {lp.quantile(.05):+.1f} | mediana {lp.median():+.1f} | p95 {lp.quantile(.95):+.1f} pp")
        p = SAIDA / "carteira"
        p.mkdir(parents=True, exist_ok=True)
        Rc["metricas"].round(4).to_csv(p / "metricas.csv")
        Rc["pesos"].round(4).to_csv(p / "pesos.csv")
        Rc["corr"].round(3).to_csv(p / "correlacao_oos.csv")
        Rc["mc"].round(4).to_csv(p / "monte_carlo.csv")
        Rc["sem_fundo"].round(4).to_csv(p / "sem_cada_fundo.csv")
        Rc["r"].to_csv(p / "cota_diaria.csv")
        G.carteira(Rc, SAIDA / "carteira.png")
    print("\nArquivos em", SAIDA)
