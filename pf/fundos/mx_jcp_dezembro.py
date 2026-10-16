"""
mx_jcp_dezembro — frente pf3_mecanismos. Mecanismo 1 (calendário obriga) com o motor do vencedor bb_dividendo_extra_aud.

Inspiração: bb_dividendo_extra_aud (comprador de renda forçado pela data-com; só paga acima de ~3–5% do preço).
Hipótese: em dezembro o calendário obriga o LADO DA EMPRESA — o JCP só é dedutível se for declarado no próprio exercício, então dezenas de
companhias aprovam JCP/dividendo entre 1º e 31/12 com data-com no próprio mês. Se o que paga é o calendário (e não o tamanho), proventos
de dezembro MENORES (0,5–2% do preço, abaixo do limiar do vencedor) também deveriam render até a data-com. Se o que paga é a magnitude,
dezembro com provento pequeno não rende.
Regra: mesmo motor/execução/custos/IR do vencedor (sinal = 1ª entrega na CVM, compra no fechamento de t+1, venda no fechamento da
data-com, ADV >= R$ 5 mi), só proventos APROVADOS em dezembro, com limiar e tipo escolhidos no IS (2014–2020) pelo maior IR.
Tipo 'jcp' = só JCP (JRS CAP PROPRIO); 'todos' = JCP + dividendo. Teto de 3% para isolar o efeito do calendário do efeito tamanho
(o vencedor já opera acima de 2%).
"""
import pandas as pd

import _mx_comum as X
import bb_dividendo_extra_aud as A

BB, B, C, pf, DIAS = X.BB, X.B, X.C, X.pf, X.DIAS

NOME = "JCP/dividendo de dezembro (calendário fiscal) até a data-com"
TESE = ("Em dezembro a empresa é obrigada pelo calendário fiscal a declarar o JCP; compro após o aviso e vendo na data-com ao investidor "
        "de renda, mesmo com provento pequeno (0,5–3% do preço)")
BENCHMARK = "CDI"
INICIO, CORTE = A.INICIO, A.CORTE
REGIME = "nenhum"
CLASSE_IR = "acoes"
CUSTO_TROCA = .001
PARAMS = {"limiar": .005, "tipo": "jcp", "teto": .03, "frac": .20}
GRADE = {"limiar": [.005, .01, .02], "tipo": ["jcp", "todos"]}
VIZINHANCA = {"limiar": (.004, .02), "frac": (.12, .25)}
INSTRUMENTOS = A.INSTRUMENTOS
APLICAVEL = True
MOTIVO = "pagadoras com ADV >= R$ 5 mi; ~R$ 4 mil por evento com R$ 20 mil; concentra em dezembro"
ALAVANCAGENS = [1]
MOTIVO_ALAV = "limitado pelo nº de eventos"
_F = {}


def carrega():
    return A.carrega()


def _filtra(d, tipo, teto):
    k = (id(d), tipo, teto)
    if k not in _F:
        if len(_F) > 8:
            _F.clear()
        dd = dict(d)
        pv = d["prov"]
        m = pv.aprov.dt.month == 12
        if tipo == "jcp":
            m &= pv.tipo.str.contains("JRS")
        pv = pv[m]
        # teto de tamanho (soma dos proventos da mesma aprovação/data-com / preço do dia da aprovação): acima é o vencedor
        P = d["P"].reindex(DIAS).ffill(limit=5)
        g = pv.groupby(["aprov", "ticker", "com"]).valor.transform("sum")
        px = [P[t].asof(a) if t in P else float("nan") for t, a in zip(pv.ticker, pv.aprov)]
        y = g.values / pd.Series(px, index=pv.index).values
        dd["prov"] = pv[~(y >= teto)]
        _F[k] = (d, dd)
    return _F[k][1]


def roda(d, capital=20000, custo_mult=1, lag=0, alavancagem=1, limiar=.01, tipo="todos", teto=.03, frac=.20):
    dd = A._filtra(_filtra(d, tipo, teto), 5.0)
    return A.O.roda(dd, capital, custo_mult, lag, alavancagem, limiar=limiar, frac=frac, saida="com", min_preg=2)


X.contrato(globals(), roda)

if __name__ == "__main__":
    import sys
    X.escolhe_is(sys.modules[__name__], carrega())
