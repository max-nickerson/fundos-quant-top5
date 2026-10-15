"""
Peças comuns da frente "pf2_juros_fx" (pf/fundos/jx_*.py): juros, câmbio e renda fixa para pessoa física (R$ 20–50 mil).
Não altera comum.py / robustez.py / pf.py. Reaproveita o livro de compra-e-segura e o Tesouro Direto de _rf_comum.py.

Dados (cache em pf/dados/pf2_juros_fx/, montado UMA vez por prepara() a partir dos brutos já baixados — sem internet):
  td.parquet       Tesouro Direto COMPLETO (inclui Renda+ e Educa+, que não estavam no arquivo da frente renda_fixa):
                   quant/dados/tesouro_direto.csv (Tesouro Transparente, "precotaxatesourodireto.csv", PU e taxa de compra/venda da manhã)
  vendas_td.csv    vitrine (houve venda liquidada do título) — cópia de pf/dados/rev_tesouro/vendas_td.csv
  mercado.parquet  diário: PTAX, USD/BRL e EUR/USD (Yahoo), ETFs de Treasury (IEF, IEI, SHY, TLT, BIL), FRED (DGS3MO/2/10, DFF, VIX),
                   juro de política BIS (XM = zona do euro, US, BR), DOL rolado da B3 (dol_ret, cupom_aa; pf/dados/macro_hedge/br.parquet)
  selic/copom      pf/dados/renda_fixa/selic_meta.csv e copom_reunioes.csv (BCB)

Convenções (iguais às de _rf_comum): excesso = fração do capital sobre o CDI, calendário comum.DIAS; o que está aplicado no ativo não rende
CDI; futuros: o ajuste diário já é excesso (margem em Tesouro Selic rende CDI); decisão no fechamento de t, execução em t+1+lag.
"""
import shutil
import sys
from pathlib import Path

import numpy as np
import pandas as pd

AQUI = Path(__file__).resolve().parent
PF = AQUI.parent
RAIZ = PF.parent
for _p in (str(RAIZ), str(PF), str(AQUI)):
    if _p not in sys.path:
        sys.path.insert(0, _p)
import comum as C  # noqa: E402
import pf  # noqa: E402
import _rf_comum as K  # noqa: E402

QUANT = RAIZ.parent
FD, QD = QUANT / "fundos" / "dados", QUANT / "dados"
DIR = PF / "dados" / "pf2_juros_fx"
RF = PF / "dados" / "renda_fixa"
DIAS = C.DIAS
CDI = C.CDI.reindex(DIAS).fillna(0)
PTAX = pf.PTAX
_MEMO = {}


def memo(nome, fonte, f):
    k = (nome, id(fonte))
    if k not in _MEMO or _MEMO[k][0] is not fonte:
        if len(_MEMO) > 40:
            _MEMO.clear()
        _MEMO[k] = (fonte, f())
    return _MEMO[k][1]


# ============================================================================ preparação (uma vez)
def prepara(forca=False):
    DIR.mkdir(parents=True, exist_ok=True)
    if forca or not (DIR / "td.parquet").exists():
        t = pd.read_csv(QD / "tesouro_direto.csv", sep=";", decimal=",")
        t.columns = ["tipo", "venc", "data", "tx_compra", "tx_venda", "pu_compra", "pu_venda", "pu_base"]
        for c in ("venc", "data"):
            t[c] = pd.to_datetime(t[c], dayfirst=True)
        t = t.drop(columns="pu_base").sort_values(["data", "tipo", "venc"]).reset_index(drop=True)
        t.to_parquet(DIR / "td.parquet", compression="zstd")
    if forca or not (DIR / "vendas_td.csv").exists():
        shutil.copy(PF / "dados" / "rev_tesouro" / "vendas_td.csv", DIR / "vendas_td.csv")
    if forca or not (DIR / "mercado.parquet").exists():
        fx = pd.read_parquet(FD / "y_fx.parquet")[["EURUSD=X", "BRL=X"]].rename(columns={"EURUSD=X": "eurusd", "BRL=X": "usdbrl_y"})
        et = pd.read_parquet(FD / "y_etf.parquet")[["IEF", "IEI", "SHY", "TLT", "BIL"]]
        et.columns = [c.lower() for c in et.columns]
        fr = pd.read_parquet(FD / "fred_diario.parquet")[["DGS3MO", "DGS2", "DGS10", "DFF", "VIXCLS"]]
        fr.columns = ["dgs3mo", "dgs2", "dgs10", "dff", "vix"]
        bis = pd.read_parquet(FD / "bis_juros_politica.parquet")[["XM", "US", "BR"]]
        bis.columns = ["pol_eur", "pol_usd", "pol_brl"]
        br = pd.read_parquet(PF / "dados" / "macro_hedge" / "br.parquet")[["dol_ret", "dol_px", "cupom_aa"]]
        x = pd.concat([fx, et, fr, bis, br], axis=1).sort_index()
        x.index = pd.DatetimeIndex(x.index).normalize()
        x = x[~x.index.duplicated(keep="last")]
        x = x[x.index >= "2004-01-01"]
        x.index.name = "data"
        x.to_parquet(DIR / "mercado.parquet", compression="zstd")


