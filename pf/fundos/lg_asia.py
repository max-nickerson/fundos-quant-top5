"""
(3) Ásia: noite depois de queda forte em Tóquio (.T) e Hong Kong (.HK), ou nos ETFs de país negociados em NY (EWJ/EWY/EWT/EWH/...).

Mesa: Tóquio e Hong Kong têm leilão de fechamento (TSE: call das 15h25-15h30 desde nov/2024, antes 'itayose' às 15h00; HKEX: Closing
Auction Session 16h00-16h10 desde 2016) e de abertura (itayose 9h00; HK pre-opening 9h00-9h30). O varejo local é enorme em Tóquio (margem
de varejo 'shinyo' com chamada de margem diária -> vendas forçadas no fechamento depois de dias ruins) e em HK o fluxo do Southbound
Connect chega no fechamento. Pessoa física do Brasil opera Japão e HK pela IBKR; Coreia e Taiwan NÃO (a IBKR não dá acesso a não
residentes) -> ficam só como diagnóstico (universo 'kr_tw', fora da grade). Dados: Yahoo, OHLC desde 2012 (abertura japonesa pré-2010 no
Yahoo = fechamento anterior: não usada). Lote: Japão 100 ações (com capital/n de R$ 7-10 mil só cabem papéis de até ~JPY 2-3 mil);
HK: lote por papel (tabela aproximada em lg_comum.LOTE_HK, padrão 500). Custos: 0,08% mín. JPY 80 / HKD 18; HK stamp 0,1% por lado
(0,13% ago/2021-nov/2023) + taxas. As decisões são encadeadas: Tóquio fecha primeiro e escolhe primeiro; HK preenche as vagas restantes.
'etf_eua': ETFs de país em NY — a noite deles (16h ET -> 9h30 ET) contém o pregão asiático inteiro: é outra coisa (aposta direcional).
"""
import pandas as pd

import lg_comum as L

C, pf = L.C, L.pf
NOME = "Noite após queda forte — Japão/Hong Kong (IBKR) ou ETFs de país"
TESE = ("Compro no leilão de fechamento de Tóquio/HK as large caps que caíram forte (margem de varejo 'shinyo', Southbound) e vendo no "
        "leilão de abertura; Coreia/Taiwan só como diagnóstico (inacessíveis para PF brasileira)")
BENCHMARK = "CDI"
INICIO, CORTE = "2012-01-02", "2021-01-01"
REGIME = "nenhum"
CUSTO_TROCA = .001
CLASSE_IR = "exterior"
JAPAO = ["7203", "6758", "8306", "6861", "9984", "9432", "8035", "6098", "4063", "9983", "8316", "8411", "6501", "7974", "4502", "8058",
         "8031", "8001", "6367", "7267", "6902", "6954", "4519", "4568", "6981", "7741", "9433", "8766", "6273", "4661", "2914", "6594",
         "7751", "6702", "6752", "8802", "8801", "3382", "6503", "5108", "4503", "7011", "8053", "6301", "4901", "6178", "9020", "9022",
         "8604", "8591"]
ETF_EUA = ["EWJ", "EWY", "EWT", "EWH", "FXI", "MCHI", "EWS", "EWA"]
PARAMS = {"universo": "etf_eua", "limiar": .04, "n": 2}          # melhor no IS (grade de 8)
GRADE = {"universo": ["jp_hk", "etf_eua"], "limiar": [.02, .04], "n": [2, 3]}
VIZINHANCA = {"limiar": (.015, .045)}
INSTRUMENTOS = [{"onde": "IBKR (TSE, SEHK)", "ticker": "large caps do Nikkei/Hang Seng (ou EWJ/EWH/... em NY)",
                 "lote": "100 ações (Japão); lote do papel (HK)", "custo": "0,08% mín. JPY 80/HKD 18; HK stamp 0,1%/lado; 1 bp; margem 1 dia"}]
APLICAVEL = True
MOTIVO = ("MOC de Tóquio às 3h25 de Brasília e de HK às 5h: só com ordem programada pela API da IBKR (decide com o preço indicativo do "
          "call); Coreia/Taiwan não são acessíveis")
ALAVANCAGENS = [1, 1.5, 2]
MOTIVO_ALAV = "margem Reg T na IBKR (multimoeda): até 2x numa noite; juros de margem de 1 dia"


def carrega():
    return {"asia": L.ler("asia"), "eua": L.ler("eua")}


def _grupo_local(d, tk, mkt, limiar, lote=1):
    g = L.grupo(d, "asia", tk)
    liq = L.adv_usd(g, L.MERC[mkt][0]) >= 1e7
    return {"g": g, "mkt": mkt, "score": L.score_queda(g, limiar, "rel", liq), "lote": lote}


def roda(d, capital=20000, custo_mult=1, lag=0, alavancagem=1, universo="jp_hk", limiar=.02, n=2):
    if universo == "etf_eua":
        g = L.grupo(d, "eua", ETF_EUA)
        grupos = [{"g": g, "mkt": "US", "score": L.score_queda(g, limiar, "abs", L.adv_usd(g, "USD") >= 2e6)}]
    elif universo == "kr_tw":                                           # diagnóstico: não operável por PF brasileira
        tw = sorted(t for t in d["asia"]["ticker"].unique() if t.endswith(".TW"))
        ks = sorted(t for t in d["asia"]["ticker"].unique() if t.endswith(".KS"))
        grupos = [_grupo_local(d, tw, "TW", limiar, 1), _grupo_local(d, ks, "KS", limiar)]
    else:
        hk = L.lista("hk")
        lote = pd.Series({t: L.LOTE_HK.get(t, 500) for t in hk})
        grupos = [_grupo_local(d, [t + ".T" for t in JAPAO], "T", limiar, 100), _grupo_local(d, hk, "HK", limiar, lote)]
    return L.roda_ibkr(grupos, capital, int(n), lag, custo_mult, alavancagem)


excesso, classes_ir, posicoes, negocios, _roda = L.interface(roda, PARAMS, REGIME, CUSTO_TROCA)
