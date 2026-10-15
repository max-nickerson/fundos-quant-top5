"""
Eleições em emergentes: compro o ETF do país depois do pânico eleitoral — regra fixada ANTES de olhar o resultado PF.

Tese de mesa: o estrangeiro vende primeiro e pergunta depois; o eleito costuma moderar (Chile dez/2021 +30%, Argentina set/2025 +27%,
Índia jun/2024). Mas quando a eleição muda de fato a política econômica (Argentina PASO 2019, México jun/2024, Peru jun/2021) o pânico
é informação e continua. A pesquisa institucional (IM9) tinha 20 negócios e PBO 82%: não dá para separar os dois casos olhando os
negócios. Regra honesta (definida antes, do "próximo passo" do IM9, e escolhida pelo IS, não pelo OOS):
  - lista FECHADA de todas as eleições nacionais/referendos de 16 emergentes 2008–2026 (copiada do IM9 + as de 2025–26 que já
    aconteceram: Polônia mai–jun/2025, Chile nov/2025, Peru abr–jun/2026, Brasil 04/10/2026) — a regra decide, não a escolha das datas;
  - pânico = ETF em US$ cai mais que `queda` do fechamento da véspera da eleição ao 1º pregão depois;
  - filtro "moeda" (opção da grade): NÃO compro se a moeda caiu mais que metade da queda do ETF no mesmo intervalo (saída de capital =
    o mercado está precificando mudança de política, não ruído);
  - compro no fechamento seguinte, seguro `dias` pregões, tamanho 10% de vol (vol de 126d), teto 50% do capital por eleição.
Sobrevivência: Rússia/Egito/Nigéria/Colômbia ficam fora (sem ETF vivo no Yahoo) — eleições lá não entram nem a favor nem contra.

PF: ETF na IBKR (fração). Brasil poderia ser BOVA11 (sem remessa); usamos EWZ para manter tudo na mesma conta.
"""
import numpy as np
import pandas as pd

import em_comum as E

NOME = "Eleições EM: ETF do país depois do pânico eleitoral (regra fechada)"
TESE = ("Lista fechada de eleições de 16 emergentes; se o ETF cai > 3–6% da véspera ao 1º pregão pós-eleição, compro (sem comprar quando a "
        "moeda cai junto — fuga de capital), seguro 1–3 meses")
BENCHMARK = "CDI"
INICIO, CORTE = "2009-01-01", "2021-01-01"
REGIME = "nenhum"
CUSTO_TROCA = .001
CLASSE_IR = "exterior"
ELEICOES = {
    "BR": ["2010-10-03", "2010-10-31", "2014-10-05", "2014-10-26", "2018-10-07", "2018-10-28", "2022-10-02", "2022-10-30", "2026-10-04"],
    "MX": ["2012-07-01", "2018-07-01", "2021-06-06", "2024-06-02"],
    "AR": ["2011-08-14", "2011-10-23", "2013-08-11", "2013-10-27", "2015-08-09", "2015-10-25", "2015-11-22", "2017-08-13", "2017-10-22",
           "2019-08-11", "2019-10-27", "2021-09-12", "2021-11-14", "2023-08-13", "2023-10-22", "2023-11-19", "2025-09-07", "2025-10-26"],
    "TR": ["2011-06-12", "2014-08-10", "2015-06-07", "2015-11-01", "2017-04-16", "2018-06-24", "2019-03-31", "2019-06-23",
           "2023-05-14", "2023-05-28", "2024-03-31"],
    "IN": ["2009-05-16", "2014-05-16", "2019-05-23", "2024-06-04"],
    "ZA": ["2009-04-22", "2014-05-07", "2019-05-08", "2024-05-29"],
    "ID": ["2014-07-09", "2019-04-17", "2024-02-14"],
    "KR": ["2012-12-19", "2017-05-09", "2022-03-09", "2024-12-03", "2025-06-03"],
    "TW": ["2012-01-14", "2016-01-16", "2020-01-11", "2024-01-13"],
    "MY": ["2013-05-05", "2018-05-09", "2022-11-19"],
    "TH": ["2011-07-03", "2014-05-22", "2019-03-24", "2023-05-14"],
    "PH": ["2016-05-09", "2022-05-09"],
    "CL": ["2009-12-13", "2010-01-17", "2013-12-15", "2017-12-17", "2019-10-18", "2021-11-21", "2021-12-19", "2022-09-04", "2025-11-16",
           "2025-12-14"],
    "PE": ["2011-06-05", "2016-06-05", "2021-06-06", "2026-04-12", "2026-06-07"],
    "PL": ["2015-10-25", "2019-10-13", "2023-10-15", "2025-05-18", "2025-06-01"],
    "GR": ["2012-05-06", "2012-06-17", "2015-01-25", "2015-07-05", "2015-09-20", "2019-07-07", "2023-06-25"],
}
VEIC = {"BR": ("EWZ", "BRL=X"), "MX": ("EWW", "MXN=X"), "AR": ("ARGT", "ARS=X"), "TR": ("TUR", "TRY=X"), "IN": ("INDA", "INR=X"),
        "ZA": ("EZA", "ZAR=X"), "ID": ("EIDO", "IDR=X"), "KR": ("EWY", "KRW=X"), "TW": ("EWT", "TWD=X"), "MY": ("EWM", "MYR=X"),
        "TH": ("THD", "THB=X"), "PH": ("EPHE", "PHP=X"), "CL": ("ECH", "CLP=X"), "PE": ("EPU", "PEN=X"), "PL": ("EPOL", "PLN=X"),
        "GR": ("GREK", None)}
