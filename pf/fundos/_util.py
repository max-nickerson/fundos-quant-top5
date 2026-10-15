"""
Utilidades comuns aos fundos PF da frente "revisita" (pf/fundos/rev_*.py). Não altera comum.py/robustez.py/pf.py.

- Caminhos dos dados brutos já baixados (quant/fundos/dados e quant/dados) e um cache local em pf/dados/<fundo>/.
- IR de ações de pessoa física: separa o P&L de cada mês em "acoes_isentas" (vendas no mês ≤ R$ 20 mil) e "acoes".
- Convenção de classes_ir(d, capital, **params): dict classe -> P&L diário em R$ (ganho tributável REAL da classe, sem o CDI do caixa),
  mais a chave especial "_cdi_perdido": R$ de CDI que o capital aplicado fora do CDI deixou de ganhar (positivo). O excesso antes do IR
  deve bater com (soma das classes - _cdi_perdido) / capital. O runner calcula o excesso depois do IR como
  [apos_ir_por_classe(classes) - 0,85 x _cdi_perdido] / capital  (o CDI perdido também teria pago 15%).
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

PF = Path(__file__).resolve().parent.parent
RAIZ = PF.parent
for p in (str(RAIZ), str(PF)):
    if p not in sys.path:
        sys.path.insert(0, p)

import comum as C  # noqa: E402
import pf  # noqa: E402

QUANT = RAIZ.parent                               # .../itau/quant
FD = QUANT / "fundos" / "dados"                   # dados da pesquisa de 109 estratégias
QD = QUANT / "dados"                              # dados da rodada 1
TOP5 = RAIZ / "dados"                             # dados do repositório top 5
CACHE = PF / "dados"


def cache(nome, f):
    """Lê pf/dados/<nome>.parquet se existir; senão roda f() (que lê os dados brutos), salva e devolve. Só DataFrame."""
    p = CACHE / f"{nome}.parquet"
    if p.exists():
        return pd.read_parquet(p)
    x = f()
    p.parent.mkdir(parents=True, exist_ok=True)
    x.to_parquet(p, compression="zstd")
    return x


def acoes_ir(pnl, vendas):
    """pnl: P&L diário em R$ de ações à vista (swing); vendas: R$ vendidos por dia. Meses com vendas ≤ R$ 20 mil -> isentos."""
    pnl = pnl.reindex(C.DIAS).fillna(0)
    v = vendas.reindex(C.DIAS).fillna(0)
    mes = C.DIAS.to_period("M")
    isento = pd.Series(mes.map(v.groupby(mes).sum() <= 20_000), index=C.DIAS).astype(bool)
    return {"acoes_isentas": pnl.where(isento, 0.0), "acoes": pnl.where(~isento, 0.0)}


def soma_classes(*dicts):
    out = {}
    for dd in dicts:
        for k, v in dd.items():
            v = v.reindex(C.DIAS).fillna(0)
            out[k] = out[k] + v if k in out else v
    return out


def cdi_perdido(valor_aplicado_brl):
    """R$ de CDI que deixam de ser ganhos por manter `valor_aplicado_brl` (série diária, valor em t-1) fora do CDI."""
    return valor_aplicado_brl.reindex(C.DIAS).fillna(0).shift(1).fillna(0) * C.CDI
