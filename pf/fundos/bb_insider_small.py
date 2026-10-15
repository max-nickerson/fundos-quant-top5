"""
Insiders comprando em small caps (VLMO/CVM), em lote pequeno — frente "pf2_b3".

Mesa: controlador, conselheiro e diretor são obrigados (Res. CVM 44, art. 11) a informar à CVM, até o 10º dia do mês seguinte, tudo o
que negociaram. Compra líquida relevante de quem conhece a empresa é informação — e em small cap ilíquida (ADV < R$ 2 mi) o institucional
não consegue seguir o sinal (a pesquisa institucional só testou ADV >= R$ 2 mi). A PF com R$ 2 mil por papel segue sem mover o preço.
"Recompra executada" (a própria companhia comprando em tesouraria) NÃO está no VLMO baixado (o formulário consolidado só traz
administradores/controladores; não há linha de tesouraria) — fica como próximo passo.
Dados: quant/fundos/dados/cvm_vlmo.parquet (posição consolidada mensal; última versão por companhia/mês). Compras e vendas à vista de
ações/units de pessoas da Companhia e da Controladora; R$ líquido do mês. Data do sinal = DATA DE ENTREGA do formulário (descarta
entregas > 75 dias após o mês de referência). Obs.: o arquivo tem acentos corrompidos ("Compra � vista") — casamos por prefixo.
Regra: compra líquida >= `limiar` x giro mensal (ADV 60d x 21) do papel mais líquido da companhia; ADV entre R$ `adv_min` e R$ 2 mi
(small/micro cap — o pedaço que o institucional não testou); compra no fechamento de t+1+lag, segura `hold` pregões. R$ `frac` x capital.
IR: ações (vendas pequenas -> isento na maioria dos meses).
"""
import numpy as np
import pandas as pd

import bb_base as BB

B, C, pf = BB.B, BB.C, BB.pf
DIAS = BB.DIAS

NOME = "Insiders comprando small caps (VLMO, lote pequeno)"
TESE = ("Compro a small cap (ADV < R$ 2 mi) em que controlador/administradores fizeram compra líquida relevante no mês (formulário VLMO "
        "entregue à CVM) e seguro hold pregões; o institucional não escala nesse tamanho")
BENCHMARK = "CDI"
INICIO, CORTE = "2019-01-01", "2023-01-01"
REGIME = "nenhum"
CLASSE_IR = "acoes"
CUSTO_TROCA = .001
PARAMS = {"limiar": .02, "hold": 126, "adv_min": 5e4, "adv_max": 2e6, "frac": .10}
GRADE = {"limiar": [.02, .05, .10], "hold": [63, 126]}
VIZINHANCA = {"limiar": (.015, .035), "hold": (90, 160), "adv_min": (2e4, 1e5)}
INSTRUMENTOS = [{"onde": "Clear/Rico/XP (corretagem zero)", "ticker": "small caps com compra de insider", "lote": "1 ação",
                 "custo": "emolumentos 0,03% + meio spread real do fechamento + 0,2% no fracionário"}]
APLICAVEL = True
MOTIVO = "small caps com ADV R$ 50 mil–2 mi; R$ 2 mil por papel com R$ 20 mil"
ALAVANCAGENS = [1]
MOTIVO_ALAV = "papel ilíquido: alavancar só aumenta o lote"
_CACHE = BB.Cache()


