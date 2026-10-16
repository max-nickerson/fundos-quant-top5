# Frente pf3_internacional — resultados da bateria final (gerado automaticamente)

Gerado por `pf/gerar_cadernos.py` a partir de `pf/resultados/bateria/`. IR de pessoa física por `pf/ir.py` (mensal na B3 com isenção de ações ≤ R$ 20 mil/mês, anual no exterior). Ordem: nota do ranking.

### Argentina no pânico v2: cesta de ADRs (conta em dólar v2)  (`em_argentina_v2`)

**Tese:** Compro a cesta de ADRs argentinos quando ela cai > 20% em 21 pregões (estrangeiro vendendo à força); a escolha pelo CCL implícito (ADR barato contra a ação em pesos) perdeu no IS; saio em 63 pregões; sleeve permanente na IBKR em T-bill, câmbio hedgeado com WDO

**Instrumentos:** IBKR: ADRs YPF, GGAL, BMA, PAM, CEPU (compra fracionária, US$ 0,0035/ação mín. US$ 0,35). Na B3 não há BDR desses ADRs (ver COTAHIST). Ações locais (.BA) só como DADO para o CCL implícito (PF brasileiro não opera BYMA). Caixa parado em SGOV/BIL; B3: WDO vendido como hedge do sleeve.

**Aplicável:** True — Operável em conta cash: 50% do sleeve na cesta (R$ 2,5–18,75 mil). Sem remessa por negócio.

| métrica | valor |
|---|---|
| OOS desde | 2021-01 |
| retorno OOS a.a. (R$ 20 mil) | 12.4% vs CDI 11.4% |
| ativo OOS pp (R$ 20 mil / R$ 50 mil) | +0.95 / -1.74 |
| depois do IR (classe exterior) pp, 20k / 50k | +0.73 / -1.91 |
| IR OOS / Sharpe | +0.14 / +0.14 |
| pior queda | -13.1% |
| PBO / Sharpe deflacionado | 7% / +5% |
| leque de parâmetros p5 / mediana / p95 | -2.12 / +0.16 / +5.75 |
| custo 2x / execução t+2 | +0.78 / +1.66 |
| walk-forward | +0.95 |
| sem os 10 melhores negócios | -2.36 |
| placebo p | 0.36 |
| look-ahead (truncamento) | passou |

**10 melhores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| PAM     |      1 | 2014-12-16 00:00:00 | 2015-03-13 00:00:00 |     63 |       76.83 |         5.09 |
| PAM     |      1 | 2014-01-24 00:00:00 | 2014-04-23 00:00:00 |     63 |       70.6  |         4.19 |
| GGAL    |      1 | 2009-03-03 00:00:00 | 2009-05-29 00:00:00 |     63 |       56.97 |         4.19 |
| GGAL    |      1 | 2014-12-16 00:00:00 | 2015-03-13 00:00:00 |     63 |       63.07 |         4.16 |
| GGAL    |      1 | 2014-01-24 00:00:00 | 2014-04-23 00:00:00 |     63 |       69.33 |         4.06 |
| CEPU    |      1 | 2023-09-27 00:00:00 | 2023-12-26 00:00:00 |     64 |       75.64 |         3.78 |
| BMA     |      1 | 2014-01-24 00:00:00 | 2014-04-23 00:00:00 |     63 |       60.65 |         3.48 |
| GGAL    |      1 | 2015-10-02 00:00:00 | 2015-12-30 00:00:00 |     63 |       53.04 |         3.29 |
| BMA     |      1 | 2014-12-16 00:00:00 | 2015-03-13 00:00:00 |     63 |       49.28 |         3.27 |
| BMA     |      1 | 2015-10-02 00:00:00 | 2015-12-30 00:00:00 |     63 |       53.22 |         3.27 |

**10 piores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| GGAL    |      1 | 2008-10-13 00:00:00 | 2009-01-08 00:00:00 |     63 |      -39.04 |        -3.42 |
| PAM     |      1 | 2012-04-17 00:00:00 | 2012-07-13 00:00:00 |     63 |      -45.73 |        -3.05 |
| GGAL    |      1 | 2011-08-09 00:00:00 | 2011-11-04 00:00:00 |     63 |      -33.82 |        -2.41 |
| BMA     |      1 | 2011-08-09 00:00:00 | 2011-11-04 00:00:00 |     63 |      -33.85 |        -2.38 |
| BMA     |      1 | 2019-08-13 00:00:00 | 2019-11-08 00:00:00 |     63 |      -36.7  |        -1.96 |
| GGAL    |      1 | 2019-08-13 00:00:00 | 2019-11-08 00:00:00 |     63 |      -27.97 |        -1.5  |
| GGAL    |      1 | 2018-05-09 00:00:00 | 2018-08-06 00:00:00 |     63 |      -25.82 |        -1.44 |
| PAM     |      1 | 2018-05-09 00:00:00 | 2018-08-06 00:00:00 |     63 |      -21.75 |        -1.26 |
| BMA     |      1 | 2008-10-13 00:00:00 | 2009-01-08 00:00:00 |     63 |      -16.39 |        -1.26 |
| BMA     |      1 | 2012-04-17 00:00:00 | 2012-07-13 00:00:00 |     63 |      -19.48 |        -1.23 |

**Quem trouxe o retorno (soma por ativo, pp)**

| ativo   |   sum |   count |
|:--------|------:|--------:|
| PAM     | 16.31 |      18 |
| YPF     | 14.41 |      22 |
| BMA     | 14.41 |      21 |
| GGAL    | 14.26 |      22 |
| CEPU    |  9.76 |      12 |

### Carry G10 micro FX — conta em dólar v2 (só a margem fora, SGOV, hedge WDO)  (`carry_g10_v2`)

**Tese:** Comprado no micro da moeda de maior juro e vendido no de menor, 1 contrato por perna, fora quando o risco global vira; a margem mora na IBKR em SGOV e o saldo é hedgeado com WDO

