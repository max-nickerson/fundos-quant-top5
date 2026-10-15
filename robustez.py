"""
Bateria de robustez para qualquer fundo que siga o CONTRATO_FUNDO.md.

  1. resultado base (total, dentro e fora da amostra, ano a ano)
  2. grade original: PBO (CSCV), Sharpe deflacionado, % de variantes que batem o benchmark
  3. leque de parâmetros: N sorteios contínuos ao redor dos parâmetros escolhidos -> faixas da curva
  4. custo (0x a 3x) e atraso de execução (t+1 a t+6)
  5. Monte Carlo (bootstrap em blocos) do excesso fora da amostra: faixas de 1, 3 e 5 anos, P(bater o CDI), queda máxima
  6. look-ahead: (a) truncamento — corta todos os dados em T e exige o mesmo excesso até T-1;
                  (b) placebo — desloca as posições no tempo (deslocamento circular) e compara com o real
  7. quem trouxe o retorno: melhores/piores negócios, contribuição por ativo, resultado sem os maiores negócios, sem cada ativo
  8. regime ligado x desligado
"""
import itertools
import time

import numpy as np
import pandas as pd
from scipy.stats import norm

import comum as C

DESPESAS = .0015          # custódia, auditoria etc. a.a. (fundo próprio: sem taxa de gestão/performance)
N_TOTAL_TESTES = 109      # estratégias testadas na pesquisa inteira (para o Sharpe deflacionado "honesto")


# ---------------------------------------------------------------- utilidades
def cota(m, e):
    """Retorno diário do fundo = CDI + excesso - despesas, a partir do início do fundo."""
    e = e[e.index >= pd.Timestamp(m.INICIO)]
    return C.CDI.reindex(e.index).fillna(0) + e - DESPESAS / 252


def ativo(m, r):
    return r - C.BENCH[m.BENCHMARK].reindex(r.index).fillna(0)


def oos(m, x):
    return x[x.index >= pd.Timestamp(m.CORTE)]


def ins(m, x):
    return x[x.index < pd.Timestamp(m.CORTE)]


def ativo_aa(m, r, parte=oos):
    x = parte(m, r)
    return C.anual(x) - C.anual(C.BENCH[m.BENCHMARK].reindex(x.index).fillna(0))


def ir(x):
    return x.mean() / x.std() * np.sqrt(252) if x.std() > 0 else np.nan


# ---------------------------------------------------------------- 1. base
def base(m, d):
    e = m.excesso(d)
    r = cota(m, e)
    b = C.BENCH[m.BENCHMARK]
    tab = pd.DataFrame({"total": C.metricas(r, b), "dentro da amostra": C.metricas(ins(m, r), b), "fora da amostra": C.metricas(oos(m, r), b)})
    ano = r.groupby(r.index.year).apply(lambda x: ((1 + x).prod() - (1 + b.reindex(x.index).fillna(0)).prod()) * 100)
    return e, r, tab, ano.rename("ativo no ano (pp)")


