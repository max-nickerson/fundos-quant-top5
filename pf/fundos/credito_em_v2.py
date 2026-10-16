"""
Crédito high yield emergente via ETF (HYEM/EMHY/CEMB) comprado no PÂNICO DE CRÉDITO com âncora — conta em dólar v2 (pf.conta_usd).

Origem: institucional fundos/eurobonds.py (eurobonds HY Brasil, lote US$ 200 mil — não cabe) e varejo/fundos/eurobonds_varejo.py
(HYEM sempre carregado na IBKR, câmbio sem hedge: −4,0 pp; com hedge teórico ≈ +4,0 pp... a diferença era o câmbio/CDI).

Tese de mesa (mecanismos 2 e 3 do BRIEF PF3):
  - quem vende no pânico: fundos de EM/HY abertos com resgate diário vendem o que tem liquidez (o ETF e os bonds mais líquidos) quando
    o fluxo vira; o ETF negocia com desconto ao NAV e o spread abre além do que o default esperado justifica. Quem compra 1 cota sem
    pressa recebe o prêmio de liquidez quando o fluxo volta (mesmo negócio do "petróleo em pânico com âncora no Brent").
  - ÂNCORA (mecanismo 2): o pânico tem que ser de CRÉDITO, não de juro: retorno do ETF MENOS beta x IEF (Treasury 7–10 anos, beta de
    1 ano em retornos de 5 dias, só passado) — se a queda veio do Treasury não é pânico de crédito; e o "spread" do ETF (dividendos de
    12 meses / preço − Treasury de 5 anos) tem que estar no quintil de cima do último ano (o preço divergiu da âncora de valor).
  - MAGNITUDE (mecanismo 3): só entra se a queda de crédito em `jan` dias passar de k desvios (k na grade: 1,5 e 2,5).
  - segura H pregões (gatilho novo renova); opcional `dur`: vende IEF (ações inteiras, Reg T, aluguel ~0,30% a.a.) no beta para ficar
    só com o spread (precisa de conta margem: patrimônio >= US$ 2 mil, senão não vende).
Execução (IBKR, conta em dólar v2): compra com fração (US$ 0,0035/ação, mín. US$ 0,35; meio spread 0,05% HYEM/EMHY, 0,10% CEMB),
decisão no fechamento de t, execução no fechamento de t+1+lag; tamanho = alavancagem x saldo da conta no 1º pregão do mês.
RETENÇÃO NOS EUA (premissa corrigida, conservadora): dividendos de ETF americano a não residente sem tratado (Brasil) sofrem 30% de
retenção; a isenção de "interest-related dividends" (IRC 871(k)) só cobre juros de fonte americana — o grosso do HYEM/EMHY é juro de
emissor estrangeiro -> retenção de 30% sobre os dividendos (parâmetro `retencao`; o crédito no IR brasileiro não é modelado). Variante
retencao=0 = um ETF UCITS irlandês equivalente (acumulação, sem retenção ao investidor; disponibilidade/custo não verificados).
Fora do ETF o dinheiro fica em SGOV (a conta_usd credita T-bill sobre o saldo; o livro é passado em EXCESSO do T-bill).
IR: dict da conta_usd ('exterior' 15% ao ano; 'futuros_b3' = hedge WDO 15% mensal; 'cdi_perdido').
Dados: varejo/dados/eurobonds/etfs.csv (preço de fechamento + dividendo na data ex, Yahoo; ^FVX), IEF ajustado (quant/fundos/dados/y_etf).
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _util as U  # noqa: E402
import _v2_comum as V2  # noqa: E402

C, pf = U.C, U.pf

CONTA_USD_V2 = True
NOME = "Crédito EM high yield (ETF) no pânico de crédito com âncora — conta em dólar v2"
TESE = ("Compra HYEM quando a queda de crédito (ETF − beta x Treasury) passa de k desvios E o spread do ETF está no topo do ano; segura H dias; "
        "o dinheiro mora na IBKR em SGOV, hedgeado com WDO")
BENCHMARK, INICIO, CORTE, REGIME, CUSTO_TROCA = "CDI", "2013-06-01", "2021-01-01", "nenhum", .001
PARAMS = {"etf": "HYEM", "modo": "panico", "k": 1.5, "H": 84, "jan": 10, "q": .8, "dur": False, "retencao": .30}
GRADE = {"k": [1.5, 2.5], "H": [42, 84], "dur": [False, True]}
VIZINHANCA = {"k": (1.25, 2.75), "H": (30, 110), "jan": (5, 20), "q": (.7, .9)}
INSTRUMENTOS = ("IBKR: HYEM (VanEck EM High Yield Bond, ~US$ 20), EMHY (iShares EM HY), CEMB (iShares EM corporativo) com frações; IEF vendido "
                "em ações inteiras (opcional); caixa em SGOV. B3: WDO vendido sobre o saldo (hedge cambial).")
APLICAVEL = True
MOTIVO = ("ETF com frações cabe em qualquer sleeve; venda de IEF (dur=True) só com patrimônio >= US$ 2 mil (sleeve >= ~R$ 11 mil). "
          "Os eurobonds do institucional (lote US$ 200 mil) continuam fora do alcance.")
ALAVANCAGENS = [1, 1.5, 2]
MOTIVO_ALAV = ("Reg T: até 2x o saldo, só com patrimônio >= US$ 2 mil (abaixo disso a alavancagem pedida vira 1x); juros T-bill + 1,5% sobre a "
               "dívida; 5x impossível (sem futuro de crédito EM para PF; portfolio margin só acima de US$ 110 mil)")
SLEEVES = V2.SLEEVES
MEIO_SPREAD = {"HYEM": .0005, "EMHY": .0005, "CEMB": .001}
ALUGUEL_IEF = .003
JUROS_MARGEM = .015
REG_T_MIN = 2000.0
_CACHE = {}


def carrega():
    x = pd.read_csv(U.RAIZ / "varejo" / "dados" / "eurobonds" / "etfs.csv", index_col=0, parse_dates=True)
    ief = pd.read_parquet(U.FD / "y_etf.parquet")["IEF"].rename("IEF")
    return {"etfs": x, "ief": ief}


def _base(d, etf):
    x = d["etfs"]
    P = x[f"{etf}_preco"].dropna()
    idx = P.index
    dv = x[f"{etf}_div"].reindex(idx).fillna(0)
    ief = d["ief"].dropna()
    ief = ief[~ief.index.duplicated(keep="last")].reindex(idx.union(ief.index)).ffill(limit=3).reindex(idx)
    return P, dv, ief, x["ust5_pct"].reindex(idx).ffill()


def sinal(d, etf="HYEM", modo="panico", k=1.5, H=84, jan=10, q=.8):
    """Lado desejado decidido no fechamento de t (1 = carregar o ETF), só com dados até t. Devolve (sinal, beta ao IEF)."""
    P, dv, ief, u5 = _base(d, etf)
    tr = ((P + dv) / P.shift(1) - 1)
    ri = ief.pct_change(fill_method=None)
    t5, i5 = tr.rolling(5).sum(), ri.rolling(5).sum()
    beta = (t5.rolling(252, min_periods=126).cov(i5) / i5.rolling(252, min_periods=126).var()).clip(0, 1.5)
    if modo == "sempre":
        return pd.Series(1.0, index=P.index), beta.fillna(0)
    c = tr - beta.shift(1) * ri                                         # retorno de crédito (sem a parte de juro)
    z = c.rolling(jan).sum() / (c.rolling(252, min_periods=126).std() * np.sqrt(jan))
    spread = dv.rolling("365D").sum() / P * 100 - u5                    # "spread" do ETF vs Treasury 5 anos (p.p.)
    ancora = spread >= spread.rolling(252, min_periods=126).quantile(q)
    gat = ((z <= -k) & ancora).astype(float)
    if modo == "magnitude":                                             # controle: só o limiar, sem âncora
        gat = (z <= -k).astype(float)
    s = gat.copy()
    for j in range(1, H):
        s = s.where(s != 0, gat.shift(j).fillna(0))
    return s.fillna(0), beta.fillna(0)


def livro_usd(d, capital, sleeve_brl, custo_mult=1, lag=0, alavancagem=1, etf="HYEM", modo="panico", k=1.5, H=84, jan=10, q=.8,
              dur=False, retencao=.30):
    key = (id(d["etfs"]), len(d["etfs"]), d["etfs"].index.max(), capital, sleeve_brl, custo_mult, lag, alavancagem, etf, modo, round(k, 6), int(H),
           int(jan), round(q, 6), dur, retencao)
    if key in _CACHE:
        return _CACHE[key]
    P, dv, ief, _ = _base(d, etf)
    s, beta = sinal(d, etf, modo, k, int(H), int(jan), q)
    idx = P.index
    s = s.where(idx >= pd.Timestamp(INICIO), 0)
    sx = s.shift(1 + lag).fillna(0).values                              # executa no fechamento de t+1+lag
    bx = beta.shift(1 + lag).fillna(0).values
    E = V2.usd_conta_mes(sleeve_brl, idx).values                         # US$ na conta (1º pregão do mês)
    tb = C.TB_US.reindex(idx, method="ffill").fillna(0).values
    Pv, dvv, Iv = P.values, dv.values, ief.ffill().values
    T = len(idx)
    sh = np.zeros(T)                                                     # cotas do ETF (fração)
    qi = np.zeros(T)                                                     # IEF vendido (ações inteiras, negativo)
    custo = np.zeros(T)
    for t in range(1, T):
        sh[t], qi[t] = sh[t - 1], qi[t - 1]
        margem = E[t] >= REG_T_MIN
        if sx[t] > 0 and sh[t - 1] == 0:                                 # entra
            L = alavancagem if margem else 1.0
            sh[t] = L * E[t] / Pv[t]
            if dur and margem and np.isfinite(Iv[t]) and Iv[t] > 0:
                qi[t] = -np.round(bx[t] * sh[t] * Pv[t] / Iv[t])
        elif sx[t] == 0 and sh[t - 1] != 0:                              # sai
            sh[t], qi[t] = 0.0, 0.0
        d_sh, d_qi = abs(sh[t] - sh[t - 1]), abs(qi[t] - qi[t - 1])
        if d_sh:
            custo[t] += float(pf.custo_ordem_ibkr_usd(d_sh * Pv[t], Pv[t])) + d_sh * Pv[t] * MEIO_SPREAD.get(etf, .0005)
        if d_qi:
            custo[t] += float(pf.custo_ordem_ibkr_usd(d_qi * Iv[t], Iv[t])) + d_qi * Iv[t] * .0003
    sp, qp = np.r_[0, sh[:-1]], np.r_[0, qi[:-1]]
    P0, I0 = np.r_[np.nan, Pv[:-1]], np.r_[np.nan, Iv[:-1]]
    val0 = np.nan_to_num(sp * P0)
    pnl_etf = sp * np.nan_to_num(Pv - P0) + sp * dvv * (1 - retencao) - val0 * tb          # excesso do T-bill
    divida = np.clip(val0 - E, 0, None)                                  # Reg T: comprado acima do patrimônio paga T-bill + 1,5%
    pnl_ief = qp * np.nan_to_num(Iv - I0) - np.abs(qp) * np.nan_to_num(I0) * ALUGUEL_IEF / 252 * custo_mult
    pnl = pnl_etf + pnl_ief - divida * JUROS_MARGEM / 252 - custo * custo_mult
    out = {"pnl_usd": pd.Series(pnl, index=idx), "etf": pd.Series(pnl_etf, index=idx), "ief": pd.Series(pnl_ief, index=idx),
           "sh": pd.Series(sh, index=idx), "qi": pd.Series(qi, index=idx), "s": s, "P": P}
    if len(_CACHE) > 80:
        _CACHE.clear()
    _CACHE[key] = out
    return out


def _roda(d, capital, sleeve_brl, hedge, custo_mult, lag, alavancagem, params):
    p = {**PARAMS, **params}
    sl = V2.sleeve(capital, sleeve_brl)
    L = livro_usd(d, capital, sl, custo_mult, lag, alavancagem, **p)
    ex, cls = V2.fecha(L["pnl_usd"], sl, capital, hedge, custo_mult)
    return ex, cls, L


def excesso(d, capital=20000, custo_mult=1, lag=0, regime=REGIME, alavancagem=1, sleeve_brl=None, hedge="inteiro", **params):
    ex = _roda(d, capital, sleeve_brl, hedge, custo_mult, lag, alavancagem, params)[0]
    return C.aplica_regime(ex, regime, CUSTO_TROCA * custo_mult) if regime not in ("nenhum", None) else ex


def classes_ir(d, capital=20000, alavancagem=1, sleeve_brl=None, hedge="inteiro", **params):
    params.pop("regime", None)
    return _roda(d, capital, sleeve_brl, hedge, 1, 0, alavancagem, params)[1]


def posicoes(d, capital=20000, **params):
    """Peso 1 quando carrega o ETF (no calendário dos EUA); retorno do ETF em excesso do T-bill (com dividendos líquidos da retenção)."""
    p = {**PARAMS, **params}
    P, dv, _, _ = _base(d, p["etf"])
    s, _ = sinal(d, p["etf"], p["modo"], p["k"], int(p["H"]), int(p["jan"]), p["q"])
    s = s.where(s.index >= pd.Timestamp(INICIO), 0)
    r = ((P - P.shift(1) + dv * (1 - p["retencao"])) / P.shift(1)) - C.TB_US.reindex(P.index, method="ffill").fillna(0)
    return s.to_frame(p["etf"]), r.to_frame(p["etf"])


def negocios(d, capital=20000, sleeve_brl=None, hedge="inteiro", **params):
    """Um negócio por período carregado: P&L do livro (ETF + IEF) em R$ pela PTAX, em pp do capital."""
    ex, cls, L = _roda(d, capital, sleeve_brl, hedge, 1, 0, 1, params)
    p = {**PARAMS, **params}
    h = L["sh"].shift(1).fillna(0) > 0
    g = (h != h.shift()).cumsum()
    ptax = C.PTAX.reindex(h.index, method="ffill")
    brl = L["pnl_usd"] * ptax
    lin = []
    for _, dias in h[h].groupby(g[h]).groups.items():
        P = L["P"]
        lin.append({"ativo": p["etf"], "lado": 1, "entrada": dias.min(), "saida": dias.max(), "dias": len(dias),
                    "retorno_%": (P.loc[dias.max()] / P.shift(1).loc[dias.min()] - 1) * 100, "contrib_pp": brl.loc[dias].sum() / capital * 100})
    return pd.DataFrame(lin, columns=["ativo", "lado", "entrada", "saida", "dias", "retorno_%", "contrib_pp"])
