"""
Variância do S&P vendida — versão pessoa física (R$ 20 mil).

O institucional (fundos/variancia.py) vende um SWAP DE VARIÂNCIA de 1 mês a VIX−1: instrumento de balcão (ISDA, dealer, nocional de
milhões). NÃO APLICÁVEL a varejo. Aqui testamos os substitutos reais de varejo, todos com o mesmo esqueleto do institucional
(hedge de beta rolante, vol-alvo de 8%, teto de risco calibrado no choque de fev/2018, regime risco_global):

  veiculo="svxy"  compra ETF SVXY (−0,5x futuros de VIX de ~1 mês desde 28/02/2018; −1x antes)            IBKR, ação fracionária
  veiculo="svix"  compra ETF SVIX (−1x, desde 30/03/2022)                                                   IBKR, ação fracionária
  veiculo="vxm"   vende mini futuro de VIX VXM (Cboe CFE, US$ 100 x VIX, desde 2020)                        IBKR, contrato inteiro
  veiculo="bfly"  vende iron butterfly mensal em XSP (mini-SPX = SPX/10; ATM vendido, asas 5%)              IBKR, contrato inteiro
  veiculo="cndr"  vende iron condor mensal em XSP (20-delta vendido, 5-delta comprado)                      IBKR, contrato inteiro
  veiculo="put"   vende put ATM mensal em XSP (como o índice PUT)                                           IBKR, contrato inteiro
Hedge de beta: compra SH (−1x S&P, fracionária, sem margem) — ou vende SPY a descoberto (hedge="spy", ações inteiras).

Proxies (premissas documentadas):
  - Antes de existir o ETF, SVXY/SVIX = −1x o índice de futuros de VIX de 30 dias (montado aqui com os ajustes da Cboe CFE dos dois
    primeiros vencimentos) menos a taxa do ETF (0,95% / 1,35% a.a.). Depois, preço real do ETF (com o decaimento real).
  - VXM: P&L = contratos x US$ 100 x variação do mesmo índice de 30 dias (o VXM liquida no mesmo VIX que o VX); rolagem mensal cobrada.
  - Opções XSP: sem histórico gratuito de preço de opção -> índices Cboe BFLY/CNDR/PUT como proxy (excesso sobre T-bill). Os índices
    BFLY/CNDR guardam caixa = 10x a perda máxima; um contrato XSP "vale" então 10x a perda máxima em capital do índice. Perda máxima
    calibrada na foto de cotação XSP de 15/10/2026 (vencimento 20/11/2026, S=771,9): BFLY 2,31% de S, CNDR 7,75% de S (constantes; na
    prática variam com a vol). PUT: 1 contrato = S x 100 de nocional; margem de put a descoberto ~17% do nocional (Reg T índice: 15% + prêmio).
  - Meio spread observado nas opções XSP: US$ 0,045 (mediana) -> US$ 5 por perna; comissão IBKR US$ 0,60/contrato (faixa US$ 0,31-0,60).

Conta pequena (o que muda de verdade):
  - Só manda para a IBKR a fração `exterior` do capital (o resto fica no CDI no Brasil): dinheiro lá fora fica SEM hedge cambial (o mini
    dólar WDO tem US$ 10 mil; só é viável a partir de ~US$ 10 mil lá fora — variante hedge_cambial=True arredonda para WDOs inteiros).
  - Conta mensal: no 1º pregão do mês a conta lá fora volta ao nominal (lucro volta ao Brasil / perda é reposta). Dentro do mês, o
    patrimônio anda; abaixo da margem de manutenção a IBKR liquida (chamada de margem); patrimônio <= 0 = QUEBRA (−100%, fica no CDI).
  - Conta de margem (futuros, opções, venda a descoberto, alavancagem) exige patrimônio >= US$ 2.000 na IBKR (regra FINRA/IBKR);
    abaixo disso, só ETF comprado em conta cash.
  - Margens: VXM manutenção ~45% do nocional (IBKR: US$ 744 com VIX ~16,5; inicial US$ 856); SVXY/SVIX: premissa conservadora de 50%
    (IBKR cobra margem "house" maior em ETPs de volatilidade — não confirmado); SH/SPY Reg T 50% inicial / 25% manutenção (30% vendido).
  - Juros: caixa só rende se comprar SGOV (T-bill − 0,10%); dívida de margem paga T-bill + 1,5%; aluguel de SPY 0,5% a.a. (varejo.py).
  - Premissas de varejo.py corrigidas AQUI: comissão IBKR Pro tiered (US$ 0,0035/ação, mín. US$ 0,35) em vez do fixo (mín. US$ 1);
    IOF da volta 0,38% (não 1,1%).

Resultado (OOS 2021+, antes do IR, R$ 20 mil): SVXY+SH −2,1 pp a.a. vs CDI; com câmbio hedgeado (teórico) +0,7 pp. O livro em dólar
(SVXY + SH) rende ~+1 pp a.a. sobre o capital; o carregamento CDI − T-bill e o real forte sobre os 30% remetidos custam ~−2,8 pp.
Validação (capital de R$ 100 mi, custo 0,2x, câmbio hedgeado com WDO): SVXY ≈ 0 pp IS e OOS, VXM +0,9/+0,5, PUT −1,5/+0,3 contra
+3,4/+7,6 do institucional (correlação diária 0,4-0,5). A diferença é estrutural: o swap sintético vendido a VIX−1 captura o
prêmio variância implícita − realizada inteiro; futuro de VIX e índices de opção com hedge de beta capturam pouco dele.
"""
import numpy as np
import pandas as pd

