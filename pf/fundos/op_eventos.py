"""
Volatilidade de evento na B3: Copom e eleição (opções de BOVA11) e resultado trimestral (opções do próprio papel), comprando a vol
de evento quando ela está barata e vendendo quando está cara.

Tese de mesa: antes de evento agendado, o formador de mercado sobe a IV do vencimento curto para cobrir o salto. Se o salto que a
curva embute é maior que o salto típico daquele tipo de evento, vendo (iron butterfly ATM com asas, risco definido); se é menor,
compro o straddle. O salto implícito sai da estrutura a termo das IVs ATM (1º e 2º vencimentos, ambos depois do evento):
    var_dia = (IV2²·T2 − IV1²·T1)/(T2 − T1);  salto² = IV1²·T1 − var_dia·T1
e o salto "justo" é o desvio do retorno do papel nos eventos ANTERIORES do mesmo tipo (só passado; mínimo 4 eventos).
Por que PF: lotes de 100, 1–5 estruturas por evento (R$ 300–1.500 de risco) — o institucional não monta tamanho em 2 dias; o
varejo que compra call de PETR na véspera do balanço paga o formador. Entrada no fechamento da véspera (calendário conhecido),
saída no fechamento do 1º pregão depois do evento, sempre no bid/ask.

Datas (= divulgação): Copom = dia da decisão (sai depois do fechamento; BCB, historicotaxasjuros); eleição = domingo do 1º/2º turno
(TSE: 2014, 2018, 2022, 2026); resultado = data de entrega do ITR/DFP à CVM (pode sair antes da abertura: por isso entro na véspera).
`lag` = sinal mais cedo e saída mais tarde (segura o evento por mais dias). IR: opcoes_b3.
"""
import numpy as np
import pandas as pd

import op_base as O

NOME = "Vol de evento na B3: Copom/eleição (BOVA11) e resultado (opções do papel)"
TESE = ("Compro straddle quando o salto embutido na estrutura a termo da IV é menor que o salto histórico do tipo de evento e vendo "
        "iron butterfly quando é maior; entra na véspera, sai no dia seguinte, no bid/ask")
BENCHMARK = "CDI"
INICIO, CORTE = "2014-03-01", "2021-01-01"
REGIME, CUSTO_TROCA = "nenhum", 0.0
CLASSE_IR = "opcoes_b3"
RAIZES = [r for r in O.TICKER]
ELEICOES = ["2014-10-05", "2014-10-26", "2018-10-07", "2018-10-28", "2022-10-02", "2022-10-30", "2026-10-04"]
PARAMS = {"eventos": "macro", "modo": "vende", "k": 1.2, "largura": .05, "risco": .03}   # maior IR no IS (−0,86: todas negativas)
GRADE = {"eventos": ["todos", "macro", "resultado"], "modo": ["regra", "vende", "compra"]}
VIZINHANCA = {"k": (1.0, 1.5), "largura": (.03, .08), "risco": (.02, .05)}
INSTRUMENTOS = [{"onde": "B3", "ticker": "opções mensais de BOVA11 e das ações (vencimento mais curto com >= 3 pregões)", "lote": 100,
                 "custo": "bid/ask na entrada e na saída + ~0,10% do prêmio por lado"},
                {"onde": "Tesouro Direto / B3", "ticker": "Tesouro Selic (garantia)", "lote": "R$ ~170", "custo": "igual ao benchmark"}]
APLICAVEL = True
MOTIVO = ("Cabe: iron butterfly de 5% em PETR (R$ 30) perde no máximo ~R$ 100 por lote; straddle de BOVA11 custa ~R$ 300–600 por lote. "
          "Com 3% de risco por evento (R$ 600) são 1–5 estruturas. Liquidez: BOVA11 só a partir de 2019.")
ALAVANCAGENS = [1, 1.5, 2]
MOTIVO_ALAV = "Alavancagem = múltiplo do risco por evento (3% -> 6%); eventos se sobrepõem na temporada de balanços."


def carrega():
    d = O.carrega_b3(RAIZES)
    cp = pd.read_csv(O.DADOS / "copom.csv", parse_dates=["data"])
    ev = [pd.DataFrame({"data": cp.data, "tipo": "copom", "raiz": "BOVA"}),
          pd.DataFrame({"data": pd.to_datetime(ELEICOES), "tipo": "eleicao", "raiz": "BOVA"})]
    r = pd.read_parquet(O.AQUI.parent / "dados" / "rev_pead_ev.parquet")      # entregas de ITR/DFP à CVM (frente revisita)
    inv = {t: k for k, t in O.TICKER.items()}
    for tk, raiz in inv.items():
        x = r[r.tickers.astype(str).str.split(",").apply(lambda l: tk in l)]
        if len(x):
            ev.append(pd.DataFrame({"data": pd.to_datetime(x.data).drop_duplicates(), "tipo": "resultado", "raiz": raiz}))
    e = pd.concat(ev, ignore_index=True).drop_duplicates(["data", "raiz", "tipo"])
    d["ev"] = e[e.data >= "2014-01-01"].sort_values("data").reset_index(drop=True)
    return d