def ler(nome):
    prepara()
    p = DIR / nome
    if p.suffix == ".parquet":
        return pd.read_parquet(p)
    x = pd.read_csv(p, sep=";", decimal=",") if nome.startswith("vendas") else pd.read_csv(p)
    return x


def mercado():
    return ler("mercado.parquet")


def selic():
    s = pd.read_csv(RF / "selic_meta.csv", parse_dates=["data"]).set_index("data")
    return s


def copom():
    c = pd.read_csv(RF / "copom_reunioes.csv", parse_dates=["DataReuniaoCopom", "DataInicioVigencia"])
    return c.rename(columns={"DataReuniaoCopom": "data"})[["data", "MetaSelic", "ReuniaoExtraordinaria"]].sort_values("data").reset_index(drop=True)


def vendas_td():
    v = ler("vendas_td.csv")
    v.columns = ["tipo", "venc", "data", "pu", "qtd", "valor"]
    v["venc"] = pd.to_datetime(v.venc, dayfirst=True)
    v["data"] = pd.to_datetime(v.data, dayfirst=True)
    return v[["data", "tipo", "venc", "qtd"]]


# ============================================================================ séries no calendário B3 (só passado)
def serie(d, col, limit=5):
    s = d["mkt"][col].dropna()
    return s.reindex(DIAS.union(s.index)).ffill(limit=limit).reindex(DIAS)


def ret_eua(d, col):
    """Retorno (US$) composto entre pregões da B3 (último preço disponível até a data)."""
    s = d["mkt"][col].dropna()
    s = s.reindex(DIAS.union(s.index)).ffill(limit=5)
    r = s.pct_change(fill_method=None).fillna(0)
    return np.expm1(np.log1p(r).cumsum().reindex(DIAS).diff()).fillna(0)


def selic_meta(d):
    s = d["selic"]["selic_meta"]
    return s.reindex(s.index.union(DIAS)).ffill().reindex(DIAS)


def ciclo_copom(d):
    """+1 se a última decisão do Copom (já vigente) foi alta, -1 corte, 0 manutenção. Vigência = dia seguinte à reunião (anúncio à noite)."""
    def f():
        sm = selic_meta(d)
        dif = sm.diff()
        ult = dif.where(dif != 0).ffill()
        # manutenção: a meta ficou igual por >= 2 reuniões (~90 dias) -> 0
        dias_sem = (dif == 0).astype(int).groupby((dif != 0).cumsum()).cumsum()
        out = np.sign(ult).where(dias_sem < 63 * 1.5, 0).fillna(0)
        return out
    return memo("ciclo", d["selic"], f)


# ============================================================================ mini-dólar (WDO) contínuo em excesso
def wdo(d):
    """(retorno em excesso diário do dólar futuro, nocional em R$ de 1 WDO). DOL rolado da B3 desde 2019; antes, sintético:
    PTAX - (CDI - cupom)/252 com cupom = Fed funds + 1,07 pp (mesma premissa de mh_base)."""
    def f():
        ff = serie(d, "dff").fillna(0) / 100
        cupom = (serie(d, "cupom_aa") / 100).fillna(ff + .0107)
        sint = PTAX.pct_change(fill_method=None).fillna(0) - (CDI - cupom / 252)
        dol = d["mkt"]["dol_ret"].dropna()
        ini = dol.index.min()
        r = sint.where(DIAS < ini, dol.reindex(DIAS).fillna(0)) if pd.notna(ini) else sint
        return r, 10_000 * PTAX
    return memo("wdo", d["mkt"], f)


def contratos_inteiros(alvo_noc, noc1, minimo=0):
    """Nº inteiro de contratos para um nocional-alvo (R$); `minimo` força pelo menos 1 contrato quando o alvo é != 0."""
    n = (alvo_noc.abs() / noc1).round()
    if minimo:
        n = n.where(~((alvo_noc.abs() > 0) & (n < minimo)), minimo)
    return n * np.sign(alvo_noc)


