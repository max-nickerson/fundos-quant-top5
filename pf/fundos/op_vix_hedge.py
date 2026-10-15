"""
Hedge de cauda de uma carteira de ações brasileiras de R$ 20–50 mil: trava de alta com call de VIX (IBKR) x collar / put de BOVA11 (B3).

Tese de mesa: a carteira típica de PF é Brasil comprado (isento até R$ 20 mil/mês). Nas quedas globais (2008, 2011, 2015, 2018, 2020)
o VIX dispara e o Ibovespa cai junto; uma trava de call de VIX (compro K1 ~ 20% acima do futuro, vendo K1+10) paga até US$ 1.000 por
contrato — ~R$ 5 mil, ~25% de uma carteira de R$ 20 mil — e custa US$ 30–80 por mês. O "collar barato" faz o hedge com o próprio
BOVA11: compro put 8% OTM e financio vendendo call 6% OTM (custo ~zero, abro mão da alta). Aqui o fundo é o OVERLAY: o excesso é só o
P&L do hedge (custo do seguro, positivo nas crises); o caderno mostra a carteira BOVA11 com e sem cada hedge (queda máxima, retorno).

Dados e modelo:
  - VIX: não há histórico gratuito de opções de VIX. Preço = Black-76 sobre o futuro VX do MESMO vencimento (Cboe, todos os vencimentos
    em pf/dados/micro_cme/vx.csv) com IV = VVIX (vol implícita de 30 dias das opções de VIX) x sorriso de calls OTM
    (IV(K) = VVIX x (1 + 0,4 x ln(K/F)); o sorriso de VIX é para cima — calls OTM são mais caras: premissa conservadora para o comprador).
    Compra no 1º pregão depois do vencimento anterior (t+1), segura até o vencimento (liquida pelo ajuste final = SOQ). Custo:
    US$ 0,65 de comissão + US$ 0,05 de meio spread (x100) por perna. A conta na IBKR guarda só o prêmio (pf.custo_conta_exterior).
  - Collar/put BOVA11: opções reais da B3 (bid/ask do fechamento, 2019+ com liquidez), 1 lote por R$ 12–15 mil de carteira.
Tamanho: cobertura = fração da carteira a proteger (25%): n travas de VIX = arredonda(capital x cobertura / pagamento máximo em R$);
lotes de BOVA11 = arredonda(capital x 4 x cobertura / (100 x S)) (cobertura 25% -> carteira inteira em lotes de BOVA11).
IR: exterior (VIX) / opcoes_b3 (BOVA) — declarado "exterior" (as duas são 15%).
"""
import numpy as np
import pandas as pd
from scipy.stats import norm

import op_base as O

C, P = O.C, O.P

NOME = "Hedge de cauda da carteira: call spread de VIX (IBKR) x collar/put de BOVA11"
TESE = "Overlay de proteção de uma carteira Brasil: trava de call de VIX comprada todo mês (modelo VVIX) ou collar/put de BOVA11"
BENCHMARK = "CDI"
INICIO, CORTE = "2010-03-01", "2021-01-01"
REGIME, CUSTO_TROCA = "nenhum", 0.0
CLASSE_IR = "exterior"
# maior IR no IS (0,42): put de BOVA11 só com IV abaixo da mediana; a trava de VIX fica na grade
PARAMS = {"hedge": "put", "gatilho": "vol_baixa", "cobertura": .25, "k1": 1.2, "largura": 10.0, "put_otm": .08, "call_otm": .06}
GRADE = {"hedge": ["vix_cs", "collar", "put"], "gatilho": ["sempre", "vol_baixa"]}
VIZINHANCA = {"cobertura": (.15, .4), "k1": (1.1, 1.4), "put_otm": (.05, .12), "call_otm": (.04, .10)}
CUSTO_PERNA_USD = .65 + .05 * 100
SORRISO = .4
INSTRUMENTOS = [{"onde": "IBKR (Cboe)", "ticker": "opções de VIX (US$ 100 x VIX), trava K1/K1+10", "lote": 1, "custo": "US$ 0,65 + ~US$ 5 por perna"},
                {"onde": "B3", "ticker": "puts/calls mensais de BOVA11", "lote": 100, "custo": "bid/ask do fechamento + 0,10%"}]
