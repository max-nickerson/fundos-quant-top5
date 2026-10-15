"""
Peças comuns da frente "pf2_cripto" (cripto para pessoa física brasileira; arquivos pf/fundos/cr_*.py). Não altera comum.py/pf.py.

REGULAÇÃO E ROTAS (verificado em out/2026; fontes no caderno pf/pesquisa/pf2_cripto.md):
  - Corretora brasileira (Mercado Bitcoin, Foxbit, Binance BR, Bitso...): à vista em R$, ISENÇÃO de IR para vendas de cripto ≤ R$ 35 mil/mês
    (IN RFB 1.888/2019; Lei 8.981/95 art. 21 c/c IN 1.888). A MP 1.303/2025 (17,5% sem isenção) caducou em 08/10/2025 -> regra antiga vale
    em 2026. Classe IR "cripto" (pf/ir.py: mensal, 15%, isenção 35 mil).
  - Marco do BCB (Res. 519/520/521, nov/2025, vigência 02/02/2026): SPSAVs autorizadas até 30/10/2026; operações com stablecoin em moeda
    estrangeira, transferências internacionais e carteiras autocustodiadas viram operação de CÂMBIO. Proposta de IOF de 3,5% na compra de
    cripto/stablecoin (isento até R$ 10 mil/mês para PF) em consulta — NÃO vigente; testado como sensibilidade onde importa.
  - Derivativos de cripto (perpétuos) para residente: a CVM proibiu a Binance de ofertar futuros a brasileiros (Ato Declaratório 17.961/2020).
    Em 2026 a Binance migrou os brasileiros para a entidade local e deixou derivativos só via "conta internacional" (Abu Dhabi), fora da
    supervisão de CVM/BCB; margem/empréstimo cortados a partir de 27/10/2026. A Bybit encerrou derivativos para brasileiros (2026, migração
    para entidade local em 24/09/2026). OKX ainda opera, sem confirmar pedido de SPSAV. => perpétuo para PF = conta offshore, risco de
    contraparte e regulatório; IR como aplicação no exterior (Lei 14.754/2023, 15% anual, classe "exterior").
  - B3: BIT (bitcoin em R$, 0,01 BTC desde 16/06/2025; 0,1 antes), ETR (0,25 ETH, cotado em US$) e SOL (5 SOL, em US$) desde 16/06/2025;
    ETFs HASH11/QBTC11/BITH11/QETH11/ETHE11/SOLH11/QSOL11 (15% sem isenção). IBKR: MBT/MET (0,1 BTC/ETH) na CME.

DADOS (pf/dados/pf2_cripto/, gerados por `python pf/fundos/cr_comum.py baixa`; o backtest não usa internet):
  binance_1h.parquet    candles de 1h (fechamento, volume em US$) de ~85 pares USDT da Binance, INCLUSIVE deslistados (LUNA, FTT, SRM...,
                        do arquivo público data.binance.vision), 2017-08 a 2026-10. Índice = HORA DE FECHAMENTO do candle (UTC).
  funding.parquet       taxa de financiamento 8h dos perpétuos USDT-M da Binance (BTC, ETH, SOL, BNB, XRP, DOGE), 2019-09+
  spot_perp_d.parquet   fechamento diário (00h UTC) spot e perpétuo dos mesmos (mesma corretora, mesmo instante)
  lido_apy.csv          APY diário do stETH (Lido) — DefiLlama
  listagens.parquet     1º candle diário de todo par USDT listado na Binance desde 2019 + 120 dias de fechamento (inclui deslistados)
"""
import io
import sys
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd

PF = Path(__file__).resolve().parent.parent
for _p in (str(PF), str(PF.parent), str(Path(__file__).resolve().parent)):
    if _p not in sys.path:
        sys.path.insert(0, _p)
import comum as C  # noqa: E402
import pf  # noqa: E402

DADOS = PF / "dados" / "pf2_cripto"
GC = PF / "dados" / "global_cripto"
DIAS, CDI, PTAX = C.DIAS, C.CDI.fillna(0), pf.PTAX
CDI_D = CDI.reindex(DIAS).fillna(0)

