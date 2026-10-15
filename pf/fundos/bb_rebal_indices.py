"""
Rebalanceamento dos OUTROS índices da B3 (SMLL e IBrX-100) — PF com R$ 20–50 mil, frente "pf2_b3".

Mesa: o Ibovespa (rev_rebal_ibovespa, +1,0 pp) não é o único índice com dinheiro passivo. A cada quadrimestre (carteiras de jan/mai/set)
o SMLL (SMAL11 + fundos de small caps com benchmark SMLL) e o IBrX-100 (BRAX11 + fundos indexados) trocam papéis no fechamento do último
pregão da carteira velha. Os entrantes do SMLL são papéis ilíquidos — se há comprador forçado, o impacto deveria ser maior que no
Ibovespa e o lote de R$ 1–2 mil da PF entra sem mover o preço.
Regra reconstruída só com dados até a data (prévias públicas saem no mês anterior; aqui usamos só preços/volumes até a decisão):
  - índice de negociabilidade 12m IN = (n/N)^(1/3) (v/V)^(2/3), presença >= 95%, preço >= R$ 1;
  - IBrX-100 = 100 maiores IN; IBrA = IN acumulado até 99%;
  - SMLL = IBrA sem as companhias que somam 85% do valor de mercado (valor de mercado = nº de ações do último ITR/FRE ENTREGUE até a
    data x último preço; um ticker por companhia);
  - entrantes = no proxy agora e não no proxy da revisão anterior, EXCLUINDO os entrantes prováveis do Ibovespa (já testado).
Execução: decide `antes` pregões antes do último pregão da carteira velha, compra no fechamento seguinte, vende no fechamento do último
pregão da carteira velha (quando o passivo compra). R$ `frac` x capital por papel. Sem hedge (WIN não cabe no capital; ver
rev_rebal_ibovespa). IR: ações, vendas do mês < R$ 20 mil na maior parte das revisões -> isento.
Estudo de evento (IS 2015–2020, excesso sobre o Ibovespa da decisão 10 pregões antes até a troca): entrantes SMLL −0,45% (192),
entrantes IBrX −0,16% (115); saintes −1,2% a −1,5% (pressão de venda existe, mas a PF não vende a descoberto small cap barato).
"""
import numpy as np
import pandas as pd

import bb_base as BB

B, C, pf = BB.B, BB.C, BB.pf
DIAS = BB.DIAS

NOME = "Rebalanceamento SMLL/IBrX-100 (entrantes, PF)"
TESE = ("Compro os prováveis entrantes do SMLL e do IBrX-100 (regra da B3 reconstruída com dados até a data, sem os do Ibovespa) antes da "
        "troca e vendo no fechamento do último pregão da carteira velha para o ETF/fundos passivos; lote pequeno em papel ilíquido")
BENCHMARK = "CDI"
INICIO, CORTE = "2015-01-01", "2021-01-01"
REGIME = "nenhum"          # evento de calendário com fluxo mecânico: regime de mercado não tem razão econômica aqui
CLASSE_IR = "acoes"
CUSTO_TROCA = .001
PARAMS = {"indice": "ibrx", "antes": 42, "frac": .08, "adv_min": 2e5}
GRADE = {"indice": ["smll", "ibrx", "ambos"], "antes": [10, 21, 42]}
VIZINHANCA = {"antes": (30, 55), "frac": (.05, .12)}
INSTRUMENTOS = [{"onde": "Clear/Rico/XP (corretagem zero)", "ticker": "entrantes prováveis do SMLL/IBrX-100 (lote + fracionário XXXX3F)",
                 "lote": "1 ação", "custo": "emolumentos 0,03% + meio spread real do fechamento + 0,2% no fracionário"}]
APLICAVEL = True
MOTIVO = "ações à vista no fracionário, 8% do capital por papel; 5–12 entrantes por revisão; vendas do mês quase sempre < R$ 20 mil"
ALAVANCAGENS = [1]
MOTIVO_ALAV = "exposição média baixa (3 janelas de 2–8 semanas por ano); alavancar só aumenta o lote em papel ilíquido"
_CACHE = BB.Cache()


def carrega():
    d = BB.acoes()
    d = {k: d[k] for k in ("P", "R", "V", "NEG", "BID", "ASK", "HS")}
    d["emit"] = B.ler("acoes_emitidas")[["data", "cnpj", "acoes"]].copy()
    return d


