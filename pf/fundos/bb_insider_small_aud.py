"""
bb_insider_small — AUDITADA (pf/pesquisa/auditoria_pf2.md, item 6). Mesmo motor e regra; a leitura do VLMO usa `_texto_cvm.normaliza`
(casamento EXATO de "compra a vista"/"compra"/"venda a vista"/"venda" e "acoes"/"units", à prova de mojibake e U+FFFD) em vez do regex
com curinga. Resultado da auditoria: o parquet já estava certo (o "�" era só o console) e o regex com '.' já casava — as mesmas
11.048 companhias-mês; o fundo não muda. Cache próprio: pf/dados/auditoria/vlmo_liquido_norm.parquet.
"""
import numpy as np
import pandas as pd

import bb_insider_small as O
from _texto_cvm import normaliza
from bb_insider_small import BB, B, C, pf, DIAS  # noqa: F401

NOME = "Insiders comprando small caps (VLMO, lote pequeno) — AUDITADA (leitura normalizada do VLMO)"
TESE, BENCHMARK, INICIO, CORTE, REGIME, CLASSE_IR, CUSTO_TROCA = O.TESE, O.BENCHMARK, O.INICIO, O.CORTE, O.REGIME, O.CLASSE_IR, O.CUSTO_TROCA
PARAMS = dict(O.PARAMS)
GRADE = dict(O.GRADE)
VIZINHANCA = dict(O.VIZINHANCA)
INSTRUMENTOS, APLICAVEL, MOTIVO, ALAVANCAGENS, MOTIVO_ALAV = O.INSTRUMENTOS, O.APLICAVEL, O.MOTIVO, O.ALAVANCAGENS, O.MOTIVO_ALAV
CACHE = B.PF / "dados" / "auditoria" / "vlmo_liquido_norm.parquet"
MOV = {"compra a vista": 1, "compra": 1, "venda a vista": -1, "venda": -1}


def vlmo_liquido():
    if CACHE.exists():
        return pd.read_parquet(CACHE)
    v = pd.read_parquet(BB.FD / "cvm_vlmo.parquet", columns=["CNPJ_Companhia", "Data_Referencia", "Versao", "Data_Entrega", "Tipo_Empresa",
                                                             "Tipo_Movimentacao", "Tipo_Ativo", "Volume", "Quantidade", "Preco_Unitario"])
    v["Versao"] = pd.to_numeric(v.Versao, errors="coerce")
    v = v[v.Versao == v.groupby(["CNPJ_Companhia", "Data_Referencia"]).Versao.transform("max")]
    mov, ativo, emp = normaliza(v.Tipo_Movimentacao), normaliza(v.Tipo_Ativo), normaliza(v.Tipo_Empresa)
    v = v[emp.isin(["companhia", "controladora"]) & ativo.isin(["acoes", "units"]) & mov.isin(list(MOV))]
    vol = pd.to_numeric(v.Volume, errors="coerce")
    vol = vol.fillna(pd.to_numeric(v.Quantidade, errors="coerce") * pd.to_numeric(v.Preco_Unitario, errors="coerce"))
    v = v.assign(liq=normaliza(v.Tipo_Movimentacao).map(MOV) * vol)
    g = v.groupby(["CNPJ_Companhia", "Data_Referencia"]).agg(liq=("liq", "sum"), data=("Data_Entrega", "max")).reset_index()
    g["data"] = pd.to_datetime(g.data, errors="coerce")
    g["ref"] = pd.to_datetime(g.Data_Referencia, errors="coerce")
    g = g[(g.data - g.ref).dt.days.between(0, 75)]
    g["cnpj"] = BB.cnpj14(g.CNPJ_Companhia)
    g = g[["data", "ref", "cnpj", "liq"]].reset_index(drop=True)
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    g.to_parquet(CACHE)
    return g


def carrega():
    d = O.carrega()
    d["vlmo"] = vlmo_liquido()
    return d


def excesso(d, capital=20000, custo_mult=1, lag=0, regime=REGIME, alavancagem=1, **params):
    return O.excesso(d, capital, custo_mult, lag, regime, alavancagem, **params)


classes_ir, posicoes, negocios = O.classes_ir, O.posicoes, O.negocios

if __name__ == "__main__":
    a = vlmo_liquido()
    b = pd.read_parquet(BB.DADOS / "vlmo_liquido.parquet")
    m = a.merge(b, on=["cnpj", "ref"], how="outer", suffixes=("_norm", "_orig"), indicator=True)
    print("normalizado", a.shape, (a.liq > 0).sum(), "| original", b.shape, (b.liq > 0).sum())
    print(m._merge.value_counts().to_dict(), "| |dif liq| máx:", (m.liq_norm - m.liq_orig).abs().max())
