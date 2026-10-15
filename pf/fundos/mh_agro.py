"""
Margem da cadeia agro lida nos futuros da B3: frigoríficos (BEEF3, MBRF3/MRFG3, JBSS3), BRF (BRFS3), SLC (SLCE3) e São Martinho (SMTO3).

Tese de mesa: a margem do frigorífico é "carne exportada em dólar - boi gordo"; a da BRF é "frango/porco em dólar - milho"; a da SLC é
"milho + soja em reais"; a da São Martinho é "etanol + açúcar em reais". Os futuros da B3 (BGI boi, CCM milho, SJC soja, ETH etanol) e o
dólar mostram a margem do trimestre ANTES do balanço; o analista e o preço da ação reagem com atraso. Todo fim de mês compro as `k` ações
cuja margem implícita mais melhorou nos últimos `jan` pregões (só se melhorou) e, opcionalmente, vendo o Ibovespa (WIN) no beta.
Contexto da pesquisa anterior (C2): a ideia tinha IS forte e OOS fraco (PBO 90%) — aqui a margem é a da cadeia inteira e o universo
é maior; o resultado diz se a informação dos futuros ainda está no preço das ações.

Hedge "na commodity" (variante): o frigorífico é VENDIDO em boi (compra o insumo) — o hedge natural seria comprar BGI. Mas 1 BGI = 330 @
x R$ 150–400 = R$ 50–130 mil: com R$ 20–50 mil nunca cabe (o arredondamento dá 0). O CCM (450 sacas x R$ 35–90 = R$ 15–40 mil) cabe
às vezes com R$ 50 mil. Conclusão operacional: para PF o futuro agro serve como SINAL, não como hedge.
Dados: futuros agro da B3 só desde 2018 (boletim BVBG.086) -> fundo começa em 2019, fora da amostra desde 2023.
"""
import numpy as np
import pandas as pd

import mh_base as B
import comum as C

NOME = "Margem agro nos futuros B3 -> frigoríficos/SLC/São Martinho"
TESE = ("Compro as ações da cadeia agro cuja margem implícita nos futuros B3 (boi, milho, soja, etanol) e no dólar mais melhorou, antes "
        "do balanço; hedge opcional de Ibovespa em WIN")
BENCHMARK = "CDI"
INICIO, CORTE = "2019-01-01", "2023-01-01"
REGIME = "nenhum"
CUSTO_TROCA = .001
PARAMS = {"jan": 63, "k": 1, "hedge": "nenhum", "peso": 1.0}
GRADE = {"jan": [63, 126], "k": [1, 2], "hedge": ["win", "nenhum"]}
VIZINHANCA = {"jan": (42, 126)}
VARIANTES = {"hedge na commodity (BGI/CCM)": {"hedge": "agro"}, "k=3": {"k": 3}}
# ação -> [(fator, sinal na margem)] ; fatores = retorno acumulado dos futuros rolados (sem salto de vencimento) e da PTAX
CADEIA = {"BEEF3": [("usd", 1), ("bgi", -1)], "MBRF3": [("usd", 1), ("bgi", -1)], "JBSS3": [("usd", 1), ("bgi", -1)],
          "BRFS3": [("usd", 1), ("ccm", -1)], "SLCE3": [("ccm", 1), ("sjc", 1), ("usd", 1)], "SMTO3": [("eth", 1), ("usd", .5)]}
HEDGE_AGRO = {"BEEF3": "BGI", "MBRF3": "BGI", "JBSS3": "BGI", "BRFS3": "CCM", "SLCE3": "CCM"}
APLICAVEL = True
MOTIVO = ("Aplicável: ações no fracionário; WIN só cabe com o índice baixo ou R$ 50 mil (hedge parcial); os futuros agro como hedge NÃO "
          "cabem (BGI R$ 50–130 mil por contrato) — servem como sinal")
INSTRUMENTOS = ("B3 (Clear/Rico): BEEF3, MBRF3 (ex-MRFG3), JBSS3 (até jun/2025), BRFS3 (até set/2025), SLCE3, SMTO3 no fracionário, 1/k do "
                "capital cada, rebalanceio mensal; WIN vendido no beta; sinal dos ajustes de BGI/CCM/SJC/ETH (B3) e PTAX")
