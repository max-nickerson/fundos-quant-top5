"""
Debêntures para pessoa física (R$ 20–50 mil, lotes de ~R$ 1 mil, só comprado) — três livros da pesquisa institucional de crédito:
  carry        "C3 Carry com filtro de faca caindo": top-n por spread entre papéis líquidos, sai fora do top 2n;
  distressed   "C4 Distressed / recuperação": papel que negociava >= 90% do par e caiu para <= thr% (preço de crédito), compra e vende a 95%;
  incentivadas "C8 Incentivadas IPCA+ contra NTN-B": quando o spread mediano das IPCA+ sobre a NTN-B está largo contra o histórico,
               compra as 15 mais líquidas — aqui SÓ incentivadas (Lei 12.431: isentas de IR para PF = o edge de pessoa física) e SEM
               hedge de duration (PF não vende NTN-B no Tesouro Direto e 1 DAP ~ R$ 90 mil de PU = 2–5x o PL).

Preços: o painel do institucional (quant/fundos/ideias_credito.painel): %PU da curva do ÚLTIMO negócio >= R$ 100 mil do SND (2019+),
filtro de prints (salto > 10% só vale confirmado), acréscimo do PU par (CDI+spread, %CDI, IPCA+taxa). Cache em pf/dados/rev_debentures/.
Diferenças PF (tudo no motor _simula, em R$, com patrimônio que cresce):
  - quantidade INTEIRA de debêntures: alvo = patrimônio/n; unidades = piso(alvo / PU em R$ do último negócio x (1+markup)); papel com
    PU alto (VNE R$ 10 mil+) simplesmente não cabe e o livro passa ao próximo candidato.
  - custo de varejo MEDIDO no balcão B3 (2023–26, 651 mil pares de negócios: lote <= R$ 50 mil contra o VWAP dos lotes >= R$ 1 mi do mesmo
    papel e dia): o cliente compra em mediana 0,2–0,5% acima até 2 anos, 0,9–1,3% em 2–5 anos, 1,8–2,8% acima de 5 anos (~0,40% x
    duration) e vende 0,2–1,3% abaixo (~0,15% x duration). Uso markup = max(0,2%; 0,40% x D) na compra e haircut = max(0,15%; 0,15% x D)
    na venda; no livro distressed (via mesa, papel estressado) mínimo de 2% por lado. Script: scratchpad markup.py; ver caderno.
    Custódia: zero (XP, Rico, BTG, Inter, Nubank não cobram custódia de renda fixa — https://www.itaucorretora.com.br/explore/custosoperacionais.aspx,
    https://www.nordinvestimentos.com.br/blog/taxas-de-corretagem-das-corretoras-hoje/).
  - execução no 1º pregão >= t+1+lag em que o papel tem negócio (preço real), compra-e-segura (sem rebalancear: prints ruidosos).
  - marca parada: papel com marca < 90% e sem negócio há mais de 21 pregões deixa de acumular o carrego (só volta a render quando um
    negócio novo confirma o valor). Papel que vence/some sem negócio fecha na última marca (perda fica). Papel que pede RJ fica preso
    até negociar de novo.
  - IR: incentivada (cadastro SND) -> "isento" (Lei 12.431/2011 art. 2º; MP 1.303/2025, que taxaria em 5%, caducou em out/2025:
    https://www.infomoney.com.br/minhas-financas/mp-1-303-cai-no-congresso-veja-como-fica-a-tributacao-dos-investimentos-agora/);
    não incentivada -> tabela regressiva 22,5–15% sobre o ganho realizado na venda (truque de classes: MTM em "isento", no dia da venda
    G x alíquota/15% em "renda_fixa" contra -G x alíquota/15% em "isento"). Cupons/amortizações tributados só na venda (aproximação).
  - acesso: oferta pública ao varejo só após lock-up (Res. CVM 160 art. 86: 6 meses p/ qualificado, 1 ano p/ público geral; ICVM 476 até
    2022: só qualificados no secundário) -> proxy de "prateleira": o papel teve negócios de varejo (ticket médio diário <= R$ 30 mil no SND)
    em >= 3 dos últimos 63 pregões. Distressed quase nunca está na prateleira (comitês tiram o papel da vitrine): só via mesa/assessor e,
    muitas vezes, só para investidor qualificado (R$ 1 mi+) -> APLICÁVEL PARCIAL.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _util as U  # noqa: E402

C, pf = U.C, U.pf
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

NOME = "Debêntures PF em lotes de R$ 1 mil (carry / distressed / incentivadas isentas)"
TESE = ("CDI+spread paga o spread se o emissor não quebra: compro em lotes de R$ 1 mil, na prateleira das corretoras, as 5 debêntures DI de "
        "maior spread entre as líquidas (giro >= R$ 5 mi em 63 dias, PU >= 90% da curva) e seguro no mínimo 2 anos (ou até vencer) — "
        "o markup de varejo (1–3%) proíbe o giro do institucional; depois de 2 anos sai se cair fora do top 2n. Livros alternativos: "
        "distressed (comprar a 70–80% do par quem não pediu RJ, vender a 95%) e incentivadas IPCA+ isentas quando o mercado todo está largo "
        "contra a NTN-B (pós-Americanas, COVID).")
BENCHMARK = "CDI"
INICIO, CORTE = "2019-07-01", "2023-01-01"
REGIME = "nenhum"          # crédito ilíquido: liga/desliga custa 2–5% (markup + haircut de varejo); o institucional usava HMM (não existe aqui)
CUSTO_TROCA = .03
PARAMS = {"livro": "carry", "n": 5, "liq": 5e6, "filtro": 0, "ind": "DI", "prateleira": 1, "min_dias": 504,
          "thr": 80, "modo": "todos", "z": 1.0, "so_incent": 1, "mk": .40, "hc": .15}
GRADE = {"n": [5, 10], "min_dias": [0, 252, 504], "liq": [5e6, 2e7]}
VIZINHANCA = {"n": (4, 8), "min_dias": (378, 630), "liq": (3e6, 1e7), "mk": (.30, .50), "hc": (.10, .25)}
# grades/parâmetros por livro (o runner roda o "carry"; os outros dois são rodados com estes dicionários — ver caderno)
LIVROS = {
    "carry": {"PARAMS": {}, "GRADE": GRADE, "VIZINHANCA": VIZINHANCA},
    "distressed": {"PARAMS": {"livro": "distressed", "thr": 80, "modo": "todos", "prateleira": 0, "min_dias": 0},
                   "GRADE": {"thr": [70, 80], "modo": ["todos", "sem_rj", "sem_rj_ou_plano"]},
                   "VIZINHANCA": {"thr": (72, 85), "mk": (.30, .50), "hc": (.10, .25)}},
    "incentivadas": {"PARAMS": {"livro": "incentivadas", "modo": "mercado", "z": 1.0, "so_incent": 1, "min_dias": 0},
                     "GRADE": {"modo": ["papel", "mercado"], "z": [1.0, 1.5]},
                     "VIZINHANCA": {"z": (.75, 1.5), "mk": (.30, .50), "hc": (.10, .25)}},
}
RANKING = ["C3 Carry com filtro de faca caindo", "C4 Distressed / recuperação", "C8 Incentivadas IPCA+ contra NTN-B"]
INSTRUMENTOS = {"debêntures DI/IPCA+ (secundário)": {"onde": "XP/BTG/Inter/Rico/Nubank (prateleira de renda fixa) ou mesa/assessor",
                                                     "lote": "1 debênture (PU ~R$ 1 mil)", "custo": "markup ~0,40% x duration na compra, ~0,15% x duration na venda; custódia 0"},
                "caixa": {"onde": "Tesouro Selic / CDB liquidez diária", "custo": "0"}}
APLICAVEL = "parcial"
MOTIVO = ("Carry e incentivadas: rota real de varejo (prateleira das corretoras, lote de R$ 1 mil), mas o varejo paga 1–3% de markup e só vê "
          "papéis já fora do lock-up/oferta pública. Distressed: papel estressado sai da prateleira e boa parte (ICVM 476) só é negociável por "
          "investidor qualificado — rota só via mesa/assessor, com custo de 2%+ por lado.")
ALAVANCAGENS = [1]
MOTIVO_ALAV = ("Debênture é comprada à vista: não há crédito para PF comprar debênture, não aceita ser vendida a descoberto e não há futuro "
               "de crédito. Alavancar exigiria compromissada/conta margem que o varejo não tem.")
VARIANTES = {
    "carry DI+IPCA (sem hedge)": {"ind": "todos"},
    "carry sem filtro de prateleira": {"prateleira": 0},
    "carry com filtro de faca": {"filtro": 1},
    "carry regra institucional (n 10, sem prazo mínimo)": {"n": 10, "min_dias": 0},
    "carry custo institucional (30 bps/lado)": {"mk": 0.0, "hc": 0.0, "custo_fixo": .003},
    "distressed (thr 80, todos, via mesa)": {"livro": "distressed", "thr": 80, "modo": "todos", "prateleira": 0, "min_dias": 0},
    "distressed sem RJ": {"livro": "distressed", "thr": 80, "modo": "sem_rj", "prateleira": 0, "min_dias": 0},
    "distressed só prateleira": {"livro": "distressed", "thr": 80, "modo": "todos", "prateleira": 1, "min_dias": 0},
    "incentivadas mercado z1 (isentas, sem hedge)": {"livro": "incentivadas", "modo": "mercado", "z": 1.0, "so_incent": 1, "min_dias": 0},
    "incentivadas papel z1": {"livro": "incentivadas", "modo": "papel", "z": 1.0, "so_incent": 1, "min_dias": 0},
    "IPCA+ mercado z1 todas (como o institucional, sem hedge)": {"livro": "incentivadas", "modo": "mercado", "z": 1.0, "so_incent": 0, "min_dias": 0},
}

DIR = U.CACHE / "rev_debentures"
PAINEIS = ["Pf", "R2", "D", "S", "prem", "fin21", "fin63", "age", "T", "pc", "pcb", "PU", "varejo", "caiu",
           "obs", "vivo", "elig", "so_par", "faca", "em_rj", "plano"]


# =============================================================================== cache (roda uma vez, a partir dos dados brutos)
def _constroi():
    """Monta os painéis com o código do institucional (painel(), eventos_rj(), preco_balcao()) + PU em R$ e proxy de varejo do SND."""
    sys.path.insert(0, str(U.QUANT / "fundos"))
    import ideias_credito as IC
    p = IC.painel()
    ev = IC.eventos_rj()
    pcb = IC.preco_balcao()
    dias, cad = p["dias"], p["cad"]
    cols = cad.index[cad.indice.isin(["DI", "IPCA"]) & p["vivo"].any().reindex(cad.index).values]
    f = lambda x: x.reindex(columns=cols)
    Pf, obs, vivo, age = f(p["Pf"]), f(p["obs"]), f(p["vivo"]), f(p["age"])
    # retorno total SEM hedge; marca parada: papel < 90% sem negócio há > 21 pregões não acumula carrego até o próximo negócio
    L = np.log1p(f(p["R"]).fillna(0)).cumsum()
    ok = (age <= 21) | (Pf >= 90) | ~vivo
    R2 = np.expm1(L.where(ok).ffill().fillna(0).diff().fillna(0)).where(vivo)
    ind = cad.indice.reindex(cols)
    pc = Pf.copy()
    ip = (ind == "IPCA").to_numpy()
    pc.loc[:, ip] = 100 * np.exp(-(f(p["S"]).loc[:, ip] - 1.5).clip(lower=0) * f(p["D"]).loc[:, ip] / 100)
    caiu = pc.where(obs).rolling(252, min_periods=1).max().shift(1) >= 90
    snd = pd.read_parquet(U.QD / "snd_negocios.parquet", columns=["date", "codigo", "qtd", "negocios", "pu_med"])
    snd = snd[snd.codigo.isin(cols)]
    PU = snd.pivot_table(index="date", columns="codigo", values="pu_med", aggfunc="last").reindex(index=dias, columns=cols).ffill()
    tk = (snd.qtd * snd.pu_med / snd.negocios.clip(lower=1))
    pequeno = (snd.assign(s=(tk <= 3e4).astype(float)).pivot_table(index="date", columns="codigo", values="s", aggfunc="max")
               .reindex(index=dias, columns=cols).fillna(0))
    varejo = pequeno.rolling(63, min_periods=1).sum()
    evr = ev.reindex(cols)
    D = dias.values[:, None]
    em_rj = pd.DataFrame(D >= evr.rj.values.astype("datetime64[ns]")[None, :], index=dias, columns=cols) & evr.rj.notna().values[None, :]
    plano = pd.DataFrame(D >= evr.plano.values.astype("datetime64[ns]")[None, :], index=dias, columns=cols) & evr.plano.notna().values[None, :]
    faca = ((f(p["prem"]) - f(p["prem"]).shift(21)) > .5) | (Pf < Pf.rolling(63, min_periods=1).max() - 3)
    out = {"Pf": Pf, "R2": R2, "D": f(p["D"]), "S": f(p["S"]), "prem": f(p["prem"]), "fin21": f(p["fin21"]), "fin63": f(p["fin63"]),
           "age": age, "T": f(p["T"]), "pc": pc, "pcb": f(pcb), "PU": PU, "varejo": varejo, "caiu": caiu, "obs": obs, "vivo": vivo,
           "elig": f(p["elig"]), "so_par": f(p["so_par"]), "faca": faca, "em_rj": em_rj, "plano": plano}
    DIR.mkdir(parents=True, exist_ok=True)
    for k, v in out.items():
        v = v.astype("float32") if v.dtypes.iloc[0] != bool else v.astype(bool)
        v.index.name = "data"
        v.to_parquet(DIR / f"{k}.parquet", compression="zstd")
    cd = pd.DataFrame({"empresa": cad.empresa, "indice": cad.indice, "incentivada": cad.incentivada.fillna(False).astype(bool),
                       "raiz": p["raiz"], "venc": cad.venc, "juros": cad.juros}).reindex(cols)
    cd.to_parquet(DIR / "cad.parquet")


def carrega():
    if not (DIR / "cad.parquet").exists():
        _constroi()
    d = {k: pd.read_parquet(DIR / f"{k}.parquet") for k in PAINEIS}
    d["cad"] = pd.read_parquet(DIR / "cad.parquet")          # estático (sem data): emissor, indexador, incentivada
    return d


# =============================================================================== sinais (só dados até t)
def _sinais(d, livro, n, liq, filtro, ind, prateleira, thr, modo, z, so_incent):
    """Devolve quer, sai, prioridade (DataFrames booleanos/float decididos no fechamento de t), máx. dias e se é livro estressado."""
    cad, Pf, S = d["cad"], d["Pf"], d["S"]
    cols = Pf.columns
    shelf = d["varejo"] >= 3 if prateleira else pd.DataFrame(True, index=Pf.index, columns=cols)
    if livro == "carry":
        base = d["elig"] & (d["fin63"] >= liq) & (Pf >= 90) & (S < 8)
        if ind != "todos":
            base &= (cad.indice == ind).to_numpy()[None, :]
        if filtro:
            base &= ~d["faca"]
        rk = S.where(base).rank(axis=1, ascending=False)
        quer = (rk <= n) & shelf
        sai = (d["elig"] & ~(rk <= 2 * n)) | (d["faca"] if filtro else False)
        return quer, sai, S.where(base), None, False, n
    if livro == "distressed":
        pc = d["pc"]
        quer = d["obs"] & (pc <= thr) & (pc >= 10) & d["caiu"] & (d["T"] > .25) & (d["fin21"] >= 5e5) & shelf
        dias = Pf.index
        quer &= (dias < pd.Timestamp("2023-04-01"))[:, None] | (d["pcb"] <= thr + 5)
        sai = pc >= 95
        if modo == "sem_rj":
            quer &= ~d["em_rj"]
            sai |= d["em_rj"]
        elif modo == "sem_rj_ou_plano":
            quer &= ~d["em_rj"] | d["plano"]
            sai |= d["em_rj"] & ~d["plano"]
        return quer, sai, -pc, 504, True, 10
    # incentivadas IPCA+ contra NTN-B
    m = (cad.indice == "IPCA").to_numpy()
    if so_incent:
        m &= cad.incentivada.to_numpy()
    c2 = cols[m]
    base = d["elig"][c2] & (Pf[c2] >= 85) & (S[c2] < 6)
    Sx = S[c2]
    if modo == "papel":
        so = Sx.where(d["obs"][c2])
        mu = so.rolling(252, min_periods=30).mean().shift(1)
        sd = so.rolling(252, min_periods=30).std().shift(1)
        zz = ((Sx - mu) / sd).where(base)
        quer, sai, pri, mx = zz >= z, zz <= 0, zz, 252
    else:
        M = Sx.where(base).median(axis=1)
        mz = (M - M.expanding(126).mean().shift(1)) / M.expanding(126).std().shift(1)
        top = d["fin63"][c2].where(base).rank(axis=1, ascending=False) <= 15
        quer = top.mul(mz >= z, axis=0)
        sai = pd.DataFrame(np.repeat((mz <= 0).to_numpy()[:, None], len(c2), 1), index=Sx.index, columns=c2)
        pri, mx = d["fin63"][c2], None
    quer = quer.reindex(columns=cols, fill_value=False) & shelf
    return quer, sai.reindex(columns=cols, fill_value=False), pri.reindex(columns=cols), mx, False, 15


def _aliq(dc):
    return .225 if dc <= 180 else .20 if dc <= 360 else .175 if dc <= 720 else .15


# =============================================================================== motor PF
_MEMO, _SIN, _ARR = {}, {}, {}


def _simula(d, capital=20000, custo_mult=1, lag=0, alavancagem=1, livro="carry", n=10, liq=5e6, filtro=0, ind="DI", prateleira=1,
            thr=80, modo="todos", z=1.0, so_incent=1, mk=.40, hc=.15, custo_fixo=0.0, min_dias=0):
    chave = (id(d["Pf"]), len(d["Pf"]), capital, custo_mult, lag, livro, n, liq, filtro, ind, prateleira, thr, modo, z, so_incent, mk, hc,
             custo_fixo, min_dias)
    if chave in _MEMO:
        return _MEMO[chave]
    cols = d["Pf"].columns
    dias_d = d["Pf"].index
    dias = C.DIAS[(C.DIAS >= dias_d[0]) & (C.DIAS <= dias_d[-1])]
    al = lambda x: x.reindex(index=dias, columns=cols)
    ks = (id(d["Pf"]), len(d["Pf"]), livro, n, liq, filtro, ind, prateleira, thr, modo, z, so_incent)
    if ks not in _SIN:                                                    # sinais não dependem de custo/lag/capital
        quer, sai, pri, max_dias, estressado, n_max = _sinais(d, livro, int(n), liq, filtro, ind, prateleira, thr, modo, z, so_incent)
        if len(_SIN) > 8:
            _SIN.clear()
        _SIN[ks] = (al(quer).fillna(False).to_numpy(bool), al(sai).fillna(False).to_numpy(bool), al(pri).to_numpy(float),
                    max_dias, estressado, n_max)
    Q, X, PR, max_dias, estressado, n_max = _SIN[ks]
    ka = (id(d["Pf"]), len(d["Pf"]))
    if ka not in _ARR:
        _ARR.clear()
        _ARR[ka] = (al(d["obs"]).fillna(False).to_numpy(bool), al(d["vivo"]).fillna(False).to_numpy(bool),
                    *(al(d[k]).to_numpy(float) for k in ("R2", "PU", "D", "Pf")))
    OB, VV, R2, PU, DD, PF = _ARR[ka]
    cad = d["cad"].reindex(cols)
    em, inc = cad.raiz.to_numpy(), cad.incentivada.to_numpy(bool)
    cdi = C.CDI.reindex(dias).fillna(0).to_numpy()
    nT = len(dias)
    k0 = 1 + lag
    mn = .02 if estressado else 0.0

    def cmk(k, t):            # markup na compra (fração do PU)
        dd = DD[t, k] if not np.isnan(DD[t, k]) else 3.0
        return (max(.002, mk / 100 * dd, mn) + custo_fixo) * custo_mult if (mk or mn) else custo_fixo * custo_mult

    def chc(k, t):            # haircut na venda antecipada
        dd = DD[t, k] if not np.isnan(DD[t, k]) else 3.0
        return (max(.0015, hc / 100 * dd, mn) + custo_fixo) * custo_mult if (hc or mn) else custo_fixo * custo_mult

    ex, mtm, rf, perd = np.zeros(nT), np.zeros(nT), np.zeros(nT), np.zeros(nT)
    W = np.zeros((nT, len(cols)))
    CT = np.zeros((nT, len(cols)))
    nav = float(capital)
    held, trades = {}, []
    for t in range(nT):
        navp = nav
        pnl = 0.0
        vt = 0.0
        for k, h in held.items():                                         # carrego/marcação do dia
            r = R2[t, k]
            r = 0.0 if np.isnan(r) else r
            g = h["V"] * r
            pnl += g
            vt += h["V"]
            CT[t, k] += g / navp - h["V"] * cdi[t] / navp
            h["V"] += g
        perd[t] = vt * cdi[t] / navp
        s = t - k0
        for k in list(held):                                              # saídas
            h = held[k]
            morto = not VV[t, k]
            fim = t == nT - 1
            if morto or fim or (s >= 0 and OB[t, k] and ((X[s, k] and t - h["t0"] >= min_dias) or (max_dias and t - h["t0"] >= max_dias))):
                c = 0.0 if (morto or fim) else h["V"] * chc(k, t)
                pnl -= c
                CT[t, k] -= c / navp
                h["V"] -= c
                G = h["V"] - h["custo"]
                if not inc[k]:
                    rf[t] += G * _aliq((dias[t] - h["d0"]).days) / .15 / navp
                trades.append({"ativo": cols[k], "emissor": str(cad.empresa.iloc[k])[:30], "indice": cad.indice.iloc[k],
                               "incentivada": bool(inc[k]), "lado": 1, "entrada": h["d0"], "saida": dias[t], "dias": t - h["t0"],
                               "unidades": h["u"], "pct_entrada": h["p0"], "pct_saida": PF[t - 1 if morto else t, k],
                               "retorno_%": (h["V"] / h["custo"] - 1) * 100, "contrib_pp": CT[h["t0"]:t + 1, k].sum() * 100,
                               "motivo_saida": "vencimento/sumiu" if morto else ("aberta" if fim else "sinal")})
                del held[k]
        if s >= 0 and len(held) < n_max and t < nT - 1:                  # entradas: só quem negociou hoje
            cand = np.flatnonzero(Q[s] & OB[t] & VV[t])
            if len(cand):
                cand = cand[np.argsort(-np.nan_to_num(PR[s, cand], nan=-1e9), kind="stable")]
                ne = {}
                for k in held:
                    ne[em[k]] = ne.get(em[k], 0) + 1
                alvo = nav / n_max
                caixa = nav - sum(h["V"] for h in held.values())
                for k in cand:
                    if len(held) >= n_max:
                        break
                    if k in held or ne.get(em[k], 0) >= 1 or np.isnan(PU[t, k]) or PU[t, k] <= 0:
                        continue
                    m_ = cmk(k, t)
                    u = np.floor(min(alvo, caixa) / (PU[t, k] * (1 + m_)))
                    if u < 1:
                        continue                                          # lote não cabe (PU alto) -> próximo candidato
                    V0 = u * PU[t, k]
                    c = V0 * m_
                    pnl -= c
                    CT[t, k] -= c / navp
                    caixa -= V0 + c
                    held[k] = {"V": V0, "custo": V0 + c, "u": int(u), "d0": dias[t], "t0": t, "p0": PF[t, k]}
                    ne[em[k]] = ne.get(em[k], 0) + 1
        for k, h in held.items():
            W[t, k] = h["V"] / navp
        mtm[t] = pnl / navp
        ex[t] = mtm[t] - perd[t]
        nav = navp * (1 + cdi[t] + ex[t])
    out = {"ex": pd.Series(ex, dias).reindex(C.DIAS).fillna(0), "mtm": pd.Series(mtm, dias).reindex(C.DIAS).fillna(0),
           "rf": pd.Series(rf, dias).reindex(C.DIAS).fillna(0), "perd": pd.Series(perd, dias).reindex(C.DIAS).fillna(0),
           "W": pd.DataFrame(W, dias, cols), "trades": pd.DataFrame(trades), "dias": dias}
    if len(_MEMO) > 6:
        _MEMO.clear()
    _MEMO[chave] = out
    return out


def excesso(d, capital=20000, custo_mult=1, lag=0, regime=REGIME, alavancagem=1, **params):
    s = _simula(d, capital, custo_mult, lag, alavancagem, **{**PARAMS, **params})
    return C.aplica_regime(s["ex"], regime, CUSTO_TROCA * custo_mult)


def classes_ir(d, capital=20000, **params):
    s = _simula(d, capital, **{**PARAMS, **params})
    return {"isento": (s["mtm"] - s["rf"]) * capital, "renda_fixa": s["rf"] * capital, "_cdi_perdido": s["perd"] * capital}


def posicoes(d, capital=20000, **params):
    s = _simula(d, capital, **{**PARAMS, **params})
    R = (d["R2"].reindex(index=s["dias"]) .sub(C.CDI.reindex(s["dias"]), axis=0)).fillna(0)
    W = s["W"]
    W = W.loc[:, (W != 0).any()]
    return W.shift(-1).fillna(0).reindex(C.DIAS).fillna(0), R[W.columns].reindex(C.DIAS).fillna(0)


def negocios(d, capital=20000, **params):
    return _simula(d, capital, **{**PARAMS, **params})["trades"]
