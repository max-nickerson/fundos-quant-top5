# Frente micro_cme — resultados da bateria final (gerado automaticamente)

Gerado por `pf/gerar_cadernos.py` a partir de `pf/resultados/bateria/`. IR de pessoa física por `pf/ir.py` (mensal na B3 com isenção de ações ≤ R$ 20 mil/mês, anual no exterior). Ordem: nota do ranking.

### Carry G10 com micro FX (CME)  (`cme_carry_g10`)

**Tese:** Comprado no micro da moeda de maior juro e vendido no de menor, 1 contrato por perna, fora quando o risco global vira

**Instrumentos:** [('IBKR/CME', 'M6E', '€ 12.500', 'US$ 0,40 + 2 ticks/lado'), ('IBKR/CME', 'M6B', '£ 6.250', 'idem'), ('IBKR/CME', 'M6A', 'A$ 10.000', 'idem'), ('IBKR/CME', 'MCD', 'C$ 10.000', 'idem'), ('IBKR/CME', 'MSF', 'CHF 12.500', 'idem'), ('IBKR/CME', 'MJY', '¥ 1.250.000', 'idem'), ('Tesouro Direto', 'Tesouro Selic', 'R$ ~150', '0')]

**Aplicável:** True — opera com R$ 20 mil (margem de 2 micros FX ≈ US$ 500-900), mas cada perna tem nocional de 2-4x o capital: 1 par já dá vol de ~15-30% do patrimônio. Micro FX tem pouca liquidez (spread 1-2 ticks); MJY é o micro de iene (¥ 1,25 mi), MSF franco.

| métrica | valor |
|---|---|
| OOS desde | 2021-01 |
| retorno OOS a.a. (R$ 20 mil) | 12.4% vs CDI 11.4% |
| ativo OOS pp (R$ 20 mil / R$ 50 mil) | +0.96 / +0.75 |
| depois do IR (classe exterior) pp, 20k / 50k | +0.03 / +0.40 |
| IR OOS / Sharpe | +0.14 / +0.14 |
| pior queda | -32.3% |
| PBO / Sharpe deflacionado | 69% / +20% |
| leque de parâmetros p5 / mediana / p95 | -0.41 / +0.91 / +1.29 |
| custo 2x / execução t+2 | -2.05 / -0.19 |
| walk-forward | +0.95 |
| sem os 10 melhores negócios | -22.00 |
| placebo p | 0.19 |
| look-ahead (truncamento) | passou |

**10 melhores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| MJY     |     -1 | 2023-03-22 00:00:00 | 2024-07-30 00:00:00 |    341 |       23.55 |        47    |
| MJY     |     -1 | 2012-11-21 00:00:00 | 2014-02-04 00:00:00 |    302 |       22.15 |        30.6  |
| MSF     |     -1 | 2026-04-10 00:00:00 | 2026-10-14 00:00:00 |    130 |        7.05 |        27.54 |
| MJY     |     -1 | 2024-09-23 00:00:00 | 2025-02-27 00:00:00 |    108 |        5.72 |        13.86 |
| MSF     |     -1 | 2022-06-01 00:00:00 | 2022-06-13 00:00:00 |      9 |        3.87 |        12.09 |
| MJY     |     -1 | 2014-10-30 00:00:00 | 2014-12-11 00:00:00 |     30 |        8.62 |        11.74 |
| MSF     |     -1 | 2022-08-12 00:00:00 | 2022-08-23 00:00:00 |      8 |        2.52 |         8.38 |
| MJY     |     -1 | 2014-08-13 00:00:00 | 2014-09-26 00:00:00 |     32 |        6.12 |         8.06 |
| MSF     |     -1 | 2016-06-30 00:00:00 | 2017-04-13 00:00:00 |    199 |        3.29 |         7.65 |
| M6A     |      1 | 2017-05-22 00:00:00 | 2017-08-11 00:00:00 |     58 |        6.1  |         7.21 |

