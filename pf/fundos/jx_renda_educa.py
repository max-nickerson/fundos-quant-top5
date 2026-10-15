"""
Tesouro RendA+ / Educa+ contra a curva de NTN-B — existe prêmio no título "só de varejo"?

Pesquisa: há histórico. O arquivo de preços do Tesouro Transparente (precotaxatesourodireto.csv) traz Renda+ (8 vencimentos, 2049–2084,
desde jan/2023) e Educa+ (19 vencimentos, 2030–2048, desde ago/2023) com taxa e PU de compra/venda. Os dois pagam parcelas mensais iguais
corrigidas pelo IPCA (Renda+: 240 parcelas nos 20 anos até o vencimento; Educa+: 60 parcelas nos 5 anos até o vencimento).
Tese de mesa: são títulos que SÓ pessoa física compra (CPF, sem secundário institucional) — se a demanda de varejo some (ou o varejo vende
em pânico) o Tesouro teria de pagar prêmio sobre a NTN-B da mesma duration, e o PF de mesa compraria esse prêmio. O hedge natural seria
vender DAP (futuro de cupom de IPCA) — mas 1 DAP longo tem DV01 de ~R$ 75–95 por bp, contra ~R$ 15–30 por bp de R$ 20 mil em Renda+/Educa+:
o hedge arredonda para ZERO (R$ 20 mil) ou 1 contrato que hedgeia 1,5–4x demais (R$ 50 mil). Logo, sem hedge (exposição a juro real).
O que os dados mostram (ver caderno): o Tesouro precifica Renda+/Educa+ PELA CURVA DA NTN-B — o spread contra a curva de IPCA+ na mesma
duration (Macaulay das parcelas) tem mediana ~0,00 pp e oscila +-0,1 pp (ruído de interpolação), enquanto o custo de compra/recompra é de
0,4% (Educa+ curto) a 5% do PU (Renda+ 2079/2084). Não há prêmio de varejo para capturar; o teste confirma.

Implementação:
  - spread = taxa de venda do título - taxa da curva real do Tesouro Direto (IPCA+ e IPCA+ com juros; _rf_comum.curva_real) na duration de
    Macaulay do fluxo de parcelas (limitada a 30 anos — além disso, curva plana);
  - entra no título de MAIOR spread quando spread >= `thr` (fechamento de t; compra em t+1 no PU de compra); sai quando o spread <= 0
    ou após 252 pregões; 100% do capital; custódia 0,20% a.a.; IR regressivo (renda fixa).
Dados: Tesouro Direto 2023+. Corte OOS 2025-01-01 (IS de 22 meses — amostra curta, resultado não conclusivo por construção).
"""
import numpy as np
import pandas as pd

import _rf_comum as K
import jx_comum as J

NOME = "Tesouro Renda+/Educa+ contra a curva de NTN-B"
TESE = ("Compro Renda+/Educa+ (títulos só de pessoa física) quando pagam prêmio sobre a NTN-B de mesma duration e vendo quando o "
        "prêmio some — hedge em DAP é grande demais para o PF")
BENCHMARK = "CDI"
INICIO, CORTE = "2023-03-01", "2025-01-01"
REGIME = "nenhum"
CUSTO_TROCA = 0.0
PARAMS = {"tipo": "Tesouro Renda+ Aposentadoria Extra", "thr": 0.05, "dias": 252}   # maior IR no IS (todos negativos)
GRADE = {"tipo": ["Tesouro Renda+ Aposentadoria Extra", "Tesouro Educa+"], "thr": [0.05, 0.10]}
VIZINHANCA = {"thr": (0.06, 0.15), "dias": (126, 378)}
NPARC = {"Tesouro Renda+ Aposentadoria Extra": 240, "Tesouro Educa+": 60}
CLASSE_IR = "renda_fixa"
INSTRUMENTOS = [{"onde": "Tesouro Direto", "ticker": "Tesouro Renda+ 20XX / Tesouro Educa+ 20XX", "lote": "0,01 título; mínimo R$ 30",
                 "custo": "spread de compra/recompra 0,4% (Educa+ curto) a 5% (Renda+ 2084) do PU; custódia 0,20% a.a. (isenção de custódia só "
                          "para quem leva Renda+/Educa+ até a conversão)"}]
