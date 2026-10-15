"""
Debêntures BOAS em lote pequeno compradas no secundário durante uma onda de resgates de fundos de crédito (contágio, não default).

Tese de mesa: quando um evento de crédito grande acontece (Covid mar/2020, Americanas jan/2023, Light/Gol 2023, ondas de resgate de
fundos de crédito privado em 2024–25), os fundos com resgate D+1/D+30 precisam vender O QUE TEM LIQUIDEZ — e o que tem liquidez são os
papéis bons, não o que deu default. O preço dos papéis bons cai 2–5 pontos por fluxo, sem mudança de crédito, e volta em meses quando os
resgates param. O PF, com lote de R$ 1 mil, compra justamente esses papéis no balcão (prateleira/mesa da corretora) de quem é vendedor
forçado; institucional grande não consegue montar posição em lote pequeno sem mexer no preço — e incentivada é ISENTA só para o PF.
Diferente do já testado: rev_debentures (carry top-n por spread; "distressed" = comprar papel a 70–80% do par) e rf_incentivadas
(carry até o vencimento). Aqui é EVENTO: só papel que estava no par, caiu pouco (2–3 pts) enquanto o MERCADO TODO caía (onda de resgates),
sem RJ, e sai quando recupera.

Implementação (painéis da frente revisita, pf/dados/rev_debentures: SND 2019+, %PU da curva do último negócio >= R$ 100 mil, retorno
total R2 com marca parada tratada, duration, RJ por data de divulgação):
  - preço de crédito CP: DI -> %PU da curva (só crédito mexe); IPCA+ -> 100 - spread sobre a NTN-B x duration (tira o juro real do sinal);
  - onda de resgates (fechamento de t): mediana, entre os papéis negociados nos últimos 5 dias, da variação de CP em 21 pregões <= -`m`;
  - candidato: negociou hoje, CP(t) <= máximo de 63 pregões - `q`, máximo de 63 pregões >= 98 (era papel "no par"), CP(t) >= 85, sem RJ;
    universo "DI" (DI/%CDI, tributadas — IR regressivo) ou "incent" (incentivadas IPCA+, isentas para PF);
  - até 5 papéis (1/5 do capital cada), comprados no 1º dia >= t+1 em que negociam, lote inteiro de PU (~R$ 1 mil); sai quando CP volta a
    >= referência - 0,5 pt ou após 252 pregões; custos de varejo MEDIDOS no balcão (rev_debentures): compra max(0,2%; 0,40% x duration),
    venda antecipada max(0,15%; 0,15% x duration), x custo_mult. Custódia zero (corretoras não cobram em renda fixa).
Corte OOS 2023-01-01 (IS 2019-2022 tem Covid; OOS tem Americanas e as ondas de 2024–25).
"""
import numpy as np
import pandas as pd

import _rf_comum as K
import jx_comum as J

NOME = "Debêntures boas na onda de resgates (lote pequeno, secundário)"
TESE = ("Compro em lote de R$ 1 mil debêntures que estavam no par e caíram 2–3 pts enquanto o mercado todo caía (fundos de crédito vendendo "
        "o que tem liquidez), sem RJ; vendo quando o preço volta")
BENCHMARK = "CDI"
INICIO, CORTE = "2019-07-01", "2023-01-01"
REGIME = "nenhum"
CUSTO_TROCA = 0.0
PARAMS = {"m": 0.6, "q": 2.0, "universo": "incent", "n": 5, "dias": 252}   # maior IR no IS (2019-07 a 2022; todos negativos)
GRADE = {"m": [0.3, 0.6], "q": [2.0, 3.0], "universo": ["DI", "incent"]}
VIZINHANCA = {"m": (0.2, 0.8), "q": (1.5, 3.5), "n": (3, 8), "dias": (126, 378)}
CLASSE_IR = "isento"                # universo escolhido = incentivadas (Lei 12.431)
INSTRUMENTOS = [{"onde": "XP/BTG/Inter/Rico (prateleira de secundário) ou mesa/assessor", "ticker": "debêntures DI / incentivadas IPCA+",
                 "lote": "1 debênture (PU ~R$ 1 mil)", "custo": "markup max(0,2%; 0,40% x duration) na compra, max(0,15%; 0,15% x duration) na venda"}]
APLICAVEL = "parcial"
MOTIVO = ("Os papéis bons seguem na prateleira, mas no pico do estresse a corretora alarga o markup e parte dos papéis é ICVM 476 (só "
          "qualificado). Lote de R$ 1 mil é o edge; o preço de referência é o negócio >= R$ 100 mil do SND (o varejo paga o markup medido).")
ALAVANCAGENS = [1]
MOTIVO_ALAV = "Debênture é à vista; não há crédito/margem para PF em crédito privado."
DIR = J.PF / "dados" / "rev_debentures"
PAINEIS = ["Pf", "R2", "D", "S", "PU", "obs", "vivo", "em_rj"]


def carrega():
    d = {k: pd.read_parquet(DIR / f"{k}.parquet") for k in PAINEIS}
    for k in ("obs", "vivo", "em_rj"):
        d[k] = d[k].astype(bool)
    d["cad"] = pd.read_parquet(DIR / "cad.parquet")      # estático: indexador, incentivada
    return d


