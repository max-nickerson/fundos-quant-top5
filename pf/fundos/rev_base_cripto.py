"""
Revisita PF de "IAC9 Base: cripto (trimestral e perpétuo) e S&P" e "A7 Cash-and-carry cripto (futuro trimestral x spot)".

Tese de mesa: quem quer bitcoin alavancado em reais compra o Futuro de Bitcoin da B3 (BIT) e paga uma base acima do custo de carregar o
à vista. Quando a base anualizada do BIT passa do CDI + limiar, compro o à vista em reais (ETF BITH11, 15% de IR, sem isenção) e vendo o
BIT do mês; a base converge até o vencimento. O institucional fazia isso na Binance (COIN-M/perpétuo) — para residente no Brasil a Binance
não oferece derivativos (CVM, Ato Declaratório 17.961/2020); aqui tudo é B3 e em R$.

Por que o limiar é sobre o CDI (e não T-bill): o BIT é em reais; carregar o à vista custa o CDI (o dinheiro do ETF deixa de render CDI).
Base "justa" = CDI. Só sobra prêmio quando base − CDI > 0.

Rota PF (B3, conta única, garantia em Tesouro Selic):
  - perna vendida: BIT do mês (vence na última sexta do mês; liquidação financeira pelo Nasdaq Bitcoin Reference Price - Settlement
    (NQBTCS) convertido a R$). Tamanho 0,1 BTC até 13/06/2025 e 0,01 BTC desde 16/06/2025 (o multiplicador é lido do próprio boletim:
    AdjstdValCtrct / variação do ajuste). Margem ~R$ 45–100 por contrato, coberta pelo Tesouro Selic (rende CDI -> custo zero).
    Fontes: https://www.b3.com.br/pt_br/produtos-e-servicos/negociacao/criptoativos/futuro-de-bitcoin-em-reais.htm ;
    https://clientes.b3.com.br/w/contrato-futuro-de-bitcoin-tem-seu-tamanho-reduzido-em-10-vezes
  - perna comprada: BITH11 (Hashdex Bitcoin, só BTC, maior PL entre os ETFs de BTC da B3), cotas INTEIRAS. Taxa de adm 0,70% a.a. —
    já está DENTRO do preço da cota (não desconto de novo). Fonte: https://www.etfsbrasil.com.br/comparador/bith11/qbtc11
    HASH11 é cesta (não só BTC); IBIT39 é BDR (câmbio + custo de BDR); QBTC11/BITI11 0,70–0,75% e menos líquidos.
  - alocação: 80% do capital no ETF (cotas inteiras) e o resto em Tesouro Selic como garantia + colchão do ajuste diário (alta de 25% do BTC
    ainda cabe sem vender ETF). Sem alavancagem: o ETF tem de ser pago à vista (PF não financia ETF ao CDI).

Custos (custo_mult multiplica todos):
  - BIT: tarifa única ~0,04% do nocional por lado (B3: tarifa única x NQBTCS em R$ x fator do contrato; day trade R$ 0,72 por contrato de
    0,01 BTC com 70% de desconto -> ~R$ 2,4 por contrato fora do day trade ≈ 0,04%; fonte: link da B3 acima e
    https://www.b3.com.br/pt_br/produtos-e-servicos/tarifas/listados-a-vista-e-derivativos/) + meio spread do fechamento do boletim
    (BestBid/BestAsk do próprio dia; padrão 0,05% se faltar ou se absurdo).
  - BITH11: emolumentos 0,03% + meio spread do fechamento do boletim (padrão 0,15%; mediana observada ~0,1%).

Preços NÃO simultâneos (o que matou box/termo): o ajuste do BIT sai no fim da tarde (perto das 17h de Brasília; medido abaixo), o BITH11
fecha no leilão de fechamento da B3 e o NQBTCS liquida às 15h de Nova York.
  - SINAL: a base é medida contra o BTC/BRL da Binance na HORA do ajuste (vela de 1h mais próxima, escolhida pela menor dispersão diária de
    ln(ajuste/spot) — ver `hora_ajuste`), não contra o fechamento do ETF. Suavizada pela mediana de `suav` pregões (só passado).
  - P&L: futuro marcado pelo AJUSTE, ETF pelo FECHAMENTO. O descasamento de horário gera ruído diário (±0,5–1% do nocional) que se desfaz no
    dia seguinte; não cria tendência, mas aparece no ganho/perda de cada negócio (entrada e saída). Entrada/saída: futuro executado no ajuste,
    ETF no fechamento do mesmo pregão (t+1 da decisão), pagando meio spread.

IR: ETF de cripto na B3 e futuro são "operações comuns" de renda variável, 15%, e prejuízo de uma perna compensa ganho da outra
(IN RFB 1.585/2015, arts. 57 e 61 — mercados à vista, futuro, ETF de renda variável). Por isso o P&L líquido das duas pernas vai numa classe
só ("futuros_b3"): separar em duas classes (como o motor compensa só dentro da classe) faria o IR incidir sobre a perna vencedora e
ignorar a perdedora — erro grande num hedge. `classes_ir(..., separar=True)` mostra essa conta errada para comparação.

Variante IBKR (rota="ibkr"): MBT (micro bitcoin CME, 0,1 BTC) vendido x IBIT comprado; o à vista inteiro fica em US$ fora do CDI, exposto ao
câmbio e pagando IOF na remessa (pf.custo_conta_exterior). Base do CME pelo Yahoo (BTC=F x BTC-USD, mediana de 21 dias: horários diferentes)
e o carry é MODELADO (base travada na entrada), não marcado — só como ordem de grandeza.

Dados (pf/dados/rev_base_cripto/): bit_b3.parquet (boletim BVBG.086 da B3, BIT e ETFs de BTC, 2024-04+, baixado por `baixa()`),
binance_1h.parquet (BTCBRL, USDTBRL, BTCUSDT 1h da API pública da Binance), cme (pf/dados/micro_cme/precos.parquet).
Uso:  python pf/fundos/rev_base_cripto.py baixa     (download; o backtest não usa internet)
"""
import io
import re
import sys
import time
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _util as U  # noqa: E402
from _util import C, pf  # noqa: E402

