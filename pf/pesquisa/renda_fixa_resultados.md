# Frente renda_fixa — resultados da bateria final (gerado automaticamente)

Gerado por `pf/gerar_cadernos.py` a partir de `pf/resultados/bateria/`. IR de pessoa física por `pf/ir.py` (mensal na B3 com isenção de ações ≤ R$ 20 mil/mês, anual no exterior). Ordem: nota do ranking.

### Tesouro IPCA+ de valor (Tesouro Direto)  (`rf_ipca_valor`)

**Tese:** Compro Tesouro IPCA+ longo quando o juro real passa de ~6,5% (prêmio fiscal) e vendo de volta ao Tesouro quando a taxa fecha; recompra diária garantida e títulos de R$ 30 são vantagem do varejo

**Instrumentos:** [{'onde': 'Tesouro Direto (qualquer corretora; XP/Rico/Clear/Inter/Nubank sem taxa)', 'ticker': 'Tesouro IPCA+ 20XX (NTN-B principal)', 'lote': '0,01 título (~R$ 20–40); mínimo R$ 30', 'custo': 'spread compra/recompra 0,12 pp de taxa (≈ duration x 0,12%); custódia B3 0,20% a.a.'}]

**Aplicável:** True — Tesouro Direto aceita R$ 30 e recompra todo dia útil; o capital inteiro cabe em um título.

| métrica | valor |
|---|---|
| OOS desde | 2021-01 |
| retorno OOS a.a. (R$ 20 mil) | 10.2% vs CDI 11.4% |
| ativo OOS pp (R$ 20 mil / R$ 50 mil) | -1.28 / -1.28 |
| depois do IR (classe renda_fixa) pp, 20k / 50k | -1.26 / -1.26 |
| IR OOS / Sharpe | -0.04 / -0.04 |
| pior queda | -16.2% |
| PBO / Sharpe deflacionado | 50% / +27% |
| leque de parâmetros p5 / mediana / p95 | -3.43 / -1.25 / +0.50 |
| custo 2x / execução t+2 | -1.81 / -1.38 |
| walk-forward | -1.28 |
| sem os 10 melhores negócios | -0.94 |
| placebo p | 0.10 |
| look-ahead (truncamento) | passou |

**10 melhores negócios**

| ativo     |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:----------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| IPCA+2035 |      1 | 2014-01-27 00:00:00 | 2014-08-29 00:00:00 |    149 |       38.67 |        31.96 |
| IPCA+2035 |      1 | 2015-08-10 00:00:00 | 2016-08-15 00:00:00 |    256 |       40.6  |        26.54 |
| IPCA+2024 |      1 | 2008-03-18 00:00:00 | 2010-11-12 00:00:00 |    669 |       50.2  |        21.42 |
| IPCA+2045 |      1 | 2024-12-02 00:00:00 | 2026-10-13 00:00:00 |    468 |       20.64 |        -1.96 |

**10 piores negócios**

| ativo     |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:----------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| IPCA+2045 |      1 | 2024-12-02 00:00:00 | 2026-10-13 00:00:00 |    468 |       20.64 |        -1.96 |
| IPCA+2024 |      1 | 2008-03-18 00:00:00 | 2010-11-12 00:00:00 |    669 |       50.2  |        21.42 |
| IPCA+2035 |      1 | 2015-08-10 00:00:00 | 2016-08-15 00:00:00 |    256 |       40.6  |        26.54 |
| IPCA+2035 |      1 | 2014-01-27 00:00:00 | 2014-08-29 00:00:00 |    149 |       38.67 |        31.96 |

**Quem trouxe o retorno (soma por ativo, pp)**

| ativo     |   sum |   count |
|:----------|------:|--------:|
| IPCA+2035 | 58.51 |       2 |
| IPCA+2024 | 21.42 |       1 |
| IPCA+2045 | -1.96 |       1 |

### FI-Infra/FII de papel com desconto ao VP (pânico de varejo)  (`rf_fii_infra`)

