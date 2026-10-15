"""
(1) Carry de financiamento dos perpétuos: à vista comprado x perpétuo vendido (delta neutro), em corretora offshore, com haircut de contraparte.

Tese de mesa: o varejo global quer cripto ALAVANCADO e usa o perpétuo; quando há mais comprados que vendidos, o comprado paga ao vendido a
taxa de financiamento (a cada 8h). Quem compra o à vista e vende o perpétuo na mesma corretora é o "banco" desse varejo: não corre o preço,
recebe o financiamento. Vendedor forçado do outro lado: o comprado alavancado que precisa manter a posição (e paga para isso). Em 2021 o
financiamento pagou 20–50% a.a.; em 2023 0–10%; 2024 12–14%. O edge de PF: tamanho pequeno não move o livro; o problema é ONDE fazer.

Rota PF (verificado em 2026, ver cr_comum): perpétuo NÃO é oferecido a residente pela entidade brasileira (CVM, AD 17.961/2020; Binance e
Bybit migraram brasileiros para entidades locais em 2026 e cortaram derivativos/margem). Sobra a "conta internacional" (Binance Abu Dhabi /
OKX) — fora da supervisão de CVM/BCB, com risco de contraparte (FTX, nov/2022) e regulatório. Dinheiro sai do Brasil: perde o CDI, fica em
US$/USDT (câmbio no P&L) e paga remessa (pf.custo_conta_exterior). IR: aplicação no exterior (Lei 14.754/2023), 15% anual -> "exterior".

Implementação: 6 moedas (BTC, ETH, SOL, BNB, XRP, DOGE). No fechamento diário (00h UTC) liga a moeda se o financiamento médio dos últimos
`janela` dias, anualizado, passa de CDI + `thr`; executa no fechamento seguinte (t+1). Nocional por moeda = capital x 1/(1+1/alav) / 6
(à vista N + margem do perpétuo N/alav). P&L por dia = financiamento recebido (todas as liquidações do dia) + (retorno do à vista − retorno
do perpétuo) — mesma corretora, mesmo instante (00h UTC). Liquidação: se a máxima horária do à vista passar 85% de 1/alav acima do preço de
entrada, o vendido é liquidado (perde 1% do nocional + remonta). Custo 0,15% do nocional por lado (taker 0,10% à vista + 0,05% perpétuo) +
0,05% de spread em altcoins. Haircut de contraparte: `contraparte` a.a. sobre o saldo na corretora (perda esperada; auditoria anterior:
5% a.a. de chance x 50% de perda = 2,5%). Saldo na corretora segue pf.custo_conta_exterior (revisão mensal, sem folga extra).
"""
import numpy as np
import pandas as pd

import cr_comum as K

NOME = "Carry de financiamento de perpétuos (à vista x perpétuo, offshore, com contraparte)"
TESE = "compro o à vista e vendo o perpétuo quando o financiamento médio passa do CDI + limiar; recebo o que o alavancado paga"
BENCHMARK = "CDI"
INICIO, CORTE = "2020-01-01", "2023-01-01"
REGIME = "nenhum"
CUSTO_TROCA = .0
CLASSE_IR = "exterior"
PARAMS = {"thr": .20, "janela": 14, "alav": 2.0, "contraparte": .025}   # maior IR dentro da amostra
GRADE = {"thr": [.05, .10, .20], "janela": [3, 7, 14], "alav": [1.0, 2.0]}
VIZINHANCA = {"thr": (.06, .15), "janela": (4, 12), "alav": (1.5, 3.0), "contraparte": (.015, .04)}
MOEDAS = ["BTC", "ETH", "SOL", "BNB", "XRP", "DOGE"]
INSTRUMENTOS = [{"onde": "Binance internacional (Abu Dhabi) / OKX — offshore", "ticker": f"{m}USDT spot + {m}USDT perpétuo",
                 "lote": "fração (mín. ~US$ 5-100)", "custo": "0,10% à vista + 0,05% perpétuo por lado"} for m in MOEDAS]
APLICAVEL = "parcial"
MOTIVO = ("perpétuo só via conta offshore fora da CVM/BCB (Binance internacional/OKX); Bybit e Binance BR cortaram derivativos a brasileiros "
          "em 2026. Exige remessa (IOF 1,1%), USDT e aceitar risco de contraparte e regulatório; lotes fracionários cabem com R$ 20 mil.")
ALAVANCAGENS = [1, 1.5]
MOTIVO_ALAV = "alavancagem = nocional maior com a mesma margem do perpétuo; acima de 1,5x o vendido é liquidado em altas de 30-40% (SOL/DOGE)"
CUSTO = {"BTC": .0015, "ETH": .0015}


def carrega():
    sp = K.ler("spot_perp_d.parquet").copy()
    sp["fecha"] = sp.t + pd.Timedelta(days=1)                       # candle diário fecha às 00h UTC do dia seguinte
    S = sp.pivot_table(index="fecha", columns=["mkt", "sym"], values="fech")
    S.columns = [f"{a}_{b.replace('USDT', '')}" for a, b in S.columns]
    f = K.ler("funding.parquet").copy()
    f["fecha"] = f.t.dt.round("h").dt.ceil("D")                     # liquidações em (00h, 00h do dia seguinte]
    F = f.pivot_table(index="fecha", columns="sym", values="taxa", aggfunc="sum")
    F.columns = [c.replace("USDT", "") for c in F.columns]
    H = K.painel_1h()[MOEDAS]
    Hmax = H.resample("D", label="right", closed="right").max()
    return {"px": S.sort_index(), "fund": F.sort_index(), "hmax": Hmax}


