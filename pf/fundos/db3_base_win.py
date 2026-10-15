"""
Base WIN x BOVA11 nos dias antes do vencimento, em tamanho de varejo (1 WIN contra ~200 cotas de BOVA11).

Tese de mesa: nos ~10 pregões antes do vencimento a ponta curta do índice futuro sofre a pressão da rolagem (quem carrega comprado
rola para o próximo e vende o vencimento; o arbitrador institucional precisa de balanço para montar o "cash and carry"). A taxa
implícita do WIN contra o Ibovespa, (F/Ibov)^(252/du) − 1, se afasta do CDI. Se está acima de CDI + limiar: vendo WIN e compro BOVA11
(recebo mais que o CDI até o vencimento, quando o futuro converge ao índice); abaixo de CDI − limiar: compro WIN e vendo BOVA11 alugado.
Na pesquisa (arbitragem.md A9, institucional) deu +0,7 pp a.a. sobre o CDI com vol de 1% — mas a taxa medida fica quase sempre ABAIXO
do CDI, e parte disso pode ser descasamento de horário (^BVSP x ajuste) e o ajuste final ser média, não fechamento.

Pessoa física: 1 WIN = 0,2 x Ibov (R$ 25–41 mil) => ~200 cotas de BOVA11 (mesmo nocional). Comprar BOVA11 exige o dinheiro (não rende
CDI): com R$ 20 mil só cabe quando 200 cotas ≤ capital x alav; vender BOVA11 exige alugar: corretora cobra ~0,5% do volume por contrato
de aluguel (Clear/Rico) + taxa ao doador ~1% a.a. — o custo do lado "reverso" é 0,5% de saída contra um ganho médio de ~0,1%.

Implementação: ajustes do IND/WIN nos 12 pregões antes de cada vencimento (boletim BVBG.086, quant/fundos/dados/arb_ind.parquet,
2019+); Ibovespa = ^BVSP (Yahoo); BOVA11 = fechamento + proventos. Sinal no fechamento de t (dentro da janela de `dias` pregões antes do
vencimento), execução no fechamento de t+1 (WIN no ajuste, BOVA11 no fechamento), segura até o vencimento (WIN liquida no ajuste do dia
do vencimento = índice de liquidação; BOVA11 vendida/recomprada no fechamento). P&L diário: WIN = n x 0,2 x ΔF; BOVA11 = ±q x S(t−1) x
(r_total − CDI) (dinheiro da compra sai do CDI; o da venda a descoberto fica em Selic). Custos: WIN R$ 1,10/lado; BOVA11 0,11%/lado;
aluguel 0,5% do volume + 1% a.a. IR: WIN "futuros_b3", BOVA11 "etf_b3" (15%, sem isenção). Corte 2023.
"""
import numpy as np
import pandas as pd

import db3_base as B

NOME = "Base WIN x BOVA11 no vencimento (varejo)"
TESE = "Antes do vencimento: se a taxa implícita do WIN > CDI + limiar vendo WIN/compro BOVA11; se < CDI − limiar o inverso (aluguel)"
BENCHMARK = "CDI"
INICIO, CORTE = "2019-02-01", "2023-01-01"
REGIME, CUSTO_TROCA = "nenhum", 0.0
PARAMS = {"limiar": .01, "dias": 10, "lado": "direto"}   # maior IR no IS (todas negativas)
GRADE = {"limiar": [.01, .02], "dias": [5, 10], "lado": ["ambos", "direto"]}
VIZINHANCA = {"limiar": (.008, .03), "dias": (4, 12)}
MULT, CUSTO_WIN = .2, 1.10
ALUGUEL_CORRETORA, ALUGUEL_DOADOR = P_ALUG = (.005, .01)
INSTRUMENTOS = [{"onde": "B3", "ticker": "WIN (vencimento corrente)", "lote": "0,2 x Ibovespa", "custo": "R$ 1,10/contrato/lado"},
                {"onde": "B3", "ticker": "BOVA11 (compra ou venda com aluguel)", "lote": "1 cota", "custo": "0,11%/lado; aluguel 0,5% + 1% a.a."}]
APLICAVEL = False
MOTIVO = ("Monta, mas não paga: com R$ 20 mil o lado 'direto' (comprar ~R$ 25–41 mil de BOVA11) não cabe sem alavancagem e o lado "
          "'reverso' paga 0,5% de aluguel na corretora por operação, contra um ganho bruto médio de ~0,1% por vencimento.")
ALAVANCAGENS = [1, 2]
MOTIVO_ALAV = "Alavancagem 2 permite o lado direto com R$ 20 mil (BOVA11 como garantia do WIN). 5x: não há nocional que justifique."


def carrega():
    a = pd.read_parquet(B.FD / "arb_ind.parquet").dropna(subset=["AdjstdQt"])
    a = a[a.ticker.str.startswith("WIN")].rename(columns={"date": "data", "AdjstdQt": "ajuste"})[["data", "ticker", "ajuste"]]
    S, R = B.painel_acoes(B.acoes(("BOVA11",)))
    y = B.yahoo_idx(("^BVSP",))
    return {"win": a.reset_index(drop=True), "S": S, "R": R, "ibov": y["^BVSP"].dropna().to_frame("ibov")}


