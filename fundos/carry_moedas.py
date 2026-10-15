"""
Carry de moedas G10 + emergentes (versão auditada).

Tese de mesa: o mercado paga para quem financia moedas de juro baixo (JPY, CHF...) e aplica em moedas de juro alto (MXN, BRL...).
Todo fim de mês compramos as 3 moedas de maior carry e vendemos as 3 de menor carry contra o dólar, com peso pelo inverso da vol,
carteira escalada para 8% de vol, teto de 25% do PL por moeda (aplicado DEPOIS do vol-alvo). O resultado em dólar (excesso sobre
o juro americano) vira excesso sobre o CDI com hedge cambial (comum.brl).

Carry "realista" = o que o forward/NDF de fato paga, não a taxa de política pura:
  - G10: diferencial de política BIS (moeda - EUA);
  - EM entregável (MXN, ZAR, PLN, HUF, CZK, ILS): BIS - 0,5 pp (forward points pagam menos que a política);
  - NDF asiáticos/latinos: 50% do diferencial BIS;
  - TRY: diferencial x try_hc (haircut; o fundo escolheu 0 no IS = TRY entra no ranking com carry zero);
  - BRL: CDI - cupom cambial do 1º FRC da B3 (2019+); antes de 2019, Selic - FF (BIS) - 1,07 pp (spread médio medido em 2019+;
    é uma constante estimada depois, herdada do fundo auditado).
Custos por giro: G10 2 bps, EM 10, NDF 20, TRY 30, BRL 10.

Dados (dados/carry_moedas/, já prontos no repositório):
  fx_usd_por_moeda.parquet  USD por 1 unidade de cada moeda (Yahoo). A LIMPEZA DE ERROS DO YAHOO FOI FEITA NA EXPORTAÇÃO, com a
                            mesma regra do fundo de referência: (1) salto em log > 8% que se desfaz em até 8 dias vira o último nível
                            bom (COP jun/2015 a 26,2, IDR 2013, NOK mar/2020...); (2) retorno diário > 4% que se desfaz no dia
                            seguinte (resíduo < 30%) vira retorno zero nos dois dias. Crises de verdade (CHF jan/2015, TRY) ficam.
                            Essa limpeza olha o futuro por construção (precisa ver o erro se desfazer) — é tratamento de dado, não sinal.
  bis_juros_politica.csv    taxa de política do BIS (% a.a.).
  cupom_frc.csv             cupom cambial do 1º FRC (% a.a.).

Calendário: o livro roda no calendário dos EUA (comum.DIAS_US), decide no fechamento de t, executa em t+1(+lag), rende de t+2.
"""
import numpy as np
import pandas as pd

import comum
from comum import DIAS, DIAS_US, aplica_regime, brl, ler, mensal, vol_alvo

NOME = "Carry de moedas G10 + emergentes"
TESE = "Compra as 3 moedas de maior carry e vende as 3 de menor (forward/NDF realista; BRL = CDI - cupom), inverso da vol, vol-alvo 8%"
BENCHMARK = "CDI"
INICIO, CORTE = "2010-01-01", "2021-01-01"
REGIME = "dd_stop"
CUSTO_TROCA = .001
PARAMS = {"n": 3, "try_hc": 0.0}
GRADE = {"n": [3, 4], "try_hc": [.5, 0.0]}
VIZINHANCA = {"n": (2, 5), "try_hc": (0.0, .5)}

ALVO, TETO = .08, .25          # vol-alvo da carteira e teto por moeda
SPREAD_CUPOM_BRL = .0107       # cupom curto - SOFR médio medido em 2019+ (usado só antes de 2019)

# moeda (Yahoo) -> (país no BIS, tipo)
MOEDAS = {"EURUSD=X": ("XM", "G10"), "GBPUSD=X": ("GB", "G10"), "AUDUSD=X": ("AU", "G10"), "NZDUSD=X": ("NZ", "G10"),
          "JPY=X": ("JP", "G10"), "CAD=X": ("CA", "G10"), "CHF=X": ("CH", "G10"), "NOK=X": ("NO", "G10"), "SEK=X": ("SE", "G10"),
          "MXN=X": ("MX", "EM"), "ZAR=X": ("ZA", "EM"), "PLN=X": ("PL", "EM"), "HUF=X": ("HU", "EM"), "CZK=X": ("CZ", "EM"),
          "ILS=X": ("IL", "EM"), "TRY=X": ("TR", "TRY"), "INR=X": ("IN", "NDF"), "IDR=X": ("ID", "NDF"), "KRW=X": ("KR", "NDF"),
          "CLP=X": ("CL", "NDF"), "COP=X": ("CO", "NDF"), "THB=X": ("TH", "NDF"), "PHP=X": ("PH", "NDF"), "CNY=X": ("CN", "NDF"),
          "BRL=X": ("BR", "BRL")}
CUSTO = {"G10": .0002, "EM": .0010, "NDF": .0020, "TRY": .0030, "BRL": .0010}


def carrega():
    return {"fx": ler("carry_moedas/fx_usd_por_moeda.parquet"),
            "bis": ler("carry_moedas/bis_juros_politica.csv"),
            "cupom": ler("carry_moedas/cupom_frc.csv")["cupom_frc_aa_pct"]}


