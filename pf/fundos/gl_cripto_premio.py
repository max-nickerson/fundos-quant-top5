"""
Desconto dos ETFs de cripto da B3 contra o próprio bitcoin/ether em reais, com ORDEM LIMITADA (e o "kimchi premium" brasileiro medido).

Tese de mesa: QBTC11/BITH11 (bitcoin) e ETHE11/QETH11 (ether) são cestas de cripto à vista; o NAV acompanha o BTC/ETH em R$ minuto a
minuto, mas o preço na B3 é feito por formadores e por varejo que vende a mercado em dia de pânico cripto (FTX, nov/2022; ETF spot
aprovado, jan/2024). Deixo uma ordem de compra parada em K = justo x (1 - thr), justo = BTC-BRL (Binance, candle que fecha no horário do
fechamento da B3) x razão (mediana de 60 pregões de ETF/BTC-BRL até a véspera). Executa se a mínima do dia passar 0,25% abaixo de K;
vendo com ordem limitada no justo do dia anterior (ou no fechamento depois de `max_dias`). Hedge opcional com BIT (futuro de bitcoin
em R$ da B3) vendido em contratos inteiros: só cabe a partir de 16/06/2025, quando o contrato caiu de 0,1 para 0,01 BTC (R$ 4-6 mil).

"Kimchi premium" brasileiro (pesquisado, ver caderno): BTC-BRL do Mercado Bitcoin (2014+, 1h desde 2019) e da Binance (BTCBRL/USDTBRL
desde 10/2020) contra BTCUSDT x dólar: prêmio médio de 0,6-0,7% (dp 0,5-0,8%), o mesmo do USDT contra o dólar à vista — é o custo do
IOF/remessa que o brasileiro evita comprando cripto em reais; caiu de 1,6% (2019) para 0,25% (2026). Não há kimchi de 5-10% como na
Coreia, porque o real é conversível via USDT; o prêmio vira só um sinal de demanda local (usado no gl_cripto_tendencia).

CORREÇÃO (auditoria final): a ordem em "justo de ontem x (1 - thr)" só executava quando o próprio cripto caía no dia (desconto de
entrada sempre -2,47%) — era comprar a queda, não o desconto. Agora (execucao='fechamento', padrão) o desconto é medido no MESMO
instante (oferta de venda do ETF no fechamento x justo do candle de 1h que fecha no fechamento da B3), executado em t+1 na oferta de
venda e vendido na oferta de compra quando o desconto fecha. BIT vazio antes da listagem -> sem hedge (antes: erro de argmax no truncamento).
Custos: emolumentos 0,03% (limitada); saída forçada paga meio spread do fechamento. ETFs têm taxa de administração no preço.
IR: ETF na B3 15% (etf_b3), sem isenção; BIT 15% (futuros_b3). Dados de BTC-BRL a cada hora só desde 2019 -> INICIO 2021-07-01
(listagem dos ETFs), CORTE 2023-01-01.
"""
import numpy as np
import pandas as pd

import gl_comum as G

NOME = "Desconto de ETFs de cripto da B3 vs BTC/ETH em R$ (ordem limitada)"
TESE = "Ordem de compra parada abaixo do NAV dos ETFs de bitcoin/ether da B3; vende no NAV; hedge com BIT quando o contrato cabe"
BENCHMARK = "CDI"
INICIO, CORTE = "2021-07-01", "2023-01-01"
REGIME = "nenhum"
CLASSE_IR = "etf_b3"                                   # ETF na B3: 15%, sem isenção
CUSTO_TROCA = .001
PARAMS = {"thr": .025, "max_dias": 3, "hedge": "bit"}         # maior IR dentro da amostra (todas negativas no IS)
GRADE = {"thr": [.01, .015, .025], "max_dias": [1, 3], "hedge": ["nenhum", "bit"]}
VIZINHANCA = {"thr": (.018, .035), "max_dias": (2, 5)}
ETFS = {"QBTC11": "BTC", "BITH11": "BTC", "ETHE11": "ETH", "QETH11": "ETH"}
PESO, FURA = .20, .0025
BIT_MULT = lambda d: .1 if d < pd.Timestamp("2025-06-16") else .01         # BTC por contrato (B3; redução aprovada pela CVM em 2025)
BIT_CUSTO = .0005                                                          # emolumentos + meio tick por lado (premissa)
INSTRUMENTOS = {t: {"onde": "B3", "ticker": t, "lote": 1, "custo": "0,03% (limitada)"} for t in ETFS}
INSTRUMENTOS["BIT"] = {"onde": "B3 (futuro)", "ticker": "BIT", "lote": "0,01 BTC desde 06/2025 (0,1 antes)", "custo": "~0,05%"}
APLICAVEL = True
MOTIVO = "ETFs em cotas de R$ 10-100, ordem limitada em qualquer corretora; o hedge com BIT só cabe desde 06/2025."
ALAVANCAGENS = [1]
MOTIVO_ALAV = "Até 4 posições de 20% já usam 80% do PL."


