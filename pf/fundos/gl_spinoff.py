"""
Spin-offs dos EUA depois da venda forçada, na IBKR com só o necessário fora; hedge de bolsa E de dólar com IVVB11 vendido na B3.

Tese de mesa: quando uma empresa separa uma divisão, os acionistas recebem ações de uma empresa menor, fora do índice e do mandato
(fundo de S&P recebe uma small cap, gestor de dividendos recebe uma empresa que não paga). Nas primeiras semanas eles VENDEM sem olhar
preço. Compro `espera` pregões depois do 1º preço (passou a venda forçada), seguro `dias` pregões, 5% do PL por nome (frações na IBKR).
Hedge: IVVB11 vendido (aluguel na B3) no tamanho da carteira — tira o beta do S&P e também o dólar (o IVVB11 é S&P em R$), então o que
sobra é o spin-off contra o S&P. Não tem BDR para quase nenhum spin-off: a perna comprada tem de ficar na IBKR.

Eventos: Form 10-12B na SEC (data de arquivamento; ponto no tempo) + ticker dos Forms 3/4 + preço do Yahoo (exportado de
quant/fundos/ideias_global.spin_eventos). Viés de sobrevivência corrigido como na auditoria (G3): spin-offs que negociaram (insiders
arquivando > 90 dias) mas sumiram do Yahoo entram com trajetória sintética de -30% em 166 pregões a partir do 1º Form 3/4.
Custos: IBKR US$ 0,0035/ação (mín. US$ 0,35) + 0,2% de meio spread (small caps) por lado; conta na IBKR = valor da carteira x 1,1
(conta à vista não precisa de margem; folga de 10% — premissa nossa, o pf.custo_conta_exterior usa 1,5 por padrão) perdendo CDI,
remessa 1,1% + 0,5% ida e 0,38% + 0,5% volta. IVVB11 vendido: aluguel 1% a.a. + 0,5% por contrato aberto, dinheiro da venda rende 95% CDI.
IR: exterior 15% sobre o ganho anual em R$ (Lei 14.754/2023, inclui variação cambial); IVVB11 vendido 15% (etf_b3).
"""
import numpy as np
import pandas as pd

import gl_comum as G
import pf as P

NOME = "Spin-offs dos EUA (IBKR) com hedge em IVVB11 vendido"
TESE = "Compro o spin-off depois da venda forçada dos indexados (IBKR, 5% por nome) e vendo IVVB11 na B3 contra (bolsa + dólar)"
BENCHMARK = "CDI"
INICIO, CORTE = "2012-01-01", "2021-01-01"
REGIME = "nenhum"
CUSTO_TROCA = .002
PARAMS = {"espera": 40, "dias": 252, "hedge": "nenhum"}   # maior IR dentro da amostra (todas negativas no IS)
GRADE = {"espera": [20, 40], "dias": [126, 252], "hedge": ["nenhum", "ivvb11"]}
VIZINHANCA = {"espera": (25, 60), "dias": (180, 300)}
PESO, SPREAD, PERDA_SUMIU, FOLGA = .05, .002, -.30, 1.1
INSTRUMENTOS = {"spin-offs": {"onde": "IBKR", "ticker": "~10-20 por ano", "lote": "fração", "custo": "US$ 0,0035/ação mín. 0,35 + 0,2%"},
                "IVVB11": {"onde": "B3 (aluguel)", "ticker": "IVVB11", "lote": 1, "custo": "1% a.a. + 0,5% por contrato"}}
APLICAVEL = True
MOTIVO = ("Com R$ 20 mil, 5% = R$ 1 mil (~US$ 200) por nome: comissão mínima de US$ 0,35 = 0,2% por lado, aceitável. "
          "Exige conta na IBKR (só com o valor da carteira) e aluguel de IVVB11 na B3.")
ALAVANCAGENS = [1]
MOTIVO_ALAV = "A carteira usa 20-60% do PL; alavancar small caps na IBKR (Reg T) com conta pequena não compensa os juros de margem."


