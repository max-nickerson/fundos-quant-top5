"""
Peças comuns da frente PF2 "fluxo global" (pf/fundos/fg_*.py): fluxos FORÇADOS e eventos fora do Brasil em tamanho de pessoa física.

- Dados: só o que já está baixado (quant/fundos/dados: Yahoo, SEC, Wikipédia) + downloads gratuitos novos (yfinance, SEC frames) com cache
  em pf/dados/pf2_fluxo_global/. Nada é re-baixado se o cache existe.
- `livro(...)`: livro de EVENTOS na IBKR com compra-e-segura (tamanho fixo na entrada, sem rebalanceio diário — rebalancear small caps a
  peso fixo cria ganho falso), comissão IBKR real (US$ 0,0035/ação, mín. US$ 0,35; Europa 0,05% mín. ~€ 1,75), meio spread por negócio,
  hedge em ações INTEIRAS de ETF vendido (revisto quando o livro muda ou na virada do mês, aluguel a.a.), e a conta no exterior com SÓ o
  necessário (pf.custo_conta_exterior: o saldo perde CDI, fica em dólar e paga IOF + spread de câmbio na remessa).
  Execução: decisão no fechamento t (dia do evento público), compra no fechamento t+1+lag; saída no fechamento i0+dias (ou na data de saída
  decidida, +1+lag); se o preço some (comprada/deslistada), vende no último preço.
"""
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _util as U  # noqa: E402

C, pf = U.C, U.pf
FD = U.FD                                              # quant/fundos/dados
CACHE = U.CACHE / "pf2_fluxo_global"
CACHE.mkdir(parents=True, exist_ok=True)
REG_T_MIN_USD, FOLGA_CONTA = 2_000.0, 1.05             # IBKR: US$ 2 mil para conta margem (vender a descoberto); folga do saldo
ALUGUEL_ETF = {"SPY": .0025, "IWM": .003, "QQQ": .0025, "EWG": .005, "EWQ": .005, "IWC": .01}   # a.a. (IBKR, ETFs líquidos; EWG/EWQ estimado)
MEIO_SPREAD_ETF = {"SPY": .0001, "IWM": .0002, "QQQ": .0001, "EWG": .0005, "EWQ": .0007, "IWC": .001}
WDO_USD, WDO_CUSTO = 10_000.0, 3.70                     # mini-dólar (B3): R$ 1,20 emolumentos + meio tick por lado; rola todo mês
CUPOM = C.ler("carry_moedas/cupom_frc.csv")["cupom_frc_aa_pct"]   # cupom cambial do 1º FRC (2019+); antes: T-bill + 1,07 pp
EUR_MIN, EUR_PCT = 1.75, .0005                         # IBKR Pro escalonado Europa: 0,05% do valor, mín. ~€ 1,25 + taxas de bolsa (~€ 0,5)


# ---------------------------------------------------------------- dados
def ler_fd(nome):
    x = pd.read_parquet(FD / nome)
    if isinstance(x.index, pd.DatetimeIndex):
        x.index = pd.DatetimeIndex(x.index).tz_localize(None).normalize()
        x = x[~x.index.duplicated()].sort_index()
    return x


def painel_y(nome, campo="Close"):
    """quant/fundos/dados/y_ie_<nome>.parquet ('TK|Close', 'TK|Volume') -> DataFrame de um campo, colunas = tickers."""
    X = ler_fd(f"y_ie_{nome}.parquet")
    P = X[[c for c in X if c.endswith("|" + campo)]]
    P.columns = [c.split("|")[0] for c in P]
    return P


def etf(cols=("SPY", "IWM", "QQQ", "TLT", "IEF", "EWG", "EWQ")):
    return ler_fd("y_etf.parquet")[list(cols)]


def eurusd():
    return ler_fd("y_fx.parquet")["EURUSD=X"]


