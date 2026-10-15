"""AUDITORIA (pf/pesquisa/auditoria_pf.md): mesma estratégia de gl_bdr_limite.py com execução conservadora — a ordem limitada só conta
como executada se a mínima do dia passou `fura` (1%) abaixo do limite (fila + negócio isolado no COTAHIST), e opção entrada="fech" (compra no
fechamento do dia pagando meio spread, só se o fechamento ficou abaixo do limite).
"""
"""
BDR x ação nos EUA com ORDEM LIMITADA: em vez de pagar o spread no fechamento seguinte (que matou a versão t+1 da pesquisa anterior, A1),
deixo uma ordem de compra parada abaixo do valor justo e só compro quando alguém vende o BDR barato durante o pregão.

Tese de mesa: o BDR não patrocinado é cotado por um formador que acompanha a ação lá fora x dólar. Quando um varejista vende a mercado
num livro raso (abertura, notícia, dólar mexendo), o BDR "descola" para baixo por minutos. A ordem limitada pega esse descolamento — é o
papel do formador de mercado, possível porque o lote é pequeno (R$ 2 mil por ordem não mexe o livro). Saída: ordem limitada de venda no
valor justo do dia anterior (+ `saida`), ou no fechamento depois de `max_dias`.

Valor justo do BDR em t = preço EUA (fechamento não ajustado) x dólar (DOL 1º vencimento convertido para à vista; antes de 2019 BRL=X) x
razão, onde a razão é a mediana móvel de 60 pregões de log(BDR/EUA x dólar) até t-1 (quebras > 15% = desdobramento -> bloqueia 60 dias),
mais o fator comum do dia (mediana do desvio dos BDRs líquidos: corrige o horário diferente do câmbio e do fechamento).
Ordem para t+1: compra limitada em K = justo_t x exp(-thr). Executa se a mínima de t+1 < K x (1 - 0,25%), ao preço min(abertura, K) — sem look-ahead:
K é conhecido antes da abertura. Seleção adversa medida de verdade: a ordem executa justamente quando o mercado cai durante o dia.
Hedge (hedge="ivvb11", escolhido): IVVB11 vendido via aluguel na B3 no tamanho da exposição média do mês anterior (o risco que sobra é
sobretudo S&P x dólar; aluguel 1% a.a. + 0,5% por contrato aberto; o dinheiro da venda rende 95% do CDI). Hedge (hedge="ibkr"): vende a ação na IBKR no fechamento do dia da compra (ações INTEIRAS; sobra fica sem hedge), recompra no fechamento da
saída; conta na IBKR com 50% do vendido (Reg T) + folga, perdendo CDI e pagando remessa (pf.custo_conta_exterior); comissão US$ 0,35
mín.; aluguel 0,5% a.a. Sem hedge: o BDR fica exposto à ação e ao dólar por 1-5 dias.

Universo: BDRs com mapa validado e mediana de volume de 20 dias > R$ 1 mi (só passado). BDR só é acessível a PF desde 22/10/2020
(Resolução CVM 3/2020) -> INICIO 2020-11-01, CORTE 2023-01-01. Patrocinados (sufixo 31-33: INBR32, XPBR31, NUBR33, STOC31, JBSS32,
EVEB31, EXCO32) marcados. Custos B3: emolumentos 0,03% (ordem limitada não paga spread); saída forçada paga meio spread do fechamento.
Dividendos dos BDRs ignorados (posições de poucos dias). IR: BDR = 15% sem isenção (classe acoes); perna na IBKR = exterior.
"""
import numpy as np
import pandas as pd

import gl_comum as G
import pf as P

