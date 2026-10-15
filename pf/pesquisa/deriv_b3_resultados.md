# Frente deriv_b3 — resultados da bateria final (gerado automaticamente)

Gerado por `pf/gerar_cadernos.py` a partir de `pf/resultados/bateria/`. IR de pessoa física por `pf/ir.py` (mensal na B3 com isenção de ações ≤ R$ 20 mil/mês, anual no exterior). Ordem: nota do ranking.

### Trava de alta / iron condor em BOVA11  (`db3_trava_bova`)

**Tese:** Vendo put spread (e call spread no condor) de 1 mês em BOVA11 com perda máxima conhecida = 'risco' x capital, só com IV > RV

**Instrumentos:** [{'onde': 'B3', 'ticker': 'BOVA*X / BOVA*L (puts/calls mensais de BOVA11)', 'lote': 100, 'custo': 'bid/ask do fechamento por perna + ~0,10% do prêmio'}, {'onde': 'Tesouro Direto / B3', 'ticker': 'Tesouro Selic (garantia)', 'lote': 'R$ ~170', 'custo': 'igual ao benchmark'}]

**Aplicável:** True — Cabe: perda máxima de 1 trava de 5% em BOVA11 (R$ 130–200) ≈ R$ 500–900; com 10% de risco (R$ 2 mil) são 2–4 travas. Limitação real: liquidez das opções de BOVA11 antes de 2019 (spread > 25% na maioria dos strikes).

| métrica | valor |
|---|---|
| OOS desde | 2021-01 |
| retorno OOS a.a. (R$ 20 mil) | 13.3% vs CDI 11.4% |
| ativo OOS pp (R$ 20 mil / R$ 50 mil) | +1.87 / +2.02 |
| depois do IR (classe opcoes_b3) pp, 20k / 50k | +1.56 / +1.68 |
| IR OOS / Sharpe | +0.67 / +0.67 |
| pior queda | -2.8% |
| PBO / Sharpe deflacionado | 4% / +32% |
| leque de parâmetros p5 / mediana / p95 | -3.51 / +1.54 / +2.69 |
| custo 2x / execução t+2 | +1.33 / +1.21 |
| walk-forward | +1.87 |
| sem os 10 melhores negócios | +0.39 |
| placebo p | 0.00 |
| look-ahead (truncamento) | passou |

**10 melhores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| BOVA    |     -1 | 2020-06-17 00:00:00 | 2020-07-20 00:00:00 |     23 |       19.29 |         1.62 |
| BOVA    |     -1 | 2026-09-22 00:00:00 | 2026-10-13 00:00:00 |     15 |       13.79 |         1.27 |
| BOVA    |     -1 | 2022-09-20 00:00:00 | 2022-10-21 00:00:00 |     23 |       13.86 |         1.22 |
| BOVA    |     -1 | 2022-01-25 00:00:00 | 2022-02-18 00:00:00 |     18 |       11.26 |         1.06 |
| BOVA    |     -1 | 2020-08-19 00:00:00 | 2020-09-21 00:00:00 |     23 |       10.35 |         1.03 |
| BOVA    |     -1 | 2022-08-23 00:00:00 | 2022-09-16 00:00:00 |     18 |       11.39 |         1.02 |
| BOVA    |     -1 | 2020-12-23 00:00:00 | 2021-01-18 00:00:00 |     18 |       12.75 |         1.02 |
| BOVA    |     -1 | 2021-04-22 00:00:00 | 2021-05-21 00:00:00 |     21 |       11.49 |         0.93 |
| BOVA    |     -1 | 2020-07-22 00:00:00 | 2020-08-17 00:00:00 |     18 |        9.85 |         0.9  |
| BOVA    |     -1 | 2020-09-23 00:00:00 | 2020-10-19 00:00:00 |     18 |        9.79 |         0.89 |

