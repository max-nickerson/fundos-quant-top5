"""
Venda coberta (covered call) em ações isentas de IR: PETR4, VALE3, ITUB4 em lotes de 100, call de 1 mês vendida só quando a vol paga.

Tese de mesa: a pessoa física tem um benefício que nenhum fundo tem — vendas de ações de até R$ 20 mil no mês são ISENTAS de IR
(e dividendos são isentos). Com R$ 20–50 mil, uma carteira de 3 blue chips com opções quase nunca passa do limite. A ideia: carregar a
ação (ganho isento) e vender a call de 1 mês OTM (prêmio tributado a 15% em opções, mas que compensa perdas da mesma classe) nos meses
em que a IV está cara — o comprador de call de PETR/VALE paga pela "loteria" (alta violenta de commodity/política) e pelo evento
(resultado, dividendo). Filtros: sempre / IV acima da mediana dos 12 ciclos anteriores (iv_alta) / IV > vol realizada 21d (iv_rv).

Aviso da pesquisa (arbitragem.md A6): em PETR4/VALE3 o overlay de calls PERDEU (−1 a −4% a.a.): as altas de PETR/VALE são
violentas. O fundo é, antes de tudo, AÇÕES − CDI (beta): o relatório separa as duas partes.

Implementação: a cada ciclo mensal (sinal no 1º pregão após o vencimento, execução t+1) o capital x alav é dividido em 3 e cada parte
compra lotes INTEIROS de 100 (piso) — resto em Selic. Ação com retorno total (proventos e bonificações, Yahoo) sobre o preço bruto do
COTAHIST; o dinheiro na ação deixa de render CDI (excesso = retorno da ação − CDI nessa parcela). Call vendida no bid sobre as ações em
carteira (lotes cobertos), segura até o vencimento; exercício = entrega a ação ao strike e recompra (custo 0,14% do nocional; o P&L
da opção já carrega a perda do teto). Ajuste de lotes paga 0,11% por lado (emolumentos + meio spread).
IR: ações em "acoes_isentas" nos meses com vendas ≤ R$ 20 mil (exercício + ajustes), senão "acoes"; opções em "opcoes_b3";
"_cdi_perdido" = CDI que o dinheiro aplicado em ações deixou de ganhar (o runner desconta 85% dele no pós-IR). JCP (15% na fonte)
não é separado do dividendo no Yahoo — premissa: provento isento (otimista em ~0,1–0,2 pp a.a. para ITUB4).
"""
import numpy as np
import pandas as pd

import db3_base as B

NOME = "Covered call em ações isentas (PETR4/VALE3/ITUB4)"
TESE = "Carrego 3 blue chips em lotes de 100 (ganho isento até R$ 20 mil/mês de vendas) e vendo call de 1 mês OTM quando a IV está cara"
BENCHMARK = "CDI"
INICIO, CORTE = "2014-03-01", "2021-01-01"
REGIME, CUSTO_TROCA = "nenhum", 0.0
ATIVOS = ["PETR", "VALE", "ITUB"]
PARAMS = {"otm": .10, "filtro": "iv_alta"}
GRADE = {"otm": [.05, .10], "filtro": ["sempre", "iv_alta", "iv_rv"]}
VIZINHANCA = {"otm": (.06, .14)}
INSTRUMENTOS = [{"onde": "B3", "ticker": "PETR4, VALE3, ITUB4 (lote padrão 100)", "lote": 100, "custo": "0,11%/lado (emolumentos + meio spread)"},
                {"onde": "B3", "ticker": "calls mensais PETR*/VALE*/ITUB* (A–L)", "lote": 100, "custo": "bid + 0,10% do prêmio; exercício 0,14%"},
                {"onde": "Tesouro Direto", "ticker": "Tesouro Selic (resto do caixa)", "lote": "R$ ~170", "custo": "igual ao benchmark"}]
APLICAVEL = True
MOTIVO = ("Cabe: 1 lote de PETR4/ITUB4 ≈ R$ 3–4 mil, VALE3 ≈ R$ 5–7 mil; com R$ 20 mil compra 1–2 lotes de cada (sobra em Selic). "
          "Isenção: vendas ≤ R$ 20 mil/mês — com R$ 50 mil, exercício de vários lotes no mesmo mês pode estourar o limite.")
ALAVANCAGENS = [1]
MOTIVO_ALAV = "Ações à vista compradas com o próprio capital (sem termo/margem): só 1x faz sentido para uma carteira coberta."


def carrega():
    S, R = B.painel_acoes(B.acoes(("PETR4", "VALE3", "ITUB4")))
    return {"opc": B.opcoes(ATIVOS), "S": S, "R": R}


