"""
Futuro de Bitcoin da B3 (BIT) comprado na LIQUIDAÇÃO dos alavancados em perpétuos (funding negativo + queda forte) — margem em Tesouro Selic.

Tese de mesa: o grosso da alavancagem em cripto está em contratos perpétuos offshore (Binance/Bybit) com margem cruzada e liquidação
automática. Numa queda forte o motor de risco das corretoras vende a mercado as posições compradas que perderam a margem (cascata de
liquidação) e o funding fica NEGATIVO (os vendidos passam a pagar). Esse vendedor é forçado e cego a preço; quem compra depois da cascata
e segura alguns dias recebe o prêmio de liquidez. O pessoa física brasileira faz isso SEM sair do Brasil: compra o BIT na B3 (0,01 BTC
desde jun/2025 ≈ R$ 4,1 mil), garantia em Tesouro Selic rendendo CDI, nada de remessa nem conta em corretora offshore.
  - "liquidacao": queda de k desvios em 3 dias (BTC em US$, vol de 1 ano) E funding do dia < 0 -> compra H dias;
  - "queda": só a queda (controle: sem a assinatura da liquidação forçada).
Não repete gl_cripto_tendencia/cme_cripto (tendência) nem rev_base_cripto/gl_cripto_premio (base/desconto de ETF).

Dados: BTC no fechamento da B3 (candle de 1h da Binance BTCUSDT que fecha às 17h/18h de Brasília, x PTAX), funding 8h do perpétuo
BTCUSDT da Binance (somado no dia UTC; 00h/08h/16h UTC, todos antes do fechamento da B3), ajuste do BIT (boletim B3) desde abr/2024
segurando o vencimento mais negociado da véspera (sem salto de rolagem).
Retorno do contrato: BIT real desde abr/2024; antes, sintético = BTC em R$ − CDI − 3% a.a. (o BIT negocia acima do à vista: quem está
comprado paga a base; mediana medida 2024-26 em rev_base_cripto ≈ CDI + 2-5%). Antes de abr/2024 o resultado é hipotético.
Contrato (B3): 0,1 BTC até 13/06/2025 e 0,01 BTC desde 16/06/2025 (R$ 4,1 mil hoje; 0,1 BTC = R$ 40 mil+ = 2x R$ 20 mil -> antes de
jun/2025 só cabe com teto de 2,5x). Custo: tarifa B3 ~0,04% do nocional + meio spread ~0,06% = 0,10% por lado. IR: futuros B3 15%.
"""
import numpy as np
import pandas as pd

import fu_comum as F
from gl_cripto_premio import bit_continuo

NOME = "Bitcoin B3 (BIT) na liquidação dos perpétuos: funding negativo + queda"
TESE = "Compra o futuro de bitcoin da B3 depois da cascata de liquidação offshore (queda forte + funding negativo), segura H dias"
BENCHMARK = "CDI"
INICIO, CORTE = "2019-10-01", "2023-01-01"
REGIME = "nenhum"
CUSTO_TROCA = 0.0
CLASSE_IR = "futuros_b3"
PARAMS = {"modo": "liquidacao", "k": 1.5, "H": 5}          # maior excesso IS (2019-2022) da grade
GRADE = {"modo": ["liquidacao", "queda"], "k": [1.5, 2.0], "H": [5, 10]}
VIZINHANCA = {"k": (1.25, 2.25), "H": (3, 15)}
LANCAMENTO = {"BIT": "2024-04-17"}
TETO_ALAV, CUSTO, BASE_EXTRA = 2.5, .001, .03
INSTRUMENTOS = [("B3", "BIT", "0,01 BTC (≈ R$ 4,1 mil; 0,1 BTC até jun/2025)", "0,10%/lado"), ("Tesouro Direto", "Tesouro Selic", "garantia", "0")]
APLICAVEL = True
MOTIVO = ("Cabe com folga desde jun/2025 (0,01 BTC); de abr/2024 a jun/2025 o contrato de 0,1 BTC (R$ 35-60 mil) só entrava até 2,5x o capital. "
          "Antes de abr/2024 é hipotético (BIT não existia).")
ALAVANCAGENS = [1, 2]
MOTIVO_ALAV = "exposição-alvo 1x ou 2x o capital em contratos inteiros (teto 2,5x)."


def carrega():
    return {"btc": F.ler("btc_fech_b3.parquet"), "fund": F.ler("btc_funding.parquet"), "bit": F.ler("cripto_b3_fut.parquet")}


def _contrato(d):
    def f():
        idx = F.pf.DIAS[(F.pf.DIAS >= d["btc"]["btcusdt"].first_valid_index()) & (F.pf.DIAS <= d["btc"].index.max())]
        usd = F.nivel(d["btc"]["btcusdt"], idx)
        brl = usd * F.nivel(F.PTAX_FULL, idx)
        cdi = F.pf.CDI.reindex(idx).fillna(0)
        r_sint = brl.pct_change(fill_method=None) - cdi - BASE_EXTRA / 252
        b = d["bit"]
        b = b[b.ticker.str.startswith("BIT")]
        if len(b):
            r_real, nv = bit_continuo(b)
            r_real, nv = r_real.reindex(idx), nv.reindex(idx)
        else:
            r_real = nv = pd.Series(np.nan, index=idx)
        r = r_real.where(r_real.notna() & (idx >= pd.Timestamp(LANCAMENTO["BIT"])), r_sint).fillna(0)
        lvl = nv.where(nv.notna(), brl).ffill()
        mult = pd.Series(np.where(idx < pd.Timestamp("2025-06-16"), .1, .01), index=idx)
        noc = lvl * mult
        K = pd.DataFrame({"pc": noc.shift(1) * r, "noc": noc, "margem": 0.0, "r": r, "custo": noc * CUSTO, "rol": 12.0, "local": "b3"})
        return K, usd
    return F.memo("bit", (d["btc"], d["bit"]), f)


def gera(d, capital=20000, regime=REGIME, alavancagem=1, modo="liquidacao", k=1.5, H=5):
    K, usd = _contrato(d)
    r = np.log(usd).diff()
    z = r.rolling(3).sum() / (r.rolling(365, min_periods=150).std() * np.sqrt(3))
    gat = z <= -k
    if modo == "liquidacao":
        fu = F.nivel(d["fund"]["funding_dia"], K.index)
        gat &= fu < 0
    lado = F.segura(gat.astype(float), H)
    n = F.n_por_exposicao(K, capital, alavancagem).clip(lower=1)
    n = n.where(K["noc"] * n <= TETO_ALAV * alavancagem * capital, 0)
    return pd.DataFrame({"BIT": (lado * n).fillna(0)}, index=K.index), {"BIT": K}


F.montar(globals(), gera, carrega)
