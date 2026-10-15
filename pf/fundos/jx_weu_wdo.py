"""
Euro/dólar pela B3, sem remessa: mini-euro (WEU) contra mini-dólar (WDO), pelo ciclo RELATIVO de juros Fed x BCE.

Tese de mesa: o par EUR/USD anda na direção do diferencial de política monetária esperado; os bancos centrais andam em ciclos longos
(passos de 25 bp, sinalizados) e o câmbio demora a precificar o ciclo inteiro (2014–15 BCE em QE e Fed saindo do zero: euro de 1,39 a
1,05; 2017 BCE "tapering" e Fed parando; 2022 Fed muito mais rápido: euro abaixo de 1,00; 2024–25 Fed cortando: euro a 1,17). Quem paga:
empresas e gestores que fazem hedge por calendário/contabilidade, não por visão, e bancos centrais de reservas que rebalanceiam devagar.
O veículo é o que interessa ao PF: 1 WEU (EUR 10 mil) comprado + 1 WDO (USD 10 mil) vendido = ~EUR 10 mil de EUR/USD, tudo na B3, em R$,
garantia em Tesouro Selic rendendo CDI — sem IOF de remessa (1,1%), sem saldo parado na IBKR, IR de futuros B3 (15%, compensa no mês).
O carry do par (juro do euro - juro do dólar) entra no ajuste dos dois futuros.

Implementação:
  - sinal: variação em `janela` pregões do diferencial de juro de política (Fed funds alvo - taxa do BCE, BIS diário). Diferencial CAINDO
    (Fed cortando relativo ao BCE) >= 25 bp -> comprado em euro (WEU comprado, WDO vendido); SUBINDO >= 25 bp -> vendido em euro.
    `modo`="ciclo_tend": só se o EUR/USD estiver do mesmo lado da média de 63 pregões (o mercado confirma); "tend": só tendência;
  - preços: WDO = DOL rolado da B3 (2019+) / sintético antes; WEU sintético (não há histórico baixado do WEU): retorno de EUR/BRL
    (EUR/USD do Yahoo x PTAX) - (CDI - cupom do euro)/252, cupom do euro = taxa do BCE + 1,07 pp (mesma base de conversibilidade do
    cupom cambial do dólar). Na perna do par a PTAX quase cancela (preços não simultâneos só afetam o ruído diário);
  - contratos: n pares = arred(capital x alavancagem / nocional do WEU), mínimo 1 (1 par ~ R$ 60–65 mil: 3x o capital de R$ 20 mil,
    1,2x o de R$ 50 mil); sobra de ~USD 1 mil comprado (EUR 10 mil x 1,1 - USD 10 mil) entra no P&L;
  - custo por lado: WDO R$ 3,70; WEU R$ 6 (livro raso: emolumentos + ~2,5 ticks de R$ 1); rolagem mensal dos dois (1º dia útil);
  - IR futuros B3 15%.
Dados: EUR/USD (Yahoo) 2005+, PTAX, BIS (política monetária diária), DOL B3 2019+. Corte OOS 2021-01-01.
"""
import numpy as np
import pandas as pd

import jx_comum as J

NOME = "Euro x dólar na B3 (WEU vs WDO) pelo ciclo Fed x BCE"
TESE = ("Compro euro contra dólar (WEU comprado, WDO vendido) quando o Fed corta relativo ao BCE e vendo no contrário, confirmado pela "
        "tendência; tudo na B3 em R$, sem remessa nem saldo na IBKR")
BENCHMARK = "CDI"
INICIO, CORTE = "2008-06-01", "2021-01-01"
REGIME = "nenhum"
CUSTO_TROCA = 0.0
PARAMS = {"janela": 252, "modo": "ciclo", "minimo": 1}           # maior IS (2008-2020)
GRADE = {"janela": [126, 252], "modo": ["ciclo", "ciclo_tend", "tend"]}
VIZINHANCA = {"janela": (90, 300)}
CLASSE_IR = "futuros_b3"
CUSTO_WDO, CUSTO_WEU, BASE = 3.70, 6.0, .0107
INSTRUMENTOS = [{"onde": "B3", "ticker": "WEU (mini-euro, EUR 10 mil)", "lote": "1 contrato", "custo": "R$ 6 por lado (livro raso), rolagem mensal"},
                {"onde": "B3", "ticker": "WDO (mini-dólar, USD 10 mil)", "lote": "1 contrato", "custo": "R$ 3,70 por lado, rolagem mensal"}]
