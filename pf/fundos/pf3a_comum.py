"""
Peças comuns da frente PF3 "internacional A" (pf/fundos/*_v2.py): refaz estratégias internacionais com a CONTA EM DÓLAR v2 (pf.conta_usd).

Ideia: o livro original (em_comum.livro, fg_comum.livro, lg_comum.noites) continua calculando o P&L dos papéis com os MESMOS custos de IBKR
(comissão US$ 0,0035/ação mín. 0,35, meio spread, aluguel, Reg T/juros de margem). O que muda é só a conta:
  - o livro é dimensionado pelo SLEEVE (R$ que moram na IBKR), não pelo capital: peso x sleeve por negócio (conta cash = não passa do sleeve);
  - jogamos fora o custo de conta do motor antigo (remessa por negócio, CDI perdido do saldo, câmbio) e extraímos o P&L em US$:
        P&L dos papéis em R$ = ext − ganho_cambial + remessa   (identidade dos motores antigos)  ->  / PTAX do dia = US$;
  - pf.conta_usd cobra: CDI perdido sobre o sleeve inteiro (o tempo todo), T-bill no caixa parado, 1ª remessa (IOF+spread, só uma vez),
    câmbio do saldo e o hedge em WDO (contratos inteiros, 1x por mês).
Premissas novas (anotadas aqui, não em pf.py):
  - conta MARGEM na IBKR exige US$ 2.000 (FINRA/IBKR). Com sleeve < ~R$ 11 mil (US$ 2 mil a R$ 5,5) a conta é cash: sem venda a
    descoberto (fora o hedge IWM/EEM) e, nas noites (lg), só metade do sleeve por noite (o caixa da venda liquida em D+1: alternância);
  - a decisão "margem ou cash" usa um câmbio fixo de R$ 5,5/US$ (nível do OOS 2021+), para não depender do câmbio futuro.
"""
import numpy as np
import pandas as pd

import comum as C
import pf

DIAS = C.DIAS
PTAX = pf.PTAX
SLEEVES = {20000: [5000, 10000, 15000], 50000: [12500, 25000, 37500]}
FX_FIXO_MARGEM = 5.5
REG_T_MIN_USD = 2000.0


def sleeve_padrao(capital, sleeve_brl):
    return capital / 2 if sleeve_brl is None else sleeve_brl


def tem_margem(sleeve_brl):
    return sleeve_brl / FX_FIXO_MARGEM >= REG_T_MIN_USD


def usd_de_ext(ext, ganho, remessa):
    """P&L dos papéis (US$, calendário B3) a partir das peças do motor antigo."""
    brl = (ext - ganho + remessa).reindex(DIAS).fillna(0)
    return brl / PTAX


def conta(pnl_usd_b3, sleeve_brl, capital, hedge="inteiro", custo_mult=1.0):
    """Leva o P&L em US$ do livro (tamanho do sleeve) ao excesso do fundo com a conta v2. Devolve (excesso, classes)."""
    e, cls = pf.conta_usd(pnl_usd_b3.reindex(DIAS).fillna(0), 0.0, sleeve_brl, capital, hedge=hedge, custo_mult=custo_mult)
    return e, cls


def reescala_negocios(ng, sleeve_brl, capital):
    ng = ng.copy()
    if "contrib_pp" in ng:
        ng["contrib_pp"] = ng["contrib_pp"] * sleeve_brl / capital
    return ng


def bench_usd(tk):
    """Retorno diário em US$ de um ETF (EEM/SPY/IWM) menos T-bill, no calendário da B3 (para separar beta)."""
    import em_comum as E
    X = E.yahoo()
    if f"Adj Close|{tk}" in X:
        p = X[f"Adj Close|{tk}"].dropna()
    else:                                                     # SPY/IWM: ETFs ajustados da base quant/fundos (fg_comum.etf)
        import fg_comum as G
        p = G.etf([tk])[tk].dropna()
    p.index = pd.DatetimeIndex(p.index)
    l = np.log(p).reindex(DIAS.union(p.index)).ffill().reindex(DIAS)
    r = np.expm1(l.diff()).fillna(0)
    tb = C.TB_US.reindex(DIAS, method="ffill").fillna(0)
    return r - tb


def beta_alfa(e, tk, inicio="2021-01-01"):
    """Regressão do excesso diário do fundo (sobre o CDI) no excesso do ETF em US$ (sobre o T-bill). Com a conta hedgeada o fundo
    não carrega câmbio, então o ETF em US$ é o fator certo; sem hedge o câmbio entra no resíduo."""
    x = bench_usd(tk).reindex(e.index).fillna(0)
    y = e.fillna(0)
    m = y.index >= pd.Timestamp(inicio)
    x, y = x[m], y[m]
    b = np.cov(y, x)[0, 1] / x.var()
    res = y - b * x
    a = res.mean() * 252 * 100
    t = res.mean() / (res.std() / np.sqrt(len(res))) if res.std() > 0 else np.nan
    return {"beta": float(b), "beta pp a.a.": float(b * x.mean() * 252 * 100), "alfa pp a.a.": float(a), "t alfa": float(t),
            "R2": float(np.corrcoef(y, x)[0, 1] ** 2) if y.std() > 0 else np.nan}