**10 piores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| BOVA    |     -1 | 2021-01-20 00:00:00 | 2021-02-22 00:00:00 |     23 |      -18.9  |        -1.43 |
| BOVA    |     -1 | 2025-06-24 00:00:00 | 2025-07-18 00:00:00 |     18 |        1.39 |         0.11 |
| BOVA    |     -1 | 2024-07-23 00:00:00 | 2024-08-16 00:00:00 |     18 |        1.41 |         0.14 |
| BOVA    |     -1 | 2025-09-23 00:00:00 | 2025-10-17 00:00:00 |     18 |        1.78 |         0.14 |
| BOVA    |     -1 | 2021-07-20 00:00:00 | 2021-08-20 00:00:00 |     23 |        1.92 |         0.16 |
| BOVA    |     -1 | 2024-01-23 00:00:00 | 2024-02-16 00:00:00 |     18 |        2.33 |         0.16 |
| BOVA    |     -1 | 2025-11-25 00:00:00 | 2025-12-19 00:00:00 |     18 |        2.38 |         0.21 |
| BOVA    |     -1 | 2023-08-22 00:00:00 | 2023-09-15 00:00:00 |     18 |        2.73 |         0.24 |
| BOVA    |     -1 | 2026-01-20 00:00:00 | 2026-02-20 00:00:00 |     23 |        2.97 |         0.26 |
| BOVA    |     -1 | 2024-09-24 00:00:00 | 2024-10-18 00:00:00 |     18 |        2.87 |         0.28 |

**Quem trouxe o retorno (soma por ativo, pp)**

| ativo   |   sum |   count |
|:--------|------:|--------:|
| BOVA    | 16.65 |      30 |

### Put coberta por Tesouro Selic (PETR4/VALE3/ITUB4/BOVA11)  (`db3_put_selic`)

**Tese:** Vendo put de 1 mês 3–6% OTM com o strike inteiro em Tesouro Selic, só quando IV > vol realizada e o papel está acima da média de 100d

**Instrumentos:** [{'onde': 'B3 (Clear/Rico/XP/BTG)', 'ticker': 'PETR*X / VALE*X / ITUB*X / BOVA*X (puts mensais)', 'lote': 100, 'custo': 'bid/ask do fechamento + ~0,10% do prêmio; exercício ~0,14% do nocional'}, {'onde': 'Tesouro Direto / B3', 'ticker': 'Tesouro Selic (LFT) como garantia', 'lote': 'R$ ~170', 'custo': 'custódia B3 (igual ao benchmark)'}]

**Aplicável:** True — Cabe: 1 lote de PETR4/ITUB4 = R$ 3–4 mil de strike, VALE3 R$ 5–7 mil, BOVA11 R$ 10–20 mil; com R$ 20 mil a alocação gulosa fica com 2–4 lotes por mês. Corretoras de varejo permitem venda de put coberta com Tesouro Selic como garantia.

| métrica | valor |
|---|---|
| OOS desde | 2021-01 |
| retorno OOS a.a. (R$ 20 mil) | 10.3% vs CDI 11.4% |
| ativo OOS pp (R$ 20 mil / R$ 50 mil) | -1.12 / -0.54 |
| depois do IR (classe opcoes_b3) pp, 20k / 50k | -1.10 / -0.54 |
| IR OOS / Sharpe | -0.11 / -0.11 |
| pior queda | -11.2% |
| PBO / Sharpe deflacionado | 5% / +0% |
| leque de parâmetros p5 / mediana / p95 | -1.70 / -0.59 / +0.20 |
| custo 2x / execução t+2 | -2.23 / -1.38 |
| walk-forward | -1.22 |
| sem os 10 melhores negócios | -3.25 |
| placebo p | 0.44 |
| look-ahead (truncamento) | passou |

