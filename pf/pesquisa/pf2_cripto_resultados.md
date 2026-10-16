# Frente pf2_cripto — resultados da bateria final (gerado automaticamente)

Gerado por `pf/gerar_cadernos.py` a partir de `pf/resultados/bateria/`. IR de pessoa física por `pf/ir.py` (mensal na B3 com isenção de ações ≤ R$ 20 mil/mês, anual no exterior). Ordem: nota do ranking.

### Altcoins top 20: momentum/reversão semanal (long-only, hedge BTC opcional)  (`cr_alts`)

**Tese:** compro as 5 altcoins de maior (ou menor) retorno recente entre as 20 maiores e, opcionalmente, vendo BTC contra no BIT

**Instrumentos:** [{'onde': 'Binance BR', 'ticker': '<alt>USDT (via USDTBRL)', 'lote': 'fração', 'custo': '0,35% por lado'}, {'onde': 'B3', 'ticker': 'BIT vendido (hedge)', 'lote': '0,01 BTC desde 06/2025', 'custo': '0,05% por lado'}]

**Aplicável:** parcial — long-only em corretora brasileira (Binance BR lista ~350 pares; MB menos); o hedge com BIT só cabe em contratos inteiros desde 06/2025 (antes 0,1 BTC). Em 10/2026 a Binance BR deslistou 22 tokens e cortou margem.

| métrica | valor |
|---|---|
| OOS desde | 2023-01 |
| retorno OOS a.a. (R$ 20 mil) | 10.2% vs CDI 13.1% |
| ativo OOS pp (R$ 20 mil / R$ 50 mil) | -2.91 / -2.91 |
| depois do IR (classe cripto) pp, 20k / 50k | -2.88 / -3.50 |
| IR OOS / Sharpe | +0.14 / +0.14 |
| pior queda | -65.5% |
| PBO / Sharpe deflacionado | 7% / +0% |
| leque de parâmetros p5 / mediana / p95 | -8.62 / +1.72 / +7.69 |
| custo 2x / execução t+2 | -10.87 / -1.21 |
| walk-forward | -2.91 |
| sem os 10 melhores negócios | -30.08 |
| placebo p | 0.38 |
| look-ahead (truncamento) | passou |

**10 melhores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| AXS     |      1 | 2021-07-19 00:00:00 | 2021-09-06 00:00:00 |     49 |      252.29 |        17.43 |
| DOGE    |      1 | 2024-10-28 00:00:00 | 2024-12-09 00:00:00 |     42 |      230.27 |        15.61 |
| LUNA    |      1 | 2021-08-02 00:00:00 | 2021-09-20 00:00:00 |     49 |      217.6  |        15.22 |
| VET     |      1 | 2020-06-01 00:00:00 | 2020-08-10 00:00:00 |     70 |      236.6  |        14.77 |
| ETC     |      1 | 2019-12-23 00:00:00 | 2020-02-17 00:00:00 |     56 |      196.23 |        14.24 |
| LINK    |      1 | 2020-06-29 00:00:00 | 2020-09-14 00:00:00 |     77 |      165.75 |        12.71 |
| BNB     |      1 | 2019-01-21 00:00:00 | 2019-04-08 00:00:00 |     77 |      198.54 |        12.3  |
| FTM     |      1 | 2021-09-06 00:00:00 | 2021-10-11 00:00:00 |     35 |      135.9  |        12.17 |
| SEI     |      1 | 2023-12-04 00:00:00 | 2024-02-05 00:00:00 |     63 |      154.53 |        12.16 |
| UNI     |      1 | 2021-01-25 00:00:00 | 2021-02-17 00:00:00 |     21 |      160.54 |        11.96 |

**10 piores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| DASH    |      1 | 2026-01-19 00:00:00 | 2026-02-18 00:00:00 |     28 |      -56.77 |        -7.68 |
| DASH    |      1 | 2025-11-10 00:00:00 | 2025-12-08 00:00:00 |     28 |      -53.56 |        -6.72 |
| ZIL     |      1 | 2022-04-04 00:00:00 | 2022-05-02 00:00:00 |     28 |      -54.66 |        -6.27 |
| XLM     |      1 | 2018-11-05 00:00:00 | 2018-12-10 00:00:00 |     35 |      -51.78 |        -5.93 |
| IOTA    |      1 | 2018-11-19 00:00:00 | 2018-12-17 00:00:00 |     28 |      -48.71 |        -5.81 |
| ETC     |      1 | 2021-05-10 00:00:00 | 2021-06-07 00:00:00 |     28 |      -45.96 |        -5.64 |
| OP      |      1 | 2022-08-01 00:00:00 | 2022-08-29 00:00:00 |     28 |      -44.56 |        -5.48 |
| WLD     |      1 | 2025-09-15 00:00:00 | 2025-10-13 00:00:00 |     28 |      -47.69 |        -5.31 |
| ETH     |      1 | 2018-11-12 00:00:00 | 2018-12-03 00:00:00 |     21 |      -46.04 |        -5.28 |
| DOGE    |      1 | 2022-04-18 00:00:00 | 2022-05-30 00:00:00 |     42 |      -44.03 |        -5.15 |

**Quem trouxe o retorno (soma por ativo, pp)**

