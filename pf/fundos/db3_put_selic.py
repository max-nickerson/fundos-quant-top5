"""
Venda de put coberta por Tesouro Selic (cash-secured put) em PETR4, VALE3, ITUB4 e BOVA11 — pessoa física, lotes de 100.

Tese de mesa: o varejo e os gestores de ações compram proteção (put) de 1 mês na B3 e pagam por isso um prêmio de volatilidade
(IV ATM − vol realizada mediana de +1 a +2 pontos em 2014–2026, quant/fundos/pesquisa/arbitragem.md A4). Quem vende a put com o
strike inteiro guardado em Tesouro Selic (garantia que rende CDI) recebe o prêmio + CDI. O risco é ser "comprador de ação no
fundo do poço": por isso só vendo (i) quando a IV paga acima da vol que o papel está realizando (o prêmio existe naquele mês) e
(ii) com o papel acima da média de 100 dias (não vendo seguro de incêndio com a casa já pegando fogo: put vendida em tendência de
queda é onde estão os piores meses — PETR fev/2021, Covid mar/2020).

Edge de capital pequeno: 1 lote (100 ações) por papel é o tamanho do varejo; o livro de cada strike de put 3–6% OTM negocia R$ 10–50 mi
de nocional por dia — sem impacto. Com R$ 20 mil não cabe 1 lote de BOVA11 (R$ 12–20 mil de strike) junto com os outros: a alocação
é gulosa por lote inteiro, do papel com maior prêmio (IV − RV) para o menor, até o nocional dos strikes = capital x alavancagem.

Implementação:
  - ciclos mensais: sinal no 1º pregão após o vencimento mensal (ds), execução no pregão seguinte (d0 = t+1+lag) vendendo no BID a
    put do próximo vencimento mensal com strike mais perto de S x (1 − otm), segura até o vencimento (marcação no meio, nunca abaixo do
    intrínseco; no vencimento vale o intrínseco e paga o custo do exercício: comprar a ação ao strike e vender no dia seguinte);
  - garantia: strike x 100 x lotes em Tesouro Selic (rende CDI = benchmark; excesso = P&L das opções / capital);
  - B3 exige margem bem menor que o strike (~15–30%); usar 100% do strike é a versão "coberta" — alavancagem > 1 usa a folga de margem.
IR: tudo em "opcoes_b3" (15%, compensação de prejuízo dentro do ano/classe; o exercício gera ação que é vendida no dia seguinte —
tratado como parte do resultado da opção, simplificação).
"""
import numpy as np
import pandas as pd

import db3_base as B

NOME = "Put coberta por Tesouro Selic (PETR4/VALE3/ITUB4/BOVA11)"
TESE = "Vendo put de 1 mês 3–6% OTM com o strike inteiro em Tesouro Selic, só quando IV > vol realizada e o papel está acima da média de 100d"
BENCHMARK = "CDI"
INICIO, CORTE = "2014-03-01", "2021-01-01"
REGIME, CUSTO_TROCA = "nenhum", 0.0
ATIVOS = ["PETR", "VALE", "ITUB", "BOVA"]
PARAMS = {"otm": .03, "filtro": "iv_rv", "tendencia": False, "max_ativo": .5}   # maior IR no IS (2014–2020) da GRADE
GRADE = {"otm": [.03, .06], "filtro": ["sempre", "iv_rv"], "tendencia": [False, True]}
VIZINHANCA = {"otm": (.02, .08), "max_ativo": (.35, .7)}
CLASSE_IR = "opcoes_b3"
INSTRUMENTOS = [
    {"onde": "B3 (Clear/Rico/XP/BTG)", "ticker": "PETR*X / VALE*X / ITUB*X / BOVA*X (puts mensais)", "lote": 100,
     "custo": "bid/ask do fechamento + ~0,10% do prêmio; exercício ~0,14% do nocional"},
    {"onde": "Tesouro Direto / B3", "ticker": "Tesouro Selic (LFT) como garantia", "lote": "R$ ~170", "custo": "custódia B3 (igual ao benchmark)"},
]
APLICAVEL = True
MOTIVO = ("Cabe: 1 lote de PETR4/ITUB4 = R$ 3–4 mil de strike, VALE3 R$ 5–7 mil, BOVA11 R$ 10–20 mil; com R$ 20 mil a alocação gulosa "
          "fica com 2–4 lotes por mês. Corretoras de varejo permitem venda de put coberta com Tesouro Selic como garantia.")
