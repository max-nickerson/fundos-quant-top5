"""
Opções de dólar da B3 (sobre o dólar comercial, liquidação pela PTAX): trava vendida de call (vende o skew do dólar), de put ou condor,
mensal, risco definido, garantia em Tesouro Selic.

Tese de mesa: o importador e a tesouraria com dívida em dólar compram call de dólar (proteção contra o "Brasil quebrou"); o
exportador vende. O resultado é um sorriso inclinado para as calls (risk reversal positivo) e IV acima da vol realizada da PTAX na
maioria dos meses. Vender a trava de call OTM captura esse prêmio com perda máxima conhecida.
Dados (o grande limite): o histórico gratuito é o BVBG.086 da B3 (PriceReport, pf/dados/pf2_opcoes/pr_opcoes.parquet, baixado só
nos 2º–4º pregões de cada mês, 2018+, script baixa_pr.py). As opções de DOL (US$ 50 mil) têm só NEGÓCIOS (10–30 séries/dia, quase
sempre em blocos de 100+ contratos entre institucionais) e quase nunca oferta no fechamento; as de WDO (US$ 10 mil, as que cabem
na PF) têm ~2 negócios por dia. Então: IV de cada negócio de DOL do vencimento seguinte (Black-76 sobre o futuro DOL do mesmo mês),
sorriso linear em log(K/F), preço das pernas pelo sorriso ± meio spread de varejo (max(1,5 ponto; 5% do prêmio)) — e tamanho de
WDO (R$ 10 por ponto). Marcação diária = Black-76 com a IV da entrada e o futuro do dia (modelo); no vencimento (1º pregão do mês)
vale o intrínseco contra a PTAX do pregão anterior x 1000. Entrada no 2º pregão do mês (t+1 do vencimento), segura até o vencimento.
Filtro: IV ATM > vol realizada de 21 dias da PTAX. IR: futuros_b3 (15% mensal, sem isenção).
"""
import numpy as np
import pandas as pd
from scipy.optimize import brentq
from scipy.stats import norm

import op_base as O

C, P = O.C, O.P

NOME = "Opções de dólar B3: trava vendida de call/put ou condor (IV dos negócios de DOL, tamanho WDO)"
TESE = "Vendo a trava de call de dólar OTM (o skew que o importador paga) com risco definido e garantia em Tesouro Selic, só com IV > RV"
BENCHMARK = "CDI"
INICIO, CORTE = "2018-01-01", "2023-01-01"
REGIME, CUSTO_TROCA = "nenhum", 0.0
CLASSE_IR = "futuros_b3"
PARAMS = {"estrutura": "put_spread", "otm": .03, "largura": .03, "risco": .10, "filtro": "sempre"}   # maior IR no IS (0,28)
GRADE = {"estrutura": ["call_spread", "put_spread", "condor"], "otm": [.01, .03], "filtro": ["sempre", "iv_rv"]}
VIZINHANCA = {"otm": (.005, .04), "largura": (.02, .05), "risco": (.06, .15)}
MULT = 10.0                     # WDO: US$ 10 mil -> R$ 10 por ponto (ponto = R$ por US$ 1.000)
TARIFA = .30                    # R$ por contrato de opção por lado (emolumentos/registro de opção sobre disponível, PF)
INSTRUMENTOS = [{"onde": "B3", "ticker": "opções de WDO/DOL (dólar comercial, vencimento no 1º pregão do mês)", "lote": "1 contrato WDO = US$ 10 mil",
                 "custo": "meio spread ~max(1,5 pt; 5% do prêmio) + R$ 0,30 por contrato"},
                {"onde": "Tesouro Direto / B3", "ticker": "Tesouro Selic (garantia)", "lote": "-", "custo": "igual ao benchmark"}]
APLICAVEL = "parcial: as opções de WDO quase não negociam (2/dia, sem oferta no fechamento); o teste usa preços de DOL (institucional)"
MOTIVO = ("Cabe no capital: trava de 3% (≈160 pontos) em WDO perde no máximo ~R$ 1,2–1,4 mil; 10% de risco = 1 trava com 20k, 3 com 50k. "
          "Não cabe na LIQUIDEZ: a PF dependeria de achar contraparte em WDO (book vazio) — premissa otimista.")
ALAVANCAGENS = [1, 1.5, 2]
MOTIVO_ALAV = "Alavancagem = múltiplo do risco mensal (10% -> 15–20%)."
LETRA = "FGHJKMNQUVXZ"


