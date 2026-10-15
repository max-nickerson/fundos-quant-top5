"""
Mineradoras vs metal — valor relativo entre a mineradora e o metal que ela produz.

Tese de mesa: a mineradora é uma opção alavancada no metal. Quando ela fica para trás do metal além do normal (resíduo
da regressão rolante "mineradora contra metal" barato), compro a mineradora e vendo o metal na proporção do beta;
quando fica cara, faço o contrário. Saio quando o resíduo volta à média, no stop (|z| > 4) ou no prazo máximo (120 dias).

Pares (em dólar, com hedge cambial -> excesso sobre o T-bill = excesso sobre o CDI):
  GDX x GLD, GDXJ x GDX, SIL x SLV, COPX x CPER, FCX x CPER, VALE x média(BHP, RIO).

Correções da auditoria (em relação à primeira versão da pesquisa):
  1. depois de sair por prazo ou stop, o mesmo lado fica bloqueado até o z voltar a 0 (no original reabria no mesmo dia);
  2. preços limpos em NÍVEL: salto > 15% que se desfaz em até 8 dias é erro de print (CPER 04/12/2014 e 02/02/2015).

Observação de look-ahead: a limpeza (2) olha até 8 dias à frente para confirmar que o salto se desfez. Só os prints
errados do CPER em 2014/2015 são afetados; os testes de truncamento em 2019 e 2024 não mudam o passado.
custo_mult multiplica TODOS os custos (corretagem, aluguel e financiamento da alavancagem); no original só a corretagem.
"""
import numpy as np
import pandas as pd

import comum

NOME = "Mineradoras vs metal"
TESE = "Mineradora é opção alavancada no metal: compro a mineradora que ficou para trás do metal e vendo o metal (e vice-versa)"
BENCHMARK = "CDI"
INICIO, CORTE = "2012-01-01", "2021-01-01"
REGIME = "nenhum"
CUSTO_TROCA = .001
PARAMS = {"jan": 63, "z_in": 1.0}
GRADE = {"jan": [63, 126], "z_in": [1.0, 2.0]}
VIZINHANCA = {"jan": (45, 90), "z_in": (.75, 1.5)}

PARES = {"GDX x GLD": ("GDX", ["GLD"]), "GDXJ x GDX": ("GDXJ", ["GDX"]), "SIL x SLV": ("SIL", ["SLV"]),
         "COPX x CPER": ("COPX", ["CPER"]), "FCX x CPER": ("FCX", ["CPER"]), "VALE x BHP/RIO": ("VALE", ["BHP", "RIO"])}
CUSTO = {k: .0008 if k == "FCX x CPER" else .0006 for k in PARES}   # ida, por unidade de giro do par (2 pernas)
ALUG_COMPRA, ALUG_VENDA = .003, .005                                 # a.a. sobre o par comprado / vendido
ALVO, BETA_JAN, Z_STOP, T_MAX = .10, 252, 4.0, 120


def carrega():
    return {"precos": comum.ler("mineradoras/precos.csv"), "tb": comum.TB_US}


# ---------------------------------------------------------------- peças
def _no_calendario(s, lim=5):
    """Leva uma série dos EUA ao calendário da B3 (último fechamento disponível, no máximo 5 dias)."""
    s = s[~s.index.duplicated(keep="last")]
    return s.reindex(comum.DIAS.union(s.index)).ffill(limit=lim).reindex(comum.DIAS)


def _limpa_niveis(P, lim=.15, k_max=8):
    """Erro de print: salto em log > lim desfeito em até k_max dias -> preços do intervalo viram o último preço bom."""
    P = P.copy()
    for c in P.columns:
        v = P[c]
        ok = v.dropna()
        x = np.log(ok).diff().to_numpy()
        ruim = np.zeros(len(x), bool)
        for i in range(1, len(x)):
            if np.isfinite(x[i]) and abs(x[i]) > lim and not ruim[i]:
                for k in range(1, k_max + 1):
                    if i + k < len(x) and abs(x[i] + x[i + 1:i + k + 1].sum()) < .15 * abs(x[i]):
                        ruim[i:i + k] = True
                        break
        P.loc[ok.index[ruim], c] = np.nan
        P[c] = P[c].where(P[c].notna() | v.isna()).ffill().where(v.notna() | P[c].notna())
    return P


