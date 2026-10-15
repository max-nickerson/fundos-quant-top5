"""
Aluguel de ações como DOADOR: a PF compra as ações com a maior taxa de aluguel esperada (5–30% a.a.) e as empresta pelo BTC da B3
(carteira doadora automática da corretora), com ou sem hedge de Ibovespa (BOVA11 vendido).

Tese de mesa: o institucional que vende a descoberto paga 5–20% a.a. para alugar small caps "apertadas"; a PF com R$ 20–50 mil pode ser
o doador e embolsar a taxa — prêmio que fundo grande não pega porque o papel é pequeno demais para ele. O risco: a taxa é alta
PORQUE alguém informado está vendido — as ações mais alugadas costumam cair mais do que a taxa paga (anomalia de "short interest").
Este fundo mede exatamente isso: taxa recebida x retorno do papel (sem hedge = taxa + beta + seleção; com hedge = taxa + seleção).

Dados de taxa (limite): a B3 só tem no nosso cache as taxas REAIS de dez/2025 a out/2026 (BDI 04-2, a cada 3 pregões,
pf/dados/btc/btc_taxas_b3.parquet, baixado pela frente revisita); antes disso uso o MODELO de taxa da frente revisita
(_ev_pf.taxa_modelo: ADV, queda de 60 pregões, vol, preço < R$ 2, alta > 30% — calibrado nessas mesmas taxas de 2025–26:
o modelo usa só dados até t, mas os coeficientes vieram do fim da amostra — é uma ESTIMATIVA, não histórico). Quando há taxa real,
uso a real (ffill de até 10 pregões).
Repasse: corretoras de varejo repassam ao doador ~70% da taxa (o resto é tarifa da corretora/B3) — premissa `repasse`.
Implementação: no último pregão do mês ordeno as ações com ADV60 >= R$ 1 mi e preço >= R$ 1 pela taxa esperada; compro as N maiores
(com taxa >= taxa_min) em pesos iguais, ações INTEIRAS (fracionário), custo = emolumentos + meio spread por liquidez + 0,2% do
fracionário; executa t+1. Taxa recebida diária = peso x taxa x repasse / 252 (supõe que a carteira inteira fica emprestada: nas
taxas altas a demanda é maior que a oferta). Hedge: BOVA11 vendido (aluguel 0,88% + 0,5% a.a.) no mesmo valor da carteira.
IR: "acoes" (vendas <= R$ 20 mil/mês isentas; a taxa de aluguel é, na verdade, renda fixa com 15–22,5% retido — aproximação otimista
de ~1 pp da taxa).
"""
import numpy as np
import pandas as pd

import b3_base as B3
import _ev_pf as EV
import op_base as O

C, P = O.C, O.P

NOME = "Doador de aluguel: small caps com taxa alta emprestadas (com/sem hedge de Ibovespa)"
TESE = "Compro as N ações com maior taxa de aluguel esperada e empresto (BTC); o teste mostra se a taxa paga a queda do papel"
BENCHMARK = "CDI"
INICIO, CORTE = "2014-06-01", "2021-01-01"
REGIME, CUSTO_TROCA = "nenhum", 0.0
CLASSE_IR = "acoes"
PARAMS = {"n": 10, "hedge": 0, "taxa_min": .08, "repasse": .7}            # melhor IS da grade (−6,5 pp)
GRADE = {"n": [5, 10], "hedge": [0, 1], "taxa_min": [.03, .08]}
VIZINHANCA = {"taxa_min": (.02, .10), "repasse": (.5, .9)}
ALUGUEL_BOVA = .0088 + .005
INSTRUMENTOS = [{"onde": "B3 (Clear/XP/Rico)", "ticker": "small caps com taxa de aluguel alta, carteira doadora", "lote": "1 ação (fracionário)",
                 "custo": "emolumentos 0,03% + meio spread 0,08–0,8% + 0,2% fracionário; corretora fica com ~30% da taxa"},
                {"onde": "B3", "ticker": "BOVA11 vendido (hedge opcional)", "lote": "1 cota", "custo": "aluguel 0,88% + 0,5% a.a."}]
APLICAVEL = True
MOTIVO = "Cabe: R$ 2–4 mil por papel em 5–10 papéis, fracionário; doação automática em qualquer corretora grande."
ALAVANCAGENS = [1]
MOTIVO_ALAV = "Carteira à vista sem alavancagem (alavancar = conta margem, fora do escopo PF)."


def carrega():
    d = B3.painel("P", "R", "V")
    cols = B3.acao_comum(d["P"].columns)
    out = {k: v[cols] for k, v in d.items()}
    out["btc"] = EV.btc_b3(cols)
    return out


def _taxas(d):
    def f():
        adv = d["V"].rolling(60, min_periods=40).mean()
        t = EV.taxa_aluguel(adv, d["R"], d["P"], d["btc"])
        return t, adv
    return O.memo("alug_taxa", d["P"], f)