def yf_baixa(tickers, arquivo, ini="2005-01-01", campos=("Close", "Volume"), lote=200, auto_adjust=True, pausa=0):
    """yfinance em lotes com cache (pf/dados/pf2_fluxo_global/<arquivo>.parquet, colunas 'TK|Campo') e lista de tentados."""
    import yfinance as yf
    f, ft = CACHE / f"{arquivo}.parquet", CACHE / f"{arquivo}_tentados.txt"
    X = pd.read_parquet(f) if f.exists() else pd.DataFrame()
    tent = set(ft.read_text().split()) if ft.exists() else set()
    falta = [t for t in dict.fromkeys(tickers) if t not in tent]
    for k in range(0, len(falta), lote):
        lt = falta[k:k + lote]
        for tent_n in range(3):
            try:
                y = yf.download(lt, start=ini, progress=False, auto_adjust=auto_adjust, threads=True, group_by="column",
                                actions=bool({"Dividends", "Stock Splits"} & set(campos)))
                break
            except Exception as ex:                                     # noqa: BLE001
                print("   yfinance falhou, nova tentativa:", ex)
                time.sleep(10)
        else:
            continue
        if len(y):
            if not isinstance(y.columns, pd.MultiIndex):
                y.columns = pd.MultiIndex.from_product([y.columns, lt])
            partes = []
            for c in campos:
                if c in y.columns.get_level_values(0):
                    z = y[c].copy()
                    z.columns = [f"{t}|{c}" for t in z.columns]
                    partes.append(z)
            Z = pd.concat(partes, axis=1).dropna(how="all", axis=1)
            Z.index = pd.DatetimeIndex(Z.index).tz_localize(None).normalize()
            X = pd.concat([X, Z[[c for c in Z.columns if c not in X.columns]]], axis=1) if len(X) else Z
        vieram = {c.split("|")[0] for c in (Z.columns if len(y) else [])}
        if len(vieram) < .2 * len(lt) and pausa:                   # provável limite de requisições: não marca, espera e segue
            print(f"   poucos tickers vieram ({len(vieram)}/{len(lt)}), pausa {pausa * 3}s", flush=True)
            tent |= vieram
            time.sleep(pausa * 3)
        else:
            tent |= set(lt)
        if pausa:
            time.sleep(pausa)
        X.astype("float32").to_parquet(f, compression="zstd")
        ft.write_text("\n".join(sorted(tent)))
        print(f"   {arquivo}: {min(k + lote, len(falta))}/{len(falta)} tickers, {X.shape[1]} colunas", flush=True)
    return X


def sintetico(idx, ini, perda=-.30, n=166, nome="X*"):
    """Trajetória sintética para quem SUMIU do Yahoo (deslistada): perde `perda` em `n` pregões a partir de `ini` e fica parada
    (mesma regra da auditoria de spin-offs, quant/fundos/pesquisa/auditoria_eventos.md). Conservador para livro COMPRADO."""
    i0 = idx.searchsorted(pd.Timestamp(ini))
    k = np.log1p(perda) / n
    v = np.full(len(idx), np.nan)
    m = min(300, len(idx) - i0)
    if m > 0:
        v[i0:i0 + m] = np.exp(k * np.minimum(np.arange(m), n))
    return pd.Series(v, index=idx, name=nome)


def para_b3(X):
    """Retornos diários (calendário dos EUA) -> calendário da B3 (composição dos dias até o pregão da B3)."""
    l = np.log1p(X.fillna(0).clip(lower=-.99)).cumsum()
    l = l.reindex(C.DIAS.union(l.index)).ffill().reindex(C.DIAS).fillna(0)
    return np.expm1(l.diff().fillna(0))


def no_idx(s, idx):
    return s.reindex(idx.union(s.index)).ffill().reindex(idx)


# ---------------------------------------------------------------- livro de eventos na IBKR
def comissao(valor_usd, preco_usd, regiao, eurusd_=1.1):
    """Comissão por ordem em US$ (vetorizado em valor)."""
    v = np.abs(valor_usd)
    if str(regiao).startswith("US"):
        return pf.custo_ordem_ibkr_usd(v, np.maximum(preco_usd, .01))
    return np.where(v > 0, np.maximum(EUR_MIN * eurusd_, EUR_PCT * v), 0.0)


