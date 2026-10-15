"""
Carry de moedas — versão pessoa física (R$ 20 mil).

O livro é o MESMO do institucional (fundos/carry_moedas.py: pesos decididos em t, mensais, vol-alvo 8%); muda só COMO ele é executado.
Três caminhos reais para um brasileiro, todos pela IBKR (conta margem exige US$ 2.000 de patrimônio), mais o mini-dólar na B3:

  via="micro"  micro futuros de moeda da CME: M6E (12.500 EUR), M6B (6.250 GBP), M6A (10.000 AUD), MCD (10.000 CAD), MSF (12.500 CHF),
               MJY (1.250.000 JPY). O carry vem embutido no preço do futuro (pontos a termo ~ diferencial de juros). Não há micro de
               MXN, BRL, ZAR, COP, HUF, NZD, NOK, SEK: essas pernas ficam de fora. Contratos INTEIROS: 1 contrato = US$ 6,5–15 mil.
  via="spot"   câmbio à vista com margem na IBKR (G10 + MXN, ZAR, PLN, HUF, CZK, ILS, TRY, CNH; sem BRL/COP/CLP/INR/IDR/KRW/THB/PHP).
               Quantia livre (odd lot), mas o carry vem dos JUROS DA CONTA: saldo credor em moeda só rende acima de US$ 10 mil e
               proporcional a NAV/US$ 100 mil (conta de R$ 20 mil: ZERO); saldo devedor paga referência + 1,5% a.a. Então quem está
               comprado em MXN não recebe nada e quem está vendido em JPY paga JPY + 1,5%: o carry fica com o sinal TROCADO.
  via="etf"    ETFs de moeda: FXE, FXB, FXA, FXC, FXF, FXY (depósito na moeda, taxa 0,40%) e CEW (cesta EM via forwards, 0,55%) no
               lugar de TODAS as pernas emergentes. Carry embutido no ETF (o fundo recebe os juros, não a conta). Pernas vendidas
               = venda a descoberto (ações inteiras, aluguel, Reg T); compradas são pagas à vista -> quase todo o capital vai para fora.
  Perna BRL (todas as vias): vender mini-dólar WDO (US$ 10 mil, contrato inteiro, garantia em Tesouro Selic rende CDI).
  hedge=True: vende WDO também contra o dinheiro mandado para fora (só cabe com capital grande; WDO = US$ 10 mil).

Ponto (d) do pedido — "ficar no CDI já é estar comprado em real": verdade para quem mede em dólar; contra o benchmark CDI, o caixa em
CDI rende excesso ZERO. A perna BRL do institucional (comprado em real contra dólar: CDI - cupom + variação) é uma aposta A MAIS, e
para o varejo ela só existe via WDO (grande demais). Pior: todo dólar mandado para fora sem hedge é uma posição VENDIDA em real
(perde CDI - T-bill ~ 8 pp a.a. no OOS e leva a volatilidade do câmbio) — o contrário da maior perna do fundo.

Contabilidade (calendário união B3 + EUA, depois agregado nos pregões da B3; patrimônio nominal constante = capital, em R$):
  excesso_t = [ E_{t-1}·PTAX_{t-1}·(ΔPTAX + rende_caixa - CDI)      dinheiro lá fora: câmbio sem hedge e custo de oportunidade do CDI
              + PnL do livro (US$)·PTAX                              nocional constante entre rebalanceamentos (como o institucional)
              + PnL do WDO (R$) - custos - IOF/spread de remessa ] / capital
  E = patrimônio na IBKR. A cada rebalanceamento: manda o que falta para max(US$ 2.000, 1,5x a margem inicial [, compras à vista no
  ETF]); devolve o excesso se E > 1,5x o alvo. Remessa: IOF 1,1% (investimento, mesmo titular; Decreto 12.499/2025) + 0,5% de spread na
  ida e 0,38% + 0,5% na volta, cobrados JUNTOS na ida (varejo.py usa 1,1% na volta: errado, o ingresso paga 0,38%).
  Caixa da IBKR parado em SGOV (T-bill - 0,09%); saldo devedor em US$ paga T-bill + 1,5%.
  Chamada de margem: se E < margem de manutenção no fim do dia, a IBKR zera/reduz posições até caber na inicial (custo de giro);
  QUEBRA se o patrimônio total (CDI + excessos acumulados) zerar: -100% e fica em CDI.
  Regime dd_stop do institucional aplicado no fim, como no contrato.

Premissas verificadas (out/2026) e onde divergem de varejo.py:
  - IBKR: juros credores 0% em conta com NAV < US$ 10 mil; acima, BM - 0,5% proporcional a NAV/US$ 100 mil; devedor BM + 1,5% (Pro).
  - IBKR conta margem: mínimo US$ 2.000 (futuros e FX à vista exigem conta margem) -> com R$ 4 mil (~US$ 800) NÃO dá para operar.
  - Margens de manutenção CME (aprox.): M6E US$ 231, MJY 308, MSF 396 (corretoras, out/2026); M6A/M6B/MCD ~US$ 150–200 (estimado).
  - FX à vista IBKR: margem ~3% G10, 5% CNH, 6% MXN/PLN/HUF/CZK/ILS, 7% ZAR, 20% TRY; comissão 0,2 bp, mínimo US$ 2/ordem.
  - IOF: ida 1,1% (remessa para investimento), volta 0,38% (varejo.py supõe 1,1% na volta).
"""
from pathlib import Path

