"""
Peças comuns da frente "pf2_b3" (rodada PF2: mais edges na B3 com vendedor/comprador forçado, para R$ 20–50 mil).
Não altera comum.py/robustez.py/pf.py; reaproveita o motor de carteira PF da frente b3_acoes (b3_base.carteira_pf).

Dados:
  - ações: painel COTAHIST 2014+ com RJ, retorno total ajustado e melhor oferta no fechamento (pf/dados/b3_acoes, via b3_base);
  - FIIs: pf/dados/pf2_b3/fii_cotas.parquet (COTAHIST bruto CODBDI 12, lote padrão) + rendimento do informe mensal CVM
    (DY do mês x valor patrimonial da cota). Calibração: o rendimento do mês de referência m é pago com data-com no último pregão de m
    e "ex" no 1º pregão de m+1 (HGLG11 2025–26: CVM 1,10 x Yahoo 1,10 ex em 01/09, 01/10, 03/11 ...). FIIs com data-com em outro dia
    ficam com o rendimento no dia errado (erro de timing dentro do mês, não de valor);
  - direitos de FII: pf/dados/pf2_b3/fii_direitos.parquet; direitos/recibos/bônus de ações: pf/dados/b3_acoes/direitos.parquet.

Motor de episódios (`episodios`): cada evento (data de DIVULGAÇÃO, ticker) vira um alvo de R$ `tam` decidido no fechamento do dia do
evento (ou do pregão seguinte, se não houve pregão), executado no fechamento de t+1+lag com ações inteiras (lote + fracionário), custo
= emolumentos 0,03% + meio spread REAL do fechamento + 0,2% na parte fracionária; compra só se o volume do dia >= 10x a ordem (tenta 3
pregões); vende `hold` pregões depois (ou na data de saída do evento, conhecida antes — ex.: último pregão da carteira velha); papel
parado 30 pregões sai pelo último preço. Dinheiro em ação NÃO rende CDI.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import b3_base as B  # noqa: E402

C, pf = B.C, B.pf
DIAS, CDI = B.DIAS, B.CDI
DADOS = B.PF / "dados" / "pf2_b3"
QUANT = B.RAIZ.parent
FD = QUANT / "fundos" / "dados"
_C = {}


# ---------------------------------------------------------------- dados
def acoes():
    """P, R, V, NEG, BID, ASK, O, H, L, HS (meio spread) — DIAS x tickers (ações/units)."""
    if "acoes" not in _C:
        _C["acoes"] = B.dados_acoes()
    return dict(_C["acoes"])


def _fii_painel():
    if "fii" in _C:
        return _C["fii"]
    x = pd.read_parquet(DADOS / "fii_cotas.parquet")
    # ESPECI "CI" também é ETF (BOVA11, HASH11, ETHE11...): só fica quem entrega informe mensal de FII à CVM
    fii = set(pd.read_parquet(DADOS / "fii_rend.parquet", columns=["raiz"]).raiz)
    x = x[(x.fech > 0) & x.ticker.str[:4].isin(fii)].sort_values(["ticker", "data"]).drop_duplicates(["ticker", "data"], keep="last")
    piv = lambda c: x.pivot(index="data", columns="ticker", values=c).reindex(DIAS).astype("float64")
    P, V, NEG, BID, ASK = piv("fech"), piv("volume"), piv("negocios"), piv("oferta_compra"), piv("oferta_venda")
    ult = P.ffill()
    r = P / ult.shift(1) - 1
    # desdobramento/grupamento de cotas (COTAHIST não ajusta): salto > 35% perto de razão "redonda" -> 0; erro que se desfaz -> 0
    lq = np.log1p(r)
    cand = np.log(np.array([k for b in (2, 3, 4, 5, 8, 10, 20, 25, 50, 100) for k in (b, 1 / b)]))
    dist = np.min(np.abs(lq.values[..., None] + cand[None, None, :]), axis=2)
    split = (lq.abs().values > .35) & (dist < .08)
    r = r.mask(split, 0.0)
    erro = (r.abs() > .3) & ((1 + r) * (1 + r.shift(-1)) - 1).abs().lt(.08)
    r = r.mask(erro | erro.shift(1, fill_value=False), 0.0)
    r = r.where(r.abs() < .6, 0.0)
    _C["fii"] = {"P": P, "r": r, "V": V, "NEG": NEG, "BID": BID, "ASK": ASK, "split": pd.DataFrame(split, index=P.index, columns=P.columns)}
    return _C["fii"]


def fii_rend():
    """Rendimento por cota (R$) do informe mensal CVM: data = 1º dia do mês de referência (formato longo, coluna 'data')."""
    c = pd.read_parquet(DADOS / "fii_rend.parquet")
    c["ticker"] = c.raiz + "11"
    return c


def fiis():
    """Painel de FIIs: P, R (retorno total: preço + rendimento no 1º pregão do mês seguinte), V, NEG, BID, ASK, HS, mais 'rend' (longo)."""
    p = _fii_painel()
    rend = fii_rend()
    return {"P": p["P"], "r": p["r"], "V": p["V"], "NEG": p["NEG"], "BID": p["BID"], "ASK": p["ASK"], "rend": rend[rend.ticker.isin(p["P"].columns)]}


def fii_retorno(d):
    """R total dos FIIs só com os dados em d (respeita o truncamento): rendimento do mês m entra no 1º pregão de m+1."""
    P, r = d["P"], d["r"]
    rd = d["rend"]
    rd = rd[(rd.rend > 0) & (rd.rend < 50)]
    ex = DIAS[np.clip(DIAS.searchsorted(rd.data + pd.offsets.MonthBegin(1)), 0, len(DIAS) - 1)]
    dv = pd.DataFrame({"data": ex, "ticker": rd.ticker.values, "rend": rd.rend.values}).groupby(["data", "ticker"]).rend.sum().unstack()
    dv = dv.reindex(index=P.index, columns=P.columns).fillna(0)
    ult = P.ffill().shift(1)
    y = (dv / ult).where(ult > 0, 0).clip(0, .05)            # rendimento mensal > 5% = erro de cadastro
    R = r.fillna(0) + y
    return R.where(ult.notna()), y


def com_hs(d):
    d = dict(d)
    d["HS"] = B.meio_spread(d["BID"], d["ASK"], d["V"].fillna(0))
    return d


# ---------------------------------------------------------------- motor de episódios
def alvo_de_eventos(ev, cols, hold, tam, prazo_compra=3):
    """ev: DataFrame com data (decisão), ticker, opcional 'fim' (data da decisão de saída, conhecida na entrada) e 'tam' (R$).
    Devolve (alvo, manter): alvo>0 só nos `prazo_compra` primeiros pregões (janela de compra); manter=True até a saída."""
    A = np.zeros((len(DIAS), len(cols)))
    M = np.zeros((len(DIAS), len(cols)), bool)
    ci = {c: j for j, c in enumerate(cols)}
    i0 = DIAS.searchsorted(pd.DatetimeIndex(ev["data"]))
    fim = ev["fim"] if "fim" in ev else pd.Series(pd.NaT, index=ev.index)
    tm = ev["tam"].values if "tam" in ev else np.full(len(ev), tam)
    for i, t, f, q in zip(i0, ev["ticker"].values, fim.values, tm):
        if i >= len(DIAS) or t not in ci:
            continue
        j = ci[t]
        i_f = DIAS.searchsorted(pd.Timestamp(f)) if pd.notna(f) else i + int(hold)
        i_f = min(max(i_f, i + 1), len(DIAS))
        A[i:min(i + prazo_compra, i_f), j] = np.maximum(A[i:min(i + prazo_compra, i_f), j], q)
        M[i:i_f, j] = True
    return pd.DataFrame(A, index=DIAS, columns=cols), pd.DataFrame(M, index=DIAS, columns=cols)


def episodios(ev, d, capital, hold, tam, custo_mult=1.0, lag=0, alavancagem=1.0, vol_min=10.0):
    cols = sorted(set(ev["ticker"]) & set(d["P"].columns))
    if not cols:
        z = pd.Series(0.0, index=DIAS)
        return {"e": z, "pnl": z, "custo": z, "cdi_perdido": z, "vendas": z, "W": pd.DataFrame(index=DIAS), "negocios": pd.DataFrame(
            columns=["ativo", "lado", "entrada", "saida", "dias", "retorno_%", "contrib_pp", "valor", "ganho"]), "investido": z}
    ev = ev[ev.ticker.isin(cols)]
    A, M = alvo_de_eventos(ev, cols, hold, tam)
    return B.carteira_pf(A, d, capital, custo_mult=custo_mult, lag=lag, alavancagem=alavancagem, manter=M, vol_min=vol_min)


def rotula(ng, ev):
    """Anexa o rótulo do evento mais recente (<= entrada) a cada negócio."""
    if ng is None or not len(ng) or "rotulo" not in ev:
        return ng
    ng = ng.copy()
    e = ev[["data", "ticker", "rotulo"]].sort_values("data")
    lab = []
    for a, t in zip(ng.ativo, pd.to_datetime(ng.entrada)):
        x = e[(e.ticker == a) & (e.data <= t)]
        lab.append(x.rotulo.iloc[-1] if len(x) else "")
    ng["rotulo"] = lab
    return ng


class Cache:
    """Cache de resultados por (id dos dados, parâmetros): a bateria chama excesso/posicoes/negocios muitas vezes."""

    def __init__(self, n=48):
        self.d, self.n = {}, n

    def get(self, chave, f):
        if chave not in self.d:
            if len(self.d) >= self.n:
                self.d.clear()
            self.d[chave] = f()
        return self.d[chave]


def mapa_cnpj():
    """CNPJ (14 dígitos) -> raízes de ticker (pf/dados/b3_acoes/mapa_cnpj.parquet, FCA)."""
    m = B.ler("mapa_cnpj")
    return m.groupby("cnpj").raiz.apply(list)


def cnpj14(s):
    return s.astype(str).str.replace(r"\D", "", regex=True).str.zfill(14)