def _pesos(d, capital, p):
    t, adv = _taxas(d)
    Pc = d["P"].ffill(limit=5)
    ok = (adv >= 1e6) & (Pc >= 1.0) & t.notna() & (t >= p["taxa_min"])
    fim = pd.Series(O.DIAS.to_period("M"), index=O.DIAS)
    fim = fim.ne(fim.shift(-1))
    W = pd.DataFrame(np.nan, index=O.DIAS, columns=d["P"].columns)
    for dia in O.DIAS[fim.values]:
        if dia not in t.index or dia < pd.Timestamp(INICIO) - pd.Timedelta(days=40):
            continue
        s = t.loc[dia].where(ok.loc[dia]).dropna().nlargest(p["n"])
        w = pd.Series(0.0, index=W.columns)
        if len(s):
            alvo = capital / p["n"]
            q = np.floor(alvo / Pc.loc[dia, s.index])
            w[s.index] = (q * Pc.loc[dia, s.index] / capital).values
        W.loc[dia] = w.values
    return W.ffill().fillna(0), t, adv


def _livro(d, capital, p, lag, custo_mult):
    W, t, adv = _pesos(d, capital, p)
    We = W.shift(1 + lag).fillna(0)                                        # executa no fechamento de t+1+lag
    R = d["R"].reindex(O.DIAS).fillna(0)
    cdi = O.CDI.reindex(O.DIAS).fillna(0)
    acoes = (We.shift(1) * R.sub(cdi, axis=0)).sum(axis=1)
    taxa = (We.shift(1) * t.shift(1).fillna(0)).sum(axis=1) * p["repasse"] / 252
    meio = pd.DataFrame(EV.meio_spread(adv.shift(1).values), index=adv.index, columns=adv.columns)
    custo = (We.diff().abs() * (B3.EMOL + meio + B3.FRAC_EXTRA)).sum(axis=1) * custo_mult
    exp = We.sum(axis=1)
    rb = C.R_IBOV.reindex(O.DIAS).fillna(0)
    hedge = -p["hedge"] * exp.shift(1) * ((rb - cdi) + ALUGUEL_BOVA * custo_mult / 252)
    hedge -= p["hedge"] * exp.diff().abs() * (B3.EMOL + 2e-4 + P.ALUGUEL_PF_CORRETORA) * custo_mult
    tot = (acoes + taxa - custo + hedge.fillna(0)) * capital
    return tot.fillna(0), We, R.sub(cdi, axis=0), taxa * capital


def _p(params):
    return {**PARAMS, **params}


def excesso(d, capital=20000, custo_mult=1, lag=0, regime=REGIME, alavancagem=1, **params):
    tot, *_ = _livro(d, capital, _p(params), lag, custo_mult)
    return O.fecha(tot / capital, regime, CUSTO_TROCA, custo_mult)


def classes_ir(d, capital=20000, **params):
    tot, *_ = _livro(d, capital, _p(params), 0, 1)
    return {CLASSE_IR: tot}


def posicoes(d, capital=20000, **params):
    p = _p(params)
    W, t, _ = _pesos(d, capital, p)
    R = d["R"].reindex(O.DIAS).fillna(0).sub(O.CDI.reindex(O.DIAS).fillna(0), axis=0)
    W = W.loc[:, (W != 0).any()]
    R = R[W.columns].copy()
    W["ALUGUEL"] = 1.0
    R["ALUGUEL"] = (W.drop(columns="ALUGUEL").shift(1) * t[W.columns.drop("ALUGUEL")].shift(1).fillna(0)).sum(axis=1) * p["repasse"] / 252
    if p["hedge"]:
        W["BOVA_hedge"] = -W.drop(columns="ALUGUEL").sum(axis=1)
        R["BOVA_hedge"] = C.R_IBOV.reindex(O.DIAS).fillna(0) - O.CDI.reindex(O.DIAS).fillna(0)
    return W, R


def negocios(d, capital=20000, **params):
    p = _p(params)
    tot, We, Rx, taxa = _livro(d, capital, p, 0, 1)
    linhas = []
    for c in We.columns[(We != 0).any()]:
        w = We[c]
        on = (w.shift(1) > 0)
        grp = (on != on.shift()).cumsum()
        for _, g in w[on].groupby(grp[on]):
            idx = g.index
            r = (w.shift(1).reindex(idx) * Rx[c].reindex(idx)).sum() * capital
            tx = (w.shift(1).reindex(idx) * _taxas(d)[0][c].shift(1).reindex(idx).fillna(0)).sum() * p["repasse"] / 252 * capital
            linhas.append(dict(ativo=c, lado=1, entrada=idx[0], saida=idx[-1], taxa_media=float(_taxas(d)[0][c].reindex(idx).mean()),
                               pnl_acao_rs=float(r), pnl_taxa_rs=float(tx), pnl_rs=float(r + tx),
                               **{"retorno_%": float((r + tx) / (w.shift(1).reindex(idx).mean() * capital) * 100)}))
    return O.negocios_df(linhas, capital)
