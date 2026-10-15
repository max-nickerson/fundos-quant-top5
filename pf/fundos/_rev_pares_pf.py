"""
Motor de PARES para pessoa física (usado por rev_mineradoras e rev_petroleo). Não altera comum/robustez/pf/_util.

Ideia: o SINAL vem da pesquisa institucional (peso |W| da perna A, beta da perna H, lado +1/-1, decididos em t). A EXECUÇÃO é de varejo:
  - o tamanho do par é fixado na ENTRADA (sem rebalanceio diário: no varejo isso seria uma ordem de centavos por dia) e mantido até a saída;
  - cada perna num instrumento real, com quantidade INTEIRA quando o mercado exige:
      "b3"   ação na B3 (fracionário, 1 ação): comprada = dinheiro sai do CDI (CDI perdido); vendida = aluguel BTC de PF
             (taxa da corretora por contrato + taxa ao doador a.a.), o dinheiro da venda vai para Tesouro Selic (rende CDI, classe renda fixa);
      "ibkr" ação/ETF na IBKR em US$: comprada com fração (dinheiro na IBKR = 100% do valor, perde CDI, fica em dólar);
             vendida em ações inteiras (Reg T: 150% depositado, 100% vem da própria venda -> 50% do valor é patrimônio nosso; venda não
             rende juros em conta pequena; aluguel a.a. do arquivo público de short da IBKR; Reg T exige US$ 2.000 de patrimônio para vender);
      "fut"  futuro CME em contratos INTEIROS: só a margem fica na IBKR. Retorno = excesso do metal/petróleo sobre o T-bill (ETF físico ou
             de futuros como proxy: futuro ~ spot - juro dos EUA), aplicado sobre o NÍVEL do contrato (Yahoo contínuo só para contar contratos,
             nunca para retorno: o salto da rolagem não entra). Rolagem paga 2 x custo por lado a cada vencimento usado.
  - "auto" para a perna de hedge: futuro se arredondar para >= 1 contrato, senão o ETF/ação na IBKR (rota alternativa da mesma perna).
  - se uma perna inteira arredondar para zero, o par não abre (fica registrado como "não coube").
  - caixa total limitado ao capital: dinheiro na IBKR (margem + Reg T) + ações compradas na B3 <= capital (senão o par não abre).
Conta na IBKR: pf.custo_conta_exterior(exigido) — saldo = 1,5 x o maior exigido do mês anterior; perde CDI, ganha/perde câmbio, paga
IOF + spread nas remessas. custo_mult multiplica corretagem, spread, emolumentos, aluguel, rolagem e remessa (o CDI perdido e o câmbio não são custo).

Classes de IR: "exterior" (IBKR: ações, futuros, câmbio do saldo, remessa), "acoes_isentas"/"acoes" (B3, via U.acoes_ir), "renda_fixa"
(CDI do dinheiro da venda a descoberto na B3), "_cdi_perdido" (CDI que o dinheiro aplicado fora do CDI deixou de render).
Por construção: excesso = (soma das classes - _cdi_perdido) / capital.
"""
import numpy as np
import pandas as pd

import _util as U

C, pf = U.C, U.pf
DIAS = C.DIAS

# ---------------------------------------------------------------- premissas de execução (fontes no módulo de cada fundo)
REG_T_MIN_USD = 2_000.0          # IBKR: patrimônio mínimo para conta margem / vender a descoberto
REG_T_SHORT = .5                 # Reg T: 50% de margem inicial sobre comprado e vendido (150% do vendido depositado, 100% vem da venda)


def patrimonio_ibkr(L, S, financia="caixa"):
    """Dinheiro nosso na IBKR para L comprado e S vendido (R$), sem tomar empréstimo de margem: Reg T exige 50% de (L + S) e o caixa
    (depósito - L + S) não pode ficar negativo (senão paga juros de margem) -> max(0,5(L+S), L - S). Ex.: par L = S -> 100% de um lado;
    só comprado -> 100%; só vendido -> 50%."""
    if financia == "margem":                 # toma empréstimo de margem: só os 50% da Reg T (o resto é dívida a T-bill + 1,5%)
        return REG_T_SHORT * (L + S)
    return np.maximum(REG_T_SHORT * (L + S), L - S)


