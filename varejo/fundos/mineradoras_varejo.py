"""
Mineradoras vs metal — versão pessoa física (IBKR com R$ 20 mil; B3 para contas pequenas).

Mesmo sinal do institucional (fundos/mineradoras.py: resíduo "mineradora - beta x metal", z semanal, entrada |z| > z_in, saída na média,
stop |z| > 4, prazo 120 dias). O que muda é a EXECUÇÃO, feita ação por ação:
  - IBKR Pro fixo: US$ 0,005/ação, mínimo US$ 1, máximo 1% da ordem (varejo.custo_ordem_usd) + meio spread por perna;
  - tamanho do par fixado na ENTRADA (o institucional rebalanceia todo dia ao beta/vol do dia; no varejo isso seria uma ordem de US$ 1
    por perna por dia). A ponta vendida é arredondada para AÇÕES INTEIRAS e define o tamanho; a comprada (fracionária) acompanha o beta.
    Se a ponta vendida arredonda para zero ação, o par não é aberto;
  - aluguel da ponta vendida (IBKR não repassa rebate a conta < US$ 100 mil); o dinheiro da venda a descoberto NÃO rende;
  - caixa livre só rende via ETF de T-bill (SGOV), reajustado uma vez por mês (1 ordem/mês); conta < US$ 10 mil não recebe juros;
  - Reg T: só vende a descoberto com patrimônio >= US$ 2.000; margem inicial 50% (bruto comprado + vendido, inclusive SGOV, <= 2x o
    patrimônio); manutenção IBKR 25% do comprado + 30% do vendido -> abaixo disso a IBKR liquida (chamada de margem, reduz tudo no fechamento);
  - patrimônio nominal constante = capital em R$ (em US$ = capital / PTAX); câmbio SEM hedge (o capital inteiro fica em dólar) e remessa
    (varejo.remessa_diaria). Hedge cambial não cabe: 1 WDO = US$ 10 mil > conta inteira (US$ ~4 mil); a variante com_hedge=True é teórica.

Quantos pares cabem: parâmetro n_pares (6, 3 ou 2), cada um com vol-alvo 10%/sqrt(n). Os pares mantidos são os n primeiros de ORDEM_IS,
ordenados pelo IR de cada par no institucional SÓ dentro da amostra (2012-2020; função ordem_is). Fixado como constante para o teste de
truncamento não depender dela (ela não usa nada depois do CORTE).

B3 (mercado="b3"; é o que roda em contas pequenas, mercado="auto" com capital < LIMIAR_IBKR): só 2 pares têm os dois lados na B3 e
só num sentido cada (BDR não-patrocinado/BDR de ETF praticamente não tem aluguel para PF):
  - GDX x GLD  = compra GDXB39 (BDR do GDX, 1 BDR ~ 1/3 GDX) e vende GOLD11 (ETF de ouro em R$, aluguel ~1,3% a.a. no BTC) — só o lado +1;
  - VALE x BHP/RIO = vende VALE3 (aluguel barato) e compra RIOT34 (BDR da Rio, R$ ~0,4 mi/dia) — só o lado -1 (BDR da BHP sem histórico).
  Preços: BDR "sintético" = preço EUA x PTAX x razão do BDR (GOLD11/VALE3/RIOT34 batem com o sintético; ver varejo/dados/mineradoras/b3.csv).
  Sem remessa e sem câmbio no capital; a garantia fica em Tesouro Selic (rende CDI), mas o dinheiro gasto na ponta comprada não rende
  e o da venda a descoberto também não. Corretagem zero (Clear/Rico/Inter), emolumentos 0,03% + meio spread.

Alavancagem: multiplica o tamanho de todos os pares; limitada pela Reg T (bruto <= 2x patrimônio, com a ponta vendida consumindo margem).
Micro futuros de metal (MGC 10 oz ~ US$ 41 mil; SIL micro prata 1.000 oz ~ US$ 50 mil; MHG 2.500 lb ~ US$ 12 mil) têm nocional de
3 a 10x a conta inteira e de 5 a 30x a perna de metal de um par -> não cabem em contratos inteiros (ver MOTIVO_ALAV).

Validação: excesso(d, capital=1e9, inst=True) (custos e financiamento do institucional, rebalanceio diário, sem lotes) dá OOS +10,9 pp
vs +11,7 pp do institucional, correlação diária 0,94 (diferença: custo cobrado por perna e não por par, aluguel só na perna vendida).

Premissas verificadas (out/2026): IBKR só paga juros sobre caixa e sobre recursos de venda a descoberto a contas com NAV > US$ 100 mil
(proporcional abaixo disso, e nada nos primeiros US$ 10 mil) — interactivebrokers.com/en/pricing/short-sale-cost.php e
Attachment-F (Interest Schedule); Reg T US$ 2.000 mínimo para vender a descoberto e 150% de depósito inicial no short (IBKR Campus);
IOF da remessa para investimento em conta própria no exterior 1,1% em 2026 (Decreto 12.499/2025). varejo.REMESSA_IDA_VOLTA cobra 1,1%
também na volta; o ingresso costuma pagar 0,38% — mantido 1,1% (conservador).
"""
import numpy as np
import pandas as pd

