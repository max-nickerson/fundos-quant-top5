"""
(8) Combinação das noites operáveis (B3: blue chips com ADR + ETFs da B3; opcional: EUA na IBKR) com filtro de REGIME (VIX) e de DIA
DA SEMANA.

Mesa: a venda forçada no fechamento é maior quando o mercado está em estresse — VIX alto = mais margin call, mais fundos de vol-alvo e
de risk parity reduzindo exposição no MOC, formadores de mercado com menos balanço. A reversão da noite deveria ser maior com VIX acima da
mediana de 1 ano (e o custo é o mesmo). Dia da semana: a noite de sexta carrega o fim de semana inteiro (notícia acumulada, 64 h de risco)
— quem foi forçado a vender na sexta vende risco de fim de semana, que não é o mesmo 'prêmio de liquidez'; 'seg_qui' só entra de segunda
a quinta. VIX de t-1 (o de t fecha às 16h15 ET, depois do prazo do MOC). Universos: 'b3' = 20 blue chips com ADR (PETR4, VALE3, ITUB4,
...) + ETFs de ações/ouro da B3, uma decisão conjunta no leilão de fechamento da B3; 'b3_eua' = + ETFs americanos e S&P 100 na IBKR
(mesma hora de fechamento: a B3 escolhe primeiro, os EUA preenchem as vagas; a conta na IBKR paga o custo de conta no exterior).
IR: 'b3' = ações/ETF B3 15% (vendas >> R$ 20 mil/mês); a parte EUA, exterior 15% anual (aproximação: classe única 'acoes').
"""
import pandas as pd

import lg_adr_br
import lg_b3_etf_bdr
import lg_comum as L
import lg_eua_etf

C, pf = L.C, L.pf
NOME = "Noites combinadas (blue chips + ETFs B3, opcional EUA) com filtro de VIX e dia da semana"
TESE = ("Compro no leilão de fechamento o que caiu forte no dia SÓ quando o VIX de ontem está acima da mediana de 1 ano (estresse = mais "
        "venda forçada no fechamento) e evito a noite de sexta (risco de fim de semana); vendo na abertura")
BENCHMARK = "CDI"
INICIO, CORTE = "2014-06-02", "2021-01-01"
REGIME = "nenhum"
CUSTO_TROCA = .001
CLASSE_IR = "acoes"
PARAMS = {"universo": "b3", "vix": "todos", "dias": "seg_qui", "limiar": .03, "n": 3}
# escolha no IS SEM o ganho cambial do saldo na IBKR (b3_eua): de 2014 a 2020 o real perdeu ~55% e o saldo em US$ "ganhou" isso -> beta
GRADE = {"universo": ["b3", "b3_eua"], "vix": ["todos", "alto"], "dias": ["todos", "seg_qui"]}
VIZINHANCA = {"limiar": (.02, .045), "n": (2, 5)}
INSTRUMENTOS = [{"onde": "B3 (home broker); opcional IBKR", "ticker": "PETR4, VALE3, ITUB4, BBDC4, ... + BOVA11, SMAL11, IVVB11, ...; SPY/S&P 100",
                 "lote": "1 ação/cota (fracionário)", "custo": "B3: emolumentos 0,03% + 1 bp por lado; IBKR: US$ 0,35 mín. + 1 bp"}]
APLICAVEL = True
MOTIVO = "ordens nos leilões de fechamento/abertura da B3 (e MOC/MOO na IBKR na variante b3_eua); VIX de ontem é público"
ALAVANCAGENS = [1, 1.5, 2]
MOTIVO_ALAV = "limite operacional da corretora (ações/ETFs como garantia); IBKR Reg T"


def carrega():
    d = lg_adr_br.carrega()
    e = L.ler("b3_etf_bdr")
    e = e[e["ticker"].isin(lg_b3_etf_bdr.ETF)][["data", "ticker", "O", "H", "L", "C", "AC", "V", "div"]].assign(PX=lambda x: x["C"])
    d["b3"] = pd.concat([d["b3"], e], ignore_index=True)
    return d


def roda(d, capital=20000, custo_mult=1, lag=0, alavancagem=1, universo="b3", vix="alto", dias="todos", limiar=.03, n=3):
    tk = sorted(d["b3"]["ticker"].unique())
    g = dict(L.grupo(d, "b3", tk, min_cobertura=.2))
    g["PX"] = d["b3"].pivot_table(index="data", columns="ticker", values="PX", aggfunc="last").reindex(
        index=g["C"].index, columns=g["C"].columns).where(g["C"].notna())
    grupos = [{"g": g, "mkt": "B3", "score": L.score_queda(g, limiar, "abs", L.adv_usd(g, "BRL") >= 4e5)}]
    if universo == "b3_eua":
        gu = L.grupo(d, "eua", lg_eua_etf.ETF + L.lista("sp100"))
        grupos.append({"g": gu, "mkt": "US", "score": L.score_queda(gu, limiar, "abs", L.adv_usd(gu, "USD") >= 1e7)})
    for G in grupos:
        idx = G["score"].index
        ok = pd.Series(True, index=idx)
        if vix == "alto":
            v = L.vix_ontem(d, idx)
            med = L.vix_ontem(d, idx).rolling(252, min_periods=120).median()       # mediana de 1 ano (só passado)
            ok &= (v > med).fillna(False)
        if dias == "seg_qui":
            ok &= pd.Series(idx.weekday < 4, index=idx)
        G["score"] = G["score"].where(ok, axis=0)
    res = L.noites(grupos, capital, int(n), lag, custo_mult, alavancagem)
    noc_b3 = L.para_b3(res["noc_grupos"][0])
    e = (res["pnl"] - noc_b3 * L.CDI) / capital
    res.update({"pnl_classe": res["pnl"], "cdi_perdido": noc_b3 * L.CDI, "classe": "acoes"})
    if universo == "b3_eua":
        e_us, x = L.excesso_ibkr(res, capital, alavancagem, custo_mult, nocional=res["noc_grupos"][1])
        e = e - (x["conta"] + x["juros"]) / capital
        res.update({"conta": x["conta"], "juros": x["juros"]})
    res["e"] = e.reindex(L.DIAS).fillna(0)
    return res


excesso, classes_ir, posicoes, negocios, _roda = L.interface(roda, PARAMS, REGIME, CUSTO_TROCA)