**10 melhores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| VALE    |     -1 | 2015-05-20 00:00:00 | 2015-06-15 00:00:00 |     18 |       13.58 |         6.62 |
| VALE    |     -1 | 2016-01-20 00:00:00 | 2016-02-15 00:00:00 |     18 |       12.3  |         5.99 |
| VALE    |     -1 | 2015-08-19 00:00:00 | 2015-09-21 00:00:00 |     23 |        8.69 |         3.81 |
| VALE    |     -1 | 2014-03-19 00:00:00 | 2014-04-22 00:00:00 |     24 |        7.41 |         3.22 |
| VALE    |     -1 | 2016-07-20 00:00:00 | 2016-08-15 00:00:00 |     18 |        6.46 |         3.22 |
| PETR    |     -1 | 2016-01-20 00:00:00 | 2016-02-15 00:00:00 |     18 |        6.58 |         3.22 |
| VALE    |     -1 | 2016-02-17 00:00:00 | 2016-03-21 00:00:00 |     23 |        6.46 |         3.13 |
| VALE    |     -1 | 2015-09-23 00:00:00 | 2015-10-19 00:00:00 |     18 |        6.45 |         3    |
| VALE    |     -1 | 2016-12-21 00:00:00 | 2017-01-16 00:00:00 |     18 |        6.08 |         2.92 |
| PETR    |     -1 | 2016-04-20 00:00:00 | 2016-05-16 00:00:00 |     18 |        5.88 |         2.91 |

**10 piores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| PETR    |     -1 | 2020-02-19 00:00:00 | 2020-03-16 00:00:00 |     18 |      -54.31 |       -24.19 |
| VALE    |     -1 | 2015-12-23 00:00:00 | 2016-01-18 00:00:00 |     18 |      -14.18 |        -6.74 |
| PETR    |     -1 | 2021-01-20 00:00:00 | 2021-02-22 00:00:00 |     23 |      -18.46 |        -5.03 |
| VALE    |     -1 | 2021-07-20 00:00:00 | 2021-08-20 00:00:00 |     23 |       -9.17 |        -5.03 |
| PETR    |     -1 | 2024-02-20 00:00:00 | 2024-03-15 00:00:00 |     18 |      -10.62 |        -4.38 |
| PETR    |     -1 | 2014-09-17 00:00:00 | 2014-10-20 00:00:00 |     23 |      -10    |        -4.23 |
| PETR    |     -1 | 2014-02-19 00:00:00 | 2014-03-17 00:00:00 |     18 |       -7.2  |        -3.53 |
| PETR    |     -1 | 2017-02-22 00:00:00 | 2017-03-20 00:00:00 |     18 |       -7.46 |        -3.36 |
| VALE    |     -1 | 2023-07-25 00:00:00 | 2023-08-18 00:00:00 |     18 |       -8.61 |        -3    |
| PETR    |     -1 | 2019-03-20 00:00:00 | 2019-04-15 00:00:00 |     18 |       -6.5  |        -2.76 |

**Quem trouxe o retorno (soma por ativo, pp)**

| ativo   |   sum |   count |
|:--------|------:|--------:|
| VALE    | 60.54 |      76 |
| BOVA    |  8    |      47 |
| ITUB    |  5.27 |      50 |
| PETR    | -1.5  |      76 |

### Mini-índice WIN 1 contrato: tendência/reversão com regime VIX  (`db3_win_regime`)

**Tese:** 1 WIN comprado/vendido conforme a tendência (média móvel) ou reversão de 5 dias do Ibovespa; sem compra com VIX alto

**Instrumentos:** [{'onde': 'B3', 'ticker': 'WIN (mini-Ibovespa, vencimento par mais próximo)', 'lote': '1 contrato = 0,2 x Ibovespa', 'custo': 'R$ 1,10/contrato/lado + rolagem bimestral'}, {'onde': 'Tesouro Direto / B3', 'ticker': 'Tesouro Selic (margem ~R$ 2–4 mil)', 'lote': 'R$ ~170', 'custo': 'igual ao benchmark'}]

**Aplicável:** True — Cabe: 1 WIN = R$ 13–41 mil de nocional (0,7–2x com R$ 20 mil; 0,3–0,8x com R$ 50 mil), margem ~10% em Selic.