NOME = "BDR x EUA com ordem limitada — versão AUDITADA (execução conservadora)"
TESE = "Ordem de compra parada abaixo do valor justo do BDR (EUA x dólar); vende no justo no dia seguinte; hedge opcional na IBKR"
BENCHMARK = "CDI"
INICIO, CORTE = "2020-11-01", "2023-01-01"
REGIME = "nenhum"
CUSTO_TROCA = .001
PARAMS = {"thr": .015, "saida": 0.0, "max_dias": 5, "hedge": "ivvb11"}
AUD = {"fura": .01, "entrada": "limite", "saida_lim": True}   # AUDITORIA: execução conservadora (ver topo)   # maior IR dentro da amostra (todas negativas no IS)
GRADE = {"thr": [.015, .02, .03], "saida": [0.0, .005], "hedge": ["nenhum", "ivvb11", "ibkr"]}
VIZINHANCA = {"thr": (.01, .025), "saida": (-.003, .008)}
PESO, MAX_POS, ADV_MIN = .10, 8, 1e6
ALUGUEL_IVVB = .01               # taxa ao doador do IVVB11 a.a. (premissa; + 0,5% por contrato aberto, pf.ALUGUEL_PF_CORRETORA)
FURA = .0025                     # a mínima do dia tem de passar 0,25% abaixo da ordem para contar execução (fila/negócio isolado)
MAPA = {'INBR32': 'INTR', 'XPBR31': 'XP', 'TSLA34': 'TSLA', 'ROXO34': 'NU', 'MELI34': 'MELI', 'NUBR33': 'NU', 'NVDC34': 'NVDA',
        'M2ST34': 'MSTR', 'M1TA34': 'META', 'AMZO34': 'AMZN', 'MSFT34': 'MSFT', 'AAPL34': 'AAPL', 'GOGL34': 'GOOGL', 'GOGL35': 'GOOG',
        'STOC34': 'STNE', 'STOC31': 'STNE', 'BABA34': 'BABA', 'FBOK34': 'META', 'NFLX34': 'NFLX', 'BERK34': 'BRK-B', 'A1MD34': 'AMD',
        'C2OI34': 'COIN', 'TSMC34': 'TSM', 'JPMC34': 'JPM', 'IBIT39': 'IBIT', 'DISB34': 'DIS', 'COCA34': 'KO', 'M1RN34': 'MRNA',
        'VISA34': 'V', 'S2GM34': 'SGML', 'EXXO34': 'XOM', 'JNJB34': 'JNJ', 'ITLC34': 'INTC', 'NIKE34': 'NKE', 'AVGO34': 'AVGO',
        'BIVB39': 'IVV', 'SSFO34': 'CRM', 'PYPL34': 'PYPL', 'MSCD34': 'MA', 'UNHH34': 'UNH', 'MUTC34': 'MU', 'BOAC34': 'BAC',
        'BACW39': 'ACWI', 'CHVX34': 'CVX', 'PAGS34': 'PAGS', 'LILY34': 'LLY', 'U1BE34': 'UBER', 'RGTI34': 'RGTI', 'WALM34': 'WMT',
        'PFIZ34': 'PFE', 'BKNG34': 'BKNG', 'BIAU39': 'IAU', 'ASML34': 'ASML', 'MCDC34': 'MCD', 'COWC34': 'COST', 'ADBE34': 'ADBE',
        'BIEU39': 'IEUR', 'BSLV39': 'SLV', 'AIRB34': 'ABNB', 'S2EA34': 'SE', 'CMCS34': 'CMCSA', 'HOME34': 'HD', 'GDXB39': 'GDX',
        'P2LT34': 'PLTR', 'S1PO34': 'SPOT', 'MRCK34': 'MRK', 'TWTR34': 'TWTR', 'ORCL34': 'ORCL', 'PEPB34': 'PEP', 'WFCO34': 'WFC',
        'QCOM34': 'QCOM', 'FCXO34': 'FCX', 'GMCO34': 'GM', 'BTLT39': 'TLT', 'GSGI34': 'GS', 'BAAX39': 'AAXJ', 'N1VO34': 'NVO',
        'W1DC34': 'WDC', 'C2RW34': 'CRWD', 'TMOS34': 'TMO', 'G1WW34': 'GWW', 'ARGT39': 'ARGT', 'PGCO34': 'PG', 'TGTB34': 'TGT',
        'A1MT34': 'AMAT', 'TJXC34': 'TJX', 'CATP34': 'CAT', 'BEEM39': 'EEM', 'N1EM34': 'NEM', 'ATVI34': 'ATVI', 'CTGP34': 'C',
        'RIGG34': 'RIG', 'P1DD34': 'PDD', 'BIDU34': 'BIDU', 'VERZ34': 'VZ', 'BIVE39': 'IVE', 'A1PP34': 'APP', 'OXYP34': 'OXY',
        'QUBT34': 'QUBT', 'CHCM34': 'CHTR', 'V1RT34': 'VRT', 'EVEB31': 'EVEX', 'BIWM39': 'IWM', 'SBUB34': 'SBUX', 'AALL34': 'AAL',
        'JDCO34': 'JD', 'BLAK34': 'BLK', 'A1PO34': 'APO', 'HONB34': 'HON', 'B1NT34': 'BNTX', 'AXPB34': 'AXP', 'TEXA34': 'TXN',
        'JBSS32': 'JBS', 'BEGU39': 'EWG', 'EXCO32': 'EXCE'}
