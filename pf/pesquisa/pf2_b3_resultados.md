# Frente pf2_b3 — resultados da bateria final (gerado automaticamente)

Gerado por `pf/gerar_cadernos.py` a partir de `pf/resultados/bateria/`. IR de pessoa física por `pf/ir.py` (mensal na B3 com isenção de ações ≤ R$ 20 mil/mês, anual no exterior). Ordem: nota do ranking.

### Dividendo/JCP extraordinário (até a data-com) — AUDITADA (universo completo de proventos B3)  (`bb_dividendo_extra_aud`)

**Tese:** Compro a ação no dia seguinte à aprovação de um provento extraordinário (>= limiar do preço) e vendo na data-com para o investidor de renda que compra para estar na base; lote pequeno

**Instrumentos:** [{'onde': 'Clear/Rico/XP (corretagem zero)', 'ticker': 'pagadoras de provento extraordinário (103 companhias)', 'lote': '1 ação', 'custo': 'emolumentos 0,03% + meio spread real do fechamento + 0,2% no fracionário'}]

**Aplicável:** True — universo completo (todas as pagadoras do COTAHIST, inclusive deslistadas)

| métrica | valor |
|---|---|
| OOS desde | 2021-01 |
| retorno OOS a.a. (R$ 20 mil) | 29.1% vs CDI 11.4% |
| ativo OOS pp (R$ 20 mil / R$ 50 mil) | +17.64 / +19.08 |
| depois do IR (classe O.CLASSE_IR) pp, 20k / 50k | +14.37 / +15.53 |
| IR OOS / Sharpe | +1.25 / +1.25 |
| pior queda | -8.6% |
| PBO / Sharpe deflacionado | 0% / +80% |
| leque de parâmetros p5 / mediana / p95 | +10.49 / +16.73 / +24.26 |
| custo 2x / execução t+2 | +11.41 / +9.88 |
| walk-forward | +15.83 |
| sem os 10 melhores negócios | +10.35 |
| placebo p | 0.00 |
| look-ahead (truncamento) | passou |

**10 melhores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| BOAS3   |      1 | 2022-12-16 00:00:00 | 2022-12-21 00:00:00 |      3 |       51.36 |        10.27 |
| MRVE3   |      1 | 2019-04-29 00:00:00 | 2019-12-10 00:00:00 |    158 |       38.19 |         7.63 |
| MRVE3   |      1 | 2020-04-20 00:00:00 | 2020-10-13 00:00:00 |    121 |       29.93 |         5.97 |
| BRAP3   |      1 | 2021-11-09 00:00:00 | 2021-12-16 00:00:00 |     26 |       23.36 |         4.66 |
| BRAP4   |      1 | 2021-11-09 00:00:00 | 2021-12-16 00:00:00 |     26 |       21.24 |         4.23 |
| VLID3   |      1 | 2024-07-17 00:00:00 | 2024-08-09 00:00:00 |     17 |       19.78 |         3.95 |
| HGTX3   |      1 | 2017-04-27 00:00:00 | 2017-05-05 00:00:00 |      5 |       19.36 |         3.86 |
| PETR3   |      1 | 2023-05-12 00:00:00 | 2023-06-12 00:00:00 |     20 |       16.98 |         3.39 |
| MRFG3   |      1 | 2024-11-14 00:00:00 | 2024-12-12 00:00:00 |     18 |       16.97 |         3.38 |
| MRFG3   |      1 | 2021-08-11 00:00:00 | 2021-09-10 00:00:00 |     21 |       16.59 |         3.31 |

**10 piores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| MRVE3   |      1 | 2018-04-23 00:00:00 | 2018-12-13 00:00:00 |    162 |      -16.18 |        -3.22 |
| VIVT3   |      1 | 2026-03-16 00:00:00 | 2026-05-22 00:00:00 |     46 |      -14.5  |        -2.88 |
| BBSE3   |      1 | 2021-06-23 00:00:00 | 2021-08-11 00:00:00 |     35 |      -12.49 |        -2.48 |
| LEVE3   |      1 | 2023-10-24 00:00:00 | 2023-11-01 00:00:00 |      6 |      -11.29 |        -2.26 |
| QUAL3   |      1 | 2016-11-08 00:00:00 | 2016-11-11 00:00:00 |      3 |      -10.89 |        -2.18 |
| STBP3   |      1 | 2022-11-08 00:00:00 | 2022-11-10 00:00:00 |      2 |      -10.86 |        -2.17 |
| VULC3   |      1 | 2022-11-03 00:00:00 | 2022-11-10 00:00:00 |      5 |      -10.76 |        -2.15 |
| GGBR4   |      1 | 2021-10-28 00:00:00 | 2021-11-05 00:00:00 |      5 |      -10.79 |        -2.14 |
| GOAU4   |      1 | 2021-10-28 00:00:00 | 2021-11-05 00:00:00 |      5 |      -10.08 |        -1.94 |
| DTEX3   |      1 | 2021-02-09 00:00:00 | 2021-02-17 00:00:00 |      4 |       -9.53 |        -1.9  |

**Quem trouxe o retorno (soma por ativo, pp)**

| ativo   |   sum |   count |
|:--------|------:|--------:|
| MRVE3   | 10.56 |       4 |
| BOAS3   | 10.27 |       1 |
| MRFG3   |  9.02 |       7 |
| BRAP4   |  8.42 |       6 |
| BBSE3   |  7.63 |      20 |
| PETR4   |  7.16 |      13 |
| PETR3   |  6    |      13 |
| VLID3   |  5.85 |       4 |
| CPLE6   |  5.6  |       9 |
| BRAP3   |  4.66 |       1 |

### Vencimento de opções: objetos comprados no fechamento do vencimento  (`bb_vencimento_opcoes`)

**Tese:** Compro PETR4/VALE3/ITUB4/BBDC4/BBAS3/ABEV3 no fechamento do vencimento mensal de opções (fim da venda mecânica de lançadores cobertos/exercício/delta-hedge) e vendo k pregões depois

**Instrumentos:** [{'onde': 'Clear/Rico/XP (corretagem zero)', 'ticker': 'PETR4, VALE3, ITUB4, BBDC4, BBAS3, ABEV3', 'lote': '1 ação (fracionário)', 'custo': 'emolumentos 0,03% + meio spread real do fechamento + 0,2% no fracionário'}]

**Aplicável:** True — blue chips no fracionário; 12 entradas por ano de 3 pregões; vendas do mês ~R$ 18 mil com R$ 20 mil (isento)

| métrica | valor |
|---|---|
| OOS desde | 2021-01 |
| retorno OOS a.a. (R$ 20 mil) | 12.8% vs CDI 11.4% |
| ativo OOS pp (R$ 20 mil / R$ 50 mil) | +1.33 / +2.13 |
| depois do IR (classe acoes) pp, 20k / 50k | +1.31 / +1.65 |
| IR OOS / Sharpe | +0.18 / +0.18 |
| pior queda | -17.7% |
| PBO / Sharpe deflacionado | 26% / +17% |
| leque de parâmetros p5 / mediana / p95 | -1.64 / +0.61 / +1.44 |
| custo 2x / execução t+2 | -1.33 / +0.67 |
| walk-forward | +1.33 |
| sem os 10 melhores negócios | -3.93 |
| placebo p | 0.14 |
| look-ahead (truncamento) | passou |