import comum
import varejo as V
from fundos import variancia as VI

NOME = "Variância do S&P vendida (beta neutro) — varejo"
TESE = "Sem swap de variância: vender vol do S&P com ETF inverso de VIX (SVXY) + SH, vol-alvo 8% e regime risco_global"
BENCHMARK = "CDI"
INICIO, CORTE = VI.INICIO, VI.CORTE
REGIME = "risco_global"
CUSTO_TROCA = 0.0                 # liga/desliga já paga custo de verdade (as ordens na simulação)
CAPITAL = V.CAPITAL
PARAMS = {"veiculo": "svxy", "teto": .4, "hedge": "sh", "exterior": .3, "banda": .5, "hedge_cambial": False}
GRADE = {"veiculo": ["svxy", "svix", "vxm", "bfly", "cndr", "put"], "teto": [.25, .4]}
VIZINHANCA = {"teto": (.25, .5), "exterior": (.2, .45), "banda": (.25, .75)}
ALAVANCAGENS = [1, 1.5, 2, 5]
MOTIVO_ALAV = ("todas são operáveis: alavancar = remeter mais (30% -> 45/60/100% do capital) e comprar mais SVXY; 5x usa margem Reg T "
               "(conta >= US$ 2 mil). Sem chamada de margem nem quebra (o teto e a vol-alvo limitam o SVXY a <= 1x o capital), mas a 5x "
               "fev/2018 custa −21% do capital e o dólar sem hedge sobre 100% do capital domina; VXM 5x idem (−25% em fev/2018)")

ALVO, JANELA_VOL = .08, 126
APLICAVEL = True
MOTIVO = ("swap de variância não é de varejo; o substituto operável com R$ 20 mil é SVXY + SH na IBKR (frações de ação), "
          "mas o prêmio do futuro de VIX é bem menor que o do swap e o dólar sem hedge pesa")
INSTRUMENTOS = ("IBKR (conta cash ou margem; ações fracionárias): COMPRAR SVXY (ProShares −0,5x futuros de VIX; ~US$ 64) com ~10-25% "
                "do capital e SH (−1x S&P; ~US$ 32) no valor beta x SVXY; caixa lá fora em SGOV. Remeter só ~30% do capital; o resto em "
                "Tesouro Selic. Rebalancear só se a posição se afastar >50% do alvo; comissão IBKR Pro tiered. Alternativas testadas: VXM (Cboe, US$ 100 x VIX, "
                "margem ~US$ 750-860 por contrato -> 1 contrato ≈ 45% de R$ 20 mil, grande demais), opções XSP (1 iron butterfly ≈ US$ 1,8 "
                "mil de risco; 1 iron condor ≈ US$ 6 mil; 1 put ATM ≈ US$ 13 mil de margem).")

