"""
Debêntures incentivadas (Lei 12.431) — carry ISENTO de IR de pessoa física, comprado no varejo (XP/BTG/Inter/Rico).

Tese de mesa: a debênture incentivada IPCA+ paga juro real acima da NTN-B e, para pessoa física, o cupom E o ganho são isentos. Contra um
CDI que paga 15% de IR, IPCA+7% isento equivale a ~IPCA+8,2% tributado (gross-up). Compro as de maior spread sobre a NTN-B de mesma
duration, 1 por emissor, em lotes de R$ 1 mil, e SEGURO ATÉ O VENCIMENTO (vender antes paga o spread da plataforma de novo). Filtros de
mesa: (i) "faca caindo" — não compro papel cujo preço caiu > 3 pts em 21 dias (o mercado sabe algo); (ii) "isenção careca" — só compro
quando a mediana das incentivadas paga >= `premio_min` pp sobre a NTN-B (em 2025–26 incentivada AAA chegou a pagar MENOS que a NTN-B:
o comprador isento paga a isenção inteira; aí o certo é ficar no Tesouro/CDI).
Vantagem de pessoa física: só PF (e fundos de infra) têm isenção total; institucional tributado não compete pelo papel — o prêmio é
"pago" pela demanda isenta e capturado só por quem é isento.

Implementação:
  - preço: %PU da curva (SND) do VWAP diário com volume >= R$ 100 mil, filtro de prints (salto > 10% só vale confirmado depois), marca
    = último negócio (compra e segura); retorno diário = Pf(t)/Pf(t-1) x (1+IPCA do dia) x (1+taxa de emissão)^(1/252) - 1;
  - duration de MERCADO medida no balcão B3 2023+ (inclinação ln PU x taxa dentro do mesmo dia): ~0,63 x prazo até 10 anos, 7–8 depois;
    taxa ≈ taxa de emissão - ln(%PU)/duration; spread = taxa - NTN-B (Tesouro IPCA+, taxa de venda) na mesma duration;
  - spread de VAREJO (medido no balcão B3, DEB incentivadas com >= 10 negócios no dia, 2023–26): p10–p90 do PU do mesmo papel no
    mesmo dia = 3,2% (mediana; 0,72 pp de taxa) — a plataforma compra na ponta alta da taxa e vende na baixa. Premissa: compra 1,6% acima
    da marca e venda antecipada 1,6% abaixo (no vencimento, sem custo); custo_mult escala os dois;
  - execução: decide no fechamento de t, compra no 1º dia >= t+1+lag em que o papel negocia; lotes inteiros de PU (~R$ 1–1,5 mil);
  - sem hedge (pessoa física não opera DAP com esse tamanho): o fundo carrega juro real + crédito contra o CDI.
  - IR: classe "isento" (cupons e ganho); o CDI perdido pagaria 15% (convenção _cdi_perdido).
Dados: SND (negócios diários 2019+, cadastro com `incentivada`), Tesouro Direto, IPCA. Corte OOS 2023-01-01.
"""
import numpy as np
import pandas as pd

import _rf_comum as K

NOME = "Debêntures incentivadas isentas (carry de varejo)"
TESE = ("Carrego até o vencimento as incentivadas IPCA+ de maior spread sobre a NTN-B (isentas para PF), sem faca caindo e só quando a "
        "isenção não está 'careca'")
BENCHMARK = "CDI"
INICIO, CORTE = "2019-07-01", "2023-01-01"
REGIME = "nenhum"
CUSTO_TROCA = 0.0
PARAMS = {"n": 5, "saida": "vencimento", "premio_min": 0.5, "faca": 1}
GRADE = {"n": [5, 10], "saida": ["vencimento", "rotaciona"], "premio_min": [-9.0, 0.5], "faca": [0, 1]}
VIZINHANCA = {"n": (4, 10), "premio_min": (0.25, 0.9)}
CLASSE_IR = "isento"
ALIQUOTAS = None
T_MAX = 6.0                    # escada de varejo: só papéis que vencem em até 6 anos (limita duration e gira a carteira)
CUSTO_VAREJO = .016            # por lado, fração do PU (metade da faixa p10–p90 de 3,2% medida no balcão B3)
D_T = (np.array([0, 1, 2, 3, 4, 5, 6, 8, 10, 15, 30.]), np.array([0, .55, 1.06, 1.8, 2.37, 3.09, 3.79, 4.6, 5.7, 7.3, 7.8]))
INSTRUMENTOS = [{"onde": "XP / BTG / Inter / Rico / Nubank (prateleira de debêntures, secundário)", "ticker": "debêntures incentivadas IPCA+ (ex.: CMGDB1, TAEE17)",
                 "lote": "1 debênture (~R$ 1–1,5 mil)", "custo": "sem taxa explícita; spread embutido ~1,6% do PU na compra e ~1,6% na venda antecipada"}]
