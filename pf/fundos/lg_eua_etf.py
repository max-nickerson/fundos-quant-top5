"""
(1) EUA: noite de ETFs (SPY, QQQ, setoriais XL*, ...) e large caps do S&P 100 depois de um dia de queda forte, na IBKR.

Mesa: o equivalente americano do edge nº 1 da B3. Nos EUA o retorno das ações também mora na noite (o pregão devolve), e depois de um
dia de liquidação (ETFs alavancados/inversos rebalanceando no fechamento, CTAs e fundos de vol-alvo vendendo no MOC, margin calls de
varejo) o leilão de fechamento sai pressionado e a abertura devolve parte. Pessoa física compra com ordem MOC no leilão de fechamento
(sem spread; preço único) e vende com MOO no leilão de abertura. Diferença para a B3: o mercado americano é o mais arbitrado do mundo
(market makers, HFT e fundos de reversão de curto prazo competem pela mesma noite) e a conta fica na IBKR (remessa, câmbio, CDI perdido
sobre o saldo de margem).
Universo 'etf': 28 ETFs de ações dos EUA; 'acoes': S&P 100 (composição ATUAL -> viés de sobrevivência; numa noite só ele é pequeno, mas
os papéis que quebraram e saíram do índice não estão aqui). Sinal: retorno do dia (absoluto ou relativo à média do universo) <= -limiar;
até n noites por dia, as maiores quedas. Execução: ver lg_comum (hipótese do leilão de fechamento; lag=1 = fechamento seguinte).
IR: exterior (Lei 14.754/2023, 15% ao ano, compensação dentro do ano/anos seguintes).
"""
import lg_comum as L

C, pf = L.C, L.pf
NOME = "Noite após queda forte — ETFs/large caps dos EUA (IBKR, MOC->MOO)"
TESE = ("Compro no leilão de fechamento (MOC) os ETFs/large caps americanos que caíram forte no dia e vendo no leilão de abertura (MOO): "
        "vendedores forçados do fechamento (ETFs alavancados, vol-alvo, margin call) pressionam o leilão e a abertura devolve")
BENCHMARK = "CDI"
INICIO, CORTE = "2012-01-02", "2021-01-01"
REGIME = "nenhum"
CUSTO_TROCA = .001
CLASSE_IR = "exterior"
ETF = ["SPY", "QQQ", "DIA", "IWM", "MDY", "XLK", "XLF", "XLE", "XLV", "XLI", "XLY", "XLP", "XLU", "XLB", "XLRE", "XLC", "SMH", "XBI",
       "KRE", "XRT", "XHB", "XOP", "GDX", "IYR", "OIH", "IBB", "ITB", "XME"]
PARAMS = {"universo": "etf", "modo": "abs", "limiar": .02, "n": 3}
GRADE = {"universo": ["etf", "acoes"], "modo": ["abs", "rel"], "limiar": [.02, .04]}
VIZINHANCA = {"limiar": (.015, .045), "n": (2, 5)}
INSTRUMENTOS = [{"onde": "IBKR (conta de margem Reg T, só o necessário: ~50% da posição)", "ticker": "SPY/QQQ/XL*/... ou S&P 100",
                 "lote": "1 ação", "custo": "US$ 0,0035/ação mín. US$ 0,35 por ordem + 1 bp de derrapagem no leilão; margem T-bill+1,5% por 1 dia"}]
APLICAVEL = True
MOTIVO = ("MOC até 15h50 ET (16h50/17h50 de Brasília) e MOO no dia seguinte: dá para fazer à mão ou com a API da IBKR; exige decidir com o "
          "preço das 15h50 (o sinal usa o fechamento -> ver t+2)")
ALAVANCAGENS = [1, 1.5, 2]
MOTIVO_ALAV = "Reg T: posição de uma noite até 2x o patrimônio na conta (exigência inicial 50%); a noite paga juros de margem de 1 dia"


def roda(d, capital=20000, custo_mult=1, lag=0, alavancagem=1, universo="etf", modo="abs", limiar=.02, n=3):
    tick = ETF if universo == "etf" else L.lista("sp100")
    g = L.grupo(d, "eua", tick)
    liq = L.adv_usd(g, "USD") >= 1e7
    sc = L.score_queda(g, limiar, modo, liq)
    return L.roda_ibkr([{"g": g, "mkt": "US", "score": sc}], capital, int(n), lag, custo_mult, alavancagem)


def carrega():
    return {"eua": L.ler("eua")}


excesso, classes_ir, posicoes, negocios, _roda = L.interface(roda, PARAMS, REGIME, CUSTO_TROCA)
