"""
Reconstituição anual do Russell 2000 (junho): compro quem CAI do índice para as micro caps no leilão de fechamento do dia da
reconstituição (vendido por todos os fundos de Russell 2000 — o maior leilão de fechamento do ano na Nasdaq/NYSE) e seguro algumas
semanas; variante: compro quem ENTRA vindo das micro caps depois da lista preliminar e vendo no leilão.

Tese de mesa: o Russell 2000 é o índice de small caps mais indexado do mundo (IWM, VTWO, fundos passivos, benchmark de gestores ativos).
Na última sexta de junho todos rebalanceiam no MESMO leilão; quem sai para baixo (vira micro cap) é vendido sem olhar preço, num papel
de US$ 100–200 milhões em que o comprador natural é pequeno. Depois do leilão o preço volta (reversão pós-efetivação, a lição da
pesquisa de índices). Um gestor grande não consegue comprar US$ 50 milhões disso; PF compra R$ 1–2 mil por nome.

Composição REAL (não estimada): carteiras trimestrais do próprio IWM no N-PORT da SEC (iShares Trust, série "iShares Russell 2000
ETF"), 31/mar (antes) e 30/jun (depois da reconstituição), 2020–2026 (o N-PORT público começa no fim de 2019; antes disso não há lista
gratuita — o arquivo histórico de posições no site da iShares bloqueia robôs, e o ranking por valor de mercado com SEC + Yahoo ficou
inviável: o Yahoo não tem as deslistadas e o "universo" de 2012 tinha < 3.000 ações). Saiu = estava em março e não está em junho;
entrou = o contrário. CUSIP -> ticker da época pelos arquivos de fails-to-deliver da SEC; ticker de preço pelo CIK (atual, se a empresa
mudou de ticker). Quem saiu por AQUISIÇÃO some do Yahoo junto com a data efetiva (sem preço na execução -> fora).
"Para baixo" = metade de menor valor na carteira de março (as que viram micro cap); "para cima" (vão para o Russell 1000) ficam fora.
"Entra de baixo" = metade de menor valor em junho, listada há >= 1 ano (sem IPOs).
Datas: reconstituição = última sexta-feira de junho (calendário FTSE Russell). A lista preliminar sai na 4ª sexta-feira de maio e é
atualizada até junho — usamos a carteira de 30/jun como a lista que já era pública na véspera da reconstituição (decisão em t−1);
na perna "entra_pre" a compra é no 1º pregão depois de 25/mai.
Em 2024–25 a carteira de 30/jun ainda não mostrava a reconstituição inteira: "saiu" = fora em junho OU em setembro.
Amostra curta: 7 reconstituições (2020–2026); CORTE 2023 (IS = 2020–2022). Sobrevivência: saídas sem preço no Yahoo (e sem ticker
com preço) entram neutras (andam com o IWM); variante "duro": −30% em 166 pregões.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

import fg_comum as G  # noqa: E402

C, pf = G.C, G.pf

NOME = "Reconstituição do Russell 2000: quem cai para micro cap comprado no leilão de junho (PF IBKR)"
TESE = ("Compro no leilão de fechamento da reconstituição (última sexta de junho) as ações que saem do Russell 2000 para baixo — vendidas "
        "por todos os indexados — e seguro algumas semanas com IWM vendido; R$ 1 mil por nome.")
BENCHMARK = "CDI"
INICIO, CORTE = "2020-01-01", "2023-01-01"
REGIME = "nenhum"
CUSTO_TROCA = .001
CLASSE_IR = "exterior"
PARAMS = {"lado": "sai_pos", "dias": 60, "faixa": .5, "n": 20, "peso": .05, "hedge_fx": "wdo", "sobrev": "neutro"}
GRADE = {"lado": ["sai_pos", "entra_pre", "ambos"], "dias": [20, 60]}
VIZINHANCA = {"dias": (10, 80), "faixa": (.3, .7), "n": (10, 30)}
MEIO_SPREAD = .004
INSTRUMENTOS = {"saídas/entradas do Russell 2000": {"onde": "IBKR", "ticker": "até 20 por ano", "lote": "fração", "custo": "US$ 0,0035/ação mín. 0,35 + 0,4%"},
                "IWM": {"onde": "IBKR (vendido)", "ticker": "IWM", "lote": "ações inteiras", "custo": "aluguel 0,3% a.a."}}
APLICAVEL = True
MOTIVO = ("Operável (ordem MOC na IBKR no dia da reconstituição, lista preliminar pública desde maio). Só 7 reconstituições com a "
          "composição real (N-PORT do IWM) -> amostra pequena.")
ALAVANCAGENS = [1, 1.5, 2]
MOTIVO_ALAV = "peso por nome x L; livro de algumas semanas por ano."
VARIANTES = {"só as com preço (sobrevivência ignorada)": {"sobrev": "ignora"}, "todas as saídas (inclui as que sobem)": {"faixa": 1.0}, "sem WDO": {"hedge_fx": "nenhum"}, "segura 20 pregões": {"dias": 20},
             "sumidas a -30%": {"sobrev": "duro"}}


def _recon(ano):
    jun = C.DIAS_US[(C.DIAS_US >= f"{ano}-06-01") & (C.DIAS_US <= f"{ano}-06-30")]
    sext = jun[jun.dayofweek == 4]
    return sext[-1] if len(sext) else jun[-1]


def _constroi():
    sys.path.insert(0, str(G.FD.parent))
    import ideias_i_eventos as IE                                     # noqa: E402  (CIK pelos Forms 3/4 e ticker atual da SEC)
    X = pd.read_parquet(G.CACHE / "iwm_nport.parquet")                # _fg_nport.py
    ct = pd.read_parquet(G.CACHE / "cusip_ticker.parquet").sort_values("data")
    ev = []
    for ano in range(2020, 2027):
        pre, pos, set_ = (X[X.periodo == f"{ano}-{m}"] for m in ("03-31", "06-30", "09-30"))
        if not len(pre) or not len(pos):
            continue
        rc = _recon(ano)
        # em 2024–25 a carteira de 30/jun do N-PORT ainda não mostra boa parte da reconstituição (41 e 81 saídas, contra 200–330 nos
        # outros anos): conta como "saiu" quem não está em junho OU em setembro (se setembro já existe); as saídas só de setembro que
        # foram compradas somem do Yahoo e caem fora na execução (só fica quem continuou negociando)
        depois = set(pos.cusip) & (set(set_.cusip) if len(set_) else set(pos.cusip))
        entrou = (set(pos.cusip) | set(set_.cusip)) - set(pre.cusip)
        novos = pd.concat([pos, set_]).drop_duplicates("cusip")
        for lado, a, z_ in (("sai", pre, set(pre.cusip) - depois), ("entra", novos, entrou)):
            a = a.assign(pct=a.valor.rank(pct=True))
            z = a[a.cusip.isin(z_)]
            for r in z.itertuples():
                m = ct[(ct.cusip == r.cusip) & (ct.data <= rc + pd.Timedelta(days=60))]
                m = m if len(m) else ct[ct.cusip == r.cusip]
                tk_era = m.tk.iloc[-1] if len(m) else ""
                cik = IE.cik_de(tk_era, rc) if tk_era else -1
                ev.append({"ano": ano, "lado": lado, "cusip": r.cusip, "nome": r.nome, "tk_era": tk_era, "cik": cik,
                           "ticker": IE.px_de(cik, tk_era) if tk_era else "", "pct_valor": r.pct, "recon": rc, "data": rc - pd.Timedelta(days=1)})
    ev = pd.DataFrame(ev)
    P, V = G.painel_universo()
    falta = sorted(set(ev.ticker) - set(P.columns) - {""})
    Y = G.yf_baixa(falta, "russell_extra", ini="2018-01-01")
    if len(Y):
        P2 = Y[[c for c in Y if c.endswith("|Close")]]
        P2.columns = [c.split("|")[0] for c in P2]
        V2 = Y[[c for c in Y if c.endswith("|Volume")]]
        V2.columns = [c.split("|")[0] for c in V2]
        P2, V2 = P2.loc[:, ~P2.columns.isin(P.columns)], V2.loc[:, ~V2.columns.isin(V.columns)]
        P = pd.concat([P, P2.reindex(P.index)], axis=1)
        V = pd.concat([V, V2.reindex(P.index)], axis=1)
    tk = sorted(set(ev.ticker) & set(P.columns))
    Pc = pd.concat([P[tk], G.etf(["IWM"])], axis=1)
    Pc = Pc[Pc.index >= "2018-06-01"].astype("float64")
    return ev, Pc, V[tk].reindex(Pc.index).astype("float64")


def carrega():
    f = G.CACHE / "russell"
    if not (f / "precos.parquet").exists():
        ev, P, V = _constroi()
        f.mkdir(parents=True, exist_ok=True)
        ev.to_parquet(f / "eventos.parquet")
        P.to_parquet(f / "precos.parquet", compression="zstd")
        V.to_parquet(f / "volume.parquet", compression="zstd")
    if not (f / "bruto.parquet").exists():
        G.preco_bruto(pd.read_parquet(f / "precos.parquet")).to_parquet(f / "bruto.parquet", compression="zstd")
    return {"eventos": pd.read_parquet(f / "eventos.parquet"), "precos": pd.read_parquet(f / "precos.parquet"),
            "volume": pd.read_parquet(f / "volume.parquet"), "bruto": pd.read_parquet(f / "bruto.parquet")}


_CACHE = {}


def _trades(d, lado, dias, faixa, n, sobrev="neutro"):
    ev, P, V = d["eventos"], d["precos"], d["volume"]
    idx = P.index
    giro = (P * V).rolling(20, min_periods=10).mean()
    out, sint = [], {}
    for ano, g in ev.groupby("ano"):
        rc = g.recon.iloc[0]
        jr = idx.searchsorted(rc)
        if jr >= len(idx) or idx[jr] != rc:
            continue
        if lado in ("sai_pos", "ambos"):
            s = g[(g.lado == "sai") & (g.pct_valor <= faixa)].sort_values("pct_valor")
            dec = idx[jr - 1]                                           # decide na véspera, compra no leilão da reconstituição
            k = 0
            for r in s.itertuples():
                t = r.ticker
                tem = bool(t) and t in P.columns and np.isfinite(P[t].ffill(limit=5).iloc[jr])
                if tem:
                    if not (d["bruto"][t].loc[:dec].iloc[-1:].ge(1).all() and giro[t].loc[:dec].iloc[-1:].ge(2e5).all()):
                        continue
                else:
                    if sobrev == "ignora" or (bool(t) and t in P.columns):  # tinha preço e sumiu antes da recon = comprada (fora)
                        continue
                    t = f"{r.tk_era or r.cusip}*{ano}"
                    if sobrev == "duro":
                        sint[t] = G.sintetico(idx, idx[jr - 1], nome=t)
                    else:
                        h = P["IWM"]
                        sint[t] = (h / h.iloc[jr - 1]).where(np.arange(len(idx)) >= jr - 1).rename(t)
                out.append({"ticker": t, "decisao": dec, "dias": int(dias), "lado": 1, "regiao": "US", "custo": MEIO_SPREAD, "aluguel": 0.0})
                k += 1
                if k >= n:
                    break
        if lado in ("entra_pre", "ambos"):
            e = g[(g.lado == "entra") & (g.pct_valor <= faixa)].sort_values("pct_valor")
            j0 = idx.searchsorted(pd.Timestamp(f"{ano}-05-26"))         # lista preliminar pública (4ª sexta de maio)
            if j0 >= jr - 1:
                continue
            dec = idx[j0]
            ok = [t for t in e.ticker if t in P.columns and d["bruto"][t].loc[:dec].iloc[-1:].ge(1).all() and giro[t].loc[:dec].iloc[-1:].ge(2e5).all()
                  and P[t].loc[:dec].notna().sum() >= 250]               # sem IPOs (entram por regra própria)
            for t in ok[:int(n)]:
                out.append({"ticker": t, "decisao": dec, "saida": idx[jr - 1], "lado": 1, "regiao": "US", "custo": MEIO_SPREAD, "aluguel": 0.0})
    return pd.DataFrame(out), (pd.concat([P, pd.DataFrame(sint)], axis=1) if sint else P)


def _roda(d, capital, custo_mult, lag, alavancagem, lado, dias, faixa, n, peso, hedge_fx, sobrev):
    k = (id(d), len(d["precos"]), d["precos"].index.max(), len(d["eventos"]), capital, custo_mult, lag, alavancagem, lado, int(dias),
         round(faixa, 4), int(n), round(peso, 5), hedge_fx, sobrev)
    if k not in _CACHE:
        tr, P = _trades(d, lado, dias, faixa, int(n), sobrev)
        res = G.livro(tr, P, capital, custo_mult, lag, alavancagem, peso, teto=1.0, hedge={"US": "IWM"}, hedge_fx=hedge_fx)
        res["P"] = P
        if len(_CACHE) > 30:
            _CACHE.clear()
        _CACHE[k] = res
    return _CACHE[k]


def excesso(d, capital=20000, custo_mult=1, lag=0, regime=REGIME, alavancagem=1, lado=PARAMS["lado"], dias=PARAMS["dias"], faixa=PARAMS["faixa"],
            n=PARAMS["n"], peso=PARAMS["peso"], hedge_fx=PARAMS["hedge_fx"], sobrev=PARAMS["sobrev"]):
    res = _roda(d, capital, custo_mult, lag, alavancagem, lado, dias, faixa, n, peso, hedge_fx, sobrev)
    return C.aplica_regime(res["e"], regime, CUSTO_TROCA * custo_mult)


def posicoes(d, capital=20000, lado=PARAMS["lado"], dias=PARAMS["dias"], faixa=PARAMS["faixa"], n=PARAMS["n"], peso=PARAMS["peso"],
             hedge_fx=PARAMS["hedge_fx"], sobrev=PARAMS["sobrev"]):
    res = _roda(d, capital, 1, 0, 1, lado, dias, faixa, n, peso, hedge_fx, sobrev)
    return G.posicoes_de(res, res["P"], capital)


def negocios(d, capital=20000, lado=PARAMS["lado"], dias=PARAMS["dias"], faixa=PARAMS["faixa"], n=PARAMS["n"], peso=PARAMS["peso"],
             hedge_fx=PARAMS["hedge_fx"], sobrev=PARAMS["sobrev"]):
    res = _roda(d, capital, 1, 0, 1, lado, dias, faixa, n, peso, hedge_fx, sobrev)
    return G.negocios_de(res, capital, res["P"])