def _venc(t):
    from db3_win_regime import venc_win
    a, m = 2000 + int(t[4:6]), "FGHJKMNQUVXZ".index(t[3]) + 1
    return [v for v in venc_win(a) if v.month == m][0]


def _livro(d, capital, lag, custo_mult, alavancagem, p):
    w = d["win"]
    ib = d["ibov"]["ibov"].reindex(B.DIAS).ffill(limit=3)
    S = d["S"]["BOVA"].reindex(B.DIAS).ffill(limit=3)
    R = d["R"]["BOVA"]
    pw = pd.Series(0.0, index=B.DIAS)
    pb = pd.Series(0.0, index=B.DIAS)
    neg = []
    for tk, g in w.groupby("ticker"):
        v = _venc(tk)
        g = g.set_index("data").ajuste.sort_index()
        g = g[g.index <= v]
        if v not in g.index or len(g) < 3:
            continue                                                   # sem o ajuste de liquidação: ciclo fora
        janela = B.DIAS[(B.DIAS < v)][-int(p["dias"]):]
        ent = None
        for t in janela:
            F, I0 = g.get(t, np.nan), ib.get(t, np.nan)
            du = B.du(t, v)
            if not (F == F and I0 == I0) or du < 2:
                continue
            taxa = (F / I0) ** (252 / du) - 1
            gap = taxa - B.CDI_AA.get(t, np.nan)
            lado = -1 if gap > p["limiar"] else (1 if gap < -p["limiar"] and p["lado"] == "ambos" else 0)
            if lado:
                ent = (t, lado, gap)
                break
        if ent is None:
            continue
        t, lado, gap = ent
        dd = B.DIAS[B.DIAS > t]
        if len(dd) <= lag or dd[lag] >= v:
            continue
        d0 = dd[lag]
        F0, S0, I0 = g.get(d0, np.nan), S.get(d0, np.nan), ib.get(d0, np.nan)
        if not (F0 == F0 and S0 == S0 and I0 == I0):
            continue
        n = max(1, round(capital * alavancagem / (MULT * F0)))
        q = round(n * MULT * F0 / S0)
        if lado < 0 and q * S0 > capital * alavancagem:               # compra de BOVA11 com dinheiro próprio
            continue
        if lado > 0 and q * S0 > 2 * capital * alavancagem:           # venda a descoberto: garantia em Selic
            continue
        dias = B.DIAS[(B.DIAS >= d0) & (B.DIAS <= v)]
        Fs = g.reindex(dias).ffill()
        x_w = lado * n * MULT * Fs.diff().fillna(0)                    # lado do WIN: +1 comprado
        x_w.iloc[0] -= n * CUSTO_WIN * custo_mult
        x_w.iloc[-1] -= n * CUSTO_WIN * custo_mult                     # liquidação no vencimento
        sb = -lado                                                     # BOVA11 do lado oposto
        val = q * S.reindex(dias).ffill()
        x_b = sb * val.shift(1).fillna(0) * (R.reindex(dias).fillna(0) - B.CDI.reindex(dias).fillna(0))
        x_b.iloc[0] -= q * S0 * B.CUSTO_ACAO * custo_mult
        x_b.iloc[-1] -= val.iloc[-1] * B.CUSTO_ACAO * custo_mult
        if sb < 0:
            x_b.iloc[0] -= q * S0 * ALUGUEL_CORRETORA * custo_mult
            x_b -= val.shift(1).fillna(0) * ALUGUEL_DOADOR / 252 * custo_mult
        pw = pw.add(x_w, fill_value=0)
        pb = pb.add(x_b, fill_value=0)
        tot = float(x_w.sum() + x_b.sum())
        neg.append(dict(ativo=tk, lado=lado, entrada=d0, saida=v, contratos=n, cotas=q, gap_aa=gap, pnl_rs=tot,
                        **{"retorno_%": tot / (q * S0) * 100}))
    return pw, pb, neg


def excesso(d, capital=20000, custo_mult=1, lag=0, regime=REGIME, alavancagem=1, **params):
    pw, pb, _ = _livro(d, capital, lag, custo_mult, alavancagem, {**PARAMS, **params})
    return B.fecha((pw + pb) / capital, regime, CUSTO_TROCA, custo_mult)


def classes_ir(d, capital=20000, **params):
    pw, pb, _ = _livro(d, capital, 0, 1, 1, {**PARAMS, **params})
    return {"futuros_b3": pw, "etf_b3": pb}            # pb já é excesso sobre o CDI na parte comprada (aprox.: IR sobre o excesso)


def posicoes(d, capital=20000, **params):
    pw, pb, _ = _livro(d, capital, 0, 0, 1, {**PARAMS, **params})
    return B.wr_de_pnl({"WIN": pw, "BOVA11": pb}, capital)


def negocios(d, capital=20000, **params):
    *_, neg = _livro(d, capital, 0, 1, 1, {**PARAMS, **params})
    return B.negocios_df(neg, capital)
