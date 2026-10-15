"""Escolha dos parâmetros SÓ dentro da amostra (antes do CORTE): IR do excesso no IS para cada variante da grade (R$ 20 mil)."""
import importlib
import itertools
import sys

import numpy as np
import pandas as pd

import gl_comum as G


def escolhe(nome, capital=20000):
    m = importlib.import_module(nome)
    d = m.carrega()
    out = []
    for v in itertools.product(*m.GRADE.values()):
        p = dict(zip(m.GRADE, v))
        e = m.excesso(d, capital=capital, **{**m.PARAMS, **p})
        e = e[(e.index >= pd.Timestamp(m.INICIO))]
        i, o = e[e.index < pd.Timestamp(m.CORTE)], e[e.index >= pd.Timestamp(m.CORTE)]
        f = lambda x: G.C.anual(x + G.CDI.reindex(x.index).fillna(0)) - G.C.anual(G.CDI.reindex(x.index).fillna(0))
        out.append({**p, "IS pp": f(i), "IR IS": i.mean() / i.std() * np.sqrt(252) if i.std() > 0 else np.nan, "OOS pp": f(o)})
    return pd.DataFrame(out).sort_values("IR IS", ascending=False)


if __name__ == "__main__":
    pd.set_option("display.width", 200)
    for n in sys.argv[1:]:
        print(n)
        print(escolhe(n).round(2).to_string())
