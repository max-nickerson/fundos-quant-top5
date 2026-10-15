"""
Peças comuns da frente "micro_cme": futuros MICRO da CME/Cboe na IBKR, mandando para fora SÓ a margem (o resto do capital fica em R$ no CDI).

Como cada contrato é simulado (sem saltos de rolagem do contínuo do Yahoo):
  - o RETORNO vem de um ativo sem rolagem: ETF com proventos (SPY, QQQ, IWM, GLD, SLV, CPER, USO) menos o T-bill (futuro = excesso sobre o juro
    em US$), somando de volta a taxa de administração do ETF; moedas = spot + diferencial de juros de política (BIS) — é exatamente o que o
    futuro de moeda paga (paridade coberta); juros = variação do yield constante do FRED (US$ 10 por bp) + carregamento (yield − Fed funds)
    convertido em bp; VIX = o PRÓPRIO vencimento do VX (Cboe) carregado até a rolagem; cripto = spot − base anualizada do CME (contango pago
    por quem está comprado).
  - o NÍVEL (índice/futuro do Yahoo) entra só para o TAMANHO do contrato (nocional = nível x multiplicador) e para a margem.
  - custo por lado = comissão IBKR + taxas da bolsa + meio spread (ticks); rolagem = 2 lados por contrato nas datas de rolagem (como fração
    anual: rolagens/ano / 252 por dia).

Conta no exterior (`pf.custo_conta_exterior`): saldo-alvo na IBKR = margem inicial (folga 1,5x o maior mês anterior). Esse saldo perde o CDI,
fica no dólar e paga IOF + spread a cada ajuste. O P&L dos futuros é liquidado em R$ todo mês (perda: remete com IOF 1,1% + spread; ganho: volta
com IOF 0,38% + spread) — premissa conservadora; deixar o lucro lá fora evitaria parte desse custo mas aumentaria o saldo exposto ao dólar.

Premissas corrigidas em relação a `pf.CONTRATOS` (fontes: especificações CME Group/Cboe CFE e tabela de margens/comissões IBKR, out/2026):
  - custo de pf.CONTRATOS é só comissão; aqui somamos o MEIO SPREAD (1 tick na maioria dos micros, 2 ticks em micro FX/VXM, que são pouco líquidos).
  - MJY (Micro JPY/USD, 1.250.000 ienes) existe e é o micro de iene; liquidez muito baixa -> 2 ticks de meio spread.
  - 10Y e 2YY (Micro Treasury Yield, US$ 10 por bp): margem fixa ~US$ 400 e 300 por contrato (pf.CONTRATOS usa 30% de "nocional", que não
    faz sentido para contrato cotado em yield).
  - 1OZ (1-Ounce Gold, desde jan/2023) incluído: é o único ouro que cabe em R$ 20 mil (1 contrato ≈ US$ 4 mil).
  - VXM: margem ~45% do nocional (IBKR ~US$ 750-860 com VIX ~16); custo US$ 5,5 por lado (comissão + ~1 tick).
  - Contratos que só existem desde 2019-2023 (MES/MNQ/M2K mai/2019; MHG ago/2021 ... ) são simulados ANTES do lançamento com o mesmo
    subjacente (o tamanho é o do micro): resultado anterior ao lançamento é hipotético (liquidez de micro não existia).
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

PF = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PF.parent))
sys.path.insert(0, str(PF))
import comum as C  # noqa: E402
import pf  # noqa: E402

DADOS = PF / "dados" / "micro_cme"
PTAX_FULL = C.PTAX.ffill()

# mult = US$ por ponto; margem = fração do nocional (ou US$ fixos se 'margem_usd'); com = comissão+taxas US$/lado; tick_meio = meio spread US$/lado
ESPEC = {
    "MES": dict(mult=5, nivel="^GSPC", ret="SPY", taxa=.0009, margem=.07, com=.62, tick_meio=.625, rol=4),
    "MNQ": dict(mult=2, nivel="^NDX", ret="QQQ", taxa=.002, margem=.08, com=.62, tick_meio=.5, rol=4),
    "M2K": dict(mult=5, nivel="^RUT", ret="IWM", taxa=.0019, margem=.08, com=.62, tick_meio=.5, rol=4),
    "MGC": dict(mult=10, nivel="GC=F", ret="GLD", taxa=.004, margem=.06, com=.85, tick_meio=1.0, rol=6),
    "1OZ": dict(mult=1, nivel="GC=F", ret="GLD", taxa=.004, margem=.07, com=.85, tick_meio=.5, rol=6),
    "SIL": dict(mult=1000, nivel="SI=F", ret="SLV", taxa=.005, margem=.09, com=.85, tick_meio=5.0, rol=5),
    "MHG": dict(mult=2500, nivel="HG=F", ret="CPER", taxa=.0075, margem=.07, com=.85, tick_meio=1.25, rol=5),
    "MCL": dict(mult=100, nivel="CL=F", ret="USO", taxa=.006, margem=.12, com=.85, tick_meio=1.0, rol=12),
    # moedas: spot em US$ por unidade (inv=True: série do Yahoo em unidades por US$) + juro de política do BIS
    "M6E": dict(mult=12_500, fx="EURUSD=X", inv=False, bis="XM", margem=.025, com=.40, tick_meio=2.5, rol=4),
    "M6B": dict(mult=6_250, fx="GBPUSD=X", inv=False, bis="GB", margem=.03, com=.40, tick_meio=2.5, rol=4),
    "M6A": dict(mult=10_000, fx="AUDUSD=X", inv=False, bis="AU", margem=.035, com=.40, tick_meio=2.5, rol=4),
    "MCD": dict(mult=10_000, fx="CAD=X", inv=True, bis="CA", margem=.025, com=.40, tick_meio=2.5, rol=4),
    "MSF": dict(mult=12_500, fx="CHF=X", inv=True, bis="CH", margem=.035, com=.40, tick_meio=2.5, rol=4),
    "MJY": dict(mult=1_250_000, fx="JPY=X", inv=True, bis="JP", margem=.035, com=.40, tick_meio=2.5, rol=4),
    # juros (yield): US$ 10 por bp; duração para converter o carregamento em bp
    "10Y": dict(mult=1000, yld="DGS10", dur=8.0, margem_usd=400, com=.62, tick_meio=1.0, rol=12),
    "2YY": dict(mult=1000, yld="DGS2", dur=1.9, margem_usd=300, com=.62, tick_meio=1.0, rol=12),
    # cripto (CME): 0,1 BTC / 0,1 ETH
    "MBT": dict(mult=.1, spot="BTC-USD", fut="BTC=F", margem=.40, com=2.5, tick_meio=1.0, rol=12),
    "MET": dict(mult=.1, spot="ETH-USD", fut="ETH=F", margem=.40, com=.5, tick_meio=.25, rol=12),
    # VXM (Cboe): US$ 100 x VIX, vencimento mensal
    "VXM": dict(mult=100, margem=.45, com=1.5, tick_meio=4.0, rol=12),
}


def carrega():
    return {"precos": pd.read_parquet(DADOS / "precos.parquet"), "fx": pd.read_parquet(DADOS / "fx_spot.parquet"),
            "bis": pd.read_csv(DADOS / "bis_juros_politica.csv", index_col=0, parse_dates=True),
            "vx": pd.read_csv(DADOS / "vx.csv", parse_dates=["data", "venc"]),
            "binance": pd.read_parquet(DADOS / "binance_base.parquet")}


# ---------------------------------------------------------------- calendário dos EUA
def dias_us(d):
    p = d["precos"]
    return p.index[p["SPY"].notna()]


def para(s, idx, soma=True):
    """Leva uma série de outro calendário para `idx`: soma (retornos/P&L) ou último valor (níveis)."""
    s = s.copy()
    s.index = pd.DatetimeIndex(s.index).normalize()
    if not soma:
        return s[~s.index.duplicated(keep="last")].reindex(idx.union(s.index)).ffill().reindex(idx)
    a = s.fillna(0).cumsum()
    a = a[~a.index.duplicated(keep="last")].reindex(idx.union(a.index)).ffill().reindex(idx).fillna(0)
    return a.diff().fillna(a.iloc[0] if len(a) else 0)


def tbill_dia(idx):
    return C.TB_US.reindex(idx, method="ffill").fillna(0)


# ---------------------------------------------------------------- base anualizada dos futuros de cripto
def _ultima_sexta_trimestre(t):
    m = ((t.month - 1) // 3 + 1) * 3
    fim = pd.Timestamp(t.year, m, 1) + pd.offsets.MonthEnd(0)
    return fim - pd.Timedelta(days=(fim.dayofweek - 4) % 7)


BASE_ANTES = .05      # base anualizada assumida antes de ago/2020 (sem futuro com fechamento no mesmo horário do spot)


def base_cripto(d, moeda, idx):
    """Base anualizada paga por quem está COMPRADO no futuro: futuro trimestral da Binance (fechamento 0h UTC, o mesmo do spot) / spot − 1,
    x 365 / dias até o vencimento (última sexta do trimestre), mediana de 21 dias, limitada a [−20%, +60%]. O CME BTC=F do Yahoo fecha
    16h CT e o spot 0h UTC: a diferença de horário gera ruído de ±2% por dia — inútil para medir base de 0,3-1% ao mês. A base do CME
    costuma ficar 1-3 p.p. a.a. acima da Binance (institucional comprado); usamos a da Binance + 1 p.p. Antes de ago/2020: 5% a.a."""
    x = d["binance"]
    F, S = x[f"{moeda}USD_trim"], x[f"{moeda}USDT"].reindex(x.index)
    venc = pd.Series([_ultima_sexta_trimestre(t) for t in x.index], index=x.index)
    dte = (venc - x.index.to_series()).dt.days.clip(lower=7)
    b = ((F / S - 1) * 365 / dte).clip(-.2, .6).rolling(21, min_periods=5).median() + .01
    b = para(b.dropna(), idx, soma=False)
    return b.where(idx >= pd.Timestamp("2020-09-01"), BASE_ANTES)


# ---------------------------------------------------------------- VX: o próprio vencimento carregado (sem salto de rolagem)
def vx_carregado(d, idx, venc_ordem=1, rolar_dias=5):
    """Contrato VX segurado em t: o `venc_ordem`-ésimo vencimento com mais de `rolar_dias` pregões até o vencimento, escolhido com a data
    de t−1 (calendário: vencimentos já listados). Devolve DataFrame: dF (variação do contrato segurado de t−1 para t), nivel (ajuste do
    contrato segurado), rola (True no dia em que troca de contrato), vx1, vx2 (1º e 2º vencimentos em t)."""
    p = d["vx"].pivot(index="data", columns="venc", values="ajuste").reindex(idx)
    vencs = np.array(sorted(p.columns))
    pos = np.arange(len(idx))
    escolha = []
    for i, t in enumerate(idx):
        lim = t + pd.Timedelta(days=round(rolar_dias * 7 / 5))           # só calendário (sem olhar pregões futuros)
        ok = vencs[vencs > np.datetime64(lim)]
        escolha.append(ok[venc_ordem - 1] if len(ok) >= venc_ordem else pd.NaT)
    escolha = pd.Series(escolha, index=idx)
    seg = escolha.shift(1)                                         # contrato segurado em t foi escolhido em t−1
    col = {v: j for j, v in enumerate(p.columns)}
    P = p.values
    hoje = np.array([P[i, col[v]] if pd.notna(v) and v in col else np.nan for i, v in zip(pos, seg)])
    ontem = np.array([P[i - 1, col[v]] if i > 0 and pd.notna(v) and v in col else np.nan for i, v in zip(pos, seg)])
    nivel = np.array([P[i, col[v]] if pd.notna(v) and v in col else np.nan for i, v in zip(pos, escolha)])
    p1 = []
    p2 = []
    for i, t in enumerate(idx):
        ok = vencs[vencs >= np.datetime64(t)]
        p1.append(P[i, col[ok[0]]] if len(ok) > 0 else np.nan)
        p2.append(P[i, col[ok[1]]] if len(ok) > 1 else np.nan)
    out = pd.DataFrame({"dF": hoje - ontem, "nivel": nivel, "vx1": p1, "vx2": p2}, index=idx)
    out["rola"] = escolha.ne(escolha.shift(1)).values
    out["dF"] = out["dF"].fillna(0)
    out[["nivel", "vx1", "vx2"]] = out[["nivel", "vx1", "vx2"]].ffill()
    return out


# ---------------------------------------------------------------- P&L de 1 contrato comprado (US$/dia, calendário dos EUA)
def contrato(d, inst, idx=None, venc_ordem=1):
    """Devolve DataFrame (índice = pregões dos EUA): pc = P&L em US$ de 1 contrato comprado no dia (posição do fechamento anterior),
    noc = nocional de 1 contrato em US$ no fechamento (para tamanho), margem = margem inicial em US$ por contrato."""
    e = ESPEC[inst]
    idx = dias_us(d) if idx is None else idx
    p = d["precos"]
    tb = tbill_dia(idx)
    if "ret" in e:
        r = p[e["ret"]].reindex(idx).pct_change(fill_method=None) - tb + e["taxa"] / 252   # NaN antes do ETF existir
        noc = para(p[e["nivel"]], idx, soma=False).clip(lower=10 if inst == "MCL" else 0) * e["mult"]
        pc = noc.shift(1) * r
    elif "fx" in e:
        s = d["fx"][e["fx"]].dropna()
        s = 1 / s if e["inv"] else s
        s = para(s, idx, soma=False)
        juros = d["bis"].reindex(idx, method="ffill")
        dif = (juros[e["bis"]] - juros["US"]).shift(1) / 100 / 252     # juro de política vigente na véspera
        dias = pd.Series(idx, index=idx).diff().dt.days.fillna(1) * 252 / 365   # fins de semana/feriados também carregam
        r = s.pct_change(fill_method=None).fillna(0) + dif.fillna(0) * dias
        noc = s * e["mult"]
        pc = noc.shift(1) * r
    elif "yld" in e:
        y = para(p[e["yld"]].dropna(), idx, soma=False)
        ff = para(p["DFF"].dropna(), idx, soma=False)
        carry_bp = ((y - ff) / e["dur"] * 100 / 252).shift(1)          # bp por dia a favor de quem está VENDIDO em yield (comprado no título)
        pc = 10.0 * (y.diff() * 100 - carry_bp)                        # comprado em yield: ganha US$ 10 por bp de alta, paga o carregamento
        noc = pd.Series(10.0 / (e["dur"] * 1e-4), index=idx)          # título equivalente em DV01 (US$ 10/bp): 10Y ≈ US$ 12,5 mil; 2Y ≈ US$ 53 mil
        r = pc / noc                                                   # retorno de estar VENDIDO no título equivalente
    elif "spot" in e:
        s = para(p[e["spot"]].dropna(), idx, soma=False)
        b = base_cripto(d, e["spot"][:3], idx)
        dias = pd.Series(idx, index=idx).diff().dt.days.fillna(1)
        r = s.pct_change(fill_method=None).fillna(0) - (b.shift(1) * dias / 365).fillna(0)
        noc = s * e["mult"]
        pc = noc.shift(1) * r
        pc[idx < pd.Timestamp("2017-12-18")] = np.nan                  # futuro de BTC do CME começou em 18/12/2017
    elif inst == "VXM":
        v = vx_carregado(d, idx, venc_ordem)
        noc = v["nivel"] * e["mult"]
        pc = v["dF"] * e["mult"]
        r = pc / (v["nivel"].shift(1) * e["mult"])
        extra = {"_rola": v["rola"].astype(float), "vx1": v["vx1"], "vx2": v["vx2"]}
    mg = pd.Series(float(e["margem_usd"]), index=idx) if "margem_usd" in e else noc * e["margem"]
    out = pd.DataFrame({"pc": pc, "noc": noc, "margem": mg, "r": r}, index=idx)
    if inst == "VXM":
        out = out.assign(**extra)
    return out


def custo_lado(inst):
    e = ESPEC[inst]
    return e["com"] + e["tick_meio"]


# ---------------------------------------------------------------- tamanho em contratos INTEIROS
def vol_contrato_brl(K, janela=63):
    """Vol anual em R$ de 1 contrato (estimada só com o passado até t): nocional x vol do retorno x PTAX."""
    v = K["r"].rolling(janela, min_periods=40).std() * np.sqrt(252)
    return (K["noc"] * v * PTAX_FULL.reindex(K.index, method="ffill")).rename(None)


def inteiros_gulosos(score, vol1, corr, orcamento, maxn=20):
    """Contratos inteiros para um vetor de sinais: adiciona 1 contrato por vez, na ordem de |sinal|, enquanto a vol ex-ante da carteira
    (vol de 1 contrato em R$ e correlação) couber no orçamento (R$ de vol anual). Devolve vetor de inteiros com o sinal do score."""
    n = np.zeros(len(score))
    ordem = [i for i in np.argsort(-np.abs(score)) if score[i] != 0 and np.isfinite(vol1[i]) and vol1[i] > 0]
    mudou = True
    while mudou:
        mudou = False
        for i in ordem:
            if abs(n[i]) >= maxn:
                continue
            m = n.copy()
            m[i] += np.sign(score[i])
            v = m * vol1
            if np.sqrt(max(v @ corr @ v, 0)) <= orcamento:
                n, mudou = m, True
    return n


# ---------------------------------------------------------------- livro: contratos -> excesso sobre o CDI em R$
def livro(d, N, K, capital, custo_mult=1.0, lag=0, folga=1.5):
    """N: contratos decididos no fechamento de t (pregões dos EUA; colunas = instrumentos); K: dict inst -> contrato(d, inst).
    Execução no fechamento de t+1+lag; P&L a partir do dia seguinte. Devolve dict com séries em R$ no calendário da B3."""
    idx = N.index
    fx = PTAX_FULL.reindex(idx, method="ffill")
    Nx = N.fillna(0).shift(1 + lag).fillna(0)
    pnl = pd.Series(0.0, index=idx)
    custo = pd.Series(0.0, index=idx)
    mg = pd.Series(0.0, index=idx)
    por = {}
    for a in N.columns:
        k = K[a]
        pa = (Nx[a].shift(1).fillna(0) * k["pc"].fillna(0))
        ca = (Nx[a].diff().abs().fillna(Nx[a].abs()) + Nx[a].abs() * ESPEC[a]["rol"] * 2 / 252) * custo_lado(a) * custo_mult
        if a == "VXM" and "_rola" in k:                                # VXM: rolagem nos dias reais de troca de vencimento
            ca = (Nx[a].diff().abs().fillna(Nx[a].abs()) + Nx[a].shift(1).abs().fillna(0) * k["_rola"] * 2) * custo_lado(a) * custo_mult
        pnl += pa * fx
        custo += ca * fx
        mg += Nx[a].abs() * k["margem"].ffill().fillna(0)
        por[a] = (pa - ca) * fx
    pnl_b, custo_b = pf.usd_para_br(pnl), pf.usd_para_br(custo)
    saldo = (para(mg, pf.DIAS, soma=False).fillna(0) * pf.PTAX).fillna(0)
    total_conta, saldo_brl = pf.custo_conta_exterior(saldo, folga)
    s_usd_brl = saldo_brl.shift(1).fillna(0)
    fx_ret = pf.PTAX.pct_change(fill_method=None).fillna(0)
    ganho_cambial = s_usd_brl * fx_ret
    cdi_perdido = s_usd_brl * pf.CDI
    remessa_saldo = total_conta - cdi_perdido + ganho_cambial
    liq = pnl_b - custo_b
    mes = liq.groupby(liq.index.to_period("M")).transform("sum")
    fim = pd.Series(liq.index.to_period("M"), index=liq.index)
    fim = fim.ne(fim.shift(-1))
    remessa_pnl = np.where(fim, np.where(mes < 0, -mes * (pf.REMESSA_IDA + pf.SPREAD_CAMBIO), mes * (pf.REMESSA_VOLTA + pf.SPREAD_CAMBIO)), 0)
    remessa_pnl = pd.Series(remessa_pnl, index=liq.index) * custo_mult
    ex = (liq - total_conta - remessa_pnl) / capital
    # quebra: se o P&L acumulado consumir o capital, o fundo para (fica no CDI com o que sobrou = zero)
    acum = (ex.cumsum())
    if (acum <= -1).any():
        q = acum.index[acum <= -1][0]
        ex[ex.index > q] = 0
    return {"excesso": ex.fillna(0), "pnl_ext": liq, "ganho_cambial": ganho_cambial, "cdi_perdido": cdi_perdido,
            "remessas": remessa_saldo + remessa_pnl, "saldo": saldo_brl, "Nx": Nx, "por_ativo": por}


def classes(L):
    """IR: P&L dos futuros no exterior = 15% ao ano com compensação (Lei 14.754/2023). Variação cambial de saldo NÃO remunerado no exterior
    é isenta (art. da mesma lei); remessas (IOF/spread) não são dedutíveis; o CDI que deixou de ser ganho custaria 15% de IR -> entra x0,85."""
    return {"exterior": L["pnl_ext"], "isento": L["ganho_cambial"] - L["remessas"] - .85 * L["cdi_perdido"]}


def apos_ir(cls, capital):
    return pf.apos_ir_por_classe(cls, capital) / capital


# ---------------------------------------------------------------- posicoes / negocios (para a bateria)
def posicoes_de(N, K, capital):
    """W: pesos decididos em t (nocional/capital, no calendário da B3); R: retorno em excesso por nocional, no calendário da B3."""
    W, R = {}, {}
    for a in N.columns:
        k = K[a]
        w = N[a].fillna(0) * k["noc"].ffill() * PTAX_FULL.reindex(N.index, method="ffill") / capital
        W[a] = para(w, pf.DIAS, soma=False).fillna(0)
        R[a] = pf.usd_para_br((k["pc"] / k["noc"].shift(1)).replace([np.inf, -np.inf], 0).fillna(0))
    return pd.DataFrame(W), pd.DataFrame(R)


def negocios_de(L, K, capital):
    """Um negócio = sequência de dias com posição do mesmo sinal (aumentos/reduções no mesmo lado ficam no mesmo negócio; no VXM, cada vencimento)."""
    linhas = []
    for a in L["Nx"].columns:
        h = L["Nx"][a].shift(1).fillna(0)                              # posição que rende no dia
        lado = np.sign(h)
        quebra = lado != lado.shift(1)
        if "_rola" in K[a]:                                            # VXM: cada vencimento carregado é um negócio
            quebra |= K[a]["_rola"].reindex(h.index).fillna(0).astype(bool)
        grupo = quebra.cumsum()
        r = (K[a]["pc"] / K[a]["noc"].shift(1)).replace([np.inf, -np.inf], 0).fillna(0)
        for g, x in h.groupby(grupo):
            s = np.sign(x.iloc[0])
            if s == 0:
                continue
            linhas.append({"ativo": a, "lado": int(s), "entrada": x.index[0], "saida": x.index[-1], "dias": len(x),
                           "contratos": float(x.abs().max()), "retorno_%": ((1 + s * r.reindex(x.index)).prod() - 1) * 100,
                           "contrib_pp": L["por_ativo"][a].reindex(x.index).sum() / capital * 100})
    return pd.DataFrame(linhas, columns=["ativo", "lado", "entrada", "saida", "dias", "contratos", "retorno_%", "contrib_pp"])


def ultimo_do_mes(idx):
    p = pd.Series(idx.to_period("M"), index=idx)
    return p.ne(p.shift(-1)).values


# lançamento de cada micro (CME/Cboe). Antes do corte OOS a simulação usa o mesmo subjacente (hipotético); DEPOIS do corte o fundo só
# negocia o contrato a partir do lançamento.
LANCAMENTO = {"MES": "2019-05-06", "MNQ": "2019-05-06", "M2K": "2019-05-06", "MHG": "2021-08-16", "MCL": "2021-07-12", "1OZ": "2023-01-09",
              "10Y": "2021-08-16", "2YY": "2021-08-16", "MBT": "2021-05-03", "MET": "2021-12-06", "VXM": "2020-08-10"}


# ---------------------------------------------------------------- cache (a bateria chama excesso ~150 vezes com os mesmos dados)
_CACHE = {}


def contratos(d, insts, idx=None, venc_ordem=1):
    out = {}
    for a in insts:
        chave = (id(d["precos"]), id(d["fx"]), id(d["vx"]), id(d["binance"]), a, venc_ordem if a == "VXM" else 0)
        if chave not in _CACHE or _CACHE[chave][0] is not d["precos"]:
            _CACHE[chave] = (d["precos"], contrato(d, a, idx, venc_ordem))
        out[a] = _CACHE[chave][1]
    if len(_CACHE) > 400:
        _CACHE.clear()
    return out


def regime_risco(idx):
    """comum.regime_risco_global (VIX < p80 de 1 ano, S&P > média 200d, HYG/IEF > média 100d) levado aos pregões dos EUA; liga se >= 2/3."""
    return (C.regime_risco_global().reindex(idx, method="ffill").fillna(1) >= .66).astype(float)


# ---------------------------------------------------------------- API do contrato de fundo (gera excesso/classes_ir/posicoes/negocios)
def montar(g, gera):
    """g = globals() do módulo do fundo; gera(d, capital, regime, alavancagem, **params) -> (N, K) com N em contratos decididos em t."""
    def _livro(d, capital, custo_mult, lag, regime, alavancagem, params):
        params = {**g["PARAMS"], **params}
        regime = params.pop("regime", regime)                          # o regime pode estar na grade (escolhido no IS como parâmetro)
        N, Kd = gera(d, capital=capital, regime=regime, alavancagem=alavancagem, **params)
        N = N.copy()
        N[N.index < pd.Timestamp(g["INICIO"])] = 0
        for a in N.columns:
            if a in LANCAMENTO:
                N.loc[(N.index >= pd.Timestamp(g["CORTE"])) & (N.index < pd.Timestamp(LANCAMENTO[a])), a] = 0
        return livro(d, N, Kd, capital, custo_mult, lag, g.get("FOLGA", 1.5)), N, Kd

    def excesso(d, capital=20000, custo_mult=1, lag=0, regime=g["REGIME"], alavancagem=1, **params):
        regime = params.pop("regime", regime)
        e = _livro(d, capital, custo_mult, lag, regime, alavancagem, params)[0]["excesso"]
        return C.aplica_regime(e, regime, g["CUSTO_TROCA"] * custo_mult) if regime in ("dd_stop", "risco_global") else e

    def classes_ir(d, capital=20000, regime=g["REGIME"], alavancagem=1, **params):
        return classes(_livro(d, capital, 1, 0, regime, alavancagem, params)[0])

    def posicoes(d, capital=20000, **params):
        params = {**g["PARAMS"], **params}
        regime = params.pop("regime", g["REGIME"])
        N, Kd = gera(d, capital=capital, regime=regime, alavancagem=1, **params)
        N = N.copy()
        N[N.index < pd.Timestamp(g["INICIO"])] = 0
        for a in N.columns:
            if a in LANCAMENTO:
                N.loc[(N.index >= pd.Timestamp(g["CORTE"])) & (N.index < pd.Timestamp(LANCAMENTO[a])), a] = 0
        return posicoes_de(N, Kd, capital)

    def negocios(d, capital=20000, **params):
        L, N, Kd = _livro(d, capital, 1, 0, g["REGIME"], 1, params)
        return negocios_de(L, Kd, capital)

    def livro_completo(d, capital=20000, regime=g["REGIME"], alavancagem=1, **params):
        return _livro(d, capital, 1, 0, regime, alavancagem, params)

    g.update(carrega=carrega, excesso=excesso, classes_ir=classes_ir, posicoes=posicoes, negocios=negocios, livro_completo=livro_completo)
