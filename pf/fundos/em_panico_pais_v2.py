"""
Pânico de país v2: o mesmo ETF de país após crash (em_panico_pais), agora (a) com a CONTA EM DÓLAR v2 (pf.conta_usd: o sleeve mora na
IBKR em T-bill, câmbio hedgeado com WDO, só a 1ª remessa paga IOF) e (b) com o MECANISMO 2 (vendedor em pânico + ÂNCORA que divergiu).

Âncora (decidida no fechamento de t, só passado):
  - "commod": o país caiu, mas o preço que paga as contas dele NÃO caiu junto. Resíduo = retorno do ETF em `jan` pregões − beta x retorno
    da âncora (beta de 252 pregões, até t). Âncoras: EWZ e KSA -> petróleo (BNO); ECH e EPU -> cobre (COPX); EZA -> ouro (GLD); os
    países sem commodity dominante (TUR, ARGT, EWW, INDA, EIDO, VNM) -> o ETF irmão EEM (o resto dos emergentes não caiu).
    Compra só se ETF caiu >= `queda` do topo de `jan` E o resíduo <= −`div` (a queda não é explicada pela âncora).
  - "moeda": o câmbio real como âncora: o ETF caiu >= `queda` mas a moeda local depreciou <= 5% em `jan` pregões -> é fluxo de resgate
    em ações, não crise de balanço de pagamentos (Turquia 2018, Argentina 2019 caem junto com a moeda).
  - "nenhuma": o sinal original (controle).
Caso Rússia: RSX/ERUS foram congelados em 03/2022 e não existem no Yahoo. Verifiquei a regra com dados que existiam: em 24/02/2022 o
petróleo SUBIA (âncora "commod" diverge ao máximo -> compra) e o rublo tinha depreciado só +3,5% em 21 pregões (78,65 -> 81,41 RUB/US$;
âncora "moeda" também compra). Nenhuma âncora de PREÇO protege de sanção: a âncora "divergiu" porque o estrangeiro ficou proibido de ser o
comprador. Por isso a perda sintética de 90% do peso (entrada 25/02, suspensão 04/03/2022) continua LIGADA em todas as variantes.
Variante só informativa: "filtro de sanção" (não compra país sob sanção ocidental vigente — Rússia desde 2014) = russia=False.

Conta: livro do tamanho do sleeve (25% do sleeve por país, até 4 países); hedge EEM vendido exigiria conta margem (US$ 2 mil) e ficou fora.
Custos da IBKR iguais aos do original (em_comum.livro).
"""
import numpy as np
import pandas as pd

import comum as C
import em_comum as E
import em_panico_pais as O
import pf3a_comum as A

CONTA_USD_V2 = True
NOME = "Pânico de país v2: ETF após crash com âncora divergente (conta em dólar v2)"
TESE = ("Compro o ETF de país que caiu >= 15% em 21 pregões SÓ quando a âncora (commodity do país ou EEM) não explica a queda; "
        "sleeve permanente na IBKR em T-bill, câmbio hedgeado com WDO")
BENCHMARK = "CDI"
INICIO, CORTE = "2012-01-01", "2021-01-01"
REGIME = "nenhum"
CUSTO_TROCA = .001
CLASSE_IR = "exterior"
PAISES = O.PAISES
ANCORA_COMMOD = {"EWZ": "BNO", "KSA": "BNO", "ECH": "COPX", "EPU": "COPX", "EZA": "GLD"}
MOEDA = {"TUR": "TRY=X", "EWZ": "BRL=X", "ARGT": "ARS=X", "EZA": "ZAR=X", "EWW": "MXN=X", "ECH": "CLP=X", "EPU": "PEN=X",
         "INDA": "INR=X", "EIDO": "IDR=X", "VNM": "VND=X", "KSA": "SAR=X"}
FX_LIM = .05
PARAMS = {"queda": .15, "jan": 21, "dias": 42, "peso": .25, "ancora": "moeda", "div": .10, "russia": True}   # melhor IS entre as âncoras (IR IS 0,45; sem âncora 0,51)
GRADE = {"queda": [.15, .20], "dias": [21, 42], "ancora": ["nenhuma", "commod", "moeda"]}
VIZINHANCA = {"queda": (.12, .20), "dias": (15, 63), "div": (.06, .14), "peso": (.18, .33)}
SLEEVES = A.SLEEVES
INSTRUMENTOS = ("IBKR: ETFs de país TUR, EWZ, ARGT, EZA, EWW, ECH, EPU, INDA, EIDO, VNM, KSA (fração, US$ 0,0035/ação mín. US$ 0,35); "
                "caixa parado em SGOV/BIL; B3: WDO vendido (US$ 10 mil, contratos inteiros) como hedge do sleeve.")
APLICAVEL = True
MOTIVO = ("Operável em conta cash: 25% do sleeve por país (R$ 1,25–9,4 mil). Sem remessa por negócio (o dinheiro mora lá). "
          "O WDO só existe a partir de ~US$ 5 mil de sleeve (round).")
