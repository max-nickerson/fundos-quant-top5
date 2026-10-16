# Frente pf2_futuros — resultados da bateria final (gerado automaticamente)

Gerado por `pf/gerar_cadernos.py` a partir de `pf/resultados/bateria/`. IR de pessoa física por `pf/ir.py` (mensal na B3 com isenção de ações ≤ R$ 20 mil/mês, anual no exterior). Ordem: nota do ranking.

### Agro B3: spread de milho set x mar+1 — AUDITADA (entra só com o H+1 negociando; meio spread R$ 0,20/saca no H+1)  (`fu_agro_spread_aud`)

**Tese:** Vendido no milho de setembro (safrinha) e comprado no março seguinte de mar a ago: anda com o hedge do produtor e vende o seguro de clima do consumidor

**Instrumentos:** [('B3', 'BGI V x K', '330 @ por perna', 'R$ 18/perna/lado'), ('B3', 'CCM U x H+1', '450 sacas', 'R$ 6/perna/lado'), ('B3', 'ICF U x Z', '100 sacas (US$)', 'R$ 29/perna/lado'), ('Tesouro Direto', 'Tesouro Selic', 'garantia', '0')]

**Aplicável:** True — Spreads de calendário cabem em R$ 20 mil (margem reduzida de spread em Tesouro Selic); vencimentos longos pouco líquidos: 1 tick de custo.

| métrica | valor |
|---|---|
| OOS desde | 2023-01 |
| retorno OOS a.a. (R$ 20 mil) | 22.5% vs CDI 13.1% |
| ativo OOS pp (R$ 20 mil / R$ 50 mil) | +9.40 / +3.79 |
| depois do IR (classe O.CLASSE_IR) pp, 20k / 50k | +7.61 / +3.12 |
| IR OOS / Sharpe | +0.69 / +0.69 |
| pior queda | -10.1% |
| PBO / Sharpe deflacionado | 33% / +39% |
| leque de parâmetros p5 / mediana / p95 | +9.40 / +9.40 / +9.40 |
| custo 2x / execução t+2 | +8.01 / +9.77 |
| walk-forward | -1.89 |
| sem os 10 melhores negócios | -0.11 |
| placebo p | 0.14 |
| look-ahead (truncamento) | passou |

**10 melhores negócios**

| ativo      |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:-----------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| CCM spread |     -1 | 2022-03-08 00:00:00 | 2022-08-31 00:00:00 |    124 |        9.9  |        24.67 |
| CCM spread |     -1 | 2021-03-08 00:00:00 | 2021-06-11 00:00:00 |     67 |        8.59 |        17.45 |
| CCM spread |     -1 | 2026-03-04 00:00:00 | 2026-08-31 00:00:00 |    125 |        9.07 |        16.19 |
| CCM spread |     -1 | 2023-03-13 00:00:00 | 2023-08-31 00:00:00 |    120 |       24.97 |        12.52 |
| CCM spread |     -1 | 2025-03-12 00:00:00 | 2025-08-29 00:00:00 |    119 |        3.8  |         6.22 |
| CCM spread |     -1 | 2018-03-08 00:00:00 | 2018-07-10 00:00:00 |     86 |        6.49 |         5.2  |
| CCM spread |     -1 | 2024-03-05 00:00:00 | 2024-08-30 00:00:00 |    126 |       -0.87 |         0.88 |
| CCM spread |     -1 | 2021-07-14 00:00:00 | 2021-08-31 00:00:00 |     35 |        0.18 |         0.48 |
| CCM spread |     -1 | 2019-07-12 00:00:00 | 2019-08-30 00:00:00 |     36 |       -1.25 |        -1.3  |
| CCM spread |     -1 | 2019-04-22 00:00:00 | 2019-07-10 00:00:00 |     56 |       -2.81 |        -1.91 |

**10 piores negócios**

| ativo      |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:-----------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| CCM spread |     -1 | 2020-04-07 00:00:00 | 2020-08-31 00:00:00 |    101 |       -4.52 |       -12.41 |
| CCM spread |     -1 | 2021-06-15 00:00:00 | 2021-07-12 00:00:00 |     20 |       -3.32 |        -2.99 |
| CCM spread |     -1 | 2018-07-12 00:00:00 | 2018-08-31 00:00:00 |     37 |       -2.35 |        -2.45 |
| CCM spread |     -1 | 2019-04-22 00:00:00 | 2019-07-10 00:00:00 |     56 |       -2.81 |        -1.91 |
| CCM spread |     -1 | 2019-07-12 00:00:00 | 2019-08-30 00:00:00 |     36 |       -1.25 |        -1.3  |
| CCM spread |     -1 | 2021-07-14 00:00:00 | 2021-08-31 00:00:00 |     35 |        0.18 |         0.48 |
| CCM spread |     -1 | 2024-03-05 00:00:00 | 2024-08-30 00:00:00 |    126 |       -0.87 |         0.88 |
| CCM spread |     -1 | 2018-03-08 00:00:00 | 2018-07-10 00:00:00 |     86 |        6.49 |         5.2  |
| CCM spread |     -1 | 2025-03-12 00:00:00 | 2025-08-29 00:00:00 |    119 |        3.8  |         6.22 |
| CCM spread |     -1 | 2023-03-13 00:00:00 | 2023-08-31 00:00:00 |    120 |       24.97 |        12.52 |

**Quem trouxe o retorno (soma por ativo, pp)**

| ativo      |   sum |   count |
|:-----------|------:|--------:|
| CCM spread | 62.56 |      13 |

### Brasil x S&P: WIN no pânico relativo (resíduo do Ibovespa em US$)  (`fu_brasil_relativo`)

