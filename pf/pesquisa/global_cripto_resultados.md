# Frente global_cripto — resultados da bateria final (gerado automaticamente)

Gerado por `pf/gerar_cadernos.py` a partir de `pf/resultados/bateria/`. IR de pessoa física por `pf/ir.py` (mensal na B3 com isenção de ações ≤ R$ 20 mil/mês, anual no exterior). Ordem: nota do ranking.

### S&P/HY com hedge para CDI na B3 (dólar só em tendência)  (`gl_hedge_cdi`)

**Tese:** Carrego o prêmio da bolsa e do HY americano por cima do CDI via ETF quanto; dólar aberto (IVVB11) só quando ele sobe

**Instrumentos:** {'SPXR11': {'onde': 'B3', 'ticker': 'SPXR11', 'lote': 1, 'custo': 'meio spread + 0,03%'}, 'IVVB11': {'onde': 'B3', 'ticker': 'IVVB11', 'lote': 1, 'custo': 'meio spread + 0,03%'}, 'HYBR11': {'onde': 'B3', 'ticker': 'HYBR11', 'lote': 1, 'custo': '0,5% (estimado)'}}

**Aplicável:** True — Tudo na B3 em cotas de R$ 10-450; SPXR11 tem R$ ~10 mi/dia. HYBR11 existe mas é pequeno (perna de HY teórica).

| métrica | valor |
|---|---|
| OOS desde | 2021-01 |
| retorno OOS a.a. (R$ 20 mil) | 12.8% vs CDI 11.4% |
| ativo OOS pp (R$ 20 mil / R$ 50 mil) | +1.41 / +1.41 |
| depois do IR (classe etf_b3) pp, 20k / 50k | +0.76 / +0.76 |
| IR OOS / Sharpe | +0.16 / +0.16 |
| pior queda | -23.6% |
| PBO / Sharpe deflacionado | 43% / +22% |
| leque de parâmetros p5 / mediana / p95 | +1.16 / +2.16 / +5.78 |
| custo 2x / execução t+2 | -0.38 / +1.18 |
| walk-forward | -0.73 |
| sem os 10 melhores negócios | -7.33 |
| placebo p | 0.59 |
| look-ahead (truncamento) | passou |

**10 melhores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| IVVB11  |      1 | 2014-10-01 00:00:00 | 2015-09-01 00:00:00 |    231 |       47.4  |        28.61 |
| IVVB11  |      1 | 2024-02-01 00:00:00 | 2025-04-01 00:00:00 |    292 |       34.04 |        18.56 |
| SPXR11  |      1 | 2009-06-01 00:00:00 | 2010-02-01 00:00:00 |    169 |       22.14 |        16.09 |
| IVVB11  |      1 | 2020-06-01 00:00:00 | 2020-12-01 00:00:00 |    127 |       16.85 |        15.59 |
| IVVB11  |      1 | 2018-03-01 00:00:00 | 2018-11-01 00:00:00 |    170 |       17.02 |        13.9  |
| SPXR11  |      1 | 2025-06-02 00:00:00 | 2026-01-02 00:00:00 |    150 |       21.94 |        11.14 |
| IVVB11  |      1 | 2021-02-01 00:00:00 | 2021-05-03 00:00:00 |     61 |       11.79 |        10.89 |
| IVVB11  |      1 | 2012-04-02 00:00:00 | 2013-02-01 00:00:00 |    210 |       17.58 |        10.29 |
| IVVB11  |      1 | 2013-06-03 00:00:00 | 2013-11-01 00:00:00 |    109 |       13.95 |         9.69 |
| SPXR11  |      1 | 2013-02-01 00:00:00 | 2013-06-03 00:00:00 |     81 |       10.93 |         8.13 |

**10 piores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| IVVB11  |      1 | 2018-12-03 00:00:00 | 2019-01-02 00:00:00 |     20 |      -11.37 |       -11.95 |
| SPXR11  |      1 | 2010-05-03 00:00:00 | 2010-06-01 00:00:00 |     21 |      -10.12 |       -11.26 |
| SPXR11  |      1 | 2022-04-01 00:00:00 | 2022-05-02 00:00:00 |     19 |       -7.89 |        -9.14 |
| SPXR11  |      1 | 2026-02-02 00:00:00 | 2026-04-01 00:00:00 |     40 |       -4.66 |        -8.2  |
| SPXR11  |      1 | 2018-02-01 00:00:00 | 2018-03-01 00:00:00 |     18 |       -4.71 |        -5.61 |
| IVVB11  |      1 | 2019-04-01 00:00:00 | 2019-06-03 00:00:00 |     43 |       -3.89 |        -5.27 |
| IVVB11  |      1 | 2023-10-02 00:00:00 | 2023-11-01 00:00:00 |     21 |       -3.07 |        -4.25 |
| IVVB11  |      1 | 2022-12-01 00:00:00 | 2023-01-02 00:00:00 |     22 |       -2.57 |        -3.94 |
| SPXR11  |      1 | 2022-02-01 00:00:00 | 2022-03-02 00:00:00 |     19 |       -2.74 |        -3.93 |
| IVVB11  |      1 | 2017-06-01 00:00:00 | 2017-08-01 00:00:00 |     42 |       -1.69 |        -3.9  |