**Tese:** Compro FI-Infra listado (isento total para PF) quando a cota negocia com desconto grande ao VP marcado a mercado e vendo quando o desconto fecha; FII de papel como variante

**Instrumentos:** [{'onde': 'qualquer corretora B3 (Clear/Rico/XP/Inter/Nubank, corretagem zero)', 'ticker': 'JURO11, KDIF11, CPTI11, BDIF11, IFRA11, BIDB11, BODB11, CDII11, SNID11, IFRI11 (FI-Infra); FIIs de papel (KNCR11, MXRF11...) na variante', 'lote': '1 cota (~R$ 8–130)', 'custo': 'emolumentos 0,03% + meio spread (0,1–0,5%)'}]

**Aplicável:** True — Cotas de R$ 8–130 na B3 com corretagem zero; 3 fundos de ~R$ 6,7 mil com R$ 20 mil.

| métrica | valor |
|---|---|
| OOS desde | 2024-01 |
| retorno OOS a.a. (R$ 20 mil) | 10.5% vs CDI 13.1% |
| ativo OOS pp (R$ 20 mil / R$ 50 mil) | -2.55 / -2.55 |
| depois do IR (classe isento) pp, 20k / 50k | -2.51 / -2.51 |
| IR OOS / Sharpe | -0.23 / -0.23 |
| pior queda | -15.8% |
| PBO / Sharpe deflacionado | 0% / +0% |
| leque de parâmetros p5 / mediana / p95 | -3.60 / -1.86 / +0.95 |
| custo 2x / execução t+2 | -2.73 / -3.15 |
| walk-forward | -2.48 |
| sem os 10 melhores negócios | -0.78 |
| placebo p | 0.82 |
| look-ahead (truncamento) | passou |

**10 melhores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| IFRA11  |      1 | 2023-03-20 00:00:00 | 2023-05-26 00:00:00 |     47 |       10.95 |         2.85 |
| BDIF11  |      1 | 2021-11-03 00:00:00 | 2022-06-17 00:00:00 |    157 |       12.51 |         2.09 |
| CPTI11  |      1 | 2023-04-18 00:00:00 | 2023-07-03 00:00:00 |     52 |        8.93 |         2.07 |
| BDIF11  |      1 | 2023-01-19 00:00:00 | 2023-06-12 00:00:00 |     97 |        9.43 |         1.53 |
| BIDB11  |      1 | 2024-01-05 00:00:00 | 2024-01-17 00:00:00 |      9 |        3.47 |         1.04 |
| BDIF11  |      1 | 2021-08-18 00:00:00 | 2021-10-25 00:00:00 |     47 |        3.81 |         0.93 |
| IFRA11  |      1 | 2021-11-19 00:00:00 | 2022-01-03 00:00:00 |     32 |        3.09 |         0.69 |
| CPTI11  |      1 | 2021-12-10 00:00:00 | 2022-01-03 00:00:00 |     17 |        1.93 |         0.46 |
| BIDB11  |      1 | 2022-12-06 00:00:00 | 2023-02-01 00:00:00 |     42 |        2.98 |         0.29 |
| BDIF11  |      1 | 2021-07-02 00:00:00 | 2021-08-13 00:00:00 |     31 |        1.31 |         0.26 |