APLICAVEL = True
MOTIVO = "Títulos acessíveis a qualquer CPF a partir de R$ 30; o hedge em DAP não cabe (ver docstring)."
ALAVANCAGENS = [1]
MOTIVO_ALAV = "Tesouro Direto não aceita alavancagem."


def carrega():
    return {"td": J.ler("td.parquet")}


def spread(d, tipo):
    def f():
        td = K.tesouro(d, tipo)
        cv = K.curva_real(d)
        X = td["tx_venda"].where(td["vivo"])
        xs = cv.columns.values.astype(float)
        out = pd.DataFrame(np.nan, index=X.index, columns=X.columns)
        for v in X.columns:
            s = X[v].dropna()
            if not len(s):
                continue
            mac = J.duration_parcelas(s.index, v, NPARC[tipo], s.values) * (1 + s / 100)
            cvs = cv.reindex(s.index).to_numpy()
            out.loc[s.index, v] = [s.iloc[i] - np.interp(min(m, 30), xs, cvs[i]) if np.isfinite(cvs[i]).all() and np.isfinite(m) else np.nan
                                   for i, m in enumerate(mac.to_numpy())]
        return out
    return J.memo(("spread_re", tipo), d["td"], f)


def _alvo(d, tipo, thr, dias):
    td = K.tesouro(d, tipo)
    S = spread(d, tipo)
    cols = list(td["pu_venda"].columns)
    pos = {c: i for i, c in enumerate(cols)}
    A = np.zeros((len(K.DIAS), len(cols)))
    Sv = S.reindex(index=K.DIAS, columns=cols).to_numpy()
    atual, t0 = None, 0
    for t in range(len(K.DIAS)):
        if atual is not None:
            s = Sv[t, pos[atual]]
            if (np.isfinite(s) and s <= 0) or t - t0 >= dias:
                atual = None
        if atual is None:
            row = Sv[t]
            if np.isfinite(row).any() and np.nanmax(row) >= thr:
                atual, t0 = cols[int(np.nanargmax(row))], t
        if atual is not None:
            A[t, pos[atual]] = 1.0
    return td, pd.DataFrame(A, index=K.DIAS, columns=cols)


def _livro(d, capital=20000, custo_mult=1, lag=0, tipo=PARAMS["tipo"], thr=PARAMS["thr"], dias=PARAMS["dias"]):
    td, alvo = _alvo(d, tipo, thr, int(dias))
    ce = (td["pu_compra"] / td["pu_venda"] - 1).clip(lower=0)
    return K.livro(alvo, td["R"], capital, lag, custo_ent=ce, custo_mult=custo_mult, lote=td["pu_compra"] * .01,
                   negocia=td["obs"], vivo=td["vivo"], custodia=K.CUSTODIA_TD, regressivo=True)


def excesso(d, capital=20000, custo_mult=1, lag=0, regime=REGIME, alavancagem=1, **params):
    e = _livro(d, capital, custo_mult, lag, **{**PARAMS, **params})["e"]
    return K.C.aplica_regime(e, regime, CUSTO_TROCA * custo_mult)


def classes_ir(d, capital=20000, **params):
    return K.classes_de_livro(_livro(d, capital, **{**PARAMS, **params}), capital, CLASSE_IR)


def posicoes(d, **params):
    p = {**PARAMS, **params}
    td, W = _alvo(d, p["tipo"], p["thr"], int(p["dias"]))
    R = td["R"].sub(K.CDI, axis=0)
    nm = "Renda+" if "Renda" in p["tipo"] else "Educa+"
    W.columns = R.columns = [f"{nm}{c:%Y}" for c in R.columns]
    return W, R


def negocios(d, capital=20000, **params):
    p = {**PARAMS, **params}
    ng = _livro(d, capital, **p)["negocios"].copy()
    S = spread(d, p["tipo"])
    if len(ng):
        ng["spread_entrada"] = [S.at[i, a] if i in S.index else np.nan for a, i in zip(ng.ativo, ng.entrada)]
        nm = "Renda+" if "Renda" in p["tipo"] else "Educa+"
        ng["ativo"] = [f"{nm}{a:%Y}" for a in ng.ativo]
    return ng