APLICAVEL = "como hedge (overlay): sim; como fundo de excesso: não (é custo de seguro)"
MOTIVO = ("1 trava 20/30 de VIX paga até US$ 1.000 (~R$ 5,4 mil) e custa US$ 30–80/mês: com R$ 20 mil, 1 contrato protege ~25% da "
          "carteira e custa 2–4% do capital por ano mesmo comprando só com vol baixa. Collar de BOVA11: 1 lote por R$ 12–15 mil.")
ALAVANCAGENS = [1]
MOTIVO_ALAV = "Hedge não se alavanca (mais cobertura = mais custo de seguro)."


def carrega():
    vx = pd.read_csv(O.AQUI.parent / "dados" / "micro_cme" / "vx.csv", parse_dates=["data", "venc"])
    y = O.B.yahoo_idx(("^VIX", "^VVIX"))
    d = O.carrega_b3(["BOVA"])
    d.update({"vx": vx[vx.data >= "2010-01-01"].reset_index(drop=True), "y": y[y.index >= "2008-01-01"]})
    return d


def b76_call(F, K, T, s):
    s, T = np.maximum(s, 1e-4), np.maximum(T, 1 / 252)
    d1 = (np.log(F / K) + s * s * T / 2) / (s * np.sqrt(T))
    return F * norm.cdf(d1) - K * norm.cdf(d1 - s * np.sqrt(T))


def _vix_cs(d, capital, p, lag, custo_mult):
    vx, y = d["vx"], d["y"]
    piv = vx.pivot_table(index="data", columns="venc", values="ajuste")
    idx = piv.index
    vv = y["^VVIX"].reindex(idx).ffill() / 100
    vix = y["^VIX"].reindex(idx).ffill()
    vix_med = vix.rolling(252, min_periods=120).median()
    ptax = P.PTAX.reindex(idx, method="ffill")
    vencs = sorted(v for v in piv.columns if v <= idx[-1] + pd.Timedelta(days=400))
    pnl = pd.Series(0.0, index=idx)
    premio = pd.Series(0.0, index=idx)
    neg = []
    for v0, v1 in zip(vencs[:-1], vencs[1:]):
        dd = idx[(idx > v0) & (idx < v1)]
        if len(dd) < 2 + lag:
            continue
        sinal = dd[lag]
        ent = dd[lag + 1] if len(dd) > lag + 1 else None
        if ent is None or v1 not in piv:
            continue
        if p["gatilho"] == "vol_baixa" and not vix.get(sinal, np.nan) < vix_med.get(sinal, np.nan):
            continue
        F0 = piv.at[sinal, v1]
        if not np.isfinite(F0) or not np.isfinite(vv.get(sinal, np.nan)):
            continue
        K1 = np.ceil(F0 * p["k1"])
        K2 = K1 + p["largura"]
        dias = idx[(idx >= ent) & (idx <= v1)]
        F = piv[v1].reindex(dias).ffill()
        T = pd.Series([max(O.du(t, v1), 0) / 252 for t in dias], index=dias)
        s = vv.reindex(dias).ffill()
        val = b76_call(F, K1, T, s * (1 + SORRISO * np.log(K1 / F))) - b76_call(F, K2, T, s * (1 + SORRISO * np.log(K2 / F)))
        fim = dias[-1] == v1 and np.isfinite(piv.at[v1, v1]) if v1 in piv.index else False
        if fim:
            val.iloc[-1] = max(piv.at[v1, v1] - K1, 0) - max(piv.at[v1, v1] - K2, 0)
        pag_max = p["largura"] * 100 * ptax.get(sinal, np.nan)
        n = int(round(capital * p["cobertura"] / pag_max)) if pag_max > 0 else 0
        if n < 1:
            continue
        v_usd = n * 100 * val
        x = v_usd.diff().fillna(0)
        x.iloc[0] -= n * 2 * CUSTO_PERNA_USD * custo_mult           # entrada (meio spread embutido no custo por perna)
        pnl = pnl.add(x, fill_value=0)
        premio = premio.add(v_usd.where(v_usd > 0, 0), fill_value=0)
        neg.append(dict(ativo="VIX_cs", lado=1, entrada=ent, saida=dias[-1], contratos=n, K=f"{K1:.0f}/{K2:.0f}", F0=F0,
                        custo_usd=float(v_usd.iloc[0]), pnl_usd=float(x.sum())))
    br = P.usd_para_br(pnl) * P.PTAX
    saldo = premio.reindex(O.DIAS, method="ffill").fillna(0) * P.PTAX
    conta, _ = P.custo_conta_exterior(saldo)
    tot = (br.fillna(0) - conta.where(saldo > 0, 0).fillna(0) * custo_mult).reindex(O.DIAS).fillna(0)
    for z in neg:
        z["pnl_rs"] = float(tot[(tot.index >= z["entrada"]) & (tot.index <= z["saida"])].sum())
        z["retorno_%"] = z["pnl_rs"] / capital * 100
    return {"VIX": tot}, neg


