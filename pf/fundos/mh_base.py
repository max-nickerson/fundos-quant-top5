"""
Peças comuns da frente "macro_hedge" (pf/fundos/mh_*.py): ações B3 inteiras (fracionário) + futuros inteiros (WIN, WDO, BGI, CCM na B3;
MCL na CME com só a margem na IBKR). Não altera comum.py / robustez.py / pf.py — premissas corrigidas ficam aqui, com fonte.

DADOS (sem internet): `pf/dados/macro_hedge/*.parquet`, montados UMA vez por `prepara()` a partir dos brutos já baixados em
quant/fundos/dados e quant/dados (COTAHIST ajustado por proventos do painel de eventos, ajustes de futuros B3, Yahoo, FRED, BCB, CVM).
Os fundos leem só o cache.

MOTOR (`livro`): decisão no fechamento de t, execução no fechamento de t+1(+lag), resultado a partir de t+2 (= comum.carteira).
  Ações: nº INTEIRO de ações = trunc(alvo x capital / preço de t), recalculado só quando o alvo muda; o que passa de lote de 100 vai ao
    fracionário (spread 2x). A posição é carregada em VALOR pelo retorno total (proventos e desdobramentos/renomeações não quebram a conta).
    Excesso de uma ação comprada = valor x (R - CDI) (o dinheiro saiu do Tesouro Selic); vendida = -valor x (R - CDI) (o produto da venda
    fica como garantia em Tesouro Selic). Custos: emolumentos 0,03% + meio spread por liquidez; aluguel PF = 0,5% do volume por contrato
    aberto/renovado (renova a cada 63 pregões) + taxa ao doador x 1,2 (tarifa B3 de 20% sobre a taxa).
  Futuros: nº INTEIRO de contratos = round(alvo x capital / nocional de 1 contrato); P&L = n x nocional x retorno em excesso do contrato
    (a garantia fica em Tesouro Selic e rende CDI); custo por contrato e lado + rolagem (2 lados) no calendário de cada contrato.
    CME (MCL): P&L em US$ convertido pela PTAX; a margem fica na IBKR (pf.custo_conta_exterior: perde CDI, paga IOF/spread, câmbio).
  Garantia: ações compradas usam caixa; futuros e aluguel usam Tesouro Selic + 70% das ações compradas como garantia (B3 aceita ações com
    deságio). É DIAGNÓSTICO (`garantia_*` em diag): cada fundo dimensiona os alvos para caber com alavancagem 1.
  Alavancagem L: multiplica os alvos; ação comprada acima do capital é financiada a termo (CDI + 4% a.a.).
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

QUANT = RAIZ.parent
FD, QD = QUANT / "fundos" / "dados", QUANT / "dados"
CACHE = PF / "dados" / "macro_hedge"
DIAS, CDI = C.DIAS, C.CDI.fillna(0)
PTAX = pf.PTAX
TBILL = C.TB_US.reindex(DIAS, method="ffill").fillna(0)

# ---------------------------------------------------------------- premissas de varejo (fontes)
EMOL = .0003            # B3 pessoa física: negociação 0,005% + liquidação 0,0224% + TTA 0,0026% (varejo/MAPA_ATIVOS_FX_B3.md)
EMOL_DT = .00023        # day trade (mesma fonte)
FRAC_MULT = 2.0         # fracionário: spread 2x o do lote padrão (varejo/fundos/rebal_ibovespa_varejo.py)
BTC_FIXO = .005         # Clear/Rico: 0,5% do volume por contrato de aluguel aberto/renovado (pf.py; atendimento Rico)
BTC_RENOVA = 63         # contrato de aluguel de ~3 meses, renovado (paga de novo o fixo)
TERMO_SPREAD = .04      # termo para alavancar ações: CDI + 4% a.a. (premissa do varejo/rebal_ibovespa_varejo.py)
GARANTIA_ACAO = .70     # ação comprada vale 70% como garantia na B3 (deságio ~30% para blue chips; premissa)
GARANTIA_VENDIDO = .25  # garantia além do produto da venda a descoberto (~125%, varejo/MAPA_ATIVOS_FX_B3.md)


def meio_spread(adv):
    """Meio spread de lote padrão pela liquidez (ADV 60d em R$): >= 50 mi 5 bps, >= 10 mi 10, >= 2 mi 25, abaixo 50."""
    adv = np.asarray(adv, dtype=float)
    return np.select([adv >= 50e6, adv >= 10e6, adv >= 2e6], [.0005, .0010, .0025], .0050)


# Futuros: custo em moeda do contrato por contrato e lado = tarifa + meio tick; margem = fração do nocional; rolagem a cada k meses.
#  WIN: R$ 0,20/ponto; tarifa ~R$ 0,60 (pf.py) + meio tick (5 pts = R$ 1) -> R$ 1,10; margem ~15% (R$ 6,6 mil com o índice a 208 mil,
#       Toro/Rankia em varejo/fundos/rebal_ibovespa_varejo.py); vence nos meses pares -> rola a cada 2 meses.
#  WDO: US$ 10 mil; tarifa ~R$ 1,20 (pf.py) + meio tick (0,5 pt = R$ 5) -> R$ 3,70; margem ~12%; vence todo mês.
#  BGI: 330 @; tarifa R$ 1,50 + meio tick (R$ 0,05/@ = R$ 16,50) -> ~R$ 10; margem ~8%; rola todo mês (liquidez no 1º vencimento).
#  CCM: 450 sc; tarifa R$ 1,50 + meio tick (R$ 0,01/sc = R$ 4,50) -> ~R$ 4; margem ~8%; vencimentos F/H/K/N/U/X -> rola a cada 2 meses.
#  MCL: 100 barris; IBKR US$ 0,85 (pf.py) + meio tick (US$ 0,01 x 100 = US$ 1) -> US$ 1,35; margem ~10%; rola todo mês.
#       ATENÇÃO: o MCL só existe desde 12/07/2021; antes disso a perna é hipotética (mesmo contrato, retorno do BNO).
FUT = {"WIN": dict(custo=1.10, margem=.15, roll=2, moeda="BRL"),
       "WDO": dict(custo=3.70, margem=.12, roll=1, moeda="BRL"),
       "BGI": dict(custo=10.0, margem=.08, roll=1, moeda="BRL"),
       "CCM": dict(custo=4.00, margem=.08, roll=2, moeda="BRL"),
       "MCL": dict(custo=1.35, margem=.10, roll=1, moeda="USD")}

# Renomeações/conversões: série única (antigo até o último pregão, depois o novo)
CADEIAS = {"BHIA3": ["VVAR3", "VIIA3", "BHIA3"], "AMER3": ["BTOW3", "AMER3"], "AZZA3": ["ARZZ3", "AZZA3"], "AXIA3": ["ELET3", "AXIA3"],
           "AXIA6": ["ELET6", "AXIA6"], "ISAE4": ["TRPL4", "ISAE4"], "MBRF3": ["MRFG3", "MBRF3"], "AUAU3": ["PETZ3", "AUAU3"],
           "CPLE3": ["CPLE6", "CPLE3"]}
_M = {}


# ================================================================ preparação dos dados (uma vez)
def _cadeia(df, novo, velhos):
    s = None
    for t in velhos:
        if t not in df:
            continue
        x = df[t].dropna()
        if s is None:
            s = x
        else:
            s = pd.concat([s, x[x.index > s.index.max()]])
    return s


def _rolado(f, raiz, meses_validos=None):
    """Contínuo de um futuro B3 sem saltos de vencimento: segura o vencimento de maior contrato em aberto entre os que vencem DEPOIS do
    mês corrente (decidido em t com dados de t); retorno de t+1 = ajuste/ajuste anterior do MESMO contrato. Devolve (ret, preço)."""
    cod = dict(zip("FGHJKMNQUVXZ", range(1, 13)))
    x = f[f.ticker.str.match(rf"^{raiz}[FGHJKMNQUVXZ]\d\d$")].copy()
    x = x.drop_duplicates(["date", "ticker"])
    x["venc"] = (2000 + x.ticker.str[-2:].astype(int)) * 12 + x.ticker.str[-3].map(cod)
    if meses_validos:
        x = x[x.ticker.str[-3].isin(meses_validos)]
    x["mes"] = x.date.dt.year * 12 + x.date.dt.month
    adj = x.pivot(index="date", columns="ticker", values="AdjstdQt")
    prv = x.pivot(index="date", columns="ticker", values="PrvsAdjstdQt")
    oi = x.pivot(index="date", columns="ticker", values="OpnIntrst")
    venc = x.drop_duplicates("ticker").set_index("ticker").venc
    mes = pd.Series(adj.index.year * 12 + adj.index.month, index=adj.index)
    ok = pd.DataFrame(venc.values[None, :] > mes.values[:, None], index=adj.index, columns=venc.index) & adj.notna()
    o = oi.reindex(columns=venc.index).where(ok)
    # sem contrato em aberto informado: o vencimento válido mais próximo
    prox = pd.DataFrame(np.where(ok, venc.values[None, :], 10 ** 9), index=adj.index, columns=venc.index).idxmin(axis=1)
    seg = o.fillna(-1).idxmax(axis=1).where(o.notna().any(axis=1), prox)
    ret, px = [], []
    ant = None
    for t in adj.index:
        if ant is not None and pd.notna(adj.at[t, ant]) and pd.notna(prv.at[t, ant]) and prv.at[t, ant] > 0:
            ret.append(adj.at[t, ant] / prv.at[t, ant] - 1)
        else:
            ret.append(0.0)
        ant = seg[t]
        px.append(adj.at[t, ant])
    return pd.Series(ret, index=adj.index), pd.Series(px, index=adj.index), seg


def prepara(forca=False):
    """Monta pf/dados/macro_hedge/ a partir dos brutos (roda uma vez; depois tudo lê o cache)."""
    CACHE.mkdir(parents=True, exist_ok=True)
    if forca or not (CACHE / "acoes_R.parquet").exists():
        d = pd.read_pickle(FD / "painel_eventos_br.pkl")
        P, R, O, V = d["P"], d["R"], d["O"], d["V"]
        adv = V.fillna(0).rolling(60, min_periods=20).mean()
        univ = list(adv.columns[adv.max() >= 20e6])
        for novo, velhos in CADEIAS.items():
            univ = [u for u in univ if u not in velhos]
        univ += ["FIBR3", "SLCE3", "SMTO3", "BEEF3"]
        out = {k: X[sorted(set(univ) & set(X.columns))].copy() for k, X in (("P", P), ("R", R), ("O", O), ("V", V))}
        for novo, velhos in CADEIAS.items():
            for k, X in (("P", P), ("R", R), ("O", O), ("V", V)):
                s = _cadeia(X, novo, velhos)
                if s is not None:
                    out[k][novo] = s.reindex(out[k].index)
        for k, X in out.items():
            X.index.name = "data"
            X.astype("float32" if k != "R" else "float64").to_parquet(CACHE / f"acoes_{k}.parquet", compression="zstd")
        # eventos CVM por ticker (data de ENTREGA): fato relevante e ITR/DFP
        fca = pd.read_parquet(FD / "cvm_fca_vm.parquet")
        fca = fca[fca.Codigo_Negociacao.notna()]
        cn = lambda s: s.astype(str).str.replace(r"\D", "", regex=True).str.zfill(14)
        mp = pd.DataFrame({"cnpj": cn(fca.CNPJ_Companhia), "raiz": fca.Codigo_Negociacao.str.strip().str[:4].str.upper()}).drop_duplicates()
        raiz_tk = {}
        for t in out["P"].columns:
            raizes = {t[:4]} | {v[:4] for v in CADEIAS.get(t, [])}
            for r_ in raizes:
                raiz_tk.setdefault(r_, []).append(t)
        mp = mp[mp.raiz.isin(raiz_tk)]
        ipe = pd.read_parquet(FD / "cvm_ipe.parquet", columns=["CNPJ_Companhia", "Categoria", "Data_Entrega"])
        ipe = ipe[ipe.Categoria.str.contains("Fato Relevante", na=False)]
        ev = [pd.DataFrame({"cnpj": cn(ipe.CNPJ_Companhia), "data": pd.to_datetime(ipe.Data_Entrega, errors="coerce"), "tipo": "FR"})]
        itr = pd.read_parquet(FD / "cvm_itr_dfp.parquet", columns=["CNPJ_CIA", "DT_RECEB"])
        ev.append(pd.DataFrame({"cnpj": cn(itr.CNPJ_CIA), "data": pd.to_datetime(itr.DT_RECEB, errors="coerce"), "tipo": "ITR"}))
        ev = pd.concat(ev).dropna().merge(mp, on="cnpj")
        ev["ticker"] = ev.raiz.map(raiz_tk)
        ev = ev.explode("ticker")[["data", "ticker", "tipo"]].drop_duplicates().sort_values("data").reset_index(drop=True)
        ev.to_parquet(CACHE / "eventos.parquet")
    if forca or not (CACHE / "br.parquet").exists():
        v = pd.read_parquet(FD / "b3_vista.parquet", filters=[("ticker", "==", "BOVA11")]).drop_duplicates("data").set_index("data").sort_index()
        br = pd.DataFrame({"bova_abre": v.abertura / v.fatcot, "bova_fech": v.fech / v.fatcot, "bova_vol": v.volume})
        yi = pd.read_parquet(FD / "y_idx.parquet")
        br["ibov"] = yi["^BVSP"]
        f = pd.read_parquet(QD / "futuros.parquet")
        r, px, _ = _rolado(f, "DOL")
        br["dol_ret"], br["dol_px"] = r, px
        cup = pd.read_csv(RAIZ / "dados" / "carry_moedas" / "cupom_frc.csv", index_col=0, parse_dates=True)["cupom_frc_aa_pct"]
        br["cupom_aa"] = cup
        a = pd.read_parquet(FD / "b3_futuros_agro.parquet")
        for raiz, meses in (("BGI", None), ("CCM", list("FHKNUX")), ("SJC", None), ("ETH", None)):
            r, px, _ = _rolado(a, raiz, meses)
            br[f"{raiz.lower()}_ret"], br[f"{raiz.lower()}_px"] = r, px
        s432 = pd.read_parquet(FD / "sgs_432.parquet")["v"]
        br["selic_meta"] = s432
        fo = pd.read_parquet(FD / "focus_ipca12m.parquet").drop_duplicates("Data", keep="last").set_index("Data")["Mediana"]
        br["focus_ipca12m"] = fo.shift(1, freq="D")                                # Focus sai no dia útil seguinte à data da pesquisa
        br.index.name = "data"
        br.sort_index().to_parquet(CACHE / "br.parquet")
    if forca or not (CACHE / "eua.parquet").exists():
        ye, yi, yf, ya = (pd.read_parquet(FD / f) for f in ("y_etf.parquet", "y_idx.parquet", "y_fx.parquet", "y_adr.parquet"))
        fr = pd.read_parquet(FD / "fred_diario.parquet")
        us = pd.DataFrame({"ewz": ye.EWZ, "bno": ye.BNO, "uso": ye.USO, "spy": ye.SPY, "brent": yi["BZ=F"], "wti": yi["CL=F"],
                           "brl": yf["BRL=X"], "pbr": ya.PBR, "vale": ya.VALE, "vix": yi["^VIX"]})
        us = us.join(fr[["DFF", "T5YIE"]].rename(columns=str.lower), how="left")
        us = us[us.index >= "2005-01-01"]
        us.index.name = "data"
        us.to_parquet(CACHE / "eua.parquet")


def dados():
    """Dicionário com tudo (DataFrames indexados por data; 'eventos' em formato longo com coluna 'data')."""
    if not _M:
        prepara()
        for k in ("P", "R", "O", "V"):
            _M[k] = pd.read_parquet(CACHE / f"acoes_{k}.parquet").astype(float)
        _M["eventos"] = pd.read_parquet(CACHE / "eventos.parquet")
        _M["br"] = pd.read_parquet(CACHE / "br.parquet")
        _M["eua"] = pd.read_parquet(CACHE / "eua.parquet")
    return dict(_M)


def seleciona(d, tickers):
    """Só as colunas pedidas (reduz memória e tempo da bateria)."""
    out = dict(d)
    for k in ("P", "R", "O", "V"):
        out[k] = d[k][[t for t in tickers if t in d[k].columns]]
    out["eventos"] = d["eventos"][d["eventos"].ticker.isin(tickers)]
    return out


# ================================================================ séries de mercado no calendário B3 (só passado)
def br(d, col):
    return d["br"][col].reindex(DIAS)


def eua_ffill(d, col):
    """Série dos EUA no calendário B3: último valor disponível até a data (fecha 16h NY, no máximo ~1h depois da B3)."""
    s = d["eua"][col].dropna()
    return s.reindex(DIAS.union(s.index)).ffill(limit=5).reindex(DIAS)


def ret_eua(d, col):
    """Retorno (em US$) acumulado entre pregões da B3."""
    s = d["eua"][col].dropna()
    s = s.reindex(DIAS.union(s.index)).ffill(limit=5)
    return s.pct_change(fill_method=None).pipe(lambda r: np.expm1(np.log1p(r.fillna(0)).cumsum().reindex(DIAS).diff())).fillna(0)


def acoes(d):
    """P (preço bruto, último negócio até 5 dias), R (retorno total), ADV (média 60d do volume, zeros incluídos)."""
    P = d["P"].reindex(DIAS)
    R = d["R"].reindex(DIAS)
    ADV = d["V"].reindex(DIAS).fillna(0).rolling(60, min_periods=20).mean()
    return P, R, ADV


def futuros(d):
    """Por contrato: (retorno em excesso diário, nocional de 1 contrato em R$). Tudo calendário B3, só dados até t."""
    cdi = CDI.reindex(DIAS).fillna(0)
    ibov = br(d, "ibov").ffill(limit=5)
    out = {"WIN": ((ibov.pct_change(fill_method=None).fillna(0) - cdi), .20 * ibov)}   # Ibovespa é índice de retorno total
    # dólar: DOL rolado (2019+); antes, PTAX - (CDI - cupom) com cupom = Fed funds + 1,07 pp (premissa do fundo institucional de carry)
    ff = eua_ffill(d, "dff").fillna(0) / 100
    cupom = (br(d, "cupom_aa") / 100).fillna(ff + .0107)
    sint = PTAX.pct_change(fill_method=None).fillna(0) - (cdi - cupom / 252)
    dol = br(d, "dol_ret")
    ini = d["br"]["dol_ret"].dropna().index.min()
    rw = sint.where(DIAS < ini, dol.fillna(0)) if pd.notna(ini) else sint
    out["WDO"] = (rw, 10_000 * PTAX)
    for k, mult in (("BGI", 330.0), ("CCM", 450.0)):
        px = br(d, f"{k.lower()}_px").ffill(limit=5)
        out[k] = (br(d, f"{k.lower()}_ret").fillna(0).where(px.notna(), 0), mult * px)
    # MCL: retorno do BNO (Brent, ETF de futuros) - T-bill, em US$; nocional = 100 barris x Brent (Yahoo) x PTAX
    rb = ret_eua(d, "bno") - TBILL
    lvl = eua_ffill(d, "brent").fillna(eua_ffill(d, "wti"))
    out["MCL"] = (rb, 100 * lvl * PTAX)
    return out


def beta_rolante(y, X, jan=252, passo=5, lim=(0, 3)):
    """Betas de y em X (DataFrame) com retornos de `passo` dias, janela `jan`, só passado (shift 1). Regressão múltipla por fórmula
    de covariâncias rolantes."""
    ys = y.rolling(passo).sum()
    Xs = X.rolling(passo).sum()
    k = X.shape[1]
    if k == 1:
        c = ys.rolling(jan, min_periods=jan // 2).cov(Xs.iloc[:, 0])
        v = Xs.iloc[:, 0].rolling(jan, min_periods=jan // 2).var()
        return pd.DataFrame({X.columns[0]: (c / v).clip(*lim).shift(1)})
    # 2 fatores: solução fechada
    a, b = Xs.iloc[:, 0], Xs.iloc[:, 1]
    r = lambda s: s.rolling(jan, min_periods=jan // 2)
    vaa, vbb, vab = r(a).var(), r(b).var(), r(a).cov(b)
    cya, cyb = r(ys).cov(a), r(ys).cov(b)
    det = vaa * vbb - vab ** 2
    ba = ((cya * vbb - cyb * vab) / det).clip(*lim).shift(1)
    bb = ((cyb * vaa - cya * vab) / det).clip(*lim).shift(1)
    return pd.DataFrame({X.columns[0]: ba, X.columns[1]: bb})


# ================================================================ motor
def _rodadas(pos):
    """Para cada coluna, id de rodada (posição contínua com o mesmo sinal); 0 = zerado."""
    s = np.sign(pos)
    nova = s.ne(s.shift(1)) & s.ne(0)
    rid = nova.cumsum().where(s.ne(0), 0)
    return rid


def livro(capital, acoes_alvo=None, fut_alvo=None, d=None, lag=0, custo_mult=1.0, alavancagem=1.0, taxa_aluguel=None,
          classe_acoes="acoes", aluguel_fixo=True):
    """acoes_alvo: DataFrame (DIAS x tickers) alvo em fração do capital, sinal = lado, decidido no fechamento de t.
    fut_alvo: dict nome_perna -> (contrato, Series alvo de nocional em fração do capital, sinal = lado).
    taxa_aluguel: dict ticker -> taxa a.a. ao doador (padrão 1%).
    Devolve dict: e (excesso diário, fração do capital), classes (P&L R$ por classe de IR + '_cdi_perdido'), contrib (excesso R$ por
    ativo), pos (ações/contratos executados), W (alvo de exposição decidido em t), Rx (retorno em excesso por ativo), diag."""
    cdi = CDI.reindex(DIAS).fillna(0)
    L = float(alavancagem)
    contrib, Wdec, Rx, pos, ret_ativo = {}, {}, {}, {}, {}
    cls = {}
    diag = {}
    marg_b3 = pd.Series(0.0, index=DIAS)
    marg_cme = pd.Series(0.0, index=DIAS)
    longo = pd.Series(0.0, index=DIAS)
    vend = pd.Series(0.0, index=DIAS)
    fut_cache = futuros(d) if fut_alvo else {}
    # ---------------- ações
    if acoes_alvo is not None and acoes_alvo.shape[1]:
        P, R, ADV = acoes(d)
        tk = list(acoes_alvo.columns)
        P, R, ADV = P.reindex(columns=tk), R.reindex(columns=tk), ADV.reindex(columns=tk)
        W = acoes_alvo.reindex(DIAS).fillna(0) * L
        Pn = P.ffill(limit=5)
        parado = P.isna().rolling(5, min_periods=5).sum().ge(5)
        W = W.where(~parado & Pn.notna(), 0.0)
        mud = W.ne(W.shift(1))
        N0 = np.trunc(W * capital / Pn).where(mud).ffill().fillna(0)
        N0 = N0.where(W.ne(0), 0.0)
        Nx = N0.shift(1 + lag).fillna(0)
        Nx = Nx.where(~parado, 0.0)
        Rf = R.fillna(0)
        I = (1 + Rf).cumprod()
        mx = Nx.ne(Nx.shift(1))
        U = (Nx * Pn / I).where(mx).ffill().fillna(0)
        U = U.where(Nx.ne(0), 0.0)
        Vv = U * I                                                     # valor (R$, sinal = lado) no fechamento de t
        V1 = Vv.shift(1).fillna(0)
        bruto = V1 * Rf                                                # ganho real (com proventos)
        dV = (Vv - V1 * (1 + Rf))                                      # o que foi negociado em t (R$, sinal)
        sh = (dV.abs() / Pn).fillna(0)
        lote = np.floor(sh / 100) * 100
        ms = pd.DataFrame(meio_spread(ADV.fillna(0).values), index=DIAS, columns=tk)
        custo = (dV.abs() * EMOL + lote * Pn.fillna(0) * ms + (sh - lote) * Pn.fillna(0) * ms * FRAC_MULT) * custo_mult
        # aluguel
        tx = pd.Series({t: (taxa_aluguel or {}).get(t, .01) for t in tk})
        curto = V1.clip(upper=0).abs()
        custo += curto * tx * 1.2 / 252 * custo_mult
        if aluguel_fixo:
            # idade da posição vendida (pregões desde a abertura) -> paga o fixo na abertura e a cada BTC_RENOVA
            nv = Vv.lt(0)
            c = nv.cumsum()
            idade = c - c.where(~nv).ffill().fillna(0)
            paga = nv & ((idade == 1) | ((idade - 1) % BTC_RENOVA == 0))
            aum = (dV < 0) & Vv.lt(0) & (idade > 1)                    # aumento de posição vendida = contrato novo
            custo += (Vv.abs().where(paga, 0) + dV.abs().where(aum, 0)) * BTC_FIXO * custo_mult
        exc = V1 * (Rf.sub(cdi, axis=0)) - custo
        longo = Vv.clip(lower=0).sum(axis=1)
        vend = Vv.clip(upper=0).abs().sum(axis=1)
        # financiamento a termo do que passa do capital (só com alavancagem > 1)
        fin = (longo.shift(1).fillna(0) - capital).clip(lower=0)
        custo_fin = fin * TERMO_SPREAD / 252 * custo_mult
        vendas = (dV.clip(upper=0).abs()).sum(axis=1)
        pnl_acoes = bruto.sum(axis=1) - custo.sum(axis=1) - custo_fin
        if classe_acoes == "acoes":
            mes = DIAS.to_period("M")
            isento = pd.Series(mes.map(vendas.groupby(mes).sum() <= 20_000), index=DIAS).astype(bool)
            cls["acoes_isentas"] = pnl_acoes.where(isento, 0.0)
            cls["acoes"] = pnl_acoes.where(~isento, 0.0)
        else:
            cls[classe_acoes] = pnl_acoes
        cls["_cdi_perdido"] = V1.sum(axis=1) * cdi                    # comprado: CDI que deixou de ganhar; vendido: CDI a mais (negativo)
        for t in tk:
            contrib[t] = exc[t]
            Wdec[t] = (N0[t] * Pn[t] / capital).fillna(0)
            Rx[t] = (Rf[t] - cdi)
            pos[t] = Nx[t]
            ret_ativo[t] = Rf[t]
        contrib["_termo"] = -custo_fin
        diag["acoes_max_long_R$"] = float(longo.max())
        diag["acoes_max_vendido_R$"] = float(vend.max())
    # ---------------- futuros
    req_b3 = pd.Series(0.0, index=DIAS)
    for nome, (ct, alvo) in (fut_alvo or {}).items():
        r, unit = fut_cache[ct]
        esp = FUT[ct]
        alvo = alvo.reindex(DIAS).fillna(0) * L
        mud = alvo.ne(alvo.shift(1))
        n0 = (alvo * capital / unit).round().where(mud).ffill().fillna(0)
        n0 = n0.where(alvo.ne(0), 0.0).where(unit.notna(), 0.0)
        n = n0.shift(1 + lag).fillna(0)
        n1 = n.shift(1).fillna(0)
        pnl = (n1 * unit.shift(1) * r).fillna(0)
        fx = PTAX if esp["moeda"] == "USD" else 1.0
        mes = pd.Series(DIAS.year * 12 + DIAS.month, index=DIAS)
        virada = mes.ne(mes.shift(1)) & (mes % esp["roll"] == 0)
        giro = (n - n1).abs() + 2 * n1.abs().where(virada & n.ne(0) & n1.ne(0), 0)
        custo = giro * esp["custo"] * fx * custo_mult
        exc = pnl - custo
        marg = n.abs() * unit * esp["margem"]
        if esp["moeda"] == "USD":
            marg_cme = marg_cme + marg.fillna(0)
            cls["exterior"] = cls.get("exterior", 0) + exc
        else:
            req_b3 = req_b3 + marg.fillna(0)
            cls["futuros_b3"] = cls.get("futuros_b3", 0) + exc
        contrib[nome] = exc
        Wdec[nome] = (n0 * unit / capital).fillna(0)
        Rx[nome] = r
        pos[nome] = n
        ret_ativo[nome] = r
        diag[f"{nome}_contratos_max"] = float(n.abs().max())
        diag[f"{nome}_dias_com_posicao_%"] = float((n != 0).mean() * 100)
    if (marg_cme > 0).any():
        custo_ext, saldo = pf.custo_conta_exterior(marg_cme)
        cdi_ext = saldo.shift(1).fillna(0) * cdi
        cls["exterior"] = cls.get("exterior", 0) - (custo_ext - cdi_ext) * custo_mult
        cls["_cdi_perdido"] = cls.get("_cdi_perdido", 0) + cdi_ext
        contrib["_conta_ibkr"] = -(custo_ext - cdi_ext) * custo_mult - cdi_ext
        diag["ibkr_saldo_max_R$"] = float(saldo.max())
    # ---------------- garantia (diagnóstico): Tesouro livre + 70% das ações compradas tem de cobrir margens + 25% do vendido
    livre = capital - longo.clip(upper=capital)
    folga = livre + GARANTIA_ACAO * longo - req_b3 - GARANTIA_VENDIDO * vend - (pf.custo_conta_exterior(marg_cme)[1] if (marg_cme > 0).any() else 0)
    diag["garantia_dias_faltando_%"] = float((folga < 0).mean() * 100)
    diag["garantia_pior_folga_R$"] = float(folga.min())
    cls = {k: (v if isinstance(v, pd.Series) else pd.Series(v, index=DIAS)).reindex(DIAS).fillna(0) for k, v in cls.items()}
    perd = cls.get("_cdi_perdido", pd.Series(0.0, index=DIAS))
    e = (sum(v for k, v in cls.items() if k != "_cdi_perdido") - perd) / capital
    return {"e": e.fillna(0), "classes": cls, "contrib": pd.DataFrame(contrib).fillna(0), "pos": pd.DataFrame(pos).fillna(0),
            "W": pd.DataFrame(Wdec).fillna(0), "Rx": pd.DataFrame(Rx).fillna(0), "ret": pd.DataFrame(ret_ativo).fillna(0), "diag": diag}


def negocios_de(res, capital, ativos=None):
    """Um negócio por rodada contínua de posição (mesmo sinal) em cada ativo/perna. contrib_pp = excesso líquido / capital x 100."""
    pos, con, ret = res["pos"], res["contrib"], res["ret"]
    linhas = []
    for a in (ativos or pos.columns):
        p = pos[a]
        if not (p != 0).any():
            continue
        rid = _rodadas(p)
        for k, g in p[rid > 0].groupby(rid[rid > 0]):
            ini, fim = g.index[0], g.index[-1]
            fim_ef = DIAS[DIAS > fim][0] if (DIAS > fim).any() else fim
            janela = DIAS[(DIAS >= ini) & (DIAS <= fim_ef)]
            linhas.append({"ativo": a, "lado": int(np.sign(g.iloc[0])), "entrada": ini.date(), "saida": fim_ef.date(), "dias": len(janela),
                           "qtd_ini": float(g.iloc[0]),
                           "retorno_%": float(((1 + ret[a].reindex(janela[1:]).fillna(0)).prod() - 1) * 100 * np.sign(g.iloc[0])),
                           "contrib_pp": float(con[a].reindex(janela).fillna(0).sum() / capital * 100)})
    cols = ["ativo", "lado", "entrada", "saida", "dias", "qtd_ini", "retorno_%", "contrib_pp"]
    return pd.DataFrame(linhas, columns=cols)


def maquina(entra, sai, max_dias, lado=1, espera=0):
    """Máquina de estados por coluna (só passado): abre quando `entra` (t), fica até `sai` ou `max_dias` pregões; depois de sair espera
    `espera` pregões para reabrir (sem reentrada no mesmo dia). entra/sai: DataFrames booleanos; lado: escalar ou DataFrame (+1/-1)."""
    E, S = entra.fillna(False).to_numpy(bool), sai.fillna(False).to_numpy(bool)
    Ld = np.broadcast_to(np.asarray(lado if np.isscalar(lado) else lado.reindex_like(entra).fillna(0).to_numpy()), E.shape)
    out = np.zeros(E.shape)
    for j in range(E.shape[1]):
        dentro, idade, sinal, pausa = False, 0, 0.0, 0
        for i in range(E.shape[0]):
            if dentro:
                idade += 1
                if S[i, j] or idade >= max_dias:
                    dentro, pausa = False, espera
                else:
                    out[i, j] = sinal
                continue                                   # nunca reabre no mesmo dia em que saiu
            if pausa > 0:
                pausa -= 1
                continue
            if E[i, j]:
                dentro, idade, sinal = True, 0, float(Ld[i, j]) if Ld[i, j] != 0 else 1.0
                out[i, j] = sinal
    return pd.DataFrame(out, index=entra.index, columns=entra.columns)


def padrao(m, d, capital, lag, custo_mult, alavancagem, params):
    """Atalho: roda o livro do fundo m com PARAMS + params."""
    return m._livro(d, capital=capital, lag=lag, custo_mult=custo_mult, alavancagem=alavancagem, **{**m.PARAMS, **params})


def congela(x, pos):
    """Valor de x (ex.: beta) fixado no dia em que a posição abriu/mudou de sinal; zero fora de posição (o hedge não é refeito todo dia)."""
    x = x.reindex_like(pos)
    abre = np.sign(pos).ne(np.sign(pos).shift(1)) & pos.ne(0)
    return x.where(abre).ffill().where(pos.ne(0), 0.0).fillna(0)
