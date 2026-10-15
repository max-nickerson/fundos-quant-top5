"""
Treasury americano com hedge para CDI (ETF T10R11 da B3) — prêmio de prazo dos EUA em R$, sem remessa.

O que foi pesquisado (out/2026):
  - existe ETF de Treasury hedgeado na B3: T10R11 (lançado em 2025; replica um índice S&P de futuros de Treasury de 10 anos "em reais",
    com hedge cambial embutido) — https://www.seudinheiro.com/2025/bolsa-dolar/e-renda-fixa-mas-e-dos-eua-etf-inedito-para-investir-no-tesouro-americano-com-protecao-da-variacao-do-dolar-chega-a-b3-mlim/
    ; BDRs de ETF de Treasury (BIYT39 7–10 anos, BTLT39 20+ anos) NÃO têm hedge (risco de juro + câmbio) — https://edu.b3.com.br/w/etf-renda-fixa-internacional
  - T-bill "financiado pelo CDI": com hedge, um T-bill rende o CDI MENOS custos (paridade coberta: o futuro de dólar devolve exatamente o
    diferencial); sem hedge é aposta no dólar (reprovada: "câmbio sem hedge sobre o capital inteiro"). Pela IBKR o caminho é pior:
    remessa (IOF 1,1% + spread 0,5% na ida, 0,38% + 0,5% na volta), saldo parado sem CDI e hedge em WDO de US$ 10 mil — com R$ 20 mil
    (US$ 3,7 mil) o hedge arredonda para ZERO contrato. Logo: o único Treasury que faz sentido para o PF é o de PRAZO, hedgeado na B3.
Tese de mesa: o ETF hedgeado rende CDI + (retorno do futuro de 10 anos - juro curto americano) = CDI + prêmio de prazo dos EUA. Esse prêmio
não é sempre positivo (2022: -15%). Quando pagar? (i) curva positivamente inclinada (carry e rolldown a favor), (ii) Fed cortando (o PU
sobe na direção do ciclo) ou (iii) depois de uma venda forte de 10 anos sem o Fed subir — vendedores forçados (hedge de convexidade de
hipotecas, risk-parity desalavancando, estrangeiros oficiais) empurram o yield acima do caminho de juros e o prêmio volta.

Implementação:
  - retorno em excesso diário do ETF = retorno total do IEF (7–10 anos) ou IEI (3–7 anos) em US$ - T-bill 3 meses - taxa de adm. 0,30% a.a.
    (premissa; sem histórico do T10R11 antes de 2025 — o futuro de 10 anos é ~ IEF menos repo) — convertido ao calendário da B3;
  - sinal (dados até t, FRED/ETF do dia anterior ao pregão B3 quando necessário):
      "inclinacao": 10 anos - 3 meses >= 0,5 pp;  "ciclo": Fed funds caiu >= 25 bp em 126 pregões;
      "venda_forte": 10 anos subiu >= 50 bp em 63 pregões e o Fed funds não subiu nesse período -> carrega 63 pregões;
  - 100% do capital no ETF quando ligado; custo de varejo 0,25% por lado (spread de ETF pouco líquido + emolumentos), x custo_mult;
  - IR: ETF de renda fixa na B3 (15% para ETF de prazo longo, retido na venda) -> classe "etf_b3".
Dados: Yahoo (IEF/IEI) e FRED 2008+. Corte OOS 2021-01-01.
"""
import numpy as np
import pandas as pd

import jx_comum as J

NOME = "Treasury 10 anos hedgeado para CDI (T10R11) com regra de prêmio"
TESE = ("Carrego o ETF de Treasury com hedge para CDI da B3 só quando o prêmio de prazo americano tende a pagar: curva inclinada, Fed "
        "cortando ou depois de venda forte de 10 anos sem o Fed subir")