**Instrumentos:** [('IBKR/CME', 'M6E', '€ 12.500', 'US$ 0,40 + 2 ticks/lado'), ('IBKR/CME', 'M6B', '£ 6.250', 'idem'), ('IBKR/CME', 'M6A', 'A$ 10.000', 'idem'), ('IBKR/CME', 'MCD', 'C$ 10.000', 'idem'), ('IBKR/CME', 'MSF', 'CHF 12.500', 'idem'), ('IBKR/CME', 'MJY', '¥ 1.250.000', 'idem'), ('Tesouro Direto', 'Tesouro Selic', 'R$ ~150', '0'), ('B3', 'WDO (hedge do saldo)', 'US$ 10 mil', 'R$ 6/mês por contrato')]

**Aplicável:** True — opera com R$ 20 mil (margem de 2 micros FX ≈ US$ 500-900), mas cada perna tem nocional de 2-4x o capital: 1 par já dá vol de ~15-30% do patrimônio. Micro FX tem pouca liquidez (spread 1-2 ticks); MJY é o micro de iene (¥ 1,25 mi), MSF franco.

| métrica | valor |
|---|---|
| OOS desde | 2021-01 |
| retorno OOS a.a. (R$ 20 mil) | 12.5% vs CDI 11.4% |
| ativo OOS pp (R$ 20 mil / R$ 50 mil) | +1.05 / -4.64 |
| depois do IR (classe exterior) pp, 20k / 50k | +0.17 / -4.55 |
| IR OOS / Sharpe | +0.15 / +0.15 |
| pior queda | -34.1% |
| PBO / Sharpe deflacionado | 83% / +30% |
| leque de parâmetros p5 / mediana / p95 | -0.29 / +1.05 / +2.04 |
| custo 2x / execução t+2 | -1.44 / +0.11 |
| walk-forward | +0.94 |
| sem os 10 melhores negócios | -21.92 |
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

### Micro Euro STOXX 50 no pânico — conta em dólar v2 (só a margem fora, SGOV, hedge WDO)  (`eurex_panico_v2`)

**Tese:** Compra 1 micro Euro STOXX 50 depois de queda forte com o V2X no topo (bancos vendidos em gama e vol-alvo vendendo), segura H dias; a margem mora na IBKR em SGOV e o saldo é hedgeado com WDO

**Instrumentos:** [('IBKR/Eurex', 'FSXE', 'EUR 1 x SX5E (≈ R$ 38 mil)', 'EUR 1,10/lado'), ('IBKR/Eurex', 'FDXS', 'EUR 1 x DAX (≈ R$ 160 mil)', 'EUR 1,60/lado'), ('Tesouro Direto', 'Tesouro Selic', 'caixa', '0'), ('B3', 'WDO (hedge do saldo)', 'US$ 10 mil', 'R$ 6/mês por contrato')]

**Aplicável:** True — FSXE cabe (1 contrato ≈ 1,9x R$ 20 mil, 0,8x R$ 50 mil, margem ~R$ 3 mil na IBKR); FDXS não cabe (8x R$ 20 mil) e nunca opera. Micros da Eurex só existem desde mar/2021: antes disso o resultado é hipotético.

| métrica | valor |
|---|---|
| OOS desde | 2021-01 |
| retorno OOS a.a. (R$ 20 mil) | 10.7% vs CDI 11.4% |
| ativo OOS pp (R$ 20 mil / R$ 50 mil) | -0.73 / -4.91 |
| depois do IR (classe exterior) pp, 20k / 50k | -0.65 / -4.67 |
| IR OOS / Sharpe | -0.01 / -0.01 |
| pior queda | -14.4% |
| PBO / Sharpe deflacionado | 20% / +13% |
| leque de parâmetros p5 / mediana / p95 | -2.86 / -0.66 / +3.90 |
| custo 2x / execução t+2 | -0.87 / +0.48 |
| walk-forward | -0.00 |
| sem os 10 melhores negócios | -4.52 |
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

### Reconstituição do Russell 2000 v2: saídas para micro cap (conta em dólar v2)  (`fg_russell_v2`)

**Tese:** Compro no leilão de fechamento da reconstituição (última sexta de junho) as ações que saem do Russell 2000 para baixo — vendidas por todos os indexados — e seguro algumas semanas com IWM vendido; R$ 1 mil por nome. Sleeve permanente na IBKR em T-bill, câmbio hedgeado com WDO.

**Instrumentos:** {'saídas/entradas do Russell 2000': {'onde': 'IBKR', 'ticker': 'até 20 por ano', 'lote': 'fração', 'custo': 'US$ 0,0035/ação mín. 0,35 + 0,4%'}, 'IWM': {'onde': 'IBKR (vendido)', 'ticker': 'IWM', 'lote': 'ações inteiras', 'custo': 'aluguel 0,3% a.a.'}}

**Aplicável:** True — Operável (MOC na IBKR). 5% do sleeve por nome = R$ 250–1.875: com sleeve de R$ 5 mil a comissão mínima (US$ 0,35) pesa ~0,8% por lado. IWM vendido só com sleeve >= R$ 11 mil (conta margem). 7 reconstituições.

| métrica | valor |
|---|---|
| OOS desde | 2023-01 |
| retorno OOS a.a. (R$ 20 mil) | 11.8% vs CDI 13.1% |
| ativo OOS pp (R$ 20 mil / R$ 50 mil) | -1.31 / -3.46 |
| depois do IR (classe exterior) pp, 20k / 50k | -0.96 / -3.12 |
| IR OOS / Sharpe | -0.03 / -0.03 |
| pior queda | -17.2% |
| PBO / Sharpe deflacionado | 1% / +1% |
| leque de parâmetros p5 / mediana / p95 | -6.19 / -2.51 / +0.66 |
| custo 2x / execução t+2 | -2.24 / -2.11 |
| walk-forward | -1.10 |
| sem os 10 melhores negócios | -7.43 |
| placebo p | 0.11 |
| look-ahead (truncamento) | passou |

