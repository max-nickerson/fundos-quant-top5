"""
"Wheel" em ações isentas da B3: vendo put coberta por Tesouro Selic; se for exercido, fico com as ações e passo a vender call coberta;
se a call for exercida, volto a vender put.

Tese de mesa: o wheel é a forma de varejo de "comprar a ação mais barato e vender mais caro" recebendo prêmio — quem paga é o
comprador de proteção (put) e o comprador de alta alavancada (call). Para PF ele tem duas vantagens que o institucional não tem:
(1) a perna em ações é ISENTA de IR se as vendas do mês ficam abaixo de R$ 20 mil (com R$ 20–50 mil, a entrega de 1–3 lotes quase
sempre fica) e os dividendos são isentos; (2) o caixa parado espera a put em Tesouro Selic (rende CDI, aceito como garantia).
O risco: na queda forte você fica com a ação (beta) — por isso o fundo é comparado com o CDI E com a própria ação (comprar e segurar
as mesmas ações), para separar o que é prêmio de opção do que é beta (caderno pf/pesquisa/pf2_opcoes.md).

Implementação: por papel, máquina de estados ciclo a ciclo (vencimentos mensais): sem ação -> vendo n puts (1−otm) no bid; no
vencimento, S < K -> compro 100n ações a K (exercício 0,03%), passo a "com ação" (a ação deixa de render CDI: excesso = retorno total −
CDI); com ação -> vendo n calls com strike >= max(S(1+otm), preço de compra) no bid; S > K no vencimento -> entrego a K e volto
para "sem ação". n = piso(capital x alavancagem / nº de papéis / (100 x strike)). Filtro opcional: só vendo opção quando a IV ATM
está acima da mediana dos 12 ciclos anteriores (senão fico só no CDI ou só com a ação). IR: declarado "opcoes_b3" (15% sobre todo o
excesso, mensal) — CONSERVADOR: a perna em ações seria isenta (o caderno mostra a diferença).
"""
import numpy as np
import pandas as pd

import op_base as O

NOME = "Wheel em ações isentas (put coberta por Selic -> ação -> call coberta)"
TESE = "Vendo put com caixa em Tesouro Selic; exercido, fico com a ação (isenta) e vendo call acima do custo; chamado, volto à put"
BENCHMARK = "CDI"
INICIO, CORTE = "2014-03-01", "2021-01-01"
REGIME, CUSTO_TROCA = "nenhum", 0.0
CLASSE_IR = "opcoes_b3"
NOMES = {"3": ["PETR", "VALE", "ITUB"], "6": ["PETR", "VALE", "ITUB", "BBDC", "BBAS", "ABEV"]}
PARAMS = {"nomes": "3", "otm": .03, "filtro": "iv_alta", "acima_custo": 1}     # maior IR no IS (0,69)
GRADE = {"nomes": ["3", "6"], "otm": [.0, .03, .06], "filtro": ["sempre", "iv_alta"]}
VIZINHANCA = {"otm": (.0, .07)}
INSTRUMENTOS = [{"onde": "B3", "ticker": "PETR4/VALE3/ITUB4 (+BBDC4/BBAS3/ABEV3) e suas opções mensais", "lote": 100,
                 "custo": "bid/ask do fechamento + 0,10% do prêmio; exercício 0,03%"},
                {"onde": "Tesouro Direto / B3", "ticker": "Tesouro Selic (garantia da put)", "lote": "R$ ~170", "custo": "igual ao benchmark"}]
APLICAVEL = True
MOTIVO = ("Cabe: 1 lote de PETR4 a R$ 30 = R$ 3 mil de garantia; com R$ 20 mil, 1–2 lotes de 3 papéis. Com 6 papéis e R$ 20 mil alguns "
          "ficam sem lote (VALE3 a R$ 60–80 = R$ 6–8 mil por lote).")
ALAVANCAGENS = [1]
MOTIVO_ALAV = "Put coberta por caixa: alavancar = vender put sem caixa para comprar as ações — perde o 'risco definido'. Só 1x."


def carrega():
    return O.carrega_b3(["PETR", "VALE", "ITUB", "BBDC", "BBAS", "ABEV"])