def divida_ibkr(L, S, financia="caixa"):
    """Empréstimo de margem (R$) quando financia='margem': caixa = 0,5(L+S) - L + S < 0 -> dívida."""
    return np.maximum(.5 * L - 1.5 * S, 0) if financia == "margem" else 0 * L
FOLGA_FUT, FOLGA_CONTA = 1.5, 1.05   # folga sobre a margem de futuros / sobre o exigido do mês anterior (pf.custo_conta_exterior)
WDO_USD, WDO_CUSTO = 10_000.0, 3.70  # mini-dólar: US$ 10 mil; R$ 1,20 de emolumentos + meio tick (0,5 pt = R$ 5) por lado; rola todo mês
SPREAD_CUPOM = .0107                 # antes de 2019 (sem FRC): cupom = T-bill + 1,07 pp (fundos/carry_moedas.py)
JUROS_MARGEM = .015                  # IBKR Pro: benchmark + 1,5% a.a. abaixo de US$ 100 mil (interactivebrokers.com/en/trading/margin-rates.php)
TETO_CAIXA = .95                 # dinheiro fora do CDI (IBKR + ações B3 compradas) <= 95% do capital


def no_calendario(s, lim=5):
    """Série dos EUA no calendário da B3 (último fechamento disponível, até 5 dias)."""
    s = s[~s.index.duplicated(keep="last")]
    return s.reindex(DIAS.union(s.index)).ffill(limit=lim).reindex(DIAS)


