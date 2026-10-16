"""
mx_noite_isenta — frente pf3_mecanismos. Mecanismo 4 (ser pequeno: a isenção de IR de R$ 20 mil de vendas de ações por mês) + 3 (magnitude)
aplicados ao vencedor b3_leilao_noite_aud, que paga 15% de IR porque vende R$ 400+ mil por mês e só sobrevive a 8 bps ida e volta
(sem o 1% melhor das noites: de 112 para 35 pp).

Inspiração: rev_rebal_ibovespa / b3_opa_leilao (vendas pequenas no mês -> ganho isento) e bb_dividendo_extra_aud (só os eventos grandes
pagam). Hipótese: se o edge da noite está na cauda (as quedas forçadas maiores), um orçamento de vendas de R$ 20 mil por mês gasto só nas
MAIORES quedas (limiar alto) captura a maior parte do ganho por negócio, sem IR e com 1/20 do giro — o custo deixa de dominar.
Regra: decisão no fechamento de t: entre as ações líquidas (ADV60 >= R$ 50 mi) que caíram >= `limiar` abaixo da média do mercado, a de
maior queda; compra R$ `tam` (fixo em reais: a isenção é por CPF, não proporcional ao capital) no leilão de fechamento de t+1 e vende no
leilão de abertura de t+2, SE as vendas do mês da venda + `tam` <= R$ 20 mil (orçamento; a ordem é cronológica — sem olhar o futuro).
Custos do auditado (emolumentos 0,03% + 1 bp de derrapagem por lado). IR: todo mês com vendas <= R$ 20 mil -> isento (Lei 11.033/2004).
limiar e tam escolhidos só no IS (2014-06 a 2020) pelo maior IR. Com R$ 50 mil o fundo usa os MESMOS reais (o ganho em pp cai à metade).
"""
import numpy as np
import pandas as pd

import _mx_comum as X
import b3_leilao_noite_aud as O

BB, B, C, pf, DIAS = X.BB, X.B, X.C, X.pf, X.DIAS

NOME = "Noite nos leilões só nas maiores quedas, dentro da isenção de R$ 20 mil/mês"
TESE = ("Gasto o orçamento de vendas isento (R$ 20 mil/mês) só nas noites depois das maiores quedas forçadas: compro no leilão de fechamento, "
        "vendo no de abertura, sem IR")
BENCHMARK = "CDI"
INICIO, CORTE = O.INICIO, O.CORTE
REGIME = "nenhum"
CLASSE_IR = "acoes"
CUSTO_TROCA = .001
ISENCAO = 20_000.0
PARAMS = {"limiar": .03, "tam": 2500.0, "adv_min": 5e7}
GRADE = {"limiar": [.03, .05, .07], "tam": [2500.0, 5000.0]}
VIZINHANCA = {"limiar": (.025, .045), "tam": (2000.0, 4000.0)}
INSTRUMENTOS = O.INSTRUMENTOS
APLICAVEL = True
MOTIVO = "ordens a mercado nos leilões; só alguns pregões por mês (até 4–8 noites)"
ALAVANCAGENS = [1]
MOTIVO_ALAV = "o limite é a isenção, não o capital"
_RES = {}


def carrega():
    return O.carrega()


def roda(d, capital=20000, custo_mult=1, lag=0, alavancagem=1, limiar=.03, tam=2500.0, adv_min=5e7):
    key = (id(d), capital, custo_mult, lag, alavancagem, limiar, tam, adv_min)
    if key in _RES:
        return _RES[key]
    P, R, Oo, V = (d[k].reindex(DIAS) for k in ("P", "R", "O", "V"))
    cols = [c for c in P.columns if c[-1] in "345678" or c.endswith("11")]
    P, R, Oo, V = P[cols], R[cols], Oo[cols], V[cols]
    adv = V.fillna(0).rolling(60, min_periods=40).mean()
    liq = (adv >= adv_min) & P.notna()
    dia = (P / Oo - 1).where(Oo > 0)
    noite = ((1 + R) / (1 + dia) - 1).where(Oo > 0)
    rel = R.sub(R.where(liq).mean(axis=1), axis=0)
    s = (-rel).where(liq & (rel <= -limiar))
    melhor = s.idxmax(axis=1, skipna=True)
    tem = s.notna().any(axis=1)
    Pv, Nv = P.values, noite.values
    T, N = Pv.shape
    sh = 1 + lag
    val = np.zeros((T, N))
    mes = DIAS.to_period("M")
    vend = {}
    t_amt = tam * alavancagem
    for i in np.flatnonzero(tem.values):
        ib = i + sh                                    # compra no fechamento
        iv = ib + 1                                    # venda na abertura seguinte
        if iv >= T:
            continue
        j = cols.index(melhor.iat[i])
        p = Pv[ib, j]
        if not (p > 0):
            continue
        q = np.floor(t_amt / p) * p
        if q <= 0 or vend.get(mes[iv], 0.0) + q > ISENCAO or val[ib].sum() > 0:
            continue
        val[ib, j] = q
        vend[mes[iv]] = vend.get(mes[iv], 0.0) + q
    val = pd.DataFrame(val, index=DIAS, columns=cols)
    no = noite.shift(-1)
    g = (val * no).fillna(0)
    custo = val * 2 * (B.EMOL + O.SLIP) * custo_mult
    pnl = (g - custo).sum(axis=1).shift(1).fillna(0)
    usado = val.sum(axis=1).shift(1).fillna(0)
    cdi_p = usado * C.CDI.reindex(DIAS).fillna(0)
    e = (pnl - cdi_p) / capital
    W = (val / capital).shift(-sh).fillna(0)
    ii, jj = np.nonzero((val > 0).values)
    ng = pd.DataFrame({"ativo": np.array(cols)[jj], "lado": 1, "entrada": DIAS[ii], "saida": DIAS[np.minimum(ii + 1, T - 1)], "dias": 1,
                       "retorno_%": (no.values[ii, jj] - 2 * (B.EMOL + O.SLIP) * custo_mult) * 100,
                       "contrib_pp": (g.values[ii, jj] - custo.values[ii, jj]) / capital * 100, "valor": val.values[ii, jj]})
    vd = usado.copy()                                   # vendas no dia da venda (abertura de t+2)
    mesv = vd.groupby(DIAS.to_period("M")).transform("sum")
    isento = mesv <= ISENCAO
    res = {"e": e.fillna(0), "pnl": pnl, "custo": pd.Series(0.0, index=DIAS), "cdi_perdido": cdi_p, "W": W.loc[:, (W != 0).any()], "R": noite,
           "negocios": ng, "vendas": vd,
           "classes": {"acoes_isentas": pnl.where(isento, 0.0), "acoes": pnl.where(~isento, 0.0), "_cdi_perdido": cdi_p}}
    if len(_RES) > 32:
        _RES.clear()
    _RES[key] = res
    return res


X.contrato(globals(), roda)

if __name__ == "__main__":
    import sys
    X.escolhe_is(sys.modules[__name__], carrega())
