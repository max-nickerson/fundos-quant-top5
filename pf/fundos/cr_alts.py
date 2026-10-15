"""
(6) Altcoins: momentum ou reversão de curto prazo entre as 20 maiores (por volume), com custos reais de PF e hedge opcional de BTC.

Tese de mesa: altcoin é a ponta mais especulativa do varejo. Duas histórias concorrentes: (a) MOMENTUM — o dinheiro novo entra numa
"narrativa" (DeFi 2020, memes 2021/2024, IA 2024) e gira por semanas; (b) REVERSÃO — a alta de uma semana é bomba de varejo/listagem e
devolve. Sem fluxo de caixa, quem decide é o fluxo. O PF só consegue o lado COMPRADO em corretora brasileira (aluguel de alt não existe;
perpétuo só offshore) -> long-only; o "market-neutral" possível é vender BTC contra (hedge="btc", via BIT vendido na B3 — 0,01 BTC desde
06/2025; antes disso é aproximação). Assim o resultado é alt escolhida − BTC: separa o beta de cripto do alfa da seleção.

Implementação: fechamento diário 00h UTC (do 1h da Binance, ~85 pares incl. deslistados — LUNA, FTT, SRM, FTM->S, MATIC->POL ficam com
o buraco tratado como saída). A cada `reb` dias: universo = 20 maiores por volume em US$ dos 30 dias anteriores, sem BTC e sem stablecoins;
ordena pelo retorno de `janela` dias; modo="mom" compra as k=5 melhores, "rev" as 5 piores; pesos iguais somando `peso`; executa no
fechamento seguinte (t+1); segura até o próximo rebalanceamento (valor flutua). Custos por lado: 0,35% nas alts (R$->USDT 0,10% + taxa
0,10% + spread 0,15%); hedge BIT 0,05%. O BIT vendido rende a base (≈ CDI − 4 pp a.a., medida) sem consumir caixa.
IR: cripto (as vendas semanais passam de R$ 35 mil/mês com R$ 50 mil; com R$ 20 mil às vezes isento) + futuros_b3 no hedge.
"""
import numpy as np
import pandas as pd

import cr_comum as K

NOME = "Altcoins top 20: momentum/reversão semanal (long-only, hedge BTC opcional)"
TESE = "compro as 5 altcoins de maior (ou menor) retorno recente entre as 20 maiores e, opcionalmente, vendo BTC contra no BIT"
BENCHMARK = "CDI"
INICIO, CORTE = "2019-01-01", "2023-01-01"
REGIME = "nenhum"
CUSTO_TROCA = .0
CLASSE_IR = "cripto"
PARAMS = {"modo": "mom", "janela": 28, "hedge": "nenhum", "reb": 7, "peso": .5}   # maior IR no IS (é beta: ver hedge="btc" no caderno)
GRADE = {"modo": ["mom", "rev"], "janela": [7, 28], "hedge": ["nenhum", "btc"]}
VIZINHANCA = {"janela": (5, 40), "reb": (5, 10), "peso": (.3, .7)}
INSTRUMENTOS = [{"onde": "Binance BR", "ticker": "<alt>USDT (via USDTBRL)", "lote": "fração", "custo": "0,35% por lado"},
                {"onde": "B3", "ticker": "BIT vendido (hedge)", "lote": "0,01 BTC desde 06/2025", "custo": "0,05% por lado"}]
APLICAVEL = "parcial"
MOTIVO = ("long-only em corretora brasileira (Binance BR lista ~350 pares; MB menos); o hedge com BIT só cabe em contratos inteiros "
          "desde 06/2025 (antes 0,1 BTC). Em 10/2026 a Binance BR deslistou 22 tokens e cortou margem.")
ALAVANCAGENS = [1]
MOTIVO_ALAV = "sem margem em corretora brasileira"
K_N, TOPN = 5, 20
BASE_BIT = .04                                      # base do BIT ≈ CDI − 4 pp a.a. (gl_cripto_tendencia, 2024-26)


def carrega():
    return {"h": K.ler("binance_1h.parquet").set_index("t")}


def _diario(d):
    x = d["h"].reset_index()
    P = K.painel_1h("fech", {"h": x})
    V = K.painel_1h("vol_usd", {"h": x})
    P = P.reindex(pd.date_range(P.index[0].ceil("D"), P.index[-1], freq="h"))
    V = V.reindex(P.index)
    P = K.mata_saltos(P.where(P > 0))
    Pd, Vd = K.diario_de_1h(P, V)
    Pd = K.mata_saltos(Pd, gap_h=48)
    return Pd, Vd