**10 melhores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| VTGN    |      1 | 2023-06-30 00:00:00 | 2023-09-26 00:00:00 |     60 |      186.63 |         4.8  |
| RCEL    |      1 | 2026-06-26 00:00:00 | 2026-09-22 00:00:00 |     60 |      189.42 |         4.7  |
| STIM    |      1 | 2026-06-26 00:00:00 | 2026-09-22 00:00:00 |     60 |      117.16 |         2.99 |
| GALT    |      1 | 2025-06-27 00:00:00 | 2025-09-23 00:00:00 |     60 |      106.44 |         2.6  |
| LUNG    |      1 | 2026-06-26 00:00:00 | 2026-09-22 00:00:00 |     60 |       64.8  |         1.55 |
| PEPG    |      1 | 2025-06-27 00:00:00 | 2025-09-23 00:00:00 |     60 |       69.57 |         1.48 |
| TUSK    |      1 | 2020-06-26 00:00:00 | 2020-09-22 00:00:00 |     60 |       62.4  |         1.44 |
| MYO     |      1 | 2026-06-26 00:00:00 | 2026-09-22 00:00:00 |     60 |       59.22 |         1.35 |
| EXFY    |      1 | 2026-06-26 00:00:00 | 2026-09-22 00:00:00 |     60 |       45.06 |         1.24 |
| INMB    |      1 | 2026-06-26 00:00:00 | 2026-09-22 00:00:00 |     60 |       52.11 |         1.19 |

**10 piores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| ORBS    |      1 | 2023-06-30 00:00:00 | 2023-09-26 00:00:00 |     60 |      -56.81 |        -1.45 |
| TZOO    |      1 | 2026-06-26 00:00:00 | 2026-09-22 00:00:00 |     60 |      -49.19 |        -1.28 |
| BKKT    |      1 | 2024-06-28 00:00:00 | 2024-09-24 00:00:00 |     60 |      -50.58 |        -1.21 |
| RENT    |      1 | 2024-06-28 00:00:00 | 2024-09-24 00:00:00 |     60 |      -45.19 |        -1.12 |
| CIRC    |      1 | 2026-06-26 00:00:00 | 2026-09-22 00:00:00 |     60 |      -53.41 |        -1.11 |
| ATXI    |      1 | 2021-06-25 00:00:00 | 2021-09-21 00:00:00 |     60 |      -39.69 |        -1.08 |
| AMPY    |      1 | 2020-06-26 00:00:00 | 2020-09-22 00:00:00 |     60 |      -39.85 |        -1.04 |
| EHTH    |      1 | 2026-06-26 00:00:00 | 2026-09-22 00:00:00 |     60 |      -42.11 |        -1.02 |
| TTEC    |      1 | 2026-06-26 00:00:00 | 2026-09-22 00:00:00 |     60 |      -39.02 |        -0.99 |
| COOK    |      1 | 2026-06-26 00:00:00 | 2026-09-22 00:00:00 |     60 |      -37.73 |        -0.97 |

**Quem trouxe o retorno (soma por ativo, pp)**

| ativo   |   sum |   count |
|:--------|------:|--------:|
| VTGN    |  4.8  |       1 |
| RCEL    |  4.7  |       1 |
| STIM    |  2.99 |       1 |
| GALT    |  2.6  |       1 |
| LUNG    |  1.55 |       1 |
| PEPG    |  1.48 |       1 |
| TUSK    |  1.46 |       2 |
| MYO     |  1.35 |       1 |
| EXFY    |  1.24 |       1 |
| INMB    |  1.19 |       1 |

### Spin-offs pequenos dos EUA v2 (conta em dólar v2)  (`fg_spinoff_pequeno_v2`)

**Tese:** Compro a separada PEQUENA (giro < US$ 10 mi/dia) no fim do 1º mês, quando os indexados da controladora já venderam; seguro 6–12 meses com IWM vendido; R$ 1–2,5 mil por nome; sintéticos para quem sumiu do Yahoo. Sleeve permanente na IBKR em T-bill, câmbio hedgeado com WDO.

**Instrumentos:** {'spin-offs': {'onde': 'IBKR', 'ticker': '~5–10 pequenos por ano', 'lote': 'fração', 'custo': 'US$ 0,0035/ação mín. 0,35 + 0,4%'}, 'IWM': {'onde': 'IBKR (vendido)', 'ticker': 'IWM', 'lote': 'ações inteiras', 'custo': 'aluguel 0,3% a.a.'}, 'WDO': {'onde': 'B3', 'ticker': 'WDO (vendido)', 'lote': '1 contrato = US$ 10 mil', 'custo': 'R$ 3,70/lado, rola todo mês'}}

**Aplicável:** True — Operável na IBKR (fração). 5% do sleeve por nome = R$ 250–1.875; IWM vendido só com sleeve >= R$ 11 mil (conta margem). Concentração: SNDK (2025) pesa muito no OOS — ver variante sem_sndk.

| métrica | valor |
|---|---|
| OOS desde | 2021-01 |
| retorno OOS a.a. (R$ 20 mil) | 9.9% vs CDI 11.4% |
| ativo OOS pp (R$ 20 mil / R$ 50 mil) | -1.58 / -6.58 |
| depois do IR (classe exterior) pp, 20k / 50k | -1.48 / -6.22 |
| IR OOS / Sharpe | -0.12 / -0.12 |
| pior queda | -11.2% |
| PBO / Sharpe deflacionado | 0% / +5% |
| leque de parâmetros p5 / mediana / p95 | -4.42 / -1.91 / -0.29 |
| custo 2x / execução t+2 | -1.84 / -1.62 |
| walk-forward | -1.58 |
| sem os 10 melhores negócios | -6.37 |
| placebo p | 0.50 |
| look-ahead (truncamento) | passou |

