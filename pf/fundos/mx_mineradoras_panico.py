"""
mx_mineradoras_panico — frente pf3_mecanismos. Mecanismo 2 (pânico + ÂNCORA de commodity) transferido do vencedor mh_petroleo
(+3,0/+3,9 pp) para mineração e siderurgia, onde os modelos de "ação vs metal" falharam (rev_mineradoras −12,8 pp: pares contínuos com
micros de metal na IBKR; rev_petroleo −8,6 pp: o mesmo erro no petróleo, corrigido no mh_petroleo comprando SÓ o pânico).

Hipótese: VALE3/BRAP4/CMIN3 são "minério em reais + risco Brasil" e GGBR4/GOAU4/CSNA3/USIM5 são "aço global em reais + risco Brasil". Num
pânico (venda forçada de estrangeiro, resgate, margem) a ação cai muito mais do que a commodity em reais justifica — o resíduo contra a
âncora despenca — e volta. Sem âncora (só "caiu muito") é faca caindo; com âncora que NÃO caiu junto é venda forçada.
Âncoras (Yahoo, quant/fundos/dados/y_comm.parquet): minério de ferro 62% SGX (TIO=F, contínuo de 1º vencimento — retornos diários
limitados a ±12% para tirar saltos de rolagem; só sinal, não é negociado) e o ETF global de siderurgia SLX (para as siderúrgicas), ambos
convertidos para reais pela PTAX e em excesso ao CDI. Preços dos EUA/Singapura não são simultâneos à B3: o sinal usa somas de 21 pregões
(o mesmo desenho do mh_petroleo), o que dilui o fuso.
Regras (iguais ao mh_petroleo, sem a perna de futuro — não há micro de minério/aço que caiba no capital): beta rolante de 252 dias (retornos
de 5 dias) contra a âncora; resíduo de 21 pregões em z-score; compra no fracionário quando z <= −z_in e a ação está >= `queda` abaixo do
topo de 63 dias (opcional: só com pânico de mercado — VIX no 1/5 mais alto do ano ou Ibovespa −10% do topo); sai quando z >= 0 ou em 42
pregões. `peso` do capital por nome, carteira limitada a 100%. Grade = a do mh_petroleo, escolhida só no IS (2015–2020) pelo maior IR.
IR: ações (isenção quando as vendas do mês <= R$ 20 mil).
"""
import numpy as np
import pandas as pd

import mh_base as B
import _mx_comum as X

C = X.C

NOME = "Mineradoras/siderúrgicas em pânico vs minério/aço em reais"
TESE = ("Compro VALE3/BRAP4/CMIN3 (âncora minério SGX) e GGBR4/GOAU4/CSNA3/USIM5 (âncora SLX) no fracionário quando a ação cai muito mais "
        "que a commodity em reais justificaria; saio quando o resíduo volta a zero")
BENCHMARK = "CDI"
INICIO, CORTE = "2015-01-01", "2021-01-01"
REGIME = "nenhum"
CLASSE_IR = "acoes"
CUSTO_TROCA = .001
ANCORA = {"VALE3": "TIO=F", "BRAP4": "TIO=F", "CMIN3": "TIO=F", "GGBR4": "SLX", "GOAU4": "SLX", "CSNA3": "SLX", "USIM5": "SLX"}
PARAMS = {"z_in": 2.0, "queda": .20, "gatilho": "mercado", "jan": 21, "max_dias": 42, "peso": .35}
GRADE = {"z_in": [1.5, 2.0], "queda": [.10, .20], "gatilho": ["acao", "mercado"]}
VIZINHANCA = {"z_in": (1.25, 2.5), "queda": (.08, .25), "jan": (15, 30), "max_dias": (30, 63)}
INSTRUMENTOS = ("B3 (Clear/Rico, corretagem zero): VALE3, BRAP4, CMIN3, GGBR4, GOAU4, CSNA3, USIM5 no fracionário, até 35% do capital por "
                "nome e 100% no total; caixa em Tesouro Selic")