| métrica | valor |
|---|---|
| OOS desde | 2021-01 |
| retorno OOS a.a. (R$ 20 mil) | -0.6% vs CDI 11.4% |
| ativo OOS pp (R$ 20 mil / R$ 50 mil) | -12.07 / -5.46 |
| depois do IR (classe futuros_b3) pp, 20k / 50k | -11.99 / -5.50 |
| IR OOS / Sharpe | -0.50 / -0.50 |
| pior queda | -40.8% |
| PBO / Sharpe deflacionado | 37% / +1% |
| leque de parâmetros p5 / mediana / p95 | -14.84 / -10.95 / -2.66 |
| custo 2x / execução t+2 | -12.35 / -9.01 |
| walk-forward | +3.72 |
| sem os 10 melhores negócios | -21.97 |
| placebo p | 0.54 |
| look-ahead (truncamento) | passou |

**10 melhores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| WIN     |      1 | 2008-10-24 00:00:00 | 2008-10-31 00:00:00 |      5 |       16.46 |        17.02 |
| WIN     |      1 | 2008-12-24 00:00:00 | 2009-01-05 00:00:00 |      8 |       13.6  |        14.76 |
| WIN     |     -1 | 2020-02-18 00:00:00 | 2020-02-27 00:00:00 |      7 |       10.9  |        12.07 |
| WIN     |      1 | 2020-11-03 00:00:00 | 2020-11-10 00:00:00 |      5 |        9.55 |         9.71 |
| WIN     |     -1 | 2020-03-27 00:00:00 | 2020-04-03 00:00:00 |      5 |       11.37 |         8.22 |
| WIN     |     -1 | 2021-10-18 00:00:00 | 2021-10-22 00:00:00 |      4 |        7.55 |         8.22 |
| WIN     |      1 | 2020-04-06 00:00:00 | 2020-04-09 00:00:00 |      3 |       10.55 |         8.09 |
| WIN     |      1 | 2010-02-08 00:00:00 | 2010-02-17 00:00:00 |      7 |        6.08 |         8    |
| WIN     |     -1 | 2014-11-24 00:00:00 | 2014-12-02 00:00:00 |      6 |        7.25 |         7.83 |
| WIN     |      1 | 2016-04-05 00:00:00 | 2016-04-13 00:00:00 |      6 |        7.77 |         7.82 |

**10 piores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| WIN     |      1 | 2020-02-28 00:00:00 | 2020-03-26 00:00:00 |     19 |      -23.3  |       -20.35 |
| WIN     |      1 | 2013-06-03 00:00:00 | 2013-07-02 00:00:00 |     21 |      -17.49 |       -17.24 |
| WIN     |     -1 | 2026-01-21 00:00:00 | 2026-02-11 00:00:00 |     15 |       -9.64 |       -16.39 |
| WIN     |      1 | 2008-10-01 00:00:00 | 2008-10-20 00:00:00 |     13 |      -15.21 |       -13.46 |
| WIN     |      1 | 2026-04-24 00:00:00 | 2026-05-12 00:00:00 |     12 |       -7.17 |       -12.25 |
| WIN     |      1 | 2018-05-21 00:00:00 | 2018-06-26 00:00:00 |     26 |      -16.91 |       -12.17 |
| WIN     |     -1 | 2022-07-25 00:00:00 | 2022-08-26 00:00:00 |     24 |      -11.6  |       -12.04 |
| WIN     |     -1 | 2016-02-19 00:00:00 | 2016-03-16 00:00:00 |     18 |      -12.6  |       -11.61 |
| WIN     |     -1 | 2016-12-29 00:00:00 | 2017-01-25 00:00:00 |     19 |       -8.44 |       -10.07 |
| WIN     |     -1 | 2026-08-26 00:00:00 | 2026-09-17 00:00:00 |     16 |       -5.78 |        -9.91 |

**Quem trouxe o retorno (soma por ativo, pp)**

| ativo   |   sum |   count |
|:--------|------:|--------:|
| WIN     | 13.23 |     379 |