def carrega():
    b = G.ler("b3_etf_bdr.parquet")
    return {"ev": pd.read_csv(G.DADOS / "spin_eventos.csv", parse_dates=["d10"]),
            "sumiu": pd.read_csv(G.DADOS / "spin_sem_preco.csv", parse_dates=["d0", "d1", "d10"]),
            "px": G.ler("spin_precos.parquet").astype(float), "ivvb": b[b.ticker == "IVVB11"],
            "spy": G.ler("us_etf_ajustado.parquet")[["SPY"]]}


def _eventos(d, espera):
    P_ = d["px"].copy()
    P_.index = pd.DatetimeIndex(P_.index).normalize()
    du = P_.index
    ev = []
    for t, d10 in zip(d["ev"].ticker, d["ev"].d10):
        if t not in P_:
            continue
        x = P_[t].dropna()
        x = x[x.index >= d10 - pd.Timedelta(days=30)]
        if len(x) > espera + 5 and x.index[0] <= d10 + pd.Timedelta(days=365) and P_[t].loc[:d10 - pd.Timedelta(days=30)].notna().sum() == 0:
            ev.append({"ticker": t, "data": x.index[espera]})
    k = np.log1p(PERDA_SUMIU) / 166
    sint = {}
    for t, d0 in zip(d["sumiu"].ticker, d["sumiu"].d0):                     # sumiu do Yahoo: -30% em 166 pregões (correção de sobrevivência)
        i0 = du.searchsorted(d0)
        n = min(300, len(du) - i0)
        if n > espera + 5:
            sint[t + "*"] = pd.Series(np.exp(k * np.arange(n)), index=du[i0:i0 + n])
            ev.append({"ticker": t + "*", "data": du[i0 + espera]})
    P_ = pd.concat([P_, pd.DataFrame(sint).reindex(du)], axis=1)
    return pd.DataFrame(ev).sort_values("data"), P_


def _simula(d, espera, dias, hedge, capital, custo_mult=1, lag=0):
    ev, Px = _eventos(d, espera)
    du = Px.index
    ptax = G.PTAX.reindex(du, method="ffill")
    cols = list(dict.fromkeys(ev.ticker))
    Pv = Px[cols].values
    T = len(du)
    pnl_usd = np.zeros((T, len(cols)))
    cus_usd = np.zeros((T, len(cols)))
    val_usd = np.zeros((T, len(cols)))
    neg = []
    ativos = []                                                  # (fim, j)
    for t, dt in zip(ev.ticker, ev.data):
        j = cols.index(t)
        e0 = du.searchsorted(dt) + 1 + lag                       # executa no fechamento seguinte à informação
        if e0 >= T or not (Pv[e0, j] > 0):
            continue
        ativos = [(f, jj) for f, jj in ativos if f > e0]
        if len(ativos) * PESO >= 1:                              # PL inteiro já alocado
            continue
        x = Pv[:, j]
        vivo = np.where(~np.isnan(x[e0:]))[0]
        fim = e0 + min(dias, vivo[-1] if len(vivo) else 0)
        fim = min(fim, T - 1)
        ult_ok = e0 + (vivo[vivo <= fim - e0][-1] if len(vivo) else 0)
        q = PESO * capital / ptax.iloc[e0] / x[e0]
        px = pd.Series(x[e0:ult_ok + 1]).ffill().values
        pnl_usd[e0 + 1:ult_ok + 1, j] += q * np.diff(px)
        val_usd[e0:ult_ok, j] += q * px[:-1]
        for k_, pr in ((e0, x[e0]), (ult_ok, px[-1])):
            cus_usd[k_, j] += (float(P.custo_ordem_ibkr_usd(q * pr, pr)) + SPREAD * q * pr) * custo_mult
        ativos.append((ult_ok, j))
        neg.append({"ativo": t, "lado": 1, "entrada": du[e0], "saida": du[ult_ok], "dias": ult_ok - e0, "retorno_%": (px[-1] / x[e0] - 1) * 100,
                    "j": j, "q": q})
    fx = ptax.values[:, None]
    pnl = pd.DataFrame(pnl_usd * fx - cus_usd * fx, index=du, columns=cols)       # R$ no calendário dos EUA
    pnl_br = pnl.apply(P.usd_para_br)
    val_br = pd.Series((val_usd * fx).sum(axis=1), index=du).reindex(G.DIAS, method="ffill").fillna(0)
    conta, _ = P.custo_conta_exterior(val_br, folga=FOLGA)
    conta = conta.where(val_br.rolling(30, min_periods=1).max() > 0, 0) * custo_mult
    hb3 = pd.Series(0.0, index=G.DIAS)
    hb3_cls = hb3.copy()
    if hedge == "ivvb11":
        b = d["ivvb"]
        piv = G.pivo(b, "fech", ["IVVB11"])
        spy = G.no_calendario(d["spy"]["SPY"]) * G.PTAX
        niv, ok = G.emenda(piv["IVVB11"], spy)
        hs = G.meio_spread(G.pivo(b, "oferta_compra", ["IVVB11"])["IVVB11"], G.pivo(b, "oferta_venda", ["IVVB11"])["IVVB11"], teto=.01).where(ok, .002)
        W = pd.DataFrame({"IVVB11": -val_br / capital})
        ex = G.executa(W, niv.to_frame("IVVB11"), capital, (hs + G.B3_EMOL).to_frame("IVVB11"), lag=lag, custo_mult=custo_mult,
                       aluguel_aa=.01)
        hb3 = (ex["pnl"] + ex["carrego"] - ex["custo"] - ex["aluguel"]).sum(axis=1)
        hb3_cls = G.pnl_classe(ex)
    return pnl_br, conta, hb3, hb3_cls, pd.DataFrame(neg), val_br