import comum
import varejo as V
from fundos import mineradoras as M

NOME = "Mineradoras vs metal (varejo IBKR/B3)"
TESE = "Mesmo valor relativo mineradora x metal, com ações inteiras na ponta vendida, comissão mínima, aluguel, Reg T e câmbio sem hedge"
BENCHMARK = "CDI"
INICIO, CORTE = M.INICIO, M.CORTE
REGIME = "nenhum"
CUSTO_TROCA = M.CUSTO_TROCA
CAPITAL = V.CAPITAL
PARAMS = {"jan": 63, "z_in": 1.0, "n_pares": 2}           # n_pares=2 escolhido no IS (2012-2020) entre 6/3/2 com R$ 20 mil
GRADE = {"jan": [63, 126], "z_in": [1.0, 2.0], "n_pares": [6, 3, 2]}
VIZINHANCA = {"jan": (45, 90), "z_in": (.75, 1.5)}            # n_pares fica fixo no leque

ORDEM_IS = ["SIL x SLV", "VALE x BHP/RIO", "GDX x GLD", "COPX x CPER", "FCX x CPER", "GDXJ x GDX"]   # IR por par 2012-2020 (ordem_is)
LIMIAR_IBKR = 15_000.0          # R$: abaixo disso "auto" usa a B3 (US$ 2 mil da Reg T + folga para o real se valorizar)

ALAVANCAGENS = [1, 1.5, 2]
MOTIVO_ALAV = ("5x não é viável: Reg T limita o bruto (comprado + vendido) a 2x o patrimônio overnight e a 1x já usa ~1,1-1,7x de bruto "
               "(a ponta vendida consome margem); portfolio margin exige US$ 110 mil; micro futuros de metal (MGC 10 oz ~US$ 41 mil, "
               "micro prata 1.000 oz ~US$ 50 mil, MHG 2.500 lb ~US$ 12 mil de nocional) são 3-12x a conta inteira de US$ ~4 mil e 5-30x a "
               "perna de metal de um par, logo não cabem em contratos inteiros. 1,5x e 2x rodam, mas o teto de 2x de bruto corta "
               "(alavancagem efetiva ~1,1-1,3x da 1x).")

APLICAVEL = True
MOTIVO = ("Operável: com R$ 20 mil (~US$ 4 mil) a IBKR deixa vender a descoberto (Reg T >= US$ 2 mil) e os pares cabem em ações "
          "inteiras; com R$ 4 mil (< US$ 2 mil) só a B3 (2 pares, um sentido cada). Mas não paga: comissão mínima, venda sem juros e "
          "câmbio sem hedge levam o excesso OOS para negativo.")
