"""
Travas vendidas (alta/baixa), iron butterfly e iron condor em 24 ativos-objeto da B3, onde a IV paga mais que a vol realizada.

Tese de mesa: na B3 o vendedor natural de volatilidade é pequeno (poucos formadores, tesourarias), e o comprador é o varejo que compra
call de PETR/VALE/MGLU como bilhete de loteria e o gestor que compra put de proteção. Em cada vencimento mensal escolho os N papéis com
maior IV ATM / vol realizada de 21 dias (o prêmio está ONDE o comprador pagou caro naquele mês) e vendo uma estrutura com perda
máxima conhecida: (a) "direcional": trava de alta com put se o papel está acima da média de 100 dias, trava de baixa com call se
abaixo (vendo o lado que a tendência protege); (b) "borboleta": iron butterfly ATM (vende o straddle, compra as asas); (c) "condor".
Por que PF: lotes de 100 e travas de R$ 100–500 de perda máxima cabem em R$ 20 mil espalhados em 3–6 papéis; o institucional não
consegue colocar tamanho nessas séries (spread de 5–25% do meio), o PF consegue.
Regime (econômico): vender vol logo depois de um choque global é vender o seguro quando a casa já pegou fogo; a variante
"risco_global" só abre estruturas novas com o regime de risco global (VIX/tendência do S&P/crédito) ligado.

Implementação: sinal no 1º pregão depois do vencimento (ds), execução t+1(+lag) agredindo bid na perna vendida e ask na comprada,
segura até o vencimento, marca no meio (limitado ao intrínseco). Orçamento de risco por ciclo = risco x capital, dividido igualmente
entre os papéis; lotes = piso(orçamento / perda máxima por lote). Garantia = Tesouro Selic (a B3 aceita; perda máxima da trava é a
margem). VALE só desde 2018 (antes a raiz misturava VALE3/VALE5). IR: opcoes_b3 (15%, mensal, sem isenção).
"""
import numpy as np
import pandas as pd

import op_base as O

NOME = "Travas vendidas em 24 papéis B3 onde IV > RV (direcional / borboleta / condor)"
TESE = ("Todo vencimento vendo trava de risco definido nos N papéis com maior IV/RV (a call/put de varejo cara), no lado da tendência; "
        "perda máxima = orçamento de risco do mês")
BENCHMARK = "CDI"
INICIO, CORTE = "2014-03-01", "2021-01-01"
REGIME, CUSTO_TROCA = "nenhum", 0.0
CLASSE_IR = "opcoes_b3"
RAIZES = [r for r in O.TICKER]
PARAMS = {"estrutura": "condor", "n_ativos": 6, "filtro_regime": "risco_global", "otm": .03, "largura": .05, "risco": .10, "iv_rv_min": 1.0}   # maior IR no IS (−0,20: todas negativas)
GRADE = {"estrutura": ["direcional", "borboleta", "condor"], "n_ativos": [3, 6], "filtro_regime": ["nenhum", "risco_global"]}
VIZINHANCA = {"otm": (.01, .06), "largura": (.03, .08), "risco": (.06, .15), "iv_rv_min": (.9, 1.3)}
INSTRUMENTOS = [{"onde": "B3 (Clear/Rico/XP)", "ticker": "opções mensais de 24 ações/ETFs (PETR, VALE, BBAS, MGLU, ...)", "lote": 100,
                 "custo": "bid/ask do fechamento por perna + ~0,10% do prêmio; exercício 0,14%"},
                {"onde": "Tesouro Direto / B3", "ticker": "Tesouro Selic (garantia)", "lote": "R$ ~170", "custo": "igual ao benchmark"}]
APLICAVEL = True
MOTIVO = ("Cabe: trava de 5% em papel de R$ 10–60 perde no máximo R$ 30–250 por lote; com 10% de risco/mês (R$ 2 mil) são 1–10 lotes "
          "por papel. Limite real: liquidez das séries fora de PETR/VALE/BOVA (o filtro de spread <= 25% do meio descarta muitas).")
ALAVANCAGENS = [1, 1.5, 2]
MOTIVO_ALAV = "Alavancagem = múltiplo do orçamento de perda máxima mensal (10% -> 15%/20%); 5x = 50% do capital num mês: inviável."


def carrega():
    return O.carrega_b3(RAIZES)


def _todos_ciclos(d):
    def f():
        cs = [O.ciclos(d, r) for r in RAIZES]
        cs = [c for c in cs if len(c)]
        return pd.concat(cs, ignore_index=True) if cs else pd.DataFrame()
    return O.memo("travas_ciclos", d["opc"], f)


