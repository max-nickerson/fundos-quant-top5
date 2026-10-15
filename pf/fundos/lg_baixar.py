"""
Frente pf2_leilao_global — download ÚNICO dos dados (Yahoo via yfinance + listas de componentes da Wikipedia). Os fundos lg_*.py não usam
internet: só leem pf/dados/pf2_leilao_global/*.parquet.

    python pf/fundos/lg_baixar.py

OHLC do Yahoo com auto_adjust=False: Open/High/Low/Close já vêm ajustados por DESDOBRAMENTO (retroativamente), não por dividendo;
'Dividends' = provento em dinheiro na data EX. Noite = (abertura t+1 + dividendo ex em t+1) / fechamento t - 1.
Listas de componentes = composição ATUAL (viés de sobrevivência: documentado nos fundos).
"""
import io
import sys
from pathlib import Path

import pandas as pd
import requests
import yfinance as yf

DADOS = Path(__file__).resolve().parent.parent / "dados" / "pf2_leilao_global"
INI, FIM = "2010-01-01", "2026-10-14"          # FIM exclusivo: último pregão comum.DIAS = 2026-10-13
H = {"User-Agent": "Mozilla/5.0"}

ETF_EUA = ["SPY", "QQQ", "DIA", "IWM", "MDY", "XLK", "XLF", "XLE", "XLV", "XLI", "XLY", "XLP", "XLU", "XLB", "XLRE", "XLC", "SMH", "XBI",
           "KRE", "XRT", "XHB", "XOP", "GDX", "IYR", "OIH", "IBB", "ITB", "XME"]
ETF_EUROPA_EUA = ["EWG", "EWU", "EWQ", "EWP", "EWI", "EWL", "EWN", "FEZ", "VGK", "EWD"]
ETF_ASIA_EUA = ["EWJ", "EWY", "EWT", "EWH", "FXI", "MCHI", "EWS", "EWA"]
UCITS = ["EXS1.DE", "ISF.L", "CAC.PA", "EXW1.DE", "CSPX.L", "IUSA.DE"]
ADR = {"PBR": "PETR3", "PBR-A": "PETR4", "VALE": "VALE3", "ITUB": "ITUB4", "BBD": "BBDC4", "ABEV": "ABEV3", "GGB": "GGBR4", "SID": "CSNA3",
       "EMBJ": "EMBR3", "SBS": "SBSP3", "CIG": "CMIG4", "UGP": "UGPA3", "BSBR": "SANB11", "SUZ": "SUZB3", "BRFS": "BRFS3", "BAK": "BRKM5",
       "TIMB": "TIMS3", "VIV": "VIVT3", "BDORY": "BBAS3", "ELPC": "CPLE6"}   # ERJ->EMBJ; EBR, BRFS, CBD sumiram do Yahoo (sobrevivência)
JAPAO = ["7203", "6758", "8306", "6861", "9984", "9432", "8035", "6098", "4063", "9983", "8316", "8411", "6501", "7974", "4502", "8058",
         "8031", "8001", "6367", "7267", "6902", "6954", "4519", "4568", "6981", "7741", "9433", "8766", "6273", "4661", "2914", "6594",
         "7751", "6702", "6752", "8802", "8801", "3382", "6503", "5108", "4503", "7011", "8053", "6301", "4901", "6178", "9020", "9022",
         "8604", "8591"]
COREIA = ["005930", "000660", "005380", "035420", "051910", "006400", "005490", "000270", "068270", "105560", "055550", "012330",
          "035720", "028260", "066570", "003550", "017670", "096770", "034730", "015760"]
TAIWAN = ["2330", "2317", "2454", "2308", "2412", "2882", "2881", "1301", "1303", "2002", "2303", "3711", "2891", "2886", "1216", "2357",
          "2382", "3008", "2884", "5880"]


def wiki(url, k, col):
    t = [x for x in pd.read_html(io.StringIO(requests.get(url, headers=H, timeout=60).text)) if x.shape[0] > 20]
    return [str(s).replace("\xa0", " ") for s in t[k][col].tolist()]


def baixa(tickers, nome, lote=150):
    out = []
    for i in range(0, len(tickers), lote):
        x = yf.download(tickers[i:i + lote], start=INI, end=FIM, auto_adjust=False, actions=True, progress=False, group_by="ticker",
                        threads=True)
        for t in tickers[i:i + lote]:
            if t not in x.columns.get_level_values(0):
                continue
            y = x[t].dropna(subset=["Close"])
            if len(y) < 100:
                continue
            y = y.rename(columns={"Open": "O", "High": "H", "Low": "L", "Close": "C", "Adj Close": "AC", "Volume": "V", "Dividends": "div"})
            y = y[["O", "H", "L", "C", "AC", "V", "div"]].astype("float32")
            y["ticker"] = t
            out.append(y.reset_index().rename(columns={"Date": "data"}))
        print(nome, i, flush=True)
    df = pd.concat(out, ignore_index=True)
    df["data"] = pd.to_datetime(df["data"]).dt.tz_localize(None).dt.normalize()
    df.to_parquet(DADOS / f"{nome}.parquet", compression="zstd")
    print(nome, df.ticker.nunique(), "tickers", len(df), "linhas")


