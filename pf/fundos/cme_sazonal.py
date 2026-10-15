"""
Sazonalidade e fluxo de índice com MES / M2K: virada do mês, véspera de feriado e rebalanceamento de fim de trimestre.

Negócios (todos com calendário conhecido de antemão — NYSE, sem dado de mercado):
  - virada do mês (último pregão do mês + 3 primeiros): salário, 401(k) e previdência entram no começo do mês e são investidos no índice;
    fundos fazem window dressing no último dia. Comprado em MES/M2K nesses 4 dias.
  - véspera de feriado da NYSE: vendedores a descoberto e market makers reduzem risco antes de 3-4 dias fechados; volume baixo e viés de
    alta documentado (Ariel 1990; ainda presente em small caps). Comprado no pregão anterior ao feriado.
  - fim de trimestre ("trimestre"): fundos de pensão balanceados rebalanceiam ações x títulos nos últimos 5 pregões do trimestre —
    se as ações subiram mais que os títulos no trimestre (SPY − IEF até 7 pregões antes do fim), eles VENDEM ações -> vendido; se
    caíram mais, compram -> comprado. Depois a virada do mês volta a ser comprada.
Tamanho: n = arredonda(alvo x capital / (vol anual de 1 contrato x √fração de dias investidos)). 1 MES ≈ R$ 200 mil (10x R$ 20 mil);
1 M2K ≈ R$ 70 mil. Com R$ 20 mil só cabe M2K, e mesmo assim 1 contrato = ~1,5% do capital por 1% do Russell.
Retorno: SPY/IWM − T-bill (com proventos), sem salto de rolagem; tamanho por ^GSPC/^RUT.
"""
import numpy as np
import pandas as pd
from pandas.tseries.holiday import (AbstractHolidayCalendar, GoodFriday, Holiday, USLaborDay, USMartinLutherKingJr, USMemorialDay,
                                    USPresidentsDay, USThanksgivingDay, nearest_workday)

import cme_comum as K

NOME = "Sazonalidade de índice com MES/M2K"
TESE = "Comprado em micro de índice na virada do mês e véspera de feriado; no fim do trimestre, contra o rebalanceamento das pensões"
BENCHMARK = "CDI"
INICIO, CORTE = "2012-01-01", "2021-01-01"
REGIME = "nenhum"
CUSTO_TROCA = 0.0
PARAMS = {"inst": "MES", "componentes": "tom", "alvo": .2}          # melhor excesso IS (2012-2020) com R$ 20 mil
GRADE = {"inst": ["MES", "M2K"], "componentes": ["tom", "tom+feriado", "tom+feriado+trimestre"]}
VIZINHANCA = {"alvo": (.15, .3)}
CLASSE_IR = "exterior"
APLICAVEL = False
MOTIVO = ("o IS escolheu MES (1 contrato ≈ R$ 200 mil = 10x R$ 20 mil, 4x R$ 50 mil): cada virada de mês vira uma aposta de 4-5 dias "
          "alavancada (ago/2024: −36% do capital num negócio). M2K (≈ R$ 70 mil) perdeu no IS. Só faria sentido com R$ 100 mil+ e, mesmo "
          "assim, o efeito virada do mês sumiu no S&P depois de 2021")
INSTRUMENTOS = [("IBKR/CME", "MES", "US$ 5 x S&P", "US$ 1,25/lado"), ("IBKR/CME", "M2K", "US$ 5 x Russell 2000", "US$ 1,12/lado"),
                ("Tesouro Direto", "Tesouro Selic", "R$ ~150", "0")]
ALAVANCAGENS = [1, 1.5, 2]
MOTIVO_ALAV = "vol-alvo x 1/1,5/2 (o risco é concentrado em ~60 pregões/ano); 5x = 5-15 M2K com R$ 20 mil: um dia de −5% leva 25-75% do capital"


class NYSE(AbstractHolidayCalendar):
    rules = [Holiday("Ano novo", month=1, day=1, observance=nearest_workday), USMartinLutherKingJr, USPresidentsDay, GoodFriday,
             USMemorialDay, Holiday("Juneteenth", month=6, day=19, start_date="2022-01-01", observance=nearest_workday),
             Holiday("Independência", month=7, day=4, observance=nearest_workday), USLaborDay, USThanksgivingDay,
             Holiday("Natal", month=12, day=25, observance=nearest_workday)]


def calendario(ini="2005-01-01", fim="2028-12-31"):
    fer = NYSE().holidays(ini, fim)
    fer = fer[~((fer.month == 12) & (fer.day == 31))]                   # NYSE não fecha 31/12 quando 1/1 cai no sábado
    extra = pd.to_datetime(["2012-10-29", "2012-10-30", "2018-12-05", "2025-01-09"])   # Sandy, Bush, Carter
    dias = pd.bdate_range(ini, fim)
    return dias[~dias.isin(fer.union(extra))]


def gera(d, capital=20000, regime=REGIME, alavancagem=1, inst="MES", componentes="tom", alvo=.2):
    idx = K.dias_us(d)
    Kd = K.contratos(d, [inst], idx)
    cal = calendario()
    s = pd.Series(0.0, index=cal)
    per = pd.Series(cal.to_period("M"), index=cal)
    ult = per.ne(per.shift(-1))
    pos_mes = per.groupby(per).cumcount()
    s[ult | (pos_mes < 3)] = 1.0
    if "feriado" in componentes:
        prox_util = cal[1:].append(pd.DatetimeIndex([cal[-1] + pd.Timedelta(days=1)]))
        vesp = (prox_util - cal).days > np.where(cal.dayofweek == 4, 3, 1)     # próximo pregão pula um dia útil = feriado amanhã
        s[vesp] = 1.0
    if "trimestre" in componentes:
        p = d["precos"]
        tri = pd.Series(cal.to_period("Q"), index=cal)
        pos_fim = tri.groupby(tri).cumcount(ascending=False)                 # 0 = último pregão do trimestre
        ini_tri = tri.ne(tri.shift(1))
        spy = K.para(p["SPY"].dropna(), cal, soma=False)
        rel = np.log(spy)                                                    # ações no trimestre até 7 pregões antes do fim
        rel_ini = rel.where(ini_tri).ffill()
        ganho = (rel - rel_ini).where(pos_fim == 7).groupby(tri).transform("max")
        janela = (pos_fim >= 1) & (pos_fim <= 5)
        s[janela] = np.where(ganho[janela] > .05, -1.0, np.where(ganho[janela] < -.05, 1.0, s[janela]))
    # posição que deve RENDER no pregão D é decidida 2 pregões antes (execução no fechamento de D−1)
    alvo_dia = s.shift(-2).reindex(idx).fillna(0)
    frac = max(float((s != 0).mean()), .05)
    v1 = K.vol_contrato_brl(Kd[inst])
    n = np.floor(alvo * alavancagem * capital / (v1 * np.sqrt(frac)) + .5).clip(upper=20).fillna(0)
    return pd.DataFrame({inst: alvo_dia * n}, index=idx), Kd


K.montar(globals(), gera)