### Milho B3 (CCM) comprado — prêmio de hedge do produtor  (`db3_agro_ccm`)

**Tese:** Compro 1 contrato de milho B3 para receber o prêmio que o produtor paga pelo hedge; filtros de curva / tendência / safra

**Instrumentos:** [{'onde': 'B3', 'ticker': 'CCM (milho, vencimentos F/H/K/N/U/X)', 'lote': '1 contrato = 450 sacas (R$ 25–35 mil)', 'custo': 'R$ 6/contrato/lado + rolagem ~6x/ano'}, {'onde': 'Tesouro Direto / B3', 'ticker': 'Tesouro Selic (margem ~R$ 2–3 mil/contrato)', 'lote': 'R$ ~170', 'custo': 'igual ao benchmark'}]

**Aplicável:** True — Cabe: 1 CCM ≈ R$ 25–35 mil de nocional (1,3–1,7x com R$ 20 mil; 0,6x com R$ 50 mil), margem ~R$ 2–3 mil em Selic. Os outros agro (BGI, ICF, SJC, ETH) não cabem.

| métrica | valor |
|---|---|
| OOS desde | 2023-01 |
| retorno OOS a.a. (R$ 20 mil) | -19.7% vs CDI 13.1% |
| ativo OOS pp (R$ 20 mil / R$ 50 mil) | -32.78 / -19.39 |
| depois do IR (classe futuros_b3) pp, 20k / 50k | -32.21 / -19.05 |
| IR OOS / Sharpe | -1.56 / -1.56 |
| pior queda | -63.6% |
| PBO / Sharpe deflacionado | 27% / +0% |
| leque de parâmetros p5 / mediana / p95 | -34.03 / -31.81 / -20.55 |
| custo 2x / execução t+2 | -33.08 / -32.55 |
| walk-forward | -26.46 |
| sem os 10 melhores negócios | -33.97 |
| placebo p | 0.94 |
| look-ahead (truncamento) | passou |

**10 melhores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| CCM     |      1 | 2020-08-04 00:00:00 | 2020-11-10 00:00:00 |     70 |       46.95 |        68.98 |
| CCM     |      1 | 2021-06-22 00:00:00 | 2021-07-01 00:00:00 |      7 |       14    |        23.21 |
| CCM     |      1 | 2021-01-27 00:00:00 | 2021-06-02 00:00:00 |     90 |       10.61 |        22.48 |
| CCM     |      1 | 2018-01-29 00:00:00 | 2018-07-02 00:00:00 |    110 |       15.35 |        13.33 |
| CCM     |      1 | 2020-01-03 00:00:00 | 2020-07-02 00:00:00 |    129 |       12.18 |        13.15 |
| CCM     |      1 | 2025-01-03 00:00:00 | 2025-05-12 00:00:00 |     91 |        5.78 |        10.01 |
| CCM     |      1 | 2019-10-18 00:00:00 | 2019-11-21 00:00:00 |     24 |       10.28 |         9.85 |
| CCM     |      1 | 2019-05-13 00:00:00 | 2019-05-17 00:00:00 |      4 |       12.72 |         7.03 |
| CCM     |      1 | 2019-05-24 00:00:00 | 2019-05-28 00:00:00 |      2 |       12.6  |         5.16 |
| CCM     |      1 | 2018-11-01 00:00:00 | 2018-11-21 00:00:00 |     14 |        4.59 |         3.61 |

