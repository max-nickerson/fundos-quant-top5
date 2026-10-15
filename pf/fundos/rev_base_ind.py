"""
Revisita PF — base mini-índice (WIN) x BOVA11 perto do vencimento (linha A9 "Base IND x BOVA11 no vencimento").

Tese de mesa: perto do vencimento a taxa implícita do índice futuro contra o Ibovespa à vista, (F/Ibov)^(252/du) - 1, às vezes se afasta do
CDI (fluxo de rolagem dos comprados/vendidos). Se a taxa está acima do CDI + limiar, compro BOVA11 e vendo WIN do 1º vencimento ("caixa
sintético" que rende a taxa travada); se está abaixo do CDI - limiar (só na variante "ambos"), vendo BOVA11 alugado e compro WIN.
Seguro até o vencimento (quarta-feira mais próxima do dia 15 dos meses pares).

Rota PF: WIN (R$ 0,20 por ponto) na Clear/Rico + BOVA11 no à vista (aceito como garantia do WIN).
  - contratos INTEIROS: nº de WIN = piso(capital x alavancagem / (0,2 x F)); BOVA11 = mesmo nocional em cotas inteiras.
    1 WIN = R$ 20–42 mil de nocional (Ibovespa 100–210 mil pontos) -> com R$ 20 mil só cabe em parte de 2019–2020 (Ibov <= 100 mil);
    com R$ 50 mil cabe 1 WIN sempre. Acima de 1x o BOVA11 é comprado com dinheiro emprestado (termo/conta margem, CDI + 6% a.a. — não
    confirmado, conservador).
  - preços SIMULTÂNEOS (o artefato do institucional era o Ibovespa do Yahoo x ajuste): o ajuste diário do IND é a média dos negócios das
    17h00–17h15, logo depois do leilão de fechamento do à vista (16h55–17h00) -> sinal com ajuste x fechamento oficial do Ibovespa (ruído de
    ~15 min). Entrada: BOVA11 no ask do fechamento de t+1 e WIN no ajuste de t+1 (ruído de média zero, independente do sinal de t).
    Saída no vencimento: o WIN liquida pela MÉDIA do Ibovespa nas 3 últimas horas; o arbitrador vende o BOVA11 ao longo dessas 3 horas
    (TWAP), então a saída do BOVA11 = preço de liquidação x (BOVA11/Ibovespa no fechamento do dia) — a razão ETF/índice quase não muda
    no dia. Usar o fechamento do BOVA11 contra a média criaria um ruído de ~0,1–0,3% por negócio do tamanho do próprio edge.
  - custos: BOVA11 0,03% de emolumentos + meio spread do fechamento por lado; WIN R$ 0,39 por contrato na entrada + R$ 0,30 de liquidação;
    aluguel PF na variante reversa: 0,5% do volume ao abrir + 0,4% a.a. ao doador (BOVA11).
  - IR: ETF e futuro são "operações comuns" (15%) e o prejuízo de um compensa o lucro do outro no mesmo mês (IN RFB 1585/2015) ->
    o P&L líquido das duas pernas vai na classe futuros_b3 (separar superestimaria o IR de um hedge).
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _util as U  # noqa: E402

C, pf = U.C, U.pf

NOME = "Base WIN x BOVA11 no vencimento (caixa sintético)"
TESE = ("Nos últimos pregões antes do vencimento, se a taxa implícita do índice futuro contra o Ibovespa passa do CDI + limiar, compro "
        "BOVA11 e vendo WIN do 1º vencimento e travo a taxa até a liquidação (média do Ibovespa das 3 últimas horas).")
BENCHMARK = "CDI"
INICIO, CORTE = "2019-02-01", "2023-01-01"
REGIME = "nenhum"
CUSTO_TROCA = .001
PARAMS = {"thr": .01, "dias_antes": 10, "lado": "caixa"}       # melhor IS da grade com R$ 50 mil (+0,04 pp; tudo ~0)
GRADE = {"thr": [.005, .01, .02], "dias_antes": [5, 10], "lado": ["caixa", "ambos"]}
VIZINHANCA = {"thr": (.005, .02), "dias_antes": (7, 12)}
RANKING = ["A9 Base IND x BOVA11 no vencimento"]
VARIANTES = {"ambos os lados (reverso com BOVA11 alugado)": {"lado": "ambos"},
             "limiar 2%, 5 pregões (institucional)": {"thr": .02, "dias_antes": 5},
             "institucional: ambos, 2%, 5 pregões": {"thr": .02, "dias_antes": 5, "lado": "ambos"},
             "custos institucionais (custo 0)": {"custo_mult": 0.0}}
INSTRUMENTOS = [
    {"onde": "B3 (Clear/Rico)", "ticker": "WIN (1º vencimento, meses pares)", "lote": "1 contrato = R$ 0,20 x pontos (R$ 20–42 mil)",
     "custo": "R$ 0,39 por contrato + R$ 0,30 na liquidação; margem em BOVA11/Tesouro Selic"},
    {"onde": "B3", "ticker": "BOVA11 (e BOVA11F)", "lote": 1, "custo": "0,03% + meio spread (~0,03%) por lado; aluguel 0,5% + 0,4% a.a. no reverso"},
]
APLICAVEL = "R$ 20 mil: só em parte de 2019–2020 (1 WIN > patrimônio desde 2021); R$ 50 mil: sim (1 WIN)"
MOTIVO = ("1 WIN = 0,2 x Ibovespa: R$ 20 mil em 2019 e ~R$ 34–42 mil em 2025–26. Contra 1 WIN é preciso ter o mesmo nocional em BOVA11 "
          "comprado com caixa (ou emprestado). Com R$ 20 mil o fundo fica parado (CDI) quase todo o tempo; com R$ 50 mil opera 1 WIN.")
ALAVANCAGENS = [1, 1.5, 2]
MOTIVO_ALAV = ("Acima de 1x o BOVA11 que casa com o WIN é financiado (termo/conta margem a CDI + 6% a.a., não confirmado); 2x já põe 2 WIN "
               "com R$ 50 mil. 5x exigiria R$ 250 mil de BOVA11 financiado -> não viável para PF.")

MULT_WIN = .2
TARIFA_WIN, LIQ_WIN = .39, .30
EMOL = .0003
ALUG_ABRE, ALUG_DOADOR_AA = .005, .004
SPREAD_FIN_AA = .06


# =============================================================== dados
def _vencs():
    """IND/WIN: quarta-feira mais próxima do dia 15 dos meses pares; sem pregão, a sessão seguinte (regra da B3)."""
    out = []
    for a in range(2018, 2028):
        for m in (2, 4, 6, 8, 10, 12):
            d15 = pd.Timestamp(a, m, 15)
            q = d15 + pd.Timedelta(days=(2 - d15.weekday() + 3) % 7 - 3)
            i = C.DIAS.searchsorted(q)
            if i < len(C.DIAS):
                out.append((f"{'GJMQVZ'[(m // 2) - 1]}{a % 100:02d}", C.DIAS[i]))
    return out


def _le_ind():
    x = pd.read_parquet(U.FD / "arb_ind.parquet", columns=["date", "ticker", "AdjstdQt"])
    x = x[x.ticker.str.startswith("IND")].rename(columns={"date": "data", "AdjstdQt": "ajuste"})
    vs = dict(_vencs())
    x["venc"] = x.ticker.str[3:].map(vs)
    x = x.dropna(subset=["venc", "ajuste"])
    x = x[x.data <= x.venc].sort_values(["data", "venc"])
    x["ordem"] = x.groupby("data").cumcount()
    return x[x.ordem <= 1].drop(columns="ordem").reset_index(drop=True)


def _le_vista():
    v = pd.read_parquet(U.FD / "b3_vista.parquet", columns=["data", "ticker", "fech", "oferta_compra", "oferta_venda", "fatcot"],
                        filters=[("ticker", "=", "BOVA11")]).sort_values("data").drop_duplicates("data", keep="last").set_index("data")
    out = pd.DataFrame({"bova": v.fech / v.fatcot.clip(lower=1), "bid": v.oferta_compra.where(v.oferta_compra > 0),
                        "ask": v.oferta_venda.where(v.oferta_venda > 0)})
    ib = pd.read_parquet(U.FD / "y_idx.parquet")["^BVSP"].dropna()
    out["ibov"] = ib.reindex(out.index)
    return out


def carrega():
    return {"ind": U.cache("rev_base_ind_ind", _le_ind), "vista": U.cache("rev_base_ind_vista", _le_vista)}


# =============================================================== simulação
def _simula(d, capital=20000, custo_mult=1, lag=0, alavancagem=1, thr=.02, dias_antes=5, lado="caixa"):
    x, vi = d["ind"], d["vista"]
    dias = C.DIAS[C.DIAS >= x.data.min()]          # calendário inteiro: vencimento depois do fim dos dados = marca até o último dado
    nD = len(dias)
    cdi = C.CDI.reindex(dias).fillna(0).values
    cdi_aa = (1 + C.CDI.reindex(dias).ffill()) ** 252 - 1
    B = vi.bova.reindex(dias).values
    bid, ask = vi.bid.reindex(dias).values, vi.ask.reindex(dias).values
    ib = vi.ibov.reindex(dias).values
    pos = {dt: i for i, dt in enumerate(dias)}
    fut, rf, perd = np.zeros(nD), np.zeros(nD), np.zeros(nD)
    held = np.zeros(nD)
    negs = []
    p1 = x[x.data.isin(dias)]
    for v, g in p1.groupby("venc"):
        if v not in pos:
            continue
        i_v = pos[v]
        F = pd.Series(g.ajuste.values, index=g.data.values).reindex(dias).values
        cand = [pos[t] for t in g.data if t in pos and 1 <= i_v - pos[t] <= dias_antes]
        if not cand:
            continue
        i_s = min(cand)
        du = i_v - i_s
        if not (F[i_s] == F[i_s] and ib[i_s] == ib[i_s] and ib[i_s] > 0):
            continue
        imp = (F[i_s] / ib[i_s]) ** (252 / du) - 1
        edge = imp - cdi_aa.iloc[i_s]
        sg = 1 if edge > thr else (-1 if (edge < -thr and lado == "ambos") else 0)
        i0 = i_s + 1 + lag
        if sg == 0 or i0 >= i_v:
            continue
        if not (F[i0] == F[i0] and B[i0] == B[i0]):
            continue
        sai = F[i_v] == F[i_v] and B[i_v] == B[i_v] and ib[i_v] == ib[i_v]      # sem dado do vencimento (fim da base): só marca
        W = int(np.floor(capital * alavancagem / (MULT_WIN * F[i0])))
        if W < 1:
            continue
        n = int(round(W * MULT_WIN * F[i0] / B[i0]))
        seg = slice(i0 + 1, i_v + 1)
        Fp = pd.Series(F[i0:i_v + 1]).ffill().values
        Bp = pd.Series(B[i0:i_v + 1]).ffill().values.copy()
        if sai:
            Bp[-1] = F[i_v] * B[i_v] / ib[i_v]                              # BOVA11 vendido em TWAP contra a média de liquidação
        meio = lambda px, i: min(abs(px / B[i] - 1), .005) if (px == px and px > 0) else .0003
        hs0 = meio(ask[i0] if sg > 0 else bid[i0], i0)
        hs1 = meio(bid[i_v] if sg > 0 else ask[i_v], i_v)
        pnl = sg * (n * np.diff(Bp) - W * MULT_WIN * np.diff(Fp))
        custo = (n * B[i0] * (EMOL + hs0) + W * TARIFA_WIN) * custo_mult
        c_sai = (n * Bp[-1] * (EMOL + hs1) + W * LIQ_WIN) * custo_mult if sai else 0.0
        val = n * Bp[:-1]
        if sg > 0:
            perd[seg] += val * cdi[seg]                                     # BOVA11 comprado não rende CDI
            emprest = np.maximum(val - capital, 0)
            fin = emprest * SPREAD_FIN_AA / 252 * custo_mult
            fut[seg] -= fin
        else:
            rf[seg] += val * cdi[seg]                                       # dinheiro da venda alugada rende CDI
            fin = val * ALUG_DOADOR_AA / 252 * custo_mult
            fut[seg] -= fin
            custo += n * B[i0] * ALUG_ABRE * custo_mult
        fut[seg] += pnl
        fut[i0] -= custo
        fut[i_v] -= c_sai
        custo += c_sai
        held[seg] = sg
        tot = pnl.sum() - custo - fin.sum() + (rf[seg].sum() if sg < 0 else -perd[seg].sum())
        negs.append({"ativo": f"BOVA11/WIN{g.ticker.iloc[0][3:]}", "lado": sg, "entrada": dias[i0], "saida": v, "dias": i_v - i0,
                     "retorno_%": tot / (n * B[i0]) * 100, "contrib_pp": tot / capital * 100, "taxa_impl_%": imp * 100,
                     "cdi_%": cdi_aa.iloc[i_s] * 100, "n_win": W, "n_bova": n,
                     "liquidacao_vs_fech_ibov_%": (F[i_v] / ib[i_v] - 1) * 100 if sai else np.nan})
    idx = dias
    cls = {"futuros_b3": pd.Series(fut, index=idx), "renda_fixa": pd.Series(rf, index=idx), "_cdi_perdido": pd.Series(perd, index=idx)}
    # unidade de base para o placebo: BOVA11 - CDI - futuro do 1º vencimento (ajuste), todos os dias
    F1 = p1.drop_duplicates("data").set_index("data")
    rfut = (F1.ajuste / F1.groupby("venc").ajuste.shift(1) - 1).reindex(idx).fillna(0).values
    rb = pd.Series(B).ffill().pct_change(fill_method=None).fillna(0).values
    unid = pd.Series(rb - cdi - rfut, index=idx)
    return {"classes": cls, "negocios": pd.DataFrame(negs), "held": pd.Series(held, index=idx), "unid": unid}


def excesso(d, capital=20000, custo_mult=1, lag=0, regime=REGIME, alavancagem=1, **params):
    p = {**PARAMS, **params}
    cls = _simula(d, capital, custo_mult, lag, alavancagem, **p)["classes"]
    perd = cls.pop("_cdi_perdido")
    e = ((sum(cls.values()) - perd) / capital).reindex(C.DIAS).fillna(0)
    return C.aplica_regime(e, regime, CUSTO_TROCA * custo_mult)


def classes_ir(d, capital=20000, **params):
    p = {**PARAMS, **params}
    kw = {k: p.pop(k) for k in ("custo_mult", "lag", "alavancagem") if k in p}
    p.pop("regime", None)
    return _simula(d, capital, **kw, **p)["classes"]


def _limpa(params):
    p = {**PARAMS, **params}
    for k in ("custo_mult", "lag", "alavancagem", "regime"):
        p.pop(k, None)
    return p


def posicoes(d, capital=20000, **params):
    """W = lado do negócio nos dias carregados (alinhado ao deslocamento de 2 dias de C.carteira); R = base diária de 1 unidade
    (BOVA11 - CDI - retorno do futuro do 1º vencimento). O placebo mede se o timing perto do vencimento importa."""
    s = _simula(d, capital, **_limpa(params))
    W = s["held"].reindex(C.DIAS).fillna(0).shift(-2).fillna(0).to_frame("BOVA11/WIN")
    R = s["unid"].reindex(C.DIAS).fillna(0).to_frame("BOVA11/WIN")
    return W, R


def negocios(d, capital=20000, **params):
    ng = _simula(d, capital, **_limpa(params))["negocios"]
    return ng if len(ng) else pd.DataFrame(columns=["ativo", "lado", "entrada", "saida", "dias", "retorno_%", "contrib_pp"])


if __name__ == "__main__":
    import time
    d = carrega()
    for cap in (20000, 50000, 1e8):
        for kw in ({}, {"lado": "ambos"}, {"thr": .005}, {"custo_mult": 0, "lado": "ambos"}):
            t = time.time()
            e = excesso(d, capital=cap, **kw)
            r = C.CDI + e
            f = lambda a, b: round(C.anual(r[(r.index >= a) & (r.index < b)]) - C.anual(C.CDI[(C.CDI.index >= a) & (C.CDI.index < b)]), 2)
            print(cap, kw, f"{time.time() - t:.1f}s IS", f(INICIO, CORTE), "OOS", f(CORTE, "2030"), "n", len(negocios(d, capital=cap, **kw)))
