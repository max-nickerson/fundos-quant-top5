"""
(7) O espelho e a variante: vender a descoberto no fechamento depois de ALTA forte (recomprar na abertura) e comprar no fechamento
depois de um GAP de baixa na abertura (ETFs e S&P 100 na IBKR).

Mesa: (a) 'alta' — se o leilão de fechamento depois de queda forte sai barato por venda forçada, o de alta forte deveria sair caro por
compra forçada (short squeeze, ETFs alavancados comprando no MOC, recompra de vendidos): vendo no MOC e recompro no MOO. O problema
estrutural é que a noite tem prêmio POSITIVO (o retorno das ações mora na noite) — o vendido paga esse prêmio todas as noites. Venda a
descoberto na IBKR: papéis 'easy to borrow' (aluguel ~0,3% a.a., 1 dia), Reg T 50%. (b) 'gap' — o papel abriu com gap de baixa
>= limiar (notícia da noite) e passou o dia sem recuperar; quem não conseguiu vender na abertura vende ao longo do dia e no MOC: compro
no fechamento e vendo na abertura seguinte. O sinal do gap usa a abertura de t e o fechamento de t (conhecidos no leilão).
"""
import lg_comum as L

C, pf = L.C, L.pf
NOME = "Noite após ALTA forte (vendido) ou após GAP de baixa (comprado) — ETFs/S&P 100 (IBKR)"
TESE = ("Vendo no MOC o que subiu forte no dia e recompro no MOO (espelho da compra forçada), ou compro no MOC o que abriu com gap de baixa "
        "e não recuperou (vendedor atrasado) e vendo no MOO")
BENCHMARK = "CDI"
INICIO, CORTE = "2012-01-02", "2021-01-01"
REGIME = "nenhum"
CUSTO_TROCA = .001
CLASSE_IR = "exterior"
ETF = ["SPY", "QQQ", "DIA", "IWM", "MDY", "XLK", "XLF", "XLE", "XLV", "XLI", "XLY", "XLP", "XLU", "XLB", "XLRE", "XLC", "SMH", "XBI",
       "KRE", "XRT", "XHB", "XOP", "GDX", "IYR", "OIH", "IBB", "ITB", "XME"]
PARAMS = {"modo": "gap", "universo": "etf", "limiar": .02, "n": 3}   # melhor no IS (grade de 8)
GRADE = {"modo": ["alta", "gap"], "universo": ["etf", "acoes"], "limiar": [.02, .04]}
VIZINHANCA = {"limiar": (.015, .05), "n": (2, 5)}
INSTRUMENTOS = [{"onde": "IBKR (NYSE/Nasdaq)", "ticker": "SPY/QQQ/XL*/... e S&P 100", "lote": "1 ação",
                 "custo": "US$ 0,0035/ação mín. US$ 0,35 + 1 bp; vendido: aluguel ~0,3% a.a. por 1 dia; margem 1 dia"}]
APLICAVEL = True
MOTIVO = "MOC/MOO na IBKR; venda a descoberto só em papel 'easy to borrow' (todos os ETFs e S&P 100); regra de uptick não se aplica na alta"
ALAVANCAGENS = [1, 1.5, 2]
MOTIVO_ALAV = "Reg T: até 2x numa noite (comprado ou vendido); juros de margem de 1 dia"


def carrega():
    return {"eua": L.ler("eua")}


def roda(d, capital=20000, custo_mult=1, lag=0, alavancagem=1, modo="gap", universo="acoes", limiar=.04, n=3):
    g = L.grupo(d, "eua", ETF if universo == "etf" else L.lista("sp100"))
    liq = L.adv_usd(g, "USD") >= 1e7
    if modo == "alta":
        sc = L.score_alta(g, limiar, "abs" if universo == "etf" else "rel", liq)
        lado = -1
    else:
        gap = (g["O"] / g["C"].shift(1) - 1).where(liq)                # gap de abertura de t (desdobramento já ajustado no Yahoo)
        dia = g["C"] / g["O"] - 1                                       # o pregão não devolveu o gap
        sc = (-gap).where((gap <= -limiar) & (dia < -gap / 2) & (gap > -.4))
        lado = 1
    return L.roda_ibkr([{"g": g, "mkt": "US", "score": sc}], capital, int(n), lag, custo_mult, alavancagem, lado=lado)


excesso, classes_ir, posicoes, negocios, _roda = L.interface(roda, PARAMS, REGIME, CUSTO_TROCA)
