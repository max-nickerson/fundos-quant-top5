"""
ADRs chineses x Hong Kong (BABA x 9988, JD x 9618, BIDU x 9888, NTES x 9999 e mais 8 pares): compro a listagem barata, vendo a cara.

Tese de mesa: desde 2019–22 as grandes chinesas têm dupla listagem (ADR em NY e ação em HK, fungíveis via depositário — conversão leva
dias e custa US$ 0,05/ADR). O prêmio do ADR sobre HK oscila com o fuso (HK fecha 12h antes de NY) e com fluxo forçado: medo de
deslistagem (HFCAA 2022) fez o americano vender o ADR, o Southbound (chinês do continente) compra HK, inclusão no Stock Connect, MSCI
trocando a linha. Quem arbitra de verdade (converte) é institucional; o PF só pode apostar na volta do desvio, com as duas pernas.

No máximo 2 pares abertos (os de maior |z|): perna de 30% cada, bruto <= ~120% do capital (Reg T exige ~60%).
Regra: prêmio p = log(ADR) − log(HK x ações por ADR / HKD) com Adj Close; z = (p − média de `jan` dias)/desvio de 126 dias, só passado.
z >= z_in: vendo o ADR e compro HK; z <= −z_in: compro o ADR e vendo HK; saio quando z volta a 0 ou em 10 dias.
HONESTIDADE DE FUSO: o sinal usa o fechamento de HK de t (04h ET) e o de NY de t (16h ET) — não simultâneos. A execução é no PRÓXIMO
fechamento de cada praça (HK em t+1, NY em t+1), ou seja, a parte do desvio que é só fuso (HK abre em t+1 já ajustada) NÃO é capturada.

PF: HK em lotes (board lot; 9988 = 100 ações ~ US$ 1,7 mil; 9888/9618 = 50; tamanhos não confirmados um a um), ADR do mesmo valor em
dólar (fração na compra, inteiro na venda). Custos HK: corretagem IBKR 0,05% (mín. HK$ 18), selo 0,1% (0,13% entre ago/2021 e nov/2023),
taxas; aluguel para vender HK ~1,5% a.a., ADR ~1%. Conta margem (US$ 2.000 mínimos) porque há perna vendida; o livro está sempre ativo, então o saldo na IBKR é o maior exigido
em 12 meses (conta="anual" em em_comum) — com a regra mensal o IOF de ida e volta custava ~18 pp a.a. Perna HK limitada a 40% do
capital: com R$ 20 mil o lote de 9988 (~R$ 9 mil) entra, o de 9999/9961/9987 (~R$ 10–16 mil) às vezes não.
"""
import numpy as np
import pandas as pd

import em_comum as E

NOME = "ADRs chineses x Hong Kong: prêmio/desconto com as duas pernas (IBKR)"
TESE = ("Prêmio do ADR sobre a ação de HK (Adj Close, ajustado pela razão e pelo HKD) longe da média: compro a listagem barata e vendo a "
        "cara, executando no fechamento seguinte de cada praça (o fuso não é capturado)")
BENCHMARK = "CDI"
INICIO, CORTE = "2020-07-01", "2023-01-01"
REGIME = "nenhum"
CUSTO_TROCA = .001
CLASSE_IR = "exterior"
PARES = E.HK_PAR
PARAMS = {"z_in": 2.5, "jan": 20, "max_dias": 10, "peso": .30, "teto_hk": .40, "max_pares": 2}   # escolhido no IS (maior IR IS)
GRADE = {"z_in": [1.5, 2.0, 2.5], "jan": [20, 60]}
VIZINHANCA = {"z_in": (2.1, 3.0), "jan": (12, 40), "max_dias": (5, 20), "peso": (.2, .4)}
INSTRUMENTOS = ("IBKR: ADRs BABA, JD, BIDU, NTES, BILI, TCOM, NIO, LI, XPEV, BEKE, ZTO, YUMC e as linhas de HK 9988, 9618, 9888, 9999, "
                "9626, 9961, 9866, 2015, 9868, 2423, 2057, 9987 (SEHK, board lots). Vender HK exige papel 'designated for short selling'. "
                "Na B3: BABA34/JDCO34/BIDU34 — negociam em ~1/3 dos pregões, sem aluguel na prática: não usados.")