**Quem trouxe o retorno (soma por ativo, pp)**

| ativo   |   sum |   count |
|:--------|------:|--------:|
| IVVB11  | 73.78 |      25 |
| SPXR11  | 41.06 |      24 |

### Rotação de ETFs globais da B3 (tendência, caixa em CDI)  (`gl_rotacao`)

**Tese:** Compro os ETFs globais da B3 que mais subiram em R$ e bateram o CDI; senão fico no Tesouro Selic

**Instrumentos:** {'IVVB11': {'onde': 'B3 (Clear/Rico/XP/Inter)', 'ticker': 'IVVB11', 'lote': 1, 'custo': 'meio spread + 0,03%'}, 'NASD11': {'onde': 'B3 (Clear/Rico/XP/Inter)', 'ticker': 'NASD11', 'lote': 1, 'custo': 'meio spread + 0,03%'}, 'XINA11': {'onde': 'B3 (Clear/Rico/XP/Inter)', 'ticker': 'XINA11', 'lote': 1, 'custo': 'meio spread + 0,03%'}, 'EURP11': {'onde': 'B3 (Clear/Rico/XP/Inter)', 'ticker': 'EURP11', 'lote': 1, 'custo': 'meio spread + 0,03%'}, 'ACWI11': {'onde': 'B3 (Clear/Rico/XP/Inter)', 'ticker': 'ACWI11', 'lote': 1, 'custo': 'meio spread + 0,03%'}, 'GOLD11': {'onde': 'B3 (Clear/Rico/XP/Inter)', 'ticker': 'GOLD11', 'lote': 1, 'custo': 'meio spread + 0,03%'}, 'BSLV39': {'onde': 'B3 (Clear/Rico/XP/Inter)', 'ticker': 'BSLV39', 'lote': 1, 'custo': 'meio spread + 0,03%'}, 'HASH11': {'onde': 'B3 (Clear/Rico/XP/Inter)', 'ticker': 'HASH11', 'lote': 1, 'custo': 'meio spread + 0,03%'}}

**Aplicável:** True — Tudo na B3, cotas inteiras de R$ 10-450; com R$ 20 mil cabem 2-3 ETFs sem distorção relevante.

| métrica | valor |
|---|---|
| OOS desde | 2021-01 |
| retorno OOS a.a. (R$ 20 mil) | 11.5% vs CDI 11.4% |
| ativo OOS pp (R$ 20 mil / R$ 50 mil) | +0.05 / +0.04 |
| depois do IR (classe etf_b3) pp, 20k / 50k | -1.23 / -1.23 |
| IR OOS / Sharpe | +0.12 / +0.12 |
| pior queda | -32.8% |
| PBO / Sharpe deflacionado | 87% / +51% |
| leque de parâmetros p5 / mediana / p95 | -4.57 / -0.80 / +5.42 |
| custo 2x / execução t+2 | -1.90 / -1.76 |
| walk-forward | +3.89 |
| sem os 10 melhores negócios | -12.88 |
| placebo p | 0.29 |
| look-ahead (truncamento) | passou |

**10 melhores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| HASH11  |      1 | 2015-10-01 00:00:00 | 2018-06-01 00:00:00 |    666 |     1903.41 |       114.9  |
| HASH11  |      1 | 2020-10-01 00:00:00 | 2021-07-01 00:00:00 |    186 |      143.83 |        59.77 |
| NASD11  |      1 | 2014-09-01 00:00:00 | 2016-02-01 00:00:00 |    357 |       90.14 |        24.97 |
| BSLV39  |      1 | 2025-07-01 00:00:00 | 2026-07-01 00:00:00 |    252 |       56.93 |        20.42 |
| BSLV39  |      1 | 2010-07-01 00:00:00 | 2011-07-01 00:00:00 |    252 |       63.93 |        19.32 |
| GOLD11  |      1 | 2020-04-01 00:00:00 | 2020-09-01 00:00:00 |    105 |       26.96 |        16.52 |
| NASD11  |      1 | 2018-03-01 00:00:00 | 2018-12-03 00:00:00 |    190 |       23.65 |        14.61 |
| IVVB11  |      1 | 2013-04-01 00:00:00 | 2013-12-02 00:00:00 |    172 |       35.76 |        14.14 |
| HASH11  |      1 | 2023-11-01 00:00:00 | 2024-09-02 00:00:00 |    209 |       78.44 |        13.91 |
| XINA11  |      1 | 2017-07-03 00:00:00 | 2018-03-01 00:00:00 |    165 |       25.45 |        13.74 |