import numpy as np
import pandas as pd

import comum
import varejo as V
from fundos import carry_moedas as I

NOME = "Carry de moedas G10 + emergentes (varejo)"
TESE = "Mesmo livro do institucional executado como pessoa física: micro futuros CME / FX à vista IBKR / ETFs de moeda + WDO na B3"
BENCHMARK = "CDI"
INICIO, CORTE = I.INICIO, I.CORTE
REGIME = I.REGIME
CUSTO_TROCA = I.CUSTO_TROCA
PARAMS, GRADE, VIZINHANCA = dict(I.PARAMS), I.GRADE, I.VIZINHANCA
CAPITAL = V.CAPITAL
VIA = "etf"              # único caminho que de fato monta o livro com R$ 20 mil (micro = zero contratos; à vista = carry invertido)

APLICAVEL = False
MOTIVO = ("Com R$ 20 mil o carry não sobrevive: micro futuros (US$ 6,5–15 mil/contrato) e WDO (US$ 10 mil) não cabem nas pernas de ~US$ 1 mil "
          "(zero contratos = CDI); FX à vista inverte o carry (conta < US$ 10 mil não recebe juros e paga BM+1,5% no vendido); ETFs montam o "
          "livro mas exigem ~77% do capital em dólar sem hedge, que custa ~8 pp a.a. de CDI - T-bill.")
INSTRUMENTOS = ("Via ETF (padrão): IBKR Pro — compra/venda FXE, FXB, FXA, FXC, FXF, FXY (CurrencyShares, 0,40%) e CEW (cesta EM via forwards, "
                "0,55%) no lugar das pernas emergentes; venda a descoberto só em conta margem (mín. US$ 2.000), ações inteiras, aluguel ~0,5% "
                "(CEW 2%), Reg T 50% inicial / 25–30% manutenção; abaixo de US$ 2 mil só as pernas compradas (conta caixa). Perna BRL: vender "
                "WDO na B3 (US$ 10 mil, garantia em Tesouro Selic) — nunca cabe em R$ 20 mil. Alternativas testadas: via='micro' (M6E 12.500 EUR, "
                "M6B 6.250 GBP, M6A 10.000 AUD, MCD 10.000 CAD, MSF 12.500 CHF, MJY 1,25 mi JPY; margem US$ 150–400) e via='spot' (IBKR FX).")