APLICAVEL = True
MOTIVO = "Lotes de ~R$ 1 mil nas plataformas; com R$ 20 mil cabem 5 papéis de ~R$ 4 mil (10 com R$ 50 mil)."
ALAVANCAGENS = [1]
MOTIVO_ALAV = "Debênture não aceita alavancagem no varejo (não serve de garantia para termo; não há compromissada para PF)."


def carrega():
    return {"snd": K.ler("snd_negocios_incentivadas.parquet"), "cad": K.ler("snd_cadastro_incentivadas.parquet"),
            "td": K.ler("tesouro_direto.parquet"), "ipca": K.ler("ipca_mensal.csv")}


def _limpa_precos(P, tol=.10, conf=.03):
    """Filtro de prints sem olhar o futuro: um negócio que se afasta > tol da última marca só vira marca quando outro negócio em dia
    POSTERIOR confirma (dentro de conf). Até lá o papel fica na marca antiga e não é negociável (copiado da pesquisa de crédito)."""
    X = P.to_numpy()
    out = np.full(X.shape, np.nan)
    for j in range(X.shape[1]):
        idx = np.flatnonzero(~np.isnan(X[:, j]))
        m = pend = np.nan
        for i in idx:
            x = X[i, j]
            if np.isnan(m) or abs(x / m - 1) <= tol or (not np.isnan(pend) and abs(x / pend - 1) <= conf):
                m, pend = x, np.nan
                out[i, j] = x
            else:
                pend = x
    return pd.DataFrame(out, index=P.index, columns=P.columns)


def painel(d):
    def f():
        cad = d["cad"]
        cad = cad[(cad.indice == "IPCA")].drop_duplicates("codigo").set_index("codigo")
        s = d["snd"]
        s = s[s.codigo.isin(cad.index) & s.pct_curva.between(5, 200)]
        s = s.assign(vol=s.qtd * s.pu_med)
        s = s[s.vol >= 1e5]
        s = s.assign(w=s.pct_curva * s.vol)
        g = s.groupby(["data", "codigo"])
        P = _limpa_precos((g.w.sum() / g.vol.sum()).unstack().reindex(K.DIAS).reindex(columns=cad.index).dropna(axis=1, how="all"))
        cols = P.columns
        cad = cad.loc[cols]
        PU = g.pu_med.median().unstack().reindex(index=K.DIAS, columns=cols).ffill()
        vol = g.vol.sum().unstack().reindex(index=K.DIAS, columns=cols).fillna(0)
        venc = cad.venc
        vivo = pd.DataFrame({k: K.DIAS < venc[k] for k in cols}, index=K.DIAS)
        obs = P.notna() & vivo
        Pf = P.ffill().where(vivo)
        ipd = K.ipca_diario(d).to_numpy()[:, None]
        j = np.nan_to_num(cad.juros.to_numpy(dtype=float)) / 100
        G = (1 + ipd) * (1 + j[None, :]) ** (1 / 252)
        R = (Pf / Pf.shift(1) * G - 1).where(vivo & Pf.shift(1).notna())
        R = R.where(R.abs() < .5).fillna(0)
        T = pd.DataFrame({k: (venc[k] - K.DIAS).days / 365.25 for k in cols}, index=K.DIAS).where(vivo)
        D = pd.DataFrame(np.interp(T.fillna(0).to_numpy(), *D_T), index=K.DIAS, columns=cols).where(vivo)
        taxa = j[None, :] * 100 - np.log(Pf / 100) / D.clip(lower=.3) * 100
        ntnb = K.interp_curva(K.curva_real(d), D.clip(1, 30))
        S = taxa - ntnb
        pos = np.arange(len(K.DIAS))[:, None]
        ult = pd.DataFrame(np.where(obs, pos, np.nan), index=K.DIAS, columns=cols).ffill()
        idade = pos - ult
        no_par = ((P - 100).abs() < .05).rolling(126, min_periods=1).sum() / obs.rolling(126, min_periods=1).sum().replace(0, np.nan)
        elig = (vivo & (idade <= 5) & (vol.rolling(21).sum() >= 1e6) & (T > 1.5) & (T <= T_MAX) & S.notna() & (no_par < .8)
                & (Pf >= 85) & (Pf <= 115))
        raiz = cad.cnpj.astype(str).str.replace(r"\D", "", regex=True).str.zfill(14).str[:8]
        return dict(P=P, Pf=Pf, PU=PU, R=R, S=S, D=D, T=T, obs=obs, vivo=vivo, elig=elig, raiz=raiz, cad=cad, ntnb=ntnb, taxa=taxa)
    return K.memo("deb_painel", d["snd"], f)


