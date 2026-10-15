"""
XSP (mini-SPX, 1/10 do S&P 500, liquidação financeira europeia) na IBKR: iron condor, iron butterfly ou trava de alta com put,
mensais, risco definido — com só a margem (= perda máxima) na conta no exterior.

Tese de mesa: o prêmio de variância do S&P é o mais documentado do mundo (IV > RV em ~85% dos meses); quem paga é o fundo de pensão
que compra put de proteção e o gestor que precisa de "tail hedge" no relatório. Uma PF não precisa de seguro: vende a trava e deixa
o resto em CDI no Brasil.
Dados: não há histórico gratuito de opções de SPX/XSP. Uso os índices de estratégia da Cboe como PROXY do P&L por unidade de
nocional (todos rolam no 3º vencimento mensal, com preços de SPX):
  CNDR = iron condor (vende put/call ~20 delta, compra ~5 delta); BFLY = iron butterfly (vende straddle ATM, compra asas ~5% OTM);
  trava_put = PUT (put ATM vendida) + perna comprada de PPUT (put 5% OTM; PPUT − S&P total) -> trava de alta com put ATM/−5%.
P&L de 1 XSP = (retorno do índice − T-bill) x nocional (S&P/10 x 100 = S&P x 10) — o índice é colateralizado em T-bill pelo nocional;
na conta da PF o colateral NÃO rende (só a margem fica lá, sem juros), por isso tiro o T-bill.
Tamanho: contratos INTEIROS = piso(capital x risco x alavancagem / perda máxima de 1 XSP), perda máxima estimada na rolagem com
o VIX do dia anterior: condor ~ largura das asas (0,8 x VIX x raiz(1/12)) x 75%; borboleta ~ 5% − crédito (~2,5%); trava 5% − ~2%.
Custos de varejo IBKR: US$ 0,65 de comissão + ~US$ 0,06 de meio spread (x100) por perna na abertura; liquidação financeira no
vencimento (sem custo). Conta no exterior: margem = n x perda máxima (pf.custo_conta_exterior: perde o CDI, câmbio, IOF de remessa).
IR: exterior (15% ao ano, Lei 14.754/2023).
"""
import numpy as np
import pandas as pd

import op_base as O

C, P = O.C, O.P

NOME = "XSP (mini-SPX) iron condor / borboleta / trava de put mensal — proxy índices Cboe"
TESE = "Vendo o prêmio de variância do S&P em XSP com risco definido; só a perda máxima fica na IBKR, o resto em CDI"
BENCHMARK = "CDI"
INICIO, CORTE = "2010-01-01", "2021-01-01"
REGIME, CUSTO_TROCA = "nenhum", 0.0
CLASSE_IR = "exterior"
PARAMS = {"estrutura": "trava_put", "filtro": "nenhum", "risco": .25}       # maior IR no IS (0,68)
GRADE = {"estrutura": ["condor", "borboleta", "trava_put"], "filtro": ["nenhum", "risco_global"]}
VIZINHANCA = {"risco": (.15, .35)}
PERNAS = {"condor": 4, "borboleta": 4, "trava_put": 2}
CUSTO_PERNA_USD = .65 + .06 * 100
DIV_SP = .018                                  # dividend yield aproximado do S&P para a perna comprada de PPUT (PPUT − S&P total)
INSTRUMENTOS = [{"onde": "IBKR (Cboe)", "ticker": "XSP (opções mensais, US$ 100 x XSP = S&P/10)", "lote": "1 contrato (~US$ 66 mil de nocional)",
                 "custo": "US$ 0,65 + meio spread ~US$ 6 por perna"},
                {"onde": "IBKR", "ticker": "margem = perda máxima da estrutura", "lote": "-", "custo": "sem CDI + câmbio + IOF 1,1%"}]
APLICAVEL = "parcial: com R$ 20 mil quase nunca cabe 1 estrutura (perda máxima de 1 XSP ~ US$ 1,5–2,5 mil = 40–60% do capital)"
MOTIVO = ("1 XSP tem ~US$ 66 mil de nocional; a perda máxima de 1 condor/borboleta é ~2,5–4% disso (US$ 1,6–2,6 mil ~ R$ 9–14 mil). "
          "Com 25% de risco por mês: 20k -> 0 contratos quase sempre; 50k -> 0–1. O PF só consegue com asas estreitas (fora do proxy).")
ALAVANCAGENS = [1, 2]
MOTIVO_ALAV = "Alavancagem = múltiplo do orçamento de perda máxima (25% -> 50% do capital por mês): 2x já é aposta de metade do capital."


def carrega():
    x = pd.read_parquet(O.FD / "i_arb_cboe.parquet", columns=["CNDR", "BFLY", "PUT", "PPUT"])
    x.index = pd.DatetimeIndex(x.index).normalize()
    y = O.B.yahoo_idx(("^GSPC", "^VIX"))
    return {"cboe": x[x.index >= "2008-01-01"].sort_index(), "y": y[y.index >= "2008-01-01"]}