TAXA_ETF = {"svxy": .0095, "svix": .0135}
INICIO_ETF = {"svxy": "2011-10-05", "svix": "2022-03-31"}
IDX = {"bfly": "BFLY", "cndr": "CNDR", "put": "PUT"}
PERDA_MAX = {"bfly": .0231, "cndr": .0775}          # perda máxima de 1 contrato, fração de S x 100 (foto XSP 15/10/2026)
PERNAS = {"bfly": 4, "cndr": 4, "put": 1}
CUSTO_PERNA = 5.0 + .60                               # US$ por contrato por perna: meio spread + comissão IBKR
CUSTO_VXM = 4.0 + 1.5                                 # US$ por contrato por lado: meio spread (~1 tick) + comissão/taxas IBKR+CFE
MARGEM_VXM = .45                                      # manutenção / nocional (IBKR ~US$ 744 com VIX ~16,5); inicial = 1,15x
MARGEM_PUT = .17
MARGEM_ETF_VOL = .50                                  # SVXY/SVIX (premissa conservadora)
MIN_CONTA_MARGEM = 2000.0
EXTERIOR_MIN = {"vxm": 1.0, "bfly": 1.0, "cndr": 1.0, "put": 1.0}   # futuro/opção: precisa de conta de margem (>= US$ 2 mil) -> remete tudo
WDO_USD, WDO_CUSTO_MES = 10_000.0, 10.0              # mini dólar B3: US$ 10 mil; ~R$ 10/mês por contrato (rolagem + emolumentos)
IBKR_TIER_ACAO, IBKR_TIER_MIN = .0035, .35            # IBKR Pro tiered (interactivebrokers.com/en/pricing/commissions-home.php)
# IOF 2026 (Decreto 12.499/2025): remessa para investimento 1,1%; ingresso (volta) 0,38% — varejo.py usa 1,1% na volta (corrigido aqui)
REMESSA_IDA_VOLTA = .011 + .0038 + .01
CHOQUE_INST = .10                                     # teto 0,4 do institucional ≈ perder 10% do PL num choque tipo 5/fev/2018


# ---------------------------------------------------------------- dados
def carrega():
    p = V.C.AQUI / "varejo" / "dados" / "variancia"
    return {"etf": pd.read_csv(p / "etfs.csv", index_col=0, parse_dates=True),
            "idx": pd.read_csv(p / "cboe_idx.csv", index_col=0, parse_dates=True),
            "vx": pd.read_csv(p / "vx.csv", parse_dates=["data", "venc"]),
            "px": VI.carrega()["px"]}


def _vx30(vx, cal):
    """Índice de futuros de VIX com prazo constante de 30 dias (como o SPVXSP): pesos entre o 1º e o 2º vencimento decididos em t−1.
    Devolve retorno diário e nível (preço médio ponderado), no calendário `cal`."""
    p = vx.pivot(index="data", columns="venc", values="ajuste")
    venc = p.columns.values
    dias = p.index.values
    k = np.searchsorted(venc, dias, side="right")            # 1º vencimento depois da data
    ok = k + 1 < len(venc)
    k = np.minimum(k, len(venc) - 2)
    d1 = (venc[k] - dias) / np.timedelta64(1, "D")
    d2 = (venc[k + 1] - dias) / np.timedelta64(1, "D")
    w1 = np.clip((d2 - 30) / (d2 - d1), 0, 1)
    P = p.values
    i = np.arange(len(dias))
    f1, f2 = P[i, k], P[i, k + 1]
    nivel = np.where(ok, w1 * f1 + (1 - w1) * f2, np.nan)
    # hoje, com os contratos e pesos de ontem
    f1h, f2h = P[np.minimum(i + 1, len(i) - 1), k], P[np.minimum(i + 1, len(i) - 1), k + 1]
    amanha = w1 * f1h + (1 - w1) * f2h
    r = pd.Series(amanha / nivel - 1, index=p.index).shift(1)
    out = pd.DataFrame({"ret": r, "nivel": nivel}, index=p.index)
    return out.reindex(cal), pd.Series(venc, index=venc)


def _terceiras_sextas(cal):
    """Dia de rolagem das opções mensais (3ª sexta; feriado -> pregão anterior). Só calendário, sem dado de mercado."""
    m = pd.date_range(cal[0] - pd.offsets.MonthBegin(1), cal[-1] + pd.offsets.MonthEnd(1), freq="WOM-3FRI")
    pos = np.searchsorted(cal.values, m.values, side="right") - 1
    return pd.DatetimeIndex(cal[pos[pos >= 0]]).unique()