| ativo   |   sum |   count |
|:--------|------:|--------:|
| LUNA    | 23.51 |      10 |
| LINK    | 22.78 |      24 |
| ZEC     | 20.78 |      11 |
| AAVE    | 17.28 |      12 |
| SOL     | 16.49 |      24 |
| AXS     | 16.12 |       5 |
| FTM     | 14.75 |      14 |
| SAND    | 13.9  |       5 |
| UNI     | 13.87 |      11 |
| GRT     | 13.5  |       3 |

### Fim de semana/horário: BTC/ETH só quando B3 e CME estão fechadas  (`cr_fds`)

**Tese:** seguro cripto à vista só nas janelas sem ETF/futuro (fim de semana, noite) se o livro raso paga prêmio; senão fico no CDI

**Instrumentos:** [{'onde': 'Binance BR / Mercado Bitcoin', 'ticker': 'BTCBRL / ETHBRL', 'lote': 'fração', 'custo': '0,15% por lado'}]

**Aplicável:** True — à vista em R$ em corretora brasileira; ordens agendadas por horário (manual ou API da corretora)

| métrica | valor |
|---|---|
| OOS desde | 2023-01 |
| retorno OOS a.a. (R$ 20 mil) | 11.0% vs CDI 13.1% |
| ativo OOS pp (R$ 20 mil / R$ 50 mil) | -2.07 / -2.07 |
| depois do IR (classe cripto) pp, 20k / 50k | -2.02 / -2.02 |
| IR OOS / Sharpe | +0.11 / +0.11 |
| pior queda | -43.9% |
| PBO / Sharpe deflacionado | 0% / +0% |
| leque de parâmetros p5 / mediana / p95 | -1.97 / -1.24 / -0.23 |
| custo 2x / execução t+2 | -18.26 / -27.68 |
| walk-forward | -2.07 |
| sem os 10 melhores negócios | -23.91 |
| placebo p | 0.09 |
| look-ahead (truncamento) | passou |

**10 melhores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| ETH     |      1 | 2021-01-04 00:00:00 | 2021-01-04 00:00:00 |      2 |       39.75 |        39.58 |
| ETH     |      1 | 2018-12-21 00:00:00 | 2018-12-24 00:00:00 |      2 |       34.28 |        33.93 |
| ETH     |      1 | 2019-02-15 00:00:00 | 2019-02-18 00:00:00 |      2 |       18.74 |        18.41 |
| ETH     |      1 | 2018-01-05 00:00:00 | 2018-01-08 00:00:00 |      2 |       18.16 |        17.84 |
| ETH     |      1 | 2021-05-07 00:00:00 | 2021-05-10 00:00:00 |      2 |       17.45 |        17.39 |
| ETH     |      1 | 2020-11-20 00:00:00 | 2020-11-23 00:00:00 |      2 |       16.69 |        16.79 |
| ETH     |      1 | 2022-07-15 00:00:00 | 2022-07-18 00:00:00 |      2 |       17.3  |        16.2  |
| ETH     |      1 | 2020-12-28 00:00:00 | 2020-12-28 00:00:00 |      2 |       16.9  |        15.99 |
| ETH     |      1 | 2021-07-23 00:00:00 | 2021-07-26 00:00:00 |      2 |       16.24 |        14.92 |
| ETH     |      1 | 2017-09-15 00:00:00 | 2017-09-18 00:00:00 |      2 |       15.12 |        14.8  |

**10 piores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| ETH     |      1 | 2017-09-01 00:00:00 | 2017-09-04 00:00:00 |      2 |      -27.84 |       -28.1  |
| ETH     |      1 | 2022-06-10 00:00:00 | 2022-06-13 00:00:00 |      2 |      -27    |       -26.24 |
| ETH     |      1 | 2024-08-02 00:00:00 | 2024-08-05 00:00:00 |      2 |      -26.01 |       -23.11 |
| ETH     |      1 | 2025-01-31 00:00:00 | 2025-02-03 00:00:00 |      2 |      -22.18 |       -21.89 |
| ETH     |      1 | 2022-01-21 00:00:00 | 2022-01-24 00:00:00 |      2 |      -20.21 |       -20.12 |
| ETH     |      1 | 2019-07-12 00:00:00 | 2019-07-15 00:00:00 |      2 |      -19.33 |       -19.6  |
| ETH     |      1 | 2020-09-04 00:00:00 | 2020-09-08 00:00:00 |      2 |      -16.14 |       -16.42 |
| ETH     |      1 | 2020-03-13 00:00:00 | 2020-03-16 00:00:00 |      2 |      -16.08 |       -16.35 |
| ETH     |      1 | 2025-04-04 00:00:00 | 2025-04-07 00:00:00 |      2 |      -15.97 |       -15.71 |
| ETH     |      1 | 2018-03-16 00:00:00 | 2018-03-19 00:00:00 |      2 |      -14.78 |       -15.06 |

**Quem trouxe o retorno (soma por ativo, pp)**

| ativo   |    sum |   count |
|:--------|-------:|--------:|
| ETH     | 204.56 |     485 |

### ETF cripto B3 x futuro B3 (BITH11/ETHE11/SOLH11 x BIT/ETR/SOL), market-neutral  (`cr_etf_futuro`)

**Tese:** compro o ETF de cripto quando ele fecha barato contra o próprio futuro da B3 e vendo o futuro em contratos inteiros

