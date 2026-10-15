# Frente macro_hedge — resultados da bateria final (gerado automaticamente)

Gerado por `pf/gerar_cadernos.py` a partir de `pf/resultados/bateria/`. IR de pessoa física por `pf/ir.py` (mensal na B3 com isenção de ações ≤ R$ 20 mil/mês, anual no exterior). Ordem: nota do ranking.

### Petróleo em pânico: PETR4/PRIO3 x MCL  (`mh_petroleo`)

**Tese:** Compro PETR4/PRIO3 no fracionário quando a ação cai muito mais que o petróleo em reais num pânico de mercado e vendo micro WTI (MCL) na proporção do beta; saio quando o resíduo volta a zero

**Instrumentos:** B3 (Clear/Rico, corretagem zero): PETR4/PRIO3 (lote 100, fracionário PETR4F 1 ação), até 50% do capital por nome; IBKR: MCL (CME micro WTI, 100 barris, margem ~US$ 600–1.000, US$ 0,85 por lado), só a margem remetida (IOF 1,1%); caixa em Tesouro Selic/LFTS11

**Aplicável:** True — Aplicável: PETR4/PRIO3 no fracionário com qualquer capital; o hedge em MCL só sai do zero com R$ 50 mil e petróleo barato (com R$ 20 mil o fundo é, na prática, PETR4/PRIO3 comprado sem hedge nos pânicos)

| métrica | valor |
|---|---|
| OOS desde | 2021-01 |
| retorno OOS a.a. (R$ 20 mil) | 14.4% vs CDI 11.4% |
| ativo OOS pp (R$ 20 mil / R$ 50 mil) | +2.97 / +3.88 |
| depois do IR (classe acoes) pp, 20k / 50k | +2.92 / +3.36 |
| IR OOS / Sharpe | +0.36 / +0.36 |
| pior queda | -7.8% |
| PBO / Sharpe deflacionado | 10% / +38% |
| leque de parâmetros p5 / mediana / p95 | -0.17 / +1.99 / +6.43 |
| custo 2x / execução t+2 | +2.72 / +3.39 |
| walk-forward | +0.37 |
| sem os 10 melhores negócios | -2.41 |
| placebo p | 0.14 |
| look-ahead (truncamento) | passou |

**10 melhores negócios**

| ativo   |   lado | entrada    | saida      |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:-----------|:-----------|-------:|------------:|-------------:|
| PRIO3   |      1 | 2019-08-28 | 2019-09-19 |     17 |       16.9  |         8.69 |
| PETR4   |      1 | 2016-06-01 | 2016-06-21 |     15 |       16.5  |         7.9  |
| PRIO3   |      1 | 2020-03-09 | 2020-04-07 |     22 |       22.28 |         6.92 |
| PETR4   |      1 | 2015-09-14 | 2015-10-09 |     20 |       13.99 |         6.47 |
| PRIO3   |      1 | 2024-05-31 | 2024-07-04 |     25 |       11.51 |         5.07 |
| PETR4   |      1 | 2024-03-11 | 2024-04-10 |     22 |       11.05 |         4.9  |
| PRIO3   |      1 | 2022-06-23 | 2022-07-22 |     22 |       10.75 |         4.55 |
| PETR4   |      1 | 2021-03-08 | 2021-03-24 |     13 |        8.15 |         3.7  |
| PETR4   |      1 | 2022-06-22 | 2022-07-19 |     20 |        8.11 |         3.47 |
| PETR4   |      1 | 2018-09-05 | 2018-09-19 |     10 |        7.13 |         3.37 |

**10 piores negócios**

