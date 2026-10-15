"""
DI1 x Focus reunião a reunião — "Copom com tamanho de varejo" (pessoa física em corretora que oferece DI1: XP, BTG, Genial, Safra).

Tese de mesa: o DI1 de 6–12 meses é a soma das decisões do Copom esperadas + prêmio. Quando a curva curta precifica Selic bem acima
do caminho reunião a reunião do Focus (choque de RISCO: o mercado paga para se proteger), recebo taxa (comprado em PU) e espero o
prêmio fechar; se `lado`="ambos", também pago taxa quando a curva precifica cortes que o Focus não vê. O risco é o de 2021/2024:
o Focus estava atrás do BC e o "prêmio" era informação.
Varejo: DI1 vale R$ 100 mil no vencimento e não tem mini; DV01 de ~R$ 4,5 (6 meses) a ~R$ 8 (1 ano) por bp por contrato. Com R$ 20 mil
o tamanho honesto é 1–3 contratos (100 bps = ~5% do capital). A margem fica em Tesouro Selic (rende CDI); o ajuste diário da B3 já é o
P&L em EXCESSO ao CDI (ajuste = PU - PU anterior x (1+CDI), conferido no arquivo).

Implementação:
  - CDI esperado até o vencimento do contrato: Selic meta vigente, e depois de cada reunião do Copom a mediana do Focus para ESSA
    reunião (coleta de t-1); datas de reunião do calendário do BC (divulgado com 1 ano de antecedência); CDI = Selic - 0,10;
  - prêmio = taxa de ajuste do DI1 de referência (vencimento mais perto de `prazo` anos) - CDI esperado; entra com |prêmio| >= thr,
    sai quando o prêmio volta a thr/4; contrato travado até faltarem 3 meses (aí rola);
  - contratos INTEIROS: n = round(alavancagem x 5% do capital / (DV01 x 100)); se arredondar para 0, não opera;
  - custos por contrato e lado: emolumentos/registro B3 ~R$ 1,10 + corretagem R$ 5 (XP cobra R$ 16 no swing; BTG/Genial menos) + meio
    tick (0,5 bp x DV01); margem B3 estimada em 1,5% do PU por contrato (sem tabela pública por vencimento; CORE da B3) — se o patrimônio
    cair abaixo da margem, corta contratos (chamada de margem); patrimônio <= 0 = quebra.
  - IR: futuros B3, 15% sobre o ganho anual (classe "futuros_b3"); a margem em Tesouro Selic é CDI (benchmark).
Dados: ajustes DI1 B3 2019+, Focus Selic por reunião (BCB/Olinda), calendário do Copom (BCB). Corte OOS 2023-01-01.
"""
import numpy as np
import pandas as pd

import _rf_comum as K

NOME = "DI1 x Focus reunião a reunião (Copom de varejo)"
TESE = ("Recebo DI1 de 6–12 meses quando a curva curta precifica Selic bem acima do caminho do Focus reunião a reunião (prêmio de "
        "risco) e saio quando o prêmio fecha; contratos inteiros, margem em Tesouro Selic")
BENCHMARK = "CDI"
INICIO, CORTE = "2019-03-01", "2023-01-01"
REGIME = "nenhum"
CUSTO_TROCA = 0.0
PARAMS = {"thr": 0.25, "prazo": 0.5, "lado": "ambos"}          # escolhidos no IS (maior IR 2019-03 a 2022)
GRADE = {"thr": [0.25, 0.5], "prazo": [0.5, 1.0], "lado": ["recebe", "ambos"]}
VIZINHANCA = {"thr": (0.15, 0.4), "prazo": (0.35, 0.75)}
CLASSE_IR = "futuros_b3"
ALIQUOTAS = None
RISCO = .05                    # perda de 5% do capital para 100 bps contra (alavancagem 1)
B3_FEE, CORRETAGEM, MEIO_TICK_BP, MARGEM = 1.10, 5.0, .5, .015
INSTRUMENTOS = [{"onde": "XP / BTG / Genial / Safra (DI1 para PF; Clear/Rico não oferecem)", "ticker": "DI1F27, DI1N27... (contrato mais perto de 6–12 meses)",
                 "lote": "1 contrato = R$ 100 mil no vencimento (DV01 ~R$ 4,5–8/bp)",
                 "custo": "B3 ~R$ 1,10 + corretagem R$ 0–16 + meio tick por contrato e lado; margem ~1,5% do PU em Tesouro Selic"}]
