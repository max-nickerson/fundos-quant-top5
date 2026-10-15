"""
Motor PF para livros de eventos da B3 (usado por rev_rebal_ibovespa, rev_opa, rev_followon, rev_crise). Não altera _util/pf/comum.

Como a conta de pessoa física funciona aqui (R$ 20–50 mil, Clear/Rico, corretagem zero):
  - cada evento vira um EPISÓDIO: o tamanho é decidido no fechamento de t (fração do capital), executado no fechamento de t+1+lag
    com AÇÕES INTEIRAS (fracionário abaixo de 100) e a quantidade fica FIXA até a saída (sem rebalancear todo dia como o institucional);
  - entrada/saída só em dia COM negócio no papel (sem negócio a ordem não executa e fica para o pregão seguinte);
  - papel sem negócio por `parado` pregões seguidos (OPA liquidada, deslistagem, suspensão) -> posição encerrada ao último preço, sem custo;
  - comprado: o dinheiro sai do Tesouro Selic -> perde o CDI (`_cdi_perdido`); acima do capital (alavancagem) paga termo CDI + 4% a.a.;
  - vendido (BTC): o produto da venda fica em Tesouro Selic como garantia e rende CDI (classe renda_fixa); paga taxa ao doador (a.a.,
    fixa no contrato, revista na renovação) + B3 20% da taxa (piso 0,025%, teto 0,70% a.a.) + corretora 0,5% do volume por contrato
    aberto ou renovado (renovação a cada `renova` pregões);
  - custo de negociação por perna: emolumentos 0,03% + meio spread por liquidez (ADV60 conhecido em t-1: >= 50 mi 0,08%; >= 10 mi 0,20%;
    >= 2 mi 0,50%; abaixo 1,0% — "micro", premissa deste motor) + 0,20% extra na parte fracionária;
  - hedge opcional em BOVA11 (cotas inteiras; vendido = alugado, taxa BOVA11) ou WIN (contratos inteiros, R$ 0,20/ponto, margem em
    Tesouro Selic rende CDI); refeito só quando entra/sai algum episódio.
  - custos="inst": modo de validação com o motor institucional (sem arredondamento, custo 10/20/40/80 bps, aluguel passado pelo módulo,
    sem corretora/B3 no aluguel, hedge contínuo de 3 bps).
IR (classes_ir): P&L do episódio vai inteiro para "acoes_isentas" se as VENDAS de ações do mês da SAÍDA somam <= R$ 20 mil (IN RFB 1.585/2015
art. 59; vale só para ações no mercado à vista — ETF, futuro e termo não entram); venda a descoberto: o ganho é apurado na recompra e a
venda é contada no mês da recompra (prática de mercado; premissa). Aluguel e custos são dedutíveis na própria classe.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _util as U  # noqa: E402

C, pf = U.C, U.pf
DIAS = C.DIAS
EMOL = pf.B3_EMOL                                   # 0,03%
FRAC_EXTRA = pf.B3_SPREAD["fracionario_extra"]     # 0,20%
SPREAD_MICRO = .010                                 # ADV < R$ 2 mi: meio spread 1% (premissa)
ALUG_CORRETORA = pf.ALUGUEL_PF_CORRETORA           # 0,5% do volume por contrato aberto/renovado (Clear/Rico)
RENOVA = 21                                         # pregões por contrato de aluguel
TERMO_SPREAD = .04                                  # termo/financiamento: CDI + 4% a.a. (premissa do varejo/rebal_ibovespa_varejo)
BOVA_TAXA = .0088                                   # BOVA11 tomador, média ponderada B3 em 30/12/2025 (BDI 04-2): 0,88% a.a.
BOVA_SPREAD = .0002
WIN_MULT, WIN_CUSTO = .20, 1.30                    # R$/ponto; R$ por contrato e lado (varejo: emolumentos ~0,30 + 1 tick)
LIMIAR_ISENCAO = 20_000


def meio_spread(adv):
    adv = np.nan_to_num(np.asarray(adv, dtype=float))
    return np.select([adv >= 50e6, adv >= 10e6, adv >= 2e6], [pf.B3_SPREAD["liquida"], pf.B3_SPREAD["media"], pf.B3_SPREAD["pequena"]],
                     SPREAD_MICRO)


def custo_inst(adv):
    adv = np.nan_to_num(np.asarray(adv, dtype=float))
    return np.select([adv >= 50e6, adv >= 10e6, adv >= 2e6], [.0010, .0020, .0040], .0080)


def b3_btc(taxa):
    """Tarifa B3 do tomador no empréstimo eletrônico: 20% da taxa, piso 0,025% e teto 0,70% a.a. (b3.com.br, Tarifas de Empréstimo de Ativos)."""
    return np.clip(.2 * np.asarray(taxa, dtype=float), .00025, .007)


def _perna(valor, n, adv, inst, mult):
    """Custo (R$) de negociar `valor` R$ de um papel em `n` ações."""
    if inst:
        return valor * custo_inst(adv) * mult
    frac = (n % 100) / max(n, 1)
    return valor * (EMOL + meio_spread(adv) + frac * FRAC_EXTRA) * mult


def simula(W, P, R, ADV, capital, custo_mult=1.0, lag=0, alavancagem=1.0, taxa=None, r_ajuste=None, hedge=0.0, instrumento="bova",
           ibov=None, custos="pf", parado=5, renova=RENOVA, rotulos=None, hedge_px=None):
    """W: pesos-alvo decididos no fechamento de t (DIAS x papéis; + comprado, - vendido; fração do capital).
    P: fechamento NÃO ajustado (NaN = sem negócio); R: retorno total ajustado do dia; ADV: média de volume 60d (R$).
    taxa: DataFrame a.a. da taxa ao doador por papel (NaN = sem aluguel disponível -> não vende); r_ajuste: {(data, papel): retorno}.
    hedge: fração da exposição líquida a neutralizar (1 = beta 1) com `instrumento` ("bova" ou "win"; ibov = pontos do Ibovespa).
    Devolve dict: excesso (fração do capital), classes (R$), episodios (DataFrame), contrib (R$/dia por papel + HEDGE)."""
    inst = custos == "inst"
    idx = DIAS
    T = len(idx)
    tk = list(W.columns)
    Wx = W.reindex(idx).fillna(0).shift(1 + lag).fillna(0).to_numpy() * alavancagem
    Pm = P.reindex(index=idx, columns=tk).to_numpy(dtype=float)
    Rm = R.reindex(index=idx, columns=tk).to_numpy(dtype=float)
    Rm = np.where(np.isnan(Rm), 0.0, Rm)
    if r_ajuste:
        pos_d = {d: i for i, d in enumerate(idx)}
        col = {t: j for j, t in enumerate(tk)}
        for (dt, t), v in r_ajuste.items():
            if dt in pos_d and t in col:
                Rm[pos_d[dt], col[t]] = v
    Am = ADV.reindex(index=idx, columns=tk).ffill().shift(1).to_numpy(dtype=float)     # ADV conhecido antes do pregão
    Tx = taxa.reindex(index=idx, columns=tk).to_numpy(dtype=float) if taxa is not None else np.full((T, len(tk)), np.nan)
    cdi = C.CDI.reindex(idx).fillna(0).to_numpy()
    teve = ~np.isnan(Pm)
    Pff = pd.DataFrame(Pm).ffill().to_numpy()
    # dias seguidos sem negócio (inclusive o dia)
    sem = np.zeros_like(Pm)
    for i in range(1, T):
        sem[i] = np.where(teve[i], 0, sem[i - 1] + 1)

    con = np.zeros((T, len(tk)))                    # excesso em R$ por papel
    acao_pnl = []                                   # (array T, mês de saída) por episódio -> classe de IR
    rfix = np.zeros(T)                              # CDI do produto das vendas a descoberto
    perd = np.zeros(T)                              # CDI perdido do dinheiro aplicado em ações
    longv = np.zeros(T)                             # valor comprado no fechamento (para o termo)
    netv = np.zeros(T)                              # exposição líquida no fechamento (para o hedge)
    muda = np.zeros(T, dtype=bool)                  # algum episódio entrou/saiu no dia
    vendas = {}
    eps = []
    for j, t in enumerate(tk):
        w = Wx[:, j]
        sg = np.sign(w)
        mud = np.flatnonzero(np.diff(np.r_[0, sg, 0]) != 0)
        for a0, b0 in zip(mud[:-1], mud[1:]):
            if sg[a0] == 0:
                continue
            s = sg[a0]
            ok = np.flatnonzero(teve[a0:b0, j])
            if not len(ok):
                continue
            a = a0 + ok[0]
            if s < 0 and np.isnan(Tx[a, j]) and not inst:
                continue                                                    # sem aluguel disponível: não vende
            alvo = abs(w[a]) * capital
            n = alvo / Pm[a, j] if inst else np.floor(alvo / Pm[a, j])
            if n <= 0 or (not inst and n < 1):
                continue
            # saída: primeiro dia com negócio a partir de b0; ou papel parado `parado` pregões -> encerra ao último preço
            par = np.flatnonzero(sem[a + 1:, j] >= parado)
            k_par = a + 1 + par[0] if len(par) else T
            sai = np.flatnonzero(teve[b0:, j]) if b0 < T else np.array([], int)
            k_sai = b0 + sai[0] if len(sai) else T
            if k_par < k_sai:
                b, fecha, custo_saida = k_par, True, False
            elif k_sai < T:
                b, fecha, custo_saida = k_sai, True, True
            else:
                b, fecha, custo_saida = T - 1, False, False
            seg = slice(a + 1, b + 1)
            rr = Rm[seg, j]
            v0 = n * Pm[a, j]
            v = v0 * np.cumprod(1 + rr)
            vp = np.r_[v0, v[:-1]]
            pnl = np.zeros(T)
            pnl[seg] = s * vp * rr
            c_in = _perna(v0, n, Am[a, j], inst, custo_mult)
            pnl[a] -= c_in
            c_out = _perna(v[-1] if len(v) else v0, n, Am[b, j], inst, custo_mult) if custo_saida else 0.0
            pnl[b] -= c_out
            alug = 0.0
            if s > 0:
                perd[seg] += vp * cdi[seg]
                longv[a:b] += np.r_[v0, v[:-1]][:b - a] if b > a else 0
            else:
                rfix[seg] += v0 * cdi[seg]
                if inst:
                    tx = np.nan_to_num(Tx[a, j], nan=.08)
                    custo_al = vp * tx / 252 * custo_mult
                else:
                    # contratos: abre em a e renova a cada `renova` pregões (taxa do dia da renovação; se sumiu, mantém a anterior)
                    custo_al = np.zeros(b - a)
                    tx = Tx[a, j]
                    for k0 in range(a, b, renova):
                        if not np.isnan(Tx[k0, j]):
                            tx = Tx[k0, j]
                        k1 = min(k0 + renova, b)
                        vk = v0 if k0 == a else v[k0 - a - 1]
                        pnl[k0] -= ALUG_CORRETORA * vk * custo_mult
                        alug += ALUG_CORRETORA * vk * custo_mult
                        custo_al[k0 - a:k1 - a] += vp[k0 - a:k1 - a] * (tx + b3_btc(tx)) / 252 * custo_mult
                pnl[seg] -= custo_al
                alug += custo_al.sum()
            netv[a:b] += s * np.r_[v0, v[:-1]][:b - a] if b > a else 0
            muda[a] = True
            if fecha:
                muda[b] = True
            mes = idx[b].to_period("M")
            venda = (v[-1] if len(v) else v0) if s > 0 else v0
            if fecha:
                vendas[mes] = vendas.get(mes, 0.0) + venda
            con[:, j] += pnl - (s > 0) * 0                                  # CDI perdido entra em `perd`
            acao_pnl.append((pnl, mes))
            ret = (v[-1] / v0 - 1) if len(v) else 0.0
            eps.append({"ativo": t, "lado": int(s), "entrada": idx[a], "saida": idx[b], "dias": b - a, "acoes": n, "valor_entrada": v0,
                        "retorno_%": ret * 100, "custo_R$": c_in + c_out, "aluguel_R$": alug, "saiu_parado": bool(k_par < k_sai),
                        "_j": j, "_a": a, "_b": b, "_s": s})
    # CDI por papel (para a contribuição): comprado perde, vendido ganha (produto da venda)
    exc_acoes = con.sum(axis=1)
    # ---------------------------------------------------------------- financiamento (alavancagem acima do capital)
    fin = np.zeros(T)
    if not inst:
        exced = np.maximum(longv - capital, 0)
        fin[1:] = exced[:-1] * TERMO_SPREAD / 252 * custo_mult
    # ---------------------------------------------------------------- hedge
    h_pnl = np.zeros(T)
    h_cdi_perd = np.zeros(T)
    h_rfix = np.zeros(T)
    classe_h = "etf_b3"
    if hedge:
        rb = C.R_IBOV.reindex(idx).fillna(0).to_numpy()
        if inst:
            hv = -hedge * netv
            h_pnl[1:] = hv[:-1] * rb[1:] - np.abs(np.diff(hv)) * .0003 * custo_mult
            h_cdi_perd[1:] = hv[:-1] * cdi[1:]                              # excesso = hv (R - CDI)
            h_rfix[:] = 0
            classe_h = "futuros_b3"
            h_pnl, h_cdi_perd = h_pnl - h_cdi_perd, np.zeros(T)
        elif instrumento in ("bova", "serie"):
            # BOVA11 (ou outro ETF passado em hedge_px: preço do ETF, mesma lógica de cotas inteiras/aluguel)
            px = (C.BOVA if hedge_px is None else hedge_px).reindex(idx).ffill().to_numpy()
            if hedge_px is not None:
                rb = pd.Series(px, index=idx).pct_change(fill_method=None).fillna(0).to_numpy()
            cot = 0.0
            v0h = 0.0
            ab = 0                                                          # dia de abertura do aluguel vigente
            for i in range(1, T):
                vh = cot * px[i - 1] if np.isfinite(px[i - 1]) else 0.0
                h_pnl[i] += vh * rb[i]
                if cot > 0:
                    h_cdi_perd[i] += vh * cdi[i]
                elif cot < 0:
                    h_rfix[i] += -v0h * cdi[i]
                    h_pnl[i] -= abs(vh) * (BOVA_TAXA + b3_btc(BOVA_TAXA)) / 252 * custo_mult
                    if i - ab >= renova:
                        h_pnl[i] -= ALUG_CORRETORA * abs(vh) * custo_mult
                        ab = i
                if muda[i] and np.isfinite(px[i]) and px[i] > 0:
                    novo = np.round(-hedge * netv[i] / px[i])
                    if novo != cot:
                        dq = novo - cot
                        h_pnl[i] -= abs(dq) * px[i] * (EMOL + BOVA_SPREAD) * custo_mult
                        if novo < 0 and novo < min(cot, 0):                # aumentou o vendido: novo contrato de aluguel
                            h_pnl[i] -= ALUG_CORRETORA * (min(cot, 0) - novo) * px[i] * custo_mult
                            ab = i
                        cot = novo
                        v0h = cot * px[i] if cot < 0 else 0.0
        else:                                                               # WIN inteiro
            classe_h = "futuros_b3"
            pts = ibov.reindex(idx).ffill().to_numpy()
            nw = 0.0
            for i in range(1, T):
                h_pnl[i] += nw * WIN_MULT * pts[i - 1] * (rb[i] - cdi[i])   # futuro: rende Ibov - CDI sobre o nocional
                if muda[i] and np.isfinite(pts[i]):
                    novo = np.round(-hedge * netv[i] / (WIN_MULT * pts[i]))
                    if novo != nw:
                        h_pnl[i] -= abs(novo - nw) * WIN_CUSTO * custo_mult
                        nw = novo
    exc = (exc_acoes - perd + rfix - fin + h_pnl - h_cdi_perd + h_rfix) / capital
    excesso = pd.Series(exc, index=idx)
    # ---------------------------------------------------------------- classes de IR
    isento = {m: v <= LIMIAR_ISENCAO for m, v in vendas.items()}
    ac_is, ac = np.zeros(T), np.zeros(T)
    for pnl, mes in acao_pnl:
        if isento.get(mes, True) and not inst:
            ac_is += pnl
        else:
            ac += pnl
    classes = {"acoes_isentas": pd.Series(ac_is, index=idx), "acoes": pd.Series(ac - fin, index=idx),
               "renda_fixa": pd.Series(rfix + h_rfix, index=idx), classe_h: pd.Series(h_pnl, index=idx),
               "_cdi_perdido": pd.Series(perd + h_cdi_perd, index=idx)}
    contrib = pd.DataFrame(con, index=idx, columns=tk)
    # contribuição por papel em excesso (inclui o CDI perdido/ganho de cada episódio)
    E = pd.DataFrame(eps)
    if len(E):
        cp = np.zeros((T, len(tk)))
        for e in eps:
            a, b, j, s = e["_a"], e["_b"], e["_j"], e["_s"]
            seg = slice(a + 1, b + 1)
            v0 = e["valor_entrada"]
            vv = v0 * np.cumprod(1 + Rm[seg, j])
            vp = np.r_[v0, vv[:-1]]
            cp[seg, j] += -vp * cdi[seg] if s > 0 else v0 * cdi[seg]
        contrib = contrib + cp
        tot = []
        for e in eps:
            a, b, j = e["_a"], e["_b"], e["_j"]
            tot.append(contrib.iloc[a:b + 1, j].sum())
        # episódios sobrepostos no mesmo papel não existem (runs disjuntos) -> soma por janela é o episódio
        E["contrib_pp"] = np.array(tot) / capital * 100
        E["mes_saida"] = E["saida"].dt.to_period("M")
        E["isento"] = E["mes_saida"].map(lambda m: isento.get(m, True))
        if rotulos is not None and len(rotulos):
            rot = rotulos.sort_values("data")[["data", "ticker", "rotulo"]].rename(columns={"ticker": "ativo", "data": "_d"})
            E = pd.merge_asof(E.sort_values("entrada"), rot, left_on="entrada", right_on="_d", by="ativo", direction="backward",
                              tolerance=pd.Timedelta(days=30)).drop(columns="_d")
        E = E.drop(columns=["_j", "_a", "_b", "_s"])
    contrib["HEDGE"] = h_pnl - h_cdi_perd + h_rfix
    return {"excesso": excesso, "classes": classes, "episodios": E, "contrib": contrib, "vendas_mes": pd.Series(vendas, dtype=float),
            "financiamento": pd.Series(fin, index=idx)}


def negocios_de(res, capital):
    """Formato do contrato (ativo, lado, entrada, saida, dias, retorno_%, contrib_pp) + colunas extras; hedge numa linha por mês."""
    E = res["episodios"]
    out = E.copy() if len(E) else pd.DataFrame(columns=["ativo", "lado", "entrada", "saida", "dias", "retorno_%", "contrib_pp"])
    h = res["contrib"]["HEDGE"]
    if h.abs().sum() > 0:
        hm = h[h != 0].groupby(h[h != 0].index.to_period("M")).sum()
        hh = pd.DataFrame({"ativo": "HEDGE", "lado": 0, "entrada": [p.to_timestamp() for p in hm.index],
                           "saida": [p.to_timestamp(how="end").normalize() for p in hm.index], "dias": 21, "retorno_%": np.nan,
                           "contrib_pp": hm.values / capital * 100})
        out = pd.concat([out, hh], ignore_index=True)
    return out.sort_values("entrada").reset_index(drop=True)


def posicoes_de(W, R, extra=None):
    """(W, R) para placebo/atribuição: pesos decididos em t e retornos em excesso ao CDI."""
    Rx = R.reindex(index=DIAS, columns=W.columns).fillna(0).sub(C.CDI.reindex(DIAS).fillna(0), axis=0)
    W = W.reindex(DIAS).fillna(0)
    if extra is not None:
        W = W.copy()
        W["IBOV (hedge)"] = extra
        Rx["IBOV (hedge)"] = C.R_IBOV.reindex(DIAS).fillna(0) - C.CDI.reindex(DIAS).fillna(0)
    return W, Rx


# ---------------------------------------------------------------- calendário: dias do CDI sem pregão na B3 (feriados de SP, 24/12, último dia do ano)
_SEM_PREGAO = pd.DatetimeIndex([
    "2014-06-12", "2014-07-09", "2014-11-20", "2014-12-24", "2014-12-31", "2015-07-09", "2015-11-20", "2015-12-24", "2015-12-31",
    "2016-01-25", "2016-12-30", "2017-01-25", "2017-11-20", "2017-12-29", "2018-01-25", "2018-07-09", "2018-11-20", "2018-12-24",
    "2018-12-31", "2019-01-25", "2019-07-09", "2019-11-20", "2019-12-24", "2019-12-31", "2020-12-24", "2020-12-31", "2021-01-25",
    "2021-07-09", "2021-12-24", "2021-12-31", "2022-12-30", "2023-12-29", "2024-12-24", "2024-12-31", "2025-12-24", "2025-12-31"])


def sem_pregao():
    """Série booleana no calendário DIAS: True nos dias sem pregão (lista observada no COTAHIST 2014–2025 + regra fixa depois)."""
    x = pd.Series(DIAS.isin(_SEM_PREGAO), index=DIAS)
    fut = DIAS > "2025-12-31"
    md = DIAS.strftime("%m-%d")
    ult = pd.Series(DIAS, index=DIAS).groupby(DIAS.year).transform("max") == DIAS
    x[fut] = (pd.Index(md).isin(["01-25", "07-09", "11-20", "12-24", "12-31"]) | ult.values)[fut]
    return x


def antecipa_saida(W):
    """Se o dia de saída planejado (2 pregões depois da última decisão não nula, execução t+1) não tem pregão, sai no pregão anterior."""
    sp = sem_pregao().reindex(W.index).fillna(False).to_numpy()
    A = W.to_numpy().copy()
    T = len(A)
    for j in range(A.shape[1]):
        nz = A[:, j] != 0
        fim = np.flatnonzero(nz[:-1] & ~nz[1:])                   # último dia não nulo de cada sequência
        for k in fim:
            if k + 2 < T and sp[k + 2]:
                A[k, j] = 0.0
    return pd.DataFrame(A, index=W.index, columns=W.columns)


# ---------------------------------------------------------------- dados de eventos (lidos UMA vez da pesquisa institucional e guardados em pf/dados/rev_eventos/)
def _eb():
    """Módulo institucional de eventos (quant/fundos/ideias_eventos_br.py): painel COTAHIST com RJ/deslistadas + IPE/CVM."""
    p = str(U.QUANT / "fundos")
    if p not in sys.path:
        sys.path.insert(0, p)
    import ideias_eventos_br as eb
    return eb


def _ev_queda_bruto():
    """ev_queda do institucional SEM a exclusão de RJ (que olhava até 5 dias à frente); a exclusão causal é feita no módulo."""
    eb = _eb()
    p = eb.painel()
    R = p["R"]
    A = np.log1p(R.fillna(0).sub(eb.R_IBOV.reindex(R.index).fillna(0), axis=0))
    c3 = np.expm1(A.rolling(3).sum())
    noti = eb._noticia_ticker(p["P"])
    m = (c3 <= -.20) & (p["ADV"].shift(3) >= 5e6) & p["P"].notna() & noti
    st = m.stack()
    st = st[st]
    x = pd.DataFrame({"data": st.index.get_level_values(0), "ticker": st.index.get_level_values(1)})
    x["queda"] = [c3.at[d, t] for d, t in zip(x.data, x.ticker)]
    x = eb._primeiro(x, 30)
    return x.assign(rotulo="queda " + (x.queda * 100).round(0).astype(str) + "% em 3 dias").reset_index(drop=True)


def _leilao():
    eb = _eb()
    e = eb.eventos()
    x = e[e.a.str.contains("leilao", regex=False) & e.Categoria.isin(["Fato Relevante", "Comunicado ao Mercado"])]
    return x[["data", "ticker", "a"]].rename(columns={"a": "rotulo"}).reset_index(drop=True)


_FONTES = {"opa": lambda: _eb().ev_opa(), "leilao": _leilao, "oferta": lambda: _eb().ev_oferta(), "queda": _ev_queda_bruto,
           "rj": lambda: _eb().ev_rj()}


def eventos(nome):
    """Eventos com DATA DE DIVULGAÇÃO (Data_Entrega no IPE/CVM) -> DataFrame com coluna 'data' (o teste de truncamento corta por ela)."""
    def f():
        x = _FONTES[nome]().reset_index(drop=True)
        keep = [c for c in x.columns if c in ("data", "ticker", "oferta", "p0", "spread", "adv", "dinheiro", "rotulo", "queda", "s")]
        x = x[keep].copy()
        x["data"] = pd.to_datetime(x["data"])
        for c in x.columns:
            if x[c].dtype == object and c not in ("ticker", "rotulo"):
                x[c] = x[c].astype(float)
        return x
    return U.cache(f"rev_eventos/{nome}", f)


def painel(tickers, nome):
    """Painel longo (data, ticker, P não ajustado, R retorno total ajustado, V volume R$) do COTAHIST completo (com RJ/deslistadas)."""
    def f():
        p = _eb().painel()
        tk = sorted(set(tickers) & set(p["P"].columns))
        out = []
        for c, k in (("P", "P"), ("R", "R"), ("V", "V")):
            s = p[k][tk].stack(dropna=True) if hasattr(p[k][tk], "stack") else None
            out.append(s.rename(c))
        x = pd.concat(out, axis=1).reset_index()
        x.columns = ["data", "ticker", "P", "R", "V"]
        return x
    return U.cache(f"rev_eventos/painel_{nome}", f)


def largo(pn):
    """Painel longo -> P, R, ADV largos no calendário DIAS (ADV = média de 60 pregões do volume, zeros nos dias sem negócio)."""
    P = pn.pivot(index="data", columns="ticker", values="P").reindex(DIAS)
    R = pn.pivot(index="data", columns="ticker", values="R").reindex(DIAS)
    V = pn.pivot(index="data", columns="ticker", values="V").reindex(DIAS)
    V.loc[sem_pregao().reindex(DIAS).values] = np.nan
    ADV = V.fillna(0).rolling(60, min_periods=20).mean()
    return P, R, ADV


# ---------------------------------------------------------------- regime aplicado também às classes de IR
def regime_serie(e, nome):
    """Mesma escala de comum.aplica_regime (sinal de mercado de t-2; dd_stop da própria cota com shift(1))."""
    if nome in (None, "nenhum"):
        return None
    if nome == "dd_stop":
        return C.regime_dd_stop(e)
    s = {"risco_global": C.regime_risco_global, "ibov_tendencia": C.regime_ibov_tendencia}[nome]()
    return s.reindex(e.index).ffill().fillna(1.0).shift(2).fillna(1.0)


def com_regime(res, nome, custo_troca, capital):
    """Devolve (excesso, classes) com o regime aplicado; o custo de liga/desliga entra na classe 'acoes'."""
    e = res["excesso"]
    s = regime_serie(e, nome)
    if s is None:
        return e, res["classes"]
    troca = s.diff().abs().fillna(0) * custo_troca
    cl = {k: v * s for k, v in res["classes"].items()}
    cl["acoes"] = cl["acoes"] - troca * capital
    return e * s - troca, cl


# ---------------------------------------------------------------- pesos de livros de eventos (igual ao institucional ideias_eventos_br.posicoes)
def pesos_eventos(ev, hold, n_max, ini="2014-01-02"):
    """Cada evento vale s/n_max do capital por `hold` pregões a partir do dia da divulgação (decisão no fechamento; novo evento no mesmo
    papel renova o prazo); com mais de n_max posições todas são reduzidas (bruto máx. 100%)."""
    idx = DIAS[DIAS >= ini]
    tks = sorted(ev.ticker.unique())
    A = np.zeros((len(idx), len(tks)))
    col = {t: j for j, t in enumerate(tks)}
    i0 = idx.searchsorted(pd.to_datetime(ev["data"]).values)
    for i, t, s in zip(i0, ev.ticker, ev["s"]):
        if i < len(idx):
            A[i:i + int(hold), col[t]] = s
    W = pd.DataFrame(A, index=idx, columns=tks) / n_max
    W = W.div(np.maximum(W.abs().sum(axis=1), 1), axis=0)
    return W.reindex(DIAS).fillna(0)


def aluguel_inst(adv):
    """Aluguel do motor institucional: 1% (ADV >= 50 mi), 3% (>= 10 mi), 8% a.a."""
    adv = adv.reindex(DIAS).ffill()
    return pd.DataFrame(np.select([adv >= 50e6, adv >= 10e6], [.01, .03], .08), index=adv.index, columns=adv.columns)


def etfs():
    """SMAL11 (Yahoo, fechamento) para hedge de tamanho."""
    def f():
        y = pd.read_parquet(U.FD / "y_br_local.parquet")
        y.index = pd.DatetimeIndex(y.index).tz_localize(None).normalize()
        return y[["SMAL11.SA", "BOVA11.SA"]].rename(columns=lambda c: c[:-3])
    return U.cache("rev_eventos/etfs", f)


def btc_b3(tickers=None):
    """Taxas REAIS de aluguel da B3 (BDI 04-2, 'Empréstimos registrados' + 'Posições em aberto'), dez/2025 a out/2026, a cada 3 pregões.
    Colunas: data, ticker, tomador_med (% a.a.), valor (R$ emprestado no dia), saldo_rs (posição em aberto R$). Fonte:
    https://arquivos.b3.com.br/bdi/download/bdi/AAAA-MM-DD/BDI_04-2_AAAAMMDD.pdf"""
    x = pd.read_parquet(U.CACHE / "btc" / "btc_taxas_b3.parquet")
    if tickers is not None:
        x = x[x.ticker.isin(set(tickers))]
    return x[["data", "ticker", "tomador_med", "valor", "saldo_rs", "contratos"]].reset_index(drop=True)