ALAVANCAGENS = [1, 1.5, 2, 5]
MOTIVO_ALAV = ("Todas rodam no motor, mas: ETF é limitado pela Reg T (5x vira ~2,3x efetivo; abaixo de US$ 2 mil, conta caixa = no máximo 1x); "
               "micro futuros só têm contrato a partir de 5x (1x–2x = zero contratos); FX à vista a 5x QUEBRA em abr/2025 (choque de tarifas, "
               "iene) depois de perder o CDI todo ano.")

PASTA = Path(__file__).resolve().parents[1] / "dados" / "carry_moedas"
MIN_MARGEM = 2000.0                                   # US$: patrimônio mínimo para conta margem na IBKR
IDA = .011 + .005 + .0038 + .005                      # IOF ida + spread ida + IOF volta + spread volta (pago na ida)
SGOV_TAXA = .0009
FOLGA = 3.0                                           # patrimônio na IBKR = 3x a margem inicial (futuro/FX); ETF: Reg T 50%
DEV, CRED_SPREAD, CRED_LIMIAR, NAV_CHEIO = .015, .005, 10_000.0, 100_000.0
WDO_USD, WDO_CUSTO = 10_000.0, 4.0                   # R$ por contrato por lado (emolumentos + meio tick)

# micro futuros CME: coluna -> (tamanho em moeda, margem de manutenção US$)
MICRO = {"EURUSD=X": (12_500, 231), "GBPUSD=X": (6_250, 200), "AUDUSD=X": (10_000, 180), "CAD=X": (10_000, 150),
         "CHF=X": (12_500, 396), "JPY=X": (1_250_000, 308)}
MICRO_CUSTO = 1.05                                    # US$ por contrato por lado: IBKR 0,25 + CME/NFA ~0,20 + meio tick ~0,60
# FX à vista IBKR: margem de manutenção (% do nocional)
SPOT = {"EURUSD=X": .03, "GBPUSD=X": .03, "AUDUSD=X": .03, "NZDUSD=X": .03, "JPY=X": .03, "CAD=X": .03, "CHF=X": .03, "NOK=X": .03,
        "SEK=X": .03, "MXN=X": .06, "ZAR=X": .07, "PLN=X": .06, "HUF=X": .06, "CZK=X": .06, "ILS=X": .06, "TRY=X": .20, "CNY=X": .05}
ODD_LOT = .0003                                       # spread extra de odd lot (< US$ 25 mil) por lado
# ETFs: ETF -> colunas do livro que ele representa
ETF = {"FXE": ["EURUSD=X"], "FXB": ["GBPUSD=X"], "FXA": ["AUDUSD=X"], "FXC": ["CAD=X"], "FXF": ["CHF=X"], "FXY": ["JPY=X"],
       "CEW": [k for k, (_, t) in I.MOEDAS.items() if t not in ("G10", "BRL")]}
ETF_SLIP = {"CEW": .0015}
ETF_ALUGUEL = {"CEW": .02}


def carrega():
    d = I.carrega()
    e = pd.read_csv(PASTA / "etfs_moeda.csv", index_col=0, parse_dates=True)
    d["etf"] = e[[f"{k}_adj" for k in ETF]].set_axis(list(ETF), axis=1)
    return d


def _mercado(d, via, U, Wus, Rus):
    """Pesos (US$ por R$ 1 de capital), retornos por lado e preço unitário de cada instrumento, no calendário U."""
    bis = d["bis"].reindex(U.union(d["bis"].index)).ffill().reindex(U) / 100
    us_dia = pd.Series(U.isin(comum.DIAS_US), index=U)
    if via == "etf":
        px = d["etf"].reindex(U.union(d["etf"].index)).ffill(limit=5).reindex(U)
        r = d["etf"].pct_change(fill_method=None).reindex(U).fillna(0)
        W = pd.DataFrame({k: Wus[c].sum(axis=1) for k, c in ETF.items()})
        alug = pd.Series({k: ETF_ALUGUEL.get(k, V.ALUGUEL_ETF_EUA) for k in ETF})
        return W, r, r + np.outer(us_dia.values, alug.values / 252), px, None
    cols = list(MICRO) if via == "micro" else list(SPOT) if via == "spot" else list(I.MOEDAS)
    R = Rus[cols].reindex(U).fillna(0)
    if via != "spot":                                  # futuro / institucional: spot + carry embutido
        return Wus[cols], R, R, None, None
    spot = (Rus[cols] - I.carry(d).shift(1).reindex(Rus.index)[cols] / 252).reindex(U).fillna(0)
    bm = pd.DataFrame({c: bis[I.MOEDAS[c][0]] for c in cols})
    return Wus[cols], spot, spot, None, bm             # juros aplicados no motor (dependem do saldo)