ALAVANCAGENS = [1, 1.5, 2]
MOTIVO_ALAV = "Até 2x com termo (CDI+4%); 5x em 1–2 small/mid caps agro de vol 35–50% é inviável (chamada de margem certa)"


def carrega():
    return B.seleciona(B.dados(), list(CADEIA))


def _fatores(d):
    f = B.futuros(d)
    idx = lambda r: np.log1p(r.fillna(0)).cumsum()
    out = {"usd": np.log(B.PTAX.reindex(B.DIAS).ffill()), "bgi": idx(f["BGI"][0]), "ccm": idx(f["CCM"][0]),
           "sjc": idx(B.br(d, "sjc_ret").fillna(0)), "eth": idx(B.br(d, "eth_ret").fillna(0))}
    vivo = {k: B.br(d, f"{k}_px").ffill(limit=5).notna() for k in ("bgi", "ccm", "sjc", "eth")}
    return out, vivo


def _livro(d, capital=20000, lag=0, custo_mult=1, alavancagem=1, jan=63, k=2, hedge="win", peso=1.0):
    P, R, ADV = B.acoes(d)
    F, vivo = _fatores(d)
    tk = [t for t in CADEIA if t in R.columns]
    m = pd.DataFrame({t: sum(s * (F[f] - F[f].shift(jan)) for f, s in CADEIA[t]) for t in tk})
    ok_fut = pd.DataFrame({t: pd.concat([vivo[f].astype(float).rolling(jan).min().eq(1) for f, _ in CADEIA[t] if f in vivo], axis=1).all(axis=1)
                           for t in tk})
    elig = (ADV[tk] >= 5e6) & P[tk].notna() & ok_fut & pd.DataFrame({t: B.DIAS >= pd.Timestamp("2018-07-01") for t in tk}, index=B.DIAS)
    m = m.where(elig)
    rank = m.rank(axis=1, ascending=False)
    W = ((rank <= k) & (m > 0)).astype(float) * peso / k
    W = C.mensal(W)                                                    # decide no último pregão do mês
    f = None
    cdi = C.CDI.reindex(B.DIAS).fillna(0)
    if hedge == "win":
        rw = B.futuros(d)["WIN"][0]
        bi = pd.DataFrame({t: B.beta_rolante(R[t] - cdi, rw.to_frame("w"), lim=(0, 2))["w"] for t in tk})
        f = {"WIN": ("WIN", -(W * B.congela(bi, W)).sum(axis=1))}
    elif hedge == "agro":
        fu = B.futuros(d)
        f = {}
        for ct in ("BGI", "CCM"):
            nomes = [t for t in tk if HEDGE_AGRO.get(t) == ct]
            if not nomes:
                continue
            b = pd.DataFrame({t: B.beta_rolante(R[t] - cdi, fu[ct][0].to_frame("c"), lim=(-2, 2))["c"] for t in nomes})
            f[ct] = (ct, -(W[nomes] * B.congela(b, W[nomes])).sum(axis=1))
    return B.livro(capital, W, f, d, lag=lag, custo_mult=custo_mult, alavancagem=alavancagem,
                   taxa_aluguel={t: .02 for t in tk})


def excesso(d, capital=20000, custo_mult=1, lag=0, regime=REGIME, alavancagem=1, **params):
    e = B.padrao(__import__(__name__), d, capital, lag, custo_mult, alavancagem, params)["e"]
    return C.aplica_regime(e, regime, CUSTO_TROCA * custo_mult)


def classes_ir(d, capital=20000, **params):
    return B.padrao(__import__(__name__), d, capital, 0, 1, 1, params)["classes"]


def posicoes(d, capital=20000, **params):
    r = B.padrao(__import__(__name__), d, capital, 0, 1, 1, params)
    return r["W"], r["Rx"]


def negocios(d, capital=20000, **params):
    return B.negocios_de(B.padrao(__import__(__name__), d, capital, 0, 1, 1, params), capital)


def diagnostico(d, capital=20000, **params):
    out = dict(B.padrao(__import__(__name__), d, capital, 0, 1, 1, params)["diag"])
    ra = B.padrao(__import__(__name__), d, capital, 0, 1, 1, {**params, "hedge": "agro"})["diag"]
    out.update({f"[hedge agro] {a}": b for a, b in ra.items() if "BGI" in a or "CCM" in a})
    return out
