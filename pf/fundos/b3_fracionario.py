"""
Fracionário x lote padrão: vender caro no fracionário (onde o varejo compra com ordem a mercado) e recomprar no lote padrão.

Mesa: o mercado fracionário (TPMERC 020, sufixo F) tem livro próprio, quase só pessoa física e poucos formadores; o lote padrão tem os
algoritmos. O COTAHIST traz a melhor oferta de compra e de venda no fim do dia dos DOIS livros. Quando a melhor oferta de COMPRA do
fracionário fica acima da melhor oferta de VENDA do lote (alguém no fracionário está pagando mais do que o lote pede), uma pessoa
física com conta de day trade pode, no pregão seguinte, deixar uma ordem de VENDA limitada de 100 ações no fracionário a esse preço
e, se executada, recomprar 1 lote de 100 no lote padrão no fechamento — posição zerada no dia (day trade), lucro = prêmio do fracionário.
Execução da ordem limitada: sempre ao preço LIMITE (conservador). Na bolsa, se o fracionário abre além do limite a ordem sai na
abertura (melhor); isso vale +10 pp a.a. a mais na simulação (fill='abertura'), mas o preço de abertura de um livro fino com a minha
ordem dentro seria outro — não conto com isso. Consequência: o teste de atraso (t+2) é pessimista, pois o limite fica velho.
O simétrico: oferta de venda do fracionário abaixo da de compra do lote -> compra 100 no fracionário e vende 1 lote.
O institucional não faz isso: 100 ações de cada vez não pagam a mesa.

Regras (sem olhar o futuro): sinal no fim do pregão t (prêmio >= `limiar`); em t+1+lag deixo a ordem limitada ao preço da oferta de t;
ela só conta como executada se o fracionário negociou ACIMA (venda) / ABAIXO (compra) do meu preço em pelo menos 1 centavo E negociou
>= `qmin` ações no dia (minhas 100 cabem na fila); a outra perna é no lote padrão ao PIOR entre o fechamento e a melhor oferta do fim
do dia (compro no maior, vendo no menor). Até `n_max` operações por dia (as de maior prêmio), 100 ações (200 com R$ 50 mil),
só papéis até R$ 50 e com giro médio de 20 dias no lote >= `adv_min` (a perna do lote tem de ser executável). Custos: emolumentos de day trade 0,023% por perna. IR: day trade 20%. Capital fica no CDI (garantia em Tesouro
Selic); o excesso é só o P&L das operações.
Ressalva honesta: o COTAHIST não informa a quantidade na melhor oferta nem o horário; a regra de execução exige que o preço tenha sido
ultrapassado no dia seguinte, o que é o mínimo para a ordem ter sido executada.
"""
import numpy as np
import pandas as pd

import b3_base as B

C, pf = B.C, B.pf

NOME = "Fracionário x lote padrão em day trade (PF)"
TESE = ("Vendo 100 ações no fracionário quando o varejo ali paga mais do que o lote padrão pede (e recompro 1 lote), ou o inverso: prêmio "
        "entre dois livros da mesma ação que só existe em lotes de 100 ações, pequeno demais para o institucional")
BENCHMARK = "CDI"
INICIO, CORTE = "2014-06-01", "2021-01-01"
REGIME = "nenhum"
CUSTO_TROCA = .001
PARAMS = {"limiar": .01, "lado": "ambos", "qmin": 1000, "n_max": 5, "preco_max": 50.0, "adv_min": 1e6}
GRADE = {"limiar": [.005, .01, .02], "lado": ["ambos", "vende_frac"], "adv_min": [2e5, 2e6]}
VIZINHANCA = {"limiar": (.004, .03), "qmin": (300, 3000), "n_max": (2, 8), "adv_min": (3e5, 5e6)}
INSTRUMENTOS = [{"onde": "Clear/Rico/XP (conta com day trade)", "ticker": "ações com fracionário ativo", "lote": "100 ações (fracionário 1-99 + 1 ordem)",
                 "custo": "emolumentos de day trade 0,023% por perna; corretagem zero"}]
APLICAVEL = True
MOTIVO = ("exige conta de day trade e venda a descoberto intradiária no fracionário (permitida em Clear/Rico para papéis líquidos; restrita em "
          "papéis pequenos) e automação (MetaTrader/Profit) para deixar várias ordens por dia")
ALAVANCAGENS = [1, 1.5, 2]
MOTIVO_ALAV = "day trade usa margem pequena; dobrar o nº de lotes é possível, mas a fila do fracionário limita (a execução simulada já é otimista)"
_RES = {}


def carrega():
    d = B.painel("P", "BID", "ASK", "V")
    f = B.ler("fracionario")
    f = f[f.ticker.isin(d["P"].columns)].copy()
    d["frac"] = f
    return d


