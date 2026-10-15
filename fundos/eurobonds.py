"""
Eurobonds corporativos brasileiros high yield.

Mesa: compro os bonds em dólar das empresas brasileiras com MAIOR spread sobre a Treasury (top 10% do mês) e travo tudo:
  - câmbio: vendo dólar futuro (DOL, B3) no valor da posição -> o dólar vira CDI menos o cupom cambial;
  - juros americanos: vendo Treasury na duration do bond -> sobra o spread de crédito.
Fica o carrego do high yield brasileiro em reais, sobre o CDI.

Regras (versão auditada, compra-e-segura):
  - sinal: no fim de cada mês, spread = yield do último print do mês - curva da Treasury no prazo; força = percentil entre os
    corporativos; vale do 2º pregão após o fim do mês até o próximo.
  - entra se força >= 0,90, print "vivo" (mudou nos últimos 5 dias), negociou em >= 40% dos dias em 63 dias e não caiu > 4% em
    5 dias; 1 bond por emissor; até n bonds com 1/n do PL (vaga vazia fica no CDI).
  - só compra bond descontado: se o print de execução passar de 88, desiste (teto herdado do livro auditado, hi=85 + 3).
  - sai só se força < 0,50 (ou some do ranking). Execução no 1º print a partir de t+1 (entrada: até t+5, senão desiste).
  - bid/ask por faixa de preço: meia ponta de 0,5 (>= 90), 1 (75-90), 1,5 (50-75), 2 pontos (< 50).
  - marcação no último print (sem ffill limitado); cupom corrido só com o bond >= 50 (bond em default negocia "flat").
  - o filtro de liquidez exclui sozinho a Andrade Gutierrez 2029 (print em ~10% dos dias), que no original era 45% do OOS.

Divergências em relação à versão auditada da pesquisa original:
  - duration do hedge de Treasury: o original usava o spread do PRÓPRIO mês (look-ahead pequeno); aqui uso o do mês anterior.
  - o original reconstruía o cupom cambial pela mediana entre bonds e financiava o hedge no T-bill; aqui uso direto
    PTAX - DOL (idêntico a menos de 1e-8) e o juro de 3 meses da própria curva da Treasury.
  - NÃO uso comum.brl (excesso em dólar sobre o T-bill -> CDI): o cupom cambial real (DOL vs PTAX) difere do CDI - T-bill em
    ~1,3 pp a.a. e tem ruído diário de ~11% a.a.; com comum.brl a correlação com a referência cai para 0,72.
  - safra dos dados: na referência faltava o DOL de 02 a 16/05/2023 (usava CDI - T-bill); hoje o dado existe e é usado.
Validação (2021-2026): correlação diária 0,996 com a referência; excesso a.a. IS 0,66 vs 0,88 pp; OOS 3,35 vs 3,33 pp.
"""
import numpy as np
import pandas as pd

import comum

NOME = "Eurobonds high yield Brasil com hedge"
TESE = ("Carrego os 15 eurobonds corporativos brasileiros de maior spread, com hedge de câmbio (DOL) e de Treasury: "
        "sobra CDI + spread de crédito high yield BR")
BENCHMARK = "CDI"
INICIO, CORTE = "2021-01-01", "2024-01-01"
REGIME = "nenhum"
CUSTO_TROCA = .02                     # ligar/desligar um livro de HY custa ~2 pontos ida e volta
PARAMS = {"n": 15}
GRADE = {"n": [10, 15, 25]}
VIZINHANCA = {"n": (10, 25)}

ENTRA, SAI, QUEDA_MAX, LIQ_MIN = .90, .50, -.04, .40
PRECO_MAX = 88                        # só compra bond descontado: se o print de execução passar de 88, desiste
INICIO_SINAL = pd.Period("2021-01", "M")
PRAZOS = {"1m": 1 / 12, "3m": .25, "6m": .5, "1a": 1, "2a": 2, "3a": 3, "5a": 5, "7a": 7, "10a": 10, "20a": 20, "30a": 30}
PASTA = comum.DADOS / "eurobonds"


def carrega():
    return {"precos": pd.read_parquet(PASTA / "precos.parquet"),                       # data, isin, preco (FINRA/TradingView)
            "cadastro": pd.read_csv(PASTA / "cadastro.csv", parse_dates=["venc"]).set_index("isin"),
            "treasury": comum.ler("eurobonds/treasury.csv"),                          # curva par da Treasury, % a.a.
            "dol": pd.read_parquet(PASTA / "dol.parquet")}                            # ajustes do dólar futuro (B3)


