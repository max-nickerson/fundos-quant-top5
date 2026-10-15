"""
OPA até o LEILÃO: comprar o alvo depois do fato relevante e entregar no leilão (preço da oferta corrigido/melhorado), em lote pequeno.

Mesa: na OPA de fechamento de capital / saída do Novo Mercado / alienação de controle, o preço do fato relevante é só o PISO. Até o
leilão (3-12 meses) o preço costuma ser corrigido pela Selic (laudo/regulamento), melhorado para atingir o quórum de 2/3 dos
acionistas livres, ou disputado por um concorrente (Eletropaulo 2018: R$ 28 -> R$ 45,22). O arbitrador institucional sai quando o
"spread" fecha; a pessoa física com R$ 2-6 mil por OPA pode simplesmente ENTREGAR no leilão — a corretora habilita o cliente — e
receber o preço final, inclusive em alvos ilíquidos (ADV de R$ 20 mil) em que o fundo grande não monta posição.
Dados: preço por ação lido do texto do fato relevante (pesquisa institucional E1: valor "R$ x" perto de "por ação"/"preço da oferta",
aceito entre 0,9x e 1,5x o preço da ação, só ofertas em dinheiro) com a DATA DE ENTREGA no IPE/CVM; LEILÃO = negócio no mercado
de leilão do COTAHIST (TPMERC 017, ticker com sufixo L) — o preço e a data reais do leilão (a data é pública no edital semanas antes).
Regras: compra no fechamento de t+1+lag (meio spread real) se preço <= oferta x (1 - smin); sai (a) no leilão ao preço do leilão;
(b) no modo 'spread', quando o preço passa de 99,5% da oferta (vende na oferta de compra real); (c) papel parado 30 pregões: sai pelo
último preço; (d) após `prazo` pregões, vende pela oferta de compra. R$ `por_opa` por OPA (até o caixa).
IR: alienação em bolsa (o leilão é pregão especial): isento se as vendas do mês <= R$ 20 mil — quase sempre com R$ 2-6 mil por OPA.
Diferença para rev_opa (frente revisita): aqui a saída é o leilão REAL (TPMERC 017) com o preço final (corrigido/melhorado), sem piso
de liquidez (ADV >= R$ 20 mil) e com a opção de segurar até o leilão em vez de sair no fechamento do spread.
"""
import numpy as np
import pandas as pd

import b3_base as B

C, pf = B.C, B.pf

NOME = "OPA até o leilão em lote pequeno (PF)"
TESE = ("Compro o alvo de OPA em dinheiro depois do fato relevante e entrego no leilão: o preço do FR é piso (Selic, melhora para o quórum, "
        "concorrente); R$ 2-6 mil cabem até em alvos que giram R$ 20 mil/dia")
BENCHMARK = "CDI"
INICIO, CORTE = "2014-03-01", "2021-01-01"
REGIME = "nenhum"
CUSTO_TROCA = .001
PARAMS = {"smin": 0.0, "modo": "leilao", "prazo": 300, "adv_min": 2e4, "por_opa": 3000.0}
GRADE = {"smin": [-.03, 0.0, .03], "modo": ["leilao", "spread"]}
VIZINHANCA = {"smin": (-.04, .05), "prazo": (150, 400)}
INSTRUMENTOS = [{"onde": "Clear/Rico/XP/BTG (à vista + habilitação no leilão de OPA pela corretora)", "ticker": "alvos de OPA em dinheiro",
                 "lote": "1 ação", "custo": "emolumentos 0,03% + meio spread real na compra; leilão sem spread"}]
APLICAVEL = True
MOTIVO = "pessoa física se habilita no leilão pela corretora (formulário + ações na custódia até a véspera); OPAs são poucas (5-10/ano)"
ALAVANCAGENS = [1]
MOTIVO_ALAV = "o limite é o nº de OPAs, não o capital; o caixa ocioso rende CDI"
_RES = {}


def carrega():
    d = B.painel("P", "R", "V", "BID", "ASK")
    d["HS"] = B.meio_spread(d["BID"], d["ASK"], d["V"].fillna(0))
    ev = B.ler("opa_eventos")
    ev = ev[ev.dinheiro & ~ev.rotulo.str.contains("leilao|liquidacao|sucesso|resultado|encerramento", regex=True)]   # FR depois do leilão
    d["ev"] = ev[["data", "ticker", "oferta", "p0", "rotulo"]].copy()
    lz = B.ler("leiloes_017")
    d["leilao"] = lz[["data", "base", "fech", "volume"]].rename(columns={"base": "ticker"}).copy()
    return d


