"""
Carry de moedas — versão PF (R$ 20–50 mil): micro FX da CME na IBKR (só a margem lá fora) + mini-dólar WDO na B3 (garantia em Tesouro
Selic rende CDI). Cobre as linhas 11, A1, JF7 e I9 do ranking (carry G10+EM, G10+LatAm com teto, carry "realista" CME/B3, real tático).

Negócio de mesa: todo fim de mês ranqueio as moedas que têm futuro de varejo pelo carry que o FUTURO paga (paridade coberta: o futuro
comprado na moeda rende spot + (juro da moeda − juro do dólar)). Compro a de maior carry e vendo a de menor (n por lado), contratos
INTEIROS. Na prática o livro vira quase sempre "vendido em WDO (= comprado em real a CDI − cupom) contra vendido em MJY/MSF (= comprado
em dólar contra iene/franco)": o cruzado BRL/JPY, o carry trade clássico de emergente contra financiador. Quem paga: o importador/
tesouraria que compra dólar a termo no Brasil (cupom cambial abaixo do Fed funds + CDI alto) e o investidor japonês/suíço que hedgeia.
Lição JF7/I9 (lira turca): regra EX-ANTE de juro real — não fico comprado em moeda com juro real negativo (política − CPI 12m do BIS,
defasado 2 meses). Em 2021 isso tirou o real do lado comprado (Selic 2% com IPCA 6–10%).

Rota PF (o que muda frente ao institucional):
  - pernas G10 por micro futuros da CME (M6E, M6B, M6A, MCD, MSF, MJY) na IBKR; perna BRL por WDO na B3 (Clear/Rico, corretagem zero).
    Variante "mex_afs": MEX e AFS da B3 (US$ 10 mil, moeda contra USD liquidado em R$) — acesso de varejo NÃO confirmado (MAPA_ATIVOS_FX_B3).
  - contratos inteiros: alvo = vol-alvo por perna / vol da perna x capital; se o alvo arredonda para 0, entra 1 contrato SE o risco de
    1 contrato (nocional x vol / capital) <= teto_vol x alavancagem. Com R$ 20 mil, 1 WDO (US$ 10 mil ~ R$ 50 mil) tem vol de ~35% do
    capital e só entra com teto_vol alto; MJY/M6A (~1,7–2x o capital) entram. A alavancagem efetiva (nocional bruto / capital) é reportada.
  - caixa: a garantia da B3 fica em Tesouro Selic (rende CDI: excesso = só o ajuste do futuro); na IBKR fica max(US$ 2.000, 1,5x a margem
    inicial) — conta margem exige US$ 2.000 de patrimônio (FINRA 4210 / IBKR). Esse saldo perde o CDI e fica exposto ao dólar
    (pf.custo_conta_exterior). sgov=True: o que excede 1,5x a margem fica em SGOV (T-bill − 0,09%), que conta para os US$ 2.000.
  - P&L da IBKR volta ao Brasil todo mês (remessa: volta 0,38% + 0,5%; reposição de perda: 1,1% + 0,5%).

Retorno de cada perna = variação do spot + carry/252 (não uso futuro contínuo do Yahoo: rolagem com salto). Carry:
  G10 = juro de política BIS (vigente na véspera) da moeda − EUA; BRL = CDI − cupom cambial do 1º FRC (2019+), antes Selic − FF − 1,07 pp
  (constante medida em 2019+, herdada do institucional — premissa estimada depois, documentada); MXN/ZAR (variante) com −0,5 pp para
  quem compra e +0,5 pp para quem vende (como o institucional). Validação do carry G10 contra os futuros da CME: ver o caderno.

Custos (custo_mult multiplica todos):
  micro FX CME: comissão IBKR US$ 0,25 + taxa CME/IBKR US$ 0,24 + NFA 0,02 ~ US$ 0,51 + 1 tick de meio spread (US$ 0,6–1,25) ~ US$ 1,6/lado
    (fontes: interactivebrokers.com/en/accounts/fees/CME.php; brokerchooser.com .../micro-eurusd-futures-fees). Rolagem trimestral = 2 lados.
  margem de manutenção (CME, out/2026, MAPA_ATIVOS_FX_B3): M6E US$ 210, MJY 280, MSF 360, M6A 175, MCD 80, M6B 170 -> como fração do
    nocional de hoje, aplicada ao nocional histórico; inicial = 1,1x.
  WDO: R$ 1,20 (emolumentos/registro) + meio tick (0,5 pt x R$ 10 = R$ 5 -> R$ 2,50) = R$ 3,70/lado; rolagem mensal = 2 lados.
  MEX/AFS (variante): R$ 1,20 + 2,5 bps do nocional por lado (livro raso: ~80–270 contratos/dia), rolagem mensal.
IR (pf.apos_ir_por_classe): CME -> "exterior" (Lei 14.754/2023, 15% anual com compensação); WDO/MEX/AFS -> "futuros_b3"; variação cambial
  do saldo parado na IBKR (depósito não remunerado) -> "isento"; IOF/spread de remessa (não dedutível) -> "isento" negativo; SGOV -> "exterior".
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _util as U  # noqa: E402

C, pf = U.C, U.pf

NOME = "Carry de moedas PF (micro FX CME + WDO)"
TESE = ("Fim de mês: comprado na moeda de maior carry e vendido na de menor entre as que têm futuro de varejo (micro FX CME na IBKR, "
        "real via WDO), sem comprar moeda de juro real negativo; contratos inteiros, garantia B3 em Tesouro Selic, só margem na IBKR")
BENCHMARK = "CDI"
INICIO, CORTE = "2010-01-01", "2021-01-01"
REGIME = "nenhum"
CUSTO_TROCA = .0005
PARAMS = {"n": 1, "filtro_real": 1, "teto_vol": .40, "alvo": .08, "livro": "g10_brl", "sgov": True}
GRADE = {"n": [1, 2], "filtro_real": [0, 1], "teto_vol": [.25, .40]}
VIZINHANCA = {"teto_vol": (.25, .5), "alvo": (.05, .12)}
RANKING = ["11 Carry de moedas global", "A1 Carry G10+LatAm (teto real + stop)", "JF7 Carry de moedas realista (CME/B3)",
           "I9 Carry de moedas realista / real tático EM"]
INSTRUMENTOS = ("IBKR/CME (conta margem, mín. US$ 2.000): M6E € 12.500, M6B £ 6.250, M6A A$ 10.000, MCD C$ 10.000, MSF CHF 12.500, "
                "MJY ¥ 1,25 mi; margem manutenção US$ 80–360/contrato; custo ~US$ 1,6/lado (comissão 0,25 + taxas 0,26 + 1 tick). "
                "B3 (Clear/Rico): WDO US$ 10 mil, garantia em Tesouro Selic, R$ 3,70/lado, rolagem mensal. Variante: MEX/AFS (B3, US$ 10 mil, "
                "acesso de varejo não confirmado). Caixa em Tesouro Selic; na IBKR só max(US$ 2 mil, 1,5x margem), excedente em SGOV.")
APLICAVEL = True
MOTIVO = ("opera de verdade com R$ 20–50 mil (1–2 contratos por perna, margem < US$ 1 mil), mas cada contrato é 1,4–3x o capital: "
          "o livro é um par concentrado (tipicamente vendido WDO x vendido MJY = BRL/JPY), vol 15–35% do capital, não o carry diversificado")
ALAVANCAGENS = [1, 1.5, 2, 5]
MOTIVO_ALAV = ("alavancagem multiplica o alvo de nocional e o teto de risco de 1 contrato; com contratos inteiros 1x e 1,5x quase "
               "sempre dão o mesmo livro (1 contrato por perna); 5x = 2–4 contratos por perna (nocional 8–15x o capital)")
VARIANTES = {"só WDO (real tático)": {"livro": "wdo_tatico"}, "G10 micro top1/bottom1": {"livro": "g10"},
             "com MEX/AFS B3": {"livro": "g10_brl_mex_afs"}, "sem SGOV (saldo IBKR parado)": {"sgov": False},
             "regime risco_global": {"regime": "risco_global"}, "regime dd_stop": {"regime": "dd_stop"},
             "1 contrato sempre (teto_vol 9)": {"teto_vol": 9.0}}

# ---------------------------------------------------------------- especificações
# moeda (coluna do Yahoo: US$ por 1 unidade) -> (contrato, país BIS, tamanho em moeda ou US$, onde, margem manutenção US$ hoje, custo)
CME = {"EURUSD=X": ("M6E", "XM", 12_500, 210), "GBPUSD=X": ("M6B", "GB", 6_250, 170), "AUDUSD=X": ("M6A", "AU", 10_000, 175),
       "CAD=X": ("MCD", "CA", 10_000, 80), "CHF=X": ("MSF", "CH", 12_500, 360), "JPY=X": ("MJY", "JP", 1_250_000, 280)}
# câmbio de referência (out/2026, US$ por unidade) usado só para converter a margem em US$ numa fração do nocional (constante, sem dado)
REF = {"EURUSD=X": 1.12, "GBPUSD=X": 1.325, "AUDUSD=X": .69, "CAD=X": .70, "CHF=X": 1.20, "JPY=X": .00633}
B3 = {"BRL": ("WDO", "BR"), "MXN=X": ("MEX", "MX"), "ZAR=X": ("AFS", "ZA")}
LIVROS = {"g10_brl": list(CME) + ["BRL"], "g10": list(CME), "g10_brl_mex_afs": list(CME) + ["BRL", "MXN=X", "ZAR=X"],
          "wdo_tatico": ["BRL"]}
CME_LADO = .51 + 1.10                       # US$ por contrato por lado (comissão+taxas + ~1 tick de meio spread)
WDO_LADO = 1.20 + 2.50                      # R$ por contrato por lado
B3FX_LADO_FIXO, B3FX_LADO_BPS = 1.20, .00025
B3_USD = 10_000.0                            # WDO/MEX/AFS: US$ 10 mil
MIN_CONTA = 2000.0                           # US$
SGOV_TAXA = .0009
SPREAD_CUPOM_BRL = .0107
VOLTA, IDA = pf.REMESSA_VOLTA + pf.SPREAD_CAMBIO, pf.REMESSA_IDA + pf.SPREAD_CAMBIO


def carrega():
    return {"fx": pd.read_parquet(U.TOP5 / "carry_moedas" / "fx_usd_por_moeda.parquet"),
            "bis": pd.read_csv(U.TOP5 / "carry_moedas" / "bis_juros_politica.csv", index_col=0, parse_dates=True),
            "cupom": pd.read_csv(U.TOP5 / "carry_moedas" / "cupom_frc.csv", index_col=0, parse_dates=True)["cupom_frc_aa_pct"],
            "cpi": pd.read_parquet(U.FD / "icj_cpi.parquet")}


# ---------------------------------------------------------------- mercado (cache por id + tamanho + data máxima de d)
_CACHE = {}


def _no(s, idx):
    """Nível (último disponível) no calendário idx."""
    s = s[~s.index.duplicated(keep="last")]
    return s.reindex(idx.union(s.index)).ffill().reindex(idx)


def _mercado(d):
    chave = (id(d["fx"]), len(d["fx"]), d["fx"].index.max(), len(d["bis"]), len(d["cupom"]), len(d["cpi"]))
    if chave in _CACHE:
        return _CACHE[chave]
    D = C.DIAS
    D = D[D <= max(d["fx"].index.max(), d["bis"].index.max())]
    bis = _no(d["bis"], D).shift(1) / 100                                # juro vigente na véspera
    ptax = pf.PTAX.reindex(D)
    nivel, ret, car = {}, {}, {}
    for m in list(CME) + ["MXN=X", "ZAR=X"]:
        s = _no(d["fx"][m], D)
        nivel[m] = s
        ret[m] = s.pct_change(fill_method=None).fillna(0)
        pais = CME[m][1] if m in CME else B3[m][1]
        car[m] = bis[pais] - bis["US"]
    # BRL: comprado em real = vendido em WDO. Retorno = −ΔPTAX/PTAX + (CDI − cupom)
    cup = _no(d["cupom"], D).shift(1) / 100
    cup = cup.where(D >= d["cupom"].index.min())
    b3 = (1 + C.CDI.reindex(D).shift(1)) ** 252 - 1 - cup
    car["BRL"] = b3.combine_first(bis["BR"] - bis["US"] - SPREAD_CUPOM_BRL)
    nivel["BRL"] = 1 / ptax
    ret["BRL"] = -ptax.pct_change(fill_method=None).fillna(0)
    # juro real ex-ante: política − CPI 12m (mês de referência + 2 meses), por país
    cpi = d["cpi"].copy()
    cpi.index = cpi.index + pd.offsets.MonthBegin(2)
    cpi = _no(cpi, D) / 100
    paises = {m: (CME[m][1] if m in CME else B3[m][1]) for m in nivel}
    real = pd.DataFrame({m: bis[p] - cpi[p] if p in cpi else np.nan for m, p in paises.items()})
    reald = pd.DataFrame({m: real[m] - (bis["US"] - cpi["US"]) for m in nivel})
    M = {"D": D, "ptax": ptax, "nivel": pd.DataFrame(nivel), "ret": pd.DataFrame(ret), "car": pd.DataFrame(car), "real": real,
         "reald": reald, "tb": C.TB_US.reindex(D, method="ffill").fillna(0), "cdi": C.CDI.reindex(D).fillna(0)}
    vol = M["ret"].rolling(63, min_periods=40).std() * np.sqrt(252)
    M["vol"] = vol
    # nocional de 1 contrato em R$
    noc = {}
    for m in M["nivel"]:
        noc[m] = (M["nivel"][m] * CME[m][2] * ptax) if m in CME else pd.Series(B3_USD, index=D) * ptax
    M["noc1"] = pd.DataFrame(noc)
    M["marg_frac"] = pd.Series({m: CME[m][3] / (REF[m] * CME[m][2]) for m in CME})
    _CACHE.clear()
    _CACHE[chave] = M
    return M


def _fim_mes(D):
    p = pd.Series(D.to_period("M"), index=D)
    return p.ne(p.shift(-1))


# ---------------------------------------------------------------- livro: contratos decididos em t
def _contratos(M, capital, alavancagem, n, filtro_real, teto_vol, alvo, livro):
    cols = LIVROS[livro]
    D = M["D"]
    car, vol, noc1 = M["car"][cols], M["vol"][cols], M["noc1"][cols]
    if livro == "wdo_tatico":
        # real tático (I9/JF6): comprado em real quando o diferencial de juro REAL do Brasil vs EUA está acima da média de 5 anos
        r = M["reald"]["BRL"]
        z = (r - r.rolling(1260, min_periods=750).mean()) / r.rolling(1260, min_periods=750).std()
        lado = pd.DataFrame({"BRL": ((z > 0) & (car["BRL"] > 0)).astype(float)})
        if filtro_real:
            lado = lado.where(M["real"][["BRL"]] > 0, 0.0)
        npernas = 1
    else:
        sc = car.copy()
        rk = sc.rank(axis=1, ascending=False)
        q = sc.notna().sum(axis=1)
        compra = (rk <= n)
        if filtro_real:
            compra &= (M["real"][cols] > 0).reindex(columns=cols).fillna(True)
        vende = (rk > q.values[:, None] - n) & sc.notna() & ~(rk <= n)
        lado = compra.astype(float) - vende.astype(float)
        npernas = 2 * n
    w = alvo / (vol * np.sqrt(npernas)) * alavancagem
    bruto = (w * capital / noc1).round()
    risco1 = noc1 * vol / capital
    um = (bruto == 0) & (risco1 <= teto_vol * alavancagem)
    N = lado * bruto.where(~um, 1.0)
    N = N.where(vol.notna() & noc1.notna() & car.notna(), 0.0).fillna(0)
    # rebalanceamento mensal: só a decisão do último pregão do mês
    fim = _fim_mes(D)
    N.loc[~fim.values] = np.nan
    N = N.ffill().fillna(0)
    N.loc[N.index < pd.Timestamp(INICIO) - pd.Timedelta(days=5)] = 0.0
    return N


# ---------------------------------------------------------------- motor
def _motor(d, capital=20000, custo_mult=1, lag=0, alavancagem=1, n=1, filtro_real=1, teto_vol=.4, alvo=.08, livro="g10_brl", sgov=True):
    M = _mercado(d)
    D, ptax = M["D"], M["ptax"]
    Nd = _contratos(M, capital, alavancagem, n, filtro_real, teto_vol, alvo, livro)
    Ne = Nd.shift(1 + lag).fillna(0)                                    # executado no fechamento de t+1+lag
    cols = list(Ne.columns)
    R = M["ret"][cols] + M["car"][cols].fillna(0) / 252                 # retorno do futuro comprado (excesso sobre o caixa)
    noc_ant = M["noc1"][cols].shift(1)
    pnl = Ne.shift(1).fillna(0) * noc_ant * R                           # R$ (nocional de ontem x retorno de hoje)
    pnl = pnl * (ptax / ptax.shift(1)).where(pd.Series([c in CME for c in cols], index=cols).reindex(cols).any(), 1.0).values[:, None] \
        if False else pnl
    # P&L das pernas CME em US$ convertidas pela PTAX de hoje (nocional x retorno em US$ x PTAX_t)
    for c in cols:
        if c in CME:
            pnl[c] = Ne[c].shift(1).fillna(0) * (M["nivel"][c].shift(1) * CME[c][2]) * R[c] * ptax
    giro = Ne.diff().abs().fillna(Ne.abs())
    mes = pd.Series(D.to_period("M"), index=D)
    novo_mes = mes.ne(mes.shift()).values
    rola_cme = novo_mes & np.isin(D.month, [3, 6, 9, 12])               # rolagem trimestral (início do mês de vencimento)
    custo = pd.DataFrame(0.0, index=D, columns=cols)
    for c in cols:
        if c in CME:
            lados = giro[c] + 2 * Ne[c].abs().shift(1).fillna(0) * rola_cme
            custo[c] = lados * CME_LADO * ptax
        elif c == "BRL":
            lados = giro[c] + 2 * Ne[c].abs().shift(1).fillna(0) * novo_mes
            custo[c] = lados * WDO_LADO
        else:
            lados = giro[c] + 2 * Ne[c].abs().shift(1).fillna(0) * novo_mes
            custo[c] = lados * (B3FX_LADO_FIXO + B3FX_LADO_BPS * M["noc1"][c])
    custo = custo * custo_mult
    liq = pnl - custo
    cme = [c for c in cols if c in CME]
    b3 = [c for c in cols if c not in CME]
    # conta na IBKR: só existe se há perna CME
    if cme:
        noc_cme = (Ne[cme].abs() * M["noc1"][cme]).sum(axis=1)
        marg = (Ne[cme].abs() * M["noc1"][cme] * M["marg_frac"][cme]).sum(axis=1) * 1.1      # inicial, R$
        req = np.maximum(MIN_CONTA * ptax, 1.5 * marg).where(noc_cme > 0, 0.0)
        custo_conta, saldo = pf.custo_conta_exterior(req, folga=1.0)
        custo_conta, saldo = custo_conta.reindex(D).fillna(0), saldo.reindex(D).fillna(0)
        fx_ret = pf.PTAX.pct_change(fill_method=None).reindex(D).fillna(0)
        cdi_perd = saldo.shift(1).fillna(0) * M["cdi"]
        cambial = saldo.shift(1).fillna(0) * fx_ret
        remessa = (custo_conta - cdi_perd + cambial) * custo_mult
        sg = ((saldo - 1.5 * marg).clip(lower=0).shift(1).fillna(0) * (M["tb"] - SGOV_TAXA / 252)) if sgov else pd.Series(0.0, index=D)
        # P&L do mês na IBKR volta (ou é reposto) no 1º pregão do mês seguinte
        pm = liq[cme].sum(axis=1).groupby(mes).sum()
        flx = pd.Series(0.0, index=D)
        prim = D[novo_mes]
        v = pm.shift(1).reindex(mes[novo_mes].values).fillna(0).values
        flx.loc[prim] = -(np.where(v > 0, v * VOLTA, -v * IDA)) * custo_mult
        exterior = liq[cme].sum(axis=1) + sg
        isento = cambial - remessa + flx
        alav_cme = noc_cme
    else:
        exterior = isento = cdi_perd = pd.Series(0.0, index=D)
        alav_cme = pd.Series(0.0, index=D)
    fut_b3 = liq[b3].sum(axis=1) if b3 else pd.Series(0.0, index=D)
    nocb = (Ne.abs() * M["noc1"][cols]).sum(axis=1)
    cls = {"exterior": exterior, "futuros_b3": fut_b3, "isento": isento, "_cdi_perdido": cdi_perd}
    cls = {k: v.reindex(C.DIAS).fillna(0) for k, v in cls.items()}
    e = (cls["exterior"] + cls["futuros_b3"] + cls["isento"] - cls["_cdi_perdido"]) / capital
    info = {"Ne": Ne, "R": R, "liq": liq, "noc": nocb.reindex(C.DIAS).fillna(0), "alav": (nocb / capital).reindex(C.DIAS).fillna(0),
            "Nd": Nd, "M": M}
    return e, cls, info


def _sinal_regime(e, regime):
    if regime in (None, "nenhum"):
        return pd.Series(1.0, index=e.index)
    if regime == "dd_stop":
        return C.regime_dd_stop(e)
    s = {"risco_global": C.regime_risco_global, "ibov_tendencia": C.regime_ibov_tendencia}[regime]()
    return s.reindex(e.index).ffill().fillna(1.0).shift(2).fillna(1.0)


def _com_regime(d, capital, custo_mult, lag, regime, alavancagem, **params):
    p = {**PARAMS, **params}
    e, cls, info = _motor(d, capital, custo_mult, lag, alavancagem, **p)
    e = e[e.index >= pd.Timestamp(INICIO)].reindex(C.DIAS).fillna(0)
    s = _sinal_regime(e, regime)
    troca = s.diff().abs().fillna(0) * CUSTO_TROCA * custo_mult
    cls = {k: v * s for k, v in cls.items()}
    cls = {k: v.where(v.index >= pd.Timestamp(INICIO), 0.0) for k, v in cls.items()}
    cls["isento"] = cls["isento"] - troca * capital
    return e * s - troca, cls, info


def excesso(d, capital=20000, custo_mult=1, lag=0, regime=REGIME, alavancagem=1, **params):
    return _com_regime(d, capital, custo_mult, lag, regime, alavancagem, **params)[0]


def classes_ir(d, capital=20000, regime=REGIME, **params):
    return _com_regime(d, capital, 1, 0, regime, 1, **params)[1]


def posicoes(d, capital=20000, **params):
    """W: nocional decidido em t / capital (com sinal); R: excesso diário do futuro comprado (spot + carry), em R$."""
    p = {**PARAMS, **params}
    M = _mercado(d)
    N = _contratos(M, capital, 1, p["n"], p["filtro_real"], p["teto_vol"], p["alvo"], p["livro"])
    W = N * M["noc1"][N.columns] / capital
    R = M["ret"][N.columns] + M["car"][N.columns].fillna(0) / 252
    nome = {c: (CME[c][0] if c in CME else B3[c][0]) for c in N.columns}
    return W.rename(columns=nome).reindex(C.DIAS).fillna(0), R.rename(columns=nome).reindex(C.DIAS).fillna(0)


def negocios(d, capital=20000, **params):
    """Um episódio de posição constante (mesmo sinal) por contrato; contrib_pp = P&L líquido de custos de negociação / capital.
    A conta IBKR (CDI perdido + remessas + câmbio do saldo + SGOV) entra como uma linha por ano ('conta IBKR')."""
    p = {**PARAMS, **params}
    e, cls, info = _com_regime(d, capital, 1, 0, "nenhum", 1, **p)
    Ne, R, liq = info["Ne"], info["R"], info["liq"]
    M = info["M"]
    lin, idx = [], Ne.index
    for c in Ne.columns:
        nome = CME[c][0] if c in CME else B3[c][0]
        s = np.sign(Ne[c].values)
        mud = np.flatnonzero(np.diff(np.r_[0, s]) != 0)
        for k, i0 in enumerate(mud):
            if s[i0] == 0:
                continue
            i1 = mud[k + 1] if k + 1 < len(mud) else len(s)
            seg = slice(i0 + 1, min(i1 + 1, len(s)))
            lado = int(s[i0])
            if idx[i0] < pd.Timestamp(INICIO):
                continue
            lin.append({"ativo": nome, "lado": lado, "entrada": idx[i0], "saida": idx[min(i1, len(s) - 1)], "dias": int(i1 - i0),
                        "contratos": float(np.abs(Ne[c].values[i0:i1]).mean()),
                        "nocional_x_capital": float((np.abs(Ne[c].values[i0:i1]) * M["noc1"][c].values[i0:i1]).mean() / capital),
                        "carry_aa_%": float(lado * M["car"][c].values[i0:i1].mean() * 100),
                        "spot_%": (np.prod(1 + lado * M["ret"][c].values[seg]) - 1) * 100,
                        "retorno_%": (np.prod(1 + lado * R[c].fillna(0).values[seg]) - 1) * 100,
                        "contrib_pp": liq[c].values[seg].sum() / capital * 100})
    conta = (cls["isento"] + cls["exterior"] - liq[[c for c in Ne.columns if c in CME]].sum(axis=1).reindex(C.DIAS).fillna(0)
             - cls["_cdi_perdido"]) if any(c in CME for c in Ne.columns) else None
    if conta is not None:
        for ano, x in conta[conta.index >= pd.Timestamp(INICIO)].groupby(conta[conta.index >= pd.Timestamp(INICIO)].index.year):
            if x.abs().sum() > 0:
                lin.append({"ativo": "conta IBKR", "lado": 1, "entrada": x.index[0], "saida": x.index[-1], "dias": len(x),
                            "retorno_%": np.nan, "contrib_pp": x.sum() / capital * 100})
    return pd.DataFrame(lin).sort_values(["entrada", "ativo"]).reset_index(drop=True)


def detalhe(d, capital=20000, **params):
    """Para o caderno: alavancagem efetiva média, % de dias com posição, livro mais comum."""
    p = {**PARAMS, **params}
    e, cls, info = _com_regime(d, capital, 1, 0, "nenhum", 1, **p)
    a = info["alav"]
    o = a[a.index >= pd.Timestamp(CORTE)]
    return {"alav. efetiva média OOS (x capital)": float(o[o > 0].mean()) if (o > 0).any() else 0.0,
            "alav. efetiva máx OOS": float(o.max()), "% dias com posição OOS": float((o > 0).mean() * 100),
            "alav. efetiva média IS": float(a[(a.index < pd.Timestamp(CORTE)) & (a > 0)].mean())}