INSTRUMENTOS = ("IBKR Pro (EUA): pares GDX/GLD, GDXJ/GDX, SIL/SLV, COPX/CPER, FCX/CPER, VALE/(BHP+RIO); compra fracionária, venda a "
                "descoberto em ações inteiras (1 ação: GLD ~US$ 380, SLV ~US$ 50, CPER ~US$ 40, GDX ~US$ 85, RIO ~US$ 91); conta margem "
                ">= US$ 2 mil; margem Reg T 50% inicial, 25%/30% manutenção; caixa em SGOV. B3 (Clear/Rico/XP, conta pequena): GDXB39 "
                "comprado x GOLD11 vendido (BTC) e VALE3 vendido (BTC) x RIOT34 comprado, garantia em Tesouro Selic.")

# ---------------------------------------------------------------- premissas próprias do fundo
SLIP = {"SIL": .001, "COPX": .001, "CPER": .001, "GDXJ": .0007}          # meio spread por perna (demais: varejo.SLIPPAGE_ETF)
ALUGUEL = {"CPER": .02, "COPX": .01, "SIL": .01, "GDXJ": .0075}          # a.a. (demais: varejo.ALUGUEL_ETF_EUA = 0,5%)
REG_T_MIN_USD, BRUTO_MAX, MANUT_LONG, MANUT_SHORT = 2_000.0, 2.0, .25, .30
B3_VENDA_RENDE = .95                       # B3: dinheiro da venda a descoberto comprado em Tesouro Selic/LFTS11 e dado em garantia
SGOV_COLCHAO = .10                                                       # deixa 10% do PL em dinheiro (não rende)
# B3: ticker EUA -> (ticker B3, ativos EUA por papel, meio spread, aluguel a.a. se vendido)
B3 = {"GDX": ("GDXB39", 1 / 3, .003, None), "GLD": ("GOLD11", .0113, .001, .02),
      "VALE": ("VALE3", 1.0, .0005, .01), "RIO": ("RIOT34", 1.0, .003, None)}
PARES_B3 = {"GDX x GLD": ("GDX", ["GLD"], +1), "VALE x BHP/RIO": ("VALE", ["RIO"], -1)}   # sentido permitido do par


def carrega():
    d = M.carrega()
    d["brutos"] = pd.read_csv(comum.DADOS.parent / "varejo" / "dados" / "mineradoras" / "precos_brutos.csv", index_col=0, parse_dates=True)
    d["ptax"] = comum.PTAX
    return d


# ---------------------------------------------------------------- sinal (o mesmo do institucional, com beta exposto)
def _base(d):
    P = M._limpa_niveis(d["precos"].apply(M._no_calendario))
    tb = M._no_calendario(d["tb"]).fillna(0)
    Rt = P.apply(lambda s: M._limpa(s.pct_change(fill_method=None)))            # retorno total de cada papel (US$)
    ex = Rt.sub(tb, axis=0)
    res, beta = {}, {}
    for k, (a, hs) in M.PARES.items():
        rh = sum(ex[h] for h in hs) / len(hs)
        beta[k] = M._beta(ex[a], rh)
        res[k] = ex[a] - beta[k] * rh
    R = pd.DataFrame(res).reindex(comum.DIAS)
    R = R.where(R.notna().cumsum() > 0)
    bruto = d["brutos"].apply(M._no_calendario).reindex(columns=P.columns)
    adj = d["precos"].apply(M._no_calendario)
    Pc = P * (bruto / adj).ffill()                                             # preço "de tela" (sem ajuste de dividendo) para contar ações
    return P, Rt, R, pd.DataFrame(beta).reindex(comum.DIAS), Pc, tb


