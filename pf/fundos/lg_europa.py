"""
(2) Europa: noite depois de queda forte em ações do DAX/CAC 40/FTSE 100 (Xetra, Euronext, LSE) ou ETFs da Europa (EWG/EWU/... em NY;
UCITS EXS1/ISF/CAC no local), na IBKR.

Mesa: o leilão de fechamento europeu (17h30 CET, call de 5 min com preço indicativo público) concentra 25-35% do volume do dia — é ali
que os fundos passivos e os vendedores forçados executam. A tese é a mesma da B3: quem precisa vender no dia (resgate, stop, rebalance)
paga o leilão e a abertura devolve. Diferença decisiva para pessoa física: IMPOSTO DE TRANSAÇÃO — stamp duty de 0,5% na compra de ações
do Reino Unido e FTT francesa de 0,2-0,4% na compra de ações francesas > EUR 1 bi; Alemanha/Holanda não têm. Mais a comissão mínima da
IBKR na Europa (EUR 1,25 / GBP 1 por ordem, ~10 bps numa ordem de EUR 1.100). ETFs (UCITS e os americanos) não pagam stamp/FTT.
Universo 'local': componentes ATUAIS do DAX, CAC 40 e FTSE 100 (viés de sobrevivência), uma decisão conjunta no leilão das 17h30 CET.
'etf_eua': EWG, EWU, EWQ, EWP, EWI, EWL, EWN, FEZ, VGK, EWD (negociados em NY: a noite deles contém a manhã européia).
'ucits': EXS1.DE (DAX), ISF.L (FTSE 100), CAC.PA (CAC 40).
"""
import lg_comum as L

C, pf = L.C, L.pf
NOME = "Noite após queda forte — Europa (DAX/CAC/FTSE ou ETFs, IBKR)"
TESE = ("Compro no leilão de fechamento europeu (ou MOC em NY nos ETFs de país) o que caiu forte no dia e vendo no leilão de abertura; "
        "custos reais de varejo: comissão mínima IBKR, stamp duty 0,5% (UK), FTT 0,2-0,4% (França)")
BENCHMARK = "CDI"
INICIO, CORTE = "2012-01-02", "2021-01-01"
REGIME = "nenhum"
CUSTO_TROCA = .001
CLASSE_IR = "exterior"
ETF_EUA = ["EWG", "EWU", "EWQ", "EWP", "EWI", "EWL", "EWN", "FEZ", "VGK", "EWD"]
UCITS = ["EXS1.DE", "ISF.L", "CAC.PA"]
PARAMS = {"universo": "etf_eua", "limiar": .02, "n": 2}          # melhor no IS (grade de 12)
GRADE = {"universo": ["local", "etf_eua", "ucits"], "limiar": [.02, .04], "n": [2, 3]}
VIZINHANCA = {"limiar": (.015, .045)}
INSTRUMENTOS = [{"onde": "IBKR (Xetra/Euronext/LSE ou NYSE Arca)", "ticker": "ações DAX/CAC/FTSE; EWG/EWU/...; EXS1/ISF/CAC",
                 "lote": "1 ação", "custo": "0,05% mín. EUR 1,25/GBP 1; stamp 0,5% UK; FTT 0,2-0,4% FR; 1 bp de derrapagem; margem 1 dia"}]
APLICAVEL = True
MOTIVO = ("ordens no leilão de fechamento (Xetra/Euronext/LSE aceitam MOC/LOC na IBKR) às 12h25-13h25 de Brasília e MOO às 4h-5h: "
          "precisa de API/ordem programada; impostos de transação matam a versão em ações UK/FR")
ALAVANCAGENS = [1, 1.5, 2]
MOTIVO_ALAV = "Reg T na IBKR: até 2x o patrimônio da conta numa noite; juros de margem de 1 dia por noite"


def carrega():
    return {"europa": L.ler("europa"), "eua": L.ler("eua")}


def roda(d, capital=20000, custo_mult=1, lag=0, alavancagem=1, universo="local", limiar=.02, n=3):
    if universo == "etf_eua":
        g = L.grupo(d, "eua", ETF_EUA)
        G = {"g": g, "mkt": "US", "score": L.score_queda(g, limiar, "abs", L.adv_usd(g, "USD") >= 2e6)}
    elif universo == "ucits":
        g = L.grupo(d, "europa", UCITS)
        G = {"g": g, "mkt": None, "score": L.score_queda(g, limiar, "abs")}
    else:
        tk = [t for t in L.lista("dax") + L.lista("cac") + L.lista("ftse") if t not in UCITS]
        g = L.grupo(d, "europa", list(dict.fromkeys(tk)))
        adv = None
        for m in ("DE", "PA", "AS", "L"):
            cc = [c for c in g["C"].columns if L.mercado(c) == m]
            a = L.adv_usd({k: v[cc] for k, v in g.items()}, L.MERC[m][0]).reindex(columns=g["C"].columns).fillna(0)
            adv = a if adv is None else adv + a
        G = {"g": g, "mkt": None, "score": L.score_queda(g, limiar, "rel", adv >= 1e7)}
    return L.roda_ibkr([G], capital, int(n), lag, custo_mult, alavancagem)


excesso, classes_ir, posicoes, negocios, _roda = L.interface(roda, PARAMS, REGIME, CUSTO_TROCA)
