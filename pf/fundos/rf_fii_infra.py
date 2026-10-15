"""
FI-Infra listados e FIIs de papel com desconto ao valor patrimonial — "comprar no pânico, vender no fechamento do desconto".

Tese de mesa: o FI-Infra listado (JURO11, KDIF11, CPTI11, BDIF11, IFRA11...) é uma carteira de debêntures incentivadas MARCADA A
MERCADO todo dia (taxas ANBIMA); o cotista é quase todo pessoa física. Quando o varejo entra em pânico (alta de juro real em 2024,
ameaça da MP 1.303 de tributar isentos em 2025, Selic a 15%), a cota negocia a 0,75–0,90 do valor patrimonial — um desconto que não é
perda escondida (o VP já está a mercado), é fluxo. Compro os mais descontados e vendo quando a cota volta para perto do VP. Para pessoa
física o FI-Infra é isento TANTO no rendimento QUANTO no ganho de capital (Lei 12.431, art. 3º) — o institucional tributado não
arbitra esse desconto. FIIs de papel (CRI) entram como variante: o rendimento é isento, mas o ganho de capital paga 20% e o VP é
marcado pelo gestor (atrasa a perda: Hectare, Devant) — a pesquisa anterior (C9) perdeu dinheiro com eles.

Implementação:
  - preço de fechamento do COTAHIST (codbdi 14 = fundos listados; 12 = FII); proventos: FI-Infra pelo Yahoo (data-ex), FII pelo
    informe mensal da CVM (DY x VP, data-ex no 1º pregão do mês seguinte, conferido com KNCR11 na pesquisa C9);
  - VP: FI-Infra = cota diária do informe diário da CVM (CNPJ achado pelo nome e conferido pelo nível; disponível em t+1 -> uso a de
    t-1, descontado o provento que fica ex no dia); FII = VP do informe mensal a partir da DATA DE ENTREGA;
  - desdobramento/grupamento: dia com |retorno| > 40% vira retorno zero (cota e VP mudam de escala juntas; nenhum FI-Infra/FII de
    papel líquido teve queda real de 40% num dia nesta amostra);
  - KDIF11 só a partir de ago/2024 e NUIF11 só a partir de jun/2026 (o Yahoo não tem os proventos de antes — a cota caía sem provento);
  - entra nos n mais descontados com P/VP <= thr e giro >= R$ 300 mil/dia (21d); sai com P/VP >= saida (0,98); 1/n do capital;
  - custo: emolumentos 0,03% + meio spread do fechamento (oferta de compra/venda do COTAHIST, mediana de 21d, teto 1%);
  - IR: FI-Infra "isento" (tudo); FII: provento "isento", ganho de capital "fii_ganho" a 20% (ALIQUOTAS).
Dados: 2021-01 (cota diária CVM) a 2026-10; corte OOS 2024-01-01 (dados curtos: 3 anos de IS).
"""
import numpy as np
import pandas as pd

import _rf_comum as K

NOME = "FI-Infra/FII de papel com desconto ao VP (pânico de varejo)"
TESE = ("Compro FI-Infra listado (isento total para PF) quando a cota negocia com desconto grande ao VP marcado a mercado e vendo quando "
        "o desconto fecha; FII de papel como variante")
BENCHMARK = "CDI"
INICIO, CORTE = "2021-07-01", "2024-01-01"
REGIME = "nenhum"
CUSTO_TROCA = 0.0
PARAMS = {"universo": "infra", "thr": 0.95, "n": 3}           # escolhidos no IS (maior IR 2021-07 a 2023)
GRADE = {"universo": ["infra", "ambos"], "thr": [0.90, 0.95], "n": [3, 6]}
VIZINHANCA = {"thr": (0.90, 0.97), "n": (2, 5)}
SAIDA_PVP = 0.98
CLASSE_IR = "isento"
ALIQUOTAS = {"fii_ganho": .20}
EMOL, SPREAD_MAX = .0003, .01
INFRA = ["JURO11", "KDIF11", "CPTI11", "BDIF11", "CDII11", "BODB11", "IFRA11", "BIDB11", "SNID11", "IFRI11", "NUIF11", "KNDI11"]
INICIO_TK = {"KDIF11": "2024-08-01", "NUIF11": "2026-06-01"}
INSTRUMENTOS = [{"onde": "qualquer corretora B3 (Clear/Rico/XP/Inter/Nubank, corretagem zero)", "ticker": "JURO11, KDIF11, CPTI11, BDIF11, IFRA11, BIDB11, "
                 "BODB11, CDII11, SNID11, IFRI11 (FI-Infra); FIIs de papel (KNCR11, MXRF11...) na variante", "lote": "1 cota (~R$ 8–130)",
                 "custo": "emolumentos 0,03% + meio spread (0,1–0,5%)"}]
