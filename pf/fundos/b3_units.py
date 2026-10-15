"""
Units x ações componentes com CONVERSÃO no escriturador (sem venda a descoberto): compro o lado barato e converto.

Mesa: a unit (ex.: TAEE11 = 1 TAEE3 + 2 TAEE4) e a cesta de ações componentes são o mesmo papel; o institucional arbitra vendendo o lado
caro a descoberto (aluguel) e comprando o barato, no mesmo instante — e em t+1 já não sobrava nada (pesquisa A3). A pessoa física não
precisa vender a descoberto: compra o lado barato e pede ao escriturador (pela corretora) o DESMEMBRAMENTO da unit em ações (ou a
COMPOSIÇÃO das ações em unit), recebe o outro lado em alguns pregões e vende. O prêmio que sobra está justamente nos componentes
ILÍQUIDOS (ON/PN que giram R$ 100-500 mil/dia), onde o desvio é grande e o institucional não consegue escala — e onde R$ 5-10 mil cabem.
Regras: desvio executável no fim do pregão t: unit barata = oferta de venda da unit / (n x oferta de compra da ON + m x oferta de compra
da PN) - 1 (e o simétrico para a cesta barata) abaixo de -`limiar` E abaixo da mediana de 60 pregões (desvio "normal" não conta);
compro o lado barato no fechamento de t+1+lag pela oferta de venda REAL desse dia; converto (`prazo` pregões, sem custo de escriturador
- premissa a conferir na corretora); vendo o outro lado pela oferta de compra REAL do dia da venda. Marcação diária pelo retorno total
das ações que tenho (a unit e a cesta são o mesmo risco). Tamanho: até metade do capital por operação, no máximo 10% do giro diário
da perna mais ilíquida; até 2 operações ao mesmo tempo. Risco: o preço da empresa no prazo da conversão (beta por `prazo` pregões).
Composições (n ON + m PN, conferidas pelo menor erro na pesquisa A3 e no estatuto): ver UNITS.
IR: swing trade de ações (vendas do mês costumam passar de R$ 20 mil com operações de R$ 10 mil -> parte isenta, parte 15%).
"""
import numpy as np
import pandas as pd

import b3_base as B

C, pf = B.C, B.pf

UNITS = {"TAEE11": ("TAEE3", 1, "TAEE4", 2), "KLBN11": ("KLBN3", 1, "KLBN4", 4), "SAPR11": ("SAPR3", 1, "SAPR4", 4),
         "ENGI11": ("ENGI3", 1, "ENGI4", 4), "ALUP11": ("ALUP3", 1, "ALUP4", 2), "SANB11": ("SANB3", 1, "SANB4", 1),
         "BPAC11": ("BPAC3", 1, "BPAC5", 2), "TIET11": ("TIET3", 1, "TIET4", 4), "IGTI11": ("IGTI3", 1, "IGTI4", 2),
         "SULA11": ("SULA3", 1, "SULA4", 2), "CPLE11": ("CPLE3", 1, "CPLE6", 4), "BIDI11": ("BIDI3", 1, "BIDI4", 2),
         "MODL11": ("MODL3", 1, "MODL4", 2), "RNEW11": ("RNEW3", 1, "RNEW4", 2)}

NOME = "Units x componentes com conversão no escriturador (PF)"
TESE = ("Compro o lado barato (unit ou cesta ON+PN) e converto no escriturador em vez de vender a descoberto: o desvio que sobra está nos "
        "componentes ilíquidos, onde R$ 5-10 mil cabem e o institucional não escala")
BENCHMARK = "CDI"
INICIO, CORTE = "2014-06-01", "2021-01-01"
REGIME = "nenhum"
CLASSE_IR = "acoes"                                   # swing trade 15% (operações de até R$ 10-25 mil: vendas do mês passam de R$ 20 mil)
CUSTO_TROCA = .001
PARAMS = {"limiar": .02, "prazo": 5, "lado": "ambos", "max_part": .10}
GRADE = {"limiar": [.01, .02, .04], "lado": ["ambos", "unit_barata"], "prazo": [3, 10]}
VIZINHANCA = {"limiar": (.01, .05), "prazo": (2, 12), "max_part": (.05, .2)}
INSTRUMENTOS = [{"onde": "Clear/Rico/XP/BTG + escriturador (Itaú/Bradesco) via corretora", "ticker": ", ".join(UNITS), "lote": "1 unit / 1 ação",
                 "custo": "emolumentos 0,03% + meio spread real nas duas pontas; conversão sem custo (premissa) em `prazo` pregões"}]
APLICAVEL = True
MOTIVO = ("desmembramento de units é pedido padrão no escriturador (3-5 dias úteis); a composição de unit nem sempre está aberta "
          "(algumas companhias suspendem) — a variante 'unit_barata' usa só o desmembramento")
ALAVANCAGENS = [1]
MOTIVO_ALAV = "operações limitadas pelo giro dos componentes ilíquidos, não pelo capital"
_RES = {}


def carrega():
    tks = sorted(set(UNITS) | {x[0] for x in UNITS.values()} | {x[2] for x in UNITS.values()})
    d = B.painel("P", "R", "V", "BID", "ASK")
    return {k: v.reindex(columns=tks) for k, v in d.items()}


