"""
IAC4 — Variância do S&P 500 vendida (auditado).

Tese de mesa: a vol implícita (VIX) fica, na média, acima da vol que o S&P de fato realiza no mês seguinte — quem compra
proteção paga um prêmio. Vendemos todo mês um swap de variância de 1 mês no S&P com strike = VIX − 1 ponto (o bid do dealer),
tiramos o beta ao S&P com um hedge rolante e dimensionamos para 8% de vol, mas com teto de vega de 0,4x o PL
(o choque de 5/fev/2018, ~25 pontos de vol, custa ~10% do PL). Regime risco_global: só fica ligado com risco global calmo.

Swap sintético (marcação diária): valor = K − [i/n·RV_i + (n−i)/n·VIX_t²], RV com teto de 2,5x o strike em vol (padrão de mercado).
P&L por 1 de vega-nocional = Δvalor / (2·K_vol), em pontos de vol (fração). Tudo em dólar, sem caixa (swap não financiado),
convertido para excesso sobre o CDI com hedge cambial (comum.brl).

Versão auditada da estratégia de venda de variância da pesquisa original.
"""
import numpy as np
import pandas as pd

import comum

NOME = "Variância do S&P vendida (beta neutro)"
TESE = "Vender variância de 1 mês do S&P a VIX−1 (prêmio de vol), com hedge de beta e teto de vega que sobrevive a fev/2018"
BENCHMARK = "CDI"
INICIO, CORTE = "2008-01-01", "2021-01-01"
REGIME = "risco_global"
CUSTO_TROCA = .001
PARAMS = {"spread": .01, "teto": .4}
# grade original: 2 strikes x 2 tetos; no auditado foi cruzada com 4 regimes (nenhum, risco_global, vix_contango, dd_stop) = 16 variantes
GRADE = {"spread": [.01, .02], "teto": [.25, .4]}
VIZINHANCA = {"spread": (.005, .025), "teto": (.25, .5)}

ALVO = .08         # vol-alvo da carteira
N = 21             # dias úteis de cada swap (1 mês)
CAP = 2.5          # teto da vol realizada, em múltiplos do strike
CUSTO = .0041      # custo por unidade de giro do vega-nocional (além do spread no strike)
INICIO_ROLAGEM = "2005-01-03"   # o calendário de rolagens começa aqui (igual ao código de origem)


def carrega():
    return {"px": comum.ler("variancia/vix_sp500.csv")}


def _cal(d):
    """Dias úteis seg-sex; preço do último fechamento (até 5 dias de feriado)."""
    px = d["px"].dropna(how="all")
    cal = pd.bdate_range(INICIO_ROLAGEM, px.index.max())
    return px.reindex(cal.union(px.index)).ffill(limit=5).reindex(cal)


def _swaps(d, spread):
    """P&L diário (por 1 de vega) de vender um swap de variância de 1 mês, rolado a cada N dias. Devolve também o livro de swaps."""
    px = _cal(d)
    iv = (px["vix"] / 100).values
    r = np.log(px["sp500"]).diff().values
    pnl = np.zeros(len(px))
    livro = []
    i0 = 0
    while i0 + 1 < len(px):
        if not np.isfinite(iv[i0]):
            i0 += 1
            continue
        k_vol = max(iv[i0] - spread, .01)            # strike em vol: VIX da entrada menos o spread do dealer
        K, vega = k_vol ** 2, 1 / (2 * k_vol)
        v_ant, soma = 0.0, 0.0
        for i in range(1, N + 1):
            j = i0 + i
            if j >= len(px):
                break
            soma += (r[j] if np.isfinite(r[j]) else 0.0) ** 2
            rv = min(soma * 252 / i, (CAP * k_vol) ** 2)      # variância realizada até aqui (com teto)
            ivt = iv[j] if np.isfinite(iv[j]) else iv[i0]
            val = K - (i / N * rv + (N - i) / N * ivt ** 2) if i < N else K - rv
            pnl[j] = (val - v_ant) * vega
            v_ant = val
        livro.append((i0, min(i0 + N, len(px) - 1), k_vol, np.sqrt(soma * 252 / max(i, 1))))
        i0 += N
    return pd.Series(pnl, index=px.index), px, livro


def posicoes(d, spread=PARAMS["spread"], teto=PARAMS["teto"]):
    """W: vega-nocional (fração do PL) decidido em t. R: P&L diário do swap vendido menos o hedge de beta no S&P."""
    x, px, _ = _swaps(d, spread)
    h = px["sp500"].pct_change(fill_method=None)
    # beta do swap ao S&P: retornos de 5 dias, janela de 1 ano, só passado
    x5, h5 = x.rolling(5).sum(), h.rolling(5).sum()
    beta = (x5.rolling(252, min_periods=126).cov(h5) / (h5.rolling(252, min_periods=126).var() + 1e-12)).shift(1).clip(-1, 2)
    R = (x - beta * h).where(x.index >= x.ne(0).idxmax())
    vol = R.rolling(126, min_periods=40).std().shift(1) * np.sqrt(252)
    W = (ALVO / vol).clip(upper=min(3, teto)).fillna(0).where(R.notna().cumsum() > 40, 0)
    return W.to_frame("VS_EUA"), R.to_frame("VS_EUA")


def excesso(d, custo_mult=1, lag=0, regime=REGIME, **params):
    p = {**PARAMS, **params}
    W, R = posicoes(d, **p)
    e_usd = comum.carteira(W, R.fillna(0), CUSTO * custo_mult, lag)
    return comum.aplica_regime(comum.brl(e_usd), regime, CUSTO_TROCA * custo_mult)


def negocios(d, spread=PARAMS["spread"], teto=PARAMS["teto"]):
    """Um negócio por swap mensal vendido. retorno_% = P&L do swap por 1 de vega (pontos de vol);
    contrib_pp = contribuição ao PL (vega-nocional executado x P&L com hedge, menos custos), em dólar e antes do regime."""
    x, px, livro = _swaps(d, spread)
    W, R = posicoes(d, spread, teto)
    We = W["VS_EUA"].shift(1).fillna(0)                           # executado em t+1
    c = We.shift(1).fillna(0) * R["VS_EUA"].fillna(0) - We.diff().abs().fillna(0) * CUSTO
    lin = []
    for a, b, k_vol, rv in livro:
        dias = slice(a + 1, b + 1)
        lin.append({"ativo": "VS_EUA", "lado": -1, "entrada": px.index[a], "saida": px.index[b], "dias": b - a,
                    "strike_%": k_vol * 100, "vol_realizada_%": rv * 100, "retorno_%": x.iloc[dias].sum() * 100,
                    "vega_medio": We.iloc[dias].mean(), "contrib_pp": c.iloc[dias].sum() * 100})
    return pd.DataFrame(lin)
