"""
Excluídos de índice comprados DEPOIS da venda forçada (S&P 500, Nasdaq-100, DAX, CAC 40) — PF na IBKR, só o necessário fora.

Tese de mesa: quem sai de um índice é vendido no fechamento da véspera da data efetiva por TODO fundo indexado, sem olhar preço
(o vendedor forçado). O comprador do outro lado cobra um desconto, e o papel volta nas semanas seguintes (lição da pesquisa
institucional IE06: a reversão PÓS-efetivação pagou; o "antes" já é arbitrado). Pessoa física compra R$ 2–5 mil por nome no leilão
de fechamento (MOC) junto com a venda dos indexados, segura `dias` pregões e vende SPY/QQQ (ou EWG/EWQ na Europa) em ações inteiras
como hedge. Só exclusões por VALOR DE MERCADO / revisão regular (o comunicado diz o motivo): aquisição, cisão e falência ficam de fora.

Dados: mudanças da Wikipédia (data efetiva; S&P/Nasdaq com data do comunicado), tickers pelo CIK (Forms 3/4, pega deslistadas),
preços Yahoo (ajustados) — base quant/fundos (ideias_i_eventos.ev_indices_us/ev_indices_loc). Europa em EUR convertida a US$ (EURUSD).
FTSE 100, STOXX 600, Nikkei e KOSPI 200: sem histórico gratuito de mudanças com data (ja.wiki só tem o ANO do Nikkei) -> fora.
NIFTY: PF brasileiro não compra ação indiana (só FPI) -> fora.

Viés de sobrevivência (tratado): 29% das exclusões por valor de mercado nos EUA não têm preço no Yahoo depois da efetiva. As que
pediram recuperação judicial (8-K item 1.03 na SEC) em até 5 anos (FTR, MNK, WIN, RSH, DNR...) entram com trajetória SINTÉTICA de
−30% em 166 pregões (regra da auditoria de spin-offs); as outras (compradas/fechadas depois: JOY, LM, AVP, BMS, IGT...) andam com o
ETF de hedge (alfa zero). Variantes: `sobrev="ignora"` (o viés) e `"duro"` (todas as que sumiram a −30%).
Custos: IBKR US$ 0,0035/ação (mín. US$ 0,35) + meio spread 0,05% (mid caps); Europa 0,05% mín. ~€ 1,75 + meio spread 0,08%, TTF
francesa 0,4% na compra (empresas > € 1 bi); ações INTEIRAS na Europa, fração nos EUA. Aluguel do hedge: SPY/QQQ 0,25%, EWG/EWQ 0,5% a.a.
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

import fg_comum as G  # noqa: E402

C, pf = G.C, G.pf

NOME = "Excluídos de índice após a venda forçada (S&P 500, Nasdaq-100, DAX, CAC) — PF IBKR"
TESE = ("Compro no leilão de fechamento o papel que os indexados vendem na véspera da exclusão (só exclusão por valor de mercado), "
        "seguro algumas semanas com hedge em SPY/QQQ/EWG/EWQ vendidos; caixa no CDI.")
BENCHMARK = "CDI"
INICIO, CORTE = "2008-01-01", "2021-01-01"
REGIME = "nenhum"
CUSTO_TROCA = .001
CLASSE_IR = "exterior"
PARAMS = {"dias": 60, "mercados": "US", "peso": .10, "entrada": 0, "sobrev": "sintetico", "hedge_fx": "wdo"}
GRADE = {"dias": [20, 60, 120], "mercados": ["US", "US+EU"]}
VIZINHANCA = {"dias": (40, 90), "peso": (.07, .14)}
INSTRUMENTOS = {"ações excluídas": {"onde": "IBKR (NYSE/Nasdaq/Xetra/Euronext)", "ticker": "~25/ano", "lote": "fração (EUA), inteira (Europa)",
                                   "custo": "US$ 0,0035/ação mín. 0,35; Europa 0,05% mín. € 1,75; TTF 0,4% (FR)"},
                "hedge": {"onde": "IBKR", "ticker": "SPY/QQQ/EWG/EWQ vendidos", "lote": "ações inteiras", "custo": "aluguel 0,25–0,5% a.a."},
                "caixa": {"onde": "Tesouro Selic", "ticker": "LFT", "lote": "R$ ~150", "custo": "0"}}
APLICAVEL = True
MOTIVO = ("Operável: a exclusão é anunciada 1–4 semanas antes (S&P/Nasdaq) e o PF manda ordem MOC na IBKR no dia da venda dos indexados; "
          "10% por nome = R$ 2 mil com R$ 20 mil (0,2% de comissão mínima). Vender SPY exige conta margem com US$ 2 mil parados.")
ALAVANCAGENS = [1, 1.5, 2]
MOTIVO_ALAV = "peso por nome x L (10% -> 15%/20%), pago à vista; 5x concentraria em 2 nomes e o dinheiro fora passaria do capital."
HEDGE = {"US_SP": "SPY", "US_NDX": "QQQ", "DE": "EWG", "FR": "EWQ"}
CUSTO = {"US_SP": .0005, "US_NDX": .0005, "DE": .0008, "FR": .0008}
TTF = {"FR": .004}
FORA = r"conservator|acqui|merger|merged|spun|spin|split into|purchas|bought|bankrupt|chapter|receivership|delist|no longer listed|taken private|buyout|privat|ticker symbol|renam"


# ---------------------------------------------------------------- dados
def _constroi():
    sys.path.insert(0, str(G.FD.parent))
    import ideias_i_eventos as IE                       # noqa: E402  (base da pesquisa institucional; só para montar o cache)
    us = IE.ev_indices_us()
    us = us[us.lado == "sai"].copy()
    us["regiao"] = np.where(us.indice == "NDX", "US_NDX", "US_SP")
    us["regular"] = ~us.motivo.fillna("").str.contains(FORA, case=False)
    lo = IE.ev_indices_loc()
    lo = lo[(lo.lado == "sai") & lo.indice.isin(["DAX", "CAC"])].copy()
    lo["regiao"] = np.where(lo.indice == "DAX", "DE", "FR")
    lo["anuncio"] = pd.NaT
    lo["motivo"] = ""
    lo["tk_era"] = lo["nome"]
    lo["cik"] = -1
    cols = ["indice", "regiao", "tk_era", "ticker", "cik", "efetiva", "anuncio", "motivo", "regular"]
    ev = pd.concat([us[cols], lo[cols]], ignore_index=True)
    # falência (8-K item 1.03) da empresa em até 5 anos depois da exclusão: só para modelar quem SUMIU do Yahoo
    c11 = IE._fts_ev("cap11", ["8-K"])
    c11 = c11[c11.itens.str.contains("1.03", regex=False)].groupby("cik").data.apply(list)
    ev["falencia"] = [next((x for x in sorted(c11.get(int(c), [])) if e - pd.Timedelta(days=30) <= x <= e + pd.Timedelta(days=1826)), pd.NaT)
                      for c, e in zip(ev.cik, ev.efetiva)]
    ev = ev[ev.efetiva >= "2008-01-01"].reset_index(drop=True)
    ev["ticker"] = ev.ticker.fillna("").astype(str)
    Pus = pd.concat([G.painel_y("sp"), G.painel_y("us")], axis=1)
    Pus = Pus.loc[:, ~Pus.columns.duplicated()]
    Peu = G.painel_y("eur")
    fx = G.no_idx(G.eurusd(), Peu.index)
    tus = [t for t in ev[ev.regiao.str.startswith("US")].ticker if t in Pus.columns]
    teu = [t for t in ev[~ev.regiao.str.startswith("US")].ticker if t in Peu.columns]
    P = pd.concat([Pus[sorted(set(tus))], Peu[sorted(set(teu))].mul(fx, axis=0), G.etf(list(set(HEDGE.values())))], axis=1)
    P = P.loc[:, ~P.columns.duplicated()].sort_index()
    ev["data"] = ev.efetiva
    return ev, P[P.index >= "2007-06-01"].astype("float64")


def carrega():
    f = G.CACHE / "indices_exclusao"
    if not (f / "precos.parquet").exists():
        ev, P = _constroi()
        f.mkdir(parents=True, exist_ok=True)
        ev.to_parquet(f / "eventos.parquet")
        P.to_parquet(f / "precos.parquet", compression="zstd")
    return {"eventos": pd.read_parquet(f / "eventos.parquet"), "precos": pd.read_parquet(f / "precos.parquet")}


# ---------------------------------------------------------------- motor
_CACHE = {}


def _negocios_base(d, dias, mercados, peso, entrada, sobrev):
    """Tabela de negócios + painel de preços (com as trajetórias sintéticas de quem sumiu)."""
    ev = d["eventos"]
    P = d["precos"]
    idx = P.index
    ev = ev[ev.regular & (ev.regiao.str.startswith("US") | (mercados == "US+EU"))]
    linhas, sint = [], {}
    for _, r in ev.iterrows():
        kE = idx.searchsorted(r.efetiva)                       # 1º pregão FORA do índice
        j = kE - 2 + entrada                                   # decide na antevéspera (anúncio já público) -> MOC na véspera
        if j < 1 or kE - 1 + entrada >= len(idx):
            continue
        t = r.ticker
        tem = bool(t) and t in P.columns and np.isfinite(P[t].ffill(limit=5).iloc[min(j + 1, len(idx) - 1)])
        if not tem:
            if sobrev == "ignora":
                continue
            t = f"{r.tk_era or r.ticker}*{r.efetiva:%Y%m}"
            if sobrev == "duro" or pd.notna(r.falencia):           # quebrou depois (ou regra dura): -30% em 166 pregões
                sint[t] = G.sintetico(idx, idx[j], nome=t)
            else:                                                  # comprada/fechou capital depois: anda com o hedge (alfa zero)
                h = P[HEDGE[r.regiao]]
                sint[t] = (h / h.iloc[j]).where(np.arange(len(idx)) >= j).rename(t)
        linhas.append({"ticker": t, "decisao": idx[j], "dias": dias, "lado": 1, "regiao": r.regiao, "custo": CUSTO[r.regiao],
                       "extra_compra": TTF.get(r.regiao, 0.0), "aluguel": 0.0, "sintetico": not tem})
    if sint:
        P = pd.concat([P, pd.DataFrame(sint)], axis=1)
    return pd.DataFrame(linhas), P


def _roda(d, capital, custo_mult, lag, alavancagem, dias, mercados, peso, entrada, sobrev, hedge_fx=PARAMS["hedge_fx"]):
    k = (id(d), len(d["precos"]), d["precos"].index.max(), len(d["eventos"]), capital, custo_mult, lag, alavancagem, dias, mercados,
         round(peso, 5), entrada, sobrev, hedge_fx)
    if k not in _CACHE:
        tr, P = _negocios_base(d, dias, mercados, peso, entrada, sobrev)
        res = G.livro(tr, P, capital, custo_mult, lag, alavancagem, peso, teto=1.0, hedge=HEDGE, hedge_fx=hedge_fx)
        res["P"] = P
        if len(_CACHE) > 40:
            _CACHE.clear()
        _CACHE[k] = res
    return _CACHE[k]


def excesso(d, capital=20000, custo_mult=1, lag=0, regime=REGIME, alavancagem=1, dias=PARAMS["dias"], mercados=PARAMS["mercados"],
            peso=PARAMS["peso"], entrada=PARAMS["entrada"], sobrev=PARAMS["sobrev"], hedge_fx=PARAMS["hedge_fx"]):
    res = _roda(d, capital, custo_mult, lag, alavancagem, dias, mercados, peso, entrada, sobrev, hedge_fx)
    return C.aplica_regime(res["e"], regime, CUSTO_TROCA * custo_mult)


def posicoes(d, capital=20000, dias=PARAMS["dias"], mercados=PARAMS["mercados"], peso=PARAMS["peso"], entrada=PARAMS["entrada"],
             sobrev=PARAMS["sobrev"], hedge_fx=PARAMS["hedge_fx"]):
    res = _roda(d, capital, 1, 0, 1, dias, mercados, peso, entrada, sobrev, hedge_fx)
    return G.posicoes_de(res, res["P"], capital)


def negocios(d, capital=20000, dias=PARAMS["dias"], mercados=PARAMS["mercados"], peso=PARAMS["peso"], entrada=PARAMS["entrada"],
             sobrev=PARAMS["sobrev"], hedge_fx=PARAMS["hedge_fx"]):
    res = _roda(d, capital, 1, 0, 1, dias, mercados, peso, entrada, sobrev, hedge_fx)
    return G.negocios_de(res, capital, res["P"])


VARIANTES = {"sobrevivência ignorada": {"sobrev": "ignora"}, "entra no dia seguinte (fech. da efetiva)": {"entrada": 1},
             "EUA + Europa": {"mercados": "US+EU"}, "sem WDO": {"hedge_fx": "nenhum"}, "20 pregões": {"dias": 20}, "120 pregões": {"dias": 120}}
