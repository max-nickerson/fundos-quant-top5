"""
Arbitragem de ofertas públicas de aquisição (tender offers em dinheiro) nos EUA em tamanho de PF — com o viés de sobrevivência EXPLÍCITO.

Tese de mesa: quando um comprador lança oferta em dinheiro por uma empresa pequena, o alvo negocia abaixo do preço da oferta (o spread é
o seguro contra a quebra do negócio + o custo do dinheiro até o fechamento). Os arbitradores grandes não se dão ao trabalho em alvos
de US$ 100–500 milhões (o spread em dólares é pequeno para o tamanho deles), e fundos de índice/gestores long-only VENDEM o alvo logo
depois do anúncio (não querem o risco de quebra) — o vendedor forçado. PF compra R$ 1–2 mil por alvo no dia seguinte ao SC 14D9
(recomendação do alvo, arquivado na SEC no início da oferta) e segura até a liquidação (o papel some) ou `dias` pregões.

O problema (lição da pesquisa, global.md G1/IE): o Yahoo APAGA quem foi comprado. Dos alvos com SC 14D9 desde 2008, ~75% deslistaram em
até 1 ano (negócio concluído) e NÃO têm preço; os que têm preço são os fracassos, as ofertas parciais e os tickers reaproveitados por
outra empresa. Tratamento (sem inventar o resultado):
  - alvo COM preço e coerente (se o EDGAR diz que deslistou, o preço do Yahoo tem de acabar até 30 dias depois; senão é outra empresa
    com o mesmo ticker -> fora): trajetória real;
  - alvo SEM preço que deslistou em até 1 ano (25-NSE/15-12 no EDGAR) = negócio concluído: trajetória sintética que rende
    `spread_concluido` (a.p., linear até a data de deslistagem). NÃO há preço para medir esse spread — por isso o fundo roda com
    spread_concluido = 0 ("piso": o concluído só devolve o dinheiro) e as variantes mostram 2% e 4% (spread bruto típico de oferta em
    dinheiro em small cap, literatura: Mitchell & Pulvino 2001; Jetley & Ji 2010);
  - alvo SEM preço que NÃO deslistou em 1 ano: sem informação (o 25-NSE muitas vezes sai sob o CIK do comprador; prazo regulatório
    longo) -> neutro (rende 0%); variante "duro": −30% em 166 pregões (regra da auditoria, como se todos tivessem fracassado).
APLICAVEL = False: o resultado depende de uma hipótese não mensurável com dado gratuito (preço dos alvos comprados).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

import fg_comum as G  # noqa: E402

C, pf = G.C, G.pf

NOME = "Arbitragem de ofertas em dinheiro (tender offers) de small caps nos EUA — PF IBKR, sobrevivência explícita"
TESE = ("Compro o alvo de oferta pública em dinheiro no dia seguinte ao SC 14D9 e seguro até a liquidação; R$ 1–2 mil por alvo; "
        "concluídos sem preço no Yahoo entram com spread hipotético (0% no fundo, 2–4% nas variantes).")
BENCHMARK = "CDI"
INICIO, CORTE = "2008-01-01", "2021-01-01"
REGIME = "nenhum"
CUSTO_TROCA = .001
CLASSE_IR = "exterior"
PARAMS = {"dias": 63, "peso": .05, "spread_concluido": 0.0, "hedge_fx": "wdo", "sobrev": "neutro"}
GRADE = {"dias": [63, 126], "peso": [.05, .08]}
VIZINHANCA = {"dias": (50, 180), "peso": (.04, .10)}
MEIO_SPREAD = .002
INSTRUMENTOS = {"alvos de oferta": {"onde": "IBKR", "ticker": "~40–100 por ano (SC 14D9)", "lote": "fração", "custo": "US$ 0,0035/ação mín. 0,35 + 0,2%"},
                "WDO": {"onde": "B3", "ticker": "WDO (vendido)", "lote": "US$ 10 mil", "custo": "R$ 3,70/lado"}}
APLICAVEL = False
MOTIVO = ("Intestável com dado gratuito: o Yahoo não tem preço dos alvos comprados (~75% dos casos); o número do fundo é um PISO (concluído "
          "rende 0%) e as variantes com spread de 2–4% são hipóteses, não medidas. A operação em si é viável na IBKR (fração).")
ALAVANCAGENS = [1, 1.5, 2]
MOTIVO_ALAV = "peso por alvo x L; carteira de 5–15 alvos simultâneos; o risco é a quebra de um negócio (−20 a −40% no dia)."
VARIANTES = {"concluídos rendem 2%": {"spread_concluido": .02}, "concluídos rendem 4%": {"spread_concluido": .04},
             "concluídos rendem 6%": {"spread_concluido": .06}, "só alvos com preço (anti-sobrevivência)": {"spread_concluido": None},
             "sem preço e sem deslistagem a -30%": {"sobrev": "duro"}}


def carrega():
    f = G.CACHE / "merger_arb"
    if not (f / "precos.parquet").exists():
        a = pd.read_parquet(G.CACHE / "alvos_ofertas.parquet")          # ideias_global.alvos_ofertas() (SEC: SC 14D9 + 25-NSE/15-12)
        a = a[a.data >= "2007-06-01"].copy()
        P = pd.concat([G.ler_fd("y_alvos.parquet"), G.painel_y("us"), G.painel_y("sp")], axis=1)
        P = P.loc[:, ~P.columns.duplicated()]
        tk = sorted(set(a.ticker.dropna()) & set(P.columns))
        P = P[tk].copy()
        P.index = pd.DatetimeIndex(P.index).normalize()
        P = P[P.index >= "2007-01-01"].astype("float64")
        f.mkdir(parents=True, exist_ok=True)
        a.to_parquet(f / "eventos.parquet")
        P.to_parquet(f / "precos.parquet", compression="zstd")
    return {"eventos": pd.read_parquet(f / "eventos.parquet"), "precos": pd.read_parquet(f / "precos.parquet")}


_CACHE = {}


def _trades(d, dias, spread_concluido, sobrev="neutro"):
    P, ev = d["precos"], d["eventos"]
    idx = P.index
    out, sint = [], {}
    for r in ev.itertuples():
        j = idx.searchsorted(r.data)                                     # 1º pregão >= SC 14D9 (decide no fechamento)
        if j >= len(idx) - 1:
            continue
        t = r.ticker if isinstance(r.ticker, str) else ""
        tem = False
        if t and t in P.columns:
            s = P[t]
            antes = s.iloc[max(j - 10, 0):j + 1].notna().any()
            tem = bool(antes)
            if tem and bool(r.concluiu_1a) and pd.notna(r.dl):         # EDGAR diz que deslistou: o preço tem de acabar até 30 dias depois
                depois = s[s.index > r.dl + pd.Timedelta(days=30)].notna().any()
                if depois:
                    continue                                             # ticker reaproveitado por outra empresa
        if not tem:
            if spread_concluido is None:
                continue
            nome = f"{t or r.cik}*{pd.Timestamp(r.data):%Y%m%d}"
            if bool(r.concluiu_1a) and pd.notna(r.dl):                   # concluído: rende spread linear até a deslistagem e some
                k1 = idx.searchsorted(r.dl)
                n = max(k1 - j, 2)
                v = np.full(len(idx), np.nan)
                m = min(k1 + 1, len(idx)) - j
                if m < 2:
                    continue
                v[j:j + m] = 1 + spread_concluido * np.minimum(np.arange(m) / n, 1.0)
                sint[nome] = pd.Series(v, index=idx)
            elif sobrev == "duro":                                       # não deslistou em 1 ano (fracassou?) e sumiu depois: −30%
                sint[nome] = G.sintetico(idx, idx[j], nome=nome)
            else:                                                        # sem informação (o 25-NSE pode ter saído com outro CIK): neutro
                v = np.full(len(idx), np.nan)
                v[j:min(j + dias + 2, len(idx))] = 1.0
                sint[nome] = pd.Series(v, index=idx)
            t = nome
        out.append({"ticker": t, "decisao": idx[j], "dias": dias, "lado": 1, "regiao": "US", "custo": MEIO_SPREAD, "aluguel": 0.0,
                    "sintetico": not tem})
    if sint:
        P = pd.concat([P, pd.DataFrame(sint)], axis=1)
    return pd.DataFrame(out), P


def _roda(d, capital, custo_mult, lag, alavancagem, dias, peso, spread_concluido, hedge_fx, sobrev="neutro"):
    k = (id(d), len(d["precos"]), d["precos"].index.max(), len(d["eventos"]), capital, custo_mult, lag, alavancagem, int(dias), round(peso, 5),
         spread_concluido, hedge_fx, sobrev)
    if k not in _CACHE:
        tr, P = _trades(d, int(dias), spread_concluido, sobrev)
        res = G.livro(tr, P, capital, custo_mult, lag, alavancagem, peso, teto=1.0, hedge=None, hedge_fx=hedge_fx)
        res["P"] = P
        if len(_CACHE) > 30:
            _CACHE.clear()
        _CACHE[k] = res
    return _CACHE[k]


def excesso(d, capital=20000, custo_mult=1, lag=0, regime=REGIME, alavancagem=1, dias=PARAMS["dias"], peso=PARAMS["peso"],
            spread_concluido=PARAMS["spread_concluido"], hedge_fx=PARAMS["hedge_fx"], sobrev=PARAMS["sobrev"]):
    res = _roda(d, capital, custo_mult, lag, alavancagem, dias, peso, spread_concluido, hedge_fx, sobrev)
    return C.aplica_regime(res["e"], regime, CUSTO_TROCA * custo_mult)


def posicoes(d, capital=20000, dias=PARAMS["dias"], peso=PARAMS["peso"], spread_concluido=PARAMS["spread_concluido"], hedge_fx=PARAMS["hedge_fx"],
             sobrev=PARAMS["sobrev"]):
    res = _roda(d, capital, 1, 0, 1, dias, peso, spread_concluido, hedge_fx, sobrev)
    return G.posicoes_de(res, res["P"], capital)


def negocios(d, capital=20000, dias=PARAMS["dias"], peso=PARAMS["peso"], spread_concluido=PARAMS["spread_concluido"], hedge_fx=PARAMS["hedge_fx"],
             sobrev=PARAMS["sobrev"]):
    res = _roda(d, capital, 1, 0, 1, dias, peso, spread_concluido, hedge_fx, sobrev)
    ng = G.negocios_de(res, capital, res["P"])
    ng["sintetico"] = ng.ativo.astype(str).str.contains(r"\*")
    return ng