APLICAVEL = True
MOTIVO = "ações líquidas no fracionário; âncora só como sinal (não há hedge de minério/aço que caiba em R$ 20–50 mil)"
ALAVANCAGENS = [1]
MOTIVO_ALAV = "posição concentrada em ações de vol 35–60% em pânicos; sem alavancagem"


def carrega():
    d = B.seleciona(B.dados(), list(ANCORA))
    y = pd.read_parquet(B.FD / "y_comm.parquet")[["TIO=F", "SLX"]]
    y.index = pd.DatetimeIndex(y.index).normalize()
    d["comm"] = y[~y.index.duplicated(keep="last")]
    return d


def _ret_comm(d, col):
    s = d["comm"][col].dropna()
    s = s.reindex(DIAS_U(s)).ffill(limit=5)
    r = s.reindex(B.DIAS).pct_change(fill_method=None).fillna(0)
    return r.clip(-.12, .12) if col == "TIO=F" else r


def DIAS_U(s):
    return B.DIAS.union(s.index)


def _sinais(d, z_in, queda, gatilho, jan, max_dias):
    P, R, ADV = B.acoes(d)
    cdi = C.CDI.reindex(B.DIAS).fillna(0)
    fx = B.PTAX.pct_change(fill_method=None).fillna(0)
    tk = [t for t in ANCORA if t in R.columns]
    anc = {c: (1 + _ret_comm(d, c)) * (1 + fx) - 1 - cdi for c in set(ANCORA.values())}
    ex = R[tk].sub(cdi, axis=0)
    res, beta = {}, {}
    for t in tk:
        a = anc[ANCORA[t]].to_frame("a")
        b = B.beta_rolante(ex[t], a, lim=(.2, 2))["a"]
        beta[t] = b
        res[t] = ex[t] - b * a["a"]
    res = pd.DataFrame(res)
    z = res.rolling(jan).sum() / (res.rolling(252, min_periods=126).std() * np.sqrt(jan))
    I = (1 + R[tk].fillna(0)).cumprod()
    dd = I / I.rolling(63, min_periods=20).max() - 1
    liq = ADV[tk] >= 10e6
    ent = (z <= -z_in) & (dd <= -queda) & liq & R[tk].notna() & z.notna()
    if gatilho == "mercado":
        vix = B.eua_ffill(d, "vix")
        ibov = B.br(d, "ibov").ffill(limit=5)
        panico = (vix >= vix.rolling(252, min_periods=126).quantile(.8)) | (ibov / ibov.rolling(63, min_periods=20).max() - 1 <= -.10)
        ent = ent & panico.to_numpy()[:, None]
    pos = B.maquina(ent, z >= 0, max_dias)
    return pos, z


def _livro(d, capital=20000, lag=0, custo_mult=1, alavancagem=1, z_in=2.0, queda=.20, gatilho="mercado", jan=21, max_dias=42, peso=.35):
    pos, _ = _sinais(d, z_in, queda, gatilho, int(jan), int(max_dias))
    W = pos * peso
    tot = W.sum(axis=1)
    W = W.div(np.maximum(tot, 1.0), axis=0)                    # carteira limitada a 100% do capital
    return B.livro(capital, W, None, d, lag=lag, custo_mult=custo_mult, alavancagem=alavancagem)


def _pad(d, capital, lag, custo_mult, alavancagem, params):
    return _livro(d, capital=capital, lag=lag, custo_mult=custo_mult, alavancagem=alavancagem, **{**PARAMS, **params})


def excesso(d, capital=20000, custo_mult=1, lag=0, regime=REGIME, alavancagem=1, **params):
    return C.aplica_regime(_pad(d, capital, lag, custo_mult, alavancagem, params)["e"], regime, CUSTO_TROCA * custo_mult)


def classes_ir(d, capital=20000, **params):
    return _pad(d, capital, 0, 1, 1, params)["classes"]


def posicoes(d, capital=20000, **params):
    r = _pad(d, capital, 0, 1, 1, params)
    return r["W"], r["Rx"]


def negocios(d, capital=20000, **params):
    return B.negocios_de(_pad(d, capital, 0, 1, 1, params), capital)


if __name__ == "__main__":
    import sys
    X.escolhe_is(sys.modules[__name__], carrega())
