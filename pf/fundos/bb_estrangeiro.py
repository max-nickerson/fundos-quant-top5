"""
Saída de estrangeiro (EWZ como proxy do fluxo): comprar BOVA11 depois do resgate em pânico — frente "pf2_b3".

Mesa: o estrangeiro é ~50% do volume da B3 e entra/sai por ETFs (EWZ, US$ 4–8 bi). Num resgate forte de EWZ o participante autorizado
vende a cesta na B3 para entregar o resgate — vendedor forçado que não olha preço. A tese contrária (comprar o Brasil depois da saída
forçada) é o que o dono pediu testar. Não há histórico diário gratuito de fluxo por investidor da B3 baixado; proxy: EWZ (Yahoo, OHLCV
desde 2005) — queda de 5 pregões em dólar < `queda` E volume financeiro de 5 dias > `vol_mult` x a média de 120 dias (resgate/
capitulação, não só queda).
Execução: o fechamento do EWZ (16h NY) é conhecido perto do fechamento da B3; por segurança a decisão é no 1º pregão da B3 DEPOIS da data
do EWZ e a compra no fechamento seguinte (t+1). BOVA11 (cotas de ~R$ 100–150, inteiras; meio spread 0,02% + emolumentos 0,03%), R$ `frac`
x capital, segura `hold` pregões; um sinal novo durante a janela estende a posição.
Estudo de evento (BOVA11 menos CDI): 2008–2020, queda < −8% e volume > 1,5x: −1,7% em 5 pregões, −3,3% em 10 (18 sinais); 2021–26 −1,0%
(4). O estrangeiro sai em ONDAS (semanas), não num dia: o vendedor forçado continua do outro lado depois do sinal.
IR: ETF de ações na B3 (15%, sem isenção de R$ 20 mil).
"""
import numpy as np
import pandas as pd

import bb_base as BB

B, C, pf = BB.B, BB.C, BB.pf
DIAS = BB.DIAS

NOME = "Saída de estrangeiro (EWZ) -> BOVA11 comprado"
TESE = ("Compro BOVA11 depois de queda forte do EWZ com volume de resgate (o AP vende a cesta na B3 para entregar o resgate do estrangeiro) "
        "e seguro hold pregões")
BENCHMARK = "CDI"
INICIO, CORTE = "2008-06-01", "2021-01-01"
REGIME = "nenhum"
CLASSE_IR = "etf_b3"
CUSTO_TROCA = .001
CUSTO = .0003 + .0002                      # emolumentos + meio spread BOVA11
PARAMS = {"queda": -.08, "vol_mult": 1.0, "hold": 21, "frac": .9}
GRADE = {"queda": [-.08, -.12], "vol_mult": [1.0, 1.5], "hold": [10, 21]}
VIZINHANCA = {"queda": (-.11, -.06), "vol_mult": (.8, 1.3), "hold": (15, 30)}
INSTRUMENTOS = [{"onde": "Clear/Rico/XP", "ticker": "BOVA11", "lote": "1 cota", "custo": "emolumentos 0,03% + meio spread 0,02%"}]
APLICAVEL = True
MOTIVO = "BOVA11 em cotas inteiras; sinais raros (2–4 por ano)"
ALAVANCAGENS = [1, 1.5, 2]
MOTIVO_ALAV = "BOVA11 com garantia em Tesouro Selic (termo/ WIN não cabe com R$ 20 mil); o excedente paga CDI (premissa)"
_CACHE = BB.Cache()


def carrega():
    x = pd.read_parquet(BB.DADOS / "ewz_yahoo.parquet")[["Close_EWZ", "Volume_EWZ"]]
    return {"ewz": x[x.index <= DIAS[-1]], "bova": C.BOVA.reindex(DIAS)}


def pesos(d, queda, vol_mult, hold, frac):
    x = d["ewz"]
    p, v = x.Close_EWZ, x.Volume_EWZ * x.Close_EWZ
    r5, vz = p.pct_change(5), v.rolling(5).mean() / v.rolling(120).mean()
    s = x.index[(r5 < queda) & (vz > vol_mult)]
    i = DIAS.searchsorted(s, side="right")                 # 1º pregão da B3 depois da data do EWZ
    W = np.zeros(len(DIAS))
    for k in i[i < len(DIAS)]:
        W[k:k + int(hold)] = frac
    return pd.DataFrame({"BOVA11": W}, index=DIAS), [DIAS[k] for k in i[i < len(DIAS)]]


def roda(d, capital=20000, custo_mult=1, lag=0, alavancagem=1, queda=-.08, vol_mult=1.0, hold=21, frac=.9):
    key = (id(d), capital, custo_mult, lag, alavancagem, round(queda, 4), round(vol_mult, 3), int(round(hold)), round(frac, 3))

    def f():
        W, sinais = pesos(d, queda, vol_mult, int(round(hold)), frac * alavancagem)
        rb = d["bova"].pct_change(fill_method=None).reindex(DIAS).fillna(0)
        R = pd.DataFrame({"BOVA11": rb - BB.CDI.reindex(DIAS).fillna(0)})
        e = C.carteira(W, R, CUSTO * custo_mult, lag)
        # excedente acima do capital (alavancagem > 1) já paga CDI em R (excesso), sem spread
        Wx = W.shift(1 + lag).fillna(0)["BOVA11"]
        ent = Wx.index[(Wx > 0) & (Wx.shift(1).fillna(0) == 0)]
        sai = Wx.index[(Wx == 0) & (Wx.shift(1).fillna(0) > 0)]
        ng = []
        for a in ent:
            b = sai[sai > a]
            b = b[0] if len(b) else DIAS[-1]
            g = e[(e.index > a) & (e.index <= b)].sum()
            ng.append({"ativo": "BOVA11", "lado": 1, "entrada": a, "saida": b, "dias": int(DIAS.get_loc(b) - DIAS.get_loc(a)),
                       "retorno_%": ((1 + rb[(rb.index > a) & (rb.index <= b)]).prod() - 1) * 100, "contrib_pp": g * 100,
                       "rotulo": "sinal EWZ"})
        return {"e": e, "W": W, "R": R, "negocios": pd.DataFrame(ng)}
    return _CACHE.get(key, f)


def excesso(d, capital=20000, custo_mult=1, lag=0, regime=REGIME, alavancagem=1, **params):
    e = roda(d, capital, custo_mult, lag, alavancagem, **{**PARAMS, **params})["e"]
    return C.aplica_regime(e, regime, CUSTO_TROCA * custo_mult)


def posicoes(d, capital=20000, **params):
    r = roda(d, capital, **{**PARAMS, **params})
    return r["W"], r["R"]


def negocios(d, capital=20000, **params):
    return roda(d, capital, **{**PARAMS, **params})["negocios"]


if __name__ == "__main__":
    d = carrega()
    import itertools
    for q, v, h in itertools.product(*GRADE.values()):
        e = excesso(d, queda=q, vol_mult=v, hold=h)
        print(q, v, h, "IS %.2f OOS %.2f" % (C.anual(e[INICIO:CORTE]), C.anual(e[CORTE:])), len(negocios(d, queda=q, vol_mult=v, hold=h)))
