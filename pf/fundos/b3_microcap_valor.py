"""
Valor + qualidade em small/micro caps, com giro que cabe na isenção de IR de R$ 20 mil/mês.

Mesa: empresa pequena, lucrativa e barata (lucro 12m / valor de mercado alto, patrimônio acima do preço) fica barata porque NINGUÉM grande
pode comprá-la: giro de R$ 30 mil-10 milhões/dia, sem cobertura de corretora, fora dos índices. O preço só converge quando o lucro
aparece no balanço seguinte, alguém compra o controle (OPA) ou a empresa paga dividendos. Pessoa física tem duas vantagens que o
institucional não tem: (1) R$ 2-5 mil por papel entram e saem sem mover o preço; (2) se as vendas do mês ficarem em até R$ 20 mil, o
ganho é ISENTO de IR (o fundo de ações/ETF paga 15%). O fundo é desenhado para isso: rebalanceamento trimestral (depois da temporada de
balanços), quem continua barato e lucrativo fica, e as vendas do mês são limitadas a R$ 20 mil (o excedente fica para o mês seguinte).
Dados: lucro 12m, PL e nº de ações dos ITR/DFP/FRE da CVM, cada um a partir da DATA DE ENTREGA (DT_RECEB da versão disponível;
FRE: data de aprovação do capital); valor de mercado = ações x preço do papel mais líquido, atualizado pelo retorno de preço (robusto a
desdobramento). Um papel por empresa (o mais líquido). Lucro > 0, PL > 0, ROE entre 5% e 60% (filtro de qualidade; ROE absurdo = erro
de dado ou lucro não recorrente).
Sinais (escolha no IS): 'ep' (lucro/valor), 'ep_bp' (média dos rankings de lucro/valor e PL/valor), 'ep_max' (lucro/valor só entre os
papéis na metade de cima da distância à máxima de 52 semanas — evita a armadilha de valor que está quebrando).
"""
import numpy as np
import pandas as pd

import b3_base as B

C, pf = B.C, B.pf

NOME = "Valor + qualidade em small/micro caps, isento de IR (PF)"
TESE = ("Compro R$ 2-5 mil das small/micro caps lucrativas mais baratas (lucro e PL sobre valor de mercado, dados da CVM na data de "
        "entrega): baratas porque nenhum fundo grande consegue comprá-las; vendas do mês limitadas a R$ 20 mil para o ganho ser isento")
BENCHMARK = "CDI"
INICIO, CORTE = "2015-06-01", "2021-01-01"
REGIME = "nenhum"
CUSTO_TROCA = .001
PARAMS = {"sinal": "ep_max", "n": 10, "freq": 63, "adv_min": 3e4, "adv_max": 1e7, "manter": .33, "roe_min": .05, "spread_max": .03,
          "teto_vendas": 20000.0}
GRADE = {"sinal": ["ep", "ep_bp", "ep_max"], "freq": [21, 63], "adv_max": [3e6, 1e7]}
VIZINHANCA = {"n": (7, 14), "freq": (40, 90), "adv_max": (5e6, 2e7), "manter": (.2, .5), "roe_min": (0, .1)}
INSTRUMENTOS = [{"onde": "Clear/Rico/XP/BTG (B3 à vista + fracionário)", "ticker": "small/micro caps lucrativas", "lote": "1 ação",
                 "custo": "emolumentos 0,03% + meio spread real do fechamento + 0,2% na parte fracionária"}]
APLICAVEL = True
MOTIVO = "ações à vista; R$ 2-5 mil por papel; vendas do mês até R$ 20 mil (isenção de IR)"
ALAVANCAGENS = [1]
MOTIVO_ALAV = "comprado à vista; alavancar small caps com termo/conta margem (CDI + 4-8% a.a.) não se paga e quebra a isenção (giro)"
_RES = {}