**10 piores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| MJY     |     -1 | 2022-10-24 00:00:00 | 2023-03-13 00:00:00 |     96 |       -9.36 |       -20.78 |
| M6A     |      1 | 2012-11-21 00:00:00 | 2014-02-04 00:00:00 |    302 |      -13.17 |       -14.87 |
| M6B     |      1 | 2024-09-23 00:00:00 | 2025-02-27 00:00:00 |    108 |       -4.43 |       -11.06 |
| MSF     |     -1 | 2025-05-14 00:00:00 | 2025-10-13 00:00:00 |    105 |       -2.68 |       -10.78 |
| MSF     |     -1 | 2025-11-26 00:00:00 | 2026-03-04 00:00:00 |     66 |       -2.52 |       -10    |
| MCD     |      1 | 2022-09-08 00:00:00 | 2022-09-26 00:00:00 |     13 |       -4.2  |        -8.52 |
| M6A     |      1 | 2014-10-30 00:00:00 | 2014-12-11 00:00:00 |     30 |       -5.69 |        -6.43 |
| MSF     |     -1 | 2015-11-20 00:00:00 | 2015-12-04 00:00:00 |     10 |       -2.52 |        -5.84 |
| M6B     |      1 | 2022-06-02 00:00:00 | 2022-06-13 00:00:00 |      8 |       -2.71 |        -5.49 |
| MSF     |     -1 | 2019-10-11 00:00:00 | 2020-01-28 00:00:00 |     74 |       -1.98 |        -5.28 |

**Quem trouxe o retorno (soma por ativo, pp)**

| ativo   |    sum |   count |
|:--------|-------:|--------:|
| MJY     |  83.86 |      21 |
| MSF     |  45.3  |      52 |
| M6B     | -14.2  |      14 |
| MCD     | -15.5  |      26 |
| M6A     | -29.37 |      37 |

### Micro BTC/ETH: tendência pagando a base  (`cme_cripto`)

**Tese:** Comprado em MET/MBT quando a tendência é de alta e a base não está eufórica; vendido (recebendo a base) na tendência de baixa

**Instrumentos:** [('IBKR/CME', 'MBT', '0,1 BTC', 'US$ 3,50/lado'), ('IBKR/CME', 'MET', '0,1 ETH', 'US$ 0,75/lado'), ('Tesouro Direto', 'Tesouro Selic', 'R$ ~150', '0')]

**Aplicável:** True — opera com R$ 20 mil só via MET (0,1 ETH ≈ US$ 240); MBT (0,1 BTC ≈ US$ 8 mil) entra só quando a vol cabe (R$ 50 mil+). Margem de cripto ~40% do nocional, fins de semana sem negociação no CME

| métrica | valor |
|---|---|
| OOS desde | 2023-01 |
| retorno OOS a.a. (R$ 20 mil) | 12.1% vs CDI 13.1% |
| ativo OOS pp (R$ 20 mil / R$ 50 mil) | -0.99 / -1.97 |
| depois do IR (classe exterior) pp, 20k / 50k | -0.98 / -1.93 |
| IR OOS / Sharpe | +0.00 / +0.00 |
| pior queda | -21.2% |
| PBO / Sharpe deflacionado | 46% / +11% |
| leque de parâmetros p5 / mediana / p95 | -9.09 / +0.13 / +13.99 |
| custo 2x / execução t+2 | -3.47 / -1.57 |
| walk-forward | +1.22 |
| sem os 10 melhores negócios | -8.56 |
| placebo p | 0.12 |
| look-ahead (truncamento) | passou |

**10 melhores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| MBT     |      1 | 2019-04-02 00:00:00 | 2019-07-01 00:00:00 |     63 |      151.41 |        30.93 |
| MET     |      1 | 2023-10-31 00:00:00 | 2024-03-18 00:00:00 |     95 |       85.92 |        26.83 |
| MET     |      1 | 2020-11-10 00:00:00 | 2021-01-04 00:00:00 |     37 |      128.76 |        23.07 |
| MET     |      1 | 2026-08-18 00:00:00 | 2026-10-14 00:00:00 |     41 |       29.59 |        11.41 |
| MET     |      1 | 2025-05-13 00:00:00 | 2025-10-20 00:00:00 |    111 |       54.19 |        10.49 |
| MET     |      1 | 2021-01-12 00:00:00 | 2021-02-16 00:00:00 |     24 |       59.65 |         6.34 |
| MET     |      1 | 2020-05-27 00:00:00 | 2020-10-19 00:00:00 |    102 |       83.28 |         6.33 |
| MBT     |      1 | 2020-10-27 00:00:00 | 2020-11-09 00:00:00 |     10 |       16.75 |         6.02 |
| MBT     |      1 | 2019-07-23 00:00:00 | 2019-08-05 00:00:00 |     10 |       13.93 |         2.72 |
| MET     |      1 | 2023-01-24 00:00:00 | 2023-06-20 00:00:00 |    102 |        7.45 |         2.6  |

