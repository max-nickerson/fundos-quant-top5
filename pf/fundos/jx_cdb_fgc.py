"""
CDB / LCI / LCA de bancos médios com FGC — prêmio sobre o CDI que só a pessoa física (até R$ 250 mil por CPF e instituição) pega sem
risco de crédito. NÃO TESTÁVEL com dados públicos: o módulo é a CONTA da premissa, marcado APLICAVEL=False.

Pesquisa de séries (out/2026):
  - não há série pública de taxas de CDB/LCI/LCA POR EMISSOR: BCB, B3 e ANBIMA não publicam; Yubb/plataformas mostram só a prateleira
    do dia (ex.: BS2 112%, Pine 110%, outros 107–109% do CDI em 2026 — https://www.moneytimes.com.br/cdbs-bancos-ainda-oferecem-ate-112-do-cdi-e-hora-de-investir/ ;
    https://yubb.com.br); sem arquivo histórico baixável;
  - BCB SGS 28663 (taxa média de captação de CDB, % a.a., mensal 1994 – jan/2024, salva em pf/dados/pf2_juros_fx/sgs_28663_cdb_medio.json):
    é a média do MERCADO (dominada por grandes bancos e por CDB pré curto), sem emissor — não serve para escolher banco médio;
  - balcão B3 (quant/dados/balcao.parquet) traz Letras Financeiras de bancos médios, mas SEM taxa (campo vazio) e com lote de R$ 50 mil+,
    sem FGC — não é proxy honesta do CDB de varejo;
  - frente renda_fixa já documentou o mesmo (rf_lci_lca.py). Este módulo acrescenta a conta com IR e o risco de evento:
Conta: CDB de banco médio a p% do CDI por 2 anos (IR 15%), escada (vence 1/24 por mês; reaplica na mesma taxa). Excesso antes do IR =
(p - 100%) x CDI sobre o capital aplicado. Evento (liquidação, ex.: Banco Master, nov/2025): o FGC paga principal + juros até a data da
liquidação, mas o dinheiro fica parado sem render por ~1–3 meses -> custo ≈ CDI x atraso sobre a parcela daquele banco (com 5 bancos,
1/5 do capital). Não simulado (seria escolher eventos a dedo); só documentado.
"""
import numpy as np
import pandas as pd

import jx_comum as J

NOME = "CDB de banco médio com FGC (premissa — não testável)"
TESE = "Escada de CDB de 2 anos de 4–5 bancos médios pagando 110–115% do CDI, garantidos pelo FGC (até R$ 250 mil por CPF/instituição)"
BENCHMARK = "CDI"
INICIO, CORTE = "2012-01-01", "2021-01-01"
REGIME = "nenhum"
CUSTO_TROCA = 0.0
PARAMS = {"premio": 0.10, "atraso_evento": 0.0}
GRADE = {"premio": [0.05, 0.10, 0.15]}
VIZINHANCA = {"premio": (0.05, 0.15)}
CLASSE_IR = "renda_fixa"
INSTRUMENTOS = [{"onde": "XP/BTG/Inter/Rico/Nubank (prateleira de bancários)", "ticker": "CDB 2 anos de banco médio (BS2, Pine, Daycoval, BMG...)",
                 "lote": "R$ 1 mil (às vezes R$ 100)", "custo": "sem taxa explícita; sem liquidez até o vencimento; FGC até R$ 250 mil"}]
APLICAVEL = False
MOTIVO = "Sem histórico público de taxas por emissor (BCB/B3/ANBIMA/Yubb); o 'resultado' abaixo é só a premissa de taxa."
ALAVANCAGENS = [1]
MOTIVO_ALAV = "CDB não aceita alavancagem para PF."


def carrega():
    return {"cdi": J.C.CDI.to_frame("cdi")}


def excesso(d, capital=20000, custo_mult=1, lag=0, regime=REGIME, alavancagem=1, premio=PARAMS["premio"], atraso_evento=0.0, **_):
    cdi = d["cdi"]["cdi"].reindex(J.DIAS).fillna(0)
    e = cdi * premio * (pd.Series(J.DIAS, index=J.DIAS) >= pd.Timestamp(INICIO))
    e = e.where(pd.Series(J.DIAS <= d["cdi"].index.max(), index=J.DIAS), 0.0)
    return J.C.aplica_regime(e.shift(1 + lag).fillna(0), regime, 0.0)


def classes_ir(d, capital=20000, **params):
    return {CLASSE_IR: excesso(d, capital, **params) * capital}


def posicoes(d, **params):
    p = {**PARAMS, **params}
    cdi = d["cdi"]["cdi"].reindex(J.DIAS).fillna(0)
    W = pd.DataFrame({"CDB": (pd.Series(J.DIAS, index=J.DIAS) >= pd.Timestamp(INICIO)).astype(float)})
    return W, pd.DataFrame({"CDB": cdi * p["premio"]})


def negocios(d, capital=20000, **params):
    e = excesso(d, capital, **params)
    out = []
    for a in sorted(set(J.DIAS.year)):
        x = e[e.index.year == a]
        if len(x) and a >= int(INICIO[:4]):
            out.append({"ativo": f"escada CDB {a}", "lado": 1, "entrada": x.index[0], "saida": x.index[-1], "dias": len(x),
                        "retorno_%": x.sum() * 100, "contrib_pp": x.sum() * 100})
    return pd.DataFrame(out)