def _motor(d, capital, custo_mult, lag, alavancagem, via, hedge, inst, params):
    W0, Rus, _, _, _ = I._livro(d, **params)
    Rus = Rus.fillna(0)
    Wus = W0.reindex(Rus.index).fillna(0).shift(1 + lag).fillna(0)          # executado em t+1+lag
    U = comum.DIAS.union(Rus.index)
    U = U[U >= max(Rus.index[0], comum.PTAX.first_valid_index())]
    W, RL, RS, px, bm = _mercado(d, "inst" if inst else via, U, Wus, Rus)
    cols = list(W.columns)
    Wv = W.reindex(U).ffill().fillna(0).values
    RLv, RSv = RL.values, RS.values
    bmv = None if bm is None else bm.fillna(0).values
    if via == "micro" and not inst:                                          # preço de 1 contrato em US$
        unit = d["fx"].reindex(U.union(d["fx"].index)).ffill(limit=5).reindex(U)[cols].values * np.array([MICRO[c][0] for c in cols])
    elif via == "etf" and not inst:
        unit = px.values
    else:
        unit = None                                                          # quantia livre
    mm = np.array([MICRO[c][1] for c in cols]) if via == "micro" and not inst else None
    mspot = np.array([SPOT[c] for c in cols]) if via == "spot" and not inst else None
    custo_tipo = np.array([I.CUSTO[I.MOEDAS[c][1]] for c in cols]) if unit is None else None
    slip = np.array([ETF_SLIP.get(c, 0) for c in cols])
    ptax = comum.PTAX.reindex(U).ffill().values
    b3, usd = U.isin(comum.DIAS), U.isin(comum.DIAS_US)
    fx = np.where(b3, comum.PTAX.reindex(U).ffill().pct_change(fill_method=None).fillna(0).values, 0)
    cdi = comum.CDI.reindex(U).fillna(0).values
    tb = np.where(usd, comum.TB_US.reindex(U).fillna(0).values, 0)
    brl_car = np.where(b3, (I.carry_brl(d).shift(1) / 252).reindex(U).fillna(0).values, 0)
    wbrl = np.zeros(len(U)) if inst else Wus["BRL=X"].reindex(U).ffill().fillna(0).values
    mes = np.r_[False, U.month[1:] != U.month[:-1]]
    roll = mes & np.isin(U.month, [3, 6, 9, 12])

    def margem(n, X):
        """(manutenção, inicial) em US$."""
        if via == "micro":
            m = (np.abs(n) * mm).sum()
            return m, 1.1 * m
        if via == "spot":
            m = (np.abs(X) * mspot).sum()
            return m, 1.25 * m
        L, S = X.clip(min=0).sum(), -X.clip(max=0).sum()
        return .25 * L + .30 * S, .5 * (L + S)

    def custo_giro(dn, dX, t):
        if not (np.abs(dX) > 1e-9).any():
            return 0.0
        if inst:
            return (np.abs(dX) * custo_tipo).sum()
        if via == "micro":
            return np.abs(dn).sum() * MICRO_CUSTO
        if via == "spot":
            g = np.abs(dX)
            return (g * (custo_tipo + ODD_LOT) + np.where(g > 1e-9, np.maximum(2.0, .00002 * g), 0)).sum()
        return (V.custo_ordem_usd(dX, np.nan_to_num(unit[t], nan=1.0)) + np.abs(dX) * slip).sum()

    def quantidades(alvo, t):
        if unit is None:
            return alvo.copy(), alvo.copy()
        u = np.nan_to_num(unit[t])
        n = np.round(np.divide(alvo, u, out=np.zeros_like(alvo), where=u > 0))
        return n, n * u

    k = len(cols)
    n, X, E, nw, P = np.zeros(k), np.zeros(k), 0.0, 0.0, 1.0
    quebrou, chamadas, wprev = None, 0, np.full(k, np.nan)
    ex, bruto, fora = np.zeros(len(U)), np.zeros(len(U)), np.zeros(len(U))
    t0 = max(int(U.searchsorted(pd.Timestamp(INICIO))), 1)                 # o fundo começa a operar em INICIO
    for t in range(t0, len(U)):
        cap_usd = capital / ptax[t - 1]
        pnl, custo = 0.0, 0.0
        # ---- resultado do dia com as posições de ontem (US$)
        if usd[t]:
            pnl = (X * np.where(X >= 0, RLv[t], RSv[t])).sum()
            if bmv is not None:                                              # FX à vista: juros por moeda na conta
                phi = min(cap_usd / NAV_CHEIO, 1.0)
                cred = np.clip(bmv[t] - CRED_SPREAD, 0, None) * phi * np.clip(np.abs(X) - CRED_LIMIAR, 0, None) / np.maximum(np.abs(X), 1)
                pnl += (X.clip(min=0) * cred - (-X.clip(max=0)) * np.clip(bmv[t] + DEV, 0, None)).sum() / 252
            if not inst:
                B = E - (X.sum() if via != "micro" else 0.0)                 # dinheiro livre (vendas a descoberto entram como caixa)
                pnl += B * (tb[t] - SGOV_TAXA / 252) if B > 0 else B * (tb[t] + DEV / 252)
        reais = pnl * ptax[t] + E * ptax[t - 1] * (fx[t] - cdi[t]) + nw * WDO_USD * ptax[t - 1] * (brl_car[t] - fx[t])
        E += pnl
        # ---- chamada de margem no fechamento: a IBKR reduz até caber na inicial
        if not inst and (X != 0).any():
            req, ini = margem(n, X)
            if E < req:
                chamadas += 1
                f = max(E, 0) / ini
                n2 = np.sign(n) * np.floor(np.abs(n) * f) if unit is not None else n * f
                X2 = X * np.divide(n2, n, out=np.zeros_like(n), where=n != 0) if unit is not None else X * f
                custo += custo_giro(n - n2, X - X2, t)
                n, X = n2, X2
        # ---- rebalanceamento quando o peso executado muda
        if usd[t] and not np.array_equal(Wv[t], wprev):
            wprev = Wv[t].copy()
            n2, X2 = quantidades(Wv[t] * alavancagem * cap_usd, t)
            if not inst and (X2 != 0).any():
                margem_conta = via != "etf" or (X2 < 0).any()                # ETF só comprado roda em conta caixa
                piso = MIN_MARGEM if margem_conta else 0.0
                _, ini = margem(n2, X2)
                exige = FOLGA * ini if via != "etf" else ini                   # folga de 50% na margem inicial (Reg T: 50%)
                need = max(piso, exige) if via != "etf" else max(piso, X2.clip(min=0).sum() - .5 * X2.clip(max=0).sum())
                if margem_conta and cap_usd < MIN_MARGEM:                    # nem abre conta margem
                    if via == "etf":                                         # conta caixa: só as pernas compradas, à vista
                        n2, X2 = n2.clip(min=0), X2.clip(min=0)
                        f = min(1.0, cap_usd / max(X2.sum(), 1e-9))
                        n2, X2 = np.floor(n2 * f), np.floor(n2 * f) * np.nan_to_num(unit[t])
                        need = X2.sum()
                    else:
                        n2, X2, need = n2 * 0, X2 * 0, 0.0
                elif exige > cap_usd:                                        # não cabe no capital: corta a posição
                    n2, X2 = quantidades(Wv[t] * alavancagem * cap_usd * cap_usd / exige, t)
                need = min(need, cap_usd)                                    # ETF acima do caixa: saldo devedor (Reg T)
                if E < need:                                                 # manda o que falta (IOF + spread)
                    reais -= (need - E) * ptax[t] * IDA * custo_mult
                    E = need
                elif E > min(1.5 * need, cap_usd):                           # traz de volta o que sobra
                    E = need
            elif not inst:
                E = 0.0                                                      # sem posição: traz o dinheiro de volta
            custo += custo_giro(n2 - n, X2 - X, t)
            n, X = n2, X2
            alvo_brl = wbrl[t] * alavancagem * cap_usd + (E if hedge else 0)  # perna BRL (+ hedge) em WDO inteiros
            nw2 = np.round(alvo_brl / WDO_USD)
            reais -= abs(nw2 - nw) * WDO_CUSTO * custo_mult
            nw = nw2
        if roll[t] and via == "micro" and not inst:
            custo += 2 * np.abs(n).sum() * MICRO_CUSTO
        if mes[t]:
            reais -= 2 * abs(nw) * WDO_CUSTO * custo_mult                    # rolagem mensal do WDO
        custo *= custo_mult
        E -= custo
        reais -= custo * ptax[t]
        ex[t] = (pnl - custo) / cap_usd if inst else reais / capital
        bruto[t] = (np.abs(X).sum() + abs(nw) * WDO_USD) / cap_usd
        fora[t] = E / cap_usd
        P = P * (1 + cdi[t]) + ex[t]
        if P <= 0:                                                           # quebra: perde o que restava e fica em CDI
            quebrou = U[t]
            ex[t] -= P
            break
    s = pd.Series(ex, index=U)
    if inst:
        e = comum.brl(s)                                                     # institucional: excesso em US$ com hedge
    else:
        a = s.cumsum().reindex(comum.DIAS.union(U)).ffill().reindex(comum.DIAS).fillna(0)
        e = a.diff().fillna(a)                                               # dias fora da B3 entram no pregão seguinte
    oos = U >= pd.Timestamp(CORTE)
    info = {"chamadas de margem": chamadas, "quebrou": None if quebrou is None else str(quebrou.date()),
            "alavancagem efetiva média (OOS)": float(bruto[oos].mean()), "fração do capital lá fora (OOS)": float(fora[oos].mean())}
    return e, info


