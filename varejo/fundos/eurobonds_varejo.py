"""
Eurobonds high yield Brasil — versão pessoa física: NÃO APLICÁVEL como no institucional; substituto = ETF de high yield emergente (HYEM).

Por que o original não cabe em R$ 20 mil (~US$ 3,7 mil):
  - o livro carrega ~10-15 eurobonds de 1/15 do PL (~US$ 250 cada com R$ 20 mil). Os bonds que ele compra (Hidrovias, Braskem, Simpar,
    Movida, MC/Minerva, Açu, Globo, BRF, Americanas, Natura, Raízen) são 144A/Reg S com lote mínimo de US$ 200 mil + múltiplos de US$ 1 mil
    (offering memoranda de Hidrovias e Braskem); só os registrados na SEC, como Petrobras, têm US$ 2 mil + US$ 1 mil;
  - Avenue: US$ 1 mil só para Treasuries, corporativos americanos e soberanos brasileiros; bonds corporativos brasileiros a partir de
    US$ 50 mil; XP/BTG (contas internacionais) operam bonds em geral a partir de US$ 10-200 mil, com spread de balcão; IBKR vende o lote
    mínimo do emissor, Reg S/144A sem margem (100%) e comissão 0,1% do face (mín. US$ 1);
  - o hedge do institucional (DOL cheio US$ 50 mil, WDO US$ 10 mil; Treasury vendida) também não cabe.

Substituto testado: ETF listado nos EUA (IBKR), câmbio SEM hedge, mesma ideia de "comprar crédito HY descontado/estressado":
  - HYEM (VanEck EM High Yield Bond: corporativo HY emergente; Brasil é um dos maiores países) — o mais parecido; variantes EMHY
    (iShares EM HY, em boa parte soberano) e CEMB (iShares EM corporativo, mais grau de investimento);
  - regra de estresse análoga à do institucional (que entra no decil de MAIOR spread e sai abaixo da mediana): no fim de cada mês,
    spread do ETF ≈ dividendos dos últimos 12 meses / preço - Treasury de 5 anos; força = percentil desse spread nos últimos 60 meses
    (mín. 24); entra se força >= `entra`, sai se força < `entra` - 0,4 (entra 0,9 -> sai 0,5, como no institucional); `entra` = 0 =
    carrega sempre. Fora do ETF o dinheiro fica em SGOV (T-bill; conta IBKR < US$ 10 mil não rende juro sobre caixa).
  - custos: comissão IBKR Pro fixa (US$ 0,005/ação, mín. US$ 1), slippage 0,05%, cotas inteiras; remessa diluída em 5 anos.
  - variante `via="bdr"`: HYEM39 (BDR do HYEM na B3, em reais): sem remessa nem IBKR; custo = emolumentos + meio spread de 0,5% (BDR pouco
    líquido, premissa); caixa em Tesouro Selic (CDI - 0,10%). Sem alavancagem.
  - `hedge_fx=True`: mini-dólar WDO (US$ 10 mil, inteiro) — com US$ 3,7 mil o arredondamento dá zero contratos (só cabe a partir de ~R$ 28 mil).
ALAVANCAGEM: margem Reg T da IBKR (inicial 50% -> no máximo 2x overnight; manutenção 25%; exige patrimônio >= US$ 2 mil, então com R$ 4 mil
  ~US$ 730 NÃO há margem e a alavancagem pedida vira 1x); juros T-bill + 1,5% a.a. sobre o saldo devedor (IBKR Pro, até US$ 100 mil).
  Se o patrimônio cair abaixo de 25% da posição, a IBKR liquida no fechamento até voltar a 30% (chamada); patrimônio <= 0 = quebra.
  5x não é viável: não há futuro de crédito HY emergente para pessoa física e Reg T não passa de 2x (portfolio margin exige US$ 110 mil).

Premissas de varejo.py corrigidas aqui (sem alterar varejo.py):
  - REMESSA_IDA_VOLTA = 1,1% + 1,1% + 1% -> 1,1% (IOF de saída para investimento) + 0,38% (IOF de ingresso) + 1% de spread = 2,48%
    (Safra "O Especialista", alíquotas de IOF 2026, após a decisão do STF de 16/07/2025).
IR (fora do excesso): 15% anual sobre o ganho no exterior (Lei 14.754/2023); dividendos de ETF americano sofrem retenção de até 30% nos EUA
  na parte que não for "interest-related dividend" (crédito na declaração limitado ao IR brasileiro).
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

_R = Path(__file__).resolve().parents[2]
for _p in (str(_R), str(_R / "varejo")):                 # para rodar o arquivo sozinho (o rodar_varejo.py já põe isso no path)
    if _p not in sys.path:
        sys.path.insert(0, _p)
import comum  # noqa: E402
import varejo as V  # noqa: E402

NOME = "Eurobonds HY Brasil — substituto de varejo (ETF HYEM, câmbio sem hedge)"
TESE = ("Lote mínimo de US$ 200 mil inviabiliza os eurobonds; carrego o ETF de high yield corporativo emergente (HYEM) quando o spread dele "
        "está alto na própria história (compra em estresse), câmbio sem hedge, na IBKR")
BENCHMARK = "CDI"
INICIO, CORTE = "2021-01-01", "2024-01-01"            # iguais ao institucional
REGIME = "nenhum"
CUSTO_TROCA = .001
PARAMS = {"etf": "HYEM", "entra": 0.0}   # carrega sempre, como o institucional (sempre investido nos 15 de maior spread). A melhor
                                         # variante no IS (2021-23) seria entra=0,9 (quase sempre fora, em SGOV): IS -9,8/-10,2, OOS -7,1 pp
GRADE = {"etf": ["HYEM", "EMHY", "CEMB"], "entra": [0.0, 0.5, 0.9]}
VIZINHANCA = {"entra": (0.0, 0.3)}

CAPITAL = V.CAPITAL
APLICAVEL = False
MOTIVO = ("Não aplicável: os eurobonds HY que o fundo compra têm lote mínimo de US$ 200 mil (15 bonds = US$ 3 mi) e corporativos BR na "
          "Avenue começam em US$ 50 mil; testado o substituto ETF HYEM na IBKR, sem hedge cambial (WDO de US$ 10 mil não cabe)")
INSTRUMENTOS = ("IBKR (conta em US$; remessa com IOF 1,1% ida / 0,38% volta): HYEM (VanEck EM High Yield Bond ETF, ~US$ 19/cota, cota inteira, "
                "comissão US$ 0,005/cota mín. US$ 1); caixa em SGOV. Alternativa B3 sem remessa: BDR HYEM39 (Clear/Rico/XP, pouco líquido). "
                "Alavancagem: margem Reg T da IBKR (até 2x, conta >= US$ 2 mil).")
ALAVANCAGENS = [1, 1.5, 2]
MOTIVO_ALAV = ("5x não é viável: não existe futuro de crédito HY emergente para pessoa física e a margem Reg T da IBKR vai no máximo a 2x "
               "(portfolio margin só acima de US$ 110 mil); com R$ 4 mil (< US$ 2 mil) não há conta margem e tudo vira 1x; BDR não alavanca.")

REMESSA = .011 + .0038 + .01          # IOF ida (investimento) + IOF volta + spread de câmbio total
ANOS_REMESSA = 5
SIM_INICIO = pd.Timestamp("2020-12-01")   # a conta começa com o capital aqui (antes do INICIO, para já estar montada)
REG_T_INICIAL, REG_T_MANUT, REG_T_ALVO, REG_T_MIN_USD = .50, .25, .30, 2000.0
REBAL_TOL = .10                       # rebalanceia a quantidade de cotas se desviar > 10% do alvo (evita comissão mínima todo mês)
BDR_MEIO_SPREAD, CAIXA_SELIC_TAXA = .005, .001
WDO_USD, WDO_CUSTO_BRL = 10_000, 6.0
_DIAG = {}


def carrega():
    """ETFs em dólar (Yahoo): preço de fechamento e dividendo na data ex; ^FVX = Treasury 5 anos em % a.a."""
    x = pd.read_csv(comum.AQUI / "varejo" / "dados" / "eurobonds" / "etfs.csv", index_col=0, parse_dates=True)
    return {"etfs": x}


# ---------------------------------------------------------------- sinal (só dados até t)
def sinal(d, etf="HYEM", entra=PARAMS["entra"]):
    """1 = carregar o ETF no mês seguinte, decidido no último pregão americano de cada mês."""
    x = d["etfs"]
    p = x[f"{etf}_preco"].dropna()
    if entra <= 0:
        return pd.Series(1.0, index=p.index)
    div12 = x[f"{etf}_div"].reindex(p.index).fillna(0).rolling("365D").sum()
    sp = (div12 / p * 100 - x["ust5_pct"].reindex(p.index).ffill())
    fm = p.index.to_series().groupby(p.index.to_period("M")).max()
    s_m = sp.reindex(fm.values)
    forca = s_m.rolling(60, min_periods=24).apply(lambda w: (w <= w[-1]).mean(), raw=True)
    on, est = [], 0.0
    for f in forca.values:
        est = 1.0 if f >= entra else (0.0 if (np.isnan(f) or f < entra - .4) else est)
        on.append(est)
    return pd.Series(on, index=fm.values).reindex(p.index).ffill().fillna(0)


# ---------------------------------------------------------------- conta IBKR (US$)
def _conta_usd(d, etf, entra, capital, alavancagem, lag, custo_mult, inst):
    """Conta em dólar dia a dia: cotas inteiras, margem Reg T, chamada e quebra. Devolve o retorno diário da conta em US$ e o peso."""
    x = d["etfs"]
    P = x[f"{etf}_preco"].dropna()
    dv = x[f"{etf}_div"].reindex(P.index).fillna(0).to_numpy()
    idx = P.index
    s = sinal(d, etf, entra).reindex(idx).fillna(0).shift(1 + lag).fillna(0).to_numpy()   # decidido em t, executa no fechamento de t+1+lag
    tb = V.TBILL.reindex(idx, method="ffill").fillna(0).to_numpy()
    ptax = comum.PTAX.reindex(idx, method="ffill").to_numpy()
    Pv = P.to_numpy()
    T = len(idx)
    r = np.zeros(T)
    w = np.zeros(T)
    t0 = idx.searchsorted(SIM_INICIO)
    E = capital / ptax[t0]
    L = alavancagem if (E >= REG_T_MIN_USD or inst) else 1.0
    L = min(L, 1 / REG_T_INICIAL)
    sh, chamadas, quebra, morto = 0.0, 0, None, False
    for t in range(t0 + 1, T):
        if morto:
            continue
        V_ = sh * Pv[t - 1]
        caixa = E - V_
        juro = caixa * ((tb[t] - V.TAXA_SGOV / 252 * custo_mult) if not inst else tb[t]) if caixa > 0 else caixa * (tb[t] + (0 if inst else V.MARGEM_SPREAD / 252 * custo_mult))
        pnl = sh * (Pv[t] - Pv[t - 1] + dv[t]) + juro
        E0 = E
        E += pnl
        custo = 0.0
        if E <= 0:
            r[t], quebra, morto = -1.0, idx[t], True
            continue
        V_ = sh * Pv[t]
        if V_ > 0 and E < REG_T_MANUT * V_:                             # chamada de margem: liquida até a garantia voltar a 30%
            novo = np.floor(E / REG_T_ALVO / Pv[t])
            custo += float(V.custo_ordem_usd((sh - novo) * Pv[t], Pv[t])) * custo_mult
            sh, chamadas = novo, chamadas + 1
        alvo = s[t] * L * E / Pv[t]
        alvo = alvo if inst else np.floor(alvo)
        if (alvo == 0) != (sh == 0) or abs(alvo - sh) > REBAL_TOL * max(alvo, 1):
            if inst:
                custo += abs(alvo - sh) * Pv[t] * .0003 * custo_mult
            else:
                custo += float(V.custo_ordem_usd((alvo - sh) * Pv[t], Pv[t])) * custo_mult
            sh = alvo
        E -= custo
        r[t] = (E - E0) / E0
        w[t] = sh * Pv[t] / E
    _DIAG.update({"chamadas de margem": chamadas, "quebrou em": quebra, "alavancagem efetiva média": float(w[w > 0].mean()) if (w > 0).any() else 0.0,
                  "alavancagem disponível": L})
    return pd.Series(r, index=idx), pd.Series(w, index=idx)


def _r_usd_br(r_usd):
    return V.usd_para_dias_br(r_usd)


def excesso(d, custo_mult=1, lag=0, regime=REGIME, etf=PARAMS["etf"], entra=PARAMS["entra"], capital=CAPITAL, alavancagem=1,
            via="ibkr", hedge_fx=False, custos="varejo"):
    _DIAG.clear()
    inst = custos == "institucional"
    if via == "bdr":                                                    # HYEM39 na B3: em reais, sem remessa
        x = d["etfs"]
        P = x[f"{etf}_preco"].dropna()
        r_usd = ((P + x[f"{etf}_div"].reindex(P.index).fillna(0)) / P.shift(1) - 1).fillna(0)
        w = sinal(d, etf, entra).reindex(P.index).fillna(0).shift(1 + lag).fillna(0)
        w = w.where(w.index >= SIM_INICIO, 0)
        wb = _r_usd_br(w.diff().fillna(0)).abs().clip(upper=1)          # troca (aprox.) nos dias da B3
        hold = w.reindex(comum.DIAS, method="ffill").fillna(0).shift(1).fillna(0)
        r_brl = (1 + _r_usd_br(r_usd)) * (1 + V.FX_RET.reindex(comum.DIAS).fillna(0)) - 1
        e = hold * (r_brl - comum.CDI) - (1 - hold) * CAIXA_SELIC_TAXA / 252 * custo_mult - wb * (V.B3_EMOLUMENTOS + BDR_MEIO_SPREAD) * custo_mult
        _DIAG.update({"chamadas de margem": 0, "quebrou em": None, "alavancagem efetiva média": 1.0, "alavancagem disponível": 1.0})
    else:
        r_usd, w_usd = _conta_usd(d, etf, entra, capital, alavancagem, lag, custo_mult, inst)
        if custos == "institucional" and hedge_fx == "teorico":
            e = V.excesso_brl_com_hedge_teorico(r_usd)
        else:
            e = V.excesso_brl_sem_hedge(r_usd)
            e = e - (0 if inst else REMESSA / (ANOS_REMESSA * 252) * custo_mult)
            if hedge_fx is True:                                        # WDO inteiro sobre o patrimônio em dólar
                t0 = r_usd.index.searchsorted(SIM_INICIO)
                E_usd = (capital / comum.PTAX.asof(SIM_INICIO) * (1 + r_usd.iloc[t0:]).cumprod()).reindex(comum.DIAS, method="ffill")
                k = np.round(E_usd / WDO_USD).shift(1).fillna(0)
                h = (k * WDO_USD / E_usd).fillna(0)
                fx = V.FX_RET.reindex(comum.DIAS).fillna(0)
                tb = V.TBILL.reindex(comum.DIAS, method="ffill").fillna(0)
                e = e - h.shift(1).fillna(0) * (fx - comum.CDI + tb) - k.diff().abs().fillna(0) * WDO_CUSTO_BRL / capital * custo_mult
        if _DIAG.get("quebrou em") is not None:
            q = comum.DIAS[comum.DIAS.searchsorted(_DIAG["quebrou em"])]
            e[e.index > q] = 0.0
            e[q] = -1 - comum.CDI[q]
    e = e.where(e.index >= SIM_INICIO, 0.0).reindex(comum.DIAS).fillna(0)
    e = comum.aplica_regime(e, regime, CUSTO_TROCA * custo_mult)
    e.attrs.update(_DIAG)
    return e


def posicoes(d, etf=PARAMS["etf"], entra=PARAMS["entra"]):
    """Peso 1 quando carrega o ETF; retorno em excesso ao CDI do ETF em reais (sem hedge)."""
    x = d["etfs"]
    P = x[f"{etf}_preco"].dropna()
    r_usd = ((P + x[f"{etf}_div"].reindex(P.index).fillna(0)) / P.shift(1) - 1).fillna(0)
    s = sinal(d, etf, entra)
    s = s.where(s.index >= SIM_INICIO, 0).reindex(comum.DIAS, method="ffill").fillna(0)
    R = pd.DataFrame({etf: V.excesso_brl_sem_hedge(r_usd)})
    return pd.DataFrame({etf: s}), R


def negocios(d, etf=PARAMS["etf"], entra=PARAMS["entra"], capital=CAPITAL):
    """Um 'negócio' por período carregado, cortado por ano-calendário (para a atribuição não virar uma linha só)."""
    e = excesso(d, etf=etf, entra=entra, capital=capital)
    W, R = posicoes(d, etf, entra)
    on = W[etf].shift(1).fillna(0) > 0
    grp = (on != on.shift()).cumsum().astype(str) + "_" + on.index.year.astype(str)
    out = []
    for g, dias in on[on].groupby(grp[on]).groups.items():
        out.append({"ativo": etf, "lado": 1, "entrada": dias.min(), "saida": dias.max(), "dias": len(dias),
                    "retorno_%": ((1 + R[etf].loc[dias] + comum.CDI.loc[dias]).prod() / (1 + comum.CDI.loc[dias]).prod() - 1) * 100,
                    "contrib_pp": e.loc[dias].sum() * 100})
    return pd.DataFrame(out).sort_values("entrada").reset_index(drop=True)


if __name__ == "__main__":
    d = carrega()
    for kw in ({}, {"capital": 4000}, {"via": "bdr"}, {"entra": .9}, {"etf": "CEMB"}):
        e = excesso(d, **kw)
        print(kw, "IS %.2f OOS %.2f" % (comum.anual(e[INICIO:CORTE]), comum.anual(e[CORTE:])), e.attrs)