def _eventos(d, limiar, lado, qmin, n_max, preco_max, lag, adv_min, fill="limite"):
    f = d["frac"]
    idx = B.DIAS
    i = idx.get_indexer(pd.to_datetime(f.data))
    f = f.assign(i=i)[i >= 0]
    P, BID, ASK = d["P"], d["BID"], d["ASK"]
    adv = d["V"].reindex(P.index).fillna(0).rolling(20, min_periods=10).mean().values
    cols = {t: k for k, t in enumerate(P.columns)}
    j = f.ticker.map(cols).values
    ii = f.i.values
    bl, al, pl = BID.values[ii, j], ASK.values[ii, j], P.values[ii, j]
    mid = (bl + al) / 2
    ok = (bl > 0) & (al > bl) & (f.oferta_compra_f > 0) & (f.oferta_venda_f > f.oferta_compra_f) & (pl <= preco_max) & (adv[ii, j] >= adv_min)
    s_v = (f.oferta_compra_f.values - al) / mid                         # fracionário caro: vendo frac, compro lote
    s_c = (bl - f.oferta_venda_f.values) / mid                          # fracionário barato: compro frac, vendo lote
    ev = []
    for s, sgn, lim in ((s_v, -1, f.oferta_compra_f.values), (s_c, 1, f.oferta_venda_f.values)):
        if lado == "vende_frac" and sgn == 1:
            continue
        m = ok.values & (s >= limiar)
        ev.append(pd.DataFrame({"i": ii[m], "ticker": f.ticker.values[m], "j": j[m], "premio": s[m], "lado": sgn, "lim": lim[m]}))
    ev = pd.concat(ev)
    ev = ev.sort_values(["i", "premio"], ascending=[True, False]).groupby("i").head(int(n_max))
    # execução em t+1+lag: dados do fracionário desse dia
    fx = f.set_index(["i", "ticker"])[["max_f", "min_f", "quantidade_f", "abertura_f"]]
    ev["ie"] = ev.i + 1 + lag
    ev = ev[ev.ie < len(idx)]
    k = pd.MultiIndex.from_arrays([ev.ie.values, ev.ticker.values])
    x = fx.reindex(k)
    ev["max_f"], ev["min_f"], ev["q_f"], ev["ab_f"] = x.max_f.values, x.min_f.values, x.quantidade_f.values, x.abertura_f.values
    ie, jj = ev.ie.values, ev.j.values
    ev["p_l"], ev["b_l"], ev["a_l"] = P.values[ie, jj], BID.values[ie, jj], ASK.values[ie, jj]
    vend = (ev.lado == -1) & (ev.max_f >= ev.lim + .01)
    comp = (ev.lado == 1) & (ev.min_f <= ev.lim - .01)
    ev = ev[(vend | comp) & (ev.q_f >= qmin) & (ev.p_l > 0)].copy()
    # outra perna no lote: pior entre fechamento e oferta do fim do dia
    pior_compra = np.fmax(ev.p_l, ev.a_l.fillna(ev.p_l))
    pior_venda = np.fmin(ev.p_l, ev.b_l.fillna(ev.p_l))
    # ordem limitada deixada antes da abertura: se o fracionário abre além do limite, executa no preço de abertura (melhor que o limite)
    # (sensibilidade 'abertura'; o padrão 'limite' é conservador: com a minha ordem no leilão de abertura, o preço poderia cair até o limite)
    px = ev.lim.values if fill == "limite" else np.where(ev.lado == -1, np.fmax(ev.lim, ev.ab_f.fillna(0)), np.fmin(ev.lim, ev.ab_f.fillna(np.inf)))
    ev["px"] = px
    ev["ret"] = np.where(ev.lado == -1, px / pior_compra - 1, pior_venda / px - 1)
    return ev


def roda(d, capital=20000, custo_mult=1, lag=0, limiar=.01, lado="ambos", qmin=1000, n_max=5, preco_max=50.0, adv_min=1e6, alavancagem=1.0,
         fill="limite"):
    key = (id(d), capital, custo_mult, lag, limiar, lado, qmin, n_max, preco_max, adv_min, alavancagem, fill)
    if key in _RES:
        return _RES[key]
    ev = _eventos(d, limiar, lado, int(qmin), int(n_max), preco_max, lag, adv_min, fill)
    lotes = (100 if capital < 50000 else 200) * alavancagem
    ev["qtd"] = np.floor(lotes / 100) * 100
    ev["notional"] = ev.qtd * ev.lim
    ev["pnl"] = ev.notional * ev.ret - ev.notional * 2 * B.EMOL_DT * custo_mult
    idx = B.DIAS
    pnl = ev.groupby("ie").pnl.sum().reindex(range(len(idx))).fillna(0)
    pnl.index = idx
    W = pd.DataFrame(0.0, index=idx, columns=sorted(ev.ticker.unique()))
    ng = pd.DataFrame({"ativo": ev.ticker.values, "lado": -ev.lado.values, "entrada": idx[ev.ie.values], "saida": idx[ev.ie.values], "dias": 0,
                       "retorno_%": ev.ret.values * 100 - 2 * B.EMOL_DT * 100, "contrib_pp": ev.pnl.values / capital * 100,
                       "valor": ev.notional.values, "ganho": ev.pnl.values, "premio_sinal_%": ev.premio.values * 100})
    res = {"e": pnl / capital, "pnl": pnl, "negocios": ng, "W": W}
    if len(_RES) > 64:
        _RES.clear()
    _RES[key] = res
    return res


def excesso(d, capital=20000, custo_mult=1, lag=0, regime=REGIME, alavancagem=1, **params):
    e = roda(d, capital, custo_mult, lag, alavancagem=alavancagem, **{**PARAMS, **params})["e"]
    return C.aplica_regime(e, regime, CUSTO_TROCA * custo_mult)


def classes_ir(d, capital=20000, **params):
    return {"day_trade": roda(d, capital, **{**PARAMS, **params})["pnl"]}


def posicoes(d, capital=20000, **params):
    """Posições zeradas no dia: não há peso de fim de dia (placebo/atribuição por ativo via negócios)."""
    res = roda(d, capital, **{**PARAMS, **params})
    W = res["W"].iloc[:, :1] if res["W"].shape[1] else pd.DataFrame({"x": 0.0}, index=B.DIAS)
    return W, pd.DataFrame(0.0, index=B.DIAS, columns=W.columns)


def negocios(d, capital=20000, **params):
    return roda(d, capital, **{**PARAMS, **params})["negocios"]
