"""
(4) Fim de semana e horário: segurar BTC/ETH (à vista em R$) só nas janelas em que os mercados tradicionais estão FECHADOS.

Tese de mesa: de sexta 17h (Brasília) a segunda 10h a B3 e a CME estão fechadas; os ETFs (QBTC11, IBIT) e os futuros (BIT, MBT) não
negociam, então quem quer reduzir risco no fim de semana só tem o à vista — e o livro do fim de semana é mais raso (sem formadores dos
ETFs, sem arbitragem de base). Se há prêmio de liquidez, ele aparece como retorno médio diferente nas janelas "fechadas" vs "abertas".
Versões (calendário fixo, nenhuma estimativa):
  modo="fds":    comprado de sexta no fechamento da B3 até segunda às 13h UTC (abertura da B3/pregão dos EUA);
  modo="noite":  comprado nas noites de dias úteis (fechamento da B3 -> 13h UTC do dia seguinte);
  modo="eua":    comprado no horário dos EUA em dias úteis (13h -> 21h UTC, B3/CME abertas: o fluxo dos ETFs);
  modo="asia":   comprado de 00h a 08h UTC.
Ativo: BTC, ETH ou os dois (metade cada). Executa na hora seguinte à decisão (ordem agendada; t+1 = a janela começa uma hora depois do
sinal de calendário). Custo 0,15% por lado (Binance BR, par em R$). IR cripto: o giro semanal (52 vendas/ano do capital) passa de R$ 35 mil
no mês -> 15% na prática. Dinheiro fora da janela fica no CDI.
"""
import numpy as np
import pandas as pd

import cr_comum as K

NOME = "Fim de semana/horário: BTC/ETH só quando B3 e CME estão fechadas"
TESE = "seguro cripto à vista só nas janelas sem ETF/futuro (fim de semana, noite) se o livro raso paga prêmio; senão fico no CDI"
BENCHMARK = "CDI"
INICIO, CORTE = "2018-01-01", "2023-01-01"
REGIME = "nenhum"
CUSTO_TROCA = .0
CLASSE_IR = "cripto"
PARAMS = {"modo": "fds", "ativo": "ETH", "peso": 1.0}   # maior IR no IS
GRADE = {"modo": ["fds", "noite", "eua", "asia"], "ativo": ["BTC", "ETH", "ambos"]}
VIZINHANCA = {"peso": (.7, 1.0)}
INSTRUMENTOS = [{"onde": "Binance BR / Mercado Bitcoin", "ticker": "BTCBRL / ETHBRL", "lote": "fração", "custo": "0,15% por lado"}]
APLICAVEL = True
MOTIVO = "à vista em R$ em corretora brasileira; ordens agendadas por horário (manual ou API da corretora)"
ALAVANCAGENS = [1]
MOTIVO_ALAV = "sem margem em corretora brasileira"


def carrega():
    x = K.ler("binance_1h.parquet")
    x = x[x.sym.isin(["BTCUSDT", "ETHUSDT"])]
    return {"h": x.set_index("t")}


def janela(idx, modo):
    """True nas horas (fechamento do candle) em que quero estar POSICIONADO (o candle que termina em t pertence à janela)."""
    h, dw = idx.hour, idx.dayofweek                     # candle que fecha em h cobre (h-1, h]
    dst = pd.Series(idx.normalize()).map(lambda t: t.tz_localize("America/New_York").dst().total_seconds() > 0)
    ab = np.where(dst.values, 20, 21)                   # fechamento da B3 em UTC
    if modo == "fds":                                   # de sexta após o fechamento da B3 até segunda 13h UTC
        return ((dw == 4) & (h > ab)) | (dw == 5) | (dw == 6) | ((dw == 0) & (h <= 13))
    if modo == "noite":                                 # noites de seg-qui (fechamento da B3 -> 13h UTC do dia seguinte)
        return (((dw <= 3) & (h > ab)) | ((dw >= 1) & (dw <= 4) & (h <= 13)))
    if modo == "eua":
        return (dw <= 4) & (h > 13) & (h <= ab)
    if modo == "asia":
        return (h >= 1) & (h <= 8)
    raise ValueError(modo)


def _simula(d, capital, custo_mult, lag, modo, ativo, peso, alavancagem=1):
    P = K.painel_1h("fech", {"h": d["h"].reset_index()})[["BTC", "ETH"]]
    P = P.reindex(pd.date_range(P.index[0], P.index[-1], freq="h"))
    R = P / P.shift(1) - 1
    jan = pd.Series(janela(P.index, modo), index=P.index)
    # decisão em t para estar posicionado no candle que fecha em t+2 (executa no fechamento de t+1): alvo = janela de t+2
    alvo = jan.shift(-2).fillna(False).astype(float)   # calendário fixo (conhecido de antemão): não é olhar o futuro de preço
    cols = ["BTC", "ETH"] if ativo == "ambos" else [ativo]
    W = pd.DataFrame(0.0, index=P.index, columns=["BTC", "ETH"])
    for c in cols:
        W[c] = alvo * peso * alavancagem / len(cols)
    fxr = K.fx_horario(P.index)
    fxr = fxr / fxr.shift(1) - 1
    M = K.motor(W, R, capital, .0015, lag_passos=1 + 24 * lag, custo_mult=custo_mult, fx_r=fxr)
    M["R"] = R
    return M


def excesso(d, capital=20000, custo_mult=1, lag=0, regime=REGIME, alavancagem=1, **params):
    p = {**PARAMS, **params}
    M = _simula(d, capital, custo_mult, lag, p["modo"], p["ativo"], p["peso"], alavancagem)
    e, _ = K.excesso_spot(M, capital)
    e = e.where(e.index >= pd.Timestamp(INICIO), 0)
    return K.C.aplica_regime(e, regime, CUSTO_TROCA * custo_mult)


def posicoes(d, capital=20000, **params):
    p = {**PARAMS, **params}
    M = _simula(d, capital, 1, 0, p["modo"], p["ativo"], p["peso"])
    return K.W_com_vendas(M["V"], M["R"], capital)


def negocios(d, capital=20000, **params):
    p = {**PARAMS, **params}
    M = _simula(d, capital, 1, 0, p["modo"], p["ativo"], p["peso"])
    return K.negocios_blocos(M["E"], M["pnl"], capital, M["R"])


if __name__ == "__main__":
    d = carrega()
    for m in ["fds", "noite", "eua", "asia"]:
        e = excesso(d, modo=m)
        print(m, (e.groupby(e.index.year).sum() * 100).loc[2018:].round(1).to_dict())