**10 melhores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| VALE3   |      1 | 2015-04-20 00:00:00 | 2015-04-24 00:00:00 |      3 |       30.72 |        13.81 |
| PETR4   |      1 | 2014-11-17 00:00:00 | 2014-11-21 00:00:00 |      4 |       13.34 |         6    |
| PETR4   |      1 | 2015-01-19 00:00:00 | 2015-01-22 00:00:00 |      3 |       11.33 |         5.1  |
| PETR4   |      1 | 2014-03-17 00:00:00 | 2014-03-20 00:00:00 |      3 |       11.14 |         5.01 |
| VALE3   |      1 | 2021-11-19 00:00:00 | 2021-11-24 00:00:00 |      3 |       10.65 |         4.78 |
| PETR4   |      1 | 2021-11-19 00:00:00 | 2021-11-24 00:00:00 |      3 |        8.52 |         3.83 |
| VALE3   |      1 | 2016-02-15 00:00:00 | 2016-02-18 00:00:00 |      3 |        7.73 |         3.48 |
| PETR4   |      1 | 2018-04-16 00:00:00 | 2018-04-19 00:00:00 |      3 |        7.52 |         3.38 |
| VALE3   |      1 | 2018-09-17 00:00:00 | 2018-09-20 00:00:00 |      3 |        7.51 |         3.37 |
| PETR4   |      1 | 2023-06-16 00:00:00 | 2023-06-21 00:00:00 |      3 |        7.36 |         3.3  |

**10 piores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| PETR4   |      1 | 2021-02-17 00:00:00 | 2021-02-22 00:00:00 |      3 |      -27.6  |       -12.41 |
| PETR4   |      1 | 2018-05-21 00:00:00 | 2018-05-24 00:00:00 |      3 |      -19.85 |        -8.93 |
| PETR4   |      1 | 2017-05-15 00:00:00 | 2017-05-18 00:00:00 |      3 |      -16.4  |        -7.37 |
| PETR4   |      1 | 2014-10-20 00:00:00 | 2014-10-23 00:00:00 |      3 |      -14.23 |        -6.4  |
| PETR4   |      1 | 2022-10-21 00:00:00 | 2022-10-26 00:00:00 |      3 |      -13.42 |        -6.03 |
| VALE3   |      1 | 2022-04-18 00:00:00 | 2022-04-22 00:00:00 |      3 |      -11.64 |        -5.22 |
| VALE3   |      1 | 2017-02-20 00:00:00 | 2017-02-23 00:00:00 |      3 |       -9.15 |        -4.12 |
| PETR4   |      1 | 2016-05-16 00:00:00 | 2016-05-19 00:00:00 |      3 |       -8.27 |        -3.72 |
| VALE3   |      1 | 2017-03-20 00:00:00 | 2017-03-23 00:00:00 |      3 |       -8    |        -3.59 |
| VALE3   |      1 | 2015-09-21 00:00:00 | 2015-09-24 00:00:00 |      3 |       -7.78 |        -3.5  |

**Quem trouxe o retorno (soma por ativo, pp)**

| ativo   |   sum |   count |
|:--------|------:|--------:|
| VALE3   | 32.9  |     153 |
| PETR4   | 28.59 |     153 |

### Rebalanceamento SMLL/IBrX-100 (entrantes, PF)  (`bb_rebal_indices`)

**Tese:** Compro os prováveis entrantes do SMLL e do IBrX-100 (regra da B3 reconstruída com dados até a data, sem os do Ibovespa) antes da troca e vendo no fechamento do último pregão da carteira velha para o ETF/fundos passivos; lote pequeno em papel ilíquido

**Instrumentos:** [{'onde': 'Clear/Rico/XP (corretagem zero)', 'ticker': 'entrantes prováveis do SMLL/IBrX-100 (lote + fracionário XXXX3F)', 'lote': '1 ação', 'custo': 'emolumentos 0,03% + meio spread real do fechamento + 0,2% no fracionário'}]

**Aplicável:** True — ações à vista no fracionário, 8% do capital por papel; 5–12 entrantes por revisão; vendas do mês quase sempre < R$ 20 mil

| métrica | valor |
|---|---|
| OOS desde | 2021-01 |
| retorno OOS a.a. (R$ 20 mil) | 9.1% vs CDI 11.4% |
| ativo OOS pp (R$ 20 mil / R$ 50 mil) | -2.39 / -2.26 |
| depois do IR (classe acoes) pp, 20k / 50k | -2.35 / -2.22 |
| IR OOS / Sharpe | -0.21 / -0.21 |
| pior queda | -13.4% |
| PBO / Sharpe deflacionado | 57% / +0% |
| leque de parâmetros p5 / mediana / p95 | -4.68 / -2.02 / +1.79 |
| custo 2x / execução t+2 | -3.09 / -2.92 |
| walk-forward | -2.22 |
| sem os 10 melhores negócios | -7.36 |
| placebo p | 0.61 |
| look-ahead (truncamento) | passou |

**10 melhores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| BIDI4   |      1 | 2019-07-04 00:00:00 | 2019-08-30 00:00:00 |     41 |       66.27 |         5.27 |
| MDIA3   |      1 | 2022-07-05 00:00:00 | 2022-08-31 00:00:00 |     41 |       51.75 |         4.09 |
| MEAL3   |      1 | 2020-11-03 00:00:00 | 2021-01-04 00:00:00 |     42 |       47.17 |         3.77 |
| FLRY3   |      1 | 2016-07-05 00:00:00 | 2016-08-31 00:00:00 |     41 |       45.96 |         3.67 |
| CVCB3   |      1 | 2016-03-01 00:00:00 | 2016-04-29 00:00:00 |     41 |       44.34 |         3.52 |
| ELET3   |      1 | 2015-03-02 00:00:00 | 2015-04-30 00:00:00 |     41 |       42.37 |         3.39 |
| BIDI4   |      1 | 2021-03-02 00:00:00 | 2021-04-30 00:00:00 |     41 |       42.4  |         3.35 |
| CMIG3   |      1 | 2018-10-30 00:00:00 | 2019-01-02 00:00:00 |     42 |       41.54 |         3.32 |
| POMO4   |      1 | 2023-10-30 00:00:00 | 2024-01-02 00:00:00 |     42 |       38.37 |         3.07 |
| BIDI11  |      1 | 2021-03-02 00:00:00 | 2021-04-30 00:00:00 |     41 |       40.55 |         2.99 |