def carrega():
    d = B.dados_acoes()
    f = B.ler("fundamentos").rename(columns={"dt_receb": "data"})
    a = B.ler("acoes_emitidas")
    return {**d, "fund": f[["data", "cnpj", "lucro_12m", "pl"]].copy(), "acoes": a[["data", "cnpj", "acoes"]].copy(),
            "mapa": B.ler("mapa_cnpj")}


def _por_empresa(d):
    """Valor de mercado, lucro 12m e PL por empresa (índice = DIAS, colunas = cnpj), com o papel mais líquido de cada empresa."""
    P, R, V = d["P"], d["R"], d["V"]
    mapa = d["mapa"].set_index("raiz").cnpj
    tk = [t for t in P.columns if t[:4] in mapa.index]
    emp = pd.Series({t: mapa[t[:4]] for t in tk})
    adv = V[tk].fillna(0).rolling(60, min_periods=20).mean()
    # papel mais líquido de cada empresa em cada dia
    lider = {}
    for cn, ts in emp.groupby(emp).groups.items():
        ts = list(ts)
        lider[cn] = adv[ts].fillna(-1).idxmax(axis=1).where(adv[ts].max(axis=1) > 0) if len(ts) > 1 else pd.Series(ts[0], index=P.index)
    lider = pd.DataFrame(lider)
    padj = np.exp(np.log1p(R.fillna(0).clip(-.9, 5)).cumsum())
    praw = P.ffill(limit=10)

    def pega(M, L):
        out = pd.DataFrame(np.nan, index=L.index, columns=L.columns)
        for cn in L.columns:
            l = L[cn]
            for t in l.dropna().unique():
                m = l == t
                out.loc[m, cn] = M.loc[m, t]
        return out
    PA, PR = pega(padj, lider), pega(praw, lider)
    # nº de ações: vale a partir da data do registro; valor de mercado = (ações x preço no dia do registro) x retorno de preço desde então
    ac = d["acoes"].copy()
    ac = ac[ac.cnpj.isin(lider.columns)]
    K = pd.DataFrame(np.nan, index=P.index, columns=lider.columns)
    for cn, g in ac.groupby("cnpj"):
        i = P.index.searchsorted(pd.to_datetime(g.data))
        pv = PR[cn].first_valid_index()
        if pv is None:
            continue
        i = np.maximum(i, P.index.get_loc(pv))                     # registro anterior ao início dos preços vale a partir do 1º preço
        for ii, q in zip(i, g.acoes):
            if ii < len(P) and PR[cn].iloc[ii] > 0:
                K.iloc[ii, K.columns.get_loc(cn)] = q * PR[cn].iloc[ii] / PA[cn].iloc[ii]
    mcap = K.ffill() * PA
    fu = d["fund"].copy()
    fu = fu[fu.cnpj.isin(lider.columns)]
    fu["i"] = P.index.searchsorted(pd.to_datetime(fu.data))
    fu = fu[fu.i < len(P)].sort_values("data").drop_duplicates(["cnpj", "i"], keep="last")
    L = fu.pivot(index="i", columns="cnpj", values="lucro_12m").reindex(range(len(P))).ffill(limit=400)
    PL = fu.pivot(index="i", columns="cnpj", values="pl").reindex(range(len(P))).ffill(limit=400)
    L.index = PL.index = P.index
    return mcap, L.reindex(columns=lider.columns), PL.reindex(columns=lider.columns), lider, padj


