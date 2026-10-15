"""
Mineradoras vs metal — versão PESSOA FÍSICA (R$ 20–50 mil), caixa em CDI e só o necessário na IBKR.

Sinal = o do institucional auditado (fundos/mineradoras.py, top 5): resíduo "mineradora - beta x metal" (excesso sobre o T-bill),
beta de 1 ano em retornos de 5 dias, z do resíduo acumulado (decisão semanal), entra |z| > z_in, sai na média, stop |z| > 4, prazo 120
dias, lado bloqueado depois de stop/prazo até o z voltar a 0; risco igual por par (vol-alvo 10%/raiz(n)).

O que muda (execução PF, motor em _rev_pares_pf.py):
  - tamanho fixado na entrada, sem rebalanceio diário (o varejo antigo também; o institucional rebalanceia todo dia);
  - perna do METAL em micro futuros CME, contratos inteiros, só a margem fora: ouro 1OZ (1 oz) -> MGC (10 oz); prata micro (1.000 oz);
    cobre MHG (2.500 lb). Se o futuro arredonda para 0 contrato, a perna vai para o ETF na IBKR (GLD/SLV/CPER; vendido em ações inteiras,
    comprado com fração). Retorno do futuro = (retorno do ETF físico/de futuros - T-bill + taxa do ETF) sobre o NÍVEL do contrato
    (GC=F/SI=F/HG=F do Yahoo só para contar contratos: o salto da rolagem não entra no P&L); rolagem: 2 x custo por lado por vencimento;
  - perna da MINERADORA em ETF/ação na IBKR (GDX, GDXJ, SIL, COPX, FCX, VALE, BHP, RIO): comprada com fração, vendida em ações inteiras;
    patrimônio exigido Reg T (100% do comprado, 50% do vendido, mínimo US$ 2.000 se houver venda) fica em dólar e perde o CDI;
  - pares só de ações (GDXJ x GDX, VALE x BHP/RIO): as duas pernas na IBKR.
  - LIÇÃO do varejo anterior (varejo/fundos/mineradoras_varejo.py, -11,9 pp): lá o capital inteiro ia para a IBKR sem hedge. Aqui o
    capital fica no CDI e só a margem/Reg T vai (pf.custo_conta_exterior).

Rota B3 (BDRs GDXB39, BSIL39, BCPX39, FCXO34, BHPG34, RIOT34; VALE3): só serve para a perna COMPRADA da mineradora (aluguel de BDR para PF
não confirmado — varejo/MAPA_ATIVOS_EUA.md); não modelada como padrão porque o lado vendido do par (metade dos negócios) precisa da IBKR
de qualquer forma e o BDR tem spread maior. A perna comprada em BDR troca remessa (IOF 1,1%) por spread de BDR (~0,3%): diferença pequena.

Premissas corrigidas (out/2026), com fonte:
  - 1-Ounce Gold (1OZ): 1 oz, liquidação financeira, lançado em 13/01/2025, OI ~81 mil contratos; margem inicial ~US$ 505 (~12% do
    nocional), taxa de bolsa US$ 0,25/contrato. https://www.cmegroup.com/markets/metals/files/1-ounce-gold-fact-card.pdf ;
    https://lpfutures.com/1ounce-gold-futures-contract/ ; https://www.tradingview.com/symbols/COMEX-1OZ1!/
    -> antes de 2025 o 1OZ NÃO existia. Padrão: 1OZ "como se existisse" (o que o grupo pode fazer hoje); VARIANTE "historico" usa só o que
    existia na data (MGC desde 2010; 1OZ desde 2025).
  - MGC: IBKR US$ 0,25/contrato + taxas de bolsa/regulatórias ~US$ 0,70 (https://brokerchooser.com/broker-reviews/interactive-brokers-review/micro-gold-futures-fees);
    margem ~US$ 2,3–2,6 mil (~6%) (varejo/MAPA_ATIVOS_EUA.md).
  - MHG: margem inicial IBKR US$ 1.680 (~10% do nocional de US$ 16,5 mil); micro prata: margem inicial ~US$ 7,4 mil (~13% de US$ 56 mil)
    (https://futuresspecs.com/mhg/ ; https://www.discounttrading.com/margin.html ; https://www.interactivebrokers.com/en/trading/margin-futures-fops.php).
    pf.CONTRATOS tinha MHG 6% e SIL 8% (baixo para 2026) -> corrigido aqui.
  - Custo por lado (comissão + bolsa + meio tick): 1OZ US$ 0,80; MGC US$ 1,50; micro prata US$ 3,50 (tick de US$ 5); MHG US$ 1,60.
  - CPER: taxa 0,97% a.a. (https://etfdb.com/etf/CPER/); GLD 0,40%; SLV 0,50%.
  - Aluguel IBKR (arquivo público de short, lido em 15/10/2026, varejo/mapa_ativos_eua.csv): GDX 0,42%, GDXJ 0,55%, SIL 0,52%, SLV 0,42%,
    COPX 0,45%, CPER 0,28% (só 10 mil ações disponíveis), FCX 0,41%, VALE 0,25%, BHP 0,63%, RIO 0,30%, GLD 0,43% a.a.
  - Preço usado para contar ações = preço ajustado do Yahoo (sem os brutos; erro pequeno na contagem de ações vendidas).

Quantos pares cabem: com R$ 20 mil e os 6 pares, a perna de ouro de um par é ~R$ 4–8 mil (GDX R$ ~4 mil x beta ~1,8) => 0 ou 1 1OZ;
cobre (MHG = R$ 50–85 mil) e prata (micro = R$ 120–300 mil) nunca cabem -> vão para CPER/SLV em ações. Ver "negócios" (coluna rota).
"""
import importlib.util
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