**Instrumentos:** [{'onde': 'B3', 'ticker': 'BITH11 x BIT', 'lote': '1 cota x 0.01 BTC', 'custo': 'ETF 0,03%+spread; futuro 0,05%/lado'}, {'onde': 'B3', 'ticker': 'ETHE11 x ETR', 'lote': '1 cota x 0.25 ETH', 'custo': 'ETF 0,03%+spread; futuro 0,05%/lado'}, {'onde': 'B3', 'ticker': 'SOLH11 x SOL', 'lote': '1 cota x 5.0 SOL', 'custo': 'ETF 0,03%+spread; futuro 0,05%/lado'}]

**Aplicável:** True — tudo na B3 (conta única, garantia em Tesouro Selic); contratos de 0,01 BTC / 0,25 ETH / 5 SOL cabem em R$ 20 mil desde 06/2025

| métrica | valor |
|---|---|
| OOS desde | 2026-01 |
| retorno OOS a.a. (R$ 20 mil) | 0.8% vs CDI 14.4% |
| ativo OOS pp (R$ 20 mil / R$ 50 mil) | -13.55 / -15.11 |
| depois do IR (classe futuros_b3) pp, 20k / 50k | -13.30 / -14.83 |
| IR OOS / Sharpe | -2.14 / -2.14 |
| pior queda | -2.8% |
| PBO / Sharpe deflacionado | 30% / +nan% |
| leque de parâmetros p5 / mediana / p95 | -4.94 / +0.69 / +2.23 |
| custo 2x / execução t+2 | -21.74 / -8.19 |
| walk-forward | +nan |
| sem os 10 melhores negócios | -21.67 |
| placebo p | 1.00 |
| look-ahead (truncamento) | passou |

**10 melhores negócios**

| ativo      |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:-----------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| ETHE11xETR |      1 | 2026-07-01 00:00:00 | 2026-07-09 00:00:00 |      6 |        9.47 |         1.94 |
| SOLH11xSOL |      1 | 2026-07-01 00:00:00 | 2026-07-03 00:00:00 |      2 |        3.29 |         0.95 |
| BITH11xBIT |      1 | 2026-06-30 00:00:00 | 2026-07-08 00:00:00 |      6 |        5.31 |         0.8  |
| SOLH11xSOL |      1 | 2025-11-17 00:00:00 | 2025-11-21 00:00:00 |      3 |        3.51 |         0.65 |
| SOLH11xSOL |      1 | 2026-08-25 00:00:00 | 2026-08-31 00:00:00 |      4 |        2.04 |         0.52 |
| ETHE11xETR |      1 | 2026-06-03 00:00:00 | 2026-06-09 00:00:00 |      3 |        2.09 |         0.48 |
| SOLH11xSOL |      1 | 2026-04-17 00:00:00 | 2026-04-20 00:00:00 |      1 |        1.72 |         0.38 |
| ETHE11xETR |      1 | 2026-07-22 00:00:00 | 2026-07-27 00:00:00 |      3 |        1.54 |         0.37 |
| SOLH11xSOL |      1 | 2026-09-25 00:00:00 | 2026-09-29 00:00:00 |      2 |        2.12 |         0.34 |
| ETHE11xETR |      1 | 2026-09-14 00:00:00 | 2026-09-18 00:00:00 |      4 |        2    |         0.33 |

**10 piores negócios**

| ativo      |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:-----------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| SOLH11xSOL |      1 | 2026-05-29 00:00:00 | 2026-06-01 00:00:00 |      1 |       -6.59 |        -1.37 |
| SOLH11xSOL |      1 | 2026-10-02 00:00:00 | 2026-10-05 00:00:00 |      1 |       -6.67 |        -1.04 |
| ETHE11xETR |      1 | 2026-04-01 00:00:00 | 2026-04-02 00:00:00 |      1 |       -3.56 |        -0.98 |
| SOLH11xSOL |      1 | 2026-07-09 00:00:00 | 2026-07-16 00:00:00 |      5 |       -3.19 |        -0.96 |
| ETHE11xETR |      1 | 2026-10-02 00:00:00 | 2026-10-07 00:00:00 |      3 |       -5.5  |        -0.96 |
| SOLH11xSOL |      1 | 2026-06-29 00:00:00 | 2026-06-30 00:00:00 |      1 |       -2.67 |        -0.79 |
| SOLH11xSOL |      1 | 2025-07-21 00:00:00 | 2025-07-24 00:00:00 |      3 |       -2.86 |        -0.77 |
| SOLH11xSOL |      1 | 2026-07-27 00:00:00 | 2026-07-28 00:00:00 |      1 |       -2.54 |        -0.74 |
| SOLH11xSOL |      1 | 2026-03-09 00:00:00 | 2026-03-11 00:00:00 |      2 |       -2.98 |        -0.67 |
| SOLH11xSOL |      1 | 2026-07-17 00:00:00 | 2026-07-21 00:00:00 |      2 |       -2.28 |        -0.66 |

**Quem trouxe o retorno (soma por ativo, pp)**

| ativo      |   sum |   count |
|:-----------|------:|--------:|
| BITH11xBIT | -0.82 |      18 |
| ETHE11xETR | -2.1  |      23 |
| SOLH11xSOL | -7.43 |      36 |

### Staking de ETH: neutro (staking + perpétuo vendido, offshore) ou cupom sobre o beta  (`cr_staking`)

