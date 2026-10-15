"""
Peças comuns da frente "pf2_futuros" (pf/fundos/fu_*.py): futuros do mundo que CABEM em R$ 20–50 mil (micro/mini), com SÓ a margem
fora do Brasil (IBKR) ou garantia em Tesouro Selic (B3). Não altera comum.py / robustez.py / pf.py.

Como cada contrato é simulado (sem saltos de rolagem do contínuo do Yahoo):
  - RETORNO de 1 contrato = retorno do subjacente SEM rolagem (índice de retorno total, ou índice de preço + dividendos assumidos, ETF que
    rola os futuros, ou o próprio vencimento do boletim da B3 segurado até a troca) MENOS o juro da moeda (o futuro é excesso sobre o juro);
  - o NÍVEL do índice/preço (contínuo do Yahoo, com salto) entra SÓ para o tamanho (nocional = nível x multiplicador) e para a margem;
  - P&L em moeda local -> R$ pela PTAX do dia (EUR/JPY/KRW/MXN cruzados pelo dólar do Yahoo);
  - decisão no fechamento de t (calendário do próprio mercado), execução no fechamento de t+1+lag, P&L a partir do pregão seguinte;
  - custo por lado = comissão + taxas + meio spread (em moeda local, por contrato) + rolagem (2 lados x rolagens/ano);
  - IBKR: a margem (folga 1,5x) fica lá fora (pf.custo_conta_exterior: perde o CDI, fica no dólar, paga IOF+spread a cada ajuste) e o
    P&L é trazido/levado todo mês (IOF 0,38%/1,1% + spread 0,5%), exatamente como em cme_comum;
  - B3: a garantia é Tesouro Selic (rende CDI = benchmark) -> o excesso é só o ajuste diário menos os custos.
IR: exterior 15% anual (Lei 14.754/2023), B3 15% mensal (futuros_b3), via pf/ir.py com a CLASSE_IR declarada no fundo.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

PF = Path(__file__).resolve().parent.parent
for _p in (str(PF.parent), str(PF)):
    if _p not in sys.path:
        sys.path.insert(0, _p)
import comum as C  # noqa: E402
import pf  # noqa: E402

DADOS = PF / "dados" / "pf2_futuros"
QFD = PF.parent.parent / "fundos" / "dados"
PTAX_FULL = C.PTAX.ffill()
_CACHE = {}


def ler(nome, **kw):
    f = DADOS / nome
    if f.suffix == ".csv":
        x = pd.read_csv(f, index_col=0, parse_dates=True, **kw)
    else:
        x = pd.read_parquet(f, **kw)
    if isinstance(x.index, pd.DatetimeIndex):
        x.index = pd.DatetimeIndex(x.index).normalize().tz_localize(None) if x.index.tz is None else x.index.tz_convert(None).normalize()
        x = x[~x.index.duplicated(keep="last")].sort_index()
    return x


def memo(chave, objs, f):
    k = (chave,) + tuple(id(o) for o in objs)
    if k not in _CACHE or any(a is not b for a, b in zip(_CACHE[k][0], objs)):
        _CACHE[k] = (objs, f())
    if len(_CACHE) > 300:
        _CACHE.clear()
        _CACHE[k] = (objs, f())
    return _CACHE[k][1]


# ---------------------------------------------------------------- calendário e conversões
def dias_uteis(*series):
    """Calendário de segunda a sexta entre o 1º e o último dado das séries (nunca além do último dado: truncamento)."""
    ini = min(s.dropna().index.min() for s in series)
    fim = max(s.dropna().index.max() for s in series)
    return pd.bdate_range(ini, fim)


def nivel(s, idx):
    """Último valor conhecido até cada dia de idx (ffill)."""
    s = s.dropna()
    s = s[~s.index.duplicated(keep="last")]
    return s.reindex(idx.union(s.index)).ffill().reindex(idx)


def brl_por(moeda, idx, fx=None):
    """R$ por 1 unidade da moeda, no dia (PTAX x cruzado do Yahoo). fx = DataFrame do Yahoo (y_fx: 'EURUSD=X', 'JPY=X', ...)."""
    usd = nivel(PTAX_FULL, idx)
    if moeda == "BRL":
        return pd.Series(1.0, index=idx)
    if moeda == "USD":
        return usd
    col, inv = {"EUR": ("EURUSD=X", False), "JPY": ("JPY=X", True), "KRW": ("KRW=X", True), "MXN": ("MXN=X", True),
                "ZAR": ("ZAR=X", True)}[moeda]
    x = nivel(fx[col], idx)
    return usd * (1 / x if inv else x)


def juro_dia(taxa_aa_pct, idx):
    """Juro de política (% a.a.) vigente na véspera -> fração por dia corrido acumulada entre pregões (fins de semana carregam)."""
    j = nivel(taxa_aa_pct, idx).shift(1) / 100
    dias = pd.Series(idx, index=idx).diff().dt.days.fillna(1)
    return (j * dias / 365).fillna(0)


def para_b3(x):
    """Soma de valores diários (P&L em R$) do calendário de origem para os pregões da B3."""
    return pf.usd_para_br(x)


# ---------------------------------------------------------------- contrato genérico
def contrato(r_exc, nivel_loc, mult, moeda, idx, fx, custo_loc, margem, rol=4, local="ext", margem_fixa=False):
    """1 contrato comprado: DataFrame (índice idx) com
      pc     P&L em R$ no dia (retorno em excesso do dia x nocional da véspera em R$),
      noc    nocional em R$ no fechamento, margem (R$ por contrato: fração do nocional ou valor fixo em moeda local),
      r      retorno em excesso do dia, custo (R$ por lado por contrato), rol (rolagens/ano), local ('ext' IBKR / 'b3').
    r_exc: retorno em excesso diário (moeda local) no calendário idx; nivel_loc: nível do subjacente (para o nocional)."""
    b = brl_por(moeda, idx, fx)
    noc = nivel(nivel_loc, idx) * mult * b
    r = r_exc.reindex(idx)
    pc = noc.shift(1) * r
    mg = (pd.Series(float(margem), index=idx) * b) if margem_fixa else noc * margem
    return pd.DataFrame({"pc": pc, "noc": noc, "margem": mg, "r": r, "custo": custo_loc * b, "rol": float(rol), "local": local})


def vol_brl(K, janela=63):
    """Vol anual em R$ de 1 contrato, só com o passado."""
    return K["noc"] * K["r"].rolling(janela, min_periods=40).std() * np.sqrt(252)


def n_por_exposicao(K, capital, expo):
    """Nº INTEIRO de contratos para uma exposição-alvo (nocional/capital): arredonda; 0 se 1 contrato passar de 2x o alvo."""
    return np.floor(expo * capital / K["noc"] + .5).fillna(0)


# ---------------------------------------------------------------- livro: contratos -> excesso sobre o CDI
def livro(N, K, capital, custo_mult=1.0, lag=0, folga=1.5):
    """N: contratos decididos no fechamento de t (colunas = instrumentos, índice = calendário do mercado); K: dict inst -> contrato().
    Devolve dict com o excesso diário (fração do capital, pregões da B3) e as peças para o IR/atribuição."""
    idx = N.index
    Nx = N.fillna(0).shift(1 + lag).fillna(0)
    pnl_ext = pd.Series(0.0, index=idx)
    pnl_b3 = pd.Series(0.0, index=idx)
    mg_ext = pd.Series(0.0, index=idx)
    por = {}
    for a in N.columns:
        k = K[a].reindex(idx)
        pa = Nx[a].shift(1).fillna(0) * k["pc"].fillna(0)
        giro = Nx[a].diff().abs().fillna(Nx[a].abs()) + Nx[a].abs() * k["rol"].fillna(0) * 2 / 252
        ca = giro * k["custo"].ffill().fillna(0) * custo_mult
        por[a] = pa - ca
        if (k["local"] == "ext").any():
            pnl_ext += pa - ca
            mg_ext += Nx[a].abs() * k["margem"].ffill().fillna(0)
        else:
            pnl_b3 += pa - ca
    pe, pb = para_b3(pnl_ext), para_b3(pnl_b3)
    saldo = nivel(mg_ext, pf.DIAS).fillna(0)
    if saldo.abs().sum() > 0:
        total_conta, saldo_brl = pf.custo_conta_exterior(saldo, folga)
    else:
        total_conta, saldo_brl = pd.Series(0.0, index=pf.DIAS), pd.Series(0.0, index=pf.DIAS)
    s_ant = saldo_brl.shift(1).fillna(0)
    ganho_cambial = s_ant * pf.PTAX.pct_change(fill_method=None).fillna(0)
    cdi_perdido = s_ant * pf.CDI
    remessa_saldo = total_conta - cdi_perdido + ganho_cambial
    mes = pe.groupby(pe.index.to_period("M")).transform("sum")
    per = pd.Series(pe.index.to_period("M"), index=pe.index)
    fim = per.ne(per.shift(-1))
    rem = np.where(fim, np.where(mes < 0, -mes * (pf.REMESSA_IDA + pf.SPREAD_CAMBIO), mes * (pf.REMESSA_VOLTA + pf.SPREAD_CAMBIO)), 0)
    remessa_pnl = pd.Series(rem, index=pe.index) * custo_mult
    ex = (pe + pb - total_conta - remessa_pnl) / capital
    acum = ex.cumsum()
    if (acum <= -1).any():                                   # quebrou: o fundo para
        q = acum.index[acum <= -1][0]
        ex[ex.index > q] = 0
    return {"excesso": ex.fillna(0), "pnl_ext": pe, "pnl_b3": pb, "ganho_cambial": ganho_cambial, "cdi_perdido": cdi_perdido,
            "remessas": remessa_saldo + remessa_pnl, "saldo": saldo_brl, "Nx": Nx, "por_ativo": por}


def classes(L):
    return {"exterior": L["pnl_ext"], "futuros_b3": L["pnl_b3"],
            "isento": L["ganho_cambial"] - L["remessas"] - .85 * L["cdi_perdido"]}


def posicoes_de(N, K, capital):
    W, R = {}, {}
    for a in N.columns:
        k = K[a].reindex(N.index)
        W[a] = nivel(N[a].fillna(0) * k["noc"].ffill() / capital, pf.DIAS).fillna(0)
        R[a] = para_b3((k["pc"] / k["noc"].shift(1)).replace([np.inf, -np.inf], 0).fillna(0))
    return pd.DataFrame(W), pd.DataFrame(R)


def negocios_de(L, K, capital):
    linhas = []
    for a in L["Nx"].columns:
        h = L["Nx"][a].shift(1).fillna(0)
        lado = np.sign(h)
        grupo = (lado != lado.shift(1)).cumsum()
        r = (K[a]["pc"] / K[a]["noc"].shift(1)).reindex(h.index).replace([np.inf, -np.inf], 0).fillna(0)
        for _, x in h.groupby(grupo):
            s = np.sign(x.iloc[0])
            if s == 0:
                continue
            linhas.append({"ativo": a, "lado": int(s), "entrada": x.index[0], "saida": x.index[-1], "dias": len(x),
                           "contratos": float(x.abs().max()), "retorno_%": ((1 + s * r.reindex(x.index)).prod() - 1) * 100,
                           "contrib_pp": L["por_ativo"][a].reindex(x.index).sum() / capital * 100})
    return pd.DataFrame(linhas, columns=["ativo", "lado", "entrada", "saida", "dias", "contratos", "retorno_%", "contrib_pp"])


def segura(sinal, dias):
    """Liga 1 (ou o sinal) no dia do gatilho e mantém por `dias` pregões (o gatilho novo renova o prazo)."""
    s = sinal.fillna(0)
    out = s.copy()
    for k in range(1, dias):
        out = out.where(out != 0, s.shift(k).fillna(0))
    return out


# ---------------------------------------------------------------- API do contrato de fundo
def montar(g, gera, carrega):
    """g = globals() do fundo; gera(d, capital, regime, alavancagem, **params) -> (N, K)."""
    lanc = g.get("LANCAMENTO", {})

    def _N(d, capital, regime, alavancagem, params):
        params = {**g["PARAMS"], **params}
        regime = params.pop("regime", regime)
        N, K = gera(d, capital=capital, regime=regime, alavancagem=alavancagem, **params)
        N = N.copy().fillna(0)
        N[N.index < pd.Timestamp(g["INICIO"])] = 0
        for a in N.columns:
            if a in lanc:                                     # depois do corte, só opera o contrato depois de lançado
                N.loc[(N.index >= pd.Timestamp(g["CORTE"])) & (N.index < pd.Timestamp(lanc[a])), a] = 0
        return N, K

    def _livro(d, capital, custo_mult, lag, regime, alavancagem, params):
        N, K = _N(d, capital, regime, alavancagem, params)
        return livro(N, K, capital, custo_mult, lag, g.get("FOLGA", 1.5)), N, K

    def excesso(d, capital=20000, custo_mult=1, lag=0, regime=g["REGIME"], alavancagem=1, **params):
        regime = params.pop("regime", regime)
        e = _livro(d, capital, custo_mult, lag, regime, alavancagem, params)[0]["excesso"]
        return C.aplica_regime(e, regime, g["CUSTO_TROCA"] * custo_mult) if regime in ("dd_stop", "risco_global") else e

    def classes_ir(d, capital=20000, regime=g["REGIME"], alavancagem=1, **params):
        return classes(_livro(d, capital, 1, 0, regime, alavancagem, params)[0])

    def posicoes(d, capital=20000, **params):
        N, K = _N(d, capital, g["REGIME"], 1, params)
        return posicoes_de(N, K, capital)

    def negocios(d, capital=20000, **params):
        L, N, K = _livro(d, capital, 1, 0, g["REGIME"], 1, params)
        return negocios_de(L, K, capital)

    def livro_completo(d, capital=20000, regime=g["REGIME"], alavancagem=1, **params):
        return _livro(d, capital, 1, 0, regime, alavancagem, params)

    g.update(carrega=carrega, excesso=excesso, classes_ir=classes_ir, posicoes=posicoes, negocios=negocios, livro_completo=livro_completo)


# ---------------------------------------------------------------- sinais de índice (pânico / reversão / tendência), só com o passado
def sinal_indice(px, modo, k=2.0, H=5, medo=None, q=.9, janela=5):
    """px: nível do índice (calendário do mercado). Devolve o lado desejado decidido em t (+1 comprado, -1 vendido, 0 fora).
      panico   : retorno de `janela` dias <= -k desvios (vol de 1 ano) E índice de medo (V2X/VI) acima do quantil q de 1 ano -> compra H dias;
      reversao : retorno de `janela` dias <= -k desvios -> compra H dias; >= +k desvios -> vende H dias (sem filtro de medo);
      tendencia: comprado acima da média de 200 dias, vendido abaixo."""
    r = np.log(px).diff()
    if modo == "tendencia":
        return np.sign(px - px.rolling(200, min_periods=150).mean()).fillna(0)
    z = r.rolling(janela).sum() / (r.rolling(252, min_periods=150).std() * np.sqrt(janela))
    baixo = z <= -k
    if modo == "panico":
        m = nivel(medo, px.index)
        baixo &= m >= m.rolling(252, min_periods=150).quantile(q)
        return segura(baixo.astype(float), H)
    alto = (z >= k).astype(float)
    return segura(baixo.astype(float) - alto, H)
