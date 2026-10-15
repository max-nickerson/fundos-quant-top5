"""
Trava de alta com put (bull put spread) e iron condor em BOVA11 — risco limitado que cabe em R$ 20 mil.

Tese de mesa: quem compra proteção de índice no Brasil paga o skew (IV da put 90% − ATM ~4,5–7 pontos, arbitragem.md A4). A trava
vendida captura esse prêmio com a perda máxima CONHECIDA na entrada (largura − crédito), o que permite a uma pessoa física dimensionar
pelo pior caso em vez de pela margem. O iron condor adiciona a call vendida (a alta do índice é menos violenta que a de PETR/VALE,
onde vender call perdeu). Filtro: só monto quando IV ATM > vol realizada de 21d (o prêmio existe naquele mês) e — para a trava de
alta — com BOVA11 acima da média de 100 dias (não vendo put em tendência de queda).

Implementação: ciclo mensal como db3_put_selic (sinal no 1º pregão depois do vencimento, execução t+1, agride bid na perna vendida e ask
na comprada, segura até o vencimento, marca no meio limitado pelo intrínseco). Lotes de 100 e número de travas = piso(capital x
alavancagem x risco / perda máxima por trava). Garantia em Tesouro Selic (a B3 cobra a perda máxima da trava como margem).
Liquidez: as opções de BOVA11 só ficaram líquidas a partir de 2019 (antes, poucos strikes com spread ≤ 25%): ciclos sem pernas
negociáveis ficam em CDI. IR: "opcoes_b3".
"""
import numpy as np
import pandas as pd

import db3_base as B

NOME = "Trava de alta / iron condor em BOVA11"
TESE = "Vendo put spread (e call spread no condor) de 1 mês em BOVA11 com perda máxima conhecida = 'risco' x capital, só com IV > RV"
BENCHMARK = "CDI"
INICIO, CORTE = "2014-03-01", "2021-01-01"
REGIME, CUSTO_TROCA = "nenhum", 0.0
PARAMS = {"estrutura": "put_spread", "otm": .05, "largura": .05, "filtro": "iv_rv", "risco": .10}   # maior IR no IS
GRADE = {"estrutura": ["put_spread", "iron_condor"], "otm": [.02, .05], "filtro": ["sempre", "iv_rv"]}
VIZINHANCA = {"otm": (.02, .07), "largura": (.03, .08), "risco": (.06, .15)}
CLASSE_IR = "opcoes_b3"
INSTRUMENTOS = [{"onde": "B3", "ticker": "BOVA*X / BOVA*L (puts/calls mensais de BOVA11)", "lote": 100,
                 "custo": "bid/ask do fechamento por perna + ~0,10% do prêmio"},
                {"onde": "Tesouro Direto / B3", "ticker": "Tesouro Selic (garantia)", "lote": "R$ ~170", "custo": "igual ao benchmark"}]
APLICAVEL = True
MOTIVO = ("Cabe: perda máxima de 1 trava de 5% em BOVA11 (R$ 130–200) ≈ R$ 500–900; com 10% de risco (R$ 2 mil) são 2–4 travas. "
          "Limitação real: liquidez das opções de BOVA11 antes de 2019 (spread > 25% na maioria dos strikes).")
ALAVANCAGENS = [1, 1.5, 2]
MOTIVO_ALAV = "Alavancagem aqui = múltiplo do risco por ciclo (10% x 1,5 = 15% do capital em perda máxima mensal); 5x = 50% do capital num mês: inviável."


def carrega():
    S, R = B.painel_acoes(B.acoes(("BOVA11",)))
    return {"opc": B.opcoes(["BOVA"]), "S": S, "R": R}


def _livro(d, capital, estrutura, otm, largura, filtro, risco, lag, custo_mult, alavancagem):
    c = B.sinais_ciclos(d, "BOVA")
    pnl = pd.Series(0.0, index=B.DIAS)
    neg = []
    if c is None or c.empty:
        return {"BOVA": pnl}, neg
    for _, z in c.iterrows():
        if z.iv != z.iv:
            continue
        if filtro == "iv_rv" and not z.iv_rv > 0:
            continue
        if estrutura == "put_spread" and not z.tend > 0:
            continue
        dd = B.DIAS[B.DIAS > z.ds]
        if len(dd) <= lag or dd[lag] >= z.v:
            continue
        d0 = dd[lag]
        S0 = d["S"]["BOVA"].get(d0, np.nan)
        spec = [("P", 1 - otm, -1), ("P", 1 - otm - largura, 1)]
        if estrutura == "iron_condor":
            spec += [("C", 1 + otm, -1), ("C", 1 + otm + largura, 1)]
        pernas = [B.perna(d, "BOVA", z.v, d0, S0 * k, tp, sg, custo_mult) for tp, k, sg in spec]
        if any(p is None for p in pernas):
            continue
        Ks = [p["K"] for p in pernas]
        if Ks[1] >= Ks[0] or (estrutura == "iron_condor" and Ks[3] <= Ks[2]):
            continue
        credito = sum(-sg * p["preco"] for p, (_, _, sg) in zip(pernas, spec))
        larg = max(Ks[0] - Ks[1], Ks[3] - Ks[2] if estrutura == "iron_condor" else 0)
        perda_max = (larg - credito) * 100
        if credito <= 0 or perda_max <= 0:
            continue
        n = int(np.floor(capital * alavancagem * risco / perda_max))
        if n < 1:
            continue
        x = B.pnl_pernas(pernas, n, [sg for _, _, sg in spec], custo_mult)
        pnl = pnl.add(x, fill_value=0)
        neg.append(dict(ativo="BOVA", lado=-1, entrada=x.index[0], saida=x.index[-1], lotes=n, estrutura=estrutura,
                        strikes="/".join(f"{k:.1f}" for k in Ks), credito=credito, iv=z.iv, rv=z.rv, pnl_rs=float(x.sum()),
                        **{"retorno_%": float(x.sum() / (n * perda_max) * 100)}))
    return {"BOVA": pnl}, neg


def _p(params):
    p = {**PARAMS, **params}
    return p["estrutura"], p["otm"], p["largura"], p["filtro"], p["risco"]


def excesso(d, capital=20000, custo_mult=1, lag=0, regime=REGIME, alavancagem=1, **params):
    pnl, _ = _livro(d, capital, *_p(params), lag, custo_mult, alavancagem)
    return B.fecha(pnl["BOVA"] / capital, regime, CUSTO_TROCA, custo_mult)


def classes_ir(d, capital=20000, **params):
    pnl, _ = _livro(d, capital, *_p(params), 0, 1, 1)
    return {CLASSE_IR: pnl["BOVA"]}


def posicoes(d, capital=20000, **params):
    pnl, _ = _livro(d, capital, *_p(params), 0, 0, 1)
    return B.wr_de_pnl(pnl, capital)


def negocios(d, capital=20000, **params):
    _, neg = _livro(d, capital, *_p(params), 0, 1, 1)
    return B.negocios_df(neg, capital)