def _series(d, veiculo):
    """Retornos (calendário dos EUA) do veículo e do hedge, e o excesso por unidade do veículo vendido em vol."""
    etf = d["etf"]
    cal = etf.index[etf["SPY_close"].notna()]
    etf = etf.reindex(cal)
    tb = V.TBILL.reindex(cal).ffill().fillna(0)
    ret = lambda s: s.pct_change(fill_method=None)
    vx, vencs = _vx30(d["vx"], cal)
    out = {"cal": cal, "tb": tb, "spy": ret(etf["SPY_adj"]).fillna(0), "sh": ret(etf["SH_adj"]).fillna(0),
           "p_spy": etf["SPY_close"].ffill(), "p_sh": etf["SH_close"].ffill(), "vx": vx}
    if veiculo in TAXA_ETF:
        mult = pd.Series(np.where(cal < pd.Timestamp("2018-02-28"), -1.0, -.5), index=cal) if veiculo == "svxy" else -1.0
        sint = mult * vx["ret"] - TAXA_ETF[veiculo] / 252
        real = ret(etf[f"{veiculo.upper()}_adj"])
        r = real.where(cal >= pd.Timestamp(INICIO_ETF[veiculo]), sint)
        out.update(r=r, x=r - tb, p=etf[f"{veiculo.upper()}_close"].ffill().fillna(50.0), tipo="etf",   # preço só p/ comissão
                   choque=(-mult if np.ndim(mult) else pd.Series(1.0, index=cal)))
    elif veiculo == "vxm":
        out.update(r=-vx["ret"], x=-vx["ret"], p=vx["nivel"].ffill() * 100, tipo="fut", choque=pd.Series(1.0, index=cal),
                   venc=vencs)
    else:
        ix = d["idx"][IDX[veiculo]].reindex(cal)
        s = d["px"]["sp500"].reindex(cal).ffill() / 10 * 100           # nocional de 1 contrato XSP
        unidade = s * (10 * PERDA_MAX[veiculo] if veiculo in PERDA_MAX else 1.0)
        x = ret(ix) - tb
        out.update(r=x, x=x, p=unidade, nocional=s, tipo="opt", choque=pd.Series(.10, index=cal))
    return out


def _alvos(S, teto, alavancagem, regime, lag):
    """Peso-alvo do veículo (fração do capital total, decidido em t) e beta para o hedge — só passado (rolling + shift)."""
    x, h = S["x"], S["spy"] - S["tb"]
    x5, h5 = x.rolling(5).sum(), h.rolling(5).sum()
    beta = (x5.rolling(252, min_periods=126).cov(h5) / (h5.rolling(252, min_periods=126).var() + 1e-12)).shift(1).clip(-1, 3)
    Rh = x - beta * h
    vol = Rh.rolling(JANELA_VOL, min_periods=40).std().shift(1) * np.sqrt(252)
    wmax = teto / .4 * CHOQUE_INST / S["choque"]
    W = (ALVO / vol).clip(upper=wmax).where(Rh.notna().cumsum() > 40) * alavancagem
    if regime == "risco_global":
        W = W * comum.regime_risco_global().reindex(S["cal"], method="ffill").fillna(1.0)
    return W.fillna(0), beta.fillna(0), Rh


