"""
Peças comuns da frente "pf2_emergentes" (pf/fundos/em_*.py): emergentes e fronteira via ETFs/ADRs na IBKR (só o necessário fora).
Não altera comum.py / robustez.py / pf.py — premissas ficam aqui, com fonte.

DADOS: `pf/dados/pf2_emergentes/yahoo.parquet` (Yahoo, OHLC bruto + Adj Close + volume, baixado UMA vez por `baixa()`; os fundos só leem
o cache). Formato largo, colunas "campo|ticker". Calendário = união dos pregões dos ativos escolhidos (EUA, HK, Índia, Argentina...).
Mortos que o Yahoo não tem mais (RSX/ERUS Rússia, EGPT, NGE, PAK, FM, GXG/ICOL): ver `MORTOS` e o tratamento de sobrevivência nos fundos.

MOTOR (`livro`): pesos-alvo W (fração do capital em R$, com sinal) decididos no fechamento de t (calendário união); execução no 1º pregão
REAL do ativo a partir de t+1+lag (o HK executa no fechamento de HK, o ADR no fechamento de NY); resultado a partir do dia seguinte.
  - nº de ações fixado na execução (alvo x capital / preço da decisão), sem rebalanceio enquanto o alvo não muda;
    compra fracionária nos EUA (IBKR), venda a descoberto em ações inteiras; HK em lotes (board lot); posição marcada pelo Adj Close
    (proventos entram no retorno);
  - custos: IBKR Pro EUA US$ 0,0035/ação (mín. US$ 0,35, máx. 1%); HK 0,05% (mín. HK$ 18) + imposto do selo 0,1% (0,13% de ago/2021
    a nov/2023) + taxas ~0,0085%; meio spread por ativo (`MEIO_SPREAD`), multiplicado por vol21/vol252 (1x a 3x) — spread abre no pânico;
    aluguel a.a. por ativo vendido (arquivo de short da IBKR, varejo/MAPA_ATIVOS_EUA.md; não listados: 1% a.a. ADR grande, 3% pequeno);
  - conta IBKR só com o necessário: comprado à vista (conta cash) = valor das posições; com vendido = Reg T (50% de L+S, >= L-S,
    mín. US$ 2.000). pf.custo_conta_exterior (folga 1,05 sobre o maior exigido do mês anterior): perde CDI, câmbio, IOF 1,1% + spread
    na ida e 0,38% + spread na volta. O P&L em US$ vira R$ pela PTAX do dia e cai no pregão seguinte da B3;
  - conta="anual" (livros sempre ativos, ex. pares L/S): o saldo exigido é o maior dos últimos 12 meses, para não pagar IOF de ida e
    volta todo mês; conta="mensal" (eventos raros): a regra padrão de pf.custo_conta_exterior;
  - hedge_fx="wdo": o saldo em dólar na IBKR é hedgeado com mini-dólar vendido na B3 quando passa de US$ 8 mil (0,8 contrato):
    o "câmbio aberto sobre o capital" morreu na rodada anterior; com R$ 20 mil quase nunca há contrato, com R$ 50 mil às vezes;
  - alavancagem L multiplica os alvos; acima do patrimônio, o comprado é financiado pela IBKR (T-bill + 1,5% a.a.).
IR: classe "exterior" (15% ao ano sobre o ganho em R$, Lei 14.754/2023), com compensação no ano.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

PF = Path(__file__).resolve().parent.parent
RAIZ = PF.parent
for _p in (str(RAIZ), str(PF)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import comum as C  # noqa: E402
import pf  # noqa: E402

CACHE = PF / "dados" / "pf2_emergentes"
DIAS, CDI = C.DIAS, C.CDI.fillna(0)
PTAX = pf.PTAX
TB = C.TB_US

# ---------------------------------------------------------------- universo (Yahoo)
PAISES = ["EEM", "SPY", "TUR", "EWZ", "ARGT", "EZA", "EWW", "ECH", "EPU", "INDA", "EIDO", "VNM", "KSA", "EWY", "EWT", "THD", "EPHE",
          "EWM", "EPOL", "GREK", "MCHI", "FXI", "QAT", "UAE", "KWT", "AFK", "ECNS", "KWEB", "VNAM", "FRDM", "EWZS"]
ARG_ADR = {"YPF": ("YPFD.BA", 10), "GGAL": ("GGAL.BA", 10), "BMA": ("BMA.BA", 10), "PAM": ("PAMP.BA", 25), "CEPU": ("CEPU.BA", 10),
           "TEO": ("TECO2.BA", 5), "TGS": ("TGSU2.BA", 5), "EDN": ("EDN.BA", 20), "LOMA": ("LOMA.BA", 5), "SUPV": ("SUPV.BA", 5),
           "CRESY": ("CRES.BA", 10), "IRS": ("IRSA.BA", 10), "BBAR": ("BBAR.BA", 3)}
HK_PAR = {"BABA": ("9988.HK", 8, 100), "JD": ("9618.HK", 2, 50), "BIDU": ("9888.HK", 8, 50), "NTES": ("9999.HK", 5, 100),
          "BILI": ("9626.HK", 1, 20), "TCOM": ("9961.HK", 1, 50), "NIO": ("9866.HK", 1, 100), "LI": ("2015.HK", 2, 100),
          "XPEV": ("9868.HK", 2, 100), "BEKE": ("2423.HK", 3, 100), "ZTO": ("2057.HK", 1, 50), "YUMC": ("9987.HK", 1, 50)}   # ADR: (HK, ações por ADR, lote)
IN_PAR = {"INFY": ("INFY.NS", 1), "HDB": ("HDFCBANK.NS", 3), "IBN": ("ICICIBANK.NS", 2), "WIT": ("WIPRO.NS", 1), "RDY": ("DRREDDY.NS", 1)}
COMMOD = ["EC", "SCCO", "BVN", "SQM", "TX", "BNO", "USO", "CPER", "GLD", "SLV", "GDX", "XLE", "COPX"]
EXPORT = ["GFI", "HMY", "SBSW", "DRD", "SSL", "AU", "ASR", "PAC", "OMAB", "TKC", "CIB"]
FX = ["ARS=X", "HKD=X", "INR=X", "ZAR=X", "MXN=X", "TRY=X", "COP=X", "CLP=X", "IDR=X", "PHP=X", "THB=X", "MYR=X", "VND=X", "PLN=X",
      "PEN=X", "SAR=X", "BRL=X", "KRW=X", "TWD=X", "CNY=X"]
LOCAIS = ["XU100.IS", "^JKSE", "PSEI.PS", "^SET.BK", "^KLSE", "^JN0U.JO", "^NSEI", "WIG20.WA", "E1VFVN30.VN", "^MXX", "^BVSP", "^IPSA",
          "^SPBLPGPT", "^MERV", "^KS11", "^TWII", "^VIX"]
MORTOS = ["RSX", "ERUS", "EGPT", "NGE", "PAK", "FM", "FRN", "GXG", "ICOL", "EMFM", "AFTY"]

# meio spread típico (fração) fora do pânico — estimativa de varejo (spreads cotados de ETFs/ADRs; mais largo nos pequenos)
MEIO_SPREAD = {"EEM": .0001, "SPY": .00005, "EWZ": .0001, "EWW": .0001, "INDA": .0001, "FXI": .0001, "MCHI": .0001, "KWEB": .0002,
               "EZA": .0003, "TUR": .0005, "ECH": .0005, "EIDO": .0005, "EWY": .0001, "EWT": .0001, "THD": .0005, "EWM": .0005,
               "EPHE": .0007, "EPOL": .0005, "GREK": .0007, "KSA": .0005, "VNM": .0007, "EPU": .0010, "ARGT": .0010, "QAT": .0020,
               "UAE": .0020, "KWT": .0030, "AFK": .0030, "ECNS": .0020, "VNAM": .0030, "FRDM": .0010, "EWZS": .0010,
               "YPF": .0005, "GGAL": .0005, "BMA": .0008, "PAM": .0008, "CEPU": .0010, "TEO": .0015, "TGS": .0010, "EDN": .0020,
               "LOMA": .0020, "SUPV": .0020, "CRESY": .0020, "IRS": .0020, "BBAR": .0015,
               "BABA": .0001, "JD": .0002, "BIDU": .0002, "NTES": .0003, "BILI": .0004, "TCOM": .0003, "NIO": .0003, "LI": .0003,
               "XPEV": .0004, "BEKE": .0004, "ZTO": .0004, "YUMC": .0004,
               "INFY": .0002, "HDB": .0002, "IBN": .0002, "WIT": .0005, "RDY": .0005,
               "EC": .0008, "SCCO": .0004, "BVN": .0008, "SQM": .0005, "TX": .0006, "BNO": .0005, "USO": .0002, "CPER": .0010,
               "GLD": .00005, "SLV": .0001, "GDX": .0001, "XLE": .00005, "COPX": .0005,
               "GFI": .0004, "HMY": .0005, "SBSW": .0006, "DRD": .0010, "SSL": .0010, "AU": .0004, "ASR": .0008, "PAC": .0008,
               "OMAB": .0010, "TKC": .0015, "CIB": .0006}
MEIO_SPREAD_HK = .0005       # HK large caps (spread de 1 tick em HK$ 100+ ~ 0,05–0,1%)
# aluguel a.a. para vender (IBKR usa.txt 15/10/2026 quando no mapa; demais premissa conservadora)
ALUGUEL = {"EEM": .0025, "SPY": .0025, "EWZ": .003, "EWW": .003, "INDA": .003, "MCHI": .004, "FXI": .004, "BNO": .005, "USO": .003,
           "CPER": .0028, "GLD": .0043, "SLV": .0042, "GDX": .0042, "COPX": .0045, "XLE": .0025, "EZA": .005}
ALUGUEL_PADRAO, ALUGUEL_HK = .01, .015
REG_T_MIN = 2_000.0
FOLGA_CONTA = 1.05


# ---------------------------------------------------------------- download (uma vez) e leitura
def todos():
    t = PAISES + list(ARG_ADR) + [v[0] for v in ARG_ADR.values()] + list(HK_PAR) + [v[0] for v in HK_PAR.values()]
    t += list(IN_PAR) + [v[0] for v in IN_PAR.values()] + COMMOD + EXPORT + FX + LOCAIS + MORTOS
    return list(dict.fromkeys(t))


def baixa(forca=False):
    """Baixa do Yahoo (yfinance) e grava o cache. Só roda se o arquivo não existir (ou forca=True)."""
    f = CACHE / "yahoo.parquet"
    if f.exists() and not forca:
        return
    import yfinance as yf
    tk = todos()
    partes = []
    for i in range(0, len(tk), 25):
        x = yf.download(tk[i:i + 25], start="2005-01-01", end="2026-10-15", auto_adjust=False, progress=False, threads=True,
                        group_by="column")
        x.columns = [f"{a}|{b}" for a, b in x.columns]
        partes.append(x)
    X = pd.concat(partes, axis=1)
    X.index = pd.DatetimeIndex(X.index).tz_localize(None).normalize()
    X = X[~X.index.duplicated(keep="last")].sort_index()
    X = X.loc[:, X.notna().any()]
    CACHE.mkdir(parents=True, exist_ok=True)
    X.to_parquet(f, compression="zstd")
    (CACHE / "tickers_tentados.txt").write_text(" ".join(tk), encoding="utf-8")


_Y = {}


def yahoo():
    if "x" not in _Y:
        baixa()
        _Y["x"] = pd.read_parquet(CACHE / "yahoo.parquet")
    return _Y["x"]


def seleciona(tickers, extra=None):
    """Dados brutos dos tickers pedidos (calendário = dias em que algum deles negociou). Devolve dict de DataFrames por data."""
    X = yahoo()
    tk = [t for t in dict.fromkeys(tickers) if f"Close|{t}" in X]
    g = lambda campo: X[[f"{campo}|{t}" for t in tk if f"{campo}|{t}" in X]].rename(columns=lambda c: c.split("|")[1])
    raw = g("Close")
    raw = raw.loc[raw.notna().any(axis=1)]
    adj = g("Adj Close").reindex(raw.index).reindex(columns=tk)
    adj = adj.fillna(raw)                                  # índices/moedas: Adj Close = Close
    vol = g("Volume").reindex(raw.index).reindex(columns=tk)
    d = {"raw": raw, "adj": adj, "vol": vol}
    if extra:
        d.update(extra)
    return d


# ---------------------------------------------------------------- utilidades de sinal (só passado)
def moeda(t):
    if t.endswith(".HK"):
        return "HKD=X"
    if t.endswith(".NS"):
        return "INR=X"
    if t.endswith(".BA"):
        return "ARS=X"
    return None


def preco_usd(d, col="adj"):
    """Preço em US$ (local / moeda por US$), ffill. Índices/moedas ficam como estão."""
    P = d[col].ffill()
    for t in P.columns:
        m = moeda(t)
        if m is not None and m in d["raw"]:
            P[t] = P[t] / d["raw"][m].ffill()
    return P


def negociou(d):
    """True no dia em que o ativo teve fechamento (e volume > 0 quando há volume)."""
    ok = d["raw"].notna()
    v = d["vol"].reindex_like(ok)
    return ok & ~(v.notna() & (v <= 0))


def maquina(entra, sai, max_dias, espera=0):
    """Estado 0/1 por coluna: abre quando `entra` (t), fica até `sai` ou `max_dias` dias; não reabre no dia em que saiu."""
    E, S = entra.fillna(False).to_numpy(bool), sai.fillna(False).to_numpy(bool)
    out = np.zeros(E.shape)
    for j in range(E.shape[1]):
        dentro, idade, pausa = False, 0, 0
        for i in range(E.shape[0]):
            if dentro:
                idade += 1
                if S[i, j] or idade >= max_dias:
                    dentro, pausa = False, espera
                else:
                    out[i, j] = 1.0
                continue
            if pausa > 0:
                pausa -= 1
                continue
            if E[i, j]:
                dentro, idade = True, 0
                out[i, j] = 1.0
    return pd.DataFrame(out, index=entra.index, columns=entra.columns)


def congela(x, estado):
    """Valor de x no dia da entrada, mantido enquanto o estado está ligado (peso fixo por negócio)."""
    ent = (estado > 0) & (estado.shift(1).fillna(0) <= 0)
    return x.where(ent).ffill().where(estado > 0, 0.0).fillna(0.0)


def limita(W, teto=1.0):
    """Soma dos |pesos| <= teto (corta proporcionalmente)."""
    s = W.abs().sum(axis=1)
    return W.mul((teto / s).clip(upper=1).fillna(1), axis=0)


def beta_rolante(y, X, jan=252, minp=126, lim=(0, 3)):
    """Beta de y (Series) contra cada coluna de X (DataFrame, regressão simples por coluna, univariada), só passado (até t)."""
    out = {}
    for c in X.columns:
        cov = y.rolling(jan, min_periods=minp).cov(X[c])
        var = X[c].rolling(jan, min_periods=minp).var()
        out[c] = (cov / var).clip(*lim)
    return pd.DataFrame(out)


# ---------------------------------------------------------------- motor PF (IBKR)
def _custo_hk(val, data):
    selo = np.where((data >= pd.Timestamp("2021-08-01")) & (data < pd.Timestamp("2023-11-17")), .0013, .001)
    com = np.maximum(.0005 * val, 18 / 7.8)
    return np.where(val > 0, com + val * (selo + .000085), 0.0)


def livro(d, W, capital=20000, lag=0, custo_mult=1.0, alavancagem=1.0, lotes=None, spread_extra=None, conta="mensal", hedge_fx="wdo"):
    """W: pesos-alvo (fração do capital, com sinal) decididos no fechamento de t, índice = calendário de d['raw'].
    Devolve dict: e (excesso diário sobre o CDI, calendário da B3), classes, Q (ações), Pusd, pnl_ativo_brl, idx, fx, saldo."""
    idx = d["raw"].index
    W = (W.reindex(idx).fillna(0) * alavancagem)
    cols = list(W.columns)
    Pu = preco_usd(d).reindex(columns=cols)
    neg = negociou(d).reindex(columns=cols).fillna(False)
    fx = PTAX.reindex(idx.union(PTAX.index)).ffill().reindex(idx).bfill()
    lotes = lotes or {}
    # alvo vigente a partir do dia de execução (t+1+lag); ações fixadas com o preço da decisão
    Wex = W.shift(1 + lag).fillna(0)
    Pdec, fxdec = Pu.shift(1 + lag), fx.shift(1 + lag)
    muda = Wex.ne(Wex.shift(1).fillna(0))
    alvo_sh = (Wex * capital).div(fxdec, axis=0) / Pdec
    alvo_sh = alvo_sh.where(Wex != 0, 0.0)
    for c in cols:
        lote = lotes.get(c, 1 if not c.endswith(".HK") else 100)
        a = alvo_sh[c]
        if c.endswith(".HK"):
            a = np.round(a / lote) * lote                     # lotes inteiros em HK (o fundo já dimensiona em lotes)
        else:
            a = a.where(a > 0, np.trunc(a))                   # vendido: ações inteiras; comprado: fracionário
        alvo_sh[c] = a
    Q = alvo_sh.where(muda).ffill().fillna(0)                 # desejado
    Q = Q.where(neg).ffill().fillna(0)                        # só executa em pregão real do ativo
    Q = Q.fillna(0)
    Qv, Pv = Q.to_numpy(), np.nan_to_num(Pu.ffill().to_numpy())
    Qp = np.vstack([np.zeros((1, Qv.shape[1])), Qv[:-1]])
    dP = np.vstack([np.zeros((1, Pv.shape[1])), np.diff(Pv, axis=0)])
    pnl = Qp * dP
    dQ = np.abs(np.diff(np.vstack([np.zeros((1, Qv.shape[1])), Qv]), axis=0))
    val = dQ * Pv
    # spread abre no pânico: vol de 21d / mediana da vol de 252d (até t-1), entre 1x e 3x
    r = Pu.ffill().pct_change(fill_method=None)
    v21 = r.rolling(21, min_periods=10).std()
    mult = (v21 / v21.rolling(252, min_periods=60).median()).shift(1).clip(1, 3).fillna(1).to_numpy()
    hs = np.array([(MEIO_SPREAD_HK if c.endswith(".HK") else MEIO_SPREAD.get(c, .002)) for c in cols])
    if spread_extra is not None:
        hs = hs * spread_extra
    cst = val * hs * mult
    datas = np.asarray(idx)
    for j, c in enumerate(cols):
        if c.endswith(".HK"):
            cst[:, j] += _custo_hk(val[:, j], idx)
        else:
            cst[:, j] += pf.custo_ordem_ibkr_usd(val[:, j], np.where(Pv[:, j] > 0, Pv[:, j], 1.0))
    alug = np.array([(ALUGUEL_HK if c.endswith(".HK") else ALUGUEL.get(c, ALUGUEL_PADRAO)) for c in cols])
    Pprev = np.vstack([Pv[:1], Pv[:-1]])
    cst += np.clip(-Qp, 0, None) * Pprev * alug / 252
    cst *= custo_mult
    V = Qv * Pv
    L, S = np.clip(V, 0, None).sum(axis=1), np.clip(-V, 0, None).sum(axis=1)
    cap_usd = capital / fx.to_numpy()
    req = np.where(S > 0, np.maximum(np.maximum(.5 * (L + S), L - S), REG_T_MIN), L)
    req = np.where(S > 0, req, np.minimum(req, np.maximum(cap_usd, .5 * L)))       # acima do patrimônio: margem da IBKR
    divida = np.where(S > 0, 0.0, np.clip(L - req, 0, None))
    tb = TB.reindex(idx.union(TB.index)).ffill().reindex(idx).fillna(0).to_numpy()
    juros = np.r_[0, divida[:-1]] * (tb + .015 / 252) * custo_mult
    pnl_usd = pnl.sum(axis=1) - cst.sum(axis=1) - juros
    pnl_brl = pd.Series(pnl_usd * fx.to_numpy(), index=idx)
    ativo_brl = pd.DataFrame((pnl - cst) * fx.to_numpy()[:, None], index=idx, columns=cols)
    exig = pd.Series(req * fx.to_numpy(), index=idx)
    exig = exig.reindex(DIAS.union(idx)).ffill().reindex(DIAS).fillna(0) * 1.02
    if conta == "anual":                                   # livro sempre ativo: deixa na IBKR o maior exigido dos últimos 12 meses
        exig = exig.rolling(252, min_periods=1).max()      # (evita ida e volta mensal com IOF; só passado)
    conta, saldo = pf.custo_conta_exterior(exig, folga=FOLGA_CONTA)
    perd = saldo.shift(1).fillna(0) * CDI
    ganho = saldo.shift(1).fillna(0) * PTAX.pct_change(fill_method=None).fillna(0)
    remessa = (conta - perd + ganho) * custo_mult
    ext = pf.usd_para_br(pnl_brl) + ganho - remessa
    wdo, n_wdo = hedge_wdo(saldo, lag, custo_mult) if hedge_fx == "wdo" else (pd.Series(0.0, index=DIAS), pd.Series(0.0, index=DIAS))
    e = (ext - perd + wdo) / capital
    return {"e": e, "classes": {"exterior": ext, "futuros_b3": wdo, "_cdi_perdido": perd}, "wdo": wdo, "n_wdo": n_wdo, "Q": Q, "Pusd": Pu.ffill(), "ativo_brl": ativo_brl, "idx": idx,
            "fx": fx, "saldo": saldo, "exig": exig, "cambio": ganho, "remessa": remessa, "W": W}


WDO_CUSTO = 1.20 + 2.50       # R$ por contrato e lado: corretagem/emolumentos (pf.CONTRATOS) + meio tick (0,25 ponto x R$ 10)


def hedge_wdo(saldo_brl, lag=0, custo_mult=1.0):
    """Hedge do saldo em dólar na IBKR com mini-dólar vendido (B3, US$ 10 mil por contrato, garantia em Tesouro Selic):
    n = piso(saldo em US$ / 10 mil + 0,2) — só hedgeia a partir de US$ 8 mil, nunca sobre-hedgeia mais que 25% (com round(), US$ 5 mil
    viravam 1 contrato de US$ 10 mil: metade seria aposta vendida em dólar = carry do real, o db3_wdo_carry reprovado); decidido com o saldo de t e executado em t+1+lag. P&L diário de n vendidos ~
    -n x 10 mil x (ΔPTAX - PTAX x (CDI - T-bill)) — o vendido ganha o cupom (diferencial de juros) embutido no futuro. Rolagem mensal
    (2 lados). Com R$ 20 mil o saldo nunca chega a US$ 8 mil; com R$ 50 mil só quando quase todo o capital está na IBKR."""
    S = PTAX.reindex(DIAS).ffill()
    tb = TB.reindex(DIAS.union(TB.index)).ffill().reindex(DIAS).fillna(0)
    n = -np.floor(saldo_brl / S / 10_000 + .2).fillna(0)      # nunca mais que ~25% acima do saldo (arredondar para cima viraria aposta no real)
    n = n.shift(1 + lag).fillna(0)
    np_ = n.shift(1).fillna(0)
    pnl = np_ * 10_000 * (S.diff().fillna(0) - S.shift(1).fillna(S) * (CDI - tb))
    mes = pd.Series(DIAS.to_period("M"), index=DIAS)
    rola = (mes != mes.shift(1)) & (np_ != 0)
    custo = (n.diff().abs().fillna(n.abs()) + rola * 2 * np_.abs()) * WDO_CUSTO * custo_mult
    return pnl - custo, n


# ---------------------------------------------------------------- contrato: posicoes / negocios a partir do livro
def para_b3(x, como="ultimo"):
    x = x[~x.index.duplicated(keep="last")]
    return x.reindex(DIAS.union(x.index)).ffill().reindex(DIAS)


def posicoes_de(res, capital):
    """Pesos (valor/capital, decididos na véspera da execução) e retorno do ativo em R$ menos CDI, no calendário da B3."""
    Pbrl = res["Pusd"].mul(res["fx"], axis=0)
    V = (res["Q"] * Pbrl) / capital
    Wb = para_b3(V).fillna(0).shift(-1).fillna(0)
    R = para_b3(Pbrl).pct_change(fill_method=None).fillna(0).sub(CDI, axis=0)
    return Wb, R


def negocios_de(res, capital, rotulo=None):
    """Um negócio por trecho contínuo de posição com o mesmo sinal: entrada/saída (datas de execução), retorno do ativo em US$ e
    contribuição (P&L em R$ do ativo no trecho, com custos, / capital, em pp)."""
    Q, P, A, idx = res["Q"], res["Pusd"], res["ativo_brl"], res["idx"]
    lin = []
    for c in Q.columns:
        q = Q[c].to_numpy()
        s = np.sign(q)
        i = 0
        n = len(q)
        while i < n:
            if s[i] == 0:
                i += 1
                continue
            j = i
            while j + 1 < n and s[j + 1] == s[i]:
                j += 1
            k = min(j + 1, n - 1)                              # dia em que zerou (execução da saída)
            p0, p1 = P[c].iloc[i], P[c].iloc[k]
            lin.append({"ativo": c, "lado": int(s[i]), "entrada": idx[i], "saida": idx[k], "dias": int(k - i),
                        "retorno_%": float((p1 / p0 - 1) * 100 * s[i]) if p0 > 0 else np.nan,
                        "contrib_pp": float(A[c].iloc[i:k + 1].sum() / capital * 100),
                        **({"grupo": rotulo.get(c, c)} if rotulo else {})})
            i = j + 1
    return pd.DataFrame(lin, columns=["ativo", "lado", "entrada", "saida", "dias", "retorno_%", "contrib_pp"] + (["grupo"] if rotulo else []))


def eem_brl(d=None):
    """Retorno do EEM em R$ (sem hedge) menos CDI, calendário da B3 — para separar beta de alfa."""
    X = yahoo()
    p = X["Adj Close|EEM"].dropna()
    p.index = pd.DatetimeIndex(p.index)
    pb = para_b3(p * PTAX.reindex(p.index.union(PTAX.index)).ffill().reindex(p.index))
    return pb.pct_change(fill_method=None).fillna(0) - CDI


def beta_alfa(e, inicio="2021-01-01"):
    """Regressão do excesso diário (sobre o CDI) no excesso do EEM em R$: beta, alfa a.a. (pp), R²."""
    x = eem_brl().reindex(e.index).fillna(0)
    y = e.fillna(0)
    m = y.index >= pd.Timestamp(inicio)
    x, y = x[m], y[m]
    b = np.cov(y, x)[0, 1] / x.var() if x.var() > 0 else np.nan
    a = (y - b * x).mean() * 252 * 100
    r2 = np.corrcoef(y, x)[0, 1] ** 2 if y.std() > 0 else np.nan
    return {"beta EEM": b, "alfa a.a. pp": a, "R2": r2}


# ---------------------------------------------------------------- casca comum dos fundos (excesso/classes/posicoes/negocios)
_CACHE = {}


def roda(mod, d, capital=20000, custo_mult=1, lag=0, alavancagem=1, **kw):
    """Chama mod._pesos(d, **params) -> (W, opções do livro) e o livro PF; cache por (dados, parâmetros)."""
    p = {**mod.PARAMS, **kw}
    k = (mod.__name__, id(d), d["raw"].index[-1], len(d["raw"]), capital, custo_mult, lag, alavancagem,
         tuple(sorted((a, str(b)) for a, b in p.items())))
    if k in _CACHE:
        return _CACHE[k]
    W, opc = mod._pesos(d, capital=capital, **p) if "capital" in mod._pesos.__code__.co_varnames else mod._pesos(d, **p)
    res = livro(d, W, capital, lag, custo_mult, alavancagem, **opc)
    if hasattr(mod, "_ajuste"):
        res = mod._ajuste(d, res, capital, alavancagem, **p)
    if len(_CACHE) > 80:
        _CACHE.clear()
    _CACHE[k] = res
    return res


def contrato(mod):
    """Gera excesso/classes_ir/posicoes/negocios padrão no módulo."""
    def excesso(d, capital=20000, custo_mult=1, lag=0, regime=None, alavancagem=1, **params):
        e = roda(mod, d, capital, custo_mult, lag, alavancagem, **params)["e"]
        return C.aplica_regime(e, mod.REGIME if regime is None else regime, mod.CUSTO_TROCA * custo_mult)

    def classes_ir(d, capital=20000, **params):
        return roda(mod, d, capital, **params)["classes"]

    def posicoes(d, capital=20000, **params):
        return posicoes_de(roda(mod, d, capital, **params), capital)

    def negocios(d, capital=20000, **params):
        res = roda(mod, d, capital, **params)
        ng = negocios_de(res, capital, getattr(mod, "ROTULO", None))
        extra = res.get("negocios_extra")
        return pd.concat([ng, extra], ignore_index=True) if extra is not None else ng

    return excesso, classes_ir, posicoes, negocios


def pre_corrigido(p, salto=.15):
    """Série de prêmio em log sem os saltos de razão/desdobramento (|variação diária| > salto vira degrau removido) — só passado."""
    dp = p.diff()
    s = dp.where(dp.abs() > salto, 0.0).fillna(0.0).cumsum()
    return p - s


def panico_mercado(d_eem, d_vix):
    """Pânico de mercado (só passado): VIX no 1/5 mais alto do último ano OU EEM 10% abaixo do topo de 63 dias."""
    v = d_vix.ffill()
    e = d_eem.ffill()
    return (v >= v.rolling(252, min_periods=126).quantile(.8)) | (e / e.rolling(63, min_periods=20).max() - 1 <= -.10)


def limita_n(est, n, prioridade=None):
    """No máximo n posições abertas: um trecho ligado de `est` só entra se houver vaga no dia da entrada (prioridade maior primeiro);
    trecho recusado fica fora inteiro (sem entrar no meio). Só passado."""
    E_ = est.to_numpy() > 0
    Pr = prioridade.reindex_like(est).fillna(0).to_numpy() if prioridade is not None else np.zeros(E_.shape)
    T, N = E_.shape
    out = np.zeros((T, N))
    ativo = np.zeros(N, bool)
    recus = np.zeros(N, bool)
    for i in range(T):
        for j in range(N):
            if not E_[i, j]:
                ativo[j] = recus[j] = False
        novos = [j for j in range(N) if E_[i, j] and not ativo[j] and not recus[j]]
        vagas = n - int(ativo.sum())
        for j in sorted(novos, key=lambda j: -Pr[i, j]):
            if vagas > 0:
                ativo[j], vagas = True, vagas - 1
            else:
                recus[j] = True
        out[i] = ativo
    return pd.DataFrame(out, index=est.index, columns=est.columns)


def limpa_saltos(s, lim=.25):
    """Remove pontos que saltam mais que `lim` (em log) contra o último valor ACEITO (erros do Yahoo do tipo x10/÷10 por um dia).
    Só passado: o ponto é julgado contra o histórico, nunca contra o dia seguinte."""
    x = s.to_numpy(dtype=float).copy()
    ult = np.nan
    for i in range(len(x)):
        if not np.isfinite(x[i]) or x[i] <= 0:
            x[i] = np.nan
            continue
        if np.isfinite(ult) and abs(np.log(x[i] / ult)) > lim:
            x[i] = np.nan
            continue
        ult = x[i]
    return pd.Series(x, index=s.index)