**10 piores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| MBT     |      1 | 2020-02-04 00:00:00 | 2020-03-16 00:00:00 |     29 |      -46.36 |       -12.2  |
| MET     |      1 | 2024-07-16 00:00:00 | 2024-08-05 00:00:00 |     15 |      -31.22 |        -9.53 |
| MET     |      1 | 2018-06-05 00:00:00 | 2018-06-25 00:00:00 |     15 |      -22.6  |        -5.82 |
| MET     |      1 | 2020-02-11 00:00:00 | 2020-03-23 00:00:00 |     29 |      -40    |        -5.44 |
| MET     |      1 | 2024-11-12 00:00:00 | 2025-02-10 00:00:00 |     60 |      -24.11 |        -5.27 |
| MET     |      1 | 2024-04-02 00:00:00 | 2024-05-13 00:00:00 |     30 |      -17.4  |        -4.96 |
| MBT     |      1 | 2018-09-05 00:00:00 | 2018-09-17 00:00:00 |      9 |      -14.83 |        -4.79 |
| MET     |      1 | 2019-11-12 00:00:00 | 2019-11-25 00:00:00 |     10 |      -21.19 |        -4.47 |
| MET     |      1 | 2026-04-21 00:00:00 | 2026-05-26 00:00:00 |     25 |      -10.7  |        -4.18 |
| MET     |      1 | 2022-04-05 00:00:00 | 2022-04-25 00:00:00 |     14 |      -14.81 |        -3.78 |

**Quem trouxe o retorno (soma por ativo, pp)**

| ativo   |   sum |   count |
|:--------|------:|--------:|
| MET     | 23    |      27 |
| MBT     | 18.11 |      13 |

### Juros EUA pelo ciclo do Fed (micro yield 2Y/10Y)  (`cme_juros_fed`)

**Tese:** Vendido no título (comprado em yield) quando o Fed sobe e comprado quando corta, confirmado pela tendência do próprio yield

**Instrumentos:** [('IBKR/CME', '2YY', 'US$ 10/bp', 'US$ 1,62/lado'), ('IBKR/CME', '10Y', 'US$ 10/bp', 'US$ 1,62/lado'), ('Tesouro Direto', 'Tesouro Selic', 'R$ ~150', '0')]

**Aplicável:** True — opera com R$ 20 mil: margem ~US$ 300-400 por contrato; 1 contrato de 2 anos tem vol de ~25% do capital. Micro Treasury Yield tem pouca liquidez fora do vencimento corrente (rolagem mensal)

| métrica | valor |
|---|---|
| OOS desde | 2021-01 |
| retorno OOS a.a. (R$ 20 mil) | 9.3% vs CDI 11.4% |
| ativo OOS pp (R$ 20 mil / R$ 50 mil) | -2.09 / -2.64 |
| depois do IR (classe exterior) pp, 20k / 50k | -3.06 / -3.40 |
| IR OOS / Sharpe | -0.01 / -0.01 |
| pior queda | -24.3% |
| PBO / Sharpe deflacionado | 67% / +2% |
| leque de parâmetros p5 / mediana / p95 | -5.74 / -3.23 / -0.44 |
| custo 2x / execução t+2 | -3.30 / -3.73 |
| walk-forward | -2.09 |
| sem os 10 melhores negócios | -12.64 |
| placebo p | 0.60 |
| look-ahead (truncamento) | passou |

**10 melhores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| 2YY     |     -1 | 2019-12-31 00:00:00 | 2020-08-24 00:00:00 |    164 |        2.77 |        50.93 |
| 2YY     |      1 | 2022-08-10 00:00:00 | 2022-12-02 00:00:00 |     81 |        1.56 |        20.98 |
| 2YY     |      1 | 2022-03-22 00:00:00 | 2022-07-14 00:00:00 |     79 |        1.32 |        16.38 |
| 2YY     |      1 | 2017-12-19 00:00:00 | 2018-02-02 00:00:00 |     31 |        0.52 |        15.4  |
| 2YY     |      1 | 2018-06-01 00:00:00 | 2018-09-24 00:00:00 |     80 |        0.59 |        14.84 |
| 2YY     |      1 | 2023-06-22 00:00:00 | 2023-10-30 00:00:00 |     91 |        0.78 |         9.58 |
| 2YY     |      1 | 2022-08-02 00:00:00 | 2022-08-08 00:00:00 |      5 |        0.57 |         7.86 |
| 2YY     |      1 | 2018-02-06 00:00:00 | 2018-03-02 00:00:00 |     18 |        0.27 |         6.93 |
| 2YY     |      1 | 2018-03-06 00:00:00 | 2018-05-30 00:00:00 |     60 |        0.16 |         3.22 |
| 2YY     |      1 | 2017-03-01 00:00:00 | 2017-03-02 00:00:00 |      2 |        0.18 |         2.96 |