def carrega():
    b = G.ler("b3_etf_bdr.parquet")
    f = G.ler("futuros_b3.parquet")
    c = G.ler("cripto_br.parquet")
    return {"b3": b[b.ticker.isin(ETFS)], "bit": f[f.ticker.str.startswith("BIT")], "cripto": c[c.fonte == "BN"]}


def bit_continuo(f):
    """Retorno diário do BIT segurando o contrato mais negociado da véspera (sem salto de rolagem) e o contrato do dia."""
    A = f.pivot_table(index="data", columns="ticker", values="AdjstdQt", aggfunc="last").reindex(G.DIAS)
    Q = f.pivot_table(index="data", columns="ticker", values="FinInstrmQty", aggfunc="last").reindex(G.DIAS)
    if A.shape[1] == 0:                       # BIT ainda não listado (dados cortados antes de 2021/2022): sem hedge possível
        vazio = pd.Series(np.nan, index=G.DIAS)
        return vazio, vazio
    ct = Q.fillna(-1).idxmax(axis=1).where(Q.notna().any(axis=1)).ffill()
    ct_ant = ct.shift(1)
    r = pd.Series([A.at[t, c] / A.at[p, c] - 1 if isinstance(c, str) and c in A and p is not None else np.nan
                   for t, p, c in zip(A.index, [None] + list(A.index[:-1]), ct_ant)], index=A.index)
    nivel = pd.Series([A.at[t, c] if isinstance(c, str) else np.nan for t, c in zip(A.index, ct)], index=A.index)
    return r, nivel


def _painel(d):
    b, c = d["b3"], d["cripto"]
    ref = {"BTC": G.cripto_no_fech_b3(c, "BN", "BTCBRL"), "ETH": G.cripto_no_fech_b3(c, "BN", "ETHBRL")}
    V = {k: G.pivo(b, k, list(ETFS)) for k in ("abertura", "max", "min", "fech", "oferta_compra", "oferta_venda", "negocios")}
    U = pd.DataFrame({t: ref[u] for t, u in ETFS.items()})
    neg = V["negocios"].fillna(0) > 0
    q = (np.log(V["fech"]) - np.log(U)).where(neg)
    med = q.rolling(60, min_periods=20).median().shift(1)
    salto = q.ffill().diff().abs() > .15
    bloq = salto.rolling(60, min_periods=1).max().fillna(0).astype(bool)
    justo = (np.exp(med) * U).where(~bloq)
    hs = G.meio_spread(V["oferta_compra"], V["oferta_venda"], .005, .05)
    return V, U, justo, hs, ref