**10 piores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| BDIF11  |      1 | 2024-08-02 00:00:00 | 2026-10-13 00:00:00 |    552 |       16.12 |        -3.15 |
| BIDB11  |      1 | 2022-05-18 00:00:00 | 2022-11-10 00:00:00 |    123 |        0.82 |        -1.65 |
| CPTI11  |      1 | 2024-10-10 00:00:00 | 2026-06-10 00:00:00 |    416 |       16.35 |        -1.27 |
| BODB11  |      1 | 2024-10-03 00:00:00 | 2026-07-01 00:00:00 |    436 |       18.35 |        -0.89 |
| CPTI11  |      1 | 2026-07-01 00:00:00 | 2026-10-13 00:00:00 |     73 |        2.02 |        -0.55 |
| BODB11  |      1 | 2022-10-05 00:00:00 | 2022-12-27 00:00:00 |     57 |        1.15 |        -0.55 |
| BODB11  |      1 | 2026-07-13 00:00:00 | 2026-10-13 00:00:00 |     65 |        2.92 |        -0.1  |
| BDIF11  |      1 | 2021-07-02 00:00:00 | 2021-08-13 00:00:00 |     31 |        1.31 |         0.26 |
| BIDB11  |      1 | 2022-12-06 00:00:00 | 2023-02-01 00:00:00 |     42 |        2.98 |         0.29 |
| CPTI11  |      1 | 2021-12-10 00:00:00 | 2022-01-03 00:00:00 |     17 |        1.93 |         0.46 |

**Quem trouxe o retorno (soma por ativo, pp)**

| ativo   |   sum |   count |
|:--------|------:|--------:|
| IFRA11  |  3.54 |       2 |
| BDIF11  |  1.66 |       5 |
| CPTI11  |  0.7  |       4 |
| BIDB11  | -0.33 |       3 |
| BODB11  | -1.53 |       3 |

### Tesouro Prefixado x Focus (Tesouro Direto)  (`rf_pre_focus`)

**Tese:** Compro Tesouro Prefixado de 1,5–3 anos quando a taxa paga muito mais que a Selic esperada pelo Focus (prêmio de risco em pânico) e vendo de volta ao Tesouro quando o prêmio some; não entro quando o Focus revisa a Selic para cima

**Instrumentos:** [{'onde': 'Tesouro Direto', 'ticker': 'Tesouro Prefixado 20XX (LTN)', 'lote': '0,01 título (~R$ 7–9); mínimo R$ 30', 'custo': 'spread compra/recompra 0,12 pp de taxa (≈ 0,2–0,35% do PU); custódia B3 0,20% a.a.'}]

**Aplicável:** True — Tesouro Direto aceita R$ 30 e recompra todo dia útil.

| métrica | valor |
|---|---|
| OOS desde | 2021-01 |
| retorno OOS a.a. (R$ 20 mil) | 9.7% vs CDI 11.4% |
| ativo OOS pp (R$ 20 mil / R$ 50 mil) | -1.75 / -1.75 |
| depois do IR (classe renda_fixa) pp, 20k / 50k | -1.73 / -1.73 |
| IR OOS / Sharpe | -0.35 / -0.35 |
| pior queda | -5.7% |
| PBO / Sharpe deflacionado | 18% / +2% |
| leque de parâmetros p5 / mediana / p95 | -4.10 / -2.33 / -1.72 |
| custo 2x / execução t+2 | -2.18 / -1.68 |
| walk-forward | -1.75 |
| sem os 10 melhores negócios | -1.79 |
| placebo p | 0.00 |
| look-ahead (truncamento) | passou |

**10 melhores negócios**

| ativo      |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:-----------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| PRE2021-01 |      1 | 2018-07-06 00:00:00 | 2019-07-11 00:00:00 |    254 |       14.28 |         7.8  |
| PRE2015-01 |      1 | 2011-09-16 00:00:00 | 2012-05-08 00:00:00 |    161 |       13.38 |         6.86 |
| PRE2019-01 |      1 | 2016-11-14 00:00:00 | 2018-07-06 00:00:00 |    412 |       21.85 |         6.75 |
| PRE2023-01 |      1 | 2019-08-28 00:00:00 | 2020-03-05 00:00:00 |    132 |        8.01 |         5.47 |
| PRE2026-01 |      1 | 2022-07-06 00:00:00 | 2023-06-07 00:00:00 |    232 |       16.29 |         4.45 |
| PRE2011-01 |      1 | 2009-02-16 00:00:00 | 2010-07-06 00:00:00 |    346 |       15.09 |         2.57 |
| PRE2013-01 |      1 | 2010-07-06 00:00:00 | 2011-08-31 00:00:00 |    293 |       14.07 |         1.67 |
| PRE2010-01 |      1 | 2008-01-04 00:00:00 | 2009-01-08 00:00:00 |    257 |       12.32 |         0.65 |
| PRE2029-01 |      1 | 2025-07-08 00:00:00 | 2026-10-13 00:00:00 |    320 |       16.9  |        -0.12 |
| PRE2018-01 |      1 | 2015-07-07 00:00:00 | 2016-09-26 00:00:00 |    309 |       15.32 |        -0.44 |