def _sinais(d, jan, z_in, n_pares):
    P, Rt, R, B, Pc, tb = _base(d)
    pares = [k for k in ORDEM_IS[:n_pares]]
    S, Mo = M._histerese(M._semanal(M._zscore(R[pares], jan)), z_in)
    v = R[pares].rolling(63, min_periods=40).std().shift(1) * np.sqrt(252)
    W = (S * (M.ALVO / np.sqrt(len(pares))) / v).replace([np.inf, -np.inf], 0).fillna(0).clip(-2, 2).where(S != 0, 0)
    return W, R[pares], Mo, B[pares], P, Rt, Pc, tb


def ordem_is(d):
    """Ordena os pares pelo IR de cada um no institucional, só com dados antes do CORTE (reproduz ORDEM_IS)."""
    d = {k: (v[v.index < CORTE] if isinstance(v, (pd.Series, pd.DataFrame)) else v) for k, v in d.items()}
    W, R, _ = M._sinais(d, M.PARAMS["jan"], M.PARAMS["z_in"])
    _, Cc, _ = M._contrib(W, R)
    Cc = Cc[Cc.index >= INICIO]
    return list((Cc.mean() / Cc.std()).sort_values(ascending=False).index)


# ---------------------------------------------------------------- motor ação por ação
def _motor(d, jan, z_in, n_pares, lag, custo_mult, capital, alavancagem, mercado, inst=False):
    W, R, Mo, B, P, Rt, Pc, tb = _sinais(d, jan, z_in, n_pares)
    idx, T = W.index, len(W)
    fx = d["ptax"].reindex(idx).ffill()
    b3 = mercado == "b3"
    pares = list(W.columns)
    if b3:                                                                     # B3: sempre os 2 pares possíveis (n_pares não se aplica)
        pares = list(PARES_B3)
        W, R, Mo, B = _sinais(d, jan, z_in, 6)[:4]
        W = W[pares] * np.sqrt(6) / np.sqrt(len(pares))                       # vol-alvo redistribuída entre os pares da B3
        pernas = {k: (PARES_B3[k][0], PARES_B3[k][1]) for k in pares}
        tks = sorted({t for a, hs in pernas.values() for t in [a, *hs]})
        raz = pd.Series({t: B3[t][1] for t in tks})
        Pv = P[tks].mul(fx, axis=0) * raz                                      # valor (ajustado) em R$ por papel B3
        Pk = Pc[tks].mul(fx, axis=0) * raz                                     # preço de tela em R$
        nav = pd.Series(capital, index=idx)
    else:
        pernas = {k: M.PARES[k] for k in pares}
        tks = sorted({t for a, hs in pernas.values() for t in [a, *hs]})
        Pv, Pk = P[tks], Pc[tks]
        nav = capital / fx
    Pv, Pk = Pv.ffill().values, Pk.ffill().values
    col = {t: i for i, t in enumerate(tks)}
    Wv, Bv, navv = W[pares].values, B[pares].fillna(1.0).values, nav.values
    slip = np.array([B3[t][2] + V.B3_EMOLUMENTOS if b3 else SLIP.get(t, V.SLIPPAGE_ETF) for t in tks])
    alug = np.array([(B3[t][3] or .05) if b3 else ALUGUEL.get(t, V.ALUGUEL_ETF_EUA) for t in tks])
    if inst:                                                                    # validação: custos/financiamento do institucional
        slip[:] = M.CUSTO["GDX x GLD"] / 2
        alug[:] = M.ALUG_VENDA

    def custo(dn, i):                                                          # custo de negociar dn papéis (vetor por ticker) no fechamento i
        val = np.abs(dn) * np.nan_to_num(Pv[i])
        spr = (val * slip).sum() * custo_mult
        com = 0.0 if (b3 or inst) else (np.where(val > 0, V.custo_ordem_usd(val, np.nan_to_num(Pk[i], nan=1.0)) - V.SLIPPAGE_ETF * val, 0)).sum() * custo_mult
        partes[i, 1] += com                                                    # comissão IBKR (mínimo US$ 1)
        partes[i, 2] += spr
        return com + spr

    n = np.zeros((len(pares), len(tks)))           # papéis por par (em "unidades ajustadas"; valor = n * Pv)
    lado = np.zeros(len(pares))
    acum = np.zeros(len(pares))                    # resultado do par desde a entrada (para a margem)
    contrib = np.zeros((T, len(pares)))
    expo = np.zeros(T)                             # exposição bruta (comprado + vendido) / PL, depois das ordens
    partes = np.zeros((T, 5))                      # bruto, comissão, spread, aluguel, financiamento/caixa (em fração do PL)
    r = np.zeros(T)
    sgov, chamadas, quebra = 0.0, [], None
    tbv = tb.reindex(idx).fillna(0).values
    cdi = comum.CDI.reindex(idx).fillna(0).values
    mes = idx.to_period("M")
    for i in range(1, T):
        if quebra is not None:
            break
        dP = np.nan_to_num(Pv[i] - Pv[i - 1])
        pv0 = np.nan_to_num(Pv[i - 1])
        alug_par = (np.clip(-n, 0, None) * pv0 * alug).sum(axis=1) / 252 * (custo_mult if not inst else 1)
        pnl_par = n @ dP - alug_par
        partes[i, 0], partes[i, 3] = (n @ dP).sum(), -alug_par.sum()
        longs = (np.clip(n, 0, None) @ pv0).sum()
        shorts = (np.clip(-n, 0, None) @ pv0).sum()
        nv = navv[i - 1]
        if b3:
            fin = -(longs - shorts * B3_VENDA_RENDE) * cdi[i]                  # comprado sai do Tesouro Selic; venda vira LFT/garantia
        elif inst:
            fin = -(longs - shorts) * tbv[i]                                   # institucional: tudo financiado/remunerado a T-bill
        else:
            fin = sgov * nv * (tbv[i] - V.TAXA_SGOV / 252) - max(longs + sgov * nv - nv - shorts, 0) * (tbv[i] + V.MARGEM_SPREAD / 252)
        custo_dia = 0.0
        acum += pnl_par
        # -------- chamada de margem / quebra (fechamento de i, antes das ordens novas)
        Lc, Sc = (np.clip(n, 0, None) @ np.nan_to_num(Pv[i])).sum(), (np.clip(-n, 0, None) @ np.nan_to_num(Pv[i])).sum()
        eq = nv + acum.sum()
        manut = MANUT_LONG * Lc + MANUT_SHORT * Sc
        if not inst and eq <= 0 and (Lc + Sc) > 0:
            quebra = idx[i]
            r[i] = -1.0
            break
        if not inst and manut > 0 and eq < manut:
            f = max(eq / manut, 0) * .9                                        # IBKR reduz para voltar com folga acima da manutenção
            novo = np.where(n < 0, -np.floor(-n * f), n * f)
            custo_dia += custo(novo - n, i)
            n = novo
            chamadas.append(idx[i])
        # -------- ordens decididas em j = i-1-lag
        j = i - 1 - lag
        alvo_lado = np.sign(Wv[j]) if j >= 0 else np.zeros(len(pares))
        novo = n.copy()
        for k, par in enumerate(pares):
            a, hs = pernas[par]
            s = alvo_lado[k]
            if b3 and s != PARES_B3[par][2]:
                s = 0
            if inst and s != 0:                                                # validação: rebalanceia todo dia ao alvo
                lado[k] = 0
            if s == lado[k]:
                continue
            novo[k] = 0
            lado[k], acum[k] = 0, 0.0
            if s == 0 or j < 0:
                continue
            # entrada: nocional da mineradora e do metal com informação de j
            na = abs(Wv[j, k]) * alavancagem * navv[j]
            nh = Bv[j, k] * na / len(hs)
            liv = BRUTO_MAX * navv[j] - (np.abs(novo) @ np.nan_to_num(Pv[j])).sum()     # SGOV é vendido se precisar
            if not inst and na + nh * len(hs) > liv:
                f = max(liv, 0) / (na + nh * len(hs))
                na, nh = na * f, nh * f
            if b3:                                                             # B3: compra só com o dinheiro que há
                cx = navv[j] - (np.clip(novo, 0, None) @ np.nan_to_num(Pv[j])).sum()
                comp = na if s > 0 else nh * len(hs)
                if comp > cx and comp > 0:
                    na, nh = na * max(cx, 0) / comp, nh * max(cx, 0) / comp
            pa, ph = Pk[j, col[a]], np.array([Pk[j, col[h]] for h in hs])
            if not np.isfinite(pa) or not np.all(np.isfinite(ph)) or na <= 0:
                continue
            if inst:
                qa, qh = na / pa, nh / ph
            elif s > 0:                                                        # vende o metal: ações inteiras definem o tamanho
                qh = np.round(nh / ph)
                if (qh == 0).any():
                    continue
                qa = (qh * ph).sum() / max(Bv[j, k], 1e-6) / pa
                qa = np.floor(qa) if b3 else qa
            else:                                                              # vende a mineradora
                qa = np.round(na / pa)
                if qa == 0:
                    continue
                qh = Bv[j, k] * qa * pa / len(hs) / ph
                qh = np.floor(qh) if b3 else qh
            if not inst and (navv[j] < REG_T_MIN_USD and not b3):              # Reg T: sem US$ 2 mil não vende a descoberto
                continue
            conv = lambda q, t: q * Pk[j, col[t]] / Pv[j, col[t]]              # papéis de tela -> unidades ajustadas
            novo[k, col[a]] = s * conv(qa, a)
            for h, q in zip(hs, qh):
                novo[k, col[h]] -= s * conv(q, h)
            lado[k] = s
        dn = novo - n
        if np.abs(dn).sum() > 0:
            por_par = np.array([custo(dn[k], i) for k in range(len(pares))])
            contrib[i] -= por_par
            custo_dia += por_par.sum()
        n = novo
        expo[i] = (np.abs(n) @ np.nan_to_num(Pv[i])).sum() / navv[i]
        # -------- SGOV: reajuste mensal (1 ordem) para o caixa livre; vendido na hora se a Reg T ou o caixa pedirem
        if not (b3 or inst):
            Li = (np.clip(n, 0, None) @ np.nan_to_num(Pv[i])).sum() / navv[i]
            Gi = (np.abs(n) @ np.nan_to_num(Pv[i])).sum() / navv[i]
            teto = max(0.0, min(1 - SGOV_COLCHAO - Li, BRUTO_MAX - Gi))
            alvo = teto if mes[i] != mes[i - 1] else (max(teto - .05, 0.0) if sgov > teto + .05 else sgov)
            if abs(alvo - sgov) > .02:
                partes[i, 1] += V.IBKR_MIN * custo_mult
                partes[i, 2] += abs(alvo - sgov) * navv[i] * V.SLIPPAGE_ETF * custo_mult
                custo_dia += (V.IBKR_MIN + abs(alvo - sgov) * navv[i] * V.SLIPPAGE_ETF) * custo_mult
                sgov = alvo
        contrib[i] += pnl_par
        r[i] = (pnl_par.sum() + fin - custo_dia) / nv
        partes[i, 1:3] *= -1
        partes[i, 4] = fin
        partes[i] /= nv
        contrib[i] /= nv
    r = pd.Series(r, index=idx)
    partes = pd.DataFrame(partes, index=idx, columns=["bruto", "comissao", "spread", "aluguel", "caixa_financiamento"]).assign(exposicao=expo)
    return r, pd.DataFrame(contrib, index=idx, columns=pares), chamadas, quebra, partes