# Universo candidato (pares USDT que estiveram entre os maiores em algum momento; inclui os que morreram/renomearam).
# A seleção de cada estratégia é por VOLUME passado (ponto no tempo), não por esta lista.
UNIVERSO = ("BTC ETH BNB XRP ADA SOL DOGE DOT MATIC POL LTC BCH BCC BCHABC LINK AVAX TRX XLM EOS ETC XMR ATOM UNI FIL VET VEN NEO IOTA "
            "XTZ ICP SHIB NEAR APT ARB OP SUI TON PEPE WIF TIA SEI INJ HBAR ALGO THETA AAVE FTM S LUNA FTT EGLD SAND MANA AXS GALA CRV "
            "WAVES ZEC DASH QTUM ONT ZIL ENJ CHZ KSM COMP MKR SNX GRT RUNE STX IMX RNDR RENDER WLD FET JUP ENA BONK TAO TRUMP ONDO SRM "
            "BTT HNT CAKE KAVA").split()
ESTAVEIS = {"USDC", "BUSD", "TUSD", "FDUSD", "DAI", "USDP", "PAX", "USDS", "EUR", "GBP", "AUD", "UST", "USTC", "SUSD", "USDSB", "AEUR",
            "EURI", "XUSD", "USD1", "BFUSD", "PAXG", "WBTC", "WBETH", "BETH"}
_CACHE = {}


def ler(nome):
    if nome not in _CACHE:
        f = DADOS / nome
        _CACHE[nome] = pd.read_csv(f, index_col=0, parse_dates=True) if f.suffix == ".csv" else pd.read_parquet(f)
    return _CACHE[nome]


# ================================================================ calendário: cripto (24x7, UTC) -> pregões da B3
def hora_fech_b3_utc(d):
    return 20 if pd.Timestamp(d).tz_localize("America/New_York").dst().total_seconds() > 0 else 21


_FECH = None


def fech_b3():
    """Instante (UTC, sem tz) do fechamento de cada pregão da B3."""
    global _FECH
    if _FECH is None:
        _FECH = pd.DatetimeIndex([d + pd.Timedelta(hours=hora_fech_b3_utc(d)) for d in DIAS])
    return _FECH


def balde(ts):
    """Para cada instante UTC (fechamento de um candle), o pregão da B3 em que o resultado entra: o 1º pregão cujo fechamento é >= ts.
    Fim de semana/feriado vai para o pregão seguinte. Nenhum resultado entra num pregão ANTES de acontecer (truncamento ok)."""
    F = fech_b3()
    i = F.searchsorted(pd.DatetimeIndex(ts), side="left")
    i = np.minimum(i, len(DIAS) - 1)
    return DIAS[i]


def para_dias(s, how="sum"):
    """Série horária/diária UTC -> pregões da B3 (soma para P&L; 'last' para níveis/posições)."""
    s = s.dropna() if how == "last" else s.fillna(0)
    if not len(s):
        return pd.Series(0.0 if how == "sum" else np.nan, index=DIAS)
    g = s.groupby(balde(s.index))
    out = g.sum() if how == "sum" else g.last()
    out = out.reindex(DIAS)
    return out.fillna(0) if how == "sum" else out.ffill()


def fx_horario(idx):
    """R$ por US$ em cada hora: USDTBRL da Binance (desde 10/2020) e PTAX antes (o USDT carrega 0,2–0,7% de ágio local; medido)."""
    return memo(("fx", len(idx), str(idx[0]), str(idx[-1])), lambda: _fx_horario(idx)).copy()


def _fx_horario(idx):
    c = pd.read_parquet(GC / "cripto_br.parquet")
    u = c[(c.fonte == "BN") & (c.sym == "USDTBRL") & (c.res == "1h")].set_index("data").fech
    u.index = u.index + pd.Timedelta(hours=1)                     # hora de fechamento
    u = u[~u.index.duplicated()]
    p = PTAX.dropna()
    p.index = p.index + pd.Timedelta(hours=16)                    # PTAX sai ~13h de Brasília
    base = p.reindex(p.index.union(idx)).ffill().reindex(idx)
    uu = u.reindex(u.index.union(idx)).ffill(limit=6).reindex(idx)
    return uu.where(uu.notna() & (idx >= u.index.min()), base)


# ================================================================ preços
_MEMO = {}


def memo(chave, f):
    """Cache em memória (a bateria chama excesso() dezenas de vezes com os mesmos dados; a chave inclui o tamanho/fim dos dados, então
    os dados truncados do teste de look-ahead geram entradas próprias)."""
    if chave not in _MEMO:
        if len(_MEMO) > 40:
            _MEMO.clear()
        _MEMO[chave] = f()
    return _MEMO[chave]