**Tese:** Compra 1 WIN quando o Ibovespa em dólar cai muito mais que beta x S&P (estrangeiro vendendo Brasil), segura H dias; hedge em MES não cabe

**Instrumentos:** [('B3', 'WIN', 'R$ 0,20 x Ibovespa (≈ R$ 41 mil)', 'R$ 1,10/lado'), ('IBKR/CME', 'MES', 'US$ 5 x S&P (≈ R$ 210 mil)', 'US$ 1,25/lado'), ('Tesouro Direto', 'Tesouro Selic', 'garantia', '0')]

**Aplicável:** True — WIN cabe (≈ 2x R$ 20 mil, 0,8x R$ 50 mil); o hedge em MES (≈ R$ 210 mil) arredonda para zero contratos — o fundo é WIN sem hedge.

| métrica | valor |
|---|---|
| OOS desde | 2021-01 |
| retorno OOS a.a. (R$ 20 mil) | 11.2% vs CDI 11.4% |
| ativo OOS pp (R$ 20 mil / R$ 50 mil) | -0.25 / +0.71 |
| depois do IR (classe futuros_b3) pp, 20k / 50k | -0.25 / +0.69 |
| IR OOS / Sharpe | +0.02 / +0.02 |
| pior queda | -9.9% |
| PBO / Sharpe deflacionado | 10% / +7% |
| leque de parâmetros p5 / mediana / p95 | -5.12 / -2.18 / -0.17 |
| custo 2x / execução t+2 | -0.33 / -2.88 |
| walk-forward | -0.25 |
| sem os 10 melhores negócios | -6.22 |
| placebo p | 0.51 |
| look-ahead (truncamento) | passou |

**10 melhores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| WIN     |      1 | 2008-10-28 00:00:00 | 2008-11-05 00:00:00 |      7 |       27.93 |        24.65 |
| WIN     |      1 | 2016-04-08 00:00:00 | 2016-04-14 00:00:00 |      5 |        7.76 |         7.52 |
| WIN     |      1 | 2010-05-20 00:00:00 | 2010-05-31 00:00:00 |      8 |        5.33 |         6.36 |
| WIN     |      1 | 2012-06-28 00:00:00 | 2012-07-05 00:00:00 |      6 |        5.96 |         6.32 |
| WIN     |      1 | 2022-10-03 00:00:00 | 2022-10-07 00:00:00 |      5 |        5.49 |         6.04 |
| WIN     |      1 | 2011-11-25 00:00:00 | 2011-12-01 00:00:00 |      5 |        4.96 |         5.48 |
| WIN     |      1 | 2015-03-12 00:00:00 | 2015-03-18 00:00:00 |      5 |        5.11 |         5    |
| WIN     |      1 | 2018-02-14 00:00:00 | 2018-02-20 00:00:00 |      5 |        5.93 |         4.79 |
| WIN     |      1 | 2013-09-03 00:00:00 | 2013-09-09 00:00:00 |      5 |        4.49 |         4.65 |
| WIN     |      1 | 2010-07-02 00:00:00 | 2010-07-13 00:00:00 |      8 |        3.68 |         4.5  |

**10 piores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| WIN     |      1 | 2020-02-28 00:00:00 | 2020-03-31 00:00:00 |     23 |      -29.35 |       -25.07 |
| WIN     |      1 | 2013-06-04 00:00:00 | 2013-07-03 00:00:00 |     22 |      -17.04 |       -18.46 |
| WIN     |      1 | 2008-10-01 00:00:00 | 2008-10-20 00:00:00 |     14 |      -20.96 |       -13.43 |
| WIN     |      1 | 2018-05-23 00:00:00 | 2018-06-21 00:00:00 |     21 |      -15.75 |       -13.06 |
| WIN     |      1 | 2016-01-11 00:00:00 | 2016-01-26 00:00:00 |     12 |       -8.25 |        -8.97 |
| WIN     |      1 | 2022-06-13 00:00:00 | 2022-07-01 00:00:00 |     14 |       -6.83 |        -7.22 |
| WIN     |      1 | 2024-12-18 00:00:00 | 2025-01-03 00:00:00 |     11 |       -5.42 |        -6.78 |
| WIN     |      1 | 2026-03-05 00:00:00 | 2026-03-17 00:00:00 |      9 |       -3.16 |        -5.86 |
| WIN     |      1 | 2022-04-26 00:00:00 | 2022-05-05 00:00:00 |      8 |       -5.2  |        -5.77 |
| WIN     |      1 | 2014-10-20 00:00:00 | 2014-11-04 00:00:00 |     12 |       -2.89 |        -3.22 |

**Quem trouxe o retorno (soma por ativo, pp)**

| ativo   |   sum |   count |
|:--------|------:|--------:|
| WIN     | 15.04 |      85 |

### Nikkei 225 Micro (OSE): pânico com iene forte (carry + margem do varejo)  (`fu_asia_nikkei`)

**Tese:** Compra 1 micro Nikkei depois de queda forte com o iene subindo (desmonte do carry e chamada de margem do varejo japonês), segura H dias

**Instrumentos:** [('IBKR/OSE', 'N225MC', '¥10 x Nikkei (≈ R$ 25 mil)', '¥57/lado'), ('Tesouro Direto', 'Tesouro Selic', 'caixa', '0')]

**Aplicável:** True — Nikkei Micro cabe (≈ 1,25x R$ 20 mil; margem ≈ R$ 2,5 mil na IBKR); Mini-KOSPI 200 (≈ R$ 170 mil) e mini Nikkei (≈ R$ 250 mil) não cabem. Micro só existe desde mai/2023: antes o resultado é hipotético.