| ativo   |   lado | entrada    | saida      |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:-----------|:-----------|-------:|------------:|-------------:|
| PETR4   |      1 | 2026-05-26 | 2026-07-06 |     29 |      -11.59 |        -6.56 |
| PETR4   |      1 | 2018-05-29 | 2018-07-03 |     25 |       -9.33 |        -5.7  |
| PRIO3   |      1 | 2023-03-01 | 2023-03-31 |     23 |       -6.56 |        -3.87 |
| PRIO3   |      1 | 2024-10-24 | 2024-12-12 |     34 |       -2.17 |        -1.86 |
| PETR4   |      1 | 2022-11-08 | 2022-12-07 |     21 |       -0.37 |        -0.78 |
| PETR4   |      1 | 2017-06-14 | 2017-07-13 |     21 |        1.98 |         0.52 |
| PRIO3   |      1 | 2025-08-20 | 2025-09-17 |     21 |        2.52 |         0.61 |
| PRIO3   |      1 | 2024-09-13 | 2024-09-25 |      9 |        3.46 |         1.51 |
| PETR4   |      1 | 2024-06-13 | 2024-06-25 |      9 |        4.43 |         1.94 |
| PETR4   |      1 | 2025-04-15 | 2025-05-13 |     18 |        6.16 |         2.48 |

**Quem trouxe o retorno (soma por ativo, pp)**

| ativo   |   sum |   count |
|:--------|------:|--------:|
| PRIO3   | 24.4  |       9 |
| PETR4   | 24.33 |      13 |

### Exportadoras atrasadas vs dólar, hedge WDO+WIN  (`mh_exportadoras`)

**Tese:** Compro SUZB3/KLBN11/VALE3 quando a ação ficou muito abaixo do que o dólar e o Ibovespa explicam e vendo WDO e WIN nos betas; saio quando o resíduo zera

**Instrumentos:** B3 (Clear/Rico): SUZB3/KLBN11/VALE3 no fracionário, 1/3 do capital por nome; WDO (US$ 10 mil, margem ~12%, R$ 1,20 + meio tick por lado, rola todo mês) e WIN (R$ 0,20/ponto, margem ~15%) vendidos; garantia em Tesouro Selic

**Aplicável:** True — Aplicável nas ações (fracionário); o hedge não cabe: com R$ 20 mil o WDO arredonda para zero (fundo vira ação comprada com hedge parcial de WIN), com R$ 50 mil o WDO sai em 0 ou 1 contrato (1 = hedge 2–5x maior que o pedido)

| métrica | valor |
|---|---|
| OOS desde | 2021-01 |
| retorno OOS a.a. (R$ 20 mil) | 11.1% vs CDI 11.4% |
| ativo OOS pp (R$ 20 mil / R$ 50 mil) | -0.32 / -0.93 |
| depois do IR (classe acoes) pp, 20k / 50k | -0.32 / -0.92 |
| IR OOS / Sharpe | -0.04 / -0.04 |
| pior queda | -6.4% |
| PBO / Sharpe deflacionado | 38% / +11% |
| leque de parâmetros p5 / mediana / p95 | -0.71 / +0.83 / +3.63 |
| custo 2x / execução t+2 | -0.42 / -0.59 |
| walk-forward | -1.01 |
| sem os 10 melhores negócios | -0.28 |
| placebo p | 0.48 |
| look-ahead (truncamento) | passou |

**10 melhores negócios**

| ativo   |   lado | entrada    | saida      |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:-----------|:-----------|-------:|------------:|-------------:|
| VALE3   |      1 | 2015-04-14 | 2015-04-27 |      9 |       29.17 |         9.77 |
| SUZB3   |      1 | 2020-07-14 | 2020-08-12 |     22 |       28.83 |         9.58 |
| VALE3   |      1 | 2024-08-15 | 2024-09-27 |     32 |       13.75 |         4.11 |
| FIBR3   |      1 | 2016-07-29 | 2016-09-02 |     26 |       13.85 |         3.92 |
| SUZB3   |      1 | 2024-05-21 | 2024-07-08 |     34 |        8.28 |         2.16 |
| KLBN11  |      1 | 2018-12-03 | 2019-03-06 |     64 |        6.98 |         1.72 |
| VALE3   |      1 | 2023-05-23 | 2023-07-26 |     46 |        7.81 |         1.69 |
| SUZB3   |      1 | 2025-04-07 | 2025-06-06 |     42 |        5.78 |         1.1  |
| KLBN11  |      1 | 2019-04-11 | 2019-07-05 |     59 |        2.85 |         0.43 |
| VALE3   |      1 | 2026-10-08 | 2026-10-13 |      3 |       -0.71 |        -0.31 |