def roda(d, capital=20000, custo_mult=1, lag=0, sinal="ep_max", n=10, freq=63, adv_min=3e4, adv_max=1e7, manter=.33, roe_min=.05,
         spread_max=.03, teto_vendas=20000.0):
    k = (id(d), capital, custo_mult, lag, sinal, n, freq, adv_min, adv_max, manter, roe_min, spread_max, teto_vendas)
    if k in _RES:
        return _RES[k]
    ck = ("emp", id(d))
    if ck not in _RES:
        _RES[ck] = _por_empresa(d)
    mcap, L, PL, lider, padj = _RES[ck]
    P, V, HS = d["P"], d["V"], d["HS"]
    n, freq = int(n), int(freq)
    ep, bp, roe = L / mcap, PL / mcap, L / PL
    ok = (L > 0) & (PL > 0) & (roe >= roe_min) & (roe <= .6) & (ep < 1) & (bp < 10)
    # liquidez/spread do papel líder
    adv = V.fillna(0).rolling(60, min_periods=40).mean()
    pres = P.notna().rolling(60, min_periods=40).mean()
    hs = HS.where(P.notna()).rolling(10, min_periods=3).median()
    tick_ok = (adv >= adv_min) & (adv <= adv_max) & (pres >= .8) & (P.ffill(limit=5) >= 1) & (hs <= spread_max / 2)
    dist = np.log(padj / padj.rolling(252, min_periods=200).max())
    T = pd.DataFrame(False, index=P.index, columns=lider.columns)
    DS = pd.DataFrame(np.nan, index=P.index, columns=lider.columns)
    for cn in lider.columns:
        l = lider[cn]
        for t in l.dropna().unique():
            m = (l == t).values
            T.loc[m, cn] = tick_ok.loc[m, t].values
            DS.loc[m, cn] = dist.loc[m, t].values
    univ = ok & T
    if sinal == "ep":
        s = ep.where(univ)
    elif sinal == "ep_bp":
        s = ep.where(univ).rank(axis=1, pct=True) + bp.where(univ).rank(axis=1, pct=True)
    else:                                                                       # ep só na metade de cima da distância à máxima
        s = ep.where(univ & (DS.where(univ).rank(axis=1, pct=True) >= .5))
    rk = s.rank(axis=1, ascending=False, method="first")
    pct = s.rank(axis=1, pct=True)
    marca = pd.Series(np.arange(len(P)) % freq == 0, index=P.index) & (P.index >= pd.Timestamp(INICIO) - pd.Timedelta(days=100))
    tam = .95 * capital / n
    # empresa -> papel líder no dia da decisão
    sel = (rk <= n) & marca.values[:, None]
    mt = (pct >= 1 - manter) & marca.values[:, None]
    alvo, mant = {}, {}
    for cn in lider.columns:
        if not (sel[cn].any() or mt[cn].any()):
            continue
        for t in lider[cn].dropna().unique():
            m = (lider[cn] == t)
            alvo.setdefault(t, pd.Series(0.0, index=P.index))
            mant.setdefault(t, pd.Series(False, index=P.index))
            alvo[t] = alvo[t] + (sel[cn] & m).astype(float) * tam
            mant[t] = mant[t] | (mt[cn] & m)
    alvo = pd.DataFrame(alvo).where(marca, np.nan, axis=0)
    mant = pd.DataFrame(mant).where(marca, False, axis=0)
    res = B.carteira_pf(alvo, d, capital, custo_mult, lag, teto_vendas=teto_vendas, manter=mant, apara=(2 * tam, tam))
    if len(_RES) > 64:
        _RES.clear()
    _RES[k] = res
    return res


def excesso(d, capital=20000, custo_mult=1, lag=0, regime=REGIME, alavancagem=1, **params):
    e = roda(d, capital, custo_mult, lag, **{**PARAMS, **params})["e"] * alavancagem
    return C.aplica_regime(e, regime, CUSTO_TROCA * custo_mult)


def classes_ir(d, capital=20000, **params):
    return B.classes_acoes(roda(d, capital, **{**PARAMS, **params}))


def posicoes(d, capital=20000, **params):
    W = roda(d, capital, **{**PARAMS, **params})["W"]
    return W, d["R"].reindex(index=B.DIAS, columns=W.columns).fillna(0).sub(B.CDI, axis=0)


def negocios(d, capital=20000, **params):
    return roda(d, capital, **{**PARAMS, **params})["negocios"]
