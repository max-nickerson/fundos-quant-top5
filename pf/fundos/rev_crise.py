"""
E9 Crise corporativa (queda > 20% / RJ) — versão pessoa física (R$ 20–50 mil), frente "revisita".

Mesa: ação que cai > 20% contra o Ibovespa em 3 pregões COM documento na CVM (fato relevante, comunicado) está digerindo notícia ruim
de verdade (rebaixamento, covenant, fraude, resultado desastroso, aumento de capital forçado). A pesquisa institucional mostrou que o
contrarian é armadilha (OOS −15% a.a.) e que o papel CONTINUA caindo (mediana −6,8% em 60 pregões; OOS −7,9%): investidor institucional
vende aos poucos (comitê de risco, mandato), o varejo compra a "promoção". Modo escolhido no ranking: CONTINUAÇÃO — vendo a descoberto no
fechamento seguinte ao 3º dia de queda, seguro 20 pregões, até 10 nomes (1/10 do capital), comprado em BOVA11 contra.
Opcional (rj=True): pedidos de recuperação judicial/fraude em FR também vendidos.

Rota PF: mesmo motor de aluguel do follow-on (rev_followon): BTC tomador na Clear/Rico, 0,5% por contrato + taxa ao doador (B3 real
quando publicada; senão modelo calibrado nas taxas B3 dez/2025–out/2026, onde queda forte e vol alta encarecem muito) + B3 20%;
papel sem doador / taxa acima do teto não é vendido. Garantia em Tesouro Selic rende CDI.
Pergunta da revisita: a taxa de aluguel REAL desses papéis em crise inviabiliza? (ver caderno e VARIANTES: o institucional usava 10% a.a.)
Diferenças em relação ao institucional: a exclusão de empresas com RJ/fraude usava documentos até 5 dias DEPOIS da queda (olhava à
frente) -> aqui só o passado (365 dias até a data); o regime 'dd_stop' do ranking é avaliado no IS (ver REGIME).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _util as U  # noqa: E402

C, pf = U.C, U.pf
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

import _ev_pf as M  # noqa: E402

NOME = "E9 Crise corporativa — continuação vendida (PF, aluguel real)"
TESE = ("Vendo a descoberto (BTC de PF) a ação que caiu > 20% em 3 pregões com fato na CVM: a notícia ruim é digerida devagar "
        "(institucional vende aos poucos, varejo compra a 'promoção'), por 20 pregões, comprado em BOVA11 contra; o custo é o aluguel "
        "caro dos papéis em crise")
BENCHMARK = "CDI"
INICIO, CORTE = "2014-06-01", "2021-01-01"
REGIME = "dd_stop"        # escolhido no IS (nenhum -6,1; dd_stop +0,1; risco_global -4,2; ibov_tendencia -5,0 pp a.a.), igual ao ranking:
                          # livro vendido em papel de crise perde em rajadas (squeeze/rebote coletivo) -> pausa 21 pregões após cair 5%
CUSTO_TROCA = .001
PARAMS = {"modo": "continuacao", "hold": 20, "rj": False, "n_max": 10, "hedge": 1.0, "teto_taxa": .30, "piso_taxa": 0.0}
GRADE = {"modo": ["contrarian", "continuacao"], "hold": [20, 60], "rj": [True, False]}
VIZINHANCA = {"hold": (14, 30)}
RANKING = ["E9 Crise corporativa (queda >20% / RJ)"]
INSTRUMENTOS = ("Clear/Rico/XP/BTG: venda a descoberto via aluguel tomador (BTC), ações inteiras, 1/10 do capital por nome; garantia e "
                "produto da venda em Tesouro Selic; hedge BOVA11 comprado. Modo contrarian (grade): compra à vista no fracionário")
APLICAVEL = True
MOTIVO = ("Aplicável operacionalmente, mas só nos papéis em crise que ainda têm doador; a taxa real desses papéis é de 5–50% a.a. "
          "(B3) e a corretora cobra 0,5% por contrato")
ALAVANCAGENS = [1, 1.5, 2]
MOTIVO_ALAV = ("Vendido bruto até L x 100% do capital; garantia ~125% coberta pelo produto da venda + capital até ~2x; 5x inviável "
               "(squeeze de papel em crise, ex. OIBR/LIGT, quebraria a conta)")
VARIANTES = {"sem regime": {"regime": "nenhum"}, "aluguel ao doador >= 10% a.a. (premissa institucional)": {"piso_taxa": .10},
             "só papéis com taxa <= 15% a.a.": {"teto_taxa": .15}, "sem hedge": {"hedge": 0.0},
             "inclui RJ/fraude vendidos": {"rj": True},
             "custos institucionais, sem arredondamento (validação)": {"custos": "inst"}}


def carrega():
    q, rj = M.eventos("queda"), M.eventos("rj")
    tk = set(M.eventos("opa").ticker) | set(M.eventos("oferta").ticker) | set(q.ticker) | set(rj.ticker) | set(M.eventos("leilao").ticker)
    pn = M.painel(tk, "eventos")
    pn = pn[pn.ticker.isin(set(q.ticker) | set(rj.ticker))]
    return {"queda": q[["data", "ticker", "queda", "rotulo"]], "rj": rj[["data", "ticker", "adv", "rotulo"]], "painel": pn,
            "btc": M.btc_b3(set(q.ticker) | set(rj.ticker))}


MULT_EVENTO = 2.0          # papel em crise = 2x o modelo (B3 dez/2025–out/2026: 1,6x na entrada, 2,0x no pico de 30 dias)
_CACHE = {}


def _largo(d):
    pn = d["painel"]
    k = (id(pn), len(pn))
    if k not in _CACHE:
        _CACHE.clear()
        _CACHE[k] = M.largo(pn)
    return _CACHE[k]


def _eventos(d, modo, rj):
    q, r = d["queda"].copy(), d["rj"]
    # exclui quedas de empresas com pedido de RJ/fraude nos 365 dias ANTERIORES (só passado; o institucional olhava +5 dias)
    m = q.merge(r[["data", "ticker"]].rename(columns={"data": "d_rj"}), on="ticker", how="left")
    ruim = (m.d_rj <= m.data) & (m.d_rj >= m.data - pd.Timedelta(days=365))
    excl = m[ruim][["data", "ticker"]].drop_duplicates()
    q = q.merge(excl.assign(_x=1), on=["data", "ticker"], how="left")
    q = q[q._x.isna()].drop(columns="_x")
    q["s"] = 1.0 if modo == "contrarian" else -1.0
    ev = pd.concat([q, r.assign(s=-1.0)]) if rj else q
    return ev.sort_values("data")


def _roda(d, capital=20000, custo_mult=1, lag=0, alavancagem=1, modo=PARAMS["modo"], hold=PARAMS["hold"], rj=PARAMS["rj"],
          n_max=PARAMS["n_max"], hedge=PARAMS["hedge"], teto_taxa=PARAMS["teto_taxa"], piso_taxa=PARAMS["piso_taxa"], custos="pf"):
    capital = 1e9 if custos == "inst" else capital            # validação: capital enorme, custos institucionais
    P, R, ADV = _largo(d)
    ev = _eventos(d, modo, rj)
    W = M.pesos_eventos(ev, int(hold), int(n_max))
    tk = list(W.columns)
    if custos == "inst":
        taxa = np.maximum(M.aluguel_inst(ADV[tk]), .10)
        ins = "inst"
    else:
        taxa = M.taxa_aluguel(ADV[tk], R[tk], P[tk], d["btc"], mult=MULT_EVENTO, piso=piso_taxa, teto=teto_taxa)
        ins = "bova"
    return M.simula(W, P[tk], R[tk], ADV[tk], capital, custo_mult, lag, alavancagem, taxa=taxa, hedge=hedge, instrumento=ins,
                    custos=custos, rotulos=ev)


def excesso(d, capital=20000, custo_mult=1, lag=0, regime=REGIME, alavancagem=1, **params):
    res = _roda(d, capital, custo_mult, lag, alavancagem, **{**PARAMS, **params})
    return M.com_regime(res, regime, CUSTO_TROCA * custo_mult, capital)[0]


def classes_ir(d, capital=20000, regime=REGIME, **params):
    res = _roda(d, capital, **{**PARAMS, **params})
    return M.com_regime(res, regime, CUSTO_TROCA, capital)[1]


def posicoes(d, **params):
    kw = {**PARAMS, **params}
    P, R, ADV = _largo(d)
    W = M.pesos_eventos(_eventos(d, kw["modo"], kw["rj"]), int(kw["hold"]), int(kw["n_max"]))
    return M.posicoes_de(W, R, extra=-kw["hedge"] * W.reindex(C.DIAS).fillna(0).sum(axis=1))


def negocios(d, capital=20000, **params):
    return M.negocios_de(_roda(d, capital, **{**PARAMS, **params}), capital)


if __name__ == "__main__":
    import time
    d = carrega()
    for kw in ({}, {"capital": 50000}, {"modo": "contrarian"}, {"hedge": 0.0}, {"piso_taxa": .1}, {"teto_taxa": .15}, {"rj": True},
               {"custos": "inst"}, {"regime": "dd_stop"}, {"regime": "risco_global"}, {"regime": "ibov_tendencia"}):
        t = time.time()
        e = excesso(d, **kw)
        print(kw, "IS %.2f OOS %.2f (%.1fs)" % (C.anual(e[INICIO:CORTE]), C.anual(e[CORTE:]), time.time() - t))