**10 piores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| IVVB11  |      1 | 2022-01-03 00:00:00 | 2022-03-02 00:00:00 |     40 |      -17.98 |       -11.38 |
| HASH11  |      1 | 2024-12-02 00:00:00 | 2025-04-01 00:00:00 |     82 |      -24.94 |        -9.72 |
| NASD11  |      1 | 2019-05-02 00:00:00 | 2019-06-03 00:00:00 |     22 |      -11.04 |        -7.08 |
| NASD11  |      1 | 2010-04-01 00:00:00 | 2010-07-01 00:00:00 |     62 |       -9.69 |        -6.98 |
| XINA11  |      1 | 2019-05-02 00:00:00 | 2019-06-03 00:00:00 |     22 |      -13.72 |        -6.21 |
| BSLV39  |      1 | 2023-05-02 00:00:00 | 2023-06-01 00:00:00 |     22 |       -6.95 |        -6.05 |
| BSLV39  |      1 | 2009-02-02 00:00:00 | 2009-07-01 00:00:00 |    101 |       -8.56 |        -5.94 |
| BSLV39  |      1 | 2022-12-01 00:00:00 | 2023-03-01 00:00:00 |     62 |       -7.87 |        -5.93 |
| XINA11  |      1 | 2013-12-02 00:00:00 | 2014-02-03 00:00:00 |     43 |      -10.28 |        -5.49 |
| HASH11  |      1 | 2021-12-01 00:00:00 | 2022-01-03 00:00:00 |     23 |      -20.69 |        -5.42 |

**Quem trouxe o retorno (soma por ativo, pp)**

| ativo   |    sum |   count |
|:--------|-------:|--------:|
| HASH11  | 172.68 |      11 |
| NASD11  |  75.64 |      21 |
| XINA11  |  26.06 |      13 |
| IVVB11  |  15.38 |      12 |
| GOLD11  |  13.72 |      18 |
| BSLV39  |   3.48 |      16 |
| ACWI11  |   0.3  |       3 |
| EURP11  |  -6.92 |       5 |

### BDR x EUA com ordem limitada (formador de mercado de varejo)  (`gl_bdr_limite`)

**Tese:** Ordem de compra parada abaixo do valor justo do BDR (EUA x dólar); vende no justo no dia seguinte; hedge opcional na IBKR

**Instrumentos:** {'BDRs': {'onde': 'B3 (Clear/Rico/XP)', 'ticker': '~115 BDRs líquidos', 'lote': 1, 'custo': '0,03% (limitada) / meio spread'}, 'hedge': {'onde': 'IBKR', 'ticker': 'ação-objeto', 'lote': '1 ação', 'custo': 'US$ 0,0035/ação, mín. 0,35; aluguel 0,5% a.a.'}}

**Aplicável:** True — BDRs de R$ 20-200 em lote 1; ordem limitada é padrão em qualquer corretora. O hedge na IBKR é opcional (exige conta lá).

| métrica | valor |
|---|---|
| OOS desde | 2023-01 |
| retorno OOS a.a. (R$ 20 mil) | 25.6% vs CDI 13.1% |
| ativo OOS pp (R$ 20 mil / R$ 50 mil) | +12.53 / +12.75 |
| depois do IR (classe etf_b3) pp, 20k / 50k | +11.54 / +11.72 |
| IR OOS / Sharpe | +0.77 / +0.77 |
| pior queda | -13.4% |
| PBO / Sharpe deflacionado | 0% / +0% |
| leque de parâmetros p5 / mediana / p95 | +4.43 / +10.35 / +17.94 |
| custo 2x / execução t+2 | +3.75 / +10.52 |
| walk-forward | +13.76 |
| sem os 10 melhores negócios | +6.58 |
| placebo p | 0.13 |
| look-ahead (truncamento) | passou |