ALAVANCAGENS = [1, 1.5, 2]
MOTIVO_ALAV = ("1x = strike 100% coberto (perda máxima = ação a zero). 1,5–2x usa a folga de margem da B3 (margem de put OTM ~15–30% do strike): "
               "num crash de 30% a perda chega a 40–60% do capital. 5x não é viável (chamada de margem antes do vencimento).")


def carrega():
    a = B.acoes()
    S, R = B.painel_acoes(a)
    return {"opc": B.opcoes(ATIVOS), "S": S, "R": R}


def _livro(d, capital, otm, filtro, tendencia, lag, custo_mult, alavancagem, max_ativo=.5):
    """Executa os ciclos. Devolve P&L por ativo (R$/dia) e lista de negócios."""
    cand = []
    for raiz in ATIVOS:
        c = B.sinais_ciclos(d, raiz)
        if c is None or c.empty:
            continue
        for _, z in c.iterrows():
            ok = True
            if filtro == "iv_rv":
                ok = z.iv_rv > 0
            if tendencia:
                ok = ok and z.tend > 0
            if ok and z.iv == z.iv:
                cand.append(z)
    pnl = {a: pd.Series(0.0, index=B.DIAS) for a in ATIVOS}
    neg = []
    if not cand:
        return pnl, neg
    cand = pd.DataFrame(cand)
    cand["mes"] = cand.v.dt.to_period("M")
    teto = capital * alavancagem
    for mes, g in cand.sort_values("iv_rv", ascending=False).groupby("mes", sort=False):
        pernas = {}
        for _, z in g.iterrows():
            dd = B.DIAS[B.DIAS > z.ds]
            if len(dd) <= lag or dd[lag] >= z.v:
                continue
            d0 = dd[lag]
            p = B.perna(d, z.raiz, z.v, d0, d["S"][z.raiz].get(d0, np.nan) * (1 - otm), "P", -1, custo_mult)
            if p is not None and p["preco"] > 0:
                pernas[z.raiz] = (p, z)
        # alocação gulosa por lote inteiro: maior prêmio primeiro, rodadas até não caber mais nenhum lote
        lotes, usado = {k: 0 for k in pernas}, 0.0              # teto por papel: max_ativo do capital (diversifica o risco de evento)
        ordem = list(pernas)
        mudou = True
        while mudou:
            mudou = False
            for k in ordem:
                nk = pernas[k][0]["K"] * 100
                if usado + nk <= teto and ((lotes[k] + 1) * nk <= max_ativo * teto or lotes[k] == 0):
                    lotes[k] += 1
                    usado += nk
                    mudou = True
        for k, n in lotes.items():
            if n == 0:
                continue
            p, z = pernas[k]
            x = B.pnl_pernas([p], n, [-1], custo_mult)
            pnl[k] = pnl[k].add(x, fill_value=0)
            neg.append(dict(ativo=k, lado=-1, entrada=x.index[0], saida=x.index[-1], lotes=n, serie=p["serie"], strike=p["K"],
                            premio=p["preco"], iv=z.iv, rv=z.rv, pnl_rs=float(x.sum()),
                            **{"retorno_%": float(x.sum() / (n * 100 * p["K"]) * 100)}))
    return pnl, neg


def excesso(d, capital=20000, custo_mult=1, lag=0, regime=REGIME, alavancagem=1, **params):
    p = {**PARAMS, **params}
    pnl, _ = _livro(d, capital, p["otm"], p["filtro"], p["tendencia"], lag, custo_mult, alavancagem, p["max_ativo"])
    e = sum(pnl.values()) / capital
    return B.fecha(e, regime, CUSTO_TROCA, custo_mult)


def classes_ir(d, capital=20000, **params):
    p = {**PARAMS, **params}
    pnl, _ = _livro(d, capital, p["otm"], p["filtro"], p["tendencia"], 0, 1, 1, p["max_ativo"])
    return {CLASSE_IR: sum(pnl.values())}


def posicoes(d, capital=20000, **params):
    p = {**PARAMS, **params}
    pnl, _ = _livro(d, capital, p["otm"], p["filtro"], p["tendencia"], 0, 0, 1, p["max_ativo"])
    return B.wr_de_pnl(pnl, capital)


def negocios(d, capital=20000, **params):
    p = {**PARAMS, **params}
    _, neg = _livro(d, capital, p["otm"], p["filtro"], p["tendencia"], 0, 1, 1, p["max_ativo"])
    return B.negocios_df(neg, capital)
