"""
FII na data-com: o varejo que COMPRA para receber o rendimento (isento para PF) — frente "pf2_b3".

Mesa: o investidor de FII é quase todo pessoa física e compra "para pegar o rendimento" nos últimos pregões antes da data-com (último
pregão do mês para a maioria dos FIIs de tijolo/papel grandes). É um comprador que não olha preço — no estudo de evento (FIIs com ADV
>= R$ 2 mi, 2017–2020) os 3 últimos pregões do mês rendem +0,27% contra +0,12% de um período normal de 3 pregões; em 2021–26 +0,38%
contra +0,05%. Compro uma cesta dos FIIs líquidos `k` pregões antes da data-com e vendo:
  - saida="com": no fechamento da própria data-com (vendo para quem quer o rendimento, sem receber o rendimento);
  - saida="ex": no 1º pregão seguinte (recebo o rendimento — ISENTO para PF — e realizo a queda ex como prejuízo de FII, que compensa
    ganhos de FII a 20%).
Execução: decide no fechamento de t, executa no fechamento de t+1+lag, cotas inteiras (lote de FII = 1 cota, sem custo extra de
fracionário), custo = emolumentos 0,03% + meio spread REAL do fechamento (oferta de compra/venda do COTAHIST). Dinheiro em FII não rende CDI.
Dados: COTAHIST bruto (CODBDI 12) + rendimento do informe mensal CVM (pago no 1º pregão do mês seguinte; ver bb_base). FIIs com data-com
em outro dia do mês só diluem o efeito (o rendimento deles cai no dia certo do mês na média, mas não na data-com).
Obs.: o estudo acima ainda incluía ETFs (ESPECI CI); só com FIIs a grade escolheu k=10 na data-com (IS +8,4, OOS −2,0 pp).
IR: CLASSE_IR = "fii" (20% sobre TODO o excesso, inclusive o rendimento) — conservador para saida="ex", em que o rendimento é isento.
"""
import numpy as np
import pandas as pd

import bb_base as BB

B, C, pf = BB.B, BB.C, BB.pf
DIAS = BB.DIAS

NOME = "FII na data-com (compra do varejo pelo rendimento)"
TESE = ("Compro FIIs líquidos k pregões antes da data-com (último pregão do mês) e vendo no fechamento da data-com para o varejo que compra "
        "para receber o rendimento; lote de 1 cota, spread real")
BENCHMARK = "CDI"
INICIO, CORTE = "2017-03-01", "2021-01-01"
REGIME = "nenhum"          # fluxo de calendário do varejo; sem razão econômica para regime
CLASSE_IR = "fii"
CUSTO_TROCA = .001
PARAMS = {"k": 10, "saida": "com", "n": 10, "adv_min": 2e6, "frac": .09}
GRADE = {"k": [3, 5, 10], "saida": ["com", "ex"]}
VIZINHANCA = {"k": (7, 14), "n": (6, 15), "adv_min": (1e6, 4e6)}
INSTRUMENTOS = [{"onde": "Clear/Rico/XP/Inter (corretagem zero)", "ticker": "FIIs líquidos (XXXX11), os n maiores ADV",
                 "lote": "1 cota", "custo": "emolumentos 0,03% + meio spread real do fechamento"}]
APLICAVEL = True
MOTIVO = "FIIs líquidos, cotas de R$ 10–150, R$ 1,8 mil por FII com R$ 20 mil; 12 ciclos por ano"
ALAVANCAGENS = [1]
MOTIVO_ALAV = "o fundo fica ~90% investido só 3–10 pregões por mês; alavancar = termo de FII (não disponível no varejo)"
_CACHE = BB.Cache()


def carrega():
    d = BB.fiis()
    return BB.com_hs(d)


def roda(d, capital=20000, custo_mult=1, lag=0, alavancagem=1, k=10, saida="com", n=10, adv_min=2e6, frac=.09):
    k, n = int(round(k)), int(round(n))
    key = (id(d), capital, custo_mult, lag, alavancagem, k, saida, n, adv_min, round(frac, 4))

    def f():
        dd = dict(d)
        dd["R"], _ = BB.fii_retorno(d)
        P = d["P"].reindex(DIAS)
        adv = d["V"].reindex(DIAS).fillna(0).rolling(60, min_periods=20).mean()
        mes = pd.Series(DIAS.to_period("M"), index=DIAS)
        ic = np.flatnonzero((mes != mes.shift(-1)).values)               # último pregão de cada mês (data-com), calendário conhecido
        fim_dados = P.dropna(how="all").index.max()
        ev = []
        for i in ic:
            dec = i - k                                                  # decide k pregões antes; compra em dec+1
            if dec < 60 or DIAS[dec] > fim_dados:
                continue
            a = adv.iloc[dec]
            a = a[(a >= adv_min) & P.iloc[dec].notna()].nlargest(n)
            fim = i - 1 if saida == "com" else i                         # decisão de saída -> executa na data-com (ou no dia ex)
            ev += [(DIAS[dec], t, DIAS[fim], f"data-com {DIAS[i]:%Y-%m-%d}") for t in a.index]
        ev = pd.DataFrame(ev, columns=["data", "ticker", "fim", "rotulo"])
        tam = frac * capital * alavancagem
        old = B.FRAC_EXTRA
        B.FRAC_EXTRA = 0.0                                               # FII negocia em lote de 1 cota
        try:
            res = BB.episodios(ev, dd, capital, None, tam, custo_mult, lag, alavancagem)
        finally:
            B.FRAC_EXTRA = old
        res["negocios"] = BB.rotula(res["negocios"], ev)
        res["R"] = dd["R"]
        return res
    return _CACHE.get(key, f)


def excesso(d, capital=20000, custo_mult=1, lag=0, regime=REGIME, alavancagem=1, **params):
    e = roda(d, capital, custo_mult, lag, alavancagem, **{**PARAMS, **params})["e"]
    return C.aplica_regime(e, regime, CUSTO_TROCA * custo_mult)


def classes_ir(d, capital=20000, **params):
    r = roda(d, capital, **{**PARAMS, **params})
    return {"fii": (r["pnl"] - r["custo"]), "_cdi_perdido": r["cdi_perdido"]}


def posicoes(d, capital=20000, **params):
    r = roda(d, capital, **{**PARAMS, **params})
    W = r["W"]
    return W, r["R"].reindex(index=DIAS, columns=W.columns).fillna(0).sub(BB.CDI, axis=0)


def negocios(d, capital=20000, **params):
    return roda(d, capital, **{**PARAMS, **params})["negocios"]


if __name__ == "__main__":
    import time
    d = carrega()
    for kw in [{"k": k, "saida": s} for k in GRADE["k"] for s in GRADE["saida"]]:
        t = time.time()
        e = excesso(d, **kw)
        print(kw, "IS %.2f OOS %.2f (%.0fs)" % (C.anual(e[INICIO:CORTE]), C.anual(e[CORTE:]), time.time() - t), flush=True)