# ---------------------------------------------------------------- taxa de aluguel ao doador (a.a.) — modelo calibrado nas taxas REAIS da B3
# Calibração (scratch calib_btc.py, fora do repositório): 18.231 observações papel-dia COM empréstimo registrado no dia (BDI 04-2,
# 70 datas de 15/12/2025 a 13/10/2026, 378 ações). OLS da taxa tomador média (% a.a.) em: (7,5 − log10 ADV60)+, queda de 60 pregões,
# vol de 20 pregões, preço < R$ 2, alta de 60 pregões acima de 30%. R² 0,17, mas a média por decil do previsto bate a média real
# (0,6% -> 10,5% a.a.). Média real por faixa: ADV >= R$ 100 mi 2,3% (mediana 0,09%); ADV < R$ 1 mi 6,4%; queda 60d > 40% 10,2%
# (p90 21%); vol > 120% 12,7%. Disponibilidade: com ADV60 >= R$ 300 mil ~97% dos papéis têm saldo de empréstimo em aberto; abaixo, 64%
# -> exigimos ADV60 >= R$ 1 mi para vender.
# Efeito do EVENTO (papéis com evento entre dez/2025 e out/2026, taxa real na 1ª data B3 até 30 dias depois do evento vs modelo):
#   follow-on (11 eventos): real média 4,5% vs modelo 2,0% (2,2x); máximo em 30 dias 7,6% (3,8x: PINE4 29%, CSMG3 6%->30%, EGIE3 ->15%)
#   queda > 20% (21 eventos): real média 15,9% vs modelo 10,1% (1,6x); máximo em 30 dias 2,0x (RAIZ4 44–74%, BHIA3 20–55%, BRKM5 27–36%)
# -> multiplicador conservador por tipo de evento (passado pelo módulo): follow-on 3x, crise 2x.
# Quando a B3 já publicou taxa do papel até a data (dez/2025+), usa-se a taxa REAL (média ponderada do dia, ffill até 10 pregões).
COEF_TAXA = (-0.756, 1.335, 3.620, 6.158, 1.914, 2.474)       # em % a.a.
TAXA_PISO = .002
ADV_MIN_ALUGUEL = 1e6