| métrica | valor |
|---|---|
| OOS desde | 2021-01 |
| retorno OOS a.a. (R$ 20 mil) | 8.2% vs CDI 11.4% |
| ativo OOS pp (R$ 20 mil / R$ 50 mil) | -3.22 / -2.00 |
| depois do IR (classe exterior) pp, 20k / 50k | -3.17 / -1.97 |
| IR OOS / Sharpe | -0.34 / -0.34 |
| pior queda | -15.2% |
| PBO / Sharpe deflacionado | 74% / +4% |
| leque de parâmetros p5 / mediana / p95 | -3.08 / -1.71 / -0.49 |
| custo 2x / execução t+2 | -3.33 / +3.03 |
| walk-forward | -0.56 |
| sem os 10 melhores negócios | -1.62 |
| placebo p | 0.94 |
| look-ahead (truncamento) | passou |

**10 melhores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| N225MC  |      1 | 2008-10-28 00:00:00 | 2008-11-04 00:00:00 |      6 |       27.29 |        25.76 |
| N225MC  |      1 | 2016-01-22 00:00:00 | 2016-01-29 00:00:00 |      6 |        9.41 |         9.86 |
| N225MC  |      1 | 2024-08-07 00:00:00 | 2024-08-16 00:00:00 |      8 |        9.81 |         9.76 |
| N225MC  |      1 | 2011-03-16 00:00:00 | 2011-03-28 00:00:00 |      9 |       10.22 |         8.95 |
| N225MC  |      1 | 2020-04-03 00:00:00 | 2020-04-13 00:00:00 |      7 |        6.93 |         6.02 |
| N225MC  |      1 | 2014-12-18 00:00:00 | 2014-12-24 00:00:00 |      5 |        6.19 |         5.88 |
| N225MC  |      1 | 2023-10-06 00:00:00 | 2023-10-12 00:00:00 |      5 |        4.61 |         4.9  |
| N225MC  |      1 | 2015-10-01 00:00:00 | 2015-10-07 00:00:00 |      5 |        5.41 |         4.62 |
| N225MC  |      1 | 2014-04-15 00:00:00 | 2014-04-21 00:00:00 |      5 |        4.36 |         4.48 |
| N225MC  |      1 | 2016-04-07 00:00:00 | 2016-04-13 00:00:00 |      5 |        4.27 |         4.35 |

**10 piores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| N225MC  |      1 | 2020-03-02 00:00:00 | 2020-03-23 00:00:00 |     16 |      -20.02 |       -19.11 |
| N225MC  |      1 | 2024-07-22 00:00:00 | 2024-08-05 00:00:00 |     11 |      -21.42 |       -16.27 |
| N225MC  |      1 | 2008-10-07 00:00:00 | 2008-10-20 00:00:00 |     10 |      -13.97 |       -11.51 |
| N225MC  |      1 | 2013-05-29 00:00:00 | 2013-06-17 00:00:00 |     14 |       -8.85 |        -9.31 |
| N225MC  |      1 | 2025-04-07 00:00:00 | 2025-04-17 00:00:00 |      9 |        1.81 |        -8.66 |
| N225MC  |      1 | 2008-01-09 00:00:00 | 2008-01-16 00:00:00 |      6 |       -7.02 |        -7.32 |
| N225MC  |      1 | 2016-01-11 00:00:00 | 2016-01-20 00:00:00 |      8 |       -7.19 |        -6.55 |
| N225MC  |      1 | 2018-02-01 00:00:00 | 2018-02-08 00:00:00 |      6 |       -5.19 |        -5.3  |
| N225MC  |      1 | 2015-08-25 00:00:00 | 2015-09-04 00:00:00 |      9 |       -3.99 |        -4.64 |
| N225MC  |      1 | 2008-03-05 00:00:00 | 2008-03-13 00:00:00 |      7 |       -4.27 |        -4.42 |

**Quem trouxe o retorno (soma por ativo, pp)**

| ativo   |   sum |   count |
|:--------|------:|--------:|
| N225MC  |  3.92 |      43 |

### Micro Treasury Yield: concessão de leilão (30Y/10Y) e curva 2s10s  (`fu_treasury_micro`)

**Tese:** Comprado em yield do micro de 30 anos do anúncio até o leilão (dealers abrindo balanço para a oferta nova), vendido depois

**Instrumentos:** [('IBKR/CBOT', '30Y', 'US$ 10/bp', 'US$ 1,62/lado'), ('IBKR/CBOT', '10Y', 'US$ 10/bp', 'US$ 1,62/lado'), ('IBKR/CBOT', '2YY', 'US$ 10/bp', 'US$ 1,62/lado'), ('Tesouro Direto', 'Tesouro Selic', 'caixa', '0')]

**Aplicável:** True — 1 micro de yield tem vol ≈ US$ 600-1.000/ano (≈ 15-25% de R$ 20 mil) e margem ≈ R$ 2 mil: cabe. Antes de ago/2021 é hipotético.

| métrica | valor |
|---|---|
| OOS desde | 2021-01 |
| retorno OOS a.a. (R$ 20 mil) | 4.1% vs CDI 11.4% |
| ativo OOS pp (R$ 20 mil / R$ 50 mil) | -7.37 / -2.86 |
| depois do IR (classe exterior) pp, 20k / 50k | -7.31 / -2.83 |
| IR OOS / Sharpe | -0.43 / -0.43 |
| pior queda | -28.5% |
| PBO / Sharpe deflacionado | 48% / +1% |
| leque de parâmetros p5 / mediana / p95 | -12.59 / -7.37 / -0.88 |
| custo 2x / execução t+2 | -9.98 / -15.89 |
| walk-forward | -4.14 |
| sem os 10 melhores negócios | -18.61 |
| placebo p | 0.79 |
| look-ahead (truncamento) | passou |

