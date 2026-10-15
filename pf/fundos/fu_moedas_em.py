"""
Moedas emergentes na B3 sem passar pelo real: Futuro de Peso Mexicano (MEX) e de Rande (AFS) em USD — carry e compra depois do pânico.

Tese de mesa: MXN e ZAR pagam juro alto (Banxico/SARB 6,5-11% vs Fed 0-5%) e são as moedas "líquidas" usadas pelo mundo para carry
de emergentes — e para HEDGE de emergentes (quem tem risco em EM e não consegue vender o ativo vende MXN/ZAR). Por isso apanham nas
crises de forma exagerada: fundos de carry alavancados batem stop, CTAs viram e hedgers de carteira vendem ao mesmo tempo (mar/2020,
ago/2024). Esses são os vendedores forçados. "pos_panico": compro a moeda (vendo o futuro de USD/MXN ou USD/ZAR) depois de uma
alta de k desvios do dólar em 5 dias, se o diferencial de juros > 3 p.p., e seguro H pregões, recebendo o carry; "carry": comprado o
tempo todo enquanto o diferencial > 3 p.p. (controle: o prêmio "puro").

Contratos (B3, "Futuro de Peso Mexicano (em USD)" e "Futuro de Rande da África do Sul (em USD)"): US$ 10 mil por contrato, cotação em
MXN (ZAR) por US$ 1.000, tick MXN/ZAR 1,00 por US$ 1.000, todos os meses, liquidação financeira; negocia a paridade USD/MXN direto (o
real não entra no preço; o ajuste é pago em R$). 1 contrato ≈ R$ 55 mil = 2,75x R$ 20 mil, 1,1x R$ 50 mil.
LIQUIDEZ REAL (boletim BVBG.086 da B3 baixado em 12/03/2025, 01/06/2026, 15/09/2026 e 07/10/2026): MEX 0-7 negócios/dia, em blocos de
40-720 contratos (rolagens estruturadas institucionais), contratos em aberto 1-4 mil; AFS 0-1 negócio/dia (86 contratos), aberto
~300-600; NENHUMA oferta de compra/venda no livro no fechamento. Para pessoa física isso significa: não há tela — a ordem depende de
um formador/RFQ via corretora (Clear/XP em geral nem habilitam o contrato). Custo assumido: meio spread de 0,30% do nocional por lado
(≈ US$ 30 = R$ 165 por contrato) + emolumentos ~R$ 2, carregando o vencimento trimestral (4 rolagens/ano). A bateria mostra custo 0,5x-3x.
A alternativa na CME (6M = MXN 500 mil ≈ US$ 28 mil ≈ R$ 150 mil; 6Z = ZAR 500 mil ≈ US$ 28 mil) é 3-7x o capital e não tem micro:
não cabe. Retorno do contrato (comprado na moeda) = variação do spot (Yahoo MXN=X/ZAR=X) + diferencial do juro de política (BIS) —
paridade coberta, exatamente o que o futuro paga. Garantia em Tesouro Selic. IR: futuros B3 15%.
Tamanho: 1 contrato por moeda; não opera se a vol de 1 contrato (63 dias, em R$) passar de 35% do capital (mesma régua de fu_energia_curva).
"""
import numpy as np
import pandas as pd

import fu_comum as F

NOME = "Peso mexicano e rande na B3 (MEX/AFS, US$ 10 mil): carry e compra depois do pânico"
TESE = "Compra MXN/ZAR contra o dólar (vende o futuro da B3) depois de alta forte do dólar (stop de carry/hedge de EM), carregando o juro"
BENCHMARK = "CDI"
INICIO, CORTE = "2008-01-01", "2021-01-01"
REGIME = "nenhum"
CUSTO_TROCA = 0.0
CLASSE_IR = "futuros_b3"
PARAMS = {"modo": "pos_panico", "k": 2.0, "H": 10}          # maior excesso IS da grade (todas perdem; com R$ 20 mil o fundo quebra no IS)
GRADE = {"modo": ["pos_panico", "carry"], "k": [1.5, 2.0], "H": [10, 20]}
VIZINHANCA = {"k": (1.25, 2.25), "H": (8, 30)}
TETO_VOL, CUSTO_FRAC, EMOL = .35, .003, 2.0
MOEDAS = {"MEX": ("MXN=X", "MX"), "AFS": ("ZAR=X", "ZA")}
INSTRUMENTOS = [("B3", "MEX", "US$ 10 mil (≈ R$ 55 mil)", "0,30% + R$ 2/lado (sem livro: RFQ)"), ("B3", "AFS", "US$ 10 mil", "0,30% + R$ 2/lado"),
                ("Tesouro Direto", "Tesouro Selic", "garantia", "0")]
APLICAVEL = False
MOTIVO = ("Tecnicamente existe (B3, US$ 10 mil), mas não há livro: 0-7 negócios/dia em blocos institucionais, nenhuma oferta no fechamento; "
          "pessoa física depende de RFQ e a maioria das corretoras não habilita. 1 contrato = 2,75x R$ 20 mil (vol ~40% do capital). "
          "CME 6M/6Z (≈ R$ 150 mil) não cabe.")
ALAVANCAGENS = [1, 2]
MOTIVO_ALAV = "1 ou 2 contratos por moeda (sujeito ao teto de vol)."


def carrega():
    return {"fx": F.ler("fx.parquet")[["MXN=X", "ZAR=X"]], "bis": F.ler("bis.parquet")[["MX", "ZA", "US"]]}


def _contrato(d, inst):
    def f():
        col, bis = MOEDAS[inst]
        s = d["fx"][col].dropna()
        s = s[(s.pct_change().abs() < .15) | s.pct_change().isna()]                 # erros do Yahoo (saltos de 15%+ que desfazem)
        idx = pd.bdate_range(s.index.min(), s.index.max())
        sp = F.nivel(s, idx)
        dif = F.juro_dia(d["bis"][bis], idx) - F.juro_dia(d["bis"]["US"], idx)
        r = (sp.shift(1) / sp - 1).fillna(0) + dif                                   # comprado na moeda (vendido no USD/moeda)
        K = F.contrato(r, pd.Series(1.0, index=idx), 10_000.0, "USD", idx, None, 0.0, 0.0, rol=4, local="b3")
        K["custo"] = K["noc"] * CUSTO_FRAC + EMOL
        carry = F.nivel(d["bis"][bis], idx) - F.nivel(d["bis"]["US"], idx)
        return K, sp, carry
    return F.memo(("em", inst), (d["fx"], d["bis"]), f)


def gera(d, capital=20000, regime=REGIME, alavancagem=1, modo="pos_panico", k=1.5, H=20):
    N, Ks = {}, {}
    idx = None
    for inst in MOEDAS:
        K, sp, carry = _contrato(d, inst)
        ok = carry > 3.0
        if modo == "carry":
            lado = ok.astype(float)
        else:
            r = np.log(sp).diff()
            z = r.rolling(5).sum() / (r.rolling(252, min_periods=150).std() * np.sqrt(5))
            lado = F.segura(((z >= k) & ok).astype(float), H)
        n = pd.Series(float(round(alavancagem)), index=K.index)
        n = n.where(F.vol_brl(K) * n <= TETO_VOL * alavancagem * capital, 0)
        N[inst], Ks[inst] = (lado * n).fillna(0), K
        idx = K.index if idx is None else idx.union(K.index)
    return pd.DataFrame(N).reindex(idx).fillna(0), {a: k.reindex(idx) for a, k in Ks.items()}


F.montar(globals(), gera, carrega)
