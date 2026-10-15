"""
LCI/LCA/CDB de bancos médios com FGC — NÃO testável (sem histórico de taxas por emissor). Módulo só documenta a conta e as premissas.

Tese de mesa: o varejo com FGC (até R$ 250 mil por CPF e instituição) pode carregar risco de banco médio sem risco de crédito efetivo;
LCI/LCA são isentas de IR para pessoa física. Um "fundo" seria: rodar uma escada de LCA/LCI de 9–12 meses (prazo mínimo CMN desde 2024:
9 meses para LCA e LCI) dos emissores que pagam mais, e CDB de banco médio quando o CDB líquido de IR supera a LCA.

Por que não há backtest:
  - não existe série pública de taxas de CDB/LCI/LCA POR EMISSOR (BCB, B3 e ANBIMA não publicam; plataformas mostram só a prateleira
    do dia). O BCB tem a taxa média mensal de CDB/RDB pós-fixado (SGS 28663), agregada e encerrada em jan/2024 — não serve para escolher
    emissor nem tem LCI/LCA;
  - o balcão B3 que temos (balcao.parquet) só traz DEB/CRI/CRA/LF/NC — sem CDB/LCI/LCA;
  - o retorno seria determinístico dado a taxa contratada (sem marcação a mercado para quem segura até o vencimento): o "backtest" seria
    só a premissa de taxa. Fica a conta do equivalente tributado (abaixo) e as taxas de prateleira citadas no caderno.

Conta (gross-up): uma LCA a p% do CDI isenta equivale a um CDB a p / (1 - aliquota) % do CDI. Com prazo de 9–12 meses a alíquota do CDB
é 20% (181–360 dias) ou 17,5% (361–720): LCA 90% do CDI = CDB 112,5% (9 meses) ou 109% (> 1 ano). Prateleiras de out/2026 (InfoMoney,
Seu Dinheiro): LCA até 86–88% do CDI, LCI até 83–88%, CDB de banco grande ~100–103% — ou seja, hoje a LCA ganha do CDB de 1 ano só se o
CDB pagar menos de ~104–107% do CDI.
"""
import numpy as np

NOME = "LCI/LCA/CDB de bancos médios (sem histórico — não testado)"
TESE = "Escada de LCA/LCI isentas (FGC) contra CDB tributado; escolher pelo equivalente bruto"
APLICAVEL = False
MOTIVO = "Sem histórico público de taxas por emissor (BCB/B3/ANBIMA); o retorno seria só a premissa de taxa. Ver caderno."
INSTRUMENTOS = [{"onde": "XP / BTG / Inter / Nubank / Rico (prateleira de bancários)", "ticker": "LCA/LCI 9–24 meses, CDB",
                 "lote": "R$ 1 mil (às vezes R$ 100)", "custo": "sem taxa explícita; carência até o vencimento; FGC até R$ 250 mil por CPF e instituição"}]


def aliquota(dias):
    return np.select([dias <= 180, dias <= 360, dias <= 720], [.225, .20, .175], .15)


def equivalente_tributado(pct_isento, dias):
    """% do CDI que um CDB precisa pagar para empatar com uma LCI/LCA a pct_isento % do CDI, no prazo `dias` (corridos)."""
    return pct_isento / (1 - aliquota(dias))