PATROCINADOS = [t for t in MAPA if t[-2:] in ("31", "32", "33")]
INSTRUMENTOS = {"BDRs": {"onde": "B3 (Clear/Rico/XP)", "ticker": "~115 BDRs líquidos", "lote": 1, "custo": "0,03% (limitada) / meio spread"},
                "hedge": {"onde": "IBKR", "ticker": "ação-objeto", "lote": "1 ação", "custo": "US$ 0,0035/ação, mín. 0,35; aluguel 0,5% a.a."}}
APLICAVEL = True
MOTIVO = "BDRs de R$ 20-200 em lote 1; ordem limitada é padrão em qualquer corretora. O hedge na IBKR é opcional (exige conta lá)."
ALAVANCAGENS = [1]
MOTIVO_ALAV = "Posições de 10% x até 8 BDRs já usam até 80% do PL; alavancar exigiria margem de ações (cara para PF)."


def carrega():
    b = G.ler("b3_etf_bdr.parquet")
    us = G.ler("us_fech_bruto.parquet")
    return {"b3": b[b.ticker.isin(list(MAPA) + ["IVVB11"])], "us": us[[u for u in set(MAPA.values()) if u in us.columns]], "dolar": G.ler("dolar.csv")}


def _painel(d):
    b = d["b3"]
    tk = [t for t in MAPA if MAPA[t] in d["us"].columns and t in set(b.ticker)]
    b = b[b.ticker.isin(tk)]
    V = {c: G.pivo(b, c, tk) for c in ("abertura", "max", "min", "fech", "oferta_compra", "oferta_venda", "volume", "negocios")}
    dol = d["dolar"]
    fx = dol["dol_b3"].reindex(G.DIAS).fillna(dol["brlx"].reindex(G.DIAS)).ffill(limit=3)
    usd = d["us"].copy()
    usd.index = pd.DatetimeIndex(usd.index).normalize()
    us_ok = usd.reindex(G.DIAS).notna()
    U = pd.DataFrame({t: usd[MAPA[t]].reindex(G.DIAS) for t in tk})
    U_ok = pd.DataFrame({t: us_ok[MAPA[t]] for t in tk})
    neg = V["negocios"].fillna(0) > 0
    q = (np.log(V["fech"]) - np.log(U.mul(fx, axis=0))).where(neg & U_ok)
    salto = q.ffill().diff().abs() > .15
    bloq = salto.rolling(60, min_periods=1).max().fillna(0).astype(bool)
    med = q.rolling(60, min_periods=20).median().shift(1)
    dev = (q - med).where(~bloq)
    adv = V["volume"].fillna(0).rolling(20, min_periods=5).median()
    liq = adv > ADV_MIN
    fator = dev.where(liq).median(axis=1).where(dev.where(liq).notna().sum(axis=1) >= 8, 0).fillna(0)
    justo = np.exp(med.add(fator, axis=0)) * U.mul(fx, axis=0)                 # preço justo do BDR no fechamento de t
    justo = justo.where(~bloq & U_ok & med.notna())
    hs = G.meio_spread(V["oferta_compra"], V["oferta_venda"], .01, .05)
    return dict(V=V, U=U, fx=fx, justo=justo, liq=liq, hs=hs, tk=tk, neg=neg)