def _cp(d):
    def f():
        cad = d["cad"].reindex(d["Pf"].columns)
        ipca = (cad.indice == "IPCA").to_numpy()
        cp = d["Pf"].astype(float).copy()
        cp.loc[:, ipca] = 100 - (d["S"].astype(float).loc[:, ipca] * d["D"].astype(float).loc[:, ipca]).to_numpy()
        return cp.reindex(J.DIAS)
    return J.memo("cp", d["Pf"], f)


def _sinal(d, m, q, universo):
    def f():
        cp = _cp(d)
        obs = d["obs"].reindex(J.DIAS).fillna(False).astype(bool)
        cpo = cp.where(obs).ffill(limit=5)
        rec = obs.rolling(5, min_periods=1).max().astype(bool)
        ch = (cpo - cpo.shift(21)).where(rec)
        M = ch.median(axis=1)
        mx = cpo.rolling(63, min_periods=10).max()
        cad = d["cad"].reindex(cp.columns)
        uni = (cad.indice == "DI").to_numpy() if universo == "DI" else ((cad.indice == "IPCA") & cad.incentivada).to_numpy()
        rj = d["em_rj"].reindex(J.DIAS).fillna(False).astype(bool)
        cand = obs & (cp <= mx - q) & (mx >= 98) & (cp >= 85) & ~rj
        cand = cand & uni[None, :]
        cand = cand.mul(M <= -m, axis=0)
        return cp, cpo, mx, cand.astype(bool), M
    return J.memo(("sin_deb", m, q, universo), d["Pf"], f)


def _alvo(d, m, q, universo, n, dias):
    cp, cpo, mx, cand, M = _sinal(d, m, q, universo)
    cols = cp.columns
    C_ = cand.to_numpy()
    CP, MX = cpo.to_numpy(), mx.to_numpy()
    A = np.zeros(C_.shape)
    held = {}
    for t in range(len(J.DIAS)):
        for k in list(held):
            ref, t0 = held[k]
            if (np.isfinite(CP[t, k]) and CP[t, k] >= ref - .5) or t - t0 >= dias:
                del held[k]
        if len(held) < n and C_[t].any():
            ks = np.flatnonzero(C_[t])
            ks = ks[np.argsort(-(MX[t, ks] - CP[t, ks]))]
            for k in ks:
                if len(held) >= n:
                    break
                if k not in held:
                    held[k] = (MX[t, k], t)
        for k in held:
            A[t, k] = 1.0 / n
    return pd.DataFrame(A, index=J.DIAS, columns=cols)


def _livro(d, capital=20000, custo_mult=1, lag=0, m=PARAMS["m"], q=PARAMS["q"], universo=PARAMS["universo"], n=PARAMS["n"], dias=PARAMS["dias"]):
    alvo = _alvo(d, m, q, universo, int(n), int(dias))
    use = alvo.columns[(alvo > 0).any()]
    alvo = alvo[use]
    al = lambda x: x[use].reindex(J.DIAS).astype(float)
    D = al(d["D"]).ffill().fillna(3.0)
    ce = np.maximum(.002, .004 * D)
    cs = np.maximum(.0015, .0015 * D)
    R = al(d["R2"]).fillna(0)
    obs = d["obs"][use].reindex(J.DIAS).fillna(False).astype(bool)
    vivo = d["vivo"][use].reindex(J.DIAS).fillna(False).astype(bool)
    PU = al(d["PU"]).ffill(limit=5)
    return K.livro(alvo, R, capital, lag, custo_ent=ce, custo_sai=cs, custo_mult=custo_mult, lote=PU, negocia=obs, vivo=vivo,
                   regressivo=(universo == "DI"))


def excesso(d, capital=20000, custo_mult=1, lag=0, regime=REGIME, alavancagem=1, **params):
    e = _livro(d, capital, custo_mult, lag, **{**PARAMS, **params})["e"]
    return K.C.aplica_regime(e, regime, CUSTO_TROCA * custo_mult)


def classes_ir(d, capital=20000, **params):
    p = {**PARAMS, **params}
    return K.classes_de_livro(_livro(d, capital, **p), capital, "renda_fixa" if p["universo"] == "DI" else "isento")


def posicoes(d, **params):
    p = {**PARAMS, **params}
    W = _alvo(d, p["m"], p["q"], p["universo"], int(p["n"]), int(p["dias"]))
    W = W.loc[:, (W > 0).any()]
    R = d["R2"][W.columns].reindex(J.DIAS).astype(float).fillna(0).sub(J.CDI, axis=0)
    return W, R


def negocios(d, capital=20000, **params):
    p = {**PARAMS, **params}
    ng = _livro(d, capital, **p)["negocios"].copy()
    if len(ng):
        cad = d["cad"]
        cp = _cp(d)
        ng["emissor"] = [str(cad.empresa.get(a, ""))[:28] for a in ng.ativo]
        ng["cp_entrada"] = [cp.at[i, a] for a, i in zip(ng.ativo, ng.entrada)]
        ng["cp_saida"] = [cp.at[f, a] for a, f in zip(ng.ativo, ng.saida)]
    return ng
