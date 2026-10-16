"""
mx_ofertas_desconto — frente pf3_mecanismos. Mecanismo 3 (magnitude) aplicado à tranche de varejo dos FOLLOW-ONS (b3_ofertas_varejo_aud:
+2,6 pp, mas "raro: depende de 1–2 ofertas grandes por ano"; os IPOs dão o grosso do risco).

Inspiração: bb_dividendo_extra_aud (só paga acima de um limiar de tamanho) e a própria tese da oferta (o coordenador dá desconto para
fechar o livro institucional).
Hipótese: no follow-on o "tamanho" do presente é o desconto do preço da oferta contra o último fechamento antes da precificação. A pessoa
física pode condicionar o pedido de reserva a um PREÇO MÁXIMO (pedido com limite de preço, previsto nos prospectos ICVM 400 / Res. 160):
coloco o limite = fechamento da véspera da precificação x (1 − Y). A oferta tem preço único; se ele ficar acima do limite, o pedido é
cancelado sem custo além do bloqueio. Não é fill de ordem limitada com dado diário: o preço da oferta é um só para todos.
Regra: só follow-ons (empresa já listada) com tranche de varejo; Y escolhido só no IS (2014–2020) pelo maior IR com >= 10 negócios no IS.
Alocação/rateio/venda/custos iguais ao auditado (rateio 15% nas ICVM 400 que estrearam em alta; Res. 160 = 0,5x a média por PF; venda no
fechamento do k-ésimo pregão). O pedido é bloqueado 5 pregões em TODO follow-on pedido (mesmo os cancelados pelo limite).
"""
import numpy as np
import pandas as pd

import _mx_comum as X
import b3_ofertas_varejo as O
import b3_ofertas_varejo_aud as A

BB, B, C, pf, DIAS = X.BB, X.B, X.C, X.pf, X.DIAS

NOME = "Follow-on pela tranche de varejo só com desconto >= Y (pedido com preço máximo)"
TESE = ("Peço R$ 5 mil em todo follow-on com tranche de varejo, com preço máximo = fechamento da véspera da precificação x (1 − Y): só recebo "
        "quando o coordenador dá desconto grande; vendo no 1º pregão")
BENCHMARK = "CDI"
INICIO, CORTE = O.INICIO, O.CORTE
REGIME = "nenhum"
CLASSE_IR = "acoes"
CUSTO_TROCA = .001
PARAMS = {"desc_min": -1.0, "k": 1, "pedido": 5000.0, "fator": .5, "rateio": .15}
GRADE = {"desc_min": [-1.0, .02, .04, .06]}
VIZINHANCA = {"desc_min": (-.05, .01), "pedido": (3000.0, 10000.0), "rateio": (.1, .3)}
INSTRUMENTOS = O.INSTRUMENTOS
APLICAVEL = True
MOTIVO = "pedido de reserva com limite de preço em qualquer corretora consorciada; poucos follow-ons com varejo por ano"
ALAVANCAGENS = [1]
MOTIVO_ALAV = O.MOTIVO_ALAV
_F = {}


def carrega():
    return O.carrega()


def _filtra(d, desc_min):
    k = (id(d), desc_min)
    if k not in _F:
        if len(_F) > 16:
            _F.clear()
        P = d["P"].reindex(DIAS)
        of = d["ofertas"]
        of = of[~of.inicial].copy()
        desc = []
        for dt, t, pr, fo in zip(of.data, of.ticker, of.preco, of.fonte):
            i0 = DIAS.searchsorted(dt) + (1 if "rcvm160" in str(fo) else 0)    # 1º pregão depois da precificação
            ip = i0 - 2                                                       # véspera da precificação: o limite é fixado aqui
            ref = P[t].iloc[:max(ip, 0) + 1].dropna() if t in P else pd.Series(dtype=float)
            desc.append(1 - pr / ref.iloc[-1] if len(ref) else np.nan)
        of["desc"] = desc
        dd = dict(d)
        dd["ofertas_pedidas"] = of.drop(columns="desc")
        dd["ofertas"] = of[of.desc >= desc_min].drop(columns="desc")
        _F[k] = (d, dd)
    return _F[k][1]


def roda(d, capital=20000, custo_mult=1, lag=0, alavancagem=1, desc_min=-1.0, k=1, pedido=5000.0, fator=.5, rateio=.15):
    dd = _filtra(d, desc_min)
    r = dict(O.roda(dd, capital, custo_mult, lag, tipo="todos", k=k, pedido=pedido, fator=fator, rateio=rateio))
    bl = A._bloqueio({"ofertas": dd["ofertas_pedidas"]}, capital, pedido)
    r["e"] = r["e"] * alavancagem - bl / capital
    r["cdi_perdido"] = r["cdi_perdido"] + bl
    r["custo"] = pd.Series(0.0, index=DIAS)
    return r


X.contrato(globals(), roda)

if __name__ == "__main__":
    import sys
    X.escolhe_is(sys.modules[__name__], carrega())
