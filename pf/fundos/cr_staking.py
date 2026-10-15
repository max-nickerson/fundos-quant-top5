"""
(8) Staking de ETH vs CDI depois do IR: o rendimento "de renda fixa" do ether — com e sem o preço do ether.

Tese de mesa: o staking paga 2,4–4,5% a.a. EM ETH (APY do stETH/Lido: 2022 4,5%, 2023 4,3%, 2024 3,2%, 2025 2,8%, 2026 2,4%). Contra um
CDI de 10–15% isso só vale se (a) o PF já quer o beta do ether (staking = cupom sobre o que ele seguraria de qualquer jeito) ou (b) o preço
for neutralizado vendendo o perpétuo — aí o retorno é staking + financiamento do perpétuo (o comprado alavancado paga o vendido) e o
problema vira o mesmo do cr_funding: dinheiro offshore, sem CDI, em US$, com contraparte.
Versões:
  modo="neutro":  ETH em staking (WBETH/Lido na corretora offshore, usado como garantia) + perpétuo ETHUSDT vendido 1:1, quando
                  staking + financiamento médio de 14 dias > CDI + thr; saldo na corretora = nocional x (1 + 1/2) (perpétuo 2x);
                  IR exterior (15% anual); haircut de contraparte 2,5% a.a. sobre o saldo; IOF/remessa via pf.custo_conta_exterior.
  modo="beta":    ETH em staking numa corretora brasileira (Mercado Bitcoin/Binance BR oferecem), sempre comprado, em R$: o cupom
                  sobre o beta (classe cripto, isenção de R$ 35 mil/mês nas vendas; o rendimento do staking é tributado como ganho na
                  venda — simplificação). Reportado para separar BETA de ALFA.
Staking líquido = APY do stETH x 0,90 (a corretora fica com ~10–25%; Lido já desconta 10%). Antes de 05/2022 (sem dado do DefiLlama)
uso 4,5% (APR da beacon chain em 2021 ~5%) — PREMISSA; e o ETH em staking só pôde ser sacado depois de 04/2023 (Shapella).
"""
import numpy as np
import pandas as pd

import cr_comum as K

NOME = "Staking de ETH: neutro (staking + perpétuo vendido, offshore) ou cupom sobre o beta"
TESE = "ganho o staking do ether e, no modo neutro, vendo o perpétuo para receber também o financiamento sem correr o preço"
BENCHMARK = "CDI"
INICIO, CORTE = "2021-01-01", "2023-01-01"
REGIME = "nenhum"
CUSTO_TROCA = .0
CLASSE_IR = "exterior"
PARAMS = {"modo": "neutro", "thr": .05, "janela": 14, "peso": .6, "contraparte": .025}
GRADE = {"modo": ["neutro", "beta"], "thr": [-.05, .0, .05]}
VIZINHANCA = {"thr": (-.03, .03), "janela": (7, 21), "peso": (.5, .66)}
APY_PRE = 4.5
CORTE_EXCH = .90
INSTRUMENTOS = [{"onde": "Binance internacional / OKX (offshore)", "ticker": "WBETH + ETHUSDT perpétuo", "lote": "fração", "custo": "0,15%/lado"},
                {"onde": "Mercado Bitcoin / Binance BR", "ticker": "ETH em staking", "lote": "fração", "custo": "0,15%/lado"}]
APLICAVEL = "parcial"
MOTIVO = "neutro só offshore (perpétuo fora da CVM, contraparte); o modo beta cabe em corretora brasileira (staking de ETH oferecido)"
ALAVANCAGENS = [1]
MOTIVO_ALAV = "no neutro o perpétuo já está 2x; mais que isso é liquidação em alta forte do ETH"


def carrega():
    sp = K.ler("spot_perp_d.parquet")
    sp = sp[sp.sym == "ETHUSDT"].copy()
    sp["fecha"] = sp.t + pd.Timedelta(days=1)
    S = sp.pivot_table(index="fecha", columns="mkt", values="fech")
    f = K.ler("funding.parquet")
    f = f[f.sym == "ETHUSDT"].copy()
    f["fecha"] = f.t.dt.round("h").dt.ceil("D")
    F = f.groupby("fecha").taxa.sum().rename("fund")
    apy = K.ler("lido_apy.csv")["apy"].copy()
    apy.index = apy.index + pd.Timedelta(days=1)                       # APY do dia publicado no fim do dia
    return {"px": S, "fund": F.to_frame(), "apy": apy.to_frame()}


