"""
Prêmio de hedge do produtor: COMPRADO em milho B3 (CCM), 1 contrato, garantia em Tesouro Selic.

Tese de mesa (Keynes/Hicks, "normal backwardation"): o produtor e a trading vendem futuro para travar o preço da safra e pagam um
prêmio a quem carrega o risco comprado. Na pesquisa (commodities.md, C5) quem ficou comprado nos futuros agro da B3 ganhou ~8% a.a. de
excesso (BGI, CCM), 15% (ICF), 10% (ETH) em 2018–2026 — qualquer sinal vendido pagava esse prêmio. A pessoa física é um dos poucos
agentes sem estoque físico que pode ser a contraparte natural do hedge do produtor em tamanho pequeno.

O que cabe: só o milho. CCM = 450 sacas (R$ 25–35 mil); boi (BGI, 330 @ ≈ R$ 100 mil), café (ICF, 100 sacas ≈ R$ 150–200 mil),
soja Chicago (SJC ≈ R$ 55 mil) e etanol (ETH, 30 m³ ≈ R$ 90 mil) são grandes demais para R$ 20–50 mil sem alavancagem de 2–10x.
Sem contrato mini de agro na B3.

Filtros (grade): sempre; curva (só comprado quando a curva não está em contango forte: ln(F1/F2) anualizado > piso — contango
forte = estoque sobrando, o comprado paga a armazenagem); tendência (preço rolado acima da média de 100d: choques de estoque
persistem); safra (fora de jun–ago, colheita da safrinha, quando a venda física pressiona a base).
Implementação: contrato de vencimento mais próximo (vence no dia 15 do mês do contrato), rolado 10 pregões antes; P&L pela variação
do ajuste do MESMO contrato; 1 contrato (n = max(1, arred(capital x alav / nocional))). Custo R$ 6/contrato/lado (emolumentos + meio
tick) + rolagem. IR: "futuros_b3". Dados agro B3 2018+ (deduplicados: o arquivo tem cada linha repetida até 6x) -> corte 2023.
"""
import numpy as np
import pandas as pd

import db3_base as B

NOME = "Milho B3 (CCM) comprado — prêmio de hedge do produtor"
TESE = "Compro 1 contrato de milho B3 para receber o prêmio que o produtor paga pelo hedge; filtros de curva / tendência / safra"
BENCHMARK = "CDI"
INICIO, CORTE = "2018-06-01", "2023-01-01"
REGIME, CUSTO_TROCA = "nenhum", 0.0
PARAMS = {"filtro": "curva", "curva_min": -.10, "janela": 100}   # maior IR no IS (2018–2022) da GRADE
GRADE = {"filtro": ["sempre", "curva", "tendencia", "safra"]}
VIZINHANCA = {"curva_min": (-.2, 0.0), "janela": (60, 150)}
CLASSE_IR = "futuros_b3"
MULT, CUSTO_LADO = 450.0, 6.0
INSTRUMENTOS = [{"onde": "B3", "ticker": "CCM (milho, vencimentos F/H/K/N/U/X)", "lote": "1 contrato = 450 sacas (R$ 25–35 mil)",
                 "custo": "R$ 6/contrato/lado + rolagem ~6x/ano"},
                {"onde": "Tesouro Direto / B3", "ticker": "Tesouro Selic (margem ~R$ 2–3 mil/contrato)", "lote": "R$ ~170", "custo": "igual ao benchmark"}]
APLICAVEL = True
MOTIVO = ("Cabe: 1 CCM ≈ R$ 25–35 mil de nocional (1,3–1,7x com R$ 20 mil; 0,6x com R$ 50 mil), margem ~R$ 2–3 mil em Selic. Os outros "
          "agro (BGI, ICF, SJC, ETH) não cabem.")
ALAVANCAGENS = [1, 1.5, 2]
MOTIVO_ALAV = "Com R$ 20 mil, 1 contrato já é ~1,5x; 2 contratos (≈3x) só com R$ 50 mil seria 1,2x. 5x não cabe na vol do milho (~25% a.a.)."


def venc_ccm(t):
    a, m = 2000 + int(t[4:6]), "FGHJKMNQUVXZ".index(t[3]) + 1
    x = B.DIAS[B.DIAS <= pd.Timestamp(a, m, 15)]
    return x[-1] if len(x) and x[-1].month == m else pd.Timestamp(a, m, 15)


def carrega():
    return {"ccm": B.futuros(["CCM"], arquivo="agro")}


def _serie(d):
    return B.memo("ccm_sr", d["ccm"], lambda: B.serie_rolada(d["ccm"], venc_ccm, antes=10))


def _livro(d, capital, lag, custo_mult, alavancagem, p):
    sr = _serie(d)
    noc = (sr.ajuste * MULT).ffill(limit=5)                           # dia sem ajuste (feriado só na B3) não zera a posição
    ret = (sr.dP / sr.ajuste.shift(1)).fillna(0)
    on = noc.notna()
    if p["filtro"] == "curva":
        dt = (sr.faltam2 - sr.faltam) / 252
        on &= (np.log(sr.ajuste / sr.ajuste2) / dt > p["curva_min"]).fillna(False)
    elif p["filtro"] == "tendencia":
        idx = (1 + ret).cumprod()
        on &= (idx > idx.rolling(int(p["janela"]), min_periods=int(p["janela"] * .8)).mean()).fillna(False)
    elif p["filtro"] == "safra":
        on &= ~pd.Series(B.DIAS.month.isin([6, 7, 8]), index=B.DIAS)
    n = np.maximum(1, np.round(capital * alavancagem / noc)).where(on, 0).fillna(0)
    pnl, ne, custo = B.livro_futuro(n, sr, MULT, CUSTO_LADO, lag, custo_mult)
    return pnl, ne, noc, ret


def excesso(d, capital=20000, custo_mult=1, lag=0, regime=REGIME, alavancagem=1, **params):
    pnl, *_ = _livro(d, capital, lag, custo_mult, alavancagem, {**PARAMS, **params})
    return B.fecha(pnl / capital, regime, CUSTO_TROCA, custo_mult)


def classes_ir(d, capital=20000, **params):
    pnl, *_ = _livro(d, capital, 0, 1, 1, {**PARAMS, **params})
    return {CLASSE_IR: pnl}


def posicoes(d, capital=20000, **params):
    pnl, ne, noc, ret = _livro(d, capital, 0, 0, 1, {**PARAMS, **params})
    return B.wr_futuro(ne, noc.ffill(), ret, capital, "CCM")


def negocios(d, capital=20000, **params):
    pnl, ne, noc, _ = _livro(d, capital, 0, 1, 1, {**PARAMS, **params})
    ng = B.blocos(ne, pnl, "CCM", capital, ne.abs() * noc)
    if len(ng) <= 3:                                     # comprado quase sempre: quebra o negócio em cada rolagem (vencimento)
        sr = _serie(d)
        ng = []
        for t, g in pnl[ne.shift(1).fillna(0) != 0].groupby(sr.ticker.shift(1).reindex(pnl.index)):
            ng.append(dict(ativo="CCM " + t, lado=1, entrada=g.index[0], saida=g.index[-1], pnl_rs=float(g.sum()),
                           **{"retorno_%": float(g.sum() / (noc.reindex(g.index).mean() * ne.shift(1).reindex(g.index).abs().mean()) * 100)}))
    return B.negocios_df(ng, capital)