**10 piores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| 2YY     |     -1 | 2024-09-24 00:00:00 | 2024-10-08 00:00:00 |     11 |       -0.83 |       -12.02 |
| 2YY     |      1 | 2023-02-08 00:00:00 | 2023-03-14 00:00:00 |     24 |       -0.53 |        -7.34 |
| 2YY     |      1 | 2018-09-27 00:00:00 | 2018-11-20 00:00:00 |     39 |       -0.18 |        -5.81 |
| 2YY     |     -1 | 2019-08-06 00:00:00 | 2019-09-13 00:00:00 |     28 |       -0.44 |        -4.82 |
| 2YY     |      1 | 2022-07-18 00:00:00 | 2022-07-22 00:00:00 |      5 |       -0.32 |        -4.65 |
| 2YY     |      1 | 2017-02-13 00:00:00 | 2017-02-24 00:00:00 |      9 |       -0.17 |        -4.55 |
| 2YY     |     -1 | 2025-06-06 00:00:00 | 2025-06-06 00:00:00 |      1 |       -0.23 |        -3.43 |
| 2YY     |      1 | 2023-11-13 00:00:00 | 2023-11-15 00:00:00 |      3 |       -0.26 |        -3.4  |
| 2YY     |     -1 | 2025-02-06 00:00:00 | 2025-02-10 00:00:00 |      3 |       -0.21 |        -3.25 |
| 2YY     |      1 | 2017-03-06 00:00:00 | 2017-04-04 00:00:00 |     22 |       -0.18 |        -3.05 |

**Quem trouxe o retorno (soma por ativo, pp)**

| ativo   |   sum |   count |
|:--------|------:|--------:|
| 2YY     | 73.68 |      70 |

### Metais com micros: pares de razão e sazonalidade do ouro  (`cme_metais`)

**Tese:** Reversão da razão ouro/prata ou cobre/ouro com micros (perna de ouro em 1OZ) e ouro comprado na temporada de demanda física

**Instrumentos:** [('IBKR/COMEX', 'SIL', '1.000 oz', 'US$ 5,85/lado'), ('IBKR/COMEX', 'MHG', '2.500 lb', 'US$ 2,10/lado'), ('IBKR/COMEX', '1OZ', '1 oz', 'US$ 1,35/lado'), ('Tesouro Direto', 'Tesouro Selic', 'R$ ~150', '0')]

**Aplicável:** True — pares de prata não cabem (1 SIL ≈ US$ 56 mil = 15x R$ 20 mil: vol de 1 par > 100% do capital); cobre x ouro só com R$ 50 mil e vol-alvo alta; o sazonal com 1-OUNCE GOLD (1OZ, desde jan/2023, ≈ US$ 4 mil) opera com R$ 20 mil

| métrica | valor |
|---|---|
| OOS desde | 2021-01 |
| retorno OOS a.a. (R$ 20 mil) | 16.8% vs CDI 11.4% |
| ativo OOS pp (R$ 20 mil / R$ 50 mil) | +5.37 / +7.78 |
| depois do IR (classe exterior) pp, 20k / 50k | +4.31 / +6.35 |
| IR OOS / Sharpe | +0.45 / +0.45 |
| pior queda | -18.5% |
| PBO / Sharpe deflacionado | 50% / +63% |
| leque de parâmetros p5 / mediana / p95 | +4.19 / +7.74 / +14.61 |
| custo 2x / execução t+2 | +4.65 / +7.37 |
| walk-forward | +3.34 |
| sem os 10 melhores negócios | -0.71 |
| placebo p | 0.20 |
| look-ahead (truncamento) | passou |

**10 melhores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| 1OZ     |      1 | 2025-08-01 00:00:00 | 2025-12-30 00:00:00 |    105 |       29.8  |        26.69 |
| 1OZ     |      1 | 2019-08-01 00:00:00 | 2020-02-28 00:00:00 |    146 |       10.59 |        14.75 |
| 1OZ     |      1 | 2015-08-03 00:00:00 | 2016-02-29 00:00:00 |    145 |       13.24 |        12.3  |
| 1OZ     |      1 | 2026-08-03 00:00:00 | 2026-08-20 00:00:00 |     14 |       11.56 |        12.15 |
| 1OZ     |      1 | 2024-08-01 00:00:00 | 2025-02-28 00:00:00 |    145 |       13.51 |         9.33 |
| 1OZ     |      1 | 2018-08-01 00:00:00 | 2019-02-28 00:00:00 |    145 |        5.77 |         6.49 |
| 1OZ     |      1 | 2017-08-01 00:00:00 | 2018-02-28 00:00:00 |    146 |        3.03 |         5.51 |
| 1OZ     |      1 | 2026-01-02 00:00:00 | 2026-01-06 00:00:00 |      3 |        4.22 |         4.89 |
| 1OZ     |      1 | 2012-01-05 00:00:00 | 2012-02-29 00:00:00 |     38 |        4.89 |         3.39 |
| 1OZ     |      1 | 2026-01-21 00:00:00 | 2026-01-21 00:00:00 |      1 |        1.44 |         1.8  |