def taxa_modelo(adv, R, P):
    """Taxa média esperada ao doador (fração a.a.) com dados até t (ADV de t-1, retornos e vol até t)."""
    adv = adv.reindex(DIAS).ffill()
    lr = np.log1p(R.reindex(DIAS).fillna(0))
    ladv = np.log10(adv.shift(1).clip(lower=1e4))
    r60 = np.expm1(lr.rolling(60, min_periods=20).sum())
    vol = R.reindex(DIAS).rolling(20, min_periods=10).std() * np.sqrt(252)
    px = P.reindex(DIAS).ffill()
    b = COEF_TAXA
    t = (b[0] + b[1] * (7.5 - ladv).clip(0, 3) + b[2] * (-r60).clip(0, 1) + b[3] * vol.clip(0, 2) + b[4] * (px < 2)
         + b[5] * (r60 - .3).clip(0, 2)) / 100
    return t.clip(lower=TAXA_PISO).where(adv.shift(1) >= ADV_MIN_ALUGUEL)


def taxa_aluguel(adv, R, P, btc=None, mult=1.0, piso=0.0, teto=.30):
    """Taxa ao doador por papel e dia (fração a.a.); NaN = não aluga (sem doador ou taxa acima do teto -> o livro não vende).
    mult: prêmio do evento sobre o modelo (só onde não há taxa B3 publicada); piso: taxa mínima (cenário de estresse)."""
    t = taxa_modelo(adv, R, P) * mult
    if btc is not None and len(btc):
        b = btc[btc.ticker.isin(t.columns)].pivot_table(index="data", columns="ticker", values="tomador_med", aggfunc="max") / 100
        b = b.reindex(DIAS).ffill(limit=10).reindex(columns=t.columns)
        t = b.where(b.notna(), t).where(t.notna() | b.notna())
    t = np.maximum(t, piso).where(t.notna())
    return t.where(t <= teto)