**10 melhores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| A1MD34  |      1 | 2025-10-03 00:00:00 | 2025-10-06 00:00:00 |      1 |       34.85 |         3.3  |
| GDXB39  |      1 | 2026-08-19 00:00:00 | 2026-08-20 00:00:00 |      1 |       27.46 |         2.71 |
| C2OI34  |      1 | 2023-07-13 00:00:00 | 2023-07-14 00:00:00 |      1 |       26.48 |         2.62 |
| C2OI34  |      1 | 2023-03-13 00:00:00 | 2023-03-14 00:00:00 |      1 |       25.69 |         2.55 |
| BABA34  |      1 | 2022-03-15 00:00:00 | 2022-03-16 00:00:00 |      1 |       23.54 |         2.34 |
| NUBR33  |      1 | 2022-08-15 00:00:00 | 2022-08-16 00:00:00 |      1 |       23.49 |         2.33 |
| M1RN34  |      1 | 2026-02-13 00:00:00 | 2026-02-18 00:00:00 |      1 |       20.28 |         2.01 |
| P2LT34  |      1 | 2025-04-07 00:00:00 | 2025-04-08 00:00:00 |      1 |       20.17 |         1.89 |
| M2ST34  |      1 | 2024-12-20 00:00:00 | 2024-12-23 00:00:00 |      1 |       18.89 |         1.88 |
| M2ST34  |      1 | 2024-08-05 00:00:00 | 2024-08-06 00:00:00 |      1 |       19.56 |         1.86 |

**10 piores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| NFLX34  |      1 | 2022-04-19 00:00:00 | 2022-04-27 00:00:00 |      5 |      -39.51 |        -3.93 |
| PYPL34  |      1 | 2021-09-17 00:00:00 | 2021-09-24 00:00:00 |      5 |      -37.45 |        -3.73 |
| N1VO34  |      1 | 2025-07-28 00:00:00 | 2025-08-01 00:00:00 |      4 |      -32.9  |        -3.26 |
| STOC31  |      1 | 2022-06-08 00:00:00 | 2022-06-14 00:00:00 |      4 |      -28.74 |        -2.88 |
| S2GM34  |      1 | 2024-02-01 00:00:00 | 2024-02-06 00:00:00 |      3 |      -26.97 |        -2.69 |
| FBOK34  |      1 | 2022-02-02 00:00:00 | 2022-02-09 00:00:00 |      5 |      -26.9  |        -2.64 |
| M1TA34  |      1 | 2022-10-26 00:00:00 | 2022-10-28 00:00:00 |      2 |      -24.6  |        -2.47 |
| AMZO34  |      1 | 2022-10-27 00:00:00 | 2022-11-04 00:00:00 |      5 |      -24.62 |        -2.46 |
| S2GM34  |      1 | 2026-01-15 00:00:00 | 2026-01-19 00:00:00 |      2 |      -23.9  |        -2.4  |
| NFLX34  |      1 | 2022-01-20 00:00:00 | 2022-01-25 00:00:00 |      3 |      -23.62 |        -2.31 |

**Quem trouxe o retorno (soma por ativo, pp)**

| ativo   |   sum |   count |
|:--------|------:|--------:|
| C2OI34  | 20.47 |     258 |
| S2GM34  |  9.44 |     112 |
| AIRB34  |  8.83 |      58 |
| NUBR33  |  8.63 |     151 |
| A1MD34  |  6.99 |     191 |
| M2ST34  |  5.81 |     202 |
| P2LT34  |  5.37 |      69 |
| MUTC34  |  5.37 |      92 |
| STOC31  |  5.08 |     140 |
| STOC34  |  4.6  |      59 |

### Desconto de ETFs de cripto da B3 vs BTC/ETH em R$ (ordem limitada)  (`gl_cripto_premio`)

**Tese:** Ordem de compra parada abaixo do NAV dos ETFs de bitcoin/ether da B3; vende no NAV; hedge com BIT quando o contrato cabe

**Instrumentos:** {'QBTC11': {'onde': 'B3', 'ticker': 'QBTC11', 'lote': 1, 'custo': '0,03% (limitada)'}, 'BITH11': {'onde': 'B3', 'ticker': 'BITH11', 'lote': 1, 'custo': '0,03% (limitada)'}, 'ETHE11': {'onde': 'B3', 'ticker': 'ETHE11', 'lote': 1, 'custo': '0,03% (limitada)'}, 'QETH11': {'onde': 'B3', 'ticker': 'QETH11', 'lote': 1, 'custo': '0,03% (limitada)'}, 'BIT': {'onde': 'B3 (futuro)', 'ticker': 'BIT', 'lote': '0,01 BTC desde 06/2025 (0,1 antes)', 'custo': '~0,05%'}}

**Aplicável:** True — ETFs em cotas de R$ 10-100, ordem limitada em qualquer corretora; o hedge com BIT só cabe desde 06/2025.

| métrica | valor |
|---|---|
| OOS desde | 2023-01 |
| retorno OOS a.a. (R$ 20 mil) | 15.4% vs CDI 13.1% |
| ativo OOS pp (R$ 20 mil / R$ 50 mil) | +2.28 / +2.28 |
| depois do IR (classe etf_b3) pp, 20k / 50k | +2.08 / +2.08 |
| IR OOS / Sharpe | +0.53 / +0.53 |
| pior queda | -3.1% |
| PBO / Sharpe deflacionado | 66% / +31% |
| leque de parâmetros p5 / mediana / p95 | +1.65 / +2.39 / +4.68 |
| custo 2x / execução t+2 | +2.19 / +3.08 |
| walk-forward | +2.28 |
| sem os 10 melhores negócios | -2.40 |
| placebo p | 0.05 |
| look-ahead (truncamento) | passou |

