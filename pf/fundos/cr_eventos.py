"""
(7) Eventos: listagens na Binance (o "efeito listagem") e halving do bitcoin.

Medição (caderno): das 452 moedas listadas em US$ na Binance desde 2019 com volume real (> US$ 5 mi no 1º dia, INCLUSIVE as que foram
deslistadas depois), a mediana do retorno do fechamento do 1º dia ao 30º é −13% a −33% em TODOS os anos e −19% a −50% até o 60º.
Negócio: a listagem é o EVENTO DE LIQUIDEZ de quem tem a moeda barata (fundos de venture, equipe, airdrop, launchpool) — o vendedor
forçado/desejoso é o insider destravando; o comprador é o varejo que vê "listou na Binance". O pico é o anúncio (antes da listagem),
que não temos com hora — o que sobra depois é deriva para baixo.
Rotas:
  modo="venda_offshore": vendo o perpétuo da moeda recém-listada (a Binance lista perpétuos junto) numa conta OFFSHORE (a única rota para
      PF; ver cr_comum), `peso` do capital por moeda, a partir do fechamento seguinte ao 1º dia, por `h` dias, SÓ se o perpétuo USDT-M
      já negociava (até 3 dias depois do à vista; 415 das moedas têm perpétuo no arquivo da Binance). Preço e FINANCIAMENTO REAIS do
      perpétuo (arquivo data.binance.vision; moeda nova costuma ter financiamento negativo = o vendido paga); `fin` = custo extra a.a.
      (sensibilidade). Liquidação com margem 1x (+85% = perde 85% do nocional). Saldo na corretora = nocional (pf.custo_conta_exterior)
      + contraparte 2,5% a.a.
  modo="compra": o que o PF consegue em corretora brasileira (comprar a novidade) — para medir o custo do "efeito listagem" ao contrário.
  modo="halving": BTC comprado de `h` dias antes a `h` dias depois do halving (2020-05-11, 2024-04-20; datas conhecidas com meses de
      antecedência pela altura do bloco). Só 2 eventos no período de dados: anedota, não estatística.
Execução t+1 (fechamento diário 00h UTC seguinte). Custos: 0,35%/lado (moeda nova, spread largo) e 0,15% no BTC.
"""
import numpy as np
import pandas as pd

import cr_comum as K

NOME = "Eventos cripto: listagens na Binance (venda offshore / compra) e halving"
TESE = "vendo (offshore) o perpétuo da moeda recém-listada: o insider destrava e o varejo da listagem paga a conta; halving como controle"
BENCHMARK = "CDI"
INICIO, CORTE = "2019-01-01", "2023-01-01"
REGIME = "nenhum"
CUSTO_TROCA = .0
CLASSE_IR = "exterior"
PARAMS = {"modo": "venda_offshore", "h": 30, "peso": .05, "fin": .0, "vol_min": 5e6}
GRADE = {"modo": ["venda_offshore", "compra", "halving"], "h": [10, 30, 60]}
VIZINHANCA = {"h": (20, 45), "peso": (.03, .08), "fin": (.0, .30)}
LIQ = .60
HALVINGS = [pd.Timestamp("2020-05-11"), pd.Timestamp("2024-04-20")]
INSTRUMENTOS = [{"onde": "Binance internacional / OKX (offshore)", "ticker": "<nova>USDT perpétuo", "lote": "fração", "custo": "0,35%/lado + financiamento"},
                {"onde": "Binance BR", "ticker": "<nova>USDT / BTCBRL", "lote": "fração", "custo": "0,35% / 0,15% por lado"}]
APLICAVEL = "parcial"
MOTIVO = ("a venda só existe offshore (perpétuo fora da CVM, contraparte e regulatório; Bybit/Binance BR cortaram derivativos a brasileiros "
          "em 2026); a compra e o halving cabem em corretora brasileira")
ALAVANCAGENS = [1]
MOTIVO_ALAV = "vendido em moeda nova com margem 1x já perde até 85% do nocional num squeeze; alavancar é pedir liquidação"


def carrega():
    x = K.ler("listagens.parquet").set_index("t")
    h = K.ler("binance_1h.parquet")
    h = h[h.sym == "BTCUSDT"].set_index("t")
    pp = K.ler("perps_listagens.parquet")
    perp = pp[pp.tipo == "perp"][["t", "sym", "fech"]].set_index("t")
    fu = pp[pp.tipo == "funding"][["t", "sym", "fund"]].copy()
    fu["t"] = fu.t.dt.round("h").dt.ceil("D")                      # liquidações em (00h, 00h seguinte]
    return {"lst": x, "btc": h, "perp": perp, "fund": fu.set_index("t")}


