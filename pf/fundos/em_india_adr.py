"""
ADRs indianos x NSE (INFY, HDB, IBN, WIT, RDY): o prêmio estrutural do ADR e a volta quando ele sai do normal.

Tese de mesa: o estrangeiro de varejo não entra na NSE (precisa de registro FPI); o caminho é o ADR. A conversão é de mão única na
prática: ADR -> ação local é livre (prende o desconto perto de zero), ação local -> ADR depende de "headroom" (limite de participação
estrangeira, fungibilidade de duas vias limitada pelo RBI). Daí o PRÊMIO estrutural (HDB/IBN historicamente +5–20%, WIT às vezes +20%).
O prêmio dispara quando o estrangeiro compra com pressa (índice MSCI/ fluxo para "Índia via ADR") e desaba quando ele vende à força ou
quando o headroom abre (fusão HDFC 2023, aumento de limite). O PF não opera a NSE (IBKR Índia é só para residentes/NRIs): só a perna ADR.

Regra: prêmio p = log(ADR) − log(local x ações por ADR / INR), Adj Close dos dois (desdobramentos e proventos ajustados), média de 5 dias
(o fuso NSE 06h ET x NY 16h ET vira ruído de curto prazo); z = (p5 − média de `jan` dias)/desvio de `jan` dias, só passado.
z <= −z_in: compro o ADR (prêmio anormalmente baixo, o ADR foi vendido além da ação) e vendo INDA no mesmo valor (tira o beta Índia);
z >= z_in: vendo o ADR e compro INDA (lado vendido opcional). Saio quando z volta a 0 ou em `max_dias`. 25% do capital por ADR, no máximo 2 ao mesmo tempo (bruto <= 100% com o INDA; Reg T ~50%).
PF: ADR e INDA na IBKR (fração na compra, inteiro na venda; aluguel ADR ~1% a.a., INDA ~0,3%), conta margem (US$ 2.000) quando há vendido.
"""
import numpy as np
import pandas as pd

import em_comum as E

NOME = "ADRs indianos x NSE: prêmio fora do normal, hedge INDA (IBKR)"
TESE = ("O ADR indiano tem prêmio estrutural (conversão de mão única); quando o prêmio cai muito abaixo do normal compro o ADR e vendo "
        "INDA (e o contrário quando dispara); saio na volta do prêmio")
BENCHMARK = "CDI"
INICIO, CORTE = "2013-01-01", "2021-01-01"
REGIME = "nenhum"
CUSTO_TROCA = .001
CLASSE_IR = "exterior"
PARES = E.IN_PAR
PARAMS = {"z_in": 2.0, "jan": 252, "lado": "compra", "max_dias": 63, "peso": .25}   # escolhido no IS (maior IR IS)
GRADE = {"z_in": [1.5, 2.0], "jan": [126, 252], "lado": ["ambos", "compra"]}
VIZINHANCA = {"z_in": (1.6, 2.5), "jan": (180, 330), "max_dias": (40, 90), "peso": (.18, .33)}
INSTRUMENTOS = ("IBKR: ADRs INFY, HDB, IBN, WIT, RDY (NYSE) + INDA (hedge). Ações da NSE só como DADO (PF brasileiro não opera a NSE). "
                "B3: H1DB34/I1BN34 (BDRs) negociam em <15% dos pregões: não usados.")
APLICAVEL = True
MOTIVO = "Operável: 1–3 ADRs líquidos de R$ 5 mil (20k) cada + INDA vendido; exige conta margem (US$ 2.000 parados) quando há vendido."
ALAVANCAGENS = [1, 1.5, 2]
MOTIVO_ALAV = "L multiplica o peso por ADR (25% -> 37,5%/50%); Reg T cobre."


def carrega():
    return E.seleciona(list(PARES) + [v[0] for v in PARES.values()] + ["INR=X", "INDA"])


def premio(d):
    P = E.preco_usd(d)
    out = {}
    for a, (l, k) in PARES.items():
        ok = d["raw"][a].notna() & d["raw"][l].notna()
        out[a] = (np.log(P[a]) - np.log(P[l] * k)).where(ok)
    return pd.DataFrame(out)


def _pesos(d, z_in, jan, lado, max_dias, peso):
    p = premio(d).ffill(limit=3)
    p5 = p.rolling(5, min_periods=3).mean()
    m = p5.rolling(jan, min_periods=jan // 2).mean().shift(1)
    s = p5.rolling(jan, min_periods=jan // 2).std().shift(1)
    z = (p5 - m) / s
    neg = E.negociou(d)[list(PARES)]
    est_c = E.maquina((z <= -z_in) & neg, z >= 0, max_dias, espera=5)
    est_v = E.maquina((z >= z_in) & neg & (est_c == 0), z <= 0, max_dias, espera=5) if lado == "ambos" else est_c * 0
    lado_ = est_c - est_v
    lado_ = lado_ * E.limita_n(lado_.abs(), 2, z.abs())                  # no máximo 2 ADRs (bruto <= 100% com o INDA)
    W = lado_ * peso
    W["INDA"] = -W[list(PARES)].sum(axis=1)
    return W, {"conta": "anual"}


excesso, classes_ir, posicoes, negocios = E.contrato(__import__(__name__))