def _simula(d, thr, max_dias, hedge, capital, custo_mult=1, lag=0, execucao="fechamento"):
    if execucao == "fechamento":
        return _simula_fech(d, thr, max_dias, hedge, capital, custo_mult, lag)
    V, U, J, HS, ref = _painel(d)
    tk = list(ETFS)
    O, H, L, F = (V[c][tk].values for c in ("abertura", "max", "min", "fech"))
    Jv, HSv = J[tk].values, HS[tk].values
    T, N = F.shape
    pnl, cus, car = np.zeros((T, N)), np.zeros((T, N)), np.zeros((T, N))
    cdi = G.CDI.reindex(G.DIAS).fillna(0).values
    pos, neg = {}, []
    btc_expo = np.zeros(T)
    ini = G.DIAS.searchsorted(pd.Timestamp(INICIO))
    for i in range(max(ini, 1 + lag), T):
        s = i - 1 - lag
        for j, p in list(pos.items()):
            if p["dia"] < i:
                car[i, j] -= p["n"] * p["ref"] * cdi[i]
                p["acc"] -= p["n"] * p["ref"] * cdi[i]
                if F[i, j] > 0:
                    x = p["n"] * (F[i, j] - p["ref"])
                    pnl[i, j] += x
                    p["acc"] += x
                    p["ref"] = F[i, j]
        for j, p in list(pos.items()):
            if p["dia"] >= i or not (F[i, j] > 0):
                continue
            k = Jv[s, j]
            px = None
            if k > 0 and O[i, j] >= k:
                px = O[i, j]
            elif k > 0 and H[i, j] > k * (1 + FURA):
                px = k
            elif i - p["dia"] >= max_dias:
                px = F[i, j] * (1 - HSv[i, j])
            if px is None:
                continue
            x = p["n"] * (px - p["ref"])
            c_ = p["n"] * px * G.B3_EMOL * custo_mult
            pnl[i, j] += x
            cus[i, j] += c_
            p["acc"] += x - c_
            neg.append({"ativo": tk[j], "lado": 1, "entrada": G.DIAS[p["dia"]], "saida": G.DIAS[i], "dias": i - p["dia"],
                        "retorno_%": (px / p["px"] - 1) * 100, "desconto_entrada_%": (p["px"] / p["justo"] - 1) * 100,
                        "contrib_pp": p["acc"] / capital * 100})
            del pos[j]
        for j in range(N):
            if j in pos or s < 0 or not (Jv[s, j] > 0) or not (L[i, j] > 0) or not (F[s, j] > 0):
                continue
            if not (.8 < O[i, j] / F[s, j] < 1.25):
                continue
            k = Jv[s, j] * np.exp(-thr)
            if L[i, j] < k * (1 - FURA):
                px = min(O[i, j], k)
                n = np.floor(PESO * capital / px)
                if n < 1:
                    continue
                x, c_ = n * (F[i, j] - px), n * px * G.B3_EMOL * custo_mult
                pnl[i, j] += x
                cus[i, j] += c_
                pos[j] = {"n": n, "px": px, "ref": F[i, j], "dia": i, "justo": Jv[s, j], "acc": x - c_}
        btc_expo[i] = sum(p["n"] * F[i, j] for j, p in pos.items() if ETFS[tk[j]] == "BTC" and F[i, j] > 0)
    f = lambda a: pd.DataFrame(a, index=G.DIAS, columns=tk)
    hedge_pnl = pd.Series(0.0, index=G.DIAS)
    if hedge == "bit":
        r, nivel = bit_continuo(d["bit"])
        mult = pd.Series([BIT_MULT(t) for t in G.DIAS], index=G.DIAS)
        noc1 = nivel * mult
        n = -(pd.Series(btc_expo, index=G.DIAS) / noc1).round().fillna(0)      # decidido no fechamento de i (posição já conhecida)
        n = n.shift(lag).fillna(0)
        hedge_pnl = ((n.shift(1).fillna(0) * noc1.shift(1) * r).fillna(0)
                     - (n.diff().abs().fillna(0) * noc1 * BIT_CUSTO * custo_mult).fillna(0))
    return f(pnl), f(cus), f(car), hedge_pnl, pd.DataFrame(neg)


def _hedge_bit(d, btc_expo, lag, custo_mult):
    r, nivel = bit_continuo(d["bit"])
    mult = pd.Series([BIT_MULT(t) for t in G.DIAS], index=G.DIAS)
    noc1 = nivel * mult
    n = -(pd.Series(btc_expo, index=G.DIAS) / noc1).round().fillna(0)          # decidido no fechamento de i (posição já conhecida)
    n = n.shift(lag).fillna(0)
    return ((n.shift(1).fillna(0) * noc1.shift(1) * r).fillna(0) - (n.diff().abs().fillna(0) * noc1 * BIT_CUSTO * custo_mult).fillna(0))