# ---------------------------------------------------------------- simulação diária da conta na IBKR
def _simula(d, veiculo, teto, hedge, exterior, banda, capital, custo_mult, lag, regime, alavancagem, sgov=True):
    S = _series(d, veiculo)
    cal, tipo = S["cal"], S["tipo"]
    W, beta, _ = _alvos(S, teto, alavancagem, regime, lag)
    W, beta = W.shift(1 + lag).fillna(0).values, beta.shift(1 + lag).fillna(0).values      # executa no fechamento de t+1+lag
    ptax = V.PTAX.reindex(cal, method="ffill").bfill().values
    f = min(1.0, max(exterior, EXTERIOR_MIN.get(veiculo, 0)) * max(alavancagem, 1))
    C_usd = capital / ptax                     # capital total em US$ (R$ constante)
    B = f * C_usd                              # nominal da conta lá fora
    r_main = S["r"].fillna(0).values
    tb = S["tb"].values
    r_sh, r_spy = S["sh"].values, S["spy"].values
    p_main, p_sh, p_spy = S["p"].values, S["p_sh"].values, S["p_spy"].values
    nocional = S["nocional"].values if "nocional" in S else None
    mes = pd.Series(cal.to_period("M"), index=cal)
    novo_mes = mes.ne(mes.shift()).values
    rola = np.zeros(len(cal), bool)
    if tipo == "opt":
        rola[np.isin(cal, _terceiras_sextas(cal))] = True
    if tipo == "fut":
        v = S["venc"].values
        rola[1:] = np.searchsorted(v, cal.values[1:], side="left") != np.searchsorted(v, cal.values[:-1], side="left")
    m_main_i, m_main_m = {"etf": (MARGEM_ETF_VOL, MARGEM_ETF_VOL), "fut": (MARGEM_VXM * 1.15, MARGEM_VXM)}.get(tipo, (None, None))
    n = len(cal)
    pnl = np.zeros((n, 3))                     # veículo, SH, SPY
    custo = np.zeros(n)
    juros = np.zeros(n)
    expo = np.zeros(n)
    chamadas, quebra = [], None
    E = B[0]
    q = 0.0                                    # veículo: valor (etf), contratos (fut/opt)
    k_opt = 0.0                                # capital-do-índice por contrato na entrada (opções)
    v_sh = v_spy = 0.0
    for t in range(1, n):
        if quebra is not None:
            break
        if novo_mes[t]:
            E = B[t - 1]                       # acerto mensal com o Brasil (antes do pregão)
        # ---- P&L do dia (posições do fechamento de t-1)
        if tipo == "etf":
            pm = q * r_main[t]
            q *= 1 + r_main[t]
        elif tipo == "fut":
            pm = q * p_main[t - 1] * r_main[t] if np.isfinite(p_main[t - 1]) else 0.0   # vendido: r_main = −Δ% do futuro
        else:
            pm = q * k_opt * r_main[t]
        ps, pp = v_sh * r_sh[t], v_spy * r_spy[t]
        v_sh *= 1 + r_sh[t]
        v_spy *= 1 + r_spy[t]
        trava = (abs(q) * p_main[t - 1] * m_main_m if tipo == "fut" else 0.0) + \
                (abs(q) * (k_opt / 10 if veiculo in PERDA_MAX else nocional[t - 1] * MARGEM_PUT) if tipo == "opt" else 0.0)
        longos = (q if tipo == "etf" else 0.0) + v_sh + max(v_spy, 0.0)
        caixa = E - longos - trava
        j = caixa * (tb[t] - V.TAXA_SGOV / 252) * sgov if caixa > 0 else caixa * (tb[t] + V.MARGEM_SPREAD / 252)
        j -= max(-v_spy, 0.0) * V.ALUGUEL_ETF_EUA / 252 * custo_mult
        pnl[t] = pm, ps, pp
        juros[t] = j
        E += pm + ps + pp + j
        if E <= 0:                             # quebrou: perdeu toda a conta (e mais)
            quebra = t
            break
        # ---- chamada de margem (manutenção)
        conta_margem = B[t] >= MIN_CONTA_MARGEM
        def exig(qq, vsh, vspy, ini):
            """Margem exigida (inicial ou manutenção). ETF comprado só exige margem se a conta estiver tomando emprestado."""
            emprestado = vsh + max(vspy, 0) + (qq if tipo == "etf" else 0) > E
            if tipo == "etf":
                vm = qq * (m_main_i if ini else m_main_m) * emprestado
            elif tipo == "fut":
                vm = abs(qq) * p_main[t] * (m_main_i if ini else m_main_m)
            else:
                vm = abs(qq) * (k_opt / 10 if veiculo in PERDA_MAX else nocional[t] * MARGEM_PUT)
            return vm + (.5 if ini else .25) * (vsh + max(vspy, 0)) * emprestado + (.5 if ini else .30) * max(-vspy, 0)
        if exig(q, v_sh, v_spy, False) > E:
            corte = max(E / max(exig(q, v_sh, v_spy, True), 1e-9), 0)
            q0, s0, y0 = q, v_sh, v_spy
            q = np.floor(q * corte) if tipo != "etf" else q * corte
            v_sh, v_spy = v_sh * corte, v_spy * corte
            c = _custo_troca(tipo, q - q0, p_main[t], s0 - v_sh, p_sh[t], y0 - v_spy, p_spy[t], veiculo) * custo_mult
            custo[t] += c
            E -= c
            chamadas.append(cal[t])
        # ---- rebalanceamento para o alvo
        alvo = W[t] * C_usd[t]
        q0, s0, y0 = q, v_sh, v_spy
        if tipo == "etf":
            if abs(alvo - q) > banda * max(abs(alvo), 1e-9) or (alvo == 0 and q != 0):
                q = alvo
            expo_v = q
        elif tipo == "fut":
            if conta_margem and np.isfinite(p_main[t]):
                q = float(np.round(alvo / p_main[t]))
            else:
                q = 0.0
            if rola[t] and q0 != 0:
                custo[t] += 2 * abs(q0) * CUSTO_VXM * custo_mult        # rolagem para o próximo vencimento
            expo_v = q * p_main[t] if np.isfinite(p_main[t]) else 0.0
        else:
            if rola[t]:
                k_opt = p_main[t]
                q = float(np.round(alvo / k_opt)) if conta_margem and np.isfinite(k_opt) else 0.0
                custo[t] += abs(q) * PERNAS[veiculo] * CUSTO_PERNA * custo_mult
            expo_v = q * k_opt
        # hedge de beta sobre a exposição de fato
        hz = beta[t] * expo_v                  # quanto de S&P vender
        if hedge == "sh" or hz < 0:
            alvo_sh, alvo_spy = max(hz, 0.0), max(-hz, 0.0)
        else:
            alvo_sh, alvo_spy = 0.0, (-np.round(hz / p_spy[t]) * p_spy[t]) if conta_margem else 0.0
        if abs(alvo_sh - v_sh) > banda * max(alvo_sh, 1e-9) or (alvo_sh == 0 and v_sh != 0):
            v_sh = alvo_sh
        if abs(alvo_spy - v_spy) > banda * max(abs(alvo_spy), 1e-9) or (alvo_spy == 0 and v_spy != 0):
            v_spy = alvo_spy
        # cabe na conta? (cash: só o caixa; margem: Reg T / margem de futuro)
        longos = (q if tipo == "etf" else 0.0) + v_sh + max(v_spy, 0.0)
        if not conta_margem and longos > E:
            s = E / longos
            q, v_sh, v_spy = (q * s if tipo == "etf" else q), v_sh * s, v_spy * s
        elif conta_margem and exig(q, v_sh, v_spy, True) > E:
            s = E / exig(q, v_sh, v_spy, True)
            q = q * s if tipo == "etf" else np.floor(abs(q) * s) * np.sign(q)
            v_sh, v_spy = v_sh * s, v_spy * s
        c = _custo_troca(tipo, q - q0, p_main[t], v_sh - s0, p_sh[t], v_spy - y0, p_spy[t], veiculo, opt_ja=True) * custo_mult
        custo[t] += c
        E -= c
        expo[t] = (q if tipo == "etf" else q * (p_main[t] if tipo == "fut" else k_opt)) / C_usd[t]
    idx = cal
    r_conta = pd.Series((pnl.sum(axis=1) + juros - custo) / np.maximum(B, 1e-9), index=idx)
    pnl = pd.DataFrame(pnl / C_usd[:, None], index=idx, columns=[veiculo, "SH", "SPY"])
    return {"r_conta": r_conta, "f": f, "pnl": pnl, "custo": pd.Series(custo / C_usd, index=idx), "expo": pd.Series(expo, index=idx),
            "chamadas": chamadas, "quebra": cal[quebra] if quebra is not None else None, "W": pd.Series(W, index=idx)}


