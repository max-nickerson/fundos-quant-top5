"""
bb_dividendo_extra — AUDITADA (pf/pesquisa/auditoria_pf2.md). Mesmo motor e mesmas regras do original; muda só o UNIVERSO de proventos:

  - original: arb_proventos.parquet = 103 companhias (membros do Ibovespa, atuais e alguns antigos) -> viés de seleção/sobrevivência;
  - auditada: + proventos B3 de TODAS as raízes do painel COTAHIST (pf/dados/auditoria/proventos_b3_extra.parquet, mesma API da B3
    `GetListedCashDividends`, que devolve também companhias deslistadas: SULA, ENBR, BRML, ...). 302 companhias a mais; 123 raízes sem
    resposta da API (a maioria trocou de código: ESTC->YDUQ, TIMP->TIMS, DTEX->DXCO, ALSO->ALOS — tratadas abaixo; CESP/LIGT etc. ficam fora);
  - troca de código: o provento da raiz nova (YDUQ) com data-com antes da estreia do ticker novo vai para o ticker antigo do MESMO CNPJ
    (mapa_cnpj) que tinha preço na data-com; a entrega IPE/CVM é casada pelo CNPJ (qualquer raiz da companhia).
Filtro de liquidez `adv_min` (R$ milhões/dia, mediana de 60 pregões ANTES da aprovação): no universo completo o resultado sem
filtro (+31,6 pp) vem de micro caps com fechamento de 1–30 negócios (MERC4, BMIN3, CEEB3), que não aguenta custo 2x (+1,7) nem t+2 (+9,0).
Sinal, execução (fechamento de t+1 após a ENTREGA na CVM), saída no fechamento da data-com, custos e IR: iguais ao original.
"""
import numpy as np
import pandas as pd
from pathlib import Path

import bb_dividendo_extra as O
from bb_dividendo_extra import B, BB, C, CLS, DIAS, pf  # noqa: F401

NOME = "Dividendo/JCP extraordinário (até a data-com) — AUDITADA (universo completo de proventos B3)"
TESE = O.TESE
BENCHMARK = O.BENCHMARK
INICIO, CORTE = O.INICIO, O.CORTE
REGIME = O.REGIME
CLASSE_IR = O.CLASSE_IR
CUSTO_TROCA = O.CUSTO_TROCA
PARAMS = {**O.PARAMS, "adv_min": 5.0}     # R$ mi/dia (mediana de 60 pregões até a véspera da aprovação), fixado a priori
GRADE = dict(O.GRADE)
VIZINHANCA = dict(O.VIZINHANCA)
INSTRUMENTOS = O.INSTRUMENTOS
APLICAVEL = True
MOTIVO = "universo completo (todas as pagadoras do COTAHIST, inclusive deslistadas)"
ALAVANCAGENS = [1]
MOTIVO_ALAV = O.MOTIVO_ALAV
EXTRA = BB.B.PF / "dados" / "auditoria" / "proventos_b3_extra.parquet"


def carrega():
    d = O.carrega()
    P = d["P"]
    a = pd.concat([pd.read_parquet(Path(__file__).resolve().parent.parent / "dados" / "auditoria" / "arb_proventos.parquet"), pd.read_parquet(EXTRA)], ignore_index=True)
    a = a.drop_duplicates(["code4", "typeStock", "dateApproval", "lastDatePriorEx", "valueCash", "corporateAction"])
    num = lambda s: pd.to_numeric(s.astype(str).str.replace(".", "", regex=False).str.replace(",", ".", regex=False), errors="coerce")
    x = pd.DataFrame({"data": pd.to_datetime(a.dateApproval, dayfirst=True, errors="coerce"),
                      "com": pd.to_datetime(a.lastDatePriorEx, dayfirst=True, errors="coerce"),
                      "raiz": a.code4.values, "suf": a.typeStock.map(CLS).fillna("?").values,
                      "valor": num(a.valueCash) / num(a.quotedPerShares).replace(0, np.nan).fillna(1),
                      "tipo": a.corporateAction})
    x = x.dropna(subset=["data", "com", "valor"])
    x = x[x.data >= "2013-06-01"]
    # troca de código: escolhe a raiz do mesmo CNPJ que tinha preço na data-com
    m = B.ler("mapa_cnpj")
    cn = dict(zip(m.raiz, m.cnpj))
    grupo = m.groupby("cnpj").raiz.apply(list).to_dict()
    Pf = P.ffill(limit=5)
    tick = []
    for r, s, c in zip(x.raiz, x.suf, x.com):
        cand = [r] + [q for q in grupo.get(cn.get(r), []) if q != r]
        k = DIAS.searchsorted(c)
        esc = r + s
        for q in cand:
            t = q + s
            if t in Pf and k < len(DIAS) and pd.notna(Pf[t].iat[k]):
                esc = t
                break
        tick.append(esc)
    x["ticker"] = tick
    x = x[x.ticker.isin(P.columns)].rename(columns={"data": "aprov"})
    x["data"] = x.aprov
    x = x[["aprov", "com", "ticker", "valor", "tipo", "data"]]
    d["prov"] = x
    dv = x.copy()
    dv["data"] = dv.com
    d["divs"] = dv
    # entregas IPE casadas pelo CNPJ: replica a entrega para todas as raízes da companhia
    ip = d["ipe"]
    ip = ip.assign(raiz=ip.raiz.map(lambda r: grupo.get(cn.get(r), [r]) if r in cn else [r])).explode("raiz")
    d["ipe"] = ip.drop_duplicates()
    return d


_FILT = {}


def _filtra(d, adv_min):
    k = (id(d), adv_min)
    if k not in _FILT:
        if len(_FILT) > 16:
            _FILT.clear()
        dd = dict(d)
        if adv_min and adv_min > 0:
            adv = d["V"].reindex(DIAS).rolling(60, min_periods=20).median().shift(1)
            pv = d["prov"]
            a = np.array([adv[t].asof(x) if t in adv else np.nan for t, x in zip(pv.ticker, pv.aprov)])
            dd["prov"] = pv[a >= adv_min * 1e6]
        _FILT[k] = (d, dd)                      # guarda d para o id não ser reaproveitado
    return _FILT[k][1]


def _sep(params):
    p = {**PARAMS, **params}
    return p.pop("adv_min"), p


def excesso(d, capital=20000, custo_mult=1, lag=0, regime=REGIME, alavancagem=1, **params):
    a, p = _sep(params)
    return O.excesso(_filtra(d, a), capital, custo_mult, lag, regime, alavancagem, **p)


def classes_ir(d, capital=20000, **params):
    a, p = _sep(params)
    return O.classes_ir(_filtra(d, a), capital, **p)


def posicoes(d, capital=20000, **params):
    a, p = _sep(params)
    return O.posicoes(_filtra(d, a), capital, **p)


def negocios(d, capital=20000, **params):
    a, p = _sep(params)
    return O.negocios(_filtra(d, a), capital, **p)


if __name__ == "__main__":
    d = carrega()
    print(len(d["prov"]), d["prov"].ticker.str[:4].nunique())
    for kw in [{"limiar": l, "saida": s} for l in GRADE["limiar"] for s in GRADE["saida"]]:
        e = excesso(d, **kw)
        print(kw, "IS %.2f OOS %.2f n=%d" % (C.anual(e[INICIO:CORTE]), C.anual(e[CORTE:]), len(negocios(d, **kw))), flush=True)