def painel_1h(campo="fech", d=None):
    """Data x símbolo (sem 'USDT'), índice = hora de FECHAMENTO do candle (UTC)."""
    x = d["h"] if d is not None else ler("binance_1h.parquet")
    tt = x["t"] if "t" in x.columns else x.index

    def f():
        p = x.pivot_table(index="t", columns="sym", values=campo, aggfunc="last", observed=True).sort_index()
        p.columns = [str(c).replace("USDT", "") for c in p.columns]
        return p
    return memo(("painel", campo, len(x), str(tt.max())), f).copy()


def diario_de_1h(P, V=None):
    """Fechamento às 00h UTC e volume do dia (US$) a partir do 1h; dia = data do fechamento (00h UTC do dia seguinte ao do pregão)."""
    Pd = P[P.index.hour == 0]
    if V is None:
        return Pd
    Vd = V.resample("D", label="right", closed="right").sum(min_count=1)
    return Pd, Vd.reindex(Pd.index)


def mata_saltos(P, gap_h=48):
    """Preço com buraco > gap_h horas (deslistagem/relançamento, ex.: LUNA em 05/2022 -> LUNA 2.0) vira série nova: o retorno através do
    buraco NÃO é contado e quem estava posicionado sai no último preço antes do buraco (o motor zera a posição sem preço)."""
    out = P.copy()
    for c in P.columns:
        s = P[c].dropna()
        if len(s) < 2:
            continue
        gaps = s.index.to_series().diff() > pd.Timedelta(hours=gap_h)
        for t in s.index[gaps.values]:
            out.loc[t, c] = np.nan                                  # primeiro preço depois do buraco não gera retorno
    return out


def retornos(P):
    """Retorno simples entre preços consecutivos; NaN sem preço (posição sem preço não rende e é zerada pelo motor)."""
    return P / P.shift(1) - 1


# ================================================================ motor genérico (pesos-alvo em fração do capital, frações de moeda)
def motor(W, R, capital, custo_lado, lag_passos=1, custo_mult=1.0, fx_r=None, rebal=None):
    """W: pesos-alvo decididos no FECHAMENTO do passo t (DataFrame no índice de R). Executa no fechamento de t+lag_passos (lag_passos=1 é
    o "t+1" do contrato; com passos de 1h, t+1 = próxima hora). R: retornos por passo (US$ se fx_r dado; o capital é em R$).
    Comprar e SEGURAR: na execução a posição vale w x capital; depois o valor flutua com o preço (sem rebalanceamento) até o alvo mudar.
    Ativo sem preço (deslistado / buraco) -> posição zerada no último preço.
    Devolve dict: E (alvo executado), V (valor em R$ no fim do passo), pnl (R$ por ativo e passo, já sem custo), custo, expo (R$ no início)."""
    W = W.reindex(R.index).fillna(0)
    E = W.shift(lag_passos).fillna(0)
    E = E.where(R.notna() | (E == 0), 0)                          # sem preço neste passo -> posição zerada (sai no último preço)
    Rr = R.fillna(0)
    if fx_r is not None:
        Rr = (1 + Rr).mul(1 + fx_r.reindex(R.index).fillna(0), axis=0) - 1
    Rr = Rr.clip(lower=-.999)
    ini = E.ne(E.shift(1).fillna(0))                              # passo em que a posição é (re)feita
    if rebal is not None:                                         # rebalanceamento: volta ao peso-alvo mesmo sem mudar o alvo
        rb = rebal.reindex(R.index).fillna(False).astype(bool).shift(lag_passos).fillna(False).astype(bool)
        ini = ini | (E.ne(0) & rb.values[:, None])
    Lg = np.log1p(Rr).where(~ini, 0)
    Cs = Lg.cumsum()
    G = np.exp(Cs - Cs.where(ini).ffill().fillna(0))
    V = E * capital * G
    V0 = V.shift(1).fillna(0)
    bruto = V0 * Rr
    giro = (V - (V0 + bruto)).abs().where(ini, 0)
    cus = giro * custo_lado * custo_mult
    return {"E": E, "V": V, "pnl": bruto - cus, "custo": cus, "expo": V0.abs()}


def excesso_spot(M, capital, rende_cdi=False):
    """Resultado do motor -> excesso diário sobre o CDI (fração do capital) no calendário da B3. Dinheiro em cripto à vista NÃO rende CDI:
    cobra o CDI do pregão sobre a exposição média do balde do pregão. Devolve (excesso, exposição média diária em R$)."""
    p = para_dias(M["pnl"].sum(axis=1))
    ex = M["expo"].sum(axis=1)
    ex = ex.groupby(balde(ex.index)).mean().reindex(DIAS).fillna(0)
    return (p - (0 if rende_cdi else ex * CDI_D)) / capital, ex