DADOS = U.CACHE / "rev_base_cripto"

NOME = "Base do Futuro de Bitcoin B3 x ETF BITH11 (cash-and-carry em R$)"
TESE = ("vendo o BIT do mês e compro BITH11 quando a base anualizada do BIT paga mais que CDI + limiar; recebo a base até a rolagem, "
        "sem risco de preço; garantia em Tesouro Selic")
BENCHMARK = "CDI"
INICIO = "2024-04-17"            # lançamento do BIT
CORTE = "2025-07-01"             # 1º mês inteiro com o contrato de 0,01 BTC (antes disso 1 contrato = R$ 35–60 mil: R$ 20/50 mil não operam);
                                 # deixa 15 meses de OOS. O IS (abr/2024–jun/2025) serve para medir a base, quase sem negócios.
REGIME = "nenhum"
CUSTO_TROCA = .001
PARAMS = {"thr": .05, "barreira": 1.0, "saida": 0.0, "min_dias": 10, "suav": 3, "sentido": "compra"}
# thr: base − CDI mínima (a.a.); barreira: o carry esperado até o vencimento tem de pagar `barreira` x o custo de ida e volta (0 = ignora custo)
GRADE = {"thr": [0.0, .025, .05, .10], "barreira": [0.0, 1.0]}
VIZINHANCA = {"thr": (.02, .08), "barreira": (.5, 1.5), "saida": (-.02, .02), "min_dias": (7, 14), "suav": (1, 5)}
RANKING = ["IAC9 Base: cripto (trimestral e perpétuo) e S&P (SPY x ES)", "A7 Cash-and-carry cripto (futuro trimestral x spot)"]
INSTRUMENTOS = [
    {"onde": "B3 (Clear/XP/BTG...)", "ticker": "BIT<mês><ano>", "lote": "1 contrato = 0,1 BTC até 13/06/2025; 0,01 BTC desde 16/06/2025",
     "custo": "~0,04% do nocional/lado + meio spread (boletim)"},
    {"onde": "B3", "ticker": "BITH11", "lote": "1 cota", "custo": "emolumentos 0,03% + meio spread (boletim); adm 0,70% a.a. no preço"},
    {"onde": "Tesouro Direto / B3", "ticker": "Tesouro Selic (LFT)", "lote": "fração", "custo": "garantia, rende CDI"},
]
APLICAVEL = True
MOTIVO = ("tudo na B3 em R$ (BIT + BITH11 + Tesouro Selic como garantia); com 0,01 BTC por contrato desde jun/2025 cabem 2 (R$ 20 mil) a "
          "6 (R$ 50 mil) contratos; antes disso 1 contrato (0,1 BTC) era maior que o capital")