def futuro_livro(n, r_exc, noc1, custo_lado, capital, lag=0, custo_mult=1.0, roll_mask=None):
    """n: contratos-alvo decididos em t (Series); executa em t+1+lag; P&L de t+2 em diante = n x nocional(t-1) x retorno em excesso.
    custo_lado em R$ por contrato e lado; roll_mask (bool Series): dias de rolagem (paga 2 lados por contrato carregado).
    Devolve dict: e (excesso, fração do capital), pnl (R$), pos (contratos efetivos), custo (R$)."""
    n = n.reindex(DIAS).fillna(0).shift(1 + lag).fillna(0)
    pnl = n.shift(1).fillna(0) * noc1.shift(1).ffill() * r_exc.reindex(DIAS).fillna(0)
    giro = n.diff().abs().fillna(n.abs())
    if roll_mask is not None:
        giro = giro + roll_mask.reindex(DIAS).fillna(False).astype(float) * n.shift(1).abs().fillna(0) * 2
    custo = giro * custo_lado * custo_mult
    tot = pnl.fillna(0) - custo
    return {"e": tot / capital, "pnl": tot, "pos": n, "custo": custo}


def primeiro_util_do_mes():
    m = pd.Series(DIAS.to_period("M"), index=DIAS)
    return m.ne(m.shift(1))


def maquina(entra, sai, max_dias, espera=0):
    """Estado ligado/desligado: liga quando `entra` (t), desliga quando `sai` ou após max_dias; espera = pregões mínimos entre eventos."""
    e, s = entra.reindex(DIAS).fillna(False).to_numpy(), sai.reindex(DIAS).fillna(False).to_numpy()
    on = np.zeros(len(DIAS), bool)
    ligado, t0, ult = False, -10 ** 9, -10 ** 9
    for t in range(len(DIAS)):
        if ligado and (s[t] or t - t0 >= max_dias):
            ligado, ult = False, t
        elif not ligado and e[t] and t - ult > espera:
            ligado, t0 = True, t
        on[t] = ligado
    return pd.Series(on, index=DIAS)


def negocios_de_estado(on, contrib, nome="pos", lado=1, extra=None):
    """Lista de negócios a partir de um estado ligado (decidido em t) e da contribuição diária (fração do capital)."""
    on = on.reindex(DIAS).fillna(False).astype(bool)
    ini = on & ~on.shift(1, fill_value=False)
    fim = ~on & on.shift(1, fill_value=False)
    I, F = list(DIAS[ini]), list(DIAS[fim])
    out = []
    for a in I:
        b = next((x for x in F if x > a), DIAS[-1])
        i, j = DIAS.get_loc(a), DIAS.get_loc(b)          # decidido em t, executa em t+1, rende de t+2 até a saída (t_saída+1)
        c = contrib.reindex(DIAS).iloc[i + 2:j + 2].sum() * 100
        lado_ = lado.loc[a] if isinstance(lado, pd.Series) else lado
        out.append({"ativo": nome, "lado": int(np.sign(lado_) or 1), "entrada": a, "saida": b, "dias": int(((DIAS > a) & (DIAS <= b)).sum()),
                    "retorno_%": c, "contrib_pp": c})
    ng = pd.DataFrame(out)
    if extra is not None and len(ng):
        for k, s in extra.items():
            ng[k] = [s.get(a, np.nan) if hasattr(s, "get") else np.nan for a in ng.entrada]
    return ng


# ============================================================================ Tesouro: Renda+/Educa+ (fluxo de parcelas)
def fluxo_parcelas(venc, n_parc):
    """Datas das parcelas mensais (iguais em termos reais) de Renda+ (240) / Educa+ (60): vencem dia 15, a última em `venc`."""
    v = pd.Timestamp(venc)
    return pd.DatetimeIndex([v - pd.DateOffset(months=k) for k in range(n_parc)][::-1])


def duration_parcelas(datas_ref, venc, n_parc, taxa):
    """Duration modificada (anos) de um título de parcelas reais iguais, na taxa real (% a.a.), para cada data (vetorizado no tempo)."""
    parc = fluxo_parcelas(venc, n_parc)
    out = np.full(len(datas_ref), np.nan)
    tx = np.asarray(taxa, dtype=float)
    for i, dt in enumerate(datas_ref):
        if not np.isfinite(tx[i]):
            continue
        tt = (parc[parc > dt] - dt).days.values / 365.25
        if not len(tt):
            continue
        df = (1 + tx[i] / 100) ** (-tt)
        out[i] = (tt * df).sum() / df.sum() / (1 + tx[i] / 100)
    return pd.Series(out, index=datas_ref)
