"""
JF1 "Juro real de valor (NTN-B longa)" refeito para pessoa física no TESOURO DIRETO (R$ 20–50 mil).

Mesa: "IPCA+6,5% numa NTN-B longa é prêmio fiscal demais". Quando o juro real de 10 anos (curva das NTN-B do Tesouro Direto) passa de
6,5% a.a., compro Tesouro IPCA+ (NTN-B principal) de ~15 anos no Tesouro Direto e seguro até o juro real voltar abaixo de 5,5%.
O resto do capital fica em Tesouro Selic/CDB liquidez diária (= CDI).

Diferenças contra o institucional (quant/fundos/ideias_juros_fx.py, juro_real):
  - institucional: NTN-B (principal ou cupom) escolhida TODO DIA (rolava de título), 5 anos de duration por PL financiados no CDI (DAP),
    marcada pela taxa de venda, custo 3 bps de taxa x duration.
  - PF: só Tesouro IPCA+ (principal: sem cupom semestral tributado); só títulos À VENDA no dia (vitrine do Tesouro Direto = houve venda
    liquidada nos últimos 5 pregões, arquivo de vendas do Tesouro Transparente); compra-e-segura o MESMO título até o sinal de saída;
    compra no PU de COMPRA e é marcado/vendido no PU de VENDA (spread real do arquivo, ~0,12 pp de taxa desde 2017 = 1–1,8% do PU num
    título de 15 anos); quantidade em múltiplos de 0,01 título (mínimo R$ 30); custódia B3 provisionada diariamente; IR regressivo real
    no resgate (22,5% até 180 dias ... 15% acima de 720 dias), com a custódia deduzida da base.
  - tamanho: dur x alavancagem anos de duration por PL, LIMITADO a 100% do capital (Tesouro Direto não aceita alavancagem; DAP é grande
    demais: 100.000 x R$ 0,00025 x IPCA acumulado ~ R$ 180 mil de face, ~R$ 90 mil de PU num DAP de 10 anos -> 1 contrato = 2–5x o PL).

Premissas corrigidas (com fonte):
  - custódia B3 no Tesouro Direto: 0,30% a.a. até 2019, 0,25% em 2020–2021, 0,20% a.a. desde 01/01/2022; isenção do Tesouro Selic até
    R$ 10 mil (desde ago/2020) — não se aplica ao IPCA+.
    https://www.gov.br/tesouronacional/pt-br/noticias/taxa-de-custodia-do-tesouro-direto-cai-para-0-20
    https://blog.toroinvestimentos.com.br/renda-fixa/taxa-semestral-tesouro-direto/
    Desde 31/12/2024 a custódia é cobrada só nos resgates/vencimentos (mesmo valor, provisionada diariamente):
    https://agenciabrasil.ebc.com.br/economia/noticia/2024-12/taxa-de-custodia-do-tesouro-direto-deixa-de-ser-cobrada-semestralmente
  - taxa de agente/corretora: zero (todas as grandes corretoras zeraram; antes de ~2015 havia corretoras com 0–0,5% a.a. — ignorado).
  - IR regressivo de renda fixa (Lei 11.033/2004 art. 1º): 22,5% / 20% / 17,5% / 15% (até 180, 360, 720 dias, acima). Passado ao motor
    pelo truque de classes: P&L marcado a mercado em "isento" e, no dia da venda, o ganho realizado G x (alíquota/15%) em "renda_fixa"
    contra -G x (alíquota/15%) em "isento" (soma diária intacta, imposto = alíquota x G no ano da venda). Posição aberta no fim é
    tributada como se vendida no último dia (conservador). IOF regressivo (< 30 dias) não ocorre (nenhum negócio < 30 dias).
  - disponibilidade (sobrevivência): o arquivo de preços do Tesouro traz PU de compra até para título que saiu da vitrine (ex.: IPCA+
    2035 e 2045 deixaram de ser vendidos em fev/2025) — por isso a vitrine vem do arquivo de VENDAS (pf/dados/rev_tesouro/vendas_td.csv,
    https://www.tesourotransparente.gov.br/ckan/dataset/vendas-do-tesouro-direto).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _util as U  # noqa: E402

C, pf = U.C, U.pf
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

NOME = "Tesouro IPCA+ longo quando o juro real passa de 6,5% (Tesouro Direto)"
TESE = ("IPCA+6,5% numa NTN-B de 10 anos é prêmio fiscal/político extremo (o neutro do Focus é 4,3–6,3%): compro Tesouro IPCA+ ~15 anos "
        "no Tesouro Direto pagando o PU de compra e seguro até o juro real voltar a < 5,5% (ganhos de 2008, 2013, 2015–17, 2022–23 vieram "
        "de choques fiscais/políticos que se desfizeram em 6–24 meses). O resto fica em Tesouro Selic.")
BENCHMARK = "CDI"
INICIO, CORTE = "2010-01-01", "2021-01-01"
REGIME = "nenhum"          # tese de valor com prazo longo: stop por queda vende no pior momento e paga 1–2% de spread do TD na volta
CUSTO_TROCA = .015
PARAMS = {"entra": 6.5, "banda": 1.0, "dur": 5.0, "tipo": "a"}
GRADE = {"entra": [6.0, 6.5, 7.0], "banda": [0.5, 1.0]}
VIZINHANCA = {"entra": (6.2, 6.8), "banda": (0.7, 1.3), "dur": (4.0, 6.0)}
RANKING = ["JF1 Juro real de valor (NTN-B longa)"]
INSTRUMENTOS = {"Tesouro IPCA+ (NTN-B principal) ~15 anos": {"onde": "Tesouro Direto (qualquer corretora; B3)", "lote": "0,01 título, mín. R$ 30",
                                                            "custo": "PU compra - PU venda (0,12 pp de taxa desde 2017) + custódia B3 0,20% a.a."},
                "caixa": {"onde": "Tesouro Selic / CDB liquidez diária 100% CDI", "custo": "0 (Selic isento de custódia até R$ 10 mil)"}}
APLICAVEL = True
MOTIVO = ("Rota 100% varejo: Tesouro Direto vende NTN-B principal de 10–25 anos em frações de 0,01; o spread de compra/venda e a "
          "custódia estão no arquivo oficial. Só não dá para alavancar (o institucional usava DAP, 1 contrato ~R$ 90 mil).")
ALAVANCAGENS = [1, 1.5, 2]
MOTIVO_ALAV = ("'Alavancagem' = mais duration por PL (dur x L), sempre com o título comprado à vista e no máximo 100% do capital: "
               "1x = 5 anos de duration (~40% do PL num IPCA+ de 15 anos), 1,5x ~ 60%, 2x ~ 80%. Acima disso exigiria DAP (grande demais) — "
               "não existe empréstimo para comprar Tesouro.")
VARIANTES = {"percentil 80 (5 anos)": {"tipo": "p", "entra": 80, "banda": 30},
             "percentil 90 (5 anos)": {"tipo": "p", "entra": 90, "banda": 40},
             "entra 7%": {"entra": 7.0},
             "sem custos TD (spread e custódia zero)": {"custo_mult": 0},
             "100% do capital (dur 15)": {"dur": 15.0}}

TIPOS = {"Tesouro IPCA+": "P", "Tesouro IPCA+ com Juros Semestrais": "C"}
DADOS = U.CACHE / "rev_tesouro"


# =============================================================================== dados
def carrega():
    """td: preços/taxas diários (formato longo, coluna data) das NTN-B do Tesouro Direto; vendas: volume vendido por título e data de
    liquidação (para saber o que estava na vitrine)."""
    t = pd.read_csv(U.QD / "tesouro_direto.csv", sep=";", decimal=",")
    t = t[t["Tipo Titulo"].isin(TIPOS)]
    td = pd.DataFrame({"data": pd.to_datetime(t["Data Base"], dayfirst=True), "tipo": t["Tipo Titulo"].map(TIPOS).values,
                       "venc": pd.to_datetime(t["Data Vencimento"], dayfirst=True), "tx_c": t["Taxa Compra Manha"].values,
                       "tx_v": t["Taxa Venda Manha"].values, "pu_c": t["PU Compra Manha"].values, "pu_v": t["PU Venda Manha"].values})
    v = pd.read_csv(DADOS / "vendas_td.csv", sep=";", decimal=",")
    v = v[v["Tipo Titulo"].eq("Tesouro IPCA+")]
    vd = pd.DataFrame({"data": pd.to_datetime(v["Data de Liquidacao da Venda"], dayfirst=True),
                       "venc": pd.to_datetime(v["Vencimento do Titulo"], dayfirst=True), "qtd": v["Quantidade"].values})
    return {"td": td.sort_values("data").reset_index(drop=True), "vendas": vd.sort_values("data").reset_index(drop=True)}


_CACHE = {}


def _painel(d):
    """Pivôs por título no calendário B3 + curva real de 10 anos (só com o que existe em d). Cache pela última data/tamanho de d."""
    td, vd = d["td"], d["vendas"]
    ch = (len(td), td["data"].iloc[-1], len(vd), vd["data"].iloc[-1])
    if ch in _CACHE:
        return _CACHE[ch]
    td = td.assign(col=td.tipo + "_" + td.venc.dt.strftime("%Y-%m"))
    venc = td.groupby("col").venc.first()
    piv = lambda c: td.pivot_table(index="data", columns="col", values=c, aggfunc="last")
    YV0 = piv("tx_v") / 100
    T0 = pd.DataFrame((venc.reindex(YV0.columns).values[None, :] - YV0.index.values[:, None]) / np.timedelta64(1, "D") / 365.25,
                      index=YV0.index, columns=YV0.columns)
    # curva real de 10 anos (NTN-B principal + cupom, taxa de venda/resgate) — mesmo sinal do institucional
    Y, Tm = YV0.where(T0 > .2).to_numpy(), T0.to_numpy()
    y10 = np.full(len(Y), np.nan)
    for i in range(len(Y)):
        ok = ~np.isnan(Y[i]) & (Tm[i] > .2)
        if ok.sum() >= 2:
            o = np.argsort(Tm[i][ok])
            x, yv = Tm[i][ok][o], Y[i][ok][o]
            if x[0] <= 16 and x[-1] >= 6:
                y10[i] = np.interp(10, x, yv)
    y10 = pd.Series(y10, index=YV0.index)
    re_ = lambda s: s.reindex(C.DIAS.union(s.index)).ffill(limit=3).reindex(C.DIAS)
    P = [c for c in YV0.columns if c.startswith("P_")]
    PUC = piv("pu_c")[P].reindex(C.DIAS)
    PUV = piv("pu_v")[P].reindex(C.DIAS)
    TXC = piv("tx_c")[P].reindex(C.DIAS)
    # vitrine: título com venda liquidada nos últimos 5 pregões (liquidação = compra de t-1); arquivo de vendas só tem IPCA+ principal
    vd = vd.assign(col="P_" + vd.venc.dt.strftime("%Y-%m"))
    vend = vd.pivot_table(index="data", columns="col", values="qtd", aggfunc="sum").reindex(columns=P)
    vend = vend.reindex(C.DIAS.union(vend.index)).fillna(0).rolling(5, min_periods=1).sum().reindex(C.DIAS)
    ult_v = vd["data"].iloc[-1]
    vitr = (vend > 0) & (C.DIAS <= ult_v)[:, None]
    T = pd.DataFrame((venc.reindex(P).values[None, :] - C.DIAS.values[:, None]) / np.timedelta64(1, "D") / 365.25, index=C.DIAS, columns=P)
    ok = PUV.notna() & PUC.notna() & (T > 0)
    Dm = T / (1 + TXC / 100)                                             # duration modificada de zero-cupom, na taxa de compra
    out = {"y10": re_(y10), "y10_0": y10, "PUC": PUC.where(ok), "PUV": PUV.ffill(limit=3).where(T > 0), "T": T, "Dm": Dm,
           "vitr": vitr & ok, "txv": (piv("tx_v")[P].reindex(C.DIAS))}
    _CACHE.clear()
    _CACHE[ch] = out
    return out


def _percentil(y0, n=1250):
    return y0.rolling(n, min_periods=500).apply(lambda x: (x[-1] >= x).mean(), raw=True)


def _sinal(p, entra, banda, tipo):
    if tipo == "p":
        k = ("pct", len(p["y10_0"]), p["y10_0"].index[-1])
        if k not in _CACHE:
            _CACHE[k] = _percentil(p["y10_0"]).reindex(C.DIAS.union(p["y10_0"].index)).ffill(limit=3).reindex(C.DIAS) * 100
        s = _CACHE[k]
        ent, sai = s > entra, s < entra - banda
    else:
        s = p["y10"] * 100
        ent, sai = s > entra, s < entra - banda
    st = pd.Series(np.nan, index=C.DIAS)
    st[sai.fillna(False).to_numpy()] = 0.0
    st[ent.fillna(False).to_numpy()] = 1.0
    return st.ffill().fillna(0)


def _custodia(dia):
    return .0030 if dia.year <= 2019 else (.0025 if dia.year <= 2021 else .0020)


def _aliq(dias_corridos):
    return .225 if dias_corridos <= 180 else .20 if dias_corridos <= 360 else .175 if dias_corridos <= 720 else .15


# =============================================================================== motor
def _simula(d, capital=20000, custo_mult=1, lag=0, alavancagem=1, entra=6.5, banda=1.0, dur=5.0, tipo="a"):
    """Simula o livro em R$ com patrimônio que cresce (caixa no CDI). Devolve dict com séries em fração do patrimônio de t-1."""
    p = _painel(d)
    st = _sinal(p, entra, banda, tipo).to_numpy()
    dias = C.DIAS
    cdi = C.CDI.reindex(dias).fillna(0).to_numpy()
    PUC, PUV, T, Dm, VIT = (p[k].to_numpy() for k in ("PUC", "PUV", "T", "Dm", "vitr"))
    cols = p["PUC"].columns
    n = len(dias)
    i0 = 0                          # começa em 2008 (como o institucional) para herdar a posição aberta antes do INICIO
    k0 = 1 + lag
    ex = np.zeros(n)               # excesso diário sobre o CDI (fração do patrimônio de t-1)
    mtm = np.zeros(n)              # P&L do título (R$/patrimônio) — classe "isento" antes do ajuste de IR
    rf_real = np.zeros(n)          # ganho realizado x (alíquota/15%) — classe renda_fixa
    perd = np.zeros(n)             # CDI perdido sobre o valor aplicado
    W = np.zeros((n, len(cols)))   # peso executado no fechamento de t (fração do patrimônio)
    nav = float(capital)
    pos = None
    trades = []
    for t in range(i0, n):
        navp = nav
        pnl = 0.0
        if pos is not None:                                              # marcação do dia
            j = pos["j"]
            pv = PUV[t, j] if not np.isnan(PUV[t, j]) else pos["pv"]
            dv = pos["u"] * (pv - pos["pv"])
            cust = pos["u"] * pos["pv"] * _custodia(dias[t]) / 252 * custo_mult
            pos["cust"] += cust
            pnl += dv - cust
            perd[t] = pos["u"] * pos["pv"] * cdi[t] / navp
            pos["pv"] = pv
            pos["contrib"] += (dv - cust) / navp - perd[t]
            vence = T[t, j] < 5 / 365
            if (t - k0 >= 0 and st[t - k0] == 0) or vence or t == n - 1:    # venda no PU de venda (já marcado)
                g = pos["u"] * pv - pos["custo"] - pos["cust"]
                al = _aliq((dias[t] - pos["d0"]).days)
                rf_real[t] += g * al / .15 / navp
                trades.append({"ativo": "Tesouro IPCA+ " + cols[j][2:6], "lado": 1, "entrada": pos["d0"], "saida": dias[t],
                               "dias": int(t - pos["t0"]), "retorno_%": (pos["u"] * pv - pos["cust"]) / pos["custo"] * 100 - 100,
                               "contrib_pp": pos["contrib"] * 100, "taxa_compra_%": pos["tx0"], "juro_real_10a_entrada_%": pos["y0"],
                               "juro_real_10a_saida_%": p["y10"].iloc[t] * 100, "aliquota_IR_%": al * 100,
                               "aberta": t == n - 1 and st[t - k0] == 1 and not vence})
                pos = None
        if pos is None and t - k0 >= 0 and st[t - k0] == 1 and t < n - 1:   # compra no PU de compra, só título na vitrine
            ok = VIT[t] & (T[t] >= 8) & (T[t] <= 30)
            if ok.any():
                j = int(np.nanargmin(np.where(ok, np.abs(T[t] - 15), np.inf)))
                w = min(1.0, dur * alavancagem / Dm[t, j])
                puc = PUV[t, j] + (PUC[t, j] - PUV[t, j]) * custo_mult
                u = np.floor(w * nav / puc * 100) / 100
                if u * puc >= 30:
                    pnl -= u * (puc - PUV[t, j])
                    pos = {"j": j, "u": u, "pv": PUV[t, j], "custo": u * puc, "cust": 0.0, "d0": dias[t], "t0": t,
                           "tx0": p["txv"].iloc[t, j], "y0": p["y10"].iloc[t] * 100, "contrib": -u * (puc - PUV[t, j]) / navp}
        if pos is not None:
            W[t, pos["j"]] = pos["u"] * pos["pv"] / max(nav, 1)
        mtm[t] = pnl / navp
        ex[t] = mtm[t] - perd[t]
        nav = navp * (1 + cdi[t] + ex[t])
    idx = dias
    return {"ex": pd.Series(ex, idx), "mtm": pd.Series(mtm, idx), "rf": pd.Series(rf_real, idx), "perd": pd.Series(perd, idx),
            "W": pd.DataFrame(W, idx, cols), "trades": pd.DataFrame(trades), "p": p}


def excesso(d, capital=20000, custo_mult=1, lag=0, regime=REGIME, alavancagem=1, **params):
    s = _simula(d, capital, custo_mult, lag, alavancagem, **{**PARAMS, **params})
    return C.aplica_regime(s["ex"], regime, CUSTO_TROCA * custo_mult)


def classes_ir(d, capital=20000, **params):
    """MTM em 'isento'; no dia da venda, ganho realizado x alíquota/15% em 'renda_fixa' contra o mesmo valor negativo em 'isento'."""
    s = _simula(d, capital, **{**PARAMS, **params})
    return {"isento": (s["mtm"] - s["rf"]) * capital, "renda_fixa": s["rf"] * capital, "_cdi_perdido": s["perd"] * capital}


def posicoes(d, capital=20000, **params):
    s = _simula(d, capital, **{**PARAMS, **params})
    p = s["p"]
    R = (p["PUV"] / p["PUV"].shift(1) - 1).sub(C.CDI.reindex(C.DIAS), axis=0).fillna(0)
    return s["W"].shift(-1).fillna(0), R


def negocios(d, capital=20000, **params):
    s = _simula(d, capital, **{**PARAMS, **params})
    return s["trades"]