**Tese:** ganho o staking do ether e, no modo neutro, vendo o perpétuo para receber também o financiamento sem correr o preço

**Instrumentos:** [{'onde': 'Binance internacional / OKX (offshore)', 'ticker': 'WBETH + ETHUSDT perpétuo', 'lote': 'fração', 'custo': '0,15%/lado'}, {'onde': 'Mercado Bitcoin / Binance BR', 'ticker': 'ETH em staking', 'lote': 'fração', 'custo': '0,15%/lado'}]

**Aplicável:** parcial — neutro só offshore (perpétuo fora da CVM, contraparte); o modo beta cabe em corretora brasileira (staking de ETH oferecido)

| métrica | valor |
|---|---|
| OOS desde | 2023-01 |
| retorno OOS a.a. (R$ 20 mil) | 9.7% vs CDI 13.1% |
| ativo OOS pp (R$ 20 mil / R$ 50 mil) | -3.43 / -3.43 |
| depois do IR (classe exterior) pp, 20k / 50k | -3.37 / -3.37 |
| IR OOS / Sharpe | -0.53 / -0.53 |
| pior queda | -8.0% |
| PBO / Sharpe deflacionado | 19% / +0% |
| leque de parâmetros p5 / mediana / p95 | -8.85 / -3.64 / -2.64 |
| custo 2x / execução t+2 | -8.17 / -3.93 |
| walk-forward | -11.19 |
| sem os 10 melhores negócios | -4.81 |
| placebo p | 0.00 |
| look-ahead (truncamento) | passou |

**10 melhores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| ETH     |      1 | 2020-03-30 00:00:00 | 2021-06-02 00:00:00 |    430 |       67.26 |        30.73 |
| ETH     |      1 | 2019-12-11 00:00:00 | 2020-03-26 00:00:00 |    106 |       10.45 |         5.81 |
| ETH     |      1 | 2024-02-27 00:00:00 | 2024-04-18 00:00:00 |     51 |        4.97 |         2.73 |
| ETH     |      1 | 2021-10-11 00:00:00 | 2021-12-15 00:00:00 |     67 |        4.71 |         2.58 |
| ETH     |      1 | 2021-08-03 00:00:00 | 2021-10-01 00:00:00 |     59 |        3.73 |         2.02 |
| ETH     |      1 | 2023-12-14 00:00:00 | 2024-01-18 00:00:00 |     35 |        2.45 |         1.27 |
| ETH     |      1 | 2024-11-14 00:00:00 | 2024-12-23 00:00:00 |     37 |        2.27 |         1.16 |
| ETH     |      1 | 2021-06-04 00:00:00 | 2021-06-28 00:00:00 |     23 |        0.73 |         0.26 |
| ETH     |      1 | 2024-06-03 00:00:00 | 2024-06-17 00:00:00 |     14 |        0.71 |         0.25 |
| ETH     |      1 | 2023-11-13 00:00:00 | 2023-11-27 00:00:00 |     14 |        0.7  |         0.24 |

**10 piores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| ETH     |      1 | 2023-12-12 00:00:00 | 2023-12-13 00:00:00 |      1 |        0.01 |        -0.18 |
| ETH     |      1 | 2023-01-27 00:00:00 | 2023-01-30 00:00:00 |      3 |        0.04 |        -0.16 |
| ETH     |      1 | 2021-12-29 00:00:00 | 2021-12-30 00:00:00 |      1 |        0.06 |        -0.14 |
| ETH     |      1 | 2023-01-24 00:00:00 | 2023-01-25 00:00:00 |      1 |        0.08 |        -0.13 |
| ETH     |      1 | 2021-07-13 00:00:00 | 2021-07-23 00:00:00 |     10 |        0.2  |        -0.06 |
| ETH     |      1 | 2023-11-13 00:00:00 | 2023-11-27 00:00:00 |     14 |        0.7  |         0.24 |
| ETH     |      1 | 2024-06-03 00:00:00 | 2024-06-17 00:00:00 |     14 |        0.71 |         0.25 |
| ETH     |      1 | 2021-06-04 00:00:00 | 2021-06-28 00:00:00 |     23 |        0.73 |         0.26 |
| ETH     |      1 | 2024-11-14 00:00:00 | 2024-12-23 00:00:00 |     37 |        2.27 |         1.16 |
| ETH     |      1 | 2023-12-14 00:00:00 | 2024-01-18 00:00:00 |     35 |        2.45 |         1.27 |

**Quem trouxe o retorno (soma por ativo, pp)**

| ativo   |   sum |   count |
|:--------|------:|--------:|
| ETH     | 46.38 |      15 |

### Carry de financiamento de perpétuos (à vista x perpétuo, offshore, com contraparte)  (`cr_funding`)

**Tese:** compro o à vista e vendo o perpétuo quando o financiamento médio passa do CDI + limiar; recebo o que o alavancado paga