# ---------------------------------------------------------------- peças
def ytm(preco, cupom, anos):
    """Yield (% a.a., semestral) por bisseção, preço limpo."""
    lo, hi = np.full(len(preco), -20.0), np.full(len(preco), 200.0)
    n = np.ceil(anos * 2)
    k = np.arange(1, max(n.max(), 1) + 1)[None, :]
    t = k - (n[:, None] - anos[:, None] * 2)
    for _ in range(60):
        y = (lo + hi) / 2
        pv = cupom / 2 * ((1 + y[:, None] / 200) ** -t * (k <= n[:, None])).sum(1) + 100 * (1 + y / 200) ** -(anos * 2) - cupom / 2 * (n - anos * 2)
        alto = pv > preco
        lo, hi = np.where(alto, y, lo), np.where(alto, hi, y)
    return (lo + hi) / 2


def curva_em(ust, datas):
    """Curva da Treasury vigente em cada data (último dia publicado <= data)."""
    ust = ust[ust.notna().sum(axis=1) > 2]
    return ust.reindex(ust.index.union(datas)).ffill().bfill().reindex(datas)


def juro_no_prazo(curva, anos):
    """Juro (fração a.a.) interpolado na curva de cada linha, no prazo (anos) de cada coluna."""
    x = np.array(list(PRAZOS.values()))
    out = np.full(anos.shape, np.nan)
    for i, (v, a) in enumerate(zip(curva.to_numpy(), anos.to_numpy())):
        ok = ~np.isnan(v)
        out[i] = np.interp(a, x[ok], v[ok]) / 100
    return pd.DataFrame(out, index=anos.index, columns=anos.columns).where(anos.notna())


def meio_spread(p):
    """Meia ponta do bid/ask em pontos: perto do par 0,5; 75-90 1,0; 50-75 1,5; distressed < 50 2,0."""
    return np.where(p >= 90, .5, np.where(p >= 75, 1.0, np.where(p >= 50, 1.5, 2.0)))


