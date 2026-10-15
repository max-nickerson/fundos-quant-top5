"""
IR de pessoa física, do jeito certo (simplificações explicitadas):

  Renda variável na B3 (ações, units, ETFs, futuros, opções, termo) — apuração MENSAL:
    - swing trade 15%, day trade 20%; prejuízo acumulado compensa lucros futuros (sem prazo), dentro de cada modalidade;
    - ações (inclusive units) com vendas totais no mês ≤ R$ 20 mil: lucro do mês ISENTO (o prejuízo do mês continua compensável);
      ETFs, BDRs, futuros e opções NÃO têm isenção;
    - FII: ganho de capital 20%, rendimento isento.
  Exterior (IBKR) — Lei 14.754/2023: 15% sobre o ganho líquido do ANO (inclui variação cambial), com compensação de prejuízo.
  Renda fixa tributada (Tesouro, CDB, debênture comum): tabela regressiva — usamos 15% (prazo > 720 dias), conservador para giro curto
    seria até 22,5%.
  Isentos: LCI/LCA, debêntures incentivadas, CRI/CRA, rendimentos de FII.
  Caixa em CDI (Tesouro Selic/CDB): 15% ao ano sobre o rendimento — igual ao benchmark "CDI depois do IR".

Decomposição usada: cota = CDI + excesso. O CDI paga 15% ao ano (como o benchmark); o EXCESSO paga o IR da classe do fundo.
Para classes isentas isso é levemente conservador (cobra 15% sobre o CDI de uma parcela que, na prática, estava aplicada no ativo isento).
"""
import numpy as np
import pandas as pd

ALIQ = {"acoes": .15, "acoes_isentas": .15, "etf_b3": .15, "futuros_b3": .15, "opcoes_b3": .15, "day_trade": .20, "fii": .20,
        "exterior": .15, "renda_fixa": .15, "isento": 0.0, "cripto": .15}
MENSAL = {"acoes", "acoes_isentas", "etf_b3", "futuros_b3", "opcoes_b3", "day_trade", "fii", "cripto"}
ISENCAO = {"acoes": 20_000.0, "acoes_isentas": 20_000.0, "cripto": 35_000.0}   # cripto em corretora brasileira: vendas ≤ R$ 35 mil/mês isentas


def _cdi_liquido(cdi):
    out, cota = cdi.fillna(0).copy(), 1.0
    for _, x in cdi.fillna(0).groupby(cdi.index.year):
        ini = cota
        cota *= (1 + x).prod()
        imp = (cota - ini) * .15
        out.loc[x.index[-1]] = (1 + out.loc[x.index[-1]]) * (cota - imp) / cota - 1
        cota -= imp
    return out


def imposto_excesso(excesso, capital, classe, vendas_mensais=None):
    """excesso: retorno diário sobre o CDI (fração do capital). Devolve o excesso depois do IR (fração do capital), cobrando no último
    dia útil do período de apuração (mês para renda variável B3, ano para exterior/renda fixa)."""
    aliq = ALIQ.get(classe, .15)
    e = excesso.fillna(0)
    pnl = e * capital
    if aliq == 0:
        return e.copy()
    per = e.index.to_period("M" if classe in MENSAL else "Y")
    out = pnl.copy()
    prejuizo = 0.0
    for p, x in pnl.groupby(per):
        g = x.sum()
        if g <= 0:
            prejuizo += -g
            continue
        isento = (classe in ISENCAO and vendas_mensais is not None and float(vendas_mensais.get(p, np.inf)) <= ISENCAO[classe])
        if isento:
            continue                                     # lucro do mês isento; prejuízo acumulado fica para depois
        base = max(g - prejuizo, 0.0)
        prejuizo = max(prejuizo - g, 0.0)
        out.loc[x.index[-1]] -= base * aliq
    return out / capital


def vendas_mensais_de_pesos(W, capital):
    """Vendas de ações no mês em R$, a partir dos pesos-alvo W (fração do capital): reduções de posição comprada + zeragens."""
    W = W.fillna(0)
    vend = (W.shift(1).clip(lower=0) - W.clip(lower=0)).clip(lower=0).sum(axis=1) * capital
    return vend.groupby(vend.index.to_period("M")).sum()


def cota_apos_ir(r, cdi, capital, classe, vendas_mensais=None):
    """Cota diária depois do IR = CDI depois de 15% + excesso depois do IR da classe."""
    cdi = cdi.reindex(r.index).fillna(0)
    return _cdi_liquido(cdi) + imposto_excesso(r - cdi, capital, classe, vendas_mensais)