**10 piores negócios**

| ativo   |   lado | entrada    | saida      |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:-----------|:-----------|-------:|------------:|-------------:|
| SUZB3   |      1 | 2026-04-17 | 2026-07-20 |     64 |      -12.59 |        -5.28 |
| KLBN11  |      1 | 2025-03-17 | 2025-06-10 |     59 |       -5.26 |        -2.82 |
| SUZB3   |      1 | 2019-06-03 | 2019-08-30 |     64 |       -6.94 |        -2.79 |
| VALE3   |      1 | 2018-11-27 | 2019-02-26 |     64 |       -5.45 |        -2.38 |
| KLBN11  |      1 | 2016-04-08 | 2016-06-10 |     44 |       -0.63 |        -1    |
| KLBN11  |      1 | 2026-05-04 | 2026-06-19 |     34 |       -0.87 |        -0.91 |
| VALE3   |      1 | 2026-10-08 | 2026-10-13 |      3 |       -0.71 |        -0.31 |
| KLBN11  |      1 | 2019-04-11 | 2019-07-05 |     59 |        2.85 |         0.43 |
| SUZB3   |      1 | 2025-04-07 | 2025-06-06 |     42 |        5.78 |         1.1  |
| VALE3   |      1 | 2023-05-23 | 2023-07-26 |     46 |        7.81 |         1.69 |

**Quem trouxe o retorno (soma por ativo, pp)**

| ativo   |   sum |   count |
|:--------|------:|--------:|
| VALE3   | 12.89 |       5 |
| SUZB3   |  4.77 |       5 |
| FIBR3   |  3.92 |       1 |
| KLBN11  | -2.58 |       5 |

### Margem agro nos futuros B3 -> frigoríficos/SLC/São Martinho  (`mh_agro`)

**Tese:** Compro as ações da cadeia agro cuja margem implícita nos futuros B3 (boi, milho, soja, etanol) e no dólar mais melhorou, antes do balanço; hedge opcional de Ibovespa em WIN

**Instrumentos:** B3 (Clear/Rico): BEEF3, MBRF3 (ex-MRFG3), JBSS3 (até jun/2025), BRFS3 (até set/2025), SLCE3, SMTO3 no fracionário, 1/k do capital cada, rebalanceio mensal; WIN vendido no beta; sinal dos ajustes de BGI/CCM/SJC/ETH (B3) e PTAX

**Aplicável:** True — Aplicável: ações no fracionário; WIN só cabe com o índice baixo ou R$ 50 mil (hedge parcial); os futuros agro como hedge NÃO cabem (BGI R$ 50–130 mil por contrato) — servem como sinal

| métrica | valor |
|---|---|
| OOS desde | 2023-01 |
| retorno OOS a.a. (R$ 20 mil) | -0.2% vs CDI 13.1% |
| ativo OOS pp (R$ 20 mil / R$ 50 mil) | -13.34 / -13.32 |
| depois do IR (classe acoes) pp, 20k / 50k | -13.10 / -13.08 |
| IR OOS / Sharpe | -0.15 / -0.15 |
| pior queda | -46.6% |
| PBO / Sharpe deflacionado | 14% / +3% |
| leque de parâmetros p5 / mediana / p95 | -8.25 / +11.39 / +25.45 |
| custo 2x / execução t+2 | -14.58 / -19.79 |
| walk-forward | +15.71 |
| sem os 10 melhores negócios | -39.31 |
| placebo p | 0.87 |
| look-ahead (truncamento) | passou |

**10 melhores negócios**