def _ordem_ibkr(valor, preco):
    """IBKR Pro TIERED (melhor que o fixo de varejo.py para ordens pequenas): US$ 0,0035/ação, mínimo US$ 0,35, teto 1% da ordem,
    + ~US$ 0,0006/ação de bolsa/clearing/regulatório + slippage de varejo.py. (varejo.py usa o FIXO: mínimo US$ 1 por ordem.)"""
    valor = abs(valor)
    if valor == 0:
        return 0.0
    acoes = valor / max(preco, .01)
    return min(max(IBKR_TIER_ACAO * acoes, IBKR_TIER_MIN), .01 * valor) + .0006 * acoes + V.SLIPPAGE_ETF * valor


def _custo_troca(tipo, dq, pm, dsh, psh, dspy, pspy, veiculo, opt_ja=False):
    c = 0.0
    if tipo == "etf" and dq != 0:
        c += _ordem_ibkr(dq, pm)
    if tipo == "fut" and dq != 0:
        c += abs(dq) * CUSTO_VXM
    if tipo == "opt" and dq != 0 and not opt_ja:
        c += abs(dq) * PERNAS[veiculo] * CUSTO_PERNA          # fechar antes do vencimento (só na chamada de margem)
    if dsh != 0:
        c += _ordem_ibkr(dsh, psh)
    if dspy != 0:
        c += _ordem_ibkr(dspy, pspy)
    return c


