"""Gera um caderno por frente (pf/pesquisa/<frente>_resultados.md) a partir das baterias salvas em pf/resultados/bateria/."""
import pickle
from pathlib import Path

import pandas as pd

AQUI = Path(__file__).resolve().parent
BAT, PESQ = AQUI / "resultados" / "bateria", AQUI / "pesquisa"
FRENTES = {"rev_": "revisita", "b3_": "b3_acoes", "rf_": "renda_fixa", "gl_": "global_cripto", "db3_": "deriv_b3", "cme_": "micro_cme",
           "mh_": "macro_hedge", "lg_": "pf2_leilao_global", "fg_": "pf2_fluxo_global", "op_": "pf2_opcoes", "fu_": "pf2_futuros",
           "cr_": "pf2_cripto", "em_": "pf2_emergentes", "bb_": "pf2_b3", "jx_": "pf2_juros_fx", "mx_": "pf3_mecanismos"}


def f(x, d=2):
    try:
        return f"{float(x):+.{d}f}"
    except Exception:
        return "n/d"


def bloco(o, rk):
    R = o["R20"]
    met = R["metricas"]["fora da amostra"]
    rg = R["resumo_grade"]
    lq = R["leque"]["ativo OOS pp"]
    linha = rk.get(o["nome"], {})
    s = [f"### {o['NOME']}  (`{o['nome']}`)", "", f"**Tese:** {o.get('TESE', '')}", "",
         f"**Instrumentos:** {o.get('INSTRUMENTOS', '')}", "",
         f"**Aplicável:** {o.get('APLICAVEL')} — {o.get('MOTIVO', '')}", "",
         "| métrica | valor |", "|---|---|",
         f"| OOS desde | {o['CORTE'][:7]} |",
         f"| retorno OOS a.a. (R$ 20 mil) | {met['retorno a.a. %']:.1f}% vs CDI {met['benchmark a.a. %']:.1f}% |",
         f"| ativo OOS pp (R$ 20 mil / R$ 50 mil) | {f(o['ativo20'])} / {f(o['ativo50'])} |",
         f"| depois do IR (classe {linha.get('classe IR', '?')}) pp, 20k / 50k | {f(linha.get('depois do IR 20k pp'))} / {f(linha.get('depois do IR 50k pp'))} |",
         f"| IR OOS / Sharpe | {f(met['IR vs bench'])} / {f(met['Sharpe'])} |",
         f"| pior queda | {met['pior queda %']:.1f}% |",
         f"| PBO / Sharpe deflacionado | {rg.get('PBO %', float('nan')):.0f}% / {f(linha.get('Sharpe defl. %'), 0)}% |",
         f"| leque de parâmetros p5 / mediana / p95 | {f(lq.quantile(.05))} / {f(lq.median())} / {f(lq.quantile(.95))} |",
         f"| custo 2x / execução t+2 | {f(R['custo'].get('2x'))} / {f(R['atraso'].get('t+2'))} |",
         f"| walk-forward | {f(R['wf_ativo'])} |",
         f"| sem os 10 melhores negócios | {f(R['sem_maiores'].get('sem os 10 melhores'))} |",
         f"| placebo p | {R['placebo']['p-valor (fração de placebos >= real)']:.2f} |",
         f"| look-ahead (truncamento) | {'passou' if R['truncamento']['passou'].all() else 'FALHOU'} |", ""]
    ng = R["negocios"]
    cols = [c for c in ["ativo", "lado", "entrada", "saida", "dias", "retorno_%", "contrib_pp"] if c in ng]
    if len(ng):
        s += ["**10 melhores negócios**", "", ng.nlargest(10, "contrib_pp")[cols].round(2).to_markdown(index=False), "",
              "**10 piores negócios**", "", ng.nsmallest(10, "contrib_pp")[cols].round(2).to_markdown(index=False), ""]
        pa = R["por_ativo"].head(10)
        s += ["**Quem trouxe o retorno (soma por ativo, pp)**", "", pa.round(2).to_markdown(), ""]
    return "\n".join(s)


if __name__ == "__main__":
    rk = pd.read_csv(AQUI / "resultados" / "ranking_pf.csv", index_col=0).set_index("arquivo").to_dict("index")
    grupos = {}
    for p in sorted(BAT.glob("*.pkl")):
        o = pickle.load(open(p, "rb"))
        fr = "pf3_internacional" if o["nome"].endswith("_v2") else next((v for k, v in FRENTES.items() if o["nome"].startswith(k)), "outros")
        grupos.setdefault(fr, []).append(o)
    for fr, lst in grupos.items():
        lst.sort(key=lambda o: -(rk.get(o["nome"], {}).get("nota", 0) or 0))
        txt = [f"# Frente {fr} — resultados da bateria final (gerado automaticamente)", "",
               "Gerado por `pf/gerar_cadernos.py` a partir de `pf/resultados/bateria/`. IR de pessoa física por `pf/ir.py` "
               "(mensal na B3 com isenção de ações ≤ R$ 20 mil/mês, anual no exterior). Ordem: nota do ranking.", ""]
        txt += [bloco(o, rk) for o in lst]
        (PESQ / f"{fr}_resultados.md").write_text("\n".join(txt), encoding="utf-8")
        print(fr, len(lst))