**10 melhores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| 10Y     |     -1 | 2023-03-09 00:00:00 | 2023-03-13 00:00:00 |      3 |        3.47 |        11    |
| 10Y     |      1 | 2025-04-07 00:00:00 | 2025-04-09 00:00:00 |      3 |        2.67 |         9.55 |
| 10Y     |     -1 | 2023-12-12 00:00:00 | 2023-12-14 00:00:00 |      3 |        2.48 |         7.58 |
| 10Y     |     -1 | 2022-11-10 00:00:00 | 2022-11-14 00:00:00 |      3 |        1.91 |         6.11 |
| 10Y     |      1 | 2023-02-03 00:00:00 | 2023-02-08 00:00:00 |      4 |        1.86 |         5.75 |
| 10Y     |      1 | 2024-02-02 00:00:00 | 2024-02-07 00:00:00 |      4 |        1.78 |         5.38 |
| 10Y     |      1 | 2020-11-06 00:00:00 | 2020-11-10 00:00:00 |      3 |        1.52 |         5.11 |
| 10Y     |     -1 | 2024-06-12 00:00:00 | 2024-06-14 00:00:00 |      3 |        1.52 |         5.01 |
| 10Y     |      1 | 2022-03-07 00:00:00 | 2022-03-09 00:00:00 |      3 |        1.59 |         4.92 |
| 10Y     |      1 | 2025-02-07 00:00:00 | 2025-02-12 00:00:00 |      4 |        1.36 |         4.79 |

**10 piores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| 10Y     |     -1 | 2022-06-09 00:00:00 | 2022-06-13 00:00:00 |      3 |       -3.15 |        -9.88 |
| 10Y     |      1 | 2023-10-09 00:00:00 | 2023-10-11 00:00:00 |      3 |       -1.59 |        -5.21 |
| 10Y     |     -1 | 2022-03-10 00:00:00 | 2022-03-14 00:00:00 |      3 |       -1.57 |        -5    |
| 10Y     |      1 | 2023-07-10 00:00:00 | 2023-07-12 00:00:00 |      3 |       -1.58 |        -4.94 |
| 10Y     |      1 | 2023-08-04 00:00:00 | 2023-08-09 00:00:00 |      4 |       -1.58 |        -4.93 |
| 10Y     |     -1 | 2023-04-13 00:00:00 | 2023-04-17 00:00:00 |      3 |       -1.53 |        -4.78 |
| 10Y     |     -1 | 2023-08-10 00:00:00 | 2023-08-14 00:00:00 |      3 |       -1.53 |        -4.73 |
| 10Y     |      1 | 2023-11-03 00:00:00 | 2023-11-08 00:00:00 |      4 |       -1.43 |        -4.52 |
| 10Y     |      1 | 2025-08-01 00:00:00 | 2025-08-06 00:00:00 |      4 |       -1.2  |        -4.3  |
| 10Y     |     -1 | 2024-12-12 00:00:00 | 2024-12-16 00:00:00 |      3 |       -1.04 |        -3.95 |

**Quem trouxe o retorno (soma por ativo, pp)**

| ativo   |   sum |   count |
|:--------|------:|--------:|
| 10Y     | 49.61 |     428 |

### Energia micro (MNG/MCL): curva (quem rola paga o contango) e sazonalidade do gás  (`fu_energia_curva`)

**Tese:** Vendido em micro gás natural quando a curva está em contango (UNG/índices rolando pagam), comprado na backwardation; MCL pela mesma regra

**Instrumentos:** [('IBKR/NYMEX', 'MNG', '1.000 MMBtu (≈ R$ 18 mil)', 'US$ 3,15/lado'), ('IBKR/NYMEX', 'MCL', '100 bbl (≈ R$ 53 mil)', 'US$ 1,85/lado'), ('Tesouro Direto', 'Tesouro Selic', 'caixa', '0')]

**Aplicável:** True — Teto de risco: 1 contrato com vol anual > 35% do capital não opera (1 MNG tem vol de 45-80% de R$ 20 mil: na prática só opera com R$ 50 mil). MNG cabe em nocional com R$ 20 mil (≈ 0,9x; margem ≈ R$ 2,7 mil); MCL (≈ R$ 53 mil) só cabe com R$ 50 mil. MNG existe desde nov/2023 e MCL desde jul/2021: antes disso o resultado é hipotético (subjacente igual, tamanho do micro).

| métrica | valor |
|---|---|
| OOS desde | 2021-01 |
| retorno OOS a.a. (R$ 20 mil) | 5.9% vs CDI 11.4% |
| ativo OOS pp (R$ 20 mil / R$ 50 mil) | -5.56 / +1.44 |
| depois do IR (classe exterior) pp, 20k / 50k | -5.47 / +1.26 |
| IR OOS / Sharpe | -0.41 / -0.41 |
| pior queda | -15.4% |
| PBO / Sharpe deflacionado | 82% / +2% |
| leque de parâmetros p5 / mediana / p95 | -5.56 / -5.56 / -5.56 |
| custo 2x / execução t+2 | -6.36 / -7.60 |
| walk-forward | -8.02 |
| sem os 10 melhores negócios | -2.04 |
| placebo p | 0.72 |
| look-ahead (truncamento) | passou |