**Instrumentos:** [{'onde': 'Binance internacional (Abu Dhabi) / OKX — offshore', 'ticker': 'BTCUSDT spot + BTCUSDT perpétuo', 'lote': 'fração (mín. ~US$ 5-100)', 'custo': '0,10% à vista + 0,05% perpétuo por lado'}, {'onde': 'Binance internacional (Abu Dhabi) / OKX — offshore', 'ticker': 'ETHUSDT spot + ETHUSDT perpétuo', 'lote': 'fração (mín. ~US$ 5-100)', 'custo': '0,10% à vista + 0,05% perpétuo por lado'}, {'onde': 'Binance internacional (Abu Dhabi) / OKX — offshore', 'ticker': 'SOLUSDT spot + SOLUSDT perpétuo', 'lote': 'fração (mín. ~US$ 5-100)', 'custo': '0,10% à vista + 0,05% perpétuo por lado'}, {'onde': 'Binance internacional (Abu Dhabi) / OKX — offshore', 'ticker': 'BNBUSDT spot + BNBUSDT perpétuo', 'lote': 'fração (mín. ~US$ 5-100)', 'custo': '0,10% à vista + 0,05% perpétuo por lado'}, {'onde': 'Binance internacional (Abu Dhabi) / OKX — offshore', 'ticker': 'XRPUSDT spot + XRPUSDT perpétuo', 'lote': 'fração (mín. ~US$ 5-100)', 'custo': '0,10% à vista + 0,05% perpétuo por lado'}, {'onde': 'Binance internacional (Abu Dhabi) / OKX — offshore', 'ticker': 'DOGEUSDT spot + DOGEUSDT perpétuo', 'lote': 'fração (mín. ~US$ 5-100)', 'custo': '0,10% à vista + 0,05% perpétuo por lado'}]

**Aplicável:** parcial — perpétuo só via conta offshore fora da CVM/BCB (Binance internacional/OKX); Bybit e Binance BR cortaram derivativos a brasileiros em 2026. Exige remessa (IOF 1,1%), USDT e aceitar risco de contraparte e regulatório; lotes fracionários cabem com R$ 20 mil.

| métrica | valor |
|---|---|
| OOS desde | 2023-01 |
| retorno OOS a.a. (R$ 20 mil) | 10.2% vs CDI 13.1% |
| ativo OOS pp (R$ 20 mil / R$ 50 mil) | -2.90 / -2.90 |
| depois do IR (classe exterior) pp, 20k / 50k | -2.85 / -2.85 |
| IR OOS / Sharpe | -0.97 / -0.97 |
| pior queda | -5.1% |
| PBO / Sharpe deflacionado | 62% / +1% |
| leque de parâmetros p5 / mediana / p95 | -4.77 / -3.96 / -2.94 |
| custo 2x / execução t+2 | -5.99 / -2.91 |
| walk-forward | -4.68 |
| sem os 10 melhores negócios | -3.20 |
| placebo p | 0.00 |
| look-ahead (truncamento) | passou |

**10 melhores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| XRP     |      1 | 2021-01-08 00:00:00 | 2021-05-26 00:00:00 |    138 |       41.44 |         3.04 |
| ETH     |      1 | 2020-12-21 00:00:00 | 2021-05-03 00:00:00 |    134 |       32.04 |         2.48 |
| BTC     |      1 | 2020-12-23 00:00:00 | 2021-03-10 00:00:00 |     77 |       15.58 |         1.29 |
| SOL     |      1 | 2021-01-22 00:00:00 | 2021-05-24 00:00:00 |    121 |       24.36 |         1.14 |
| BNB     |      1 | 2021-03-12 00:00:00 | 2021-05-24 00:00:00 |     71 |       12    |         0.91 |
| BTC     |      1 | 2021-03-12 00:00:00 | 2021-05-03 00:00:00 |     51 |        7.06 |         0.73 |
| DOGE    |      1 | 2021-03-15 00:00:00 | 2021-05-21 00:00:00 |     69 |       14.72 |         0.71 |
| XRP     |      1 | 2020-01-21 00:00:00 | 2020-03-06 00:00:00 |     45 |        8.03 |         0.66 |
| BNB     |      1 | 2020-12-21 00:00:00 | 2021-02-03 00:00:00 |     45 |        7.06 |         0.56 |
| DOGE    |      1 | 2021-02-17 00:00:00 | 2021-03-08 00:00:00 |     23 |        5.26 |         0.53 |

**10 piores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| BNB     |      1 | 2020-08-03 00:00:00 | 2020-08-10 00:00:00 |      9 |        0.03 |        -0.04 |
| DOGE    |      1 | 2024-12-10 00:00:00 | 2024-12-11 00:00:00 |      1 |        0.05 |        -0.04 |
| BNB     |      1 | 2024-03-15 00:00:00 | 2024-03-18 00:00:00 |      2 |        0.1  |        -0.03 |
| BNB     |      1 | 2020-12-15 00:00:00 | 2020-12-16 00:00:00 |      1 |        0.11 |        -0.03 |
| BTC     |      1 | 2024-01-04 00:00:00 | 2024-01-08 00:00:00 |      2 |        0.07 |        -0.03 |
| BTC     |      1 | 2021-09-08 00:00:00 | 2021-09-08 00:00:00 |      1 |        0.08 |        -0.02 |
| SOL     |      1 | 2024-04-02 00:00:00 | 2024-04-08 00:00:00 |      6 |        0.21 |        -0.02 |
| BNB     |      1 | 2020-02-26 00:00:00 | 2020-03-06 00:00:00 |     10 |        0.25 |        -0.02 |
| ETH     |      1 | 2020-05-11 00:00:00 | 2020-05-18 00:00:00 |      5 |        0.2  |        -0.01 |
| DOGE    |      1 | 2020-12-30 00:00:00 | 2021-02-01 00:00:00 |     32 |        4.56 |        -0.01 |