**10 piores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| 1OZ     |      1 | 2016-08-01 00:00:00 | 2017-02-28 00:00:00 |    146 |       -7.56 |       -11.42 |
| 1OZ     |      1 | 2014-08-01 00:00:00 | 2015-02-27 00:00:00 |    145 |       -5.65 |        -9.11 |
| 1OZ     |      1 | 2026-01-26 00:00:00 | 2026-02-02 00:00:00 |      6 |       -6.81 |        -8.76 |
| 1OZ     |      1 | 2012-08-01 00:00:00 | 2013-02-28 00:00:00 |    144 |       -2.05 |        -7.3  |
| 1OZ     |      1 | 2026-09-14 00:00:00 | 2026-10-14 00:00:00 |     23 |       -6.02 |        -6.82 |
| 1OZ     |      1 | 2023-01-11 00:00:00 | 2023-02-28 00:00:00 |     33 |       -3.37 |        -3.4  |
| 1OZ     |      1 | 2023-08-01 00:00:00 | 2024-02-29 00:00:00 |    147 |        0.91 |        -0.67 |
| 1OZ     |      1 | 2026-01-13 00:00:00 | 2026-01-13 00:00:00 |      1 |       -0.15 |        -0.23 |
| 1OZ     |      1 | 2020-08-03 00:00:00 | 2021-01-05 00:00:00 |    108 |       -1.25 |         0.61 |
| 1OZ     |      1 | 2013-08-01 00:00:00 | 2014-02-28 00:00:00 |    146 |       -0.06 |         0.9  |

**Quem trouxe o retorno (soma por ativo, pp)**

| ativo   |   sum |   count |
|:--------|------:|--------:|
| 1OZ     | 51.09 |      20 |

### Sazonalidade de índice com MES/M2K  (`cme_sazonal`)

**Tese:** Comprado em micro de índice na virada do mês e véspera de feriado; no fim do trimestre, contra o rebalanceamento das pensões

**Instrumentos:** [('IBKR/CME', 'MES', 'US$ 5 x S&P', 'US$ 1,25/lado'), ('IBKR/CME', 'M2K', 'US$ 5 x Russell 2000', 'US$ 1,12/lado'), ('Tesouro Direto', 'Tesouro Selic', 'R$ ~150', '0')]

**Aplicável:** False — o IS escolheu MES (1 contrato ≈ R$ 200 mil = 10x R$ 20 mil, 4x R$ 50 mil): cada virada de mês vira uma aposta de 4-5 dias alavancada (ago/2024: −36% do capital num negócio). M2K (≈ R$ 70 mil) perdeu no IS. Só faria sentido com R$ 100 mil+ e, mesmo assim, o efeito virada do mês sumiu no S&P depois de 2021

| métrica | valor |
|---|---|
| OOS desde | 2021-01 |
| retorno OOS a.a. (R$ 20 mil) | 2.6% vs CDI 11.4% |
| ativo OOS pp (R$ 20 mil / R$ 50 mil) | -8.79 / -3.78 |
| depois do IR (classe exterior) pp, 20k / 50k | -8.90 / -3.86 |
| IR OOS / Sharpe | -0.16 / -0.16 |
| pior queda | -45.1% |
| PBO / Sharpe deflacionado | 70% / +8% |
| leque de parâmetros p5 / mediana / p95 | -20.12 / -8.94 / -1.34 |
| custo 2x / execução t+2 | -9.93 / +3.89 |
| walk-forward | -7.37 |
| sem os 10 melhores negócios | -28.05 |
| placebo p | 0.72 |
| look-ahead (truncamento) | passou |