**10 melhores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| MNG     |     -1 | 2008-07-17 00:00:00 | 2008-09-18 00:00:00 |     46 |       45.4  |        31.33 |
| MNG     |     -1 | 2009-03-02 00:00:00 | 2009-09-30 00:00:00 |    153 |       16.71 |        14.02 |
| MNG     |     -1 | 2010-03-01 00:00:00 | 2010-09-30 00:00:00 |    154 |       27.93 |        11.77 |
| MNG     |     -1 | 2019-03-01 00:00:00 | 2019-09-30 00:00:00 |    152 |       19.17 |        10.02 |
| MNG     |     -1 | 2026-06-03 00:00:00 | 2026-09-30 00:00:00 |     86 |        7.15 |         8.07 |
| MNG     |     -1 | 2015-03-02 00:00:00 | 2015-09-30 00:00:00 |    153 |       10.42 |         7.33 |
| MNG     |     -1 | 2014-03-03 00:00:00 | 2014-09-30 00:00:00 |    152 |       10.13 |         5.87 |
| MNG     |     -1 | 2011-03-01 00:00:00 | 2011-09-30 00:00:00 |    154 |       12.08 |         5.31 |
| MNG     |     -1 | 2024-05-28 00:00:00 | 2024-05-31 00:00:00 |      4 |        7.65 |         4.94 |
| MNG     |     -1 | 2024-07-15 00:00:00 | 2024-07-15 00:00:00 |      1 |        6.6  |         4.1  |

**10 piores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| MNG     |     -1 | 2016-03-01 00:00:00 | 2016-09-30 00:00:00 |    154 |      -34.95 |       -14.46 |
| MNG     |     -1 | 2024-07-26 00:00:00 | 2024-09-30 00:00:00 |     47 |      -18.42 |       -11.6  |
| MNG     |     -1 | 2008-03-03 00:00:00 | 2008-04-29 00:00:00 |     42 |      -13.88 |       -10.4  |
| MNG     |     -1 | 2026-05-04 00:00:00 | 2026-05-29 00:00:00 |     20 |      -11.46 |        -8.21 |
| MNG     |     -1 | 2024-03-01 00:00:00 | 2024-05-16 00:00:00 |     55 |      -13.17 |        -7.23 |
| MNG     |     -1 | 2018-03-01 00:00:00 | 2018-09-28 00:00:00 |    152 |      -11.97 |        -6.35 |
| MNG     |     -1 | 2020-09-23 00:00:00 | 2020-09-24 00:00:00 |      2 |      -10.01 |        -5.38 |
| MNG     |     -1 | 2008-05-02 00:00:00 | 2008-05-06 00:00:00 |      3 |       -4.76 |        -4.22 |
| MNG     |     -1 | 2025-08-27 00:00:00 | 2025-08-28 00:00:00 |      2 |       -4.87 |        -3.86 |
| MNG     |     -1 | 2025-09-22 00:00:00 | 2025-09-30 00:00:00 |      7 |       -4.04 |        -3.29 |

**Quem trouxe o retorno (soma por ativo, pp)**

| ativo   |   sum |   count |
|:--------|------:|--------:|
| MNG     | 26.47 |      30 |

### Bitcoin B3 (BIT) na liquidação dos perpétuos: funding negativo + queda  (`fu_b3_cripto_panico`)

**Tese:** Compra o futuro de bitcoin da B3 depois da cascata de liquidação offshore (queda forte + funding negativo), segura H dias

**Instrumentos:** [('B3', 'BIT', '0,01 BTC (≈ R$ 4,1 mil; 0,1 BTC até jun/2025)', '0,10%/lado'), ('Tesouro Direto', 'Tesouro Selic', 'garantia', '0')]

**Aplicável:** True — Cabe com folga desde jun/2025 (0,01 BTC); de abr/2024 a jun/2025 o contrato de 0,1 BTC (R$ 35-60 mil) só entrava até 2,5x o capital. Antes de abr/2024 é hipotético (BIT não existia).

| métrica | valor |
|---|---|
| OOS desde | 2023-01 |
| retorno OOS a.a. (R$ 20 mil) | 6.6% vs CDI 13.1% |
| ativo OOS pp (R$ 20 mil / R$ 50 mil) | -6.50 / -5.19 |
| depois do IR (classe futuros_b3) pp, 20k / 50k | -6.39 / -5.10 |
| IR OOS / Sharpe | -0.49 / -0.49 |
| pior queda | -16.2% |
| PBO / Sharpe deflacionado | 58% / +0% |
| leque de parâmetros p5 / mediana / p95 | -8.44 / -6.40 / -3.87 |
| custo 2x / execução t+2 | -6.87 / -3.34 |
| walk-forward | +8.23 |
| sem os 10 melhores negócios | -1.47 |
| placebo p | 0.97 |
| look-ahead (truncamento) | passou |

**10 melhores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| BIT     |      1 | 2020-03-17 00:00:00 | 2020-03-24 00:00:00 |      6 |       38.79 |        32.98 |
| BIT     |      1 | 2022-02-23 00:00:00 | 2022-03-03 00:00:00 |      5 |       10.3  |         9.75 |
| BIT     |      1 | 2021-06-23 00:00:00 | 2021-06-30 00:00:00 |      6 |        6.71 |         5.33 |
| BIT     |      1 | 2022-03-09 00:00:00 | 2022-03-15 00:00:00 |      5 |        3.74 |         3.53 |
| BIT     |      1 | 2026-06-29 00:00:00 | 2026-07-03 00:00:00 |      5 |        2.87 |         3.05 |
| BIT     |      1 | 2026-06-09 00:00:00 | 2026-06-15 00:00:00 |      5 |        2.35 |         2.2  |
| BIT     |      1 | 2019-11-27 00:00:00 | 2019-12-03 00:00:00 |      5 |        1.29 |         1.96 |
| BIT     |      1 | 2022-06-17 00:00:00 | 2022-06-27 00:00:00 |      7 |       -1.95 |        -2.31 |
| BIT     |      1 | 2021-05-21 00:00:00 | 2021-05-27 00:00:00 |      5 |       -3.6  |        -3.96 |
| BIT     |      1 | 2024-08-09 00:00:00 | 2024-08-15 00:00:00 |      5 |       -5.94 |       -10.15 |