def carrega():
    pr = pd.read_parquet(O.DADOS / "pr_opcoes.parquet")
    pr = pr[pr.ticker.str.startswith("DOL") & (pr.ticker.str.len() == 13)].copy()
    pr["mes"] = pr.ticker.str[3:6]
    pr["tipo"] = pr.ticker.str[6]
    pr["strike"] = pr.ticker.str[7:].astype(float)
    pr["preco"] = pr.TradAvrgPric.where(pr.RglrTraddCtrcts.fillna(0) > 0)
    pr = pr[pr.preco.notna()][["data", "mes", "tipo", "strike", "preco", "RglrTraddCtrcts"]].reset_index(drop=True)
    f = O.B.futuros(["DOL"])
    f = f[f.ticker.str.len() == 6].assign(mes=lambda x: x.ticker.str[3:6])[["data", "mes", "ajuste"]]
    ptax = P.PTAX.rename("ptax").to_frame()
    return {"pr": pr, "fut": f.reset_index(drop=True), "ptax": ptax[ptax.index >= "2017-06-01"]}


def b76(F, K, T, r, s, tipo):
    s, T = max(s, 1e-4), max(T, 1 / 252)
    d1 = (np.log(F / K) + s * s * T / 2) / (s * np.sqrt(T))
    d2 = d1 - s * np.sqrt(T)
    c = np.exp(-r * T) * (F * norm.cdf(d1) - K * norm.cdf(d2))
    return c if tipo == "C" else c - np.exp(-r * T) * (F - K)


def iv76(p, F, K, T, r, tipo):
    intr = max(F - K, 0) if tipo == "C" else max(K - F, 0)
    if not p > intr * np.exp(-r * T) + 1e-6:
        return np.nan
    try:
        return brentq(lambda s: b76(F, K, T, r, s, tipo) - p, 1e-3, 3.0, xtol=1e-6)
    except ValueError:
        return np.nan


def _venc(mes):
    a, m = 2000 + int(mes[1:]), LETRA.index(mes[0]) + 1
    dd = O.DIAS[O.DIAS >= pd.Timestamp(a, m, 1)]
    return dd[0] if len(dd) else pd.Timestamp(a, m, 1)


def _mes(ts):
    return f"{LETRA[ts.month - 1]}{ts.year % 100:02d}"


def _sorriso(pr, dia, mes, F, T, r):
    x = pr[(pr.data == dia) & (pr.mes == mes)]
    pts = []
    for _, z in x.iterrows():
        if abs(z.strike / F - 1) > .06:
            continue
        s = iv76(z.preco, F, z.strike, T, r, z.tipo)
        if s == s and .03 < s < .6:
            pts.append((np.log(z.strike / F), s, z.RglrTraddCtrcts))
    if not pts:
        return None
    a = np.array(pts)
    perto = a[np.abs(a[:, 0]) < .02]
    if len(np.unique(np.round(a[:, 0], 4))) >= 2 and np.ptp(a[:, 0]) > .01:
        b, c = np.polyfit(a[:, 0], a[:, 1], 1, w=np.sqrt(a[:, 2]))
        return lambda m, b=b, c=c: float(np.clip(c + b * m, .03, .6))
    if len(perto):
        v = float(np.average(perto[:, 1], weights=perto[:, 2]))
        return lambda m, v=v: v
    return None