# ---------------------------------------------------------------- contrato
def _excesso_e_sim(d, capital=CAPITAL, custo_mult=1, lag=0, regime=REGIME, alavancagem=1, **params):
    p = {**PARAMS, **params}
    reg_dentro = regime if regime in ("risco_global", "nenhum", None) else "nenhum"
    sim = _simula(d, p["veiculo"], p["teto"], p["hedge"], p["exterior"], p["banda"], capital, custo_mult, lag, reg_dentro, alavancagem)
    f, r = sim["f"], sim["r_conta"]
    e = f * V.excesso_brl_sem_hedge(r)
    if p["hedge_cambial"]:                      # WDO inteiros (US$ 10 mil cada) sobre o que está lá fora
        usd = f * capital / V.PTAX.reindex(comum.DIAS).ffill()
        h = (np.round(usd / WDO_USD) * WDO_USD / usd).clip(0, 1).fillna(0)
        e = e + f * h * (V.excesso_brl_com_hedge_teorico(r) - V.excesso_brl_sem_hedge(r)) \
            - np.round(usd / WDO_USD) * WDO_CUSTO_MES * 12 / 252 / capital * custo_mult
    e = e - f * REMESSA_IDA_VOLTA / (5 * 252) * custo_mult
    if sim["quebra"] is not None:              # quebrou: −100% no dia, depois fica no CDI (cota zerada)
        dq = comum.DIAS[comum.DIAS.searchsorted(sim["quebra"])]
        e.loc[dq] = -1 - comum.CDI.loc[dq]
        e.loc[e.index > dq] = 0.0
    if regime not in ("risco_global", "nenhum", None):
        e = comum.aplica_regime(e, regime, .001 * custo_mult)
    return e, sim


def excesso(d, capital=CAPITAL, custo_mult=1, lag=0, regime=REGIME, alavancagem=1, **params):
    return _excesso_e_sim(d, capital, custo_mult, lag, regime, alavancagem, **params)[0]


def relatorio_alavancagem(d, alavancagem=1, capital=CAPITAL, **params):
    e, sim = _excesso_e_sim(d, capital, alavancagem=alavancagem, **params)
    x = sim["expo"][sim["expo"].index >= pd.Timestamp(CORTE)]
    return {"chamadas de margem": len(sim["chamadas"]), "datas das chamadas": ", ".join(str(t.date()) for t in sim["chamadas"][:8]),
            "quebrou em": str(sim["quebra"].date()) if sim["quebra"] is not None else "-",
            "exposição média ao veículo OOS (% capital)": float(x[x != 0].mean() * 100) if (x != 0).any() else 0.0,
            "% dias com posição OOS": float((x != 0).mean() * 100), "fração remetida": sim["f"]}


def posicoes(d, **params):
    """W: peso-alvo do veículo (fração do capital, antes de arredondar); R: excesso diário do veículo com hedge de beta (US$)."""
    p = {**PARAMS, **params}
    S = _series(d, p["veiculo"])
    W, beta, Rh = _alvos(S, p["teto"], 1, REGIME, 0)
    return W.to_frame(p["veiculo"]), Rh.to_frame(p["veiculo"])


def negocios(d, capital=CAPITAL, **params):
    """Um negócio por mês: veículo (vendido em vol), hedge (SH/SPY) e câmbio+caixa+custos (o resto do excesso em R$)."""
    p = {**PARAMS, **params}
    e, sim = _excesso_e_sim(d, capital, **params)
    m = sim["pnl"].copy()
    m["hedge S&P"] = m.pop("SH") + m.pop("SPY")
    m = m.groupby(m.index.to_period("M")).sum()
    em = e.groupby(e.index.to_period("M")).sum()
    m["câmbio+caixa+custos"] = em.reindex(m.index).fillna(0) - m.sum(axis=1)
    x = sim["expo"].groupby(sim["expo"].index.to_period("M")).mean()
    lin = []
    for per, row in m.iterrows():
        for a, v in row.items():
            if v != 0:
                lin.append({"ativo": a, "lado": -1 if a == p["veiculo"] else 1, "entrada": per.start_time, "saida": per.end_time.normalize(),
                            "dias": 21, "retorno_%": v / max(x.get(per, 0), 1e-9) * 100 if a == p["veiculo"] and x.get(per, 0) > 0 else np.nan,
                            "contrib_pp": v * 100})
    return pd.DataFrame(lin)