**10 piores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| CCM     |      1 | 2023-02-16 00:00:00 | 2023-05-03 00:00:00 |     54 |      -33.23 |       -58.88 |
| CCM     |      1 | 2024-01-03 00:00:00 | 2024-05-03 00:00:00 |     87 |      -23.59 |       -32.78 |
| CCM     |      1 | 2026-01-05 00:00:00 | 2026-04-20 00:00:00 |     75 |       -8.98 |       -14.16 |
| CCM     |      1 | 2021-06-15 00:00:00 | 2021-06-21 00:00:00 |      4 |       -8.89 |       -12.71 |
| CCM     |      1 | 2019-01-29 00:00:00 | 2019-05-03 00:00:00 |     68 |      -14.61 |       -12.24 |
| CCM     |      1 | 2023-01-03 00:00:00 | 2023-02-10 00:00:00 |     28 |       -5.53 |       -10.84 |
| CCM     |      1 | 2022-01-04 00:00:00 | 2022-04-29 00:00:00 |     83 |       -4.99 |       -10.72 |
| CCM     |      1 | 2024-11-01 00:00:00 | 2024-12-26 00:00:00 |     39 |       -4.99 |        -8.07 |
| CCM     |      1 | 2021-07-13 00:00:00 | 2021-09-02 00:00:00 |     37 |       -3.71 |        -7.9  |
| CCM     |      1 | 2018-01-03 00:00:00 | 2018-01-26 00:00:00 |     17 |       -4.78 |        -3.32 |

**Quem trouxe o retorno (soma por ativo, pp)**

| ativo   |   sum |   count |
|:--------|------:|--------:|
| CCM     |  5.24 |      47 |

### Covered call em ações isentas (PETR4/VALE3/ITUB4)  (`db3_cc_isenta`)

**Tese:** Carrego 3 blue chips em lotes de 100 (ganho isento até R$ 20 mil/mês de vendas) e vendo call de 1 mês OTM quando a IV está cara

**Instrumentos:** [{'onde': 'B3', 'ticker': 'PETR4, VALE3, ITUB4 (lote padrão 100)', 'lote': 100, 'custo': '0,11%/lado (emolumentos + meio spread)'}, {'onde': 'B3', 'ticker': 'calls mensais PETR*/VALE*/ITUB* (A–L)', 'lote': 100, 'custo': 'bid + 0,10% do prêmio; exercício 0,14%'}, {'onde': 'Tesouro Direto', 'ticker': 'Tesouro Selic (resto do caixa)', 'lote': 'R$ ~170', 'custo': 'igual ao benchmark'}]

**Aplicável:** True — Cabe: 1 lote de PETR4/ITUB4 ≈ R$ 3–4 mil, VALE3 ≈ R$ 5–7 mil; com R$ 20 mil compra 1–2 lotes de cada (sobra em Selic). Isenção: vendas ≤ R$ 20 mil/mês — com R$ 50 mil, exercício de vários lotes no mesmo mês pode estourar o limite.

| métrica | valor |
|---|---|
| OOS desde | 2021-01 |
| retorno OOS a.a. (R$ 20 mil) | 23.3% vs CDI 11.4% |
| ativo OOS pp (R$ 20 mil / R$ 50 mil) | +11.84 / +10.03 |
| depois do IR (classe acoes) pp, 20k / 50k | +11.66 / +9.75 |
| IR OOS / Sharpe | +0.85 / +0.85 |
| pior queda | -14.5% |
| PBO / Sharpe deflacionado | 52% / +93% |
| leque de parâmetros p5 / mediana / p95 | +11.35 / +12.13 / +12.49 |
| custo 2x / execução t+2 | +11.41 / +12.15 |
| walk-forward | +11.84 |
| sem os 10 melhores negócios | -4.35 |
| placebo p | 0.24 |
| look-ahead (truncamento) | passou |

**10 melhores negócios**