def negocios_blocos(E, PNL, capital, R=None, extra=None):
    """Um negócio por bloco contíguo de posição não nula (por ativo). PNL: R$ por passo e ativo (já com custos), atribuído ao bloco da
    posição que o gerou (passo seguinte ao da posição). retorno_% = soma dos retornos do ativo no bloco (no sentido da posição)."""
    L = []
    for a in E.columns:
        w = E[a].fillna(0)
        on = (w != 0) | (w.shift(1).fillna(0) != 0)                 # passo de saída (custo) pertence ao bloco
        if not (w != 0).any():
            continue
        ini = (w != 0) & (w.shift(1).fillna(0) == 0)
        bloco = ini.cumsum().where(on)
        pa = PNL[a].fillna(0)
        rr = R[a].fillna(0) if R is not None else None
        for b, g in pa.groupby(bloco):
            idx = g.index
            lado = int(np.sign(w.loc[idx[0]]))
            ret = float(((1 + rr.loc[idx].iloc[1:].clip(lower=-.999)).prod() - 1) * lado * 100) if rr is not None else np.nan
            L.append({"ativo": a, "lado": lado, "entrada": balde([idx[0]])[0], "saida": balde([idx[-1]])[0],
                      "dias": max((idx[-1] - idx[0]).days, 0), "retorno_%": ret, "contrib_pp": float(g.sum() / capital * 100)})
    cols = ["ativo", "lado", "entrada", "saida", "dias", "retorno_%", "contrib_pp"]
    return pd.DataFrame(L)[cols] if L else pd.DataFrame(columns=cols)


def W_diario(E, R=None):
    """Posição executada (passos UTC) -> pesos no calendário da B3 (último valor do pregão) e retorno diário por ativo (para posicoes())."""
    Wd = E.groupby(balde(E.index)).last().reindex(DIAS).ffill().fillna(0)
    if R is None:
        return Wd
    Rd = np.expm1(np.log1p(R.fillna(0).clip(lower=-.99)).groupby(balde(R.index)).sum().reindex(DIAS).fillna(0))
    return Wd, Rd.sub(CDI_D, axis=0)


def W_com_vendas(V, R, capital):
    """Para posicoes(): pesos diários = exposição média do pregão (fração do capital) + duas colunas técnicas '_vendas_a/_b' (retorno 0)
    cujas reduções somam as VENDAS reais de cripto do pregão (giro intradiário que o peso de fim de dia não mostra). O motor de IR
    (pf/ir.vendas_mensais_de_pesos) soma as reduções -> vendas do mês (isenção de R$ 35 mil). Conta um pouco a mais (conservador)."""
    b = balde(V.index)
    Wd = (V.abs().groupby(b).mean().reindex(DIAS).fillna(0)) / capital
    dV = V.diff().fillna(V)
    vend = (-dV.clip(upper=0)).sum(axis=1)
    vend = vend.groupby(b).sum().reindex(DIAS).fillna(0) / capital
    par = np.arange(len(DIAS)) % 2 == 0
    Wd["_vendas_a"] = np.where(par, vend, 0)
    Wd["_vendas_b"] = np.where(~par, vend, 0)
    Rd = np.expm1(np.log1p(R.fillna(0).clip(lower=-.99)).groupby(balde(R.index)).sum().reindex(DIAS).fillna(0))
    Rd = Rd.reindex(columns=Wd.columns).fillna(0).sub(CDI_D, axis=0)
    Rd[["_vendas_a", "_vendas_b"]] = 0.0
    return Wd, Rd


def btc_brl_dia():
    """Retorno diário do BTC em R$ no calendário da B3 (para o alfa vs BTC): BTCUSDT 1h x câmbio, somado por pregão (log)."""
    P = painel_1h()[["BTC"]]
    fx = fx_horario(P.index)
    s = np.log(P["BTC"] * fx).diff()
    return np.expm1(para_dias(s))


def alfa_vs_btc(e, corte):
    """Alfa (a.a., pp) e beta do excesso diário sobre o CDI contra o excesso do BTC em R$ sobre o CDI, fora da amostra."""
    b = btc_brl_dia() - CDI_D
    x = pd.concat([e, b], axis=1, keys=["e", "b"]).dropna()
    x = x[x.index >= pd.Timestamp(corte)]
    if len(x) < 30 or x.b.var() == 0:
        return np.nan, np.nan
    beta = np.cov(x.e, x.b)[0, 1] / x.b.var()
    return float((x.e - beta * x.b).mean() * 252 * 100), float(beta)


