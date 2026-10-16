"""
mx_opa_desconto — frente pf3_mecanismos. Mecanismo 3 (o edge cresce com o TAMANHO do evento) aplicado à arbitragem de OPA, que foi
marginal na versão corrigida (rev_opa ≈ +0,5 pp sem HBOR3) e pequena no vencedor b3_opa_leilao (+4,1 pp com o spread mínimo de 0%).

Inspiração: bb_dividendo_extra_aud — retorno por negócio monotônico no tamanho do provento (< 3%: −0,2%; 3–5%: +1,5%; > 5%: +3,5%).
Hipótese: na OPA, o "tamanho" é o desconto da ação contra o preço da oferta. Se o leilão paga o piso + correção/melhora, quanto maior o
desconto na entrada maior o ganho até o leilão; abaixo de alguns % o prêmio não paga o CDI perdido de 3–12 meses. Há um teto: desconto
> 30% é o mercado duvidando da OPA (a auditoria: HBOR3 entrou com 44% de desconto, acima da regra).
Correção da auditoria incorporada: o desconto é checado na DECISÃO (fechamento do dia do FR) e no PREÇO DE EXECUÇÃO (ordem limitada
no leilão de fechamento de t+1 com limite = oferta x (1 − smin): no leilão o preço é único, a ordem executa se o preço do leilão for <=
limite; o lote de R$ 3 mil não move o leilão) e tem de ficar entre smin e 30%.
Resto igual ao b3_opa_leilao: saída no leilão real (TPMERC 017) ao preço do leilão, R$ 3 mil por OPA, isento (vendas < R$ 20 mil/mês).
smin escolhido só no IS (2014–2020) pelo maior IR (com >= 10 negócios no IS).
"""
import pandas as pd

import _mx_comum as X
import b3_opa_leilao as O

BB, B, C, pf, DIAS = X.BB, X.B, X.C, X.pf, X.DIAS

NOME = "OPA até o leilão só com desconto grande (magnitude)"
TESE = ("Compro o alvo de OPA em dinheiro só quando o desconto contra o preço da oferta é >= smin (e <= 30%) na decisão e na execução, e "
        "entrego no leilão")
BENCHMARK = "CDI"
INICIO, CORTE = O.INICIO, O.CORTE
REGIME = "nenhum"
CLASSE_IR = "acoes_isentas"
CUSTO_TROCA = .001
PARAMS = {"smin": 0.0, "teto": .30, "prazo": 300, "adv_min": 2e4, "por_opa": 3000.0}
GRADE = {"smin": [0.0, .02, .04, .07]}
VIZINHANCA = {"smin": (-.02, .02), "prazo": (150, 400)}
INSTRUMENTOS = O.INSTRUMENTOS
APLICAVEL = True
MOTIVO = O.MOTIVO
ALAVANCAGENS = [1]
MOTIVO_ALAV = O.MOTIVO_ALAV
_F = {}


def carrega():
    return O.carrega()


def _filtra(d, smin, teto, lag):
    k = (id(d), smin, teto, lag)
    if k not in _F:
        if len(_F) > 16:
            _F.clear()
        P = d["P"].reindex(DIAS)
        ev = d["ev"]
        keep = []
        for dt, t, of in zip(ev.data, ev.ticker, ev.oferta):
            i = DIAS.searchsorted(dt)
            ie = i + 1 + lag
            if t not in P or ie >= len(DIAS):
                keep.append(False)
                continue
            p0, pe = P[t].iat[i], P[t].iat[ie]
            ok = all(pd.notna(x) and of * (1 - teto) <= x <= of * (1 - smin) for x in (p0, pe))
            keep.append(ok)
        dd = dict(d)
        dd["ev"] = ev[keep]
        _F[k] = (d, dd)
    return _F[k][1]


def roda(d, capital=20000, custo_mult=1, lag=0, alavancagem=1, smin=0.0, teto=.30, prazo=300, adv_min=2e4, por_opa=3000.0):
    dd = _filtra(d, smin, teto, lag)
    r = O.roda(dd, capital, custo_mult, lag, smin=-9.0, modo="leilao", prazo=prazo, adv_min=adv_min, por_opa=por_opa)
    r = dict(r)
    r["e"] = r["e"] * alavancagem
    return r


X.contrato(globals(), roda)

if __name__ == "__main__":
    import sys
    X.escolhe_is(sys.modules[__name__], carrega())
