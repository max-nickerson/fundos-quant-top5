"""
mx_vencimento_queda — frente pf3_mecanismos. Mecanismo 1 (calendário obriga) + 3 (magnitude) aplicados ao bb_vencimento_opcoes
(OOS +1,3 pp, sem os 10 melhores −3,9: marginal).

Inspiração: bb_dividendo_extra_aud (o calendário cria o fluxo; o edge só paga quando o evento é GRANDE) e b3_leilao_noite_aud (comprar
quem foi vendido à força).
Hipótese: o vencimento mensal de opções obriga o lançador coberto/financiador a entregar ou rolar e o formador a desmontar o delta-hedge;
essa venda mecânica só deixa marca de preço quando foi GRANDE — nos objetos que caíram forte nos pregões até o vencimento. Em vez da cesta
inteira todo mês (o original), compro no fechamento do vencimento só os objetos que caíram >= `queda` nos `jan` pregões até a véspera e vendo
`k` pregões depois.
Universo (raízes com opções mais negociadas na B3 de 2014–2026; escolhido pelo volume de opções, que é conhecido, mas com algum viés de
quem continuou líquido): PETR4, PETR3, VALE3, ITUB4, BBDC4, BBAS3, ABEV3, ITSA4, MGLU3, GGBR4, CSNA3, USIM5.
Execução: calendário de vencimentos da B3 (bb_vencimento_opcoes.vencimentos, conhecido antes), decisão no fechamento da véspera, compra no
fechamento do vencimento (t+1), R$ `frac` x capital por objeto (até o caixa), ações inteiras, custo real (bb_base). IR: ações.
Regra (queda x k) escolhida só no IS (2014–2020) pelo maior IR.
"""
import pandas as pd

import _mx_comum as X
import bb_vencimento_opcoes as O

BB, B, C, pf, DIAS = X.BB, X.B, X.C, X.pf, X.DIAS

NOME = "Vencimento de opções só nos objetos que caíram forte (calendário + magnitude)"
TESE = ("Compro no fechamento do vencimento só os objetos de opção que caíram >= queda nos pregões anteriores (a venda mecânica foi grande) "
        "e vendo k pregões depois")
BENCHMARK = "CDI"
INICIO, CORTE = O.INICIO, O.CORTE
REGIME = "nenhum"
CLASSE_IR = "acoes"
CUSTO_TROCA = .001
UNIV = ["PETR4", "PETR3", "VALE3", "ITUB4", "BBDC4", "BBAS3", "ABEV3", "ITSA4", "MGLU3", "GGBR4", "CSNA3", "USIM5"]
PARAMS = {"queda": .06, "k": 1, "jan": 5, "frac": .25}
GRADE = {"queda": [0.0, .02, .04, .06], "k": [1, 3]}
VIZINHANCA = {"queda": (.045, .08), "jan": (3, 7), "frac": (.15, .30)}
INSTRUMENTOS = [{"onde": "Clear/Rico/XP (corretagem zero)", "ticker": ", ".join(UNIV), "lote": "1 ação (fracionário)",
                 "custo": "emolumentos 0,03% + meio spread real + 0,2% no fracionário"}]
APLICAVEL = True
MOTIVO = "blue chips no fracionário; poucas entradas por mês"
ALAVANCAGENS = [1]
MOTIVO_ALAV = "R$ frac por objeto; o caixa limita"
_CACHE = BB.Cache()


def carrega():
    a = BB.acoes()
    return {k: a[k][[t for t in UNIV if t in a[k].columns]] for k in ("P", "R", "V", "BID", "ASK", "HS")}


def roda(d, capital=20000, custo_mult=1, lag=0, alavancagem=1, queda=.04, k=3, jan=5, frac=.25):
    k, jan = int(round(k)), int(round(jan))
    key = (id(d), capital, custo_mult, lag, alavancagem, round(queda, 4), k, jan, round(frac, 4))

    def f():
        P = d["P"].reindex(DIAS)
        R = d["R"].reindex(DIAS).fillna(0)
        acum = (1 + R).rolling(jan).apply(lambda x: x.prod(), raw=True) - 1
        fim_dados = P.dropna(how="all").index.max()
        ev = []
        for v in O.vencimentos():
            i = DIAS.get_loc(v) - 1
            if i < jan or DIAS[i] > fim_dados:
                continue
            q = acum.iloc[i]
            for t in q.index[(q <= -queda) & P.iloc[i].notna()] if queda > 0 else q.index[P.iloc[i].notna()]:
                ev.append((DIAS[i], t, f"vencimento {v:%Y-%m-%d} ({q[t] * 100:+.1f}% em {jan} pregões)"))
        ev = pd.DataFrame(ev, columns=["data", "ticker", "rotulo"])
        res = BB.episodios(ev, d, capital, k, frac * capital * alavancagem, custo_mult, lag, alavancagem, vol_min=10)
        res["negocios"] = BB.rotula(res["negocios"], ev)
        return res
    return _CACHE.get(key, f)


X.contrato(globals(), roda)

if __name__ == "__main__":
    import sys
    X.escolhe_is(sys.modules[__name__], carrega())
