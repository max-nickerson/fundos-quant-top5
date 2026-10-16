"""
Spin-offs pequenos v2: mesmo sinal e custos de IBKR de fg_spinoff_pequeno (separada com giro < US$ 10 mi/dia comprada no fim do 2º mês
(espera 40), segura 252 pregões, 5% do livro por nome; sintéticos para quem sumiu do Yahoo pela classe do EDGAR), mas com a CONTA EM DÓLAR v2 (pf.conta_usd): o livro é do tamanho do sleeve que mora na IBKR em T-bill; só a
1ª remessa paga IOF; câmbio hedgeado com WDO (contratos inteiros).
Hedge de beta (IWM vendido) exige conta margem (US$ 2 mil): só quando o sleeve >= R$ 11 mil (pf3a_comum.tem_margem); abaixo disso o
livro fica comprado sem hedge (beta IWM aparece na regressão do caderno).
"""
import comum as C
import fg_comum as G
import fg_spinoff_pequeno as O
import pf3a_comum as A

CONTA_USD_V2 = True
NOME = "Spin-offs pequenos dos EUA v2 (conta em dólar v2)"
TESE = O.TESE + " Sleeve permanente na IBKR em T-bill, câmbio hedgeado com WDO."
BENCHMARK = "CDI"
INICIO, CORTE = O.INICIO, O.CORTE
REGIME = "nenhum"
CUSTO_TROCA = .001
CLASSE_IR = "exterior"
PARAMS = {k: v for k, v in O.PARAMS.items() if k != "hedge_fx"}
PARAMS["beta_hedge"] = "auto"
PARAMS["sem"] = ""
GRADE = dict(O.GRADE)
VIZINHANCA = dict(O.VIZINHANCA)
SLEEVES = A.SLEEVES
INSTRUMENTOS = O.INSTRUMENTOS
APLICAVEL = True
MOTIVO = ("Operável na IBKR (fração). 5% do sleeve por nome = R$ 250–1.875; IWM vendido só com sleeve >= R$ 11 mil (conta margem). "
          "Concentração: SNDK (2025) pesa muito no OOS — ver variante sem_sndk.")
ALAVANCAGENS = [1, 1.5, 2]
MOTIVO_ALAV = O.MOTIVO_ALAV
_CACHE = {}


def carrega():
    return O.carrega()


def _roda(d, capital, custo_mult, lag, alavancagem, sleeve_brl, hedge, espera, dias, peso, giro_max, sinteticos, beta_hedge, sem=""):
    sl = A.sleeve_padrao(capital, sleeve_brl)
    k = (id(d), len(d["precos"]), d["precos"].index.max(), capital, custo_mult, lag, alavancagem, sl, hedge, espera, dias, round(peso, 5),
         giro_max, sinteticos, beta_hedge, sem)
    if k in _CACHE:
        return _CACHE[k]
    tr, P = O._trades(d, espera, dias, giro_max, sinteticos)
    if sem and len(tr):                                       # variante de concentração: tira um nome (ex.: "SNDK")
        tr = tr[~tr.ticker.astype(str).str.split("*").str[0].isin(sem.split(","))]
    hb = beta_hedge == "IWM" or (beta_hedge == "auto" and A.tem_margem(sl))
    res = G.livro(tr, P, sl, custo_mult, lag, alavancagem, peso, teto=1.0, hedge={"US": "IWM"} if hb else None, hedge_fx="nenhum")
    res["P"] = P
    usd = A.usd_de_ext(res["ext"], res["ganho"], res["remessa"])
    e, cls = A.conta(usd, sl, capital, hedge, custo_mult)
    out = {"e": e, "classes": cls, "res": res, "usd": usd, "sl": sl}
    if len(_CACHE) > 40:
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
    W, R = G.posicoes_de(o["res"], o["res"]["P"], o["sl"])
    return W * o["sl"] / capital, R


def negocios(d, capital=20000, sleeve_brl=None, hedge="inteiro", **kw):
    o = _roda(d, capital, 1, 0, 1, sleeve_brl, hedge, **_p(kw))
    return A.reescala_negocios(G.negocios_de(o["res"], o["sl"], o["res"]["P"]), o["sl"], capital)