def _simula(d, thr, saida, max_dias, hedge, capital, custo_mult=1, lag=0, fura=None, entrada="limite", saida_lim=True):
    FURA = AUD["fura"] if fura is None else fura
    X = _painel(d)
    V, tk = X["V"], X["tk"]
    O, H, L, F = (V[c][tk].values for c in ("abertura", "max", "min", "fech"))
    J = X["justo"][tk].values
    LQ = X["liq"][tk].values
    HS = X["hs"][tk].values
    Uv = X["U"][tk].ffill().values
    fx = X["fx"].ffill().values
    T, N = F.shape
    pnl = np.zeros((T, N))
    cus = np.zeros((T, N))
    car = np.zeros((T, N))
    cdi = G.CDI.reindex(G.DIAS).fillna(0).values
    pos = {}                       # j -> dict(n, px, dia, nus)
    neg = []
    noc_short = np.zeros(T)
    expo = np.zeros(T)
    ini = G.DIAS.searchsorted(pd.Timestamp(INICIO))
    for i in range(max(ini, 1 + lag), T):
        s = i - 1 - lag                                          # dia da informação (ordem montada no fechamento de s)
        # 1) marcação das posições abertas no fechamento de i-1 -> i (o dinheiro no BDR deixa de render CDI)
        for j, p in list(pos.items()):
            if p["dia"] < i:
                car[i, j] -= p["n"] * p["ref"] * cdi[i]
                p["acc"] -= p["n"] * p["ref"] * cdi[i]
            if p["dia"] < i and F[i, j] > 0:
                ru = Uv[i, j] * fx[i] / p["refu"] if p["refu"] > 0 and Uv[i, j] > 0 else 1.0
                if abs(np.log(F[i, j] / p["ref"] / ru)) > .25:              # desdobramento/grupamento do BDR: preserva o valor
                    x = p["n"] * p["ref"] * (ru - 1)
                    p["n"] *= p["ref"] * ru / F[i, j]
                    p["px"] *= F[i, j] / (p["ref"] * ru)
                else:
                    x = p["n"] * (F[i, j] - p["ref"])
                pnl[i, j] += x
                p["acc"] += x
                p["ref"], p["refu"] = F[i, j], Uv[i, j] * fx[i]
            if p["nus"] and p["dia"] < i and Uv[i, j] > 0:
                pnl[i, j] -= p["nus"] * (Uv[i, j] * fx[i] - p["ref_us"])
                p["acc"] -= p["nus"] * (Uv[i, j] * fx[i] - p["ref_us"])
                p["ref_us"] = Uv[i, j] * fx[i]
        # 2) saída: limitada no justo de s (+saida); senão no fechamento depois de max_dias
        for j, p in list(pos.items()):
            if p["dia"] >= i or not (F[i, j] > 0):
                continue
            k = J[s, j] * np.exp(saida) if J[s, j] > 0 else np.nan
            px = None
            if k == k and O[i, j] >= k:
                px = O[i, j]
            elif saida_lim and k == k and H[i, j] > k * (1 + .0025):        # saída: regra original (0,25%)
                px = k
            elif not saida_lim and k == k and F[i, j] >= k:
                px = F[i, j] * (1 - HS[i, j])
            elif i - p["dia"] >= max_dias:
                px = F[i, j] * (1 - HS[i, j])
            if px is None:
                continue
            x = p["n"] * (px - p["ref"]) - p["n"] * px * G.B3_EMOL * custo_mult   # ref = F[i] já marcado; desfaz até o preço da saída
            pnl[i, j] += p["n"] * (px - p["ref"])
            cus[i, j] += p["n"] * px * G.B3_EMOL * custo_mult           # saída forçada já paga o meio spread no preço
            p["acc"] += x
            if p["nus"]:
                c_us = P.custo_ordem_ibkr_usd(p["nus"] * Uv[i, j], Uv[i, j]) + p["nus"] * Uv[i, j] * .0003
                cus[i, j] += float(c_us) * fx[i] * custo_mult
                p["acc"] -= float(c_us) * fx[i] * custo_mult
            ret_bdr = px / p["px"] - 1
            neg.append({"ativo": tk[j], "lado": 1, "entrada": G.DIAS[p["dia"]], "saida": G.DIAS[i], "dias": i - p["dia"],
                        "retorno_%": ret_bdr * 100, "desconto_entrada_%": (p["px"] / p["justo"] - 1) * 100,
                        "contrib_pp": p["acc"] / capital * 100, "j": j})
            del pos[j]
        # 3) entradas: compra limitada em K = justo_s x exp(-thr) nos BDRs líquidos sem posição
        livres = MAX_POS - len(pos)
        if livres > 0 and s >= 0:
            cand = []
            for j in range(N):
                if j in pos or not LQ[s, j] or not (J[s, j] > 0) or not (L[i, j] > 0):
                    continue
                k = J[s, j] * np.exp(-thr)
                if not (.75 < O[i, j] / F[s, j] < 1.33) if F[s, j] > 0 else True:
                    continue                                            # salto na abertura = desdobramento/evento (aviso prévio da B3)
                if L[i, j] < k * (1 - FURA):                           # só conta execução se o preço passou da ordem (fila)
                    pxe = min(O[i, j], k) if entrada == "limite" else F[i, j] * (1 + HS[i, j])   # 'fech': compra no fechamento de i pagando meio spread
                    if entrada == "fech" and not pxe < k:
                        continue
                    cand.append((pxe / J[s, j], j, pxe))
            for _, j, px in sorted(cand)[:livres]:
                n = np.floor(PESO * capital / px)
                if n < 1:
                    continue
                pnl[i, j] += n * (F[i, j] - px)
                cus[i, j] += n * px * G.B3_EMOL * custo_mult
                nus, c_us = 0, 0.0
                if hedge == "ibkr" and Uv[i, j] > 0:
                    nus = np.floor(n * F[i, j] / (Uv[i, j] * fx[i]))          # ações inteiras lá fora
                    if nus >= 1:
                        c_us = P.custo_ordem_ibkr_usd(nus * Uv[i, j], Uv[i, j]) + nus * Uv[i, j] * .0003
                        cus[i, j] += float(c_us) * fx[i] * custo_mult
                acc = n * (F[i, j] - px) - n * px * G.B3_EMOL * custo_mult - (float(c_us) * fx[i] * custo_mult if nus >= 1 else 0)
                pos[j] = {"n": n, "px": px, "ref": F[i, j], "dia": i, "acc": acc, "justo": J[s, j], "nus": nus, "ref_us": Uv[i, j] * fx[i],
                          "refu": Uv[i, j] * fx[i]}
        expo[i] = sum(p["n"] * F[i, j] for j, p in pos.items() if F[i, j] > 0)
        if hedge == "ibkr":
            noc_short[i] = sum(p["nus"] * Uv[i, j] * fx[i] for j, p in pos.items())
    f = lambda a: pd.DataFrame(a, index=G.DIAS, columns=tk)
    pnl, cus, carrego = f(pnl), f(cus), f(car)
    val = pd.DataFrame(0.0, index=G.DIAS, columns=tk)
    ng = pd.DataFrame(neg)
    for r in neg:
        a, b_ = G.DIAS.get_loc(r["entrada"]), G.DIAS.get_loc(r["saida"])
        val.iloc[a:b_, r["j"]] = 1.0
    extra = pd.Series(0.0, index=G.DIAS)
    extra_b3 = pd.Series(0.0, index=G.DIAS)
    if hedge == "ibkr":
        req = pd.Series(noc_short * .5, index=G.DIAS)
        conta, _ = P.custo_conta_exterior(req)
        aluguel = pd.Series(noc_short, index=G.DIAS) * .005 / 252
        extra = -(conta.where(req.rolling(2).max() > 0, 0) + aluguel) * custo_mult
    elif hedge == "ivvb11":
        # IVVB11 vendido (aluguel na B3) no tamanho da exposição média em BDRs do mês anterior, refeito todo mês
        e = pd.Series(expo, index=G.DIAS)
        alvo = -e.rolling(21, min_periods=5).mean() / capital
        W = G.mensal(pd.DataFrame({"IVVB11": alvo.fillna(0)}))
        b = d["b3"]
        piv = G.pivo(b[b.ticker == "IVVB11"], "fech")
        hs = G.meio_spread(G.pivo(b[b.ticker == "IVVB11"], "oferta_compra"), G.pivo(b[b.ticker == "IVVB11"], "oferta_venda"), teto=.01)
        ex = G.executa(W, piv, capital, hs + G.B3_EMOL, lag=lag, custo_mult=custo_mult, aluguel_aa=ALUGUEL_IVVB)
        extra_b3 = (ex["pnl"] + ex["carrego"] - ex["custo"] - ex["aluguel"]).sum(axis=1)
        extra_b3.attrs["classe"] = G.pnl_classe(ex)              # sem o CDI do dinheiro da venda (vai para o caixa no IR)
    return pnl, cus, carrego, extra, ng, val, extra_b3


