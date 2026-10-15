"""
CRI/CRA IPCA+ isentos via balcão — carry isento de pessoa física, comprado nas plataformas (XP/BTG/Inter/Rico).

Tese de mesa: CRI e CRA são isentos para pessoa física (cupom e ganho) e pagam mais spread que a debênture incentivada do mesmo risco
porque o comprador institucional tributado não os quer (estrutura de securitização, pouca liquidez) e os fundos isentos são menores.
Compro os de maior spread sobre a NTN-B de mesma duration, com negócios frequentes (para ter preço), 1 por securitizadora/emissor, e
seguro até sumir do balcão (vencimento/amortização final) — vender antes paga o spread de varejo outra vez.

Implementação (balcão B3: PU desde 2023-03, mas a TAXA de CRI/CRA só a partir de abr/2025 -> amostra de 17 meses; corte OOS 2026-01-01;
resultado NÃO conclusivo, serve para medir custo de varejo e o tipo de risco que o carry carrega):
  - o balcão NÃO traz o cadastro do CRI/CRA (indexador, vencimento, fluxo). Indexador inferido pela taxa: mediana da taxa do papel
    entre 4,5 e 10,5 = IPCA+ (NTN-B 2023–26: 5,3–8%; prefixado de CRA nesse período negociou >= 10,5; DI+ < 4; %CDI > 80).
    Erro de classificação possível (prefixado a 9–10% em 2024) — documentado;
  - taxa de marcação = mediana das taxas do dia (>= 3 negócios com taxa); duration de MERCADO do papel = mediana (só passado) da
    inclinação ln(PU) x taxa dentro do mesmo dia (>= 5 negócios, faixa de taxa >= 0,2 pp); sem histórico: 2,9 (mediana da classe);
  - retorno diário = (1+IPCA do dia) x (1+taxa)^(1/252) - 1 - duration x Δtaxa (carry + IPCA - marcação); cupons/amortizações não
    importam porque o retorno vem da taxa, não do PU sujo;
  - custo de varejo: metade da faixa p10–p90 do PU do papel no dia (mediana móvel do passado; sem dado: 1,6%), na compra; na venda
    antecipada também; papel que some do balcão por 63 dias sai sem custo na última marca (vencimento ou papel parado — RISCO: um
    default que pare de negociar fica marcado na última taxa; ver caderno);
  - lotes de R$ 1 mil (CRI/CRA de varejo têm PU ~R$ 1 mil); 1/n do capital por papel;
  - IR: classe "isento".
"""
import numpy as np
import pandas as pd

import _rf_comum as K

NOME = "CRI/CRA IPCA+ isentos (balcão, varejo)"
TESE = "Carrego os CRI/CRA IPCA+ de maior spread sobre a NTN-B (isentos para PF), com preço frequente no balcão, até vencerem"
BENCHMARK = "CDI"
INICIO, CORTE = "2025-05-01", "2026-01-01"      # o balcão só traz a TAXA de CRI/CRA a partir de abr/2025
REGIME = "nenhum"
CUSTO_TROCA = 0.0
PARAMS = {"n": 10, "faca": 1, "spread_max": 4.0}             # escolhidos no IS (maior IR mai-dez/2025; todos negativos)
GRADE = {"n": [5, 10], "faca": [0, 1], "spread_max": [2.5, 4.0]}
VIZINHANCA = {"n": (6, 12), "spread_max": (2.5, 5.0)}
CLASSE_IR = "isento"
ALIQUOTAS = None
D_PADRAO, CUSTO_PADRAO, SUMIU = 2.9, .016, 63
INSTRUMENTOS = [{"onde": "XP / BTG / Inter / Rico (secundário de CRI/CRA)", "ticker": "CRI/CRA IPCA+ (código B3 tipo CRA022007EP / 22E1095384)",
                 "lote": "~R$ 1 mil", "custo": "spread embutido (metade da faixa p10–p90 do PU no dia, mediana ~1,5–2%) na compra e na venda antecipada"}]
APLICAVEL = True
MOTIVO = "Lotes de ~R$ 1–1,3 mil; com R$ 20 mil e 10 papéis só cabe 1 lote por papel (~55% do capital aplicado; o resto fica no CDI)."
ALAVANCAGENS = [1]
MOTIVO_ALAV = "CRI/CRA não aceitam alavancagem no varejo."


def carrega():
    return {"bal": K.ler("balcao_cri_cra_dia.parquet"), "td": K.ler("tesouro_direto.parquet"), "ipca": K.ler("ipca_mensal.csv")}