| ativo   |   lado | entrada    | saida      |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:-----------|:-----------|-------:|------------:|-------------:|
| BRFS3   |      1 | 2023-04-03 | 2023-08-01 |     83 |       62.83 |        55.18 |
| SLCE3   |      1 | 2019-11-01 | 2020-01-02 |     42 |       40.64 |        40.29 |
| SLCE3   |      1 | 2021-02-01 | 2021-04-01 |     42 |       33.63 |        33.22 |
| BRFS3   |      1 | 2024-03-01 | 2024-06-03 |     64 |       25.82 |        22.34 |
| SLCE3   |      1 | 2020-08-03 | 2021-01-04 |    106 |       22.56 |        21.61 |
| SMTO3   |      1 | 2026-02-02 | 2026-03-02 |     19 |       20.71 |        19.29 |
| SLCE3   |      1 | 2022-02-01 | 2022-05-02 |     61 |       14    |        11.43 |
| SMTO3   |      1 | 2020-02-03 | 2020-03-02 |     19 |       11.06 |        10.42 |
| BRFS3   |      1 | 2022-07-01 | 2022-09-01 |     45 |       11.06 |         8.84 |
| SLCE3   |      1 | 2026-09-01 | 2026-10-13 |     29 |       10.36 |         8.84 |

**10 piores negócios**

| ativo   |   lado | entrada    | saida      |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:-----------|:-----------|-------:|------------:|-------------:|
| BRFS3   |      1 | 2023-02-01 | 2023-03-01 |     19 |      -24.27 |       -27.07 |
| SMTO3   |      1 | 2022-05-02 | 2022-07-01 |     44 |      -18.43 |       -19.76 |
| SMTO3   |      1 | 2026-04-01 | 2026-05-04 |     21 |      -14.66 |       -14.67 |
| SLCE3   |      1 | 2026-05-04 | 2026-06-01 |     21 |      -12.23 |       -13.68 |
| SMTO3   |      1 | 2022-12-01 | 2023-01-02 |     23 |      -12.14 |       -12.71 |
| SMTO3   |      1 | 2024-08-01 | 2024-10-01 |     44 |      -10.06 |       -11.95 |
| SMTO3   |      1 | 2026-06-01 | 2026-07-01 |     22 |       -7.49 |        -8.85 |
| SLCE3   |      1 | 2024-10-01 | 2025-01-02 |     64 |       -5.87 |        -8.78 |
| BRFS3   |      1 | 2024-07-01 | 2024-08-01 |     24 |       -7.17 |        -8.32 |
| SMTO3   |      1 | 2021-07-01 | 2021-09-01 |     45 |       -6.48 |        -7.47 |

**Quem trouxe o retorno (soma por ativo, pp)**

| ativo   |    sum |   count |
|:--------|-------:|--------:|
| SLCE3   |  93.5  |      15 |
| BRFS3   |  42.42 |       8 |
| SMTO3   | -47.64 |      17 |

### Real tático (juro real BR-EUA) em WDO + Brasil após pânico  (`mh_real_tatico`)

**Tese:** Vendo/compro mini-dólar quando o diferencial de juro real Brasil-EUA está extremo vs 5 anos; e compro Brasil (BOVA11/WIN) por 42 pregões depois de pânico brasileiro que não foi global

**Instrumentos:** B3 (Clear/Rico): WDO (US$ 10 mil, margem ~12% em Tesouro Selic, ~R$ 3,70 por contrato e lado com meio tick, rola todo mês); BOVA11 (cotas inteiras; lote/fracionário) ou WIN (R$ 0,20/ponto) no livro de pânico

**Aplicável:** True — Pânico: aplicável com qualquer capital (BOVA11). Juro: só com R$ 50 mil (1 WDO ~ 1x o capital); com R$ 20 mil arredonda para 0 ou vira 2,5x o capital em dólar