def _mercado(capital, mercado):
    return mercado if mercado != "auto" else ("ibkr" if capital >= LIMIAR_IBKR else "b3")


# ---------------------------------------------------------------- contrato
def excesso(d, custo_mult=1, lag=0, regime=REGIME, jan=PARAMS["jan"], z_in=PARAMS["z_in"], n_pares=PARAMS["n_pares"],
            capital=CAPITAL, alavancagem=1.0, mercado="auto", com_hedge=False, inst=False, info=None):
    """Excesso diário sobre o CDI em R$ (antes do IR). mercado: "auto" (IBKR se capital >= LIMIAR_IBKR, senão B3), "ibkr" ou "b3".
    inst=True: validação (custos/financiamento do institucional, rebalanceio diário, sem lotes) — deve reproduzir fundos/mineradoras.py.
    info: dict opcional que recebe chamadas de margem, quebra e contribuições por par."""
    mk = _mercado(capital, mercado)
    r, Cp, ch, qb, pt = _motor(d, jan, z_in, n_pares, lag, custo_mult, capital, alavancagem, mk, inst)
    if info is not None:
        info.update(chamadas=ch, quebra=qb, contrib=Cp, mercado=mk, partes=pt, r_moeda=r)
    if inst:
        e = r.copy()                                                           # já é excesso sobre o T-bill com hedge = excesso sobre o CDI
    elif mk == "b3":
        e = r                                                                  # capital em R$, garantia em Tesouro Selic: já é excesso sobre o CDI
    else:
        e = (V.excesso_brl_com_hedge_teorico(r) if com_hedge else V.excesso_brl_sem_hedge(r)) - V.remessa_diaria() * custo_mult
    if qb is not None:                                                         # quebrou: -100% no dia e nada depois
        e = e.where(e.index <= qb, -comum.CDI.reindex(e.index).fillna(0))
        e.loc[qb] = -1.0
    return comum.aplica_regime(e.reindex(comum.DIAS).fillna(0), regime, CUSTO_TROCA * custo_mult)


