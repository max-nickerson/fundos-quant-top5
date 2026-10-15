"""
Argentina no pânico: ADRs (YPF, GGAL, BMA, PAM, CEPU) comprados quando a cesta despenca em semanas, escolhendo pelo CCL implícito.

Tese de mesa: Argentina é o mercado de pânicos (PASO 2019 −50% num dia, cepo, Guzmán 2022, Buenos Aires set/2025). Quem vende o ADR
no pânico é o estrangeiro que precisa sair (resgate de fundo EM/fronteira, stop, margem); o argentino que compra o ADR com pesos via
"contado con liqui" (CCL) chega depois. Pelo CCL implícito de cada ação (preço em pesos x razão / ADR) dá para ver QUAL ADR o estrangeiro
vendeu mais: o ADR com CCL implícito acima dos outros está barato contra a própria ação local. "Só nos pânicos": a pesquisa
institucional (G7) operava o desvio de CCL todo dia, L/S, e o custo comia tudo; aqui o CCL é só o critério de escolha dentro do pânico.

Pânico = cesta igual dos ADRs disponíveis cai mais que `queda` do topo de 21 pregões. Compro `peso` do capital (metade em cada um dos 2–3
ADRs de CCL mais alto, ou a cesta) e saio em `dias`. Sem hedge: o que se compra é a volta do pânico argentino (beta Argentina). O beta
contra o EEM é medido no caderno.

PF: ADRs na IBKR (fração), pequenos (R$ 10 mil com 20k). Os pregões de Buenos Aires e NY fecham quase juntos (17h BA = 16h NY), então o
CCL implícito é quase simultâneo (diferente de Ásia). Razões ADR/local: YPF 1, GGAL 10, BMA 10, PAM 25, CEPU 10 (folhetos dos
depositários; o YPFD.BA do Yahoo vem em escala 1/10 contra o oficial — constante, some no desvio); as razões ficaram estáveis em todo o período (CCL implícito igual entre os 5 nomes ano a ano), sem filtro de salto.
"""
import numpy as np
import pandas as pd

import em_comum as E

NOME = "Argentina no pânico: cesta de ADRs (CCL implícito testado na grade) (IBKR)"
TESE = ("Compro a cesta de ADRs argentinos quando ela cai > 20% em 21 pregões (estrangeiro vendendo à força); a escolha pelo CCL "
        "implícito (ADR barato contra a ação em pesos) perdeu no IS; saio em 63 pregões")
BENCHMARK = "CDI"
INICIO, CORTE = "2012-01-01", "2021-01-01"
REGIME = "nenhum"
CUSTO_TROCA = .001
CLASSE_IR = "exterior"
ADRS = ["YPF", "GGAL", "BMA", "PAM", "CEPU"]
PARAMS = {"queda": .20, "dias": 63, "escolha": "cesta", "n": 3, "peso": .5}   # escolhido no IS (maior IR IS)
GRADE = {"queda": [.20, .30], "dias": [21, 63], "escolha": ["ccl", "cesta"]}
VIZINHANCA = {"queda": (.15, .27), "dias": (40, 90), "peso": (.35, .65)}
INSTRUMENTOS = ("IBKR: ADRs YPF, GGAL, BMA, PAM, CEPU (compra fracionária, US$ 0,0035/ação mín. US$ 0,35). Na B3 não há BDR desses ADRs "
                "(ver COTAHIST). Ações locais (.BA) só como DADO para o CCL implícito (PF brasileiro não opera BYMA).")
APLICAVEL = True
MOTIVO = "Operável: R$ 10 mil (20k) / 25 mil (50k) em 2–5 ADRs líquidos (YPF/GGAL > US$ 50 mi/dia). Custo fixo = remessa (IOF) por pânico."
ALAVANCAGENS = [1, 1.5, 2]
MOTIVO_ALAV = "L multiplica o peso (50% -> 75%/100%). 5x seria 250% em ADRs de vol 60–80%: quebra num PASO 2019."


def carrega():
    return E.seleciona(ADRS + [E.ARG_ADR[a][0] for a in ADRS] + ["ARS=X"])


def ccl_desvio(d, jan=60):
    """Desvio do CCL implícito de cada ADR contra a mediana dos outros, menos a média dos últimos `jan` dias (só passado)."""
    adj = d["adj"].ffill(limit=3)
    ok = d["raw"][ADRS].notna() & d["raw"][[E.ARG_ADR[a][0] for a in ADRS]].notna().to_numpy()
    c = pd.DataFrame({a: np.log(adj[E.ARG_ADR[a][0]] * E.ARG_ADR[a][1] / adj[a]) for a in ADRS})
    c = c.where(ok)
    dev = c.sub(c.median(axis=1), axis=0)
    return dev - dev.rolling(jan, min_periods=jan // 2).mean().shift(1)


def _pesos(d, queda, dias, escolha, n, peso):
    P = E.preco_usd(d)[ADRS]
    neg = E.negociou(d)[ADRS]
    r = P.pct_change(fill_method=None).where(neg)
    cesta = (1 + r.mean(axis=1).fillna(0)).cumprod()
    dd = cesta / cesta.rolling(21, min_periods=10).max() - 1
    ent = (dd <= -queda).to_frame("ARG")
    est = E.maquina(ent, pd.DataFrame(False, index=ent.index, columns=["ARG"]), dias, espera=10)["ARG"]
    inicio = (est > 0) & (est.shift(1).fillna(0) <= 0)
    disp = neg & P.notna()
    if escolha == "ccl":
        s = ccl_desvio(d)
        rk = s.where(disp).rank(axis=1, ascending=False)
        sel = (rk <= n).astype(float)
        sel = sel.where(sel.sum(axis=1) > 0, disp.astype(float))          # sem CCL (dado faltando): cesta
    else:
        sel = disp.astype(float)
    w0 = sel.div(sel.sum(axis=1).replace(0, np.nan), axis=0).fillna(0) * peso
    W = w0.where(inicio).ffill().mul(est, axis=0).fillna(0)                # escolha congelada na entrada
    return W, {}


def _ajuste(d, res, capital, alavancagem, **p):
    return res


excesso, classes_ir, posicoes, negocios = E.contrato(__import__(__name__))