| métrica | valor |
|---|---|
| OOS desde | 2021-01 |
| retorno OOS a.a. (R$ 20 mil) | 9.1% vs CDI 11.4% |
| ativo OOS pp (R$ 20 mil / R$ 50 mil) | -2.34 / +4.79 |
| depois do IR (classe acoes) pp, 20k / 50k | -2.30 / +4.71 |
| IR OOS / Sharpe | -0.08 / -0.08 |
| pior queda | -37.6% |
| PBO / Sharpe deflacionado | 45% / +0% |
| leque de parâmetros p5 / mediana / p95 | -2.34 / -2.34 / -2.34 |
| custo 2x / execução t+2 | -2.40 / -2.05 |
| walk-forward | -2.34 |
| sem os 10 melhores negócios | -2.34 |
| placebo p | 0.61 |
| look-ahead (truncamento) | passou |

**10 melhores negócios**

| ativo   |   lado | entrada    | saida      |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:-----------|:-----------|-------:|------------:|-------------:|
| WDO     |      1 | 2017-06-02 | 2021-08-11 |   1052 |       42.46 |        74.45 |
| WDO     |     -1 | 2016-03-24 | 2017-04-17 |    268 |       25.43 |        48.69 |

**10 piores negócios**

| ativo   |   lado | entrada    | saida      |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:-----------|:-----------|-------:|------------:|-------------:|
| WDO     |     -1 | 2016-03-24 | 2017-04-17 |    268 |       25.43 |        48.69 |
| WDO     |      1 | 2017-06-02 | 2021-08-11 |   1052 |       42.46 |        74.45 |

**Quem trouxe o retorno (soma por ativo, pp)**

| ativo   |    sum |   count |
|:--------|-------:|--------:|
| WDO     | 123.14 |       2 |

### Pares intra-setor B3 sem notícia (aluguel PF)  (`mh_pares`)

**Tese:** Vendo a ação que disparou contra a par do mesmo negócio sem notícia e compro a que ficou para trás; saio quando o resíduo zera (aluguel PF real, fracionário)

**Instrumentos:** B3: compra no fracionário e venda a descoberto com aluguel (BTC) de pessoa física — 0,5% do volume por contrato + taxa ao doador; garantia 25% em Tesouro Selic/ações; até 2 pares de 40% do capital por perna

**Aplicável:** True — Aplicável: ações no fracionário e aluguel de PF (Clear/Rico/XP/BTG); 2 pares de ~R$ 8 mil por perna com R$ 20 mil

| métrica | valor |
|---|---|
| OOS desde | 2021-01 |
| retorno OOS a.a. (R$ 20 mil) | 9.3% vs CDI 11.4% |
| ativo OOS pp (R$ 20 mil / R$ 50 mil) | -2.10 / -2.07 |
| depois do IR (classe acoes) pp, 20k / 50k | -2.07 / -2.03 |
| IR OOS / Sharpe | -0.26 / -0.26 |
| pior queda | -8.6% |
| PBO / Sharpe deflacionado | 28% / +0% |
| leque de parâmetros p5 / mediana / p95 | -9.07 / -3.03 / +0.91 |
| custo 2x / execução t+2 | -3.50 / -1.35 |
| walk-forward | -1.90 |
| sem os 10 melhores negócios | -9.41 |
| placebo p | 0.75 |
| look-ahead (truncamento) | passou |

**10 melhores negócios**

| ativo   |   lado | entrada    | saida      |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:-----------|:-----------|-------:|------------:|-------------:|
| GUAR3   |     -1 | 2022-02-07 | 2022-03-11 |     23 |       24.86 |         9.67 |
| CEAB3   |     -1 | 2023-01-31 | 2023-02-28 |     19 |       32.21 |         8.27 |
| ITUB4   |     -1 | 2022-10-05 | 2022-11-11 |     26 |       10.25 |         6.75 |
| CPFE3   |     -1 | 2022-05-13 | 2022-06-13 |     22 |       10.68 |         4.51 |
| SANB11  |     -1 | 2018-06-06 | 2018-07-02 |     19 |       14.44 |         3.54 |
| BBDC4   |     -1 | 2022-02-04 | 2022-02-11 |      6 |        7.81 |         2.94 |
| GUAR3   |     -1 | 2023-06-26 | 2023-08-04 |     30 |        9.14 |         2.72 |
| CPFE3   |     -1 | 2026-05-08 | 2026-06-22 |     31 |        9.34 |         1.99 |
| ENGI11  |     -1 | 2026-03-13 | 2026-03-20 |      6 |        6.54 |         1.9  |
| BBDC4   |     -1 | 2020-04-23 | 2020-05-05 |      8 |        5.33 |         1.87 |

