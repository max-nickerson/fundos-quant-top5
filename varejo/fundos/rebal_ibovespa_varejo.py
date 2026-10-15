"""
Rebalanceamento do Ibovespa — versão pessoa física (B3: Clear/Rico/Inter, corretagem zero).

Mesma tese e mesmo sinal do institucional (fundos/rebal_ibovespa.py): compra os prováveis entrantes 10 pregões antes do último pregão
da carteira velha e vende no fechamento desse pregão (leilão de fechamento). O que muda no varejo:
  - ações INTEIRAS com o capital dado; abaixo de 100 ações a ordem vai para o mercado fracionário (ticker com F), de spread mais largo;
  - custo por perna = emolumentos+liquidação B3 (0,03%) + meio spread por liquidez (padrão 0,05/0,10/0,25/0,50%; fracionário 2x);
  - o capital parado fica em Tesouro Selic / LFTS11 (rende CDI menos ~0,10% a.a.); `caixa_rende=False` mostra o caso "dinheiro parado na conta";
  - hedge (parâmetro `hedge`):
      "win"     mini-índice WIN vendido, CONTRATOS INTEIROS: nocional = R$ 0,20 x pontos do Ibovespa (~R$ 40 mil com o índice a 200 mil
                pontos) -> com R$ 20 mil e ~4 entrantes de 1/15 (~R$ 5 mil de exposição) o arredondamento dá ZERO contratos quase sempre;
                custo ~R$ 1,30 por contrato e lado (emolumentos ~R$ 0,30 + 1 tick de R$ 1); margem de posição ~25% do nocional
                (~R$ 6,6 mil/contrato segundo Toro/Rankia), depositada em Tesouro Selic (rende CDI);
      "bova"    BOVA11 vendido a descoberto via aluguel (BTC), cotas inteiras: taxa média do BOVA11 ~0,37% a.a. + ~20% de tarifas B3 sobre
                a taxa (≈0,45% a.a.) + taxa da corretora de 0,25% do volume por contrato de aluguel (Genial; Rico cita 0,5%);
                garantia ~25% além do produto da venda (que fica em Tesouro Selic como garantia e rende CDI);
      "nenhum"  sem hedge (fica com o Ibovespa dos entrantes);
      "continuo" só para validação: hedge fracionário, custo institucional.
  - ALAVANCAGEM: alvo = L x pesos do institucional. Ações acima do patrimônio compradas a TERMO (XP/Rico) a CDI + 4% a.a. (premissa: a taxa do
    termo é negociada caso a caso, não achei tabela pública), margem do termo 30% do financiado; hedge em WIN inteiros. Garantia exigida =
    30% x financiado + 25% x |vendido| + 25% x nocional WIN. Na abertura a posição é cortada até caber na garantia (a alavancagem efetiva
    fica menor que a pedida); se o patrimônio cair abaixo da garantia, redução forçada no fechamento (com custo) = chamada de margem; se o
    patrimônio zerar, o fundo QUEBRA (retorno -100% no dia, depois nada).

Premissas de varejo.py corrigidas aqui (sem alterar varejo.py):
  - ALUGUEL_BOVA11_VAREJO = 2% a.a. -> 0,45% a.a. + 0,25% fixo por contrato de aluguel (B3: taxa média do BOVA11 0,37% a.a.; Genial: custos do BTC).
IR (não entra no excesso, que é ANTES do IR): ações têm isenção se as VENDAS de ações no mês somarem <= R$ 20 mil (não vale para ETF,
termo/day trade nem futuros) -> veja `isencao_ir`.
Patrimônio nominal constante = capital (posições dimensionadas sobre o capital; o patrimônio para margem = capital + resultado acumulado).
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

_R = Path(__file__).resolve().parents[2]
for _p in (str(_R), str(_R / "varejo")):                 # para rodar o arquivo sozinho (o rodar_varejo.py já põe isso no path)
    if _p not in sys.path:
        sys.path.insert(0, _p)
import comum  # noqa: E402
import varejo as V  # noqa: E402
from fundos import rebal_ibovespa as I  # noqa: E402

NOME = "Rebalanceamento do Ibovespa (varejo B3)"
TESE = I.TESE + " — pessoa física, ações inteiras/fracionário, hedge em WIN inteiro"
BENCHMARK = "CDI"
INICIO, CORTE = I.INICIO, I.CORTE
REGIME = "nenhum"
CUSTO_TROCA = I.CUSTO_TROCA
PARAMS = {"antes": 10, "lado": "compra"}
GRADE = dict(I.GRADE)
VIZINHANCA = dict(I.VIZINHANCA)

CAPITAL = V.CAPITAL
APLICAVEL = True
MOTIVO = ("Aplicável: ações de mid caps em fracionário com corretagem zero; o hedge em WIN não cabe (1 contrato ~R$ 40 mil > exposição), "
          "então na prática com R$ 20 mil o fundo fica SEM hedge (risco de Ibovespa nos ~10 dias de posição)")
INSTRUMENTOS = ("Clear/Rico/Inter (corretagem zero): ~4 entrantes do Ibovespa por revisão (jan/mai/set), 1/15 do capital cada (~R$ 1,3 mil "
                "com R$ 20 mil -> fracionário, ticker XXXX3F, 1 ação mínima), compra 10 pregões antes e venda no leilão de fechamento do último "
                "pregão da carteira velha; resto em Tesouro Selic/LFTS11. Hedge: WINxxx vendido (R$ 0,20 x pontos, margem ~R$ 6-10 mil/contrato) "
                "só quando a exposição >= meio contrato; alternativa BOVA11 vendido via aluguel (Rico/XP; garantia ~125%). "
                "Alavancagem: termo (XP/Rico).")
ALAVANCAGENS = [1, 1.5, 2, 5]
MOTIVO_ALAV = ("Todas rodam: a posição média é só ~25% do capital; com 5x a garantia (termo 30% + WIN 25%) limita a exposição e a alavancagem "
               "efetiva fica abaixo de 5x. Termo em fracionário/mid cap depende da corretora aceitar (premissa).")

# ---------------------------------------------------------------- premissas de varejo (B3)
EMOL = V.B3_EMOLUMENTOS                       # 0,03% por perna
MEIO_SPREAD = (.0005, .0010, .0025, .0050)    # ADV >= 50 mi, >= 10 mi, >= 2 mi, abaixo
FRAC_MULT = 2.0                               # fracionário: spread 2x o do lote padrão
CAIXA_TAXA = .001                             # Tesouro Selic/LFTS11: CDI - 0,10% a.a. (custódia/taxa)
CAIXA_GIRO = .0002                            # vender/comprar Tesouro Selic quando monta/desmonta
WIN_MULT, WIN_CUSTO, WIN_MARGEM = .20, 1.30, .25   # R$/ponto; R$ por contrato e lado; margem (fração do nocional)
BOVA_SPREAD, ALUGUEL_BOVA, BTC_FIXO = .0002, .0045, .0025
TERMO_SPREAD, TERMO_MARGEM, VENDIDO_MARGEM = .04, .30, .25
_DIAG = {}


def carrega():
    d = I.carrega()
    d["ibov"] = pd.read_csv(comum.AQUI / "varejo" / "dados" / "rebal_ibovespa" / "ibov.csv", index_col=0, parse_dates=True)["ibov_pts"]
    return d


def _meio_spread(adv):
    return np.select([adv >= 50e6, adv >= 10e6, adv >= 2e6], MEIO_SPREAD[:3], MEIO_SPREAD[3])


def _simula(d, custo_mult=1, lag=0, antes=10, lado="compra", capital=CAPITAL, hedge="win", alavancagem=1, custos="varejo", caixa_rende=True):
    """Simula a conta dia a dia (R$). Devolve excesso diário (fração do capital), contribuição por ativo e diagnósticos."""
    p = I._painel(d)
    W = I._pesos(d, antes, lado)                                       # decidido em t (fração do PL, bruto <= 1)
    tk = list(W.columns)
    idx = comum.DIAS
    alvo = (W * alavancagem).shift(1 + lag).fillna(0)                   # posição que deve estar montada no fechamento de t
    P = p["P"].reindex(index=idx, columns=tk).ffill()
    Pdec = P.shift(1 + lag)                                             # preço conhecido na decisão
    R = p["R"].reindex(index=idx, columns=tk).fillna(0).to_numpy()
    adv = p["ADV"].reindex(index=idx, columns=tk).ffill().fillna(0)
    inst = custos == "institucional"
    cperna = (I.custo_acao(adv).to_numpy() if inst else EMOL + _meio_spread(adv.to_numpy())) * custo_mult
    alug = I.aluguel_acao(adv).to_numpy() * custo_mult
    if inst:                                                            # validação: sem arredondamento
        N = (alvo * capital / Pdec).fillna(0).to_numpy()
    else:
        N = np.trunc((alvo * capital / Pdec).fillna(0).to_numpy())     # ações inteiras (trunca para não passar do capital)
    Pn = P.fillna(0).to_numpy()
    cdi = comum.CDI.reindex(idx).fillna(0).to_numpy()
    rib = comum.R_IBOV.reindex(idx).fillna(0).to_numpy()
    bova = comum.BOVA.reindex(idx).ffill().fillna(1.0).to_numpy()            # antes de 2014 não há posição
    ibov = d["ibov"].reindex(idx).ffill().fillna(1e9).to_numpy()
    T, K = len(idx), len(tk)

    v = np.zeros(K)                    # valor de cada ação (R$, sinal = lado)
    sh = np.zeros(K)                   # ações em carteira
    hv = 0.0                           # valor do hedge (R$, negativo = vendido): BOVA11 ou WIN (nocional)
    nwin = nbova = 0.0
    E = capital                        # patrimônio para margem = capital + resultado acumulado
    esc = 1.0                          # corte de posição por garantia (vale até o fim do episódio)
    morto = False
    e = np.zeros(T)
    con = np.zeros((T, K + 1))         # última coluna = hedge
    chamadas, quebra, vendas_mes = 0, None, {}
    alav_ef = []
    for t in range(1, T):
        if morto:
            continue
        # ---- resultado de t-1 a t (em excesso ao CDI)
        cv = v * (R[t] - cdi[t])
        ch = hv * (rib[t] - cdi[t])
        v = v * (1 + R[t])
        hv = hv * (1 + rib[t]) if hedge == "bova" else (-nwin * WIN_MULT * ibov[t] if hedge == "win" else hv * (1 + rib[t]))
        caixa = E - v.sum() - (hv if hedge in ("bova", "continuo") else 0.0)   # produto da venda de BOVA11 fica em Tesouro Selic
        if inst:
            custo = 0.0
        elif caixa > 0:                                                 # caixa: Tesouro Selic (CDI - taxa) ou parado na conta (perde o CDI)
            custo = caixa * (CAIXA_TAXA / 252 * custo_mult if caixa_rende else cdi[t])
        else:                                                           # financiado a termo: CDI + spread
            custo = -caixa * TERMO_SPREAD / 252 * custo_mult
        custo += np.abs(np.minimum(v, 0)) @ alug[t] / 252
        if hedge == "bova" and not inst:
            custo += abs(hv) * ALUGUEL_BOVA * custo_mult / 252
        pnl = cv.sum() + ch - custo
        con[t, :K] += cv
        con[t, K] += ch
        E += pnl
        if E <= 0:                                                      # quebra: perdeu todo o patrimônio
            e[t] = -1 - cdi[t]
            quebra, morto = idx[t], True
            continue
        # ---- alvo de hoje (executa no fechamento de t)
        n_alvo = N[t] * esc
        if not inst:
            n_alvo = np.trunc(n_alvo)
        exp_alvo = (n_alvo * Pn[t]).sum()
        if hedge == "win":
            hw = np.round(exp_alvo / (WIN_MULT * ibov[t])) if exp_alvo > 0 else 0.0
        elif hedge == "bova":
            hw = np.round(exp_alvo / bova[t]) if not inst else exp_alvo / bova[t]
        elif hedge == "continuo":
            hw = exp_alvo / bova[t]
        else:
            hw = 0.0

        def garantia(n, h):
            s = n * Pn[t]
            fin = max(s.sum() - E, 0.0)
            vend = np.abs(np.minimum(s, 0)).sum()
            if hedge == "win":
                return TERMO_MARGEM * fin + VENDIDO_MARGEM * vend + WIN_MARGEM * h * WIN_MULT * ibov[t]
            if hedge == "bova":
                return TERMO_MARGEM * fin + VENDIDO_MARGEM * (vend + h * bova[t])
            return TERMO_MARGEM * fin + VENDIDO_MARGEM * vend

        abrindo = (np.abs(sh).sum() == 0) and (np.abs(n_alvo).sum() > 0)
        if alavancagem > 1 or hedge == "win":
            g = garantia(n_alvo, hw)
            if g > E and not inst:
                f = E / g
                if not abrindo:
                    chamadas += 1                                       # posição já aberta: redução forçada
                esc *= f
                n_alvo = np.trunc(n_alvo * f)
                hw = np.floor(hw * f)
        if np.abs(n_alvo).sum() == 0:
            esc = 1.0
        # ---- negocia até o alvo
        dn = n_alvo - sh
        giro = np.abs(dn) * Pn[t]
        if inst:
            c_ac = giro * cperna[t]
        else:
            lote = np.abs(dn) // 100 * 100
            frac = np.abs(dn) - lote
            c_ac = (lote * EMOL + lote * (cperna[t] - EMOL) + frac * EMOL + frac * (cperna[t] - EMOL) * FRAC_MULT) * Pn[t]
            c_ac += np.where((dn != 0) & (n_alvo < 0) & (np.abs(n_alvo) > np.abs(sh)), giro * BTC_FIXO * custo_mult, 0)
        c_ac += giro * CAIXA_GIRO * custo_mult * (not inst)
        venda = np.where(dn < 0, np.abs(dn) * Pn[t], 0).sum()
        if venda > 0 and not inst:
            m = idx[t].to_period("M")
            vendas_mes[m] = vendas_mes.get(m, 0) + venda
        if hedge == "win":
            c_h = abs(hw - nwin) * WIN_CUSTO * custo_mult
            nwin = hw
            hv = -nwin * WIN_MULT * ibov[t]
        elif hedge == "bova":
            c_h = abs(hw - nbova) * bova[t] * ((EMOL + BOVA_SPREAD) * custo_mult if not inst else I.HEDGE_CUSTO * custo_mult)
            if hw > nbova and not inst:
                c_h += (hw - nbova) * bova[t] * BTC_FIXO * custo_mult
            nbova = hw
            hv = -nbova * bova[t]
        elif hedge == "continuo":
            c_h = abs(hw - nbova) * bova[t] * I.HEDGE_CUSTO * custo_mult
            nbova = hw
            hv = -nbova * bova[t]
        else:
            c_h = 0.0
        sh = n_alvo
        v = sh * Pn[t]
        E -= c_ac.sum() + c_h
        con[t, :K] -= c_ac
        con[t, K] -= c_h
        if np.abs(sh).sum() > 0:
            base = np.abs(alvo.iloc[t].to_numpy()).sum() / alavancagem * capital
            alav_ef.append((np.abs(v).sum(), base))
        e[t] = (pnl - c_ac.sum() - c_h) / capital
    ex = pd.Series(e, index=idx)
    C = pd.DataFrame(con / capital, index=idx, columns=tk + ["HEDGE"])
    a = np.array(alav_ef) if alav_ef else np.zeros((1, 2))
    diag = {"chamadas de margem": chamadas, "quebrou em": quebra, "alavancagem efetiva média": a[:, 0].sum() / max(a[:, 1].sum(), 1e-9),
            "vendas_mes": pd.Series(vendas_mes, dtype=float)}
    return ex, C, diag


def excesso(d, custo_mult=1, lag=0, regime=REGIME, antes=PARAMS["antes"], lado=PARAMS["lado"], capital=CAPITAL, hedge="win",
            alavancagem=1, custos="varejo", caixa_rende=True):
    ex, _, diag = _simula(d, custo_mult, lag, antes, lado, capital, hedge, alavancagem, custos, caixa_rende)
    _DIAG.clear()
    _DIAG.update(diag)
    ex = comum.aplica_regime(ex, regime, CUSTO_TROCA * custo_mult)
    ex.attrs.update({k: v for k, v in diag.items() if k != "vendas_mes"})
    return ex


def posicoes(d, antes=PARAMS["antes"], lado=PARAMS["lado"]):
    """Pesos-alvo e retornos em excesso do institucional (o varejo só muda arredondamento e custos)."""
    W, R = I.posicoes(d, antes, lado)
    return W, R


def negocios(d, antes=PARAMS["antes"], lado=PARAMS["lado"], capital=CAPITAL, hedge="win", alavancagem=1):
    """Um negócio por papel e episódio; o hedge de cada episódio aparece como linha própria ("HEDGE")."""
    ex, C, _ = _simula(d, antes=antes, lado=lado, capital=capital, hedge=hedge, alavancagem=alavancagem)
    W = I._pesos(d, antes, lado).shift(1).fillna(0)
    ep = (W.abs().sum(axis=1) > 0).astype(int)
    ini = ep.diff().fillna(ep) > 0
    lab = ini.cumsum().where(ep > 0)
    lab2 = lab.reindex(C.index).ffill(limit=2)                          # resultado do dia seguinte à saída ainda é do episódio
    out = []
    for g, dias in lab2.dropna().groupby(lab2.dropna()).groups.items():
        ent, sai = dias.min(), dias.max()
        bloco = C.loc[dias]
        for a in bloco.columns:
            c = bloco[a].sum()
            if abs(c) < 1e-12:
                continue
            lado_ = -1 if a == "HEDGE" else int(np.sign(W.loc[ent:sai, a].sum()) or 1)
            out.append({"ativo": a, "lado": lado_, "entrada": ent, "saida": sai, "dias": len(dias), "contrib_pp": c * 100})
    return pd.DataFrame(out).sort_values("entrada").reset_index(drop=True)


def isencao_ir(d, capital=CAPITAL, **kw):
    """Meses com venda de ações e quanto ficaria isento (vendas de ações no mês <= R$ 20 mil; ETF/futuro/termo não entram)."""
    _, C, diag = _simula(d, capital=capital, **kw)
    vm = diag["vendas_mes"]
    ganho = C.drop(columns="HEDGE").sum(axis=1).groupby(C.index.to_period("M")).sum().reindex(vm.index) * capital
    isento = vm <= 20_000
    return {"meses com venda": len(vm), "meses isentos": int(isento.sum()), "% meses isentos": isento.mean() * 100,
            "% do ganho em ações isento": ganho[isento & (ganho > 0)].sum() / max(ganho[ganho > 0].sum(), 1e-9) * 100,
            "maior venda num mês R$": vm.max()}


if __name__ == "__main__":
    d = carrega()
    for h in ("win", "bova", "nenhum"):
        for c in (20_000, 4_000):
            e = excesso(d, capital=c, hedge=h)
            print(h, c, "IS %.2f OOS %.2f" % (comum.anual(e[INICIO:CORTE]), comum.anual(e[CORTE:])), e.attrs)
