"""
Energia com micros da CME (IBKR): Micro Henry Hub (MNG) e Micro WTI (MCL) pela CURVA (quem rola paga o contango) e pela sazonalidade do gás.

Tese de mesa: os compradores "passivos" de energia (UNG, USO, índices de commodities BCOM/GSCI, varejo comprado em ETF) rolam o 1º
vencimento para o 2º todo mês, por regra e em data conhecida. Quando a curva está em contango, eles compram o 2º caro e vendem o 1º
barato — quem tem tancagem/estocagem do outro lado (trading houses, utilities com armazenagem) embolsa a diferença. Esse é o comprador
forçado. No gás natural o contango é enorme na primavera/verão (estação de injeção): UNG perdeu ~99% desde 2007 em boa parte por isso.
  - "gas_curva": vendido em 1 MNG quando o contango estimado (2º/1º vencimento) > `lim` ao mês; fora no resto (a versão que também
    comprava a backwardation perdeu todo o capital em 2008/2018: picos de inverno);
  - "petroleo_curva": o mesmo com MCL (comprado na backwardation = recebe o roll; vendido em contango forte);
  - "gas_sazonal": vendido em 1 MNG de março a setembro (estação de injeção), fora no resto do ano — calendário fixo.
Não repete cme_metais (ouro sazonal e razões) nem cme_tendencia (tendência multiativos).

Dados / rolagem (sem o salto do contínuo do Yahoo):
  - RETORNO de 1 contrato = ETF que rola os futuros (UNG para o gás, USO para o petróleo; preço ajustado) − T-bill + taxa do ETF
    (UNG 1,1% a.a., USO 0,6%) — é exatamente o que o futuro rolado paga, inclusive o roll;
  - CURVA: a EIA publicava os vencimentos 1-4 da NYMEX (RNGC1/RNGC2, RCLC1/RCLC2) só até 05/abr/2024 (licença). Para ter uma série
    homogênea e SEM look-ahead até 2026, estimo o declive no dia da troca do contínuo do Yahoo: salto do NG=F/CL=F − retorno do ETF
    (que já está no 2º vencimento) ≈ log(2º/1º) da véspera. Pego o maior salto absoluto do mês e uso só A PARTIR DO MÊS SEGUINTE.
    Validação contra a EIA 2007-2024 (mensal): gás corr 0,91, mesmo sinal em 85% dos meses; petróleo corr 0,79, mesmo sinal em 74%;
  - NÍVEL (NG=F, CL=F) só para o nocional.
Contratos (CME Group, fact cards; IBKR, out/2026):
  - MNG: 1.000 MMBtu (1/10 do NG), tick US$ 0,001 = US$ 1, lançado em 06/nov/2023; ~US$ 3,2 mil (≈ R$ 18 mil) -> cabe em R$ 20 mil.
    Custo por lado: IBKR US$ 0,85 + taxas ~US$ 0,30 + meio spread 2 ticks (pouco líquido) = US$ 3,15. Margem ~15% do nocional.
    Antes de nov/2023 é hipotético (existia o E-mini QG, 2.500 MMBtu = 2,5x maior).
  - MCL: 100 barris, tick US$ 0,01 = US$ 1, lançado em 12/jul/2021; ~US$ 9,6 mil (≈ R$ 53 mil = 2,6x R$ 20 mil) -> com teto de 2,5x
    o capital só opera com R$ 50 mil (ou quando o petróleo estava barato). Custo US$ 1,85/lado; margem ~12%.
"""
import numpy as np
import pandas as pd

import fu_comum as F

NOME = "Energia micro (MNG/MCL): curva (quem rola paga o contango) e sazonalidade do gás"
TESE = "Vendido em micro gás natural quando a curva está em contango (UNG/índices rolando pagam), comprado na backwardation; MCL pela mesma regra"
BENCHMARK = "CDI"
INICIO, CORTE = "2008-01-01", "2021-01-01"
REGIME = "nenhum"
CUSTO_TROCA = 0.0
CLASSE_IR = "exterior"
PARAMS = {"modo": "gas_sazonal", "lim": .02}          # maior excesso IS (2008-2020) da grade
GRADE = {"modo": ["gas_curva", "petroleo_curva", "gas_sazonal"], "lim": [.02, .05]}
VIZINHANCA = {"lim": (.01, .07)}
LANCAMENTO = {"MNG": "2023-11-06", "MCL": "2021-07-12"}
TETO_ALAV = 2.5
TETO_VOL = .35          # vol anual de 1 contrato (63 dias, em R$) acima de 35% do capital = contrato grande demais (quebrou em 2019 sem isso)
ESPEC = {"MNG": dict(etf="UNG", fut="NG=F", taxa=.011, mult=1000, custo=3.15, margem=.15),
         "MCL": dict(etf="USO", fut="CL=F", taxa=.006, mult=100, custo=1.85, margem=.12)}