def _janela(ev):
    """(entrada, saída) em pregões: Copom sai depois do fechamento (entro no próprio dia); eleição/resultado: véspera."""
    dt = pd.Timestamp(ev.data)
    antes = O.DIAS[O.DIAS <= dt] if ev.tipo == "copom" else O.DIAS[O.DIAS < dt]
    depois = O.DIAS[O.DIAS > dt]
    if not len(antes) or not len(depois):
        return None, None
    return antes[-1], depois[0]


def _salto_implicito(d, raiz, dia, saida):
    """Salto do evento embutido nas IVs ATM dos 2 vencimentos seguintes (ambos depois da saída + 3 pregões)."""
    S0 = d["S"][raiz].get(dia, np.nan)
    if not np.isfinite(S0):
        return np.nan, None
    vs = [v for v in O.vencimentos(d["opc"], raiz) if v > saida and O.du(saida, v) >= 3]
    if len(vs) < 2:
        return np.nan, None
    (iv1, _), (iv2, _) = O.iv_atm(d, raiz, vs[0], dia, S0), O.iv_atm(d, raiz, vs[1], dia, S0)
    T1, T2 = O.du(dia, vs[0]) / 252, O.du(dia, vs[1]) / 252
    if not (iv1 == iv1 and iv2 == iv2) or T2 <= T1:
        return np.nan, vs[0]
    var_dia = max((iv2 ** 2 * T2 - iv1 ** 2 * T1) / (T2 - T1), 0.0)
    return np.sqrt(max(iv1 ** 2 * T1 - var_dia * T1, 0.0)), vs[0]


def _livro(d, capital, p, lag, custo_mult, alavancagem):
    ev = d["ev"]
    if p["eventos"] == "macro":
        ev = ev[ev.tipo.isin(["copom", "eleicao"])]
    elif p["eventos"] == "resultado":
        ev = ev[ev.tipo == "resultado"]
    pnl = {r: pd.Series(0.0, index=O.DIAS) for r in RAIZES}
    neg, hist = [], {}
    R = d["R"]
    for _, e in ev.iterrows():
        ent, sai = _janela(e)
        if ent is None or e.raiz not in d["S"]:
            continue
        ii = O.DIAS.get_loc(ent)
        js = O.DIAS.get_loc(sai) + lag
        if ii - lag < 1 or js >= len(O.DIAS):
            continue
        sinal, sai = O.DIAS[ii - lag], O.DIAS[js]
        chave = (e.tipo, e.raiz if e.tipo == "resultado" else "BOVA")
        passados = [m for (dt, m) in hist.get(chave, []) if dt <= sinal]
        mov = float(np.log1p(R[e.raiz].loc[ent:sai].iloc[1:]).sum())          # movimento realizado do evento (para o histórico)
        hist.setdefault(chave, []).append((sai, mov))
        if p["modo"] == "regra":
            if len(passados) < 4:
                continue
            justo = float(np.sqrt(np.mean(np.square(passados))))
            salto, _ = _salto_implicito(d, e.raiz, sinal, sai)
            if not salto == salto:
                continue
            lado = -1 if salto > p["k"] * justo else (1 if salto < justo / p["k"] else 0)
        else:
            lado = -1 if p["modo"] == "vende" else 1
        if lado == 0:
            continue
        S0 = d["S"][e.raiz].get(ent, np.nan)
        vs = [v for v in O.vencimentos(d["opc"], e.raiz) if v > sai and O.du(sai, v) >= 3]
        if not vs or not np.isfinite(S0):
            continue
        v = vs[0]
        if lado < 0:
            spec = [("P", 1.0, -1), ("C", 1.0, -1), ("P", 1 - p["largura"], 1), ("C", 1 + p["largura"], 1)]
        else:
            spec = [("P", 1.0, 1), ("C", 1.0, 1)]
        pernas = [O.perna(d, e.raiz, v, ent, S0 * k, tp, sg, custo_mult, saida=sai) for tp, k, sg in spec]
        if any(x is None for x in pernas):
            continue
        Ks = [x["K"] for x in pernas]
        if lado < 0 and not (Ks[2] < Ks[0] and Ks[3] > Ks[1]):
            continue
        cred, pm = O.perda_maxima(pernas, [sg for _, _, sg in spec])
        if not pm > 0 or (lado < 0 and cred <= 0):
            continue
        n = int(np.floor(capital * alavancagem * p["risco"] / pm))
        if n < 1:
            continue
        x = O.limita_perda(O.pnl_pernas(pernas, n, [sg for _, _, sg in spec], custo_mult), pm, n)
        pnl[e.raiz] = pnl[e.raiz].add(x, fill_value=0)
        neg.append(dict(ativo=e.raiz, lado=lado, entrada=x.index[0], saida=x.index[-1], evento=e.tipo, data_evento=e.data, lotes=n,
                        strikes="/".join(f"{k:.2f}" for k in Ks), premio=cred, mov_real_pct=mov * 100, pnl_rs=float(x.sum()),
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
