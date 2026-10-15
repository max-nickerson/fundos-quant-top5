"""
Spin-offs EUA após a venda forçada — versão PESSOA FÍSICA (R$ 20–50 mil) na IBKR, só o necessário fora.

Tese de mesa: a empresa separada nasce pequena e fora do mandato de quem tinha a controladora; fundos de índice e gestores vendem nas
primeiras semanas sem olhar preço. Compro `espera` pregões depois do 1º preço (quando a venda forçada acabou) e seguro `dias` pregões.

Base CORRIGIDA da auditoria (quant/fundos/pesquisa/auditoria_eventos.md, código ideias_aud_eventos.spin_aud):
  - eventos: CIK com Form 10-12B na SEC (data do 1º arquivamento = informação pública) -> ticker pelos Forms 3/4 dos próprios diretores
    (pega deslistadas) -> preço Yahoo; só vale se o 1º preço vier até 1 ano depois do 10-12B e não houver preço antes (empresa nova);
  - viés de sobrevivência: spin-offs que NEGOCIARAM (insiders arquivando por > 90 dias) mas sumiram do Yahoo (158; 70% foram compradas
    depois, 18% deslistadas) entram com trajetória sintética de -30% em 166 pregões. Diferença para a auditoria: a trajetória começa em
    max(1º Form 3/4, data do 10-12B) — a auditoria começava no 1º Form 3/4 mesmo quando ele era ANTERIOR ao 10-12B (ex.: SELR, Forms
    desde 2010 e 10-12B em 2017), o que é olhar uma informação antes de ela existir;
  - hedge 50% SPY + 50% IWM (IWM puro embute small - large = -7,5 pp/ano no OOS);
  - parâmetros fixos espera=40, dias=126, sem regime (a auditoria: com IS corrigido o protocolo completo não escolhe esta configuração;
    publicado +8,9 pp -> corrigido +4,3 pp com parâmetros fixos -> -0,5 pp no protocolo completo; sem os 5 maiores ~0).
  - A condição "pelo menos espera+5 preços" do original (exige 5 dias de futuro) virou "pelo menos espera+1" (sem olhar à frente).

Execução PF (o que muda):
  - compra na IBKR com fração (IBKR Pro: US$ 0,0035/ação, mín. US$ 0,35 por ordem — com R$ 1.000 por nome = US$ ~200, a comissão mínima
    é ~0,18% por lado) + meio spread de 0,20% (small/mid cap recém-listada, igual ao custo do institucional);
  - tamanho FIXO na entrada (peso x capital), sem rebalanceio diário até a saída (o institucional rebalanceia para 1/n todo dia);
  - hedge em ações INTEIRAS de SPY (~US$ 670 = R$ 3,4 mil) e IWM (~US$ 240 = R$ 1,2 mil) vendidas, revisto só quando entra/sai um nome
    ou na virada do mês; aluguel SPY 0,25% a.a., IWM 0,30% a.a. (arquivo de short da IBKR, varejo/mapa_ativos_eua.csv; IWM não confirmado);
    vender exige conta margem com >= US$ 2.000 de patrimônio (R$ ~10 mil parados na IBKR, sem juros) — custo fixo pesado em R$ 20 mil.
    MES (micro S&P, ~US$ 38 mil) e M2K (micro Russell, ~US$ 12 mil) não cabem: o livro comprado é de R$ 3–10 mil;
  - dinheiro na IBKR = só o necessário: 100% do comprado (sem empréstimo) + Reg T do vendido (pf.custo_conta_exterior: perde CDI, fica
    em dólar, paga IOF 1,1% + spread na ida e 0,38% + spread na volta). Sem WDO: o saldo em dólar (US$ 1–4 mil) não chega a 1 WDO (US$ 10 mil);
  - IR: classe "exterior" (15% ao ano sobre o ganho, Lei 14.754/2023 — aplicações financeiras no exterior, compensação dentro do ano).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

import _util as U  # noqa: E402
import _rev_pares_pf as PP  # noqa: E402

C, pf = U.C, U.pf

NOME = "Spin-offs EUA após a venda forçada (PF: IBKR com só o necessário fora)"
TESE = ("A separada é vendida por fundos de índice e gestores da controladora nas 1as semanas; compro 40 pregões depois do 1º preço na "
        "IBKR (fração), seguro 6 meses, hedge com SPY/IWM vendidos em ações inteiras; caixa no CDI.")
BENCHMARK = "CDI"
INICIO, CORTE = "2008-01-01", "2021-01-01"
REGIME = "nenhum"
CUSTO_TROCA = .001
PARAMS = {"espera": 40, "dias": 126, "peso": .05, "hedge": "50/50"}
GRADE = {"espera": [10, 20, 40], "dias": [126, 252]}
VIZINHANCA = {"espera": (25, 60), "dias": (90, 180), "peso": (.035, .07)}
RANKING = ["G3 Spin-offs após a venda forçada"]

PERDA_SINT, N_SINT = -.30, 166            # trajetória sintética dos que sumiram (auditoria)
MEIO_SPREAD = {"spin": .002, "SPY": .0001, "IWM": .0002}
ALUGUEL = {"SPY": .0025, "IWM": .003}
INSTRUMENTOS = ("IBKR Pro: ações dos spin-offs (compra fracionária, US$ 0,0035/ação mín. US$ 0,35, ~R$ 1.000 por nome com R$ 20 mil); "
                "hedge: SPY e IWM vendidos em ações inteiras (aluguel 0,25–0,30% a.a.; conta margem >= US$ 2.000). Caixa em Tesouro Selic; "
                "na IBKR só o comprado + Reg T do vendido.")
APLICAVEL = True
MOTIVO = ("Operável: compra fracionária na IBKR resolve o lote (R$ 1–2,5 mil por nome); o hedge em ações inteiras de SPY/IWM fica "
          "grosseiro (1 SPY = R$ 3,4 mil) e exige US$ 2.000 parados para vender a descoberto; sem hedge cambial (WDO não cabe).")
ALAVANCAGENS = [1, 1.5, 2]
MOTIVO_ALAV = ("Alavancagem = peso por nome x L (5% -> 7,5%/10%); o livro comprado continua pago à vista (sem empréstimo de margem). "
               "5x (25% por nome) concentraria em 4 nomes — não é a mesma estratégia; com R$ 20 mil o dinheiro fora passaria do capital.")
VARIANTES = {"sem hedge": {"hedge": "nenhum"}, "hedge só IWM (original)": {"hedge": "IWM"}, "hedge só SPY": {"hedge": "SPY"},
             "10% por nome": {"peso": .10}, "sem os sintéticos (sobrevivência ignorada)": {"sinteticos": False}}


# ---------------------------------------------------------------- dados (cache em pf/dados; base: quant/fundos)
def _constroi():
    """Lê a base da auditoria (ideias_aud_eventos/ideias_global em quant/fundos) e grava eventos + preços (com os sintéticos)."""
    sys.path.insert(0, str(U.FD.parent))
    import ideias_aud_eventos as A                       # noqa: E402  (importa base.py da pesquisa; lê dados/ de quant/fundos)
    g = A._g()
    s = g.spin_eventos()
    P = g._precos_ev("spinoffs")
    sem = A.spin_sem_preco()
    ev = [{"ticker": t, "data": d10, "sintetico": False} for t, d10 in zip(s.ticker, s.d10) if t in P.columns]
    idx = P.index
    k = np.log1p(PERDA_SINT) / N_SINT
    sint = {}
    for t, d0, d10 in zip(sem.ticker, sem.d0, sem.d10):
        ini = max(pd.Timestamp(d0), pd.Timestamp(d10))
        i0 = idx.searchsorted(ini)
        n = min(300, len(idx) - i0)
        if n > 1:
            sint[t + "*"] = pd.Series(np.exp(k * np.arange(n)), index=idx[i0:i0 + n])
            ev.append({"ticker": t + "*", "data": pd.Timestamp(d10), "sintetico": True})
    P = pd.concat([P[[e["ticker"] for e in ev if not e["sintetico"]]], pd.DataFrame(sint).reindex(idx)], axis=1)
    etf = pd.read_parquet(U.FD / "y_etf.parquet")[["SPY", "IWM"]]
    etf.index = pd.DatetimeIndex(etf.index).tz_localize(None).normalize()
    P = pd.concat([P, etf[~etf.index.duplicated()].reindex(idx)], axis=1)
    return pd.DataFrame(ev), P.loc[:, ~P.columns.duplicated()]            # mesmo ticker em 2 eventos (MSGE 2020 e 2023)


def carrega():
    f = U.CACHE / "rev_spinoffs"
    if not (f / "precos.parquet").exists():
        ev, P = _constroi()
        f.mkdir(parents=True, exist_ok=True)
        ev.to_parquet(f / "eventos.parquet")
        P.to_parquet(f / "precos.parquet", compression="zstd")
    ev = pd.read_parquet(f / "eventos.parquet")
    P = pd.read_parquet(f / "precos.parquet")
    return {"eventos": ev, "precos": P, "tb": C.TB_US}


_CACHE = {}


def _chave(d, *a):
    return (id(d), len(d["eventos"]), len(d["precos"]), d["precos"].index.max()) + a


# ---------------------------------------------------------------- motor
def _entradas(d, espera, sinteticos=True):
    """Dia de DECISÃO de cada evento (fechamento do pregão `espera` contado a partir do 1º preço) — só com preços até ali."""
    P = d["precos"]
    out = []
    for t, d10, sint in zip(d["eventos"].ticker, pd.to_datetime(d["eventos"]["data"]), d["eventos"].sintetico):
        if (sint and not sinteticos) or t not in P:
            continue
        x = P[t].dropna()
        antes = x[x.index < d10 - pd.Timedelta(days=30)]
        x = x[x.index >= d10 - pd.Timedelta(days=30)]
        if len(antes) or len(x) <= espera + 1 or x.index[0] > d10 + pd.Timedelta(days=365):
            continue
        out.append((t, x.index[espera]))
    return out


def _roda(d, capital, custo_mult, lag, alavancagem, espera, dias, peso, hedge, sinteticos=True, validacao=False):
    """validacao=True: institucional (sem custos, hedge fracionário, comprado financiado e vendido remunerado a T-bill, câmbio hedgeado)."""
    if validacao:
        custo_mult = 0
    k = _chave(d, capital, custo_mult, lag, alavancagem, espera, dias, round(peso, 6), hedge, sinteticos, validacao)
    if k in _CACHE:
        return _CACHE[k]
    P = d["precos"]
    idx = P.index
    T = len(idx)
    fx = pf.PTAX.reindex(idx.union(pf.PTAX.index)).ffill().reindex(idx).bfill().values
    tb = (d["tb"].reindex(idx.union(d["tb"].index)).ffill().reindex(idx).fillna(0)).values
    ent = _entradas(d, espera, sinteticos)
    nomes = sorted({t for t, _ in ent})
    col = {t: i for i, t in enumerate(nomes)}
    Pm = P[nomes].values if nomes else np.zeros((T, 0))
    Q = np.zeros((T, len(nomes)))                          # ações (unidades ajustadas) no fechamento i
    trades = []
    for t, dd in ent:
        j = idx.searchsorted(dd)                          # decisão no fechamento j
        i0 = j + 1 + lag                                  # execução
        if i0 >= T:
            continue
        c = col[t]
        p0 = Pm[i0 - 1 - lag, c] if np.isfinite(Pm[i0 - 1 - lag, c]) else np.nan
        if not np.isfinite(p0) or p0 <= 0:
            continue
        sh = peso * alavancagem * capital / fx[j] / p0
        i1 = min(i0 + dias, T - 1)                        # sai no fechamento i0+dias (ou quando o preço some)
        viv = np.isfinite(Pm[i0:i1 + 1, c])
        if not viv[0]:
            continue
        if not viv.all():                                 # preço sumiu (comprada/deslistada): vende no último preço (1 dia depois)
            i1 = i0 + int(np.argmin(viv))
        Q[i0:i1, c] += sh
        trades.append((t, i0, i1))
    Pf = np.where(np.isfinite(Pm), Pm, np.nan)
    Pf = pd.DataFrame(Pf, index=idx).ffill().values       # último preço para marcar/vender quem sumiu
    dQ = np.diff(np.vstack([np.zeros((1, Q.shape[1])), Q]), axis=0)
    Qp = np.vstack([np.zeros((1, Q.shape[1])), Q[:-1]])
    dP = np.nan_to_num(np.diff(np.vstack([Pf[:1], Pf]), axis=0))
    pnl_usd = Qp * dP
    val = np.abs(dQ) * np.nan_to_num(Pf)
    com = pf.custo_ordem_ibkr_usd(val, np.nan_to_num(Pf, nan=1.0))
    cst_usd = (com + val * MEIO_SPREAD["spin"]) * custo_mult
    L = (Q * np.nan_to_num(Pf)).sum(axis=1)               # US$ comprados (fechamento i)
    # ---- hedge em ações inteiras, revisto quando o livro muda ou na virada do mês
    hs = {"50/50": {"SPY": .5, "IWM": .5}, "IWM": {"IWM": 1.0}, "SPY": {"SPY": 1.0}, "nenhum": {}}[hedge]
    H = {h: np.zeros(T) for h in hs}
    mes = idx.to_period("M")
    muda = np.r_[True, (np.abs(dQ).sum(axis=1) > 0)[1:] | (mes[1:] != mes[:-1])]
    ph = {h: P[h].ffill().values for h in hs}
    atual = {h: 0.0 for h in hs}
    for i in range(T):
        if muda[i] and i >= 1:
            for h, f in hs.items():
                atual[h] = -(f * L[i - 1] / ph[h][i - 1] if validacao else np.round(f * L[i - 1] / ph[h][i - 1])) if np.isfinite(ph[h][i - 1]) and L[i - 1] > 0 else 0.0
        for h in hs:
            H[h][i] = atual[h]
    pnl_h = np.zeros(T)
    cst_h = np.zeros(T)
    S_val = np.zeros(T)
    for h in hs:
        q = H[h]
        qp = np.r_[0, q[:-1]]
        p = ph[h]
        pnl_h += qp * np.nan_to_num(np.diff(np.r_[p[0], p]))
        dq = np.abs(np.diff(np.r_[0, q]))
        cst_h += (pf.custo_ordem_ibkr_usd(dq * np.nan_to_num(p), np.nan_to_num(p, nan=1.0)) + dq * np.nan_to_num(p) * MEIO_SPREAD[h]) * custo_mult
        cst_h += np.clip(-qp, 0, None) * np.nan_to_num(np.r_[p[0], p[:-1]]) * ALUGUEL[h] / 252 * custo_mult
        S_val += np.abs(q) * np.nan_to_num(p)
    # ---- para o calendário da B3 (R$): P&L em US$ x PTAX do dia, somado no pregão seguinte da B3
    pnl_brl = pd.Series((pnl_usd.sum(axis=1) - cst_usd.sum(axis=1) + pnl_h - cst_h) * fx, index=idx)
    nome_brl = pd.DataFrame((pnl_usd - cst_usd) * fx[:, None], index=idx, columns=nomes)
    hedge_brl = pd.Series((pnl_h - cst_h) * fx, index=idx)
    exig_us = pd.Series(np.where(S_val > 0, np.maximum(PP.patrimonio_ibkr(L, S_val), PP.REG_T_MIN_USD), L) * fx, index=idx)
    exig = exig_us.reindex(C.DIAS.union(idx)).ffill().reindex(C.DIAS).fillna(0) * 1.05
    conta, saldo = pf.custo_conta_exterior(exig, folga=PP.FOLGA_CONTA)
    perd = saldo.shift(1).fillna(0) * C.CDI.reindex(C.DIAS).fillna(0)
    ganho = saldo.shift(1).fillna(0) * pf.PTAX.pct_change(fill_method=None).fillna(0)
    remessa = (conta - perd + ganho) * custo_mult
    ext = pf.usd_para_br(pnl_brl) + ganho - remessa
    e = (ext - perd) / capital
    if validacao:                                         # excesso em US$ sobre o T-bill, com hedge cambial (= excesso sobre o CDI)
        Lp, Sp = np.r_[0, L[:-1]], np.r_[0, S_val[:-1]]
        e_us = pd.Series((pnl_usd.sum(axis=1) + pnl_h - tb * (Lp - Sp)) / (capital / fx), index=idx)
        e = C.brl(e_us)
    res = {"e": e, "classes": {"exterior": ext, "_cdi_perdido": perd}, "trades": trades, "nome_brl": nome_brl, "hedge_brl": hedge_brl,
           "idx": idx, "Q": Q, "nomes": nomes, "Pf": Pf, "fx": fx, "saldo": saldo, "exig": exig, "conta": perd - ganho + remessa, "H": H}
    if len(_CACHE) > 60:
        _CACHE.clear()
    _CACHE[k] = res
    return res


# ---------------------------------------------------------------- contrato
def excesso(d, capital=20000, custo_mult=1, lag=0, regime=REGIME, alavancagem=1, espera=PARAMS["espera"], dias=PARAMS["dias"],
            peso=PARAMS["peso"], hedge=PARAMS["hedge"], sinteticos=True, validacao=False):
    res = _roda(d, capital, custo_mult, lag, alavancagem, espera, dias, peso, hedge, sinteticos, validacao)
    return C.aplica_regime(res["e"], regime, CUSTO_TROCA * custo_mult)


def classes_ir(d, capital=20000, espera=PARAMS["espera"], dias=PARAMS["dias"], peso=PARAMS["peso"], hedge=PARAMS["hedge"]):
    return _roda(d, capital, 1, 0, 1, espera, dias, peso, hedge)["classes"]


def _para_b3(X):
    """Retornos diários (calendário dos EUA) -> calendário da B3 (composição dos dias até o pregão da B3)."""
    l = np.log1p(X.fillna(0).clip(lower=-.99)).cumsum()
    l = l.reindex(C.DIAS.union(l.index)).ffill().reindex(C.DIAS).fillna(0)
    return np.expm1(l.diff().fillna(0))


def posicoes(d, capital=20000, espera=PARAMS["espera"], dias=PARAMS["dias"], peso=PARAMS["peso"], hedge=PARAMS["hedge"]):
    """Pesos (fração do capital, decididos em t = véspera da execução) e retorno em excesso ao T-bill, no calendário da B3."""
    res = _roda(d, capital, 1, 0, 1, espera, dias, peso, hedge)
    idx, fx = res["idx"], res["fx"]
    Pf = pd.DataFrame(res["Pf"], index=idx, columns=res["nomes"])
    V = pd.DataFrame(res["Q"], index=idx, columns=res["nomes"]) * Pf.mul(fx, axis=0) / capital
    tb = d["tb"].reindex(idx).ffill().fillna(0)
    R = Pf.pct_change(fill_method=None).sub(tb, axis=0)
    for h, q in res["H"].items():
        V[h] = q * d["precos"][h].ffill().values * fx / capital
        R[h] = d["precos"][h].ffill().pct_change(fill_method=None) - tb
    W = V.shift(-1).fillna(0)                             # decidido na véspera da execução
    W = W.reindex(C.DIAS.union(idx)).ffill().reindex(C.DIAS).fillna(0)
    return W, _para_b3(R)


def negocios(d, capital=20000, espera=PARAMS["espera"], dias=PARAMS["dias"], peso=PARAMS["peso"], hedge=PARAMS["hedge"], lag=0):
    res = _roda(d, capital, 1, lag, 1, espera, dias, peso, hedge)
    idx, NB, Pf = res["idx"], res["nome_brl"], res["Pf"]
    col = {t: i for i, t in enumerate(res["nomes"])}
    tbl = d["tb"].reindex(idx).ffill().fillna(0)
    lh = {h: np.log(d["precos"][h].ffill()) for h in ("SPY", "IWM")}
    lin = []
    for t, i0, i1 in res["trades"]:
        c = col[t]
        ret = (Pf[i1, c] / Pf[i0, c] - 1) * 100
        hed = np.mean([np.expm1(lh[h].iloc[i1] - lh[h].iloc[i0]) for h in lh]) * 100
        lin.append({"ativo": t, "lado": 1, "entrada": idx[i0], "saida": idx[i1], "dias": int(i1 - i0), "retorno_%": ret,
                    "contrib_pp": float(NB[t].iloc[i0 + 1:i1 + 1].sum() / capital * 100), "hedge_%": hed, "ret_menos_hedge_%": ret - hed,
                    "sintetico": t.endswith("*")})
    # hedge: um "negócio" por ano (para a atribuição)
    hb = res["hedge_brl"]
    for a, x in hb.groupby(idx.year):
        if x.abs().sum() > 0:
            lin.append({"ativo": f"hedge {res_hedge_nome(hedge)}", "lado": -1, "entrada": x.index[0], "saida": x.index[-1], "dias": len(x),
                        "retorno_%": np.nan, "contrib_pp": float(x.sum() / capital * 100), "hedge_%": np.nan, "ret_menos_hedge_%": np.nan,
                        "sintetico": False})
    return pd.DataFrame(lin)


def res_hedge_nome(h):
    return {"50/50": "SPY+IWM", "IWM": "IWM", "SPY": "SPY"}.get(h, h)


def diagnostico(d, capital=20000, **kw):
    p = {**PARAMS, **kw}
    res = _roda(d, capital, 1, 0, 1, p["espera"], p["dias"], p["peso"], p["hedge"], kw.get("sinteticos", True))
    o = lambda s: s[s.index >= CORTE]
    idx = res["idx"]
    L = pd.Series((res["Q"] * np.nan_to_num(res["Pf"])).sum(axis=1) * res["fx"], index=idx)
    ng = negocios(d, capital, p["espera"], p["dias"], p["peso"], p["hedge"])
    ns = ng[~ng.ativo.str.startswith("hedge")]
    hh = {h: pd.Series(q, index=idx) for h, q in res["H"].items()}
    return {"negocios": len(ns), "negocios OOS": int((ns.entrada >= CORTE).sum()), "sinteticos": int(ns.sintetico.sum()),
            "livro comprado medio OOS R$": round(float(o(L).mean())), "saldo IBKR medio OOS R$": round(float(o(res["saldo"]).mean())),
            "acoes de hedge medias OOS": {h: round(float(-o(q).mean()), 2) for h, q in hh.items()},
            "hedge/comprado OOS": round(float(sum((-o(q) * d["precos"][h].reindex(o(q).index).ffill() * pd.Series(res["fx"], index=idx).reindex(o(q).index)).mean() for h, q in hh.items()) / max(o(L).mean(), 1)), 2) if hh else 0}