**10 melhores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| QBTC11  |      1 | 2024-02-23 00:00:00 | 2024-02-29 00:00:00 |      4 |       21.39 |         4.22 |
| QETH11  |      1 | 2024-02-23 00:00:00 | 2024-02-29 00:00:00 |      4 |       16.4  |         3.23 |
| QBTC11  |      1 | 2023-03-14 00:00:00 | 2023-03-20 00:00:00 |      4 |       14.09 |         2.76 |
| QETH11  |      1 | 2023-01-13 00:00:00 | 2023-01-18 00:00:00 |      3 |       11.07 |         2.17 |
| QBTC11  |      1 | 2024-03-19 00:00:00 | 2024-03-25 00:00:00 |      4 |        7.02 |         1.35 |
| QBTC11  |      1 | 2024-07-16 00:00:00 | 2024-07-22 00:00:00 |      4 |        5.62 |         1.08 |
| QETH11  |      1 | 2024-05-22 00:00:00 | 2024-05-28 00:00:00 |      4 |        5.32 |         1.02 |
| QETH11  |      1 | 2024-02-02 00:00:00 | 2024-02-08 00:00:00 |      4 |        5.13 |         0.98 |
| QETH11  |      1 | 2022-12-28 00:00:00 | 2023-01-03 00:00:00 |      4 |        3.7  |         0.68 |
| QETH11  |      1 | 2022-12-12 00:00:00 | 2022-12-16 00:00:00 |      4 |        3.24 |         0.59 |

**10 piores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| ETHE11  |      1 | 2024-07-23 00:00:00 | 2024-07-25 00:00:00 |      2 |       -9.15 |        -1.85 |
| QETH11  |      1 | 2024-04-09 00:00:00 | 2024-04-15 00:00:00 |      4 |       -7.75 |        -1.59 |
| ETHE11  |      1 | 2023-05-30 00:00:00 | 2023-06-05 00:00:00 |      4 |       -7.15 |        -1.47 |
| QETH11  |      1 | 2022-05-16 00:00:00 | 2022-05-20 00:00:00 |      4 |       -6.41 |        -1.33 |
| QETH11  |      1 | 2022-11-11 00:00:00 | 2022-11-18 00:00:00 |      4 |       -5.42 |        -1.13 |
| QETH11  |      1 | 2022-10-26 00:00:00 | 2022-11-01 00:00:00 |      4 |       -5.37 |        -1.12 |
| QETH11  |      1 | 2021-12-06 00:00:00 | 2021-12-10 00:00:00 |      4 |       -5.41 |        -1.12 |
| QETH11  |      1 | 2022-12-02 00:00:00 | 2022-12-08 00:00:00 |      4 |       -5.12 |        -1.07 |
| QBTC11  |      1 | 2024-04-09 00:00:00 | 2024-04-15 00:00:00 |      4 |       -4.59 |        -0.96 |
| QETH11  |      1 | 2022-07-21 00:00:00 | 2022-07-27 00:00:00 |      4 |       -4.26 |        -0.9  |

**Quem trouxe o retorno (soma por ativo, pp)**

| ativo   |   sum |   count |
|:--------|------:|--------:|
| QBTC11  |  5.9  |      14 |
| QETH11  |  0.17 |      19 |
| BITH11  | -0.5  |       3 |
| ETHE11  | -5.3  |       6 |

### Bitcoin em R$ com tendência (à vista isento ou BIT) e contra a manada local  (`gl_cripto_tendencia`)

**Tese:** BTC acima da média longa, tamanho por vol, à vista em corretora BR (isenção de R$ 35 mil/mês) ou BIT; sai com ágio local alto

**Instrumentos:** {'BTC à vista': {'onde': 'Binance BR / Mercado Bitcoin', 'ticker': 'BTCBRL', 'lote': 'fração', 'custo': '0,15% (0,5% MB pré-2020)'}, 'BIT': {'onde': 'B3 (futuro)', 'ticker': 'BIT', 'lote': '0,01 BTC desde 06/2025', 'custo': '~0,05%'}}

**Aplicável:** True — BTC à vista é fracionário (qualquer valor); BIT só cabe para R$ 20 mil desde 06/2025.