PARAMS = {"queda": .03, "dias": 21, "filtro": "moeda", "alvo_vol": .10}   # escolhido no IS (maior IR IS)
GRADE = {"queda": [.03, .06], "dias": [21, 63], "filtro": ["nenhum", "moeda"]}
VIZINHANCA = {"queda": (.025, .05), "dias": (15, 35), "alvo_vol": (.07, .14)}
INSTRUMENTOS = ("IBKR: EWZ, EWW, ARGT, TUR, INDA, EZA, EIDO, EWY, EWT, EWM, THD, EPHE, ECH, EPU, EPOL, GREK (fração). Caixa em Tesouro Selic; "
                "dinheiro na IBKR só durante o negócio.")
APLICAVEL = True
MOTIVO = "Operável (R$ 5–10 mil por evento, ETFs líquidos), mas são ~1–3 negócios por ano: o resultado é uma loteria de poucos eventos."
ALAVANCAGENS = [1, 1.5, 2]
MOTIVO_ALAV = "L multiplica o tamanho por evento (vol-alvo 10% -> 15%/20%); eventos raramente se sobrepõem."
ROTULO = None


def carrega():
    tk = [v[0] for v in VEIC.values()] + [v[1] for v in VEIC.values() if v[1]]
    ev = pd.DataFrame([{"pais": p, "data": pd.Timestamp(x)} for p, xs in ELEICOES.items() for x in xs])
    return E.seleciona(tk, {"eventos": ev})


def _pesos(d, queda, dias, filtro, alvo_vol):
    P = E.preco_usd(d)
    neg = E.negociou(d)
    idx = P.index
    W = pd.DataFrame(0.0, index=idx, columns=sorted({v[0] for v in VEIC.values()}))
    fim = idx[-1]
    sinais = []
    for _, ev in d["eventos"].iterrows():
        etf, fx = VEIC[ev.pais]
        p = P[etf].where(neg[etf]).dropna()
        p = p[p.index <= fim]
        k1 = p.index.searchsorted(ev.data)                        # 1º pregão do ETF no dia da eleição ou depois
        if k1 == 0 or k1 >= len(p):
            continue
        t0, t1 = p.index[k1 - 1], p.index[k1]
        mov = p.iloc[k1] / p.iloc[k1 - 1] - 1
        if mov > -queda:
            continue
        if filtro == "moeda" and fx is not None:
            f = d["raw"][fx].dropna()
            f = f.shift(-1)                                       # Yahoo: o "Close" do dia t é a cotação do INÍCIO de t (~ fech. de t-1);
            mfx = f.asof(t0) / f.asof(t1) - 1                     # o fim de t é o da linha seguinte (sai ~20h ET de t, antes da execução)
            if not np.isfinite(mfx):
                mfx = 0.0
            if mfx < .5 * mov:
                sinais.append((ev.pais, t1, mov, mfx, "filtrado"))
                continue
        r = p.pct_change()
        vol = r.iloc[max(0, k1 - 126):k1 + 1].std() * np.sqrt(252)
        w = min(alvo_vol / vol, .5) if np.isfinite(vol) and vol > 0 else .25
        i = idx.get_loc(t1)
        W.iloc[i:i + dias, W.columns.get_loc(etf)] = np.maximum(W.iloc[i:i + dias, W.columns.get_loc(etf)], w)
        sinais.append((ev.pais, t1, mov, None, "comprado"))
    W = E.limita(W, 1.0)
    return W, {}


excesso, classes_ir, posicoes, negocios = E.contrato(__import__(__name__))