def _estrutura(est, tend, otm, larg):
    """Lista (tipo, k/S, lado) e se é a de alta."""
    if est == "direcional":
        if tend > 0:
            return [("P", 1 - otm, -1), ("P", 1 - otm - larg, 1)]
        return [("C", 1 + otm, -1), ("C", 1 + otm + larg, 1)]
    if est == "borboleta":
        return [("P", 1.0, -1), ("C", 1.0, -1), ("P", 1 - larg, 1), ("C", 1 + larg, 1)]
    return [("P", 1 - otm, -1), ("C", 1 + otm, -1), ("P", 1 - otm - larg, 1), ("C", 1 + otm + larg, 1)]


def _largura_ok(pernas, spec, S0, larg):
    """A asa comprada precisa ficar a pelo menos metade da largura-alvo da vendida (senão a 'trava' vira só custo)."""
    for tp in ("P", "C"):
        v = [p["K"] for p, (t, _, sg) in zip(pernas, spec) if t == tp and sg < 0]
        c = [p["K"] for p, (t, _, sg) in zip(pernas, spec) if t == tp and sg > 0]
        if v and c and abs(v[0] - c[0]) < .5 * larg * S0:
            return False
    return True


def _livro(d, capital, p, lag, custo_mult, alavancagem):
    c = _todos_ciclos(d)
    pnl = {r: pd.Series(0.0, index=O.DIAS) for r in RAIZES}
    neg = []
    if c.empty:
        return pnl, neg
    c = c[c.iv.notna() & c.rv.gt(0) & c.tend.notna() & (c.iv_rv >= p["iv_rv_min"])]
    for v, g in c.groupby("v"):
        ds = g.ds.min()
        if p["filtro_regime"] == "risco_global" and O.regime_global_em(ds) < .67:
            continue
        g = g.sort_values("iv_rv", ascending=False)
        orc = capital * alavancagem * p["risco"] / p["n_ativos"]
        feitos = 0
        for _, z in g.iterrows():
            if feitos >= p["n_ativos"]:
                break
            d0 = O.execucao(z.ds, lag, z.v)
            if d0 is None:
                continue
            S0 = d["S"][z.raiz].get(d0, np.nan)
            if not np.isfinite(S0):
                continue
            spec = _estrutura(p["estrutura"], z.tend, p["otm"], p["largura"])
            pernas = [O.perna(d, z.raiz, z.v, d0, S0 * k, tp, sg, custo_mult) for tp, k, sg in spec]
            if any(x is None for x in pernas):
                continue
            if not _largura_ok(pernas, spec, S0, p["largura"]):
                continue
            cred, pm = O.perda_maxima(pernas, [sg for _, _, sg in spec])
            if not (cred > 0 and pm > 0):
                continue
            n = int(np.floor(orc / pm))
            if n < 1:
                continue
            x = O.pnl_pernas(pernas, n, [sg for _, _, sg in spec], custo_mult)
            pnl[z.raiz] = pnl[z.raiz].add(x, fill_value=0)
            feitos += 1
            neg.append(dict(ativo=z.raiz, lado=-1, entrada=x.index[0], saida=x.index[-1], lotes=n, estrutura=p["estrutura"],
                            strikes="/".join(f"{q['K']:.2f}" for q in pernas), credito=cred, iv=z.iv, rv=z.rv, pnl_rs=float(x.sum()),
                            **{"retorno_%": float(x.sum() / (n * pm) * 100)}))
    return pnl, neg


def _p(params):
    return {**PARAMS, **params}


def excesso(d, capital=20000, custo_mult=1, lag=0, regime=REGIME, alavancagem=1, **params):
    pnl, _ = _livro(d, capital, _p(params), lag, custo_mult, alavancagem)
    return O.fecha(sum(pnl.values()) / capital, regime, CUSTO_TROCA, custo_mult)


def classes_ir(d, capital=20000, **params):
    pnl, _ = _livro(d, capital, _p(params), 0, 1, 1)
    return {CLASSE_IR: sum(pnl.values())}


def posicoes(d, capital=20000, **params):
    pnl, _ = _livro(d, capital, _p(params), 0, 0, 1)
    return O.wr_de_pnl(pnl, capital)


def negocios(d, capital=20000, **params):
    _, neg = _livro(d, capital, _p(params), 0, 1, 1)
    return O.negocios_df(neg, capital)
