"""
Fim do quiet period de IPOs nos EUA (compra) e, como variante, fim do lock-up (venda) — PF na IBKR.

Tese de mesa: até o fim do quiet period os bancos do sindicato não podem publicar research; no dia ~25 (regra NASD 2711 até 2015;
FINRA 2241 encurtou para 10 dias, mas a maioria dos bancos ainda inicia em bloco ~25 dias depois) chegam 3–6 coberturas iniciais,
quase todas "compra" (o banco que colocou a ação quer o papel de pé). É um fluxo previsível, com data conhecida desde o IPO: quem
compra antes é pago pelo fundo que só pode comprar depois da cobertura (Bradley, Jordan & Ritter, 2003: ~+4% anormais na janela).
Compro `antes` pregões antes do dia 25 e vendo `depois` pregões depois; hedge IWM vendido; R$ 1 mil por IPO (5%).
Variante "quiet+lockup": também vende a descoberto o IPO 5 pregões antes do fim do lock-up de 180 dias (venda de PE/VC/fundadores)
e recompra 10 depois, com aluguel de PF caro (10% a.a. — IPO recente e pequeno; a IBKR cobra a taxa do dia, que passa de 20–50% nos
casos de squeeze) — a pesquisa institucional (IE03) achou o lock-up instável (PBO 100%).

Eventos: 1º 424B4/424B1 do CIK na SEC e 1º preço do Yahoo entre −3 e +10 dias (sem preço antes; SPACs fora) — base quant/fundos
(ideias_i_eventos.eventos_ipos), 1.913 IPOs 2006–2026. Data do IPO = 1º pregão (pública). Filtros na decisão: preço DA ÉPOCA (não ajustado: o Yahoo
ajusta o passado pelos grupamentos futuros — um IPO de US$ 4 que fez grupamento 1:20 aparece a US$ 80) >= US$ 10 e giro
médio desde o IPO >= US$ 5 mi/dia — só IPO com sindicato de verdade tem cobertura em bloco no fim do quiet period; os micro IPOs de
US$ 4 (best efforts, Nasdaq Capital Market, muitos asiáticos em 2024–26) não têm research e caíram 80–90% em uma semana (LNKS, PUSA,
TLIH). ATENÇÃO: este filtro foi colocado DEPOIS de ver esses negócios (com o filtro antigo, US$ 3 e US$ 1 mi, o IS também era
negativo); a variante "sem filtro de tamanho" mostra o original.
Sobrevivência: cobertura de IPOs no Yahoo vai de 37% (2007) a 99% (2026). A janela do quiet period começa ~3 semanas depois do IPO e
dura 2 semanas: quase nenhuma empresa some nesse intervalo — o viés é de SELEÇÃO (no IS faltam os IPOs que fracassaram depois), não de
trajetória; o OOS (2021+, cobertura 65–99%) é a medida confiável. Para o lock-up vendido o viés é contra nós (quem sumiu seria ganho).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

import fg_comum as G  # noqa: E402

C, pf = G.C, G.pf

NOME = "Fim do quiet period de IPOs nos EUA (compra antes das coberturas) — PF IBKR"
TESE = ("Compro o IPO alguns pregões antes do dia 25 (fim do quiet period, quando os bancos do sindicato iniciam cobertura em bloco) e "
        "vendo logo depois; hedge IWM; R$ 1 mil por IPO; caixa no CDI.")
BENCHMARK = "CDI"
INICIO, CORTE = "2008-01-01", "2021-01-01"
REGIME = "nenhum"
CUSTO_TROCA = .001
CLASSE_IR = "exterior"
PARAMS = {"antes": 8, "depois": 0, "dia_quiet": 25, "componente": "quiet", "peso": .05, "hedge_fx": "wdo", "preco_min": 10.0, "giro_min": 5e6}
GRADE = {"antes": [3, 8], "depois": [0, 3], "componente": ["quiet", "quiet+lockup"]}
VIZINHANCA = {"antes": (2, 10), "depois": (0, 5), "peso": (.035, .07)}
MEIO_SPREAD = .003                         # IPO de 3 semanas: meio spread ~0,3% (pequeno) — o giro ainda é alto nas 1as semanas
ALUGUEL_LOCKUP = .10
INSTRUMENTOS = {"IPOs": {"onde": "IBKR", "ticker": "~100–200/ano", "lote": "fração", "custo": "US$ 0,0035/ação mín. 0,35 + 0,3%"},
                "IWM": {"onde": "IBKR (vendido)", "ticker": "IWM", "lote": "ações inteiras", "custo": "aluguel 0,3% a.a."},
                "WDO": {"onde": "B3", "ticker": "WDO (vendido)", "lote": "US$ 10 mil", "custo": "R$ 3,70/lado"}}
APLICAVEL = True
MOTIVO = ("Operável: data do fim do quiet period é conhecida desde o IPO; IBKR compra fração (R$ 1 mil por IPO). A perna vendida do "
          "lock-up depende de haver ação para alugar na IBKR, o que em IPO pequeno muitas vezes não há (ou a taxa explode).")
ALAVANCAGENS = [1, 1.5, 2]
MOTIVO_ALAV = "peso por IPO x L; livro médio pequeno (~6 nomes); 5x = R$ 5 mil num IPO de 3 semanas."
VARIANTES = {"sem filtro de tamanho (US$ 3, US$ 1 mi)": {"preco_min": 3.0, "giro_min": 1e6}, "dia 10 (FINRA 2241)": {"dia_quiet": 10, "antes": 2}, "com lock-up vendido": {"componente": "quiet+lockup"}, "sem WDO": {"hedge_fx": "nenhum"},
             "só lock-up vendido": {"componente": "lockup"}}


def carrega():
    f = G.CACHE / "ipo_quiet"
    if not (f / "precos.parquet").exists():
        ev = pd.read_parquet(G.CACHE / "ipos_eventos.parquet")         # ideias_i_eventos.eventos_ipos() (ver docstring)
        ev = ev[~ev.spac].copy()
        P = pd.concat([G.painel_y("sp"), G.painel_y("us")], axis=1)
        V = pd.concat([G.painel_y("sp", "Volume"), G.painel_y("us", "Volume")], axis=1)
        P, V = P.loc[:, ~P.columns.duplicated()], V.loc[:, ~V.columns.duplicated()]
        tk = sorted(set(ev.ticker) & set(P.columns))
        Pq = pd.concat([P[tk], G.etf(["IWM"])], axis=1)
        Pq = Pq[Pq.index >= "2006-01-01"].astype("float64")
        Vq = V[tk].reindex(Pq.index).astype("float64")
        f.mkdir(parents=True, exist_ok=True)
        ev["data"] = ev.ipo
        ev[["ticker", "nome", "ipo", "data"]].to_parquet(f / "eventos.parquet")
        Pq.to_parquet(f / "precos.parquet", compression="zstd")
        Vq.to_parquet(f / "volume.parquet", compression="zstd")
    if not (f / "bruto.parquet").exists():
        G.preco_bruto(pd.read_parquet(f / "precos.parquet")).to_parquet(f / "bruto.parquet", compression="zstd")
    return {"eventos": pd.read_parquet(f / "eventos.parquet"), "precos": pd.read_parquet(f / "precos.parquet"),
            "volume": pd.read_parquet(f / "volume.parquet"), "bruto": pd.read_parquet(f / "bruto.parquet")}


_CACHE = {}


def _trades(d, antes, depois, dia_quiet, componente, preco_min=10.0, giro_min=5e6):
    P, V, ev = d["precos"], d["volume"], d["eventos"]
    idx = P.index
    out = []
    for t, ipo in zip(ev.ticker, pd.to_datetime(ev.ipo)):
        if t not in P:
            continue
        for comp, dia, a, dp, lado in (("quiet", dia_quiet, antes, depois, 1), ("lockup", 180, 5, 10, -1)):
            if comp not in componente:
                continue
            cal = C.DIAS_US                                             # calendário da NYSE (sabido de antemão; não depende dos dados)
            kq = cal.searchsorted(ipo + pd.Timedelta(days=dia))         # 1º pregão >= fim do quiet period / lock-up (data sabida no IPO)
            j = kq - a - 1                                              # decide no fechamento j, compra no fechamento j+1 = kq - a
            if j < 1 or kq + dp >= len(cal) or cal[j] <= ipo or cal[j] > idx[-1]:
                continue
            px = P[t].loc[:cal[j]].dropna()
            if len(px) < 5:
                continue
            giro = (px * V[t].reindex(px.index)).iloc[-20:].mean()          # ajustado x volume ajustado = giro em US$ (sem viés)
            pb = d["bruto"][t].loc[:cal[j]].dropna()                        # preço da época (sem os grupamentos posteriores)
            if not (pb.iloc[-1] >= preco_min and giro >= giro_min):
                continue
            out.append({"ticker": t, "decisao": cal[j], "saida": cal[kq + dp - 1], "lado": lado, "regiao": "US",
                        "custo": MEIO_SPREAD, "aluguel": ALUGUEL_LOCKUP})
    return pd.DataFrame(out)


def _roda(d, capital, custo_mult, lag, alavancagem, antes, depois, dia_quiet, componente, peso, hedge_fx, preco_min, giro_min):
    k = (id(d), len(d["precos"]), d["precos"].index.max(), capital, custo_mult, lag, alavancagem, antes, depois, dia_quiet, componente,
         round(peso, 5), hedge_fx, preco_min, giro_min)
    if k not in _CACHE:
        tr = _trades(d, int(antes), int(depois), dia_quiet, componente, preco_min, giro_min)
        res = G.livro(tr, d["precos"], capital, custo_mult, lag, alavancagem, peso, teto=1.0, hedge={"US": "IWM"}, hedge_fx=hedge_fx)
        if len(_CACHE) > 40:
            _CACHE.clear()
        _CACHE[k] = res
    return _CACHE[k]


def excesso(d, capital=20000, custo_mult=1, lag=0, regime=REGIME, alavancagem=1, antes=PARAMS["antes"], depois=PARAMS["depois"],
            dia_quiet=PARAMS["dia_quiet"], componente=PARAMS["componente"], peso=PARAMS["peso"], hedge_fx=PARAMS["hedge_fx"],
            preco_min=PARAMS["preco_min"], giro_min=PARAMS["giro_min"]):
    res = _roda(d, capital, custo_mult, lag, alavancagem, antes, depois, dia_quiet, componente, peso, hedge_fx, preco_min, giro_min)
    return C.aplica_regime(res["e"], regime, CUSTO_TROCA * custo_mult)


def posicoes(d, capital=20000, antes=PARAMS["antes"], depois=PARAMS["depois"], dia_quiet=PARAMS["dia_quiet"], componente=PARAMS["componente"],
             peso=PARAMS["peso"], hedge_fx=PARAMS["hedge_fx"], preco_min=PARAMS["preco_min"], giro_min=PARAMS["giro_min"]):
    res = _roda(d, capital, 1, 0, 1, antes, depois, dia_quiet, componente, peso, hedge_fx, preco_min, giro_min)
    return G.posicoes_de(res, d["precos"], capital)


def negocios(d, capital=20000, antes=PARAMS["antes"], depois=PARAMS["depois"], dia_quiet=PARAMS["dia_quiet"], componente=PARAMS["componente"],
             peso=PARAMS["peso"], hedge_fx=PARAMS["hedge_fx"], preco_min=PARAMS["preco_min"], giro_min=PARAMS["giro_min"]):
    res = _roda(d, capital, 1, 0, 1, antes, depois, dia_quiet, componente, peso, hedge_fx, preco_min, giro_min)
    return G.negocios_de(res, capital, d["precos"])