def _simula_fech(d, thr, max_dias, hedge, capital, custo_mult=1, lag=0, base=1):
    """CORREÇÃO (auditoria final). A versão original deixava a ordem em K = justo de ONTEM x (1 - thr): a 'compra com desconto' só
    acontecia quando o próprio bitcoin caía 2,5% no dia (todo desconto de entrada saía exatamente -2,47%) — era comprar a queda do
    cripto, não o desconto do ETF. Aqui o desconto é medido SIMULTANEAMENTE: no fechamento do dia i, oferta de venda do ETF contra o
    justo do MESMO instante (BTC/ETH-BRL do candle de 1h que fecha no fechamento da B3 x razão mediana até a véspera). Ordem de
    compra limitada atrelada ao justo ao vivo (atualizada antes do call de fechamento): compra na OFERTA DE VENDA do fechamento
    (não no último preço) se ela <= justo x e^-thr; com lag k compra no fechamento de i+k pela oferta de venda desse dia. Saída: vende
    na OFERTA DE COMPRA do fechamento quando ela >= justo do mesmo instante (desconto fechou) ou depois de `max_dias` pregões.
    Marca a mercado no fechamento; dinheiro no ETF não rende CDI.
    EXECUÇÃO t+1 (regra do dono): o sinal do fechamento de i é executado no fechamento de i+1+lag (base=1). base=0 = ordem atrelada ao
    justo ao vivo executada no MESMO call (sensibilidade; o desconto só existe aí — ver caderno correcoes_finais.md)."""
    V, U, J, HS, ref = _painel(d)
    tk = list(ETFS)
    F = V["fech"][tk].values
    hs = HS[tk].values
    AS = np.where(V["oferta_venda"][tk].values > 0, V["oferta_venda"][tk].values, F * (1 + hs))
    BI = np.where(V["oferta_compra"][tk].values > 0, V["oferta_compra"][tk].values, F * (1 - hs))
    Jv = J[tk].values
    ok = (V["negocios"][tk].fillna(0).values > 0) & (F > 0) & (Jv > 0)
    sinal = ok & (AS <= Jv * np.exp(-thr))
    fechou = ok & (BI >= Jv)
    T, N = F.shape
    pnl, cus, car = np.zeros((T, N)), np.zeros((T, N)), np.zeros((T, N))
    cdi = G.CDI.reindex(G.DIAS).fillna(0).values
    neg, btc_expo = [], np.zeros(T)
    ini = G.DIAS.searchsorted(pd.Timestamp(INICIO))
    for j in range(N):
        i = ini
        while i < T:
            if not sinal[i, j]:
                i += 1
                continue
            ie = i + base + lag
            if ie >= T or not (F[ie, j] > 0) or not (AS[ie, j] > 0):
                i += 1
                continue
            px = AS[ie, j]
            n = np.floor(PESO * capital / px)
            if n < 1:
                i += 1
                continue
            c0 = n * px * G.B3_EMOL * custo_mult
            pnl[ie, j] += n * (F[ie, j] - px)
            cus[ie, j] += c0
            acc, ref_p, ix, mot = n * (F[ie, j] - px) - c0, F[ie, j], None, ""
            k = ie + 1
            while k < T:
                car[k, j] -= n * ref_p * cdi[k]
                acc -= n * ref_p * cdi[k]
                if F[k, j] > 0:
                    pnl[k, j] += n * (F[k, j] - ref_p)
                    acc += n * (F[k, j] - ref_p)
                    ref_p = F[k, j]
                dec = k - base - lag                                      # decisão de saída em dec, execução em k
                if dec >= ie and (fechou[dec, j] or dec - ie >= max_dias) and F[k, j] > 0 and BI[k, j] > 0:
                    sai = BI[k, j]
                    pnl[k, j] += n * (sai - ref_p)
                    c1 = n * sai * G.B3_EMOL * custo_mult
                    cus[k, j] += c1
                    acc += n * (sai - ref_p) - c1
                    ix, mot = k, ("desconto fechou" if fechou[dec, j] else "prazo")
                    break
                k += 1
            for kk in range(ie, (ix if ix is not None else T)):
                if ETFS[tk[j]] == "BTC":
                    btc_expo[kk] += n * F[kk, j] if F[kk, j] > 0 else 0
            neg.append({"ativo": tk[j], "lado": 1, "entrada": G.DIAS[ie], "saida": G.DIAS[ix] if ix is not None else G.DIAS[-1],
                        "dias": (ix if ix is not None else T - 1) - ie, "retorno_%": ((BI[ix, j] if ix is not None else ref_p) / px - 1) * 100,
                        "desconto_entrada_%": (AS[i, j] / Jv[i, j] - 1) * 100, "contrib_pp": acc / capital * 100,
                        "saida_motivo": mot or "aberta"})
            if ix is None:
                break
            i = ix + 1
    f = lambda a: pd.DataFrame(a, index=G.DIAS, columns=tk)
    h = _hedge_bit(d, btc_expo, lag, custo_mult) if hedge == "bit" else pd.Series(0.0, index=G.DIAS)
    return f(pnl), f(cus), f(car), h, pd.DataFrame(neg)


