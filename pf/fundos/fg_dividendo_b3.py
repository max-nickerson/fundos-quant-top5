"""
Dividendo isento na data-com (B3): ações com DIVIDENDO (não JCP) e, como variante, FIIs — o lado "B3 vs EUA" da ideia de dividendos.

Por que só B3: o PF brasileiro paga 30% de imposto retido na fonte nos EUA sobre dividendo (sem tratado; Lei 14.754 só deixa compensar
até 15%) — comprar ação americana antes da data-ex é perder 15–30% do dividendo; na B3, DIVIDENDO é isento para o PF (e também para o
estrangeiro), JCP paga 15% na fonte (a pesquisa A8 mediu queda de 92% do JCP bruto -> PF perde). Rendimento de FII é isento para PF.
Tese de mesa: na data-ex o preço cai MENOS que o dividendo quando o comprador marginal é tributado ou não pode carregar o papel
(fundos que pagam come-cotas, tesourarias, estrangeiro com custo de câmbio) — o PF isento, com lote pequeno, coleta a diferença.
A pesquisa institucional (A8) mediu queda média de 100% do dividendo bruto (mediana 97%) para yield > 1%: a margem é estreita.

Negócio: decisão no fechamento do dia da APROVAÇÃO (data pública, B3 listedCompaniesProxy), compra no fechamento da data-com (se a
aprovação veio ao menos 1 pregão antes) e vende na abertura (ou no fechamento) da data-ex; recebe o dividendo (pago semanas depois — o
atraso de caixa entra como CDI perdido de 30 dias sobre o dividendo). Só yield >= `y_min`, giro >= R$ 5 mi/dia, 25% do capital por evento.
Eventos com variação noturna > 25% (desdobramento ou redução de capital em espécie no mesmo dia: CSAN3 mai/2021 1:4, BRAP3/4
dez/2021) ficam de fora — são anunciados antes e o PF não compraria; o filtro é simétrico (tira altas e quedas). Custos: meio spread real do fechamento (melhor oferta de compra/venda do COTAHIST) + 0,03% de emolumentos por lado + 0,05% extra
quando vende no leilão de abertura. O dinheiro fica 1 noite fora do CDI.
FIIs (variante "fii"): proventos do Yahoo só existem de 2022 em diante (antes, quase vazio) — não há IS; a data-com do FII é anunciada
no próprio dia, então a regra prevê a data-ex pelo MESMO dia útil do mês do provento anterior (sem olhar o futuro); se o FII mudar a
data, o negócio é feito sem dividendo (só custo).
IR: dividendo e rendimento de FII isentos; a queda de preço é prejuízo de ações (compensável). CLASSE_IR "acoes" (com a isenção de
vendas <= R$ 20 mil/mês pelo motor) é CONSERVADOR: o runner tributa o excesso inteiro (inclui o dividendo isento) nos meses com
vendas acima de R$ 20 mil.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

import fg_comum as G  # noqa: E402

C, pf = G.C, G.pf

NOME = "Dividendo isento na data-com (ações B3 com dividendo; FIIs como variante)"
TESE = ("Compro na data-com ações com dividendo (isento para PF) já aprovado, yield >= 1%, e vendo na abertura da data-ex; ganho = "
        "dividendo − queda do preço − custos.")
BENCHMARK = "CDI"
INICIO, CORTE = "2014-03-01", "2021-01-01"
REGIME = "nenhum"
CUSTO_TROCA = .001
CLASSE_IR = "acoes"
PARAMS = {"universo": "acoes", "y_min": .02, "saida": "abertura", "peso": .25}
GRADE = {"y_min": [.01, .02], "saida": ["abertura", "fechamento"]}
VIZINHANCA = {"y_min": (.008, .03), "peso": (.15, .35)}
EMOL, EXTRA_ABERTURA, GIRO_MIN = .0003, .0005, 5e6
TIPO = {"ON": "3", "PN": "4", "PNA": "5", "PNB": "6", "UNT": "11"}
INSTRUMENTOS = {"ações com dividendo": {"onde": "B3", "ticker": "~100 eventos/ano com yield >= 1%", "lote": "fracionário (1 ação)",
                                        "custo": "meio spread real + 0,03%"},
                "FIIs (variante)": {"onde": "B3", "ticker": "~100 FIIs líquidos", "lote": "1 cota", "custo": "meio spread real + 0,03%"}}
APLICAVEL = True
MOTIVO = "Operável em qualquer corretora; dividendo de ação e rendimento de FII são isentos para PF; ordem no fechamento e na abertura."
ALAVANCAGENS = [1, 1.5, 2]
MOTIVO_ALAV = "peso por evento x L (até 50% do capital num evento); acima disso, risco de um único papel de 1 noite."
VARIANTES = {"FIIs (2022+)": {"universo": "fii"}, "sai no fechamento": {"saida": "fechamento"}, "yield >= 1%": {"y_min": .01}}


def carrega():
    f = G.CACHE / "dividendo_b3"
    if not (f / "eventos.parquet").exists():
        a = G.ler_fd("arb_proventos.parquet")
        a = a[a.corporateAction == "DIVIDENDO"].copy()
        a["com"] = pd.to_datetime(a.lastDatePriorEx, dayfirst=True, errors="coerce")
        a["data"] = pd.to_datetime(a.dateApproval, dayfirst=True, errors="coerce")
        a["div"] = pd.to_numeric(a.valueCash.astype(str).str.replace(",", "."), errors="coerce") / pd.to_numeric(
            a.quotedPerShares.astype(str).str.replace(",", "."), errors="coerce").replace(0, 1).fillna(1)
        a["ticker"] = a.code4 + a.typeStock.str.strip().map(TIPO).fillna("")
        a = a.dropna(subset=["com", "data", "div"])
        a = a[(a.com >= "2014-01-01") & a.ticker.str.len().ge(5)]
        ev = a.groupby(["ticker", "com"]).agg(data=("data", "max"), div=("div", "sum")).reset_index()
        tk = sorted(set(ev.ticker))
        pn = {}
        for c in ("P", "O", "BID", "ASK", "V"):
            x = pd.read_parquet(G.U.CACHE / "b3_acoes" / f"painel_{c}.parquet")
            pn[c] = x[[t for t in tk if t in x.columns]]
        # FIIs: proventos do Yahoo (ex-data) + preços do COTAHIST
        X = pd.read_parquet(G.CACHE / "fii_div.parquet")
        D = X[[c for c in X if c.endswith("|Dividends")]]
        D.columns = [c.split(".SA")[0] for c in D]
        fe = D.stack()
        fe = fe[fe > 0].reset_index()
        fe.columns = ["ex", "ticker", "div"]
        fe["data"] = fe.ex
        q = G.cotahist_fundos(sorted(set(fe.ticker)))
        f.mkdir(parents=True, exist_ok=True)
        ev.to_parquet(f / "eventos.parquet")
        fe.to_parquet(f / "fii_eventos.parquet")
        for c in pn:
            pn[c].to_parquet(f / f"acoes_{c}.parquet", compression="zstd")
        for c, col in (("P", "fech"), ("O", "abertura"), ("BID", "oferta_compra"), ("ASK", "oferta_venda"), ("V", "volume")):
            G.pivo(q, col).to_parquet(f / f"fii_{c}.parquet", compression="zstd")
    out = {"eventos": pd.read_parquet(f / "eventos.parquet"), "fii_eventos": pd.read_parquet(f / "fii_eventos.parquet")}
    for u in ("acoes", "fii"):
        for c in ("P", "O", "BID", "ASK", "V"):
            out[f"{u}_{c}"] = pd.read_parquet(f / f"{u}_{c}.parquet").reindex(C.DIAS)
    return out


def _eventos_fii(d):
    """Data-com prevista pelo dia útil do mês do provento ANTERIOR do mesmo FII (só passado). Devolve ticker, decisão, com, ex, div."""
    fe = d["fii_eventos"].sort_values(["ticker", "ex"])
    idx = C.DIAS
    mes = pd.Series(idx.to_period("M"), index=idx)
    ordinal = mes.groupby(mes).cumcount().values                      # 0 = 1º dia útil do mês
    out = []
    for t, g in fe.groupby("ticker"):
        ex = list(pd.to_datetime(g.ex))
        dv = list(g["div"])
        reais = {idx.searchsorted(x): v for x, v in zip(ex, dv)}
        for k in range(len(ex)):                                        # do provento k (passado) prevê o próximo
            i_prev = idx.searchsorted(ex[k])
            if i_prev >= len(idx):
                continue
            o = ordinal[i_prev]
            alvo = (ex[k] + pd.offsets.MonthBegin(1)).to_period("M")
            dias_mes = np.where(mes.values == alvo)[0]
            if len(dias_mes) == 0:
                continue
            i_ex = dias_mes[min(o, len(dias_mes) - 1)]                   # data-ex prevista
            out.append({"ticker": t, "i_com": i_ex - 1, "i_ex": i_ex, "div": reais.get(i_ex, 0.0), "div_esp": dv[k],
                        "decisao": idx[i_ex - 2], "real": i_ex in reais})
    return pd.DataFrame(out)


def _eventos_acoes(d):
    ev = d["eventos"]
    idx = C.DIAS
    out = []
    for t, com, ap, dv in zip(ev.ticker, ev.com, ev.data, ev["div"]):
        i_com = idx.searchsorted(com)
        j = idx.searchsorted(ap)                                        # decisão no fechamento do dia da aprovação
        if i_com >= len(idx) - 1 or idx[i_com] != com or j > i_com - 1:
            continue
        out.append({"ticker": t, "i_com": i_com, "i_ex": i_com + 1, "div": dv, "div_esp": dv, "decisao": idx[j], "real": True})
    return pd.DataFrame(out)


def _roda(d, capital, custo_mult, lag, alavancagem, universo, y_min, saida, peso):
    u = universo
    P, O, B, A, V = (d[f"{u}_{c}"].reindex(C.DIAS) for c in ("P", "O", "BID", "ASK", "V"))   # truncado: NaN depois de T
    ev = _eventos_fii(d) if u == "fii" else _eventos_acoes(d)
    idx = C.DIAS
    T = len(idx)
    cdi = C.CDI.reindex(idx).fillna(0).values
    giro = V.rolling(20, min_periods=10).median().shift(1)
    ms = ((A - B) / P / 2).clip(0, .03)
    ms = ms.where(ms > 0).rolling(20, min_periods=1).median().shift(1)
    pnl = np.zeros(T)
    W = pd.DataFrame(0.0, index=idx, columns=sorted(set(ev.ticker) & set(P.columns)) if len(ev) else [])
    usado = np.zeros(T)
    trades = []
    for r in ev.itertuples():
        t = r.ticker
        if t not in P.columns:
            continue
        i0 = r.i_com + lag                                              # compra no fechamento da data-com (lag: atrasa e perde o direito)
        i1 = r.i_ex + lag
        jd = idx.searchsorted(r.decisao)
        if i1 >= T or jd >= i0:
            continue
        p0 = P[t].values[i0]
        if not (np.isfinite(p0) and p0 > 0):
            continue
        g = giro[t].values[i0 - 1] if i0 >= 1 else np.nan
        dv = r.div if lag == 0 else 0.0                                 # atrasou: comprou já sem o direito
        y_esp = (r.div_esp / P[t].values[jd]) if np.isfinite(P[t].values[jd]) and P[t].values[jd] > 0 else 0   # FII: provento anterior
        if not (np.isfinite(g) and g >= GIRO_MIN and y_esp >= y_min):
            continue
        alvo = peso * alavancagem * capital
        if usado[i0] + alvo > alavancagem * capital * 1.0001:
            continue
        q = np.floor(alvo / p0)
        if q < 1:
            continue
        px1 = O[t].values[i1] if saida == "abertura" else P[t].values[i1]
        if not (np.isfinite(px1) and px1 > 0):
            px1 = P[t].values[i1]
        if not (np.isfinite(px1) and px1 > 0):
            continue
        if abs(px1 / p0 - 1) > .25:                                     # desdobramento/redução de capital em espécie no mesmo dia (CSAN3
            continue                                                    # 2021 1:4, BRAP 2021 Vale em espécie): evento anunciado, o PF evita
        m0 = ms[t].values[i0] if np.isfinite(ms[t].values[i0]) else .003
        c = q * p0 * (m0 + EMOL) + q * px1 * (m0 + EMOL + (EXTRA_ABERTURA if saida == "abertura" else 0))
        ganho = q * (px1 - p0) + q * dv - q * dv * cdi[i1] * 21 - q * p0 * cdi[i1]   # dividendo pago ~1 mês depois; 1 noite sem CDI
        res = ganho - c * custo_mult
        pnl[i1] += res
        usado[i0] += alvo
        W.loc[idx[i0 - 1], t] += q * p0 / capital
        trades.append({"ativo": t, "lado": 1, "entrada": idx[i0], "saida": idx[i1], "dias": 1, "retorno_%": (px1 / p0 - 1) * 100,
                       "dividendo_%": dv / p0 * 100, "queda/dividendo": (p0 - px1) / dv if dv > 0 else np.nan,
                       "contrib_pp": res / capital * 100, "vendas_brl": q * px1})
    return pd.Series(pnl / capital, index=idx), pd.DataFrame(trades), W, P


def excesso(d, capital=20000, custo_mult=1, lag=0, regime=REGIME, alavancagem=1, universo=PARAMS["universo"], y_min=PARAMS["y_min"],
            saida=PARAMS["saida"], peso=PARAMS["peso"]):
    e = _roda(d, capital, custo_mult, lag, alavancagem, universo, y_min, saida, peso)[0]
    return C.aplica_regime(e, regime, CUSTO_TROCA * custo_mult)


def posicoes(d, capital=20000, universo=PARAMS["universo"], y_min=PARAMS["y_min"], saida=PARAMS["saida"], peso=PARAMS["peso"]):
    """W: peso decidido na véspera da compra (carregado 1 noite); R: retorno do papel − CDI (sem o dividendo: só para placebo/vendas)."""
    _, _, W, P = _roda(d, capital, 1, 0, 1, universo, y_min, saida, peso)
    R = P[W.columns].pct_change(fill_method=None).sub(C.CDI.reindex(C.DIAS).fillna(0), axis=0).fillna(0)
    return W, R


def negocios(d, capital=20000, universo=PARAMS["universo"], y_min=PARAMS["y_min"], saida=PARAMS["saida"], peso=PARAMS["peso"]):
    return _roda(d, capital, 1, 0, 1, universo, y_min, saida, peso)[1]