def _papel(d, raiz, cap, p, lag, custo_mult):
    """P&L diário (opções, ações) de um papel e lista de negócios."""
    c = O.ciclos(d, raiz)
    S, R = d["S"][raiz], d["R"][raiz]
    opc = pd.Series(0.0, index=O.DIAS)
    acao = pd.Series(0.0, index=O.DIAS)
    neg = []
    q, base, desde = 0, np.nan, None                  # ações em carteira, preço de compra, data da compra
    for _, z in c.iterrows():
        d0 = O.execucao(z.ds, lag, z.v)
        if d0 is None:
            continue
        S0 = S.get(d0, np.nan)
        if not np.isfinite(S0):
            continue
        vende = p["filtro"] == "sempre" or (z.iv == z.iv and z.iv_med == z.iv_med and z.iv > z.iv_med)
        if q == 0:
            if not vende:
                continue
            n = int(np.floor(cap / (S0 * (1 - p["otm"]) * 100)))
            if n < 1:
                continue
            pr = O.perna(d, raiz, z.v, d0, S0 * (1 - p["otm"]), "P", -1, custo_mult)
            if pr is None:
                continue
            x = O.pnl_pernas([pr], n, [-1], custo_mult)
            ST = S.get(z.v, np.nan)
            if not np.isfinite(ST):
                opc = opc.add(x, fill_value=0)
                break
            if pr["intr_fim"] > 0:                     # exercido: compro as ações a K (a perda K − S_T já está na opção)
                x.iloc[-1] += n * 100 * ST * (O.P.B3_EMOL + O.P.B3_SPREAD["liquida"]) * custo_mult   # pnl_pernas desmonta o saldo; aqui fico
                q, base, desde = n * 100, pr["K"], z.v
            opc = opc.add(x, fill_value=0)
            neg.append(dict(ativo=raiz + "_put", lado=-1, entrada=x.index[0], saida=x.index[-1], lotes=n, K=pr["K"], premio=pr["preco"],
                            exercida=pr["intr_fim"] > 0, pnl_rs=float(x.sum()), **{"retorno_%": float(x.sum() / (n * 100 * pr["K"]) * 100)}))
        else:
            if not vende:
                continue
            n = q // 100
            k_alvo = max(S0 * (1 + p["otm"]), base if p["acima_custo"] else 0)
            pr = O.perna(d, raiz, z.v, d0, k_alvo, "C", -1, custo_mult)
            if pr is None or (p["acima_custo"] and pr["K"] < .98 * base):
                continue
            x = O.pnl_pernas([pr], n, [-1], custo_mult)
            ST = S.get(z.v, np.nan)
            if not np.isfinite(ST):
                opc = opc.add(x, fill_value=0)
                break
            if pr["intr_fim"] > 0:                     # chamado: entrego as ações a K; volto para o caixa
                x.iloc[-1] += n * 100 * ST * (O.P.B3_EMOL + O.P.B3_SPREAD["liquida"]) * custo_mult   # não recompro: só a tarifa do exercício
                ate = z.v
                a = _acao(S, R, q, desde, ate)
                acao = acao.add(a, fill_value=0)
                neg.append(dict(ativo=raiz + "_acao", lado=1, entrada=desde, saida=ate, lotes=n, K=base, premio=np.nan, exercida=True,
                                pnl_rs=float(a.sum()), **{"retorno_%": float(a.sum() / (q * base) * 100)}))
                q, base, desde = 0, np.nan, None
            opc = opc.add(x, fill_value=0)
            neg.append(dict(ativo=raiz + "_call", lado=-1, entrada=x.index[0], saida=x.index[-1], lotes=n, K=pr["K"], premio=pr["preco"],
                            exercida=pr["intr_fim"] > 0, pnl_rs=float(x.sum()), **{"retorno_%": float(x.sum() / (n * 100 * S0) * 100)}))
    if q > 0:                                          # ainda com ações no fim dos dados
        a = _acao(S, R, q, desde, O.DIAS[-1])
        acao = acao.add(a, fill_value=0)
        neg.append(dict(ativo=raiz + "_acao", lado=1, entrada=desde, saida=O.DIAS[-1], lotes=q // 100, K=base, premio=np.nan, exercida=False,
                        pnl_rs=float(a.sum()), **{"retorno_%": float(a.sum() / (q * base) * 100)}))
    return opc, acao, neg


def _acao(S, R, q, de, ate):
    """P&L em R$ de q ações do fechamento de `de` ao de `ate`: retorno total menos o CDI que o dinheiro deixou de render."""
    dias = O.DIAS[(O.DIAS > de) & (O.DIAS <= ate)]
    v = (q * S.reindex(O.DIAS).ffill()).shift(1).reindex(dias)
    return (v * (R.reindex(dias).fillna(0) - O.CDI.reindex(dias).fillna(0))).fillna(0)


def _livro(d, capital, p, lag, custo_mult):
    nomes = NOMES[p["nomes"]]
    cap = capital / len(nomes)
    pnl, neg = {}, []
    for r in nomes:
        o, a, ng = _papel(d, r, cap, p, lag, custo_mult)
        pnl[r + "_opc"], pnl[r + "_acao"] = o, a
        neg += ng
    return pnl, neg


def _p(params):
    return {**PARAMS, **params}


def excesso(d, capital=20000, custo_mult=1, lag=0, regime=REGIME, alavancagem=1, **params):
    pnl, _ = _livro(d, capital * alavancagem, _p(params), lag, custo_mult)
    return O.fecha(sum(pnl.values()) / capital, regime, CUSTO_TROCA, custo_mult)


def classes_ir(d, capital=20000, **params):
    pnl, _ = _livro(d, capital, _p(params), 0, 1)
    return {"opcoes_b3": sum(v for k, v in pnl.items() if k.endswith("_opc")), "acoes_isentas": sum(v for k, v in pnl.items() if k.endswith("_acao"))}


def posicoes(d, capital=20000, **params):
    pnl, _ = _livro(d, capital, _p(params), 0, 0)
    return O.wr_de_pnl(pnl, capital)


def negocios(d, capital=20000, **params):
    _, neg = _livro(d, capital, _p(params), 0, 1)
    return O.negocios_df(neg, capital)
