"""
Spin-offs PEQUENOS dos EUA depois da venda forçada — versão PF honesta (IBKR com só o necessário fora, sobrevivência tratada).

Tese de mesa: a separada pequena nasce fora do mandato de quem tinha a controladora: o fundo de S&P 500 recebe ações de uma empresa de
US$ 300 milhões que não está no índice e vende no 1º mês sem olhar preço; o gestor de large cap faz o mesmo. Quanto MENOR a separada,
maior a venda forçada em relação ao giro e menor o interesse de quem compraria (analistas só começam a cobrir depois). É um papel que o
institucional não consegue comprar em tamanho — R$ 1–2 mil por nome é a escala certa. Compro no fim do 1º mês de negociação (a venda
dos indexados já passou), seguro 6–12 meses, hedge com IWM (small caps, o mesmo tamanho) vendido em ações inteiras.

Diferenças para os fundos já testados (rev_spinoffs: todos os tamanhos, 40 dias, hedge SPY+IWM; gl_spinoff: sem tratamento de
sobrevivência): (i) só separadas pequenas — giro médio dos primeiros 20 pregões < US$ 10 mi/dia (decidido na entrada, sem olhar à
frente); (ii) entrada no fim do 1º mês; (iii) hedge cambial com WDO quando o saldo em dólar arredonda para 1 contrato.

Sobrevivência (base da auditoria, pf/dados/global_cripto/spin_sem_preco.csv): 158 separadas que NEGOCIARAM (insiders arquivando
Forms 3/4 por > 90 dias) mas sumiram do Yahoo. Classificadas pelo EDGAR (sec_indice + 8-K item 1.03): 24 pediram recuperação judicial
e 34 sumiram sem registro de compra (deslistadas/deregistradas) -> trajetória sintética de −30% em 166 pregões (regra da auditoria);
100 com proxy de fusão/oferta (DEFM14A, SC 14D9, SC TO-T, PREM14A, SC 13E3) -> andam com o IWM (alfa zero; conservador, porque a
compra costuma vir com prêmio). Como não há giro para elas, entram TODAS no livro "pequeno" (conservador). Variantes: sem os
sintéticos (o viés) e "duro" (todas as que sumiram a −30%).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

import fg_comum as G  # noqa: E402

C, pf = G.C, G.pf

NOME = "Spin-offs pequenos dos EUA após a venda forçada (PF: IBKR, sobrevivência tratada)"
TESE = ("Compro a separada PEQUENA (giro < US$ 10 mi/dia) no fim do 1º mês, quando os indexados da controladora já venderam; seguro "
        "6–12 meses com IWM vendido; R$ 1–2,5 mil por nome; sintéticos para quem sumiu do Yahoo.")
BENCHMARK = "CDI"
INICIO, CORTE = "2008-01-01", "2021-01-01"
REGIME = "nenhum"
CUSTO_TROCA = .001
CLASSE_IR = "exterior"
PARAMS = {"espera": 40, "dias": 252, "peso": .05, "giro_max": 10e6, "sinteticos": "classe", "hedge_fx": "wdo"}
GRADE = {"espera": [20, 40], "dias": [126, 252]}
VIZINHANCA = {"espera": (15, 50), "dias": (100, 300), "peso": (.035, .07)}
MEIO_SPREAD = .004                       # separada pequena recém-listada: meio spread ~0,4% (o dobro da mid cap)
INSTRUMENTOS = {"spin-offs": {"onde": "IBKR", "ticker": "~5–10 pequenos por ano", "lote": "fração", "custo": "US$ 0,0035/ação mín. 0,35 + 0,4%"},
                "IWM": {"onde": "IBKR (vendido)", "ticker": "IWM", "lote": "ações inteiras", "custo": "aluguel 0,3% a.a."},
                "WDO": {"onde": "B3", "ticker": "WDO (vendido)", "lote": "1 contrato = US$ 10 mil", "custo": "R$ 3,70/lado, rola todo mês"}}
APLICAVEL = True
MOTIVO = ("Operável na IBKR com fração (R$ 1–2,5 mil por nome); hedge em ações inteiras de IWM (~R$ 1,3 mil) e conta margem com US$ 2 mil. "
          "Poucos nomes por ano: carteira concentrada.")
ALAVANCAGENS = [1, 1.5, 2]
MOTIVO_ALAV = "peso por nome x L, pago à vista; o livro dura 12 meses — 5x passaria o capital."
VARIANTES = {"todos os tamanhos": {"giro_max": 1e12}, "sem os sintéticos (viés)": {"sinteticos": "nao"}, "todas as que sumiram a -30%": {"sinteticos": "duro"}, "sem WDO": {"hedge_fx": "nenhum"},
             "6 meses": {"dias": 126}, "entra no fim do 1º mês": {"espera": 20}}


def carrega():
    f = G.U.CACHE / "rev_spinoffs"
    if not (f / "precos.parquet").exists():                 # cache montado por rev_spinoffs (base da auditoria)
        import rev_spinoffs as RS                            # noqa: E402
        RS.carrega()
    ev = pd.read_parquet(f / "eventos.parquet")
    ev = ev[~ev.sintetico]                                   # os sintéticos da auditoria são refeitos aqui, com a classe do EDGAR
    P = pd.read_parquet(f / "precos.parquet")
    P = P[[c for c in P.columns if not c.endswith("*")]]
    X = G.yf_baixa(list(ev[~ev.sintetico].ticker), "spin_volume", ini="2006-01-01")
    V = X[[c for c in X if c.endswith("|Volume")]]
    V.columns = [c.split("|")[0] for c in V]
    Pv = X[[c for c in X if c.endswith("|Close")]]
    Pv.columns = [c.split("|")[0] for c in Pv]
    giro = (Pv * V.reindex(columns=Pv.columns)).reindex(P.index)
    return {"eventos": ev, "precos": P, "giro": giro, "sumidas": _sumidas()}


def _sumidas():
    """Separadas que negociaram e sumiram do Yahoo, com a classe pelo EDGAR (quebra / sumiu / comprada). Cache."""
    f = G.CACHE / "spin_sumidas.parquet"
    if f.exists():
        return pd.read_parquet(f)
    sys.path.insert(0, str(G.FD.parent))
    import ideias_i_eventos as IE                            # noqa: E402
    s = pd.read_csv(G.U.CACHE / "global_cripto" / "spin_sem_preco.csv", parse_dates=["d0", "d1", "d10"])
    ix = pd.read_parquet(G.FD / "sec_indice.parquet")
    c11 = IE._fts_ev("cap11", ["8-K"])
    c11 = c11[c11.itens.str.contains("1.03", regex=False)].groupby("cik").data.min()
    aq = ix[ix.forma.isin(["DEFM14A", "SC 14D9", "SC TO-T", "DEFM14C", "SC 13E3", "PREM14A"])].groupby("cik").data.min()
    s["classe"] = ["quebra" if pd.notna(c11.get(c)) and c11.get(c) >= d else ("comprada" if pd.notna(aq.get(c)) and aq.get(c) >= d else "sumiu")
                   for c, d in zip(s.cik, s.d10)]
    s["ini"] = np.maximum(s.d0, s.d10)
    s["data"] = s.d10
    s.to_parquet(f)
    return s


_CACHE = {}


def _trades(d, espera, dias, giro_max, sinteticos):
    P, ev, giro = d["precos"], d["eventos"].copy(), d["giro"]
    ev["sintetico"] = False
    if sinteticos != "nao":                                  # trajetórias sintéticas de quem sumiu (desde max(1º Form 3/4, 10-12B))
        su = d["sumidas"]
        sint, datas = {}, {}
        for t, ini, cl, d10 in zip(su.ticker, su.ini, su.classe, su.d10):
            nome = f"{t}*{pd.Timestamp(d10):%Y%m}"
            datas[nome] = d10
            if cl == "comprada" and sinteticos == "classe":
                h = P["IWM"]
                k = P.index.searchsorted(ini)
                if k < len(P):
                    sint[nome] = (h / h.iloc[k]).where(np.arange(len(P)) >= k)
            else:
                sint[nome] = G.sintetico(P.index, ini, nome=nome)
        P = pd.concat([P, pd.DataFrame(sint, index=P.index)], axis=1)
        ev = pd.concat([ev, pd.DataFrame({"ticker": list(sint), "data": [datas[n] for n in sint], "sintetico": True})], ignore_index=True)
    out = []
    for t, d10, sint in zip(ev.ticker, pd.to_datetime(ev["data"]), ev.sintetico):
        if t not in P:
            continue
        x = P[t].dropna()
        antes = x[x.index < d10 - pd.Timedelta(days=30)]
        x = x[x.index >= d10 - pd.Timedelta(days=30)]
        if len(antes) or len(x) <= espera + 1 or x.index[0] > d10 + pd.Timedelta(days=365):
            continue
        dd = x.index[espera]                                  # decisão no fechamento do pregão `espera` (contado do 1º preço)
        if not sint:
            g = giro[t].reindex(x.index[:espera + 1]).iloc[-20:].median() if t in giro else np.nan
            if not (np.isfinite(g) and g < giro_max):
                continue
        out.append({"ticker": t, "decisao": dd, "dias": dias, "lado": 1, "regiao": "US", "custo": MEIO_SPREAD, "aluguel": 0.0})
    return pd.DataFrame(out), P


def _roda(d, capital, custo_mult, lag, alavancagem, espera, dias, peso, giro_max, sinteticos, hedge_fx):
    k = (id(d), len(d["precos"]), d["precos"].index.max(), capital, custo_mult, lag, alavancagem, espera, dias, round(peso, 5), giro_max,
         sinteticos, hedge_fx)
    if k not in _CACHE:
        tr, P = _trades(d, espera, dias, giro_max, sinteticos)
        res = G.livro(tr, P, capital, custo_mult, lag, alavancagem, peso, teto=1.0, hedge={"US": "IWM"}, hedge_fx=hedge_fx)
        if len(_CACHE) > 40:
            _CACHE.clear()
        res["P"] = P
        _CACHE[k] = res
    return _CACHE[k]


def excesso(d, capital=20000, custo_mult=1, lag=0, regime=REGIME, alavancagem=1, espera=PARAMS["espera"], dias=PARAMS["dias"],
            peso=PARAMS["peso"], giro_max=PARAMS["giro_max"], sinteticos=PARAMS["sinteticos"], hedge_fx=PARAMS["hedge_fx"]):
    res = _roda(d, capital, custo_mult, lag, alavancagem, espera, dias, peso, giro_max, sinteticos, hedge_fx)
    return C.aplica_regime(res["e"], regime, CUSTO_TROCA * custo_mult)


def posicoes(d, capital=20000, espera=PARAMS["espera"], dias=PARAMS["dias"], peso=PARAMS["peso"], giro_max=PARAMS["giro_max"],
             sinteticos=PARAMS["sinteticos"], hedge_fx=PARAMS["hedge_fx"]):
    res = _roda(d, capital, 1, 0, 1, espera, dias, peso, giro_max, sinteticos, hedge_fx)
    return G.posicoes_de(res, res["P"], capital)


def negocios(d, capital=20000, espera=PARAMS["espera"], dias=PARAMS["dias"], peso=PARAMS["peso"], giro_max=PARAMS["giro_max"],
             sinteticos=PARAMS["sinteticos"], hedge_fx=PARAMS["hedge_fx"]):
    res = _roda(d, capital, 1, 0, 1, espera, dias, peso, giro_max, sinteticos, hedge_fx)
    ng = G.negocios_de(res, capital, res["P"])
    ng["sintetico"] = ng.ativo.astype(str).str.endswith("*")
    return ng