**Quem trouxe o retorno (soma por ativo, pp)**

| ativo   |   sum |   count |
|:--------|------:|--------:|
| XRP     |  5.55 |      11 |
| ETH     |  4.26 |      10 |
| BTC     |  3.4  |      10 |
| DOGE    |  2.42 |      11 |
| BNB     |  2.03 |      11 |
| SOL     |  1.43 |       6 |

### Prêmio brasileiro: arbitragem MB x Binance BR e triangular em R$ (estoque nas duas pontas)  (`cr_premio_br`)

**Tese:** com BTC/ETH e R$ parados em duas corretoras, vendo onde o varejo pagou caro e compro onde vendeu barato, na mesma hora

**Instrumentos:** [{'onde': 'Mercado Bitcoin', 'ticker': 'BTC-BRL / ETH-BRL', 'lote': 'fração', 'custo': '0,70% taker + spread'}, {'onde': 'Binance BR', 'ticker': 'BTCBRL / ETHBRL / BTCUSDT / USDTBRL', 'lote': 'fração', 'custo': '0,10% + spread'}, {'onde': 'B3', 'ticker': 'BIT/ETR vendidos (hedge do estoque)', 'lote': '0,01 BTC / 0,25 ETH', 'custo': '~0,05%'}]

**Aplicável:** True — contas em duas corretoras brasileiras (PF abre em minutos), frações de BTC/ETH; o hedge do estoque com BIT só cabe para R$ 20 mil desde 06/2025 (antes: estoque em beta ou só R$ 50 mil+)

| métrica | valor |
|---|---|
| OOS desde | 2023-01 |
| retorno OOS a.a. (R$ 20 mil) | 10.6% vs CDI 13.1% |
| ativo OOS pp (R$ 20 mil / R$ 50 mil) | -2.48 / -2.48 |
| depois do IR (classe cripto) pp, 20k / 50k | -2.44 / -2.44 |
| IR OOS / Sharpe | -55.17 / -55.17 |
| pior queda | -0.0% |
| PBO / Sharpe deflacionado | 0% / +0% |
| leque de parâmetros p5 / mediana / p95 | -3.66 / -2.63 / -1.66 |
| custo 2x / execução t+2 | -2.52 / -2.48 |
| walk-forward | -2.56 |
| sem os 10 melhores negócios | -2.45 |
| placebo p | 0.79 |
| look-ahead (truncamento) | passou |

**10 melhores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| ETH     |     -1 | 2022-06-13 00:00:00 | 2022-06-14 00:00:00 |      0 |       13.55 |         0.31 |
| BTC     |     -1 | 2021-02-23 00:00:00 | 2021-02-24 00:00:00 |      0 |        4.43 |         0.07 |
| BTC     |     -1 | 2021-01-04 00:00:00 | 2021-01-04 00:00:00 |      0 |        4.32 |         0.07 |
| BTC     |     -1 | 2022-08-01 00:00:00 | 2022-08-01 00:00:00 |      0 |        1.7  |         0.06 |
| BTC     |      1 | 2021-01-29 00:00:00 | 2021-02-01 00:00:00 |      0 |        3.96 |         0.06 |
| ETH     |      1 | 2021-03-09 00:00:00 | 2021-03-10 00:00:00 |      1 |        3.87 |         0.06 |
| ETH     |     -1 | 2021-02-23 00:00:00 | 2021-02-24 00:00:00 |      0 |        3.67 |         0.05 |
| BTC     |     -1 | 2021-05-24 00:00:00 | 2021-05-24 00:00:00 |      0 |        3.45 |         0.05 |
| BTC     |      1 | 2021-03-09 00:00:00 | 2021-03-11 00:00:00 |      2 |        3.36 |         0.04 |
| ETH     |     -1 | 2021-01-08 00:00:00 | 2021-01-11 00:00:00 |      0 |        3.39 |         0.04 |

**10 piores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| BTC     |     -1 | 2022-08-01 00:00:00 | 2022-08-01 00:00:00 |      0 |       -4.64 |        -0.21 |
| ETH     |     -1 | 2021-04-19 00:00:00 | 2021-04-19 00:00:00 |      0 |       -4.2  |        -0.19 |
| ETH     |     -1 | 2021-01-07 00:00:00 | 2021-01-08 00:00:00 |      0 |       -3.65 |        -0.18 |
| BTC     |     -1 | 2022-06-13 00:00:00 | 2022-06-13 00:00:00 |      0 |       -1.49 |        -0.13 |
| ETH     |      1 | 2021-03-08 00:00:00 | 2021-03-09 00:00:00 |      1 |       -2.25 |        -0.13 |
| ETH     |      1 | 2020-12-16 00:00:00 | 2020-12-17 00:00:00 |      1 |       -1.51 |        -0.11 |
| BTC     |     -1 | 2021-04-19 00:00:00 | 2021-04-20 00:00:00 |      1 |       -1.19 |        -0.1  |
| ETH     |     -1 | 2021-04-26 00:00:00 | 2021-04-26 00:00:00 |      0 |       -0.73 |        -0.09 |
| ETH     |     -1 | 2021-05-20 00:00:00 | 2021-05-20 00:00:00 |      0 |       -0.8  |        -0.09 |
| ETH     |     -1 | 2020-11-30 00:00:00 | 2020-11-30 00:00:00 |      0 |       -0.59 |        -0.08 |