def roda(d, capital=20000, custo_mult=1, lag=0, smin=0.0, modo="leilao", prazo=300, adv_min=2e4, por_opa=3000.0):
    key = (id(d), capital, custo_mult, lag, smin, modo, prazo, adv_min, por_opa)
    if key in _RES:
        return _RES[key]
    P, R, V, HS, BI = d["P"], d["R"].fillna(0), d["V"].fillna(0), d["HS"], d["BID"]
    idx = B.DIAS
    T = len(idx)
    prazo = int(prazo)
    adv = V.rolling(60, min_periods=10).mean()
    lz = d["leilao"]
    pnl = np.zeros(T)
    cdi_p = np.zeros(T)
    vend = np.zeros(T)
    usado = np.zeros(T)
    neg = []
    tam = por_opa * capital / 20000
    ev = d["ev"].sort_values("data")
    W = pd.DataFrame(0.0, index=idx, columns=sorted(ev.ticker.unique()))
    fim_tk = {}
    for _, o in ev.iterrows():
        t = o.ticker
        if t not in P:
            continue
        i = idx.searchsorted(o.data)
        ie = i + 1 + lag
        if ie >= T or fim_tk.get(t, -1) >= ie:
            continue
        p = P[t].values
        if not p[ie] > 0 or not (adv[t].iloc[i] >= adv_min) or p[i] > o.oferta * (1 - smin):
            continue
        livre = capital - usado[ie]
        q = np.floor(min(tam, livre) / p[ie])
        if q < 1:
            continue
        v0 = q * p[ie]
        c0 = v0 * (B.EMOL + HS[t].iloc[ie]) * custo_mult
        # leilão real (TPMERC 017) depois da compra
        lt = lz[(lz.ticker == t) & (pd.to_datetime(lz.data) > idx[ie])]
        il = idx.searchsorted(pd.to_datetime(lt.data.iloc[0])) if len(lt) else T + 1
        pl = float(lt.fech.iloc[0]) if len(lt) else np.nan
        val = v0
        pnl[ie] -= c0
        ix, motivo, sai = None, None, None
        parado = 0
        for j in range(ie + 1, min(ie + prazo, T - 1) + 1):
            if j == il and pl > 0:
                ref = P[t].iloc[:j].dropna()
                sai = val * pl / ref.iloc[-1] if len(ref) else val
                ix, motivo = j, f"leilão R$ {pl:.2f}"
                break
            g = val * R[t].iloc[j]
            pnl[j] += g
            val += g
            parado = parado + 1 if not p[j] > 0 else 0
            if parado >= 30:
                ix, motivo, sai = j, "parou de negociar", val
                break
            if modo == "spread" and p[j] >= o.oferta * .995:
                b = BI[t].iloc[j]
                sai = val * (b / p[j] if b > 0 else 1 - HS[t].iloc[j]) * (1 - B.EMOL * custo_mult)
                ix, motivo = j, "spread fechou"
                break
        if ix is None:
            ix = min(ie + prazo, T - 1)
            if ix == T - 1 and ix < ie + prazo:
                motivo, sai = "aberta", val                                # ainda em carteira no fim dos dados
            else:
                b = BI[t].iloc[ix]
                sai = val * (b / p[ix] if b > 0 and p[ix] > 0 else 1 - HS[t].iloc[ix]) * (1 - B.EMOL * custo_mult)
                motivo = "prazo"
        pnl[ix] += sai - val
        if motivo not in ("aberta",):
            vend[ix] += sai
        cdi_p[ie:ix + 1] += v0 * C.CDI.reindex(idx).iloc[ie:ix + 1].values
        usado[ie:ix + 1] += v0
        W.iloc[ie - 1 - lag:ix - lag, W.columns.get_loc(t)] += v0 / capital
        fim_tk[t] = ix
        neg.append({"ativo": t, "lado": 1, "entrada": idx[ie], "saida": idx[ix], "dias": ix - ie, "retorno_%": ((sai - c0) / v0 - 1) * 100,
                    "contrib_pp": (sai - c0 - v0) / capital * 100, "valor": v0, "rotulo": f"{o.rotulo[:70]} | saída: {motivo}"})
    pnl = pd.Series(pnl, index=idx)
    cdi_p = pd.Series(cdi_p, index=idx)
    res = {"e": (pnl - cdi_p) / capital, "pnl": pnl, "custo": pd.Series(0.0, index=idx), "cdi_perdido": cdi_p, "vendas": pd.Series(vend, index=idx),
           "W": W, "negocios": pd.DataFrame(neg)}
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
