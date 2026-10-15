"""
E3 Follow-on vendido — versão pessoa física (R$ 20–50 mil), frente "revisita".

Mesa: a empresa que anuncia/precifica oferta subsequente de ações (follow-on primário ou secundário) vende papel quando acha caro; o
controlador/fundo de PE que vende na secundária sabe mais que o mercado; e a oferta adiciona papel que os coordenadores distribuem com
desconto -> o preço anda de lado/para baixo por semanas (estudo de evento da pesquisa: -3,0% vs Ibovespa em 60 pregões, t = -2,3; OOS -6%).
Vendo a descoberto no fechamento seguinte ao 1º FR de oferta da empresa em 90 dias (Data_Entrega no IPE/CVM), seguro 20 pregões, até
5 nomes (1/5 do capital cada), e compro Ibovespa (BOVA11) contra — fico só com o "efeito oferta".

Rota PF (Clear/Rico, BTC): venda a descoberto com aluguel tomador; o produto da venda + garantia ficam em Tesouro Selic (rende CDI).
Custo REAL do aluguel de PF: corretora 0,5% do volume por contrato aberto/renovado + taxa ao doador do papel + B3 (20% da taxa, piso
0,025%, teto 0,70% a.a.). Taxa ao doador: modelo por liquidez/queda/vol calibrado nas taxas REAIS da B3 (BDI 04-2 "Empréstimos
registrados", 70 datas de dez/2025 a out/2026, ~600 ações) e, quando há taxa B3 publicada até a data, a própria taxa do papel
(ver _ev_pf.taxa_aluguel). Papel sem doador (sem saldo/negócio de aluguel ou taxa estimada > teto) NÃO é vendido (indisponibilidade).
Recall: o doador pode pedir as ações de volta; modelado como custo de renovação (0,5% de novo a cada 21 pregões) — o risco de recompra
forçada num squeeze não é modelado além disso (ver caderno).
Hedge: BOVA11 comprado em cotas inteiras (sem aluguel; classe ETF 15%). Variante: SMAL11 (o fator tamanho custou −9 pp/ano em 2021–22
na auditoria institucional).
IR: ganho do vendido é apurado na recompra; a venda entra no limite de R$ 20 mil no mês da recompra (premissa) — com 5 nomes de R$ 4 mil
(20k) quase todo mês fica isento; com 50k raramente.
Diferenças em relação ao institucional: o ranking usava regime 'credito_ok' (não existe aqui; testado no IS: ver REGIME); aluguel
1/3/8% por ADV -> taxa real/estimada + 0,5% por contrato; ações inteiras; posição fixa em quantidade.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _util as U  # noqa: E402

C, pf = U.C, U.pf
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

import _ev_pf as M  # noqa: E402

NOME = "E3 Follow-on vendido (PF, aluguel real)"
TESE = ("Vendo a descoberto (BTC de PF) a ação que anuncia oferta subsequente — emissor e acionista vendedor sabem mais e vendem caro, e "
        "a oferta adiciona papel com desconto — por 20 pregões, comprado em BOVA11 contra; o custo dominante é o aluguel real do papel")
BENCHMARK = "CDI"
INICIO, CORTE = "2014-06-01", "2021-01-01"
REGIME = "risco_global"   # escolhido no IS (nenhum -4,2; risco_global -2,8; dd_stop -3,5; ibov_tendencia -4,5 pp a.a.): análogo do
                          # 'credito_ok' do ranking — em estresse de crédito o aluguel some/encarece e as small caps emissoras disparam no
                          # rebote (squeeze); fora do risco-on o livro fica em caixa
CUSTO_TROCA = .001
PARAMS = {"hold": 20, "n_max": 5, "hedge": 1.0, "hedge_etf": "bova", "teto_taxa": .30, "piso_taxa": 0.0}
GRADE = {"hold": [20, 40, 60], "n_max": [5, 10]}
VIZINHANCA = {"hold": (14, 30)}
RANKING = ["E3 Follow-on vendido"]
INSTRUMENTOS = ("Clear/Rico/XP/BTG: venda a descoberto via aluguel tomador (BTC), ações inteiras, 1/5 do capital por nome; garantia e "
                "produto da venda em Tesouro Selic; hedge BOVA11 comprado (cotas inteiras). Aluguel: 0,5% do volume por contrato + taxa "
                "ao doador (B3/estimada) + B3 20% da taxa")
APLICAVEL = True
MOTIVO = ("Aplicável operacionalmente (PF aluga e vende a descoberto na B3), mas o edge depende da taxa de aluguel dos emissores; os "
          "papéis mais lucrativos (oferta de empresa alavancada) são os de aluguel caro/indisponível")
ALAVANCAGENS = [1, 1.5, 2]
MOTIVO_ALAV = ("Vendido bruto = L x 100% do capital: a garantia exigida (~125% do vendido, segundo as corretoras) é coberta pelo produto da "
               "venda + capital em Tesouro Selic até ~2x; 5x não passa na garantia e o risco de squeeze (+50% num nome) quebraria a conta")
VARIANTES = {"sem regime": {"regime": "nenhum"}, "hedge SMAL11": {"hedge_etf": "smal"}, "sem hedge": {"hedge": 0.0},
             "aluguel ao doador >= 20% a.a. (auditoria)": {"piso_taxa": .20},
             "só papéis com taxa <= 15% a.a.": {"teto_taxa": .15},
             "custos institucionais, sem arredondamento (validação)": {"custos": "inst"}}


def carrega():
    ev = M.eventos("oferta")
    tk = set(M.eventos("opa").ticker) | set(M.eventos("oferta").ticker) | set(M.eventos("queda").ticker) | set(M.eventos("rj").ticker) \
        | set(M.eventos("leilao").ticker)
    pn = M.painel(tk, "eventos")
    pn = pn[pn.ticker.isin(set(ev.ticker))]
    return {"oferta": ev[["data", "ticker", "adv", "rotulo"]], "painel": pn, "btc": M.btc_b3(set(ev.ticker)), "etf": M.etfs()}


MULT_EVENTO = 3.0          # taxa de papel em oferta = 3x o modelo (B3 dez/2025–out/2026: 2,2x na entrada, 3,8x no pico de 30 dias)
_CACHE = {}


def _largo(d):
    pn = d["painel"]
    k = (id(pn), len(pn))
    if k not in _CACHE:
        _CACHE.clear()
        _CACHE[k] = M.largo(pn)
    return _CACHE[k]


def _pesos(d, hold, n_max):
    ev = d["oferta"].assign(s=-1.0)
    return M.pesos_eventos(ev, hold, n_max), ev


def _roda(d, capital=20000, custo_mult=1, lag=0, alavancagem=1, hold=PARAMS["hold"], n_max=PARAMS["n_max"], hedge=PARAMS["hedge"],
          hedge_etf=PARAMS["hedge_etf"], teto_taxa=PARAMS["teto_taxa"], piso_taxa=PARAMS["piso_taxa"], custos="pf"):
    capital = 1e9 if custos == "inst" else capital            # validação: capital enorme, custos institucionais
    P, R, ADV = _largo(d)
    W, ev = _pesos(d, int(hold), int(n_max))
    tk = list(W.columns)
    if custos == "inst":
        taxa = M.aluguel_inst(ADV[tk])
        ins, px = "inst", None
    else:
        taxa = M.taxa_aluguel(ADV[tk], R[tk], P[tk], d["btc"], mult=MULT_EVENTO, piso=piso_taxa, teto=teto_taxa)
        ins, px = ("bova", None) if hedge_etf == "bova" else ("serie", d["etf"]["SMAL11"])
    return M.simula(W, P[tk], R[tk], ADV[tk], capital, custo_mult, lag, alavancagem, taxa=taxa, hedge=hedge, instrumento=ins,
                    custos=custos, rotulos=ev, hedge_px=px)


def excesso(d, capital=20000, custo_mult=1, lag=0, regime=REGIME, alavancagem=1, **params):
    res = _roda(d, capital, custo_mult, lag, alavancagem, **{**PARAMS, **params})
    return M.com_regime(res, regime, CUSTO_TROCA * custo_mult, capital)[0]


def classes_ir(d, capital=20000, regime=REGIME, **params):
    res = _roda(d, capital, **{**PARAMS, **params})
    return M.com_regime(res, regime, CUSTO_TROCA, capital)[1]


def posicoes(d, **params):
    kw = {**PARAMS, **params}
    P, R, ADV = _largo(d)
    W, ev = _pesos(d, int(kw["hold"]), int(kw["n_max"]))
    return M.posicoes_de(W, R, extra=-kw["hedge"] * W.reindex(C.DIAS).fillna(0).sum(axis=1))


def negocios(d, capital=20000, **params):
    return M.negocios_de(_roda(d, capital, **{**PARAMS, **params}), capital)


if __name__ == "__main__":
    import time
    d = carrega()
    for kw in ({}, {"capital": 50000}, {"hedge_etf": "smal"}, {"hedge": 0.0}, {"piso_taxa": .2}, {"teto_taxa": .15},
               {"custos": "inst"}, {"regime": "risco_global"}, {"regime": "ibov_tendencia"}, {"regime": "dd_stop"}):
        t = time.time()
        e = excesso(d, **kw)
        print(kw, "IS %.2f OOS %.2f (%.1fs)" % (C.anual(e[INICIO:CORTE]), C.anual(e[CORTE:]), time.time() - t))