def _bova(d, capital, p, lag, custo_mult):
    c = O.ciclos(d, "BOVA")
    pnl = pd.Series(0.0, index=O.DIAS)
    neg = []
    for _, z in c.iterrows():
        if p["gatilho"] == "vol_baixa" and not (z.iv == z.iv and z.iv_med == z.iv_med and z.iv < z.iv_med):
            continue
        d0 = O.execucao(z.ds, lag, z.v)
        if d0 is None:
            continue
        S0 = d["S"]["BOVA"].get(d0, np.nan)
        if not np.isfinite(S0):
            continue
        n = int(round(capital * 4 * p["cobertura"] / (100 * S0)))
        if n < 1:
            continue
        spec = [("P", 1 - p["put_otm"], 1)] + ([("C", 1 + p["call_otm"], -1)] if p["hedge"] == "collar" else [])
        pernas = [O.perna(d, "BOVA", z.v, d0, S0 * k, tp, sg, custo_mult) for tp, k, sg in spec]
        if any(x is None for x in pernas):
            continue
        x = O.pnl_pernas(pernas, n, [sg for _, _, sg in spec], custo_mult)
        pnl = pnl.add(x, fill_value=0)
        neg.append(dict(ativo="BOVA_" + p["hedge"], lado=1, entrada=x.index[0], saida=x.index[-1], lotes=n,
                        K="/".join(f"{q['K']:.1f}" for q in pernas), custo_rs=float(sum(sg * q["preco"] for q, (_, _, sg) in zip(pernas, spec)) * 100 * n),
                        pnl_rs=float(x.sum()), **{"retorno_%": float(x.sum() / capital * 100)}))
    return {"BOVA": pnl}, neg


def _livro(d, capital, p, lag, custo_mult):
    return _vix_cs(d, capital, p, lag, custo_mult) if p["hedge"] == "vix_cs" else _bova(d, capital, p, lag, custo_mult)


def _p(params):
    return {**PARAMS, **params}


def excesso(d, capital=20000, custo_mult=1, lag=0, regime=REGIME, alavancagem=1, **params):
    pnl, _ = _livro(d, capital * alavancagem, _p(params), lag, custo_mult)
    return O.fecha(sum(pnl.values()) / capital, regime, CUSTO_TROCA, custo_mult)


def classes_ir(d, capital=20000, **params):
    pnl, _ = _livro(d, capital, _p(params), 0, 1)
    return {CLASSE_IR: sum(pnl.values())}


def posicoes(d, capital=20000, **params):
    pnl, _ = _livro(d, capital, _p(params), 0, 0)
    return O.wr_de_pnl(pnl, capital)


def negocios(d, capital=20000, **params):
    _, neg = _livro(d, capital, _p(params), 0, 1)
    return O.negocios_df(neg, capital)