ALAVANCAGENS = [1]
MOTIVO_ALAV = ("o ETF tem de ser pago à vista; PF não financia BITH11 ao CDI. 80% do capital no ETF + 20% de garantia/colchão é o máximo "
               "seguro (alta de 25% do BTC num dia de ajuste já consome o colchão)")
VARIANTES = {"IBKR: MBT vendido x IBIT (fora do CDI, câmbio, IOF)": {"rota": "ibkr"},
             "reverso: aluga e vende BITH11, compra BIT, venda no Tesouro Selic (aluguel 3% a.a.)": {"sentido": "reverso"},
             "reverso sem barreira de custo, limiar 2,5%": {"sentido": "reverso", "thr": .025, "barreira": 0.0},
             "ambos os sentidos": {"sentido": "ambos"},
             "compra sem barreira de custo, limiar 0": {"thr": 0.0, "barreira": 0.0}}

ALOC = .80
EMOL_BIT, SPR_BIT = .0004, .0005
EMOL_ETF, SPR_ETF = pf.B3_EMOL, .0015
ETF = "BITH11"
CUSTO_IDA_VOLTA = .006           # BIT (0,04% + ~0,09%) x 2 + BITH11 (0,03% + ~0,13%) x 2 ≈ 0,6% do nocional: o carry esperado tem de pagar isso
CUSTO_ROLAGEM = .0026            # rolar só o futuro (fecha + abre) com o ETF parado
CUSTO_SAIDA = .003
# reverso: aluguel de BITH11 (BTC da B3). Sem dado público de taxa para esse ETF: 3% a.a. ao doador (ETF de nicho; blue chips 0,5–1%) +
# 0,5% do volume por contrato aberto (corretora, pf.ALUGUEL_PF_CORRETORA). Disponibilidade de lote para alugar NÃO verificada.
ALUGUEL_DOADOR, ALUGUEL_CORRETORA = .03, pf.ALUGUEL_PF_CORRETORA
ANTES = 2                         # rola (ou sai) quando faltam <= 2 pregões para o vencimento
LETRAS = "FGHJKMNQUVXZ"


# ================================================================ download (não é usado no backtest)
def baixa():
    """Baixa o boletim BVBG.086 (PRyymmdd.zip) de cada pregão desde abr/2024, guarda BIT e ETFs/BDRs de bitcoin, e o 1h da Binance."""
    import requests
    from concurrent.futures import ThreadPoolExecutor
    pasta = DADOS / "dias"
    pasta.mkdir(parents=True, exist_ok=True)
    tk = re.compile(rb"<TckrSymb>(BIT[FGHJKMNQUVXZ]\d\d|[A-Z0-9]*BI?T[A-Z0-9]*(?:11|39)|HASH11|ETHE11|QETH11)</TckrSymb>")
    campos = ["AdjstdQt", "PrvsAdjstdQt", "AdjstdValCtrct", "OpnIntrst", "FinInstrmQty", "NtlFinVol", "BestBidPric", "BestAskPric",
              "FrstPric", "MinPric", "MaxPric", "TradAvrgPric", "LastPric", "RglrTxsQty"]
    S = requests.Session()
    S.headers["User-Agent"] = "Mozilla/5.0"

    def dia(d):
        f = pasta / f"{d:%Y%m%d}.parquet"
        if f.exists():
            return
        for i in range(4):
            try:
                r = S.get(f"https://www.b3.com.br/pesquisapregao/download?filelist=PR{d:%y%m%d}.zip,", timeout=180)
                r.raise_for_status()
                z = zipfile.ZipFile(io.BytesIO(r.content))
                z2 = zipfile.ZipFile(io.BytesIO(z.read(z.namelist()[0])))
                break
            except Exception:
                if i == 3:
                    return                                          # feriado (24/12, 31/12) ou falha
                time.sleep(5 * (i + 1))
        L = []
        for n in z2.namelist():
            t = z2.read(n)
            for m in tk.finditer(t):
                b = t[m.end(): t.find(b"</PricRpt>", m.end())]
                x = {"data": d, "ticker": m.group(1).decode()}
                for c in campos:
                    v = re.search(rb"<" + c.encode() + rb"[^>]*>([-\d.]+)<", b)
                    x[c] = float(v.group(1)) if v else np.nan
                L.append(x)
        pd.DataFrame(L).to_parquet(f)

    dias = [d for d in C.DIAS if d >= pd.Timestamp("2024-04-10")]
    with ThreadPoolExecutor(6) as ex:
        list(ex.map(dia, dias))
    # o mesmo papel aparece em vários XMLs do dia, às vezes sem preço: junta pegando o 1º valor não nulo de cada campo
    x = pd.concat([pd.read_parquet(f) for f in sorted(pasta.glob("*.parquet"))]).groupby(["data", "ticker"], as_index=False).first()
    x.to_parquet(DADOS / "bit_b3.parquet", compression="zstd")

    def kl(sym, ini="2024-03-01"):
        t, L = int(pd.Timestamp(ini, tz="UTC").timestamp() * 1000), []
        while True:
            r = requests.get("https://data-api.binance.vision/api/v3/klines", params=dict(symbol=sym, interval="1h", startTime=t, limit=1000),
                             timeout=60).json()
            if not r:
                break
            L += r
            t = r[-1][0] + 3_600_000
            if len(r) < 1000:
                break
        df = pd.DataFrame(L).iloc[:, [0, 1, 4, 7]]
        df.columns = ["t", "abre", "fech", "vol_quote"]
        df["t"] = pd.to_datetime(df.t, unit="ms")
        df[["abre", "fech", "vol_quote"]] = df[["abre", "fech", "vol_quote"]].astype(float)
        return df.assign(sym=sym)
    pd.concat([kl(s) for s in ("BTCBRL", "USDTBRL", "BTCUSDT")]).to_parquet(DADOS / "binance_1h.parquet", compression="zstd")


