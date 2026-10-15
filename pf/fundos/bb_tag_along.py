"""
Troca de controle / tag along: comprar a ON no anúncio da alienação de controle — frente "pf2_b3".

Mesa: pela Lei das S.A. (art. 254-A) quem compra o controle de companhia aberta é OBRIGADO a fazer OPA para as ações ON dos minoritários a
pelo menos 80% do preço pago ao controlador (100% no Novo Mercado; PN só se o estatuto der tag along). O preço pago ao controlador
costuma ter prêmio sobre a bolsa — o comprador é forçado por lei a comprar o minoritário. O mercado precifica com desconto (prazo de
CADE/agência reguladora/registro da OPA, 6–18 meses; risco de o negócio cair) e o arbitrador institucional não carrega small caps
ilíquidas. Diferente de b3_opa_leilao/rev_opa: lá o gatilho é a OPA com PREÇO lido no fato relevante; aqui o gatilho é o ANÚNCIO da troca
de controle (antes da OPA ser registrada — muitas vezes o FR nem traz o preço por ação), e a saída é por prazo ou pela OPA/deslistagem.
Eventos: IPE/CVM, Fato Relevante ou Comunicado com assunto "mudança de controle da companhia", "transferência do controle acionário",
"alienação/alteração de controle", "tag along" (exclui "sem alteração"), data = DATA DE ENTREGA; 1º evento por companhia em 250 pregões;
ticker = a ON (raiz+3) se negociada com ADV 60d >= R$ `adv_min` (classe="ON") ou o papel mais líquido da companhia (classe="liquida").
Execução: compra no fechamento de t+1+lag (meio spread real, ações inteiras), vende `hold` pregões depois; papel parado 30 pregões
(OPA liquidada/deslistagem) sai pelo último preço. R$ `frac` x capital por evento.
IR: ações (vendas pequenas -> isento na maior parte dos meses).
"""
import unicodedata

import numpy as np
import pandas as pd

import bb_base as BB

B, C, pf = BB.B, BB.C, BB.pf
DIAS = BB.DIAS

NOME = "Troca de controle: ON no anúncio (tag along obrigatório)"
TESE = ("Compro a ON da companhia que anunciou alienação de controle (o comprador é obrigado a fazer OPA a >= 80% do preço do controle) e "
        "seguro até a OPA/prazo; lote pequeno em small cap ilíquida")
BENCHMARK = "CDI"
INICIO, CORTE = "2014-03-01", "2021-01-01"
REGIME = "nenhum"
CLASSE_IR = "acoes"
CUSTO_TROCA = .001
PARAMS = {"hold": 126, "classe": "liquida", "adv_min": 5e4, "frac": .12}
GRADE = {"hold": [63, 126, 250], "classe": ["ON", "liquida"]}
VIZINHANCA = {"hold": (90, 180), "frac": (.08, .15), "adv_min": (2e4, 2e5)}
INSTRUMENTOS = [{"onde": "Clear/Rico/XP (corretagem zero; habilitação no leilão de OPA pela corretora)", "ticker": "ON da companhia-alvo",
                 "lote": "1 ação", "custo": "emolumentos 0,03% + meio spread real do fechamento + 0,2% no fracionário"}]
APLICAVEL = True
MOTIVO = "R$ 2,4 mil por evento com R$ 20 mil; alvos com ADV a partir de R$ 50 mil; 10–25 trocas de controle por ano"
ALAVANCAGENS = [1]
MOTIVO_ALAV = "limitado pelo nº de eventos, não pelo capital"
_CACHE = BB.Cache()
RX = (r"mudanca (de|do|no) controle|alienacao (de|do) controle|transferencia (de|do) controle|venda (de|do) controle|alteracao (de|do|no) "
      r"controle|troca de controle|novo controlador|alienacao do bloco de controle|tag along")


def _sa(s):
    return unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()


def carrega():
    d = BB.acoes()
    d = {k: d[k] for k in ("P", "R", "V", "BID", "ASK", "HS")}
    f = BB.DADOS / "controle_eventos.parquet"
    if not f.exists():
        i = pd.read_parquet(BB.FD / "cvm_ipe.parquet", columns=["CNPJ_Companhia", "Nome_Companhia", "Categoria", "Assunto", "Data_Entrega"])
        i = i[i.Categoria.isin(["Fato Relevante", "Comunicado ao Mercado"])]
        i["a"] = i.Assunto.fillna("").map(_sa)
        i = i[i.a.str.contains(RX) & ~i.a.str.contains(r"sem (alteracao|mudanca)|revoga|cancelamento|desistencia")]
        i["data"] = pd.to_datetime(i.Data_Entrega, errors="coerce")
        i["cnpj"] = BB.cnpj14(i.CNPJ_Companhia)
        i["rotulo"] = i.Nome_Companhia.str[:30] + " | " + i.Assunto.str[:70]
        i[["data", "cnpj", "rotulo"]].dropna().to_parquet(f, compression="zstd")
    d["ev"] = pd.read_parquet(f)
    return d


def roda(d, capital=20000, custo_mult=1, lag=0, alavancagem=1, hold=126, classe="ON", adv_min=5e4, frac=.12):
    hold = int(round(hold))
    key = (id(d), capital, custo_mult, lag, alavancagem, hold, classe, adv_min, round(frac, 4))

    def f():
        P = d["P"].reindex(DIAS)
        adv = d["V"].reindex(DIAS).fillna(0).rolling(60, min_periods=10).mean()
        rz = BB.mapa_cnpj()
        col_rz = pd.Series(P.columns, index=P.columns.str[:4]).groupby(level=0).apply(list)
        ev, ult = [], {}
        for _, e in d["ev"].sort_values("data").iterrows():
            i = DIAS.searchsorted(e.data)
            if i >= len(DIAS) or e.cnpj not in rz.index or e.data < pd.Timestamp(INICIO):
                continue
            if ult.get(e.cnpj, -10 ** 6) > i - 250:
                continue
            cols = [t for r in rz[e.cnpj] for t in col_rz.get(r, [])]
            a = adv.iloc[max(i - 1, 0)].reindex(cols).dropna()
            if classe == "ON":
                a = a[[t for t in a.index if t.endswith("3")]]
            a = a[a >= adv_min]
            if a.empty:
                continue
            ult[e.cnpj] = i
            ev.append((DIAS[i], a.idxmax(), e.rotulo))
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
    for kw in [{"hold": h, "classe": c} for h in GRADE["hold"] for c in GRADE["classe"]]:
        t = time.time()
        e = excesso(d, **kw)
        print(kw, "IS %.2f OOS %.2f (%.0fs)" % (C.anual(e[INICIO:CORTE]), C.anual(e[CORTE:]), time.time() - t), flush=True)
    ng = negocios(d)
    print(len(ng)); print(ng.sort_values("contrib_pp").iloc[list(range(5)) + list(range(-5, 0))].to_string())