import _util as U  # noqa: E402
import _rev_pares_pf as PP  # noqa: E402

C, pf = U.C, U.pf

_spec = importlib.util.spec_from_file_location("_min_top5", U.RAIZ / "fundos" / "mineradoras.py")
M = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(M)

NOME = "Mineradoras vs metal (PF: micro futuros de metal + ETFs na IBKR, caixa em CDI)"
TESE = ("Mineradora é opção alavancada no metal: compro a mineradora que ficou para trás do metal e vendo o metal no micro futuro "
        "(1 oz de ouro) ou no ETF (e o inverso); só a margem/Reg T vai para a IBKR, o resto fica no CDI.")
BENCHMARK = "CDI"
INICIO, CORTE = "2012-01-01", "2021-01-01"
REGIME = "nenhum"
CUSTO_TROCA = .001
PARAMS = {"jan": 63, "z_in": 1.0, "alvo": .10, "pares": "todos"}
GRADE = {"jan": [63, 126], "z_in": [1.0, 2.0]}
VIZINHANCA = {"jan": (45, 90), "z_in": (.75, 1.5), "alvo": (.07, .14)}
RANKING = ["C4 Mineradoras vs metal"]

CONJ = {"todos": list(M.PARES), "ouro": ["GDX x GLD", "GDXJ x GDX"],
        "sem_cobre_prata": ["GDX x GLD", "GDXJ x GDX", "VALE x BHP/RIO"]}

# perna H: candidatos em ordem de preferência (futuro inteiro, senão ETF)
ROTAS = {
    "auto": {"GLD": "1OZ|MGC|GLD", "SLV": "MicroPrata|SLV", "CPER": "MHG|CPER"},
    "so_etf": {"GLD": "GLD", "SLV": "SLV", "CPER": "CPER"},
    "so_futuro": {"GLD": "1OZ|MGC", "SLV": "MicroPrata", "CPER": "MHG"},
    "historico": {"GLD": "1OZ|MGC|GLD", "SLV": "MicroPrata|SLV", "CPER": "MHG|CPER"},
}
FUT = {  # contrato: (nível Yahoo p/ contar, ETF proxy do retorno, mult, margem, custo US$/lado, taxa do ETF a.a., rolagens/ano, desde)
    "1OZ": ("GC=F", "GLD", 1.0, .12, .80, .0040, 6, "2025-01-13"),
    "MGC": ("GC=F", "GLD", 10.0, .06, 1.50, .0040, 6, "2010-10-04"),
    "MicroPrata": ("SI=F", "SLV", 1000.0, .13, 3.50, .0050, 5, "2011-01-01"),
    "MHG": ("HG=F", "CPER", 2500.0, .10, 1.60, .0097, 4, "2021-08-09"),
}
ALUGUEL = {"GDX": .0042, "GDXJ": .0055, "SIL": .0052, "SLV": .0042, "COPX": .0045, "CPER": .0028, "FCX": .0041, "VALE": .0025,
           "BHP": .0063, "RIO": .0030, "GLD": .0043}
SPREAD = {"SIL": .001, "COPX": .001, "CPER": .001, "GDXJ": .0007}          # meio spread por lado (demais .0005)

