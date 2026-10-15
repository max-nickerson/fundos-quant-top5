"""
Opções de juros que uma PF consegue: Opção de Copom (CPM, digital sobre a decisão da Selic) — e por que IDI fica de fora.

IDI (opção sobre o índice de DI): o BVBG.086 da B3 (pf/dados/pf2_opcoes/pr_opcoes.parquet, 2018+) mostra 10–30 séries de IDI
negociadas por dia, mas SEMPRE em blocos de 10^4–10^6 contratos entre institucionais e NUNCA com oferta de compra/venda no
fechamento (0 linhas com bid/ask em 2018–2026). Sem livro, a PF não executa; sem índice IDI no dado, não dá nem para calcular a IV.
Documentado, não testado.

CPM: cada série paga 100 pontos se o Copom decidir exatamente aquela variação (strike 100000 = manutenção, 099750 = −0,25 pp,
100500 = +0,50 pp...) e zero caso contrário. O preço é a probabilidade que o mercado dá a cada decisão. Tese de mesa: mercado de
"previsão" pequeno, dominado por tesourarias que usam a CPM como hedge de cauda da carteira de DI -> as caudas (5–25 pontos) tendem a
sair caras (o hedger paga) e o favorito barato. Testo: (a) comprar o favorito, (b) vender o favorito, (c) vender as caudas de 5–25
pontos (risco definido: perda máxima = 100 − prêmio por contrato).
Tamanho: até jun/2025 1 ponto = R$ 100 (o contrato paga R$ 10 mil); desde jul/2025 1 ponto = R$ 1 (paga R$ 100) — multiplicador lido
do próprio dado (volume financeiro / contratos / preço). Contratos INTEIROS: com R$ 20 mil e 25% de risco por reunião, antes de
jul/2025 quase nunca cabe 1 contrato. Execução: sinal com os negócios do 2º pregão do mês, compra/venda no 3º pregão (t+1) ao preço
médio dos negócios ± 1,5 ponto de meio spread (o livro de CPM é ralo: bid/ask aparecem em ~30% das séries negociadas). Liquidação
no 1º pregão depois da reunião. Posição NÃO é marcada a mercado entre a entrada e a decisão (só há preço nos dias baixados) — o P&L
do negócio é exato, mas a curva diária fica "parada" (pior queda subestimada). IR: futuros_b3 / opções (15%).
"""
import numpy as np
import pandas as pd

import op_base as O

NOME = "Opção de Copom (CPM): favorito x caudas (IDI documentado: sem livro para PF)"
TESE = "Vendo as caudas caras (5–25 pontos) da opção digital de Copom ou compro o favorito, risco definido, liquidação na decisão"
BENCHMARK = "CDI"
INICIO, CORTE = "2020-01-01", "2023-01-01"
REGIME, CUSTO_TROCA = "nenhum", 0.0
CLASSE_IR = "futuros_b3"
PARAMS = {"regra": "vende_cauda", "risco": .25, "pmin": 5.0, "pmax": 25.0}
GRADE = {"regra": ["compra_favorito", "vende_favorito", "vende_cauda"], "pmax": [15.0, 25.0]}
VIZINHANCA = {"risco": (.15, .35), "pmin": (3.0, 8.0), "pmax": (20.0, 35.0)}
MEIO = 1.5
INSTRUMENTOS = [{"onde": "B3", "ticker": "CPM<mês><ano>C<strike> (opção digital de Copom)", "lote": "1 contrato (R$ 100/ponto até jun/2025; R$ 1/ponto depois)",
                 "custo": "meio spread ~1,5 ponto + tarifa"},
                {"onde": "B3", "ticker": "IDI (opção sobre índice DI)", "lote": "-", "custo": "sem oferta no fechamento: inacessível para PF"}]
APLICAVEL = "parcial: CPM só cabe em R$ 20–50 mil desde jul/2025 (lote 100x menor); IDI não"
MOTIVO = ("Até jun/2025 1 contrato de CPM = R$ 100 por ponto: comprar o favorito a 60 = R$ 6 mil; vender uma cauda a 15 arrisca R$ 8,5 mil. "
          "Com R$ 20 mil e 25% de risco por reunião não cabe; com R$ 50 mil cabe 1. Depois de jul/2025 cabe qualquer tamanho.")
ALAVANCAGENS = [1]
MOTIVO_ALAV = "25% do capital em risco por reunião já é muito para um evento binário."
LETRA = "FGHJKMNQUVXZ"