def _beta(ra, rh, jan=BETA_JAN):
    """Beta rolante da mineradora contra o metal (retornos de 5 dias, só passado, entre 0 e 3)."""
    a5, h5 = ra.rolling(5).sum(), rh.rolling(5).sum()
    return (a5.rolling(jan, min_periods=jan // 2).cov(h5) / h5.rolling(jan, min_periods=jan // 2).var()).clip(0, 3).shift(1)


def _zscore(R, jan):
    """z do resíduo acumulado contra sua média/desvio da janela."""
    X = R.fillna(0).cumsum()
    return (X - X.rolling(jan, min_periods=jan // 2).mean()) / X.rolling(jan, min_periods=jan // 2).std()


def _semanal(Z):
    """Decide só na última sessão de cada semana (o z fica parado entre sextas)."""
    sem = pd.Series(Z.index.to_period("W-FRI"), index=Z.index)
    return Z.where(sem.ne(sem.shift(-1)), axis=0).ffill().fillna(0)


def _histerese(Z, z_in, z_out=0.0):
    """Sinal +1 (compra o par) / -1 (vende o par) e o motivo de cada saída. Prazo/stop bloqueiam o lado até o z voltar a 0."""
    Zv = Z.values
    S = np.zeros_like(Zv)
    M = np.full(Zv.shape, "", dtype=object)
    n = Zv.shape[1]
    pos, t, bl = np.zeros(n), np.zeros(n), np.zeros(n)
    for i in range(len(Zv)):
        z = Zv[i]
        ok = np.isfinite(z)
        bl[(bl == 1) & ok & (z > -z_out)] = 0
        bl[(bl == -1) & ok & (z < z_out)] = 0
        media = (pos == 1) & ok & (z > -z_out) | (pos == -1) & ok & (z < z_out)
        stop = (pos == 1) & ok & (z < -Z_STOP) | (pos == -1) & ok & (z > Z_STOP)
        prazo = (pos != 0) & (t >= T_MAX)
        M[i, (pos != 0) & ~ok] = "sem dado"
        M[i, media] = "média"
        M[i, prazo] = "prazo"
        M[i, stop] = "stop"
        forca = stop | prazo
        bl[forca] = pos[forca]
        sai = media | forca | ~ok
        pos[sai], t[sai] = 0, 0
        pos[(pos == 0) & (bl != 1) & ok & (z < -z_in) & (z > -Z_STOP)] = 1
        pos[(pos == 0) & (bl != -1) & ok & (z > z_in) & (z < Z_STOP)] = -1
        t[pos != 0] += 1
        S[i] = pos
    return pd.DataFrame(S, index=Z.index, columns=Z.columns), pd.DataFrame(M, index=Z.index, columns=Z.columns)


def _residuos(d):
    """Retorno em excesso de cada par: mineradora - beta x metal (cada perna sobre o T-bill)."""
    P = _limpa_niveis(d["precos"].apply(_no_calendario))
    tb = _no_calendario(d["tb"]).fillna(0)
    ex = lambda tk: _limpa(P[tk].pct_change(fill_method=None)) - tb
    R = {}
    for k, (a, hs) in PARES.items():
        ra, rh = ex(a), sum(ex(h) for h in hs) / len(hs)
        R[k] = ra - _beta(ra, rh) * rh
    R = pd.DataFrame(R).reindex(comum.DIAS)
    return R.where(R.notna().cumsum() > 0)


def _limpa(r, lim=.45):
    """Zera retornos absurdos (> 45% num dia) que sobraram depois da limpeza em nível."""
    return r.where((r.abs() < lim) | r.isna(), 0.0)


def _sinais(d, jan, z_in):
    R = _residuos(d)
    S, M = _histerese(_semanal(_zscore(R, jan)), z_in)
    v = R.rolling(63, min_periods=40).std().shift(1) * np.sqrt(252)            # cada par com vol-alvo 10%/sqrt(6)
    W = (S * (ALVO / np.sqrt(R.shape[1])) / v).replace([np.inf, -np.inf], 0).fillna(0).clip(-2, 2).where(S != 0, 0)
    return W, R, M


def _contrib(W, R, custo_mult=1, lag=0):
    """Pesos decididos em t, executados em t+1+lag. Devolve pesos executados, contribuição por par e custo de alavancagem."""
    R = R.fillna(0)
    We = W.shift(1 + lag).fillna(0)
    h = We.shift(1)
    C = (h * R - We.diff().abs() * pd.Series(CUSTO) * custo_mult
         - (h.clip(lower=0) * ALUG_COMPRA + (-h).clip(lower=0) * ALUG_VENDA) * custo_mult / 252).fillna(0)
    alav = (h.abs().sum(axis=1) - 2).clip(lower=0) * .01 / 252 * custo_mult   # bruto acima de 2x paga CDI + 1%
    return We, C, alav


# ---------------------------------------------------------------- contrato
def excesso(d, custo_mult=1, lag=0, regime=REGIME, jan=PARAMS["jan"], z_in=PARAMS["z_in"]):
    W, R, _ = _sinais(d, jan, z_in)
    _, C, alav = _contrib(W, R, custo_mult, lag)
    return comum.aplica_regime(C.sum(axis=1) - alav, regime, CUSTO_TROCA * custo_mult)


def posicoes(d, jan=PARAMS["jan"], z_in=PARAMS["z_in"]):
    W, R, _ = _sinais(d, jan, z_in)
    return W, R


def negocios(d, jan=PARAMS["jan"], z_in=PARAMS["z_in"], lag=0):
    W, R, M = _sinais(d, jan, z_in)
    We, C, _ = _contrib(W, R, lag=lag)
    R, idx, lin = R.fillna(0), We.index, []
    for c in We.columns:
        s = np.sign(We[c].values)
        mud = np.flatnonzero(np.diff(np.r_[0, s]) != 0)
        for k, i0 in enumerate(mud):
            if s[i0] == 0:
                continue
            i1 = mud[k + 1] if k + 1 < len(mud) else len(s)
            seg = slice(i0 + 1, min(i1 + 1, len(s)))
            dec = i1 - 1 - lag                                    # dia da decisão de sair
            motivo = "em aberto" if i1 >= len(s) else (M[c].iat[dec] or "sem vol")
            lin.append({"ativo": c, "lado": int(s[i0]), "entrada": idx[i0], "saida": idx[min(i1, len(s) - 1)], "dias": i1 - i0,
                        "retorno_%": (np.prod(1 + s[i0] * R[c].values[seg]) - 1) * 100,
                        "contrib_pp": C[c].values[seg].sum() * 100, "motivo": motivo})
    return pd.DataFrame(lin)