APLICAVEL = True
MOTIVO = ("Operável na IBKR com R$ 20 mil para os lotes pequenos (9888/9618/9626), mas é um livro L/S que exige conta margem (US$ 2.000 "
          "parados) e paga selo de HK nas duas pontas")
ALAVANCAGENS = [1, 1.5, 2]
MOTIVO_ALAV = "L multiplica o tamanho por par; o lote de HK limita (com 20k muitos pares viram 0 ou 1 lote). Reg T 50% cobre até 2x."


def carrega():
    tk = list(PARES) + [v[0] for v in PARES.values()] + ["HKD=X"]
    return E.seleciona(tk)


def premio(d):
    P = E.preco_usd(d)
    out = {}
    for a, (h, k, _) in PARES.items():
        ok = d["raw"][a].notna() & d["raw"][h].notna()
        p = np.log(P[a]) - np.log(P[h] * k)
        p = p.where(ok)
        out[a] = p                    # razões estáveis (prêmio bruto ~0 em todos os anos); sem filtro de salto: os saltos são fuso
    return pd.DataFrame(out)


def _aloca(z, ent_c, ent_v, max_dias, max_pares):
    """No máximo `max_pares` pares abertos; entre os candidatos do dia, os de maior |z|. Sai quando z cruza 0 ou em max_dias."""
    Z, C_, V_ = z.to_numpy(), ent_c.fillna(False).to_numpy(), ent_v.fillna(False).to_numpy()
    T, N = Z.shape
    out = np.zeros((T, N))
    lado, idade = np.zeros(N), np.zeros(N)
    for i in range(T):
        for j in range(N):
            if lado[j] != 0:
                idade[j] += 1
                zj = Z[i, j]
                if idade[j] >= max_dias or (np.isfinite(zj) and lado[j] * zj >= 0):
                    lado[j] = 0
        livres = max_pares - int((lado != 0).sum())
        if livres > 0:
            cand = [(abs(Z[i, j]), j, 1.0 if C_[i, j] else -1.0) for j in range(N) if lado[j] == 0 and (C_[i, j] or V_[i, j])]
            for _, j, sg in sorted(cand, reverse=True)[:livres]:
                lado[j], idade[j] = sg, 0
        out[i] = lado
    return pd.DataFrame(out, index=z.index, columns=z.columns)


def _pesos(d, z_in, jan, max_dias, peso, teto_hk, max_pares, capital=20000):
    p = premio(d)
    m = p.rolling(jan, min_periods=jan // 2).mean().shift(1)
    s = p.rolling(126, min_periods=60).std().shift(1)
    z = (p - m) / s
    ok = p.notna()
    ent_c = (z <= -z_in) & ok           # ADR barato: compra ADR, vende HK
    ent_v = (z >= z_in) & ok            # ADR caro: vende ADR, compra HK
    lado = _aloca(z, ent_c, ent_v, max_dias, max_pares)
    P = E.preco_usd(d)
    fx = E.PTAX.reindex(P.index.union(E.PTAX.index)).ffill().reindex(P.index)
    W = pd.DataFrame(0.0, index=P.index, columns=list(PARES) + [v[0] for v in PARES.values()])
    for a, (h, k, lote) in PARES.items():
        v_lote = P[h].ffill() * lote * fx                                   # R$ de 1 lote de HK
        n = (peso * capital / v_lote).round()
        n = n.where(n * v_lote <= teto_hk * capital, np.floor(teto_hk * capital / v_lote))
        w_hk = (n * v_lote / capital).fillna(0)                             # peso REAL da perna HK (lotes inteiros)
        est = lado[a].abs()
        w = E.congela(w_hk.to_frame(a), est.to_frame(a))[a]                 # fixo durante o negócio
        sg = E.congela(lado[[a]], est.to_frame(a))[a]
        W[h] = -sg * w
        W[a] = sg * w                                                        # ADR com o mesmo valor em dólar
    return W, {"lotes": {v[0]: v[2] for v in PARES.values()}, "conta": "anual"}


excesso, classes_ir, posicoes, negocios = E.contrato(__import__(__name__))
