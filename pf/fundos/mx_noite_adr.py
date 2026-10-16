"""
mx_noite_adr — frente pf3_mecanismos. Mecanismo 2 (pânico + ÂNCORA) aplicado ao vencedor b3_leilao_noite_aud (+7,1 antes do IR, mas
"depende de noites de pânico": sem o 1% melhor dos negócios cai de 112 para 35 pp; custo 2x negativo).

Inspiração: mh_petroleo (só compra o pânico quando a âncora — o Brent em reais — não acompanhou a queda).
Hipótese: a noite depois de uma queda forte reverte porque quem vendeu foi forçado (stop, zeragem, resgate), não informado. Uma âncora
separa os dois casos:
  - 'adr': a mesma ação negociada em Nova York (ADR, em reais pelo dólar do dia) caiu MENOS que a ação na B3 no mesmo dia (divergência
    <= −dmin): a venda foi local (fluxo), não notícia global. O ADR fecha às 16h de NY (17h–18h de Brasília), antes da decisão (noite de t);
    a compra é no leilão de fechamento de t+1 — sem look-ahead. Universo: só as ações com ADR líquido (PETR3/4, VALE3, ITUB4, BBDC4,
    ABEV3, GGBR4, SBSP3, CSNA3, CMIG4, SANB11, UGPA3, SUZB3, TIMS3);
  - 'adr0': o mesmo universo de ADR, SEM o filtro de divergência (controle: separa o efeito do universo do efeito da âncora);
  - 'sem_fr': âncora de informação — nenhuma entrega de Fato Relevante na CVM da companhia em t−1 ou t (a queda não tem notícia formal);
    universo líquido completo do original.
Execução/custos/IR iguais ao auditado (leilão de fechamento de t+1 -> leilão de abertura de t+2, 8 bps ida e volta, 15%).
Âncora e dmin escolhidos só no IS (2014-06 a 2020) pelo maior IR.
"""
import numpy as np
import pandas as pd

import _mx_comum as X
import b3_leilao_noite_aud as O

BB, B, C, pf, DIAS = X.BB, X.B, X.C, X.pf, X.DIAS

NOME = "Noite nos leilões após queda — só com âncora (ADR que não caiu / sem fato relevante)"
TESE = ("Compro no leilão de fechamento a ação que caiu forte só quando a âncora diverge — o ADR em NY caiu menos (venda local forçada) ou "
        "não houve fato relevante — e vendo no leilão de abertura")
BENCHMARK = "CDI"
INICIO, CORTE = O.INICIO, O.CORTE
REGIME = "nenhum"
CLASSE_IR = "acoes"
CUSTO_TROCA = .001
ADR = {"PBR": "PETR3", "PBR-A": "PETR4", "VALE": "VALE3", "ITUB": "ITUB4", "BBD": "BBDC4", "ABEV": "ABEV3", "GGB": "GGBR4", "SBS": "SBSP3",
       "SID": "CSNA3", "CIG": "CMIG4", "BSBR": "SANB11", "UGP": "UGPA3", "SUZ": "SUZB3", "TIMB": "TIMS3"}
PARAMS = {"ancora": "sem_fr", "dmin": .005, "limiar": .03, "n": 4, "adv_min": 5e7}
GRADE = {"ancora": ["adr0", "adr", "sem_fr"], "dmin": [.005, .015]}
VIZINHANCA = {"dmin": (.003, .02), "limiar": (.02, .04)}
INSTRUMENTOS = O.INSTRUMENTOS
APLICAVEL = True
MOTIVO = O.MOTIVO
ALAVANCAGENS = [1]
MOTIVO_ALAV = "mesmo do original; testado só 1x"
_RES = {}


def carrega():
    d = O.carrega()
    QUANT = B.RAIZ.parent
    ya = pd.read_parquet(QUANT / "fundos" / "dados" / "y_adr.parquet")[list(ADR)]
    fx = pd.read_parquet(QUANT / "fundos" / "dados" / "y_fx.parquet")["BRL=X"]
    us = ya.join(fx.rename("BRL"), how="outer").sort_index()
    us.index = pd.DatetimeIndex(us.index).normalize()
    d["adr"] = us[~us.index.duplicated(keep="last")]
    ev = pd.read_parquet(B.PF / "dados" / "macro_hedge" / "eventos.parquet")
    d["fr"] = ev[ev.tipo == "FR"][["data", "ticker"]].copy()
    return d


