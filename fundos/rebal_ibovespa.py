"""
E7 Rebalanceamento do Ibovespa.

Mesa: a cada quadrimestre (carteiras de jan/mai/set) os fundos de índice e ETFs são obrigados a comprar os entrantes
no último pregão da carteira velha. Reconstruímos a regra de elegibilidade da B3 só com dados até a data
(índice de negociabilidade em 12 meses, presença >= 95%, preço >= R$1, 85% acumulado), compramos os prováveis entrantes
`antes` pregões antes da troca e entregamos a eles no fechamento do último pregão da carteira velha. Hedge 1:1 em Ibovespa.

Diferenças em relação ao código de origem (pesquisa original):
- a origem encerrava posições em papel deslistado usando "ainda negocia no futuro" (olha à frente); aqui não há esse filtro
  (posição em papel sem negócio rende 0). No fundo escolhido não muda nenhum dia (nenhum entrante deslistou na janela).
- o aluguel (só na versão "ambos") também é multiplicado por custo_mult, como pede o contrato.
- os retornos diários ajustados (desdobramentos + proventos) vêm prontos do painel da origem; a limpeza de erros de cotação
  daquele painel usa o dia seguinte (erro que se desfaz), o que é tratamento de dado e não sinal.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import comum  # noqa: E402

NOME = "Rebalanceamento do Ibovespa"
TESE = ("Antecipo a carteira teórica do Ibovespa: compro os prováveis entrantes (regra da B3 reconstruída com dados até a data) "
        "antes da troca e vendo para os fundos de índice no último pregão da carteira velha, com hedge em Ibovespa")
BENCHMARK = "CDI"
INICIO, CORTE = "2014-06-01", "2021-01-01"
REGIME = "nenhum"
CUSTO_TROCA = .001
PARAMS = {"antes": 10, "lado": "compra"}
GRADE = {"antes": [10, 21, 42], "lado": ["ambos", "compra"]}
VIZINHANCA = {"antes": (7, 14)}

INICIO_DADOS = pd.Timestamp("2014-01-02")
N_MAX = 15            # cada posição = 1/15 do PL
HEDGE_CUSTO = .0003   # futuro de Ibovespa / BOVA11
_CACHE = {}


# ---------------------------------------------------------------- dados
def carrega():
    """Painel longo de ações (só dias com negócio): data, ticker, preco (não ajustado), volume (R$), negocios, retorno (total, ajustado)."""
    a = comum.ler("rebal_ibovespa/acoes.parquet")
    return {"acoes": a.astype({"ticker": str})}


def _painel(d):
    """Painéis largos no calendário da B3 (a partir de 2014). Guardado em cache pelo id do dicionário de dados."""
    a = d["acoes"]
    chave = (id(a), len(a), a.data.max())
    if chave not in _CACHE:
        idx = comum.DIAS[comum.DIAS >= INICIO_DADOS]
        piv = lambda c: a.pivot(index="data", columns="ticker", values=c).reindex(idx)
        V = piv("volume")
        _CACHE.clear()
        _CACHE[chave] = {"P": piv("preco"), "V": V, "NEG": piv("negocios"), "R": piv("retorno"),
                         "ADV": V.fillna(0).rolling(60, min_periods=20).mean(), "proxy": {}}
    return _CACHE[chave]


# ---------------------------------------------------------------- regra do índice (só dados até a data)
def custo_acao(adv):
    """Custo por perna (corretagem + emolumentos + meio spread + impacto) pela liquidez (ADV 60d em R$)."""
    return pd.DataFrame(np.select([adv >= 50e6, adv >= 10e6, adv >= 2e6], [.0010, .0020, .0040], .0080), index=adv.index, columns=adv.columns)


def aluguel_acao(adv):
    """Aluguel a.a. na ponta vendida: blue chips 1%, médias 3%, small caps 8%."""
    return pd.DataFrame(np.select([adv >= 50e6, adv >= 10e6], [.01, .03], .08), index=adv.index, columns=adv.columns)


def ibov_proxy(p, data, janela=252):
    """Carteira provável do Ibovespa em `data`: IN = (n/N)^(1/3) (v/V)^(2/3) nos últimos 12 meses,
    presença >= 95% dos pregões, último preço >= R$1, ações até 85% do IN acumulado."""
    if data not in p["proxy"]:
        i = p["NEG"].index.searchsorted(data)
        sl = slice(p["NEG"].index[max(i - janela, 0)], data)
        n, v = p["NEG"].loc[sl].fillna(0).sum(), p["V"].loc[sl].fillna(0).sum()
        pres = p["P"].loc[sl].notna().mean()
        ult = p["P"].loc[sl].ffill().iloc[-1]
        IN = (n / n.sum()) ** (1 / 3) * (v / v.sum()) ** (2 / 3)
        IN = IN[(pres >= .95) & (ult >= 1)].sort_values(ascending=False)
        acum = IN.cumsum() / IN.sum()
        p["proxy"][data] = set(acum[acum.shift(1, fill_value=0) < .85].index)
    return p["proxy"][data]


def eventos(d, antes=PARAMS["antes"]):
    """Uma linha por (rebalanceamento, papel): decisão `antes` pregões antes do último pregão da carteira velha
    (o calendário de pregões é público com antecedência); entrantes s=+1 (no proxy agora e não no da revisão anterior), saintes s=-1."""
    p, DIAS = _painel(d), comum.DIAS
    out = []
    for ano in range(2015, DIAS[-1].year + 1):
        for mes in (1, 5, 9):
            vig = pd.Timestamp(ano, mes, 1)                                  # 1ª data da carteira nova
            i_fim = DIAS.searchsorted(vig) - 1                              # último pregão da carteira velha
            if i_fim + 1 >= len(DIAS):
                continue
            dec = DIAS[i_fim - antes]
            dec_ant = DIAS[DIAS.searchsorted(vig - pd.DateOffset(months=4)) - 1 - antes]   # decisão da revisão anterior
            novo, velho = ibov_proxy(p, dec), ibov_proxy(p, dec_ant)
            out += [(dec, t, 1.0, DIAS[i_fim]) for t in sorted(novo - velho)]
            out += [(dec, t, -1.0, DIAS[i_fim]) for t in sorted(velho - novo)]
    return pd.DataFrame(out, columns=["data", "ticker", "s", "fim"])


# ---------------------------------------------------------------- carteira
def _pesos(d, antes, lado):
    """Pesos-alvo decididos no fechamento de t: 1/15 do PL por papel do dia da decisão até 2 pregões antes do fim
    (executa em t+1, então a última posição é carregada até o fechamento do último pregão da carteira velha); bruto máx. 100%."""
    ev = eventos(d, antes)
    if lado == "compra":
        ev = ev[ev.s > 0]
    idx = comum.DIAS[comum.DIAS >= INICIO_DADOS]
    W = pd.DataFrame(0.0, index=idx, columns=sorted(ev.ticker.unique()))
    for dec, t, s in zip(ev.data, ev.ticker, ev.s):
        i = idx.get_loc(dec)
        W.iloc[i:i + antes - 1, W.columns.get_loc(t)] = s / N_MAX
    return W.div(np.maximum(W.abs().sum(axis=1), 1), axis=0).reindex(comum.DIAS).fillna(0)


def _livro(d, custo_mult=1, lag=0, antes=PARAMS["antes"], lado=PARAMS["lado"]):
    """Contribuição diária (em R$ do PL) de cada papel e do hedge, já líquida de custos. Wx = posição executada no fechamento de t."""
    p = _painel(d)
    W = _pesos(d, antes, lado)
    tk = list(W.columns)
    Wx = W.shift(1 + lag).fillna(0)
    cdi = comum.CDI
    Rx = p["R"].reindex(index=comum.DIAS, columns=tk).fillna(0).sub(cdi, axis=0)
    adv = p["ADV"].reindex(index=comum.DIAS, columns=tk).ffill()
    con = Wx.shift(1).fillna(0) * Rx - Wx.diff().abs().fillna(Wx.abs()) * custo_acao(adv) * custo_mult \
        - Wx.clip(upper=0).abs() * aluguel_acao(adv) * custo_mult / 252
    h = -Wx.sum(axis=1)                                                     # hedge: vende Ibovespa contra a exposição líquida
    con["IBOV (hedge)"] = h.shift(1).fillna(0) * (comum.R_IBOV - cdi) - h.diff().abs().fillna(0) * HEDGE_CUSTO * custo_mult
    return con, Wx


def excesso(d, custo_mult=1, lag=0, regime=REGIME, antes=PARAMS["antes"], lado=PARAMS["lado"]):
    con, _ = _livro(d, custo_mult, lag, antes, lado)
    return comum.aplica_regime(con.sum(axis=1), regime, CUSTO_TROCA * custo_mult)


def posicoes(d, antes=PARAMS["antes"], lado=PARAMS["lado"]):
    """W: pesos-alvo decididos em t (inclui o hedge); R: retornos em excesso ao CDI de cada ativo."""
    p = _painel(d)
    W = _pesos(d, antes, lado)
    W["IBOV (hedge)"] = -W.sum(axis=1)
    R = p["R"].reindex(index=comum.DIAS, columns=W.columns[:-1]).fillna(0).sub(comum.CDI, axis=0)
    R["IBOV (hedge)"] = comum.R_IBOV - comum.CDI
    return W, R


def _dia_troca_real(fim):
    """Último pregão antes da 1ª segunda-feira do mês de vigência (data em que a B3 de fato troca a carteira)."""
    vig = (fim + pd.offsets.MonthBegin(1)).normalize()
    seg = vig + pd.Timedelta(days=(7 - vig.weekday()) % 7)
    return comum.DIAS[comum.DIAS.searchsorted(seg) - 1]


def negocios(d, antes=PARAMS["antes"], lado=PARAMS["lado"]):
    """Um negócio por linha. contrib_pp já inclui o hedge do próprio papel (soma das linhas = excesso total).
    entrou_indice: não temos a carteira oficial histórica -> ESTIMADO pelo fluxo dos fundos de índice: pico de volume entre o
    último pregão do mês e o último pregão antes da 1ª segunda-feira da vigência >= 2,5x a média dos 60 pregões antes da entrada
    (pico_volume = essa razão)."""
    p = _painel(d)
    con, Wx = _livro(d, antes=antes, lado=lado)
    hed = con.pop("IBOV (hedge)")
    h = -Wx.sum(axis=1)
    rx_ibov = comum.R_IBOV - comum.CDI
    R = p["R"].reindex(index=comum.DIAS, columns=Wx.columns).fillna(0)
    V = p["V"].reindex(comum.DIAS)
    out = []
    for t in Wx.columns:
        w = Wx[t].values
        mud = np.flatnonzero(np.diff(np.r_[0, np.sign(w), 0]) != 0)
        for a, b in zip(mud[:-1], mud[1:]):
            if w[a] == 0:
                continue
            seg = slice(a + 1, b + 1)                                       # dias com retorno: depois da entrada até a saída
            ent, sai = comum.DIAS[a], comum.DIAS[b]
            # parte do hedge que cobre este papel: -w x (Ibov - CDI) e o custo de montar/desmontar
            hedge = (-Wx[t].shift(1).fillna(0) * rx_ibov - Wx[t].diff().abs().fillna(0) * HEDGE_CUSTO).iloc[a:b + 1].sum()
            r, rib = (1 + R[t].iloc[seg]).prod(), (1 + comum.R_IBOV.iloc[seg]).prod()
            vol_ref = V[t].iloc[max(a - 60, 0):a].fillna(0).mean()
            pico = V[t].loc[sai:_dia_troca_real(sai)].max() / vol_ref if vol_ref > 0 else np.nan
            out.append({"ativo": t, "lado": int(np.sign(w[a])), "entrada": ent, "saida": sai, "dias": b - a,
                        "retorno_%": (r - 1) * 100, "ret_vs_ibov_%": (r / rib - 1) * 100,
                        "contrib_pp": (con[t].iloc[a:b + 1].sum() + hedge) * 100,
                        "pico_volume": pico, "entrou_indice": bool(pico >= 2.5)})
    tr = pd.DataFrame(out)
    return tr.sort_values("entrada").reset_index(drop=True)


if __name__ == "__main__":
    d = carrega()
    e = excesso(d)
    print(NOME, "| excesso a.a. IS %.2f%% OOS %.2f%%" % (comum.anual(e[INICIO:CORTE]), comum.anual(e[CORTE:])))
    print(negocios(d).tail(10).to_string())
