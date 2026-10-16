"""
Peças comuns da frente "pf3_mecanismos" (pf/fundos/mx_*.py): transferência dos 4 mecanismos dos vencedores auditados para modelos que
falharam ou foram marginais. Não altera comum.py/robustez.py/pf.py.

- `contrato(g, roda)`: define excesso/classes_ir/posicoes/negocios no módulo a partir de roda(d, capital, custo_mult, lag, alavancagem,
  **params) -> dict no formato do motor de carteira PF (b3_base.carteira_pf / bb_base.episodios): e, pnl, custo, cdi_perdido, vendas, W,
  negocios e, opcionalmente, R (retorno total usado) e classes (dict de IR pronto).
- `escolhe_is(m, d)`: roda a GRADE e escolhe a variante de maior IR DENTRO da amostra (antes do CORTE), entre as que têm >= 10 negócios no IS. É a regra de escolha de todos os
  mx_*: o OOS é impresso só para o caderno, nunca para escolher.
"""
import itertools
import sys
from pathlib import Path

import numpy as np
import pandas as pd

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import bb_base as BB  # noqa: E402

B, C, pf = BB.B, BB.C, BB.pf
DIAS, CDI = BB.DIAS, BB.CDI


def contrato(g, roda):
    def _p(params):
        return {**g["PARAMS"], **params}

    def excesso(d, capital=20000, custo_mult=1, lag=0, regime=None, alavancagem=1, **params):
        e = roda(d, capital, custo_mult, lag, alavancagem, **_p(params))["e"]
        return C.aplica_regime(e, regime or g.get("REGIME", "nenhum"), g.get("CUSTO_TROCA", .001) * custo_mult)

    def classes_ir(d, capital=20000, **params):
        r = roda(d, capital, 1, 0, 1, **_p(params))
        if "classes" in r:
            return r["classes"]
        return B.classes_acoes(r)

    def posicoes(d, capital=20000, **params):
        r = roda(d, capital, 1, 0, 1, **_p(params))
        W = r["W"]
        R = r.get("R", d.get("R"))
        return W, R.reindex(index=DIAS, columns=W.columns).fillna(0).sub(CDI, axis=0)

    def negocios(d, capital=20000, **params):
        return roda(d, capital, 1, 0, 1, **_p(params))["negocios"]

    g.update(excesso=excesso, classes_ir=classes_ir, posicoes=posicoes, negocios=negocios)


def ir_aa(e):
    e = e.dropna()
    return e.mean() / e.std() * np.sqrt(252) if e.std() > 0 else np.nan


N_MIN_IS = 10


def escolhe_is(m, d, capital=20000, mostrar_oos=True):
    """Roda a grade; escolhe pelo maior IR no IS entre as variantes com >= N_MIN_IS negócios no IS. Devolve (DataFrame, melhor dict)."""
    ks = list(m.GRADE)
    L = []
    for v in itertools.product(*[m.GRADE[k] for k in ks]):
        kw = dict(zip(ks, v))
        e = m.excesso(d, capital=capital, **kw)
        e = e[e.index >= pd.Timestamp(m.INICIO)]
        i, o = e[e.index < pd.Timestamp(m.CORTE)], e[e.index >= pd.Timestamp(m.CORTE)]
        n = m.negocios(d, capital=capital, **kw)
        ni = int((pd.to_datetime(n["entrada"]) < pd.Timestamp(m.CORTE)).sum()) if len(n) else 0
        L.append({**kw, "IS pp": C.anual(i + CDI.reindex(i.index)) - C.anual(CDI.reindex(i.index)), "IR IS": ir_aa(i), "n IS": ni,
                  "OOS pp": C.anual(o + CDI.reindex(o.index)) - C.anual(CDI.reindex(o.index)), "n OOS": len(n) - ni})
    t = pd.DataFrame(L)
    ok = t["n IS"] >= N_MIN_IS                                   # variante com menos de 10 negócios no IS não é escolhível
    best = t.loc[t["IR IS"].where(ok).fillna(-9).idxmax(), ks].to_dict()
    print(t.round(2).to_string() if mostrar_oos else t.drop(columns=["OOS pp", "n OOS"]).round(2).to_string())
    print("escolhida no IS:", best, flush=True)
    return t, best


def proximo(datas, alvo):
    """Índice em DIAS do 1º pregão >= alvo (vetorizado)."""
    return DIAS.searchsorted(pd.DatetimeIndex(alvo))