# ================================================================ dados
def carrega():
    x = pd.read_parquet(DADOS / "bit_b3.parquet")
    fut = x[x.ticker.str.fullmatch(r"BIT[FGHJKMNQUVXZ](2[4-9]|3\d)") & x.AdjstdQt.notna()].copy()
    fut = fut.rename(columns={"AdjstdQt": "ajuste", "PrvsAdjstdQt": "ajuste_ant", "OpnIntrst": "oi", "BestBidPric": "bid",
                              "BestAskPric": "ask"})[["data", "ticker", "ajuste", "ajuste_ant", "AdjstdValCtrct", "oi", "bid", "ask"]]
    etf = x[x.ticker == ETF].set_index("data").sort_index()[["LastPric", "BestBidPric", "BestAskPric", "NtlFinVol"]]
    etf.columns = ["fech", "bid", "ask", "volume"]
    h = pd.read_parquet(DADOS / "binance_1h.parquet")
    btc = h[h.sym == "BTCBRL"].set_index("t").sort_index()[["abre", "fech"]]
    cme = pd.read_parquet(U.CACHE / "micro_cme" / "precos.parquet", columns=["BTC-USD", "BTC=F"])
    return {"fut": fut.reset_index(drop=True), "etf": etf, "btc_h": btc, "cme": cme[cme.index >= "2023-01-01"]}


# ================================================================ peças
def venc_bit(ticker):
    """Última sexta-feira do mês do contrato (se não for pregão, o pregão anterior)."""
    a, m = 2000 + int(ticker[4:6]), LETRAS.index(ticker[3]) + 1
    fim = pd.Timestamp(a, m, 1) + pd.offsets.MonthEnd(0)
    sexta = fim - pd.Timedelta(days=(fim.dayofweek - 4) % 7)
    return C.DIAS[C.DIAS <= sexta][-1] if sexta <= C.DIAS[-1] else sexta      # além do fim do calendário: a própria sexta


def hora_ajuste(d):
    """Hora UTC (vela de 1h da Binance, preço no FIM da vela) em que ln(ajuste do BIT / BTCBRL) varia menos de um dia para o outro.
    Medido no IS apenas (antes do CORTE) — usado como constante de calendário."""
    f = d["fut"]
    f = f[f.data < pd.Timestamp(CORTE)].sort_values("oi").groupby("data").last()
    s = d["btc_h"].fech
    out = {}
    for hr in range(15, 23):
        sp = s[s.index.hour == hr]
        sp.index = sp.index.normalize()
        out[hr] = float(np.log(f.ajuste / sp.reindex(f.index)).diff().std())
    return pd.Series(out)


# Vela de 1h (início, UTC) cujo FECHAMENTO casa com o ajuste: 19h UTC com horário de verão nos EUA (preço das 20h UTC = 17h de Brasília) e
# 20h UTC no inverno dos EUA (21h UTC = 18h de Brasília) — é o fechamento da B3, que muda de horário com o verão americano. Medido no IS:
# desvio diário de ln(ajuste/spot) 41 bps (verão, vela 19) e 46 bps (inverno, vela 20) contra 86/83 bps na vela errada.
HORA_UTC = {True: 19, False: 20}