**10 piores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| BIT     |      1 | 2026-02-04 00:00:00 | 2026-02-18 00:00:00 |      9 |      -13.56 |       -14.03 |
| BIT     |      1 | 2022-11-11 00:00:00 | 2022-11-21 00:00:00 |      6 |      -12.85 |       -12.48 |
| BIT     |      1 | 2024-08-09 00:00:00 | 2024-08-15 00:00:00 |      5 |       -5.94 |       -10.15 |
| BIT     |      1 | 2021-05-21 00:00:00 | 2021-05-27 00:00:00 |      5 |       -3.6  |        -3.96 |
| BIT     |      1 | 2022-06-17 00:00:00 | 2022-06-27 00:00:00 |      7 |       -1.95 |        -2.31 |
| BIT     |      1 | 2019-11-27 00:00:00 | 2019-12-03 00:00:00 |      5 |        1.29 |         1.96 |
| BIT     |      1 | 2026-06-09 00:00:00 | 2026-06-15 00:00:00 |      5 |        2.35 |         2.2  |
| BIT     |      1 | 2026-06-29 00:00:00 | 2026-07-03 00:00:00 |      5 |        2.87 |         3.05 |
| BIT     |      1 | 2022-03-09 00:00:00 | 2022-03-15 00:00:00 |      5 |        3.74 |         3.53 |
| BIT     |      1 | 2021-06-23 00:00:00 | 2021-06-30 00:00:00 |      6 |        6.71 |         5.33 |

**Quem trouxe o retorno (soma por ativo, pp)**

| ativo   |   sum |   count |
|:--------|------:|--------:|
| BIT     | 15.85 |      12 |

### Agro B3: spread safra x entressafra (milho: vende setembro, compra março+1)  (`fu_agro_spread`)

**Tese:** Vendido no milho de setembro (safrinha) e comprado no março seguinte de mar a ago: anda com o hedge do produtor e vende o seguro de clima do consumidor

**Instrumentos:** [('B3', 'BGI V x K', '330 @ por perna', 'R$ 18/perna/lado'), ('B3', 'CCM U x H+1', '450 sacas', 'R$ 6/perna/lado'), ('B3', 'ICF U x Z', '100 sacas (US$)', 'R$ 29/perna/lado'), ('Tesouro Direto', 'Tesouro Selic', 'garantia', '0')]

**Aplicável:** True — Spreads de calendário cabem em R$ 20 mil (margem reduzida de spread em Tesouro Selic); vencimentos longos pouco líquidos: 1 tick de custo.

| métrica | valor |
|---|---|
| OOS desde | 2023-01 |
| retorno OOS a.a. (R$ 20 mil) | 24.8% vs CDI 13.1% |
| ativo OOS pp (R$ 20 mil / R$ 50 mil) | +11.70 / +4.67 |
| depois do IR (classe futuros_b3) pp, 20k / 50k | +9.56 / +3.86 |
| IR OOS / Sharpe | +0.84 / +0.84 |
| pior queda | -10.1% |
| PBO / Sharpe deflacionado | 17% / +50% |
| leque de parâmetros p5 / mediana / p95 | +11.70 / +11.70 / +11.70 |
| custo 2x / execução t+2 | +11.54 / +11.64 |
| walk-forward | +11.70 |
| sem os 10 melhores negócios | +0.82 |
| placebo p | 0.14 |
| look-ahead (truncamento) | passou |

**10 melhores negócios**

| ativo      |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:-----------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| CCM spread |     -1 | 2022-03-04 00:00:00 | 2022-08-31 00:00:00 |    126 |        8.92 |        24.11 |
| CCM spread |     -1 | 2026-03-04 00:00:00 | 2026-08-31 00:00:00 |    125 |        9.07 |        16.66 |
| CCM spread |     -1 | 2023-03-03 00:00:00 | 2023-08-31 00:00:00 |    126 |       26.82 |        16.25 |
| CCM spread |     -1 | 2021-03-03 00:00:00 | 2021-06-11 00:00:00 |     70 |        9.6  |        14.99 |
| CCM spread |     -1 | 2025-03-07 00:00:00 | 2025-08-29 00:00:00 |    122 |        4.26 |         6.69 |
| CCM spread |     -1 | 2018-03-05 00:00:00 | 2018-07-10 00:00:00 |     89 |        5.39 |         5.2  |
| CCM spread |     -1 | 2019-03-28 00:00:00 | 2019-07-10 00:00:00 |     72 |        0.98 |         2.21 |
| CCM spread |     -1 | 2024-03-05 00:00:00 | 2024-08-30 00:00:00 |    126 |       -0.87 |         1.36 |
| CCM spread |     -1 | 2021-07-14 00:00:00 | 2021-08-31 00:00:00 |     35 |        0.18 |         0.95 |
| CCM spread |     -1 | 2019-07-12 00:00:00 | 2019-08-30 00:00:00 |     36 |       -1.25 |        -0.83 |

**10 piores negócios**