**10 piores negócios**

| ativo      |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:-----------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| PRE2026-01 |      1 | 2023-09-27 00:00:00 | 2025-07-08 00:00:00 |    445 |       15.34 |        -4.11 |
| PRE2016-01 |      1 | 2012-07-06 00:00:00 | 2015-07-07 00:00:00 |    755 |       23.4  |        -3.72 |
| PRE2023-01 |      1 | 2020-03-13 00:00:00 | 2022-07-06 00:00:00 |    581 |       10.09 |        -1.73 |
| PRE2018-01 |      1 | 2015-07-07 00:00:00 | 2016-09-26 00:00:00 |    309 |       15.32 |        -0.44 |
| PRE2029-01 |      1 | 2025-07-08 00:00:00 | 2026-10-13 00:00:00 |    320 |       16.9  |        -0.12 |
| PRE2010-01 |      1 | 2008-01-04 00:00:00 | 2009-01-08 00:00:00 |    257 |       12.32 |         0.65 |
| PRE2013-01 |      1 | 2010-07-06 00:00:00 | 2011-08-31 00:00:00 |    293 |       14.07 |         1.67 |
| PRE2011-01 |      1 | 2009-02-16 00:00:00 | 2010-07-06 00:00:00 |    346 |       15.09 |         2.57 |
| PRE2026-01 |      1 | 2022-07-06 00:00:00 | 2023-06-07 00:00:00 |    232 |       16.29 |         4.45 |
| PRE2023-01 |      1 | 2019-08-28 00:00:00 | 2020-03-05 00:00:00 |    132 |        8.01 |         5.47 |

**Quem trouxe o retorno (soma por ativo, pp)**

| ativo      |   sum |   count |
|:-----------|------:|--------:|
| PRE2021-01 |  7.8  |       1 |
| PRE2015-01 |  6.86 |       1 |
| PRE2019-01 |  6.75 |       1 |
| PRE2023-01 |  3.74 |       2 |
| PRE2011-01 |  2.57 |       1 |
| PRE2013-01 |  1.67 |       1 |
| PRE2010-01 |  0.65 |       1 |
| PRE2026-01 |  0.34 |       2 |
| PRE2029-01 | -0.12 |       1 |
| PRE2018-01 | -0.44 |       1 |

### DI1 x Focus reunião a reunião (Copom de varejo)  (`rf_di_copom`)

**Tese:** Recebo DI1 de 6–12 meses quando a curva curta precifica Selic bem acima do caminho do Focus reunião a reunião (prêmio de risco) e saio quando o prêmio fecha; contratos inteiros, margem em Tesouro Selic

**Instrumentos:** [{'onde': 'XP / BTG / Genial / Safra (DI1 para PF; Clear/Rico não oferecem)', 'ticker': 'DI1F27, DI1N27... (contrato mais perto de 6–12 meses)', 'lote': '1 contrato = R$ 100 mil no vencimento (DV01 ~R$ 4,5–8/bp)', 'custo': 'B3 ~R$ 1,10 + corretagem R$ 0–16 + meio tick por contrato e lado; margem ~1,5% do PU em Tesouro Selic'}]

**Aplicável:** True — Opera com 1–3 contratos com R$ 20 mil (3–7 com R$ 50 mil); exige corretora que libere DI1 para PF (XP, BTG, Genial) — Clear/Rico/Nubank/Inter não oferecem.

