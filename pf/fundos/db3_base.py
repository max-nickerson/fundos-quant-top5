"""
Peças comuns da frente "deriv_b3" (pf/fundos/db3_*.py): derivativos da B3 para pessoa física, garantia em Tesouro Selic (rende CDI).
Não altera comum.py / robustez.py / pf.py. Lê os dados brutos já baixados (quant/fundos/dados e quant/dados), sem internet.

Convenções:
  - todo dado entra no dict `d` de carrega() como DataFrame com coluna "data" ou índice de datas (o teste de truncamento corta tudo);
  - excesso = P&L em R$ / capital (caixa e garantia em Tesouro Selic = CDI = benchmark; só o que sai do CDI paga custo de oportunidade);
  - contratos/lotes INTEIROS; decisão no fechamento de t, execução no fechamento de t+1+lag;
  - caches internos são indexados pelo id() do DataFrame recebido (dados cortados = objeto novo = recálculo; sem vazamento entre testes).

Premissas de custo de varejo (corretagem zero em Clear/Rico/Inter; o resto é real), out/2026:
  - opções B3: emolumentos + registro ~0,10% do prêmio por lado (tabela B3 de opções sobre ações para PF ~0,037%–0,05% + ISS/
    taxa de registro; arredondado para cima); execução no bid/ask do COTAHIST (melhor oferta de fechamento) — custo_mult = 1 agride a
    melhor oferta, 2 paga o dobro da distância do meio;
  - exercício: compra/venda do ativo ao strike + desmontagem no pregão seguinte: 0,03% x 2 de emolumentos + 0,08% de meio spread;
  - WDO: R$ 4,00 por contrato por lado (emolumentos ~R$ 1,0 + meio tick de 0,5 pt = R$ 2,50 + registro) — mesmo valor de
    varejo/fundos/carry_moedas_varejo.py; WIN: R$ 1,10 por lado (emolumentos ~R$ 0,25–0,60 + meio tick de 5 pts = R$ 0,50);
    CCM: R$ 1,50 de emolumentos (pf.CONTRATOS) + meio tick (R$ 0,01/saca x 450 = R$ 4,50) = R$ 6,00 por lado.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import brentq
from scipy.stats import norm

PF = Path(__file__).resolve().parent.parent
RAIZ = PF.parent
for p in (str(RAIZ), str(PF)):
    if p not in sys.path:
        sys.path.insert(0, p)

import comum as C  # noqa: E402
import pf as P  # noqa: E402

QUANT = RAIZ.parent
FD = QUANT / "fundos" / "dados"
QD = QUANT / "dados"
DIAS, CDI = C.DIAS, C.CDI
CDI_AA = (1 + CDI) ** 252 - 1

CUSTO_OPC = .001              # fração do prêmio por lado
CUSTO_EXERC = .0014           # fração do nocional do ativo no exercício (comprar/vender e desmontar)
CUSTO_ACAO = P.B3_EMOL + P.B3_SPREAD["liquida"]          # por lado, lote padrão
SPOT = {"PETR": "PETR4", "VALE": "VALE3", "ITUB": "ITUB4", "BOVA": "BOVA11"}

_CACHE = {}


def memo(chave, obj, f):
    """Cache por id(obj) (mantém a referência viva para o id não ser reaproveitado)."""
    k = (chave, id(obj))
    if k not in _CACHE:
        _CACHE[k] = (obj, f())
    return _CACHE[k][1]


def limpa_cache():
    _CACHE.clear()


# ================================================================ dados brutos
def opcoes(raizes):
    """Opções MENSAIS (sem semanais) das raízes, 2014+, com bid/ask/meio limpos (cálculo linha a linha, sem olhar o futuro)."""
    o = pd.read_parquet(FD / "b3_opcoes.parquet", filters=[("raiz", "in", list(raizes))])
    o = o[(o.strike > 0) & o.venc.notna() & ~o.serie.str.contains("W")]
    bid, ask = o.oferta_compra.where(o.oferta_compra > 0), o.oferta_venda.where(o.oferta_venda > 0)
    ask = ask.where(ask >= bid.fillna(0))
    sano = (ask - bid) <= .5 * (ask + bid) / 2 + .05                 # oferta absurda (venda a 99,99) não marca
    o = o.assign(bid=bid, ask=ask, mid=((bid + ask) / 2).where(sano).fillna(o.fech.where(o.negocios > 0)),
                 spr=((ask - bid) / ((ask + bid) / 2)).where(bid.notna() & ask.notna()))
    return o[["data", "serie", "raiz", "tipo", "strike", "venc", "bid", "ask", "mid", "spr", "fech", "volume"]].reset_index(drop=True)


def acoes(tickers=("PETR4", "VALE3", "ITUB4", "BOVA11")):
    """Fechamento BRUTO (sem ajuste, o mesmo em que o strike das opções é definido) + proventos e grupamentos/bonificações (Yahoo).
    Devolve DataFrame longo: data, ticker, fech, div, split. BOVA11 não está no COTAHIST filtrado (codbdi 14): vem do Yahoo (bruto)."""
    c = pd.read_parquet(FD / "b3_acoes_cotahist.parquet", filters=[("ticker", "in", list(tickers))], columns=["data", "ticker", "fech"])
    y = pd.read_parquet(FD / "y_proventos.parquet", filters=[("ticker", "in", list(tickers))])
    n_c, n_y = c.ticker.value_counts(), y.ticker.value_counts()
    fraco = [t for t in n_y.index if n_c.get(t, 0) < .8 * n_y[t]]          # BOVA11: só 92 dias no COTAHIST filtrado
    c = pd.concat([c[~c.ticker.isin(fraco)], y[y.ticker.isin(fraco)][["data", "ticker", "close"]].rename(columns={"close": "fech"})],
                  ignore_index=True)
    out = c.merge(y[["data", "ticker", "div", "split"]], on=["data", "ticker"], how="left").fillna({"div": 0.0, "split": 0.0})
    return out.sort_values(["ticker", "data"]).reset_index(drop=True)


def painel_acoes(a):
    """(S, R): preço bruto e retorno TOTAL diário (proventos e bonificações), colunas = raiz (PETR, VALE...), calendário B3."""
    inv = {v: k for k, v in SPOT.items()}
    a = a[a.ticker.isin(inv)]
    S = a.pivot_table(index="data", columns="ticker", values="fech").rename(columns=inv)
    dv = a.pivot_table(index="data", columns="ticker", values="div").rename(columns=inv).reindex(S.index).fillna(0)
    sp = a.pivot_table(index="data", columns="ticker", values="split").rename(columns=inv).reindex(S.index).fillna(0)
    sp = sp.where(sp > 0, 1.0)
    R = (S * sp + dv) / S.shift(1) - 1
    R = R.where(R.abs() < .4)                                        # erro de cotação (não há queda de 40% num dia nessas 4)
    S = S.reindex(DIAS).ffill(limit=5)
    return S, R.reindex(DIAS).fillna(0)


def futuros(prefixos, arquivo="fin"):
    """Ajustes diários de futuros B3: data, ticker, ajuste, ajuste_ant, oi, taxa (deduplicado: há linhas repetidas e linhas sem ajuste)."""
    f = QD / "futuros.parquet" if arquivo == "fin" else FD / "b3_futuros_agro.parquet"
    x = pd.read_parquet(f)
    x = x[x.ticker.str[:3].isin(prefixos)].dropna(subset=["AdjstdQt"])
    x = x.sort_values(["date", "ticker", "OpnIntrst"]).groupby(["date", "ticker"], as_index=False).last()
    out = x.rename(columns={"date": "data", "AdjstdQt": "ajuste", "PrvsAdjstdQt": "ajuste_ant", "OpnIntrst": "oi"})
    cols = ["data", "ticker", "ajuste", "ajuste_ant", "oi"] + (["taxa"] if "AdjstdQtTax" in x else [])
    if "AdjstdQtTax" in x:
        out["taxa"] = x["AdjstdQtTax"].values
    return out[cols].reset_index(drop=True)


def yahoo_idx(cols=("^BVSP", "^VIX")):
    y = pd.read_parquet(FD / "y_idx.parquet", columns=list(cols))
    y.index = pd.DatetimeIndex(y.index).normalize()
    return y[~y.index.duplicated(keep="last")].sort_index()


def selic_meta():
    s = pd.read_parquet(FD / "sgs_432.parquet")
    s.index = pd.DatetimeIndex(s.index)
    return s.iloc[:, 0].rename("selic")


def focus_ipca12m():
    f = pd.read_parquet(FD / "focus_ipca12m.parquet")
    return f.assign(Data=pd.to_datetime(f.Data)).groupby("Data").Mediana.last().rename("ipca12m")


def cftc(nome, campo="lev"):
    """Posição líquida dos especuladores / OI, por DATA DE DIVULGAÇÃO (relatório de terça sai na sexta: +3 dias corridos)."""
    c = pd.read_parquet(FD / "cot.parquet")
    c = c[c.Market_and_Exchange_Names.str.startswith(nome)].dropna(subset=["Report_Date_as_YYYY-MM-DD"])
    lg, sh = ("Lev_Money_Positions_Long_All", "Lev_Money_Positions_Short_All") if campo == "lev" else \
        ("M_Money_Positions_Long_All", "M_Money_Positions_Short_All")
    c = c.assign(data=pd.to_datetime(c["Report_Date_as_YYYY-MM-DD"]) + pd.Timedelta(days=3),
                 liq=(c[lg] - c[sh]) / c.Open_Interest_All)
    return c.groupby("data").liq.last()


# ================================================================ calendário de vencimentos
def vencimento_wdo(ticker):
    """WDO/DOL vence no 1º dia útil do mês do contrato."""
    m = "FGHJKMNQUVXZ".index(ticker[3]) + 1
    a = 2000 + int(ticker[4:6])
    return DIAS[DIAS >= pd.Timestamp(a, m, 1)][0] if (DIAS >= pd.Timestamp(a, m, 1)).any() else pd.Timestamp(a, m, 1)


def mes_contrato(ticker):
    return pd.Timestamp(2000 + int(ticker[4:6]), "FGHJKMNQUVXZ".index(ticker[3]) + 1, 1)


def serie_rolada(f, venc_de, antes=3, oi_min=0):
    """Contrato a carregar em cada pregão: o de vencimento mais próximo que vence a mais de `antes` pregões (rola `antes` pregões antes).
    Devolve DataFrame por data: ticker, ajuste, dP (variação do ajuste do MESMO contrato entre t-1 e t), troca (1 se rolou em t),
    ajuste do 2º contrato (para a inclinação da curva) e dias úteis entre os dois."""
    f = f[f.oi.fillna(0) >= oi_min] if oi_min else f
    tk = pd.Series(f.ticker.unique())
    venc = pd.Series([venc_de(t) for t in tk], index=tk)
    f = f[f.data.isin(DIAS)].assign(v=lambda x: x.ticker.map(venc))
    f = f.assign(faltam=np.busday_count(f.data.values.astype("datetime64[D]"), f.v.values.astype("datetime64[D]")))  # dias úteis (sem feriados)
    elegivel = f[f.faltam > antes].sort_values(["data", "v"])
    g = elegivel.groupby("data")
    p1 = g.nth(0).set_index("data")
    p2 = g.nth(1).set_index("data")
    out = pd.DataFrame({"ticker": p1.ticker, "ajuste": p1.ajuste, "venc": p1.v, "faltam": p1.faltam,
                        "ticker2": p2.ticker.reindex(p1.index), "ajuste2": p2.ajuste.reindex(p1.index),
                        "faltam2": p2.faltam.reindex(p1.index)})
    # variação do contrato carregado ONTEM (o que eu tinha) entre t-1 e t
    aj = f.pivot_table(index="data", columns="ticker", values="ajuste")
    tk_ontem = out.ticker.shift(1)
    dP = []
    for d, t in tk_ontem.items():
        if isinstance(t, str) and t in aj.columns:
            i = aj.index.get_loc(d)
            a1, a0 = aj[t].iloc[i], aj[t].iloc[i - 1] if i > 0 else np.nan
            dP.append(a1 - a0)
        else:
            dP.append(np.nan)
    out["dP"] = pd.Series(dP, index=out.index).fillna(0)
    out["troca"] = (out.ticker != tk_ontem).astype(int)
    out.iloc[0, out.columns.get_loc("troca")] = 0
    return out.reindex(DIAS)


# ================================================================ Black-Scholes
def bs(S, K, T, r, s, tipo):
    s, T = max(s, 1e-4), max(T, 1 / 252)
    d1 = (np.log(S / K) + (r + s * s / 2) * T) / (s * np.sqrt(T))
    d2 = d1 - s * np.sqrt(T)
    if tipo == "C":
        return S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
    return K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)


def iv(p, S, K, T, r, tipo):
    intr = max(S - K * np.exp(-r * T), 0) if tipo == "C" else max(K * np.exp(-r * T) - S, 0)
    if not (np.isfinite(p) and p > intr + 1e-6):
        return np.nan
    try:
        return brentq(lambda s: bs(S, K, T, r, s, tipo) - p, 1e-3, 5.0, xtol=1e-5)
    except ValueError:
        return np.nan


def du(a, b):
    return int(np.busday_count(np.datetime64(a, "D"), np.datetime64(b, "D")))


# ================================================================ motor de ciclos de opções (1 mês, segura até o vencimento)
def _por_venc(o):
    """dict (raiz, venc) -> opções daquele vencimento; e lista de vencimentos mensais por raiz."""
    def f():
        g = {k: x.sort_values("data") for k, x in o.groupby(["raiz", "venc"])}
        vs = {r: sorted(o[o.raiz == r].venc.unique()) for r in o.raiz.unique()}
        return g, vs
    return memo("porvenc", o, f)


def sinais_ciclos(d, raiz):
    """Um ciclo por vencimento mensal: sinal no 1º pregão após o vencimento anterior (ds), alvo = próximo vencimento (v).
    IV ATM (meio, BS com CDI), RV 21d (retorno total), skew (IV put 90% - ATM), tendência (preço / média de 100d). Só dados até ds."""
    o, S, R = d["opc"], d["S"], d["R"]

    def f():
        g, vs = _por_venc(o)
        vs = [pd.Timestamp(v) for v in vs.get(raiz, [])]
        out = []
        for v0, v1 in zip(vs[:-1], vs[1:]):
            dd = DIAS[(DIAS > v0) & (DIAS < v1)]
            if len(dd) < 8 or raiz not in S or not np.isfinite(S[raiz].get(dd[0], np.nan)):
                continue
            ds = dd[0]
            x = g.get((raiz, v1))
            if x is None:
                continue
            x = x[x.data == ds]
            S0 = S[raiz][ds]
            T, r = max(du(ds, v1), 1) / 252, np.log1p(CDI_AA.get(ds, .1))
            ivs = []
            for tp in ("C", "P"):
                y = x[(x.tipo == tp) & x.mid.notna()]
                if len(y):
                    z = y.iloc[(y.strike - S0).abs().argsort().iloc[0]]
                    if abs(z.strike / S0 - 1) < .05:
                        ivs.append(iv(z.mid, S0, z.strike, T, r, tp))
            ivs = [a for a in ivs if a == a]
            a = np.mean(ivs) if ivs else np.nan
            y = x[(x.tipo == "P") & x.mid.notna()]
            sk = np.nan
            if len(y) and a == a:
                z = y.iloc[(y.strike - .9 * S0).abs().argsort().iloc[0]]
                if abs(z.strike / S0 - .9) < .03:
                    sk = iv(z.mid, S0, z.strike, T, r, "P") - a
            rv = R[raiz].loc[:ds].tail(21).std() * np.sqrt(252)
            mm = S[raiz].loc[:ds].dropna().tail(100)
            tend = S0 / mm.mean() - 1 if len(mm) >= 80 else np.nan
            out.append(dict(raiz=raiz, ds=ds, v=v1, S0=S0, iv=a, rv=rv, skew=sk, tend=tend))
        c = pd.DataFrame(out)
        if len(c):
            c["iv_rv"] = c.iv - c.rv
            c["iv_med"] = c.iv.rolling(12, min_periods=6).median().shift(1)
        return c
    return memo(("sinais", raiz), o, f)


def perna(d, raiz, v, d0, k_alvo, tipo, lado, custo_mult=1.0, spr_max=.25):
    """Uma opção de um ciclo: escolhida em d0 (dia da execução) com strike mais perto de k_alvo e oferta do lado a agredir (spread <=
    spr_max do meio). Marca no meio (parado se não negociou; nunca abaixo do intrínseco nem acima do teto), vale o intrínseco no
    vencimento. Devolve dict com série de marcação por ação (calendário d0..v), preço de entrada, strike e série; ou None."""
    o, S = d["opc"], d["S"]
    g, _ = _por_venc(o)
    x = g.get((raiz, v))
    if x is None:
        return None
    dia = x[(x.data == d0) & (x.tipo == tipo)]
    col = "bid" if lado < 0 else "ask"
    dia = dia[dia[col].notna() & (dia.spr <= spr_max)]
    if dia.empty:
        return None
    S0 = S[raiz].get(d0, np.nan)
    # série de outra classe na mesma raiz (VALE5, PETR3...): preço viola o intrínseco do NOSSO ativo -> descarta (só dados até d0)
    viol = dia.mid.fillna(dia[col]) < np.where(tipo == "C", S0 - dia.strike, dia.strike - S0) - .03 * S0
    dia = dia[~viol.values]
    if dia.empty:
        return None
    z = dia.iloc[(dia.strike - k_alvo).abs().argsort().iloc[0]]
    meio = z.mid if z.mid == z.mid else z[col]
    preco = meio - custo_mult * (meio - z[col])
    dias = DIAS[(DIAS >= d0) & (DIAS <= v)]
    h = x[x.serie == z.serie].drop_duplicates("data").set_index("data")
    St = S[raiz].reindex(dias).ffill()
    Kt = h.strike.reindex(dias).ffill().fillna(z.strike)               # strike é ajustado por proventos ao longo da vida
    mk = h.mid.reindex(dias).ffill()
    intr = (St - Kt).clip(lower=0) if tipo == "C" else (Kt - St).clip(lower=0)
    teto = St if tipo == "C" else Kt
    mk = np.minimum(np.maximum(mk.fillna(intr), intr), teto)
    mk.iloc[0] = preco
    vencida = dias[-1] == pd.Timestamp(v) and np.isfinite(S[raiz].get(dias[-1], np.nan))
    if vencida:                                                        # no vencimento vale o intrínseco; posição ainda aberta no
        mk.iloc[-1] = intr.iloc[-1]                                    # fim dos dados fica marcada no meio
    return dict(serie=z.serie, K=float(z.strike), preco=float(preco), meio=float(meio), mk=mk, intr_fim=float(intr.iloc[-1]) if vencida else 0.0,
                S0=float(S0), ST=float(St.iloc[-1]), custo_mult=custo_mult)


def pnl_pernas(pernas, lotes, lado_por_perna, custo_mult=1.0, lote=100):
    """P&L diário em R$ de uma estrutura (lista de pernas com o mesmo calendário). lado: -1 vendido, +1 comprado."""
    pnl = None
    for p, sg in zip(pernas, lado_por_perna):
        q = lotes * lote
        x = sg * q * p["mk"].diff().fillna(0)
        x.iloc[0] -= q * p["preco"] * CUSTO_OPC * custo_mult
        if p["intr_fim"] > 0:
            x.iloc[-1] -= q * p["ST"] * CUSTO_EXERC * custo_mult
        pnl = x if pnl is None else pnl.add(x, fill_value=0)
    return pnl


# ================================================================ utilidades de saída
def negocios_df(linhas, capital):
    ng = pd.DataFrame(linhas)
    if ng.empty:
        return pd.DataFrame(columns=["ativo", "lado", "entrada", "saida", "dias", "retorno_%", "contrib_pp"])
    ng["contrib_pp"] = ng["pnl_rs"] / capital * 100
    ng["dias"] = [du(a, b) for a, b in zip(ng.entrada, ng.saida)]
    return ng


def wr_de_pnl(pnl_por_ativo, capital, lag_exec=2):
    """Para placebo/atribuição da robustez: W (decidido em t) e R tais que comum.carteira(W, R, 0) = P&L / capital.
    W_exec = 1 quando há posição; R = P&L do dia / capital. W = W_exec deslocado lag_exec dias para trás."""
    Pn = pd.DataFrame(pnl_por_ativo).reindex(DIAS).fillna(0) / capital
    We = (Pn != 0).astype(float)
    return We.shift(-lag_exec).fillna(0), Pn


def fecha(e, regime, custo_troca, custo_mult):
    return C.aplica_regime(e.reindex(DIAS).fillna(0), regime, custo_troca * custo_mult)


# ================================================================ motor de futuros (contratos inteiros, série rolada sem saltos)
def livro_futuro(n, sr, mult, custo_lado, lag=0, custo_mult=1.0, fx=None):
    """n: contratos decididos no fechamento de t (sinal +/-). Executa em t+1+lag (como pf.pnl_futuro); rende a partir do dia seguinte.
    sr: serie_rolada (dP = variação do contrato que eu carregava ontem; troca = rolagem em t). fx: multiplicador de câmbio (USD).
    Rolagem = zera o contrato velho e abre o novo (2 lados por contrato). Devolve (pnl_rs, n_exec, custo_rs)."""
    fx = pd.Series(1.0, index=DIAS) if fx is None else fx.reindex(DIAS).ffill()
    ne = n.reindex(DIAS).fillna(0).shift(1 + lag).fillna(0)
    bruto = ne.shift(1).fillna(0) * sr.dP.reindex(DIAS).fillna(0) * mult * fx
    giro = ne.diff().abs().fillna(ne.abs()) + 2 * ne.abs() * sr.troca.reindex(DIAS).fillna(0) * (ne.shift(1).fillna(0) != 0)
    custo = giro * custo_lado * custo_mult
    return bruto - custo, ne, custo


def blocos(ne, pnl, ativo, capital, nocional=None, quebra=None):
    """Negócios = trechos contínuos em que a posição de ONTEM (a que gera o P&L de hoje) tem o mesmo lado; inclui o custo de entrada."""
    lp = np.sign(ne.shift(1).fillna(0))
    chave = lp if quebra is None else lp.astype(str) + "|" + quebra.shift(1).reindex(lp.index).astype(str)  # quebra = contrato (rolagem)
    grp = (chave != chave.shift(1)).cumsum()
    out = []
    for _, g in pnl.groupby(grp):
        s = lp.reindex(g.index)
        if s.iloc[0] == 0:
            continue
        ant = DIAS[DIAS < g.index[0]][-1:]                                # dia da execução (custo de entrada)
        x = pnl.reindex(ant.union(g.index)).fillna(0) if len(ant) and lp.get(ant[0], 0) == 0 else g
        noc = float(nocional.reindex(g.index).mean()) if nocional is not None else capital
        out.append(dict(ativo=ativo, lado=int(s.iloc[0]), entrada=x.index[0], saida=g.index[-1],
                        contratos=float(ne.shift(1).reindex(g.index).abs().mean()), pnl_rs=float(x.sum()),
                        **{"retorno_%": float(x.sum() / noc * 100) if noc else np.nan}))
    return out


def wr_futuro(ne, nocional, ret, capital, ativo):
    """W (decidido em t) e R para placebo/atribuição: W = n x nocional / capital (sinal), R = retorno do contrato carregado."""
    W = (ne * nocional / capital).shift(-2).fillna(0).to_frame(ativo)
    return W, ret.reindex(DIAS).fillna(0).to_frame(ativo)