def excesso(d, capital=20000, custo_mult=1, lag=0, regime=REGIME, alavancagem=1, **params):
    p = {**PARAMS, **params}
    pnl, cus, car, h, _ = _simula(d, p["thr"], p["max_dias"], p["hedge"], capital, custo_mult, lag)
    return G.C.aplica_regime(((pnl - cus + car).sum(axis=1) + h) / capital, regime, CUSTO_TROCA * custo_mult)


def classes_ir(d, capital=20000, **params):
    p = {**PARAMS, **params}
    pnl, cus, car, h, _ = _simula(d, p["thr"], p["max_dias"], p["hedge"], capital)
    return {"etf_b3": (pnl - cus).sum(axis=1), "futuros_b3": h}


def posicoes(d, capital=20000, **params):
    p = {**PARAMS, **params}
    pnl, cus, car, h, ng = _simula(d, p["thr"], p["max_dias"], p["hedge"], capital)
    W = pd.DataFrame(0.0, index=G.DIAS, columns=pnl.columns)
    for a, b_, t in zip(ng.get("entrada", []), ng.get("saida", []), ng.get("ativo", [])):
        W.loc[(W.index >= a) & (W.index < b_), t] = PESO
    V = _painel(d)[0]
    R = V["fech"][list(ETFS)].ffill(limit=5).pct_change(fill_method=None).fillna(0).sub(G.CDI.fillna(0), axis=0)
    return W.shift(-1).fillna(0), R


def negocios(d, capital=20000, **params):
    p = {**PARAMS, **params}
    ng = _simula(d, p["thr"], p["max_dias"], p["hedge"], capital)[4]
    cols = ["ativo", "lado", "entrada", "saida", "dias", "retorno_%", "contrib_pp", "desconto_entrada_%"]
    return ng[cols] if len(ng) else pd.DataFrame(columns=cols)


def kimchi(d=None):
    """Prêmio do BTC em reais (Mercado Bitcoin e Binance) sobre BTCUSDT x dólar, no fechamento da B3 — estatísticas por ano."""
    c = G.ler("cripto_br.parquet")
    dol = G.ler("dolar.csv")
    fx = dol["dol_b3"].reindex(G.DIAS).fillna(dol["brlx"].reindex(G.DIAS))
    bu = G.cripto_no_fech_b3(c, "BN", "BTCUSDT")
    out = pd.DataFrame({"MB": np.log(G.cripto_no_fech_b3(c, "MB", "BTC-BRL") / (bu * fx)),
                        "Binance BR": np.log(G.cripto_no_fech_b3(c, "BN", "BTCBRL") / (bu * fx)),
                        "USDT/BRL vs dólar": np.log(G.cripto_no_fech_b3(c, "BN", "USDTBRL") / fx)}) * 100
    return out