| métrica | valor |
|---|---|
| OOS desde | 2023-01 |
| retorno OOS a.a. (R$ 20 mil) | 11.9% vs CDI 13.1% |
| ativo OOS pp (R$ 20 mil / R$ 50 mil) | -1.23 / -1.14 |
| depois do IR (classe futuros_b3) pp, 20k / 50k | -1.21 / -1.12 |
| IR OOS / Sharpe | -0.47 / -0.47 |
| pior queda | -2.9% |
| PBO / Sharpe deflacionado | 70% / +0% |
| leque de parâmetros p5 / mediana / p95 | -2.50 / -1.29 / -0.25 |
| custo 2x / execução t+2 | -1.80 / -1.62 |
| walk-forward | -1.23 |
| sem os 10 melhores negócios | -0.30 |
| placebo p | 0.95 |
| look-ahead (truncamento) | passou |

**10 melhores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| DI1U20  |     -1 | 2020-03-04 00:00:00 | 2020-03-12 00:00:00 |      7 |        3.37 |         3.37 |
| DI1X20  |     -1 | 2020-04-23 00:00:00 | 2020-04-27 00:00:00 |      3 |        2.18 |         2.18 |
| DI1U20  |      1 | 2020-03-13 00:00:00 | 2020-03-16 00:00:00 |      2 |        1.56 |         1.56 |
| DI1V25  |      1 | 2025-03-26 00:00:00 | 2025-04-04 00:00:00 |      8 |        1.37 |         1.37 |
| DI1Z20  |      1 | 2020-05-19 00:00:00 | 2020-06-03 00:00:00 |     12 |        1.19 |         1.19 |
| DI1M22  |      1 | 2021-11-30 00:00:00 | 2021-12-14 00:00:00 |     11 |        1.1  |         1.1  |
| DI1N25  |      1 | 2025-01-03 00:00:00 | 2025-02-12 00:00:00 |     29 |        1.08 |         1.08 |
| DI1F23  |      1 | 2022-07-12 00:00:00 | 2022-08-15 00:00:00 |     25 |        1.04 |         1.04 |
| DI1J21  |      1 | 2020-09-21 00:00:00 | 2021-01-04 00:00:00 |     72 |        1.02 |         1.02 |
| DI1H20  |      1 | 2019-08-28 00:00:00 | 2019-09-18 00:00:00 |     16 |        0.92 |         0.92 |

**10 piores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| DI1H22  |      1 | 2021-09-01 00:00:00 | 2021-11-30 00:00:00 |     61 |       -2.96 |        -2.96 |
| DI1N21  |      1 | 2021-01-05 00:00:00 | 2021-04-01 00:00:00 |     61 |       -2.77 |        -2.77 |
| DI1J25  |      1 | 2024-10-02 00:00:00 | 2025-01-02 00:00:00 |     63 |       -2.54 |        -2.54 |
| DI1V24  |      1 | 2024-03-19 00:00:00 | 2024-07-02 00:00:00 |     73 |       -2.16 |        -2.16 |
| DI1U26  |      1 | 2026-03-09 00:00:00 | 2026-06-02 00:00:00 |     59 |       -1.74 |        -1.74 |
| DI1Z21  |      1 | 2021-06-17 00:00:00 | 2021-09-01 00:00:00 |     55 |       -0.9  |        -0.9  |
| DI1G24  |     -1 | 2023-07-27 00:00:00 | 2023-08-08 00:00:00 |      9 |       -0.41 |        -0.41 |
| DI1Z25  |      1 | 2025-06-06 00:00:00 | 2025-06-24 00:00:00 |     12 |       -0.28 |        -0.28 |
| DI1G20  |     -1 | 2019-07-24 00:00:00 | 2019-08-06 00:00:00 |     10 |       -0.2  |        -0.2  |
| DI1N22  |      1 | 2021-12-17 00:00:00 | 2022-03-29 00:00:00 |     71 |       -0.09 |        -0.09 |