def painel(d):
    def f():
        x = d["bal"]
        x = x[(x.n_taxa >= 3)]
        tx = x.pivot_table(index="data", columns="codigo", values="taxa50", aggfunc="last").reindex(K.DIAS)
        # classificação do indexador só com o passado: mediana expandida da taxa do papel
        medx = tx.expanding(min_periods=3).median()
        ipca = (medx >= 4.5) & (medx <= 10.5)
        tx = tx.where((tx >= 2) & (tx <= 16))
        x2 = d["bal"]
        inc = (-x2.inclinacao * 100).where((-x2.inclinacao * 100).between(.2, 15))
        Dd = x2.assign(D=inc).pivot_table(index="data", columns="codigo", values="D", aggfunc="last").reindex(index=K.DIAS, columns=tx.columns)
        Dm = Dd.expanding(min_periods=1).median().shift(1).fillna(D_PADRAO)
        sp = (x2.pu90 / x2.pu10 - 1) / 2
        spr = x2.assign(s=sp.where(sp.between(0, .1) & (x2.n >= 5))).pivot_table(index="data", columns="codigo", values="s", aggfunc="last")
        spr = spr.reindex(index=K.DIAS, columns=tx.columns).expanding(min_periods=1).median().shift(1).fillna(CUSTO_PADRAO)
        obs = tx.notna()
        txf = tx.ffill()
        pos = np.arange(len(K.DIAS))[:, None]
        ult = pd.DataFrame(np.where(obs, pos, np.nan), index=K.DIAS, columns=tx.columns).ffill()
        idade = pd.DataFrame(pos - ult.to_numpy(), index=K.DIAS, columns=tx.columns)
        prim = obs.cumsum() > 0
        vivo = prim & (idade <= SUMIU)
        ipd = K.ipca_diario(d).to_numpy()[:, None]
        y0 = txf.shift(1)
        R = ((1 + ipd) * (1 + y0 / 100) ** (1 / 252) - 1 - Dm * (txf - y0) / 100).where(vivo & y0.notna()).fillna(0)
        ntnb = K.interp_curva(K.curva_real(d), Dm.clip(1, 30))
        S = txf - ntnb
        vol = x2.pivot_table(index="data", columns="codigo", values="vol", aggfunc="sum").reindex(index=K.DIAS, columns=tx.columns).fillna(0)
        freq = obs.rolling(21, min_periods=1).sum()
        emis = x2.groupby("codigo").emissor.first().reindex(tx.columns)
        elig = vivo & ipca.ffill().fillna(False) & (idade <= 2) & (freq >= 8) & (vol.rolling(21).sum() >= 1e6) & S.notna()
        pu = x2.pivot_table(index="data", columns="codigo", values="pu50", aggfunc="last").reindex(index=K.DIAS, columns=tx.columns).ffill()
        lote = pu * (1 + spr)
        return dict(tx=txf, obs=obs, vivo=vivo, R=R, S=S, D=Dm, spr=spr, elig=elig, emis=emis, lote=lote)
    return K.memo("cri_painel", d["bal"], f)


def _alvo(d, n, faca, spread_max):
    p = painel(d)
    S, el = p["S"], p["elig"]
    abriu = (p["tx"] - p["tx"].rolling(21, min_periods=5).min()) > .5          # taxa subiu > 50 bps em 21 dias: faca caindo
    base = el & (S < spread_max) & (S > -1)
    if faca:
        base &= ~abriu
    Sv, bv, vv = S.to_numpy(), base.to_numpy(), p["vivo"].to_numpy()
    em = p["emis"].to_numpy()
    A = np.zeros(S.shape)
    held = set()
    for t in range(len(K.DIAS)):
        held = {k for k in held if vv[t, k]}
        if len(held) < n:
            ems = {em[k] for k in held}
            for k in np.argsort(np.where(bv[t], -np.nan_to_num(Sv[t], nan=-99), 99)):
                if len(held) >= n or not bv[t, k]:
                    break
                if k in held or em[k] in ems:
                    continue
                held.add(k)
                ems.add(em[k])
        for k in held:
            A[t, k] = 1 / n
    return pd.DataFrame(A, index=K.DIAS, columns=S.columns)


def _livro(d, capital=20000, custo_mult=1, lag=0, n=PARAMS["n"], faca=PARAMS["faca"], spread_max=PARAMS["spread_max"]):
    p = painel(d)
    A = _alvo(d, n, faca, spread_max)
    return K.livro(A, p["R"], capital, lag, custo_ent=p["spr"], custo_sai=p["spr"], custo_mult=custo_mult, lote=p["lote"],
                   negocia=p["obs"], vivo=p["vivo"])


def excesso(d, capital=20000, custo_mult=1, lag=0, regime=REGIME, alavancagem=1, **params):
    e = _livro(d, capital, custo_mult, lag, **{**PARAMS, **params})["e"]
    return K.C.aplica_regime(e, regime, CUSTO_TROCA * custo_mult)


def classes_ir(d, capital=20000, **params):
    return K.classes_de_livro(_livro(d, capital, **{**PARAMS, **params}), capital, CLASSE_IR)


def posicoes(d, **params):
    p_ = {**PARAMS, **params}
    p = painel(d)
    return _alvo(d, p_["n"], p_["faca"], p_["spread_max"]), p["R"].sub(K.CDI, axis=0)


def negocios(d, capital=20000, **params):
    p = painel(d)
    ng = _livro(d, capital, **{**PARAMS, **params})["negocios"].copy()
    if len(ng):
        ng["emissor"] = ng.ativo.map(p["emis"])
        ng["taxa_entrada"] = [p["tx"].at[i, a] for a, i in zip(ng.ativo, ng.entrada)]
        ng["taxa_saida"] = [p["tx"].at[f, a] for a, f in zip(ng.ativo, ng.saida)]
        ng["spread_entrada"] = [p["S"].shift(1).at[i, a] for a, i in zip(ng.ativo, ng.entrada)]
        ng["custo_varejo_%"] = [p["spr"].at[i, a] * 100 for a, i in zip(ng.ativo, ng.entrada)]
    return ng
