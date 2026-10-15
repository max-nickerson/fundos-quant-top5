"""
Realidade de uma pessoa física com R$ 20 mil (IBKR para EUA; Clear/Rico/XP/Inter para B3). Tudo aqui é premissa explícita —
mude os números e rode de novo.

Principais diferenças para o fundo institucional:
  - conta na IBKR com menos de US$ 10 mil: NÃO rende juros sobre o caixa e NÃO recebe juros sobre o dinheiro de vendas a descoberto;
    caixa ocioso só rende se você comprar um ETF de T-bill (SGOV/BIL);
  - comissão mínima por ordem (IBKR Pro fixo: US$ 0,005/ação, mínimo US$ 1, máximo 1% da ordem);
  - venda a descoberto só com ações inteiras (fração só na compra), aluguel do papel e margem cobrada a T-bill + 1,5%;
  - dinheiro mandado para fora fica EXPOSTO AO DÓLAR (sem hedge: o mini-dólar WDO tem US$ 10 mil de nocional);
  - remessa: IOF + spread de câmbio na ida e na volta;
  - IR: 15% sobre o ganho anual no exterior (Lei 14.754/2023); B3: 15% em ações/ETFs/futuros (ações têm isenção se vendas ≤ R$ 20 mil/mês);
    o benchmark CDI de varejo (Tesouro Selic/CDB) também paga 15% de IR — compare líquido com líquido.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import comum as C  # noqa: E402

CAPITAL = 20_000.0                 # R$

# ---------------------------------------------------------------- premissas de custo (varejo)
IBKR_POR_ACAO, IBKR_MIN, IBKR_MAX_PCT = .005, 1.0, .01      # US$ por ação, mínimo por ordem, teto % da ordem
SLIPPAGE_ETF = .0005                                         # meio spread + impacto em ETF líquido, por lado
ALUGUEL_ETF_EUA = .005                                       # aluguel a.a. para vender ETF líquido a descoberto
MARGEM_SPREAD = .015                                         # juros sobre saldo devedor = T-bill + 1,5% a.a.
TAXA_SGOV = .0010                                            # custo do ETF de T-bill (SGOV/BIL) a.a.
REMESSA_IDA_VOLTA = .011 + .011 + .01                        # IOF 1,1% na ida + 1,1% na volta + ~1% de spread total (premissa; ver README)
B3_EMOLUMENTOS = .0003                                       # por lado (corretagem zero em Clear/Rico/Inter)
B3_SPREAD_ACAO = .0010                                       # meio spread médio em ação líquida, por lado
ALUGUEL_BOVA11_VAREJO = .02                                  # aluguel a.a. pago pelo tomador pessoa física
IR = .15


# ---------------------------------------------------------------- câmbio e calendário
PTAX = C.PTAX
FX_RET = PTAX.pct_change(fill_method=None).fillna(0)           # variação do R$/US$ (positivo = dólar subiu)
TBILL = C.TB_US


def usd_para_dias_br(r_usd):
    """Retorno diário em US$ (calendário dos EUA) agregado para os pregões da B3."""
    e = r_usd.fillna(0).copy()
    e.index = pd.DatetimeIndex(e.index).normalize()
    acum = np.log1p(e).cumsum()
    acum = acum[~acum.index.duplicated(keep="last")].reindex(C.DIAS.union(acum.index)).ffill().reindex(C.DIAS).fillna(0)
    return np.expm1(acum.diff().fillna(0))


def excesso_brl_sem_hedge(r_usd_total):
    """Conta em dólar SEM hedge: retorno total em US$ (já com o que o caixa rende ou não) -> retorno em R$ -> excesso sobre o CDI."""
    r = usd_para_dias_br(r_usd_total)
    return (1 + r) * (1 + FX_RET.reindex(C.DIAS).fillna(0)) - 1 - C.CDI


def excesso_brl_com_hedge_teorico(r_usd_total):
    """Só para comparação: o mesmo livro se o câmbio fosse hedgeado (excesso sobre T-bill vira excesso sobre CDI)."""
    return C.brl(r_usd_total - TBILL.reindex(r_usd_total.index).fillna(0))


def remessa_diaria(anos=5):
    """Custo de remessa (ida + volta) diluído em `anos` de permanência, por dia útil."""
    return REMESSA_IDA_VOLTA / (anos * 252)


# ---------------------------------------------------------------- custos IBKR
def custo_ordem_usd(valor, preco):
    """Comissão IBKR Pro fixo + slippage de uma ordem de `valor` US$ num papel de `preco`."""
    valor, preco = np.abs(valor), np.maximum(preco, .01)
    com = np.clip(IBKR_POR_ACAO * valor / preco, IBKR_MIN, IBKR_MAX_PCT * valor)
    return np.where(valor > 0, com + SLIPPAGE_ETF * valor, 0.0)


def carteira_varejo_usd(W, R, P, nav_usd, lag=0, custo_mult=1.0, caixa_rende=True, aluguel=ALUGUEL_ETF_EUA, inteiro_vendido=True):
    """Carteira de varejo em dólar.
    W: pesos-alvo decididos em t (fração do patrimônio); R: retorno TOTAL diário de cada papel (não excesso); P: preço de cada papel;
    nav_usd: patrimônio em US$ (série ou número). Executa em t+1+lag. Vendas a descoberto arredondadas para ações inteiras.
    Caixa livre (1 - soma dos comprados) rende T-bill via SGOV se caixa_rende; dinheiro de venda a descoberto não rende nada;
    saldo devedor (comprado > 100%) paga T-bill + 1,5%. Devolve retorno total diário em US$ (calendário dos EUA)."""
    idx = R.index
    W = W.reindex(idx).fillna(0).shift(1 + lag).fillna(0)
    P = P.reindex(idx).ffill()
    nav = nav_usd if np.isscalar(nav_usd) else nav_usd.reindex(idx).ffill()
    if inteiro_vendido:
        n = (W.clip(upper=0) * nav / P).round()                # ações inteiras na ponta vendida
        W = W.clip(lower=0) + (n * P / nav).fillna(0)
    Wv = W.shift(1).fillna(0)                                  # posição que vale para o retorno de hoje
    tb = TBILL.reindex(idx).ffill().fillna(0)
    comprado = Wv.clip(lower=0).sum(axis=1)
    vendido = Wv.clip(upper=0).abs().sum(axis=1)
    caixa = (1 - comprado).clip(lower=0)
    divida = (comprado - 1).clip(lower=0)
    r = (Wv * R.fillna(0)).sum(axis=1)
    r += caixa * (tb - TAXA_SGOV / 252) * caixa_rende - divida * (tb + MARGEM_SPREAD / 252) - vendido * aluguel / 252 * custo_mult
    giro_usd = (W.diff().abs() * nav)
    custo = pd.DataFrame(custo_ordem_usd(giro_usd.values, P.values), index=idx, columns=W.columns).sum(axis=1) / nav
    return (r - custo * custo_mult).fillna(0)


# ---------------------------------------------------------------- custos B3 (varejo)
def custo_b3(giro, spread=B3_SPREAD_ACAO):
    return giro * (B3_EMOLUMENTOS + spread)


# ---------------------------------------------------------------- imposto
def apos_ir(r, aliquota=IR):
    """Aplica IR anual de `aliquota` sobre o ganho nominal do ano (com compensação de prejuízo acumulado), cobrado no último dia do ano.
    r: retorno diário da cota em R$. Simplificação: imposto sobre o ganho do ano, como no regime anual do exterior (Lei 14.754)."""
    r = r.fillna(0)
    out = r.copy()
    prejuizo = 0.0
    cota = 1.0
    for ano, x in r.groupby(r.index.year):
        ini = cota
        cota *= (1 + x).prod()
        ganho = cota - ini
        base = ganho - prejuizo if ganho > 0 else 0.0
        prejuizo = max(prejuizo - ganho, 0.0) if ganho > 0 else prejuizo - ganho
        imposto = max(base, 0.0) * aliquota
        if imposto > 0:
            ult = x.index[-1]
            out.loc[ult] = (1 + out.loc[ult]) * (cota - imposto) / cota - 1
            cota -= imposto
    return out


def cdi_liquido(aliquota=IR):
    """Benchmark de varejo: Tesouro Selic/CDB 100% CDI com IR de 15% (mesma regra anual, para comparar justo)."""
    return apos_ir(C.CDI, aliquota)
