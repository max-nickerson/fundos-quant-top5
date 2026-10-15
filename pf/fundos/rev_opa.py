"""
E1 Arbitragem de OPA e troca de controle — versão pessoa física (R$ 20–50 mil), frente "revisita".

Mesa: quando sai o fato relevante de uma OPA (fechamento de capital, saída de segmento, OPA por alienação de controle / tag along), o alvo
continua negociando ABAIXO do preço da oferta: o mercado cobra prazo (3–12 meses até o leilão), risco de a oferta cair e o custo de
capital de quem carrega. No Brasil a OPA é regulada (Res. CVM 85, laudo, tag along de 80–100%) e raramente cai — o prêmio costuma ser
maior que o risco. Compro o alvo no fechamento seguinte ao FR (Data_Entrega no IPE/CVM) se o spread até o preço da oferta for >= smin e
<= 30%, e saio quando o spread fecha (preço >= 99,5% da oferta), vendendo NO LEILÃO ao preço da oferta (FR de resultado/realização do
leilão), na deslistagem (papel parado 5 pregões -> recebe o último preço) ou após 250 pregões.
Preço da oferta lido do PDF do FR pela pesquisa institucional (quant/fundos/ideias_eventos_br.py: valor "R$ x" perto de "por ação",
aceito só entre 0,9x e 1,5x o preço da própria ação — garante que a companhia que publicou é o ALVO); só ofertas em dinheiro (tipo='opa').

Rota PF: Clear/Rico, ações inteiras (fracionário), 1/8 do capital por OPA (R$ 2,5 mil com R$ 20 mil); a PF se habilita no leilão pela
corretora e vende ao preço da oferta. Edge de capital pequeno: alvos ilíquidos (ADV de R$ 0,5–5 mi) em que um lote de R$ 2–6 mil entra e
sai sem mover o preço; o institucional pagava 40–80 bps de impacto e não conseguia escalar. Variante: ADV >= R$ 100 mil (mais ilíquidos).
Hedge: o ranking usa 0,5 x Ibovespa; na PF isso é BOVA11 vendido via aluguel (0,5% por contrato + 0,88% a.a. + B3) — decidido no IS (GRADE).
IR: a venda no leilão é alienação em bolsa; com R$ 20–50 mil quase todo mês fica abaixo de R$ 20 mil de vendas -> isento.
Diferenças em relação ao institucional: leilão só pelos FRs de RESULTADO/REALIZAÇÃO/CONCLUSÃO do leilão (o institucional pegava o 1º
documento com "leilão", inclusive "procedimentos operacionais" semanas antes); posição em quantidade fixa (sem rebalancear diário);
sem o regime 'selic_corte' do ranking (não há razão econômica para OPA depender do ciclo da Selic) -> REGIME 'nenhum'.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _util as U  # noqa: E402

C, pf = U.C, U.pf
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

import _ev_pf as M  # noqa: E402

NOME = "E1 Arbitragem de OPA e troca de controle (PF)"
TESE = ("Compro no fracionário o alvo de OPA em dinheiro quando ainda negocia >= smin abaixo do preço da oferta (FR na CVM) e vendo no "
        "leilão ao preço da oferta: o prêmio de prazo/risco cobrado pelo mercado é maior que o risco real de uma OPA regulada; lote pequeno "
        "em alvo ilíquido é onde o institucional não escala")
BENCHMARK = "CDI"
INICIO, CORTE = "2014-06-01", "2021-01-01"
REGIME = "nenhum"
CUSTO_TROCA = .001
PARAMS = {"smin": .02, "hedge": 0.0, "hold": 250, "adv_min": 5e5, "n_max": 8}
GRADE = {"smin": [.02, .05], "hedge": [0.0, .5]}
VIZINHANCA = {"smin": (.01, .05), "hold": (150, 350)}
RANKING = ["E1 Arbitragem de OPA e troca de controle"]
INSTRUMENTOS = ("Clear/Rico (corretagem zero): ação-alvo da OPA no fracionário/lote padrão, 1/8 do capital por OPA; habilitação no leilão "
                "via corretora; caixa em Tesouro Selic. Hedge opcional: BOVA11 vendido via aluguel (0,5% por contrato + 0,88% a.a. + B3)")
APLICAVEL = True
MOTIVO = ("Aplicável: compra de ação à vista em lote pequeno + venda no leilão (PF participa via corretora). Livro pequeno: em média "
          "~1 OPA aberta (6–12% do capital); o resto rende CDI")
ALAVANCAGENS = [1, 1.5, 2, 5]
MOTIVO_ALAV = ("Alavancagem = tamanho por OPA x L (1/8 -> 5/8 com 5x). Como raramente há mais de 2 OPAs abertas, até 2x cabe no capital; "
               "acima do capital o excedente paga termo CDI + 4% a.a. (premissa; termo em papel ilíquido pode não ser aceito)")
VARIANTES = {"hedge 0,5 BOVA11 alugado": {"hedge": .5}, "ilíquidos: ADV >= R$ 100 mil": {"adv_min": 1e5},
             "4 OPAs por vez (1/4 do capital)": {"n_max": 4},
             "custos institucionais, sem arredondamento (validação)": {"custos": "inst"}}
_RX_LEILAO = "resultado|realizacao|realizado|conclusao"


def carrega():
    ev = M.eventos("opa")
    lz = M.eventos("leilao")
    tk = set(M.eventos("opa").ticker) | set(M.eventos("oferta").ticker) | set(M.eventos("queda").ticker) | set(M.eventos("rj").ticker) \
        | set(lz.ticker)
    pn = M.painel(tk, "eventos")
    pn = pn[pn.ticker.isin(set(ev.ticker))]
    return {"opa": ev, "leilao": lz, "painel": pn}


_CACHE = {}


def _largo(d):
    pn = d["painel"]
    k = (id(pn), len(pn))
    if k not in _CACHE:
        _CACHE.clear()
        _CACHE[k] = M.largo(pn)
    return _CACHE[k]


def _pesos(d, smin, hold, adv_min, n_max, tipo="opa"):
    """Pesos decididos no fechamento de t + ajustes de retorno do dia do leilão (vende ao preço da oferta). Tudo só com dados até t."""
    P, R, ADV = _largo(d)
    ev = d["opa"]
    ev = ev[(ev.spread >= smin) & (ev.spread <= .30) & (ev.adv >= adv_min)]
    if tipo == "opa":
        ev = ev[ev.dinheiro.astype(bool)]
    lz = d["leilao"]
    lz = lz[lz.rotulo.str.contains(_RX_LEILAO, regex=True)]
    idx = C.DIAS
    tks = sorted(ev.ticker.unique())
    A = pd.DataFrame(0.0, index=idx, columns=tks)
    Pf = P.reindex(columns=tks).ffill(limit=5)
    aj = {}
    for _, r in ev.iterrows():
        i = idx.searchsorted(r.data)
        if i >= len(idx):
            continue
        fim = min(i + int(hold), len(idx))
        pp = Pf[r.ticker].to_numpy()
        fecha = np.flatnonzero(pp[i + 1:fim] >= r.oferta * .995)              # spread fechou: decide sair nesse fechamento
        if len(fecha):
            fim = i + 1 + fecha[0]
        z = lz[(lz.ticker == r.ticker) & (lz.data > r.data)].data
        if len(z):
            j = idx.searchsorted(z.iloc[0])                                   # resultado do leilão publicado em j: vendeu ao preço da oferta
            if i < j <= fim and pp[j - 1] > 0:
                fim = j - 1
                aj[(idx[j], r.ticker)] = max(r.oferta / pp[j - 1] - 1, -.5)
                for k in range(j + 1, min(j + 11, len(idx))):                 # já vendeu no leilão: nada mais muda até o encerramento
                    aj[(idx[k], r.ticker)] = 0.0
        A.iloc[i:fim, A.columns.get_loc(r.ticker)] = 1.0
    W = A / n_max
    W = W.div(np.maximum(W.sum(axis=1), 1), axis=0)
    return W, aj, ev


def _roda(d, capital=20000, custo_mult=1, lag=0, alavancagem=1, smin=PARAMS["smin"], hedge=PARAMS["hedge"], hold=PARAMS["hold"],
          adv_min=PARAMS["adv_min"], n_max=PARAMS["n_max"], custos="pf"):
    capital = 1e9 if custos == "inst" else capital            # validação: capital enorme, custos institucionais
    P, R, ADV = _largo(d)
    W, aj, ev = _pesos(d, smin, hold, adv_min, n_max)
    tk = list(W.columns)
    return M.simula(W, P[tk], R[tk], ADV[tk], capital, custo_mult, lag, alavancagem, r_ajuste=aj, hedge=hedge,
                    instrumento="inst" if custos == "inst" else "bova", custos=custos, rotulos=ev)


def excesso(d, capital=20000, custo_mult=1, lag=0, regime=REGIME, alavancagem=1, **params):
    e = _roda(d, capital, custo_mult, lag, alavancagem, **{**PARAMS, **params})["excesso"]
    return C.aplica_regime(e, regime, CUSTO_TROCA * custo_mult)


def classes_ir(d, capital=20000, **params):
    return _roda(d, capital, **{**PARAMS, **params})["classes"]


def posicoes(d, **params):
    kw = {**PARAMS, **params}
    P, R, ADV = _largo(d)
    W, aj, ev = _pesos(d, kw["smin"], kw["hold"], kw["adv_min"], kw["n_max"])
    return M.posicoes_de(W, R)


def negocios(d, capital=20000, **params):
    return M.negocios_de(_roda(d, capital, **{**PARAMS, **params}), capital)


if __name__ == "__main__":
    import time
    d = carrega()
    for kw in ({}, {"capital": 50000}, {"hedge": .5}, {"smin": .05}, {"adv_min": 1e5}, {"custos": "inst"},
               {"custos": "inst", "hedge": .5}):
        t = time.time()
        e = excesso(d, **kw)
        print(kw, "IS %.2f OOS %.2f (%.1fs)" % (C.anual(e[INICIO:CORTE]), C.anual(e[CORTE:]), time.time() - t))
    ng = negocios(d)
    print(ng.sort_values("contrib_pp").drop(columns=["rotulo"], errors="ignore").to_string()[:6000])