def verao_eua(dias):
    return pd.Series([pd.Timestamp(t).tz_localize("America/New_York").dst() != pd.Timedelta(0) for t in dias], index=dias)


def spot_ajuste(btc_h, dias):
    """BTC/BRL (Binance) no horário do ajuste do BIT / fechamento da B3 de cada pregão."""
    v = verao_eua(dias)
    out = pd.Series(np.nan, index=dias)
    for vv, hr in HORA_UTC.items():
        sp = btc_h.fech[btc_h.index.hour == hr]
        sp.index = sp.index.normalize()
        sp = sp[~sp.index.duplicated()].reindex(dias)
        out[v == vv] = sp[v == vv]
    return out


def painel(d):
    """Pivots no calendário dos pregões do BIT: ajuste (data x ticker), mult (BTC por contrato), meio spread do contrato."""
    f = d["fut"]
    aj = f.pivot_table(index="data", columns="ticker", values="ajuste")
    dias = aj.index
    var = (f.ajuste - f.ajuste_ant).replace(0, np.nan)
    mult = (f.AdjstdValCtrct / var).round(3)
    mult = mult.where(mult.isin([.1, .01]))
    mult = pd.Series(mult.values, index=f.data.values).groupby(level=0).median().reindex(dias).ffill().bfill()
    spr = ((f.ask - f.bid) / 2 / ((f.ask + f.bid) / 2)).where((f.bid > 0) & (f.ask > f.bid))
    spr = f.assign(s=spr).pivot_table(index="data", columns="ticker", values="s").reindex(dias)
    return aj, mult, spr


def front(aj):
    """Contrato a carregar em cada pregão: o de vencimento mais próximo com mais de ANTES pregões até vencer E com preço PRÓPRIO.
    Armadilha do boletim: enquanto o 2º vencimento não tem negócio, a B3 publica para ele o MESMO ajuste do 1º (cópia, sem mercado);
    no dia em que passa a negociar o ajuste 'salta' ~1–3% (a base de um mês). Usar a cópia criava retorno falso na rolagem.
    Regra: contrato com ajuste idêntico ao de um vencimento mais curto no mesmo dia não é elegível; se o próximo ainda não tem preço
    próprio, continua no atual (até o vencimento)."""
    v = pd.Series({t: venc_bit(t) for t in aj.columns})
    ordem = list(v.sort_values().index)
    out, dc = [], []
    for t in aj.index:
        vivos, ant = [], None
        for k in ordem:
            a = aj.at[t, k]
            if a == a and v[k] >= t:
                if ant is None or abs(a - ant) > 1e-6:
                    vivos.append(k)
                ant = a
        ok = [k for k in vivos if np.busday_count(t.date(), v[k].date()) > ANTES]
        k = ok[0] if ok else (vivos[-1] if vivos else None)
        out.append(k)
        dc.append((v[k] - t).days if k else np.nan)
    return pd.Series(out, index=aj.index), pd.Series(dc, index=aj.index, dtype=float), v


