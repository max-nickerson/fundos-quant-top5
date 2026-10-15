"""Baixa (uma vez) as carteiras trimestrais do IWM (iShares Russell 2000 ETF) do N-PORT na SEC (2019+) -> pf/dados/pf2_fluxo_global/iwm_nport.parquet"""
import re
import sys
import time

import pandas as pd
import requests

import fg_comum as G

sys.path.insert(0, str(G.FD.parent))
from ideias_global import H  # noqa: E402  (User-Agent genérico de pesquisa)


def lista():
    out = []
    for y in range(2019, 2027):
        k = 0
        while True:
            u = (f"https://efts.sec.gov/LATEST/search-index?q=%22iShares%20Russell%202000%20ETF%22&forms=NPORT-P&ciks=0001100663"
                 f"&dateRange=custom&startdt={y}-01-01&enddt={y}-12-31&from={k}")
            j = requests.get(u, headers=H, timeout=60).json()
            hits = j["hits"]["hits"]
            for h in hits:
                acc = h["_id"].split(":")[0]
                out.append({"acc": acc, "periodo": h["_source"].get("period_ending"), "arquivado": h["_source"].get("file_date")})
            k += len(hits)
            if not hits or k >= j["hits"]["total"]["value"]:
                break
            time.sleep(.3)
    x = pd.DataFrame(out).drop_duplicates("acc")
    return x[x.periodo.str[5:].isin(["03-31", "06-30", "09-30", "12-31"])]


def carteira(acc):
    a = acc.replace("-", "")
    t = requests.get(f"https://www.sec.gov/Archives/edgar/data/1100663/{a}/primary_doc.xml", headers=H, timeout=180).text
    s = re.findall(r"<seriesName>(.*?)</seriesName>", t)
    if not s or s[0].strip() != "iShares Russell 2000 ETF":
        return None
    linhas = []
    for b in re.findall(r"<invstOrSec>(.*?)</invstOrSec>", t, flags=re.S):
        g = lambda tag: (re.findall(fr"<{tag}>(.*?)</{tag}>", b) or [""])[0]
        if g("assetCat") != "EC":
            continue
        linhas.append({"nome": g("name"), "cusip": g("cusip"), "acoes": float(g("balance") or 0), "valor": float(g("valUSD") or 0)})
    return pd.DataFrame(linhas)


if __name__ == "__main__":
    L = lista()
    print(len(L), "candidatos")
    out = []
    for r in L.itertuples():
        c = carteira(r.acc)
        time.sleep(.2)
        if c is None:
            continue
        c["periodo"] = pd.Timestamp(r.periodo)
        c["arquivado"] = pd.Timestamp(r.arquivado)
        out.append(c)
        print(r.periodo, len(c), flush=True)
    X = pd.concat(out).drop_duplicates(["periodo", "cusip"])
    X.to_parquet(G.CACHE / "iwm_nport.parquet")
    print(X.groupby("periodo").size())


def cusip_ticker(anos=range(2019, 2027), meses=("03", "04", "05", "06", "07", "08")):
    """CUSIP -> ticker na época, pelos arquivos de fails-to-deliver da SEC (cnsfailsAAAAMM[a|b].zip)."""
    import io
    import zipfile
    L = []
    for a in anos:
        for m in meses:
            for h in "ab":
                u = f"https://www.sec.gov/files/data/fails-deliver-data/cnsfails{a}{m}{h}.zip"
                r = requests.get(u, headers=H, timeout=60)
                if r.status_code != 200:
                    continue
                z = zipfile.ZipFile(io.BytesIO(r.content))
                x = pd.read_csv(z.open(z.namelist()[0]), sep="|", dtype=str, encoding="latin-1", on_bad_lines="skip")
                x = x.rename(columns={"SETTLEMENT DATE": "data", "CUSIP": "cusip", "SYMBOL": "tk"})[["data", "cusip", "tk"]].dropna()
                L.append(x.drop_duplicates(["cusip", "tk"]))
                time.sleep(.2)
        print(a, flush=True)
    X = pd.concat(L)
    X["data"] = pd.to_datetime(X.data, format="%Y%m%d", errors="coerce")
    X = X.sort_values("data").drop_duplicates(["cusip", "tk"], keep="last")
    X.to_parquet(G.CACHE / "cusip_ticker.parquet")
    return X
