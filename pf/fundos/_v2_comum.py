"""
Peças comuns da frente pf3_internacional_B (conta em dólar v2: pf.conta_usd). Não altera comum/robustez/pf.

  - sleeve(capital, sleeve_brl): R$ que moram na IBKR (padrão: metade do capital, como pede o BRIEF PF3);
  - fecha(pnl_usd, ...): livro em US$ (P&L EM EXCESSO DO T-BILL, já com custos da IBKR) -> excesso do fundo + dict de classes de IR.
    A conta_usd credita T-bill (SGOV) sobre o saldo inteiro; por isso cada livro devolve o P&L das posições MENOS o T-bill do dinheiro que
    elas ocupam (ação/ETF comprado) — futuros já são excesso do T-bill;
  - apos_ir(...): mesma regra do executor (rodar_pf.apos_ir_v2): exterior 15% ao ano, hedge WDO 15% mensal, CDI perdido x 0,85;
  - tabela(mod, d): capital x sleeve x hedge (nenhum/inteiro), OOS antes/depois do IR, e a mesma conta SEM estratégia (pnl = 0) para
    separar o que é a estratégia do que é o custo de manter o dinheiro fora.
"""
import numpy as np
import pandas as pd

import _util as U

C, pf = U.C, U.pf
import ir as IRPF  # noqa: E402

SLEEVES = {20000: [5000, 10000, 15000], 50000: [12500, 25000, 37500]}
HEDGES = ("nenhum", "inteiro")
SGOV = .0010                                    # taxa do SGOV a.a. (a conta_usd já desconta 0,10% a.a. do T-bill)


def sleeve(capital, sleeve_brl):
    return capital / 2 if sleeve_brl is None else float(sleeve_brl)


def usd_conta_mes(sleeve_brl, idx):
    """US$ na conta no início de cada mês (a conta_usd recalibra o saldo para `sleeve_brl` no 1º pregão do mês), no calendário idx."""
    per = pd.Series(pf.DIAS.to_period("M"), index=pf.DIAS)
    base = (sleeve_brl / pf.PTAX).groupby(per).transform("first")
    return base.reindex(pd.DatetimeIndex(idx).union(base.index)).ffill().reindex(idx).bfill()


def fecha(pnl_usd, sleeve_brl, capital, hedge="inteiro", custo_mult=1.0):
    ex, cls = pf.conta_usd(pnl_usd.fillna(0), float(sleeve_brl), float(sleeve_brl), capital, hedge=hedge, custo_mult=custo_mult)
    return ex.reindex(C.DIAS).fillna(0), cls


def apos_ir(cls, capital, r):
    cdi_l = pf.cdi_liquido().reindex(r.index).fillna(0)
    ex = sum(IRPF.imposto_excesso(cls[c].reindex(r.index).fillna(0) / capital, capital, c) for c in ("exterior", "futuros_b3") if c in cls)
    perdido = cls.get("cdi_perdido", 0)
    perdido = (perdido.reindex(r.index).fillna(0) if hasattr(perdido, "reindex") else perdido) / capital * .85
    return cdi_l + ex - perdido


def _aa(m, r, ri):
    import robustez as RB
    o, oi = RB.oos(m, r), RB.oos(m, ri)
    ci = RB.oos(m, pf.cdi_liquido().reindex(r.index).fillna(0))
    return RB.ativo_aa(m, r), C.anual(oi) - C.anual(ci)


def tabela(m, d, extra=None, **params):
    """Linhas: capital x sleeve x hedge. extra: {capital: [sleeves adicionais]} (ex.: sleeve = margem necessária)."""
    import robustez as RB
    lin = []
    for cap, sls in SLEEVES.items():
        for sl in list(sls) + list((extra or {}).get(cap, [])):
            for h in HEDGES:
                e = m.excesso(d, capital=cap, sleeve_brl=sl, hedge=h, **params)
                r = RB.cota(m, e)
                cls = m.classes_ir(d, capital=cap, sleeve_brl=sl, hedge=h, **params)
                a, ai = _aa(m, r, apos_ir(cls, cap, r))
                e0, c0 = fecha(pd.Series(0.0, index=C.DIAS), sl, cap, h)
                r0 = RB.cota(m, e0)
                a0, ai0 = _aa(m, r0, apos_ir(c0, cap, r0))
                n = c0["n_wdo"]
                lin.append({"capital": cap, "sleeve": sl, "hedge": h, "OOS antes IR pp": a, "OOS depois IR pp": ai,
                            "só a conta (sem estratégia) pp": a0, "estratégia sobre a conta pp": a - a0,
                            "WDO médio OOS": float(n[n.index >= pd.Timestamp(m.CORTE)].mean())})
    return pd.DataFrame(lin)
