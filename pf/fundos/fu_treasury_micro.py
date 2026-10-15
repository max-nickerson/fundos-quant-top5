"""
Micro Treasury Yield (CME, IBKR): concessão de LEILÃO do Tesouro americano no micro de 30 anos (e 10 anos) e "curve" 2s10s com micros.

Tese de mesa ("leilao30"/"leilao10"): o Tesouro anuncia cada leilão ~6 dias antes e o mercado tem que ABSORVER a oferta nova. Os primary
dealers são obrigados a dar lance em todo leilão e não querem carregar o estoque: eles vendem (ou vendem futuro) nos dias antes do
leilão para abrir espaço no balanço, e o yield sobe até o leilão — a "concessão" (Lou, Yan & Zhang 2013, "Anticipated and Repeated
Shocks in Liquid Markets", RFS). Depois do leilão a pressão some e o preço volta. Fico COMPRADO EM YIELD (vendido no título) do dia
seguinte ao anúncio até o fechamento do dia do leilão (o resultado sai às 13h de NY; o yield de fechamento já é pós-leilão) e,
opcionalmente, VENDIDO em yield `pos` dias depois (devolução da concessão). Quem paga: o dealer que precisa de espaço no balanço.
"curva": 2s10s com 1 micro 10Y comprado em yield e 1 micro 2YY vendido em yield (ambos US$ 10/bp: DV01 neutro) = inclinação, quando o Fed
CORTOU > 25 bp nos últimos 6 meses (bull steepener: o curto cai com o Fed); o contrário (flattener) quando SUBIU > 25 bp. cme_juros_fed
já testou o ciclo do Fed em yield OUTRIGHT; aqui é só a curva.

Contratos (CME Group "Micro Treasury Yield futures", lançados em 16/ago/2021; IBKR out/2026): 2YY, 5YY, 10Y, 30Y = US$ 10 por bp, tick
0,1 bp = US$ 1, liquidação financeira pelo índice BrokerTec; margem inicial ~US$ 290 (30Y) a 400 por contrato. Custo por lado: IBKR
US$ 0,62 (comissão + taxas) + meio spread de 1 tick (pouco líquido) = US$ 1,62. O "Micro Ultra Bond" (preço, US$ 10 mil de nocional,
mar/2024) tem DV01 ≈ US$ 20-25 e dados só desde 2024: fica de fora (o micro de yield de 30 anos dá a mesma exposição desde 2021).
Retorno de 1 contrato COMPRADO em yield = US$ 10 x Δyield (bp) − carregamento ((yield − Fed funds)/duração por dia, como em cme_comum).
Yields: ^TYX (30 anos, Cboe, fechamento ~15h NY), DGS10/DGS2 (FRED). Leilões: TreasuryDirect (data de ANÚNCIO = data do evento; o
leilão só entra no dado depois de anunciado). Antes de ago/2021 o micro é hipotético (mesmo yield).
"""
import numpy as np
import pandas as pd

import fu_comum as F

NOME = "Micro Treasury Yield: concessão de leilão (30Y/10Y) e curva 2s10s"
TESE = "Comprado em yield do micro de 30 anos do anúncio até o leilão (dealers abrindo balanço para a oferta nova), vendido depois"
BENCHMARK = "CDI"
INICIO, CORTE = "2008-01-01", "2021-01-01"
REGIME = "nenhum"
CUSTO_TROCA = 0.0
CLASSE_IR = "exterior"
PARAMS = {"modo": "leilao10", "pos": 3}          # maior excesso IS (2008-2020) da grade
GRADE = {"modo": ["leilao30", "leilao10", "curva"], "pos": [0, 3]}
VIZINHANCA = {"pos": (0, 5)}
LANCAMENTO = {"30Y": "2021-08-16", "10Y": "2021-08-16", "2YY": "2021-08-16"}
ESPEC = {"30Y": dict(y="^TYX", dur=17.0), "10Y": dict(y="DGS10", dur=8.0), "2YY": dict(y="DGS2", dur=1.9)}
CUSTO_USD, MARGEM_USD = 1.62, 400.0
INSTRUMENTOS = [("IBKR/CBOT", "30Y", "US$ 10/bp", "US$ 1,62/lado"), ("IBKR/CBOT", "10Y", "US$ 10/bp", "US$ 1,62/lado"),
                ("IBKR/CBOT", "2YY", "US$ 10/bp", "US$ 1,62/lado"), ("Tesouro Direto", "Tesouro Selic", "caixa", "0")]
