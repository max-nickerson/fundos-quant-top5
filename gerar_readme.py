"""Gera o README.md a partir de README_modelo.md e dos números em resultados/ (rode depois de rodar.py)."""
import importlib
import json
from pathlib import Path

import pandas as pd

from rodar import FUNDOS

AQUI = Path(__file__).resolve().parent
RES = AQUI / "resultados"


def linha(nome):
    m = importlib.import_module(f"fundos.{nome}")
    p = RES / nome
    met = pd.read_csv(p / "metricas.csv", index_col=0)["fora da amostra"]
    ca = pd.read_csv(p / "custo_e_atraso.csv", index_col=0).iloc[:, 0]
    lq = pd.read_csv(p / "leque_parametros.csv")["ativo OOS pp"]
    mc = pd.read_csv(p / "monte_carlo.csv", index_col=0)
    con = pd.read_csv(p / "concentracao.csv", index_col=0).iloc[:, 0]
    tr = pd.read_csv(p / "teste_lookahead_truncamento.csv", index_col=0)
    js = json.load(open(p / "resumo.json", encoding="utf-8"))
    dsr109 = next(v for k, v in js.items() if k.startswith("Sharpe deflacionado (109"))
    pbo = js["PBO %"]
    f = lambda x: f"{x:+.1f}"
    return (f"| {m.NOME} | {met['retorno a.a. %']:.1f}% vs {met['benchmark a.a. %']:.1f}% | **{f(met['ativo a.a. pp'])}** | {met['IR vs bench']:.2f} | "
            f"{met['pior queda %']:.1f}% | {'n/d' if pbo != pbo else f'{pbo:.0f}%'} | {js['Sharpe deflacionado (grade) %']:.0f}% / {dsr109:.0f}% | "
            f"{f(lq.quantile(.05))} / {f(lq.median())} / {f(lq.quantile(.95))} | {mc.loc['P(bater o benchmark) %', '3 ano(s)']:.0f}% | "
            f"{f(ca['2x'])} / {f(ca['t+3'])} | {f(js['walk-forward ativo OOS pp'])} | {f(con['sem os 10 melhores'])} | "
            f"{js['p-valor (fração de placebos >= real)']:.2f} | {'✅' if tr['passou'].all() else '❌'} |"), m


if __name__ == "__main__":
    cab = ("| Fundo | Retorno a.a. vs bench | Ativo pp | IR | Pior queda | PBO | Sharpe defl. grade / 109 | Leque p5 / mediana / p95 | "
           "MC P(bater 3a) | Custo 2x / exec t+3 | Walk-forward | Sem 10 melhores | Placebo p | Look-ahead |\n|" + "---|" * 14)
    linhas, fundos, paineis = [], [], []
    for n in FUNDOS:
        l, m = linha(n)
        linhas.append(l)
        fundos.append(f"| {m.NOME} | {m.TESE} | {m.BENCHMARK} | {m.CORTE[:7]} |")
        paineis.append(f"\n### {m.NOME}\n![{n}](resultados/{n}.png)")
    met = pd.read_csv(RES / "carteira" / "metricas.csv", index_col=0)
    pesos = pd.read_csv(RES / "carteira" / "pesos.csv", index_col=0).iloc[:, 0]
    mc = pd.read_csv(RES / "carteira" / "monte_carlo.csv", index_col=0)
    sem = pd.read_csv(RES / "carteira" / "sem_cada_fundo.csv", index_col=0).iloc[:, 0]
    o = met["fora da amostra"]
    cart = (f"\n- Fora da amostra (todos os fundos já fora da amostra): **{o['retorno a.a. %']:.1f}% a.a. vs CDI {o['benchmark a.a. %']:.1f}%**, "
            f"Sharpe {o['Sharpe']:.2f}, pior queda {o['pior queda %']:.1f}%; período todo: {met.loc['retorno a.a. %', 'total']:.1f}% a.a. vs "
            f"{met.loc['benchmark a.a. %', 'total']:.1f}%, Sharpe {met.loc['Sharpe', 'total']:.2f}, pior queda {met.loc['pior queda %', 'total']:.1f}%."
            f"\n- Pesos (fração do PL): " + ", ".join(f"{k} {v:.2f}" for k, v in pesos.items()) +
            f"\n- Monte Carlo: P(bater o CDI) em 1 / 3 / 5 anos = " + " / ".join(f"{mc.loc['P(bater o benchmark) %', c]:.0f}%" for c in mc.columns) +
            "\n- Ativo fora da amostra sem cada fundo (re-alavancado para 6%): " + "; ".join(f"{k.replace('sem ', '')} {v:+.1f} pp" for k, v in sem.items()))
    s = open(AQUI / "README_modelo.md", encoding="utf-8").read()
    s = s.replace("{TABELA}", cab + "\n" + "\n".join(linhas)).replace("{FUNDOS}", "\n".join(fundos)).replace("{CARTEIRA}", cart)
    s = s.replace("{PAINEIS}", "\n".join(paineis))
    open(AQUI / "README.md", "w", encoding="utf-8").write(s)
    print("README.md gerado")