# ================================================================ motor
def _simula(d, capital, custo_mult, lag, thr, saida, min_dias, suav, alavancagem=1, barreira=1.0, sentido="compra"):
    aj, mult, spr = painel(d)
    dias = aj.index
    fr, dc, venc = front(aj)
    S = spot_ajuste(d["btc_h"], dias)
    F1 = pd.Series([aj.at[t, k] if k else np.nan for t, k in zip(dias, fr)], index=dias)
    cdi_aa = (1 + C.CDI.reindex(dias).ffill()) ** 252 - 1
    base = np.log(F1 / S) * 365 / dc.clip(lower=1)
    ex = (base - np.log1p(cdi_aa)).rolling(suav, min_periods=1).median()
    etf = d["etf"].reindex(dias)
    P = etf.fech.ffill()
    s_etf = ((etf.ask - etf.bid) / (etf.ask + etf.bid)).where((etf.bid > 0) & (etf.ask > etf.bid))
    s_etf = s_etf.where(s_etf < .01).fillna(SPR_ETF)

    # ---- decisões no fechamento de t (só dados até t). lado +1 = cash-and-carry (compra ETF, vende BIT); -1 = reverso (aluga e vende ETF,
    # compra BIT, aplica a venda no Tesouro Selic) — só se `sentido` permitir
    lados = {"compra": (1,), "reverso": (-1,), "ambos": (1, -1)}[sentido]

    def tamanho(i):
        """Contratos inteiros com ~ALOC do capital; cotas do ETF com o MESMO nocional em R$ do futuro (delta neutro: dF ≈ dS x F/S)."""
        N = np.floor(ALOC * alavancagem * capital / (mult.iloc[i] * F1.iloc[i]))
        if N < 1:
            return 0.0, 0
        q = N * mult.iloc[i]
        return q, int(round(q * F1.iloc[i] / P.iloc[i]))

    n = len(dias)
    dec_k, dec_q, dec_n = [None] * n, np.zeros(n), np.zeros(n)
    on, k_atual, q, ncot, lado = False, None, 0.0, 0, 0
    for i, t in enumerate(dias):
        k = fr.iloc[i]
        e = ex.iloc[i]
        di = dc.iloc[i]
        if k is None or not np.isfinite(e) or not np.isfinite(P.iloc[i]):
            on = False
        elif not on:
            for sg in lados:
                if sg * e > thr and di >= min_dias and sg * e * di / 365 > barreira * CUSTO_IDA_VOLTA:
                    q, ncot = tamanho(i)
                    if q > 0:
                        on, k_atual, lado = True, k, sg
                    break
        else:
            if k == k_atual and np.busday_count(t.date(), venc[k].date()) <= 1:
                on = False                                          # o próximo mês ainda não negocia e este vence amanhã: desmonta tudo
            elif k == k_atual and lado * e < saida - CUSTO_SAIDA * 365 / max(di, 1):
                on = False                                          # sai antes só se o carry que falta (negativo) custa mais que sair
            elif k != k_atual:                                      # rolagem: segue no próximo mês só se ainda paga CDI + limiar
                if lado * e > thr and di >= min_dias and lado * e * di / 365 > barreira * CUSTO_ROLAGEM:
                    q2, n2 = tamanho(i)                             # refaz o tamanho na rolagem (o BTC pode ter dobrado de preço)
                    if q2 > 0:
                        k_atual, q, ncot = k, q2, n2
                    else:
                        on = False
                else:
                    on = False
        if on:
            dec_k[i], dec_q[i], dec_n[i] = k_atual, lado * q, lado * ncot
        else:
            q, ncot, k_atual, lado = 0.0, 0, None, 0

    # ---- execução em t+1+lag (pregões do BIT)
    sh = 1 + lag
    hk = [None] * sh + dec_k[:-sh]
    hq = np.r_[np.zeros(sh), dec_q[:-sh]]
    hn = np.r_[np.zeros(sh), dec_n[:-sh]]
    # contrato vencido antes de a ordem de rolar ser executada: liquidado no vencimento (fica só o ETF até a execução)
    for i, t in enumerate(dias):
        if hk[i] is not None and venc[hk[i]] < t:
            hk[i], hq[i] = None, 0.0
    pnl_f, pnl_e, cab, cfe, ccp, cvd, cdi_l, alug = (np.zeros(n) for _ in range(8))
    cdi = C.CDI.reindex(dias).fillna(0).values
    Pv = P.values

    def custo_bit(i, kk, qq):
        if kk is None or not qq or not np.isfinite(aj.at[dias[i], kk]):
            return 0.0
        sp = spr.at[dias[i], kk] if kk in spr.columns else np.nan
        sp = sp if np.isfinite(sp) and sp < .005 else SPR_BIT
        return abs(qq) * aj.at[dias[i], kk] * (EMOL_BIT + sp) * custo_mult

    for i in range(1, n):
        k0 = hk[i - 1]
        if k0 is not None and hq[i - 1]:
            a1, a0 = aj.at[dias[i], k0], aj.at[dias[i - 1], k0]
            pnl_f[i] = -hq[i - 1] * (a1 - a0) if np.isfinite(a1) and np.isfinite(a0) else 0.0
        pnl_e[i] = hn[i - 1] * (Pv[i] - Pv[i - 1])
        cdi_l[i] = hn[i - 1] * Pv[i - 1] * cdi[i]
        if hk[i] != k0 or hq[i] != hq[i - 1]:
            cfe[i] = custo_bit(i, k0, hq[i - 1])                    # fecha o contrato antigo
            cab[i] = custo_bit(i, hk[i], hq[i])                     # abre o novo
        dn = abs(hn[i]) - abs(hn[i - 1])
        c = abs(hn[i] - hn[i - 1]) * Pv[i] * (EMOL_ETF + s_etf.iloc[i]) * custo_mult
        if dn > 0:
            ccp[i] = c + (abs(dn) * Pv[i] * ALUGUEL_CORRETORA * custo_mult if hn[i] < 0 else 0)   # abre (no reverso: + corretagem do aluguel)
        elif dn < 0:
            cvd[i] = c
        if hn[i - 1] < 0:                                           # taxa ao doador do aluguel de BITH11
            alug[i] = -hn[i - 1] * Pv[i - 1] * ALUGUEL_DOADOR / 252 * custo_mult
    out = pd.DataFrame({"pnl_f": pnl_f, "pnl_e": pnl_e, "cus_f": cab + cfe, "cus_e": ccp + cvd + alug, "cab": cab + ccp, "cfe": cfe + cvd + alug,
                        "cdi_l": cdi_l, "q": hq, "n": hn, "k": hk, "base": base, "ex": ex, "F1": F1, "S": S, "P": P, "cdi_aa": cdi_aa},
                       index=dias)
    return out


