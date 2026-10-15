"""
Peças comuns da frente "global_cripto" (mercados globais e cripto acessados pela B3/corretoras brasileiras, só o necessário na IBKR).

Dados (pf/dados/global_cripto/, gerados uma vez a partir de quant/dados e downloads públicos; nada de internet aqui):
  b3_etf_bdr.parquet     ETFs e BDRs do COTAHIST (abertura, máx, mín, fech, melhores ofertas, volume) 2014-2026
  futuros_b3.parquet     boletim BVBG.086 (PR) da B3, 2023-2026: WSP/ISP (S&P), BIT (bitcoin em R$), ETR (ether), SOL — ajuste, ofertas, OI
  cripto_br.parquet      candles 1h/1d: Mercado Bitcoin (BTC-BRL desde 2014), Binance (BTCBRL/USDTBRL desde 10/2020, BTCUSDT desde 2017)
  us_etf_ajustado.parquet  ETFs dos EUA (Yahoo, ajustados) — proxy dos ETFs/BDRs da B3 antes da listagem
  us_fech_bruto.parquet  fechamentos dos EUA não ajustados (ativo-objeto dos BDRs)
  dolar.csv              dólar à vista implícito no 1º vencimento do DOL (ajuste ~16h) e BRL=X do Yahoo
  spin_*.csv/parquet     spin-offs dos EUA (Form 10-12B, SEC) e preços (Yahoo)

Motor: carteira em COTAS INTEIRAS (lote 1 para ETF/BDR), decisão no fechamento de t, execução no fechamento de t+1+lag; o dinheiro aplicado
no ativo NÃO rende CDI (excesso = retorno do ativo - CDI nessa parcela); a venda a descoberto (BTC) rende 95% do CDI (dinheiro vira LFT
em garantia) e paga aluguel de PF (0,5% por contrato aberto + taxa ao doador).
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

PF = Path(__file__).resolve().parent.parent
for _p in (str(PF), str(PF.parent)):
    if _p not in sys.path:
        sys.path.insert(0, _p)
import comum as C  # noqa: E402
import pf as P  # noqa: E402

DADOS = PF / "dados" / "global_cripto"
DIAS, CDI, PTAX = P.DIAS, P.CDI, P.PTAX
TB = C.TB_US.reindex(DIAS, method="ffill").fillna(0)
B3_EMOL = P.B3_EMOL
VENDA_RENDE = .95
ALUGUEL_ABERTURA = P.ALUGUEL_PF_CORRETORA        # 0,5% do volume a cada contrato de aluguel aberto/renovado (Clear/Rico)
_CACHE = {}


def ler(nome):
    """Lê um arquivo de dados (índice de data ou coluna 'data')."""
    if nome not in _CACHE:
        f = DADOS / nome
        _CACHE[nome] = pd.read_csv(f, index_col=0, parse_dates=True) if f.suffix == ".csv" else pd.read_parquet(f)
    return _CACHE[nome]


def pivo(df, campo, tickers=None, col="ticker", data="data"):
    """Formato longo -> tabela data x ticker no calendário da B3 (sem preencher)."""
    x = df if tickers is None else df[df[col].isin(tickers)]
    p = x.pivot_table(index=data, columns=col, values=campo, aggfunc="last").reindex(DIAS)
    return p if tickers is None else p.reindex(columns=list(tickers))


def no_calendario(s, limite=5):
    """Série dos EUA/cripto -> pregões da B3 (último valor conhecido até a data, com limite)."""
    s = s[~s.index.duplicated(keep="last")].dropna()
    return s.reindex(DIAS.union(s.index)).ffill(limit=limite).reindex(DIAS)


def hora_fech_b3_utc(d):
    """Fechamento da B3 em UTC: 20h com horário de verão nos EUA, 21h sem (17h/18h de Brasília)."""
    return 20 if pd.Timestamp(d).tz_localize("America/New_York").dst().total_seconds() > 0 else 21


def cripto_no_fech_b3(c, fonte, sym):
    """Preço do candle de 1h que FECHA na hora do fechamento da B3 (candle que abre 1h antes)."""
    x = c[(c.fonte == fonte) & (c.sym == sym) & (c.res == "1h")].set_index("data").fech
    x = x[~x.index.duplicated()]
    alvo = pd.DatetimeIndex([d + pd.Timedelta(hours=hora_fech_b3_utc(d) - 1) for d in DIAS])
    return pd.Series(x.reindex(alvo).values, index=DIAS)


def meio_spread(bid, ask, padrao=.003, teto=.03):
    """Meio spread relativo do fechamento; sem as duas ofertas, mediana móvel dos últimos 20 pregões (só passado)."""
    hs = ((ask - bid) / (ask + bid)).where((bid > 0) & (ask > 0) & (ask >= bid))
    return hs.fillna(hs.rolling(20, min_periods=1).median().shift(1)).fillna(padrao).clip(.0001, teto)


def emenda(real, proxy, min_dias=20):
    """Série de preço: retornos do ativo real da B3 a partir do `min_dias`-ésimo pregão com negócio; antes disso, retornos do proxy.
    Devolve (nível, marcador "real")."""
    ok = real.notna().cumsum() >= min_dias
    rr = real.ffill(limit=5).pct_change(fill_method=None)
    rp = proxy.ffill(limit=5).pct_change(fill_method=None)
    r = rr.where(ok, rp)
    r = r.where(r.abs() < .35)                         # salto > 35% num dia = desdobramento/erro de cadastro
    inicio = r.first_valid_index()
    if inicio is None:
        return pd.Series(np.nan, index=real.index), ok
    nivel = (1 + r.fillna(0)).cumprod().where(r.index >= inicio)
    nivel = nivel.where(proxy.ffill(limit=5).notna() | ok)
    return nivel, ok


# ---------------------------------------------------------------- motor em cotas inteiras
def executa(W, preco, capital, custo, lag=0, banda=.25, venda_rende=VENDA_RENDE, aluguel_aa=.01, custo_mult=1.0, negocia=None):
    """W: pesos-alvo (fração do capital) decididos no fechamento de t. Executa no fechamento de t+1+lag em cotas INTEIRAS
    (trunca para baixo), só refaz a posição se o valor desviar mais de `banda` do alvo, mudar de sinal ou zerar.
    preco: nível em R$ (DataFrame); custo: meio spread + emolumentos por R$ negociado (DataFrame/escalar).
    negocia: DataFrame bool — se o ativo não negociou no dia, a ordem fica para o dia seguinte.
    Devolve dict com n (cotas no fim do dia), pnl (R$ por ativo, sem CDI), carrego (CDI perdido/ganho), custo (R$), aluguel (R$)."""
    cols = list(W.columns)
    Pz = preco.reindex(index=DIAS, columns=cols).ffill(limit=5)
    Wt = W.reindex(index=DIAS, columns=cols).fillna(0).shift(1 + lag).fillna(0)
    Cz = custo.reindex(index=DIAS, columns=cols).ffill().fillna(.005) if isinstance(custo, pd.DataFrame) else pd.DataFrame(custo, index=DIAS, columns=cols)
    ok = (negocia.reindex(index=DIAS, columns=cols).fillna(False).values if negocia is not None else np.ones((len(DIAS), len(cols)), bool))
    Pv, Wv, Cv = Pz.values, Wt.values, Cz.values * custo_mult
    T, N = Pv.shape
    n = np.zeros((T, N))
    gir = np.zeros((T, N))
    for i in range(1, T):
        n[i] = n[i - 1]
        p = Pv[i]
        for j in range(N):
            if not (p[j] > 0) or not ok[i, j]:
                if not (p[j] > 0):
                    n[i, j] = 0 if np.isnan(p[j]) and Wv[i, j] == 0 else n[i, j]
                continue
            alvo = Wv[i, j] * capital
            atual = n[i, j] * p[j]
            if alvo == 0:
                novo = 0.0
            elif np.sign(alvo) != np.sign(n[i, j]) or abs(atual - alvo) > banda * abs(alvo):
                novo = np.sign(alvo) * np.floor(abs(alvo) / p[j])
            else:
                continue
            gir[i, j] = abs(novo - n[i, j])
            n[i, j] = novo
    Pf = np.nan_to_num(Pv)
    dP = np.vstack([np.zeros(N), np.diff(Pf, axis=0)])
    dP[np.isnan(Pv)] = 0
    n0 = np.vstack([np.zeros(N), n[:-1]])
    pnl = n0 * dP
    val0 = n0 * np.vstack([np.zeros(N), Pf[:-1]])
    cdi = CDI.reindex(DIAS).fillna(0).values[:, None]
    carrego = -np.where(val0 > 0, val0, val0 * venda_rende) * cdi                     # comprado não rende; vendido rende 95% do CDI
    novo_aluguel = np.where((n < 0) & (np.abs(n) > np.abs(n0) - 1e-9) & (gir > 0), gir, 0)
    alug = np.abs(np.minimum(val0, 0)) * aluguel_aa / 252 * custo_mult + novo_aluguel * Pf * ALUGUEL_ABERTURA * custo_mult
    cus = gir * Pf * Cv
    f = lambda a: pd.DataFrame(a, index=DIAS, columns=cols)
    return {"n": f(n), "pnl": f(pnl), "carrego": f(carrego), "custo": f(cus), "aluguel": f(alug)}


def excesso_de(ex, capital, extra=None):
    """Excesso diário sobre o CDI (fração do capital) a partir do resultado de `executa` (+ série extra em R$, ex. conta exterior)."""
    tot = (ex["pnl"] + ex["carrego"] - ex["custo"] - ex["aluguel"]).sum(axis=1)
    if extra is not None:
        tot = tot + extra.reindex(DIAS).fillna(0)
    return tot / capital


def contrib_ativo(ex, capital):
    return (ex["pnl"] + ex["carrego"] - ex["custo"] - ex["aluguel"]) / capital


def pnl_classe(ex):
    """P&L em R$ do ativo (sem o CDI do caixa): preço - custos - aluguel. O carrego é a parte do caixa (o runner trata)."""
    return (ex["pnl"] - ex["custo"] - ex["aluguel"]).sum(axis=1)


def negocios_de(n, contrib, preco):
    """Um negócio por trecho com o mesmo sinal de posição: ativo, lado, entrada, saída, dias, retorno_% e contrib_pp (pp do PL)."""
    out = []
    for c in n.columns:
        s = np.sign(n[c].values)
        k = contrib[c].fillna(0).values
        p = preco[c].ffill().values
        i, T = 0, len(s)
        while i < T:
            if s[i] == 0:
                i += 1
                continue
            j = i
            while j + 1 < T and s[j + 1] == s[i]:
                j += 1
            fim = min(j + 1, T - 1)
            ret = (p[fim] / p[i] - 1) * s[i] if p[i] > 0 else np.nan
            out.append({"ativo": c, "lado": int(s[i]), "entrada": n.index[i], "saida": n.index[fim], "dias": fim - i,
                        "retorno_%": ret * 100, "contrib_pp": k[i:fim + 1].sum() * 100})
            i = j + 1
    cols = ["ativo", "lado", "entrada", "saida", "dias", "retorno_%", "contrib_pp"]
    return pd.DataFrame(out, columns=cols)


def tendencia(nivel, janela):
    """1 se o preço está acima da média móvel de `janela` pregões (só passado)."""
    return (nivel > nivel.rolling(janela, min_periods=int(janela * .8)).mean()).astype(float).where(nivel.notna(), 0)


def mensal(W):
    return C.mensal(W)
