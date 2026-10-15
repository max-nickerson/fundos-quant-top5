"""
Agro B3: spreads de vencimento safra x entressafra (boi BGI, milho CCM, café ICF) — compro o vencimento que o hedger natural VENDE.

Tese de mesa (pressão de hedge, Keynes/Hicks "normal backwardation" aplicada a um vencimento contra outro): em cada cadeia há um vencimento
em que o produtor/confinador trava o preço em massa, e ninguém do outro lado tem a mesma necessidade de comprar naquela data. Esse
vencimento negocia barato contra o vizinho; quem carrega o spread (comprado no vencimento pressionado, vendido no outro) recebe o prêmio.
  - BGI: o confinador vende o boi de OUTUBRO (V, entressafra) quando compra o boi magro no 1º semestre; perna "outra" = MAIO (K, safra).
    Janela: jan-abr (sai antes do mês de vencimento do K).
  - CCM: o produtor de milho safrinha vende SETEMBRO (U) entre o plantio e a colheita; perna "outra" = MARÇO do ano seguinte (H,
    entressafra). Janela: mar-ago.
  - ICF: o cafeicultor vende SETEMBRO (U, colheita mai-set) a termo; perna "outra" = DEZEMBRO (Z). Janela: fev-ago.
  "lado" +1 = comprado na perna pressionada e vendido na outra; −1 = o contrário (teste de controle). "todos" = 1 spread de cada.
RESULTADO DO IS (2018-2022) — a tese inicial ("comprar o vencimento hedgeado") perdeu em CCM, ICF e "todos"; a melhor variante foi
CCM com lado −1: VENDIDO no setembro (safrinha) e COMPRADO no março seguinte de mar a ago. Leitura de mesa: o produtor não vende
setembro de uma vez no plantio — ele vende AO LONGO da janela, conforme a lavoura se confirma e a colheita chega (e o milho físico
pressiona a base do interior). O spread H(+1) − U abre de ~R$ 7 em março para ~R$ 10-11 em agosto quase todo ano: quem vende U junto
com o fluxo previsível de hedge (e carrega o milho da entressafra comprado) ganha a abertura. É andar junto com o vendedor forçado
antes que ele termine, não ser a liquidez dele. BGI e ICF: o spread é dominado por choques (seca/geada no café em 2021, ciclo do boi).
O "prêmio de compra" outright do milho (db3_agro_ccm) já falhou; aqui o risco direcional quase some (as duas pernas andam juntas) e o
que sobra é o desconto do vencimento hedgeado — e o spread cabe em R$ 20 mil mesmo com contratos grandes (1 BGI ≈ R$ 105 mil de nocional).

Dados: ajuste diário de CADA vencimento (boletim B3, 2018-2026; ajuste − ajuste anterior = o ajuste diário de verdade, sem rolagem).
Execução: decisão no fechamento de t (calendário fixo), execução no fechamento de t+1; garantia em Tesouro Selic (rende CDI).
Contratos (B3, especificações; out/2026): BGI 330 arrobas, tick R$ 0,05/@ (R$ 16,50); CCM 450 sacas, tick R$ 0,01 (R$ 4,50); ICF 100
sacas, cotado em US$/saca, tick US$ 0,05 (≈ R$ 27), liquidado em R$ pela PTAX. Margem de spread (calendário) na B3 é uma fração da margem
outright; aqui ela é irrelevante para o excesso (fica em Tesouro Selic).
Custo por perna por lado = emolumentos ~R$ 1,50 + 1 tick inteiro de meio spread (o vencimento longo é pouco líquido): BGI R$ 18,
CCM R$ 6, ICF R$ 29. IR: futuros B3 15% (mensal, sem isenção). OOS desde 2023 (dados 2018+).
"""
import numpy as np
import pandas as pd

import fu_comum as F

NOME = "Agro B3: spread safra x entressafra (milho: vende setembro, compra março+1)"
TESE = "Vendido no milho de setembro (safrinha) e comprado no março seguinte de mar a ago: anda com o hedge do produtor e vende o seguro de clima do consumidor"
BENCHMARK = "CDI"
INICIO, CORTE = "2018-02-01", "2023-01-01"
REGIME = "nenhum"
CUSTO_TROCA = 0.0
CLASSE_IR = "futuros_b3"
PARAMS = {"produto": "CCM", "lado": -1}        # maior excesso IS (2018-2022): o CONTRÁRIO da tese inicial (ver abaixo)
GRADE = {"produto": ["BGI", "CCM", "ICF", "todos"], "lado": [1, -1]}
VIZINHANCA = {}
# produto: (perna pressionada, ano +0), (outra perna, ano +k), meses da janela, mult, moeda, custo R$/perna/lado
PAR = {"BGI": dict(hedge=("V", 0), outra=("K", 0), meses=(1, 2, 3, 4), mult=330, usd=False, custo=18.0),
       "CCM": dict(hedge=("U", 0), outra=("H", 1), meses=(3, 4, 5, 6, 7, 8), mult=450, usd=False, custo=6.0),
       "ICF": dict(hedge=("U", 0), outra=("Z", 0), meses=(2, 3, 4, 5, 6, 7, 8), mult=100, usd=True, custo=29.0)}