def painel(d):
    """Tudo o que o livro precisa, dia a dia (só informação até cada dia)."""
    cad = d["cadastro"]
    dias = comum.DIAS[(comum.DIAS >= "2019-01-02") & (comum.DIAS <= d["precos"].data.max())]
    px = d["precos"].sort_values("data")

    # spread mensal: último print do mês -> yield -> menos a Treasury no prazo, no último pregão do mês
    fm = dias.to_series().groupby(dias.to_period("M")).max()
    Pmes = px.groupby([px.data.dt.to_period("M"), "isin"]).preco.last().unstack().reindex(index=fm.index, columns=cad.index)
    Pmes = Pmes.where((Pmes >= 5) & (Pmes <= 160))
    anos_m = pd.DataFrame({k: (cad.venc[k] - fm).dt.days.values / 365.25 for k in cad.index}, index=fm.index)
    Y = pd.DataFrame(np.nan, index=fm.index, columns=cad.index)
    for m in fm.index:
        ok = Pmes.loc[m].notna() & (anos_m.loc[m] > .3)
        if ok.any():
            Y.loc[m, ok] = ytm(Pmes.loc[m, ok].values, cad.cupom[ok].values, anos_m.loc[m, ok].values)
    ust_m = curva_em(d["treasury"], pd.DatetimeIndex(fm.values)).set_axis(fm.index)
    sprd = Y - juro_no_prazo(ust_m, anos_m.where(Y.notna())) * 100

    # força do sinal: percentil do spread no mês, a partir do 2º pregão depois do fim do mês
    r = sprd[sprd.index >= INICIO_SINAL].rank(axis=1, pct=True)
    pos = dias.searchsorted(fm[r.index].values, side="right") + 1
    r = r[pos < len(dias)].set_axis(dias[pos[pos < len(dias)]])
    F = r.reindex(dias).ffill(limit=30)

    # preço: print bruto, marca = último print
    P = px.pivot(index="data", columns="isin", values="preco").reindex(index=dias, columns=cad.index)
    P = P.where((P >= 5) & (P <= 160))
    Pm = P.ffill()
    dt = pd.Series(np.r_[1, np.diff(dias).astype("timedelta64[D]").astype(float)], index=dias)
    accr = pd.DataFrame(np.outer(dt / 365, cad.cupom), index=dias, columns=cad.index).where(Pm.shift(1) >= 50, 0.0)
    r_usd = ((Pm + accr) / Pm.shift(1) - 1).where(Pm.shift(1).notna())

    # hedge de juros: vende Treasury na duration (yield aprox. = spread do mês anterior + 4,5%), financiado no juro de 3 meses
    curva = curva_em(d["treasury"], dias)
    anos = pd.DataFrame({k: (cad.venc[k] - dias).days / 365.25 for k in cad.index}, index=dias)
    y_m = (sprd.shift(1) + 4.5).reindex(dias.to_period("M")).set_axis(dias)
    Dm = ((1 - (1 + y_m / 200) ** (-2 * anos)) / (y_m / 100)).clip(upper=12)
    yD = juro_no_prazo(curva, anos)
    y3 = juro_no_prazo(curva, pd.DataFrame({"3m": .25}, index=dias))["3m"]
    H = -(yD.shift(1) / 252 - Dm.shift(1) * (yD - yD.shift(1))).sub(y3.shift(1) / 252, axis=0)

    # hedge cambial: vendido em DOL (1º vencimento com > 5 dias, escolhido na véspera); dólar spot pela PTAX
    dol = d["dol"]
    venc = pd.to_datetime(dict(year=2000 + dol.ticker.str[4:6].astype(int), month=dol.ticker.str[3].map("FGHJKMNQUVXZ".index) + 1, day=1))
    dol = dol.assign(r=dol.ajuste / dol.ajuste_ant - 1, venc=venc)
    frente = dol[dol.venc > dol.data + pd.Timedelta(days=5)].sort_values("venc").groupby("data").ticker.first().reindex(dias)
    R_dol = dol.pivot(index="data", columns="ticker", values="r").reindex(dias)
    ontem = frente.shift(1)
    r_dol = pd.Series([R_dol.at[t, k] if isinstance(k, str) and k in R_dol else np.nan for t, k in zip(dias, ontem)], index=dias)
    fx = comum.PTAX.reindex(dias).ffill().pct_change(fill_method=None)
    cdi = comum.CDI.reindex(dias).fillna(0)
    c = (fx - r_dol).fillna(cdi - y3.shift(1).fillna(0) / 252)                # = CDI - cupom cambial (+ ruído PTAX x ajuste)

    exc = ((1 + r_usd).mul(1 + c, axis=0) - 1 + H.fillna(0)).sub(cdi, axis=0)
    vivo = P.notna() & (Pm.diff().abs() > 1e-9)                                   # print existe e mudou
    return {"dias": dias, "P": P, "Pm": Pm, "F": F, "exc": exc, "accr": accr, "emissor": cad.emissor.str.split().str[0],
            "vivo5": vivo.rolling(5, min_periods=1).max().astype(bool), "liq": vivo.rolling(63, min_periods=63).mean(),
            "q5": Pm / Pm.shift(5) - 1}