def _simula(d, capital, custo_mult, lag, thr, janela, alav, contraparte, alavancagem=1):
    S, F = d["px"], d["fund"]
    idx = S.index
    F = F.reindex(idx).reindex(columns=MOEDAS)
    spot = S[[f"spot_{m}" for m in MOEDAS]].set_axis(MOEDAS, axis=1)
    perp = S[[f"perp_{m}" for m in MOEDAS]].set_axis(MOEDAS, axis=1)
    hmax = d["hmax"].reindex(idx).reindex(columns=MOEDAS)
    cdi_aa = (1 + K.CDI_D).pow(252) - 1
    cdi_u = cdi_aa.reindex(idx - pd.Timedelta(days=1), method="ffill").values   # CDI do pregão anterior (conhecido)
    sinal = F.rolling(int(janela), min_periods=int(janela)).sum() / int(janela) * 365
    liga = sinal.sub(cdi_u + thr, axis=0) > 0
    liga &= perp.notna() & spot.notna()
    noc = capital * alavancagem / (1 + 1 / alav) / len(MOEDAS)               # nocional por moeda em R$
    custo = pd.Series({m: CUSTO.get(m, .002) for m in MOEDAS})
    rs, rp = spot / spot.shift(1) - 1, perp / perp.shift(1) - 1
    T, N = len(idx), len(MOEDAS)
    L = liga.values
    E = np.zeros((T, N))
    pnl = np.zeros((T, N))
    cus = np.zeros((T, N))
    ent = np.full(N, np.nan)
    sh = 1 + lag
    rsv, rpv, Fv, Hv, Pv = rs.values, rp.values, F.fillna(0).values, hmax.values, spot.values
    for i in range(1, T):
        for j in range(N):
            if E[i - 1, j]:                                                  # carrega o dia i com a posição de i-1
                pnl[i, j] = noc * (Fv[i, j] + np.nan_to_num(rsv[i, j] - rpv[i, j]))
                if np.isfinite(Hv[i, j]) and Hv[i, j] > ent[j] * (1 + .85 / alav):     # vendido liquidado (máxima do dia)
                    cus[i, j] += noc * (.01 + 2 * custo[MOEDAS[j]]) * custo_mult
                    ent[j] = Pv[i, j]                                        # remonta no fechamento (spot nunca foi vendido)
            alvo = bool(L[i - sh, j]) if i - sh >= 0 else False
            E[i, j] = noc if alvo else 0.0
            if E[i, j] != E[i - 1, j]:
                cus[i, j] += noc * custo[MOEDAS[j]] * custo_mult             # monta ou desmonta (as duas pernas)
                if E[i, j]:
                    ent[j] = Pv[i, j]
    f = lambda a: pd.DataFrame(a, index=idx, columns=MOEDAS)
    E, pnl, cus = f(E), f(pnl), f(cus)
    pnl_brl, cus_brl = pnl, cus                                              # nocional fixo em R$ (convertido na montagem)
    saldo = K.para_dias(E.sum(axis=1) * (1 + 1 / alav), "last").fillna(0)    # R$ necessário na corretora (à vista + margem)
    conta, saldo_ef = K.pf.custo_conta_exterior(saldo, folga=1.0)
    corr = saldo_ef * contraparte / 252
    return {"E": E, "pnl": pnl_brl - cus_brl, "cus": cus_brl, "conta": conta * custo_mult, "contraparte": corr, "saldo": saldo_ef,
            "carry": (rs - rp + F), "sinal": sinal}


def excesso(d, capital=20000, custo_mult=1, lag=0, regime=REGIME, alavancagem=1, **params):
    p = {**PARAMS, **params}
    x = _simula(d, capital, custo_mult, lag, p["thr"], p["janela"], p["alav"], p["contraparte"], alavancagem)
    e = (K.para_dias(x["pnl"].sum(axis=1)) - x["conta"] - x["contraparte"]) / capital
    return K.C.aplica_regime(e.reindex(K.DIAS).fillna(0), regime, CUSTO_TROCA * custo_mult)


def posicoes(d, capital=20000, **params):
    p = {**PARAMS, **params}
    x = _simula(d, capital, 1, 0, p["thr"], p["janela"], p["alav"], p["contraparte"])
    W, R = K.W_diario(x["E"] / capital, x["carry"])
    return W, R


def negocios(d, capital=20000, **params):
    p = {**PARAMS, **params}
    x = _simula(d, capital, 1, 0, p["thr"], p["janela"], p["alav"], p["contraparte"])
    return K.negocios_blocos(x["E"], x["pnl"], capital, x["carry"])


if __name__ == "__main__":
    d = carrega()
    x = _simula(d, 20000, 1, 0, **PARAMS)
    e = excesso(d)
    print(e[e.index >= INICIO].groupby(e[e.index >= INICIO].index.year).sum() * 100)
    print("saldo médio R$", x["saldo"][x["saldo"].index >= INICIO].mean())
    print(negocios(d).sort_values("contrib_pp").tail(10))