INSTRUMENTOS = [("B3", "BGI V x K", "330 @ por perna", "R$ 18/perna/lado"), ("B3", "CCM U x H+1", "450 sacas", "R$ 6/perna/lado"),
                ("B3", "ICF U x Z", "100 sacas (US$)", "R$ 29/perna/lado"), ("Tesouro Direto", "Tesouro Selic", "garantia", "0")]
APLICAVEL = True
MOTIVO = "Spreads de calendário cabem em R$ 20 mil (margem reduzida de spread em Tesouro Selic); vencimentos longos pouco líquidos: 1 tick de custo."
ALAVANCAGENS = [1, 2]
MOTIVO_ALAV = "2x = 2 spreads de cada (o risco de 1 spread é pequeno; 5x esbarraria na liquidez dos vencimentos longos)."


def carrega():
    return {"agro": F.ler("agro_b3.parquet")}


def _pernas(d, prod):
    """Para cada pregão, P&L em R$ de 1 contrato comprado na perna pressionada e na outra (vencimento escolhido pelo calendário)."""
    def f():
        p = PAR[prod]
        x = d["agro"][d["agro"].ticker.str[:3] == prod]
        dP = x.assign(v=x.ajuste - x.ajuste_ant).pivot_table(index="data", columns="ticker", values="v", aggfunc="last")
        A = x.pivot_table(index="data", columns="ticker", values="ajuste", aggfunc="last")
        idx = F.pf.DIAS[(F.pf.DIAS >= dP.index.min()) & (F.pf.DIAS <= dP.index.max())]
        dP, A = dP.reindex(idx), A.reindex(idx)
        fx = F.nivel(F.PTAX_FULL, idx).shift(1) if p["usd"] else pd.Series(1.0, index=idx)   # B3 converte pela PTAX da véspera
        out = {}
        for perna in ("hedge", "outra"):
            cod, k = p[perna]
            tk = [f"{prod}{cod}{(t.year + k) % 100:02d}" for t in idx]
            pc = np.array([dP.at[t, c] if c in dP.columns else np.nan for t, c in zip(idx, tk)])
            lv = np.array([A.at[t, c] if c in A.columns else np.nan for t, c in zip(idx, tk)])
            noc = pd.Series(lv, index=idx) * p["mult"] * fx
            pcs = pd.Series(pc, index=idx) * p["mult"] * fx
            K = pd.DataFrame({"pc": pcs, "noc": noc, "margem": 0.0, "r": pcs / noc.shift(1), "custo": p["custo"], "rol": 0.0, "local": "b3"})
            out[perna] = (K, pd.Series(tk, index=idx))
        return out
    return F.memo(("agro", prod), (d["agro"],), f)


def gera(d, capital=20000, regime=REGIME, alavancagem=1, produto="todos", lado=1):
    prods = list(PAR) if produto == "todos" else [produto]
    N, K = {}, {}
    idx = None
    for pr in prods:
        P = _pernas(d, pr)
        Kh, tkh = P["hedge"]
        Ko, tko = P["outra"]
        idx = Kh.index if idx is None else idx.union(Kh.index)
        mm = PAR[pr]["meses"]
        # decide em t a posição que rende a partir de t+2 (execução t+1): janela de calendário em t e em t + 2 dias úteis (fixa, sem dados
        # futuros); as janelas não cruzam a virada do ano -> o vencimento segurado é o mesmo; só entra se as duas pernas têm ajuste em t
        adiante = pd.Series((Kh.index + pd.offsets.BDay(2)).month, index=Kh.index)
        on = pd.Series(Kh.index.month, index=Kh.index).isin(mm) & adiante.isin(mm) & Kh["noc"].notna() & Ko["noc"].notna()
        n = float(round(alavancagem))
        N[f"{pr}_hedge"] = on.astype(float) * n * lado
        N[f"{pr}_outra"] = -on.astype(float) * n * lado
        K[f"{pr}_hedge"], K[f"{pr}_outra"] = Kh, Ko
    Nd = pd.DataFrame(N).reindex(idx).fillna(0)
    return Nd, {a: k.reindex(idx) for a, k in K.items()}


F.montar(globals(), gera, carrega)

_neg_pernas = negocios                                     # noqa: F821 (criado por F.montar)


def negocios(d, capital=20000, **params):
    """Um negócio = 1 spread (as duas pernas da mesma janela juntas); retorno_% = P&L do spread / nocional de 1 perna."""
    ng = _neg_pernas(d, capital=capital, **params)
    if ng.empty:
        return ng
    ng = ng.assign(prod=ng.ativo.str[:3])
    g = ng.groupby(["prod", "entrada"], as_index=False).agg(saida=("saida", "max"), dias=("dias", "max"), contratos=("contratos", "max"),
                                                             retorno_=("retorno_%", "sum"), contrib_pp=("contrib_pp", "sum"))
    g["ativo"] = g["prod"] + " spread"
    g["lado"] = int(params.get("lado", PARAMS["lado"]))
    return g.rename(columns={"retorno_": "retorno_%"})[["ativo", "lado", "entrada", "saida", "dias", "contratos", "retorno_%", "contrib_pp"]]
