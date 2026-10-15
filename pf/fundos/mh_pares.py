"""
Pares long-short de ações brasileiras do MESMO negócio (bancos, transmissoras, distribuidoras/integradas, geradoras, varejo de moda/eletro),
com aluguel REAL de pessoa física e ações inteiras no fracionário.

Tese de mesa: Itaú e Bradesco, Taesa e ISA Energia, Lojas Renner e Guararapes têm o mesmo regulador, a mesma curva de juros e o mesmo
consumidor; quando um anda muito mais que o outro em poucas semanas SEM notícia (sem fato relevante nem balanço de nenhum dos dois), é fluxo
(rebalanceamento de fundo, ETF, estrangeiro saindo de um papel) e volta. Com notícia é informação e não volta (lição dos pares globais IM1:
os piores negócios foram divergências de fundamento). Vendo o que subiu demais e compro o que ficou para trás (resíduo do beta de 1 ano),
saio quando o resíduo volta a zero, em 30 pregões ou se o desvio passar de 3,5 desvios (quebra).
Custos de PF: aluguel 0,5% do volume por contrato aberto/renovado (Clear/Rico) + taxa ao doador 1% a.a. (bancos/elétricas) ou 3% a.a.
(varejo) x 1,2 de tarifa B3; garantia 25% além do produto da venda; fracionário com spread 2x.
"""
import numpy as np
import pandas as pd

import mh_base as B
import comum as C

NOME = "Pares intra-setor B3 sem notícia (aluguel PF)"
TESE = ("Vendo a ação que disparou contra a par do mesmo negócio sem notícia e compro a que ficou para trás; saio quando o resíduo zera "
        "(aluguel PF real, fracionário)")
BENCHMARK = "CDI"
INICIO, CORTE = "2015-01-01", "2021-01-01"
REGIME = "nenhum"
CUSTO_TROCA = .001
PARAMS = {"jan": 21, "z_in": 2.0, "noticia": True, "max_pares": 2, "perna": .4, "max_dias": 30, "stop": 3.5}
GRADE = {"jan": [10, 21], "z_in": [1.5, 2.0], "noticia": [True, False]}
VIZINHANCA = {"jan": (8, 30), "z_in": (1.25, 2.5), "max_dias": (15, 45), "stop": (3.0, 4.5)}
VARIANTES = {"4 pares simultâneos": {"max_pares": 4, "perna": .25}}
PARES = [("ITUB4", "BBDC4"), ("ITUB4", "BBAS3"), ("BBDC4", "BBAS3"), ("ITUB4", "SANB11"), ("BBDC4", "SANB11"),     # bancos
         ("TAEE11", "ISAE4"), ("TAEE11", "ALUP11"), ("ISAE4", "ALUP11"),                                        # transmissão
         ("CMIG4", "CPLE3"), ("EQTL3", "ENGI11"), ("CPFE3", "ENGI11"), ("CMIG4", "CPFE3"), ("EQTL3", "CPFE3"),  # distribuição
         ("EGIE3", "AXIA3"),                                                                                   # geração
         ("LREN3", "GUAR3"), ("LREN3", "CEAB3"), ("GUAR3", "CEAB3"), ("LREN3", "AZZA3"), ("MGLU3", "BHIA3")]    # varejo
VAREJO = {"LREN3", "GUAR3", "CEAB3", "AZZA3", "MGLU3", "BHIA3"}
APLICAVEL = True
MOTIVO = "Aplicável: ações no fracionário e aluguel de PF (Clear/Rico/XP/BTG); 2 pares de ~R$ 8 mil por perna com R$ 20 mil"
INSTRUMENTOS = ("B3: compra no fracionário e venda a descoberto com aluguel (BTC) de pessoa física — 0,5% do volume por contrato + taxa ao "
                "doador; garantia 25% em Tesouro Selic/ações; até 2 pares de 40% do capital por perna")
ALAVANCAGENS = [1, 1.5, 2]
MOTIVO_ALAV = "Até 2x (bruto 3,2x do capital em 2 pares; garantia ainda cabe com ações de 70% de deságio); 5x estoura a garantia do aluguel"


def carrega():
    tk = sorted({t for p in PARES for t in p})
    return B.seleciona(B.dados(), tk)


