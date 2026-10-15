"""
Fluxos forçados de calendário no S&P 500, operados no IVVB11 (B3, sem remessa): rebalanceamento de fim de mês/trimestre dos fundos
balanceados e o rebalanceamento diário dos ETFs alavancados (LETFs).

Tese de mesa:
  (a) "pensao" — fundos balanceados/pensões (60/40, target-date) voltam ao peso-alvo no fim do mês e, com mais força, no fim do
      trimestre. Se no mês as ações caíram contra os títulos (SPY − TLT até 5 pregões antes do fim < −limiar), eles COMPRAM ações nos
      últimos dias -> fico comprado em IVVB11 do fechamento de D−4 ao fechamento do último pregão do mês (100% do capital). O lado
      vendedor (ações subiram mais) exigiria alugar IVVB11 (0,5% por contrato + taxa) por 4 dias: não paga -> só o lado comprador.
  (b) "letf" — ETFs alavancados (TQQQ/SQQQ/UPRO/SPXU/SSO...) precisam comprar no fechamento dos dias de alta e vender nos de queda
      (exposição (L²−L) x retorno do dia), na direção do movimento; a pressão some no dia seguinte. Depois de um dia de queda do S&P
      maior que `limiar_letf`, compro IVVB11 no leilão de ABERTURA da B3 do dia seguinte e vendo no fechamento (day trade); depois de
      uma alta grande, vendo na abertura e recompro no fechamento (day trade vendido não precisa de aluguel). A reversão "overnight"
      (fechamento EUA -> abertura B3) NÃO é capturada: a abertura do IVVB11 às 10h já embute o futuro do S&P da madrugada.
Instrumento: IVVB11 (iShares S&P 500 em R$, sem hedge cambial), lote de 1 cota (~R$ 440), preços do COTAHIST (abertura, fechamento,
melhor oferta de compra/venda no fechamento). Custos: meio spread do fechamento (real, 0,03–3%) + emolumentos 0,03% por lado + 0,05%
extra na abertura (leilão). O dinheiro só sai do CDI enquanto há posição carregada de um dia para o outro (day trade não usa caixa).
IR: ETF B3 15% (swing) / 20% (day trade), sem isenção — CLASSE_IR pelo componente escolhido. Desdobramentos do IVVB11 (7 saltos
> 15%) tratados: dia com |retorno − S&P em R$| > 10% usa o retorno do S&P em R$.
Sinais com SPY/TLT do Yahoo (fechamento de Nova York, conhecido antes da abertura da B3 do dia seguinte).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

import fg_comum as G  # noqa: E402

C, pf = G.C, G.pf

NOME = "Fim de mês dos balanceados + reversão dos ETFs alavancados no IVVB11 (B3)"
TESE = ("Comprado em IVVB11 nos 4 últimos pregões do mês quando as ações apanharam dos títulos (os balanceados compram); day trade "
        "contra o rebalanceamento dos ETFs alavancados depois de dias de movimento forte do S&P.")
BENCHMARK = "CDI"
INICIO, CORTE = "2014-06-01", "2021-01-01"
REGIME = "nenhum"
CUSTO_TROCA = .001
PARAMS = {"componente": "pensao", "limiar": .01, "limiar_letf": .02, "dias_fim": 4, "peso": 1.0}
GRADE = {"componente": ["pensao", "letf", "ambos"], "limiar": [.01, .02]}
VIZINHANCA = {"limiar": (.01, .03), "limiar_letf": (.01, .025), "dias_fim": (3, 6)}
CLASSE_IR = "etf_b3"
EMOL, EXTRA_ABERTURA = .0003, .0005
INSTRUMENTOS = {"IVVB11": {"onde": "B3", "ticker": "IVVB11", "lote": "1 cota (~R$ 440)", "custo": "meio spread real + 0,03% emolumentos"},
                "caixa": {"onde": "Tesouro Selic / LFTS11", "ticker": "LFT", "lote": "R$ ~150", "custo": "0"}}
APLICAVEL = True
MOTIVO = ("Operável em qualquer corretora (IVVB11 líquido, cota de R$ 440, sem remessa). A perna vendida do fim de mês exigiria aluguel "
          "por 4 dias (0,5% por contrato na Clear/Rico) e ficou de fora.")
ALAVANCAGENS = [1, 1.5, 2]
MOTIVO_ALAV = ("1,5x/2x via garantia: o day trade usa limite operacional da corretora (sem caixa); no fim de mês a parcela acima de "
               "100% precisaria de termo/margem — tratada como financiada ao CDI. 5x num ETF de S&P = risco de cauda sem sentido.")
VARIANTES = {"pensão sem limiar": {"limiar": 0.0}, "só LETF 1%": {"componente": "letf", "limiar_letf": .01},
             "só LETF 3%": {"componente": "letf", "limiar_letf": .03}, "LETF 2% sem custos (bruto)": {"componente": "letf", "custo_mult": 0}}


def carrega():
    x = G.cotahist_fundos(["IVVB11"]).set_index("data").sort_index()
    us = G.etf(["SPY", "TLT"])
    return {"ivvb": x[["abertura", "fech", "oferta_compra", "oferta_venda"]], "us": us}


def _series(d):
    x = d["ivvb"].reindex(C.DIAS)
    us = d["us"]
    spy_brl = (G.no_idx(us["SPY"], C.DIAS) * pf.PTAX).pct_change(fill_method=None)
    r = x.fech.pct_change(fill_method=None)
    r = r.where((r - spy_brl).abs() < .10, spy_brl)                    # desdobramento: usa o S&P em R$ no dia
    ms = ((x.oferta_venda - x.oferta_compra) / x.fech / 2).clip(0, .02)
    ms = ms.where(ms > 0).rolling(20, min_periods=1).median().shift(1).fillna(.002)   # meio spread típico (só passado)
    oc = (x.fech / x.abertura - 1).where(x.abertura > 0)
    return x, r.fillna(0), ms, oc


def _roda(d, capital, custo_mult, lag, alavancagem, componente, limiar, limiar_letf, dias_fim, peso):
    x, r, ms, oc = _series(d)
    idx = C.DIAS
    T = len(idx)
    us = d["us"]
    tem = x.fech.notna().values
    cdi = C.CDI.reindex(idx).fillna(0).values
    noc = peso * alavancagem * capital
    pnl = np.zeros(T)
    trades = []
    W = np.zeros(T)                                                    # peso carregado no fechamento (para posicoes)
    # ---- (a) balanceados no fim do mês: decide no fechamento de D-(dias_fim+1), compra em D-dias_fim, vende no último pregão
    if componente in ("pensao", "ambos"):
        spy, tlt = us["SPY"], us["TLT"]
        mes = pd.Series(idx.to_period("M"), index=idx)
        ult = np.where(mes.ne(mes.shift(-1)).values)[0]                # último pregão de cada mês (calendário da B3, sabido antes)
        for u in range(1, len(ult)):
            m = ult[u]
            j = m - dias_fim - 1 - lag
            ref = idx[ult[u - 1]]                                      # fechamento do mês anterior
            if j < 25 or j <= ult[u - 1]:
                continue
            sp = spy[:idx[j]].dropna()
            tl = tlt[:idx[j]].dropna()
            if not len(sp) or not len(tl) or ref not in C.DIAS:
                continue
            p0s, p0t = spy[:ref].dropna(), tlt[:ref].dropna()
            if not len(p0s) or not len(p0t):
                continue
            rel = (sp.iloc[-1] / p0s.iloc[-1]) - (tl.iloc[-1] / p0t.iloc[-1])
            if rel > -limiar:
                continue
            k = 1.0                                                     # (trimestre com o mesmo tamanho: 2x exigiria termo/margem)
            i0, i1 = j + 1, m
            if not tem[i0]:
                continue
            q = np.floor(min(k * noc, alavancagem * capital) / x.fech.values[i0])
            if q < 1:
                continue
            v = q * x.fech.values[i0]
            rr = r.values[i0 + 1:i1 + 1]
            val = v * np.cumprod(np.r_[1, 1 + rr[:-1]])
            p = val * rr - val * cdi[i0 + 1:i1 + 1]
            c0 = v * (ms.values[i0] + EMOL) * custo_mult                 # compra (só informação de i0)
            c1 = val[-1] * (1 + rr[-1]) * (ms.values[i1] + EMOL) * custo_mult   # venda no fechamento de i1
            c = c0 + c1
            pnl[i0 + 1:i1 + 1] += p
            pnl[i0] -= c0
            pnl[i1] -= c1
            W[i0:i1] += v / capital
            trades.append({"ativo": "IVVB11 fim de " + ("trimestre" if idx[m].month in (3, 6, 9, 12) else "mês"), "lado": 1, "entrada": idx[i0], "saida": idx[i1],
                           "dias": int(i1 - i0), "retorno_%": (np.prod(1 + rr) - 1) * 100, "contrib_pp": (p.sum() - c) / capital * 100})
    # ---- (b) LETF: dia forte no S&P (fechamento de NY em t) -> day trade contrário no IVVB11 da abertura ao fechamento de t+1
    if componente in ("letf", "ambos"):
        rs = us["SPY"].pct_change(fill_method=None).dropna()
        for dt, v_ in rs[rs.abs() > limiar_letf].items():
            i = idx.searchsorted(dt + pd.Timedelta(days=1)) + lag       # 1º pregão da B3 DEPOIS do fechamento de NY
            if i >= T or not tem[i] or not np.isfinite(oc.values[i]):
                continue
            lado = -1 if v_ > 0 else 1
            q = np.floor(noc / x.abertura.values[i])
            if q < 1:
                continue
            v = q * x.abertura.values[i]
            p = lado * v * oc.values[i]
            c = 2 * v * (ms.values[i] + EMOL) * custo_mult + v * EXTRA_ABERTURA * custo_mult
            pnl[i] += p - c
            trades.append({"ativo": f"IVVB11 day trade ({'compra' if lado > 0 else 'venda'})", "lado": lado, "entrada": idx[i], "saida": idx[i],
                           "dias": 0, "retorno_%": lado * oc.values[i] * 100, "contrib_pp": (p - c) / capital * 100})
    e = pd.Series(pnl / capital, index=idx)
    return e, pd.DataFrame(trades), pd.Series(W, index=idx), r


def excesso(d, capital=20000, custo_mult=1, lag=0, regime=REGIME, alavancagem=1, componente=PARAMS["componente"], limiar=PARAMS["limiar"],
            limiar_letf=PARAMS["limiar_letf"], dias_fim=PARAMS["dias_fim"], peso=PARAMS["peso"]):
    e = _roda(d, capital, custo_mult, lag, alavancagem, componente, limiar, limiar_letf, int(dias_fim), peso)[0]
    return C.aplica_regime(e, regime, CUSTO_TROCA * custo_mult)


def posicoes(d, capital=20000, componente=PARAMS["componente"], limiar=PARAMS["limiar"], limiar_letf=PARAMS["limiar_letf"],
             dias_fim=PARAMS["dias_fim"], peso=PARAMS["peso"]):
    """Só a parte carregada de um dia para o outro (fim de mês); o day trade não deixa posição no fechamento."""
    _, _, W, r = _roda(d, capital, 1, 0, 1, componente, limiar, limiar_letf, int(dias_fim), peso)
    R = (r - C.CDI.reindex(C.DIAS).fillna(0)).to_frame("IVVB11")
    return W.shift(-1).fillna(0).to_frame("IVVB11"), R


def negocios(d, capital=20000, componente=PARAMS["componente"], limiar=PARAMS["limiar"], limiar_letf=PARAMS["limiar_letf"],
             dias_fim=PARAMS["dias_fim"], peso=PARAMS["peso"]):
    return _roda(d, capital, 1, 0, 1, componente, limiar, limiar_letf, int(dias_fim), peso)[1]