# ================================================================ download (não é usado no backtest)
def baixa(o_que=("1h", "funding", "lido", "listagens")):
    import requests
    from concurrent.futures import ThreadPoolExecutor
    DADOS.mkdir(parents=True, exist_ok=True)
    S = requests.Session()
    S.headers["User-Agent"] = "Mozilla/5.0"
    ARQ = "https://data.binance.vision/data/spot/monthly/klines/{s}/{iv}/{s}-{iv}-{m}.zip"

    def zipcsv(url):
        for k in range(4):
            try:
                r = S.get(url, timeout=60)
                if r.status_code == 404:
                    return None
                r.raise_for_status()
                z = zipfile.ZipFile(io.BytesIO(r.content))
                x = pd.read_csv(z.open(z.namelist()[0]), header=None)
                if not str(x.iloc[0, 0]).isdigit():
                    x = x.iloc[1:].astype(float)
                return x
            except Exception:
                if k == 3:
                    return None

    def kl(sym, iv, ini, fim=None):
        t, L = int(pd.Timestamp(ini).timestamp() * 1000), []
        while True:
            try:
                r = S.get("https://data-api.binance.vision/api/v3/klines", params=dict(symbol=sym, interval=iv, startTime=t, limit=1000),
                          timeout=60).json()
            except Exception:
                break
            if not isinstance(r, list) or not r:
                break
            L += r
            t = r[-1][0] + 1
            if len(r) < 1000:
                break
        return pd.DataFrame(L).iloc[:, :8].astype(float) if L else None

    def norm(x, sym):
        x = x.iloc[:, [0, 4, 7]].copy()
        x.columns = ["t", "fech", "vol_usd"]
        t = x.t.astype("int64")
        t = np.where(t > 1e14, t // 1000, t)                         # arquivos de 2025+ vêm em microssegundos
        x["t"] = pd.to_datetime(t, unit="ms")
        x["sym"] = sym
        return x

    meses = [p.strftime("%Y-%m") for p in pd.period_range("2017-08", pd.Timestamp.today().to_period("M") - 1, freq="M")]
    if "1h" in o_que:
        def um(sym):
            f = DADOS / "1h" / f"{sym}.parquet"
            if f.exists():
                return
            partes = [zipcsv(ARQ.format(s=sym, iv="1h", m=m)) for m in meses]
            partes = [norm(p, sym) for p in partes if p is not None and len(p)]
            ult = kl(sym, "1h", pd.Timestamp.today().to_period("M").start_time)
            if ult is not None:
                partes.append(norm(ult, sym))
            if partes:
                f.parent.mkdir(exist_ok=True)
                x = pd.concat(partes).drop_duplicates("t").sort_values("t")
                x["t"] = x["t"] + pd.Timedelta(hours=1)               # índice = hora de FECHAMENTO
                x.to_parquet(f)
            print("1h", sym, len(partes), flush=True)
        with ThreadPoolExecutor(12) as ex:
            list(ex.map(um, [s + "USDT" for s in UNIVERSO]))
        x = pd.concat([pd.read_parquet(f) for f in sorted((DADOS / "1h").glob("*.parquet"))])
        x["fech"], x["vol_usd"] = x.fech.astype("float32"), x.vol_usd.astype("float32")
        x["sym"] = x.sym.astype("category")
        x.to_parquet(DADOS / "binance_1h.parquet", compression="zstd")
    if "funding" in o_que:
        FD = PF.parent.parent / "fundos" / "dados"
        pd.read_parquet(FD / "i_arb_funding.parquet").to_parquet(DADOS / "funding.parquet", compression="zstd")
        pd.read_parquet(FD / "i_arb_cripto_d.parquet").to_parquet(DADOS / "spot_perp_d.parquet", compression="zstd")
    if "lido" in o_que:
        r = S.get("https://yields.llama.fi/chart/747c1d2a-c668-4682-b9f9-296708a3dd90", timeout=60).json()["data"]
        x = pd.DataFrame(r)
        x["data"] = pd.to_datetime(x.timestamp).dt.tz_localize(None).dt.normalize()
        x.groupby("data")[["apy", "tvlUsd"]].last().to_csv(DADOS / "lido_apy.csv")
    if "listagens" in o_que:
        import re
        syms, marker = [], ""
        while True:
            u = "https://s3-ap-northeast-1.amazonaws.com/data.binance.vision?prefix=data/spot/monthly/klines/&delimiter=/" + (f"&marker={marker}" if marker else "")
            t = S.get(u, timeout=60).text
            ss = re.findall(r"<Prefix>data/spot/monthly/klines/([A-Z0-9]+)/</Prefix>", t)
            syms += ss
            if "<IsTruncated>true</IsTruncated>" not in t or not ss:
                break
            marker = f"data/spot/monthly/klines/{ss[-1]}/"
        usdt = [s for s in sorted(set(syms)) if s.endswith("USDT") and s[:-4] not in ESTAVEIS
                and not re.search(r"(UP|DOWN|BULL|BEAR)USDT$", s)]
        print(len(usdt), "pares USDT", flush=True)

        def lst(sym):
            u = f"https://s3-ap-northeast-1.amazonaws.com/data.binance.vision?prefix=data/spot/monthly/klines/{sym}/1d/&delimiter=/"
            try:
                ms = sorted(re.findall(sym + r"-1d-(\d{4}-\d{2})\.zip<", S.get(u, timeout=60).text))
            except Exception:
                return None
            if not ms or ms[0] <= "2019-01":                           # listado antes de 2019 (ou sem arquivo): fora do estudo
                return None
            for m in ms[:1]:
                x = zipcsv(ARQ.format(s=sym, iv="1d", m=m))
                if x is None or not len(x):
                    continue
                parts = [x]
                p0 = pd.Period(m)
                for k in range(1, 5):
                    mm = (p0 + k).strftime("%Y-%m")
                    if mm in meses:
                        y = zipcsv(ARQ.format(s=sym, iv="1d", m=mm))
                        if y is not None:
                            parts.append(y)
                y = norm(pd.concat(parts), sym)
                y["t"] = y["t"] + pd.Timedelta(days=1)                # fechamento do candle diário
                return y.head(125)
            return None
        with ThreadPoolExecutor(16) as ex:
            out = [y for y in ex.map(lst, usdt) if y is not None]
        pd.concat(out).to_parquet(DADOS / "listagens.parquet", compression="zstd")

    if "perps" in o_que:                                                # perpétuo das moedas listadas: existe? preço e financiamento reais
        import re
        x = pd.read_parquet(DADOS / "listagens.parquet")
        f0 = x.sort_values("t").groupby("sym").first()
        alvos = list(f0.index[f0.vol_usd > 1e6])

        def um(sym):
            for pre in ("", "1000", "1000000", "1M"):
                s2 = pre + sym
                u = f"https://s3-ap-northeast-1.amazonaws.com/data.binance.vision?prefix=data/futures/um/monthly/klines/{s2}/1d/&delimiter=/"
                try:
                    ms = sorted(set(re.findall(s2 + r"-1d-(\d{4}-\d{2})\.zip<", S.get(u, timeout=60).text)))
                except Exception:
                    ms = []
                if ms:
                    break
            if not ms:
                return None
            m0 = f0.loc[sym, "t"].strftime("%Y-%m")
            ms = [m for m in ms if m >= (pd.Period(m0) - 1).strftime("%Y-%m")][:5]
            kp, fp = [], []
            for m in ms:
                k = zipcsv(f"https://data.binance.vision/data/futures/um/monthly/klines/{s2}/1d/{s2}-1d-{m}.zip")
                if k is not None and len(k):
                    kp.append(k)
                fr = zipcsv(f"https://data.binance.vision/data/futures/um/monthly/fundingRate/{s2}/{s2}-fundingRate-{m}.zip")
                if fr is not None and len(fr):
                    fp.append(fr)
            if not kp:
                return None
            k = norm(pd.concat(kp), sym)
            k["t"] = k["t"] + pd.Timedelta(days=1)
            k["fund"] = np.nan
            out = [k.assign(tipo="perp")]
            if fp:
                fr = pd.concat(fp).iloc[:, [0, 2]].astype(float)
                fr.columns = ["t", "fund"]
                fr["t"] = pd.to_datetime(fr.t.astype("int64"), unit="ms")
                fr["sym"], fr["tipo"] = sym, "funding"
                out.append(fr)
            print("perp", sym, s2, len(kp), len(fp), flush=True)
            return pd.concat(out)
        with ThreadPoolExecutor(16) as ex:
            res = [r for r in ex.map(um, alvos) if r is not None]
        pd.concat(res).to_parquet(DADOS / "perps_listagens.parquet", compression="zstd")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "baixa":
        baixa(tuple(sys.argv[2:]) or ("1h", "funding", "lido", "listagens"))