**10 piores negócios**

| ativo   |   lado | entrada    | saida      |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:-----------|:-----------|-------:|------------:|-------------:|
| ITUB4   |      1 | 2021-10-05 | 2021-11-19 |     31 |      -10.56 |        -8.37 |
| CEAB3   |      1 | 2022-02-07 | 2022-03-11 |     23 |      -24.79 |        -8.16 |
| ITUB4   |     -1 | 2026-09-22 | 2026-10-13 |     15 |      -15.1  |        -6.52 |
| BBDC4   |      1 | 2022-11-08 | 2022-11-10 |      3 |      -19.81 |        -6.32 |
| GUAR3   |      1 | 2023-01-31 | 2023-02-28 |     19 |      -13.33 |        -5.87 |
| ITUB4   |     -1 | 2025-04-25 | 2025-05-19 |     16 |      -10.83 |        -4.28 |
| BBAS3   |      1 | 2025-04-25 | 2025-05-19 |     16 |      -10.6  |        -3.64 |
| CMIG4   |      1 | 2026-05-08 | 2026-06-22 |     31 |       -7.05 |        -3.52 |
| BBDC4   |      1 | 2018-06-06 | 2018-07-02 |     19 |       -5.98 |        -2.58 |
| SANB11  |      1 | 2026-01-28 | 2026-02-13 |     13 |       -8    |        -2.3  |

**Quem trouxe o retorno (soma por ativo, pp)**

| ativo   |   sum |   count |
|:--------|------:|--------:|
| CPFE3   |  7.06 |       3 |
| GUAR3   |  6.53 |       3 |
| TAEE11  |  3.99 |       3 |
| SANB11  |  3.22 |       8 |
| CEAB3   |  0.7  |       3 |
| ENGI11  |  0.18 |       2 |
| BBAS3   | -1.28 |       5 |
| BBDC4   | -1.79 |       7 |
| LREN3   | -1.86 |       1 |
| ISAE4   | -1.88 |       3 |

### Fato relevante (não-balanço) em large caps, beta em WIN  (`mh_evento_beta`)

**Tese:** Sigo a reação a fato relevante que não é balanço em large caps (comprado se a ação subiu >= thr vs Ibovespa, vendido com aluguel PF se caiu) por N pregões, com o beta líquido travado em mini-índice inteiro

**Instrumentos:** B3 (Clear/Rico): ações com ADV >= R$ 50 mi no fracionário, 20% do capital por evento, vendido via BTC de PF (0,5% por contrato + ~1% a.a.); WIN no beta líquido (R$ 0,20/ponto, margem ~15% em Tesouro Selic); sinal = FR na CVM (data de entrega)

**Aplicável:** True — Aplicável: large caps no fracionário e aluguel PF barato; o hedge WIN arredonda para 0 com R$ 20 mil (exposição líquida < meio contrato) e funciona em parte com R$ 50 mil

| métrica | valor |
|---|---|
| OOS desde | 2021-01 |
| retorno OOS a.a. (R$ 20 mil) | -3.1% vs CDI 11.4% |
| ativo OOS pp (R$ 20 mil / R$ 50 mil) | -14.58 / -12.49 |
| depois do IR (classe acoes) pp, 20k / 50k | -14.36 / -12.30 |
| IR OOS / Sharpe | -0.67 / -0.67 |
| pior queda | -43.1% |
| PBO / Sharpe deflacionado | 48% / +0% |
| leque de parâmetros p5 / mediana / p95 | -14.12 / -4.68 / +7.77 |
| custo 2x / execução t+2 | -16.97 / -13.03 |
| walk-forward | -9.37 |
| sem os 10 melhores negócios | -25.98 |
| placebo p | 0.95 |
| look-ahead (truncamento) | passou |