INSTRUMENTOS = [("IBKR/NYMEX", "MNG", "1.000 MMBtu (≈ R$ 18 mil)", "US$ 3,15/lado"), ("IBKR/NYMEX", "MCL", "100 bbl (≈ R$ 53 mil)", "US$ 1,85/lado"),
                ("Tesouro Direto", "Tesouro Selic", "caixa", "0")]
APLICAVEL = True
MOTIVO = ("Teto de risco: 1 contrato com vol anual > 35% do capital não opera (1 MNG tem vol de 45-80% de R$ 20 mil: na prática só "
          "opera com R$ 50 mil). MNG cabe em nocional com R$ 20 mil (≈ 0,9x; margem ≈ R$ 2,7 mil); MCL (≈ R$ 53 mil) só cabe com R$ 50 mil. MNG existe desde nov/2023 e MCL "
          "desde jul/2021: antes disso o resultado é hipotético (subjacente igual, tamanho do micro).")
ALAVANCAGENS = [1, 2]
MOTIVO_ALAV = "1 contrato por sinal; 2x = 2 contratos quando cabem (teto 2,5x o capital por alavancagem)."


def carrega():
    return {"en": F.ler("energia_yahoo.parquet")}


def _contrato(d, inst):
    def f():
        e = ESPEC[inst]
        x = d["en"]
        idx = pd.bdate_range(x[e["etf"]].dropna().index.min(), x.index.max())
        etf = F.nivel(x[e["etf"]], idx)
        tb = F.C.TB_US.reindex(idx, method="ffill").fillna(0)
        r = etf.pct_change(fill_method=None).fillna(0) - tb + e["taxa"] / 252
        lvl = F.nivel(x[e["fut"]].where(x[e["fut"]] > 0), idx)
        K = F.contrato(r, lvl, e["mult"], "USD", idx, None, e["custo"], e["margem"], rol=12)
        # declive estimado: salto do contínuo − retorno do ETF; maior |salto| do mês, usado a partir do mês seguinte
        fut = x[e["fut"]].where(x[e["fut"]] > 0).dropna()
        g = (np.log(fut).diff() - np.log(x[e["etf"]].reindex(fut.index)).diff()).dropna()
        per = g.index.to_period("M")
        m = g.groupby(per).apply(lambda s: s.loc[s.abs().idxmax()])
        m.index = (m.index + 1).to_timestamp()                          # disponível no 1º dia do mês seguinte
        return K, F.nivel(m, idx)
    return F.memo(("energia", inst), (d["en"],), f)


def gera(d, capital=20000, regime=REGIME, alavancagem=1, modo="gas_curva", lim=.03):
    inst = "MCL" if modo == "petroleo_curva" else "MNG"
    K, decl = _contrato(d, inst)
    if modo == "gas_sazonal":
        mes = pd.Series(K.index.month, index=K.index)
        lado = -mes.between(3, 9).astype(float)
        lado = lado.shift(-2).fillna(0)          # calendário conhecido: decido em t a posição que rende 2 pregões depois (execução t+1)
    else:
        compra = -lim if modo == "petroleo_curva" else -np.inf          # gás: só a ponta vendida (quem rola paga o contango)
        lado = pd.Series(np.where(decl > lim, -1.0, np.where(decl < compra, 1.0, 0.0)), index=K.index)
    n = pd.Series(float(alavancagem), index=K.index).round()
    n = n.where(K["noc"] * n <= TETO_ALAV * alavancagem * capital, 0)
    n = n.where(F.vol_brl(K) <= TETO_VOL * alavancagem * capital, 0)      # 1 contrato com vol > 35% do capital: não cabe
    out = {a: pd.Series(0.0, index=K.index) for a in ESPEC}
    out[inst] = (lado * n).fillna(0)
    Ko = {a: (K if a == inst else _contrato(d, a)[0].reindex(K.index)) for a in ESPEC}
    return pd.DataFrame(out), Ko


F.montar(globals(), gera, carrega)