# ---------------------------------------------------------------- carry por moeda (fração a.a., comprado na moeda contra USD)
def carry_brl(d):
    """Quem fica comprado em real via DOL/NDF recebe CDI - cupom cambial; antes de haver cupom, Selic - FF - 1,07 pp."""
    cup = d["cupom"].reindex(DIAS).ffill(limit=5) / 100
    b3 = (1 + comum.CDI) ** 252 - 1 - cup
    i = d["bis"].reindex(DIAS).ffill()
    bis = (i["BR"] - i["US"]) / 100 - SPREAD_CUPOM_BRL
    ini = b3.first_valid_index()
    if ini is None:                       # período sem cupom da B3 (ex.: dados cortados antes de 2019)
        return bis
    return b3.combine_first(bis.where(b3.index < ini))


def carry(d, try_hc=0.0):
    i = d["bis"].reindex(DIAS_US).ffill()
    out = {}
    for k, (pais, tipo) in MOEDAS.items():
        dif = (i[pais] - i["US"]) / 100
        if tipo == "EM":
            dif = dif - .005 * np.sign(dif)
        elif tipo == "NDF":
            dif = dif * .5
        elif tipo == "TRY":
            dif = dif * try_hc
        elif tipo == "BRL":
            b = carry_brl(d)
            dif = b.reindex(DIAS_US.union(b.index)).ffill().reindex(DIAS_US).combine_first(dif * .7)
        out[k] = dif
    return pd.DataFrame(out).reindex(DIAS_US)


# ---------------------------------------------------------------- livro
def _livro(d, n=3, try_hc=0.0):
    """Pesos-alvo W (decididos em t), retorno em excesso R = spot + carry, e as duas partes separadas."""
    spot = d["fx"].reindex(DIAS_US).ffill(limit=5).pct_change(fill_method=None)[list(MOEDAS)]
    dif = carry(d, try_hc)
    car = dif.shift(1) / 252
    R = (spot + car).dropna(how="all")
    # ranking pelo carry: +1 nas n maiores, -1 nas n menores
    rk = dif.rank(axis=1, ascending=False)
    W = (rk <= n).astype(float) - ((rk > dif.notna().sum(axis=1).values[:, None] - n) & dif.notna()).astype(float)
    # inverso da vol (63d), soma |w| = 1; vol-alvo; rebalanceamento mensal; teto por moeda depois do vol-alvo
    vol = spot.rolling(63, min_periods=40).std()
    W = (W / vol).div((W / vol).abs().sum(axis=1).replace(0, np.nan), axis=0).fillna(0)
    W = mensal(vol_alvo(W, R.fillna(0), ALVO)).clip(-TETO, TETO)
    return W, R, spot, car


def _executa(W, R, custo_mult=1, lag=0):
    """W decidido em t, executado em t+1+lag, rende de t+2+lag. Devolve pesos executados e contribuição diária por moeda (USD)."""
    R = R.fillna(0)
    We = W.reindex(index=R.index, columns=R.columns).fillna(0).shift(1 + lag).fillna(0)
    custo = pd.Series({k: CUSTO[MOEDAS[k][1]] for k in R.columns})
    C = We.shift(1).fillna(0) * R - We.diff().abs().fillna(We.abs()) * custo * custo_mult
    return We, C


def excesso(d, custo_mult=1, lag=0, regime=REGIME, **params):
    p = {**PARAMS, **params}
    W, R, _, _ = _livro(d, **p)
    _, C = _executa(W, R, custo_mult, lag)
    return aplica_regime(brl(C.sum(axis=1)), regime, CUSTO_TROCA * custo_mult)


def posicoes(d, **params):
    """W: pesos-alvo decididos em t; R: excesso diário por moeda em USD (spot + carry). Calendário dos EUA. Sem regime."""
    W, R, _, _ = _livro(d, **{**PARAMS, **params})
    return W, R.fillna(0)


def negocios(d, **params):
    """Um episódio contínuo de posição (mesmo lado) por moeda. Sem regime; contribuição em USD (pp do PL), líquida de custo."""
    W, R, spot, car = _livro(d, **{**PARAMS, **params})
    We, C = _executa(W, R)
    spot, car = spot.reindex(R.index).fillna(0), car.reindex(R.index).fillna(0)
    lin, idx = [], We.index
    for c in We.columns:
        s = np.sign(We[c].values)
        mud = np.flatnonzero(np.diff(np.r_[0, s]) != 0)
        for k, i0 in enumerate(mud):
            if s[i0] == 0:
                continue
            i1 = mud[k + 1] if k + 1 < len(mud) else len(s)
            seg = slice(i0 + 1, min(i1 + 1, len(s)))          # rende do dia seguinte à execução até o dia da saída
            lado = int(s[i0])
            lin.append({"ativo": c, "lado": lado, "entrada": idx[i0], "saida": idx[min(i1, len(s) - 1)], "dias": int(i1 - i0),
                        "peso_medio": float(np.abs(We[c].values[i0:i1]).mean()),
                        "retorno_spot_%": (np.prod(1 + lado * spot[c].values[seg]) - 1) * 100,
                        "carry_%": lado * car[c].values[seg].sum() * 100,
                        "retorno_%": (np.prod(1 + lado * R[c].fillna(0).values[seg]) - 1) * 100,
                        "contrib_pp": C[c].values[seg].sum() * 100})
    return pd.DataFrame(lin).sort_values(["entrada", "ativo"]).reset_index(drop=True)