**Quem trouxe o retorno (soma por ativo, pp)**

| ativo   |   sum |   count |
|:--------|------:|--------:|
| DI1U20  |  4.93 |       2 |
| DI1X20  |  2.18 |       1 |
| DI1V25  |  1.37 |       1 |
| DI1Z20  |  1.19 |       1 |
| DI1M22  |  1.1  |       1 |
| DI1N25  |  1.08 |       1 |
| DI1F23  |  1.04 |       1 |
| DI1J21  |  1.02 |       1 |
| DI1H20  |  0.92 |       1 |
| DI1K23  |  0.81 |       1 |

### Debêntures incentivadas isentas (carry de varejo)  (`rf_incentivadas`)

**Tese:** Carrego até o vencimento as incentivadas IPCA+ de maior spread sobre a NTN-B (isentas para PF), sem faca caindo e só quando a isenção não está 'careca'

**Instrumentos:** [{'onde': 'XP / BTG / Inter / Rico / Nubank (prateleira de debêntures, secundário)', 'ticker': 'debêntures incentivadas IPCA+ (ex.: CMGDB1, TAEE17)', 'lote': '1 debênture (~R$ 1–1,5 mil)', 'custo': 'sem taxa explícita; spread embutido ~1,6% do PU na compra e ~1,6% na venda antecipada'}]

**Aplicável:** True — Lotes de ~R$ 1 mil nas plataformas; com R$ 20 mil cabem 5 papéis de ~R$ 4 mil (10 com R$ 50 mil).

| métrica | valor |
|---|---|
| OOS desde | 2023-01 |
| retorno OOS a.a. (R$ 20 mil) | 10.6% vs CDI 13.1% |
| ativo OOS pp (R$ 20 mil / R$ 50 mil) | -2.49 / -3.23 |
| depois do IR (classe isento) pp, 20k / 50k | -2.44 / -3.17 |
| IR OOS / Sharpe | -0.49 / -0.49 |
| pior queda | -6.2% |
| PBO / Sharpe deflacionado | 40% / +0% |
| leque de parâmetros p5 / mediana / p95 | -3.47 / -1.79 / -0.50 |
| custo 2x / execução t+2 | -2.99 / -2.37 |
| walk-forward | -2.49 |
| sem os 10 melhores negócios | -1.58 |
| placebo p | 0.68 |
| look-ahead (truncamento) | passou |

**10 melhores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| AGRU11  |      1 | 2019-04-04 00:00:00 | 2025-03-17 00:00:00 |   1495 |       73.59 |         3.51 |
| CART12  |      1 | 2019-01-11 00:00:00 | 2024-12-16 00:00:00 |   1491 |       79.18 |         3.04 |
| MRSL27  |      1 | 2019-02-19 00:00:00 | 2025-02-17 00:00:00 |   1507 |       71.95 |         2.46 |
| CEAR25  |      1 | 2019-03-20 00:00:00 | 2024-12-16 00:00:00 |   1445 |       60.87 |         1.8  |
| CLAG13  |      1 | 2026-10-07 00:00:00 | 2026-10-13 00:00:00 |      4 |       -1.39 |        -0.27 |
| NTEN11  |      1 | 2026-10-06 00:00:00 | 2026-10-13 00:00:00 |      5 |       -3.27 |        -0.52 |
| CONX12  |      1 | 2025-01-07 00:00:00 | 2026-10-13 00:00:00 |    444 |       20.32 |        -0.55 |
| OMGE41  |      1 | 2025-01-07 00:00:00 | 2026-10-13 00:00:00 |    444 |       20.44 |        -0.58 |
| VBRR11  |      1 | 2026-10-06 00:00:00 | 2026-10-13 00:00:00 |      5 |       -3.56 |        -0.69 |
| SBSPC4  |      1 | 2025-01-10 00:00:00 | 2026-07-15 00:00:00 |    379 |       15.8  |        -0.81 |