| métrica | valor |
|---|---|
| OOS desde | 2021-01 |
| retorno OOS a.a. (R$ 20 mil) | 15.6% vs CDI 11.4% |
| ativo OOS pp (R$ 20 mil / R$ 50 mil) | +4.20 / +4.20 |
| depois do IR (classe cripto) pp, 20k / 50k | +4.14 / +4.14 |
| IR OOS / Sharpe | +0.30 / +0.30 |
| pior queda | -19.1% |
| PBO / Sharpe deflacionado | 76% / +55% |
| leque de parâmetros p5 / mediana / p95 | +3.90 / +5.54 / +9.67 |
| custo 2x / execução t+2 | +2.02 / +13.67 |
| walk-forward | +4.45 |
| sem os 10 melhores negócios | -17.24 |
| placebo p | 0.22 |
| look-ahead (truncamento) | passou |

**10 melhores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| BTC     |      1 | 2016-10-25 00:00:00 | 2017-07-18 00:00:00 |    182 |      254.44 |        97.22 |
| BTC     |      1 | 2015-06-19 00:00:00 | 2016-04-12 00:00:00 |    204 |      104.63 |        43.65 |
| BTC     |      1 | 2017-07-19 00:00:00 | 2018-02-02 00:00:00 |    136 |      259.43 |        41.39 |
| BTC     |      1 | 2019-04-10 00:00:00 | 2019-07-17 00:00:00 |     67 |       79.05 |        33.73 |
| BTC     |      1 | 2020-09-23 00:00:00 | 2020-11-27 00:00:00 |     45 |       59.16 |        32.62 |
| BTC     |      1 | 2020-11-30 00:00:00 | 2021-01-05 00:00:00 |     24 |       73.34 |        30.34 |
| BTC     |      1 | 2024-10-14 00:00:00 | 2024-12-06 00:00:00 |     37 |       66.92 |        27.38 |
| BTC     |      1 | 2016-05-27 00:00:00 | 2016-08-04 00:00:00 |     49 |       12.39 |        19.37 |
| BTC     |      1 | 2019-03-28 00:00:00 | 2019-04-09 00:00:00 |      8 |       29.45 |        17.04 |
| BTC     |      1 | 2021-08-16 00:00:00 | 2021-11-12 00:00:00 |     61 |       44.66 |        16.54 |

**10 piores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| BTC     |      1 | 2020-02-19 00:00:00 | 2020-03-13 00:00:00 |     15 |      -37.22 |       -19.87 |
| BTC     |      1 | 2014-07-02 00:00:00 | 2014-08-18 00:00:00 |     33 |      -15.79 |        -8.65 |
| BTC     |      1 | 2021-11-16 00:00:00 | 2021-12-10 00:00:00 |     18 |      -17.71 |        -8.34 |
| BTC     |      1 | 2021-05-12 00:00:00 | 2021-05-18 00:00:00 |      4 |      -21.05 |        -7.31 |
| BTC     |      1 | 2025-02-19 00:00:00 | 2025-02-26 00:00:00 |      5 |      -10.87 |        -6.28 |
| BTC     |      1 | 2021-01-08 00:00:00 | 2021-01-11 00:00:00 |      1 |      -13.71 |        -5.65 |
| BTC     |      1 | 2025-08-01 00:00:00 | 2025-09-01 00:00:00 |     21 |       -5.32 |        -5.63 |
| BTC     |      1 | 2023-01-16 00:00:00 | 2023-03-10 00:00:00 |     37 |       -5.06 |        -5.39 |
| BTC     |      1 | 2024-12-24 00:00:00 | 2025-02-17 00:00:00 |     37 |       -9.27 |        -5.32 |
| BTC     |      1 | 2023-08-02 00:00:00 | 2023-08-18 00:00:00 |     12 |       -7.38 |        -5.26 |

**Quem trouxe o retorno (soma por ativo, pp)**

| ativo   |    sum |   count |
|:--------|-------:|--------:|
| BTC     | 310.48 |     106 |

### Spin-offs dos EUA (IBKR) com hedge em IVVB11 vendido  (`gl_spinoff`)

**Tese:** Compro o spin-off depois da venda forçada dos indexados (IBKR, 5% por nome) e vendo IVVB11 na B3 contra (bolsa + dólar)

**Instrumentos:** {'spin-offs': {'onde': 'IBKR', 'ticker': '~10-20 por ano', 'lote': 'fração', 'custo': 'US$ 0,0035/ação mín. 0,35 + 0,2%'}, 'IVVB11': {'onde': 'B3 (aluguel)', 'ticker': 'IVVB11', 'lote': 1, 'custo': '1% a.a. + 0,5% por contrato'}}

**Aplicável:** True — Com R$ 20 mil, 5% = R$ 1 mil (~US$ 200) por nome: comissão mínima de US$ 0,35 = 0,2% por lado, aceitável. Exige conta na IBKR (só com o valor da carteira) e aluguel de IVVB11 na B3.