BENCHMARK = "CDI"
INICIO, CORTE = "2008-06-01", "2021-01-01"
REGIME = "nenhum"
CUSTO_TROCA = 0.0
PARAMS = {"regra": "inclinacao", "ativo": "iei", "thr": 0.5, "dias": 63}     # maior IR no IS (2008-2020)
GRADE = {"regra": ["inclinacao", "ciclo", "venda_forte"], "ativo": ["ief", "iei"]}
VIZINHANCA = {"thr": (0.3, 0.8), "dias": (42, 90)}
CLASSE_IR = "etf_b3"
TAXA_ADM, CUSTO_LADO = .003, .0025
INSTRUMENTOS = [{"onde": "B3 (qualquer corretora)", "ticker": "T10R11 (Treasury 10 anos com hedge para R$)", "lote": "1 cota",
                 "custo": "spread ~0,2–0,4% + emolumentos 0,03% por lado; taxa de administração (premissa 0,30% a.a.)"}]
APLICAVEL = "parcial"
MOTIVO = ("O ETF existe desde 2025 (o histórico é sintético: IEF/IEI - T-bill + CDI). Liquidez ainda baixa; T-bill com hedge = CDI - custos "
          "(não testado: perde por construção); IBKR com WDO não fecha o hedge com R$ 20 mil.")
ALAVANCAGENS = [1]
MOTIVO_ALAV = "ETF à vista; alavancar exigiria termo/margem em ETF de renda fixa (não oferecido ao varejo) ou micro yield na CME (já testado)."
VARIANTES = {"sempre comprado (beta do prêmio de prazo)": {"regra": "sempre"}}


def carrega():
    return {"mkt": J.mercado()}


def ret_exc(d, ativo):
    def f():
        r = J.ret_eua(d, ativo)
        tb = (J.serie(d, "dgs3mo") / 100).fillna(0)
        dt = pd.Series(J.DIAS, index=J.DIAS).diff().dt.days.fillna(1).clip(upper=5)
        return r - tb * dt / 360 - TAXA_ADM / 252
    return J.memo(("tr", ativo), d["mkt"], f)


def _sinal(d, regra, thr, dias):
    y10, y3m, ff = J.serie(d, "dgs10"), J.serie(d, "dgs3mo"), J.serie(d, "dff", limit=10)
    if regra == "sempre":
        on = pd.Series(True, index=J.DIAS)
    elif regra == "inclinacao":
        on = (y10 - y3m) >= thr
    elif regra == "ciclo":
        on = (ff - ff.shift(126)) <= -.25
    else:
        ent = ((y10 - y10.shift(63)) >= .5) & ((ff - ff.shift(63)) < .25)
        on = J.maquina(ent, pd.Series(False, index=J.DIAS), int(dias))
    fim = d["mkt"].index.max()
    return on.fillna(False) & pd.Series(J.DIAS <= fim, index=J.DIAS)


def _livro(d, capital=20000, custo_mult=1, lag=0, regra=PARAMS["regra"], ativo=PARAMS["ativo"], thr=PARAMS["thr"], dias=PARAMS["dias"]):
    on = _sinal(d, regra, thr, dias).astype(float)
    W = pd.DataFrame({"T10R11": on})
    R = pd.DataFrame({"T10R11": ret_exc(d, ativo)})
    e = J.C.carteira(W, R, CUSTO_LADO * custo_mult, lag)
    return {"e": e, "on": on.astype(bool), "W": W, "R": R}


def excesso(d, capital=20000, custo_mult=1, lag=0, regime=REGIME, alavancagem=1, **params):
    L = _livro(d, capital, custo_mult, lag, **{**PARAMS, **params})
    return J.C.aplica_regime(L["e"], regime, CUSTO_TROCA * custo_mult)


def classes_ir(d, capital=20000, **params):
    return {CLASSE_IR: _livro(d, capital, **{**PARAMS, **params})["e"] * capital}


def posicoes(d, **params):
    L = _livro(d, **{**PARAMS, **params})
    return L["W"], L["R"]


def negocios(d, capital=20000, **params):
    p = {**PARAMS, **params}
    L = _livro(d, capital, **p)
    ng = J.negocios_de_estado(L["on"], L["e"], f"T10R11 ({p['ativo'].upper()} sintético)")
    if len(ng):
        y10 = J.serie(d, "dgs10")
        ng["y10_entrada"] = [y10.get(a) for a in ng.entrada]
        ng["y10_saida"] = [y10.get(b) for b in ng.saida]
    return ng