def _simula(d, capital, custo_mult, lag, modo, thr, janela, peso, alavancagem=1, contraparte=.025):
    S = d["px"]
    idx = S.index
    F = d["fund"]["fund"].reindex(idx).fillna(0)
    apy = d["apy"]["apy"].reindex(idx, method="ffill")
    apy = apy.where(idx >= d["apy"].index.min(), APY_PRE).fillna(APY_PRE) / 100 * CORTE_EXCH
    stk = apy / 365                                                     # staking por dia corrido
    rs, rp = S["spot"] / S["spot"].shift(1) - 1, S["perp"] / S["perp"].shift(1) - 1
    cdi_aa = ((1 + K.CDI_D) ** 252 - 1).reindex(idx - pd.Timedelta(days=1), method="ffill").values
    if modo == "neutro":
        sinal = apy.shift(1) + F.rolling(int(janela), min_periods=int(janela)).mean() * 365 - cdi_aa - thr
        W = (sinal > 0).astype(float) * peso * alavancagem
        carry = (stk + F + rs - rp).fillna(0)                          # por R$ de nocional
        E = W.shift(1 + lag).fillna(0)
        E0 = E.shift(1).fillna(0)
        pnl = E0 * carry * capital - (E - E0).abs() * capital * .0015 * custo_mult
        nocional = E * capital
        saldo = K.para_dias(nocional * 1.5, "last").fillna(0)
        conta, saldo_ef = K.pf.custo_conta_exterior(saldo, folga=1.0)
        e = (K.para_dias(pnl) - conta * custo_mult - saldo_ef * contraparte / 252) / capital
        return {"e": e, "E": E.to_frame("ETH"), "pnl": pnl.to_frame("ETH"), "R": carry.to_frame("ETH")}
    # beta: ETH comprado em R$ + staking, sempre, com o PL inteiro (thr não se aplica)
    W = pd.DataFrame({"ETH": float(alavancagem)}, index=idx)
    R = ((1 + rs) * (1 + stk) - 1).to_frame("ETH")
    fxr = K.fx_horario(idx)
    fxr = fxr / fxr.shift(1) - 1
    M = K.motor(W, R, capital, .0015, lag_passos=1 + lag, custo_mult=custo_mult, fx_r=fxr,
                rebal=pd.Series(True, index=idx))           # peso fixo do PL (o excesso é sobre capital constante)
    e, _ = K.excesso_spot(M, capital)
    return {"e": e, "E": M["E"], "pnl": M["pnl"], "R": R, "V": M["V"]}


def excesso(d, capital=20000, custo_mult=1, lag=0, regime=REGIME, alavancagem=1, **params):
    p = {**PARAMS, **params}
    x = _simula(d, capital, custo_mult, lag, p["modo"], p["thr"], p["janela"], p["peso"], alavancagem, p["contraparte"])
    e = x["e"].reindex(K.DIAS).fillna(0)
    e = e.where(e.index >= pd.Timestamp(INICIO), 0)
    return K.C.aplica_regime(e, regime, CUSTO_TROCA * custo_mult)


def posicoes(d, capital=20000, **params):
    p = {**PARAMS, **params}
    x = _simula(d, capital, 1, 0, p["modo"], p["thr"], p["janela"], p["peso"])
    return K.W_diario(x["E"], x["R"])


def negocios(d, capital=20000, **params):
    p = {**PARAMS, **params}
    x = _simula(d, capital, 1, 0, p["modo"], p["thr"], p["janela"], p["peso"])
    return K.negocios_blocos(x["E"], x["pnl"], capital, x["R"])


if __name__ == "__main__":
    d = carrega()
    for m in ["neutro", "beta"]:
        e = excesso(d, modo=m)
        print(m, (e.groupby(e.index.year).sum() * 100).loc[2021:].round(1).to_dict())
    print(negocios(d).tail(10))