APLICAVEL = True
MOTIVO = ("Opera com 1–3 contratos com R$ 20 mil (3–7 com R$ 50 mil); exige corretora que libere DI1 para PF (XP, BTG, Genial) — "
          "Clear/Rico/Nubank/Inter não oferecem.")
ALAVANCAGENS = [1, 2, 5]
MOTIVO_ALAV = "1,5x arredonda para os mesmos contratos de 1x/2x com R$ 20 mil; 5x = 100 bps contra custam 25% do capital (margem ainda cabe)."
MES = {c: i + 1 for i, c in enumerate("FGHJKMNQUVXZ")}


def carrega():
    return {"di1": K.ler("di1.parquet"), "focus_r": K.ler("focus_selic_reuniao.parquet").rename(columns={"Data": "data"}),
            "selic": K.ler("selic_meta.csv"), "copom": K.ler("copom_reunioes.csv")}


def _venc(tk):
    """DI1 vence no 1º dia útil do mês do código (aprox.: dia 1)."""
    return pd.Timestamp(2000 + int(tk[4:6]), MES[tk[3]], 1)


def _paineis(d):
    def f():
        x = d["di1"]
        x = x[x.ticker.str.match(r"^DI1[FGHJKMNQUVXZ]\d\d$")]
        tx = x.pivot_table(index="data", columns="ticker", values="taxa", aggfunc="last").reindex(K.DIAS)
        pu = x.pivot_table(index="data", columns="ticker", values="pu", aggfunc="last").reindex(K.DIAS)
        aj = x.pivot_table(index="data", columns="ticker", values="ajuste_rs", aggfunc="last").reindex(K.DIAS)
        ve = pd.Series({c: _venc(c) for c in tx.columns})
        prazo = pd.DataFrame({c: (ve[c] - K.DIAS).days / 365.25 for c in tx.columns}, index=K.DIAS)
        du = pd.DataFrame({c: np.maximum((ve[c] - K.DIAS).days * 252 / 365.25, 1) for c in tx.columns}, index=K.DIAS)
        dv01 = pu * (du / 252) / (1 + tx / 100) * 1e-4
        return {"tx": tx, "pu": pu, "aj": aj.fillna(0), "venc": ve, "prazo": prazo, "dv01": dv01}
    return K.memo("di1p", d["di1"], f)


def _datas_reuniao(d):
    """Ri/AAAA -> data da i-ésima reunião ordinária do ano (calendário do BC); anos sem calendário: a cada ~46 dias desde 28/jan."""
    h = d["copom"]
    h = h[~h.ReuniaoExtraordinaria.astype(bool)].copy()
    h["dt"] = pd.to_datetime(h.DataReuniaoCopom)
    out = {}
    for ano, g in h.groupby(h.dt.dt.year):
        for i, dt in enumerate(sorted(g.dt), 1):
            out[f"R{i}/{ano}"] = dt
    for ano in range(2000, 2032):
        for i in range(1, 9):
            out.setdefault(f"R{i}/{ano}", pd.Timestamp(ano, 1, 28) + pd.Timedelta(days=46 * (i - 1)))
    return out


