"""
Peças comuns a todos os fundos. Tudo lê só a pasta dados/ (nada de internet).

Convenção de todo fundo (fundos/*.py):
  - decisão com a informação do fechamento de t; execução no fechamento de t+1 (+ lag); o retorno começa em t+2.
  - a função excesso(...) devolve o EXCESSO diário sobre o CDI (em R$), já líquido de custos, no calendário da B3.
  - o fundo = CDI + excesso.
"""
from pathlib import Path

import numpy as np
import pandas as pd

AQUI = Path(__file__).resolve().parent
DADOS = AQUI / "dados"


def ler(caminho, **kw):
    """Lê csv/parquet da pasta dados/ com a primeira coluna como data."""
    p = DADOS / caminho
    if p.suffix == ".parquet":
        return pd.read_parquet(p, **kw)
    return pd.read_csv(p, index_col=0, parse_dates=True, **kw)


# ---------------------------------------------------------------- mercado
_BR = ler("comum/mercado_br.csv")
_US = ler("comum/mercado_eua.csv")
CDI = _BR["cdi"]                                    # CDI diário (fração ao dia)
DIAS = CDI.index                                    # calendário da B3
BOVA = _BR["bova11"].ffill(limit=5)
R_IBOV = BOVA.pct_change(fill_method=None).fillna(0)
PTAX = _BR["ptax"].ffill(limit=5)
DIAS_US = _US["sp500"].dropna().index
TB_US = (_US["tbill_3m_aa_pct"].reindex(DIAS_US).ffill() / 100 / 252)
SPX_USD = _US["sp500"].reindex(DIAS_US).ffill().pct_change(fill_method=None).fillna(0)


def brl(ex_us):
    """Excesso diário em dólar (sobre o T-bill) -> excesso em reais com hedge cambial, no calendário da B3.
    (com hedge, o excesso sobre o juro em dólar vira excesso sobre o CDI; os dias são agregados para o pregão seguinte da B3)."""
    e = ex_us.fillna(0).copy()
    e.index = pd.DatetimeIndex(e.index).normalize()
    acum = np.log1p(e).cumsum()
    acum = acum[~acum.index.duplicated(keep="last")].reindex(DIAS.union(acum.index)).ffill().reindex(DIAS).fillna(0)
    return np.expm1(acum.diff().fillna(0))


BENCH = {"CDI": CDI, "Ibovespa": R_IBOV, "S&P 500 (R$ c/ hedge)": CDI + brl(SPX_USD - TB_US)}


# ---------------------------------------------------------------- carteira
def carteira(W, R, custo, lag=0, aluguel=0.0):
    """W: pesos-alvo decididos no fechamento de t. Executa no fechamento de t+1+lag; rende a partir do dia seguinte.
    R: retorno em excesso ao caixa de cada ativo. custo: por unidade de giro. aluguel: a.a. sobre posições vendidas."""
    W = W.reindex(R.index).fillna(0).shift(1 + lag).fillna(0)
    r = (W.shift(1) * R).sum(axis=1) - W.diff().abs().sum(axis=1) * custo - W.clip(upper=0).abs().sum(axis=1) * aluguel / 252
    return r.fillna(0)


def vol_alvo(W, R, alvo=.10, janela=63, teto=3.0):
    """Escala a carteira para a vol-alvo, estimada só com o passado (shift(1))."""
    rp = (W.shift(1) * R).sum(axis=1)
    v = rp.rolling(janela, min_periods=40).std().shift(1) * np.sqrt(252)
    return W.mul((alvo / v).clip(upper=teto).fillna(0), axis=0)


def mensal(W):
    """Mantém só os pesos decididos no último pregão de cada mês (rebalanceamento mensal)."""
    p = pd.Series(W.index.to_period("M"), index=W.index)
    marca = p.ne(p.shift(-1))
    W = W.copy()
    W.loc[~marca.values] = np.nan
    return W.ffill().fillna(0)


# ---------------------------------------------------------------- regimes (informação até t, usados com defasagem)
def _us(s):
    return s.reindex(DIAS, method="ffill")


def regime_risco_global():
    """Média de 3 sinais de risco: VIX abaixo do percentil 80 de 1 ano, S&P acima da média de 200d, HYG/IEF acima da média de 100d."""
    v = _US["vix"].dropna()
    vix_ok = (v < v.rolling(252, min_periods=120).quantile(.8)).astype(float)
    p = _US["sp500"].dropna()
    tend = (p > p.rolling(200, min_periods=150).mean()).astype(float)
    q = np.log(_US["hyg"] / _US["ief"]).dropna()
    cred = (q > q.rolling(100, min_periods=60).mean()).astype(float)
    return ((_us(vix_ok) + _us(tend) + _us(cred)) / 3).fillna(1.0)


def regime_ibov_tendencia():
    p = BOVA.dropna()
    return (p > p.rolling(200, min_periods=150).mean()).astype(float).reindex(DIAS).ffill().fillna(1.0)


def regime_dd_stop(e, lim=.05, pausa=21):
    """Desliga por `pausa` dias depois de cair `lim` do pico da própria cota. A cota de t-1 decide; executa em t; vale para t+1."""
    v = (1 + e.fillna(0)).cumprod().values
    on = np.ones(len(v))
    pico, desl = 1.0, 0
    for i in range(1, len(v)):
        if desl > 0:
            desl -= 1
            on[i] = 0
            if desl == 0:
                pico = v[i - 1]
            continue
        pico = max(pico, v[i - 1])
        if v[i - 1] / pico - 1 < -lim:
            desl, on[i] = pausa, 0
    return pd.Series(on, index=e.index).shift(1).fillna(1.0)


def aplica_regime(e, nome="nenhum", custo_troca=.001):
    """Escala o excesso diário pelo regime. Regimes de mercado: sinal de t-2 (decide em t-1, executa em t).
    Cada liga/desliga paga custo_troca por 100% de troca."""
    if nome in (None, "nenhum"):
        return e
    if nome == "dd_stop":
        s = regime_dd_stop(e)
    else:
        s = {"risco_global": regime_risco_global, "ibov_tendencia": regime_ibov_tendencia}[nome]()
        s = s.reindex(e.index).ffill().fillna(1.0).shift(2).fillna(1.0)
    return e * s - s.diff().abs().fillna(0) * custo_troca


# ---------------------------------------------------------------- métricas
def anual(x):
    x = x.dropna()
    return ((1 + x).prod() ** (252 / max(len(x), 1)) - 1) * 100


def metricas(r, b, cdi=None):
    """r: retorno diário do fundo; b: do benchmark."""
    cdi = CDI if cdi is None else cdi
    r = r.dropna()
    b, c = b.reindex(r.index).fillna(0), cdi.reindex(r.index).fillna(0)
    a, ex = r - b, r - c
    eq = (1 + r).cumprod()
    dd = (eq / eq.cummax() - 1).min()
    ir = lambda x: x.mean() / x.std() * np.sqrt(252) if x.std() > 0 else np.nan
    mens = (1 + a).groupby(a.index.to_period("M")).prod() - 1
    return {"retorno a.a. %": anual(r), "benchmark a.a. %": anual(b), "ativo a.a. pp": anual(r) - anual(b), "vol a.a. %": r.std() * np.sqrt(252) * 100,
            "Sharpe": ir(ex), "IR vs bench": ir(a), "pior queda %": dd * 100, "meses batendo bench %": (mens > 0).mean() * 100,
            "assimetria": ex.skew(), "pior dia %": ex.min() * 100}