**10 piores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| TCSA3   |      1 | 2020-03-02 00:00:00 | 2020-04-30 00:00:00 |     41 |      -51.95 |        -4.15 |
| PRIO3   |      1 | 2020-03-02 00:00:00 | 2020-04-30 00:00:00 |     41 |      -52.1  |        -4.08 |
| OIBR3   |      1 | 2023-02-28 00:00:00 | 2023-04-28 00:00:00 |     41 |      -50.08 |        -4.01 |
| ONCO3   |      1 | 2024-10-30 00:00:00 | 2025-01-02 00:00:00 |     42 |      -48.55 |        -3.88 |
| BPAN4   |      1 | 2020-03-02 00:00:00 | 2020-04-30 00:00:00 |     41 |      -43.64 |        -3.48 |
| CEAB3   |      1 | 2024-10-30 00:00:00 | 2025-01-02 00:00:00 |     42 |      -41.28 |        -3.3  |
| ANIM3   |      1 | 2024-03-01 00:00:00 | 2024-04-30 00:00:00 |     41 |      -35.84 |        -2.86 |
| AMBP3   |      1 | 2024-10-30 00:00:00 | 2025-01-02 00:00:00 |     42 |      -37.49 |        -2.78 |
| LIGT3   |      1 | 2023-07-05 00:00:00 | 2023-08-31 00:00:00 |     41 |      -34.21 |        -2.72 |
| BHIA3   |      1 | 2024-10-30 00:00:00 | 2025-01-02 00:00:00 |     42 |      -32.26 |        -2.58 |

**Quem trouxe o retorno (soma por ativo, pp)**

| ativo   |   sum |   count |
|:--------|------:|--------:|
| BIDI4   |  8.61 |       2 |
| VIVA3   |  5.31 |       2 |
| SIMH3   |  4.27 |       3 |
| MDIA3   |  4.09 |       1 |
| MEAL3   |  3.77 |       1 |
| FLRY3   |  3.67 |       1 |
| CVCB3   |  3.52 |       1 |
| ELET3   |  3.39 |       1 |
| CMIG3   |  3.32 |       1 |
| BIDI11  |  2.99 |       1 |

### Pânico de FII (venda forçada do varejo)  (`bb_fii_panico`)

**Tese:** Compro o FII que caiu muito mais que o índice de FIIs em 5 pregões (venda de pânico do varejo, sem comprador institucional) e seguro hold pregões; R$ 2 mil por FII

**Instrumentos:** [{'onde': 'Clear/Rico/XP/Inter (corretagem zero)', 'ticker': 'FII com queda forte (XXXX11)', 'lote': '1 cota', 'custo': 'emolumentos 0,03% + meio spread real do fechamento'}]

**Aplicável:** True — FIIs com ADV >= R$ 500 mil; R$ 2 mil por FII com R$ 20 mil

| métrica | valor |
|---|---|
| OOS desde | 2021-01 |
| retorno OOS a.a. (R$ 20 mil) | 10.4% vs CDI 11.4% |
| ativo OOS pp (R$ 20 mil / R$ 50 mil) | -1.01 / -1.00 |
| depois do IR (classe fii) pp, 20k / 50k | -1.05 / -1.04 |
| IR OOS / Sharpe | -0.15 / -0.15 |
| pior queda | -8.6% |
| PBO / Sharpe deflacionado | 3% / +0% |
| leque de parâmetros p5 / mediana / p95 | -3.86 / -1.61 / -0.07 |
| custo 2x / execução t+2 | -1.99 / -2.14 |
| walk-forward | -1.01 |
| sem os 10 melhores negócios | -4.53 |
| placebo p | 0.10 |
| look-ahead (truncamento) | passou |

**10 melhores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| HCTR11  |      1 | 2023-04-26 00:00:00 | 2023-05-26 00:00:00 |     21 |       45.61 |         4.55 |
| DEVA11  |      1 | 2023-04-26 00:00:00 | 2023-05-26 00:00:00 |     21 |       41.28 |         4.12 |
| SPTW11  |      1 | 2020-03-19 00:00:00 | 2020-04-20 00:00:00 |     21 |       37.83 |         3.78 |
| VISC11  |      1 | 2020-03-19 00:00:00 | 2020-04-20 00:00:00 |     21 |       33.28 |         3.25 |
| KFOF11  |      1 | 2020-03-23 00:00:00 | 2020-04-23 00:00:00 |     21 |       32.55 |         3.23 |
| MALL11  |      1 | 2020-03-19 00:00:00 | 2020-04-20 00:00:00 |     21 |       31.95 |         3.12 |
| VIUR11  |      1 | 2026-04-10 00:00:00 | 2026-05-13 00:00:00 |     21 |       29.01 |         2.9  |
| BCIA11  |      1 | 2020-03-20 00:00:00 | 2020-04-22 00:00:00 |     21 |       26.44 |         2.46 |
| CACR11  |      1 | 2025-09-09 00:00:00 | 2025-10-08 00:00:00 |     21 |       20.83 |         2.03 |
| XPCM11  |      1 | 2020-08-10 00:00:00 | 2020-09-09 00:00:00 |     21 |       19.98 |         1.98 |

**10 piores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| CACR11  |      1 | 2026-05-05 00:00:00 | 2026-07-03 00:00:00 |     42 |      -45.21 |        -4.51 |
| CACR11  |      1 | 2026-07-06 00:00:00 | 2026-08-04 00:00:00 |     21 |      -40.73 |        -4.04 |
| DEVA11  |      1 | 2023-03-14 00:00:00 | 2023-04-13 00:00:00 |     21 |      -26.68 |        -2.6  |
| HCTR11  |      1 | 2023-03-13 00:00:00 | 2023-04-12 00:00:00 |     21 |      -21.94 |        -2.18 |
| KISU11  |      1 | 2021-07-19 00:00:00 | 2021-08-17 00:00:00 |     21 |      -15.88 |        -1.53 |
| VSLH11  |      1 | 2023-03-30 00:00:00 | 2023-05-03 00:00:00 |     21 |      -13.36 |        -1.33 |
| HCTR11  |      1 | 2023-09-12 00:00:00 | 2023-10-11 00:00:00 |     21 |      -12.21 |        -1.2  |
| XPCM11  |      1 | 2021-02-03 00:00:00 | 2021-03-08 00:00:00 |     21 |      -11.84 |        -1.18 |
| FIGS11  |      1 | 2018-05-09 00:00:00 | 2018-06-08 00:00:00 |     21 |      -11.9  |        -1.18 |
| XPIN11  |      1 | 2020-01-27 00:00:00 | 2020-02-27 00:00:00 |     21 |      -10.32 |        -0.99 |

**Quem trouxe o retorno (soma por ativo, pp)**

| ativo   |   sum |   count |
|:--------|------:|--------:|
| SPTW11  |  3.39 |       2 |
| BCIA11  |  3.28 |       3 |
| VISC11  |  3.25 |       1 |
| KFOF11  |  3.23 |       1 |
| MALL11  |  3.12 |       1 |
| VIUR11  |  2.9  |       1 |
| DEVA11  |  2.18 |       5 |
| XPCM11  |  2    |       5 |
| HCTR11  |  1.99 |       5 |
| BPFF11  |  1.92 |       1 |

### Saída de estrangeiro (EWZ) -> BOVA11 comprado  (`bb_estrangeiro`)

**Tese:** Compro BOVA11 depois de queda forte do EWZ com volume de resgate (o AP vende a cesta na B3 para entregar o resgate do estrangeiro) e seguro hold pregões

