"""Painéis de cada fundo e da carteira combinada."""
import textwrap

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import comum as C

VERDE, VERM, AZUL, LAR, CINZA = "#2E7D4F", "#B23A3A", "#1F2A4D", "#EC7000", "#C9CFD9"
plt.rcParams.update({"axes.spines.top": False, "axes.spines.right": False, "axes.grid": True, "grid.alpha": .2, "font.size": 9})


def _tit(ax, s):
    ax.set_title(s, loc="left", fontweight="bold", color=AZUL, fontsize=10)


def _eq(r):
    return (1 + r.fillna(0)).cumprod() * 100


def painel(m, R, arquivo):
    r, b = R["r"], C.BENCH[m.BENCHMARK].reindex(R["r"].index).fillna(0)
    corte = pd.Timestamp(m.CORTE)
    fig = plt.figure(figsize=(20, 16))
    g = fig.add_gridspec(4, 3, hspace=.5, wspace=.25)

    # 1. curva com o leque de parâmetros e a grade
    ax = fig.add_subplot(g[0, :2])
    L = pd.DataFrame({k: _eq(v) for k, v in R["curvas_leque"].items()}).reindex(r.index).ffill()
    G = pd.DataFrame({k: _eq(v) for k, v in R["curvas_grade"].items()}).reindex(r.index).ffill()
    ax.fill_between(r.index, L.min(axis=1), L.max(axis=1), color=VERDE, alpha=.10, label=f"leque: {L.shape[1]} sorteios de parâmetros (mín–máx)")
    ax.fill_between(r.index, L.quantile(.05, axis=1), L.quantile(.95, axis=1), color=VERDE, alpha=.22, label="leque 5%–95%")
    ax.fill_between(r.index, G.min(axis=1), G.max(axis=1), facecolor="none", edgecolor=AZUL, hatch="///", lw=0, alpha=.35, label=f"grade original ({G.shape[1]} variantes)")
    ax.plot(r.index, _eq(r), color=VERDE, lw=2.2, label="fundo (parâmetros escolhidos)")
    ax.plot(r.index, _eq(b), "k--", lw=1.2, label=m.BENCHMARK)
    ax.plot(r.index, _eq(C.R_IBOV.reindex(r.index)), color=CINZA, lw=1, label="Ibovespa")
    ax.axvspan(corte, r.index[-1], color="#FFF1E3", zorder=0)
    ax.set_yscale("log")
    ax.legend(frameon=False, fontsize=7.5, loc="upper left")
    _tit(ax, "Cota vs benchmark, com as faixas quando mexemos nos parâmetros (laranja = fora da amostra)")

    # 2. queda
    ax = fig.add_subplot(g[0, 2])
    eq = _eq(r)
    ax.fill_between(r.index, (eq / eq.cummax() - 1) * 100, color=VERM, alpha=.5, label="fundo")
    eb = _eq(b - 0)
    ax.plot(r.index, (eq / eb / (eq / eb).cummax() - 1) * 100, color=AZUL, lw=.8, label=f"relativa ao {m.BENCHMARK}")
    ax.legend(frameon=False, fontsize=7)
    _tit(ax, "Queda a partir do pico (%)")

    # 3. ano a ano
    ax = fig.add_subplot(g[1, 0])
    a = R["ano"]
    ax.bar(a.index.astype(str), a.values, color=[VERDE if v > 0 else VERM for v in a], width=.7)
    ax.tick_params(axis="x", rotation=90, labelsize=7)
    _tit(ax, f"Ativo por ano vs {m.BENCHMARK} (pp)")

    # 4. distribuição do leque e IS x OOS
    ax = fig.add_subplot(g[1, 1])
    lq = R["leque"]
    ax.hist(lq["ativo OOS pp"], bins=25, color=VERDE, alpha=.75, label="leque (sorteios)")
    ax.axvline(R["metricas"].loc["ativo a.a. pp", "fora da amostra"], color=LAR, lw=2, label="escolhido")
    ax.axvline(0, color="k", lw=.8)
    ax.legend(frameon=False, fontsize=7)
    _tit(ax, f"Ativo OOS com parâmetros vizinhos: P(>0) = {(lq['ativo OOS pp'] > 0).mean() * 100:.0f}%")

    # 5. custo e atraso
    ax = fig.add_subplot(g[1, 2])
    ax.plot(R["custo"].index, R["custo"].values, "o-", color=AZUL, label="custo (multiplicador)")
    ax2 = ax.twiny()
    ax2.plot(R["atraso"].index, R["atraso"].values, "s--", color=LAR, label="execução")
    ax2.tick_params(colors=LAR, labelsize=7)
    ax.axhline(0, color="k", lw=.6)
    ax.legend(frameon=False, fontsize=7, loc="lower left")
    ax2.legend(frameon=False, fontsize=7, loc="lower right")
    ax.set_title("Custo e atraso (ativo OOS, pp a.a.)", loc="left", fontweight="bold", color=AZUL, fontsize=10, pad=18)

    # 6. Monte Carlo 3 anos
    ax = fig.add_subplot(g[2, 0])
    P = R["mc_caminhos"]
    x = np.arange(P.shape[1]) / 252
    for lo, hi, al in ((5, 95, .18), (25, 75, .35)):
        ax.fill_between(x, np.percentile(P, lo, axis=0) * 100, np.percentile(P, hi, axis=0) * 100, color=AZUL, alpha=al)
    ax.plot(x, np.median(P, axis=0) * 100, color=AZUL, lw=2)
    ax.axhline(100, color="k", lw=.8)
    mc = R["mc"]
    _tit(ax, f"Monte Carlo 3 anos (relativo ao bench): P(bater) {mc.loc['P(bater o benchmark) %', '3 ano(s)']:.0f}%")
    ax.set_xlabel("anos")

    # 7. 12 meses móveis
    ax = fig.add_subplot(g[2, 1])
    roll = (1 + r).rolling(252).apply(np.prod, raw=True) - (1 + b).rolling(252).apply(np.prod, raw=True)
    ax.plot(r.index, roll * 100, color=AZUL)
    ax.axhline(0, color="k", lw=.6)
    ax.axvline(corte, color=LAR, lw=1.5)
    _tit(ax, "Ativo em 12 meses móveis (pp)")

    # 8. placebo
    ax = fig.add_subplot(g[2, 2])
    ax.hist(R["placebo_dist"], bins=30, color=CINZA)
    ax.axvline(R["placebo"]["excesso bruto OOS real pp"], color=VERDE, lw=2.5, label="fundo real")
    ax.legend(frameon=False, fontsize=7)
    _tit(ax, f"Placebo (posições deslocadas no tempo): p = {R['placebo']['p-valor (fração de placebos >= real)']:.2f}")

    # 9. melhores/piores negócios
    ax = fig.add_subplot(g[3, :2])
    ng = R["negocios"]
    sel = pd.concat([ng.nsmallest(10, "contrib_pp"), ng.nlargest(10, "contrib_pp").iloc[::-1]])
    lab = [f"{a} {pd.Timestamp(e):%m/%y}–{pd.Timestamp(s):%m/%y}" for a, e, s in zip(sel["ativo"].astype(str).str[:22], sel["entrada"], sel["saida"])]
    ax.barh(range(len(sel)), sel["contrib_pp"], color=[VERDE if v > 0 else VERM for v in sel["contrib_pp"]])
    ax.set_yticks(range(len(sel)), lab, fontsize=7)
    _tit(ax, "10 melhores e 10 piores negócios (contribuição ao PL, pp)")

    # 10. por ativo
    ax = fig.add_subplot(g[3, 2])
    pa = R["por_ativo"]["sum"]
    pa = pd.concat([pa.head(8), pa.tail(4)]).drop_duplicates() if len(pa) > 12 else pa
    ax.barh([str(i)[:22] for i in pa.index][::-1], pa.values[::-1], color=[VERDE if v > 0 else VERM for v in pa.values[::-1]])
    ax.tick_params(axis="y", labelsize=7)
    _tit(ax, "Quem trouxe o retorno: soma por ativo (pp)")

    o = R["metricas"]["fora da amostra"]
    fig.suptitle(f"{m.NOME}  —  OOS {o['retorno a.a. %']:.1f}% a.a. vs {m.BENCHMARK} {o['benchmark a.a. %']:.1f}% (ativo {o['ativo a.a. pp']:+.1f} pp, IR {o['IR vs bench']:.2f})"
                 f"  |  PBO {R['resumo_grade']['PBO %']:.0f}%", fontsize=15, fontweight="bold", color=AZUL, x=.01, ha="left")
    fig.text(.01, .955, "\n".join(textwrap.wrap("Tese: " + m.TESE, 220)), fontsize=9, color="#444")
    fig.savefig(arquivo, dpi=100, bbox_inches="tight")
    plt.close(fig)