APLICAVEL = True
MOTIVO = "1 micro de yield tem vol ≈ US$ 600-1.000/ano (≈ 15-25% de R$ 20 mil) e margem ≈ R$ 2 mil: cabe. Antes de ago/2021 é hipotético."
ALAVANCAGENS = [1, 2, 5]
MOTIVO_ALAV = "nº de contratos = alavancagem (1, 2 ou 5 micros por perna); 5 micros de 30Y ≈ vol de 100% de R$ 20 mil."
TERMOS = {"leilao30": ("30-Year", "29-Year"), "leilao10": ("10-Year", "9-Year")}


def carrega():
    a = pd.read_csv(F.DADOS / "leiloes_tesouro_bruto.csv", parse_dates=["announcementDate", "auctionDate"])
    a = a.rename(columns={"announcementDate": "data"})[["data", "auctionDate", "securityTerm", "reopening"]]
    return {"y": F.ler("juros_eua.parquet"), "leiloes": a.sort_values("data").reset_index(drop=True)}


def _contrato(d, inst):
    def f():
        e = ESPEC[inst]
        y = d["y"][e["y"]].dropna()
        idx = pd.bdate_range(d["y"]["DGS10"].first_valid_index(), d["y"].index.max())
        yy = F.nivel(y, idx)
        ff = F.nivel(d["y"]["DFF"], idx)
        carry_bp = ((yy - ff) / e["dur"] * 100 / 252).shift(1)
        pc_usd = (10.0 * (yy.diff() * 100 - carry_bp)).fillna(0)
        noc_usd = 10.0 / (e["dur"] * 1e-4)                       # título equivalente em DV01
        r = pc_usd / noc_usd
        return F.contrato(r, pd.Series(1.0, index=idx), noc_usd, "USD", idx, None, CUSTO_USD, MARGEM_USD, rol=12, margem_fixa=True)
    return F.memo(("tsy", inst), (d["y"],), f)


def gera(d, capital=20000, regime=REGIME, alavancagem=1, modo="leilao30", pos=0):
    K = {a: _contrato(d, a) for a in ESPEC}
    idx = K["10Y"].index
    N = pd.DataFrame(0.0, index=idx, columns=list(ESPEC))
    n = float(round(alavancagem))
    if modo == "curva":
        ff = F.nivel(d["y"]["DFF"], idx)
        mud = ff - ff.shift(126)
        lado = pd.Series(np.where(mud < -.25, 1.0, np.where(mud > .25, -1.0, 0.0)), index=idx)   # +1 = steepener
        N["10Y"], N["2YY"] = lado * n, -lado * n
        return N, K
    inst = "30Y" if modo == "leilao30" else "10Y"
    lv = d["leiloes"]
    lv = lv[lv.securityTerm.str.startswith(TERMOS[modo])]
    s = pd.Series(0.0, index=idx)
    for a, u in zip(lv["data"], lv["auctionDate"]):
        ia, iu = idx.searchsorted(a), idx.searchsorted(u)
        if (iu < len(idx) and idx[iu] != u) or iu - ia < 2:       # leilão fora do calendário (feriado) ou anúncio em cima da hora
            continue                                              # (leilão depois do fim dos dados: posição até o fim, sem olhar o futuro)
        s.iloc[ia:iu - 1] = 1.0                                   # rende de a+2 até o fechamento do leilão (execução t+1)
        if pos > 0:
            s.iloc[iu - 1:min(iu - 1 + pos, len(idx))] = -1.0     # rende de u+1 a u+pos
    N[inst] = s * n
    return N, K


F.montar(globals(), gera, carrega)