def carrega():
    t = pd.read_parquet(O.DADOS / "pr_opcoes.parquet")
    c = t[t.ticker.str.startswith("CPM") & (t.ticker.str.len() == 13) & (t.RglrTraddCtrcts.fillna(0) > 0)].copy()
    c["mes"] = c.ticker.str[3:6]
    c["bp"] = (c.ticker.str[7:].astype(int) - 100000) / 10
    c["mult"] = (c.NtlFinVol / (c.RglrTraddCtrcts * c.TradAvrgPric)).round()
    c = c[["data", "ticker", "mes", "bp", "TradAvrgPric", "RglrTraddCtrcts", "mult"]].rename(columns={"TradAvrgPric": "preco"})
    cp = pd.read_csv(O.DADOS / "copom.csv", parse_dates=["data"]).sort_values("data")
    cp["delta"] = (cp.meta.diff() * 100).round()
    cp = cp[~cp.extra.astype(bool)]
    return {"cpm": c.reset_index(drop=True), "copom": cp[["data", "reuniao", "meta", "delta"]].reset_index(drop=True)}


def _livro(d, capital, p, lag, custo_mult):
    c, cp = d["cpm"], d["copom"]
    cp = cp.assign(mes=[f"{LETRA[x.month - 1]}{x.year % 100:02d}" for x in cp.data]).drop_duplicates("mes")
    reun = cp.set_index("mes")
    dias = sorted(c.data.unique())
    pnl = pd.Series(0.0, index=O.DIAS)
    neg = []
    por_mes = pd.Series(dias).groupby(pd.Series(dias).dt.to_period("M")).apply(list)
    for per, ds in por_mes.items():
        if len(ds) < 2 + lag:
            continue
        sinal, ex = ds[0], ds[1 + lag]
        x = c[c.data == sinal]
        prox = [m for m in x.mes.unique() if m in reun.index and reun.at[m, "data"] > ex]
        if not prox:
            continue
        m = min(prox, key=lambda k: reun.at[k, "data"])
        dt, delta = reun.at[m, "data"], reun.at[m, "delta"]
        x = x[x.mes == m].sort_values("preco", ascending=False)
        if p["regra"] == "compra_favorito":
            alvo = [(x.iloc[0].ticker, 1)] if x.iloc[0].preco < 95 else []
        elif p["regra"] == "vende_favorito":
            alvo = [(x.iloc[0].ticker, -1)] if x.iloc[0].preco < 95 else []
        else:
            alvo = [(t, -1) for t, pr in zip(x.ticker, x.preco) if p["pmin"] <= pr <= p["pmax"]]
        if not alvo:
            continue
        y = c[c.data == ex].set_index("ticker")
        liq = O.DIAS[O.DIAS > dt]
        if not len(liq):
            continue
        liq = liq[0]
        orc = capital * p["risco"] / len(alvo)
        for t, lado in alvo:
            if t not in y.index:
                continue
            z = y.loc[t]
            preco = float(np.clip(z.preco + lado * MEIO * custo_mult, .5, 99.5))
            risco_1 = (preco if lado > 0 else 100 - preco) * z.mult
            n = int(np.floor(orc / risco_1))
            if n < 1:
                continue
            ganhou = float(c.loc[c.ticker == t, "bp"].iloc[0]) == delta
            res = lado * n * z.mult * ((100.0 if ganhou else 0.0) - preco)
            pnl.loc[liq] += res
            neg.append(dict(ativo="CPM", lado=lado, entrada=ex, saida=liq, serie=t, contratos=n, preco=preco, mult=z.mult, ganhou=ganhou,
                            decisao_bp=delta, pnl_rs=res, **{"retorno_%": res / (n * risco_1) * 100}))
    return pnl, neg


def _p(params):
    return {**PARAMS, **params}


def excesso(d, capital=20000, custo_mult=1, lag=0, regime=REGIME, alavancagem=1, **params):
    pnl, _ = _livro(d, capital * alavancagem, _p(params), lag, custo_mult)
    return O.fecha(pnl / capital, regime, CUSTO_TROCA, custo_mult)


def classes_ir(d, capital=20000, **params):
    pnl, _ = _livro(d, capital, _p(params), 0, 1)
    return {CLASSE_IR: pnl}


def posicoes(d, capital=20000, **params):
    pnl, _ = _livro(d, capital, _p(params), 0, 0)
    return O.wr_de_pnl({"CPM": pnl}, capital)


def negocios(d, capital=20000, **params):
    _, neg = _livro(d, capital, _p(params), 0, 1)
    return O.negocios_df(neg, capital)