def b3_etf():
    """ETFs (CODBDI 14, mercado à vista 010) dos COTAHIST anuais já baixados (quant/dados/cotahist) + BDRs de
    pf/dados/global_cripto/b3_etf_bdr.parquet -> b3_etf_bdr.parquet (O/H/L/C brutos, V = quantidade, BID/ASK no fechamento)."""
    import zipfile
    linhas = []
    for f in sorted((DADOS.parent.parent.parent.parent / "dados" / "cotahist").glob("COTAHIST_A*.ZIP")):
        z = zipfile.ZipFile(f)
        for l in z.open(z.namelist()[0]):
            l = l.decode("latin1")
            if l[:2] == "01" and l[10:12] == "14" and l[24:27] == "010" and l[12:24].strip().endswith("11"):
                p = lambda a, b: int(l[a:b]) / 100
                linhas.append((l[2:10], l[12:24].strip(), p(56, 69), p(69, 82), p(82, 95), p(108, 121), p(121, 134), p(134, 147),
                               int(l[152:170]), int(l[147:152]), l[27:39].strip()))
        print(f.name, len(linhas), flush=True)
    e = pd.DataFrame(linhas, columns=["data", "ticker", "O", "H", "L", "C", "BID", "ASK", "V", "NEG", "nome"])
    e["data"] = pd.to_datetime(e["data"])
    b = pd.read_parquet(DADOS.parent / "global_cripto" / "b3_etf_bdr.parquet")
    b = b[~b["ticker"].str.endswith("11")].rename(columns={"abertura": "O", "max": "H", "min": "L", "fech": "C", "oferta_compra": "BID",
                                                            "oferta_venda": "ASK", "quantidade": "V", "negocios": "NEG"})
    x = pd.concat([e, b[["data", "ticker", "O", "H", "L", "C", "BID", "ASK", "V", "NEG"]]], ignore_index=True)
    x["AC"], x["div"] = x["C"], 0.0
    x = x.drop_duplicates(["data", "ticker"], keep="last")
    x.to_parquet(DADOS / "b3_etf_bdr.parquet", compression="zstd")
    print("b3_etf_bdr", x.ticker.nunique(), len(x), x.data.max())


if __name__ == "__main__":
    if sys.argv[1:] == ["b3"]:
        b3_etf()
        sys.exit()
    DADOS.mkdir(parents=True, exist_ok=True)
    so = sys.argv[1:]
    sp100 = [s.replace(".", "-") for s in wiki("https://en.wikipedia.org/wiki/S%26P_100", 0, "Symbol")]
    sp600 = [s.replace(".", "-") for s in wiki("https://en.wikipedia.org/wiki/List_of_S%26P_600_companies", 0, "Symbol")]
    dax = wiki("https://en.wikipedia.org/wiki/DAX", 1, "Ticker")
    cac = wiki("https://en.wikipedia.org/wiki/CAC_40", 1, "Ticker")
    ftse = [s.replace(".", "-") + ".L" for s in wiki("https://en.wikipedia.org/wiki/FTSE_100_Index", 1, "Ticker")]
    hk = [f"{int(s.split(':')[1]):04d}.HK" for s in wiki("https://en.wikipedia.org/wiki/Hang_Seng_Index", 1, "Ticker")]
    pd.DataFrame({"lista": ["sp100"] * len(sp100) + ["sp600"] * len(sp600) + ["dax"] * len(dax) + ["cac"] * len(cac) + ["ftse"] * len(ftse)
                  + ["hk"] * len(hk), "ticker": sp100 + sp600 + dax + cac + ftse + hk}).to_csv(DADOS / "listas.csv", index=False)
    pd.Series(ADR).rename("b3").rename_axis("adr").to_csv(DADOS / "adr_b3.csv")
    tarefas = {
        "eua": ETF_EUA + ETF_EUROPA_EUA + ETF_ASIA_EUA + sp100 + list(ADR) + ["^VIX"],
        "small": sp600,
        "europa": sorted(set(dax + cac + ftse + UCITS)),
        "asia": [t + ".T" for t in JAPAO] + hk + [t + ".KS" for t in COREIA] + [t + ".TW" for t in TAIWAN],
        "fx": ["EURUSD=X", "GBPUSD=X", "JPY=X", "HKD=X", "KRW=X", "TWD=X"],
    }
    for nome, tk in tarefas.items():
        if not so or nome in so:
            baixa(list(dict.fromkeys(tk)), nome)
