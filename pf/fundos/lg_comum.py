"""
Peças comuns da frente "pf2_leilao_global": a NOITE (leilão de fechamento -> leilão de abertura) depois de um dia forte, fora da B3 ou em
outros ativos da B3. Não altera comum.py/robustez.py/pf.py.

Dados (pf/dados/pf2_leilao_global/, baixados uma vez por lg_baixar.py; aqui nada de internet):
  eua.parquet (ETFs EUA, S&P 100, ADRs brasileiros, ^VIX), small.parquet (S&P 600), europa.parquet (DAX/CAC/FTSE + UCITS),
  asia.parquet (Japão .T, Hong Kong .HK, Coreia .KS, Taiwan .TW), fx.parquet (EUR, GBP, JPY, HKD, KRW, TWD vs US$). Formato longo:
  data, ticker, O, H, L, C (ajustados por desdobramento), AC (ajustado por dividendo), V, div (provento na data ex).

HIPÓTESE DE EXECUÇÃO (leilão de fechamento): o sinal usa o retorno até o fechamento de t e a compra é feita NO PRÓPRIO leilão de
fechamento de t (lag=0). Na prática a ordem MOC/LOC tem prazo antes do fim do leilão (NYSE 15h50 ET, Nasdaq 15h55; Xetra/Euronext/LSE:
call de 5 min com preço indicativo público; Tóquio: call de fechamento 15h25-15h30 desde nov/2024, antes 15h00; HK: CAS 16h00-16h10);
o preço indicativo publicado na fase de call é o proxy do fechamento. Erro de seleção só na margem do limiar. O teste "t+2" da bateria
(lag=1: compra no fechamento SEGUINTE, como o fundo b3_leilao_noite_aud) é o limite conservador. Venda: ordem MOO no leilão de abertura de
t+1 (preço 'Open' do Yahoo = preço oficial de abertura). Nos EUA/Europa/Japão o Open do Yahoo é o leilão de abertura; dados antes de 2012
não são usados (abertura japonesa pré-2010 no Yahoo = fechamento anterior).

Noite = (abertura de t+1 + dividendo ex em t+1 x (1 - retenção)) / fechamento de t - 1; inválida se o papel não negociou em t+1, se a
abertura sai do intervalo [mín, máx] do dia ou se |noite| > 40% (erro de unidade/cadastro do Yahoo).

CONTA NA IBKR (só o necessário): conta de margem Reg T; posição de uma noite = capital x alavancagem; exigência inicial 50% => saldo na
IBKR = max(50% da posição planejada, US$ 2.000 de mínimo da conta de margem) x folga 1,1, revisto mês a mês (pf.custo_conta_exterior: CDI
perdido sobre o saldo, IOF+spread nas remessas, variação cambial do saldo). A outra metade é emprestada pela IBKR por 1 dia por noite
(liquidação T+1: a compra liquida em t+1, a venda em t+2) a T-bill + 1,5% a.a. (taxa de margem IBKR Pro para saldos < US$ 100 mil:
benchmark + 1,5%). O restante do capital fica em CDI no Brasil.

Custos de varejo por lado (IBKR Pro escalonado, out/2026; impostos de transação por país):
  EUA: US$ 0,0035/ação, mín. US$ 0,35, máx. 1% + taxa SEC/FINRA na venda (~0,3 bp); retenção de dividendo 30% (sem tratado BR-EUA)
  Alemanha/Holanda: 0,05% mín. € 1,25; França: idem + FTT na COMPRA (0,2% ago/2012-2016, 0,3% 2017-mar/2025, 0,4% desde abr/2025;
    empresas francesas > € 1 bi); Reino Unido: 0,05% mín. £ 1 + stamp duty 0,5% na compra (ações; ETFs isentos)
  Japão: 0,08% mín. ¥ 80, lote de 100 ações; Hong Kong: 0,08% mín. HK$ 18 + stamp 0,1% por lado (0,13% ago/2021-nov/2023) + taxas
    0,01%, lote por papel (tabela abaixo, aproximada); Coreia/Taiwan: a IBKR NÃO opera para não residentes -> só diagnóstico.
  Derrapagem no leilão: 1 bp por lado (como na auditoria do fundo da B3); small caps: meio spread estimado (Abdi-Ranaldo, só passado).
B3 (ETFs, BDRs, ações): emolumentos 0,03% por lado + 1 bp de derrapagem; dinheiro fora do CDI só na noite (como b3_leilao_noite_aud).
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

PF = Path(__file__).resolve().parent.parent
for _p in (str(PF), str(PF.parent)):
    if _p not in sys.path:
        sys.path.insert(0, _p)
import comum as C  # noqa: E402
import pf  # noqa: E402

DADOS = PF / "dados" / "pf2_leilao_global"
DIAS, CDI, PTAX = pf.DIAS, pf.CDI, pf.PTAX
SLIP = .0001
MARGEM_SPREAD = .015                 # IBKR Pro: benchmark + 1,5% a.a. (saldos < US$ 100 mil)
MIN_MARGEM_USD = 2000.0
_CACHE = {}

# moeda, retenção de dividendo, ordem de fechamento (UTC aproximado) para encadear as decisões no mesmo dia
MERC = {"US": ("USD", .30, 21), "DE": ("EUR", .26375, 16.5), "PA": ("EUR", .25, 16.5), "AS": ("EUR", .15, 16.5), "L": ("GBP", .0, 16.5),
        "T": ("JPY", .15315, 6.5), "HK": ("HKD", .0, 8.2), "KS": ("KRW", .22, 6.5), "TW": ("TWD", .21, 5.5), "B3": ("BRL", .0, 20)}
LOTE_HK = {"0700.HK": 100, "0005.HK": 400, "0939.HK": 1000, "1299.HK": 200, "0941.HK": 500, "1398.HK": 1000, "3988.HK": 1000,
           "0388.HK": 100, "0001.HK": 500, "0016.HK": 500, "0002.HK": 500, "0003.HK": 1000, "0011.HK": 100, "0027.HK": 1000,
           "0066.HK": 500, "0883.HK": 1000, "0386.HK": 2000, "0857.HK": 2000, "2318.HK": 500, "2628.HK": 1000, "0688.HK": 500,
           "1928.HK": 400, "0267.HK": 1000, "0762.HK": 2000, "9988.HK": 100, "3690.HK": 100, "1810.HK": 200, "0175.HK": 1000,
           "2020.HK": 200, "0006.HK": 500, "2388.HK": 500, "3968.HK": 500, "1038.HK": 500, "0012.HK": 1000, "1109.HK": 2000,
           "1113.HK": 500, "0669.HK": 500, "0981.HK": 500, "1211.HK": 500, "9618.HK": 50, "9999.HK": 100, "1024.HK": 100,
           "2331.HK": 500, "2269.HK": 500, "0960.HK": 500, "1093.HK": 2000, "2382.HK": 100, "9888.HK": 50, "9961.HK": 50}
SEM_FTT = {"AIR.PA", "STMPA.PA", "STLAP.PA", "ERF.PA", "MT.AS", "CAC.PA"}
ETF_UCITS = {"EXS1.DE", "ISF.L", "CAC.PA"}


def mercado(t):
    if t.endswith(".SA") or t[-1:].isdigit() and len(t) <= 6 and t[:4].isalpha():
        return "B3"
    s = t.rsplit(".", 1)[-1] if "." in t else "US"
    return s if s in MERC else "US"


def ler(nome):
    if nome not in _CACHE:
        x = pd.read_parquet(DADOS / f"{nome}.parquet")
        x["data"] = pd.to_datetime(x["data"])
        _CACHE[nome] = x[x["data"] <= DIAS[-1]]
    return _CACHE[nome]


def lista(nome):
    l = pd.read_csv(DADOS / "listas.csv")
    return l.loc[l["lista"] == nome, "ticker"].tolist()


def adr_b3():
    return pd.read_csv(DADOS / "adr_b3.csv", index_col=0)["b3"].to_dict()


def fx_usd():
    """US$ por 1 unidade de cada moeda, no calendário próprio (ffill)."""
    if "fx" not in _CACHE:
        f = ler("fx").pivot_table(index="data", columns="ticker", values="C", aggfunc="last").sort_index().ffill()
        f = f.where(f > 0)
        _CACHE["fx"] = pd.DataFrame({"EUR": f["EURUSD=X"], "GBP": f["GBPUSD=X"], "JPY": 1 / f["JPY=X"], "HKD": 1 / f["HKD=X"],
                                     "KRW": 1 / f["KRW=X"], "TWD": 1 / f["TWD=X"], "USD": 1.0}).ffill()
    return _CACHE["fx"]


def brl_por_local(idx, moeda):
    """R$ por unidade da moeda local em cada data `idx` (PTAX do último pregão B3 <= data x US$ por unidade)."""
    pt = PTAX.dropna()
    pt = pt.reindex(pt.index.union(idx)).ffill().reindex(idx)
    if moeda == "BRL":
        return pd.Series(1.0, index=idx)
    if moeda == "USD":
        return pt
    f = fx_usd()[moeda].dropna()
    f = f.reindex(f.index.union(idx)).ffill().reindex(idx)
    return pt * f


def no_b3(df, como="sum"):
    """DataFrame em datas de outro calendário -> pregão B3 >= data (agregando com soma ou máximo)."""
    pos = DIAS.searchsorted(df.index)
    ok = pos < len(DIAS)
    x = df[ok]
    x.index = DIAS[pos[ok]]
    x = x.groupby(level=0).agg(como)
    return x.reindex(DIAS).fillna(0)


def para_b3(s):
    """Valores (R$) em datas de outro calendário -> soma no 1º pregão da B3 >= data."""
    s = s.fillna(0).groupby(level=0).sum()
    acum = s.cumsum()
    return acum.reindex(DIAS.union(acum.index)).ffill().reindex(DIAS).fillna(0).diff().fillna(acum.reindex(DIAS).ffill().fillna(0))


# ---------------------------------------------------------------- painéis
def grupo(d, chave, tickers, min_cobertura=.3):
    """Matrizes (data x ticker) no calendário próprio do grupo (datas em que >= 30% dos papéis negociaram). Cache por id(d)."""
    k = (id(d), chave, tuple(tickers), min_cobertura)
    if k in _CACHE and _CACHE[k][0] is d[chave]:
        return _CACHE[k][1]
    x = d[chave]
    x = x[x["ticker"].isin(tickers)]
    out = {}
    for c in ("O", "H", "L", "C", "AC", "V", "div"):
        out[c] = x.pivot_table(index="data", columns="ticker", values=c, aggfunc="last").astype("float64")
    cols = [t for t in tickers if t in out["C"].columns]
    ok = out["C"].reindex(columns=cols).notna().mean(axis=1) >= min_cobertura
    idx = out["C"].index[ok.values]
    out = {c: v.reindex(index=idx, columns=cols) for c, v in out.items()}
    neg = (out["V"] > 0) & (out["O"] > 0) & (out["C"] > 0)            # sem volume = feriado/linha repetida do Yahoo
    if all(mercado(t) == "B3" for t in cols):
        neg = (out["O"] > 0) & (out["C"] > 0)
    for c in ("O", "H", "L", "C", "AC"):
        out[c] = out[c].where(neg)
    gbp = [t for t in cols if t.endswith(".L")]                        # Yahoo .L em pence
    for c in ("O", "H", "L", "C", "AC", "div"):
        out[c][gbp] = out[c][gbp] / 100
    out["div"] = out["div"].fillna(0)
    _CACHE[k] = (d[chave], out)
    if len([kk for kk in _CACHE if isinstance(kk, tuple)]) > 40:
        for kk in [kk for kk in _CACHE if isinstance(kk, tuple)][:20]:
            _CACHE.pop(kk)
    return out


def retorno(g):
    """Retorno total do dia (fechamento a fechamento, com dividendo), NaN se não negociou ontem/hoje; |r|>40% = erro -> NaN."""
    r = g["AC"] / g["AC"].shift(1) - 1
    return r.where(r.abs() < .4)


def noite(g, ret_div, teto=.4):
    """Noite que COMEÇA no fechamento de t (fica na linha t)."""
    O1, H1, L1 = g["O"].shift(-1), g["H"].shift(-1), g["L"].shift(-1)
    n = (O1 + g["div"].shift(-1) * (1 - ret_div)) / g["C"] - 1
    ok = (O1 <= H1 * 1.0001) & (O1 >= L1 * .9999) & (n.abs() < teto)
    return n.where(ok)


def meio_spread_ar(g, janela=60, piso=.0002, teto=.02):
    """Meio spread estimado (Abdi & Ranaldo 2017) com OHLC, média móvel só com o passado (conhecido no fechamento de t)."""
    c, eta = np.log(g["C"]), (np.log(g["H"]) + np.log(g["L"])) / 2
    termo = (c.shift(1) - eta.shift(1)) * (c.shift(1) - eta)
    s2 = 4 * termo.rolling(janela, min_periods=20).mean()
    return (np.sqrt(s2.clip(lower=0)) / 2).clip(piso, teto)


def adv_usd(g, moeda):
    pt = PTAX.dropna()
    f = brl_por_local(g["C"].index, moeda) / pt.reindex(pt.index.union(g["C"].index)).ffill().reindex(g["C"].index)
    return (g["V"] * g["C"]).fillna(0).rolling(60, min_periods=40).mean().mul(f, axis=0)


# ---------------------------------------------------------------- custos por lado (moeda local)
def comissao(val, preco, mkt):
    val = np.abs(val)
    if mkt == "US":
        return np.where(val > 0, np.clip(.0035 * val / np.maximum(preco, .01), .35, .01 * val), 0)
    piso, pct = {"DE": (1.25, .0005), "PA": (1.25, .0005), "AS": (1.25, .0005), "L": (1.0, .0005), "T": (80.0, .0008),
                 "HK": (18.0, .0008), "KS": (0, .0015), "TW": (0, .001425), "B3": (0, .0)}[mkt]
    return np.where(val > 0, np.maximum(pct * val, piso), 0)


def imposto(datas, tickers, mkt, lado_compra):
    """Imposto de transação por R$ negociado (DataFrame datas x tickers)."""
    z = pd.DataFrame(0.0, index=datas, columns=tickers)
    if mkt == "PA" and lado_compra:
        tx = pd.Series(np.select([datas < "2012-08-01", datas < "2017-01-01", datas < "2025-04-01"], [0, .002, .003], .004), index=datas)
        for t in tickers:
            if t not in SEM_FTT:
                z[t] = tx
    elif mkt == "L" and lado_compra:
        for t in tickers:
            if t not in ETF_UCITS:
                z[t] = .005
    elif mkt == "HK":
        z[:] = np.select([datas < "2021-08-01", datas < "2023-11-17"], [.001, .0013], .001)[:, None] + .0001
    elif mkt == "US" and not lado_compra:
        z[:] = .00003
    elif mkt == "KS" and not lado_compra:
        z[:] = .0025
    elif mkt == "TW" and not lado_compra:
        z[:] = .003
    elif mkt == "B3":
        z[:] = .0003
    return z


# ---------------------------------------------------------------- motor da noite
def noites(grupos, capital, n=3, lag=0, custo_mult=1.0, alavancagem=1.0, lado=1, spread=None):
    """grupos: lista de dicts {"g": painel, "mkt": código, "score": DataFrame (maior = melhor; NaN = não elegível), "lote": Series/escalar,
    "slip": escalar ou DataFrame de custo extra por lado}, NA ORDEM de fechamento (Ásia -> Europa -> EUA). Cada dia, até `n` noites no
    total: o grupo que fecha primeiro escolhe primeiro (decisão causal), os seguintes preenchem as vagas restantes.
    Sinal no fechamento de t; compra no fechamento de t+lag; venda na abertura seguinte. Ações INTEIRAS em lotes, capital*alav/n por papel.
    Devolve pnl_brl (Série no calendário B3), nocional_brl (datas da noite), negócios e W/R para o motor comum."""
    tam = capital * alavancagem / n
    usados = {}                                                        # data -> vagas usadas pelos grupos anteriores
    pnl_b3, noc_b3, ngs, Ws, Rs = [], [], [], [], []
    for G in grupos:
        g = G["g"]
        idx, cols = g["C"].index, g["C"].columns
        mk = pd.Series([G["mkt"] if isinstance(G.get("mkt"), str) else mercado(t) for t in cols], index=cols)
        moedas = {m: brl_por_local(idx, MERC[m][0]) for m in mk.unique()}
        fx = pd.concat({t: moedas[mk[t]] for t in cols}, axis=1)
        ret_div = pd.Series([MERC[m][1] for m in mk], index=cols)
        lote = G.get("lote", 1)
        lote = lote.reindex(cols).fillna(1).values if isinstance(lote, pd.Series) else np.full(len(cols), lote)
        nt = noite(g, ret_div, G.get("teto", .4))
        preco = g.get("PX", g["C"])                                     # preço para o tamanho (ações inteiras)
        cabe = np.floor(tam / (preco * fx * lote)) >= 1                  # dá para comprar 1 lote com capital/n
        s = G["score"].reindex(index=idx, columns=cols).where(cabe)
        vagas = pd.Series([n - usados.get(t, 0) for t in idx], index=idx)
        rk = s.rank(axis=1, ascending=False, method="first")
        sel = rk.le(vagas, axis=0) & s.notna()
        compra = sel.shift(lag).fillna(False).astype(bool) & preco.notna()
        qtd = (np.floor(tam / (preco * fx * lote)) * lote).where(compra, 0).fillna(0)
        val = qtd * preco                                               # moeda local
        val = val.where(nt.notna(), 0).fillna(0)
        for t, k in (val > 0).sum(axis=1).items():
            if k:
                usados[t] = usados.get(t, 0) + int(k)
        venda = val * (1 + nt.fillna(0))
        cm = custo_mult
        slip = G.get("slip", SLIP)
        custo = pd.DataFrame(0.0, index=idx, columns=cols)
        O1 = g["O"].shift(-1)
        for m in mk.unique():
            cc = list(mk.index[mk == m])
            custo[cc] = (comissao(val[cc].values, preco[cc].fillna(1).values, m) + comissao(venda[cc].values, O1[cc].fillna(1).values, m)
                         + val[cc].values * imposto(idx, cc, m, lado == 1).values + venda[cc].values * imposto(idx, cc, m, lado != 1).values)
        custo *= cm
        custo += (val + venda) * (slip if np.isscalar(slip) else slip.reindex(index=idx, columns=cols).fillna(.005)) * cm
        if lado == -1:                                                  # venda a descoberto de uma noite: aluguel ~0,3% a.a. (ETB)
            custo += val * .003 / 360
        bruto = lado * val * nt.fillna(0)
        liq = (bruto - custo) * fx                            # R$, na linha da ENTRADA (t)
        sai = pd.Series(idx[1:].append(pd.DatetimeIndex([idx[-1] + pd.Timedelta(days=1)])), index=idx)   # data da abertura de venda
        tot = liq.sum(axis=1)
        tot.index = sai.values
        pnl_b3.append(para_b3(tot))
        noc = (val * fx).sum(axis=1)
        noc.index = sai.values
        noc_b3.append(noc)
        ii, jj = np.nonzero(val.values > 0)
        ngs.append(pd.DataFrame({"ativo": np.asarray(cols)[jj], "lado": lado, "entrada": idx[ii], "saida": sai.values[ii], "dias": 1,
                                 "retorno_%": (liq.values[ii, jj] / (val.values[ii, jj] * fx.values[ii, jj])) * 100,
                                 "bruto_%": lado * nt.values[ii, jj] * 100,
                                 "contrib_pp": liq.values[ii, jj] / capital * 100, "valor_brl": val.values[ii, jj] * fx.values[ii, jj],
                                 "mercado": mk.values[jj]}))
        # W/R no calendário B3 para placebo/atribuição: peso no pregão B3 da saída, deslocado 2 (o motor comum executa em t+1, rende em t+2)
        wv = val * fx / capital
        wv.index = sai.values
        rv = (lado * nt).fillna(0)
        rv.index = sai.values
        Ws.append(no_b3(wv, "max").shift(-2).fillna(0))
        Rs.append(no_b3(rv, "sum"))
    W = pd.concat(Ws, axis=1)
    R = pd.concat(Rs, axis=1)
    W = W.T.groupby(level=0).sum().T
    R = R.T.groupby(level=0).sum().T
    W = W.loc[:, (W != 0).any()]
    R = R[W.columns]
    return {"pnl": sum(pnl_b3), "nocional": pd.concat(noc_b3).groupby(level=0).sum(), "negocios": pd.concat(ngs, ignore_index=True),
            "W": W, "R": R.sub(CDI, axis=0), "noc_grupos": noc_b3, "pnl_grupos": pnl_b3}


def excesso_ibkr(res, capital, alavancagem=1.0, custo_mult=1.0, nocional=None):
    """Excesso diário sobre o CDI (fração do capital) de uma estratégia de noites na IBKR (nocional: só a parte na IBKR, se misturada)."""
    res = res if nocional is None else {**res, "nocional": nocional}
    req = pd.Series(np.maximum(.5 * capital * alavancagem, MIN_MARGEM_USD * PTAX.values), index=DIAS)
    custo_conta, saldo = pf.custo_conta_exterior(req, folga=1.1)
    tb = C.TB_US.dropna()
    tb = tb.reindex(tb.index.union(res["nocional"].index)).ffill().reindex(res["nocional"].index).fillna(0)
    sd = saldo.reindex(saldo.index.union(res["nocional"].index)).ffill().reindex(res["nocional"].index).fillna(0)
    emprestado = (res["nocional"] - sd).clip(lower=0)                  # empréstimo de margem por 1 dia por noite
    juros = para_b3(emprestado * (tb * 252 + MARGEM_SPREAD) / 360 * custo_mult)
    e = (res["pnl"] - custo_conta - juros) / capital
    return e.reindex(DIAS).fillna(0), {"conta": custo_conta, "saldo": saldo, "juros": juros}


def excesso_b3(res, capital):
    """Noites na B3: o dinheiro só sai do CDI na noite (fica preso 1 dia útil)."""
    usado = para_b3(res["nocional"])
    return ((res["pnl"] - usado * CDI) / capital).reindex(DIAS).fillna(0), usado * CDI


# ---------------------------------------------------------------- sinais
def score_queda(g, limiar, modo="rel", liq=None):
    """Quanto mais caiu (retorno do dia, absoluto ou relativo à média do universo líquido), maior o score; só se cair >= limiar."""
    r = retorno(g)
    if liq is not None:
        r = r.where(liq)
    x = r.sub(r.mean(axis=1), axis=0) if modo == "rel" else r
    return (-x).where(x <= -limiar)


def score_alta(g, limiar, modo="rel", liq=None):
    r = retorno(g)
    if liq is not None:
        r = r.where(liq)
    x = r.sub(r.mean(axis=1), axis=0) if modo == "rel" else r
    return x.where(x >= limiar)


# ---------------------------------------------------------------- interface do contrato (excesso, classes_ir, posicoes, negocios)
def interface(roda, PARAMS, REGIME="nenhum", CUSTO_TROCA=.001):
    """roda(d, capital, custo_mult, lag, alavancagem, **params) -> dict com 'e' (excesso no calendário B3), 'pnl_classe' (R$ do ativo,
    sem o CDI), 'cdi_perdido' (R$), 'W', 'R', 'negocios'. Devolve as funções do contrato com cache."""
    cache = {}

    def _r(d, capital=20000, custo_mult=1, lag=0, alavancagem=1, **params):
        p = {**PARAMS, **params}
        k = (id(d), capital, custo_mult, lag, alavancagem, tuple(sorted(p.items())))
        if k in cache and cache[k][0] is d:
            return cache[k][1]
        r = roda(d, capital=capital, custo_mult=custo_mult, lag=lag, alavancagem=alavancagem, **p)
        if len(cache) > 48:
            cache.clear()
        cache[k] = (d, r)
        return r

    def excesso(d, capital=20000, custo_mult=1, lag=0, regime=REGIME, alavancagem=1, **params):
        e = _r(d, capital, custo_mult, lag, alavancagem, **params)["e"]
        return C.aplica_regime(e, regime, CUSTO_TROCA * custo_mult)

    def classes_ir(d, capital=20000, **params):
        r = _r(d, capital, **params)
        return {r.get("classe", "exterior"): r["pnl_classe"], "_cdi_perdido": r["cdi_perdido"]}

    def posicoes(d, capital=20000, **params):
        r = _r(d, capital, **params)
        return r["W"], r["R"]

    def negocios(d, capital=20000, **params):
        return _r(d, capital, **params)["negocios"]

    return excesso, classes_ir, posicoes, negocios, _r


def roda_ibkr(grupos, capital, n, lag, custo_mult, alavancagem, lado=1):
    res = noites(grupos, capital, n, lag, custo_mult, alavancagem, lado)
    e, x = excesso_ibkr(res, capital, alavancagem, custo_mult)
    # conta exterior: o custo da conta (CDI perdido + remessas - câmbio) entra inteiro no excesso; para o IR, o ganho da classe é o P&L
    # das noites menos juros de margem e remessas (o CDI perdido é custo de oportunidade, não despesa dedutível)
    res.update({"e": e, "pnl_classe": res["pnl"] - x["juros"] - x["conta"], "cdi_perdido": pd.Series(0.0, index=DIAS),
                "conta": x["conta"], "juros": x["juros"], "saldo": x["saldo"], "classe": "exterior"})
    return res


def roda_b3(grupos, capital, n, lag, custo_mult, alavancagem, classe="etf_b3"):
    res = noites(grupos, capital, n, lag, custo_mult, alavancagem)
    e, cdi_p = excesso_b3(res, capital)
    res.update({"e": e, "pnl_classe": res["pnl"], "cdi_perdido": cdi_p, "classe": classe})
    return res


def vix_ontem(d, idx, chave="eua"):
    """VIX de fechamento do último pregão americano ANTERIOR à data (o VIX de t fecha 16h15 ET, depois do MOC)."""
    v = d[chave]
    v = v[v["ticker"] == "^VIX"].set_index("data")["C"].astype(float).sort_index()
    v.index = v.index + pd.Timedelta(days=1)
    return v.reindex(v.index.union(idx)).ffill().reindex(idx)
