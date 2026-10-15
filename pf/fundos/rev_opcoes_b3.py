"""
Revisita PF — venda de opções na B3 com garantia em Tesouro Selic (cobre A6 covered call PETR4/VALE3 e A3 put-write com hedge de beta).

Rota PF: conta B3 (Clear/Rico/XP), opções mensais de BOVA11, PETR4 e VALE3 (as mais líquidas da B3), lote padrão de 100.
  - livro "put" (put-write coberto por caixa): vendo put ~otm% fora do dinheiro no 1º pregão útil depois do vencimento (t+1 do sinal),
    no BID do fechamento; a garantia é Tesouro Selic, que continua rendendo CDI -> o excesso é só o P&L das opções (vantagem PF:
    no varejo americano o caixa da conta não rende). Nocional de strike <= capital x alavancagem (1x = 100% coberto por caixa).
    Hedge de beta opcional: BOVA11 vendido (aluguel PF) = h x delta das puts na entrada; o dinheiro da venda rende CDI.
  - livro "call" (covered call, linha A6): compro PETR4/VALE3 (e BOVA11) em lotes de 100 (a ação NÃO rende CDI; recebe dividendos
    e JCP líquido) e vendo 1 call (1+otm) por lote quando o filtro deixa.
  O prêmio de volatilidade aqui é o BRASILEIRO (IV de 1 mês das opções da B3), não o do S&P da linha A3 institucional (CBOE + SVXY).

Execução e marcação (anti-autoengano):
  - sinal no 1º pregão depois do vencimento (ds); execução no pregão seguinte (d0 = t+1, + lag), no bid (venda) / ask (compra) do
    fechamento: preço = meio - custo_mult x (meio - bid). Só agride livro com spread <= 25% do meio.
  - marcação diária da opção vendida: (1) meio das ofertas do dia se as duas existem e são sãs; (2) senão o fechamento SE houve negócio
    no dia; (3) senão Black-Scholes com a IV da entrada, S e strike do dia (nunca preço parado). Sempre >= intrínseco.
    No vencimento: intrínseco com o fechamento do ativo e o strike vigente. O total do ciclo não depende da marcação.
  - exercício/atribuição no vencimento: put no dinheiro -> compro 100 x n ações ao strike (caixa do Tesouro Selic) e vendo no fechamento
    do pregão seguinte no bid (P&L desse dia + emolumentos do exercício). Call no dinheiro (covered call) -> entrego as ações ao strike e
    recompro no pregão seguinte (custo de ida e volta + venda conta para a isenção de R$ 20 mil).
  - proventos: o strike das opções de ações é ajustado pela B3 pelos proventos em dinheiro (o dado traz o strike vigente a cada dia);
    BOVA11 não distribui. Ação comprada recebe dividendo (isento) e JCP líquido de 15%; a queda do preço na data-ex entra no P&L de ações.
  - séries de outra classe na mesma raiz: VALE só a partir de 2018 (até dez/2017 a raiz VALE misturava VALE3 e VALE5 — o institucional
    vendeu "puts de VALE3" com IV de 105–160% em 2015 que eram de VALE5, um artefato de ~+4 pp a.a. no IS); na entrada exijo IV entre 5% e 200%.

Premissas de custo (fontes no caderno, pf/... secao_rev_opcoes_b3.md):
  - tarifas B3 de opções de ações/ETF PF: 0,134% do prêmio por lado (0,037% negociação + 0,0275% liquidação + 0,0695% registro);
    exercício de opções = operação à vista: 0,03% do valor (strike x quantidade); ação/ETF à vista: 0,03% + meio spread do fechamento;
  - aluguel BOVA11 (hedge): 0,5% do volume ao abrir/aumentar o contrato e 0,5% a.a. de renovação + 1% a.a. ao doador;
  - Tesouro Selic como garantia: custódia B3 0,20% a.a. sobre o que passa de R$ 10 mil (Tesouro Selic é isento até R$ 10 mil) — cobrada
    só no livro put (a garantia precisa ser título; o CDI do benchmark pode vir de CDB sem custódia).
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import brentq
from scipy.special import ndtr

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _util as U  # noqa: E402

C, pf = U.C, U.pf

NOME = "Venda de opções B3 com garantia em Tesouro Selic (put-write / covered call)"
TESE = ("O brasileiro paga caro por proteção de 1 mês em BOVA11/PETR4/VALE3: vendo put ~3% OTM no bid depois de cada vencimento, com o "
        "caixa inteiro em Tesouro Selic como garantia (rende CDI), e seguro até o vencimento; filtro de IV alta (IV ATM acima da mediana "
        "dos 12 ciclos anteriores). Variante covered call (A6): ação em lote de 100 + call OTM vendida.")
BENCHMARK = "CDI"
INICIO, CORTE = "2014-03-01", "2021-01-01"
REGIME = "nenhum"
CUSTO_TROCA = .001
PARAMS = {"livro": "put", "otm": .03, "filtro": "iv_alta", "hedge": 0.0, "ativos": "BOVA,PETR,VALE"}   # melhor IR IS (0,28) da grade
GRADE = {"otm": [.03, .06, .10], "filtro": ["sempre", "iv_alta"], "hedge": [0.0, 0.5]}
VIZINHANCA = {"otm": (.02, .06), "hedge": (0.0, .25)}
RANKING = ["A6 Covered call PETR4/VALE3", "A3 Put-write com hedge de beta"]
VARIANTES = {
    "put sem filtro": {"filtro": "sempre"},
    "put com hedge 0,5 BOVA11 alugado": {"hedge": .5},
    "put só BOVA11": {"ativos": "BOVA"},
    "put só PETR+VALE": {"ativos": "PETR,VALE"},
    "covered call PETR+VALE iv_alta otm 10% (A6)": {"livro": "call", "ativos": "PETR,VALE", "otm": .10},
    "covered call PETR+VALE sempre otm 6%": {"livro": "call", "ativos": "PETR,VALE", "filtro": "sempre"},
    "custos institucionais (meio, sem emol.)": {"custo_mult": 0.0},
}
INSTRUMENTOS = [
    {"onde": "B3 (Clear/Rico/XP)", "ticker": "opções mensais BOVA11/PETR4/VALE3 (séries BOVAxNNN, PETRxNNN, VALExNNN)", "lote": 100,
     "custo": "bid/ask real do fechamento + 0,134% do prêmio (tarifas B3); exercício 0,03% do strike x qtd"},
    {"onde": "Tesouro Direto / B3", "ticker": "Tesouro Selic (LFT) como garantia", "lote": "~R$ 170 (fração de título)",
     "custo": "rende CDI; custódia 0,20% a.a. acima de R$ 10 mil"},
    {"onde": "B3", "ticker": "PETR4, VALE3, BOVA11 (lote de 100 no covered call; ações recebidas no exercício)", "lote": 100,
     "custo": "0,03% emolumentos + meio spread"},
    {"onde": "B3 (BTC)", "ticker": "BOVA11 alugado (hedge opcional)", "lote": 1,
     "custo": "0,5% do volume por contrato novo + 0,5% a.a. renovação + 1% a.a. doador"},
]
APLICAVEL = True
MOTIVO = ("Sim com R$ 20 mil e R$ 50 mil: 1 put de PETR4 = 100 ações (~R$ 3–4 mil de strike), VALE3 ~R$ 6–9 mil, BOVA11 ~R$ 12–17 mil; "
          "com R$ 20 mil cabe ~1 BOVA + 1–2 PETR + 1 VALE totalmente cobertos por caixa. Garantia em Tesouro Selic rende CDI.")
ALAVANCAGENS = [1, 1.5, 2]
MOTIVO_ALAV = ("Alavancagem = nocional de strike / patrimônio. A B3 exige margem de ~15–30% do nocional para put OTM vendida, então 1,5x e 2x "
               "cabem com folga de garantia em Tesouro Selic; 5x exigiria margem > patrimônio em estresse (mar/2020) -> não viável.")

ATIVOS = {"BOVA": "BOVA11", "PETR": "PETR4", "VALE": "VALE3"}
LOTE = 100
EMOL_OPC = .00134         # B3 opções de ações PF: negociação 0,037% + liquidação 0,0275% + registro 0,0695% do prêmio, por lado
EMOL_VISTA = .0003        # ação/ETF à vista e exercício
ALUG_ABRE, ALUG_RENOVA_AA, ALUG_DOADOR_AA = .005, .005, .01
CUSTODIA_TD_AA, ISENCAO_TD = .002, 10_000
VALE_DESDE = pd.Timestamp("2018-01-01")   # até a migração para o Novo Mercado (dez/2017) a raiz VALE misturava opções de VALE3 e VALE5


# =============================================================== dados
def _le_spot():
    v = pd.read_parquet(U.FD / "b3_vista.parquet", columns=["data", "ticker", "fech", "oferta_compra", "oferta_venda", "fatcot"],
                        filters=[("ticker", "in", list(ATIVOS.values()))])
    for c in ("fech", "oferta_compra", "oferta_venda"):
        v[c] = v[c] / v.fatcot.clip(lower=1)
    inv = {b: a for a, b in ATIVOS.items()}
    out = {}
    for col, nome in (("fech", "S"), ("oferta_compra", "bid"), ("oferta_venda", "ask")):
        x = v.pivot_table(index="data", columns="ticker", values=col, aggfunc="last").rename(columns=inv)
        for a in ATIVOS:
            out[f"{nome}_{a}"] = x[a].where(x[a] > 0) if a in x else np.nan
    sp = pd.DataFrame(out)
    # proventos oficiais B3: data-ex = pregão seguinte ao último "com"; dividendo bruto (isento) e JCP (15% retido)
    p = pd.read_parquet(U.FD / "arb_proventos.parquet")
    p["com"] = pd.to_datetime(p.lastDateTimePriorEx, errors="coerce").dt.normalize()
    p["val"] = pd.to_numeric(p.valueCash.astype(str).str.replace(",", "."), errors="coerce")
    p = p.drop_duplicates(["code4", "typeStock", "corporateAction", "com", "val"])
    cls = {"PETR": "PN", "VALE": "ON"}
    for a, tp in cls.items():
        q = p[(p.code4 == a) & (p.typeStock.str.strip() == tp) & p.com.notna()]
        div = pd.Series(0.0, index=sp.index)
        jcp = pd.Series(0.0, index=sp.index)
        for com, act, val in zip(q.com, q.corporateAction, q.val):
            i = sp.index.searchsorted(com, side="right")
            if i < len(sp) and val == val:
                (jcp if "JRS" in act else div).iloc[i] += val
        sp[f"div_{a}"], sp[f"jcp_{a}"] = div, jcp
    sp["div_BOVA"] = sp["jcp_BOVA"] = 0.0
    sp["ir_jcp"] = np.where(sp.index >= "2026-01-01", .175, .15)          # JCP: 15% retido; 17,5% desde 2026 (LC 224/2025)
    return sp.sort_index()


def _le_opc():
    sp = _le_spot()
    o = pd.read_parquet(U.FD / "b3_opcoes.parquet", columns=["data", "serie", "raiz", "tipo", "fech", "oferta_compra", "oferta_venda",
                                                            "negocios", "strike", "venc"],
                        filters=[("raiz", "in", list(ATIVOS))])
    o = o[(o.strike > 0) & o.venc.notna() & ~o.serie.str.contains("W")]
    dte = (o.venc - o.data).dt.days
    o = o[(dte >= 0) & (dte <= 50)]
    S = pd.Series(np.nan, index=o.index)
    for a in ATIVOS:
        m = o.raiz == a
        S[m] = o.loc[m, "data"].map(sp[f"S_{a}"]).values
    mon = o.strike / S
    o = o[(mon > .6) & (mon < 1.4)].copy()
    o["bid"] = o.oferta_compra.where(o.oferta_compra > 0)
    o["ask"] = o.oferta_venda.where(o.oferta_venda > 0)
    o["ask"] = o.ask.where(o.ask >= o.bid.fillna(0))
    return o[["data", "raiz", "serie", "tipo", "strike", "venc", "fech", "negocios", "bid", "ask"]].reset_index(drop=True)


def carrega():
    return {"opc": U.cache("rev_opcoes_b3_opc", _le_opc), "spot": U.cache("rev_opcoes_b3_spot", _le_spot)}


# =============================================================== Black-Scholes (sem dividendos: strike é ajustado por proventos)
def _bs(S, K, T, r, s, tipo):
    s = np.maximum(s, 1e-4)
    T = np.maximum(T, 1 / 252)
    d1 = (np.log(S / K) + (r + s * s / 2) * T) / (s * np.sqrt(T))
    d2 = d1 - s * np.sqrt(T)
    if tipo == "C":
        return S * ndtr(d1) - K * np.exp(-r * T) * ndtr(d2), ndtr(d1)
    return K * np.exp(-r * T) * ndtr(-d2) - S * ndtr(-d1), ndtr(d1) - 1


def _iv(p, S, K, T, r, tipo):
    intr = max(S - K * np.exp(-r * T), 0) if tipo == "C" else max(K * np.exp(-r * T) - S, 0)
    if not (p == p) or p <= intr + 1e-6:
        return np.nan
    try:
        return brentq(lambda s: float(_bs(S, K, T, r, s, tipo)[0]) - p, 1e-3, 5.0, xtol=1e-5)
    except ValueError:
        return np.nan


def _du(a, b):
    return np.busday_count(np.asarray(a, dtype="datetime64[D]"), np.asarray(b, dtype="datetime64[D]"))


def _r_aa(dt):
    return np.log1p((1 + C.CDI.get(dt, .0004)) ** 252 - 1)


def _mid(g):
    mid = (g.bid + g.ask) / 2
    sano = g.bid.notna() & g.ask.notna() & ((g.ask - g.bid) <= .5 * mid + .02)
    return mid.where(sano)


# =============================================================== estrutura pré-calculada (depende só de d; chave muda quando d é cortado)
_CACHE = {}


def _estrutura(d):
    o, sp = d["opc"], d["spot"]
    chave = (len(o), str(o.data.max()), len(sp), str(sp.index.max()))
    if chave in _CACHE:
        return _CACHE[chave]
    dias = C.DIAS[C.DIAS <= sp.index.max()]
    pos = pd.Series(np.arange(len(dias)), index=dias)
    est = {"dias": dias, "raizes": {}, "memo": {}}
    for a in ATIVOS:
        oa = o[(o.raiz == a) & o.data.isin(dias)].copy()
        oa["mid"] = _mid(oa)
        oa["di"] = pos.reindex(oa.data).values
        S = sp[f"S_{a}"].reindex(dias).ffill(limit=5)
        vm = oa.groupby("venc").size()
        vm = vm.groupby(vm.index.to_period("M")).idxmax().sort_values().values
        porv = {}
        for v, g in oa.groupby("venc"):
            g = g.sort_values(["di", "strike"])
            porv[pd.Timestamp(v)] = {"g": g, "dia": g.groupby("di").indices, "serie": g.groupby("serie").indices,
                                     "K": g.strike.values, "bid": g.bid.values, "ask": g.ask.values, "mid": g.mid.values,
                                     "fech": g.fech.values, "neg": g.negocios.values, "tipo": g.tipo.values, "di_": g.di.values.astype(int),
                                     "nome": g.serie.values}
        ciclos = []
        for v0, v1 in zip(vm[:-1], vm[1:]):
            v0, v1 = pd.Timestamp(v0), pd.Timestamp(v1)
            dd = C.DIAS[(C.DIAS > v0) & (C.DIAS < v1)]                       # calendário inteiro (não depende do corte dos dados)
            if len(dd) < 4 or v1 not in porv or dd[0] not in pos.index:
                continue
            ds = dd[0]
            P = porv[v1]
            i_ds = int(pos[ds])
            S0 = S.iloc[i_ds]
            ivs = []
            if i_ds in P["dia"] and S0 == S0:
                rows = P["dia"][i_ds]
                T, r = max(_du(ds, v1), 1) / 252, _r_aa(ds)
                for tp in ("C", "P"):
                    rr = rows[(P["tipo"][rows] == tp) & np.isfinite(P["mid"][rows])]
                    if len(rr):
                        k = rr[np.argmin(np.abs(P["K"][rr] - S0))]
                        if abs(P["K"][k] / S0 - 1) < .05:
                            ivs.append(_iv(P["mid"][k], S0, P["K"][k], T, r, tp))
            ivs = [z for z in ivs if z == z]
            if a == "VALE" and ds < VALE_DESDE:
                ivs = []
            ciclos.append({"ds": ds, "i_ds": i_ds, "v": v1, "i_v": int(pos[v1]) if v1 in pos.index else -1,
                           "iv": np.mean(ivs) if ivs else np.nan})
        c = pd.DataFrame(ciclos)
        if len(c):
            c["iv_med"] = c.iv.rolling(12, min_periods=6).median().shift(1)
            c["on_iv"] = (c.iv > c.iv_med).values
        est["raizes"][a] = {"ciclos": c, "porv": porv, "S": S.values}
    R = pd.DataFrame({a: pd.Series(est["raizes"][a]["S"], index=dias).pct_change(fill_method=None) for a in ATIVOS})
    est["beta"] = (R.rolling(126, min_periods=60).cov(R["BOVA"]).div(R["BOVA"].rolling(126, min_periods=60).var(), axis=0)
                   ).clip(0, 2).fillna(1.0).values
    est["beta_col"] = {a: k for k, a in enumerate(R.columns)}
    _CACHE.clear()
    _CACHE[chave] = est
    return est


def _alocar(noc, budget, total):
    """Contratos inteiros: cada ativo tem um orçamento (capital x alav / nº de ativos); primeiro o piso, depois completa 1 contrato por vez
    no ativo menos alocado, sem passar do total (soma dos orçamentos dos ativos ligados) nem de max(1,5 x orçamento, 1 contrato) por ativo.
    Com R$ 20 mil isso deixa caber 1 put de BOVA11 (~R$ 12–17 mil) quando ela é o único ativo ligado ou quando sobra orçamento."""
    n = {a: int(budget // x) if x > 0 else 0 for a, x in noc.items()}
    tot = sum(n[a] * noc[a] for a in noc)
    while True:
        cand = [a for a, x in noc.items() if x > 0 and tot + x <= total * 1.0001 and (n[a] + 1) * x <= max(1.5 * budget, x)]
        if not cand:
            return n
        a = min(cand, key=lambda k: (n[k] * noc[k], noc[k]))
        n[a] += 1
        tot += noc[a]


def _escolhe(est, a, v, i0, tipo, alvo):
    """Série do tipo com strike mais perto do alvo, com bid e spread <= 25% do meio, no pregão i0 (memoizado)."""
    ch = ("esc", a, v, i0, tipo, round(alvo, 4))
    if ch in est["memo"]:
        return est["memo"][ch]
    P = est["raizes"][a]["porv"][v]
    res = None
    rows = P["dia"].get(i0)
    if rows is not None:
        b, k, m, sk = P["bid"][rows], P["ask"][rows], P["mid"][rows], P["tipo"][rows]
        ok = (sk == tipo) & np.isfinite(b) & np.isfinite(m) & ((k - b) <= .25 * m)
        rr = rows[ok]
        if len(rr):
            j = rr[np.argmin(np.abs(P["K"][rr] - alvo))]
            if abs(P["K"][j] / alvo - 1) <= .04:
                res = j
    est["memo"][ch] = res
    return res


def _trilha(est, a, v, serie, i0, i1):
    """Meio (só ofertas sãs), fechamento, nº de negócios e strike da série em cada pregão i0..i1 (NaN onde não negociou)."""
    ch = ("tr", a, v, serie, i0, i1)
    if ch in est["memo"]:
        return est["memo"][ch]
    P = est["raizes"][a]["porv"][v]
    rows = P["serie"][serie]
    di = P["di_"][rows]
    n = i1 - i0 + 1
    out = {c: np.full(n, np.nan) for c in ("mid", "fech", "neg", "K")}
    sel = (di >= i0) & (di <= i1)
    for c, src in (("mid", "mid"), ("fech", "fech"), ("neg", "neg"), ("K", "K")):
        out[c][di[sel] - i0] = P[src][rows][sel]
    K = pd.Series(out["K"]).ffill().values
    out["K"] = np.where(np.isfinite(K), K, P["K"][rows][0])
    est["memo"][ch] = out
    return out


# =============================================================== simulação
def _simula(d, capital=20000, custo_mult=1, lag=0, alavancagem=1, livro="put", otm=.06, filtro="iv_alta", hedge=0.0,
            ativos="BOVA,PETR,VALE"):
    est = _estrutura(d)
    sp = d["spot"]
    dias = est["dias"]
    nD = len(dias)
    atv = [a.strip() for a in ativos.split(",") if a.strip() in ATIVOS]
    tipo = "P" if livro == "put" else "C"
    cdi = C.CDI.reindex(dias).fillna(0).values
    z = lambda: np.zeros(nD)
    opc, acoes, vendas, etf, rf, perd, isento = z(), z(), z(), z(), z(), z(), z()
    por_ativo = {a: z() for a in atv}           # P&L bruto do livro SEM filtro (1 contrato) -> placebo/atribuição
    ligado = {a: z() for a in atv}              # (colunas com o ticker do ativo-objeto, como em negocios["ativo"])
    lotes = {a: z() for a in atv}               # covered call: lotes de ação vigentes
    noc_dia = z()                               # nocional de strike vendido (garantia)
    negs = []
    S = {a: est["raizes"][a]["S"] for a in ATIVOS}
    bid_s = {a: sp[f"bid_{a}"].reindex(dias).values for a in atv}
    ask_s = {a: sp[f"ask_{a}"].reindex(dias).values for a in atv}
    liq_jcp = 1 - sp["ir_jcp"].reindex(dias).ffill().fillna(.15).values
    divs = {a: sp[f"div_{a}"].reindex(dias).fillna(0).values + liq_jcp * sp[f"jcp_{a}"].reindex(dias).fillna(0).values for a in atv}
    budget = capital * alavancagem / max(len(atv), 1)
    ciclos = {}
    for a in atv:
        for c in est["raizes"][a]["ciclos"].itertuples():
            ciclos.setdefault(c.i_ds, {})[a] = c
    cur_lotes = {a: 0 for a in atv}
    for i_ds in sorted(ciclos):
        i0 = i_ds + 1 + lag
        if i0 >= nD:
            continue
        esc = {}
        for a, c in ciclos[i_ds].items():
            if dias[i0] >= c.v or (a == "VALE" and dias[i0] < VALE_DESDE):
                continue
            S0 = S[a][i0]
            if not S0 == S0:
                continue
            j = _escolhe(est, a, c.v, i0, tipo, S0 * (1 - otm if tipo == "P" else 1 + otm))
            if j is None:
                continue
            P = est["raizes"][a]["porv"][c.v]
            K0, mid, bid = P["K"][j], P["mid"][j], P["bid"][j]
            T0, r0 = max(_du(dias[i0], c.v), 1) / 252, _r_aa(dias[i0])
            sig = est["memo"].setdefault(("iv", a, c.v, j), _iv(mid, S0, K0, T0, r0, tipo))
            if not (.05 < (sig if sig == sig else 0) < 2.0):
                continue
            on = True if filtro == "sempre" else bool(c.on_iv)
            esc[a] = dict(c=c, j=j, K0=K0, preco=mid - custo_mult * (mid - bid), sig=sig, S0=S0, on=on, T0=T0, r0=r0,
                          serie=P["nome"][j])
        # contratos inteiros só nos ativos ligados (o orçamento de um ativo desligado fica no CDI)
        liga = {a: e for a, e in esc.items() if e["on"]}
        noc = {a: (e["K0"] if livro == "put" else e["S0"]) * LOTE for a, e in liga.items()}
        n_all = _alocar(noc, budget, budget * len(noc)) if noc else {}
        if livro == "call":                                           # ações: alvo = alocação de todos os ativos com série (ligados ou não)
            noc_s = {a: e["S0"] * LOTE for a, e in esc.items()}
            n_acao = _alocar(noc_s, budget, budget * len(noc_s)) if noc_s else {}
            for a in atv:
                n_new = n_acao.get(a, cur_lotes[a]) if esc else cur_lotes[a]
                dn = n_new - cur_lotes[a]
                S0 = S[a][i0]
                if dn != 0 and S0 == S0:
                    px = ask_s[a][i0] if dn > 0 else bid_s[a][i0]
                    hs = min(abs(px / S0 - 1), .01) if (px == px and px > 0) else .0005
                    acoes[i0] -= abs(dn) * LOTE * S0 * (EMOL_VISTA + hs) * custo_mult
                    if dn < 0:
                        vendas[i0] += -dn * LOTE * S0
                cur_lotes[a] = n_new
                lotes[a][i0:] = n_new
            n_all = {a: min(n, int(cur_lotes[a])) for a, n in n_all.items()}   # 1 call por lote de ação
        delta_bova, fim_h = 0.0, None
        for a, e in esc.items():
            c = e["c"]
            fim_dados = c.i_v < 0
            i_v = nD - 1 if fim_dados else int(c.i_v)
            tr = _trilha(est, a, c.v, e["serie"], i0, i_v)
            St, Kt = S[a][i0:i_v + 1], tr["K"]
            St = pd.Series(St).ffill().values
            T = np.maximum(_du(dias[i0:i_v + 1], c.v), 1) / 252
            mod = _bs(St, Kt, T, e["r0"], e["sig"], tipo)[0]
            intr = np.maximum(St - Kt, 0) if tipo == "C" else np.maximum(Kt - St, 0)
            m = np.where(np.isfinite(tr["mid"]), tr["mid"], np.where((tr["neg"] > 0) & np.isfinite(tr["fech"]), tr["fech"], mod))
            m = np.maximum(np.where(np.isfinite(m), m, mod), intr)
            if not fim_dados:
                m[-1] = intr[-1]
            m[0] = e["preco"]
            dm = np.diff(m)
            por_ativo[a][i0 + 1:i_v + 1] += -LOTE * np.nan_to_num(dm) / capital
            n = n_all.get(a, 0)
            if not e["on"] or n == 0:
                continue
            q = LOTE * n
            ligado[a][i0 + 1:i_v + 1] = 1.0
            noc_dia[i0 + 1:i_v + 1] += q * e["K0"]
            c_ent = q * e["preco"] * EMOL_OPC * custo_mult
            opc[i0] -= c_ent
            opc[i0 + 1:i_v + 1] += -q * dm
            tot = -q * np.nansum(dm) - c_ent
            exerc = (not fim_dados) and intr[-1] > 0
            if exerc:
                K, Sv = Kt[-1], St[-1]
                c_ex = q * K * EMOL_VISTA * custo_mult
                opc[i_v] -= c_ex
                tot -= c_ex
                if tipo == "P" and i_v + 1 < nD:                     # recebo as ações ao strike e vendo no pregão seguinte, no bid
                    S1, b1 = S[a][i_v + 1], bid_s[a][i_v + 1]
                    px = S1 - custo_mult * (S1 - b1) if (b1 == b1 and b1 > 0) else S1
                    if px == px:
                        pnl1 = q * (px - Sv) - q * px * EMOL_VISTA * custo_mult
                        acoes[i_v + 1] += pnl1
                        vendas[i_v + 1] += q * px
                        perd[i_v + 1] += q * Sv * cdi[i_v + 1]
                        tot += pnl1 - q * Sv * cdi[i_v + 1]
                elif tipo == "C" and i_v + 1 < nD:                   # entrego ao strike (venda) e recompro no pregão seguinte
                    vendas[i_v] += q * K
                    c_rb = q * K * (EMOL_VISTA + .0005) * custo_mult
                    acoes[i_v + 1] -= c_rb
                    tot -= c_rb
            if livro == "put" and hedge > 0:
                b = est["beta"][i0, est["beta_col"][a]]
                delta = abs(float(_bs(e["S0"], e["K0"], e["T0"], e["r0"], e["sig"], "P")[1]))
                delta_bova += delta * q * e["S0"] * b
                fim_h = i_v if fim_h is None else min(fim_h, i_v)
            negs.append({"ativo": ATIVOS[a], "serie": e["serie"], "lado": -1, "entrada": dias[i0], "saida": dias[i_v], "dias": i_v - i0,
                         "retorno_%": tot / (q * e["S0"]) * 100, "contrib_pp": tot / capital * 100, "n_contratos": n,
                         "strike": e["K0"], "S0": e["S0"], "premio": e["preco"], "iv": e["sig"], "S_venc": St[-1], "K_venc": Kt[-1],
                         "exercido": bool(exerc)})
        # hedge de beta: BOVA11 vendido (aluguel PF), de d0 até o 1º vencimento; o dinheiro da venda rende CDI
        Pb = S["BOVA"]
        if livro == "put" and hedge > 0 and delta_bova > 0 and fim_h is not None and Pb[i0] == Pb[i0]:
            sh = np.floor(hedge * delta_bova / Pb[i0])
            if sh > 0:
                P = pd.Series(Pb[i0:fim_h + 1]).ffill().values
                pr = -sh * np.diff(P)
                c_h = (sh * P[0] * (EMOL_VISTA + .0005 + ALUG_ABRE) + sh * P[-1] * (EMOL_VISTA + .0005)
                       + sh * P[:-1].sum() * ALUG_DOADOR_AA / 252) * custo_mult
                ganho_cdi = sh * P[:-1] * cdi[i0 + 1:fim_h + 1]
                etf[i0 + 1:fim_h + 1] += pr
                etf[i0] -= c_h
                rf[i0 + 1:fim_h + 1] += ganho_cdi
                negs.append({"ativo": "BOVA11 (hedge alugado)", "lado": -1, "entrada": dias[i0], "saida": dias[fim_h],
                             "dias": fim_h - i0, "retorno_%": (pr.sum() - c_h) / (sh * P[0]) * 100,
                             "contrib_pp": (pr.sum() - c_h + ganho_cdi.sum()) / capital * 100})
    if livro == "call":
        for a in atv:
            nl = lotes[a]
            Sa = pd.Series(S[a]).ffill(limit=5).values
            q_prev = np.r_[0, nl[:-1]] * LOTE
            dS = np.r_[0, np.diff(Sa)]
            acoes += np.nan_to_num(q_prev * dS)
            isento += np.nan_to_num(q_prev * divs[a])
            perd += np.nan_to_num(q_prev * np.r_[np.nan, Sa[:-1]] * cdi)
            por_ativo[a] += np.nan_to_num(q_prev * (dS + divs[a])) / capital
            mud = np.flatnonzero(np.diff(np.r_[0, nl, 0]) != 0)
            for i, j in zip(mud[:-1], mud[1:]):
                if nl[i] == 0:
                    continue
                j = min(j, nD - 1)
                q = nl[i] * LOTE
                g = np.nansum(q * np.diff(Sa[i:j + 1])) + np.nansum(q * divs[a][i + 1:j + 1])
                cp = np.nansum(q * Sa[i:j] * cdi[i + 1:j + 1])
                negs.append({"ativo": ATIVOS[a], "serie": f"ação ({nl[i]:.0f} lotes)", "lado": 1, "entrada": dias[i], "saida": dias[j],
                             "dias": j - i, "retorno_%": g / (q * Sa[i]) * 100, "contrib_pp": (g - cp) / capital * 100})
    else:
        # custódia do Tesouro Selic usado como garantia: margem ~30% do nocional vendido; isento até R$ 10 mil
        rf -= np.maximum(.3 * noc_dia - ISENCAO_TD, 0) * CUSTODIA_TD_AA / 252 * custo_mult
    cls = {k: pd.Series(v, index=dias) for k, v in {"opcoes_b3": opc, "etf_b3": etf, "renda_fixa": rf, "isento": isento}.items()}
    cls.update(U.acoes_ir(pd.Series(acoes, index=dias), pd.Series(vendas, index=dias)))
    cls["_cdi_perdido"] = pd.Series(perd, index=dias)
    return {"classes": cls, "negocios": pd.DataFrame(negs), "por_ativo": pd.DataFrame(por_ativo, index=dias).rename(columns=ATIVOS),
            "ligado": pd.DataFrame(ligado, index=dias).rename(columns=ATIVOS)}


# =============================================================== interface do contrato
def excesso(d, capital=20000, custo_mult=1, lag=0, regime=REGIME, alavancagem=1, **params):
    p = {**PARAMS, **params}
    s = _simula(d, capital, custo_mult, lag, alavancagem, **p)
    cls = s["classes"]
    perd = cls.pop("_cdi_perdido")
    e = (sum(cls.values()) - perd) / capital
    e = e.reindex(C.DIAS).fillna(0)
    return C.aplica_regime(e, regime, CUSTO_TROCA * custo_mult)


def classes_ir(d, capital=20000, **params):
    p = {**PARAMS, **params}
    kw = {k: p.pop(k) for k in ("custo_mult", "lag", "alavancagem") if k in p}
    p.pop("regime", None)
    return _simula(d, capital, **kw, **p)["classes"]


def posicoes(d, capital=20000, **params):
    """W = 1 nos ciclos em que o filtro vendeu a opção do ativo (alinhado para C.carteira, que desloca 2 dias); R = P&L bruto diário
    do livro SEM filtro (1 contrato por ativo, fração do capital). O placebo mede se o filtro de IV acerta o timing."""
    p = {**PARAMS, **params}
    for k in ("custo_mult", "lag", "alavancagem", "regime"):
        p.pop(k, None)
    s = _simula(d, capital, **p)
    R = s["por_ativo"].reindex(C.DIAS).fillna(0)
    W = s["ligado"].reindex(C.DIAS).fillna(0).shift(-2).fillna(0)
    return W, R


def negocios(d, capital=20000, **params):
    p = {**PARAMS, **params}
    for k in ("custo_mult", "lag", "alavancagem", "regime"):
        p.pop(k, None)
    ng = _simula(d, capital, **p)["negocios"]
    return ng if len(ng) else pd.DataFrame(columns=["ativo", "lado", "entrada", "saida", "dias", "retorno_%", "contrib_pp"])


if __name__ == "__main__":
    import time
    d = carrega()
    for kw in ({}, {"filtro": "sempre"}, {"livro": "call", "ativos": "PETR,VALE", "otm": .10}):
        t = time.time()
        e = excesso(d, **kw)
        r = C.CDI + e
        print(kw, f"{time.time() - t:.1f}s", "IS", round(C.anual(r[(r.index >= INICIO) & (r.index < CORTE)]) - C.anual(C.CDI[(C.CDI.index >= INICIO) & (C.CDI.index < CORTE)]), 2),
              "OOS", round(C.anual(r[r.index >= CORTE]) - C.anual(C.CDI[C.CDI.index >= CORTE]), 2), "vol", round(e[e.index >= INICIO].std() * 252 ** .5 * 100, 2))