def _simula(d, capital, custo_mult, lag, modo, h, peso, fin, vol_min, alavancagem=1):
    h = int(h)
    if modo == "halving":
        b = d["btc"].fech
        b = b[b.index.hour == 0]
        P = b.to_frame("BTC")
        R = P / P.shift(1) - 1
        W = pd.DataFrame(0.0, index=P.index, columns=["BTC"])
        for t in HALVINGS:
            W.loc[(W.index >= t - pd.Timedelta(days=h + 1)) & (W.index < t + pd.Timedelta(days=h - 1)), "BTC"] = alavancagem * 1.0
        custo = .0015
    else:
        x = d["lst"].reset_index()
        P = x.pivot_table(index="t", columns="sym", values="fech", aggfunc="last").sort_index()
        Vv = x.pivot_table(index="t", columns="sym", values="vol_usd", aggfunc="last").reindex(P.index)
        P = P.reindex(pd.date_range(P.index[0], P.index[-1], freq="D"))
        Vv = Vv.reindex(P.index)
        R = P / P.shift(1) - 1
        prim = P.notna().idxmax()                                         # 1º fechamento de cada moeda
        lado = -1.0 if modo == "venda_offshore" else 1.0
        W = pd.DataFrame(0.0, index=P.index, columns=P.columns)
        for s, t0 in prim.items():
            if not (Vv.at[t0, s] > vol_min):                              # volume do 1º dia (conhecido no 1º fechamento)
                continue
            W.loc[(W.index >= t0) & (W.index < t0 + pd.Timedelta(days=h)), s] = lado * peso * alavancagem
        W = W.loc[:, (W != 0).any()]
        P, R = P[W.columns], R[W.columns]
        custo = .0035
        if modo == "venda_offshore":
            # perpétuo REAL: só vende se o perpétuo já negociava até 3 dias depois da listagem do à vista; preço e financiamento do perpétuo
            pe = d["perp"].reset_index().pivot_table(index="t", columns="sym", values="fech", aggfunc="last").reindex(P.index)
            fu = d["fund"].reset_index().pivot_table(index="t", columns="sym", values="fund", aggfunc="sum").reindex(P.index).fillna(0)
            Wn = pd.DataFrame(0.0, index=P.index, columns=W.columns)
            for s_ in W.columns:
                if s_ not in pe or not pe[s_].notna().any():
                    continue
                t0, tp = prim[s_], pe[s_].first_valid_index()
                if tp > t0 + pd.Timedelta(days=3):
                    continue
                Wn.loc[(Wn.index >= max(t0, tp)) & (Wn.index < t0 + pd.Timedelta(days=h)), s_] = -peso * alavancagem
            W = Wn.loc[:, (Wn != 0).any()]
            P = pe[W.columns]
            R = (P / P.shift(1) - 1) - fu.reindex(columns=W.columns).fillna(0)     # o comprado paga o financiamento -> o vendido recebe
            # liquidação (margem isolada 1x): a perda de um vendido nunca passa da margem. Só há fechamento diário do perpétuo -> uso o
            # FECHAMENTO +60% acima da entrada como sinal de que a máxima do dia passou de +85% (conservador) e cobro 85% + 1% de taxa.
            E = W.shift(1 + lag).fillna(0)                                 # posição executada (igual à do motor)
            ini = E.ne(E.shift(1).fillna(0)) & E.ne(0)
            Rv, Ev, Iv = R.values.copy(), E.values, ini.values
            for j in range(Rv.shape[1]):
                acc, morto = 1.0, False
                for i in range(Rv.shape[0]):
                    if Iv[i, j]:
                        acc, morto = 1.0, False
                        continue
                    if i == 0 or Ev[i - 1, j] == 0:
                        continue
                    if morto:
                        Rv[i, j] = np.nan                                  # sem posição depois da liquidação
                        continue
                    r = Rv[i, j] if np.isfinite(Rv[i, j]) else 0.0
                    if acc * (1 + r) > 1 + LIQ:
                        Rv[i, j] = (1 + .86) / acc - 1                     # perde 85% do nocional + 1%
                        morto = True
                    else:
                        acc *= 1 + r
            R = pd.DataFrame(Rv, index=R.index, columns=R.columns)
            M = K.motor(W, R, capital, custo, lag_passos=1 + lag, custo_mult=custo_mult)   # P&L em US$ ~ R$ (o câmbio do saldo vai na conta exterior)
            M["R"] = R
            return M
    fxr = K.fx_horario(P.index)
    fxr = fxr / fxr.shift(1) - 1
    M = K.motor(W, R, capital, custo, lag_passos=1 + lag, custo_mult=custo_mult, fx_r=fxr)
    M["R"] = R
    return M


def excesso(d, capital=20000, custo_mult=1, lag=0, regime=REGIME, alavancagem=1, **params):
    p = {**PARAMS, **params}
    M = _simula(d, capital, custo_mult, lag, p["modo"], p["h"], p["peso"], p["fin"], p["vol_min"], alavancagem)
    if p["modo"] == "venda_offshore":
        pnl = K.para_dias(M["pnl"].sum(axis=1))
        nocional = M["V"].abs().sum(axis=1)
        finc = K.para_dias(nocional * p["fin"] / 365)                     # custo EXTRA de aluguel/financiamento além do real (sensibilidade)
        saldo = K.para_dias(nocional, "last").fillna(0)
        conta, saldo_ef = K.pf.custo_conta_exterior(saldo, folga=1.0)
        e = (pnl - finc * custo_mult - conta * custo_mult - saldo_ef * .025 / 252) / capital
    else:
        e, _ = K.excesso_spot(M, capital)
    e = e.where(e.index >= pd.Timestamp(INICIO), 0).fillna(0)
    return K.C.aplica_regime(e, regime, CUSTO_TROCA * custo_mult)


def posicoes(d, capital=20000, **params):
    p = {**PARAMS, **params}
    M = _simula(d, capital, 1, 0, p["modo"], p["h"], p["peso"], p["fin"], p["vol_min"])
    return K.W_diario(M["E"], M["R"])


def negocios(d, capital=20000, **params):
    p = {**PARAMS, **params}
    M = _simula(d, capital, 1, 0, p["modo"], p["h"], p["peso"], p["fin"], p["vol_min"])
    return K.negocios_blocos(M["E"], M["pnl"], capital, M["R"])


if __name__ == "__main__":
    d = carrega()
    for m in ["venda_offshore", "compra", "halving"]:
        e = excesso(d, modo=m)
        print(m, (e.groupby(e.index.year).sum() * 100).loc[2019:].round(1).to_dict())