**Quem trouxe o retorno (soma por ativo, pp)**

| ativo   |   sum |   count |
|:--------|------:|--------:|
| BTC     | -0.43 |      27 |
| ETH     | -1.26 |      41 |

### Eventos cripto: listagens na Binance (venda offshore / compra) e halving  (`cr_eventos`)

**Tese:** vendo (offshore) o perpétuo da moeda recém-listada: o insider destrava e o varejo da listagem paga a conta; halving como controle

**Instrumentos:** [{'onde': 'Binance internacional / OKX (offshore)', 'ticker': '<nova>USDT perpétuo', 'lote': 'fração', 'custo': '0,35%/lado + financiamento'}, {'onde': 'Binance BR', 'ticker': '<nova>USDT / BTCBRL', 'lote': 'fração', 'custo': '0,35% / 0,15% por lado'}]

**Aplicável:** parcial — a venda só existe offshore (perpétuo fora da CVM, contraparte e regulatório; Bybit/Binance BR cortaram derivativos a brasileiros em 2026); a compra e o halving cabem em corretora brasileira

| métrica | valor |
|---|---|
| OOS desde | 2023-01 |
| retorno OOS a.a. (R$ 20 mil) | 32.6% vs CDI 13.1% |
| ativo OOS pp (R$ 20 mil / R$ 50 mil) | +19.48 / +19.48 |
| depois do IR (classe exterior) pp, 20k / 50k | +15.19 / +15.19 |
| IR OOS / Sharpe | +0.75 / +0.75 |
| pior queda | -27.2% |
| PBO / Sharpe deflacionado | 35% / +3% |
| leque de parâmetros p5 / mediana / p95 | +7.96 / +16.39 / +27.35 |
| custo 2x / execução t+2 | +9.32 / +21.31 |
| walk-forward | -6.07 |
| sem os 10 melhores negócios | +10.44 |
| placebo p | 0.00 |
| look-ahead (truncamento) | passou |

**10 melhores negócios**

| ativo      |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:-----------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| ICPUSDT    |     -1 | 2021-05-13 00:00:00 | 2021-06-14 00:00:00 |     30 |       77.33 |         3.85 |
| BIOUSDT    |     -1 | 2025-01-06 00:00:00 | 2025-02-04 00:00:00 |     30 |       77.04 |         3.83 |
| PEOPLEUSDT |     -1 | 2021-12-27 00:00:00 | 2022-01-24 00:00:00 |     29 |       74.7  |         3.71 |
| SHIBUSDT   |     -1 | 2021-05-12 00:00:00 | 2021-06-11 00:00:00 |     30 |       74.04 |         3.68 |
| MIRAUSDT   |     -1 | 2025-09-29 00:00:00 | 2025-10-28 00:00:00 |     30 |       72.89 |         3.62 |
| FLMUSDT    |     -1 | 2020-10-01 00:00:00 | 2020-10-30 00:00:00 |     29 |       72.06 |         3.58 |
| SOLVUSDT   |     -1 | 2025-01-20 00:00:00 | 2025-02-18 00:00:00 |     30 |       69.19 |         3.44 |
| XPLUSDT    |     -1 | 2025-09-29 00:00:00 | 2025-10-27 00:00:00 |     30 |       68.75 |         3.41 |
| EDENUSDT   |     -1 | 2025-10-02 00:00:00 | 2025-11-03 00:00:00 |     30 |       67.49 |         3.35 |
| 2ZUSDT     |     -1 | 2025-10-06 00:00:00 | 2025-11-03 00:00:00 |     30 |       66.42 |         3.3  |

**10 piores negócios**

| ativo     |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:----------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| BEAMXUSDT |     -1 | 2023-11-20 00:00:00 | 2023-12-07 00:00:00 |     18 |         -86 |        -4.35 |
| PIXELUSDT |     -1 | 2024-02-21 00:00:00 | 2024-03-12 00:00:00 |     20 |         -86 |        -4.35 |
| TIAUSDT   |     -1 | 2023-11-03 00:00:00 | 2023-11-14 00:00:00 |     12 |         -86 |        -4.35 |
| BARDUSDT  |     -1 | 2025-09-22 00:00:00 | 2025-09-25 00:00:00 |      5 |         -86 |        -4.35 |
| A2ZUSDT   |     -1 | 2025-08-01 00:00:00 | 2025-08-11 00:00:00 |      8 |         -86 |        -4.35 |
| ORDIUSDT  |     -1 | 2023-11-09 00:00:00 | 2023-11-14 00:00:00 |      5 |         -86 |        -4.35 |
| KAITOUSDT |     -1 | 2025-02-24 00:00:00 | 2025-02-28 00:00:00 |      6 |         -86 |        -4.35 |
| AVNTUSDT  |     -1 | 2025-09-17 00:00:00 | 2025-09-23 00:00:00 |      6 |         -86 |        -4.35 |
| WIFUSDT   |     -1 | 2024-03-07 00:00:00 | 2024-03-18 00:00:00 |      9 |         -86 |        -4.35 |
| SENTUSDT  |     -1 | 2026-01-26 00:00:00 | 2026-02-02 00:00:00 |      9 |         -86 |        -4.35 |

**Quem trouxe o retorno (soma por ativo, pp)**