INSTRUMENTOS = ("IBKR (EUA): GDX, GDXJ, SIL, COPX, FCX, VALE, BHP, RIO (ETF/ação; compra fracionária, venda em ações inteiras, Reg T, "
                "US$ 0,0035/ação mín. US$ 0,35; aluguel 0,25–0,63% a.a.); perna do metal: 1OZ (1 oz ouro, ~US$ 4,2 mil, margem ~12%, "
                "~US$ 0,80/lado), MGC (10 oz, ~US$ 42 mil), micro prata (1.000 oz, ~US$ 56 mil), MHG (2.500 lb, ~US$ 16,5 mil) em "
                "contratos inteiros — se não couber, GLD/SLV/CPER em ações. Caixa: Tesouro Selic/CDB no Brasil; na IBKR só margem + Reg T.")
APLICAVEL = True
MOTIVO = ("Operável: o ouro cabe no 1OZ (1 oz) com R$ 20–50 mil; cobre (MHG) e prata (micro) não cabem em contratos inteiros e vão "
          "para CPER/SLV em ações na IBKR; GDXJ x GDX e VALE x BHP/RIO só com ações. Só margem/Reg T fora (não o capital inteiro).")
ALAVANCAGENS = [1, 1.5, 2]
MOTIVO_ALAV = ("5x não é viável: as pernas em ação na IBKR exigem 100% do comprado + 50% do vendido em dinheiro (Reg T); com 6 pares a 5x o "
               "dinheiro fora passaria do capital (o motor recusa abrir o par quando o dinheiro fora do CDI > 95% do capital). "
               "1,5x/2x rodam; contratos inteiros fazem a alavancagem efetiva diferir da nominal.")
VARIANTES = {"sem hedge cambial (sem WDO)": {"hedge_fx": "nenhum"}, "sem empréstimo de margem (compra à vista)": {"financia": "caixa"}, "metal só em ETF (sem futuro)": {"rota": "so_etf"}, "metal só em futuro (par sem futuro inteiro não abre)": {"rota": "so_futuro"},
             "histórico (1OZ só desde 2025, MHG desde ago/2021)": {"rota": "historico"}, "só pares de ouro": {"pares": "ouro"},
             "sem cobre/prata": {"pares": "sem_cobre_prata"}}


# ---------------------------------------------------------------- dados
def carrega():
    d = M.carrega()                                                    # preços ajustados (Yahoo) dos 11 papéis + T-bill
    niv = pd.read_parquet(U.FD / "y_idx.parquet")[["GC=F", "SI=F", "HG=F"]]
    d["niveis"] = niv[~niv.index.duplicated(keep="last")]
    d["cupom"] = C.ler("carry_moedas/cupom_frc.csv")["cupom_frc_aa_pct"]      # cupom cambial do 1º FRC (2019+), para o hedge com WDO
    d["precos_limpos"] = M._limpa_niveis(d["precos"].apply(M._no_calendario))   # limpeza de print (olha 8 dias à frente, ver mineradoras.py)
    return d


_CACHE = {}


def _chave(d, *a):
    p = d["precos_limpos"]
    return (id(d), len(p), p.index.max(), len(d["niveis"]), d["niveis"].index.max()) + a


def _sinais(d, jan, z_in, alvo, pares):
    k = _chave(d, "s", jan, round(z_in, 6), round(alvo, 6), pares)
    if k in _CACHE:
        return _CACHE[k]
    P = d["precos_limpos"]
    tb = M._no_calendario(d["tb"]).fillna(0)
    ex = lambda t: M._limpa(P[t].pct_change(fill_method=None)) - tb
    R, B = {}, {}
    for kk in CONJ[pares]:
        a, hs = M.PARES[kk]
        rh = sum(ex(h) for h in hs) / len(hs)
        B[kk] = M._beta(ex(a), rh)
        R[kk] = ex(a) - B[kk] * rh
    R = pd.DataFrame(R).reindex(C.DIAS)
    R = R.where(R.notna().cumsum() > 0)
    B = pd.DataFrame(B).reindex(C.DIAS)
    S, Mo = M._histerese(M._semanal(M._zscore(R, jan)), z_in)
    v = R.rolling(63, min_periods=40).std().shift(1) * np.sqrt(252)
    W = (S * (alvo / np.sqrt(R.shape[1])) / v).replace([np.inf, -np.inf], 0).fillna(0).clip(-2, 2).where(S != 0, 0)
    out = (np.sign(W), W.abs(), B, R, Mo)
    if len(_CACHE) > 40:
        _CACHE.clear()
    _CACHE[k] = out
    return out


