"""
Fuso EWZ x B3: o EWZ (e os ADRs PBR/VALE) fecham em Nova York depois do leilão de fechamento da B3 (até ~1h depois, conforme o horário de
verão americano) e o dólar continua negociando. O "descasamento" do dia, s = retorno do EWZ em US$ - (BOVA11 em R$ convertido pelo dólar),
mede o que o estrangeiro fez com o Brasil depois que a B3 fechou.

Pergunta do dono: "o movimento do EWZ depois das 17h prevê a abertura?" — prevê, mas a abertura (gap do fechamento de t até o leilão de
abertura de t+1) NÃO é capturável por quem só opera na B3: o teste honesto é entrar NO LEILÃO DE ABERTURA de t+1 (ordem colocada na
pré-abertura, depois de ver o EWZ) e sair no leilão de fechamento do mesmo dia (day trade). `diagnostico` mede as duas regressões
(gap e pregão contra s). Na pesquisa anterior (G8) o efeito existe em todo o mundo mas o gap absorve 30–90% e o resto é do tamanho do
custo; aqui, com day trade de PF: emolumentos 0,023% por lado + 20% de IR, sem aluguel (venda a descoberto intradiária dispensa BTC).
Lado "segue" = comprar quando o EWZ subiu depois da B3; "reverte" = o contrário (a abertura exagera e devolve no pregão).
Execução: decisão à noite (dados de t), operação no leilão de abertura de t+1 (`lag`=1 -> no dia seguinte, sinal velho).
"""
import numpy as np
import pandas as pd

import mh_base as B
import comum as C

NOME = "Fuso EWZ/ADR x B3 no leilão de abertura (day trade)"
TESE = ("Depois de ver o EWZ/ADRs fecharem em NY, compro (ou vendo) BOVA11/PETR4/VALE3 no leilão de abertura e zero no leilão de "
        "fechamento: pega a parte do movimento noturno que a abertura não precificou")
BENCHMARK = "CDI"
INICIO, CORTE = "2014-01-01", "2021-01-01"
REGIME = "nenhum"
CUSTO_TROCA = .001
PARAMS = {"thr": .01, "lado": "segue", "universo": "bova+adr", "peso": 1.0, "impacto": .0002}
GRADE = {"thr": [.005, .01], "lado": ["segue", "reverte"], "universo": ["bova", "bova+adr"]}
VIZINHANCA = {"thr": (.004, .015)}
VARIANTES = {"reverte só BOVA11": {"lado": "reverte", "universo": "bova"}}
PARES = {"BOVA11": "ewz", "PETR4": "pbr", "VALE3": "vale"}
APLICAVEL = True
MOTIVO = "Aplicável: BOVA11/PETR4/VALE3 em day trade com qualquer capital (leilões de abertura e fechamento); IR de day trade 20%"
INSTRUMENTOS = ("B3 (Clear/Rico, corretagem zero): ordem no leilão de abertura (10h) e no de fechamento (16h55–17h) do mesmo dia, BOVA11 "
                "(cotas inteiras) ou PETR4/VALE3; venda a descoberto intradiária sem aluguel; caixa todo o tempo em Tesouro Selic (garantia)")
ALAVANCAGENS = [1, 1.5, 2]
MOTIVO_ALAV = "Day trade com garantia em Tesouro Selic: as corretoras dão 2–5x intradiário; 2x já é o limite prudente para um sinal desse tamanho"


def carrega():
    d = B.seleciona(B.dados(), ["PETR4", "VALE3"])
    br = d["br"]
    d["P"] = d["P"].join(br[["bova_fech"]].rename(columns={"bova_fech": "BOVA11"}), how="outer")
    d["O"] = d["O"].join(br[["bova_abre"]].rename(columns={"bova_abre": "BOVA11"}), how="outer")
    return d


def _mesmo_dia(d, col):
    """Retorno em US$ do ativo dos EUA NO MESMO dia do pregão da B3 (sem preencher: se NY não abriu, sem sinal)."""
    s = d["eua"][col].dropna()
    r = s.pct_change(fill_method=None)
    return r.reindex(B.DIAS)


def _base(d, universo):
    tks = ["BOVA11"] + (["PETR4", "VALE3"] if universo == "bova+adr" else [])
    P = d["P"].reindex(B.DIAS)[tks]
    O = d["O"].reindex(B.DIAS)[tks]
    brl = _mesmo_dia(d, "brl")                                           # R$ por US$ (Yahoo, fim do dia em NY)
    S, GAP, INTRA = {}, {}, {}
    for t in tks:
        r_loc = P[t] / P[t].shift(1) - 1                                  # só pregões consecutivos com negócio
        r_us = _mesmo_dia(d, PARES[t])
        S[t] = r_us - ((1 + r_loc) / (1 + brl) - 1)
        GAP[t] = O[t] / P[t].shift(1) - 1                                 # fechamento de t-1 -> abertura de t (não capturável)
        INTRA[t] = P[t] / O[t] - 1                                        # abertura -> fechamento de t (capturável)
    return pd.DataFrame(S), pd.DataFrame(GAP), pd.DataFrame(INTRA), O