**10 piores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| TBLE15  |      1 | 2019-01-22 00:00:00 | 2024-12-16 00:00:00 |   1484 |       17.67 |        -4.25 |
| SBSPC4  |      1 | 2025-01-10 00:00:00 | 2026-07-15 00:00:00 |    379 |       15.8  |        -0.81 |
| VBRR11  |      1 | 2026-10-06 00:00:00 | 2026-10-13 00:00:00 |      5 |       -3.56 |        -0.69 |
| OMGE41  |      1 | 2025-01-07 00:00:00 | 2026-10-13 00:00:00 |    444 |       20.44 |        -0.58 |
| CONX12  |      1 | 2025-01-07 00:00:00 | 2026-10-13 00:00:00 |    444 |       20.32 |        -0.55 |
| NTEN11  |      1 | 2026-10-06 00:00:00 | 2026-10-13 00:00:00 |      5 |       -3.27 |        -0.52 |
| CLAG13  |      1 | 2026-10-07 00:00:00 | 2026-10-13 00:00:00 |      4 |       -1.39 |        -0.27 |
| CEAR25  |      1 | 2019-03-20 00:00:00 | 2024-12-16 00:00:00 |   1445 |       60.87 |         1.8  |
| MRSL27  |      1 | 2019-02-19 00:00:00 | 2025-02-17 00:00:00 |   1507 |       71.95 |         2.46 |
| CART12  |      1 | 2019-01-11 00:00:00 | 2024-12-16 00:00:00 |   1491 |       79.18 |         3.04 |

**Quem trouxe o retorno (soma por ativo, pp)**

| ativo   |   sum |   count |
|:--------|------:|--------:|
| AGRU11  |  3.51 |       1 |
| CART12  |  3.04 |       1 |
| MRSL27  |  2.46 |       1 |
| CEAR25  |  1.8  |       1 |
| CLAG13  | -0.27 |       1 |
| NTEN11  | -0.52 |       1 |
| CONX12  | -0.55 |       1 |
| OMGE41  | -0.58 |       1 |
| VBRR11  | -0.69 |       1 |
| SBSPC4  | -0.81 |       1 |

### CRI/CRA IPCA+ isentos (balcão, varejo)  (`rf_cri_cra`)

**Tese:** Carrego os CRI/CRA IPCA+ de maior spread sobre a NTN-B (isentos para PF), com preço frequente no balcão, até vencerem

**Instrumentos:** [{'onde': 'XP / BTG / Inter / Rico (secundário de CRI/CRA)', 'ticker': 'CRI/CRA IPCA+ (código B3 tipo CRA022007EP / 22E1095384)', 'lote': '~R$ 1 mil', 'custo': 'spread embutido (metade da faixa p10–p90 do PU no dia, mediana ~1,5–2%) na compra e na venda antecipada'}]

**Aplicável:** True — Lotes de ~R$ 1–1,3 mil; com R$ 20 mil e 10 papéis só cabe 1 lote por papel (~55% do capital aplicado; o resto fica no CDI).

| métrica | valor |
|---|---|
| OOS desde | 2026-01 |
| retorno OOS a.a. (R$ 20 mil) | 9.9% vs CDI 14.4% |
| ativo OOS pp (R$ 20 mil / R$ 50 mil) | -4.47 / -6.96 |
| depois do IR (classe isento) pp, 20k / 50k | -4.38 / -6.82 |
| IR OOS / Sharpe | -0.56 / -0.56 |
| pior queda | -2.0% |
| PBO / Sharpe deflacionado | 93% / +22% |
| leque de parâmetros p5 / mediana / p95 | -7.29 / -4.47 / -3.40 |
| custo 2x / execução t+2 | -4.55 / -4.47 |
| walk-forward | +nan |
| sem os 10 melhores negócios | -4.79 |
| placebo p | 1.00 |
| look-ahead (truncamento) | passou |