def excesso(d, capital=20000, custo_mult=1, lag=0, regime=REGIME, alavancagem=1, **params):
    p = {**PARAMS, **params}
    pnl, cus, car, extra, _, _, eb3 = _simula(d, p["thr"], p["saida"], p["max_dias"], p["hedge"], capital, custo_mult, lag, p.get("fura"), p.get("entrada", AUD["entrada"]), p.get("saida_lim", AUD["saida_lim"]))
    e = ((pnl - cus + car).sum(axis=1) + extra + eb3) / capital
    return G.C.aplica_regime(e, regime, CUSTO_TROCA * custo_mult)


def classes_ir(d, capital=20000, **params):
    p = {**PARAMS, **params}
    pnl, cus, car, extra, _, _, eb3 = _simula(d, p["thr"], p["saida"], p["max_dias"], p["hedge"], capital, 1, 0, p.get("fura"), p.get("entrada", AUD["entrada"]), p.get("saida_lim", AUD["saida_lim"]))
    return {"acoes": (pnl - cus).sum(axis=1), "exterior": extra, "etf_b3": eb3.attrs.get("classe", eb3 * 0)}


def posicoes(d, capital=20000, **params):
    p = {**PARAMS, **params}
    pnl, cus, car, extra, _, val, _ = _simula(d, p["thr"], p["saida"], p["max_dias"], p["hedge"], capital, 1, 0, p.get("fura"), p.get("entrada", AUD["entrada"]), p.get("saida_lim", AUD["saida_lim"]))
    X = _painel(d)
    R = X["V"]["fech"][val.columns].ffill(limit=5).pct_change(fill_method=None).fillna(0).clip(-.3, .3).sub(G.CDI, axis=0)
    return (val * PESO).shift(-1).fillna(0), R


def negocios(d, capital=20000, **params):
    p = {**PARAMS, **params}
    ng = _simula(d, p["thr"], p["saida"], p["max_dias"], p["hedge"], capital, 1, 0, p.get("fura"), p.get("entrada", AUD["entrada"]), p.get("saida_lim", AUD["saida_lim"]))[4]
    cols = ["ativo", "lado", "entrada", "saida", "dias", "retorno_%", "contrib_pp", "desconto_entrada_%"]
    return ng[cols] if len(ng) else pd.DataFrame(columns=cols)