def _livro(d, capital=20000, lag=0, custo_mult=1, alavancagem=1, thr=.01, lado="reverte", universo="bova", peso=1.0, impacto=.0002):
    S, GAP, INTRA, O = _base(d, universo)
    sg = 1.0 if lado == "segue" else -1.0
    sinal = np.sign(S).where(S.abs() >= thr, 0) * sg                     # decidido com dados de t (noite de t)
    n_ativos = sinal.ne(0).sum(axis=1).replace(0, 1)
    w = sinal.div(n_ativos, axis=0) * peso * alavancagem                  # fração do capital por ativo
    w = w.shift(1 + lag).fillna(0)                                        # opera no leilão de abertura de t+1(+lag)
    Ou = O.ffill(limit=5)
    nq = np.trunc((w * capital / Ou).fillna(0))                           # ações/cotas inteiras ao preço do leilão de abertura
    ok = INTRA.notna()
    nq = nq.where(ok, 0)
    pnl = (nq * Ou * INTRA.fillna(0))
    giro = 2 * nq.abs() * Ou.fillna(0)
    custo = giro * (B.EMOL_DT + impacto) * custo_mult
    con = (pnl - custo).fillna(0)
    tot = con.sum(axis=1)
    return {"e": tot / capital, "contrib": con, "pos": nq, "W": sinal.mul(peso / n_ativos, axis=0).fillna(0),
            "Rx": INTRA.fillna(0).shift(1).fillna(0), "ret": INTRA.fillna(0), "classes": {"day_trade": tot},
            "diag": {"dias operados %": float((nq.abs().sum(axis=1) > 0).mean() * 100)}}


def excesso(d, capital=20000, custo_mult=1, lag=0, regime=REGIME, alavancagem=1, **params):
    e = B.padrao(__import__(__name__), d, capital, lag, custo_mult, alavancagem, params)["e"]
    return C.aplica_regime(e.reindex(B.DIAS).fillna(0), regime, CUSTO_TROCA * custo_mult)


def classes_ir(d, capital=20000, **params):
    return B.padrao(__import__(__name__), d, capital, 0, 1, 1, params)["classes"]


def posicoes(d, capital=20000, **params):
    r = B.padrao(__import__(__name__), d, capital, 0, 1, 1, params)
    return r["W"], r["Rx"]


def negocios(d, capital=20000, **params):
    r = B.padrao(__import__(__name__), d, capital, 0, 1, 1, params)
    pos, con, ret = r["pos"], r["contrib"], r["ret"]
    out = []
    for t in pos.columns:
        x = pos[t][pos[t] != 0]
        for dt, q in x.items():
            out.append({"ativo": t, "lado": int(np.sign(q)), "entrada": dt.date(), "saida": dt.date(), "dias": 1, "qtd_ini": float(q),
                        "retorno_%": float(ret.at[dt, t] * 100 * np.sign(q)), "contrib_pp": float(con.at[dt, t] / capital * 100)})
    return pd.DataFrame(out, columns=["ativo", "lado", "entrada", "saida", "dias", "qtd_ini", "retorno_%", "contrib_pp"])


def diagnostico(d, capital=20000, **params):
    """Regressões (por ativo, IS e OOS): gap da abertura de t+1 contra s_t e pregão de t+1 contra s_t. beta_gap ~ fração do descasamento
    que a abertura já precifica; beta_pregao > 0 = o pregão continua, < 0 = devolve."""
    p = {**PARAMS, **params}
    S, GAP, INTRA, _ = _base(d, "bova+adr")
    out = dict(B.padrao(__import__(__name__), d, capital, 0, 1, 1, params)["diag"])
    for t in S.columns:
        for nome, msk in (("IS", S.index < pd.Timestamp(CORTE)), ("OOS", S.index >= pd.Timestamp(CORTE))):
            x = S[t][msk]
            for alvo, Y in (("gap", GAP[t].shift(-1)), ("pregao", INTRA[t].shift(-1))):
                df = pd.concat([x, Y[msk]], axis=1).dropna()
                df = df[(df.iloc[:, 0].abs() < .15) & (df.iloc[:, 1].abs() < .15)]
                if len(df) > 100:
                    b = np.polyfit(df.iloc[:, 0], df.iloc[:, 1], 1)[0]
                    out[f"{t} {nome} beta_{alvo}"] = float(b)
            df = pd.concat([x, INTRA[t].shift(-1)[msk]], axis=1).dropna()
            big = df[df.iloc[:, 0].abs() >= p["thr"]]
            if len(big):
                out[f"{t} {nome} pregão médio quando |s|>=thr, no sentido de s (bps)"] = float((np.sign(big.iloc[:, 0]) * big.iloc[:, 1]).mean() * 1e4)
    return out