**10 melhores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| MES     |      1 | 2023-10-31 00:00:00 | 2023-11-03 00:00:00 |      4 |        4.51 |        23.46 |
| MES     |      1 | 2020-02-28 00:00:00 | 2020-03-04 00:00:00 |      4 |        5.14 |        17.24 |
| MES     |      1 | 2021-03-31 00:00:00 | 2021-04-06 00:00:00 |      4 |        2.89 |        16.17 |
| MES     |      1 | 2012-12-31 00:00:00 | 2013-01-04 00:00:00 |      4 |        4.53 |        16.14 |
| MES     |      1 | 2024-05-31 00:00:00 | 2024-06-05 00:00:00 |      4 |        2.22 |        15.3  |
| MES     |      1 | 2017-12-29 00:00:00 | 2018-01-04 00:00:00 |      4 |        1.38 |        11.88 |
| MES     |      1 | 2022-01-31 00:00:00 | 2022-01-31 00:00:00 |      1 |        1.8  |        10.66 |
| MES     |      1 | 2020-09-30 00:00:00 | 2020-10-05 00:00:00 |      4 |        2.22 |        10.4  |
| MES     |      1 | 2015-09-30 00:00:00 | 2015-10-05 00:00:00 |      4 |        5.5  |        10.24 |
| MES     |      1 | 2021-10-29 00:00:00 | 2021-11-03 00:00:00 |      4 |        1.4  |         9.05 |

**10 piores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| MES     |      1 | 2018-01-31 00:00:00 | 2018-02-05 00:00:00 |      4 |       -6.35 |       -43.45 |
| MES     |      1 | 2024-07-31 00:00:00 | 2024-08-05 00:00:00 |      4 |       -4.62 |       -36.21 |
| MES     |      1 | 2014-07-31 00:00:00 | 2014-08-05 00:00:00 |      4 |       -2.52 |       -16.74 |
| MES     |      1 | 2019-07-31 00:00:00 | 2019-08-05 00:00:00 |      4 |       -5.65 |       -16.54 |
| MES     |      1 | 2021-11-30 00:00:00 | 2021-12-03 00:00:00 |      4 |       -2.41 |       -15.77 |
| MES     |      1 | 2015-12-31 00:00:00 | 2016-01-06 00:00:00 |      4 |       -3.45 |       -14.3  |
| MES     |      1 | 2022-01-05 00:00:00 | 2022-01-05 00:00:00 |      1 |       -1.92 |       -13.07 |
| MES     |      1 | 2013-05-31 00:00:00 | 2013-06-05 00:00:00 |      4 |       -2.75 |       -12.16 |
| MES     |      1 | 2023-12-29 00:00:00 | 2024-01-04 00:00:00 |      4 |       -2.05 |       -12.08 |
| MES     |      1 | 2014-12-31 00:00:00 | 2015-01-06 00:00:00 |      4 |       -3.75 |       -10.53 |

**Quem trouxe o retorno (soma por ativo, pp)**

| ativo   |   sum |   count |
|:--------|------:|--------:|
| MES     | 60.42 |     137 |

### Tendência multiativos com micros (CME)  (`cme_tendencia`)

**Tese:** Segue a tendência de 12 micros com contratos inteiros: compra o que sobe e vende o que cai, vol-alvo do patrimônio

**Instrumentos:** [('IBKR/CME', 'MES', 'x5', 'US$ 1.25/lado (comissão+meio spread)'), ('IBKR/CME', 'MNQ', 'x2', 'US$ 1.12/lado (comissão+meio spread)'), ('IBKR/CME', 'M2K', 'x5', 'US$ 1.12/lado (comissão+meio spread)'), ('IBKR/CME', 'MGC', 'x10', 'US$ 1.85/lado (comissão+meio spread)'), ('IBKR/CME', '1OZ', 'x1', 'US$ 1.35/lado (comissão+meio spread)'), ('IBKR/CME', 'SIL', 'x1000', 'US$ 5.85/lado (comissão+meio spread)'), ('IBKR/CME', 'MHG', 'x2500', 'US$ 2.10/lado (comissão+meio spread)'), ('IBKR/CME', 'MCL', 'x100', 'US$ 1.85/lado (comissão+meio spread)'), ('IBKR/CME', 'M6E', 'x12500', 'US$ 2.90/lado (comissão+meio spread)'), ('IBKR/CME', 'MJY', 'x1250000', 'US$ 2.90/lado (comissão+meio spread)'), ('IBKR/CME', '10Y', 'x1000', 'US$ 1.62/lado (comissão+meio spread)')]

**Aplicável:** True — opera, mas com R$ 20 mil a carteira cabe só 1-3 contratos dos micros pequenos (1OZ, MCL, micro FX, 10Y, M2K): MES/MNQ/MGC/SIL sozinhos têm vol anual de 50-250% do capital e o algoritmo não os compra