def _simula(d, capital, custo_mult, lag, modo, janela, hedge, reb, peso, alavancagem=1):
    P, V = _diario(d)
    R = P / P.shift(1) - 1
    alts = [c for c in P.columns if c != "BTC"]
    vol30 = V[alts].fillna(0).rolling(30, min_periods=20).sum()
    eleg = (vol30.rank(axis=1, ascending=False) <= TOPN) & P[alts].notna() & P[alts].shift(int(janela)).notna()
    mom = (P[alts] / P[alts].shift(int(janela)) - 1).where(eleg)
    dia_reb = np.arange(len(P)) % int(reb) == 0
    W = pd.DataFrame(np.nan, index=P.index, columns=alts + ["BTC"])
    for i in np.where(dia_reb)[0]:
        m = mom.iloc[i].dropna()
        if len(m) < K_N * 2:
            W.iloc[i] = 0.0
            continue
        esc = m.nlargest(K_N).index if modo == "mom" else m.nsmallest(K_N).index
        w = pd.Series(0.0, index=W.columns)
        w[esc] = peso * alavancagem / K_N
        if hedge == "btc":
            w["BTC"] = -peso * alavancagem
        W.iloc[i] = w.values
    W = W.ffill().fillna(0)
    custo = pd.Series(.0035, index=W.columns)
    custo["BTC"] = .0005
    fxr = K.fx_horario(P.index)
    fxr = fxr / fxr.shift(1) - 1
    M = K.motor(W, R[W.columns], capital, custo, lag_passos=1 + lag, custo_mult=custo_mult, fx_r=fxr,
                rebal=pd.Series(dia_reb, index=P.index))
    M["R"] = R[W.columns]
    return M


def _excesso_de(M, capital):
    p = K.para_dias(M["pnl"].sum(axis=1))
    V0 = M["V"].shift(1).fillna(0)
    lng = V0.clip(lower=0).sum(axis=1)
    sht = (-V0.clip(upper=0)).sum(axis=1)
    bl = lambda s: s.groupby(K.balde(s.index)).mean().reindex(K.DIAS).fillna(0)
    # comprado à vista não rende CDI; o BIT vendido não usa caixa e rende a base (≈ CDI − 4 pp): + (CDI − 4pp) no nocional vendido
    return (p - bl(lng) * K.CDI_D + bl(sht) * (K.CDI_D - BASE_BIT / 252)) / capital


def excesso(d, capital=20000, custo_mult=1, lag=0, regime=REGIME, alavancagem=1, **params):
    p = {**PARAMS, **params}
    M = _simula(d, capital, custo_mult, lag, p["modo"], p["janela"], p["hedge"], p["reb"], p["peso"], alavancagem)
    e = _excesso_de(M, capital)
    e = e.where(e.index >= pd.Timestamp(INICIO), 0)
    return K.C.aplica_regime(e, regime, CUSTO_TROCA * custo_mult)


def classes_ir(d, capital=20000, **params):
    p = {**PARAMS, **params}
    M = _simula(d, capital, 1, 0, p["modo"], p["janela"], p["hedge"], p["reb"], p["peso"])
    alt = [c for c in M["pnl"].columns if c != "BTC"]
    return {"cripto": K.para_dias(M["pnl"][alt].sum(axis=1)), "futuros_b3": K.para_dias(M["pnl"]["BTC"])}


def _ativos(M):
    return [c for c in M["E"].columns if (M["E"][c] != 0).any()]


def posicoes(d, capital=20000, **params):
    p = {**PARAMS, **params}
    M = _simula(d, capital, 1, 0, p["modo"], p["janela"], p["hedge"], p["reb"], p["peso"])
    a = [c for c in _ativos(M) if c != "BTC"]                         # vendas de cripto (o BIT é futuro, sem isenção)
    W, R = K.W_com_vendas(M["V"][a], M["R"][a], capital)
    if "BTC" in _ativos(M):
        Wb, Rb = K.W_diario(M["E"][["BTC"]] / capital, M["R"][["BTC"]])
        W["BTC"], R["BTC"] = Wb["BTC"], Rb["BTC"]
    return W, R


def negocios(d, capital=20000, **params):
    p = {**PARAMS, **params}
    M = _simula(d, capital, 1, 0, p["modo"], p["janela"], p["hedge"], p["reb"], p["peso"])
    a = _ativos(M)
    return K.negocios_blocos(M["E"][a], M["pnl"][a], capital, M["R"][a])


if __name__ == "__main__":
    d = carrega()
    e = excesso(d)
    print((e.groupby(e.index.year).sum() * 100).loc[2019:])
    n = negocios(d)
    print(len(n), n.sort_values("contrib_pp").tail(5).to_string(), n.sort_values("contrib_pp").head(5).to_string())
