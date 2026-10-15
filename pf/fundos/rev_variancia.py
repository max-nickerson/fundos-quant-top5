"""
Prêmio de volatilidade — versão PF (R$ 20–50 mil): VXM (Mini VIX, Cboe CFE, US$ 100 x VIX) VENDIDO na IBKR, caixa em CDI, só a margem
lá fora. Cobre as linhas "IAC4 Prêmio de vol com hedge de beta" e "15 Prêmio de volatilidade" do ranking.

Negócio de mesa: o futuro de VIX de ~1 mês fica, na média, ACIMA do VIX à vista (contango: quem compra proteção de vol paga prêmio de
prazo) e converge para o VIX no vencimento. Vendo VXM do 1º vencimento NA ROLAGEM (5 dias antes do vencimento; entra/redimensiona só
nesse dia, sai em qualquer dia) quando:
  (a) contango=1: o futuro segurado está acima do VIX à vista (há prêmio de rolagem a capturar; em backwardation o mercado já está em
      pânico) — é a chave de risco: saiu antes de 5/fev/2018 (backwardation em 29/jan) e de mar/2020 (20/fev);
  (b) regime: o IS escolheu "nenhum"; o risco_global do institucional (VIX < p80, S&P > MM200, HYG/IEF > MM100) está na grade e piorou o IS
      (fica de fora nos meses de maior contango pós-choque).
Quem paga: comprador de proteção (fundos que hedgeiam carteira com call de VIX/futuro, ETPs longos de VIX que rolam comprando o 2º mês).

Rota PF e decisões:
  - Swap de variância (institucional IAC4) é balcão ISDA: não existe para PF. VXM é o substituto listado; captura o prêmio de PRAZO do VIX
    (futuro − VIX), não IV − RV inteiro, e perde mais em choques (fev/2018, mar/2020 estão no IS).
  - Hedge de beta: o institucional vende beta do S&P. 1 VXM vendido a VIX 16 equivale a ~US$ 6–8 mil de S&P comprado (o futuro de VIX
    sobe ~0,6–1 ponto por −1% do S&P); o menor hedge listado é 1 MES (US$ 5 x S&P ~ US$ 33 mil = 4–8x a exposição a hedgear e 8x R$ 20 mil):
    descartado. Hedge com SPY vendido (ações inteiras, Reg T 150%) ou SH (frações, à vista) exigiria mandar mais ~US$ 7 mil para fora (perde
    CDI − T-bill ~6–8 pp a.a. sobre ele) — também descartado. O filtro de contango (e, na grade, o regime risco_global) faz esse papel.
  - Margem — PREMISSA CORRIGIDA: a IBKR cobra margem MAIOR para VXM VENDIDO overnight: US$ 2.767 inicial / US$ 2.406 manutenção (contra
    US$ 856/744 do comprado) — fonte: interactivebrokers.com/en/trading/margin-futures-fops.php (coluna "Short Overnight", out/2026).
    pf.CONTRATOS["VXM"] supunha 45% do nocional; com VIX ~16,5 o vendido exige ~146% (manutenção) / 168% (inicial) do nocional.
    Modelo: fração do nocional fixa (constante), revista uma vez por mês (a margem não acompanha o preço tick a tick); saldo na IBKR =
    max(US$ 2.000, 1,25 x margem inicial), MANTIDO pela maior exigência dos últimos ~6 meses (ir e voltar com IOF a cada liga/desliga
    custava ~12 pp a.a. com R$ 20 mil). Chamada de margem: se o patrimônio da conta (saldo + P&L do mês) cai abaixo da manutenção, a
    IBKR liquida no fechamento (perda realizada, sem posição até o próximo pregão de decisão). Quebra: patrimônio total <= 0.
  - Contratos inteiros: alvo de vol (alvo / vol do futuro segurado, 63 d) x capital; arredonda; mínimo 1 contrato; máximo
    floor(teto x capital / nocional) — "teto" = perda máxima aceita num choque de +100% no futuro (5/fev/2018), em fração do capital.
    Com R$ 20 mil e VIX 15, 1 VXM ~ R$ 7,5–8 mil de nocional (0,4x): choque = 40% do capital; teto 0,3 => não opera; teto 0,5 => 1 contrato.
  - VXM só existe desde ago/2020; antes uso o VX (1.000 x VIX) dividido por 10 (mesmo índice de liquidação). Ajustes diários da Cboe CFE
    por vencimento (varejo/dados/variancia/vx.csv, 2007+): o P&L é sempre do MESMO contrato entre t−1 e t (sem salto de rolagem).
  - Custos: US$ 5,50/lado (comissão IBKR + taxa CFE ~US$ 1,50 + meio tick de US$ 5 ~ US$ 4; varejo/fundos/variancia_varejo.py), rolagem
    mensal = 2 lados. Remessa/IOF/CDI perdido/câmbio do saldo via pf.custo_conta_exterior; P&L do mês volta ao Brasil (0,38% + 0,5%) ou é
    reposto (1,1% + 0,5%). Excedente do saldo acima de 1,25x a margem em SGOV (T-bill − 0,09%).
  - Variante "svxy": comprar SVXY (−0,5x futuros de VIX de 30 dias desde 28/02/2018; −1x antes) na IBKR em conta CASH com frações: só o
    valor da posição vai para fora (sem mínimo de US$ 2 mil), sem chamada de margem; antes de out/2011, sintético (índice de 30 dias).
IR: VXM/SVXY -> "exterior" (Lei 14.754/2023, 15% anual); câmbio do saldo não remunerado -> "isento"; IOF/spread -> "isento" negativo.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _util as U  # noqa: E402

C, pf = U.C, U.pf

NOME = "Prêmio de vol PF (VXM vendido, só margem na IBKR)"
TESE = ("Vende 1+ Mini VIX (VXM) do 1º vencimento na rolagem quando há contango (sai se virar backwardation); caixa em CDI, só a margem (alta: "
        "US$ 2,8 mil por VXM vendido) na IBKR; contratos inteiros com teto de perda num choque tipo fev/2018")
BENCHMARK = "CDI"
INICIO, CORTE = "2008-01-01", "2021-01-01"
REGIME = "nenhum"                      # escolhido no IS (o filtro de contango já é a chave de risco; risco_global piorou o IS)
CUSTO_TROCA = 0.0                       # liga/desliga já paga custo real dentro do motor (ordens)
PARAMS = {"contango": 1, "teto": .5, "venc": 1, "alvo": .15, "veiculo": "vxm", "rolar": 5}
GRADE = {"contango": [0, 1], "teto": [.3, .5], "venc": [1, 2], "regime": ["nenhum", "risco_global"]}
VIZINHANCA = {"teto": (.35, .7), "alvo": (.08, .25), "rolar": (3, 8)}
RANKING = ["IAC4 Prêmio de vol com hedge de beta (CBOE + variância EUA/Europa)", "15 Prêmio de volatilidade"]
INSTRUMENTOS = ("IBKR (conta margem, mín. US$ 2.000): VENDER VXM (Cboe CFE, US$ 100 x VIX, ~US$ 1,5–2 mil de nocional), 1º vencimento, "
                "rolagem mensal 5 dias antes; margem IBKR p/ vendido overnight US$ 2.767 inicial / 2.406 manutenção; custo ~US$ 5,50/lado. "
                "Sem hedge de beta (MES US$ 5 x S&P ~ US$ 33 mil não cabe); filtro de contango (sai em backwardation). Caixa em Tesouro Selic. "
                "Variante: SVXY comprado em conta cash (frações), só o valor da posição lá fora.")
APLICAVEL = False
MOTIVO = ("opera (1 VXM), mas não preserva o edge: a margem de VXM VENDIDO na IBKR (~US$ 2,8 mil) prende 76–85% do capital fora do CDI "
          "e no dólar; sem hedge de beta; o futuro de VIX vendido rende ~+1 pp a.a. no OOS mesmo em escala (o prêmio do IAC4 é do swap de variância)")
ALAVANCAGENS = [1, 1.5, 2]
MOTIVO_ALAV = ("alavancagem multiplica o alvo de vol e o teto de choque; 1x/1,5x quase sempre = 1 VXM; 2x = 1–2 VXM. 5x descartado: "
               "5 VXM vendidos exigiriam ~US$ 14 mil de margem (> R$ 50 mil) e um choque de +100% custaria 2x o capital (quebra)")
VARIANTES = {"SVXY comprado (cash, frações)": {"veiculo": "svxy"}, "regime risco_global (institucional)": {"regime": "risco_global"},
             "2º vencimento": {"venc": 2}, "hedge cambial do saldo com WDO": {"hedge_fx": True}, "sem filtro de contango": {"contango": 0}}

MULT = 100.0
CUSTO_LADO = 5.50                       # US$
VXM_REF = 16.5                          # VIX de referência das margens IBKR citadas
MARG_MANUT = 2406.19 / (VXM_REF * MULT)  # ~1,46 x nocional
MARG_INI = 2767.12 / (VXM_REF * MULT)    # ~1,68 x nocional
FOLGA = 1.25
MANTEM = 126                            # pregões: saldo mantido = maior exigência dos últimos ~6 meses
MIN_CONTA = 2000.0
SGOV_TAXA = .0009
CHOQUE = 1.0                            # +100% no futuro (5/fev/2018)
VOLTA, IDA = pf.REMESSA_VOLTA + pf.SPREAD_CAMBIO, pf.REMESSA_IDA + pf.SPREAD_CAMBIO
TAXA_SVXY, SLIP_ETF = .0095, .0005


def carrega():
    p = U.RAIZ / "varejo" / "dados" / "variancia"
    return {"vx": pd.read_csv(p / "vx.csv", parse_dates=["data", "venc"]),
            "px": pd.read_csv(U.TOP5 / "variancia" / "vix_sp500.csv", index_col=0, parse_dates=True),
            "etf": pd.read_csv(p / "etfs.csv", index_col=0, parse_dates=True)[["SVXY_adj", "SVXY_close"]],
            "cupom": pd.read_csv(U.TOP5 / "carry_moedas" / "cupom_frc.csv", index_col=0, parse_dates=True)["cupom_frc_aa_pct"]}


_CACHE = {}


def _serie_vx(d, venc, rolar):
    """No calendário dos ajustes da CFE: dF do contrato segurado (escolhido em t−1), nível do contrato escolhido em t, VIX à vista,
    índice de 30 dias (para o SVXY sintético) e marca de rolagem."""
    vx = d["vx"]
    chave = ("vx", id(vx), len(vx), vx["data"].max(), venc, rolar)
    if chave in _CACHE:
        return _CACHE[chave]
    p = vx.pivot(index="data", columns="venc", values="ajuste").sort_index()
    idx = p.index
    vencs = np.array(sorted(p.columns), dtype="datetime64[ns]")
    lim = (idx + pd.Timedelta(days=int(round(rolar * 7 / 5)))).values
    k = np.searchsorted(vencs, lim, side="right") + (venc - 1)          # 1º (ou 2º) vencimento depois de t + rolar
    k = np.minimum(k, len(vencs) - 1)
    P = p.values
    i = np.arange(len(idx))
    nivel = P[i, k]
    kseg = np.r_[k[0], k[:-1]]                                          # contrato segurado hoje = escolhido ontem
    hoje, ontem = P[i, kseg], P[np.maximum(i - 1, 0), kseg]
    dF = np.where(i > 0, hoje - ontem, 0.0)
    # índice de 30 dias (1º/2º vencimentos) para o SVXY sintético
    k1 = np.minimum(np.searchsorted(vencs, idx.values, side="right"), len(vencs) - 2)
    d1 = (vencs[k1] - idx.values) / np.timedelta64(1, "D")
    d2 = (vencs[k1 + 1] - idx.values) / np.timedelta64(1, "D")
    w1 = np.clip((d2 - 30) / (d2 - d1), 0, 1)
    niv30 = w1 * P[i, k1] + (1 - w1) * P[i, k1 + 1]
    amanha = w1 * P[np.minimum(i + 1, len(i) - 1), k1] + (1 - w1) * P[np.minimum(i + 1, len(i) - 1), k1 + 1]
    r30 = pd.Series(amanha / niv30 - 1, index=idx).shift(1)
    out = pd.DataFrame({"dF": np.nan_to_num(dF), "nivel": nivel, "rola": np.r_[False, k[1:] != k[:-1]], "r30": r30.values}, index=idx)
    out["nivel"] = out["nivel"].ffill()
    vix = d["px"]["vix"].reindex(idx).ffill()
    out["vix"] = vix
    out["r_seg"] = (out["dF"] / pd.Series(ontem, index=idx)).replace([np.inf, -np.inf], np.nan).fillna(0)
    _CACHE[chave] = out
    return out


def _regime_us(idx):
    s = C.regime_risco_global()
    return s.reindex(idx, method="ffill").fillna(1.0)


def _para_b3(x):
    """Valores diários em R$ no calendário dos EUA -> soma nos pregões da B3."""
    return pf.usd_para_br(x)


# ---------------------------------------------------------------- VXM
def _motor_vxm(d, capital, custo_mult, lag, regime, alavancagem, contango, teto, venc, alvo, rolar):
    S = _serie_vx(d, venc, int(rolar))
    idx = S.index
    ptax = pf.PTAX.reindex(idx, method="ffill").bfill().values
    vol = S["r_seg"].rolling(63, min_periods=40).std() * np.sqrt(252)
    noc1 = (S["nivel"] * MULT).values                                    # US$ do contrato escolhido em t
    cap_usd = capital / ptax
    nraw = np.round((alvo * alavancagem / vol.values) * cap_usd / noc1)
    nmax = np.floor(teto * alavancagem * cap_usd / (noc1 * CHOQUE))
    n = np.minimum(np.maximum(np.nan_to_num(nraw), 1), nmax)
    ok = np.isfinite(vol.values) & np.isfinite(noc1)
    if contango:
        ok &= (S["nivel"] > S["vix"]).values
    if regime == "risco_global":
        ok &= (_regime_us(idx).values >= 1)
    n = np.where(ok & np.asarray(idx >= pd.Timestamp(INICIO)), n, 0.0)     # contratos VENDIDOS decididos em t
    nd = pd.Series(n, index=idx).shift(1 + lag).fillna(0).values        # executado em t+1+lag
    dF, rola = S["dF"].values, S["rola"].values
    nivel = S["nivel"].values
    mes = idx.to_period("M")
    novo_mes = np.r_[True, mes[1:] != mes[:-1]]
    T = len(idx)
    pos = np.zeros(T)                 # contratos vendidos no fechamento de t
    pnl = np.zeros(T)                 # US$
    custo = np.zeros(T)               # US$
    req = np.zeros(T)                 # saldo exigido na IBKR (US$)
    chamadas, quebra = [], None
    q, eq_mes, saldo, marg_frac_m = 0.0, 0.0, 0.0, MARG_MANUT
    ref_noc = 0.0
    bloqueio = -1
    acum = 0.0
    for t in range(1, T):
        pnl[t] = -q * MULT * dF[t]
        eq_mes += pnl[t]
        if novo_mes[t]:
            eq_mes = 0.0
        alvo_q = nd[t] if t > bloqueio else 0.0
        if not rola[t] and alvo_q > 0:                                   # entra/redimensiona só na rolagem; sai a qualquer dia
            alvo_q = q
        if q > 0 and rola[t]:
            custo[t] += 2 * q * CUSTO_LADO                               # rolagem (fecha o velho, vende o novo)
        # chamada de margem: patrimônio da conta (saldo do mês + P&L) < manutenção (margem revista no mês / na entrada)
        if q > 0:
            manut = q * ref_noc * MARG_MANUT
            if saldo + eq_mes < manut:
                chamadas.append(idx[t])
                custo[t] += q * CUSTO_LADO
                q = 0.0
                bloqueio = t                                             # só volta a partir do próximo pregão
                alvo_q = 0.0
        if alvo_q != q:
            custo[t] += abs(alvo_q - q) * CUSTO_LADO
            if alvo_q > 0 and (q == 0 or novo_mes[t]):
                ref_noc = nivel[t] * MULT
            q = alvo_q
        elif novo_mes[t] and q > 0:
            ref_noc = nivel[t] * MULT                                    # margem revista no mês
        pos[t] = q
        req[t] = max(MIN_CONTA, FOLGA * q * ref_noc * MARG_INI) if q > 0 else 0.0
        if novo_mes[t] or req[t] > saldo:
            saldo = max(req[max(0, t - MANTEM):t + 1].max(), req[t])
        acum += pnl[t] - custo[t]
        if (capital / ptax[t]) + acum <= 0 and quebra is None:
            quebra = idx[t]
            break
    custo *= custo_mult
    liq_brl = pd.Series((pnl - custo) * ptax, index=idx)
    # o dinheiro fica na IBKR enquanto a estratégia esteve ativa nos últimos ~6 meses (evita ida e volta com IOF a cada liga/desliga)
    req_brl = pd.Series(req, index=idx).rolling(MANTEM, min_periods=1).max() * ptax
    marg_brl = pd.Series(pos * np.r_[0, nivel[:-1]] * MULT * MARG_INI * ptax, index=idx)
    info = {"pos": pd.Series(pos, index=idx), "pnl_brl": pd.Series(pnl * ptax, index=idx), "custo_brl": pd.Series(custo * ptax, index=idx),
            "chamadas": chamadas, "quebra": quebra, "noc_brl": pd.Series(pos * nivel * MULT * ptax, index=idx), "S": S, "nd": nd, "n": n}
    return liq_brl, req_brl, marg_brl, info


# ---------------------------------------------------------------- SVXY (conta cash, frações)
def _motor_svxy(d, capital, custo_mult, lag, regime, alavancagem, contango, teto, venc, alvo, rolar, banda=.25):
    S = _serie_vx(d, 1, 5)
    etf = d["etf"]
    idx = S.index
    real = etf["SVXY_adj"].reindex(idx).pct_change(fill_method=None)
    mult = np.where(idx < pd.Timestamp("2018-02-28"), -1.0, -.5)
    sint = mult * S["r30"] - TAXA_SVXY / 252
    r = real.where(idx >= pd.Timestamp("2011-10-05"), sint).fillna(0).values
    vol = pd.Series(r, index=idx).rolling(63, min_periods=40).std() * np.sqrt(252)
    w = np.minimum(alvo * alavancagem / vol.values, teto * alavancagem / (CHOQUE * -mult))
    ok = np.isfinite(w)
    if contango:
        ok &= (S["nivel"] > S["vix"]).values
    if regime == "risco_global":
        ok &= (_regime_us(idx).values >= 1)
    w = np.where(ok & np.asarray(idx >= pd.Timestamp(INICIO)), np.nan_to_num(w), 0.0)
    wd = pd.Series(w, index=idx).shift(1 + lag).fillna(0).values
    ptax = pf.PTAX.reindex(idx, method="ffill").bfill().values
    T = len(idx)
    V = 0.0
    pnl, custo, pos = np.zeros(T), np.zeros(T), np.zeros(T)
    for t in range(1, T):
        pnl[t] = V * r[t]
        V *= 1 + r[t]
        alvo_v = wd[t] * capital / ptax[t]
        if abs(alvo_v - V) > banda * max(alvo_v, 1e-9) or (alvo_v == 0 and V != 0):
            dv = abs(alvo_v - V)
            custo[t] += max(.35, .0035 * dv / 60) + SLIP_ETF * dv          # IBKR tiered (~US$ 60/ação) + slippage
            V = alvo_v
        pos[t] = V
    custo *= custo_mult
    liq_brl = pd.Series((pnl - custo) * ptax, index=idx)
    req_brl = pd.Series(pos * ptax, index=idx)
    info = {"pos": pd.Series(pos, index=idx), "pnl_brl": pd.Series(pnl * ptax, index=idx), "custo_brl": pd.Series(custo * ptax, index=idx),
            "chamadas": [], "quebra": None, "noc_brl": req_brl, "S": S}
    return liq_brl, req_brl, req_brl, info


# ---------------------------------------------------------------- conta + classes
def _motor(d, capital=20000, custo_mult=1, lag=0, regime=REGIME, alavancagem=1, contango=1, teto=.5, venc=1, alvo=.15,
           veiculo="vxm", rolar=5, hedge_fx=False):
    f = _motor_vxm if veiculo == "vxm" else _motor_svxy
    reg_dentro = "risco_global" if regime == "risco_global" else "nenhum"
    liq, req, marg, info = f(d, capital, custo_mult, lag, reg_dentro, alavancagem, contango, teto, int(venc), alvo, rolar)
    D = C.DIAS[C.DIAS <= liq.index.max()]
    liq_b3 = _para_b3(liq).reindex(C.DIAS).fillna(0)
    req_b3 = req.reindex(D.union(req.index)).ffill().reindex(C.DIAS).fillna(0)
    marg_b3 = marg.reindex(D.union(marg.index)).ffill().reindex(C.DIAS).fillna(0)
    custo_conta, saldo = pf.custo_conta_exterior(req_b3, folga=1.0)
    saldo = saldo.reindex(C.DIAS).fillna(0)
    cdi_perd = saldo.shift(1).fillna(0) * C.CDI.fillna(0)
    cambial = saldo.shift(1).fillna(0) * pf.PTAX.pct_change(fill_method=None).reindex(C.DIAS).fillna(0)
    remessa = (custo_conta.reindex(C.DIAS).fillna(0) - cdi_perd + cambial) * custo_mult
    if veiculo == "vxm":
        livre = (saldo - FOLGA * marg_b3).clip(lower=0)
        tb = C.TB_US.reindex(C.DIAS, method="ffill").fillna(0)
        sg = livre.shift(1).fillna(0) * (tb - SGOV_TAXA / 252)
        # o valor da posição de SVXY já é o saldo (cambial e CDI perdido sobre ela); na conta do VXM o resultado do mês volta ao Brasil
        mes = pd.Series(C.DIAS.to_period("M"), index=C.DIAS)
        pm = liq_b3.groupby(mes).sum()
        prim = mes.ne(mes.shift()).values
        v = pm.shift(1).reindex(mes[prim].values).fillna(0).values
        flx = pd.Series(0.0, index=C.DIAS)
        flx.loc[C.DIAS[prim]] = -np.where(v > 0, v * VOLTA, -v * IDA) * custo_mult
    else:
        sg = pd.Series(0.0, index=C.DIAS)
        flx = pd.Series(0.0, index=C.DIAS)
    fut_b3 = pd.Series(0.0, index=C.DIAS)
    if hedge_fx:
        # variante: vende WDO (US$ 10 mil, inteiros) contra o saldo parado na IBKR, decidido no fim do mês com o saldo do dia (t+1).
        # Vendido em WDO = comprado em real: rende −ΔPTAX + (CDI − cupom cambial); antes de 2019, CDI − T-bill − 1,07 pp (premissa).
        ptx = pf.PTAX.reindex(C.DIAS)
        cup = d["cupom"].reindex(C.DIAS.union(d["cupom"].index)).ffill().reindex(C.DIAS).shift(1) / 100
        cup = cup.where(C.DIAS >= d["cupom"].index.min())
        cdi_aa = (1 + C.CDI.reindex(C.DIAS).fillna(0)) ** 252 - 1
        car = (cdi_aa - cup).combine_first(cdi_aa - C.TB_US.reindex(C.DIAS, method="ffill").fillna(0) * 252 - .0107).shift(1)
        mes = pd.Series(C.DIAS.to_period("M"), index=C.DIAS)
        fim = mes.ne(mes.shift(-1))
        nw = (saldo / ptx / 10_000).round().where(fim).ffill().fillna(0).shift(1).fillna(0)
        r = -ptx.pct_change(fill_method=None).fillna(0) + car.fillna(0) / 252
        giro = nw.diff().abs().fillna(nw) + 2 * nw.shift(1).fillna(0) * mes.ne(mes.shift()).values
        fut_b3 = nw.shift(1).fillna(0) * 10_000 * ptx.shift(1) * r - giro * 3.70 * custo_mult
    cls = {"exterior": liq_b3 + sg, "isento": cambial - remessa + flx, "futuros_b3": fut_b3, "_cdi_perdido": cdi_perd}
    ini = pd.Timestamp(INICIO)
    cls = {k: v.where(v.index >= ini, 0.0).reindex(C.DIAS).fillna(0) for k, v in cls.items()}
    e = (cls["exterior"] + cls["isento"] + cls["futuros_b3"] - cls["_cdi_perdido"]) / capital
    if info["quebra"] is not None:                                       # quebra: −100% e fica em CDI
        dq = C.DIAS[C.DIAS.searchsorted(info["quebra"])]
        cota = (1 + C.CDI.reindex(C.DIAS).fillna(0) + e)[(C.DIAS >= ini) & (C.DIAS < dq)].prod()
        e.loc[dq] = -1.0
        e.loc[e.index > dq] = 0.0
    info["liq_b3"] = liq_b3
    info["noc_b3"] = info["noc_brl"].reindex(D.union(info["noc_brl"].index)).ffill().reindex(C.DIAS).fillna(0)
    info["saldo"] = saldo
    return e, cls, info


def _com_regime(d, capital, custo_mult, lag, regime, alavancagem, **params):
    p = {**PARAMS, **params}
    e, cls, info = _motor(d, capital, custo_mult, lag, regime, alavancagem, **p)
    if regime == "dd_stop":
        s = C.regime_dd_stop(e)
        e = e * s
        cls = {k: v * s for k, v in cls.items()}
    return e, cls, info


def excesso(d, capital=20000, custo_mult=1, lag=0, regime=REGIME, alavancagem=1, **params):
    return _com_regime(d, capital, custo_mult, lag, regime, alavancagem, **params)[0]


def classes_ir(d, capital=20000, regime=REGIME, **params):
    return _com_regime(d, capital, 1, 0, regime, 1, **params)[1]


def posicoes(d, capital=20000, **params):
    """W: nocional VENDIDO de VXM decidido em t / capital (negativo); R: retorno diário do futuro segurado (fração). Calendário B3."""
    p = {**PARAMS, **params}
    e, cls, info = _motor(d, capital, 1, 0, REGIME, 1, **p)
    S = info["S"]
    if p["veiculo"] == "vxm":
        W = -pd.Series(info["n"], index=S.index) * S["nivel"] * MULT * pf.PTAX.reindex(S.index, method="ffill") / capital
        R = S["r_seg"]
    else:
        W = info["pos"] * pf.PTAX.reindex(S.index, method="ffill") / capital
        R = info["pnl_brl"] / (info["pos"].shift(1) * pf.PTAX.reindex(S.index, method="ffill")).replace(0, np.nan)
    R = R.fillna(0)
    Rb = np.expm1(pf.usd_para_br(np.log1p(R)))
    Wb = W.reindex(C.DIAS, method="ffill").fillna(0)
    return Wb.to_frame(p["veiculo"].upper()), Rb.to_frame(p["veiculo"].upper())


def negocios(d, capital=20000, **params):
    """Um negócio por contrato/vencimento vendido (do dia em que entra até sair ou rolar). contrib_pp = P&L líquido de ordens / capital.
    Conta IBKR (CDI perdido, remessas, câmbio do saldo, SGOV, retorno mensal do P&L) = uma linha por ano."""
    p = {**PARAMS, **params}
    e, cls, info = _com_regime(d, capital, 1, 0, REGIME, 1, **p)
    pos, S = info["pos"], info["S"]
    liq = (info["pnl_brl"] - info["custo_brl"])
    idx = pos.index
    lin = []
    if p["veiculo"] == "vxm":
        rola = S["rola"].values
        on = pos.values > 0
        i = 1
        while i < len(idx):
            if on[i] and not on[i - 1] or (on[i] and rola[i]):
                j = i + 1
                while j < len(idx) and on[j] and not rola[j]:
                    j += 1
                seg = slice(i + 1, min(j + 1, len(idx)))
                f0, f1 = S["nivel"].iloc[i], S["nivel"].iloc[min(j, len(idx) - 1)]
                lin.append({"ativo": "VXM", "lado": -1, "entrada": idx[i], "saida": idx[min(j, len(idx) - 1)], "dias": j - i,
                            "contratos": float(pos.values[i]), "futuro_entrada": f0, "vix_entrada": float(S["vix"].iloc[i]),
                            "retorno_%": -(np.prod(1 + S["r_seg"].values[seg]) - 1) * 100,
                            "contrib_pp": liq.values[seg].sum() / capital * 100})
                i = j
            else:
                i += 1
    else:
        m = liq.groupby(idx.to_period("M")).sum()
        for per, v in m.items():
            if v != 0:
                lin.append({"ativo": "SVXY", "lado": 1, "entrada": per.start_time, "saida": per.end_time.normalize(), "dias": 21,
                            "retorno_%": np.nan, "contrib_pp": v / capital * 100})
    conta = cls["isento"] + cls["exterior"] - info["liq_b3"] - cls["_cdi_perdido"]
    conta = conta[conta.index >= pd.Timestamp(INICIO)]
    for ano, x in conta.groupby(conta.index.year):
        if x.abs().sum() > 0:
            lin.append({"ativo": "conta IBKR", "lado": 1, "entrada": x.index[0], "saida": x.index[-1], "dias": len(x),
                        "retorno_%": np.nan, "contrib_pp": x.sum() / capital * 100})
    ng = pd.DataFrame(lin)
    return ng.sort_values("entrada").reset_index(drop=True) if len(ng) else ng


def detalhe(d, capital=20000, **params):
    p = {**PARAMS, **params}
    e, cls, info = _com_regime(d, capital, 1, 0, p.pop("regime", REGIME), 1, **p)
    a = info["noc_b3"] / capital
    s = info["saldo"] / capital
    o = C.DIAS >= pd.Timestamp(CORTE)
    return {"chamadas de margem": len(info["chamadas"]), "datas": [str(x.date()) for x in info["chamadas"]][:10],
            "quebra": str(info["quebra"]), "% dias vendido OOS": float((a[o] > 0).mean() * 100),
            "% dias vendido IS": float((a[(~o) & (C.DIAS >= pd.Timestamp(INICIO))] > 0).mean() * 100),
            "nocional médio quando vendido OOS (x capital)": float(a[o][a[o] > 0].mean()) if (a[o] > 0).any() else 0.0,
            "saldo médio na IBKR OOS (% capital)": float(s[o].mean() * 100)}