**10 melhores negócios**

| ativo   |   lado | entrada    | saida      |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:-----------|:-----------|-------:|------------:|-------------:|
| WIN     |      1 | 2016-01-14 | 2016-06-09 |    101 |       22.81 |        22.97 |
| WIN     |     -1 | 2018-04-23 | 2018-06-20 |     41 |       16.57 |        14.24 |
| BHIA3   |      1 | 2020-05-06 | 2020-07-02 |     41 |       53.75 |        10.93 |
| WIN     |     -1 | 2014-09-02 | 2014-10-28 |     41 |       16.83 |        10.47 |
| BHIA3   |      1 | 2019-12-04 | 2020-01-31 |     41 |       48.15 |         9.36 |
| IRBR3   |     -1 | 2020-03-06 | 2020-05-06 |     41 |       44.17 |         8.96 |
| WIN     |     -1 | 2021-10-18 | 2021-10-27 |      8 |        7.2  |         8.24 |
| BIDI11  |     -1 | 2021-11-24 | 2022-01-19 |     41 |       37.85 |         7.87 |
| WIN     |      1 | 2021-12-02 | 2022-03-04 |     65 |        7.08 |         7.47 |
| CVCB3   |     -1 | 2020-03-03 | 2020-04-30 |     41 |       38.69 |         7.45 |

**10 piores negócios**

| ativo   |   lado | entrada    | saida      |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:-----------|:-----------|-------:|------------:|-------------:|
| SUZB3   |     -1 | 2018-03-13 | 2018-05-10 |     41 |      -85.59 |       -17.43 |
| MRVE3   |     -1 | 2023-04-26 | 2023-06-23 |     41 |      -70.55 |       -14.63 |
| VALE5   |     -1 | 2016-02-25 | 2016-04-25 |     41 |      -73.74 |       -13.6  |
| VALE3   |     -1 | 2016-02-25 | 2016-04-25 |     41 |      -63.88 |       -11.63 |
| COGN3   |      1 | 2020-02-14 | 2020-04-15 |     41 |      -55.17 |       -11.02 |
| WIN     |     -1 | 2022-06-17 | 2022-08-12 |     41 |      -10.76 |       -10.97 |
| WIN     |     -1 | 2018-12-19 | 2019-02-15 |     41 |      -12.72 |       -10.95 |
| GOLL4   |      1 | 2020-01-10 | 2020-03-10 |     41 |      -50.81 |       -10.46 |
| WIN     |     -1 | 2020-11-10 | 2020-12-14 |     25 |       -8.94 |        -9.45 |
| PETR3   |      1 | 2020-02-10 | 2020-04-08 |     41 |      -44.59 |        -9.05 |

**Quem trouxe o retorno (soma por ativo, pp)**

| ativo   |   sum |   count |
|:--------|------:|--------:|
| WIN     | 41.84 |      68 |
| BHIA3   | 20.29 |       2 |
| GGBR4   |  9.62 |       4 |
| YDUQ3   |  9.12 |       3 |
| SBSP3   |  7.51 |       5 |
| RECV3   |  7.15 |       1 |
| CSMG3   |  7.09 |       2 |
| RENT3   |  6.87 |       2 |
| CMIG4   |  6.86 |       6 |
| RADL3   |  5.98 |       2 |

### Fuso EWZ/ADR x B3 no leilão de abertura (day trade)  (`mh_fuso_ewz`)

**Tese:** Depois de ver o EWZ/ADRs fecharem em NY, compro (ou vendo) BOVA11/PETR4/VALE3 no leilão de abertura e zero no leilão de fechamento: pega a parte do movimento noturno que a abertura não precificou

**Instrumentos:** B3 (Clear/Rico, corretagem zero): ordem no leilão de abertura (10h) e no de fechamento (16h55–17h) do mesmo dia, BOVA11 (cotas inteiras) ou PETR4/VALE3; venda a descoberto intradiária sem aluguel; caixa todo o tempo em Tesouro Selic (garantia)

