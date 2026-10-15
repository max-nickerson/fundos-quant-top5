"""
Fundo pessoa física (R$ 20–50 mil) operando em TODAS as contas como um fundo só:
  - caixa sempre em R$ rendendo CDI (Tesouro Selic / CDB liquidez diária / LFTS11) — inclusive a garantia na B3 (Tesouro Selic aceito como margem);
  - na IBKR fica SÓ o necessário: margem de futuros/opções (US$) ou o patrimônio exigido pela Reg T para ETFs/ações (US$). Só esse saldo
    fica exposto ao dólar e deixa de render CDI (conta pequena na IBKR não rende juros);
  - futuros e opções em contratos INTEIROS; ações/ETFs da B3 no fracionário (1 ação); IBKR com frações só na compra.
  - IR por classe (pessoa física): ações B3 swing 15% com isenção se vendas de ações ≤ R$ 20 mil no mês; day trade 20%; futuros/opções/ETFs
    B3 15%; exterior 15% ao ano (Lei 14.754/2023); renda fixa tributada 15% (longo prazo); isentos: LCI/LCA, debêntures incentivadas, CRI/CRA,
    rendimento de FII. Benchmark de varejo = CDI com 15% de IR.

Funções principais (todas devolvem séries no calendário da B3):
  futuro_b3(...), futuro_cme(...), conta_ibkr(...), acoes_b3(...), apos_ir_por_classe(...)
Cada fundo usa as peças que precisa e devolve o EXCESSO diário sobre o CDI (antes do IR) + um dicionário de P&L por classe de IR.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))
import comum as C  # noqa: E402

CAPITAIS = (20_000, 50_000)
DIAS = C.DIAS
CDI = C.CDI
PTAX = C.PTAX.reindex(DIAS).ffill()
TBILL = C.TB_US

# ---------------------------------------------------------------- especificações de contratos (verificar e corrigir no fundo, citando a fonte)
CONTRATOS = {
    # B3 (valor por ponto em R$; margem ~ fração do nocional; custo por contrato em R$ por lado)
    "WIN": {"mult": .20, "moeda": "BRL", "margem": .12, "custo": 0.60},          # mini-índice
    "WDO": {"mult": 10.0, "moeda": "BRL", "margem": .07, "custo": 1.20},          # mini-dólar: US$ 10 mil (preço em R$/US$ x 1000 pontos)
    "CCM": {"mult": 450.0, "moeda": "BRL", "margem": .08, "custo": 1.50},         # milho: 450 sacas
    "BGI": {"mult": 330.0, "moeda": "BRL", "margem": .08, "custo": 1.50},         # boi gordo: 330 arrobas
    "ICF": {"mult": 100.0, "moeda": "USD", "margem": .10, "custo": 1.50},         # café arábica: 100 sacas (US$/saca)
    "SJC": {"mult": 450.0, "moeda": "USD", "margem": .08, "custo": 1.50},         # soja Chicago: 450 sacas
    # CME micro (valor por ponto em US$; custo por contrato em US$ por lado: comissão IBKR + taxas)
    "MES": {"mult": 5.0, "moeda": "USD", "margem": .06, "custo": 0.62},
    "MNQ": {"mult": 2.0, "moeda": "USD", "margem": .07, "custo": 0.62},
    "M2K": {"mult": 5.0, "moeda": "USD", "margem": .07, "custo": 0.62},
    "MGC": {"mult": 10.0, "moeda": "USD", "margem": .05, "custo": 0.85},
    "SIL": {"mult": 1000.0, "moeda": "USD", "margem": .08, "custo": 0.85},
    "MHG": {"mult": 2500.0, "moeda": "USD", "margem": .06, "custo": 0.85},
    "MCL": {"mult": 100.0, "moeda": "USD", "margem": .10, "custo": 0.85},
    "M6E": {"mult": 12_500.0, "moeda": "USD", "margem": .025, "custo": 0.40},
    "M6A": {"mult": 10_000.0, "moeda": "USD", "margem": .035, "custo": 0.40},
    "M6B": {"mult": 6_250.0, "moeda": "USD", "margem": .03, "custo": 0.40},
    "MCD": {"mult": 10_000.0, "moeda": "USD", "margem": .025, "custo": 0.40},
    "MSF": {"mult": 12_500.0, "moeda": "USD", "margem": .035, "custo": 0.40},
    "MJY": {"mult": 1_250_000.0, "moeda": "USD", "margem": .035, "custo": 0.40},
    "VXM": {"mult": 100.0, "moeda": "USD", "margem": .45, "custo": 0.85},
    "MBT": {"mult": .1, "moeda": "USD", "margem": .40, "custo": 2.50},           # micro bitcoin: 0,1 BTC
    "MET": {"mult": .1, "moeda": "USD", "margem": .40, "custo": 0.50},           # micro ether: 0,1 ETH
    "10Y": {"mult": 1000.0, "moeda": "USD", "margem": .30, "custo": 0.85},       # micro yield 10 anos (US$ 10 por bp)
}

# ---------------------------------------------------------------- custos/regras de varejo
REMESSA_IDA, REMESSA_VOLTA, SPREAD_CAMBIO = .011, .0038, .005    # IOF ida (investimento) 1,1%, volta 0,38%, spread de câmbio por perna
IBKR_POR_ACAO, IBKR_MIN = .0035, .35                              # IBKR Pro escalonado
B3_EMOL = .0003
B3_SPREAD = {"liquida": .0008, "media": .002, "pequena": .005, "fracionario_extra": .002}
ALUGUEL_PF_CORRETORA = .005                                      # Clear/Rico: 0,5% do volume por contrato de aluguel aberto/renovado
ALUGUEL_PF_DOADOR = .01                                          # taxa a.a. ao doador (blue chip ~0,5–1%; small cap pode ser 5–20%)


def _br(s):
    return s.reindex(DIAS).ffill()


def usd_para_br(r_usd):
    """Soma em log de valores/retornos em US$ do calendário dos EUA para os pregões da B3."""
    e = r_usd.fillna(0).copy()
    e.index = pd.DatetimeIndex(e.index).normalize()
    acum = e.cumsum()
    acum = acum[~acum.index.duplicated(keep="last")].reindex(DIAS.union(acum.index)).ffill().reindex(DIAS).fillna(0)
    return acum.diff().fillna(0)


# ---------------------------------------------------------------- futuros
def contratos(alvo_nocional_brl, preco, contrato, capital):
    """Nº INTEIRO de contratos para chegar perto de um nocional-alvo em R$ (alvo = peso x capital). preco no ativo do contrato."""
    esp = CONTRATOS[contrato]
    fx = PTAX.reindex(preco.index).ffill() if esp["moeda"] == "USD" else 1.0
    noc_1 = preco * esp["mult"] * fx
    return (alvo_nocional_brl / noc_1).round().fillna(0)


def pnl_futuro(n, preco, contrato, lag=0, custo_mult=1.0):
    """P&L diário em R$ de n contratos (n decidido em t, executado em t+1+lag). preco: série de ajuste do contrato contínuo,
    SEM saltos de rolagem (use retornos ajustados: preco_ajustado). Devolve (pnl_brl, nocional_brl, margem_brl, custo_brl)."""
    esp = CONTRATOS[contrato]
    idx = preco.index
    n = n.reindex(idx).fillna(0).shift(1 + lag).fillna(0)
    dP = preco.diff().fillna(0)
    fx = PTAX.reindex(idx).ffill() if esp["moeda"] == "USD" else pd.Series(1.0, index=idx)
    pnl = n.shift(1).fillna(0) * dP * esp["mult"] * fx
    giro = n.diff().abs().fillna(n.abs())
    custo = giro * esp["custo"] * (fx if esp["moeda"] == "USD" else 1) * custo_mult
    noc = (n.abs() * preco * esp["mult"] * fx)
    return pnl, noc, noc * esp["margem"], custo


# ---------------------------------------------------------------- conta no exterior (só o necessário)
def custo_conta_exterior(saldo_usd_brl, folga=1.5, revisa="M"):
    """Custo de manter na IBKR o saldo necessário (margem de futuros ou patrimônio Reg T), em R$ por dia:
    - o saldo é ajustado mensalmente para folga x o maior saldo exigido no mês anterior (sem olhar o futuro: usa o mês que passou);
    - esse saldo deixa de render CDI (conta pequena não rende) e fica exposto ao câmbio (ganho/perda cambial entra no P&L);
    - cada remessa paga IOF + spread (ida 1,1%+0,5%; volta 0,38%+0,5%).
    Devolve (custo_diario_brl, saldo_brl)."""
    req = saldo_usd_brl.reindex(DIAS).fillna(0)
    per = req.index.to_period(revisa)
    teto_mes = req.groupby(per).max().shift(1).fillna(req.groupby(per).max().iloc[0])
    alvo = pd.Series(per.map(teto_mes).values * folga, index=DIAS)
    alvo = np.maximum(alvo, req)                                     # nunca abaixo do exigido no dia (aporte emergencial)
    saldo_usd = alvo / PTAX
    fx_ret = PTAX.pct_change(fill_method=None).fillna(0)
    ganho_cambial = (saldo_usd.shift(1) * PTAX.shift(1)).fillna(0) * fx_ret
    cdi_perdido = (saldo_usd.shift(1) * PTAX.shift(1)).fillna(0) * CDI
    fluxo = (saldo_usd.diff() * PTAX).fillna(saldo_usd.iloc[0] * PTAX.iloc[0])
    remessa = fluxo.clip(lower=0) * (REMESSA_IDA + SPREAD_CAMBIO) + (-fluxo.clip(upper=0)) * (REMESSA_VOLTA + SPREAD_CAMBIO)
    return cdi_perdido + remessa - ganho_cambial, saldo_usd * PTAX


def custo_ordem_ibkr_usd(valor_usd, preco_usd):
    v = np.abs(valor_usd)
    com = np.clip(IBKR_POR_ACAO * v / np.maximum(preco_usd, .01), IBKR_MIN, .01 * v)
    return np.where(v > 0, com, 0.0)


# ---------------------------------------------------------------- ações/ETFs B3
def custo_b3(giro_brl, liquidez="liquida", fracionario=True):
    s = B3_SPREAD[liquidez] + (B3_SPREAD["fracionario_extra"] if fracionario else 0)
    return giro_brl * (B3_EMOL + s)


# ---------------------------------------------------------------- imposto por classe
def apos_ir_por_classe(pnl_classes, capital, aliquotas=None):
    """pnl_classes: dict classe -> P&L diário em R$ (sem o CDI do caixa). Classes: 'acoes_isentas' (vendas ≤ R$ 20 mil/mês), 'acoes',
    'day_trade', 'futuros_b3', 'opcoes_b3', 'etf_b3', 'exterior', 'renda_fixa', 'isento'. O CDI do caixa paga 15%.
    IR simplificado: anual por classe, com compensação de prejuízo dentro da classe. Devolve o P&L diário após IR (somado) em R$."""
    al = {"acoes_isentas": 0, "acoes": .15, "day_trade": .20, "futuros_b3": .15, "opcoes_b3": .15, "etf_b3": .15, "exterior": .15,
          "renda_fixa": .15, "isento": 0.0, **(aliquotas or {})}
    tot = pd.Series(0.0, index=DIAS)
    for cls, s in pnl_classes.items():
        s = s.reindex(DIAS).fillna(0)
        out, prej = s.copy(), 0.0
        for ano, x in s.groupby(s.index.year):
            g = x.sum()
            base = max(g - prej, 0) if g > 0 else 0
            prej = max(prej - g, 0) if g > 0 else prej - g
            if base > 0 and al.get(cls, .15) > 0:
                out.loc[x.index[-1]] -= base * al.get(cls, .15)
        tot += out
    return tot


def cdi_liquido():
    """CDI de varejo depois de 15% de IR (mesma regra anual)."""
    s, out = CDI.fillna(0), CDI.fillna(0).copy()
    cota = 1.0
    for ano, x in s.groupby(s.index.year):
        ini = cota
        cota *= (1 + x).prod()
        out.loc[x.index[-1]] = (1 + out.loc[x.index[-1]]) * (cota - (cota - ini) * .15) / cota - 1
        cota -= (cota - ini) * .15
    return out


def excesso_de_pnl(pnl_brl, capital):
    """P&L diário em R$ (já com custos) sobre um patrimônio de `capital` (constante em R$) -> excesso diário sobre o CDI."""
    return (pnl_brl.reindex(DIAS).fillna(0) / capital)
