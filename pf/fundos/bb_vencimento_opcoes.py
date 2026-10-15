"""
Vencimento de opções de ações na B3: comprar os objetos no fechamento do vencimento — frente "pf2_b3".

Mesa: o varejo brasileiro é o maior lançador coberto do mundo ("financiamento": compra a ação e vende a call; e venda de put coberta).
No vencimento mensal o fluxo é mecânico: calls dentro do dinheiro são exercidas (o lançador entrega a ação e o titular que não quer a
ação vende no mercado), quem rola o financiamento vende a ação junto, o formador de mercado desmonta o delta-hedge das séries que
venceram. A pressão vendedora se concentra nos pregões até o vencimento e some no dia seguinte. Pinning NÃO funcionou (estudo: comprar
abaixo do strike de maior volume perde 0,25% no dia do vencimento) — o que aparece é o padrão "queda até o vencimento, alta depois":
estudo de evento (PETR4, VALE3, ITUB4, BBDC4, BBAS3, ABEV3; vencimentos mensais):
  3 pregões até o vencimento: IS 2014–2020 −0,60%, 2021–26 −0,22%;  3 pregões depois: IS +0,58%, 2021–26 +0,54% (Ibovespa no dia
  seguinte +0,45% / +0,15%).
Execução: o calendário de vencimentos é público (3ª segunda-feira do mês até abr/2021; 3ª sexta-feira desde mai/2021; feriado -> pregão
seguinte). Decido no fechamento da véspera do vencimento, compro no fechamento do vencimento (t+1), vendo `k` pregões depois.
Cesta igual-ponderada dos objetos, R$ `frac` x capital no total. Sem hedge (WIN de R$ 26–28 mil não cabe; BOVA11 alugado para 3 dias
custa 0,5% de corretagem do aluguel — mais que o ganho).
IR: ações (vendas do mês = ~R$ 18 mil com R$ 20 mil -> isento; com R$ 50 mil, tributado a 15%).
"""
import numpy as np
import pandas as pd

import bb_base as BB

B, C, pf = BB.B, BB.C, BB.pf
DIAS = BB.DIAS

NOME = "Vencimento de opções: objetos comprados no fechamento do vencimento"
TESE = ("Compro PETR4/VALE3/ITUB4/BBDC4/BBAS3/ABEV3 no fechamento do vencimento mensal de opções (fim da venda mecânica de lançadores "
        "cobertos/exercício/delta-hedge) e vendo k pregões depois")
BENCHMARK = "CDI"
INICIO, CORTE = "2014-02-01", "2021-01-01"
REGIME = "nenhum"
CLASSE_IR = "acoes"
CUSTO_TROCA = .001
CESTAS = {"6": ["PETR4", "VALE3", "ITUB4", "BBDC4", "BBAS3", "ABEV3"], "petr_vale": ["PETR4", "VALE3"]}
PARAMS = {"k": 3, "cesta": "petr_vale", "frac": .90}
GRADE = {"k": [1, 3, 5], "cesta": ["6", "petr_vale"]}
VIZINHANCA = {"k": (2, 5), "frac": (.6, .95)}
INSTRUMENTOS = [{"onde": "Clear/Rico/XP (corretagem zero)", "ticker": "PETR4, VALE3, ITUB4, BBDC4, BBAS3, ABEV3", "lote": "1 ação (fracionário)",
                 "custo": "emolumentos 0,03% + meio spread real do fechamento + 0,2% no fracionário"}]
APLICAVEL = True
MOTIVO = "blue chips no fracionário; 12 entradas por ano de 3 pregões; vendas do mês ~R$ 18 mil com R$ 20 mil (isento)"
ALAVANCAGENS = [1, 1.5, 2]
MOTIVO_ALAV = "posição de 3 pregões em blue chips: 1,5–2x com termo/garantia em Tesouro Selic (custo do excedente = CDI, sem spread — premissa)"
_CACHE = BB.Cache()


def vencimentos():
    """Vencimentos mensais de opções de ações (regra da B3, conhecida com antecedência)."""
    out = []
    for m in pd.period_range("2014-01", DIAS[-1].strftime("%Y-%m"), freq="M"):
        d0 = m.to_timestamp()
        dow = 0 if d0 < pd.Timestamp("2021-05-01") else 4                  # segunda até abr/2021, sexta depois
        dd = pd.date_range(d0, d0 + pd.Timedelta(days=27))
        v = dd[dd.dayofweek == dow][2]
        i = DIAS.searchsorted(v)
        if i < len(DIAS):
            out.append(DIAS[i])
    return pd.DatetimeIndex(out)


def carrega():
    a = BB.acoes()
    cols = sorted({t for c in CESTAS.values() for t in c})
    return {k: a[k][cols] for k in ("P", "R", "V", "BID", "ASK", "HS")}


def roda(d, capital=20000, custo_mult=1, lag=0, alavancagem=1, k=3, cesta="6", frac=.90):
    k = int(round(k))
    key = (id(d), capital, custo_mult, lag, alavancagem, k, cesta, round(frac, 4))

    def f():
        fim_dados = d["P"].dropna(how="all").index.max()
        tks = CESTAS[cesta]
        ev = [(DIAS[DIAS.get_loc(v) - 1], t, f"vencimento {v:%Y-%m-%d}") for v in vencimentos()
              if DIAS.get_loc(v) >= 1 and DIAS[DIAS.get_loc(v) - 1] <= fim_dados for t in tks]
        ev = pd.DataFrame(ev, columns=["data", "ticker", "rotulo"])
        res = BB.episodios(ev, d, capital, k, frac * capital * alavancagem / len(tks), custo_mult, lag, alavancagem, vol_min=10)
        res["negocios"] = BB.rotula(res["negocios"], ev)
        return res
    return _CACHE.get(key, f)


def excesso(d, capital=20000, custo_mult=1, lag=0, regime=REGIME, alavancagem=1, **params):
    e = roda(d, capital, custo_mult, lag, alavancagem, **{**PARAMS, **params})["e"]
    return C.aplica_regime(e, regime, CUSTO_TROCA * custo_mult)


def classes_ir(d, capital=20000, **params):
    return B.classes_acoes(roda(d, capital, **{**PARAMS, **params}))


def posicoes(d, capital=20000, **params):
    W = roda(d, capital, **{**PARAMS, **params})["W"]
    return W, d["R"].reindex(index=DIAS, columns=W.columns).fillna(0).sub(BB.CDI, axis=0)


def negocios(d, capital=20000, **params):
    return roda(d, capital, **{**PARAMS, **params})["negocios"]


if __name__ == "__main__":
    import time
    d = carrega()
    for kw in [{"k": k, "cesta": c} for k in GRADE["k"] for c in GRADE["cesta"]]:
        t = time.time()
        e = excesso(d, **kw)
        print(kw, "IS %.2f OOS %.2f (%.0fs)" % (C.anual(e[INICIO:CORTE]), C.anual(e[CORTE:]), time.time() - t), flush=True)
    e = excesso(d, capital=50000)
    print("50k IS %.2f OOS %.2f" % (C.anual(e[INICIO:CORTE]), C.anual(e[CORTE:])))