def cdi_esperado_reuniao(d, prazos):
    """CDI médio esperado (% a.a.) de t até t + prazo (prazos: DataFrame dias x contratos, em anos), pelo Focus reunião a reunião."""
    def f():
        fr = d["focus_r"]
        F = fr.pivot_table(index="data", columns="Reuniao", values="Mediana", aggfunc="last").sort_index()
        F = F.reindex(F.index.union(K.DIAS)).ffill(limit=10).reindex(K.DIAS).shift(1)          # coleta de t-1
        dr = _datas_reuniao(d)
        cols = [c for c in F.columns if c in dr]
        datas = np.array([dr[c] for c in cols], dtype="datetime64[ns]")
        o = np.argsort(datas)
        return F[np.array(cols)[o]], datas[o]
    F, datas = K.memo("focus_r", d["focus_r"], f)
    sm = K.selic_meta(d).to_numpy()
    Fv = F.to_numpy()
    P = prazos.to_numpy(dtype=float)
    out = np.full(P.shape, np.nan)
    for t in range(len(K.DIAS)):
        if not np.isfinite(P[t]).any() or np.isnan(sm[t]):
            continue
        hoje = np.datetime64(K.DIAS[t])
        fut = datas > hoje
        xs = (datas[fut] - hoje).astype("timedelta64[D]").astype(float) / 365.25
        ys = Fv[t, fut]
        ok = np.isfinite(ys)
        xs, ys = xs[ok], ys[ok]
        for j in np.flatnonzero(np.isfinite(P[t])):
            T = P[t, j]
            if T <= 0:
                continue
            if len(xs) == 0 or xs[0] > T + .5:            # Focus não cobre: sem sinal
                continue
            grid = np.linspace(0, T, max(int(T * 365 / 7), 2))
            idx = np.searchsorted(xs, grid, side="left")                 # quantas reuniões já passaram em cada ponto
            sel = np.where(idx == 0, sm[t], ys[np.clip(idx - 1, 0, len(ys) - 1)]) - .10
            out[t, j] = (np.exp(np.mean(np.log1p(sel / 100))) - 1) * 100
    return pd.DataFrame(out, index=prazos.index, columns=prazos.columns)


def _referencia(p, prazo):
    P = p["prazo"].where(p["tx"].notna() & (p["prazo"] > .25))
    P = P.where((P >= .5 * prazo) & (P <= 1.6 * prazo))
    dd = (P - prazo).abs()
    ok = dd.notna().any(axis=1)
    return dd.fillna(1e9).idxmin(axis=1).where(ok)


def _sinal(d, thr, prazo, lado):
    p = _paineis(d)
    ref = _referencia(p, prazo)
    cols = sorted(set(ref.dropna()))
    Pr = p["prazo"][cols].where(pd.DataFrame({c: ref == c for c in cols}))
    esp = cdi_esperado_reuniao(d, Pr)
    tx = p["tx"][cols].where(Pr.notna())
    prem = (tx - esp).max(axis=1, skipna=True).where((tx - esp).notna().any(axis=1))
    st = np.zeros(len(K.DIAS))
    s = 0
    pv = prem.to_numpy()
    for t in range(len(pv)):
        if np.isfinite(pv[t]):
            if s == 0:
                if pv[t] >= thr:
                    s = 1
                elif lado == "ambos" and pv[t] <= -thr:
                    s = -1
            elif s == 1 and pv[t] <= thr / 4:
                s = 0
            elif s == -1 and pv[t] >= -thr / 4:
                s = 0
        st[t] = s
    return p, ref, pd.Series(st, index=K.DIAS), prem