def livro(tr, P, capital, custo_mult=1.0, lag=0, alavancagem=1.0, peso=.05, teto=1.0, hedge=None, hedge_frac=1.0, fracao=True,
          ffill_lim=5, janela_conta=0, hedge_fx="nenhum"):
    """Livro de eventos (IBKR) em US$, convertido para excesso diário sobre o CDI em R$ (calendário da B3).

    tr: DataFrame com ticker, decisao (data; decide no fechamento do 1º pregão >= decisao), dias (pregões até a saída) OU saida (data de
        decisão da saída, executa no fechamento seguinte), lado (+1/-1), custo (meio spread + impostos por lado, fração), extra_compra
        (imposto só na compra, ex.: TTF francesa 0,4%), aluguel (a.a., se vendido), regiao ('US'/'EU'), peso (opcional, sobrepõe `peso`).
    P: preços em US$ (colunas = tickers do livro + ETFs de hedge), calendário dos EUA/Europa (união).
    hedge: dict regiao -> ETF vendido (em P) contra o livro comprado líquido daquela região, `hedge_frac` do valor, ações inteiras.
    teto: soma do livro comprado <= teto x capital x alavancagem (negócio novo que estoura é pulado).
    """
    idx = P.index
    T = len(idx)
    fx = no_idx(pf.PTAX, idx).bfill().values                       # R$/US$
    eu = no_idx(eurusd(), idx).bfill().values
    Pf = P.ffill(limit=ffill_lim)
    trs = []
    if len(tr):
        tr = tr.sort_values("decisao", kind="stable").reset_index(drop=True)
    pnl = np.zeros(T)
    cst = np.zeros(T)
    Lr = {}                                                         # valor comprado (US$) por região no fechamento i
    Ltot, Stot = np.zeros(T), np.zeros(T)
    pos_val = {}                                                    # ticker -> valor em US$ no fechamento i (para posicoes)
    contrib = []
    for k, r in tr.iterrows():
        t = r.ticker
        if t not in P.columns:
            continue
        j = idx.searchsorted(pd.Timestamp(r.decisao))
        i0 = j + 1 + lag
        if i0 >= T or j >= T:
            continue
        p0 = Pf[t].values[j]
        pe = Pf[t].values[i0]
        if not (np.isfinite(p0) and p0 > 0 and np.isfinite(pe) and pe > 0):
            continue
        if "saida" in tr.columns and pd.notna(r.get("saida", np.nan)):
            i1 = min(idx.searchsorted(pd.Timestamp(r.saida)) + 1 + lag, T - 1)
        else:
            i1 = min(i0 + int(r.dias), T - 1)
        if i1 <= i0:
            continue
        reg = r.get("regiao", "US") if "regiao" in tr.columns else "US"
        w = (r.peso if ("peso" in tr.columns and pd.notna(r.get("peso", np.nan))) else peso) * alavancagem
        lado = int(r.lado) if "lado" in tr.columns else 1
        L_now = Ltot[j] + Stot[j]
        if lado > 0 and (L_now + w * capital / fx[j]) > teto * alavancagem * capital / fx[j] * 1.0001:
            continue
        sh = w * capital / fx[j] / p0
        if not fracao or not str(reg).startswith("US"):
            sh = np.floor(sh)
            if sh < 1:
                continue
        x = Pf[t].values[i0:i1 + 1]
        if not np.isfinite(x).all():                                # preço sumiu (> ffill_lim pregões): vende no último preço conhecido
            i1 = i0 + max(int(np.argmin(np.isfinite(x))), 1)
            x = Pf[t].ffill().values[i0:i1 + 1]
        s = lado * sh
        dP = np.diff(x)
        pnl_k = np.zeros(T)
        pnl_k[i0 + 1:i1 + 1] = s * dP
        v0, v1 = sh * x[0], sh * x[-1]
        c0 = comissao(v0, x[0], reg, eu[i0]) + v0 * (r.custo + (r.extra_compra if lado > 0 and "extra_compra" in tr.columns else 0))
        c1 = comissao(v1, x[-1], reg, eu[i1]) + v1 * (r.custo + (r.extra_compra if lado < 0 and "extra_compra" in tr.columns else 0))
        cst_k = np.zeros(T)
        cst_k[i0] += c0 * custo_mult
        cst_k[i1] += c1 * custo_mult
        if lado < 0:
            cst_k[i0 + 1:i1 + 1] += sh * x[:-1] * r.aluguel / 252 * custo_mult
        pnl += pnl_k
        cst += cst_k
        val = np.zeros(T)
        val[i0:i1] = sh * x[:-1]
        if lado > 0:
            Ltot += val
            Lr.setdefault(reg, np.zeros(T))
            Lr[reg] += val
        else:
            Stot += val
        pv = pos_val.setdefault(t, np.zeros(T))
        pv[i0:i1] += s * x[:-1]
        net_brl = (pnl_k - cst_k) * fx
        contrib.append({"ativo": t, "lado": lado, "entrada": idx[i0], "saida": idx[i1], "dias": int(i1 - i0), "regiao": reg,
                        "retorno_%": lado * (x[-1] / x[0] - 1) * 100, "pnl_brl": float(net_brl.sum()), "i0": i0, "i1": i1,
                        "decisao": idx[j], "_val": val[i0:i1].copy(), "_reg": reg})
    # ---- hedge em ações inteiras por região
    H, hr = {}, {}
    pnl_h, cst_h, S_h = np.zeros(T), np.zeros(T), np.zeros(T)
    mes = idx.to_period("M")
    for reg, h in (hedge or {}).items():
        if h is None or reg not in Lr or h not in P.columns:
            continue
        Lg = Lr[reg]
        ph = P[h].ffill().values
        muda = np.r_[True, (np.diff(Lg) != 0) | (mes[1:] != mes[:-1])]
        q = np.zeros(T)
        atual = 0.0
        for i in range(1, T):
            if muda[i]:
                atual = -np.round(hedge_frac * Lg[i - 1] / ph[i - 1]) if (np.isfinite(ph[i - 1]) and Lg[i - 1] > 0) else 0.0
            q[i] = atual
        qp = np.r_[0, q[:-1]]
        p_h = qp * np.nan_to_num(np.diff(np.r_[ph[0], ph]))
        dq = np.abs(np.diff(np.r_[0, q]))
        c_h = (pf.custo_ordem_ibkr_usd(dq * np.nan_to_num(ph), np.nan_to_num(ph, nan=1.0)) + dq * np.nan_to_num(ph) * MEIO_SPREAD_ETF.get(h, .0005)) * custo_mult
        c_h = c_h + np.clip(-qp, 0, None) * np.nan_to_num(np.r_[ph[0], ph[:-1]]) * ALUGUEL_ETF.get(h, .005) / 252 * custo_mult
        pnl_h += p_h
        cst_h += c_h
        hr[reg] = (p_h - c_h, Lg)
        S_h += np.abs(q) * np.nan_to_num(ph)
        H[h] = q
    pnl_brl = pd.Series((pnl - cst + pnl_h - cst_h) * fx, index=idx)
    hedge_brl = pd.Series((pnl_h - cst_h) * fx, index=idx)
    S_all = Stot + S_h
    tem_short = S_all > 0
    exig_us = np.where(tem_short, np.maximum(np.maximum(.5 * (Ltot + S_all), Ltot - S_all), REG_T_MIN_USD), Ltot)
    exig = pd.Series(exig_us * fx, index=idx)
    exig = exig.reindex(C.DIAS.union(idx)).ffill().reindex(C.DIAS).fillna(0) * 1.05
    if janela_conta:          # saldo ESTÁVEL na IBKR: o maior exigido dos últimos `janela_conta` pregões (só passado) — evita remeter
        exig = exig.rolling(janela_conta, min_periods=1).max()      # todo mês (IOF 1,1% + spread na ida, 0,38% + spread na volta)
    if exig.abs().sum() > 0:
        conta, saldo = pf.custo_conta_exterior(exig, folga=FOLGA_CONTA)
    else:
        conta = saldo = pd.Series(0.0, index=C.DIAS)
    perd = saldo.shift(1).fillna(0) * C.CDI.reindex(C.DIAS).fillna(0)
    ganho = saldo.shift(1).fillna(0) * pf.PTAX.pct_change(fill_method=None).fillna(0)
    remessa = (conta - perd + ganho) * custo_mult
    # ---- hedge cambial opcional: vende WDO (US$ 10 mil) contra o saldo em dólar quando ele arredonda para >= 1 contrato
    wdo = pd.Series(0.0, index=C.DIAS)
    if hedge_fx == "wdo" and saldo.abs().sum() > 0:
        fxb = pf.PTAX.reindex(C.DIAS).ffill().values
        usd = (saldo / pf.PTAX).fillna(0).values
        n = -np.maximum(np.floor(np.r_[0, 0, usd[:-2]] / WDO_USD + .2), 0)     # só com >= 0,8 contrato de saldo (sobre-hedge <= 25%)
        cup = (CUPOM.reindex(C.DIAS).ffill(limit=5) / 100).fillna(C.TB_US.reindex(C.DIAS).ffill() * 252 + .0107).values
        cdi = C.CDI.reindex(C.DIAS).fillna(0).values
        nprev = np.r_[0, n[:-1]]
        f0 = np.r_[fxb[0], fxb[:-1]]
        pnl_w = nprev * WDO_USD * (fxb - f0) - nprev * WDO_USD * f0 * (cdi - cup / 252)  # vendido: ganha CDI − cupom, perde a alta do dólar
        cw = (np.abs(np.diff(np.r_[0, n])) * WDO_CUSTO + np.abs(nprev) * 2 * WDO_CUSTO * 12 / 252) * custo_mult   # rola todo mês
        wdo = pd.Series(np.nan_to_num(pnl_w - cw), index=C.DIAS)
    ext = pf.usd_para_br(pnl_brl) + ganho - remessa
    e = (ext + wdo - perd) / capital
    # ---- P&L do hedge rateado entre os negócios abertos da região (pelo valor de cada um no fechamento anterior)
    alocado = np.zeros(T)
    for c in contrib:
        c["hedge_brl"] = 0.0
        if c["_reg"] in hr:
            hp, Lg = hr[c["_reg"]]
            i0, i1 = c["i0"], c["i1"]
            w = np.divide(c["_val"], Lg[i0:i1], out=np.zeros(i1 - i0), where=Lg[i0:i1] > 0)
            a = hp[i0 + 1:i1 + 1] * w * fx[i0 + 1:i1 + 1]
            c["hedge_brl"] = float(a.sum())
            alocado[i0 + 1:i1 + 1] += a
        del c["_val"], c["_reg"]
    ng = pd.DataFrame(contrib)
    if len(ng):
        ng["contrib_pp"] = (ng.pnl_brl + ng.hedge_brl) / capital * 100
    hedge_res = pd.Series((pnl_h - cst_h) * fx - alocado, index=idx)   # resíduo (hedge aberto sem livro por arredondamento/defasagem)
    return {"e": e, "ng": ng, "idx": idx, "fx": fx, "Pf": Pf, "pos_val": pos_val, "H": H, "hedge_brl": hedge_brl, "hedge_res": hedge_res, "saldo": saldo,
            "conta_brl": perd - ganho + remessa, "ganho": ganho, "remessa": remessa, "wdo": wdo, "L": pd.Series(Ltot * fx, index=idx), "ext": ext, "perd": perd}


