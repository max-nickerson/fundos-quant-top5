"""
(4) ADRs brasileiros na NYSE (PBR, VALE, ITUB, BBD, ABEV, ...) — noite depois de queda forte — vs a MESMA noite na B3.

Mesa: o ADR é o ativo-objeto da mesma empresa, mas o leilão de fechamento é o de Nova York (16h ET), 0-60 min depois do leilão da B3, e
quem vende é outro: fundos de mercados emergentes/ETFs (EWZ, EEM) que resgatam em dólar e são forçados a vender no MOC. A noite do ADR
contém a abertura da B3 (10h de Brasília) inteira: se a pressão foi de fluxo estrangeiro e não de notícia, a abertura em NY (9h30 ET)
devolve. Duas pernas comparáveis: 'adr' = ADRs na IBKR (MOC -> MOO, conta no exterior com só o necessário); 'b3' = as ações-objeto
na B3 no leilão de fechamento -> abertura (como b3_leilao_noite_aud, mas só nestes 20 nomes e comprando no MESMO fechamento do sinal).
ADRs que sumiram do Yahoo (BRFS, EBR, CBD, ELP antigo) ficam de fora: viés de sobrevivência (ERJ->EMBJ e ELP->ELPC recuperados).
Dividendo do ADR: sem retenção nos EUA para emissor brasileiro (JCP retido no Brasil: ignorado, conservador nos dois lados).
IR: 'adr' = exterior (15% anual); 'b3' = ações swing (15%; vendas >> R$ 20 mil/mês).
"""
import numpy as np
import pandas as pd

import b3_base as B
import lg_comum as L

C, pf = L.C, L.pf
NOME = "Noite após queda forte — ADRs brasileiros (NYSE, IBKR) x mesmas ações na B3"
TESE = ("Compro no MOC de Nova York o ADR brasileiro que caiu forte (resgate de fundos emergentes vende no fechamento) e vendo no MOO; "
        "comparo com a mesma noite das ações-objeto na B3 (leilão de fechamento -> abertura)")
BENCHMARK = "CDI"
INICIO, CORTE = "2014-06-02", "2021-01-01"
REGIME = "nenhum"
CUSTO_TROCA = .001
CLASSE_IR = "acoes"                     # PARAMS na perna B3 (swing, vendas >> R$ 20 mil/mês)
PARAMS = {"mercado": "b3", "modo": "rel", "limiar": .02, "n": 2}     # melhor no IS: a perna B3 (ADR perde no custo)
GRADE = {"mercado": ["adr", "b3"], "modo": ["abs", "rel"], "limiar": [.02, .04]}
VIZINHANCA = {"limiar": (.015, .045), "n": (1, 4)}
INSTRUMENTOS = [{"onde": "IBKR (NYSE) ou B3 (home broker)", "ticker": "PBR, PBR-A, VALE, ITUB, BBD, ABEV, GGB, SID, EMBJ, SBS, ... / PETR4, VALE3, ...",
                 "lote": "1 ADR / 1 ação (fracionário)", "custo": "IBKR US$ 0,35 mín. + 1 bp; B3: emolumentos 0,03% + 1 bp por lado"}]
APLICAVEL = True
MOTIVO = "MOC até 15h50 ET (16h50/17h50 de Brasília) e MOO; na B3, ordem no call de fechamento (16h55-17h) e de abertura"
ALAVANCAGENS = [1, 1.5, 2]
MOTIVO_ALAV = "ADR: Reg T até 2x numa noite; B3: limite operacional da corretora com as ações como garantia"


def carrega():
    mapa = L.adr_b3()
    P = B.painel("P", "R", "O", "H", "L", "V")
    cols = [c for c in dict.fromkeys(mapa.values()) if c in P["P"].columns]
    ac = (1 + P["R"][cols].fillna(0)).cumprod().where(P["P"][cols].notna())   # índice de retorno total (com proventos)
    f = ac / P["P"][cols]                                                        # fator de ajuste do dia
    lon = {"O": P["O"][cols] * f, "H": P["H"][cols] * f, "L": P["L"][cols] * f, "C": ac, "AC": ac, "V": P["V"][cols] / ac,
           "div": P["P"][cols] * 0, "PX": P["P"][cols]}
    b3 = pd.concat({k: v.stack(future_stack=True) for k, v in lon.items()}, axis=1).dropna(subset=["C"]).reset_index()
    b3.columns = ["data", "ticker"] + list(lon)
    return {"eua": L.ler("eua"), "b3": b3}


def roda(d, capital=20000, custo_mult=1, lag=0, alavancagem=1, mercado="adr", modo="rel", limiar=.02, n=2):
    mapa = L.adr_b3()
    if mercado == "adr":
        g = L.grupo(d, "eua", list(mapa))
        sc = L.score_queda(g, limiar, modo, L.adv_usd(g, "USD") >= 2e6)
        return L.roda_ibkr([{"g": g, "mkt": "US", "score": sc}], capital, int(n), lag, custo_mult, alavancagem)
    tk = list(dict.fromkeys(mapa.values()))
    g = dict(L.grupo(d, "b3", tk))
    px = d["b3"].pivot_table(index="data", columns="ticker", values="PX", aggfunc="last").reindex(index=g["C"].index, columns=g["C"].columns)
    g["PX"] = px.where(g["C"].notna())
    sc = L.score_queda(g, limiar, modo, L.adv_usd(g, "BRL") >= 1e6)
    return L.roda_b3([{"g": g, "mkt": "B3", "score": sc}], capital, int(n), lag, custo_mult, alavancagem, classe="acoes")


excesso, classes_ir, posicoes, negocios, _roda = L.interface(roda, PARAMS, REGIME, CUSTO_TROCA)
