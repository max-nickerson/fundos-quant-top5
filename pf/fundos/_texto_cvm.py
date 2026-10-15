"""
Leitura robusta de texto dos arquivos abertos da CVM (VLMO, IPE, FCA...). Auditoria PF2.

Diagnóstico (pf/pesquisa/auditoria_pf2.md, item 6): o cvm_vlmo.parquet está CORRETO em Unicode ('Compra \xe0 vista' = "Compra à vista");
o "Compra � vista" é só o console do Windows (cp1252/cp850) imprimindo. Mesmo assim, os CSVs da CVM vêm em latin-1/cp1252 e versões
baixadas com o encoding errado geram mojibake ("Compra Ã  vista") ou U+FFFD ("Compra \ufffd vista"). `normaliza` cobre os três casos:
  1) mojibake utf-8 lido como latin-1 -> desfaz (encode latin-1 / decode utf-8);
  2) remove acentos (NFKD) e o caractere de substituição U+FFFD;
  3) minúsculas e espaços simples.
Assim "Compra à vista", "Compra Ã  vista", "Compra \ufffd vista" e "COMPRA A VISTA" viram todos "compra a vista" — e "Ações" vira "acoes".
"""
import re
import unicodedata

import pandas as pd


def _um(s):
    if not isinstance(s, str):
        return s
    if "Ã" in s or "Â" in s:
        try:
            s = s.encode("latin-1").decode("utf-8")
        except (UnicodeEncodeError, UnicodeDecodeError):
            pass
    s = s.replace("�", "a" if re.search(r"\s�\s", s) else "")      # "Compra � vista": o � isolado era "à"
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii")
    return re.sub(r"\s+", " ", s).strip().lower()


def normaliza(serie):
    """Série de texto da CVM -> texto ASCII minúsculo comparável (mapeia valores únicos: rápido em 400 mil linhas)."""
    u = pd.Series(serie.dropna().unique())
    m = dict(zip(u, u.map(_um)))
    return serie.map(m)


def ler_csv_cvm(caminho, **kw):
    """CSV aberto da CVM: tenta utf-8 e cai para cp1252 (o padrão dos arquivos do dados.cvm.gov.br), separador ';'."""
    for enc in ("utf-8", "cp1252", "latin-1"):
        try:
            return pd.read_csv(caminho, sep=";", encoding=enc, dtype=str, **kw)
        except UnicodeDecodeError:
            continue
    raise UnicodeDecodeError("cvm", b"", 0, 1, f"sem encoding válido: {caminho}")


if __name__ == "__main__":
    t = pd.Series(["Compra \xe0 vista", "Compra Ã\xa0 vista", "Compra � vista", "COMPRA À VISTA", "A\xe7\xf5es", "AÃ§Ãµes"])
    print(list(normaliza(t)))
