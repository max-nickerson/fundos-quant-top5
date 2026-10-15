"""Diagnóstico das ordens limitadas (BDR e ETFs de cripto): quanto do resultado é o 'spread' capturado e quanto é o mercado andando."""
import numpy as np
import pandas as pd

import gl_comum as G


def decompoe(m, d, ref_fn):
    ng = m.negocios(d)
    V = ref_fn(d)
    fech, ref = V
    out = []
    for a, e, s, r in zip(ng.ativo, ng.entrada, ng.saida, ng["retorno_%"]):
        rr = ref[a].loc[e:s]
        rb = fech[a].loc[e:s]
        mov_ref = (rr.iloc[-1] / rr.iloc[0] - 1) * 100 if len(rr) > 1 and rr.iloc[0] > 0 else 0.0
        out.append({"ativo": a, "entrada": e, "ano": e.year, "ret_%": r, "mercado_%": mov_ref, "ret_hedge_%": r - mov_ref})
    x = pd.DataFrame(out)
    return x.groupby("ano")[["ret_%", "mercado_%", "ret_hedge_%"]].mean().assign(n=x.groupby("ano").size()), x


if __name__ == "__main__":
    import gl_bdr_limite as B
    import gl_cripto_premio as Cp
    pd.set_option("display.width", 200)
    d = B.carrega()
    X = B._painel(d)
    ref = X["U"].mul(X["fx"], axis=0)
    t, _ = decompoe(B, d, lambda d: (X["V"]["fech"], ref))
    print("BDR (ret = BDR da compra à venda; mercado = ação EUA x dólar do fechamento da entrada ao da saída)\n", t.round(3))
    d2 = Cp.carrega()
    V, U, J, HS, r_ = Cp._painel(d2)
    t2, _ = decompoe(Cp, d2, lambda d: (V["fech"], U))
    print("ETFs cripto\n", t2.round(3))
