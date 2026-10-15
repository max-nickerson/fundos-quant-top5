"""
Tesouro Selic (LFT) com deságio — carry "sem risco de crédito" quando a LFT longa paga Selic + spread positivo.

Tese de mesa: a LFT rende a Selic over; em equilíbrio negocia com taxa ~0 (o Tesouro Direto mostra a taxa como spread sobre a Selic).
Em 2020–2022 o Tesouro encurtou a dívida emitindo LFT em volume recorde (pandemia) e os bancos — que carregam LFT no ativo contra
compromissadas e têm limite de risco de "spread de LFT" (o DV01 da LFT é sobre o spread) — viraram VENDEDORES FORÇADOS: a LFT longa chegou a
pagar Selic + 0,30–0,38% a.a. (deságio). O Tesouro Direto recompra todo dia ao PU de venda: o varejo compra o MESMO deságio que a mesa
vende, sem limite de risco, e carrega até o spread fechar (ganha o carry + a marcação: duration de spread ~4–5 anos x fechamento).
Vantagem de PF: limite de risco não existe para a pessoa física; o spread de compra/recompra da LFT no Tesouro Direto é ~0,01 pp de
taxa desde 2019 (≈ 0,05% do PU) — é o produto mais barato de girar do varejo.

Implementação:
  - LFT com prazo mais perto de `prazo` anos (vencimento travado até sair; rola a 6 meses do vencimento);
  - entra quando a taxa de VENDA (resgate) >= `entrada` (pp sobre a Selic) e sai quando cai a <= entrada x `saida` (fechou);
  - compra no PU de compra, marca/vende no PU de venda; custódia B3 0,20% a.a. sobre o que passa de R$ 10 mil (Tesouro Selic é
    isento até R$ 10 mil desde ago/2020) — com R$ 20 mil = 0,10% a.a. do capital aplicado; R$ 50 mil = 0,16%;
  - fora do sinal: CDI (o caixa normal do fundo — que, aliás, também é LFT curta);
  - IR regressivo (renda fixa); 100% do capital no título (sem alavancagem no Tesouro Direto).
Observação: a LFT rende a Selic over, que é ~0,10 pp acima do CDI desde 2012 — a parcela "LFT a taxa zero" já bate o CDI por ~0,1 pp
menos a custódia; isso entra no excesso e é real (é o mesmo motivo de o caixa do varejo ficar em Tesouro Selic).
Dados: Tesouro Direto 2005+ (PU/taxa de compra e venda da manhã). Corte OOS 2021-01-01 (o deságio grande é quase todo OOS — o IS só
tem os episódios pequenos de 2005–06 e 2016–17: a grade é escolhida neles, sem ver 2020–22).
"""
import numpy as np
import pandas as pd

import _rf_comum as K
import jx_comum as J

NOME = "Tesouro Selic com deságio (LFT longa acima da Selic)"
TESE = ("Compro a LFT longa no Tesouro Direto quando ela paga Selic + spread (bancos vendendo por limite de risco) e vendo de volta "
        "ao Tesouro quando o deságio fecha; carry + fechamento sem risco de crédito")
BENCHMARK = "CDI"
INICIO, CORTE = "2008-01-01", "2021-01-01"
REGIME = "nenhum"
CUSTO_TROCA = 0.0
PARAMS = {"entrada": 0.12, "saida": 0.34, "prazo": 3}            # maior IS (empate técnico ~0; o IS quase não tem deságio)
GRADE = {"entrada": [0.05, 0.08, 0.12], "saida": [0.34], "prazo": [3, 5]}
VIZINHANCA = {"entrada": (0.06, 0.12), "saida": (0.2, 0.5), "prazo": (3.5, 6)}
CLASSE_IR = "renda_fixa"
INSTRUMENTOS = [{"onde": "Tesouro Direto (qualquer corretora, taxa zero)", "ticker": "Tesouro Selic 20XX (LFT) mais longo",
                 "lote": "0,01 título (~R$ 170); mínimo R$ 30", "custo": "spread compra/recompra ~0,01–0,03 pp de taxa; custódia 0,20% a.a. acima de R$ 10 mil"}]
APLICAVEL = True
MOTIVO = "Tesouro Direto aceita qualquer valor e recompra todo dia útil ao PU de venda publicado."
ALAVANCAGENS = [1]
MOTIVO_ALAV = "Tesouro Direto não aceita margem/alavancagem; LFT não tem futuro listado para varejo."
TIPO = "Tesouro Selic"


def carrega():
    return {"td": J.ler("td.parquet")}


def custodia(capital):
    return .002 * max(0.0, 1 - 10_000 / capital)


def _sinal(d, entrada, saida, prazo):
    td = K.tesouro(d, TIPO)
    venc = K.escolhe_vencimento(td, prazo, faixa=(.5, 1.6))
    pos = {c: i for i, c in enumerate(td["tx_venda"].columns)}
    X = td["tx_venda"].to_numpy()
    y = np.array([X[i, pos[v]] if pd.notna(v) else np.nan for i, v in enumerate(venc.to_numpy())])
    on = np.zeros(len(y), bool)
    est = False
    for t in range(len(y)):
        if np.isfinite(y[t]):
            if not est and y[t] >= entrada - 1e-9:
                est = True
            elif est and y[t] <= entrada * saida + 1e-9:
                est = False
        on[t] = est
    return td, venc, pd.Series(on, index=K.DIAS), pd.Series(y, index=K.DIAS)


def _livro(d, capital=20000, custo_mult=1, lag=0, entrada=PARAMS["entrada"], saida=PARAMS["saida"], prazo=PARAMS["prazo"]):
    td, venc, on, _ = _sinal(d, entrada, saida, prazo)
    cols = list(td["pu_venda"].columns)
    alvo = K.alvo_de_vencimento(venc, on, cols)
    ce = (td["pu_compra"] / td["pu_venda"] - 1).clip(lower=0)
    return K.livro(alvo, td["R"], capital, lag, custo_ent=ce, custo_mult=custo_mult, lote=td["pu_compra"] * .01,
                   negocia=td["obs"], vivo=td["vivo"], custodia=custodia(capital), regressivo=True)


def excesso(d, capital=20000, custo_mult=1, lag=0, regime=REGIME, alavancagem=1, **params):
    e = _livro(d, capital, custo_mult, lag, **{**PARAMS, **params})["e"]
    return K.C.aplica_regime(e, regime, CUSTO_TROCA * custo_mult)


def classes_ir(d, capital=20000, **params):
    return K.classes_de_livro(_livro(d, capital, **{**PARAMS, **params}), capital, CLASSE_IR)


def posicoes(d, **params):
    p = {**PARAMS, **params}
    td, venc, on, _ = _sinal(d, p["entrada"], p["saida"], p["prazo"])
    W = K.alvo_de_vencimento(venc, on, list(td["pu_venda"].columns))
    R = td["R"].sub(K.CDI, axis=0)
    W.columns = R.columns = [f"LFT{c:%Y%m}" for c in R.columns]
    return W, R


def negocios(d, capital=20000, **params):
    p = {**PARAMS, **params}
    ng = _livro(d, capital, **p)["negocios"].copy()
    td = K.tesouro(d, TIPO)
    if len(ng):
        ng["taxa_entrada"] = [td["tx_compra"].at[i, a] for a, i in zip(ng.ativo, ng.entrada)]
        ng["taxa_saida"] = [td["tx_venda"].at[f, a] for a, f in zip(ng.ativo, ng.saida)]
        ng["ativo"] = [f"LFT{a:%Y%m}" for a in ng.ativo]
    return ng