def motor(S, Wabs, B, pernas, inst, capital=20_000, alavancagem=1.0, lag=0, custo_mult=1.0, validacao=False, hedge_fx="nenhum", cupom=None,
          financia="caixa"):
    """S, Wabs, B: DataFrames (DIAS x pares) decididos em t: lado (+1 compra A/vende H), |peso| de A (fração do capital), beta de H.
    pernas: {par: [("A", tk, rota), ("H", tk_ou_rotas, frac)]}; rota "b3"/"ibkr"/"fut:<contrato>"/"auto:<contrato>|<tk_etf>".
    inst: {tk: dict(tipo, P (preço/retorno total, moeda local), cont=(nível p/ contar), rx=(excesso diário) p/ futuros, custos...)}.
    hedge_fx="wdo": vende mini-dólar (WDO, US$ 10 mil, B3) no valor do saldo em dólar na IBKR (arredondado; revisto quando o saldo muda)
    -> o dinheiro fora deixa de perder "CDI - variação do dólar" e passa a perder só "cupom cambial - T-bill"; cupom: % a.a. (1º FRC).
    validacao=True: institucional (quantidades fracionárias, sem custos, sem conta no exterior, ações financiadas a T-bill, sem teto de caixa).
    Devolve dict com séries diárias (R$) e o detalhe por par/negócio."""
    T = len(DIAS)
    fx = pf.PTAX.reindex(DIAS).ffill().bfill().values
    cdi = C.CDI.reindex(DIAS).fillna(0).values
    tb = no_calendario(C.TB_US).fillna(0).values
    pares = list(pernas)
    Sx = S.reindex(DIAS).fillna(0).values
    Wv = Wabs.reindex(DIAS).fillna(0).values
    Bv = B.reindex(DIAS).fillna(1.0).values

    # ---- pernas "abertas" possíveis (cada par tem A e um ou mais H; H "auto" vira futuro OU ETF na entrada)
    slots = []                                  # (par_idx, papel, tk, tipo, contrato, peso_h)
    for p, par in enumerate(pares):
        for papel, tk, extra in pernas[par]:
            if papel == "A":
                slots.append((p, "A", tk, inst[tk]["tipo"], None, 1.0))
            else:
                frac = extra
                for t in tk.split("|"):          # "MGC|GLD": candidatos em ordem de preferência
                    slots.append((p, "H", t, inst[t]["tipo"], t, frac))
    ns = len(slots)
    Q = np.zeros((T, ns))                       # quantidade (ações em unidades ajustadas / contratos) depois do fechamento de i
    custo = np.zeros((T, ns))                   # R$ de custo de negociação no dia
    abre = np.zeros((T, ns), bool)
    naocoube = []
    Pv = {}
    for s_, (_, _, tk, tipo, _, _) in enumerate(slots):
        x = inst[tk]
        Pv[s_] = (x["cont"] if tipo == "fut" else x["P"]).reindex(DIAS).ffill().values
    # eventos: dias de execução i em que o lado executado muda
    Sexe = np.vstack([np.zeros((1 + lag, len(pares))), Sx[:T - 1 - lag]]) if T > 1 + lag else np.zeros_like(Sx)
    lado = np.zeros(len(pares))
    q_atual = np.zeros(ns)
    mud = np.flatnonzero(np.any(np.diff(np.vstack([np.zeros((1, len(pares))), Sexe]), axis=0) != 0, axis=1))
    nego = []                                    # (par, lado, i_entrada, i_saida, rota)
    aberto = {}
    marcas = np.r_[mud, T]
    for e_, i in enumerate(marcas[:-1]):
        prox = marcas[e_ + 1]
        j = i - 1 - lag
        for p, par in enumerate(pares):
            s = Sexe[i, p]
            if s == lado[p]:
                continue
            idx_p = [k for k in range(ns) if slots[k][0] == p]
            if lado[p] != 0:                     # fecha
                ent = aberto.pop(p)
                nego.append((par, lado[p], ent[0], i, ent[1]))
                q_atual[idx_p] = 0
                lado[p] = 0
            if s == 0 or j < 0:
                continue
            # ---- abre: tamanho com informação de j
            na = Wv[j, p] * alavancagem * capital          # R$ na perna A
            beta = Bv[j, p]
            if not np.isfinite(na) or na <= 0:
                continue
            q_novo = np.zeros(ns)
            rota = []
            ok = True
            # perna(s) H primeiro (é a mais "granulada" quando é futuro): define a escala do par
            hs = [k for k in idx_p if slots[k][1] == "H"]
            escala = 1.0
            grupos = {}
            for k in hs:
                grupos.setdefault(slots[k][5], []).append(k)
            escolhidos = []
            for frac, ks in grupos.items():
                nh = beta * na * frac
                feito = False
                if not np.isfinite(nh) or nh <= 0:          # beta 0: sem hedge nessa perna (par fica só com A)
                    continue
                for k in ks:                                # candidatos em ordem: futuro inteiro, senão ETF
                    tk, tipo = slots[k][2], slots[k][3]
                    x = inst[tk]
                    preco = Pv[k][j]
                    if not np.isfinite(preco) or preco <= 0:
                        continue
                    if tipo == "fut":
                        noc1 = preco * x["mult"] * fx[j]
                        n = nh / noc1 if validacao else np.round(nh / noc1)
                        if n == 0 and x.get("so_se_couber", True) and not validacao:
                            continue
                        escolhidos.append((k, n, n * noc1 / nh))
                    else:
                        moeda = fx[j] if tipo == "ibkr" else 1.0
                        sh = nh / (preco * moeda)
                        if not validacao and (tipo == "b3" or s > 0):     # vendida (H com s>0) ou B3: ação inteira
                            sh = np.round(sh)
                            if sh == 0:
                                continue
                        escolhidos.append((k, sh, sh * preco * moeda / nh))
                    feito = True
                    break
                if not feito:
                    ok = False
            if not ok:
                naocoube.append((par, DIAS[i]))
                continue
            fut = [r for (k, n, r) in escolhidos if slots[k][3] == "fut"]
            escala = float(np.mean(fut)) if fut else 1.0  # o futuro inteiro manda no tamanho (A acompanha o hedge)
            for k, n, r in escolhidos:
                q_novo[k] = -s * n
                rota.append(slots[k][2])
            ka = [k for k in idx_p if slots[k][1] == "A"][0]
            tka, tipa = slots[ka][2], slots[ka][3]
            pa = Pv[ka][j]
            if not np.isfinite(pa) or pa <= 0:
                naocoube.append((par, DIAS[i]))
                continue
            moeda = fx[j] if tipa == "ibkr" else 1.0
            sha = na * escala / (pa * moeda)
            if not validacao and (tipa == "b3" or (tipa == "ibkr" and s < 0)):
                sha = np.round(sha)
                if sha == 0:
                    naocoube.append((par, DIAS[i]))
                    continue
            q_novo[ka] = s * sha
            # ---- teto de caixa (dinheiro fora do CDI) e Reg T mínimo
            if not validacao:
                q_tot = q_atual + q_novo
                need = _exigido_pontual(q_tot, slots, inst, Pv, j, fx[j], financia)
                if need > TETO_CAIXA * capital:
                    naocoube.append((par, DIAS[i]))
                    continue
            q_atual[idx_p] = q_novo[idx_p]
            lado[p] = s
            aberto[p] = (i, "+".join([tka] + rota))
        Q[i:prox] = q_atual
    for p, (i0, rota) in aberto.items():
        nego.append((pares[p], lado[p], i0, T - 1, rota))

    # ---------------------------------------------------------------- P&L diário por slot (vetorizado)
    Qp = np.vstack([np.zeros((1, ns)), Q[:-1]])           # posição carregada de i-1 para i
    dQ = np.diff(np.vstack([np.zeros((1, ns)), Q]), axis=0)
    pnl = np.zeros((T, ns))
    alug = np.zeros((T, ns))
    rf_b3 = np.zeros((T, ns))                              # CDI do dinheiro da venda na B3 (renda fixa)
    perd_b3 = np.zeros((T, ns))                            # CDI perdido do dinheiro das compras na B3
    roll = np.zeros((T, ns))
    vexp = np.zeros((T, ns))                               # valor (R$) exposto por slot no fechamento i (para margem/Reg T)
    vend_b3 = np.zeros(T)
    for k, (p, papel, tk, tipo, _, _) in enumerate(slots):
        x = inst[tk]
        P = Pv[k]
        P0 = np.r_[np.nan, P[:-1]]
        if tipo == "fut":
            rx = x["rx"].reindex(DIAS).fillna(0).values
            pnl[:, k] = Qp[:, k] * np.nan_to_num(P0) * x["mult"] * rx * fx
            vexp[:, k] = np.abs(Q[:, k]) * np.nan_to_num(P) * x["mult"] * fx
            c1 = x["custo"] * fx                            # US$ por contrato por lado
            custo[:, k] += np.abs(dQ[:, k]) * c1 * custo_mult
            roll[:, k] = np.abs(Qp[:, k]) * 2 * c1 * x["rolagens"] / 252 * custo_mult
        else:
            dP = np.nan_to_num(P - P0)
            moeda = fx if tipo == "ibkr" else 1.0
            pnl[:, k] = Qp[:, k] * dP * moeda
            val = np.abs(dQ[:, k]) * np.nan_to_num(P) * moeda
            vexp[:, k] = Q[:, k] * np.nan_to_num(P) * moeda             # com sinal
            if tipo == "ibkr":
                com = pf.custo_ordem_ibkr_usd(np.abs(dQ[:, k]) * np.nan_to_num(P), np.nan_to_num(P, nan=1.0)) * fx
                custo[:, k] += (com + val * x["spread"]) * custo_mult
                alug[:, k] = np.clip(-Qp[:, k], 0, None) * np.nan_to_num(P0) * moeda * x["aluguel"] / 252 * custo_mult
                if validacao:                                             # institucional: comprado financiado a T-bill, vendido rende T-bill
                    pnl[:, k] -= Qp[:, k] * np.nan_to_num(P0) * moeda * tb
            else:
                custo[:, k] += pf.custo_b3(val, x.get("liquidez", "liquida"), True) * custo_mult
                # aluguel BTC de PF: taxa da corretora por contrato aberto + taxa ao doador a.a.
                abre_v = (dQ[:, k] < 0) & (Q[:, k] < 0)
                custo[:, k] += np.where(abre_v, val * pf.ALUGUEL_PF_CORRETORA, 0) * custo_mult
                alug[:, k] = np.clip(-Qp[:, k], 0, None) * np.nan_to_num(P0) * x["aluguel"] / 252 * custo_mult
                v0 = Qp[:, k] * np.nan_to_num(P0)
                perd_b3[:, k] = np.clip(v0, 0, None) * cdi
                rf_b3[:, k] = np.clip(-v0, 0, None) * cdi
                # vendas no mês (para a isenção de R$ 20 mil): vender o que tinha comprado OU abrir venda a descoberto
                vend_b3 += np.where(dQ[:, k] < 0, val, 0)
    if validacao:
        custo[:], roll[:], alug[:] = 0, 0, 0

    # ---------------------------------------------------------------- conta na IBKR (só o necessário)
    tipos = np.array([s_[3] for s_ in slots])
    margem = np.array([inst[s_[2]].get("margem", 0) for s_ in slots])
    is_fut, is_ib = tipos == "fut", tipos == "ibkr"
    # exigido com folga própria: margem de futuro x1,5 (ajuste diário), ação comprada x1,0 (é o próprio ativo), venda Reg T x1,1
    Lib, Sib = np.clip(vexp[:, is_ib], 0, None).sum(axis=1), np.clip(-vexp[:, is_ib], 0, None).sum(axis=1)
    exig = FOLGA_FUT * (vexp[:, is_fut] * margem[is_fut]).sum(axis=1) + 1.05 * patrimonio_ibkr(Lib, Sib, financia)
    tem_short = (np.clip(-vexp[:, is_ib], 0, None).sum(axis=1) > 0)
    exig = np.where(tem_short, np.maximum(exig, REG_T_MIN_USD * fx), exig)
    exig = pd.Series(exig, index=DIAS)
    if validacao or exig.abs().sum() == 0:
        conta = pd.Series(0.0, index=DIAS)
        perd_ext = ganho = remessa = conta
        saldo = conta
    else:
        conta, saldo = pf.custo_conta_exterior(exig, folga=FOLGA_CONTA)
        perd_ext = saldo.shift(1).fillna(0) * C.CDI.reindex(DIAS).fillna(0)
        ganho = saldo.shift(1).fillna(0) * pf.PTAX.pct_change(fill_method=None).fillna(0)
        remessa = (conta - perd_ext + ganho) * custo_mult

    # ---------------------------------------------------------------- hedge cambial com WDO (opcional)
    wdo = pd.Series(0.0, index=DIAS)
    n_wdo = np.zeros(T)
    if hedge_fx == "wdo" and not validacao and saldo.abs().sum() > 0:
        usd = (saldo / pf.PTAX).values                                        # dólares na IBKR (decide em t, executa em t+1)
        alvo = np.floor(np.r_[0, 0, usd[:-2]] / WDO_USD + .2)                  # só arredonda para cima até 25% de sobre-hedge (1 WDO = US$ 10 mil)
        n_wdo = -np.maximum(alvo, 0)
        cup = (cupom.reindex(DIAS).ffill(limit=5) / 100 if cupom is not None else pd.Series(np.nan, index=DIAS))
        cup = cup.fillna(pd.Series(tb * 252, index=DIAS) + SPREAD_CUPOM).values
        nprev = np.r_[0, n_wdo[:-1]]
        f0 = np.r_[fx[0], fx[:-1]]
        pnl_w = nprev * WDO_USD * (fx - f0) - nprev * WDO_USD * f0 * (cdi - cup / 252)   # vendido: ganha CDI - cupom, perde a alta do dólar
        cw = (np.abs(np.diff(np.r_[0, n_wdo])) * WDO_CUSTO + np.abs(nprev) * 2 * WDO_CUSTO * 12 / 252) * custo_mult
        wdo = pd.Series(pnl_w - cw, index=DIAS)

    # ---------------------------------------------------------------- classes e excesso
    ext_sl = is_fut | is_ib
    Lp, Sp = np.r_[0, Lib[:-1]], np.r_[0, Sib[:-1]]
    juros_margem = divida_ibkr(Lp, Sp, financia) * (tb + JUROS_MARGEM / 252) * (not validacao)   # dívida de margem: T-bill + 1,5% a.a.
    bruto_ext = (pnl[:, ext_sl] - custo[:, ext_sl] - alug[:, ext_sl] - roll[:, ext_sl]).sum(axis=1) - juros_margem
    exterior = pd.Series(bruto_ext, index=DIAS) + ganho - remessa
    b3s = ~ext_sl
    acoes_pnl = pd.Series((pnl[:, b3s] - custo[:, b3s] - alug[:, b3s]).sum(axis=1), index=DIAS)
    renda_fixa = pd.Series(rf_b3.sum(axis=1), index=DIAS)
    cdi_perd = pd.Series(perd_b3.sum(axis=1), index=DIAS) + perd_ext
    classes = {"exterior": exterior, "futuros_b3": wdo, **U.acoes_ir(acoes_pnl, pd.Series(vend_b3, index=DIAS)), "renda_fixa": renda_fixa,
               "_cdi_perdido": cdi_perd}
    e = (exterior + wdo + acoes_pnl + renda_fixa - cdi_perd) / capital

    # ---------------------------------------------------------------- contribuição por par (conta da IBKR rateada pelo exigido)
    contrib = {}
    sl_par = np.array([s_[0] for s_ in slots])
    custo_conta = (perd_ext - ganho + remessa - wdo).values + juros_margem
    peso_conta = np.zeros((T, len(pares)))
    for p in range(len(pares)):
        m = (sl_par == p)
        ex_p = (vexp[:, m & is_fut] * margem[m & is_fut]).sum(axis=1) + patrimonio_ibkr(
            np.clip(vexp[:, m & is_ib], 0, None).sum(axis=1), np.clip(-vexp[:, m & is_ib], 0, None).sum(axis=1), financia)
        peso_conta[:, p] = ex_p
    tot = peso_conta.sum(axis=1)
    peso_conta = np.divide(peso_conta, tot[:, None], out=np.zeros_like(peso_conta), where=tot[:, None] > 0)
    peso_conta = np.vstack([np.zeros((1, len(pares))), peso_conta[:-1]])
    for p, par in enumerate(pares):
        m = (sl_par == p)
        contrib[par] = (pnl[:, m] - custo[:, m] - alug[:, m] - roll[:, m] + rf_b3[:, m] - perd_b3[:, m]).sum(axis=1) \
            - custo_conta * peso_conta[:, p]
    contrib = pd.DataFrame(contrib, index=DIAS) / capital
    resto = e - contrib.sum(axis=1)                       # custo de conta sem par aberto (saldo parado entre negócios)
    return {"capital": capital, "e": e, "classes": classes, "contrib": contrib, "resto": resto, "negocios": nego, "naocoube": naocoube,
            "exigido": exig, "saldo": saldo, "n_wdo": pd.Series(n_wdo, index=DIAS), "Q": pd.DataFrame(Q, index=DIAS, columns=[f"{s_[2]}@{pares[s_[0]]}" for s_ in slots]),
            "nocional": pd.DataFrame(np.abs(vexp), index=DIAS, columns=[f"{s_[2]}@{pares[s_[0]]}" for s_ in slots])}