**10 melhores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| PRTA    |      1 | 2013-02-22 00:00:00 | 2014-02-24 00:00:00 |    252 |      373.67 |        10.96 |
| RHLD    |      1 | 2025-04-23 00:00:00 | 2026-04-24 00:00:00 |    252 |      435.84 |        10.35 |
| CRNC    |      1 | 2019-11-12 00:00:00 | 2020-11-11 00:00:00 |    252 |      316.85 |         9.88 |
| VRTS    |      1 | 2009-03-04 00:00:00 | 2010-03-04 00:00:00 |    252 |      409.65 |         8.57 |
| CLW     |      1 | 2009-02-05 00:00:00 | 2010-02-05 00:00:00 |    252 |      352.67 |         7.68 |
| MPTI    |      1 | 2022-11-30 00:00:00 | 2023-12-01 00:00:00 |    252 |      227.03 |         5.5  |
| XPEL    |      1 | 2019-08-28 00:00:00 | 2020-08-27 00:00:00 |    252 |      151.01 |         5.32 |
| ASIX    |      1 | 2016-11-11 00:00:00 | 2017-11-13 00:00:00 |    252 |      159.31 |         3.96 |
| PNTG    |      1 | 2019-11-27 00:00:00 | 2020-11-27 00:00:00 |    252 |      112.92 |         3.75 |
| VAC     |      1 | 2012-01-09 00:00:00 | 2013-01-10 00:00:00 |    252 |      142.3  |         3.73 |

**10 piores negócios**

| ativo       |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:------------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| ENVA        |      1 | 2015-01-14 00:00:00 | 2016-01-14 00:00:00 |    252 |      -72.26 |        -2.54 |
| FEAM        |      1 | 2022-05-12 00:00:00 | 2023-05-15 00:00:00 |    252 |      -84.36 |        -2.45 |
| KLXE        |      1 | 2018-10-26 00:00:00 | 2019-10-29 00:00:00 |    252 |      -70.79 |        -1.85 |
| MDIA        |      1 | 2020-03-05 00:00:00 | 2021-03-05 00:00:00 |    252 |      -51.61 |        -1.62 |
| FOR         |      1 | 2008-02-13 00:00:00 | 2009-02-12 00:00:00 |    252 |      -65.13 |        -1.61 |
| MDS*200801  |      1 | 2008-03-12 00:00:00 | 2009-03-12 00:00:00 |    252 |      -40.54 |        -1.38 |
| AHC*200710  |      1 | 2008-03-24 00:00:00 | 2009-03-23 00:00:00 |    252 |      -37.18 |        -1.26 |
| ZEP*200707  |      1 | 2007-12-10 00:00:00 | 2008-12-09 00:00:00 |    252 |      -40.39 |        -1.22 |
| IFLG*200706 |      1 | 2007-11-15 00:00:00 | 2008-11-14 00:00:00 |    252 |      -40.03 |        -1.2  |
| MGI*200802  |      1 | 2008-04-14 00:00:00 | 2009-04-14 00:00:00 |    252 |      -32.77 |        -1.13 |

**Quem trouxe o retorno (soma por ativo, pp)**

| ativo   |   sum |   count |
|:--------|------:|--------:|
| PRTA    | 10.96 |       1 |
| RHLD    | 10.35 |       1 |
| CRNC    |  9.88 |       1 |
| VRTS    |  8.57 |       1 |
| CLW     |  7.68 |       1 |
| MPTI    |  5.5  |       1 |
| XPEL    |  5.32 |       1 |
| ASIX    |  3.96 |       1 |
| PNTG    |  3.75 |       1 |
| VAC     |  3.73 |       1 |

### Pânico de país v2: ETF após crash com âncora divergente (conta em dólar v2)  (`em_panico_pais_v2`)

**Tese:** Compro o ETF de país que caiu >= 15% em 21 pregões SÓ quando a âncora (commodity do país ou EEM) não explica a queda; sleeve permanente na IBKR em T-bill, câmbio hedgeado com WDO

**Instrumentos:** IBKR: ETFs de país TUR, EWZ, ARGT, EZA, EWW, ECH, EPU, INDA, EIDO, VNM, KSA (fração, US$ 0,0035/ação mín. US$ 0,35); caixa parado em SGOV/BIL; B3: WDO vendido (US$ 10 mil, contratos inteiros) como hedge do sleeve.

**Aplicável:** True — Operável em conta cash: 25% do sleeve por país (R$ 1,25–9,4 mil). Sem remessa por negócio (o dinheiro mora lá). O WDO só existe a partir de ~US$ 5 mil de sleeve (round).

| métrica | valor |
|---|---|
| OOS desde | 2021-01 |
| retorno OOS a.a. (R$ 20 mil) | 8.0% vs CDI 11.4% |
| ativo OOS pp (R$ 20 mil / R$ 50 mil) | -3.43 / -6.89 |
| depois do IR (classe exterior) pp, 20k / 50k | -2.89 / -6.32 |
| IR OOS / Sharpe | -0.31 / -0.31 |
| pior queda | -18.8% |
| PBO / Sharpe deflacionado | 6% / +3% |
| leque de parâmetros p5 / mediana / p95 | -5.60 / -4.25 / -3.23 |
| custo 2x / execução t+2 | -3.67 / -3.81 |
| walk-forward | -2.65 |
| sem os 10 melhores negócios | -8.34 |
| placebo p | 0.21 |
| look-ahead (truncamento) | passou |

**10 melhores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| TUR     |      1 | 2022-09-30 00:00:00 | 2022-11-29 00:00:00 |     42 |       52.94 |         6.36 |
| EZA     |      1 | 2009-03-02 00:00:00 | 2009-04-29 00:00:00 |     42 |       42.82 |         4.51 |
| EWZ     |      1 | 2007-08-14 00:00:00 | 2007-10-11 00:00:00 |     42 |       37.18 |         4.44 |
| EWZ     |      1 | 2008-03-20 00:00:00 | 2008-05-19 00:00:00 |     42 |       33.77 |         4.17 |
| EZA     |      1 | 2025-04-07 00:00:00 | 2025-06-05 00:00:00 |     42 |       32.52 |         4.01 |
| EZA     |      1 | 2007-08-15 00:00:00 | 2007-10-12 00:00:00 |     42 |       30.57 |         3.66 |
| EIDO    |      1 | 2020-09-24 00:00:00 | 2020-11-23 00:00:00 |     42 |       29.4  |         3.61 |
| ARGT    |      1 | 2023-10-03 00:00:00 | 2023-11-30 00:00:00 |     42 |       28.43 |         3.28 |
| ARGT    |      1 | 2025-09-09 00:00:00 | 2025-11-06 00:00:00 |     42 |       26.18 |         3.17 |
| TUR     |      1 | 2008-07-02 00:00:00 | 2008-08-29 00:00:00 |     42 |       25.38 |         3.02 |