APLICAVEL = True
MOTIVO = ("1 par WEU/WDO = ~R$ 60–65 mil de EUR/USD: com R$ 20 mil é 3x o capital (vol ~20% a.a. do capital); com R$ 50 mil, ~1,2x. "
          "WEU tem pouca liquidez (poucos contratos/dia): ordem limitada no meio do livro.")
ALAVANCAGENS = [1, 2]
MOTIVO_ALAV = "2x = 2 pares por R$ de capital (mínimo 2); 5x com R$ 20 mil = 5 pares (~R$ 320 mil) — EUR/USD -5% custaria 80% do capital."


def carrega():
    return {"mkt": J.mercado()}


def precos(d):
    def f():
        eu = J.serie(d, "eurusd")
        eurbrl = eu * J.PTAX
        pol_eur = J.serie(d, "pol_eur", limit=40).ffill() / 100
        r_weu = eurbrl.pct_change(fill_method=None).fillna(0) - (J.CDI - (pol_eur + BASE) / 252)
        r_wdo, noc_wdo = J.wdo(d)
        return r_weu.fillna(0), 10_000 * eurbrl, r_wdo, noc_wdo
    return J.memo("weu", d["mkt"], f)


def _sinal(d, janela, modo):
    dif = (J.serie(d, "pol_usd", limit=40) - J.serie(d, "pol_eur", limit=40)).ffill()
    ddif = dif - dif.shift(int(janela))
    eu = J.serie(d, "eurusd")
    tend = np.sign(eu - eu.rolling(63, min_periods=40).mean())
    ciclo = pd.Series(np.where(ddif <= -.25, 1, np.where(ddif >= .25, -1, 0)), index=J.DIAS)
    if modo == "ciclo":
        s = ciclo
    elif modo == "tend":
        s = tend.fillna(0)
    else:
        s = ciclo.where(ciclo == tend, 0)
    fim = d["mkt"].index.max()
    return s.where(pd.Series(J.DIAS <= fim, index=J.DIAS), 0).astype(float)


def _livro(d, capital=20000, custo_mult=1, lag=0, alavancagem=1, janela=PARAMS["janela"], modo=PARAMS["modo"], minimo=PARAMS["minimo"]):
    s = _sinal(d, janela, modo)
    r_weu, noc_weu, r_wdo, noc_wdo = precos(d)
    n = J.contratos_inteiros(s * capital * alavancagem, noc_weu, minimo=minimo * max(1, int(round(alavancagem))) if minimo else 0)
    rm = J.primeiro_util_do_mes()
    a = J.futuro_livro(n, r_weu, noc_weu, CUSTO_WEU, capital, lag, custo_mult, rm)
    b = J.futuro_livro(-n, r_wdo, noc_wdo, CUSTO_WDO, capital, lag, custo_mult, rm)
    return {"e": a["e"] + b["e"], "pnl": a["pnl"] + b["pnl"], "pos": a["pos"], "s": s}


def excesso(d, capital=20000, custo_mult=1, lag=0, regime=REGIME, alavancagem=1, **params):
    L = _livro(d, capital, custo_mult, lag, alavancagem, **{**PARAMS, **params})
    return J.C.aplica_regime(L["e"], regime, CUSTO_TROCA * custo_mult)


def classes_ir(d, capital=20000, **params):
    return {CLASSE_IR: _livro(d, capital, **{**PARAMS, **params})["pnl"]}


def posicoes(d, capital=20000, **params):
    L = _livro(d, capital, **{**PARAMS, **params})
    r_weu, noc_weu, r_wdo, noc_wdo = precos(d)
    n = L["pos"].shift(-1).fillna(0)
    W = pd.DataFrame({"WEU": n * noc_weu / capital, "WDO": -n * noc_wdo / capital}).fillna(0)
    return W, pd.DataFrame({"WEU": r_weu, "WDO": r_wdo})


def negocios(d, capital=20000, **params):
    L = _livro(d, capital, **{**PARAMS, **params})
    s = L["s"]
    out = []
    for lado in (1, -1):
        ng = J.negocios_de_estado(s == lado, L["e"], "EUR/USD (WEU-WDO)", lado=lado)
        out.append(ng)
    ng = pd.concat(out, ignore_index=True).sort_values("entrada").reset_index(drop=True) if out else pd.DataFrame()
    if len(ng):
        eu = J.serie(d, "eurusd")
        ng["eurusd_entrada"] = [eu.get(a) for a in ng.entrada]
        ng["eurusd_saida"] = [eu.get(b) for b in ng.saida]
    return ng