**10 melhores negócios**

| ativo       |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:------------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| 25E0175587  |      1 | 2026-09-03 00:00:00 | 2026-10-13 00:00:00 |     27 |        3.87 |         0.25 |
| CRA022004XY |      1 | 2025-05-21 00:00:00 | 2026-10-13 00:00:00 |    353 |       19.6  |         0.03 |
| CRA021003KP |      1 | 2025-05-27 00:00:00 | 2026-10-13 00:00:00 |    349 |       16.3  |        -0.16 |
| CRA022008SZ |      1 | 2025-05-21 00:00:00 | 2025-11-13 00:00:00 |    126 |        3.18 |        -0.2  |
| 22E1325262  |      1 | 2025-05-22 00:00:00 | 2026-10-13 00:00:00 |    352 |       13.72 |        -0.25 |
| 22K0001201  |      1 | 2025-05-21 00:00:00 | 2026-10-13 00:00:00 |    353 |       13.5  |        -0.27 |
| 22I0970804  |      1 | 2025-05-27 00:00:00 | 2026-10-13 00:00:00 |    349 |       12.12 |        -0.33 |
| 22G1136327  |      1 | 2025-05-27 00:00:00 | 2026-09-02 00:00:00 |    322 |        7.66 |        -0.52 |
| 24A2721507  |      1 | 2025-11-12 00:00:00 | 2026-10-13 00:00:00 |    229 |        5.72 |        -0.58 |
| 22J0306937  |      1 | 2025-11-14 00:00:00 | 2026-10-13 00:00:00 |    227 |       -9.4  |        -1.05 |

**10 piores negócios**

| ativo       |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:------------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| CRA018002XN |      1 | 2025-05-21 00:00:00 | 2025-10-10 00:00:00 |    102 |      -14.24 |        -1.44 |
| 22K0934880  |      1 | 2025-05-21 00:00:00 | 2026-10-13 00:00:00 |    353 |       -8.58 |        -1.43 |
| CRA02300G7F |      1 | 2025-06-04 00:00:00 | 2026-10-13 00:00:00 |    343 |       -3.47 |        -1.1  |
| 22J0306937  |      1 | 2025-11-14 00:00:00 | 2026-10-13 00:00:00 |    227 |       -9.4  |        -1.05 |
| 24A2721507  |      1 | 2025-11-12 00:00:00 | 2026-10-13 00:00:00 |    229 |        5.72 |        -0.58 |
| 22G1136327  |      1 | 2025-05-27 00:00:00 | 2026-09-02 00:00:00 |    322 |        7.66 |        -0.52 |
| 22I0970804  |      1 | 2025-05-27 00:00:00 | 2026-10-13 00:00:00 |    349 |       12.12 |        -0.33 |
| 22K0001201  |      1 | 2025-05-21 00:00:00 | 2026-10-13 00:00:00 |    353 |       13.5  |        -0.27 |
| 22E1325262  |      1 | 2025-05-22 00:00:00 | 2026-10-13 00:00:00 |    352 |       13.72 |        -0.25 |
| CRA022008SZ |      1 | 2025-05-21 00:00:00 | 2025-11-13 00:00:00 |    126 |        3.18 |        -0.2  |

**Quem trouxe o retorno (soma por ativo, pp)**

| ativo       |   sum |   count |
|:------------|------:|--------:|
| 25E0175587  |  0.25 |       1 |
| CRA022004XY |  0.03 |       1 |
| CRA021003KP | -0.16 |       1 |
| CRA022008SZ | -0.2  |       1 |
| 22E1325262  | -0.25 |       1 |
| 22K0001201  | -0.27 |       1 |
| 22I0970804  | -0.33 |       1 |
| 22G1136327  | -0.52 |       1 |
| 24A2721507  | -0.58 |       1 |
| 22J0306937  | -1.05 |       1 |