def _adr_brl(d):
    us = d["adr"]
    s = us.reindex(DIAS.union(us.index)).ffill(limit=5)
    r = s.reindex(DIAS).pct_change(fill_method=None)
    out = pd.DataFrame({ADR[a]: (1 + r[a]) * (1 + r["BRL"]) - 1 for a in ADR})
    return out.where(s.reindex(DIAS)[list(ADR)].notna().values)


def roda(d, capital=20000, custo_mult=1, lag=0, alavancagem=1, ancora="adr", dmin=.01, limiar=.03, n=4, adv_min=5e7):
    key = (id(d), capital, custo_mult, lag, alavancagem, ancora, dmin, limiar, n, adv_min)
    if key in _RES:
        return _RES[key]
    P, R, Oo, V = d["P"].reindex(DIAS), d["R"].reindex(DIAS), d["O"].reindex(DIAS), d["V"].reindex(DIAS)
    cols = [c for c in P.columns if c[-1] in "345678" or c.endswith("11")]
    P, R, Oo, V = P[cols], R[cols], Oo[cols], V[cols]
    n = int(n)
    adv = V.fillna(0).rolling(60, min_periods=40).mean()
    liq = (adv >= adv_min) & P.notna()
    dia = (P / Oo - 1).where(Oo > 0)
    noite = ((1 + R) / (1 + dia) - 1).where(Oo > 0)
    rel = R.sub(R.where(liq).mean(axis=1), axis=0)
    filt = liq & (rel <= -limiar)
    if ancora in ("adr", "adr0"):
        A = _adr_brl(d).reindex(columns=cols)
        filt = filt & A.notna()
        if ancora == "adr":
            filt = filt & ((R - A) <= -dmin)
    elif ancora == "sem_fr":
        fr = d["fr"]
        fr = fr[fr.ticker.isin(cols)]
        i = DIAS.searchsorted(pd.DatetimeIndex(fr.data))
        ok = i < len(DIAS)
        M = pd.DataFrame(False, index=DIAS, columns=cols)
        for ii, t in zip(i[ok], fr.ticker.values[ok]):
            M.iat[ii, cols.index(t)] = True
        tem = M | M.shift(1, fill_value=False)
        filt = filt & ~tem
    s = (-rel).where(filt)
    rk = s.rank(axis=1, ascending=False, method="first")
    sel = rk <= n
    sh = 1 + lag
    compra = sel.shift(sh).fillna(False).astype(bool) & P.notna()
    tam = capital * alavancagem / n
    qtd = np.floor(tam / P).where(compra, 0).fillna(0)
    val = qtd * P
    no = noite.shift(-1)
    val = val.where(no.notna(), 0)
    g = (val * no).fillna(0)
    custo = val * 2 * (B.EMOL + O.SLIP) * custo_mult
    pnl = (g - custo).sum(axis=1).shift(1).fillna(0)
    usado = val.sum(axis=1).shift(1).fillna(0)
    cdi_p = usado * C.CDI.reindex(DIAS).fillna(0)
    e = (pnl - cdi_p) / capital
    W = (val / capital).shift(-sh).fillna(0)
    ii, jj = np.nonzero((val > 0).values)
    ng = pd.DataFrame({"ativo": np.array(cols)[jj], "lado": 1, "entrada": DIAS[ii], "saida": DIAS[np.minimum(ii + 1, len(DIAS) - 1)], "dias": 1,
                       "retorno_%": (no.values[ii, jj] - 2 * (B.EMOL + O.SLIP) * custo_mult) * 100,
                       "contrib_pp": (g.values[ii, jj] - custo.values[ii, jj]) / capital * 100, "valor": val.values[ii, jj]})
    res = {"e": e.fillna(0), "pnl": pnl, "custo": pd.Series(0.0, index=DIAS), "cdi_perdido": cdi_p, "W": W.loc[:, (W != 0).any()],
           "R": noite, "negocios": ng, "vendas": usado, "classes": {"acoes": pnl, "_cdi_perdido": cdi_p}}
    if len(_RES) > 32:
        _RES.clear()
    _RES[key] = res
    return res


X.contrato(globals(), roda)

if __name__ == "__main__":
    import sys
    X.escolhe_is(sys.modules[__name__], carrega())