def carrega():
    d = BB.acoes()
    d = {k: d[k] for k in ("P", "R", "V", "BID", "ASK", "HS")}
    f = BB.DADOS / "vlmo_liquido.parquet"
    if not f.exists():
        v = pd.read_parquet(BB.FD / "cvm_vlmo.parquet", columns=["CNPJ_Companhia", "Data_Referencia", "Versao", "Data_Entrega", "Tipo_Empresa",
                                                                 "Tipo_Cargo", "Tipo_Movimentacao", "Tipo_Ativo", "Volume", "Quantidade", "Preco_Unitario"])
        v["Versao"] = pd.to_numeric(v.Versao, errors="coerce")
        v = v[v.Versao == v.groupby(["CNPJ_Companhia", "Data_Referencia"]).Versao.transform("max")]
        mov = v.Tipo_Movimentacao.fillna("")
        v = v[v.Tipo_Empresa.isin(["Companhia", "Controladora"]) & v.Tipo_Ativo.fillna("").str.match(r"^(A..es|Units)$")
              & mov.str.match(r"^(Compra|Venda)( . vista)?$")]
        vol = pd.to_numeric(v.Volume, errors="coerce")
        vol = vol.fillna(pd.to_numeric(v.Quantidade, errors="coerce") * pd.to_numeric(v.Preco_Unitario, errors="coerce"))
        v["liq"] = np.where(v.Tipo_Movimentacao.str.startswith("Compra"), 1, -1) * vol
        g = v.groupby(["CNPJ_Companhia", "Data_Referencia"]).agg(liq=("liq", "sum"), data=("Data_Entrega", "max")).reset_index()
        g["data"] = pd.to_datetime(g.data, errors="coerce")
        g["ref"] = pd.to_datetime(g.Data_Referencia, errors="coerce")
        g = g[(g.data - g.ref).dt.days.between(0, 75)]
        g["cnpj"] = BB.cnpj14(g.CNPJ_Companhia)
        g[["data", "ref", "cnpj", "liq"]].to_parquet(f, compression="zstd")
    d["vlmo"] = pd.read_parquet(f)
    return d


def roda(d, capital=20000, custo_mult=1, lag=0, alavancagem=1, limiar=.05, hold=126, adv_min=5e4, adv_max=2e6, frac=.10):
    hold = int(round(hold))
    key = (id(d), capital, custo_mult, lag, alavancagem, round(limiar, 4), hold, adv_min, adv_max, round(frac, 4))

    def f():
        P = d["P"].reindex(DIAS)
        adv = d["V"].reindex(DIAS).fillna(0).rolling(60, min_periods=20).mean()
        rz = BB.mapa_cnpj()
        col_rz = pd.Series(P.columns, index=P.columns.str[:4]).groupby(level=0).apply(list)
        g = d["vlmo"]
        g = g[(g.liq > 0) & g.cnpj.isin(rz.index) & (g.data >= pd.Timestamp(INICIO))].sort_values("data")
        ev = []
        for dt, c, liq in zip(g.data, g.cnpj, g.liq):
            i = DIAS.searchsorted(dt)
            if i >= len(DIAS):
                continue
            cols = [t for r in rz[c] for t in col_rz.get(r, [])]
            a = adv.iloc[max(i - 1, 0)].reindex(cols).dropna()
            if a.empty or not a.max() > 0:
                continue
            t, av = a.idxmax(), a.max()
            if not (adv_min <= av < adv_max) or liq / (av * 21) < limiar:
                continue
            ev.append((DIAS[i], t, f"insider compra R$ {liq / 1e3:,.0f} mil = {liq / (av * 21) * 100:.0f}% do giro mensal"))
        ev = pd.DataFrame(ev, columns=["data", "ticker", "rotulo"])
        res = BB.episodios(ev, d, capital, hold, frac * capital * alavancagem, custo_mult, lag, alavancagem)
        res["negocios"] = BB.rotula(res["negocios"], ev)
        return res
    return _CACHE.get(key, f)


def excesso(d, capital=20000, custo_mult=1, lag=0, regime=REGIME, alavancagem=1, **params):
    e = roda(d, capital, custo_mult, lag, alavancagem, **{**PARAMS, **params})["e"]
    return C.aplica_regime(e, regime, CUSTO_TROCA * custo_mult)


def classes_ir(d, capital=20000, **params):
    return B.classes_acoes(roda(d, capital, **{**PARAMS, **params}))


def posicoes(d, capital=20000, **params):
    W = roda(d, capital, **{**PARAMS, **params})["W"]
    return W, d["R"].reindex(index=DIAS, columns=W.columns).fillna(0).sub(BB.CDI, axis=0)


def negocios(d, capital=20000, **params):
    return roda(d, capital, **{**PARAMS, **params})["negocios"]


if __name__ == "__main__":
    import time
    d = carrega()
    print(len(d["vlmo"]), (d["vlmo"].liq > 0).sum())
    for kw in [{"limiar": l, "hold": h} for l in GRADE["limiar"] for h in GRADE["hold"]]:
        t = time.time()
        e = excesso(d, **kw)
        print(kw, "IS %.2f OOS %.2f (%.0fs) n=%d" % (C.anual(e[INICIO:CORTE]), C.anual(e[CORTE:]), time.time() - t, len(negocios(d, **kw))), flush=True)