def _livro(d, capital, p, lag, custo_mult, alavancagem):
    pr, fut, ptax = d["pr"], d["fut"], d["ptax"]["ptax"].reindex(O.DIAS)
    F = fut.pivot_table(index="data", columns="mes", values="ajuste").reindex(O.DIAS)
    dias_pr = sorted(pr.data.unique())
    rv = np.log(ptax).diff().rolling(21, min_periods=15).std() * np.sqrt(252)
    pnl = pd.Series(0.0, index=O.DIAS)
    neg = []
    ini = pd.Timestamp(INICIO)
    meses = pd.period_range(ini, O.DIAS[-1], freq="M")
    for per in meses:
        dd = O.DIAS[(O.DIAS >= per.start_time) & (O.DIAS <= per.end_time)]
        if len(dd) < 3 + lag:
            continue
        sinal, d0 = dd[0 + lag], dd[1 + lag]                         # vencimento (1º pregão) = sinal; executa t+1
        prox = (per + 1).start_time
        mes = _mes(prox)
        v = _venc(mes)
        if mes not in F.columns or not np.isfinite(F.at[d0, mes]):
            continue
        F0 = F.at[d0, mes]
        T, r = max(O.du(d0, v), 1) / 252, np.log1p(O.CDI_AA.get(d0, .1))
        base = [x for x in dias_pr if x <= d0 and x >= dd[1]]
        if not base:
            continue
        sm = _sorriso(pr, base[-1], mes, F0, T, r)
        if sm is None:
            continue
        iv0 = sm(0.0)
        if p["filtro"] == "iv_rv" and not iv0 > rv.get(sinal, np.nan):
            continue
        o, lg = p["otm"], p["largura"]
        spec = {"call_spread": [("C", 1 + o, -1), ("C", 1 + o + lg, 1)],
                "put_spread": [("P", 1 - o, -1), ("P", 1 - o - lg, 1)],
                "condor": [("C", 1 + o, -1), ("C", 1 + o + lg, 1), ("P", 1 - o, -1), ("P", 1 - o - lg, 1)]}[p["estrutura"]]
        pernas = []
        for tp, k, sg in spec:
            K = round(F0 * k / 25) * 25                                   # strikes de 25 em 25 pontos
            s = sm(np.log(K / F0))
            teor = b76(F0, K, T, r, s, tp)
            meia = max(1.5, .05 * teor) * custo_mult
            pernas.append(dict(tipo=tp, K=K, s=s, preco=teor + sg * meia, lado=sg))   # vendida recebe teor − meia; comprada paga + meia
        cred = sum(-q["lado"] * q["preco"] for q in pernas)
        larg = max(abs(a["K"] - b["K"]) for a in pernas for b in pernas if a["tipo"] == b["tipo"] and a["lado"] != b["lado"])
        pm = (larg - cred) * MULT
        if not (cred > 0 and pm > 0):
            continue
        n = int(np.floor(capital * alavancagem * p["risco"] / pm))
        if n < 1:
            continue
        dias = O.DIAS[(O.DIAS >= d0) & (O.DIAS <= v)]
        Ft = F[mes].reindex(dias).ffill()
        liq = ptax.shift(1).get(v, np.nan) * 1000 if v <= O.DIAS[-1] else np.nan
        x = pd.Series(0.0, index=dias)
        for q in pernas:
            mk = pd.Series([b76(f, q["K"], max(O.du(t, v), 1) / 252, r, q["s"], q["tipo"]) for t, f in zip(dias, Ft)], index=dias)
            mk.iloc[0] = q["preco"]
            if dias[-1] == v and np.isfinite(liq):
                mk.iloc[-1] = max(liq - q["K"], 0) if q["tipo"] == "C" else max(q["K"] - liq, 0)
            x = x + q["lado"] * n * MULT * mk.diff().fillna(0)
            x.iloc[0] -= n * TARIFA * custo_mult
        pnl = pnl.add(x, fill_value=0)
        neg.append(dict(ativo="WDO_" + p["estrutura"], lado=-1, entrada=d0, saida=dias[-1], contratos=n, F0=F0, iv=iv0, rv=rv.get(sinal, np.nan),
                        strikes="/".join(f"{q['K']:.0f}" for q in pernas), credito_pts=cred, liquidacao=liq, pnl_rs=float(x.sum()),
                        **{"retorno_%": float(x.sum() / (n * pm) * 100)}))
    return pnl, neg


def _p(params):
    return {**PARAMS, **params}


def excesso(d, capital=20000, custo_mult=1, lag=0, regime=REGIME, alavancagem=1, **params):
    pnl, _ = _livro(d, capital, _p(params), lag, custo_mult, alavancagem)
    return O.fecha(pnl / capital, regime, CUSTO_TROCA, custo_mult)


def classes_ir(d, capital=20000, **params):
    pnl, _ = _livro(d, capital, _p(params), 0, 1, 1)
    return {CLASSE_IR: pnl}


def posicoes(d, capital=20000, **params):
    pnl, _ = _livro(d, capital, _p(params), 0, 0, 1)
    return O.wr_de_pnl({"WDO": pnl}, capital)


def negocios(d, capital=20000, **params):
    _, neg = _livro(d, capital, _p(params), 0, 1, 1)
    return O.negocios_df(neg, capital)