def carteira(Rc, arquivo):
    r, port_leque, corr, mc_c = Rc["r"], Rc["leque_pesos"], Rc["corr"], Rc["mc_caminhos"]
    fig = plt.figure(figsize=(20, 11))
    g = fig.add_gridspec(2, 3, hspace=.35, wspace=.25)
    ax = fig.add_subplot(g[0, :2])
    L = pd.DataFrame({k: _eq(v) for k, v in port_leque.items()}).reindex(r.index).ffill()
    ax.fill_between(r.index, L.quantile(.05, axis=1), L.quantile(.95, axis=1), color=VERDE, alpha=.22, label=f"pesos sorteados ({L.shape[1]}x) 5%–95%")
    ax.plot(r.index, _eq(r), color=VERDE, lw=2.4, label="carteira dos 5")
    for nome, s in Rc["fundos"].items():
        ax.plot(r.index, _eq(s.reindex(r.index)), lw=.8, alpha=.7, label=nome[:30])
    ax.plot(r.index, _eq(C.CDI.reindex(r.index)), "k--", lw=1.2, label="CDI")
    ax.plot(r.index, _eq(C.R_IBOV.reindex(r.index)), color=CINZA, lw=1, label="Ibovespa")
    ax.axvspan(Rc["corte"], r.index[-1], color="#FFF1E3", zorder=0)
    ax.set_yscale("log")
    ax.legend(frameon=False, fontsize=7, loc="upper left", ncol=2)
    _tit(ax, "Carteira combinada (pesos pelo risco do período de calibração de cada fundo, vol-alvo 6%)")
    ax = fig.add_subplot(g[0, 2])
    ax.imshow(corr, cmap="RdBu_r", vmin=-1, vmax=1)
    for i in range(len(corr)):
        for j in range(len(corr)):
            ax.text(j, i, f"{corr.iloc[i, j]:.2f}", ha="center", va="center", fontsize=8)
    ax.set_xticks(range(len(corr)), [c[:12] for c in corr.columns], rotation=45, ha="right", fontsize=7)
    ax.set_yticks(range(len(corr)), [c[:18] for c in corr.columns], fontsize=7)
    _tit(ax, "Correlação diária dos excessos (fora da amostra)")
    ax = fig.add_subplot(g[1, 0])
    a = Rc["ano"]
    ax.bar(a.index.astype(str), a.values, color=[VERDE if v > 0 else VERM for v in a])
    ax.tick_params(axis="x", rotation=90, labelsize=7)
    _tit(ax, "Ativo por ano vs CDI (pp)")
    ax = fig.add_subplot(g[1, 1])
    x = np.arange(mc_c.shape[1]) / 252
    for lo, hi, al in ((5, 95, .18), (25, 75, .35)):
        ax.fill_between(x, np.percentile(mc_c, lo, axis=0) * 100, np.percentile(mc_c, hi, axis=0) * 100, color=AZUL, alpha=al)
    ax.plot(x, np.median(mc_c, axis=0) * 100, color=AZUL, lw=2)
    ax.axhline(100, color="k", lw=.8)
    _tit(ax, f"Monte Carlo 3 anos vs CDI: P(bater) {Rc['mc'].loc['P(bater o benchmark) %', '3 ano(s)']:.0f}%")
    ax = fig.add_subplot(g[1, 2])
    s = Rc["sem_fundo"]
    ax.barh([i[:28] for i in s.index], s.values, color=[VERDE if v > 0 else VERM for v in s.values])
    _tit(ax, "Ativo OOS da carteira sem cada fundo (pp)")
    o = Rc["metricas"]["fora da amostra"]
    fig.suptitle(f"Carteira dos 5 — OOS {o['retorno a.a. %']:.1f}% a.a. vs CDI {o['benchmark a.a. %']:.1f}% | Sharpe {o['Sharpe']:.2f} | pior queda {o['pior queda %']:.1f}%",
                 fontsize=15, fontweight="bold", color=AZUL, x=.01, ha="left")
    fig.savefig(arquivo, dpi=100, bbox_inches="tight")
    plt.close(fig)
