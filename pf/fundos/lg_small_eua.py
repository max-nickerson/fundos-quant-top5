"""
(6) Small caps dos EUA (componentes do S&P 600, proxy do IWM) — noite depois de queda forte, com spread estimado.

Mesa: o equivalente das small caps líquidas da B3. Small caps americanas têm o maior desconto de liquidez no fechamento: vendas de
fundos de small caps com resgate, ETFs (IWM/IJR) rebalanceando no MOC, margin call de varejo e 'tax-loss' em dezembro concentram a
pressão no leilão de fechamento da Nasdaq/NYSE; a abertura devolve parte. Para PF o ponto fraco é o custo: o leilão tem preço único,
mas o leilão de abertura/fechamento de small cap é raso e o preço do leilão anda com a ordem — cobro METADE DO SPREAD estimado
(Abdi & Ranaldo 2017, só com OHLC passado de 250 pregões, entre 2 e 50 bps: a média de 60 dias é dominada pela volatilidade do
tombo e dá 34 bps de média com mediana de 2 bps) por lado, além da comissão da IBKR (US$ 0,0035/ação, mín. US$ 0,35).
Universo: composição ATUAL do S&P 600 (Wikipedia) -> viés de sobrevivência: faltam os papéis que quebraram/foram deslistados (o pior
caso de 'comprar a queda'); numa noite só ele é pequeno, mas é a favor da estratégia. Preço >= US$ 5, volume médio >= adv_min.
"""
import lg_comum as L

C, pf = L.C, L.pf
NOME = "Noite após queda forte — small caps dos EUA (S&P 600, spread estimado, IBKR)"
TESE = ("Compro no MOC as small caps americanas que caíram forte no dia (resgates, ETFs de small caps e margin call vendem no fechamento) "
        "e vendo no MOO; pago meio spread estimado por lado")
BENCHMARK = "CDI"
INICIO, CORTE = "2012-01-02", "2021-01-01"
REGIME = "nenhum"
CUSTO_TROCA = .001
CLASSE_IR = "exterior"
PARAMS = {"limiar": .08, "n": 6, "adv_min": 2e7}               # melhor no IS (grade de 8)
GRADE = {"limiar": [.04, .08], "n": [3, 6], "adv_min": [5e6, 2e7]}
VIZINHANCA = {"limiar": (.03, .09), "n": (2, 7), "adv_min": (3e6, 3e7)}
INSTRUMENTOS = [{"onde": "IBKR (NYSE/Nasdaq)", "ticker": "componentes do S&P 600 (proxy do Russell 2000/IWM)", "lote": "1 ação",
                 "custo": "US$ 0,0035/ação mín. US$ 0,35 + meio spread estimado (Abdi-Ranaldo) por lado; margem 1 dia"}]
APLICAVEL = True
MOTIVO = "MOC até 15h50 ET (NYSE) / 15h55 (Nasdaq) e MOO no dia seguinte; precisa de rotina diária (API da IBKR ou à mão)"
ALAVANCAGENS = [1, 1.5, 2]
MOTIVO_ALAV = "Reg T: até 2x numa noite; juros de margem de 1 dia por noite"


def carrega():
    return {"small": L.ler("small")}


def roda(d, capital=20000, custo_mult=1, lag=0, alavancagem=1, limiar=.05, n=4, adv_min=5e6):
    g = L.grupo(d, "small", sorted(d["small"]["ticker"].unique()))
    liq = (L.adv_usd(g, "USD") >= adv_min) & (g["C"] >= 5)
    sc = L.score_queda(g, limiar, "rel", liq)
    slip = L.meio_spread_ar(g, janela=250, teto=.005)            # 1 ano de OHLC: a estimativa de 60 dias explode depois do tombo
    return L.roda_ibkr([{"g": g, "mkt": "US", "score": sc, "slip": slip}], capital, int(n), lag, custo_mult, alavancagem)


excesso, classes_ir, posicoes, negocios, _roda = L.interface(roda, PARAMS, REGIME, CUSTO_TROCA)