| ativo     |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:----------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| PETR ação |      1 | 2016-01-04 00:00:00 | 2016-12-30 00:00:00 |    259 |      121.94 |        32.36 |
| VALE ação |      1 | 2016-01-04 00:00:00 | 2016-12-30 00:00:00 |    259 |       98.2  |        24.94 |
| PETR ação |      1 | 2018-01-02 00:00:00 | 2018-12-31 00:00:00 |    259 |       46.77 |        17.02 |
| PETR ação |      1 | 2026-01-02 00:00:00 | 2026-10-13 00:00:00 |    202 |       96.26 |        16.19 |
| PETR ação |      1 | 2022-01-03 00:00:00 | 2022-12-30 00:00:00 |    259 |       37.33 |        15.58 |
| PETR ação |      1 | 2023-01-02 00:00:00 | 2023-12-29 00:00:00 |    259 |       96.2  |        14.83 |
| VALE ação |      1 | 2017-01-02 00:00:00 | 2017-12-29 00:00:00 |    259 |       63.66 |        13.69 |
| PETR ação |      1 | 2020-01-02 00:00:00 | 2020-12-31 00:00:00 |    260 |       -6.09 |        10.58 |
| ITUB ação |      1 | 2025-01-02 00:00:00 | 2025-12-31 00:00:00 |    259 |       62.94 |         9.66 |
| VALE ação |      1 | 2023-08-23 00:00:00 | 2023-11-21 00:00:00 |     64 |       33.93 |         9.49 |

**10 piores negócios**

| ativo     |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:----------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| PETR call |     -1 | 2016-02-17 00:00:00 | 2016-03-21 00:00:00 |     23 |      -57.51 |       -20.19 |
| VALE ação |      1 | 2015-01-02 00:00:00 | 2015-12-31 00:00:00 |    259 |      -37.36 |       -16.3  |
| ITUB ação |      1 | 2021-01-04 00:00:00 | 2021-12-31 00:00:00 |    259 |      -31.69 |       -11.87 |
| PETR ação |      1 | 2015-01-02 00:00:00 | 2015-12-31 00:00:00 |    259 |      -33.13 |       -10.47 |
| PETR call |     -1 | 2015-03-18 00:00:00 | 2015-04-20 00:00:00 |     23 |      -29    |        -9.41 |
| PETR ação |      1 | 2014-01-23 00:00:00 | 2014-12-31 00:00:00 |    244 |      -32.64 |        -9.36 |
| VALE ação |      1 | 2014-01-23 00:00:00 | 2014-12-31 00:00:00 |    244 |      -26.48 |        -8.29 |
| ITUB ação |      1 | 2015-01-02 00:00:00 | 2015-12-31 00:00:00 |    259 |      -14.1  |        -7.29 |
| PETR call |     -1 | 2022-07-19 00:00:00 | 2022-08-19 00:00:00 |     23 |      -20.54 |        -5.99 |
| ITUB call |     -1 | 2016-02-17 00:00:00 | 2016-03-21 00:00:00 |     23 |      -21.62 |        -5.44 |

**Quem trouxe o retorno (soma por ativo, pp)**

| ativo     |    sum |   count |
|:----------|-------:|--------:|
| PETR ação |  98.2  |      13 |
| VALE ação |  39.88 |      11 |
| ITUB ação |  30.95 |      13 |
| VALE call |  -3.19 |      35 |
| ITUB call |  -5.28 |      68 |
| PETR call | -29.24 |      63 |

### Carry do real vendido em mini-dólar (WDO) com filtro de risco  (`db3_wdo_carry`)

**Tese:** Vendo WDO (recebo CDI − cupom cambial) com garantia em Selic, só com VIX calmo, juro real alto e especuladores aumentando o real

**Instrumentos:** [{'onde': 'B3', 'ticker': 'WDO (mini-dólar, vencimento mais próximo)', 'lote': '1 contrato = US$ 10 mil', 'custo': 'R$ 4/contrato/lado + rolagem mensal'}, {'onde': 'Tesouro Direto / B3', 'ticker': 'Tesouro Selic (garantia ~R$ 5 mil/contrato)', 'lote': 'R$ ~170', 'custo': 'igual ao benchmark'}]

**Aplicável:** True — Cabe em margem (R$ 4–6 mil), mas 1 WDO = R$ 50–60 mil de nocional: com R$ 20 mil é 2,5–3x de alavancagem (vol ~35–45% a.a.; um choque como mar/2020 levaria 40–50% do capital). Com R$ 50 mil, 1 contrato ≈ 1x. Não há micro-dólar na B3.