| ativo      |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:-----------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| CCM spread |     -1 | 2020-03-26 00:00:00 | 2020-08-31 00:00:00 |    109 |       -2.21 |        -9.78 |
| CCM spread |     -1 | 2021-06-15 00:00:00 | 2021-07-12 00:00:00 |     20 |       -3.32 |        -2.51 |
| CCM spread |     -1 | 2018-07-12 00:00:00 | 2018-08-31 00:00:00 |     37 |       -2.35 |        -1.97 |
| CCM spread |     -1 | 2019-07-12 00:00:00 | 2019-08-30 00:00:00 |     36 |       -1.25 |        -0.83 |
| CCM spread |     -1 | 2021-07-14 00:00:00 | 2021-08-31 00:00:00 |     35 |        0.18 |         0.95 |
| CCM spread |     -1 | 2024-03-05 00:00:00 | 2024-08-30 00:00:00 |    126 |       -0.87 |         1.36 |
| CCM spread |     -1 | 2019-03-28 00:00:00 | 2019-07-10 00:00:00 |     72 |        0.98 |         2.21 |
| CCM spread |     -1 | 2018-03-05 00:00:00 | 2018-07-10 00:00:00 |     89 |        5.39 |         5.2  |
| CCM spread |     -1 | 2025-03-07 00:00:00 | 2025-08-29 00:00:00 |    122 |        4.26 |         6.69 |
| CCM spread |     -1 | 2021-03-03 00:00:00 | 2021-06-11 00:00:00 |     70 |        9.6  |        14.99 |

**Quem trouxe o retorno (soma por ativo, pp)**

| ativo      |   sum |   count |
|:-----------|------:|--------:|
| CCM spread | 73.34 |      13 |

### Eurex micro (FSXE/FDXS): pânico europeu, reversão ou tendência  (`fu_eurex_micro`)

**Tese:** Compra 1 micro Euro STOXX 50 depois de queda forte com o V2X no topo (bancos vendidos em gama e vol-alvo vendendo), segura H dias

**Instrumentos:** [('IBKR/Eurex', 'FSXE', 'EUR 1 x SX5E (≈ R$ 38 mil)', 'EUR 1,10/lado'), ('IBKR/Eurex', 'FDXS', 'EUR 1 x DAX (≈ R$ 160 mil)', 'EUR 1,60/lado'), ('Tesouro Direto', 'Tesouro Selic', 'caixa', '0')]

**Aplicável:** True — FSXE cabe (1 contrato ≈ 1,9x R$ 20 mil, 0,8x R$ 50 mil, margem ~R$ 3 mil na IBKR); FDXS não cabe (8x R$ 20 mil) e nunca opera. Micros da Eurex só existem desde mar/2021: antes disso o resultado é hipotético.

| métrica | valor |
|---|---|
| OOS desde | 2021-01 |
| retorno OOS a.a. (R$ 20 mil) | 13.1% vs CDI 11.4% |
| ativo OOS pp (R$ 20 mil / R$ 50 mil) | +1.70 / +2.24 |
| depois do IR (classe exterior) pp, 20k / 50k | +1.67 / +2.21 |
| IR OOS / Sharpe | +0.22 / +0.22 |
| pior queda | -12.6% |
| PBO / Sharpe deflacionado | 14% / +25% |
| leque de parâmetros p5 / mediana / p95 | -0.44 / +1.77 / +6.23 |
| custo 2x / execução t+2 | +1.48 / +2.98 |
| walk-forward | +2.18 |
| sem os 10 melhores negócios | -2.09 |
| placebo p | 0.04 |
| look-ahead (truncamento) | passou |

**10 melhores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| FSXE    |      1 | 2008-10-29 00:00:00 | 2008-11-04 00:00:00 |      5 |       15.66 |        15.36 |
| FSXE    |      1 | 2024-08-06 00:00:00 | 2024-08-16 00:00:00 |      9 |        5.84 |         8.07 |
| FSXE    |      1 | 2015-08-25 00:00:00 | 2015-09-03 00:00:00 |      8 |        6.49 |         7.98 |
| FSXE    |      1 | 2011-09-26 00:00:00 | 2011-09-30 00:00:00 |      5 |        7.61 |         7.66 |
| FSXE    |      1 | 2014-12-16 00:00:00 | 2014-12-23 00:00:00 |      6 |        7.09 |         7.05 |
| FSXE    |      1 | 2016-02-10 00:00:00 | 2016-02-19 00:00:00 |      8 |        5    |         6.08 |
| FSXE    |      1 | 2016-06-16 00:00:00 | 2016-06-22 00:00:00 |      5 |        5.29 |         5.74 |
| FSXE    |      1 | 2010-05-10 00:00:00 | 2010-05-17 00:00:00 |      6 |        5.46 |         5.03 |
| FSXE    |      1 | 2022-01-26 00:00:00 | 2022-02-01 00:00:00 |      5 |        3.64 |         4.52 |
| FSXE    |      1 | 2008-09-19 00:00:00 | 2008-09-26 00:00:00 |      6 |        5.16 |         4.38 |

**10 piores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| FSXE    |      1 | 2020-02-26 00:00:00 | 2020-03-26 00:00:00 |     22 |      -20.09 |       -17.98 |
| FSXE    |      1 | 2011-08-04 00:00:00 | 2011-08-19 00:00:00 |     12 |      -13.5  |       -15.4  |
| FSXE    |      1 | 2015-07-02 00:00:00 | 2015-07-08 00:00:00 |      5 |       -4.77 |        -5.81 |
| FSXE    |      1 | 2008-11-13 00:00:00 | 2008-12-01 00:00:00 |     13 |       -4.69 |        -4.64 |
| FSXE    |      1 | 2026-03-05 00:00:00 | 2026-03-17 00:00:00 |      9 |       -1.7  |        -3.09 |
| FSXE    |      1 | 2011-09-08 00:00:00 | 2011-09-19 00:00:00 |      8 |       -2.51 |        -2.53 |
| FSXE    |      1 | 2022-02-28 00:00:00 | 2022-03-16 00:00:00 |     13 |       -1.89 |        -2.32 |
| FSXE    |      1 | 2008-03-06 00:00:00 | 2008-03-12 00:00:00 |      5 |       -1.02 |        -0.96 |
| FSXE    |      1 | 2018-02-06 00:00:00 | 2018-02-20 00:00:00 |     11 |       -1.13 |        -0.82 |
| FSXE    |      1 | 2015-09-28 00:00:00 | 2015-10-02 00:00:00 |      5 |       -0.75 |        -0.47 |

