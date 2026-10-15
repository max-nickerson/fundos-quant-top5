"""
Peças comuns da frente "renda_fixa" (pf/fundos/rf_*.py). Não altera comum.py/robustez.py/pf.py.

Convenções (iguais às da frente "revisita", pf/fundos/_util.py):
  - excesso(...) devolve o excesso diário sobre o CDI (fração do capital, antes do IR), calendário comum.DIAS;
  - dinheiro aplicado no ativo NÃO rende CDI: o excesso da parcela aplicada é (retorno do ativo - CDI); o resto do capital fica no CDI;
  - classes_ir(d, capital, **params) -> dict classe -> P&L diário REAL em R$ (ganho tributável da classe) + "_cdi_perdido" (R$ de CDI
    que o capital aplicado deixou de ganhar) + "_ir_extra" (R$ de IR além dos 15% da classe: tabela regressiva da renda fixa,
    lançado na data da venda). Excesso antes do IR = (soma das classes - _cdi_perdido) / capital.
    Depois do IR = [pf.apos_ir_por_classe(classes, aliquotas=ALIQUOTAS) - 0,85 x _cdi_perdido - _ir_extra] / capital, contra o CDI líquido.
  - posição "compra e segura": entra com o peso-alvo (lotes inteiros) e depois o peso deriva com o preço (sem rebalancear: com
    preços ruidosos o rebalanceamento diário fabrica ganho — bug conhecido da pesquisa de crédito).
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

PF = Path(__file__).resolve().parent.parent
RAIZ = PF.parent
for _p in (str(RAIZ), str(PF)):
    if _p not in sys.path:
        sys.path.insert(0, _p)
import comum as C  # noqa: E402
import pf  # noqa: E402

DADOS = PF / "dados" / "renda_fixa"
DIAS = C.DIAS
CDI = C.CDI.reindex(DIAS).fillna(0)
CDI_AA = ((1 + CDI) ** 252 - 1) * 100
CUSTODIA_TD = .002            # B3: 0,20% a.a. sobre o saldo de títulos do Tesouro Direto (Tesouro Selic isento até R$ 10 mil)
_MEMO = {}


def ler(nome, data="data"):
    """Lê um arquivo de pf/dados/renda_fixa (dados brutos). Séries pequenas viram DataFrame com índice de data."""
    p = DADOS / nome
    x = pd.read_parquet(p) if p.suffix == ".parquet" else pd.read_csv(p)
    if p.suffix == ".csv" and data in x.columns:
        x[data] = pd.to_datetime(x[data])
        x = x.set_index(data)
    return x


def memo(nome, fonte, f):
    """Cache por OBJETO de dados (o teste de truncamento cria DataFrames novos; guardamos a referência para o id não ser reaproveitado)."""
    k = (nome, id(fonte))
    if k not in _MEMO or _MEMO[k][0] is not fonte:
        _MEMO[k] = (fonte, f())
    return _MEMO[k][1]


def aliquota_rf(dias_corridos):
    """IR regressivo da renda fixa tributada (Lei 11.033/2004)."""
    d = np.asarray(dias_corridos)
    return np.select([d <= 180, d <= 360, d <= 720], [.225, .20, .175], .15)


# ============================================================================ livro de posições (compra e segura)
def livro(alvo, R, capital, lag=0, custo_ent=0.0, custo_sai=0.0, custo_mult=1.0, lote=None, negocia=None, vivo=None,
          custodia=0.0, regressivo=False, ir_aliq=.15, R2=None):
    """alvo: DataFrame (dias x ativos) com o peso-alvo (fração do capital) decidido no fechamento de t (0 = fora).
    Execução no fechamento de t+1+lag (se o ativo negocia nesse dia; senão no 1º dia em que negociar). Entra com lotes inteiros
    (`lote` = R$ por unidade) e segura até o alvo zerar ou o ativo morrer (vencimento/sem preço -> sai sem custo).
    R: retorno total diário do ativo (marcado pelo preço de SAÍDA: PU de venda/recompra, bid). custo_ent / custo_sai: fração do valor.
    R2 (opcional): parte do retorno que é provento (para separar a classe de IR: rendimento de FII isento x ganho de capital).
    Devolve dict com e (excesso diário), pnl (fração do capital, real, por ativo), perd (CDI perdido), pnl2 (parte R2), v, negocios, ir_extra."""
    dias = DIAS
    cols = list(alvo.columns)
    T, K = len(dias), len(cols)
    A = alvo.reindex(index=dias, columns=cols).fillna(0).to_numpy(dtype=float)
    Rn = R.reindex(index=dias, columns=cols).fillna(0).to_numpy(dtype=float)
    R2n = R2.reindex(index=dias, columns=cols).fillna(0).to_numpy(dtype=float) if R2 is not None else np.zeros((T, K))
    pnl2 = np.zeros((T, K))

    def _m(x, fill):
        if isinstance(x, pd.DataFrame):
            return x.reindex(index=dias, columns=cols).fillna(fill).to_numpy(dtype=float)
        return np.full((T, K), float(x))

    CE, CS = _m(custo_ent, 0) * custo_mult, _m(custo_sai, 0) * custo_mult
    L = _m(lote, np.nan) if lote is not None else None
    NG = negocia.reindex(index=dias, columns=cols).fillna(False).to_numpy() if negocia is not None else np.ones((T, K), bool)
    VV = vivo.reindex(index=dias, columns=cols).fillna(False).to_numpy() if vivo is not None else np.ones((T, K), bool)
    cdi = CDI.to_numpy()
    v = np.zeros(K)
    pnl = np.zeros((T, K))          # fração do capital, P&L real (retorno total) já com custos
    perd = np.zeros((T, K))
    V = np.zeros((T, K))
    held, trades = {}, []
    irx = np.zeros(T)
    for t in range(1, T):
        # 1) quem estava na carteira no fechamento de t-1 rende o dia t
        if held:
            g = v * Rn[t]
            pnl[t] += g - v * custodia / 252 * custo_mult
            pnl2[t] += v * R2n[t]
            perd[t] += v * cdi[t]
            v = v * (1 + Rn[t] - cdi[t])                 # peso relativo ao patrimônio (que cresce ~ CDI)
        s = t - 1 - lag
        if s >= 0:
            # 2) saídas
            for k in list(held):
                morto = not VV[t, k]
                if morto or (A[s, k] <= 0 and NG[t, k]):
                    c = 0.0 if morto else v[k] * CS[t, k]
                    pnl[t, k] -= c
                    h = held.pop(k)
                    ganho = pnl[h["i"]:t + 1, k].sum()
                    dc = (dias[t] - dias[h["i"]]).days
                    if regressivo and ganho > 0:
                        irx[t] += ganho * (float(aliquota_rf(dc)) - ir_aliq)
                    trades.append((cols[k], dias[h["i"]], dias[t], dc, h["w"], ganho, "vencimento/sem preço" if morto else "sinal"))
                    v[k] = 0.0
            # 3) entradas
            for k in np.flatnonzero(A[s] > 0):
                if k in held or not NG[t, k] or not VV[t, k]:
                    continue
                w = A[s, k]
                if L is not None:
                    if not np.isfinite(L[t, k]) or L[t, k] <= 0:
                        continue
                    w = np.floor(w * capital / L[t, k] + 1e-9) * L[t, k] / capital
                if w <= 0:
                    continue
                v[k] = w
                pnl[t, k] -= w * CE[t, k]
                held[k] = {"i": t, "w": w}
        V[t] = v
    for k, h in held.items():
        trades.append((cols[k], dias[h["i"]], dias[-1], (dias[-1] - dias[h["i"]]).days, h["w"], pnl[h["i"]:, k].sum(), "aberta"))
    e = pd.Series((pnl - perd).sum(axis=1), index=dias)
    ng = pd.DataFrame(trades, columns=["ativo", "entrada", "saida", "dias_corridos", "peso", "ganho", "motivo_saida"])
    if len(ng):
        con = pd.DataFrame(pnl - perd, index=dias, columns=cols)
        ng["dias"] = [int(((dias >= a) & (dias <= b)).sum()) for a, b in zip(ng.entrada, ng.saida)]
        ng["contrib_pp"] = [con[a].loc[i:f].sum() * 100 for a, i, f in zip(ng.ativo, ng.entrada, ng.saida)]
        ng["retorno_%"] = ng.ganho / ng.peso * 100
        ng["lado"] = 1
        ng = ng[["ativo", "lado", "entrada", "saida", "dias", "dias_corridos", "peso", "retorno_%", "contrib_pp", "motivo_saida"]]
    return {"e": e, "pnl": pd.DataFrame(pnl, index=dias, columns=cols), "perd": pd.DataFrame(perd, index=dias, columns=cols),
            "v": pd.DataFrame(V, index=dias, columns=cols), "negocios": ng, "ir_extra": pd.Series(irx, index=dias),
            "pnl2": pd.DataFrame(pnl2, index=dias, columns=cols)}


def classes_de_livro(L, capital, classe):
    """Converte a saída do livro (fração do capital) nas classes de IR em R$ (convenção do módulo)."""
    return {classe: L["pnl"].sum(axis=1) * capital, "_cdi_perdido": L["perd"].sum(axis=1) * capital,
            "_ir_extra": L["ir_extra"] * capital}


def excesso_apos_ir(cls, capital, aliquotas=None):
    """Excesso diário DEPOIS do IR sobre o CDI líquido (fração do capital), a partir das classes."""
    cls = {k: v.reindex(DIAS).fillna(0) for k, v in cls.items()}
    perd = cls.pop("_cdi_perdido", pd.Series(0.0, index=DIAS))
    irx = cls.pop("_ir_extra", pd.Series(0.0, index=DIAS))
    return (pf.apos_ir_por_classe(cls, capital, aliquotas) - .85 * perd - irx) / capital


# ============================================================================ Tesouro Direto
def tesouro(d, tipo):
    """Painéis (dias x vencimento) de taxa e PU de compra/venda de um tipo de título do Tesouro Direto (d["td"])."""
    return memo(("td", tipo), d["td"], lambda: _tesouro(d["td"], tipo))


def _tesouro(t, tipo):
    if True:
        t = t[t.tipo == tipo]
        t = t[t.data <= DIAS[-1]]
        out = {}
        for c in ("tx_compra", "tx_venda", "pu_compra", "pu_venda"):
            x = t.pivot_table(index="data", columns="venc", values=c, aggfunc="last")
            out[c] = x.reindex(DIAS).ffill(limit=6)
        obs = t.pivot_table(index="data", columns="venc", values="pu_venda", aggfunc="last").reindex(DIAS).notna()
        vencs = out["pu_venda"].columns
        fim = obs.index[obs.any(axis=1)].max()
        ultimo = {v: obs[v][obs[v]].index.max() for v in vencs}
        ultimo = {v: (DIAS[-1] if u == fim else u) for v, u in ultimo.items()}     # vivo no fim dos dados = posição aberta
        vivo = pd.DataFrame({v: (DIAS <= ultimo[v]) & (DIAS < v) for v in vencs}, index=DIAS) & out["pu_venda"].notna()
        R = out["pu_venda"].pct_change(fill_method=None).where(vivo).fillna(0)
        out.update(vivo=vivo, R=R, obs=obs.reindex(columns=vencs).fillna(False) & vivo, prazo=pd.DataFrame({v: (v - DIAS).days / 365.25 for v in vencs}, index=DIAS))
    return out


def escolhe_vencimento(td, prazo, faixa=(.6, 1.6)):
    """Para cada dia, o vencimento vivo com prazo mais perto de `prazo` anos (dentro de faixa x prazo). Devolve Series de vencimentos."""
    P = td["prazo"].where(td["vivo"])
    P = P.where((P >= faixa[0] * prazo) & (P <= faixa[1] * prazo))
    d = (P - prazo).abs()
    ok = d.notna().any(axis=1)
    return pd.to_datetime(d.fillna(1e9).idxmin(axis=1)).where(ok)


def alvo_de_vencimento(venc, ligado, cols, peso=1.0):
    """DataFrame de pesos-alvo: peso no vencimento escolhido nos dias `ligado` (o vencimento é TRAVADO na entrada até sair)."""
    A = np.zeros((len(DIAS), len(cols)))
    pos = {c: i for i, c in enumerate(cols)}
    atual = None
    lv, vv = ligado.reindex(DIAS).fillna(False).to_numpy(), venc.reindex(DIAS).to_numpy()
    for t in range(len(DIAS)):
        if not lv[t]:
            atual = None
            continue
        if atual is None or pd.isna(atual) or DIAS[t] >= atual - pd.Timedelta(days=180):
            atual = vv[t] if not pd.isna(vv[t]) else None          # entra ou rola quando faltam < 6 meses
        if atual is not None:
            A[t, pos[pd.Timestamp(atual)]] = peso
    return pd.DataFrame(A, index=DIAS, columns=cols)


# ============================================================================ Focus: CDI esperado
def focus_anual(d, indicador):
    """Mediana do Focus anual por data de coleta (usada no dia útil SEGUINTE à coleta): DataFrame dias x ano de referência."""
    def f():
        x = d["focus"]
        x = x[x.Indicador == indicador].pivot_table(index="data", columns="ref", values="Mediana", aggfunc="last").sort_index()
        return x.reindex(x.index.union(DIAS)).ffill().reindex(DIAS).shift(1)
    return memo(("focus", indicador), d["focus"], f)


def selic_meta(d):
    """Selic meta vigente (SGS 432 traz a meta até a próxima reunião, inclusive datas futuras — usamos só o valor do próprio dia)."""
    s = d["selic"]["selic_meta"]
    return s.reindex(s.index.union(DIAS)).ffill().reindex(DIAS)


def cdi_esperado(d, horizonte_anos):
    return memo(("cdi_esp", horizonte_anos), d["focus"], lambda: _cdi_esperado(d, horizonte_anos))


def _cdi_esperado(d, horizonte_anos):
    """CDI médio esperado (a.a., %) de hoje até hoje + horizonte, pelo caminho da Selic do Focus: interpola linearmente a Selic de hoje
    (meta vigente) e as medianas de fim de ano (ano corrente, +1, +2, +3, +4), e compõe dia a dia. CDI = Selic - 0,10 pp."""
    F = focus_anual(d, "Selic")
    sm = selic_meta(d).to_numpy()
    out = np.full(len(DIAS), np.nan)
    Fv = F.to_numpy()
    cols = np.array(F.columns, dtype=float)
    for t in range(0, len(DIAS), 1):
        d = DIAS[t]
        anos = np.arange(d.year, d.year + 5)
        ys = []
        for a in anos:
            j = np.flatnonzero(cols == a)
            ys.append(Fv[t, j[0]] if len(j) else np.nan)
        ys = np.array(ys, dtype=float)
        if np.isnan(ys[:2]).any() or np.isnan(sm[t]):
            continue
        ys = pd.Series(ys).ffill().to_numpy()
        xs = np.array([(pd.Timestamp(a, 12, 31) - d).days / 365.25 for a in anos])
        xg = np.linspace(0, horizonte_anos, max(int(horizonte_anos * 52), 2))
        path = np.interp(xg, np.r_[0, xs], np.r_[sm[t], ys]) - .10
        out[t] = (np.exp(np.mean(np.log1p(path / 100))) - 1) * 100
    return pd.Series(out, index=DIAS)


# ============================================================================ IPCA diário (para o PU par de títulos IPCA+)
def ipca_diario(d):
    """IPCA do mês (SGS 433) rateado pelos dias úteis do mês — é como o VNA da NTN-B/debênture IPCA+ acumula (o VNA usa a
    projeção ANBIMA no mês e corrige depois; usar o realizado só afeta a MARCAÇÃO, não sinais). Meses sem dado: média de 12 meses."""
    def f():
        m = d["ipca"]["ipca_pct"]
        m = pd.Series(m.to_numpy() / 100, index=m.index.to_period("M"))
        mes = DIAS.to_period("M")
        m = m.reindex(pd.period_range(m.index.min(), mes.max(), freq="M"))
        m = m.fillna(m.rolling(12, min_periods=1).mean().ffill())
        du = pd.Series(1, index=DIAS).groupby(mes).transform("size").to_numpy()
        return pd.Series((1 + m.reindex(mes).to_numpy()) ** (1 / du) - 1, index=DIAS)
    return memo("ipca_d", d["ipca"], f)


def curva_real(d):
    return memo("curva_real", d["td"], lambda: _curva_real(d))


def _curva_real(d):
    """Curva de juro real (Tesouro IPCA+ e IPCA+ com juros, taxa de VENDA) por prazo: DataFrame dias x prazos [1..30] anos (interpolada)."""
    if True:
        pts = []
        for tipo in ("Tesouro IPCA+", "Tesouro IPCA+ com Juros Semestrais"):
            td = tesouro(d, tipo)
            P = td["prazo"].where(td["vivo"] & (td["prazo"] > .5))
            # título com cupom: duration ~ prazo x 0,75 (aprox.); principal: prazo
            f = .75 if "Juros" in tipo else 1.0
            pts.append((P * f, td["tx_venda"].where(P.notna())))
        xs = np.arange(1, 31)
        out = np.full((len(DIAS), len(xs)), np.nan)
        for t in range(len(DIAS)):
            px = np.concatenate([p.iloc[t].to_numpy() for p, _ in pts])
            py = np.concatenate([y.iloc[t].to_numpy() for _, y in pts])
            ok = np.isfinite(px) & np.isfinite(py)
            if ok.sum() >= 2:
                o = np.argsort(px[ok])
                out[t] = np.interp(xs, px[ok][o], py[ok][o])
        return pd.DataFrame(out, index=DIAS, columns=xs)


def interp_curva(curva, prazos):
    """Taxa da curva (dias x prazos) no prazo de cada papel (dias x papéis)."""
    xs = np.array(curva.columns, dtype=float)
    cv = curva.to_numpy()
    P = prazos.to_numpy(dtype=float)
    out = np.full(P.shape, np.nan)
    for t in range(P.shape[0]):
        if np.isfinite(cv[t]).all():
            ok = np.isfinite(P[t])
            out[t, ok] = np.interp(P[t, ok], xs, cv[t])
    return pd.DataFrame(out, index=prazos.index, columns=prazos.columns)


def resumo_negocios(ng, n=10):
    if not len(ng):
        return ng
    return pd.concat([ng.nlargest(n, "contrib_pp"), ng.nsmallest(n, "contrib_pp")])