| métrica | valor |
|---|---|
| OOS desde | 2021-01 |
| retorno OOS a.a. (R$ 20 mil) | 16.1% vs CDI 11.4% |
| ativo OOS pp (R$ 20 mil / R$ 50 mil) | +4.65 / +8.31 |
| depois do IR (classe exterior) pp, 20k / 50k | +3.64 / +7.07 |
| IR OOS / Sharpe | +0.29 / +0.29 |
| pior queda | -30.3% |
| PBO / Sharpe deflacionado | 85% / +33% |
| leque de parâmetros p5 / mediana / p95 | -2.93 / +9.15 / +19.78 |
| custo 2x / execução t+2 | +0.62 / +1.73 |
| walk-forward | +5.26 |
| sem os 10 melhores negócios | -24.25 |
| placebo p | 0.10 |
| look-ahead (truncamento) | passou |

**10 melhores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| 1OZ     |      1 | 2025-01-22 00:00:00 | 2025-11-17 00:00:00 |    208 |       42.41 |        43.25 |
| MJY     |     -1 | 2021-12-14 00:00:00 | 2022-06-13 00:00:00 |    125 |       18.07 |        41.81 |
| 10Y     |     -1 | 2019-04-09 00:00:00 | 2020-03-23 00:00:00 |    241 |       14.73 |        36.64 |
| M6E     |     -1 | 2014-12-30 00:00:00 | 2015-03-16 00:00:00 |     52 |       15.68 |        30.05 |
| 1OZ     |      1 | 2024-02-13 00:00:00 | 2025-01-06 00:00:00 |    226 |       24.82 |        25.8  |
| MES     |      1 | 2012-06-12 00:00:00 | 2013-07-08 00:00:00 |    268 |       28.24 |        22.25 |
| MJY     |     -1 | 2012-12-26 00:00:00 | 2013-04-08 00:00:00 |     70 |       16.82 |        22.22 |
| 10Y     |     -1 | 2014-06-24 00:00:00 | 2015-02-09 00:00:00 |    159 |        6.89 |        15.06 |
| 1OZ     |      1 | 2019-06-11 00:00:00 | 2019-09-23 00:00:00 |     73 |       14.17 |        13.9  |
| MJY     |     -1 | 2014-09-16 00:00:00 | 2014-12-15 00:00:00 |     64 |        9.94 |        13.52 |

**10 piores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| M6E     |      1 | 2018-02-13 00:00:00 | 2018-05-29 00:00:00 |     73 |       -6.24 |       -17.51 |
| MJY     |      1 | 2016-10-11 00:00:00 | 2016-11-28 00:00:00 |     34 |       -8.01 |       -16.34 |
| MES     |      1 | 2018-09-05 00:00:00 | 2018-10-15 00:00:00 |     29 |       -5.11 |       -13.84 |
| MJY     |      1 | 2012-01-18 00:00:00 | 2012-03-19 00:00:00 |     43 |       -7.96 |       -13.51 |
| M2K     |     -1 | 2016-01-26 00:00:00 | 2016-03-07 00:00:00 |     29 |       -9.49 |       -13.35 |
| MJY     |     -1 | 2022-11-08 00:00:00 | 2022-11-14 00:00:00 |      5 |       -5.02 |       -11.64 |
| 10Y     |      1 | 2025-02-19 00:00:00 | 2025-03-03 00:00:00 |      9 |       -3.08 |       -11.34 |
| M6E     |      1 | 2021-02-09 00:00:00 | 2021-03-29 00:00:00 |     34 |       -2.32 |       -10.25 |
| 1OZ     |     -1 | 2023-02-14 00:00:00 | 2023-04-10 00:00:00 |     38 |       -6.64 |        -9.4  |
| MJY     |     -1 | 2020-02-25 00:00:00 | 2020-03-02 00:00:00 |      5 |       -3.47 |        -8.96 |

**Quem trouxe o retorno (soma por ativo, pp)**

| ativo   |    sum |   count |
|:--------|-------:|--------:|
| MJY     |  59.85 |      68 |
| MNQ     |  50.18 |      20 |
| 1OZ     |  44.03 |      55 |
| MES     |  36.61 |      20 |
| 10Y     |  34.08 |      53 |
| MGC     |  16.29 |       4 |
| MHG     |  10.93 |      20 |
| MCL     |   7.91 |      18 |
| M2K     | -10.34 |      39 |
| M6E     | -17.42 |      48 |

### VXM vendido (prêmio do futuro de VIX)  (`cme_vxm`)

**Tese:** Vende o mini futuro de VIX quando a curva está em contango e o VVIX calmo; stop de 5 dias; tamanho pela perda numa crise