**Instrumentos:** [{'onde': 'Clear/Rico/XP', 'ticker': 'BOVA11', 'lote': '1 cota', 'custo': 'emolumentos 0,03% + meio spread 0,02%'}]

**Aplicável:** True — BOVA11 em cotas inteiras; sinais raros (2–4 por ano)

| métrica | valor |
|---|---|
| OOS desde | 2021-01 |
| retorno OOS a.a. (R$ 20 mil) | 8.7% vs CDI 11.4% |
| ativo OOS pp (R$ 20 mil / R$ 50 mil) | -2.70 / -2.70 |
| depois do IR (classe etf_b3) pp, 20k / 50k | -2.66 / -2.66 |
| IR OOS / Sharpe | -0.27 / -0.27 |
| pior queda | -9.7% |
| PBO / Sharpe deflacionado | 46% / +3% |
| leque de parâmetros p5 / mediana / p95 | -4.51 / -1.84 / +0.23 |
| custo 2x / execução t+2 | -2.87 / -2.97 |
| walk-forward | -3.83 |
| sem os 10 melhores negócios | -0.79 |
| placebo p | 0.77 |
| look-ahead (truncamento) | passou |

**10 melhores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| BOVA11  |      1 | 2009-04-01 00:00:00 | 2009-05-05 00:00:00 |     21 |       20.31 |        16.17 |
| BOVA11  |      1 | 2011-08-08 00:00:00 | 2011-09-13 00:00:00 |     25 |       14.59 |        11.75 |
| BOVA11  |      1 | 2009-10-30 00:00:00 | 2009-12-01 00:00:00 |     21 |       10.41 |         8.47 |
| BOVA11  |      1 | 2011-09-26 00:00:00 | 2011-10-28 00:00:00 |     23 |       10.35 |         8.34 |
| BOVA11  |      1 | 2016-09-15 00:00:00 | 2016-10-18 00:00:00 |     22 |       10.37 |         7.93 |
| BOVA11  |      1 | 2025-04-10 00:00:00 | 2025-05-16 00:00:00 |     23 |       10.29 |         7.76 |
| BOVA11  |      1 | 2009-06-22 00:00:00 | 2009-07-23 00:00:00 |     23 |        9.29 |         7.51 |
| BOVA11  |      1 | 2020-06-17 00:00:00 | 2020-07-17 00:00:00 |     22 |        7.81 |         6.77 |
| BOVA11  |      1 | 2013-06-24 00:00:00 | 2013-07-25 00:00:00 |     23 |        6.69 |         5.46 |
| BOVA11  |      1 | 2021-03-02 00:00:00 | 2021-03-31 00:00:00 |     21 |        4.4  |         3.93 |

**10 piores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| BOVA11  |      1 | 2020-02-27 00:00:00 | 2020-04-23 00:00:00 |     38 |      -22.73 |       -17.58 |
| BOVA11  |      1 | 2015-07-28 00:00:00 | 2015-10-30 00:00:00 |     66 |       -7.85 |        -9.63 |
| BOVA11  |      1 | 2022-11-14 00:00:00 | 2022-12-15 00:00:00 |     22 |       -8    |        -8.31 |
| BOVA11  |      1 | 2014-09-16 00:00:00 | 2014-11-27 00:00:00 |     52 |       -7.34 |        -7.52 |
| BOVA11  |      1 | 2015-12-02 00:00:00 | 2016-01-06 00:00:00 |     23 |       -6.81 |        -7.22 |
| BOVA11  |      1 | 2016-11-16 00:00:00 | 2016-12-19 00:00:00 |     23 |       -6.36 |        -6.7  |
| BOVA11  |      1 | 2021-01-26 00:00:00 | 2021-02-26 00:00:00 |     21 |       -5.79 |        -5.21 |
| BOVA11  |      1 | 2018-06-04 00:00:00 | 2018-07-10 00:00:00 |     26 |       -4.61 |        -4.66 |
| BOVA11  |      1 | 2022-06-14 00:00:00 | 2022-07-20 00:00:00 |     25 |       -3.47 |        -4.15 |
| BOVA11  |      1 | 2018-08-14 00:00:00 | 2018-09-14 00:00:00 |     22 |       -4.07 |        -4.06 |

**Quem trouxe o retorno (soma por ativo, pp)**

| ativo   |   sum |   count |
|:--------|------:|--------:|
| BOVA11  |  1.28 |      37 |

### FII depois do fim do direito de preferência (emissão)  (`bb_fii_emissao`)

**Tese:** Compro a cota do FII no pregão seguinte ao último dia de negociação do direito de preferência da emissão: acaba a venda do arbitrador/cotista que pressionava a cota; seguro hold pregões

**Instrumentos:** [{'onde': 'Clear/Rico/XP/Inter (corretagem zero)', 'ticker': 'cota do FII emissor (XXXX11)', 'lote': '1 cota', 'custo': 'emolumentos 0,03% + meio spread real do fechamento'}]

**Aplicável:** True — FIIs com emissão em andamento; R$ 3 mil por oferta com R$ 20 mil; ~15–25 ofertas com direito negociado por ano

| métrica | valor |
|---|---|
| OOS desde | 2021-01 |
| retorno OOS a.a. (R$ 20 mil) | 10.3% vs CDI 11.4% |
| ativo OOS pp (R$ 20 mil / R$ 50 mil) | -1.13 / -1.13 |
| depois do IR (classe fii) pp, 20k / 50k | -1.12 / -1.12 |
| IR OOS / Sharpe | -0.42 / -0.42 |
| pior queda | -1.7% |
| PBO / Sharpe deflacionado | 22% / +7% |
| leque de parâmetros p5 / mediana / p95 | -3.67 / -1.65 / +0.15 |
| custo 2x / execução t+2 | -2.05 / -2.03 |
| walk-forward | -0.55 |
| sem os 10 melhores negócios | -2.24 |
| placebo p | 0.44 |
| look-ahead (truncamento) | passou |

**10 melhores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| RBRF11  |      1 | 2020-03-23 00:00:00 | 2020-04-23 00:00:00 |     21 |       38.1  |         5.62 |
| MXRF11  |      1 | 2019-11-21 00:00:00 | 2019-12-20 00:00:00 |     21 |       21.1  |         3.15 |
| BCFF11  |      1 | 2019-10-07 00:00:00 | 2019-11-05 00:00:00 |     21 |       13.66 |         2    |
| RBRR11  |      1 | 2018-12-04 00:00:00 | 2019-01-04 00:00:00 |     21 |       12.66 |         1.84 |
| XPML11  |      1 | 2019-10-16 00:00:00 | 2019-11-14 00:00:00 |     21 |       12.17 |         1.8  |
| HSML11  |      1 | 2019-11-05 00:00:00 | 2019-12-05 00:00:00 |     21 |        9.26 |         1.38 |
| HGCR11  |      1 | 2019-03-01 00:00:00 | 2019-04-03 00:00:00 |     21 |        9.06 |         1.34 |
| OUJP11  |      1 | 2019-06-18 00:00:00 | 2019-07-18 00:00:00 |     21 |        8.87 |         1.29 |
| BTLG11  |      1 | 2020-10-09 00:00:00 | 2020-11-11 00:00:00 |     21 |        7.92 |         1.15 |
| KISU11  |      1 | 2021-05-25 00:00:00 | 2021-06-24 00:00:00 |     21 |        7.35 |         1.09 |