**10 piores negócios**

| ativo            |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:-----------------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| RSX* (sintético) |      1 | 2022-02-25 00:00:00 | 2022-03-04 00:00:00 |      5 |      -90    |       -11.25 |
| TUR              |      1 | 2008-09-23 00:00:00 | 2008-11-20 00:00:00 |     42 |      -58.25 |        -9.15 |
| ECH              |      1 | 2008-09-30 00:00:00 | 2008-11-28 00:00:00 |     43 |      -25.77 |        -4.04 |
| EWZ              |      1 | 2008-07-10 00:00:00 | 2008-09-08 00:00:00 |     42 |      -23.25 |        -3.09 |
| ARGT             |      1 | 2012-04-19 00:00:00 | 2012-06-18 00:00:00 |     42 |      -16.9  |        -2.28 |
| EWZ              |      1 | 2011-08-05 00:00:00 | 2011-10-04 00:00:00 |     42 |      -18.88 |        -2.09 |
| ECH              |      1 | 2011-08-05 00:00:00 | 2011-10-04 00:00:00 |     42 |      -20.22 |        -1.99 |
| EPU              |      1 | 2022-04-26 00:00:00 | 2022-06-23 00:00:00 |     42 |      -13.76 |        -1.86 |
| TUR              |      1 | 2009-01-13 00:00:00 | 2009-03-12 00:00:00 |     42 |      -14.34 |        -1.86 |
| EWZ              |      1 | 2022-04-27 00:00:00 | 2022-06-24 00:00:00 |     42 |      -13.74 |        -1.81 |

**Quem trouxe o retorno (soma por ativo, pp)**

| ativo   |   sum |   count |
|:--------|------:|--------:|
| EZA     | 17.06 |      12 |
| EIDO    | 10.26 |      12 |
| ARGT    |  9.03 |      11 |
| EWW     |  4.98 |       7 |
| TUR     |  3.81 |      26 |
| VNM     |  3.69 |      14 |
| EWZ     |  3.67 |      14 |
| EPU     |  3.6  |      11 |
| INDA    |  0.93 |       2 |
| KSA     |  0.65 |       2 |

### Prêmio de vol beta neutro (SVXY + SH) — conta em dólar v2 (SGOV, hedge WDO)  (`variancia_v2`)

**Tese:** Vende vol do S&P comprando SVXY (−0,5x futuro de VIX de 30 dias) com hedge de beta em SH, vol-alvo 8% e fora no risco global; o dinheiro mora na IBKR em SGOV, hedgeado com WDO

**Instrumentos:** IBKR (conta cash ou margem; ações fracionárias): COMPRAR SVXY (ProShares −0,5x futuros de VIX; ~US$ 64) com ~10-25% do capital e SH (−1x S&P; ~US$ 32) no valor beta x SVXY; caixa lá fora em SGOV. Remeter só ~30% do capital; o resto em Tesouro Selic. Rebalancear só se a posição se afastar >50% do alvo; comissão IBKR Pro tiered. Alternativas testadas: VXM (Cboe, US$ 100 x VIX, margem ~US$ 750-860 por contrato -> 1 contrato ≈ 45% de R$ 20 mil, grande demais), opções XSP (1 iron butterfly ≈ US$ 1,8 mil de risco; 1 iron condor ≈ US$ 6 mil; 1 put ATM ≈ US$ 13 mil de margem). Hedge cambial: WDO (B3) vendido sobre o saldo da IBKR; caixa lá fora em SGOV.

**Aplicável:** True — SVXY e SH com frações na IBKR cabem em qualquer sleeve; VXM/opções XSP não (ver variancia_varejo/rev_variancia).

| métrica | valor |
|---|---|
| OOS desde | 2021-01 |
| retorno OOS a.a. (R$ 20 mil) | 6.9% vs CDI 11.4% |
| ativo OOS pp (R$ 20 mil / R$ 50 mil) | -4.50 / -7.99 |
| depois do IR (classe exterior) pp, 20k / 50k | -3.93 / -7.37 |
| IR OOS / Sharpe | -0.57 / -0.57 |
| pior queda | -10.3% |
| PBO / Sharpe deflacionado | 52% / +7% |
| leque de parâmetros p5 / mediana / p95 | -4.45 / -4.06 / -3.57 |
| custo 2x / execução t+2 | -4.92 / -3.81 |
| walk-forward | -4.84 |
| sem os 10 melhores negócios | -8.19 |
| placebo p | 0.20 |
| look-ahead (truncamento) | passou |

**10 melhores negócios**

| ativo     |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:----------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| hedge S&P |      1 | 2018-10-01 00:00:00 | 2018-10-31 00:00:00 |     21 |         nan |         3.67 |
| svxy      |     -1 | 2012-03-01 00:00:00 | 2012-03-31 00:00:00 |     21 |         nan |         3.18 |
| svxy      |     -1 | 2011-04-01 00:00:00 | 2011-04-30 00:00:00 |     21 |         nan |         2.78 |
| svxy      |     -1 | 2013-07-01 00:00:00 | 2013-07-31 00:00:00 |     21 |         nan |         2.75 |
| svxy      |     -1 | 2007-09-01 00:00:00 | 2007-09-30 00:00:00 |     21 |         nan |         2.71 |
| svxy      |     -1 | 2023-11-01 00:00:00 | 2023-11-30 00:00:00 |     21 |         nan |         2.63 |
| hedge S&P |      1 | 2022-01-01 00:00:00 | 2022-01-31 00:00:00 |     21 |         nan |         2.54 |
| svxy      |     -1 | 2017-01-01 00:00:00 | 2017-01-31 00:00:00 |     21 |         nan |         2.48 |
| svxy      |     -1 | 2010-12-01 00:00:00 | 2010-12-31 00:00:00 |     21 |         nan |         2.45 |
| svxy      |     -1 | 2020-11-01 00:00:00 | 2020-11-30 00:00:00 |     21 |         nan |         2.39 |