def excesso(d, capital=20000, custo_mult=1, lag=0, regime=REGIME, alavancagem=1, **params):
    p = {**PARAMS, **params}
    pnl, conta, hb3, _, _, _ = _simula(d, p["espera"], p["dias"], p["hedge"], capital, custo_mult, lag)
    e = (pnl.sum(axis=1) - conta + hb3) / capital
    return G.C.aplica_regime(e, regime, CUSTO_TROCA * custo_mult)


def classes_ir(d, capital=20000, **params):
    p = {**PARAMS, **params}
    pnl, conta, hb3, hb3_cls, _, val = _simula(d, p["espera"], p["dias"], p["hedge"], capital)
    # a conta lá fora: perda de CDI é custo de oportunidade (já sai do caixa); remessa e câmbio entram no ganho/perda do exterior
    cdi_perdido = (val * FOLGA).shift(1).fillna(0) * G.CDI.fillna(0)
    return {"exterior": pnl.sum(axis=1) - (conta - cdi_perdido), "etf_b3": hb3_cls}


def posicoes(d, capital=20000, **params):
    p = {**PARAMS, **params}
    pnl, conta, hb3, _, ng, val = _simula(d, p["espera"], p["dias"], p["hedge"], capital)
    W = pd.DataFrame(0.0, index=G.DIAS, columns=pnl.columns)
    for a, b_, t in zip(ng.entrada, ng.saida, ng.ativo):
        W.loc[(W.index >= a) & (W.index < b_), t] = PESO
    R = (pnl / (PESO * capital)).where(W.shift(1) > 0, 0).sub(G.CDI.fillna(0), axis=0)
    return W.shift(-1).fillna(0), R


def negocios(d, capital=20000, **params):
    p = {**PARAMS, **params}
    pnl, conta, hb3, _, ng, val = _simula(d, p["espera"], p["dias"], p["hedge"], capital)
    if ng.empty:
        return pd.DataFrame(columns=["ativo", "lado", "entrada", "saida", "dias", "retorno_%", "contrib_pp"])
    hed = hb3 / val.replace(0, np.nan)                             # resultado do hedge por R$ de carteira (rateado pelo valor)
    ng["contrib_pp"] = [(pnl[a].loc[e:s].sum() + (hed.loc[e:s].fillna(0) * PESO * capital).sum()) / capital * 100
                        for a, e, s in zip(ng.ativo, ng.entrada, ng.saida)]
    return ng.drop(columns=["j", "q"])