def _ibkr(d, capital, custo_mult, lag, thr, min_dias, **_):
    """Variante IBKR: MBT (0,1 BTC) vendido x IBIT comprado. Carry modelado: base do CME (mediana 21d, Yahoo) travada na entrada; o capital
    enviado (IBIT + margem ~40% do MBT) perde o CDI, fica no câmbio e paga remessa. Contratos inteiros: 1 MBT exige ~1,4 x 0,1 BTC em US$."""
    p = d["cme"]
    idx = p.index
    F, S = p["BTC=F"], p["BTC-USD"]
    venc = pd.Series([v if v > t + pd.Timedelta(days=2) else (t + pd.offsets.MonthEnd(1)) for t, v in
                      zip(idx, [(t + pd.offsets.MonthEnd(0)) - pd.Timedelta(days=((t + pd.offsets.MonthEnd(0)).dayofweek - 4) % 7) for t in idx])],
                     index=idx)
    dte = (venc - idx.to_series()).dt.days.clip(lower=3)
    b = ((F / S - 1) * 365 / dte).clip(-.2, .6).rolling(21, min_periods=5).median()
    tb = C.TB_US.reindex(idx, method="ffill").fillna(0) * 252
    ptax = C.PTAX.reindex(idx, method="ffill")
    # decide uma vez por vencimento (1º dia com o novo mês de contrato) e segura até a última sexta: base travada, sem vaivém de remessa
    novo = venc.ne(venc.shift(1))
    sinal = (((b - tb) > thr) & (dte >= min_dias)).astype(float).where(novo).ffill().fillna(0) > .5
    N = np.floor(capital / (1.4 * .1 * S * ptax)).where(novo).ffill().fillna(0)
    b = b.where(novo).ffill()
    pos = (sinal.astype(float) * N).shift(1 + lag).fillna(0)
    noc_brl = pos * .1 * S * ptax
    carry = pos.shift(1).fillna(0) * .1 * S.shift(1) * ptax.shift(1) * (b.shift(1) - .0025) / 365 * idx.to_series().diff().dt.days.fillna(1)
    giro = pos.diff().abs().fillna(pos)
    custo = giro * (2 * 2.5 + .1 * S * .0005) * ptax * custo_mult                  # MBT (comissão+taxa) + IBIT (comissão ~0)
    pnl_br = pf.usd_para_br(carry - custo)
    custo_conta, _ = pf.custo_conta_exterior(noc_brl.reindex(C.DIAS, method="ffill").fillna(0) * 1.4, folga=1.0)
    return (pnl_br - custo_conta * custo_mult).reindex(C.DIAS).fillna(0) / capital


def excesso(d, capital=20000, custo_mult=1, lag=0, regime=REGIME, alavancagem=1, rota="b3", **params):
    p = {**PARAMS, **params}
    if rota == "ibkr":
        e = _ibkr(d, capital, custo_mult, lag, **p)
    else:
        x = _simula(d, capital, custo_mult, lag, p["thr"], p["saida"], int(p["min_dias"]), int(p["suav"]), alavancagem, p["barreira"], p["sentido"])
        e = (x.pnl_f + x.pnl_e - x.cus_f - x.cus_e - x.cdi_l) / capital
    e = e.reindex(C.DIAS).fillna(0)
    return C.aplica_regime(e, regime, CUSTO_TROCA * custo_mult)