| métrica | valor |
|---|---|
| OOS desde | 2021-01 |
| retorno OOS a.a. (R$ 20 mil) | 27.8% vs CDI 11.4% |
| ativo OOS pp (R$ 20 mil / R$ 50 mil) | +16.36 / +16.50 |
| depois do IR (classe exterior) pp, 20k / 50k | +14.45 / +14.55 |
| IR OOS / Sharpe | +0.62 / +0.62 |
| pior queda | -28.5% |
| PBO / Sharpe deflacionado | 0% / +1% |
| leque de parâmetros p5 / mediana / p95 | +3.36 / +13.73 / +44.16 |
| custo 2x / execução t+2 | -2.20 / +16.36 |
| walk-forward | +16.36 |
| sem os 10 melhores negócios | -16.81 |
| placebo p | 0.00 |
| look-ahead (truncamento) | FALHOU |

**10 melhores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| SNDK    |      1 | 2025-04-14 00:00:00 | 2026-04-16 00:00:00 |    252 |     2640.6  |       118.4  |
| PRTA    |      1 | 2013-02-22 00:00:00 | 2014-02-24 00:00:00 |    252 |      373.67 |        21.21 |
| RHLD    |      1 | 2025-04-23 00:00:00 | 2026-04-24 00:00:00 |    252 |      435.84 |        21.13 |
| CRNC    |      1 | 2019-11-12 00:00:00 | 2020-11-11 00:00:00 |    252 |      316.85 |        20.2  |
| VRTS    |      1 | 2009-03-04 00:00:00 | 2010-03-04 00:00:00 |    252 |      409.65 |        17.49 |
| CLW     |      1 | 2009-02-05 00:00:00 | 2010-02-05 00:00:00 |    252 |      352.67 |        14.59 |
| MPTI    |      1 | 2022-11-30 00:00:00 | 2023-12-01 00:00:00 |    252 |      227.03 |        10.78 |
| XPEL    |      1 | 2019-08-28 00:00:00 | 2020-08-27 00:00:00 |    252 |      151.01 |         9.45 |
| GEV     |      1 | 2024-05-24 00:00:00 | 2025-05-29 00:00:00 |    252 |      165.95 |         9.25 |
| PNTG    |      1 | 2019-11-27 00:00:00 | 2020-11-27 00:00:00 |    252 |      112.92 |         7.52 |

**10 piores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| CVEO    |      1 | 2014-07-17 00:00:00 | 2015-07-17 00:00:00 |    252 |      -89.33 |        -5.1  |
| FEAM    |      1 | 2022-05-12 00:00:00 | 2023-05-15 00:00:00 |    252 |      -84.36 |        -4.29 |
| KLXE    |      1 | 2018-10-26 00:00:00 | 2019-10-29 00:00:00 |    252 |      -70.79 |        -3.81 |
| RYAM    |      1 | 2014-08-13 00:00:00 | 2015-08-13 00:00:00 |    252 |      -59.16 |        -3.43 |
| FOR     |      1 | 2008-02-13 00:00:00 | 2009-02-12 00:00:00 |    252 |      -65.13 |        -3.31 |
| KTB     |      1 | 2019-07-25 00:00:00 | 2020-07-24 00:00:00 |    252 |      -38.28 |        -2.96 |
| MDIA    |      1 | 2020-03-05 00:00:00 | 2021-03-05 00:00:00 |    252 |      -51.61 |        -2.96 |
| LPS*    |      1 | 2008-08-27 00:00:00 | 2009-08-27 00:00:00 |    252 |      -41.81 |        -2.81 |
| KLXI*   |      1 | 2015-01-28 00:00:00 | 2016-01-28 00:00:00 |    252 |      -41.81 |        -2.81 |
| SNI*    |      1 | 2008-08-28 00:00:00 | 2009-08-28 00:00:00 |    252 |      -41.81 |        -2.81 |

**Quem trouxe o retorno (soma por ativo, pp)**

| ativo   |    sum |   count |
|:--------|-------:|--------:|
| SNDK    | 118.4  |       1 |
| PRTA    |  21.21 |       1 |
| RHLD    |  21.13 |       1 |
| CRNC    |  20.2  |       1 |
| VRTS    |  17.49 |       1 |
| CLW     |  14.59 |       1 |
| MPTI    |  10.78 |       1 |
| XPEL    |   9.45 |       1 |
| GEV     |   9.25 |       1 |
| PNTG    |   7.52 |       1 |

### S&P 500 via WSP (B3) + SPXR11, tendência e vol-alvo, sem remessa  (`gl_wsp`)

**Tese:** Comprado em S&P pelo micro futuro da B3 (margem no Tesouro Selic) quando a tendência e o risco global deixam; resto em SPXR11

