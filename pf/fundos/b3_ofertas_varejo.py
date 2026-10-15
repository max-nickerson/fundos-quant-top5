"""
Ofertas públicas de ações com tranche de varejo (IPO e follow-on): comprar NA OFERTA e vender no primeiro pregão / em poucos dias.

Mesa: o coordenador precifica a oferta com desconto para garantir a demanda institucional (IPO: underpricing; follow-on: desconto sobre o
fechamento da véspera). O institucional grande recebe rateio; a pessoa física entra pela tranche de varejo (10-20% da oferta, pedido de
reserva de R$ 3 mil a R$ 1 milhão) ao MESMO preço, sem corretagem nem emolumentos na compra. É um prêmio que só existe em lote pequeno:
o fundo de R$ 1 bilhão não consegue usar a tranche de varejo, e quem pede R$ 3-10 mil costuma receber tudo (ou a parcela igualitária
do rateio) mesmo nas ofertas disputadas.
Dados: dataset aberto da CVM de ofertas (ICVM 400 com registro até 2022 = ofertas com tranche de varejo; Res. CVM 160 "Público Geral"
desde 2023): preço por ação, data de início (anúncio de início = 1º pregão após a precificação), nº de pessoas físicas e quantidade
alocada a elas. Alocação simulada: pedido de `pedido` R$ (até 25% do capital); Res. 160: recebido = min(pedido, `fator` x alocação
MÉDIA por pessoa física da oferta); ICVM 400 (sem o dado): recebe `rateio` (30%) do pedido se a ação estreou acima do preço da oferta e
100% se estreou abaixo — maldição do vencedor de Rock (1986), usada só para piorar o resultado. Venda no fechamento do `k`-ésimo pregão,
pagando meio spread real + emolumentos. O dinheiro sai do CDI 2 pregões antes do 1º pregão (liquidação da oferta) até a venda.
Seleção (decidida ANTES do preço, como na reserva): 'todos', 'ipo' (Oferta_Inicial) ou 'follow' (empresa já listada).
Viés conhecido: ofertas canceladas não aparecem (não havia o que comprar); ofertas de empresas sem ticker no COTAHIST ficam de fora.
"""
import numpy as np
import pandas as pd

import b3_base as B

C, pf = B.C, B.pf

NOME = "Ofertas de ações pela tranche de varejo (PF)"
TESE = ("Peço R$ 3-10 mil em toda oferta de ações com tranche de varejo e vendo no 1º pregão (ou em k pregões): o coordenador dá desconto "
        "para fechar o livro institucional e o pequeno pega o mesmo preço sem corretagem, recebendo tudo ou a parcela igualitária do rateio")
BENCHMARK = "CDI"
INICIO, CORTE = "2014-01-01", "2021-01-01"
REGIME = "nenhum"
CUSTO_TROCA = .001
PARAMS = {"tipo": "todos", "k": 1, "pedido": 5000.0, "fator": .5, "rateio": .3}
GRADE = {"tipo": ["todos", "ipo", "follow"], "k": [1, 5, 21]}
VIZINHANCA = {"k": (1, 10), "pedido": (3000.0, 10000.0), "fator": (.25, 1.0), "rateio": (.1, .6)}
INSTRUMENTOS = [{"onde": "XP/BTG/Itaú/Clear/Rico/Inter (pedido de reserva na oferta)", "ticker": "IPO/follow-on ICVM 400 / Res. 160 público geral",
                 "lote": "pedido mínimo ~R$ 1-3 mil", "custo": "compra sem custo na oferta; venda: emolumentos 0,03% + meio spread real"}]
APLICAVEL = True
MOTIVO = "qualquer corretora coordenadora/consorciada aceita pedido de reserva de pessoa física; desde 2023 quase só ofertas restritas (sem varejo)"
ALAVANCAGENS = [1]
MOTIVO_ALAV = "o pedido já é limitado pelo rateio; pedir mais que o capital (alavancar) é proibido/arriscado (a corretora bloqueia o saldo)"
_RES = {}


def carrega():
    d = B.painel("P", "R", "V", "BID", "ASK")
    d["HS"] = B.meio_spread(d["BID"], d["ASK"], d["V"].fillna(0))
    of = B.ler("ofertas")
    of = of[of.varejo & (of.tipo != "opa")].copy()
    mapa = B.ler("mapa_cnpj").groupby("cnpj").raiz.apply(list)
    tk = []
    for cn, cl in zip(of.cnpj, of.classe):
        c = [r + cl for r in mapa.get(cn, []) if r + cl in d["P"].columns]
        tk.append(c[0] if c else None)
    of["ticker"] = tk
    of = of.dropna(subset=["ticker"]).drop_duplicates(["ticker", "data", "preco"])          # oferta mista aparece 2x (primária + secundária)
    d["ofertas"] = of[["data", "ticker", "preco", "nr_pf", "qtd_pf", "inicial", "nome", "fonte", "tipo"]].reset_index(drop=True)
    return d