def posicoes_de(res, P, capital):
    """Pesos (fração do capital, decididos na véspera da execução) e retornos em excesso ao T-bill, no calendário da B3."""
    idx, fx = res["idx"], res["fx"]
    tb = no_idx(C.TB_US, idx).fillna(0)
    nomes = list(res["pos_val"])
    V = pd.DataFrame({t: res["pos_val"][t] for t in nomes}, index=idx).mul(fx, axis=0) / capital if nomes else pd.DataFrame(index=idx)
    Pf = P.ffill(limit=5)
    R = Pf[nomes].pct_change(fill_method=None).sub(tb, axis=0) if nomes else pd.DataFrame(index=idx)
    for h, q in res["H"].items():
        V[h] = q * P[h].ffill().values * fx / capital
        R[h] = P[h].ffill().pct_change(fill_method=None) - tb
    W = V.shift(-1).fillna(0)
    W = W.reindex(C.DIAS.union(idx)).ffill().reindex(C.DIAS).fillna(0)
    return W, para_b3(R)


def negocios_de(res, capital, P=None):
    ng = res["ng"].copy()
    if not len(ng):
        return pd.DataFrame(columns=["ativo", "lado", "entrada", "saida", "dias", "retorno_%", "contrib_pp"])
    if P is not None and res["H"]:
        lh = {h: np.log(P[h].ffill()) for h in res["H"]}
        h0 = list(lh)[0]
        ng["hedge_%"] = [np.expm1(lh[h0].iloc[b] - lh[h0].iloc[a]) * 100 for a, b in zip(ng.i0, ng.i1)]
        ng["ret_menos_hedge_%"] = ng["retorno_%"] - ng.lado * ng["hedge_%"]
    out = [ng.drop(columns=["i0", "i1", "pnl_brl", "hedge_brl"])]
    hb = res["hedge_res"]
    if hb.abs().sum() > 0:
        for a, x in hb.groupby(res["idx"].year):
            if x.abs().sum() > 0:
                out.append(pd.DataFrame([{"ativo": "hedge (resíduo) " + "+".join(res["H"]), "lado": -1, "entrada": x.index[0], "saida": x.index[-1],
                                          "dias": len(x), "retorno_%": np.nan, "contrib_pp": float(x.sum() / capital * 100)}]))
    return pd.concat(out, ignore_index=True)