**Aplicável:** True — Aplicável: BOVA11/PETR4/VALE3 em day trade com qualquer capital (leilões de abertura e fechamento); IR de day trade 20%

| métrica | valor |
|---|---|
| OOS desde | 2021-01 |
| retorno OOS a.a. (R$ 20 mil) | -1.2% vs CDI 11.4% |
| ativo OOS pp (R$ 20 mil / R$ 50 mil) | -12.60 / -12.64 |
| depois do IR (classe acoes) pp, 20k / 50k | -12.41 / -12.44 |
| IR OOS / Sharpe | -0.81 / -0.81 |
| pior queda | -37.5% |
| PBO / Sharpe deflacionado | 9% / +0% |
| leque de parâmetros p5 / mediana / p95 | -16.20 / -11.66 / -6.68 |
| custo 2x / execução t+2 | -18.95 / -1.56 |
| walk-forward | -9.86 |
| sem os 10 melhores negócios | -19.16 |
| placebo p | 0.88 |
| look-ahead (truncamento) | passou |

**10 melhores negócios**

| ativo   |   lado | entrada    | saida      |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:-----------|:-----------|-------:|------------:|-------------:|
| VALE3   |      1 | 2015-04-30 | 2015-04-30 |      1 |        9.95 |         9.86 |
| PETR4   |      1 | 2018-06-19 | 2018-06-19 |      1 |        8.13 |         8.05 |
| PETR4   |     -1 | 2015-05-06 | 2015-05-06 |      1 |        7.53 |         7.43 |
| VALE3   |     -1 | 2016-05-20 | 2016-05-20 |      1 |        7.34 |         7.26 |
| VALE3   |      1 | 2019-02-08 | 2019-02-08 |      1 |        6.2  |         6.11 |
| PETR4   |     -1 | 2018-06-21 | 2018-06-21 |      1 |        6.15 |         6.07 |
| VALE3   |     -1 | 2016-12-19 | 2016-12-19 |      1 |        5.96 |         5.87 |
| PETR4   |     -1 | 2014-10-23 | 2014-10-23 |      1 |        5.86 |         5.77 |
| PETR4   |     -1 | 2018-10-03 | 2018-10-03 |      1 |        5.78 |         5.7  |
| PETR4   |     -1 | 2020-04-16 | 2020-04-16 |      1 |        5.7  |         5.61 |

**10 piores negócios**

| ativo   |   lado | entrada    | saida      |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:-----------|:-----------|-------:|------------:|-------------:|
| PETR4   |      1 | 2018-06-01 | 2018-06-01 |      1 |      -17.38 |       -17.46 |
| VALE3   |     -1 | 2015-05-05 | 2015-05-05 |      1 |       -8.76 |        -8.84 |
| PETR4   |     -1 | 2014-03-27 | 2014-03-27 |      1 |       -8.2  |        -8.28 |
| PETR4   |     -1 | 2015-08-27 | 2015-08-27 |      1 |       -7.76 |        -7.84 |
| PETR4   |      1 | 2021-02-25 | 2021-02-25 |      1 |       -7.24 |        -7.33 |
| PETR4   |     -1 | 2018-05-09 | 2018-05-09 |      1 |       -6.35 |        -6.44 |
| PETR4   |     -1 | 2014-05-02 | 2014-05-02 |      1 |       -6.34 |        -6.43 |
| VALE3   |     -1 | 2016-04-20 | 2016-04-20 |      1 |       -5.79 |        -5.87 |
| VALE3   |      1 | 2020-04-03 | 2020-04-03 |      1 |       -5.37 |        -5.46 |
| VALE3   |      1 | 2015-08-07 | 2015-08-07 |      1 |       -5.3  |        -5.38 |

**Quem trouxe o retorno (soma por ativo, pp)**

| ativo   |    sum |   count |
|:--------|-------:|--------:|
| PETR4   |  46.7  |     930 |
| VALE3   | -37.14 |     722 |
| BOVA11  | -45.92 |     601 |