def _alvo(d, n, saida, premio_min, faca):
    """Pesos-alvo (1/n por papel) decididos no fechamento de t. 'vencimento': uma vez comprado, segura até vencer (o alvo fica ligado);
    'rotaciona': sai quando o papel cai para fora do top 3n (paga o spread de venda)."""
    p = painel(d)
    S, el = p["S"], p["elig"]
    Pf = p["Pf"]
    caiu = (Pf / Pf.rolling(21, min_periods=5).max() - 1) < -.03
    base = el & (S < 6) & (S > -1)
    if faca:
        base &= ~caiu
    med = S.where(el).median(axis=1)
    pode_comprar = med >= premio_min
    rk = S.where(base).rank(axis=1, ascending=False)
    Sv, bv, rv, pc = S.to_numpy(), base.to_numpy(), rk.to_numpy(), pode_comprar.to_numpy()
    Sl, mv = S.where(p["obs"]).ffill().to_numpy(), med.to_numpy()
    vv = p["vivo"].to_numpy()
    raiz = p["raiz"].reindex(S.columns).to_numpy()
    A = np.zeros(S.shape)
    held = set()
    for t in range(len(K.DIAS)):
        held = {k for k in held if vv[t, k]}
        if saida == "rotaciona":                                       # realiza quando o spread volta à mediana (papel deixou de ser barato)
            held = {k for k in held if not (np.isfinite(Sl[t, k]) and Sl[t, k] <= mv[t])}
        if pc[t] and len(held) < n:
            em = {raiz[k] for k in held}
            for k in np.argsort(np.where(bv[t], -np.nan_to_num(Sv[t], nan=-99), 99)):
                if len(held) >= n or not bv[t, k]:
                    break
                if k in held or raiz[k] in em:
                    continue
                held.add(k)
                em.add(raiz[k])
        for k in held:
            A[t, k] = 1 / n
    return pd.DataFrame(A, index=K.DIAS, columns=S.columns)


def _livro(d, capital=20000, custo_mult=1, lag=0, n=PARAMS["n"], saida=PARAMS["saida"], premio_min=PARAMS["premio_min"], faca=PARAMS["faca"]):
    p = painel(d)
    A = _alvo(d, n, saida, premio_min, faca)
    lote = p["PU"] * (1 + CUSTO_VAREJO)
    return K.livro(A, p["R"], capital, lag, custo_ent=CUSTO_VAREJO, custo_sai=CUSTO_VAREJO, custo_mult=custo_mult, lote=lote,
                   negocia=p["obs"], vivo=p["vivo"])


def excesso(d, capital=20000, custo_mult=1, lag=0, regime=REGIME, alavancagem=1, **params):
    e = _livro(d, capital, custo_mult, lag, **{**PARAMS, **params})["e"]
    return K.C.aplica_regime(e, regime, CUSTO_TROCA * custo_mult)


def classes_ir(d, capital=20000, **params):
    return K.classes_de_livro(_livro(d, capital, **{**PARAMS, **params}), capital, CLASSE_IR)


def posicoes(d, **params):
    p_ = {**PARAMS, **params}
    p = painel(d)
    W = _alvo(d, p_["n"], p_["saida"], p_["premio_min"], p_["faca"])
    return W, p["R"].sub(K.CDI, axis=0)


def negocios(d, capital=20000, **params):
    p = painel(d)
    ng = _livro(d, capital, **{**PARAMS, **params})["negocios"].copy()
    if len(ng):
        ng["emissor"] = ng.ativo.map(p["cad"].empresa).str[:28]
        ng["pct_entrada"] = [p["Pf"].at[i, a] for a, i in zip(ng.ativo, ng.entrada)]
        ng["pct_saida"] = [p["Pf"].at[f, a] if pd.notna(p["Pf"].at[f, a]) else np.nan for a, f in zip(ng.ativo, ng.saida)]
        ng["spread_entrada"] = [p["S"].shift(1).at[i, a] for a, i in zip(ng.ativo, ng.entrada)]
    return ng
