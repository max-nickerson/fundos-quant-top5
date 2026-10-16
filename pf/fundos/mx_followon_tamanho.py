"""
mx_followon_tamanho — frente pf3_mecanismos. Mecanismo 3 (magnitude) aplicado ao follow-on vendido (rev_followon: +3,3 pp antes do IR,
com regime; sem regime −4,2 no IS — marginal e caro de alugar).

Inspiração: bb_dividendo_extra_aud (o efeito só aparece acima de um limiar de tamanho do evento) e b3_ofertas_varejo (o coordenador dá
desconto para colocar o papel).
Hipótese: a pressão de preço depois de um follow-on vem do papel NOVO que precisa ser absorvido (o "overhang": quem recebeu no rateio e
não queria tanto vende nas semanas seguintes; o estabilizador para de comprar). O efeito deve crescer com o tamanho da oferta em dias de
volume (valor da oferta / ADV de 60 pregões antes) — ofertas pequenas para o giro do papel não deixam marca.
Eventos: dataset aberto de ofertas da CVM (todas as ofertas de ações de empresa já listada: ICVM 400, ICVM 476 restrita e Res. 160,
primária/secundária/mista; mapeadas pelo CNPJ ao ticker), data = início da oferta (ICVM) ou registro (Res. 160), valor total da oferta.
É uma fonte diferente do rev_followon (que usa o 1º fato relevante sobre oferta, sem o tamanho).
Execução: o motor do rev_followon (_ev_pf.simula): venda a descoberto via aluguel real de PF (0,5% por contrato + taxa ao doador B3/modelo x3
no evento + B3), 1/n_max do capital por nome, BOVA11 comprado contra, decisão no fechamento da data, execução em t+1, segura `hold`
pregões; regime 'risco_global' herdado do rev_followon (escolhido lá no IS). Limiar (dias de volume) e hold escolhidos só no IS pelo maior IR.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

import _mx_comum as X  # noqa: E402
import _ev_pf as M  # noqa: E402
import rev_followon as RF  # noqa: E402

BB, B, C, pf, DIAS = X.BB, X.B, X.C, X.pf, X.DIAS

NOME = "Follow-on vendido só nas ofertas grandes para o giro do papel (magnitude)"
TESE = ("Vendo a descoberto (BTC de PF) a ação que faz oferta subsequente só quando a oferta vale >= W dias de volume (overhang grande), "
        "com BOVA11 comprado contra")
BENCHMARK = "CDI"
INICIO, CORTE = RF.INICIO, RF.CORTE
REGIME = RF.REGIME
CLASSE_IR = "acoes"
CUSTO_TROCA = .001
PARAMS = {"dias_min": 0.0, "hold": 20, "n_max": 5, "hedge": 1.0, "teto_taxa": .30}
GRADE = {"dias_min": [0.0, 5.0, 15.0, 30.0], "hold": [20, 40]}
VIZINHANCA = {"dias_min": (0.0, 8.0), "hold": (14, 30)}
INSTRUMENTOS = RF.INSTRUMENTOS
APLICAVEL = True
MOTIVO = RF.MOTIVO
ALAVANCAGENS = [1]
MOTIVO_ALAV = "vendido bruto até 100% do capital; squeeze de small cap"
_CACHE = {}


def carrega():
    of = B.ler("ofertas")
    of = of[(~of.inicial) & (of.tipo != "opa") & (of.valor > 0)].copy()
    mapa = B.ler("mapa_cnpj").groupby("cnpj").raiz.apply(list)
    P = B.painel("P")["P"]
    tk = []
    for cn, cl in zip(of.cnpj, of.classe):
        c = [r + cl for r in mapa.get(cn, []) if r + cl in P.columns]
        tk.append(c[0] if c else None)
    of["ticker"] = tk
    of = of.dropna(subset=["ticker"]).sort_values("data").drop_duplicates(["ticker", "data"])
    pn = B.painel("P", "R", "V")
    cols = sorted(set(of.ticker))
    long = pd.concat([pn[k][cols].stack().rename(k) for k in ("P", "R", "V")], axis=1).reset_index()
    long.columns = ["data", "ticker", "P", "R", "V"]
    return {"of": of[["data", "ticker", "valor", "nome", "fonte"]].reset_index(drop=True), "painel": long,
            "btc": M.btc_b3(set(of.ticker)), "etf": M.etfs()}


def _eventos(d, dias_min):
    pn = d["painel"]
    k = (id(pn), len(pn))
    if k not in _CACHE:
        _CACHE.clear()
        _CACHE[k] = M.largo(pn)
    P, R, ADV = _CACHE[k]
    of = d["of"]
    i = DIAS.searchsorted(pd.DatetimeIndex(of.data))
    ok = i < len(DIAS)
    of, i = of[ok], i[ok]
    adv = np.array([ADV[t].iat[max(j - 1, 0)] if t in ADV else np.nan for t, j in zip(of.ticker, i)])
    dias = of.valor.values / adv
    sel = (dias >= dias_min) & (adv >= 1e6)
    ev = pd.DataFrame({"data": DIAS[i[sel]], "ticker": of.ticker.values[sel], "adv": adv[sel], "s": -1.0,
                       "rotulo": [f"oferta {v / 1e6:.0f} mi = {x:.1f} dias de volume" for v, x in zip(of.valor.values[sel], dias[sel])]})
    return ev


def roda(d, capital=20000, custo_mult=1, lag=0, alavancagem=1, dias_min=0.0, hold=20, n_max=5, hedge=1.0, teto_taxa=.30):
    ev = _eventos(d, dias_min)
    dd = {"oferta": ev, "painel": d["painel"], "btc": d["btc"], "etf": d["etf"]}
    res = RF._roda(dd, capital, custo_mult, lag, alavancagem, hold=int(hold), n_max=int(n_max), hedge=hedge, teto_taxa=teto_taxa)
    return res


def excesso(d, capital=20000, custo_mult=1, lag=0, regime=REGIME, alavancagem=1, **params):
    res = roda(d, capital, custo_mult, lag, alavancagem, **{**PARAMS, **params})
    return M.com_regime(res, regime, CUSTO_TROCA * custo_mult, capital)[0]


def classes_ir(d, capital=20000, regime=REGIME, **params):
    res = roda(d, capital, **{**PARAMS, **params})
    return M.com_regime(res, regime, CUSTO_TROCA, capital)[1]


def posicoes(d, **params):
    kw = {**PARAMS, **params}
    ev = _eventos(d, kw["dias_min"])
    P, R, ADV = _CACHE[next(iter(_CACHE))]
    W = M.pesos_eventos(ev, int(kw["hold"]), int(kw["n_max"]))
    return M.posicoes_de(W, R, extra=-kw["hedge"] * W.reindex(DIAS).fillna(0).sum(axis=1))


def negocios(d, capital=20000, **params):
    return M.negocios_de(roda(d, capital, **{**PARAMS, **params}), capital)


if __name__ == "__main__":
    X.escolhe_is(sys.modules[__name__], carrega())