def _simula(d, capital=20000, custo_mult=1, lag=0, alavancagem=1, thr=PARAMS["thr"], prazo=PARAMS["prazo"], lado=PARAMS["lado"]):
    p, ref, st, prem = _sinal(d, thr, prazo, lado)
    T = len(K.DIAS)
    aj, dv, pu, pz = p["aj"], p["dv01"], p["pu"], p["prazo"]
    k0 = 1 + lag
    pos_c, n = None, 0.0            # contrato e nº de contratos (+ = recebido / comprado em PU)
    E = capital
    pnl = np.zeros(T)
    trades, cur = [], None
    chamadas, quebra = 0, None
    stv, refv = st.to_numpy(), ref.to_numpy()
    for t in range(1, T):
        if quebra is not None:
            continue
        g = n * aj[pos_c].iat[t] if pos_c is not None else 0.0
        pnl[t] += g
        E += g
        if cur is not None:
            cur["pnl"] += g
        if E <= 0:
            quebra = K.DIAS[t]
            pnl[t] -= E
            n, pos_c = 0.0, None
            continue
        s = t - k0
        if s < 0:
            continue
        if not np.isfinite(p["tx"].iloc[t].to_numpy(dtype=float)).any():
            continue                                                  # sem pregão de DI1 no dia (24/12, 31/12...): não negocia
        alvo_s = stv[s]
        alvo_c = pos_c
        if alvo_s != 0:
            if pos_c is None or pz[pos_c].iat[t] < .25 or np.sign(n) != alvo_s:
                alvo_c = refv[s] if isinstance(refv[s], str) else None
        else:
            alvo_c = None
        if pos_c is not None and not np.isfinite(dv[pos_c].iat[t]):
            continue                                                  # contrato atual sem preço hoje: espera
        if alvo_c is not None and not np.isfinite(dv[alvo_c].iat[t]):
            alvo_c = pos_c if pos_c is not None and np.isfinite(dv[pos_c].iat[t]) else None
        if alvo_c is not None:
            if alvo_c == pos_c and np.sign(n) == alvo_s:
                n_alvo = n                                           # segura (não re-dimensiona todo dia)
            else:
                n_alvo = alvo_s * np.round(alavancagem * RISCO * capital / (dv[alvo_c].iat[t] * 100))
            marg = abs(n_alvo) * MARGEM * pu[alvo_c].iat[t]
            if marg > E and n_alvo != 0:
                n_novo = np.sign(n_alvo) * np.floor(E / (MARGEM * pu[alvo_c].iat[t]))
                if alvo_c == pos_c and n_novo != n:
                    chamadas += 1
                n_alvo = n_novo
        else:
            n_alvo = 0.0
        if alvo_c != pos_c or n_alvo != n:
            def custo(c, q):
                return abs(q) * (B3_FEE + CORRETAGEM + MEIO_TICK_BP * dv[c].iat[t]) * custo_mult if (q and c is not None) else 0.0
            if alvo_c != pos_c or n_alvo == 0:                     # fecha o negócio atual (inteiro)
                c_fecha = custo(pos_c, n)
                pnl[t] -= c_fecha
                E -= c_fecha
                if cur is not None:
                    cur["pnl"] -= c_fecha
                    trades.append({**cur, "saida": K.DIAS[t], "premio_saida": prem.iat[s]})
                    cur = None
                if n_alvo != 0:                                     # abre o novo
                    c_abre = custo(alvo_c, n_alvo)
                    pnl[t] -= c_abre
                    E -= c_abre
                    cur = {"ativo": alvo_c, "lado": int(np.sign(n_alvo)), "entrada": K.DIAS[t], "contratos": abs(n_alvo),
                           "taxa_entrada": p["tx"][alvo_c].iat[t], "premio_entrada": prem.iat[s], "pnl": -c_abre}
            else:                                                   # mesmo contrato, ajusta a quantidade (chamada de margem)
                c_aj = custo(pos_c, n_alvo - n)
                pnl[t] -= c_aj
                E -= c_aj
                if cur is not None:
                    cur["pnl"] -= c_aj
            pos_c, n = (alvo_c, n_alvo) if n_alvo != 0 else (None, 0.0)
    if cur is not None:
        trades.append({**cur, "saida": K.DIAS[-1], "premio_saida": prem.iat[-1]})
    e = pd.Series(pnl / capital, index=K.DIAS)
    ng = pd.DataFrame(trades)
    if len(ng):
        ng["dias"] = [int(((K.DIAS >= a) & (K.DIAS <= b)).sum()) for a, b in zip(ng.entrada, ng.saida)]
        ng["contrib_pp"] = ng.pnl / capital * 100
        ng["retorno_%"] = ng.contrib_pp
    return e, ng, {"chamadas de margem": chamadas, "quebrou em": quebra}


def excesso(d, capital=20000, custo_mult=1, lag=0, regime=REGIME, alavancagem=1, **params):
    e, _, diag = _simula(d, capital, custo_mult, lag, alavancagem, **{**PARAMS, **params})
    e = K.C.aplica_regime(e, regime, CUSTO_TROCA * custo_mult)
    e.attrs.update(diag)
    return e


def classes_ir(d, capital=20000, **params):
    e, _, _ = _simula(d, capital, **{**PARAMS, **params})
    return {CLASSE_IR: e * capital}


def posicoes(d, **params):
    p_ = {**PARAMS, **params}
    p, ref, st, _ = _sinal(d, p_["thr"], p_["prazo"], p_["lado"])
    cols = sorted(set(ref.dropna()))
    W = pd.DataFrame({c: st.where(ref == c, 0.0) for c in cols})
    R = (p["aj"][cols] / p["pu"][cols].shift(1)).fillna(0)             # excesso por R$ de PU (aprox.)
    return W, R


def negocios(d, capital=20000, **params):
    return _simula(d, capital, **{**PARAMS, **params})[1]
