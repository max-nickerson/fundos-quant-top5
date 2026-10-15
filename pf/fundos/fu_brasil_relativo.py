"""
Spread entre mercados: Ibovespa (WIN) x S&P (MES) no PÂNICO RELATIVO do Brasil — compra o Brasil que caiu sozinho.

Tese de mesa: metade do giro da B3 é estrangeiro. Quando o Brasil cai MUITO mais do que o S&P explicaria (ruído fiscal/político local,
resgate de fundos de emergentes, saída do EWZ), quem vende é o investidor de fora que corta "Brasil" de uma vez — fundos de emergentes
com resgate, ETFs com redenção, mandatos com limite de perda — e o comprador local (fundos de ações com patrimônio estável) não absorve
no mesmo dia. Compro 1 WIN quando o retorno de 5 dias do Ibovespa EM DÓLAR menos beta x S&P (resíduo) fica abaixo de −k desvios e seguro
H pregões. "abs" (queda do Ibovespa em R$ sem olhar o S&P) é o controle: se ele for igual, o "relativo" não acrescenta nada.

Perna de hedge (MES): o desenho de mesa seria vender beta x nocional do WIN em S&P. Só que 1 MES = US$ 5 x S&P ≈ US$ 39 mil ≈ R$ 210 mil,
5x o nocional de 1 WIN (≈ R$ 41 mil) e 10x R$ 20 mil: o nº inteiro de MES do hedge (arredondado) é ZERO com R$ 20 e 50 mil em todo o
período — o código calcula e registra, mas na prática o fundo fica só com o WIN (o WSP da B3, US$ 2,50 x S&P ≈ R$ 105 mil, também não
cabe). Petróleo x PETR4 (a outra ideia de spread entre mercados) é o mh_petroleo, já testado.

Contratos: WIN (B3) R$ 0,20 x Ibovespa (≈ R$ 41 mil), custo R$ 1,10/lado (emolumentos + meio tick), 6 rolagens/ano, garantia em
Tesouro Selic; MES (CME, IBKR) US$ 5 x S&P, US$ 1,25/lado (comissão + meio tick), margem ~7% (só se entrasse).
Retornos sem rolagem: WIN = Ibovespa (índice de retorno total) − CDI; MES = SPY (com dividendos) − T-bill. Preços de fechamento quase
simultâneos (B3 fecha 17h/18h de Brasília = 16h/17h de Nova York). Dados Yahoo 2008-2026; OOS desde 2021.
"""
import numpy as np
import pandas as pd

import fu_comum as F

NOME = "Brasil x S&P: WIN no pânico relativo (resíduo do Ibovespa em US$)"
TESE = "Compra 1 WIN quando o Ibovespa em dólar cai muito mais que beta x S&P (estrangeiro vendendo Brasil), segura H dias; hedge em MES não cabe"
BENCHMARK = "CDI"
INICIO, CORTE = "2008-01-01", "2021-01-01"
REGIME = "nenhum"
CUSTO_TROCA = 0.0
CLASSE_IR = "futuros_b3"
PARAMS = {"modo": "abs", "k": 1.5, "H": 5}          # maior excesso IS da grade (todas negativas no IS; o "rel" perde para o controle)
LANCAMENTO = {"MES": "2019-05-06"}
GRADE = {"modo": ["rel", "abs"], "k": [1.5, 2.0], "H": [5, 10]}
VIZINHANCA = {"k": (1.25, 2.25), "H": (3, 15)}
TETO_ALAV = 2.5
INSTRUMENTOS = [("B3", "WIN", "R$ 0,20 x Ibovespa (≈ R$ 41 mil)", "R$ 1,10/lado"), ("IBKR/CME", "MES", "US$ 5 x S&P (≈ R$ 210 mil)", "US$ 1,25/lado"),
                ("Tesouro Direto", "Tesouro Selic", "garantia", "0")]
APLICAVEL = True
MOTIVO = "WIN cabe (≈ 2x R$ 20 mil, 0,8x R$ 50 mil); o hedge em MES (≈ R$ 210 mil) arredonda para zero contratos — o fundo é WIN sem hedge."
ALAVANCAGENS = [1, 2]
MOTIVO_ALAV = "exposição-alvo 1x/2x em WIN inteiros (teto 2,5x o capital)."


def carrega():
    return {"px": F.ler("br_eua.parquet")}


def _contratos(d):
    def f():
        x = d["px"]
        idx = F.pf.DIAS[(F.pf.DIAS >= x["^BVSP"].first_valid_index()) & (F.pf.DIAS <= x.index.max())]
        ib = F.nivel(x["^BVSP"], idx)
        r_win = ib.pct_change(fill_method=None).fillna(0) - F.pf.CDI.reindex(idx).fillna(0)
        win = F.contrato(r_win, ib, .20, "BRL", idx, None, 1.10, 0.0, rol=6, local="b3")
        spy, spx = F.nivel(x["SPY"], idx), F.nivel(x["^GSPC"], idx)
        tb = F.C.TB_US.reindex(idx, method="ffill").fillna(0)
        dias = pd.Series(idx, index=idx).diff().dt.days.fillna(1)
        r_mes = spy.pct_change(fill_method=None).fillna(0) - tb * dias * 252 / 365
        mes = F.contrato(r_mes, spx, 5.0, "USD", idx, None, 1.25, .07, rol=4)
        return win, mes, ib, spy
    return F.memo("brrel", (d["px"],), f)


def gera(d, capital=20000, regime=REGIME, alavancagem=1, modo="rel", k=1.5, H=5):
    win, mes, ib, spy = _contratos(d)
    ptax = F.nivel(F.PTAX_FULL, win.index)
    rb = np.log(ib / ptax).diff() if modo == "rel" else np.log(ib).diff()
    rs = np.log(spy).diff()
    if modo == "rel":
        beta = (rb.rolling(252, min_periods=150).cov(rs) / rs.rolling(252, min_periods=150).var()).clip(0, 2)
        res = rb - beta * rs
    else:
        beta, res = pd.Series(0.0, index=rb.index), rb
    z = res.rolling(5).sum() / (res.rolling(252, min_periods=150).std() * np.sqrt(5))
    lado = F.segura((z <= -k).astype(float), H)
    n = F.n_por_exposicao(win, capital, alavancagem).clip(lower=1)
    n = n.where(win["noc"] * n <= TETO_ALAV * alavancagem * capital, 0)
    nw = (lado * n).fillna(0)
    # hedge: beta do Ibovespa em R$ contra o S&P em US$ x nocional do WIN / nocional de 1 MES, arredondado (dá 0 com R$ 20-50 mil)
    beta_brl = (np.log(ib).diff().rolling(252, min_periods=150).cov(rs) / rs.rolling(252, min_periods=150).var()).clip(0, 2)
    nm = -np.floor(beta_brl * nw * win["noc"] / mes["noc"] + .5).fillna(0) if modo == "rel" else nw * 0
    return pd.DataFrame({"WIN": nw, "MES": nm}), {"WIN": win, "MES": mes}


F.montar(globals(), gera, carrega)