def _instrumentos(d, rota):
    P = d["precos_limpos"]
    tb = M._no_calendario(d["tb"]).fillna(0)
    inst = {}
    for t in P.columns:
        inst[t] = {"tipo": "ibkr", "P": P[t], "spread": SPREAD.get(t, .0005), "aluguel": ALUGUEL.get(t, .005)}
    niv = d["niveis"].apply(PP.no_calendario)
    for c, (nv, etf, mult, marg, cst, taxa, rol, desde) in FUT.items():
        cont = niv[nv]
        if rota == "historico":
            cont = cont.where(cont.index >= desde)
        rx = M._limpa(P[etf].pct_change(fill_method=None)) - tb + taxa / 252
        inst[c] = {"tipo": "fut", "cont": cont, "rx": rx, "mult": mult, "margem": marg, "custo": cst, "rolagens": rol}
    return inst


def _pernas(pares, rota):
    out = {}
    for kk in CONJ[pares]:
        a, hs = M.PARES[kk]
        out[kk] = [("A", a, None)] + [("H", ROTAS[rota].get(h, h), 1 / len(hs)) for h in hs]
    return out


EXEC = {"rota": "auto", "hedge_fx": "wdo", "financia": "margem"}     # execução padrão (as VARIANTES trocam uma peça por vez)


def _roda(d, capital, custo_mult, lag, alavancagem, jan, z_in, alvo, pares, validacao=False, **ex):
    ex = {**EXEC, **ex}
    k = _chave(d, "m", capital, custo_mult, lag, alavancagem, jan, round(z_in, 6), round(alvo, 6), pares, validacao, tuple(sorted(ex.items())))
    if k in _CACHE:
        return _CACHE[k]
    S, Wa, B, R, Mo = _sinais(d, jan, z_in, alvo, pares)
    res = PP.motor(S, Wa, B, _pernas(pares, ex["rota"]), _instrumentos(d, ex["rota"]), capital, alavancagem, lag, custo_mult, validacao,
                   ex["hedge_fx"], d["cupom"], ex["financia"])
    if len(_CACHE) > 60:
        _CACHE.clear()
    _CACHE[k] = res
    return res


# ---------------------------------------------------------------- contrato
def excesso(d, capital=20000, custo_mult=1, lag=0, regime=REGIME, alavancagem=1, jan=PARAMS["jan"], z_in=PARAMS["z_in"],
            alvo=PARAMS["alvo"], pares=PARAMS["pares"], validacao=False, **ex):
    res = _roda(d, capital, custo_mult, lag, alavancagem, jan, z_in, alvo, pares, validacao, **ex)
    return C.aplica_regime(res["e"], regime, CUSTO_TROCA * custo_mult)


def classes_ir(d, capital=20000, jan=PARAMS["jan"], z_in=PARAMS["z_in"], alvo=PARAMS["alvo"], pares=PARAMS["pares"], **ex):
    return _roda(d, capital, 1, 0, 1, jan, z_in, alvo, pares, **ex)["classes"]


def posicoes(d, capital=20000, jan=PARAMS["jan"], z_in=PARAMS["z_in"], alvo=PARAMS["alvo"], pares=PARAMS["pares"]):
    """Pesos do sinal (fração do capital na perna da mineradora) e retorno em excesso do par (para placebo/atribuição)."""
    S, Wa, B, R, Mo = _sinais(d, jan, z_in, alvo, pares)
    return S * Wa, R


def negocios(d, capital=20000, jan=PARAMS["jan"], z_in=PARAMS["z_in"], alvo=PARAMS["alvo"], pares=PARAMS["pares"], lag=0, **ex):
    res = _roda(d, capital, 1, lag, 1, jan, z_in, alvo, pares, **ex)
    return PP.tabela_negocios(res)


def diagnostico(d, capital=20000, **kw):
    """Quantos pares não couberam, rotas usadas, dinheiro médio fora do CDI."""
    p = {**PARAMS, **{k: v for k, v in kw.items() if k in PARAMS}}
    ex = {k: v for k, v in kw.items() if k not in PARAMS}
    res = _roda(d, capital, 1, 0, 1, p["jan"], p["z_in"], p["alvo"], p["pares"], **ex)
    ng = PP.tabela_negocios(res)
    nc = pd.DataFrame(res["naocoube"], columns=["par", "data"])
    o = lambda s: s[s.index >= CORTE]
    return {"negocios por rota": ng.groupby("rota").size().to_dict(), "nao coube por par": nc.groupby("par").size().to_dict(),
            "saldo IBKR medio OOS R$": round(float(o(res["saldo"]).mean())), "exigido medio OOS R$": round(float(o(res["exigido"]).mean())),
            "WDO vendidos (media OOS)": round(float(-o(res["n_wdo"]).mean()), 2),
            "nocional bruto medio OOS / capital": round(float(o(res["nocional"]).sum(axis=1).mean() / capital), 2)}