**10 piores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| RBFF11  |      1 | 2020-02-21 00:00:00 | 2020-03-25 00:00:00 |     21 |      -27.66 |        -4.14 |
| PORD11  |      1 | 2020-03-05 00:00:00 | 2020-04-03 00:00:00 |     21 |      -20.02 |        -3    |
| MXRF11  |      1 | 2020-02-20 00:00:00 | 2020-03-24 00:00:00 |     21 |      -19.85 |        -2.97 |
| BCFF11  |      1 | 2020-02-12 00:00:00 | 2020-03-16 00:00:00 |     21 |      -14.06 |        -2.06 |
| HCTR11  |      1 | 2020-03-05 00:00:00 | 2020-04-03 00:00:00 |     21 |      -12.51 |        -1.82 |
| VILG11  |      1 | 2020-03-05 00:00:00 | 2020-04-03 00:00:00 |     21 |      -18.2  |        -1.69 |
| SHPH11  |      1 | 2025-02-26 00:00:00 | 2025-03-31 00:00:00 |     21 |       -9.95 |        -1.42 |
| BCIA11  |      1 | 2020-08-03 00:00:00 | 2020-09-01 00:00:00 |     21 |       -9.31 |        -1.38 |
| RZAT11  |      1 | 2024-09-17 00:00:00 | 2024-10-16 00:00:00 |     21 |       -5.67 |        -0.85 |
| BTCR11  |      1 | 2022-10-11 00:00:00 | 2022-11-11 00:00:00 |     21 |       -5.71 |        -0.84 |

**Quem trouxe o retorno (soma por ativo, pp)**

| ativo   |   sum |   count |
|:--------|------:|--------:|
| RBRF11  |  7.52 |       4 |
| XPML11  |  3.05 |       5 |
| RBRR11  |  2.5  |       4 |
| HGCR11  |  2.14 |       6 |
| HSML11  |  1.74 |       2 |
| VISC11  |  1.68 |       2 |
| UBSR11  |  1.59 |       2 |
| MGFF11  |  1.39 |       2 |
| XPLG11  |  1.32 |       3 |
| OUJP11  |  1.29 |       1 |

### FII na data-com (compra do varejo pelo rendimento)  (`bb_fii_datacom`)

**Tese:** Compro FIIs líquidos k pregões antes da data-com (último pregão do mês) e vendo no fechamento da data-com para o varejo que compra para receber o rendimento; lote de 1 cota, spread real

**Instrumentos:** [{'onde': 'Clear/Rico/XP/Inter (corretagem zero)', 'ticker': 'FIIs líquidos (XXXX11), os n maiores ADV', 'lote': '1 cota', 'custo': 'emolumentos 0,03% + meio spread real do fechamento'}]

**Aplicável:** True — FIIs líquidos, cotas de R$ 10–150, R$ 1,8 mil por FII com R$ 20 mil; 12 ciclos por ano

| métrica | valor |
|---|---|
| OOS desde | 2021-01 |
| retorno OOS a.a. (R$ 20 mil) | 9.4% vs CDI 11.4% |
| ativo OOS pp (R$ 20 mil / R$ 50 mil) | -1.99 / -1.73 |
| depois do IR (classe fii) pp, 20k / 50k | -2.00 / -1.75 |
| IR OOS / Sharpe | -0.44 / -0.44 |
| pior queda | -4.9% |
| PBO / Sharpe deflacionado | 43% / +0% |
| leque de parâmetros p5 / mediana / p95 | -5.25 / -1.63 / +0.18 |
| custo 2x / execução t+2 | -5.86 / +1.85 |
| walk-forward | +1.99 |
| sem os 10 melhores negócios | -3.33 |
| placebo p | 0.07 |
| look-ahead (truncamento) | passou |

**10 melhores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| XPML11  |      1 | 2020-03-18 00:00:00 | 2020-03-31 00:00:00 |      9 |       34.28 |         3.04 |
| VISC11  |      1 | 2020-03-18 00:00:00 | 2020-03-31 00:00:00 |      9 |       30.01 |         2.7  |
| HGBS11  |      1 | 2020-03-18 00:00:00 | 2020-03-31 00:00:00 |      9 |       26.73 |         2.26 |
| XPLG11  |      1 | 2020-03-18 00:00:00 | 2020-03-31 00:00:00 |      9 |       19.56 |         1.7  |
| HGRU11  |      1 | 2020-03-18 00:00:00 | 2020-03-31 00:00:00 |      9 |       16.16 |         1.41 |
| KNRI11  |      1 | 2020-03-18 00:00:00 | 2020-03-31 00:00:00 |      9 |       16.1  |         1.38 |
| BRCR11  |      1 | 2019-12-17 00:00:00 | 2020-01-02 00:00:00 |     10 |       15.68 |         1.37 |
| HSML11  |      1 | 2020-03-18 00:00:00 | 2020-03-31 00:00:00 |      9 |       14.35 |         1.25 |
| HGRE11  |      1 | 2019-12-17 00:00:00 | 2020-01-02 00:00:00 |     10 |       13.39 |         1.2  |
| BCFF11  |      1 | 2020-03-18 00:00:00 | 2020-03-31 00:00:00 |      9 |       12.12 |         1.05 |

**10 piores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| HCTR11  |      1 | 2023-03-20 00:00:00 | 2023-03-31 00:00:00 |      9 |      -16.31 |        -1.43 |
| CPOF11  |      1 | 2026-07-21 00:00:00 | 2026-07-31 00:00:00 |      8 |      -14.38 |        -1.23 |
| CPOF11  |      1 | 2026-03-19 00:00:00 | 2026-03-31 00:00:00 |      8 |      -12.08 |        -1.06 |
| ADSH11  |      1 | 2026-09-17 00:00:00 | 2026-09-30 00:00:00 |      9 |       -9.5  |        -0.85 |
| DEVA11  |      1 | 2023-04-14 00:00:00 | 2023-04-28 00:00:00 |      9 |       -9.21 |        -0.82 |
| CPTS11  |      1 | 2024-10-18 00:00:00 | 2024-10-31 00:00:00 |      9 |       -7.46 |        -0.67 |
| MXRF11  |      1 | 2022-01-18 00:00:00 | 2022-01-31 00:00:00 |      9 |       -7.01 |        -0.63 |
| XPML11  |      1 | 2019-03-18 00:00:00 | 2019-03-29 00:00:00 |      9 |       -6.71 |        -0.58 |
| BRCR11  |      1 | 2015-11-17 00:00:00 | 2015-11-30 00:00:00 |      9 |       -6.69 |        -0.57 |
| GGRC11  |      1 | 2019-01-18 00:00:00 | 2019-01-31 00:00:00 |      9 |       -6.68 |        -0.56 |

**Quem trouxe o retorno (soma por ativo, pp)**

