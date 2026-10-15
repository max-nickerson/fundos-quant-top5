"""
Revisita PF — deriva pós-resultado (PEAD) na B3 (linha E6 "Deriva pós-resultado (PEAD)").

Tese de mesa: o mercado brasileiro sub-reage a resultado fora do esperado; a reação anormal (contra o BOVA11) dos 2 primeiros pregões em
torno da divulgação do ITR/DFP continua por 2–3 meses. Sem consenso de analistas público, a "surpresa" é medida pela própria reação:
fechamento de t-1 até o fechamento de t+1, t = 1º pregão >= data de ENTREGA do ITR/DFP na CVM (1ª versão). |reação| >= limiar -> compro
(reação positiva) ou vendo alugado (negativa, só na variante "ambos"); decido no fechamento de t+1 e executo no fechamento de t+2.

Rota PF (edges de capital pequeno):
  - ações no lote padrão + fracionário (sufixo F, 1 ação): posição de capital x alavancagem / n_max (R$ 2 mil com R$ 20 mil e 10 posições)
    -> dá para entrar em small/mid caps com ADV de R$ 0,5–5 mi sem mover preço (o institucional exigia ADV >= R$ 5 mi);
  - isenção de IR: vendas de ações <= R$ 20 mil no mês = ganho isento (com R$ 20 mil e giro de ~40 pregões, quase todo mês);
  - venda a descoberto via aluguel PF: 0,5% do volume ao abrir (Clear/Rico) + taxa ao doador (1% a.a. ADV >= R$ 50 mi, 3% >= R$ 10 mi,
    senão 8%) e só em papel com ADV >= R$ 10 mi e preço >= R$ 3 (abaixo disso não há aluguel confiável — os piores negócios do
    institucional foram vendidos em penny stocks que dispararam);
  - hedge opcional: WIN vendido (inteiro) contra o líquido comprado, só quando ele chega a >= 0,5 contrato (R$ 50 mil).
Custos: 0,03% de emolumentos + meio spread do fechamento (mediana de 20 pregões das melhores ofertas do COTAHIST) + 0,2% na parte
fracionária (livro mais raso); custo_mult multiplica tudo. Ação comprada NÃO rende CDI; o dinheiro da venda alugada rende.
Proventos: retorno total do painel da pesquisa (COTAHIST corrigido por desdobramentos + dividendos/JCP do Yahoo no dia ex; deslistadas
ficam sem dividendo = conservador para o comprado). Ação que para de negociar (OPA/deslistagem) fica parada no último preço até a saída.
Ressalva: a limpeza de erros de cotação do painel (salto > 40% desfeito no dia seguinte) usa o pregão seguinte — é tratamento de dado,
não sinal; o teste de truncamento não a enxerga.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _util as U  # noqa: E402

C, pf = U.C, U.pf

NOME = "PEAD B3 em lote pequeno (deriva pós-resultado)"
TESE = ("Compro (no fracionário) a ação que reagiu >= 8% contra o BOVA11 nos 2 pregões em torno da entrega do ITR/DFP (e vendo alugado a "
        "líquida que caiu >= 8%) e seguro 60 pregões: o mercado sub-reage e a deriva continua; com R$ 2 mil por papel entro em small/mid "
        "caps que o institucional não pega, e com vendas <= R$ 20 mil/mês o ganho do comprado é isento. Hedge: WIN inteiro contra o líquido.")
BENCHMARK = "CDI"
INICIO, CORTE = "2014-06-01", "2021-01-01"
REGIME = "nenhum"
CUSTO_TROCA = .001
PARAMS = {"limiar": .08, "hold": 60, "lado": "ambos", "n_max": 10, "adv_min": 1e6, "hedge": "win"}   # maior IR IS (1,03) da grade x hedge
GRADE = {"limiar": [.03, .05, .08], "hold": [40, 60], "lado": ["compra", "ambos"]}
VIZINHANCA = {"limiar": (.06, .10), "hold": (45, 75), "n_max": (8, 12), "adv_min": (5e5, 3e6)}
RANKING = ["E6 Deriva pós-resultado (PEAD)"]
VARIANTES = {"institucional: ADV >= R$ 5 mi": {"adv_min": 5e6},
             "small caps: ADV >= R$ 200 mil": {"adv_min": 2e5},
             "só comprado": {"lado": "compra"},
             "sem hedge": {"hedge": "nenhum"},
             "só comprado sem hedge (o mais simples)": {"lado": "compra", "hedge": "nenhum"},
             "limiar 3%, 40 pregões (ranking institucional)": {"limiar": .03, "hold": 40},
             "só 5 posições": {"n_max": 5},
             "custo 0 (institucional, sem spread)": {"custo_mult": 0.0}}
INSTRUMENTOS = [
    {"onde": "B3 (Clear/Rico/XP/Inter/Nubank)", "ticker": "ações (lote padrão + fracionário F)", "lote": 1,
     "custo": "0,03% + meio spread real do fechamento (+0,2% na parte fracionária)"},
    {"onde": "B3 (BTC)", "ticker": "ação alugada (variante ambos)", "lote": 1, "custo": "0,5% do volume ao abrir + 1–8% a.a. ao doador"},
    {"onde": "B3", "ticker": "WIN (hedge opcional)", "lote": "1 contrato = 0,2 x Ibovespa", "custo": "R$ 0,39 por contrato"},
]
APLICAVEL = True
MOTIVO = ("Sim: ações no fracionário a partir de 1 ação; R$ 2 mil por posição com R$ 20 mil (R$ 5 mil com R$ 50 mil). Vendido só em "
          "papel líquido com aluguel. Hedge com WIN só faz sentido com R$ 50 mil (1 WIN ~ R$ 35 mil).")
ALAVANCAGENS = [1, 1.5, 2]
MOTIVO_ALAV = ("Acima de 1x a carteira comprada é financiada (conta margem/termo, CDI + 6% a.a., não confirmado) ou o fundo usa as ações como "
               "garantia de WIN; 5x de ações é inviável para PF (exigiria R$ 100–250 mil financiados).")

EMOL = .0003
FRAC_EXTRA = .002
ALUG_ABRE = .005
SPREAD_FIN_AA = .06
WIN_MULT, WIN_CUSTO = .2, .39


# =============================================================== dados
def _cnpj(s):
    return s.astype(str).str.replace(r"\D", "", regex=True).str.zfill(14)


def _le_painel():
    p = pd.read_pickle(U.FD / "painel_eventos_br.pkl")
    return {k: p[k] for k in ("P", "R", "ADV")}


def _le_spread():
    v = pd.read_parquet(U.FD / "b3_acoes_cotahist.parquet", columns=["data", "ticker", "fech", "oferta_compra", "oferta_venda", "codbdi"])
    v = v[v.codbdi == "02"]
    b, a = v.oferta_compra, v.oferta_venda
    v["hs"] = ((a - b) / (a + b)).where((b > 0) & (a >= b))
    H = v.pivot_table(index="data", columns="ticker", values="hs", aggfunc="last")
    return H.rolling(20, min_periods=3).median().clip(.0001, .05)          # meio spread mediano dos últimos 20 pregões (só passado)


def _le_eventos(cols):
    x = pd.read_parquet(U.FD / "cvm_itr_dfp.parquet", columns=["CNPJ_CIA", "DT_REFER", "DT_RECEB"])
    x["data"] = pd.to_datetime(x.DT_RECEB)
    x = x.sort_values("data").drop_duplicates(["CNPJ_CIA", "DT_REFER"])          # 1ª entrega de cada período
    x["cnpj"] = _cnpj(x.CNPJ_CIA)
    f = pd.read_parquet(U.FD / "cvm_fca_vm.parquet")
    f = f[f.Codigo_Negociacao.notna()]
    m = pd.DataFrame({"cnpj": _cnpj(f.CNPJ_Companhia), "raiz": f.Codigo_Negociacao.str.strip().str[:4].str.upper()})
    try:
        a = pd.read_csv(U.QD / "acoes_mapa.csv", dtype=str)
        m = pd.concat([m, pd.DataFrame({"cnpj": a.cnpj.str.zfill(14), "raiz": a.ticker.str[:4]})])
    except FileNotFoundError:
        pass
    m = m[m.raiz.str.match(r"^[A-Z]{4}$")].drop_duplicates()
    m = m.groupby("raiz").cnpj.agg(lambda s: s.value_counts().index[0]).reset_index()
    por_raiz = pd.Series(list(cols), index=[c[:4] for c in cols]).groupby(level=0).apply(lambda s: ",".join(s))
    m["tickers"] = m.raiz.map(por_raiz)
    tk = m.dropna(subset=["tickers"]).groupby("cnpj").tickers.agg(",".join)
    x["tickers"] = x.cnpj.map(tk)
    x = x.dropna(subset=["tickers"])
    return x[x.data >= "2013-12-01"][["data", "cnpj", "tickers"]].reset_index(drop=True)


def carrega():
    pn = {k: U.cache(f"rev_pead_{k}", lambda k=k: _le_painel()[k]) for k in ("P", "R", "ADV")}
    hs = U.cache("rev_pead_HS", _le_spread)
    ev = U.cache("rev_pead_ev", lambda: _le_eventos(pn["R"].columns))
    return {"P": pn["P"], "R": pn["R"], "ADV": pn["ADV"], "HS": hs.reindex(columns=pn["R"].columns), "ev": ev}


# =============================================================== simulação
def _simula(d, capital=20000, custo_mult=1, lag=0, alavancagem=1, limiar=.05, hold=40, lado="compra", n_max=10, adv_min=1e6,
            hedge="nenhum", venda_adv_min=1e7, venda_preco_min=3.0):
    R, P, ADV, HS, ev = d["R"], d["P"], d["ADV"], d["HS"], d["ev"]
    dias = R.index
    nD, cols = len(dias), list(R.columns)
    ci = {c: j for j, c in enumerate(cols)}
    Rv = R.values
    Pv = P.reindex(index=dias, columns=cols).ffill(limit=10).values
    Av = ADV.reindex(index=dias, columns=cols).values
    Hv = HS.reindex(index=dias, columns=cols).values
    rib = C.R_IBOV.reindex(dias).fillna(0).values
    cdi = C.CDI.reindex(dias).fillna(0).values
    A = np.cumsum(np.log1p(np.clip(np.nan_to_num(Rv) - rib[:, None], -.99, None)), axis=0)        # retorno anormal acumulado (log)
    # 1) eventos -> sinal (decisão no fechamento de t+1)
    i_ev = dias.searchsorted(ev.data.values)
    sinais = []
    for i, tks in zip(i_ev, ev.tickers.values):
        if i < 2 or i + 1 >= nD:
            continue
        js = [ci[t] for t in tks.split(",") if t in ci]
        if not js:
            continue
        a = Av[i - 1, js]
        if not np.isfinite(a).any() or np.nanmax(a) < adv_min:
            continue
        j = js[int(np.nanargmax(a))]
        if not (np.isfinite(Pv[i - 1, j]) and np.isfinite(Pv[i + 1, j])):
            continue
        reac = np.expm1(A[i + 1, j] - A[i - 1, j])
        if abs(reac) < limiar:
            continue
        s = 1 if reac > 0 else -1
        if s < 0 and (lado != "ambos" or Av[i - 1, j] < venda_adv_min or Pv[i + 1, j] < venda_preco_min):
            continue
        sinais.append((i + 1, j, s, reac, dias[i]))
    sinais.sort(key=lambda z: (z[0], -abs(z[3])))
    # 2) carteira: slots de valor fixo; entra no fechamento de t+2 (+lag), sai `hold` pregões depois
    val0 = capital * alavancagem / n_max
    acoes, vendas, perd, rf, vend = (np.zeros(nD) for _ in range(5))     # vend: P&L do livro vendido (tributável, sem isenção)
    liq = np.zeros(nD)                                                     # exposição líquida em R$ (para o hedge)
    held_W = np.zeros((nD, len(cols)))
    ativos_fim, negs = [], []                                              # ativos_fim: pregão de saída de cada posição aberta
    aberto = {}
    for i_dec, j, s, reac, dt_ev in sinais:
        i0 = i_dec + 1 + lag
        if i0 >= nD:
            continue
        ativos_fim = [x for x in ativos_fim if x > i0]
        if len(ativos_fim) >= n_max or aberto.get(j, -1) > i0:
            continue
        p0 = Pv[i0, j]
        if not np.isfinite(p0) or p0 <= 0:
            continue
        q = np.floor(val0 / p0)
        if q < 1:
            continue
        i1 = min(i0 + hold, nD - 1)
        if i1 <= i0:                                                       # entrada no último pregão da base: nada a marcar
            continue
        ativos_fim.append(i1)
        aberto[j] = i1
        r = np.nan_to_num(Rv[i0 + 1:i1 + 1, j])
        v = q * p0 * np.cumprod(1 + r)                                      # valor da posição (retorno total) no fim de cada dia
        vprev = np.r_[q * p0, v[:-1]]
        pnl = s * (v - vprev)
        hs = lambda i: Hv[i, j] if np.isfinite(Hv[i, j]) else (.002 if Av[i, j] >= 1e7 else .006)
        frac = (q % 100) / q                                               # parte no fracionário
        c0 = q * p0 * (EMOL + hs(i0) + frac * FRAC_EXTRA) * custo_mult
        sai = i0 + hold <= nD - 1                                          # saída dentro da base
        c1 = v[-1] * (EMOL + hs(i1) + frac * FRAC_EXTRA) * custo_mult if sai else 0.0
        if s < 0:
            c0 += q * p0 * ALUG_ABRE * custo_mult
            taxa = .01 if Av[i0, j] >= 5e7 else .03
            alug = vprev * taxa / 252 * custo_mult
        else:
            alug = np.zeros_like(vprev)
        seg = slice(i0 + 1, i1 + 1)
        livro = acoes if s > 0 else vend
        livro[seg] += pnl - alug
        livro[i0] -= c0
        if sai:
            livro[i1] -= c1
            if s > 0:
                vendas[i1] += v[-1]
        if s < 0:
            rf[seg] += vprev * cdi[seg]
        else:
            perd[seg] += vprev * cdi[seg]
        liq[seg] += s * vprev
        held_W[i0 - 1:i1 - 1, j] = s                                       # alinhado ao deslocamento de 2 dias de C.carteira
        tot = pnl.sum() - c0 - c1 - alug.sum()
        cdi_pos = (vprev * cdi[seg]).sum() * (-1 if s > 0 else 1)
        negs.append({"ativo": cols[j], "lado": s, "entrada": dias[i0], "saida": dias[i1], "dias": i1 - i0,
                     "retorno_%": s * (v[-1] / (q * p0) - 1) * 100, "contrib_pp": (tot + cdi_pos) / capital * 100,
                     "reacao_%": reac * 100, "entrega": dt_ev, "adv_mi": Av[i0, j] / 1e6, "acoes": q, "valor_R$": q * p0})
    # financiamento acima de 1x (comprado > patrimônio)
    excesso_fin = np.maximum(np.r_[0, np.maximum(liq, 0)[:-1]] - capital, 0)
    acoes -= excesso_fin * SPREAD_FIN_AA / 252 * custo_mult
    cls = {"renda_fixa": pd.Series(rf, index=dias)}
    cls.update(U.acoes_ir(pd.Series(acoes, index=dias), pd.Series(vendas, index=dias)))
    # venda a descoberto: tratada como tributável (conservador; a isenção de R$ 20 mil para short é controversa) e sem compensar a isenta
    cls["acoes"] = cls["acoes"] + pd.Series(vend, index=dias)
    if hedge == "win":
        # WIN vendido contra o líquido comprado (decidido no fechamento de t, vale de t+1), contratos inteiros, ajuste ~ BOVA11
        bova = C.BOVA.reindex(dias).ffill()
        ib_pts = 1000 * bova                                                            # ~ pontos do Ibovespa (BOVA11 ≈ Ibov/1000)
        n_w = -np.floor(np.maximum(liq, 0) / (WIN_MULT * ib_pts.values) + .5)
        n_w = pd.Series(n_w, index=dias).shift(1).fillna(0)
        rb = C.R_IBOV.reindex(dias).fillna(0).values
        pnl_w = n_w.shift(1).fillna(0).values * WIN_MULT * ib_pts.shift(1).values * (rb - cdi)   # futuro rende Ibov - CDI
        custo_w = np.abs(np.diff(np.r_[0, n_w.values])) * WIN_CUSTO * custo_mult
        cls["futuros_b3"] = pd.Series(np.nan_to_num(pnl_w) - custo_w, index=dias)
    cls["_cdi_perdido"] = pd.Series(perd, index=dias)
    return {"classes": cls, "negocios": pd.DataFrame(negs), "W": pd.DataFrame(held_W, index=dias, columns=cols),
            "cols": cols}


def excesso(d, capital=20000, custo_mult=1, lag=0, regime=REGIME, alavancagem=1, **params):
    p = {**PARAMS, **params}
    cls = _simula(d, capital, custo_mult, lag, alavancagem, **p)["classes"]
    perd = cls.pop("_cdi_perdido")
    e = ((sum(cls.values()) - perd) / capital).reindex(C.DIAS).fillna(0)
    return C.aplica_regime(e, regime, CUSTO_TROCA * custo_mult)


def classes_ir(d, capital=20000, **params):
    p = {**PARAMS, **params}
    kw = {k: p.pop(k) for k in ("custo_mult", "lag", "alavancagem") if k in p}
    p.pop("regime", None)
    return _simula(d, capital, **kw, **p)["classes"]


def _limpa(params):
    p = {**PARAMS, **params}
    for k in ("custo_mult", "lag", "alavancagem", "regime"):
        p.pop(k, None)
    return p


def posicoes(d, capital=20000, **params):
    """W = lado x (valor da posição / capital) nos dias carregados, alinhado ao deslocamento de 2 dias de C.carteira; R = retorno total
    da ação menos o CDI (sem custos)."""
    p = _limpa(params)
    s = _simula(d, capital, **p)
    val = capital / p["n_max"]
    W = s["W"].loc[:, (s["W"] != 0).any()] * (val / capital)
    R = d["R"].reindex(columns=W.columns).fillna(0).sub(C.CDI.reindex(d["R"].index).fillna(0), axis=0)
    return W.reindex(C.DIAS).fillna(0), R.reindex(C.DIAS).fillna(0)


def negocios(d, capital=20000, **params):
    ng = _simula(d, capital, **_limpa(params))["negocios"]
    return ng if len(ng) else pd.DataFrame(columns=["ativo", "lado", "entrada", "saida", "dias", "retorno_%", "contrib_pp"])


if __name__ == "__main__":
    import time
    d = carrega()
    for cap in (20000, 50000, 1e8):
        for kw in ({}, {"lado": "ambos"}, {"adv_min": 5e6}, {"adv_min": 2e5}, {"hedge": "win"}):
            t = time.time()
            e = excesso(d, capital=cap, **kw)
            r = C.CDI + e
            f = lambda a, b: round(C.anual(r[(r.index >= a) & (r.index < b)]) - C.anual(C.CDI[(C.CDI.index >= a) & (C.CDI.index < b)]), 2)
            print(cap, kw, f"{time.time() - t:.1f}s IS", f(INICIO, CORTE), "OOS", f(CORTE, "2030"), "n", len(negocios(d, capital=cap, **kw)))