def posicoes(d, jan=PARAMS["jan"], z_in=PARAMS["z_in"], n_pares=PARAMS["n_pares"]):
    W, R = _sinais(d, jan, z_in, n_pares)[:2]
    return W, R


def negocios(d, jan=PARAMS["jan"], z_in=PARAMS["z_in"], n_pares=PARAMS["n_pares"], lag=0, capital=CAPITAL, mercado="auto"):
    info = {}
    excesso(d, lag=lag, jan=jan, z_in=z_in, n_pares=n_pares, capital=capital, mercado=mercado, info=info)
    W, R, Mo = _sinais(d, jan, z_in, 6)[:3]                                   # superconjunto (vale para IBKR e B3)
    Cp = info["contrib"]
    lin = []
    for c in Cp.columns:
        ativo = Cp[c].values != 0
        s = np.sign(W[c].shift(1 + lag).fillna(0).values) * ativo
        mud = np.flatnonzero(np.diff(np.r_[0, s]) != 0)
        for k, i0 in enumerate(mud):
            if s[i0] == 0:
                continue
            i1 = mud[k + 1] if k + 1 < len(mud) else len(s)
            seg = slice(i0, min(i1 + 1, len(s)))
            dec = max(i1 - 1 - lag, 0)
            lin.append({"ativo": c, "lado": int(s[i0]), "entrada": Cp.index[i0], "saida": Cp.index[min(i1, len(s) - 1)], "dias": i1 - i0,
                        "retorno_%": (np.prod(1 + s[i0] * R[c].fillna(0).values[i0 + 1:min(i1 + 1, len(s))]) - 1) * 100,
                        "contrib_pp": Cp[c].values[seg].sum() * 100,
                        "motivo": "em aberto" if i1 >= len(s) else (Mo[c].iat[dec] if c in Mo else "") or "sem vol"})
    return pd.DataFrame(lin)