| ativo      |   sum |   count |
|:-----------|------:|--------:|
| ICPUSDT    |  3.85 |       1 |
| BIOUSDT    |  3.83 |       1 |
| PEOPLEUSDT |  3.71 |       1 |
| SHIBUSDT   |  3.68 |       1 |
| MIRAUSDT   |  3.62 |       1 |
| FLMUSDT    |  3.58 |       1 |
| SOLVUSDT   |  3.44 |       1 |
| XPLUSDT    |  3.41 |       1 |
| EDENUSDT   |  3.35 |       1 |
| 2ZUSDT     |  3.3  |       1 |

### Pânico cripto: compra após queda de 15%+ em 24h (liquidações), vende em dias  (`cr_panico`)

**Tese:** compro em R$ a moeda que caiu 15%+ em 24h por liquidação de alavancados e vendo dias depois; isento até R$ 35 mil/mês

**Instrumentos:** [{'onde': 'Binance BR / Mercado Bitcoin', 'ticker': 'BTCBRL, ETHBRL, <alt>USDT via USDTBRL', 'lote': 'fração', 'custo': '0,15% (BTC/ETH) / 0,35% (alts) por lado'}]

**Aplicável:** True — à vista em corretora brasileira, frações; ordem a mercado na hora seguinte ao sinal (alerta de preço no celular)

| métrica | valor |
|---|---|
| OOS desde | 2023-01 |
| retorno OOS a.a. (R$ 20 mil) | 13.6% vs CDI 13.1% |
| ativo OOS pp (R$ 20 mil / R$ 50 mil) | +0.55 / +0.55 |
| depois do IR (classe cripto) pp, 20k / 50k | +0.54 / +0.54 |
| IR OOS / Sharpe | +0.47 / +0.47 |
| pior queda | -0.8% |
| PBO / Sharpe deflacionado | 18% / +5% |
| leque de parâmetros p5 / mediana / p95 | -0.48 / +0.98 / +1.52 |
| custo 2x / execução t+2 | +0.49 / -0.47 |
| walk-forward | +3.91 |
| sem os 10 melhores negócios | -0.10 |
| placebo p | 0.21 |
| look-ahead (truncamento) | passou |

**10 melhores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| ETH     |      1 | 2021-05-24 00:00:00 | 2021-05-25 00:00:00 |      2 |       35.13 |         6.37 |
| ETH     |      1 | 2018-02-05 00:00:00 | 2018-02-07 00:00:00 |      2 |       27.36 |         5.49 |
| BTC     |      1 | 2018-02-06 00:00:00 | 2018-02-08 00:00:00 |      1 |       22.13 |         4.44 |
| BTC     |      1 | 2017-09-15 00:00:00 | 2017-09-18 00:00:00 |      2 |       21.27 |         4.11 |
| ETH     |      1 | 2017-11-30 00:00:00 | 2017-12-04 00:00:00 |      2 |       12.1  |         2.7  |
| ETH     |      1 | 2021-05-19 00:00:00 | 2021-05-21 00:00:00 |      2 |       12.03 |         2.47 |
| ETH     |      1 | 2021-01-22 00:00:00 | 2021-01-25 00:00:00 |      2 |       10    |         2.44 |
| ETH     |      1 | 2022-05-12 00:00:00 | 2022-05-16 00:00:00 |      2 |       10.63 |         2.23 |
| ETH     |      1 | 2017-09-15 00:00:00 | 2017-09-18 00:00:00 |      2 |       11.61 |         2.19 |
| BTC     |      1 | 2019-06-28 00:00:00 | 2019-07-01 00:00:00 |      2 |       11.98 |         2.15 |

**10 piores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| BTC     |      1 | 2020-03-12 00:00:00 | 2020-03-16 00:00:00 |      2 |      -10.2  |        -1.86 |
| ETH     |      1 | 2022-06-13 00:00:00 | 2022-06-15 00:00:00 |      2 |       -8.93 |        -1.78 |
| ETH     |      1 | 2019-07-15 00:00:00 | 2019-07-17 00:00:00 |      2 |       -7.4  |        -1.45 |
| ETH     |      1 | 2018-09-06 00:00:00 | 2018-09-10 00:00:00 |      2 |       -4.55 |        -1.04 |
| ETH     |      1 | 2020-03-12 00:00:00 | 2020-03-16 00:00:00 |      2 |       -5.78 |        -0.96 |
| ETH     |      1 | 2018-01-16 00:00:00 | 2018-01-18 00:00:00 |      2 |       -3.48 |        -0.54 |
| ETH     |      1 | 2021-01-11 00:00:00 | 2021-01-13 00:00:00 |      2 |        0.42 |        -0.26 |
| ETH     |      1 | 2019-09-24 00:00:00 | 2019-09-26 00:00:00 |      2 |        0.14 |        -0.15 |
| ETH     |      1 | 2021-02-23 00:00:00 | 2021-02-25 00:00:00 |      2 |        6.38 |         0.34 |
| ETH     |      1 | 2024-08-05 00:00:00 | 2024-08-07 00:00:00 |      2 |        6.87 |         0.51 |

**Quem trouxe o retorno (soma por ativo, pp)**

| ativo   |   sum |   count |
|:--------|------:|--------:|
| ETH     | 25.52 |      22 |
| BTC     | 11.66 |       7 |