**Instrumentos:** [('IBKR/Cboe CFE', 'VXM', 'US$ 100 x VIX', 'US$ 5,5/lado (comissão + ~1 tick)'), ('Tesouro Direto', 'Tesouro Selic', 'R$ ~150', '0')]

**Aplicável:** True — opera com R$ 20 mil: 1 VXM ≈ US$ 1.700-2.000 de nocional, margem ~US$ 800 (≈ R$ 4 mil); 1 contrato = R$ 550 por ponto de VIX -> 1-2 contratos com R$ 20 mil, 2-5 com R$ 50 mil. VXM tem pouca liquidez (spread de 1-2 ticks = US$ 5-10)

| métrica | valor |
|---|---|
| OOS desde | 2021-01 |
| retorno OOS a.a. (R$ 20 mil) | 31.2% vs CDI 11.4% |
| ativo OOS pp (R$ 20 mil / R$ 50 mil) | +19.78 / +21.68 |
| depois do IR (classe exterior) pp, 20k / 50k | +13.86 / +15.80 |
| IR OOS / Sharpe | +0.59 / +0.59 |
| pior queda | -57.2% |
| PBO / Sharpe deflacionado | 15% / +52% |
| leque de parâmetros p5 / mediana / p95 | +16.03 / +19.78 / +20.04 |
| custo 2x / execução t+2 | +14.00 / +19.78 |
| walk-forward | +19.78 |
| sem os 10 melhores negócios | -15.25 |
| placebo p | 0.06 |
| look-ahead (truncamento) | passou |

**10 melhores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| VXM     |     -1 | 2025-04-09 00:00:00 | 2025-05-13 00:00:00 |     24 |       56.22 |        50.35 |
| VXM     |     -1 | 2021-03-10 00:00:00 | 2021-04-13 00:00:00 |     24 |       48.46 |        25.82 |
| VXM     |     -1 | 2020-09-09 00:00:00 | 2020-10-13 00:00:00 |     25 |       29.06 |        22.27 |
| VXM     |     -1 | 2022-03-08 00:00:00 | 2022-04-12 00:00:00 |     26 |       26.22 |        21.28 |
| VXM     |     -1 | 2015-09-09 00:00:00 | 2015-10-13 00:00:00 |     25 |       16.01 |        20.5  |
| VXM     |     -1 | 2020-04-08 00:00:00 | 2020-05-12 00:00:00 |     24 |        4.86 |        19.21 |
| VXM     |     -1 | 2013-10-09 00:00:00 | 2013-11-12 00:00:00 |     25 |       39.29 |        19.08 |
| VXM     |     -1 | 2014-10-15 00:00:00 | 2014-11-11 00:00:00 |     20 |       29.03 |        18.3  |
| VXM     |     -1 | 2020-07-15 00:00:00 | 2020-08-11 00:00:00 |     20 |       25.14 |        17.64 |
| VXM     |     -1 | 2012-01-11 00:00:00 | 2012-02-07 00:00:00 |     19 |       25.95 |        17.59 |

**10 piores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| VXM     |     -1 | 2020-02-12 00:00:00 | 2020-03-10 00:00:00 |     19 |      -67.98 |       -58.26 |
| VXM     |     -1 | 2025-03-11 00:00:00 | 2025-04-08 00:00:00 |     21 |      -52.9  |       -46.87 |
| VXM     |     -1 | 2018-01-10 00:00:00 | 2018-02-06 00:00:00 |     19 |     -111.56 |       -39.43 |
| VXM     |     -1 | 2015-08-12 00:00:00 | 2015-09-08 00:00:00 |     19 |      -47.26 |       -32.19 |
| VXM     |     -1 | 2022-02-09 00:00:00 | 2022-03-07 00:00:00 |     18 |      -37.58 |       -28.28 |
| VXM     |     -1 | 2020-03-11 00:00:00 | 2020-04-07 00:00:00 |     20 |      -43    |       -23.01 |
| VXM     |     -1 | 2014-09-10 00:00:00 | 2014-10-14 00:00:00 |     25 |      -37.72 |       -22.78 |
| VXM     |     -1 | 2014-12-10 00:00:00 | 2015-01-13 00:00:00 |     23 |      -31.12 |       -22.13 |
| VXM     |     -1 | 2025-02-12 00:00:00 | 2025-03-10 00:00:00 |     18 |      -34.69 |       -21.98 |
| VXM     |     -1 | 2016-01-13 00:00:00 | 2016-02-09 00:00:00 |     19 |      -25.5  |       -21.5  |

**Quem trouxe o retorno (soma por ativo, pp)**

| ativo   |    sum |   count |
|:--------|-------:|--------:|
| VXM     | 482.79 |     179 |