**10 piores negócios**

| ativo     |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:----------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| svxy      |     -1 | 2018-02-01 00:00:00 | 2018-02-28 00:00:00 |     21 |         nan |        -5.57 |
| svxy      |     -1 | 2010-05-01 00:00:00 | 2010-05-31 00:00:00 |     21 |         nan |        -3.79 |
| svxy      |     -1 | 2007-11-01 00:00:00 | 2007-11-30 00:00:00 |     21 |         nan |        -3.23 |
| svxy      |     -1 | 2018-10-01 00:00:00 | 2018-10-31 00:00:00 |     21 |         nan |        -3.02 |
| svxy      |     -1 | 2012-05-01 00:00:00 | 2012-05-31 00:00:00 |     21 |         nan |        -2.48 |
| svxy      |     -1 | 2019-05-01 00:00:00 | 2019-05-31 00:00:00 |     21 |         nan |        -2.42 |
| svxy      |     -1 | 2022-02-01 00:00:00 | 2022-02-28 00:00:00 |     21 |         nan |        -2.41 |
| hedge S&P |      1 | 2021-10-01 00:00:00 | 2021-10-31 00:00:00 |     21 |         nan |        -2.26 |
| svxy      |     -1 | 2017-08-01 00:00:00 | 2017-08-31 00:00:00 |     21 |         nan |        -2.05 |
| svxy      |     -1 | 2016-06-01 00:00:00 | 2016-06-30 00:00:00 |     21 |         nan |        -2    |

**Quem trouxe o retorno (soma por ativo, pp)**

| ativo     |    sum |   count |
|:----------|-------:|--------:|
| svxy      |  44.18 |     224 |
| hedge S&P | -25.93 |     224 |

### Mineradoras vs metal — conta em dólar v2 (ETFs/ações na IBKR, venda em ações inteiras, SGOV, hedge WDO)  (`mineradoras_v2`)

**Tese:** Mineradora é opção alavancada no metal: compro a mineradora que ficou para trás do metal e vendo o metal (ETF) e vice-versa; o dinheiro mora na IBKR em SGOV, hedgeado com WDO.

**Instrumentos:** IBKR (EUA): GDX, GDXJ, SIL, COPX, FCX, VALE, BHP, RIO (ETF/ação; compra fracionária, venda em ações inteiras, Reg T, US$ 0,0035/ação mín. US$ 0,35; aluguel 0,25–0,63% a.a.); perna do metal: 1OZ (1 oz ouro, ~US$ 4,2 mil, margem ~12%, ~US$ 0,80/lado), MGC (10 oz, ~US$ 42 mil), micro prata (1.000 oz, ~US$ 56 mil), MHG (2.500 lb, ~US$ 16,5 mil) em contratos inteiros — se não couber, GLD/SLV/CPER em ações. Caixa: Tesouro Selic/CDB no Brasil; na IBKR só margem + Reg T. Hedge cambial: WDO (B3, US$ 10 mil, inteiro) vendido sobre o saldo da IBKR.

**Aplicável:** True — Operável na IBKR com ações inteiras na ponta vendida; com sleeve < ~R$ 11 mil (US$ 2 mil) não há venda a descoberto (Reg T) e metade dos negócios não abre.

| métrica | valor |
|---|---|
| OOS desde | 2021-01 |
| retorno OOS a.a. (R$ 20 mil) | 7.1% vs CDI 11.4% |
| ativo OOS pp (R$ 20 mil / R$ 50 mil) | -4.34 / -8.18 |
| depois do IR (classe exterior) pp, 20k / 50k | -3.74 / -7.67 |
| IR OOS / Sharpe | -0.57 / -0.57 |
| pior queda | -8.9% |
| PBO / Sharpe deflacionado | 72% / +3% |
| leque de parâmetros p5 / mediana / p95 | -4.65 / -4.12 / -3.92 |
| custo 2x / execução t+2 | -4.45 / -4.36 |
| walk-forward | -4.36 |
| sem os 10 melhores negócios | -4.54 |
| placebo p | 0.00 |
| look-ahead (truncamento) | passou |

**10 melhores negócios**

| ativo          |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:---------------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| VALE x BHP/RIO |     -1 | 2011-07-04 00:00:00 | 2011-08-08 00:00:00 |     25 |       16.04 |         4.03 |
| VALE x BHP/RIO |      1 | 2012-01-02 00:00:00 | 2012-02-06 00:00:00 |     25 |       16.13 |         3.1  |
| VALE x BHP/RIO |      1 | 2009-03-16 00:00:00 | 2009-05-18 00:00:00 |     42 |       29.09 |         2.91 |
| VALE x BHP/RIO |      1 | 2010-09-13 00:00:00 | 2010-10-04 00:00:00 |     15 |        9.19 |         2.14 |
| VALE x BHP/RIO |     -1 | 2020-01-13 00:00:00 | 2020-02-17 00:00:00 |     25 |        8.82 |         2.06 |
| COPX x CPER    |     -1 | 2015-04-27 00:00:00 | 2015-06-29 00:00:00 |     43 |       13.97 |         1.91 |
| VALE x BHP/RIO |     -1 | 2019-06-24 00:00:00 | 2019-08-12 00:00:00 |     35 |       11.93 |         1.76 |
| VALE x BHP/RIO |      1 | 2017-10-09 00:00:00 | 2017-11-27 00:00:00 |     32 |        9.6  |         1.71 |
| VALE x BHP/RIO |      1 | 2009-07-13 00:00:00 | 2009-08-10 00:00:00 |     20 |       14.42 |         1.7  |
| FCX x CPER     |      1 | 2015-12-21 00:00:00 | 2016-02-22 00:00:00 |     41 |       27.86 |         1.7  |

**10 piores negócios**