# ---------------------------------------------------------------- 2. grade, PBO, Sharpe deflacionado
def pbo(M, S=10):
    """Probabilidade de overfitting (Bailey et al., CSCV). M: retornos ativos diários, T x variantes."""
    M = M.dropna(how="all").fillna(0)
    if M.shape[1] < 4 or len(M) < S * 20:
        return np.nan
    blocos = np.array_split(np.arange(len(M)), S)
    lam = []
    sr = lambda X: X.mean() / X.std().replace(0, np.nan)
    for comb in itertools.combinations(range(S), S // 2):
        a = np.concatenate([blocos[i] for i in comb])
        b = np.concatenate([blocos[i] for i in range(S) if i not in comb])
        melhor = sr(M.iloc[a]).idxmax()
        rk = min(max(sr(M.iloc[b]).rank(pct=True)[melhor], 1e-6), 1 - 1e-6)
        lam.append(np.log(rk / (1 - rk)))
    return (np.array(lam) <= 0).mean() * 100


def sharpe_deflacionado(a, n_testes, var_sr):
    """Bailey & López de Prado: prob. de o IR verdadeiro ser > 0 dado o número de testes feitos."""
    a = a.dropna()
    s, T = a.mean() / a.std(), len(a)
    g = .5772
    n = max(n_testes, 2)
    sr0 = np.sqrt(max(var_sr, 1e-12)) * ((1 - g) * norm.ppf(1 - 1 / n) + g * norm.ppf(1 - 1 / (n * np.e)))
    den = np.sqrt(max(1 - a.skew() * s + (a.kurt() + 2) / 4 * s ** 2, 1e-9))
    return norm.cdf((s - sr0) * np.sqrt(T - 1) / den) * 100


def grade(m, d):
    combos = [dict(zip(m.GRADE, v)) for v in itertools.product(*m.GRADE.values())]
    curvas = {}
    for p in combos:
        try:
            curvas[str(p)] = cota(m, m.excesso(d, **{**m.PARAMS, **p}))
        except Exception as ex:
            print("   variante falhou", p, ex)
    A = pd.DataFrame({k: ativo(m, r) for k, r in curvas.items()})
    res = pd.DataFrame({"ativo IS pp": {k: ativo_aa(m, r, ins) for k, r in curvas.items()},
                        "ativo OOS pp": {k: ativo_aa(m, r) for k, r in curvas.items()},
                        "IR IS": {k: ir(ins(m, A[k])) for k in A}, "IR OOS": {k: ir(oos(m, A[k])) for k in A}}).sort_values("ativo OOS pp")
    var_sr = (ins(m, A).mean() / ins(m, A).std()).var()
    escolhido = ativo(m, cota(m, m.excesso(d)))
    resumo = {"variantes": len(A), "PBO %": pbo(A),
              "% variantes que batem o benchmark OOS": (res["ativo OOS pp"] > 0).mean() * 100,
              "mediana das variantes OOS pp": res["ativo OOS pp"].median(),
              "Sharpe deflacionado (grade) %": sharpe_deflacionado(oos(m, escolhido), len(A), var_sr),
              f"Sharpe deflacionado ({N_TOTAL_TESTES} estratégias x grade) %": sharpe_deflacionado(oos(m, escolhido), N_TOTAL_TESTES * len(A), var_sr)}
    return res, curvas, resumo


# ---------------------------------------------------------------- 3. leque de parâmetros
def sorteia(m, rng):
    p = dict(m.PARAMS)
    for k, (lo, hi) in m.VIZINHANCA.items():
        v = rng.uniform(lo, hi)
        p[k] = int(round(v)) if isinstance(m.PARAMS[k], (int, np.integer)) and not isinstance(m.PARAMS[k], bool) else v
    return p


def leque(m, d, n=60, seed=0):
    rng = np.random.default_rng(seed)
    curvas, pars = {}, []
    for i in range(n):
        p = sorteia(m, rng)
        try:
            curvas[i] = cota(m, m.excesso(d, **p))
            pars.append({**p, "ativo OOS pp": ativo_aa(m, curvas[i]), "ativo IS pp": ativo_aa(m, curvas[i], ins)})
        except Exception as ex:
            print("   sorteio falhou", p, ex)
    return pd.DataFrame(pars), curvas


# ---------------------------------------------------------------- 4. custo e atraso
def custo_atraso(m, d):
    c = {f"{k}x": ativo_aa(m, cota(m, m.excesso(d, custo_mult=k))) for k in (0, .5, 1, 1.5, 2, 3)}
    a = {f"t+{l + 1}": ativo_aa(m, cota(m, m.excesso(d, lag=l))) for l in (0, 1, 2, 3, 5)}
    return pd.Series(c, name="ativo OOS pp por custo"), pd.Series(a, name="ativo OOS pp por execução")


# ---------------------------------------------------------------- 5. Monte Carlo
def bootstrap_caminhos(x, n=5000, T=252, bloco=21, seed=0):
    """Bootstrap estacionário (Politis & Romano): caminhos de T dias reamostrando blocos de tamanho médio `bloco`."""
    rng = np.random.default_rng(seed)
    x = np.asarray(x)
    novo = rng.random((n, T)) < 1 / bloco
    novo[:, 0] = True
    pos = np.arange(T)
    ini = np.maximum.accumulate(np.where(novo, pos, 0), axis=1)
    idx = (np.take_along_axis(rng.integers(len(x), size=(n, T)), ini, axis=1) + pos - ini) % len(x)
    return x[idx]


def monte_carlo(m, r, n=5000):
    """Reamostra o excesso diário do fundo sobre o benchmark FORA da amostra (com blocos, preserva autocorrelação)."""
    a = oos(m, ativo(m, r)).values
    out = {}
    for anos in (1, 3, 5):
        P = bootstrap_caminhos(a, n, 252 * anos)
        eq = np.cumprod(1 + P, axis=1)
        dd = (eq / np.maximum.accumulate(eq, axis=1) - 1).min(axis=1)
        tot = eq[:, -1] ** (1 / anos) - 1
        out[f"{anos} ano(s)"] = {"P(bater o benchmark) %": (tot > 0).mean() * 100, "ativo a.a. p5 pp": np.percentile(tot, 5) * 100,
                                  "ativo a.a. mediana pp": np.median(tot) * 100, "ativo a.a. p95 pp": np.percentile(tot, 95) * 100,
                                  "pior queda relativa p5 %": np.percentile(dd, 5) * 100}
    caminhos = np.cumprod(1 + bootstrap_caminhos(a, 2000, 252 * 3), axis=1)
    return pd.DataFrame(out), caminhos


# ---------------------------------------------------------------- 6. look-ahead
def corta(d, T):
    """Remove de todos os dados tudo que é posterior a T (índice de data ou coluna 'data')."""
    out = {}
    for k, v in d.items():
        if isinstance(v, (pd.DataFrame, pd.Series)):
            if isinstance(v.index, pd.DatetimeIndex):
                v = v[v.index <= T]
            elif isinstance(v, pd.DataFrame) and "data" in v.columns:
                v = v[pd.to_datetime(v["data"]) <= T]
        out[k] = v
    return out


def teste_truncamento(m, d, datas=None):
    """Se o excesso até T-1 muda quando apagamos os dados depois de T, a estratégia está olhando o futuro."""
    e = m.excesso(d)
    e = e[e.index >= pd.Timestamp(m.INICIO)]
    datas = datas or [e.index[int(len(e) * q)] for q in (.35, .6, .85)]
    res = {}
    for T in datas:
        et = m.excesso(corta(d, T))
        idx = e.index[e.index < T]
        dif = (e.reindex(idx) - et.reindex(idx).fillna(0)).abs()
        res[str(T.date())] = {"dias comparados": len(idx), "maior diferença diária": float(dif.max()), "passou": bool(dif.max() < 1e-10)}
    return pd.DataFrame(res).T


def teste_truncamento_regimes(datas=("2012-06-29", "2018-02-05", "2020-03-16", "2024-08-05")):
    """Os regimes usam dados comuns (VIX, S&P, HYG/IEF, Ibovespa). Corta esses dados em T e confere que o regime até T não muda."""
    out = {}
    cheio = {"risco_global": C.regime_risco_global(), "ibov_tendencia": C.regime_ibov_tendencia()}
    us, bova = C._US, C.BOVA
    for T in map(pd.Timestamp, datas):
        try:
            C._US, C.BOVA = us[us.index <= T], bova[bova.index <= T]
            for nome, f in (("risco_global", C.regime_risco_global), ("ibov_tendencia", C.regime_ibov_tendencia)):
                s = f()
                idx = s.index[s.index <= T]
                out[(nome, str(T.date()))] = float((s.reindex(idx) - cheio[nome].reindex(idx)).abs().max())
        finally:
            C._US, C.BOVA = us, bova
    e = pd.Series(np.random.default_rng(0).normal(0, .01, 3000), index=C.DIAS[:3000])
    s = C.regime_dd_stop(e)
    out[("dd_stop", "1500 dias")] = float((C.regime_dd_stop(e.iloc[:1500]) - s.iloc[:1500]).abs().max())
    return pd.Series(out, name="maior diferença (0 = sem look-ahead)")


def placebo(m, d, n=200, seed=0):
    """Mantém as posições do fundo, mas as desloca no tempo (deslocamento circular de >= 1 ano). Se o fundo real não for melhor que
    quase todos os placebos, o resultado não depende do timing do sinal."""
    W, R = m.posicoes(d)
    W, R = W.reindex(R.index).fillna(0), R.fillna(0)
    real = C.carteira(W, R, 0)
    rng = np.random.default_rng(seed)
    T = len(W)
    desl = rng.integers(252, max(T - 252, 253), n)
    pl = [C.carteira(pd.DataFrame(np.roll(W.values, k, axis=0), index=W.index, columns=W.columns), R, 0) for k in desl]
    f = lambda s: C.anual(oos(m, s.reindex(C.DIAS).fillna(0)) + C.CDI) - C.anual(oos(m, C.CDI))
    v_real, v_pl = f(real), np.array([f(s) for s in pl])
    return {"excesso bruto OOS real pp": v_real, "placebo mediana pp": float(np.median(v_pl)), "placebo p95 pp": float(np.percentile(v_pl, 95)),
            "p-valor (fração de placebos >= real)": float((v_pl >= v_real).mean())}, v_pl


# ---------------------------------------------------------------- 7. quem trouxe o retorno
def atribuicao(m, d, r):
    ng = m.negocios(d).sort_values("contrib_pp")
    por_ativo = ng.groupby("ativo")["contrib_pp"].agg(["sum", "count"]).sort_values("sum", ascending=False)
    o = ng[pd.to_datetime(ng["entrada"]) >= pd.Timestamp(m.CORTE)]
    anos = max(len(oos(m, r)) / 252, .5)
    base_pp = ativo_aa(m, r)
    sem = {f"sem os {k} melhores": base_pp - o.nlargest(k, "contrib_pp")["contrib_pp"].sum() / anos for k in (1, 3, 5, 10)}
    sem.update({f"sem os {k} piores": base_pp - o.nsmallest(k, "contrib_pp")["contrib_pp"].sum() / anos for k in (1, 3, 5)})
    # sem cada ativo (os 8 maiores em |contribuição|): zera o ativo e refaz a carteira bruta
    W, R = m.posicoes(d)
    W, R = W.reindex(R.index).fillna(0), R.fillna(0)
    bruto = C.carteira(W, R, 0)
    f = lambda s: C.anual(oos(m, s.reindex(C.DIAS).fillna(0)) + C.CDI) - C.anual(oos(m, C.CDI))
    tot = f(bruto)
    sem_ativo = {}
    for a in por_ativo["sum"].abs().sort_values(ascending=False).index[:8]:
        if a in W.columns:
            W2 = W.copy()
            W2[a] = 0
            sem_ativo[a] = f(C.carteira(W2, R, 0)) - tot
    return ng, por_ativo, pd.Series(sem, name="ativo OOS pp (aprox.)"), pd.Series(sem_ativo, name="variação do excesso bruto OOS (pp)")


# ---------------------------------------------------------------- 7b. walk-forward
def walk_forward(m, curvas):
    """Re-escolhe a variante da grade todo 1º de janeiro, só com o passado (maior IR desde o início), e usa no ano seguinte.
    Mostra se o processo de escolha — não só o parâmetro de hoje — teria funcionado."""
    A = pd.DataFrame({k: ativo(m, r) for k, r in curvas.items()}).dropna(how="all").fillna(0)
    R = pd.DataFrame(curvas).reindex(A.index).fillna(0)
    out, escolhas = [], {}
    for ano in range(pd.Timestamp(m.CORTE).year, A.index[-1].year + 1):
        passado = A[A.index < f"{ano}-01-01"]
        if len(passado) < 252:
            continue
        k = (passado.mean() / passado.std()).idxmax()
        escolhas[ano] = k
        out.append(R.loc[str(ano), k])
    r = pd.concat(out) if out else pd.Series(dtype=float)
    return r, pd.Series(escolhas, name="variante escolhida"), ativo_aa(m, r) if len(r) else np.nan


# ---------------------------------------------------------------- 8. regime
def regime(m, d):
    out = {}
    for g in dict.fromkeys([m.REGIME, "nenhum"]):
        r = cota(m, m.excesso(d, regime=g))
        out[g] = {"ativo IS pp": ativo_aa(m, r, ins), "ativo OOS pp": ativo_aa(m, r), "IR OOS": ir(oos(m, ativo(m, r))),
                  "pior queda %": C.metricas(r, C.BENCH[m.BENCHMARK])["pior queda %"]}
    return pd.DataFrame(out).T


# ---------------------------------------------------------------- tudo
def bateria(m, d, n_leque=60, log=print):
    t0 = time.time()
    R = {}
    R["e"], R["r"], R["metricas"], R["ano"] = base(m, d)
    log(f"   base ok ({time.time() - t0:.0f}s)")
    R["grade"], R["curvas_grade"], R["resumo_grade"] = grade(m, d)
    log(f"   grade ok ({time.time() - t0:.0f}s)")
    R["leque"], R["curvas_leque"] = leque(m, d, n_leque)
    log(f"   leque ok ({time.time() - t0:.0f}s)")
    R["custo"], R["atraso"] = custo_atraso(m, d)
    R["mc"], R["mc_caminhos"] = monte_carlo(m, R["r"])
    R["truncamento"] = teste_truncamento(m, d)
    log(f"   truncamento ok ({time.time() - t0:.0f}s)")
    R["placebo"], R["placebo_dist"] = placebo(m, d)
    R["negocios"], R["por_ativo"], R["sem_maiores"], R["sem_ativo"] = atribuicao(m, d, R["r"])
    R["regime"] = regime(m, d)
    R["wf_r"], R["wf_escolhas"], R["wf_ativo"] = walk_forward(m, R["curvas_grade"])
    log(f"   pronto ({time.time() - t0:.0f}s)")
    return R