# ---------------------------------------------------------------- B3 (ETF/FII) — calendário da B3, preços do COTAHIST
def cotahist_fundos(tickers=None):
    x = pd.read_parquet(U.CACHE / "renda_fixa" / "cotahist_fundos.parquet")
    if tickers is not None:
        x = x[x.ticker.isin(tickers)]
    x["data"] = pd.to_datetime(x["data"])
    return x


def pivo(x, campo):
    return x.pivot_table(index="data", columns="ticker", values=campo, aggfunc="last").reindex(C.DIAS)


EXCL_NOME = (r"\bETF\b|\bETN\b|FUND\b|TRUST\b|PROSHARES|DIREXION|ISHARES|SPDR|INVESCO|VANGUARD|WISDOMTREE|GRAYSCALE|ULTRA|LEVERAGED|"
             r"INVERSE|PORTFOLIO|MUNICIPAL|INCOME|ACQUISITION CORP|ACQUISITION CO|BLANK CHECK|CAPITAL CORP|BDC|ROYALTY")


def painel_universo():
    """Ações EUA com preço no Yahoo (base quant/fundos y_ie_sp + y_ie_us + downloads novos), Close ajustado e Volume, calendário dos EUA.
    Sem ETFs/fundos/SPACs (pelo nome na SEC quando existe). Só vivas no Yahoo (viés de sobrevivência: ver cada fundo)."""
    Ps, Vs = [], []
    for nome in ("sp", "us"):
        Ps.append(painel_y(nome))
        Vs.append(painel_y(nome, "Volume"))
    X = pd.read_parquet(CACHE / "universo_extra.parquet")
    X.index = pd.DatetimeIndex(X.index).tz_localize(None).normalize()
    P2 = X[[c for c in X if c.endswith("|Close")]]
    P2.columns = [c.split("|")[0] for c in P2]
    V2 = X[[c for c in X if c.endswith("|Volume")]]
    V2.columns = [c.split("|")[0] for c in V2]
    Ps.append(P2)
    Vs.append(V2)
    idx = Ps[0].index.union(Ps[1].index).union(P2.index)
    P = pd.concat([p.reindex(idx) for p in Ps], axis=1)
    V = pd.concat([v.reindex(idx) for v in Vs], axis=1)
    P, V = P.loc[:, ~P.columns.duplicated()], V.loc[:, ~V.columns.duplicated()]
    nomes = pd.read_parquet(FD / "sec_tickers_atual.parquet").drop_duplicates("tk").set_index("tk").nome.str.upper()
    fora = set(nomes[nomes.str.contains(EXCL_NOME, regex=True, na=False)].index) | {"SPY", "IWM", "QQQ", "IWC", "DIA", "TLT", "IEF"}
    cols = [c for c in P.columns if c not in fora]
    return P[cols], V.reindex(columns=cols)


def preco_bruto(P):
    """Preço NÃO ajustado (o que se via na tela no dia) = Close ajustado do Yahoo x produto dos desdobramentos POSTERIORES (Yahoo
    'Stock Splits', cache splits.parquet). Sem isso, filtros de preço olham o futuro: um IPO de US$ 4 que fez grupamento 1:20 depois
    aparece como US$ 80 no passado. Tickers sem histórico de desdobramento ficam como estão."""
    X = pd.read_parquet(CACHE / "splits.parquet")
    X.index = pd.DatetimeIndex(X.index).tz_localize(None).normalize()
    S = X[[c for c in X if c.endswith("|Stock Splits")]]
    S.columns = [c.split("|")[0] for c in S]
    S = S.loc[:, ~S.columns.duplicated()]
    cols = [c for c in P.columns if c in S.columns]
    F = pd.DataFrame(1.0, index=P.index, columns=P.columns)
    for c in cols:
        r = S[c].replace(0, np.nan).dropna()
        r = r[r > 0]
        if not len(r):
            continue
        for dt, v in r.items():                                       # antes da data do desdobramento: multiplica pela razão
            F.loc[F.index < dt, c] *= v
    return P * F
