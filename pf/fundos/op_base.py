"""
Peças comuns da frente "pf2_opcoes" (pf/fundos/op_*.py): opções que uma pessoa física consegue montar com R$ 20–50 mil, com risco
DEFINIDO (travas), garantia em Tesouro Selic na B3 (rende CDI = benchmark) e, fora do Brasil, só a margem na IBKR.
Reaproveita o motor de opções da frente deriv_b3 (db3_base.py: Black-Scholes, IV, custos de varejo) e acrescenta:
  - painel de ações para os 24 ativos-objeto com opções no COTAHIST (b3_opcoes.parquet, bid/ask do fechamento, 2014+);
  - índice rápido (raiz, vencimento, dia) -> linhas, para montar milhares de pernas por rodada da bateria;
  - perna com SAÍDA antes do vencimento (eventos: entra na véspera, sai no dia seguinte, no bid/ask);
  - sinais por ciclo mensal para qualquer raiz (IV ATM, vol realizada, tendência, skew).
Não altera comum.py / robustez.py / pf.py. Caches por id() do DataFrame (dado cortado = recálculo; sem vazamento no truncamento).

Premissas de custo (mesmas de db3_base, fonte: tabela de tarifas B3 para PF, out/2026):
  - opção: ~0,10% do prêmio por lado de emolumentos/registro + agressão do bid (venda) / ask (compra) do fechamento;
    custo_mult = 2 paga o dobro da distância do meio;
  - exercício: 0,14% do nocional (compra/venda do ativo ao strike + desmontagem no pregão seguinte).
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

AQUI = Path(__file__).resolve().parent
if str(AQUI) not in sys.path:
    sys.path.insert(0, str(AQUI))
import db3_base as B  # noqa: E402

C, P = B.C, B.P
DIAS, CDI, CDI_AA = B.DIAS, B.CDI, B.CDI_AA
bs, iv, du, memo, fecha, negocios_df, wr_de_pnl = B.bs, B.iv, B.du, B.memo, B.fecha, B.negocios_df, B.wr_de_pnl
CUSTO_OPC, CUSTO_EXERC = B.CUSTO_OPC, B.CUSTO_EXERC
FD, QD = B.FD, B.QD
DADOS = AQUI.parent / "dados" / "pf2_opcoes"

# raiz das opções no COTAHIST -> ação/ETF-objeto (IBOV = opção de índice: fora, quase sem oferta)
TICKER = {"ABEV": "ABEV3", "B3SA": "B3SA3", "BBAS": "BBAS3", "BBDC": "BBDC4", "BOVA": "BOVA11", "BPAC": "BPAC11", "COGN": "COGN3",
          "CSNA": "CSNA3", "GGBR": "GGBR4", "ITSA": "ITSA4", "ITUB": "ITUB4", "JBSS": "JBSS3", "LREN": "LREN3", "MGLU": "MGLU3",
          "PETR": "PETR4", "PRIO": "PRIO3", "RENT": "RENT3", "SMAL": "SMAL11", "SUZB": "SUZB3", "USIM": "USIM5", "VALE": "VALE3",
          "VIIA": "VIIA3", "VVAR": "VVAR3", "WEGE": "WEGE3"}
# antes de 2018 a raiz VALE misturava VALE3 e VALE5 (rev_opcoes_b3): só usamos VALE a partir de 2018
INICIO_RAIZ = {"VALE": "2018-01-01"}


# ================================================================ dados brutos
def acoes_brutas(tickers):
    """Longo: data, ticker, fech (BRUTO do COTAHIST, o mesmo do strike), div e split (Yahoo). Os dividendos do Yahoo vêm em unidades
    ajustadas por desdobramento/bonificação: reescalo pela razão fechamento COTAHIST / fechamento Yahoo do dia. ETFs (BOVA11/SMAL11) não
    estão no COTAHIST filtrado: fechamento do Yahoo (ETF não distribui)."""
    tickers = list(tickers)
    c = pd.read_parquet(FD / "b3_acoes_cotahist.parquet", filters=[("ticker", "in", tickers)], columns=["data", "ticker", "fech"])
    y = pd.read_parquet(FD / "y_proventos.parquet", filters=[("ticker", "in", tickers)]).dropna(subset=["data"])
    etf = [t for t in tickers if t.endswith("11") and (c.ticker == t).sum() < 500]
    c = pd.concat([c[~c.ticker.isin(etf)], y[y.ticker.isin(etf)][["data", "ticker", "close"]].rename(columns={"close": "fech"})],
                  ignore_index=True)
    out = c.merge(y[["data", "ticker", "div", "split", "close"]], on=["data", "ticker"], how="left")
    razao = (out.fech / out.close).where(out.close > 0)
    razao = razao.groupby(out.ticker).transform(lambda s: s.ffill().bfill()).fillna(1.0)
    out["div"] = out["div"].fillna(0.0) * razao
    out["split"] = out["split"].fillna(0.0)
    return out[["data", "ticker", "fech", "div", "split"]].sort_values(["ticker", "data"]).reset_index(drop=True)


def painel(raizes):
    """(S, R) por raiz: fechamento BRUTO (o do strike) e retorno total diário (proventos e desdobramentos)."""
    tk = {TICKER[r]: r for r in raizes}
    a = acoes_brutas(tuple(tk))
    S = a.pivot_table(index="data", columns="ticker", values="fech").rename(columns=tk)
    dv = a.pivot_table(index="data", columns="ticker", values="div").rename(columns=tk).reindex(S.index).fillna(0)
    sp = a.pivot_table(index="data", columns="ticker", values="split").rename(columns=tk).reindex(S.index).fillna(0)
    sp = sp.where(sp > 0, 1.0)
    R = (S * sp + dv) / S.shift(1) - 1
    R = R.where(R.abs() < .4)
    return S.reindex(DIAS).ffill(limit=5), R.reindex(DIAS).fillna(0)


def opcoes(raizes):
    o = B.opcoes(raizes)
    for r, ini in INICIO_RAIZ.items():
        o = o[(o.raiz != r) | (o.data >= ini)]
    return o.reset_index(drop=True)


def carrega_b3(raizes):
    S, R = painel(raizes)
    return {"opc": opcoes(raizes), "S": S, "R": R}


# ================================================================ índice rápido
def indice(o):
    """o ordenado por (raiz, venc, data, tipo, strike) + dicionários de posições por (raiz, venc, data) e (raiz, venc)."""
    def f():
        x = o.sort_values(["raiz", "venc", "data", "tipo", "strike"]).reset_index(drop=True)
        g3 = x.groupby(["raiz", "venc", "data"], sort=False).indices
        g2 = x.groupby(["raiz", "venc"], sort=False).indices
        vs = {r: sorted(pd.Timestamp(v) for v in x.loc[x.raiz == r, "venc"].unique()) for r in x.raiz.unique()}
        return x, g3, g2, vs
    return memo("op_indice", o, f)


def linhas(o, raiz, v, dia):
    x, g3, _, _ = indice(o)
    i = g3.get((raiz, pd.Timestamp(v), pd.Timestamp(dia)))
    return x.iloc[i] if i is not None else x.iloc[:0]


def historico(o, raiz, v):
    """Pivôs (data x série) de meio, bid, ask e strike de um vencimento (memo)."""
    def f():
        x, _, g2, _ = indice(o)
        i = g2.get((raiz, pd.Timestamp(v)))
        y = x.iloc[i] if i is not None else x.iloc[:0]
        y = y.drop_duplicates(["data", "serie"])
        return {c: y.pivot(index="data", columns="serie", values=c) for c in ("mid", "bid", "ask", "strike")}
    return memo(("op_hist", raiz, pd.Timestamp(v)), o, f)


def vencimentos(o, raiz):
    return indice(o)[3].get(raiz, [])


# ================================================================ perna (com saída antecipada opcional)
def perna(d, raiz, v, d0, k_alvo, tipo, lado, custo_mult=1.0, spr_max=.25, saida=None, serie=None):
    """Uma opção escolhida em d0 (dia da execução): strike mais perto de k_alvo com oferta do lado a agredir (spread <= spr_max do meio)
    — ou a `serie` dada. Marca no meio (parado se não negociou; entre o intrínseco e o teto), vale o intrínseco no vencimento.
    saida: dia de zerar antes do vencimento (paga o bid/ask do dia; sem oferta do lado, meio +/- o meio-spread da entrada)."""
    o, S = d["opc"], d["S"]
    dia = linhas(o, raiz, v, d0)
    if dia.empty or raiz not in S:
        return None
    dia = dia[dia.tipo == tipo]
    col = "bid" if lado < 0 else "ask"
    if serie is not None:
        dia = dia[dia.serie == serie]
    dia = dia[dia[col].notna() & (dia.spr <= spr_max)]
    if dia.empty:
        return None
    S0 = S[raiz].get(d0, np.nan)
    if not np.isfinite(S0):
        return None
    viol = dia.mid.fillna(dia[col]) < np.where(tipo == "C", S0 - dia.strike, dia.strike - S0) - .03 * S0
    dia = dia[~viol.values]
    if dia.empty:
        return None
    z = dia.iloc[(dia.strike - k_alvo).abs().argsort().iloc[0]]
    meio = z.mid if z.mid == z.mid else z[col]
    preco = meio - custo_mult * (meio - z[col])
    fim = pd.Timestamp(saida) if saida is not None else pd.Timestamp(v)
    dias = DIAS[(DIAS >= d0) & (DIAS <= fim)]
    if len(dias) < 2:
        return None
    h = historico(o, raiz, v)
    St = S[raiz].reindex(dias).ffill()
    Kt = h["strike"][z.serie].reindex(dias).ffill().fillna(z.strike) if z.serie in h["strike"] else pd.Series(z.strike, index=dias)
    mk = h["mid"][z.serie].reindex(dias).ffill() if z.serie in h["mid"] else pd.Series(np.nan, index=dias)
    intr = (St - Kt).clip(lower=0) if tipo == "C" else (Kt - St).clip(lower=0)
    teto = St if tipo == "C" else Kt
    mk = np.minimum(np.maximum(mk.fillna(intr), intr), teto)
    mk.iloc[0] = preco
    vencida, fechou = False, False
    if saida is not None and dias[-1] < pd.Timestamp(v):
        b, a = (h[c][z.serie].get(dias[-1], np.nan) if z.serie in h[c] else np.nan for c in ("bid", "ask"))
        m = (b + a) / 2 if b == b and a == a else mk.iloc[-1]
        lado_saida = a if lado < 0 else b                              # zerar vendida = comprar no ask; zerar comprada = vender no bid
        if lado_saida == lado_saida and lado_saida < intr.iloc[-1] - .01 * St.iloc[-1]:
            lado_saida = np.nan                                        # oferta abaixo do intrínseco = oferta velha/defasada: não vale
        meia = abs(meio - z[col])
        px = m + custo_mult * (lado_saida - m) if lado_saida == lado_saida else m - lado * custo_mult * meia
        mk.iloc[-1] = max(px, intr.iloc[-1], 0.0)                      # comprada: posso exercer; vendida: ninguém vende abaixo do intrínseco
        fechou = True
    elif dias[-1] == pd.Timestamp(v) and np.isfinite(S[raiz].get(dias[-1], np.nan)):
        mk.iloc[-1] = intr.iloc[-1]
        vencida = True
    return dict(serie=z.serie, tipo=tipo, K=float(z.strike), preco=float(preco), meio=float(meio), mk=mk, fechou=fechou,
                intr_fim=float(intr.iloc[-1]) if vencida else 0.0, S0=float(S0), ST=float(St.iloc[-1]))


def pnl_pernas(pernas, lotes, lados, custo_mult=1.0, lote=100):
    """P&L diário em R$ de uma estrutura (pernas no mesmo calendário). lado: -1 vendido, +1 comprado. Tarifa na entrada, na saída
    antecipada e no exercício. Exercício: cada perna no dinheiro paga 0,03% do strike (operação à vista ao strike); as ações das pernas
    exercidas se compensam (trava no dinheiro = entrega e recebe as mesmas ações) e só o SALDO de ações é desmontado no pregão seguinte
    (0,03% + meio spread 0,08%)."""
    pnl, saldo, venc = None, 0.0, None
    for p, sg in zip(pernas, lados):
        q = lotes * lote
        x = sg * q * p["mk"].diff().fillna(0)
        x.iloc[0] -= q * p["preco"] * CUSTO_OPC * custo_mult
        if p["fechou"]:
            x.iloc[-1] -= q * p["mk"].iloc[-1] * CUSTO_OPC * custo_mult
        if p["intr_fim"] > 0:
            x.iloc[-1] -= q * p["K"] * P.B3_EMOL * custo_mult
            saldo += sg * q * (1 if p.get("tipo", "C") == "C" else -1)       # call comprada exercida = recebo ações; put = entrego
            venc = p
        pnl = x if pnl is None else pnl.add(x, fill_value=0)
    if venc is not None and abs(saldo) > 0:
        pnl.iloc[-1] -= abs(saldo) * venc["ST"] * (P.B3_EMOL + P.B3_SPREAD["liquida"]) * custo_mult
    return pnl


# ================================================================ sinais por ciclo mensal (qualquer raiz)
def iv_atm(d, raiz, v, dia, S0):
    """IV ATM (média call/put no strike mais perto do spot, até 5% de distância) com o meio do fechamento de `dia`."""
    x = linhas(d["opc"], raiz, v, dia)
    if x.empty:
        return np.nan, x
    T, r = max(du(dia, v), 1) / 252, np.log1p(CDI_AA.get(dia, .1))
    ivs = []
    for tp in ("C", "P"):
        y = x[(x.tipo == tp) & x.mid.notna()]
        if len(y):
            z = y.iloc[(y.strike - S0).abs().argsort().iloc[0]]
            if abs(z.strike / S0 - 1) < .05:
                ivs.append(iv(z.mid, S0, z.strike, T, r, tp))
    ivs = [a for a in ivs if a == a and .05 < a < 2.0]
    return (np.mean(ivs) if ivs else np.nan), x


def ciclos(d, raiz):
    """Um ciclo por vencimento mensal: sinal no 1º pregão depois do vencimento anterior (ds), alvo = próximo vencimento (v).
    Só dados até ds: IV ATM, vol realizada 21d, tendência (S / média 100d − 1), IV mediana dos 12 ciclos anteriores."""
    o, S, R = d["opc"], d["S"], d["R"]

    def f():
        vs = vencimentos(o, raiz)
        out = []
        for v0, v1 in zip(vs[:-1], vs[1:]):
            dd = DIAS[(DIAS > v0) & (DIAS < v1)]
            if len(dd) < 8 or raiz not in S:
                continue
            ds = dd[0]
            S0 = S[raiz].get(ds, np.nan)
            if not np.isfinite(S0):
                continue
            a, _ = iv_atm(d, raiz, v1, ds, S0)
            rv = R[raiz].loc[:ds].tail(21).std() * np.sqrt(252)
            mm = S[raiz].loc[:ds].dropna().tail(100)
            tend = S0 / mm.mean() - 1 if len(mm) >= 80 else np.nan
            out.append(dict(raiz=raiz, ds=ds, v=v1, S0=S0, iv=a, rv=rv, tend=tend))
        c = pd.DataFrame(out)
        if len(c):
            c["iv_rv"] = c.iv / c.rv
            c["iv_med"] = c.iv.rolling(12, min_periods=6).median().shift(1)
        return c
    return memo(("op_ciclos", raiz), o, f)


def execucao(ds, lag, limite):
    """Dia de execução: pregão t+1+lag depois do sinal, desde que antes de `limite`."""
    dd = DIAS[DIAS > ds]
    if len(dd) <= lag or dd[lag] >= limite:
        return None
    return dd[lag]


def regime_global_em(dia):
    """Regime de risco global (comum.regime_risco_global) com o valor do pregão ANTERIOR ao dia (sem olhar o futuro)."""
    s = memo("op_rg", C.DIAS, lambda: C.regime_risco_global().reindex(DIAS).ffill().shift(1).fillna(1.0))
    return float(s.get(dia, 1.0))


def perda_maxima(pernas, lados, lote=100):
    """(crédito por ação, perda máxima por lote em R$) de qualquer estrutura de calls/puts no vencimento: avalia o resultado nos strikes
    e nos extremos (o resultado é linear por partes). Perda infinita (call vendida descoberta) -> nan."""
    cred = sum(-sg * p["preco"] for p, sg in zip(pernas, lados))
    if sum(sg for p, sg in zip(pernas, lados) if p["tipo"] == "C") < 0:
        return cred, np.nan
    Ks = sorted({p["K"] for p in pernas})
    grade = [0.0] + Ks + [Ks[-1] * 3]
    res = [cred + sum(sg * (max(s - p["K"], 0) if p["tipo"] == "C" else max(p["K"] - s, 0)) for p, sg in zip(pernas, lados)) for s in grade]
    return cred, max(-min(res), 0.0) * lote


def limita_perda(x, pm, n):
    """Saída antecipada no bid/ask de séries ilíquidas pode custar MAIS que a perda máxima da estrutura (ex.: zerar trava de call com
    ask/bid de 10,80/4,67 numa largura de 4). Ninguém faz isso: segura até o vencimento, onde a perda é limitada. Conservador: a perda
    do negócio fica limitada à perda máxima + 3% (tarifas/exercício), lançada no dia da saída."""
    piso = -pm * n * 1.03
    tot = x.sum()
    if tot < piso:
        x = x.copy()
        x.iloc[-1] += piso - tot
    return x