def excesso(d, capital=CAPITAL, custo_mult=1, lag=0, regime=REGIME, alavancagem=1.0, via=VIA, hedge=False, inst=False, detalhe=False,
            **params):
    """Excesso diário sobre o CDI em R$ (fração do capital), antes do IR. inst=True: mesmo motor com custos/carry institucionais (validação)."""
    e, info = _motor(d, capital, custo_mult, lag, alavancagem, via, hedge, inst, {**PARAMS, **params})
    e = comum.aplica_regime(e, regime, CUSTO_TROCA * custo_mult)
    return (e, info) if detalhe else e


def posicoes(d, via=VIA, **params):
    """Pesos-alvo do institucional só nas pernas que o caminho de varejo consegue executar (+ BRL via WDO) e o excesso em US$ delas."""
    W, R = I.posicoes(d, **params)
    cols = (list(MICRO) if via == "micro" else list(SPOT) if via == "spot" else list(W.columns)) + ["BRL=X"]
    return W[cols], R[cols]


def negocios(d, via=VIA, **params):
    ng = I.negocios(d, **params)
    cols = (list(MICRO) if via == "micro" else list(SPOT) if via == "spot" else list(I.MOEDAS)) + ["BRL=X"]
    return ng[ng["ativo"].isin(cols)].reset_index(drop=True)
