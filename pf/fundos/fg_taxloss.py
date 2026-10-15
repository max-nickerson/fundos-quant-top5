"""
Tax-loss selling de dezembro em small caps dos EUA: compro os maiores perdedores do ano na 2ª quinzena de dezembro e vendo em janeiro.

Tese de mesa: o investidor americano (pessoa física e fundo com cotista tributável) vende o que caiu no ano até o fim de dezembro para
realizar o prejuízo e abater do imposto (wash sale: só pode recomprar 31 dias depois). É venda que não olha preço, concentrada em
small caps perdedoras e pouco líquidas; os fundos fazem window dressing no mesmo sentido (tiram os perdedores da carteira de fim de
ano). Em janeiro a pressão some e o papel volta (efeito janeiro, Roll 1983; Reinganum 1983). Institucional grande não entra: o papel é
pequeno demais. PF compra R$ 1 mil por nome na IBKR com fração e hedge com IWM vendido.
Regra: no fechamento do último pregão <= `dia` de dezembro, ranqueia as ações com preço da época (não ajustado) >= US$ 5, giro de 20 dias entre US$ 1 e 50
milhões/dia (small cap negociável) e retorno no ano <= `perda`; compra as `n` piores (5% cada) no fechamento seguinte e vende no
fechamento do pregão `saida` de janeiro. Hedge IWM em ações inteiras. Variante "etf": comprado em IWC (micro caps) vendido em SPY no
mesmo período (sem seleção de ações, sem viés de sobrevivência).
Viés de sobrevivência: o universo é o Yahoo de hoje (3,6 mil + 5,7 mil tickers com preço; deslistadas não existem). Em uma janela de
3–4 semanas quase nenhuma ação some, mas FALTAM no universo os perdedores que quebraram/foram comprados DEPOIS — se eles iam pior em
janeiro, o resultado é otimista. A variante ETF (IWC−SPY) é a referência sem esse viés.
Conta no exterior: o dinheiro vai em dezembro e volta em fevereiro/março (pf.custo_conta_exterior: IOF 1,1% + spread na ida, 0,38% +
spread na volta, 2–3 meses sem CDI) — o custo fixo de ~5% do livro por ano é o que o efeito janeiro tem de pagar.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

import fg_comum as G  # noqa: E402

C, pf = G.C, G.pf

NOME = "Tax-loss selling de dezembro: small caps perdedoras dos EUA de dezembro a janeiro (PF IBKR)"
TESE = ("Compro na 2ª quinzena de dezembro as small caps que mais caíram no ano (venda para abater imposto e window dressing) e vendo em "
        "janeiro; hedge IWM; R$ 1 mil por nome; o resto do ano o caixa fica no CDI.")
BENCHMARK = "CDI"
INICIO, CORTE = "2008-01-01", "2021-01-01"
REGIME = "nenhum"
CUSTO_TROCA = .001
CLASSE_IR = "exterior"
PARAMS = {"universo": "acoes", "dia": 20, "perda": -.50, "saida": 5, "n": 20, "peso": .05, "hedge_fx": "wdo"}
GRADE = {"perda": [-.3, -.5], "saida": [5, 15]}
VIZINHANCA = {"perda": (-.55, -.25), "saida": (3, 20), "dia": (15, 23), "n": (10, 25)}
MEIO_SPREAD = .004                               # small cap perdedora em dezembro: meio spread ~0,4%
INSTRUMENTOS = {"small caps perdedoras": {"onde": "IBKR", "ticker": "até 20 por ano", "lote": "fração", "custo": "US$ 0,0035/ação mín. 0,35 + 0,4%"},
                "IWM": {"onde": "IBKR (vendido)", "ticker": "IWM", "lote": "ações inteiras", "custo": "aluguel 0,3% a.a."},
                "variante": {"onde": "IBKR", "ticker": "IWC comprado / SPY vendido", "lote": "ações inteiras", "custo": "spread + aluguel"}}
APLICAVEL = True
MOTIVO = "Operável: 1 vez por ano, 20 ordens de compra e 20 de venda na IBKR com fração; precisa remeter em dezembro e trazer de volta."
ALAVANCAGENS = [1, 1.5, 2]
MOTIVO_ALAV = "peso por nome x L (5% -> 7,5%/10%), comprado à vista; livro de 1 mês por ano."
VARIANTES = {"ETF: IWC vendido SPY": {"universo": "etf"}, "sem WDO": {"hedge_fx": "nenhum"}, "dia 15": {"dia": 15}}
SUPER = {"preco": 2.0, "giro": 5e5, "perda": -.2}   # superconjunto guardado no cache (os filtros do fundo são mais estreitos)


def _constroi():
    P, V = G.painel_universo()
    P = P[P.index >= "2006-06-01"]
    V = V.reindex(P.index)
    giro = (P * V).rolling(20, min_periods=10).mean()
    keep = set()
    for ano in range(2006, 2027):
        fim_ant = P.index[P.index < f"{ano}-01-01"]
        dez = P.index[(P.index >= f"{ano}-12-01") & (P.index <= f"{ano}-12-31")]
        if not len(fim_ant) or not len(dez):
            continue
        p0 = P.loc[fim_ant[-1]]
        for dd in dez:
            ytd = P.loc[dd] / p0 - 1
            ok = (ytd <= SUPER["perda"]) & (P.loc[dd] >= SUPER["preco"]) & (giro.loc[dd] >= SUPER["giro"])
            keep |= set(ok[ok].index)
    keep = sorted(keep)
    etf = G.yf_baixa(["IWC", "IWM", "SPY", "IWN", "VTWO"], "etfs_extra", ini="2005-01-01")
    E = etf[[c for c in etf if c.endswith("|Close")]]
    E.columns = [c.split("|")[0] for c in E]
    return P[keep].astype("float64"), V[keep].astype("float64"), E.reindex(P.index).astype("float64")


def carrega():
    f = G.CACHE / "taxloss"
    if not (f / "precos.parquet").exists():
        P, V, E = _constroi()
        f.mkdir(parents=True, exist_ok=True)
        P.to_parquet(f / "precos.parquet", compression="zstd")
        V.to_parquet(f / "volume.parquet", compression="zstd")
        E.to_parquet(f / "etfs.parquet", compression="zstd")
    P = pd.read_parquet(f / "precos.parquet")
    if not (f / "bruto.parquet").exists():
        G.preco_bruto(P).to_parquet(f / "bruto.parquet", compression="zstd")
    return {"precos": P, "volume": pd.read_parquet(f / "volume.parquet"), "etfs": pd.read_parquet(f / "etfs.parquet"),
            "bruto": pd.read_parquet(f / "bruto.parquet")}


_CACHE = {}


def _trades(d, universo, dia, perda, saida, n):
    P, V, E = d["precos"], d["volume"], d["etfs"]
    idx = P.index
    giro = (P * V).rolling(20, min_periods=10).mean()
    out = []
    for ano in range(2006, 2027):
        fim_ant = idx[idx < f"{ano}-01-01"]
        dez = idx[(idx >= f"{ano}-12-01") & (idx <= pd.Timestamp(f"{ano}-12-01") + pd.Timedelta(days=int(dia) - 1))]
        jan = C.DIAS_US[C.DIAS_US >= f"{ano + 1}-01-01"]                 # calendário da NYSE (sabido de antemão)
        if not len(fim_ant) or not len(dez) or len(jan) <= saida:
            continue
        dd = dez[-1]
        sai = jan[int(saida)]
        if universo == "etf":
            out.append({"ticker": "IWC", "decisao": dd, "saida": sai, "lado": 1, "regiao": "US", "custo": .0005, "aluguel": 0.0, "peso": 1.0})
            continue
        p0, p1 = P.loc[fim_ant[-1]], P.loc[dd]
        ytd = p1 / p0 - 1
        g = giro.loc[dd]
        pb = d["bruto"].loc[dd]                                         # preço da época (sem grupamentos posteriores)
        ok = (ytd <= perda) & (pb >= 5) & (g >= 1e6) & (g <= 50e6) & (P.loc[:dd].notna().sum() >= 200)
        sel = ytd[ok].sort_values().index[:int(n)]
        for t in sel:
            out.append({"ticker": t, "decisao": dd, "saida": sai, "lado": 1, "regiao": "US", "custo": MEIO_SPREAD, "aluguel": 0.0})
    return pd.DataFrame(out)


def _roda(d, capital, custo_mult, lag, alavancagem, universo, dia, perda, saida, n, peso, hedge_fx):
    k = (id(d), len(d["precos"]), d["precos"].index.max(), capital, custo_mult, lag, alavancagem, universo, int(dia), round(perda, 4),
         int(saida), int(n), round(peso, 5), hedge_fx)
    if k not in _CACHE:
        tr = _trades(d, universo, dia, perda, saida, n)
        P = pd.concat([d["precos"], d["etfs"][["IWC", "IWM", "SPY"]]], axis=1)
        hedge = {"US": "SPY" if universo == "etf" else "IWM"}
        res = G.livro(tr, P, capital, custo_mult, lag, alavancagem, peso, teto=1.0, hedge=hedge, hedge_fx=hedge_fx)
        res["P"] = P
        if len(_CACHE) > 30:
            _CACHE.clear()
        _CACHE[k] = res
    return _CACHE[k]


def excesso(d, capital=20000, custo_mult=1, lag=0, regime=REGIME, alavancagem=1, universo=PARAMS["universo"], dia=PARAMS["dia"],
            perda=PARAMS["perda"], saida=PARAMS["saida"], n=PARAMS["n"], peso=PARAMS["peso"], hedge_fx=PARAMS["hedge_fx"]):
    res = _roda(d, capital, custo_mult, lag, alavancagem, universo, dia, perda, saida, n, peso, hedge_fx)
    return C.aplica_regime(res["e"], regime, CUSTO_TROCA * custo_mult)


def posicoes(d, capital=20000, universo=PARAMS["universo"], dia=PARAMS["dia"], perda=PARAMS["perda"], saida=PARAMS["saida"], n=PARAMS["n"],
             peso=PARAMS["peso"], hedge_fx=PARAMS["hedge_fx"]):
    res = _roda(d, capital, 1, 0, 1, universo, dia, perda, saida, n, peso, hedge_fx)
    return G.posicoes_de(res, res["P"], capital)


def negocios(d, capital=20000, universo=PARAMS["universo"], dia=PARAMS["dia"], perda=PARAMS["perda"], saida=PARAMS["saida"], n=PARAMS["n"],
             peso=PARAMS["peso"], hedge_fx=PARAMS["hedge_fx"]):
    res = _roda(d, capital, 1, 0, 1, universo, dia, perda, saida, n, peso, hedge_fx)
    return G.negocios_de(res, capital, res["P"])