| ativo   |   sum |   count |
|:--------|------:|--------:|
| KNCR11  |  7.55 |     110 |
| HGLG11  |  6.02 |      94 |
| MXRF11  |  4.58 |      76 |
| HGBS11  |  4.34 |      18 |
| XPLG11  |  3.74 |      32 |
| KNIP11  |  3.71 |      67 |
| BBPO11  |  3.45 |      63 |
| VISC11  |  3.37 |      32 |
| XPML11  |  2.95 |      66 |
| KNRI11  |  2.89 |      44 |

### Troca de controle: ON no anúncio (tag along obrigatório)  (`bb_tag_along`)

**Tese:** Compro a ON da companhia que anunciou alienação de controle (o comprador é obrigado a fazer OPA a >= 80% do preço do controle) e seguro até a OPA/prazo; lote pequeno em small cap ilíquida

**Instrumentos:** [{'onde': 'Clear/Rico/XP (corretagem zero; habilitação no leilão de OPA pela corretora)', 'ticker': 'ON da companhia-alvo', 'lote': '1 ação', 'custo': 'emolumentos 0,03% + meio spread real do fechamento + 0,2% no fracionário'}]

**Aplicável:** True — R$ 2,4 mil por evento com R$ 20 mil; alvos com ADV a partir de R$ 50 mil; 10–25 trocas de controle por ano

| métrica | valor |
|---|---|
| OOS desde | 2021-01 |
| retorno OOS a.a. (R$ 20 mil) | 2.8% vs CDI 11.4% |
| ativo OOS pp (R$ 20 mil / R$ 50 mil) | -8.61 / -8.53 |
| depois do IR (classe acoes) pp, 20k / 50k | -8.48 / -8.40 |
| IR OOS / Sharpe | -0.57 / -0.57 |
| pior queda | -20.8% |
| PBO / Sharpe deflacionado | 53% / +2% |
| leque de parâmetros p5 / mediana / p95 | -9.86 / -7.51 / -4.74 |
| custo 2x / execução t+2 | -9.98 / -8.62 |
| walk-forward | -4.87 |
| sem os 10 melhores negócios | -14.82 |
| placebo p | 0.97 |
| look-ahead (truncamento) | passou |

**10 melhores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| RNEW4   |      1 | 2022-05-09 00:00:00 | 2022-11-07 00:00:00 |    126 |       84.52 |        10.14 |
| CESP6   |      1 | 2018-10-02 00:00:00 | 2019-04-05 00:00:00 |    126 |       82.67 |         9.92 |
| PETR4   |      1 | 2016-03-22 00:00:00 | 2016-09-20 00:00:00 |    126 |       66.02 |         7.9  |
| WIZC3   |      1 | 2025-01-08 00:00:00 | 2025-07-11 00:00:00 |    126 |       48.61 |         5.82 |
| DMMO3   |      1 | 2022-01-31 00:00:00 | 2022-08-02 00:00:00 |    126 |       46.21 |         5.55 |
| PETR4   |      1 | 2018-07-04 00:00:00 | 2019-01-04 00:00:00 |    126 |       39.04 |         4.68 |
| ELET3   |      1 | 2018-10-31 00:00:00 | 2019-05-07 00:00:00 |    126 |       37.75 |         4.52 |
| ENGI11  |      1 | 2018-10-01 00:00:00 | 2019-04-04 00:00:00 |    126 |       36.15 |         4.34 |
| CLSC4   |      1 | 2025-02-17 00:00:00 | 2025-08-20 00:00:00 |    126 |       24.71 |         2.91 |
| ALPA4   |      1 | 2015-11-24 00:00:00 | 2016-05-27 00:00:00 |    126 |       23.54 |         2.82 |

**10 piores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| AALR3   |      1 | 2023-07-13 00:00:00 | 2024-01-15 00:00:00 |    126 |      -62.74 |        -7.48 |
| CASH3   |      1 | 2022-04-01 00:00:00 | 2022-09-30 00:00:00 |    126 |      -60.06 |        -7.21 |
| AZEV4   |      1 | 2025-09-24 00:00:00 | 2026-03-26 00:00:00 |    126 |      -58.6  |        -7.03 |
| GFSA3   |      1 | 2019-01-23 00:00:00 | 2019-07-25 00:00:00 |    126 |      -58.71 |        -7.01 |
| BAHI3   |      1 | 2019-10-23 00:00:00 | 2020-04-27 00:00:00 |    126 |      -47.16 |        -5.45 |
| EMAE4   |      1 | 2024-03-18 00:00:00 | 2024-09-13 00:00:00 |    126 |      -39.06 |        -4.64 |
| CASH3   |      1 | 2023-10-24 00:00:00 | 2024-04-26 00:00:00 |    126 |      -33.65 |        -4.03 |
| MLAS3   |      1 | 2022-12-01 00:00:00 | 2023-06-02 00:00:00 |    126 |      -32.51 |        -3.9  |
| EMAE4   |      1 | 2026-01-21 00:00:00 | 2026-07-24 00:00:00 |    126 |      -26.16 |        -3.11 |
| GGPS3   |      1 | 2024-09-24 00:00:00 | 2025-03-27 00:00:00 |    126 |      -25.83 |        -3.1  |

**Quem trouxe o retorno (soma por ativo, pp)**

| ativo   |   sum |   count |
|:--------|------:|--------:|
| PETR4   | 12.3  |       3 |
| RNEW4   | 10.14 |       1 |
| CESP6   |  7.53 |       2 |
| WIZC3   |  5.82 |       1 |
| DMMO3   |  5.55 |       1 |
| COCE5   |  4.82 |       2 |
| ALPA4   |  4.76 |       2 |
| ENGI11  |  4.34 |       1 |
| ELET3   |  4.2  |       2 |
| CLSC4   |  2.91 |       1 |

### Dividendo/JCP extraordinário anunciado (até a data-com)  (`bb_dividendo_extra`)

**Tese:** Compro a ação no dia seguinte à aprovação de um provento extraordinário (>= limiar do preço) e vendo na data-com para o investidor de renda que compra para estar na base; lote pequeno

**Instrumentos:** [{'onde': 'Clear/Rico/XP (corretagem zero)', 'ticker': 'pagadoras de provento extraordinário (103 companhias)', 'lote': '1 ação', 'custo': 'emolumentos 0,03% + meio spread real do fechamento + 0,2% no fracionário'}]

**Aplicável:** True — blue chips/elétricas; R$ 4 mil por evento com R$ 20 mil

| métrica | valor |
|---|---|
| OOS desde | 2021-01 |
| retorno OOS a.a. (R$ 20 mil) | 22.4% vs CDI 11.4% |
| ativo OOS pp (R$ 20 mil / R$ 50 mil) | +10.94 / +12.33 |
| depois do IR (classe acoes) pp, 20k / 50k | +9.76 / +10.29 |
| IR OOS / Sharpe | +1.04 / +1.04 |
| pior queda | -8.0% |
| PBO / Sharpe deflacionado | 2% / +69% |
| leque de parâmetros p5 / mediana / p95 | +7.94 / +13.13 / +16.21 |
| custo 2x / execução t+2 | +5.60 / +9.36 |
| walk-forward | +15.48 |
| sem os 10 melhores negócios | +5.34 |
| placebo p | 0.00 |
| look-ahead (truncamento) | passou |