**Instrumentos:** {'WSP': {'onde': 'B3 (futuro)', 'ticker': 'WSP', 'lote': '1 contrato = US$ 2,50 x S&P (~R$ 100 mil)', 'custo': 'R$ 2,50/lado'}, 'SPXR11': {'onde': 'B3', 'ticker': 'SPXR11', 'lote': 1, 'custo': 'meio spread + 0,03%'}}

**Aplicável:** True — Aplicável, mas com R$ 20 mil o WSP (≈ R$ 100 mil de nocional) não cabe a 1x: a exposição vai toda para o SPXR11; com R$ 50 mil, 1 WSP entra quando o alvo passa de ~2x (alavancagem 2x).

| métrica | valor |
|---|---|
| OOS desde | 2021-01 |
| retorno OOS a.a. (R$ 20 mil) | 16.6% vs CDI 11.4% |
| ativo OOS pp (R$ 20 mil / R$ 50 mil) | +5.14 / +8.23 |
| depois do IR (classe futuros_b3) pp, 20k / 50k | +4.10 / +6.79 |
| IR OOS / Sharpe | +0.34 / +0.34 |
| pior queda | -18.9% |
| PBO / Sharpe deflacionado | 48% / +53% |
| leque de parâmetros p5 / mediana / p95 | +4.34 / +6.01 / +13.25 |
| custo 2x / execução t+2 | +3.55 / +5.15 |
| walk-forward | +5.14 |
| sem os 10 melhores negócios | +2.96 |
| placebo p | 0.76 |
| look-ahead (truncamento) | passou |

**10 melhores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| WSP     |      1 | 2012-01-02 00:00:00 | 2015-09-01 00:00:00 |    923 |       63.72 |        62.18 |
| WSP     |      1 | 2016-04-01 00:00:00 | 2018-05-02 00:00:00 |    521 |       30.12 |        47.53 |
| SPXR11  |      1 | 2020-06-01 00:00:00 | 2022-03-02 00:00:00 |    440 |       52.84 |        41.86 |
| SPXR11  |      1 | 2023-12-01 00:00:00 | 2025-04-01 00:00:00 |    334 |       30.66 |        19.51 |
| WSP     |      1 | 2009-06-01 00:00:00 | 2010-06-01 00:00:00 |    251 |       15.61 |        14.42 |
| WSP     |      1 | 2010-10-01 00:00:00 | 2011-09-01 00:00:00 |    231 |        6.99 |        11.4  |
| SPXR11  |      1 | 2026-05-04 00:00:00 | 2026-10-13 00:00:00 |    113 |       12.69 |         8    |
| WSP     |      1 | 2018-12-24 00:00:00 | 2019-01-02 00:00:00 |      5 |        6.71 |         7.62 |
| WSP     |      1 | 2019-07-01 00:00:00 | 2020-03-02 00:00:00 |    170 |        4.34 |         6.08 |
| SPXR11  |      1 | 2013-06-03 00:00:00 | 2015-02-20 00:00:00 |    436 |       52.55 |         5.22 |

**10 piores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| SPXR11  |      1 | 2018-12-03 00:00:00 | 2018-12-26 00:00:00 |     16 |      -11.22 |       -18.78 |
| SPXR11  |      1 | 2022-04-01 00:00:00 | 2022-05-02 00:00:00 |     19 |       -7.89 |        -8.79 |
| SPXR11  |      1 | 2023-02-01 00:00:00 | 2023-11-01 00:00:00 |    187 |        8.57 |        -6.47 |
| WSP     |      1 | 2019-04-01 00:00:00 | 2019-06-03 00:00:00 |     43 |       -4.32 |        -6.25 |
| SPXR11  |      1 | 2022-12-01 00:00:00 | 2023-01-02 00:00:00 |     22 |       -5.13 |        -4.86 |
| WSP     |      1 | 2015-12-01 00:00:00 | 2016-01-04 00:00:00 |     22 |       -4.03 |        -4.06 |
| SPXR11  |      1 | 2019-03-01 00:00:00 | 2019-06-03 00:00:00 |     62 |       -1.15 |        -1.86 |
| SPXR11  |      1 | 2015-11-03 00:00:00 | 2016-01-04 00:00:00 |     42 |       -2.34 |        -1.4  |
| SPXR11  |      1 | 2015-03-05 00:00:00 | 2015-08-05 00:00:00 |    105 |        5.3  |        -1.12 |
| SPXR11  |      1 | 2010-03-30 00:00:00 | 2010-06-01 00:00:00 |     43 |       -7.34 |        -1.1  |

**Quem trouxe o retorno (soma por ativo, pp)**

| ativo   |    sum |   count |
|:--------|-------:|--------:|
| WSP     | 139.72 |       9 |
| SPXR11  |  43.79 |      33 |