APLICAVEL = True
MOTIVO = "Cotas de R$ 8–130 na B3 com corretagem zero; 3 fundos de ~R$ 6,7 mil com R$ 20 mil."
VARIANTES = {"FII de papel junto (ambos, 0,90, n 6)": {"universo": "ambos", "thr": 0.90, "n": 6}, "só FI-Infra, 0,90, n 6": {"thr": 0.90, "n": 6}}
ALAVANCAGENS = [1]
MOTIVO_ALAV = "Cotas de fundos listados não servem de garantia para termo no varejo de forma prática; sem alavancagem."


def carrega():
    return {"cot": K.ler("cotahist_fundos.parquet"), "vp_infra": K.ler("infra_vl_quota.parquet").reset_index(),
            "div_infra": K.ler("infra_dividendos.parquet"), "fii": K.ler("cvm_fii_mensal.parquet").rename(columns={"Data_Referencia": "data"})}


def _papel_tickers(fii):
    """FIIs que algum informe já declarou como de papel (Títulos e Val. Mob.); a elegibilidade em cada dia usa só informes ENTREGUES."""
    f = fii[fii.Codigo_ISIN.notna() & fii.Data_Entrega.notna()].copy()
    f["tk"] = f.Codigo_ISIN.str[2:6] + "11"
    f["papel"] = (f.Segmento_Atuacao.astype(str).str.contains("Títulos e Val", regex=False)
                  | f.Mandato.astype(str).str.contains("Títulos e Valores", regex=False))
    return f, sorted(f[f.papel].tk.unique())


def painel(d):
    def f():
        c = d["cot"]
        fii, papel = _papel_tickers(d["fii"])
        c = c[(c.codbdi.eq("14") & c.ticker.isin(INFRA)) | (c.codbdi.eq("12") & c.ticker.isin(papel))]
        px = c.pivot_table(index="data", columns="ticker", values="fech", aggfunc="last").reindex(K.DIAS)
        vol = c.pivot_table(index="data", columns="ticker", values="volume", aggfunc="last").reindex(K.DIAS).fillna(0)
        bid = c.pivot_table(index="data", columns="ticker", values="oferta_compra", aggfunc="last").reindex(K.DIAS)
        ask = c.pivot_table(index="data", columns="ticker", values="oferta_venda", aggfunc="last").reindex(K.DIAS)
        cols = px.columns
        # proventos
        dv = pd.DataFrame(0.0, index=K.DIAS, columns=cols)
        di = d["div_infra"]
        di = di[di.ticker.isin(cols)]
        for (t, dt), v in di.groupby(["ticker", "data"]).dividendo.sum().items():
            j = K.DIAS.searchsorted(dt)
            if j < len(K.DIAS):
                dv.iat[j, cols.get_loc(t)] += v
        fii = fii[fii.tk.isin(cols)].copy()
        fii["div"] = fii.Percentual_Dividend_Yield_Mes.clip(0, .05) * fii.Valor_Patrimonial_Cotas
        prim = pd.Series(K.DIAS, index=K.DIAS).groupby(K.DIAS.to_period("M")).first()
        fii["ex"] = (fii.data.dt.to_period("M") + 1).map(prim)            # data = mês de referência; provento ex no 1º pregão de M+1
        dvf = fii.dropna(subset=["ex"]).pivot_table(index="ex", columns="tk", values="div", aggfunc="sum").reindex(index=K.DIAS, columns=cols).fillna(0)
        dv = dv + dvf
        pf_ = px.ffill(limit=10)
        r = (pf_ + dv) / pf_.shift(1) - 1
        r = r.where(px.notna() & pf_.shift(1).notna())
        rdiv = (dv / pf_.shift(1)).where(r.notna())
        split = r.abs() > .4
        r, rdiv = r.mask(split, 0.0), rdiv.mask(split, 0.0)
        # VP
        vi = d["vp_infra"].set_index("data")
        vi = vi.reindex(vi.index.union(K.DIAS)).ffill(limit=5).reindex(K.DIAS).shift(1)              # cota de t-1 (publicada em t)
        fii["disp"] = fii.Data_Entrega
        vpf = fii.sort_values("disp").pivot_table(index="disp", columns="tk", values="Valor_Patrimonial_Cotas", aggfunc="last")
        vpf = vpf.reindex(vpf.index.union(K.DIAS)).ffill(limit=60).reindex(K.DIAS)
        VP = pd.concat([vi.reindex(columns=[k for k in cols if k in INFRA]), vpf.reindex(columns=[k for k in cols if k not in INFRA])], axis=1)[cols]
        VP = VP - dv.where(pd.DataFrame({k: k in INFRA for k in cols}, index=K.DIAS), 0.0)                # ex-provento no dia
        pvp = pf_ / VP
        # escala trocada (desdobramento): VP e preço em escalas diferentes por alguns dias -> fora
        pvp = pvp.where((pvp > .4) & (pvp < 1.6))
        flag = fii.sort_values("disp").pivot_table(index="disp", columns="tk", values="papel", aggfunc="last").astype(float)
        flag = flag.reindex(flag.index.union(K.DIAS)).ffill().reindex(index=K.DIAS, columns=cols)
        ok = pd.DataFrame(True, index=K.DIAS, columns=cols)
        ok.loc[:, [k for k in cols if k not in INFRA]] = (flag[[k for k in cols if k not in INFRA]] == 1)
        for t, ini in INICIO_TK.items():
            if t in cols:
                ok.loc[K.DIAS < pd.Timestamp(ini), t] = False
        hs = ((ask - bid) / (ask + bid)).where((bid > 0) & (ask > bid))
        meio = hs.rolling(21, min_periods=5).median().shift(1).clip(upper=SPREAD_MAX).fillna(.003)
        custo = EMOL + meio
        obs = px.notna() & (vol > 0)
        vivo = (obs.cumsum() > 0) & pf_.notna()
        return dict(px=pf_, r=r.fillna(0), rdiv=rdiv.fillna(0), pvp=pvp, vol21=vol.rolling(21, min_periods=10).mean(), custo=custo,
                    obs=obs, vivo=vivo, ok=ok, infra=pd.Series({k: k in INFRA for k in cols}))
    return K.memo("fii_painel", d["cot"], f)