def _livro(d, capital, otm, filtro, lag, custo_mult, alavancagem, vende_call=True):
    S, R = d["S"], d["R"]
    sinais = {a: B.sinais_ciclos(d, a) for a in ATIVOS}
    lotes = {a: pd.Series(np.nan, index=B.DIAS) for a in ATIVOS}
    call = {a: pd.Series(0.0, index=B.DIAS) for a in ATIVOS}
    vendas = pd.Series(0.0, index=B.DIAS)
    neg = []
    for a in ATIVOS:
        c = sinais[a]
        if c is None or c.empty:
            continue
        for _, z in c.iterrows():
            dd = B.DIAS[B.DIAS > z.ds]
            if len(dd) <= lag or dd[lag] >= z.v:
                continue
            d0 = dd[lag]
            n = int(np.floor(capital * alavancagem / len(ATIVOS) / (z.S0 * 100)))
            lotes[a].loc[d0] = n                                  # posição em ações a partir do fechamento de d0
            if not vende_call or n == 0 or z.iv != z.iv:
                continue
            if filtro == "iv_alta" and not z.iv > z.iv_med:
                continue
            if filtro == "iv_rv" and not z.iv_rv > 0:
                continue
            p = B.perna(d, a, z.v, d0, S[a].get(d0, np.nan) * (1 + otm), "C", -1, custo_mult)
            if p is None or p["preco"] <= 0:
                continue
            x = B.pnl_pernas([p], n, [-1], custo_mult)
            call[a] = call[a].add(x, fill_value=0)
            if p["intr_fim"] > 0:
                vendas.loc[x.index[-1]] += n * 100 * p["K"]
            neg.append(dict(ativo=a + " call", lado=-1, entrada=x.index[0], saida=x.index[-1], lotes=n, serie=p["serie"], strike=p["K"],
                            premio=p["preco"], iv=z.iv, pnl_rs=float(x.sum()), **{"retorno_%": float(x.sum() / (n * 100 * p["S0"]) * 100)}))
    acao, perd_a, custo = {}, {}, pd.Series(0.0, index=B.DIAS)
    for a in ATIVOS:
        q = (lotes[a].ffill().fillna(0) * 100)
        val = q * S[a].reindex(B.DIAS).ffill()
        acao[a] = (val.shift(1) * R[a]).fillna(0)                 # retorno total da ação
        perd_a[a] = (val.shift(1) * B.CDI).fillna(0)                 # CDI que esse dinheiro deixou de ganhar
        dq = q.diff().fillna(q)
        custo += (dq.abs() * S[a].reindex(B.DIAS).ffill()).fillna(0) * B.CUSTO_ACAO * custo_mult
        vendas += (-dq.clip(upper=0) * S[a].reindex(B.DIAS).ffill()).fillna(0)
        # negócios da perna em ações: um por ano (carregamento contínuo)
        for ano, g in acao[a][q.shift(1) > 0].groupby(lambda t: t.year):
            neg.append(dict(ativo=a + " ação", lado=1, entrada=g.index[0], saida=g.index[-1], lotes=float(q.reindex(g.index).mean() / 100),
                            pnl_rs=float(g.sum() - (val.shift(1) * B.CDI).reindex(g.index).sum()),
                            **{"retorno_%": float(((1 + R[a].reindex(g.index)).prod() - 1) * 100)}))
    acao["_perd"] = perd_a
    return acao, call, sum(perd_a.values()), custo, vendas, neg


def _sem_perd(acao):
    return {k: v for k, v in acao.items() if k != "_perd"}


def excesso(d, capital=20000, custo_mult=1, lag=0, regime=REGIME, alavancagem=1, vende_call=True, **params):
    p = {**PARAMS, **params}
    acao, call, perd, custo, _, _ = _livro(d, capital, p["otm"], p["filtro"], lag, custo_mult, alavancagem, vende_call)
    e = (sum(_sem_perd(acao).values()) + sum(call.values()) - perd - custo) / capital
    return B.fecha(e, regime, CUSTO_TROCA, custo_mult)


def classes_ir(d, capital=20000, **params):
    p = {**PARAMS, **params}
    acao, call, perd, custo, vendas, _ = _livro(d, capital, p["otm"], p["filtro"], 0, 1, 1)
    pnl_acao = sum(_sem_perd(acao).values()) - custo
    mes = B.DIAS.to_period("M")
    isento = pd.Series(mes.map(vendas.groupby(mes).sum() <= 20_000), index=B.DIAS).astype(bool)
    return {"acoes_isentas": pnl_acao.where(isento, 0.0), "acoes": pnl_acao.where(~isento, 0.0), "opcoes_b3": sum(call.values()),
            "_cdi_perdido": perd}


def posicoes(d, capital=20000, **params):
    p = {**PARAMS, **params}
    acao, call, perd, custo, _, _ = _livro(d, capital, p["otm"], p["filtro"], 0, 0, 1)
    pn = {a + " ação": acao[a] - acao["_perd"][a] for a in ATIVOS}
    pn.update({a + " call": call[a] for a in ATIVOS})
    return B.wr_de_pnl(pn, capital)


def negocios(d, capital=20000, **params):
    p = {**PARAMS, **params}
    *_, neg = _livro(d, capital, p["otm"], p["filtro"], 0, 1, 1)
    return B.negocios_df(neg, capital)