def _rolagens(idx):
    """3ª sexta-feira de cada mês (ou o pregão anterior), no calendário dos EUA."""
    out = []
    for per in pd.period_range(idx[0], idx[-1], freq="M"):
        f = pd.date_range(per.start_time, per.end_time, freq="W-FRI")
        if len(f) >= 3:
            ok = idx[idx <= f[2]]
            if len(ok) and ok[-1].to_period("M") == per:
                out.append(ok[-1])
    return pd.DatetimeIndex(out)


def _retorno(d, estrutura):
    cb, y = d["cboe"], d["y"]
    idx = cb.index[cb.index.isin(y.index)]
    tb = C.TB_US.reindex(idx).ffill().fillna(0)
    r = cb.reindex(idx).pct_change(fill_method=None)
    if estrutura == "condor":
        e = r["CNDR"] - tb
    elif estrutura == "borboleta":
        e = r["BFLY"] - tb
    else:
        spx = y["^GSPC"].reindex(idx).pct_change(fill_method=None)
        e = (r["PUT"] - tb) + (r["PPUT"] - spx - DIV_SP / 252)
    return e.fillna(0), y["^GSPC"].reindex(idx), y["^VIX"].reindex(idx)


def _perda_max_frac(estrutura, vix):
    s = vix / 100 * np.sqrt(21 / 252)
    if estrutura == "condor":
        return .8 * s * .75
    if estrutura == "borboleta":
        return np.maximum(.05 - 1.0 * s * .8, .015)          # 5% − crédito do straddle ATM (~0,8 sigma)
    return np.maximum(.05 - .4 * s, .02)                      # 5% − crédito da trava ATM/−5%


def _livro(d, capital, p, lag, custo_mult, alavancagem):
    e, spx, vix = _retorno(d, p["estrutura"])
    idx = e.index
    rol = _rolagens(idx)
    n = pd.Series(np.nan, index=idx)
    pm_usd = pd.Series(np.nan, index=idx)
    ptax = P.PTAX.reindex(idx, method="ffill")
    rg = C.regime_risco_global().reindex(idx, method="ffill").fillna(1.0)
    for rd in rol:
        i = idx.get_loc(rd)
        j = i - 1 - lag
        if j < 0:
            continue
        noc = spx.iloc[j] * 10
        pm = _perda_max_frac(p["estrutura"], vix.iloc[j]) * noc
        ok = p["filtro"] == "nenhum" or rg.iloc[j] >= .67
        k = int(np.floor(capital * p["risco"] * alavancagem / (pm * ptax.iloc[j]))) if ok and pm > 0 and ptax.iloc[j] > 0 else 0
        n.iloc[i], pm_usd.iloc[i] = k, pm
    n = n.ffill().fillna(0)
    pm_usd = pm_usd.ffill().fillna(0)
    # unidades de índice fixadas na rolagem: P&L(t) = n x nocional da rolagem x (fator do índice desde a rolagem) x excesso(t)
    grupo = pd.Series(np.searchsorted(rol.values, idx.values, side="left"), index=idx)        # (rolagem k−1, rolagem k] -> k
    fator = (1 + e).groupby(grupo).cumprod() / (1 + e)                       # crescimento até t−1 dentro do ciclo
    noc_rol = (spx * 10).where(idx.isin(rol)).ffill()
    pnl_usd = (n.shift(1) * noc_rol.shift(1) * fator * e).fillna(0)
    custo_usd = (n * PERNAS[p["estrutura"]] * CUSTO_PERNA_USD * custo_mult).where(idx.isin(rol), 0)
    liq = P.usd_para_br(pnl_usd - custo_usd) * P.PTAX
    margem = (n * pm_usd).reindex(O.DIAS, method="ffill").fillna(0) * P.PTAX                  # US$ exigidos -> R$
    conta, _ = P.custo_conta_exterior(margem.clip(lower=0))
    conta = conta * custo_mult if custo_mult != 1 else conta
    total = (liq.fillna(0) - conta.where(margem > 0, 0).fillna(0)).reindex(O.DIAS).fillna(0)
    return total, n, pnl_usd, rol


def _p(params):
    return {**PARAMS, **params}


def excesso(d, capital=20000, custo_mult=1, lag=0, regime=REGIME, alavancagem=1, **params):
    t, *_ = _livro(d, capital, _p(params), lag, custo_mult, alavancagem)
    return O.fecha(t / capital, regime, CUSTO_TROCA, custo_mult)


def classes_ir(d, capital=20000, **params):
    t, *_ = _livro(d, capital, _p(params), 0, 1, 1)
    return {CLASSE_IR: t}


def posicoes(d, capital=20000, **params):
    t, *_ = _livro(d, capital, _p(params), 0, 0, 1)
    return O.wr_de_pnl({"XSP": t}, capital)


def negocios(d, capital=20000, **params):
    p = _p(params)
    t, n, pnl_usd, rol = _livro(d, capital, p, 0, 1, 1)
    linhas = []
    for a, b in zip(rol[:-1], rol[1:]):
        k = n.get(a, 0)
        if k <= 0:
            continue
        x = t[(t.index > a) & (t.index <= b)]
        linhas.append(dict(ativo="XSP_" + p["estrutura"], lado=-1, entrada=a, saida=b, contratos=k, pnl_rs=float(x.sum()),
                           **{"retorno_%": float(x.sum() / capital * 100)}))
    return O.negocios_df(linhas, capital)