**10 melhores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| ALPA3   |      1 | 2015-08-13 00:00:00 | 2015-12-08 00:00:00 |     80 |       44.22 |         8.84 |
| MRVE3   |      1 | 2019-04-29 00:00:00 | 2019-12-10 00:00:00 |    158 |       38.19 |         7.63 |
| MRVE3   |      1 | 2020-04-20 00:00:00 | 2020-10-13 00:00:00 |    121 |       29.93 |         5.97 |
| BRAP3   |      1 | 2021-11-09 00:00:00 | 2021-12-16 00:00:00 |     26 |       23.36 |         4.66 |
| BRAP4   |      1 | 2021-11-09 00:00:00 | 2021-12-16 00:00:00 |     26 |       21.24 |         4.23 |
| PETR4   |      1 | 2023-05-15 00:00:00 | 2023-06-12 00:00:00 |     19 |       19.77 |         3.93 |
| BRAP3   |      1 | 2023-11-01 00:00:00 | 2023-11-21 00:00:00 |     12 |       15.11 |         3.02 |
| VALE3   |      1 | 2023-10-27 00:00:00 | 2023-11-21 00:00:00 |     15 |       14.76 |         2.94 |
| BRAP4   |      1 | 2023-11-01 00:00:00 | 2023-11-21 00:00:00 |     12 |       14.37 |         2.87 |
| PETR3   |      1 | 2023-05-12 00:00:00 | 2023-06-12 00:00:00 |     20 |       17.04 |         2.81 |

**10 piores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| MRVE3   |      1 | 2018-04-23 00:00:00 | 2018-12-13 00:00:00 |    162 |      -16.18 |        -3.22 |
| VIVT3   |      1 | 2026-03-16 00:00:00 | 2026-05-22 00:00:00 |     46 |      -14.5  |        -2.88 |
| BBSE3   |      1 | 2021-06-23 00:00:00 | 2021-08-11 00:00:00 |     35 |      -12.49 |        -2.48 |
| QUAL3   |      1 | 2016-11-08 00:00:00 | 2016-11-11 00:00:00 |      3 |      -10.89 |        -2.18 |
| GGBR4   |      1 | 2021-10-28 00:00:00 | 2021-11-05 00:00:00 |      5 |      -10.79 |        -2.14 |
| ENGI3   |      1 | 2021-12-22 00:00:00 | 2021-12-30 00:00:00 |      6 |      -10.41 |        -2.08 |
| SANB3   |      1 | 2019-01-02 00:00:00 | 2019-01-07 00:00:00 |      3 |      -10.23 |        -2.04 |
| PETR3   |      1 | 2024-05-14 00:00:00 | 2024-06-11 00:00:00 |     19 |       -9.05 |        -1.81 |
| GGBR3   |      1 | 2021-10-28 00:00:00 | 2021-11-05 00:00:00 |      5 |       -8.41 |        -1.68 |
| PETR4   |      1 | 2024-05-14 00:00:00 | 2024-06-11 00:00:00 |     19 |       -8.32 |        -1.65 |

**Quem trouxe o retorno (soma por ativo, pp)**

| ativo   |   sum |   count |
|:--------|------:|--------:|
| MRVE3   | 10.56 |       4 |
| ALPA3   |  9.21 |       2 |
| BRAP4   |  8.42 |       6 |
| BRAP3   |  8.11 |       6 |
| SAPR4   |  6.5  |      17 |
| BBSE3   |  6.18 |      19 |
| CPLE6   |  5.6  |       9 |
| PETR3   |  5.49 |      11 |
| PETR4   |  5.42 |      13 |
| CPLE3   |  5.39 |      10 |

### Insiders comprando small caps (VLMO, lote pequeno)  (`bb_insider_small`)

**Tese:** Compro a small cap (ADV < R$ 2 mi) em que controlador/administradores fizeram compra líquida relevante no mês (formulário VLMO entregue à CVM) e seguro hold pregões; o institucional não escala nesse tamanho

**Instrumentos:** [{'onde': 'Clear/Rico/XP (corretagem zero)', 'ticker': 'small caps com compra de insider', 'lote': '1 ação', 'custo': 'emolumentos 0,03% + meio spread real do fechamento + 0,2% no fracionário'}]

**Aplicável:** True — small caps com ADV R$ 50 mil–2 mi; R$ 2 mil por papel com R$ 20 mil

| métrica | valor |
|---|---|
| OOS desde | 2023-01 |
| retorno OOS a.a. (R$ 20 mil) | 11.5% vs CDI 13.1% |
| ativo OOS pp (R$ 20 mil / R$ 50 mil) | -1.60 / -2.22 |
| depois do IR (classe acoes) pp, 20k / 50k | -1.58 / -2.19 |
| IR OOS / Sharpe | +0.02 / +0.02 |
| pior queda | -17.9% |
| PBO / Sharpe deflacionado | 15% / +8% |
| leque de parâmetros p5 / mediana / p95 | -12.32 / -5.98 / +3.13 |
| custo 2x / execução t+2 | -3.99 / -2.83 |
| walk-forward | -1.60 |
| sem os 10 melhores negócios | -11.29 |
| placebo p | 0.19 |
| look-ahead (truncamento) | passou |

**10 melhores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| MNPR3   |      1 | 2022-07-04 00:00:00 | 2024-10-07 00:00:00 |    569 |      174.5  |        17.43 |
| TECN3   |      1 | 2020-11-10 00:00:00 | 2021-09-09 00:00:00 |    209 |      189.1  |        14.31 |
| RDNI3   |      1 | 2019-02-11 00:00:00 | 2019-12-09 00:00:00 |    209 |      127.45 |        12.74 |
| ESPA3   |      1 | 2025-01-13 00:00:00 | 2025-07-16 00:00:00 |    126 |       66.46 |         6.54 |
| TESA3   |      1 | 2020-08-11 00:00:00 | 2021-02-10 00:00:00 |    126 |       59.12 |         5.88 |
| TESA3   |      1 | 2021-03-10 00:00:00 | 2021-09-13 00:00:00 |    129 |       57.4  |         5.66 |
| MOAR3   |      1 | 2021-04-13 00:00:00 | 2021-10-11 00:00:00 |    126 |       53.36 |         5.04 |
| BIOM3   |      1 | 2023-09-13 00:00:00 | 2025-03-10 00:00:00 |    372 |       86.31 |         4.59 |
| BRIT3   |      1 | 2023-03-10 00:00:00 | 2023-10-09 00:00:00 |    146 |       45.08 |         4.5  |
| FRTA3   |      1 | 2019-01-14 00:00:00 | 2019-07-15 00:00:00 |    125 |       43.21 |         4.32 |