def _sinais(d, jan, z_in, noticia, stop):
    P, R, ADV = B.acoes(d)
    cdi = C.CDI.reindex(B.DIAS).fillna(0)
    ev = d["eventos"]
    ev_d = pd.DataFrame(0.0, index=B.DIAS, columns=P.columns)
    for t, g in ev.groupby("ticker"):
        if t in ev_d:
            dd = pd.DatetimeIndex(pd.to_datetime(g.data)).normalize()
            pos = B.DIAS.searchsorted(dd)                                 # evento em dia sem pregão -> próximo pregão
            pos = pos[pos < len(B.DIAS)]
            ev_d.iloc[np.unique(pos), ev_d.columns.get_loc(t)] = 1.0
    ev_d = ev_d.shift(1).fillna(0)                                       # FR entregue à noite só é conhecido no pregão seguinte
    ev_jan = ev_d.rolling(jan + 2, min_periods=1).max()                  # notícia dentro da janela da divergência
    Z, BT, OK = {}, {}, {}
    for a, b in PARES:
        if a not in R or b not in R:
            continue
        ea, eb = R[a] - cdi, R[b] - cdi
        bt = B.beta_rolante(ea, eb.to_frame("b"), lim=(.5, 2))["b"]
        res = ea - bt * eb
        z = res.rolling(jan).sum() / (res.rolling(252, min_periods=126).std() * np.sqrt(jan))
        ok = (ADV[a] >= 10e6) & (ADV[b] >= 10e6) & R[a].notna() & R[b].notna()
        if noticia:
            ok &= (ev_jan[a] == 0) & (ev_jan[b] == 0)
        k = f"{a}/{b}"
        Z[k], BT[k], OK[k] = z, bt, ok
    return pd.DataFrame(Z), pd.DataFrame(BT), pd.DataFrame(OK)


def _carteira(Z, OK, z_in, max_pares, max_dias, stop):
    """Loop no tempo: abre o par com maior |z| enquanto houver vaga; lado = -sinal(z) (vende o que subiu demais)."""
    z, ok = Z.to_numpy(), OK.to_numpy(bool)
    T, K = z.shape
    lado = np.zeros((T, K))
    ativo = {}                                                            # par -> (lado, idade)
    for i in range(T):
        for k in list(ativo):
            s, idade = ativo[k]
            idade += 1
            zi = z[i, k]
            if np.isnan(zi) or zi * s >= 0 or idade >= max_dias or abs(zi) >= stop:   # resíduo cruzou zero / prazo / quebra
                del ativo[k]
                continue
            ativo[k] = (s, idade)
        vagas = max_pares - len(ativo)
        if vagas > 0:
            cand = [(abs(z[i, k]), k) for k in range(K) if k not in ativo and ok[i, k] and not np.isnan(z[i, k])
                    and z_in <= abs(z[i, k]) < stop]
            for _, k in sorted(cand, reverse=True)[:vagas]:
                ativo[k] = (-np.sign(z[i, k]), 0)
        for k, (s, _) in ativo.items():
            lado[i, k] = s
    return pd.DataFrame(lado, index=Z.index, columns=Z.columns)


def _livro(d, capital=20000, lag=0, custo_mult=1, alavancagem=1, jan=21, z_in=2.0, noticia=True, max_pares=2, perna=.4, max_dias=30,
           stop=3.5):
    Z, BT, OK = _sinais(d, jan, z_in, noticia, stop)
    L = _carteira(Z, OK, z_in, max_pares, max_dias, stop)
    bt = B.congela(BT, L)
    W = pd.DataFrame(0.0, index=B.DIAS, columns=d["P"].columns)
    for k in L.columns:
        a, b = k.split("/")
        W[a] += L[k] * perna
        W[b] -= L[k] * perna * bt[k].where(L[k] != 0, 0).clip(.5, 2)
    W = W.loc[:, (W != 0).any()]
    taxa = {t: (.03 if t in VAREJO else .01) for t in W.columns}
    return B.livro(capital, W, None, d, lag=lag, custo_mult=custo_mult, alavancagem=alavancagem, taxa_aluguel=taxa)


def excesso(d, capital=20000, custo_mult=1, lag=0, regime=REGIME, alavancagem=1, **params):
    e = B.padrao(__import__(__name__), d, capital, lag, custo_mult, alavancagem, params)["e"]
    return C.aplica_regime(e, regime, CUSTO_TROCA * custo_mult)


def classes_ir(d, capital=20000, **params):
    return B.padrao(__import__(__name__), d, capital, 0, 1, 1, params)["classes"]


def posicoes(d, capital=20000, **params):
    r = B.padrao(__import__(__name__), d, capital, 0, 1, 1, params)
    return r["W"], r["Rx"]


def negocios(d, capital=20000, **params):
    return B.negocios_de(B.padrao(__import__(__name__), d, capital, 0, 1, 1, params), capital)


def diagnostico(d, capital=20000, **params):
    r = B.padrao(__import__(__name__), d, capital, 0, 1, 1, params)
    out = dict(r["diag"])
    con = r["contrib"]
    out["custo de aluguel aprox. (pp a.a.)"] = np.nan
    vend = r["pos"].clip(upper=0).ne(0).sum(axis=1)
    out["dias com perna vendida %"] = float((vend > 0).mean() * 100)
    return out
