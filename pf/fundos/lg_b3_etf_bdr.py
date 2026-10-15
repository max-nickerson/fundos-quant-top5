"""
(5) ETFs e BDRs da B3 (BOVA11, IVVB11, SMAL11, DIVO11, NASD11, GOLD11, ... e BDRs de large caps americanas) — noite depois de queda forte.

Mesa: o mesmo leilão de fechamento -> leilão de abertura do fundo nº 1 (b3_leilao_noite_aud), mas em outra classe de ativo da B3, SEM
remessa, SEM conta no exterior e SEM comissão mínima: emolumentos de 0,03% por lado. Nos ETFs/BDRs o outro lado é o formador de mercado
(obrigado a cotar com spread máximo) e o varejo que vende no pânico; o formador fecha o dia comprado e se protege no ativo-objeto/futuro
— a pressão do leilão de fechamento depois de um dia ruim tende a voltar na abertura, quando ele recompõe o estoque. Em IVVB11/BDRs a
'noite' da B3 (17h-10h) é quase a mesma noite americana; em BOVA11/SMAL11 é a noite brasileira.
Dados: COTAHIST (CODBDI 14, ETFs) e BDRs (pf/dados/global_cripto), preços brutos SEM ajuste de provento/desdobramento -> noites ou
dias com |variação| > 15%/40% são descartados (desdobramento/grupamento), e o provento na data ex fica de fora (conservador: a abertura
cai pelo provento e nós não o somamos). Spread: o COTAHIST traz a melhor oferta DEPOIS do leilão de fechamento (os formadores
tiram as ofertas -> spread largo que não é o do leilão). ETFs líquidos: 1 bp de derrapagem; BDRs: metade do meio spread mediano dos
últimos 20 pregões, entre 1 e 30 bps (leilão raso). Liquidez: volume médio >= R$ 2 mi/dia e >= 30 negócios no dia do sinal (fechamento
'parado' de papel ilíquido cria reversão falsa — foi o que apareceu na 1ª versão com FIAGRO/FIP e BDRs sem filtro: +130 bps por noite).
IR: ETF/BDR na B3 = 15% sem isenção de R$ 20 mil (classe etf_b3), apuração mensal.
"""
import numpy as np
import pandas as pd

import lg_comum as L

C, pf = L.C, L.pf
NOME = "Noite após queda forte — ETFs e BDRs da B3 (leilão de fechamento -> abertura)"
TESE = ("Compro no leilão de fechamento da B3 os ETFs (BOVA11, SMAL11, IVVB11, ...) ou BDRs que caíram forte no dia e vendo no leilão de "
        "abertura: o formador de mercado e o varejo em pânico pressionam o fechamento; sem remessa, só emolumentos")
BENCHMARK = "CDI"
INICIO, CORTE = "2014-06-02", "2021-01-01"
REGIME = "nenhum"
CUSTO_TROCA = .001
CLASSE_IR = "etf_b3"
# ETFs de ações/ouro da B3 (sem cripto: a 'noite' de um ETF de cripto contém 17 h de cripto negociando 24x7 -> aposta direcional; sem
# FIAGRO/FI-Infra/FIP, que também são CODBDI 14 no COTAHIST)
ETF = ["BOVA11", "BOVV11", "BOVB11", "BOVX11", "XBOV11", "BRAX11", "PIBB11", "SMAL11", "SMAC11", "DIVO11", "DIVD11", "FIND11", "MATB11",
       "ECOO11", "IVVB11", "SPXR11", "SPXI11", "SPYI11", "NASD11", "QQQI11", "TECK11", "USAL11", "ACWI11", "WRLD11", "EURP11", "ASIA11",
       "XINA11", "GOLD11"]
PARAMS = {"universo": "etf", "limiar": .04, "n": 2}              # melhor no IS (grade de 8)
GRADE = {"universo": ["etf", "bdr"], "limiar": [.02, .04], "n": [2, 4]}
VIZINHANCA = {"limiar": (.015, .045), "n": (1, 4)}
INSTRUMENTOS = [{"onde": "B3 (qualquer home broker)", "ticker": "ETFs (BOVA11, SMAL11, IVVB11, DIVO11, ...) e BDRs nível I/III",
                 "lote": "1 cota (ETF/BDR têm lote 1 ou fracionário)", "custo": "emolumentos 0,03%/lado + max(1 bp, 1/2 meio spread)"}]
APLICAVEL = True
MOTIVO = "ordem a mercado no call de fechamento (16h55-17h) e de abertura (9h45-10h) em qualquer corretora brasileira; sem remessa"
ALAVANCAGENS = [1, 1.5, 2]
MOTIVO_ALAV = "limite operacional da corretora com os próprios ETFs/Tesouro Selic como garantia (compra liquida junto com a venda)"


def carrega():
    return {"b3e": L.ler("b3_etf_bdr")}


def roda(d, capital=20000, custo_mult=1, lag=0, alavancagem=1, universo="etf", limiar=.02, n=2):
    x = d["b3e"]
    tk = sorted(x["ticker"].unique())
    tk = [t for t in ETF if t in tk] if universo == "etf" else [t for t in tk if not t.endswith("11")]
    g = L.grupo(d, "b3e", tk, min_cobertura=.05)
    adv = L.adv_usd(g, "BRL")
    neg = x.pivot_table(index="data", columns="ticker", values="NEG", aggfunc="last").reindex(index=g["C"].index, columns=g["C"].columns)
    # líquido: volume médio >= ~R$ 2 mi/dia e >= 30 negócios no dia do sinal (fechamento = leilão de verdade, não último negócio velho)
    liq = (adv >= 4e5) & (neg >= 30)
    bid = x.pivot_table(index="data", columns="ticker", values="BID", aggfunc="last").reindex(index=g["C"].index, columns=g["C"].columns)
    ask = x.pivot_table(index="data", columns="ticker", values="ASK", aggfunc="last").reindex(index=g["C"].index, columns=g["C"].columns)
    hs = ((ask - bid) / (ask + bid)).where((bid > 0) & (ask >= bid))
    # derrapagem: ETF líquido = 1 bp (leilão de verdade); BDR = metade do meio spread mediano no fechamento (o book do fim do pregão de
    # BDR é raso), entre 1 e 30 bps
    slip = L.SLIP if universo == "etf" else np.clip(hs.rolling(20, min_periods=1).median() / 2, L.SLIP, .003).fillna(.003)
    sc = L.score_queda(g, limiar, "abs" if universo == "etf" else "rel", liq)
    G = {"g": g, "mkt": "B3", "score": sc, "slip": slip, "teto": .15}
    return L.roda_b3([G], capital, int(n), lag, custo_mult, alavancagem, classe="etf_b3")


excesso, classes_ir, posicoes, negocios, _roda = L.interface(roda, PARAMS, REGIME, CUSTO_TROCA)
