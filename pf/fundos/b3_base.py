"""
Peças comuns da frente "b3_acoes" (fundos PF de ações/eventos na B3 que exploram ser PEQUENO). Não altera comum.py/robustez.py/pf.py.

Dados (pf/dados/b3_acoes/, exportados uma vez por exportar_*.py a partir dos dados brutos já baixados):
  painel_{P,R,V,O,H,L,NEG,dy,BID,ASK}.parquet  COTAHIST 2014+ (inclui RJ/CODBDI 08), R = retorno total ajustado (desdobramento, grupamento,
                                               dividendos do Yahoo; deslistados sem dividendo = conservador), BID/ASK = melhor oferta no fechamento
  fracionario.parquet, direitos.parquet       mercado fracionário (TPMERC 020) e direitos/recibos/bônus (CODBDI 10/22)
  fundamentos.parquet, acoes_emitidas.parquet lucro 12m, PL e nº de ações (CVM DFP/ITR/FRE) com a DATA DE ENTREGA
  mapa_cnpj.parquet                           CNPJ -> raiz de ticker (FCA)

Motor `carteira_pf`: carteira de ações de pessoa física com ações INTEIRAS (lote de 100 + fracionário), custo por lado =
emolumentos 0,03% + meio spread REAL do fechamento do dia da execução (melhor oferta de compra/venda do COTAHIST) + 0,2% extra na parte
fracionária; compra só se o volume do dia >= 10x a ordem; venda adiada se o papel não negociou; teto opcional de vendas no mês
(isenção de IR de R$ 20 mil); decisão em t, execução no fechamento de t+1+lag. Dinheiro em ações NÃO rende CDI.

Convenção de classes_ir (igual à da frente "revisita"): dict classe -> P&L diário em R$ (ganho REAL da classe, sem o CDI) e a chave
especial "_cdi_perdido" (R$ de CDI que o dinheiro aplicado em ações deixou de ganhar). Excesso antes do IR = (soma das classes -
_cdi_perdido)/capital; depois do IR = [pf.apos_ir_por_classe(classes) - 0,85 x _cdi_perdido]/capital.
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

DADOS = PF / "dados" / "b3_acoes"
DIAS = C.DIAS
CDI = C.CDI
EMOL = .0003            # emolumentos B3 pessoa física, operação normal (negociação + liquidação + TTA) — MAPA_ATIVOS_FX_B3
EMOL_DT = .00023        # day trade
FRAC_EXTRA = pf.B3_SPREAD["fracionario_extra"]
ISENCAO = 20_000.0      # vendas de ações no mês até R$ 20 mil: ganho isento (Lei 11.033/2004, art. 3º)
_CACHE = {}


def ler(nome):
    if nome not in _CACHE:
        _CACHE[nome] = pd.read_parquet(DADOS / f"{nome}.parquet")
    return _CACHE[nome]


def painel(*chaves):
    """Matrizes data x ticker no calendário comum.DIAS (float64)."""
    out = {}
    for k in chaves:
        ck = "painel_" + k
        if ck + "_dias" not in _CACHE:
            x = ler(ck).astype("float64")
            x.index = pd.DatetimeIndex(x.index)
            _CACHE[ck + "_dias"] = x.reindex(DIAS)
        out[k] = _CACHE[ck + "_dias"]
    return out


def acao_comum(cols):
    """Só ações/units negociáveis (exclui recibos e direitos, que estão em outra tabela)."""
    return [c for c in cols if c[-1] in "345678" or c.endswith("11")]


# ---------------------------------------------------------------- custos
def meio_spread(BID, ASK, V):
    """Meio spread relativo no fechamento; sem oferta dos dois lados -> estimativa pela liquidez do dia."""
    hs = ((ASK - BID) / (ASK + BID)).where((ASK > BID) & (BID > 0))
    fb = pd.DataFrame(np.select([V >= 50e6, V >= 10e6, V >= 2e6, V >= 2e5], [.0005, .001, .0025, .006], .015), index=V.index, columns=V.columns)
    return hs.clip(0, .10).fillna(fb)


# ---------------------------------------------------------------- motor da carteira
def carteira_pf(alvo, d, capital, custo_mult=1.0, lag=0, teto_vendas=None, redimensiona=False, alavancagem=1.0, prazo_compra=3,
                vol_min=10.0, rotulos=None, manter=None, apara=None):
    """alvo: DataFrame (DIAS x tickers) de R$-alvo decididos no fechamento de t (linha toda NaN = sem decisão nesse dia; numa linha
    com decisão, ticker ausente/0 = vender). Executa no fechamento de t+1+lag.
    manter: DataFrame bool opcional (decidido em t): papel já em carteira com manter=True não é vendido mesmo fora do alvo (histerese).
    apara: (teto, volta) em R$ — nas datas de decisão, posição acima de `teto` é vendida até `volta` (o capital é fixo: um vencedor
    não pode virar 100% do fundo; a venda conta para o teto de vendas do mês).
    d: dict com P (preço bruto), R (retorno total), V (volume R$), HS (meio spread) — DataFrames DIAS x tickers.
    Devolve dict com e (excesso diário sobre o CDI, fração do capital), pnl (R$ das ações), cdi_perdido (R$), vendas (R$/dia),
    custo (R$/dia), W (peso decidido, para atribuição), negocios (DataFrame)."""
    cols = list(alvo.columns)
    idx = DIAS
    P = d["P"].reindex(index=idx, columns=cols).values
    R = d["R"].reindex(index=idx, columns=cols).fillna(0).values
    V = d["V"].reindex(index=idx, columns=cols).fillna(0).values
    HS = d["HS"].reindex(index=idx, columns=cols).fillna(.015).values
    # deslistagem/parada sem olhar o futuro: sem negócio há 30 pregões -> liquida pelo último valor (OPA/incorporação pagam esse preço)
    vivo = pd.DataFrame(P).notna().rolling(30, min_periods=1).max().astype(bool).values
    A = alvo.reindex(idx)
    tem = A.notna().any(axis=1).values
    A = A.fillna(0).values
    MT = manter.reindex(index=idx, columns=cols).fillna(False).values if manter is not None else np.zeros(A.shape, bool)
    sh = 1 + lag
    T, N = P.shape
    val = np.zeros(N)                     # R$ em cada papel (fechamento)
    pend_venda = np.zeros(N, bool)
    pend_compra = np.zeros(N)             # R$ a comprar (pendente)
    pend_prazo = np.zeros(N, int)
    entrada = [None] * N
    v_entr = np.zeros(N)
    acum = np.zeros(N)                    # P&L acumulado do negócio (R$, com custos)
    pnl = np.zeros(T)
    custo = np.zeros(T)
    vendas = np.zeros(T)
    inv = np.zeros(T)
    Wv = np.zeros((T, N))
    neg = []
    mes = idx.to_period("M")
    vend_mes, mes_at = 0.0, None
    cm = custo_mult
    for i in range(T):
        if mes[i] != mes_at:
            mes_at, vend_mes = mes[i], 0.0
        g = val * R[i]
        pnl[i] = g.sum()
        acum += g
        val = val + g
        # papel parado há 30 pregões (deslistado/suspenso) sai pelo último valor, sem custo
        morto = (val > 0) & ~vivo[i]
        for j in np.flatnonzero(morto):
            neg.append((cols[j], entrada[j], idx[i], v_entr[j], acum[j]))
            val[j], acum[j], pend_venda[j] = 0.0, 0.0, False
        k = i - sh
        if k >= 0 and tem[k]:
            a = A[k]
            if not redimensiona:
                pend_venda |= (val > 0) & (a <= 0) & ~MT[k]
                pend_venda &= ~((val > 0) & ((a > 0) | MT[k]))                  # voltou ao alvo: cancela venda pendente
                novo = (val <= 0) & (a > 0)
                pend_compra[novo], pend_prazo[novo] = a[novo], prazo_compra
                pend_compra[(a <= 0)] = 0
            else:
                pend_venda |= (val > 0) & (a <= 0)
                dif = a - val
                pend_compra[:] = np.where(a > 0, np.maximum(dif, 0), 0)
                pend_prazo[:] = prazo_compra
                red = (val > 0) & (a > 0) & (dif < -.25 * a)          # reduz só se passar de 25% acima do alvo
                for j in np.flatnonzero(red & (P[i] > 0)):
                    q = -dif[j]
                    if teto_vendas is not None and vend_mes + q > teto_vendas:
                        continue
                    c = q * (EMOL + HS[i, j]) * cm
                    val[j] -= q
                    vendas[i] += q
                    vend_mes += q
                    custo[i] += c
                    acum[j] -= c
            if apara is not None:
                for j in np.flatnonzero((val > apara[0]) & ~pend_venda & (P[i] > 0)):
                    q = val[j] - apara[1]
                    if teto_vendas is not None and vend_mes + q > teto_vendas:
                        q = max(teto_vendas - vend_mes, 0)
                    if q <= 0:
                        continue
                    c = q * (EMOL + HS[i, j]) * cm
                    ganho_parcial = acum[j] * q / val[j]
                    neg.append((cols[j], entrada[j], idx[i], v_entr[j] * q / val[j], ganho_parcial - c))
                    acum[j] -= ganho_parcial
                    v_entr[j] *= 1 - q / val[j]
                    val[j] -= q
                    vendas[i] += q
                    vend_mes += q
                    custo[i] += c
        # vendas
        for j in np.flatnonzero(pend_venda & (val > 0)):
            if not P[i, j] > 0:
                continue
            q = val[j]
            if teto_vendas is not None and vend_mes + q > teto_vendas and vend_mes > 0:
                continue                                                    # adia para o mês seguinte (isenção)
            lotes = np.floor(q / P[i, j] / 100) * 100 * P[i, j]
            c = (q * (EMOL + HS[i, j]) + (q - lotes) * FRAC_EXTRA) * cm
            c += q * .01 * cm * (q > .1 * V[i, j])                             # ordem > 10% do volume do dia: impacto extra de 1%
            custo[i] += c
            acum[j] -= c
            vendas[i] += q
            vend_mes += q
            neg.append((cols[j], entrada[j], idx[i], v_entr[j], acum[j]))
            val[j], acum[j], pend_venda[j] = 0.0, 0.0, False
        # compras (ações inteiras, só se o papel negociou com volume suficiente e cabe no caixa)
        livre = capital * alavancagem - val.sum()
        for j in np.flatnonzero(pend_compra > 0):
            if livre <= 0:
                break
            if P[i, j] > 0 and V[i, j] >= vol_min * pend_compra[j]:
                n = np.floor(min(pend_compra[j], livre) / P[i, j])
                if n >= 1:
                    q = n * P[i, j]
                    lotes = np.floor(n / 100) * 100 * P[i, j]
                    c = (q * (EMOL + HS[i, j]) + (q - lotes) * FRAC_EXTRA) * cm
                    val[j] += q
                    livre -= q
                    custo[i] += c
                    acum[j] = -c
                    entrada[j], v_entr[j] = idx[i], q
                pend_compra[j] = 0
            else:
                pend_prazo[j] -= 1
                if pend_prazo[j] <= 0:
                    pend_compra[j] = 0
        inv[i] = val.sum()
        Wv[i] = val / capital
    for j in np.flatnonzero(val > 0):
        neg.append((cols[j], entrada[j], None, v_entr[j], acum[j]))
    cdi_perd = pd.Series(np.r_[0, inv[:-1]], index=idx) * CDI.reindex(idx).fillna(0)
    pnl = pd.Series(pnl, index=idx)
    custo = pd.Series(custo, index=idx)
    e = (pnl - custo - cdi_perd) / capital
    ng = pd.DataFrame(neg, columns=["ativo", "entrada", "saida", "valor", "ganho"])
    if len(ng):
        ng["lado"] = 1
        fim = ng.saida.fillna(idx[-1])
        ng["dias"] = [max(int(idx.searchsorted(b) - idx.searchsorted(a)), 0) for a, b in zip(ng.entrada, fim)]
        ng["retorno_%"] = ng.ganho / ng.valor * 100
        ng["contrib_pp"] = ng.ganho / capital * 100
        if rotulos is not None:
            ng["rotulo"] = ng.ativo.map(rotulos) if isinstance(rotulos, dict) else None
        ng = ng[["ativo", "lado", "entrada", "saida", "dias", "retorno_%", "contrib_pp", "valor", "ganho"]]
    W = pd.DataFrame(Wv, index=idx, columns=cols).shift(-sh).fillna(0)       # peso "decidido" (o motor comum.carteira desloca 1+lag)
    return {"e": e, "pnl": pnl, "custo": custo, "cdi_perdido": cdi_perd, "vendas": pd.Series(vendas, index=idx), "W": W,
            "negocios": ng, "investido": pd.Series(inv, index=idx)}


def classes_acoes(res):
    """IR de ações swing: mês com vendas <= R$ 20 mil -> ganho isento (P&L do mês inteiro, aproximação por marcação a mercado)."""
    ganho = (res["pnl"] - res["custo"]).reindex(DIAS).fillna(0)
    v = res["vendas"].reindex(DIAS).fillna(0)
    mes = DIAS.to_period("M")
    isento = pd.Series(mes.map(v.groupby(mes).sum() <= ISENCAO), index=DIAS).astype(bool)
    return {"acoes_isentas": ganho.where(isento, 0.0), "acoes": ganho.where(~isento, 0.0), "_cdi_perdido": res["cdi_perdido"]}


def excesso_apos_ir(classes, capital):
    """Excesso diário sobre o CDI depois do IR (fração do capital), a comparar com o CDI líquido (pf.cdi_liquido)."""
    cl = {k: v for k, v in classes.items() if not k.startswith("_")}
    perd = classes.get("_cdi_perdido", pd.Series(0.0, index=DIAS)).reindex(DIAS).fillna(0)
    return (pf.apos_ir_por_classe(cl, capital) - .85 * perd) / capital


def dados_acoes(janela_adv=60):
    """Painel padrão para os fundos de ações: P, R, V, NEG, BID, ASK, O, H, L e HS (meio spread)."""
    d = painel("P", "R", "V", "NEG", "BID", "ASK", "O", "H", "L")
    cols = acao_comum(d["P"].columns)
    d = {k: v[cols] for k, v in d.items()}
    d["HS"] = meio_spread(d["BID"], d["ASK"], d["V"].fillna(0))
    return d


def bateria_pf(m, d, capital, n_leque=60, log=print):
    """Roda robustez.bateria com excesso fixado no capital."""
    import types
    import robustez
    M = types.SimpleNamespace(**{k: getattr(m, k) for k in dir(m) if not k.startswith("__")})
    M.excesso = lambda dd, **kw: m.excesso(dd, capital=capital, **kw)
    M.posicoes = lambda dd, **kw: m.posicoes(dd, capital=capital, **kw)
    M.negocios = lambda dd, **kw: m.negocios(dd, capital=capital, **kw)
    return robustez.bateria(M, d, n_leque=n_leque, log=log)