| métrica | valor |
|---|---|
| OOS desde | 2023-01 |
| retorno OOS a.a. (R$ 20 mil) | 32.5% vs CDI 13.1% |
| ativo OOS pp (R$ 20 mil / R$ 50 mil) | +19.38 / +8.73 |
| depois do IR (classe futuros_b3) pp, 20k / 50k | +15.73 / +7.37 |
| IR OOS / Sharpe | +0.66 / +0.66 |
| pior queda | -42.4% |
| PBO / Sharpe deflacionado | 46% / +24% |
| leque de parâmetros p5 / mediana / p95 | +19.38 / +19.38 / +19.38 |
| custo 2x / execução t+2 | +18.75 / +19.38 |
| walk-forward | +11.40 |
| sem os 10 melhores negócios | -11.11 |
| placebo p | 0.04 |
| look-ahead (truncamento) | passou |

**10 melhores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| WDO     |     -1 | 2022-03-02 00:00:00 | 2022-03-29 00:00:00 |     19 |        8.82 |        22.09 |
| WDO     |     -1 | 2024-12-31 00:00:00 | 2025-01-29 00:00:00 |     21 |        5.72 |        17.31 |
| WDO     |     -1 | 2025-12-31 00:00:00 | 2026-01-28 00:00:00 |     20 |        5.71 |        15.35 |
| WDO     |     -1 | 2021-12-30 00:00:00 | 2022-01-27 00:00:00 |     20 |        5.36 |        14.92 |
| WDO     |     -1 | 2022-07-28 00:00:00 | 2022-08-29 00:00:00 |     22 |        5.6  |        14.5  |
| WDO     |     -1 | 2022-04-28 00:00:00 | 2022-05-27 00:00:00 |     21 |        5.32 |        13.28 |
| WDO     |     -1 | 2026-03-30 00:00:00 | 2026-04-29 00:00:00 |     22 |        5.21 |        13.22 |
| WDO     |     -1 | 2025-05-29 00:00:00 | 2025-06-26 00:00:00 |     20 |        4.12 |        11.52 |
| WDO     |     -1 | 2026-09-29 00:00:00 | 2026-10-13 00:00:00 |     10 |        4.34 |        11.09 |
| WDO     |     -1 | 2022-02-04 00:00:00 | 2022-02-25 00:00:00 |     15 |        4.17 |        10.81 |

**10 piores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| WDO     |     -1 | 2022-05-30 00:00:00 | 2022-06-28 00:00:00 |     21 |       -9.79 |       -24.66 |
| WDO     |     -1 | 2024-05-31 00:00:00 | 2024-06-26 00:00:00 |     18 |       -5.59 |       -15.04 |
| WDO     |     -1 | 2024-09-27 00:00:00 | 2024-10-29 00:00:00 |     22 |       -5.29 |       -14.85 |
| WDO     |     -1 | 2022-08-30 00:00:00 | 2022-09-28 00:00:00 |     21 |       -5.51 |       -14.41 |
| WDO     |     -1 | 2024-11-28 00:00:00 | 2024-12-30 00:00:00 |     22 |       -4.1  |       -12.52 |
| WDO     |     -1 | 2023-08-30 00:00:00 | 2023-09-27 00:00:00 |     20 |       -3.55 |        -8.77 |
| WDO     |     -1 | 2022-03-30 00:00:00 | 2022-04-27 00:00:00 |     20 |       -3.26 |        -7.75 |
| WDO     |     -1 | 2024-10-30 00:00:00 | 2024-11-27 00:00:00 |     20 |       -2.53 |        -7.34 |
| WDO     |     -1 | 2025-11-27 00:00:00 | 2025-12-30 00:00:00 |     23 |       -2.26 |        -6.18 |
| WDO     |     -1 | 2024-03-28 00:00:00 | 2024-04-29 00:00:00 |     22 |       -2.33 |        -5.98 |

**Quem trouxe o retorno (soma por ativo, pp)**

| ativo   |    sum |   count |
|:--------|-------:|--------:|
| WDO     | 127.67 |      60 |