| ativo          |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:---------------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| SIL x SLV      |     -1 | 2016-02-22 00:00:00 | 2016-08-11 00:00:00 |    120 |      -75.4  |        -9.1  |
| GDXJ x GDX     |     -1 | 2016-03-07 00:00:00 | 2016-08-25 00:00:00 |    120 |      -25.09 |        -7.35 |
| GDXJ x GDX     |     -1 | 2010-08-02 00:00:00 | 2011-01-21 00:00:00 |    120 |      -26.11 |        -6.16 |
| VALE x BHP/RIO |      1 | 2008-09-08 00:00:00 | 2008-12-01 00:00:00 |     60 |      -42.48 |        -6.12 |
| VALE x BHP/RIO |      1 | 2014-08-11 00:00:00 | 2015-01-12 00:00:00 |    108 |      -19.95 |        -5.7  |
| VALE x BHP/RIO |     -1 | 2009-09-21 00:00:00 | 2010-01-18 00:00:00 |     81 |      -28    |        -4.26 |
| VALE x BHP/RIO |     -1 | 2016-10-31 00:00:00 | 2017-04-10 00:00:00 |    111 |      -27.97 |        -3.67 |
| SIL x SLV      |      1 | 2011-01-21 00:00:00 | 2011-07-04 00:00:00 |    111 |      -18.73 |        -3.49 |
| COPX x CPER    |      1 | 2014-09-08 00:00:00 | 2015-01-05 00:00:00 |     83 |      -17.17 |        -3.47 |
| GDXJ x GDX     |      1 | 2011-07-25 00:00:00 | 2012-01-02 00:00:00 |    111 |      -13.38 |        -3.45 |

**Quem trouxe o retorno (soma por ativo, pp)**

| ativo          |    sum |   count |
|:---------------|-------:|--------:|
| FCX x CPER     |   8.19 |      27 |
| COPX x CPER    |   6.53 |      28 |
| VALE x BHP/RIO |   5.62 |      48 |
| GDX x GLD      |  -0.85 |      23 |
| SIL x SLV      |  -1.63 |      26 |
| GDXJ x GDX     | -14.25 |      10 |

### Crédito EM high yield (ETF) no pânico de crédito com âncora — conta em dólar v2  (`credito_em_v2`)

**Tese:** Compra HYEM quando a queda de crédito (ETF − beta x Treasury) passa de k desvios E o spread do ETF está no topo do ano; segura H dias; o dinheiro mora na IBKR em SGOV, hedgeado com WDO

**Instrumentos:** IBKR: HYEM (VanEck EM High Yield Bond, ~US$ 20), EMHY (iShares EM HY), CEMB (iShares EM corporativo) com frações; IEF vendido em ações inteiras (opcional); caixa em SGOV. B3: WDO vendido sobre o saldo (hedge cambial).

**Aplicável:** True — ETF com frações cabe em qualquer sleeve; venda de IEF (dur=True) só com patrimônio >= US$ 2 mil (sleeve >= ~R$ 11 mil). Os eurobonds do institucional (lote US$ 200 mil) continuam fora do alcance.

| métrica | valor |
|---|---|
| OOS desde | 2021-01 |
| retorno OOS a.a. (R$ 20 mil) | 6.9% vs CDI 11.4% |
| ativo OOS pp (R$ 20 mil / R$ 50 mil) | -4.51 / -8.54 |
| depois do IR (classe exterior) pp, 20k / 50k | -3.80 / -7.79 |
| IR OOS / Sharpe | -0.59 / -0.59 |
| pior queda | -7.8% |
| PBO / Sharpe deflacionado | 80% / +2% |
| leque de parâmetros p5 / mediana / p95 | -5.03 / -4.35 / -3.69 |
| custo 2x / execução t+2 | -4.56 / -4.45 |
| walk-forward | -4.51 |
| sem os 10 melhores negócios | -4.61 |
| placebo p | 0.30 |
| look-ahead (truncamento) | passou |

**10 melhores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| HYEM    |      1 | 2025-04-08 00:00:00 | 2025-08-19 00:00:00 |     92 |        6.27 |         3.11 |
| HYEM    |      1 | 2015-08-26 00:00:00 | 2016-05-26 00:00:00 |    190 |        3.17 |         2.95 |
| HYEM    |      1 | 2014-10-17 00:00:00 | 2015-05-20 00:00:00 |    148 |       -0.04 |         2.08 |
| HYEM    |      1 | 2019-08-14 00:00:00 | 2020-01-06 00:00:00 |    100 |        2.84 |         2.06 |
| HYEM    |      1 | 2022-07-18 00:00:00 | 2022-11-11 00:00:00 |     84 |        1.43 |         0.92 |
| HYEM    |      1 | 2013-06-05 00:00:00 | 2013-10-23 00:00:00 |     99 |        0.67 |         0.92 |
| HYEM    |      1 | 2024-08-07 00:00:00 | 2024-12-04 00:00:00 |     84 |        1.6  |         0.68 |
| HYEM    |      1 | 2020-03-02 00:00:00 | 2020-07-29 00:00:00 |    105 |       -2.79 |         0.07 |
| HYEM    |      1 | 2022-03-08 00:00:00 | 2022-07-08 00:00:00 |     85 |       -9.63 |        -4.19 |

**10 piores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| HYEM    |      1 | 2022-03-08 00:00:00 | 2022-07-08 00:00:00 |     85 |       -9.63 |        -4.19 |
| HYEM    |      1 | 2020-03-02 00:00:00 | 2020-07-29 00:00:00 |    105 |       -2.79 |         0.07 |
| HYEM    |      1 | 2024-08-07 00:00:00 | 2024-12-04 00:00:00 |     84 |        1.6  |         0.68 |
| HYEM    |      1 | 2013-06-05 00:00:00 | 2013-10-23 00:00:00 |     99 |        0.67 |         0.92 |
| HYEM    |      1 | 2022-07-18 00:00:00 | 2022-11-11 00:00:00 |     84 |        1.43 |         0.92 |
| HYEM    |      1 | 2019-08-14 00:00:00 | 2020-01-06 00:00:00 |    100 |        2.84 |         2.06 |
| HYEM    |      1 | 2014-10-17 00:00:00 | 2015-05-20 00:00:00 |    148 |       -0.04 |         2.08 |
| HYEM    |      1 | 2015-08-26 00:00:00 | 2016-05-26 00:00:00 |    190 |        3.17 |         2.95 |
| HYEM    |      1 | 2025-04-08 00:00:00 | 2025-08-19 00:00:00 |     92 |        6.27 |         3.11 |