**10 piores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| LLIS3   |      1 | 2020-01-14 00:00:00 | 2020-07-16 00:00:00 |    126 |      -72.28 |        -7.22 |
| AGXY3   |      1 | 2023-04-06 00:00:00 | 2024-02-08 00:00:00 |    210 |      -70.85 |        -7.06 |
| ATMP3   |      1 | 2021-12-10 00:00:00 | 2022-06-10 00:00:00 |    126 |      -69.04 |        -6.89 |
| ATOM3   |      1 | 2021-09-15 00:00:00 | 2023-01-10 00:00:00 |    332 |      -61.6  |        -6.16 |
| DOTZ3   |      1 | 2021-10-11 00:00:00 | 2022-04-12 00:00:00 |    126 |      -54.86 |        -5.48 |
| TCSA3   |      1 | 2026-03-11 00:00:00 | 2026-10-07 00:00:00 |    145 |      -56.04 |        -5.02 |
| PINE4   |      1 | 2022-01-11 00:00:00 | 2022-07-13 00:00:00 |    126 |      -39.78 |        -3.93 |
| SLED4   |      1 | 2019-07-11 00:00:00 | 2020-01-08 00:00:00 |    126 |      -39.13 |        -3.91 |
| BMEB4   |      1 | 2020-07-20 00:00:00 | 2022-09-09 00:00:00 |    539 |      -27.7  |        -2.76 |
| PRNR3   |      1 | 2021-12-08 00:00:00 | 2022-07-11 00:00:00 |    148 |      -25.78 |        -2.57 |

**Quem trouxe o retorno (soma por ativo, pp)**

| ativo   |   sum |   count |
|:--------|------:|--------:|
| MNPR3   | 21.57 |       2 |
| TECN3   | 19.68 |       4 |
| RDNI3   | 12.74 |       1 |
| TESA3   | 11.48 |       3 |
| ESPA3   |  7.73 |       2 |
| MOAR3   |  7.44 |       3 |
| FRTA3   |  5.92 |       2 |
| BRIT3   |  4.5  |       1 |
| PLPL3   |  3.61 |       1 |
| LPSB3   |  3.17 |       2 |

### Insiders comprando small caps (VLMO, lote pequeno) — AUDITADA (leitura normalizada do VLMO)  (`bb_insider_small_aud`)

**Tese:** Compro a small cap (ADV < R$ 2 mi) em que controlador/administradores fizeram compra líquida relevante no mês (formulário VLMO entregue à CVM) e seguro hold pregões; o institucional não escala nesse tamanho

**Instrumentos:** [{'onde': 'Clear/Rico/XP (corretagem zero)', 'ticker': 'small caps com compra de insider', 'lote': '1 ação', 'custo': 'emolumentos 0,03% + meio spread real do fechamento + 0,2% no fracionário'}]

**Aplicável:** True — small caps com ADV R$ 50 mil–2 mi; R$ 2 mil por papel com R$ 20 mil

| métrica | valor |
|---|---|
| OOS desde | 2023-01 |
| retorno OOS a.a. (R$ 20 mil) | 11.5% vs CDI 13.1% |
| ativo OOS pp (R$ 20 mil / R$ 50 mil) | -1.60 / -2.22 |
| depois do IR (classe exterior) pp, 20k / 50k | -1.58 / -2.19 |
| IR OOS / Sharpe | +0.02 / +0.02 |
| pior queda | -17.9% |
| PBO / Sharpe deflacionado | 15% / +8% |
| leque de parâmetros p5 / mediana / p95 | -12.32 / -5.98 / +3.13 |
| custo 2x / execução t+2 | -3.99 / -2.83 |
| walk-forward | -1.60 |
| sem os 10 melhores negócios | -11.29 |
| placebo p | 0.19 |
| look-ahead (truncamento) | passou |

**10 melhores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| MNPR3   |      1 | 2022-07-04 00:00:00 | 2024-10-07 00:00:00 |    569 |      174.5  |        17.43 |
| TECN3   |      1 | 2020-11-10 00:00:00 | 2021-09-09 00:00:00 |    209 |      189.1  |        14.31 |
| RDNI3   |      1 | 2019-02-11 00:00:00 | 2019-12-09 00:00:00 |    209 |      127.45 |        12.74 |
| ESPA3   |      1 | 2025-01-13 00:00:00 | 2025-07-16 00:00:00 |    126 |       66.46 |         6.54 |
| TESA3   |      1 | 2020-08-11 00:00:00 | 2021-02-10 00:00:00 |    126 |       59.12 |         5.88 |
| TESA3   |      1 | 2021-03-10 00:00:00 | 2021-09-13 00:00:00 |    129 |       57.4  |         5.66 |
| MOAR3   |      1 | 2021-04-13 00:00:00 | 2021-10-11 00:00:00 |    126 |       53.36 |         5.04 |
| BIOM3   |      1 | 2023-09-13 00:00:00 | 2025-03-10 00:00:00 |    372 |       86.31 |         4.59 |
| BRIT3   |      1 | 2023-03-10 00:00:00 | 2023-10-09 00:00:00 |    146 |       45.08 |         4.5  |
| FRTA3   |      1 | 2019-01-14 00:00:00 | 2019-07-15 00:00:00 |    125 |       43.21 |         4.32 |

**10 piores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| LLIS3   |      1 | 2020-01-14 00:00:00 | 2020-07-16 00:00:00 |    126 |      -72.28 |        -7.22 |
| AGXY3   |      1 | 2023-04-06 00:00:00 | 2024-02-08 00:00:00 |    210 |      -70.85 |        -7.06 |
| ATMP3   |      1 | 2021-12-10 00:00:00 | 2022-06-10 00:00:00 |    126 |      -69.04 |        -6.89 |
| ATOM3   |      1 | 2021-09-15 00:00:00 | 2023-01-10 00:00:00 |    332 |      -61.6  |        -6.16 |
| DOTZ3   |      1 | 2021-10-11 00:00:00 | 2022-04-12 00:00:00 |    126 |      -54.86 |        -5.48 |
| TCSA3   |      1 | 2026-03-11 00:00:00 | 2026-10-07 00:00:00 |    145 |      -56.04 |        -5.02 |
| PINE4   |      1 | 2022-01-11 00:00:00 | 2022-07-13 00:00:00 |    126 |      -39.78 |        -3.93 |
| SLED4   |      1 | 2019-07-11 00:00:00 | 2020-01-08 00:00:00 |    126 |      -39.13 |        -3.91 |
| BMEB4   |      1 | 2020-07-20 00:00:00 | 2022-09-09 00:00:00 |    539 |      -27.7  |        -2.76 |
| PRNR3   |      1 | 2021-12-08 00:00:00 | 2022-07-11 00:00:00 |    148 |      -25.78 |        -2.57 |

**Quem trouxe o retorno (soma por ativo, pp)**

| ativo   |   sum |   count |
|:--------|------:|--------:|
| MNPR3   | 21.57 |       2 |
| TECN3   | 19.68 |       4 |
| RDNI3   | 12.74 |       1 |
| TESA3   | 11.48 |       3 |
| ESPA3   |  7.73 |       2 |
| MOAR3   |  7.44 |       3 |
| FRTA3   |  5.92 |       2 |
| BRIT3   |  4.5  |       1 |
| PLPL3   |  3.61 |       1 |
| LPSB3   |  3.17 |       2 |