def _exigido_pontual(q, slots, inst, Pv, j, fxj, financia="caixa"):
    """Dinheiro fora do CDI no dia j para as quantidades q: margem dos futuros + Reg T na IBKR + ações compradas na B3."""
    tot, short, L, S = 0.0, False, 0.0, 0.0
    for k, (p, papel, tk, tipo, _, _) in enumerate(slots):
        if q[k] == 0:
            continue
        x = inst[tk]
        pr = Pv[k][j]
        if tipo == "fut":
            tot += abs(q[k]) * pr * x["mult"] * fxj * x["margem"]
        elif tipo == "ibkr":
            v = q[k] * pr * fxj
            L, S = L + max(v, 0), S + max(-v, 0)
            short |= v < 0
        else:
            tot += max(q[k] * pr, 0)
    ib = float(patrimonio_ibkr(L, S, financia))
    return tot + (max(ib, REG_T_MIN_USD * fxj) if short else ib)


def tabela_negocios(res, R=None, lag=0):
    """Um negócio por linha a partir do motor: ativo (par), lado, entrada, saída, dias, retorno_% (do par, pelo P&L sobre o nocional de A),
    contrib_pp (pp do capital), rota (instrumentos)."""
    Cp = res["contrib"]
    lin = []
    for par, s, i0, i1, rota in res["negocios"]:
        seg = Cp[par].iloc[i0:i1 + 1]
        nocA = res["nocional"][[c for c in res["nocional"].columns if c.endswith("@" + par)]].iloc[i0]
        noc = float(nocA.iloc[0]) if len(nocA) else np.nan
        lin.append({"ativo": par, "lado": int(s), "entrada": DIAS[i0], "saida": DIAS[min(i1, len(DIAS) - 1)], "dias": int(i1 - i0),
                    "retorno_%": float(seg.sum() * res["capital"] / noc * 100) if noc and noc > 0 else np.nan,
                    "contrib_pp": float(seg.sum() * 100), "rota": rota})
    return pd.DataFrame(lin)