def classes_ir(d, capital=20000, separar=False, **params):
    p = {**PARAMS, **params}
    x = _simula(d, capital, 1, 0, p["thr"], p["saida"], int(p["min_dias"]), int(p["suav"]), barreira=p["barreira"], sentido=p["sentido"])
    f, e = (x.pnl_f - x.cus_f).reindex(C.DIAS).fillna(0), (x.pnl_e - x.cus_e).reindex(C.DIAS).fillna(0)
    perd = x.cdi_l.reindex(C.DIAS).fillna(0)
    if separar:
        return {"futuros_b3": f, "etf_b3": e, "_cdi_perdido": perd}
    return {"futuros_b3": f + e, "_cdi_perdido": perd}          # renda variável comum: compensa entre ETF e futuro (IN RFB 1.585/2015)


def posicoes(d, capital=20000, **params):
    """W (decidido em t) = fração do capital no par; R = excesso diário de 1 R$ no par (BITH11 comprado − BIT do mês vendido − CDI),
    no contrato carregado ontem. comum.carteira(W, R, 0) ≈ excesso sem custos e sem arredondamento de contratos."""
    p = {**PARAMS, **params}
    x = _simula(d, capital, 0, 0, p["thr"], p["saida"], int(p["min_dias"]), int(p["suav"]), barreira=p["barreira"], sentido=p["sentido"])
    aj, _, _ = painel(d)
    fr = front(aj)[0]
    dias = x.index
    rF = pd.Series([aj.at[dias[i], fr.iloc[i - 1]] / aj.at[dias[i - 1], fr.iloc[i - 1]] - 1 if i and fr.iloc[i - 1] else 0.0
                    for i in range(len(dias))], index=dias)
    R = (x.P.pct_change(fill_method=None).fillna(0) - rF.fillna(0) - C.CDI.reindex(dias).fillna(0)).rename("BITH11 x BIT")
    w_exec = (x.n * x.P / capital)
    W = w_exec.shift(-1).fillna(0)                      # carteira desloca 1 (execução) + 1 (rende no dia seguinte)
    return W.reindex(C.DIAS).fillna(0).to_frame("BITH11 x BIT"), R.reindex(C.DIAS).fillna(0).to_frame()


def negocios(d, capital=20000, **params):
    """Um negócio por contrato carregado (rolagem abre negócio novo). P&L do dia i pertence ao contrato carregado em i-1; o custo de abrir
    (contrato novo + compra de cotas) ao negócio que abre; o de fechar ao que fecha. A soma bate com o excesso x capital."""
    p = {**PARAMS, **params}
    x = _simula(d, capital, 1, 0, p["thr"], p["saida"], int(p["min_dias"]), int(p["suav"]), barreira=p["barreira"], sentido=p["sentido"])
    corre = x.pnl_f + x.pnl_e - x.cdi_l - x.cfe
    k = pd.Series([kk if q != 0 else None for kk, q in zip(x.k, x.q)], index=x.index)
    bloco = ((k != k.shift(1)) & k.notna()).cumsum().where(k.notna())
    bdono = bloco.shift(1)
    linhas = []
    for b, g in x.groupby(bloco):
        ent = g.index[0]
        m = bdono == b
        pnl = corre[m].sum() - x.cab.loc[ent]
        sai = m[m].index[-1] if m.any() else ent
        val = abs(g.n.iloc[0]) * g.P.iloc[0]
        i0 = x.index.get_loc(ent)
        linhas.append({"ativo": g.k.iloc[0], "lado": int(np.sign(g.n.iloc[0])), "entrada": ent, "saida": sai, "dias": int(m.sum()),
                       "base_decisao_aa_%": x.base.iloc[i0 - 1] * 100, "cdi_aa_%": x.cdi_aa.iloc[i0 - 1] * 100,
                       "btc": g.q.iloc[0], "cotas": int(g.n.iloc[0]), "pnl_rs": pnl, "retorno_%": pnl / val * 100 if val else np.nan,
                       "contrib_pp": pnl / capital * 100})
    if not linhas:
        return pd.DataFrame(columns=["ativo", "lado", "entrada", "saida", "dias", "retorno_%", "contrib_pp"])
    return pd.DataFrame(linhas)


if __name__ == "__main__":
    if "baixa" in sys.argv:
        baixa()
    else:
        d = carrega()
        print(hora_ajuste(d))
        e = excesso(d)
        print(e[e.index >= INICIO].describe())
        print(negocios(d).to_string())