ALAVANCAGENS = [1, 1.5, 2]
MOTIVO_ALAV = "L multiplica o peso por país; acima do sleeve a IBKR financia (T-bill + 1,5%), o que exige conta margem."


def carrega():
    return E.seleciona(PAISES + ["EEM"] + sorted(set(ANCORA_COMMOD.values())) + sorted(set(MOEDA.values())))


def _pesos(d, queda, jan, dias, peso, ancora, div):
    Pall = E.preco_usd(d)
    P = Pall[PAISES]
    neg = E.negociou(d)[PAISES]
    dd = P / P.rolling(jan, min_periods=jan // 2).max() - 1
    ent = (dd <= -queda) & neg
    if ancora == "commod":
        lp = np.log(P.ffill())
        res = {}
        for c in PAISES:
            a = ANCORA_COMMOD.get(c, "EEM")
            la = np.log(Pall[a].ffill())
            ra, rc = la.diff(), lp[c].diff()
            b = (rc.rolling(252, min_periods=126).cov(ra) / ra.rolling(252, min_periods=126).var()).clip(0, 2)
            res[c] = (lp[c] - lp[c].shift(jan)) - b * (la - la.shift(jan))
        ent &= (pd.DataFrame(res) <= -div).fillna(False)
    elif ancora == "moeda":
        fx = pd.DataFrame({c: np.log(d["raw"][MOEDA[c]].ffill()) for c in PAISES})
        ent &= ((fx - fx.shift(jan)) <= FX_LIM).fillna(False)
    est = E.maquina(ent, pd.DataFrame(False, index=P.index, columns=PAISES), dias, espera=10)
    return E.limita(est * peso, 1.0)


_CACHE = {}


def _roda(d, capital, custo_mult, lag, alavancagem, sleeve_brl, hedge, queda, jan, dias, peso, ancora, div, russia):
    sl = A.sleeve_padrao(capital, sleeve_brl)
    k = (id(d), len(d["raw"]), d["raw"].index[-1], capital, custo_mult, lag, alavancagem, sl, hedge, queda, jan, dias, peso, ancora, div, russia)
    if k in _CACHE:
        return _CACHE[k]
    W = _pesos(d, queda, jan, dias, peso, ancora, div)
    res = E.livro(d, W, sl, lag, custo_mult, alavancagem, hedge_fx="nenhum")
    usd = A.usd_de_ext(res["classes"]["exterior"], res["cambio"], res["remessa"])
    if russia and d["raw"].index.max() >= pd.Timestamp(O.RUSSIA[1]):
        dia = A.DIAS[A.DIAS.searchsorted(pd.Timestamp(O.RUSSIA[1]))]
        perda = pd.Series(0.0, index=A.DIAS)
        perda[dia] = O.RUSSIA[2] * peso * alavancagem * sl / A.PTAX[dia]
        usd = usd + perda
        res["russia_usd"] = perda
    e, cls = A.conta(usd, sl, capital, hedge, custo_mult)
    out = {"e": e, "classes": cls, "res": res, "usd": usd, "sl": sl}
    if len(_CACHE) > 60:
        _CACHE.clear()
    _CACHE[k] = out
    return out


def _p(kw):
    return {**PARAMS, **{k: v for k, v in kw.items() if k in PARAMS}}


def excesso(d, capital=20000, custo_mult=1, lag=0, regime=REGIME, alavancagem=1, sleeve_brl=None, hedge="inteiro", **kw):
    e = _roda(d, capital, custo_mult, lag, alavancagem, sleeve_brl, hedge, **_p(kw))["e"]
    return C.aplica_regime(e, regime, CUSTO_TROCA * custo_mult)


def classes_ir(d, capital=20000, sleeve_brl=None, hedge="inteiro", **kw):
    return _roda(d, capital, 1, 0, 1, sleeve_brl, hedge, **_p(kw))["classes"]


def posicoes(d, capital=20000, sleeve_brl=None, hedge="inteiro", **kw):
    o = _roda(d, capital, 1, 0, 1, sleeve_brl, hedge, **_p(kw))
    W, R = E.posicoes_de(o["res"], o["sl"])
    return W * o["sl"] / capital, R


def negocios(d, capital=20000, sleeve_brl=None, hedge="inteiro", **kw):
    o = _roda(d, capital, 1, 0, 1, sleeve_brl, hedge, **_p(kw))
    ng = A.reescala_negocios(E.negocios_de(o["res"], o["sl"]), o["sl"], capital)
    if "russia_usd" in o["res"]:
        x = o["res"]["russia_usd"]
        ng = pd.concat([ng, pd.DataFrame([{"ativo": "RSX* (sintético)", "lado": 1, "entrada": pd.Timestamp(O.RUSSIA[0]),
                                           "saida": pd.Timestamp(O.RUSSIA[1]), "dias": 5, "retorno_%": O.RUSSIA[2] * 100,
                                           "contrib_pp": float((x * A.PTAX).sum() / capital * 100)}])], ignore_index=True)
    return ng