def _alvo(d, universo, thr, n):
    p = painel(d)
    cols = p["px"].columns
    uni = p["infra"] if universo == "infra" else pd.Series(True, index=cols)
    pv = p["pvp"].where(p["ok"] & (p["vol21"] >= 3e5) & p["obs"])
    pv = pv.loc[:, uni.reindex(cols).fillna(False).to_numpy()]
    pvl = p["pvp"].ffill(limit=5)[pv.columns].to_numpy()
    pvv = pv.to_numpy()
    A = np.zeros(pv.shape)
    held = set()
    for t in range(len(K.DIAS)):
        held = {k for k in held if not (np.isfinite(pvl[t, k]) and pvl[t, k] >= SAIDA_PVP)}
        if len(held) < n:
            cand = np.flatnonzero(np.isfinite(pvv[t]) & (pvv[t] <= thr))
            for k in cand[np.argsort(pvv[t, cand])]:
                if len(held) >= n:
                    break
                held.add(k)
        for k in held:
            A[t, k] = 1 / n
    A[K.DIAS < pd.Timestamp(INICIO)] = 0.0                                   # nada de posição herdada de antes do início
    return pd.DataFrame(A, index=K.DIAS, columns=pv.columns)


def _livro(d, capital=20000, custo_mult=1, lag=0, universo=PARAMS["universo"], thr=PARAMS["thr"], n=PARAMS["n"]):
    p = painel(d)
    A = _alvo(d, universo, thr, n)
    cols = A.columns
    return K.livro(A, p["r"][cols], capital, lag, custo_ent=p["custo"][cols], custo_sai=p["custo"][cols], custo_mult=custo_mult,
                   lote=p["px"][cols], negocia=p["obs"][cols], vivo=p["vivo"][cols], R2=p["rdiv"][cols])


def excesso(d, capital=20000, custo_mult=1, lag=0, regime=REGIME, alavancagem=1, **params):
    e = _livro(d, capital, custo_mult, lag, **{**PARAMS, **params})["e"]
    return K.C.aplica_regime(e, regime, CUSTO_TROCA * custo_mult)


def classes_ir(d, capital=20000, **params):
    L = _livro(d, capital, **{**PARAMS, **params})
    inf = painel(d)["infra"].reindex(L["pnl"].columns).fillna(False).to_numpy()
    isento = L["pnl"].loc[:, inf].sum(axis=1) + L["pnl2"].loc[:, ~inf].sum(axis=1)
    ganho_fii = L["pnl"].loc[:, ~inf].sum(axis=1) - L["pnl2"].loc[:, ~inf].sum(axis=1)
    return {"isento": isento * capital, "fii_ganho": ganho_fii * capital, "_cdi_perdido": L["perd"].sum(axis=1) * capital}


def posicoes(d, **params):
    p_ = {**PARAMS, **params}
    p = painel(d)
    A = _alvo(d, p_["universo"], p_["thr"], p_["n"])
    return A, p["r"][A.columns].sub(K.CDI, axis=0)


def negocios(d, capital=20000, **params):
    p = painel(d)
    ng = _livro(d, capital, **{**PARAMS, **params})["negocios"].copy()
    if len(ng):
        pv = p["pvp"].ffill(limit=5)
        ng["pvp_entrada"] = [pv.shift(1).at[i, a] for a, i in zip(ng.ativo, ng.entrada)]
        ng["pvp_saida"] = [pv.at[f, a] for a, f in zip(ng.ativo, ng.saida)]
    return ng