def roda(d, capital=20000, custo_mult=1, lag=0, limiar=.02, prazo=5, lado="ambos", max_part=.10):
    key = (id(d), capital, custo_mult, lag, limiar, prazo, lado, max_part)
    if key in _RES:
        return _RES[key]
    idx = B.DIAS
    # painéis no calendário completo (com dados truncados as séries ficavam mais curtas que B.DIAS -> iloc fora do intervalo)
    P, R, V, BI, AS = (d[k].reindex(idx) for k in ("P", "R", "V", "BID", "ASK"))
    R, V = R.fillna(0), V.fillna(0)
    prazo = max(int(round(prazo)), 1)
    T = len(idx)
    pnl = np.zeros(T)
    cdi_p = np.zeros(T)
    vend = np.zeros(T)
    neg = []
    ocupado = np.zeros(T)                                             # nº de operações abertas por dia
    W = pd.DataFrame(0.0, index=idx, columns=list(UNITS))
    for u, (on, n, pn, m) in UNITS.items():
        if u not in P or on not in P or pn not in P or P[u].notna().sum() < 100:
            continue
        cesta_bid = n * BI[on] + m * BI[pn]
        cesta_ask = n * AS[on] + m * AS[pn]
        u_barata = AS[u] / cesta_bid - 1                              # compro unit, desmembro, vendo ON+PN
        c_barata = cesta_ask / BI[u] - 1                              # compro ON+PN, componho, vendo unit
        mid = np.log(P[u] / (n * P[on] + m * P[pn]))
        med = mid.rolling(60, min_periods=20).median()
        neg_ok = P[[u, on, pn]].notna().all(axis=1)
        adv = V[[u, on, pn]].rolling(20, min_periods=5).median().min(axis=1)
        sinais = [("unit", u_barata.where((u_barata <= -limiar) & (np.log1p(u_barata) < med) & neg_ok))]
        if lado == "ambos":
            sinais.append(("cesta", c_barata.where((c_barata <= -limiar) & (-np.log1p(c_barata) > med) & neg_ok)))
        for tipo, s in sinais:
            ultimo_fim = -1
            for i in np.flatnonzero(s.notna().values):
                ie = i + 1 + lag                                          # compra
                ix = ie + prazo                                           # venda após a conversão
                if ie <= ultimo_fim or ix >= T or ocupado[ie] >= 2:
                    continue
                if tipo == "unit":
                    compra = [(u, 1.0)]
                    venda = [(on, n), (pn, m)]
                else:
                    compra = [(on, n), (pn, m)]
                    venda = [(u, 1.0)]
                pa = sum(q * AS[t].iloc[ie] for t, q in compra)            # custo de 1 "unidade" comprada (oferta de venda real)
                if not pa > 0 or not all(P[t].iloc[ie] > 0 for t, _ in compra):
                    continue
                tam = min(capital / 2, max_part * adv.iloc[i])
                q = np.floor(tam / pa)
                if q < 1:
                    continue
                v0 = q * pa
                # marcação: valor da posição pelo retorno total do que tenho (antes da conversão: o que comprei; depois: o que recebo)
                w_c = np.array([qq * P[t].iloc[ie] for t, qq in compra])
                val = q * w_c.sum()
                pnl[ie] += val - v0 - v0 * B.EMOL * custo_mult
                for j in range(ie + 1, ix + 1):
                    hold = compra if j <= ie + prazo // 2 else venda
                    pw = np.array([qq * P[t].iloc[j - 1] for t, qq in hold])
                    r = (pw * np.array([R[t].iloc[j] for t, _ in hold])).sum() / pw.sum() if pw.sum() > 0 else 0.0
                    if abs(r) > .3:                                       # salto suspeito (evento corporativo não ajustado): não marca
                        r = 0.0
                    g = val * r
                    pnl[j] += g
                    val += g
                # saída: oferta de compra real do dia da venda contra o fechamento
                pc = sum(qq * P[t].iloc[ix] for t, qq in venda)
                pb = sum(qq * BI[t].iloc[ix] for t, qq in venda)
                fator = pb / pc if pc > 0 and pb > 0 else 1 - .01
                sai = val * fator * (1 - B.EMOL * custo_mult)
                pnl[ix] += sai - val
                vend[ix] += sai
                cdi_p[ie:ix + 1] += v0 * C.CDI.reindex(idx).iloc[ie:ix + 1].values
                ocupado[ie:ix + 1] += 1
                W.iloc[ie - 1 - lag:ix - lag, W.columns.get_loc(u)] += v0 / capital
                ultimo_fim = ix
                neg.append({"ativo": u, "lado": 1, "entrada": idx[ie], "saida": idx[ix], "dias": prazo, "retorno_%": (sai / v0 - 1) * 100,
                            "contrib_pp": (sai - v0 - v0 * B.EMOL * custo_mult) / capital * 100, "valor": v0,
                            "rotulo": f"{tipo} barata {s.iloc[i] * 100:.1f}% (sinal {idx[i].date()})"})
    pnl = pd.Series(pnl, index=idx)
    cdi_p = pd.Series(cdi_p, index=idx)
    res = {"e": (pnl - cdi_p) / capital, "pnl": pnl, "custo": pd.Series(0.0, index=idx), "cdi_perdido": cdi_p, "vendas": pd.Series(vend, index=idx),
           "W": W, "negocios": pd.DataFrame(neg)}
    if len(_RES) > 64:
        _RES.clear()
    _RES[key] = res
    return res


def excesso(d, capital=20000, custo_mult=1, lag=0, regime=REGIME, alavancagem=1, **params):
    e = roda(d, capital, custo_mult, lag, **{**PARAMS, **params})["e"] * alavancagem
    return C.aplica_regime(e, regime, CUSTO_TROCA * custo_mult)


def classes_ir(d, capital=20000, **params):
    return B.classes_acoes(roda(d, capital, **{**PARAMS, **params}))


def posicoes(d, capital=20000, **params):
    W = roda(d, capital, **{**PARAMS, **params})["W"]
    return W, d["R"].reindex(index=B.DIAS, columns=W.columns).fillna(0).sub(B.CDI, axis=0)


def negocios(d, capital=20000, **params):
    return roda(d, capital, **{**PARAMS, **params})["negocios"]