# ---------------------------------------------------------------- livro compra-e-segura
def livro(d, n=15, custo_mult=1, lag=0):
    """Simula o livro dia a dia. Devolve excesso diário, contribuição por bond, peso no fim do dia e negócios."""
    b = painel(d)
    dias, cols = b["dias"], np.array(b["P"].columns)
    Pv, Pmv, Xv, Fv, Av = (b[k].to_numpy() for k in ("P", "Pm", "exc", "F", "accr"))
    V5, LQ, Q5 = b["vivo5"].to_numpy(), b["liq"].to_numpy(), b["q5"].to_numpy()
    em = b["emissor"].reindex(cols).to_numpy()
    T, N = len(dias), len(cols)
    out, C, W, nav = np.zeros(T), np.zeros((T, N)), np.zeros((T, N)), 1.0
    val, info, pend_in, pend_out, negs = {}, {}, {}, {}, []
    for t in range(1, T):
        ganho = custo = 0.0
        for k in val:                                                             # rende de t-1 a t pela marca
            x = 0.0 if np.isnan(Xv[t, k]) else Xv[t, k]
            ganho += val[k] * x
            C[t, k] += val[k] * x / nav
            val[k] *= 1 + x
            info[k]["cupom"] += Av[t, k]
        for k in list(pend_out):                                                  # vende no 1º print a partir de t+1+lag
            if t >= pend_out[k] and not np.isnan(Pv[t, k]):
                c_ = val[k] * custo_mult * meio_spread(Pv[t, k]) / Pv[t, k]
                custo += c_
                C[t, k] -= c_ / nav
                a = info.pop(k)
                a.update(saida=dias[t], px_saida=Pv[t, k], retorno=(val.pop(k) - c_) / a.pop("v0") - 1)
                negs.append(a)
                del pend_out[k]
        for k in list(pend_in):                                                   # compra no 1º print entre t+1+lag e t+5+lag
            t0, t1 = pend_in[k]
            if t > t1:
                del pend_in[k]
            elif t >= t0 and not np.isnan(Pv[t, k]):
                del pend_in[k]
                if not Pv[t, k] <= PRECO_MAX:
                    continue
                v = nav / n
                c_ = v * custo_mult * meio_spread(Pv[t, k]) / Pv[t, k]
                val[k] = v - c_
                custo += c_
                C[t, k] -= c_ / nav
                info[k] = {"ativo": cols[k], "emissor": em[k], "entrada": dias[t], "px_entrada": Pv[t, k], "v0": v, "cupom": 0.0}
        out[t] = (ganho - custo) / nav
        nav *= 1 + out[t]
        for k in val:
            W[t, k] = val[k] / nav
        # ---- decisões no fechamento de t
        for k in val:
            if k not in pend_out and not Fv[t, k] >= SAI:
                pend_out[k] = t + 1 + lag
        livres = n - len(val) - len(pend_in) + len(pend_out)
        if livres <= 0:
            continue
        ok = V5[t] & (LQ[t] >= LIQ_MIN) & ~np.isnan(Pmv[t]) & (Fv[t] >= ENTRA) & ~(Q5[t] < QUEDA_MAX)
        cand = np.flatnonzero(ok)
        emis = {em[k] for k in list(val) + list(pend_in)}
        for k in cand[np.argsort(-Fv[t, cand])]:
            if livres <= 0:
                break
            if k in val or k in pend_in or em[k] in emis:
                continue
            pend_in[k] = (t + 1 + lag, t + 5 + lag)
            emis.add(em[k])
            livres -= 1
    for k, a in info.items():                                                     # posições abertas: marcadas no último print
        a.update(saida=dias[-1], px_saida=Pmv[-1, k], retorno=val[k] / a.pop("v0") - 1)
        negs.append(a)
    return (pd.Series(out, index=dias), pd.DataFrame(C, index=dias, columns=cols), pd.DataFrame(W, index=dias, columns=cols),
            pd.DataFrame(negs), dias)


def excesso(d, custo_mult=1, lag=0, regime=REGIME, n=15):
    e = livro(d, n, custo_mult, lag)[0].reindex(comum.DIAS).fillna(0)
    return comum.aplica_regime(e, regime, CUSTO_TROCA * custo_mult)


def posicoes(d, n=15):
    """W[t]: peso que rende a partir de t+2 (convenção de comum.carteira: W.shift(2) * R), i.e. o peso carregado no fim de t+1
    (o livro executa no 1º print a partir de t+1). R: excesso diário de cada bond sobre o CDI, com hedge."""
    _, C, Wfim, _, dias = livro(d, n)
    usados = Wfim.columns[Wfim.abs().sum() > 0]
    R = painel(d)["exc"][usados].reindex(comum.DIAS)
    return Wfim[usados].shift(-1).reindex(comum.DIAS).fillna(0), R


def negocios(d, n=15):
    _, C, _, N, dias = livro(d, n)
    if not len(N):
        return N
    N["lado"] = 1
    N["dias"] = [((dias > a) & (dias <= z)).sum() for a, z in zip(N.entrada, N.saida)]
    N["cupom_pts"] = N.pop("cupom").round(3)
    N["retorno_%"] = (N.pop("retorno") * 100).round(2)                             # excesso sobre o CDI com hedge, líquido de bid/ask
    N["retorno_preco_%"] = ((N.px_saida / N.px_entrada - 1) * 100).round(2)
    N["contrib_pp"] = [C.loc[(C.index >= a) & (C.index <= z), k].sum() * 100 for k, a, z in zip(N.ativo, N.entrada, N.saida)]
    return N[["ativo", "emissor", "lado", "entrada", "saida", "px_entrada", "px_saida", "cupom_pts", "dias", "retorno_%",
              "retorno_preco_%", "contrib_pp"]].sort_values("entrada").reset_index(drop=True)