**Quem trouxe o retorno (soma por ativo, pp)**

| ativo   |   sum |   count |
|:--------|------:|--------:|
| HYEM    |  8.61 |       9 |

### Noite após queda forte — ETFs dos EUA v2 (MOC->MOO, conta em dólar v2)  (`lg_eua_etf_v2`)

**Tese:** Compro no leilão de fechamento (MOC) os ETFs/large caps americanos que caíram forte no dia e vendo no leilão de abertura (MOO): vendedores forçados do fechamento (ETFs alavancados, vol-alvo, margin call) pressionam o leilão e a abertura devolve; sleeve permanente na IBKR em T-bill, câmbio hedgeado com WDO

**Instrumentos:** [{'onde': 'IBKR (conta de margem Reg T, só o necessário: ~50% da posição)', 'ticker': 'SPY/QQQ/XL*/... ou S&P 100', 'lote': '1 ação', 'custo': 'US$ 0,0035/ação mín. US$ 0,35 por ordem + 1 bp de derrapagem no leilão; margem T-bill+1,5% por 1 dia'}]

**Aplicável:** True — MOC até 15h50 ET e MOO no dia seguinte (à mão ou API IBKR). Sleeve < R$ 11 mil: conta cash, metade do sleeve por noite. Decide com o preço das 15h50 (o sinal usa o fechamento -> ver t+2).

| métrica | valor |
|---|---|
| OOS desde | 2021-01 |
| retorno OOS a.a. (R$ 20 mil) | 2.0% vs CDI 11.4% |
| ativo OOS pp (R$ 20 mil / R$ 50 mil) | -9.44 / -9.24 |
| depois do IR (classe exterior) pp, 20k / 50k | -8.32 / -8.35 |
| IR OOS / Sharpe | -1.37 / -1.37 |
| pior queda | -16.2% |
| PBO / Sharpe deflacionado | 0% / +0% |
| leque de parâmetros p5 / mediana / p95 | -9.94 / -7.14 / -5.94 |
| custo 2x / execução t+2 | -14.84 / -8.51 |
| walk-forward | -5.24 |
| sem os 10 melhores negócios | -10.19 |
| placebo p | 0.98 |
| look-ahead (truncamento) | passou |

**10 melhores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| XOP     |      1 | 2020-03-09 00:00:00 | 2020-03-10 00:00:00 |      1 |       27.98 |         2.16 |
| KRE     |      1 | 2023-03-13 00:00:00 | 2023-03-14 00:00:00 |      1 |       10.35 |         0.84 |
| XOP     |      1 | 2020-11-06 00:00:00 | 2020-11-09 00:00:00 |      1 |       10.64 |         0.84 |
| OIH     |      1 | 2020-03-12 00:00:00 | 2020-03-13 00:00:00 |      1 |       10.26 |         0.8  |
| XRT     |      1 | 2021-01-28 00:00:00 | 2021-01-29 00:00:00 |      1 |       10.31 |         0.7  |
| OIH     |      1 | 2020-03-09 00:00:00 | 2020-03-10 00:00:00 |      1 |        9.78 |         0.69 |
| XLE     |      1 | 2020-03-12 00:00:00 | 2020-03-13 00:00:00 |      1 |        8.22 |         0.68 |
| XLE     |      1 | 2020-03-09 00:00:00 | 2020-03-10 00:00:00 |      1 |        7.81 |         0.63 |
| XLE     |      1 | 2020-03-23 00:00:00 | 2020-03-24 00:00:00 |      1 |        7.52 |         0.61 |
| XOP     |      1 | 2020-06-11 00:00:00 | 2020-06-12 00:00:00 |      1 |        6.1  |         0.5  |

**10 piores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| XOP     |      1 | 2020-03-06 00:00:00 | 2020-03-09 00:00:00 |      1 |      -24.49 |        -1.76 |
| OIH     |      1 | 2020-03-06 00:00:00 | 2020-03-09 00:00:00 |      1 |      -24.48 |        -1.67 |
| XLE     |      1 | 2020-03-06 00:00:00 | 2020-03-09 00:00:00 |      1 |      -17.71 |        -1.4  |
| KRE     |      1 | 2023-03-10 00:00:00 | 2023-03-13 00:00:00 |      1 |      -12.82 |        -1.01 |
| GDX     |      1 | 2020-03-13 00:00:00 | 2020-03-16 00:00:00 |      1 |      -12.07 |        -0.98 |
| OIH     |      1 | 2020-06-10 00:00:00 | 2020-06-11 00:00:00 |      1 |      -11.07 |        -0.8  |
| GDX     |      1 | 2020-03-11 00:00:00 | 2020-03-12 00:00:00 |      1 |       -8.88 |        -0.73 |
| ITB     |      1 | 2020-03-11 00:00:00 | 2020-03-12 00:00:00 |      1 |       -8.05 |        -0.65 |
| OIH     |      1 | 2020-03-11 00:00:00 | 2020-03-12 00:00:00 |      1 |       -9.87 |        -0.65 |
| XOP     |      1 | 2020-06-10 00:00:00 | 2020-06-11 00:00:00 |      1 |       -8.59 |        -0.65 |

**Quem trouxe o retorno (soma por ativo, pp)**

| ativo   |   sum |   count |
|:--------|------:|--------:|
| XLV     |  0.29 |      21 |
| MDY     |  0.03 |       1 |
| XLC     | -0.09 |      37 |
| QQQ     | -0.13 |      23 |
| DIA     | -0.14 |       2 |
| XLP     | -0.2  |      10 |
| XLY     | -0.21 |      39 |
| IWM     | -0.26 |      13 |
| XLB     | -0.32 |      22 |
| XLK     | -0.32 |      70 |