**Quem trouxe o retorno (soma por ativo, pp)**

| ativo   |   sum |   count |
|:--------|------:|--------:|
| FSXE    | 63.18 |      45 |

### Peso mexicano e rande na B3 (MEX/AFS, US$ 10 mil): carry e compra depois do pânico  (`fu_moedas_em`)

**Tese:** Compra MXN/ZAR contra o dólar (vende o futuro da B3) depois de alta forte do dólar (stop de carry/hedge de EM), carregando o juro

**Instrumentos:** [('B3', 'MEX', 'US$ 10 mil (≈ R$ 55 mil)', '0,30% + R$ 2/lado (sem livro: RFQ)'), ('B3', 'AFS', 'US$ 10 mil', '0,30% + R$ 2/lado'), ('Tesouro Direto', 'Tesouro Selic', 'garantia', '0')]

**Aplicável:** False — Tecnicamente existe (B3, US$ 10 mil), mas não há livro: 0-7 negócios/dia em blocos institucionais, nenhuma oferta no fechamento; pessoa física depende de RFQ e a maioria das corretoras não habilita. 1 contrato = 2,75x R$ 20 mil (vol ~40% do capital). CME 6M/6Z (≈ R$ 150 mil) não cabe.

| métrica | valor |
|---|---|
| OOS desde | 2021-01 |
| retorno OOS a.a. (R$ 20 mil) | 11.3% vs CDI 11.4% |
| ativo OOS pp (R$ 20 mil / R$ 50 mil) | -0.17 / -5.23 |
| depois do IR (classe futuros_b3) pp, 20k / 50k | -0.16 / -5.15 |
| IR OOS / Sharpe | -3506819813147848.50 / -3506819813147848.50 |
| pior queda | 0.0% |
| PBO / Sharpe deflacionado | 64% / +0% |
| leque de parâmetros p5 / mediana / p95 | -0.17 / -0.17 / -0.17 |
| custo 2x / execução t+2 | -0.17 / -0.17 |
| walk-forward | -0.17 |
| sem os 10 melhores negócios | -5.12 |
| placebo p | 0.50 |
| look-ahead (truncamento) | passou |

**10 melhores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| MEX     |      1 | 2022-03-10 00:00:00 | 2022-03-24 00:00:00 |     11 |        5.86 |        13.46 |
| MEX     |      1 | 2017-12-27 00:00:00 | 2018-01-09 00:00:00 |     10 |        3.51 |         5.05 |
| AFS     |      1 | 2011-09-22 00:00:00 | 2011-10-10 00:00:00 |     13 |        5.48 |         4.92 |
| MEX     |      1 | 2021-11-29 00:00:00 | 2021-12-15 00:00:00 |     13 |        2.17 |         4.91 |
| MEX     |      1 | 2016-06-16 00:00:00 | 2016-06-30 00:00:00 |     11 |        3.19 |         4.8  |
| MEX     |      1 | 2019-06-05 00:00:00 | 2019-06-18 00:00:00 |     10 |        2.55 |         4.18 |
| MEX     |      1 | 2013-06-21 00:00:00 | 2013-07-09 00:00:00 |     13 |        4.19 |         4.17 |
| AFS     |      1 | 2011-03-21 00:00:00 | 2011-04-01 00:00:00 |     10 |        4.94 |         3.69 |
| MEX     |      1 | 2022-06-15 00:00:00 | 2022-07-04 00:00:00 |     14 |        1.77 |         3.39 |
| AFS     |      1 | 2014-11-11 00:00:00 | 2014-11-24 00:00:00 |     10 |        2.8  |         3.08 |

**10 piores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| AFS     |      1 | 2008-10-06 00:00:00 | 2008-10-22 00:00:00 |     13 |      -21.3  |       -23.8  |
| MEX     |      1 | 2020-02-26 00:00:00 | 2020-03-10 00:00:00 |     10 |       -8.33 |       -20.26 |
| AFS     |      1 | 2020-03-04 00:00:00 | 2020-03-13 00:00:00 |      8 |       -6.91 |       -17.54 |
| MEX     |      1 | 2008-10-03 00:00:00 | 2008-10-16 00:00:00 |     10 |      -12.49 |       -12.5  |
| MEX     |      1 | 2023-09-29 00:00:00 | 2023-10-24 00:00:00 |     18 |       -3.54 |       -10.04 |
| AFS     |      1 | 2022-04-25 00:00:00 | 2022-05-06 00:00:00 |     10 |       -3.74 |        -9.83 |
| AFS     |      1 | 2026-03-06 00:00:00 | 2026-03-13 00:00:00 |      6 |       -2.57 |        -7.51 |
| MEX     |      1 | 2018-04-25 00:00:00 | 2018-05-23 00:00:00 |     21 |       -3.74 |        -7.47 |
| MEX     |      1 | 2018-10-26 00:00:00 | 2018-11-29 00:00:00 |     25 |       -3.38 |        -7.04 |
| AFS     |      1 | 2018-06-13 00:00:00 | 2018-06-28 00:00:00 |     12 |       -3.25 |        -6.87 |

**Quem trouxe o retorno (soma por ativo, pp)**

| ativo   |    sum |   count |
|:--------|-------:|--------:|
| MEX     | -45.02 |      35 |
| AFS     | -91.52 |      38 |