def _proxies(d, dec):
    P, V, NEG = d["P"], d["V"], d["NEG"]
    i = DIAS.searchsorted(dec)
    sl = slice(DIAS[max(i - 252, 0)], dec)
    n, v = NEG.loc[sl].fillna(0).sum(), V.loc[sl].fillna(0).sum()
    pres, ult = P.loc[sl].notna().mean(), P.loc[sl].ffill().iloc[-1]
    x = ((n / n.sum()) ** (1 / 3) * (v / v.sum()) ** (2 / 3))[(pres >= .95) & (ult >= 1)].sort_values(ascending=False)
    ac = x.cumsum() / x.sum()
    ibov = set(ac[ac.shift(1, fill_value=0) < .85].index)
    ibrx = set(x.index[:100])
    ibra = list(ac[ac.shift(1, fill_value=0) < .99].index)
    em = d["emit"]
    em = em[pd.to_datetime(em.data) <= dec].sort_values("data").drop_duplicates("cnpj", keep="last").set_index("cnpj").acoes
    r2c = dict(zip(B.ler("mapa_cnpj").raiz, B.ler("mapa_cnpj").cnpj))
    rz = pd.Series(ibra, index=ibra).groupby(lambda t: t[:4]).first()           # ticker de maior IN por companhia
    mc = pd.Series({t: em[r2c[t[:4]]] * ult[t] for t in rz.values if r2c.get(t[:4]) in em.index}).sort_values(ascending=False)
    cum = mc.cumsum() / mc.sum()
    grandes = {t[:4] for t in cum[cum.shift(1, fill_value=0) < .85].index}
    com_mc = {t[:4] for t in mc.index}
    smll = {t for t in ibra if t[:4] not in grandes and t[:4] in com_mc}
    return {"ibov": ibov, "ibrx": ibrx, "smll": smll}


def eventos(d, antes):
    def f():
        fim_dados = d["P"].dropna(how="all").index.max()
        out = []
        for ano in range(2015, DIAS[-1].year + 1):
            for mes in (1, 5, 9):
                vig = pd.Timestamp(ano, mes, 1)
                i_fim = DIAS.searchsorted(vig) - 1
                dec = DIAS[i_fim - antes]
                if i_fim + 1 >= len(DIAS) or dec > fim_dados:
                    continue
                ant = DIAS[DIAS.searchsorted(vig - pd.DateOffset(months=4)) - 1 - antes]
                a, b = _proxies(d, dec), _proxies(d, ant)
                ib = a["ibov"] - b["ibov"]
                for k in ("smll", "ibrx"):
                    out += [(dec, t, k, DIAS[i_fim]) for t in sorted(a[k] - b[k] - ib)]
        ev = pd.DataFrame(out, columns=["data", "ticker", "ind", "fim"])
        # o mesmo papel pode entrar nos dois: um negócio só
        ev = ev.groupby(["data", "ticker", "fim"]).ind.agg(lambda s: "+".join(sorted(s))).reset_index()
        return ev
    return _CACHE.get(("ev", id(d), antes), f)


def roda(d, capital=20000, custo_mult=1, lag=0, alavancagem=1, indice="ambos", antes=10, frac=.08, adv_min=2e5):
    antes = int(round(antes))
    key = (id(d), capital, custo_mult, lag, alavancagem, indice, antes, round(frac, 4), adv_min)

    def f():
        ev = eventos(d, antes).copy()
        if indice != "ambos":
            ev = ev[ev.ind.str.contains(indice)]
        adv = d["V"].fillna(0).rolling(60, min_periods=20).mean()
        i = DIAS.searchsorted(ev.data)
        ev["adv"] = [adv[t].iloc[k] if t in adv else np.nan for t, k in zip(ev.ticker, i)]
        ev = ev[ev.adv >= adv_min]
        ev["rotulo"] = "entrante " + ev.ind + " (troca " + pd.to_datetime(ev.fim).dt.strftime("%Y-%m-%d") + ")"
        # saída: decisão no penúltimo pregão da carteira velha -> executa no fechamento do último (quando o passivo compra)
        ev["fim"] = DIAS[np.maximum(DIAS.searchsorted(ev.fim) - 1, 0)]
        res = BB.episodios(ev, d, capital, None, frac * capital * alavancagem, custo_mult, lag, alavancagem)
        res["negocios"] = BB.rotula(res["negocios"], ev)
        return res
    return _CACHE.get(key, f)


def excesso(d, capital=20000, custo_mult=1, lag=0, regime=REGIME, alavancagem=1, **params):
    e = roda(d, capital, custo_mult, lag, alavancagem, **{**PARAMS, **params})["e"]
    return C.aplica_regime(e, regime, CUSTO_TROCA * custo_mult)


def classes_ir(d, capital=20000, **params):
    return B.classes_acoes(roda(d, capital, **{**PARAMS, **params}))


def posicoes(d, capital=20000, **params):
    W = roda(d, capital, **{**PARAMS, **params})["W"]
    return W, d["R"].reindex(index=DIAS, columns=W.columns).fillna(0).sub(BB.CDI, axis=0)


def negocios(d, capital=20000, **params):
    return roda(d, capital, **{**PARAMS, **params})["negocios"]


if __name__ == "__main__":
    import time
    d = carrega()
    for kw in [{"indice": i, "antes": a} for i in GRADE["indice"] for a in GRADE["antes"]]:
        t = time.time()
        e = excesso(d, **kw)
        print(kw, "IS %.2f OOS %.2f (%.0fs)" % (C.anual(e[INICIO:CORTE]), C.anual(e[CORTE:]), time.time() - t), flush=True)