def roda(d, capital=20000, custo_mult=1, lag=0, tipo="todos", k=1, pedido=5000.0, fator=.5, rateio=.3):
    key = (id(d), capital, custo_mult, lag, tipo, k, pedido, fator, rateio)
    if key in _RES:
        return _RES[key]
    P, R, HS = d["P"], d["R"].fillna(0), d["HS"]
    idx = B.DIAS
    of = d["ofertas"]
    if tipo == "ipo":
        of = of[of.inicial]
    elif tipo == "follow":
        of = of[~of.inicial]
    k = max(int(round(k)), 1)
    pnl = pd.Series(0.0, index=idx)
    cdi_p = pd.Series(0.0, index=idx)
    vend = pd.Series(0.0, index=idx)
    W = pd.DataFrame(0.0, index=idx, columns=sorted(of.ticker.unique()))
    neg = []
    usado = {}
    for _, o in of.sort_values("data").iterrows():
        t = o.ticker
        if t not in P:
            continue
        p = P[t]
        i0 = idx.searchsorted(o.data)
        if "rcvm160" in str(o.fonte):
            i0 += 1                                                    # registro = dia da precificação; 1º pregão no dia seguinte
        neg_dias = np.flatnonzero(p.iloc[i0:i0 + 6].notna().values)
        if not len(neg_dias):
            continue
        i1 = i0 + neg_dias[0] + lag                                    # lag: venda atrasada (a compra é na oferta)
        i2 = min(i1 + k - 1, len(idx) - 1)
        if not p.iloc[i1] > 0 or i1 >= len(idx):
            continue
        media_pf = o.qtd_pf * o.preco / o.nr_pf if o.nr_pf and o.nr_pf > 0 and o.qtd_pf > 0 else np.nan
        x = min(pedido * capital / 20000, .25 * capital)
        if np.isnan(media_pf):
            # ICVM 400 sem dado de alocação: maldição do vencedor (Rock, 1986) — na oferta que estreia em alta o varejo é rateado
            # (recebe `rateio` do pedido); na que estreia em queda recebe tudo. Usa o resultado só para PIORAR a alocação (conservador).
            aloc = x * (rateio if p.iloc[i1] > o.preco else 1.0)
        else:
            aloc = min(x, fator * media_pf)
        n = np.floor(aloc / o.preco)
        if n < 1:
            continue
        # dinheiro já comprometido em outra oferta no mesmo período (capital limitado)
        ocup = sum(v for (a, b), v in usado.items() if a <= i1 <= b)
        if ocup + n * o.preco > capital:
            continue
        v0 = n * o.preco
        usado[(i1 - 2, i2)] = v0
        val = v0 * p.iloc[i1] / o.preco
        pnl.iloc[i1] += val - v0
        for j in range(i1 + 1, i2 + 1):
            g = val * R[t].iloc[j]
            pnl.iloc[j] += g
            val += g
        c = val * (B.EMOL + HS[t].iloc[i2]) * custo_mult
        pnl.iloc[i2] -= c
        vend.iloc[i2] += val
        cdi_p.iloc[max(i1 - 2, 0):i2 + 1] += v0 * C.CDI.reindex(idx).iloc[max(i1 - 2, 0):i2 + 1].values
        W.iloc[i1 - 1:i2, W.columns.get_loc(t)] += v0 / capital
        neg.append({"ativo": t, "lado": 1, "entrada": idx[i1], "saida": idx[i2], "dias": i2 - i1 + 1, "retorno_%": (val - c) / v0 * 100 - 100,
                    "contrib_pp": (val - c - v0) / capital * 100, "valor": v0, "ganho": val - c - v0, "desconto_1o_dia_%": (p.iloc[i1] / o.preco - 1) * 100,
                    "rotulo": f"{o.nome[:28]} {'IPO' if o.inicial else 'follow-on'} a R$ {o.preco:.2f}"})
    e = (pnl - cdi_p) / capital
    res = {"e": e, "pnl": pnl, "custo": pd.Series(0.0, index=idx), "cdi_perdido": cdi_p, "vendas": vend, "W": W,
           "negocios": pd.DataFrame(neg)}
    if len(_RES) > 64:
        _RES.clear()
    _RES[key] = res
    return res


def excesso(d, capital=20000, custo_mult=1, lag=0, regime=REGIME, alavancagem=1, **params):
    e = roda(d, capital, custo_mult, lag, **{**PARAMS, **params})["e"] * alavancagem
    return C.aplica_regime(e, regime, CUSTO_TROCA * custo_mult)


def classes_ir(d, capital=20000, **params):
    return B.classes_acoes(roda(d, capital, **{**PARAMS, **params}))


def posicoes(d, capital=20000, **params):
    W = roda(d, capital, **{**PARAMS, **params})["W"]
    return W, d["R"].reindex(index=B.DIAS, columns=W.columns).fillna(0).sub(B.CDI, axis=0)


def negocios(d, capital=20000, **params):
    return roda(d, capital, **{**PARAMS, **params})["negocios"]
