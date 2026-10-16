# Frente pf2_juros_fx — resultados da bateria final (gerado automaticamente)

Gerado por `pf/gerar_cadernos.py` a partir de `pf/resultados/bateria/`. IR de pessoa física por `pf/ir.py` (mensal na B3 com isenção de ações ≤ R$ 20 mil/mês, anual no exterior). Ordem: nota do ranking.

### Tesouro Direto após abertura forte de taxa (regime Copom)  (`jx_td_copom`)

**Tese:** Compro Tesouro Prefixado/IPCA+ no Tesouro Direto depois que a taxa abre forte em 1 mês (vendedor forçado) se o Copom não está subindo juro; vendo de volta ao Tesouro quando metade do choque devolve

**Instrumentos:** [{'onde': 'Tesouro Direto', 'ticker': 'Tesouro Prefixado ~3 anos / Tesouro IPCA+ ~10 anos', 'lote': '0,01 título; mínimo R$ 30', 'custo': 'spread compra/recompra 0,12 pp de taxa (~0,3% do PU no pré de 3 anos, ~1% no IPCA+ de 10 anos); custódia 0,20% a.a.'}]

**Aplicável:** True — Tesouro Direto: qualquer valor, recompra diária garantida (exceto quando o Tesouro suspende o mercado em volatilidade extrema).

| métrica | valor |
|---|---|
| OOS desde | 2021-01 |
| retorno OOS a.a. (R$ 20 mil) | 11.7% vs CDI 11.4% |
| ativo OOS pp (R$ 20 mil / R$ 50 mil) | +0.24 / +0.24 |
| depois do IR (classe renda_fixa) pp, 20k / 50k | +0.19 / +0.19 |
| IR OOS / Sharpe | +0.11 / +0.11 |
| pior queda | -2.7% |
| PBO / Sharpe deflacionado | 7% / +14% |
| leque de parâmetros p5 / mediana / p95 | -3.84 / +0.06 / +0.27 |
| custo 2x / execução t+2 | -0.24 / -0.24 |
| walk-forward | +0.24 |
| sem os 10 melhores negócios | -0.15 |
| placebo p | 0.02 |
| look-ahead (truncamento) | passou |

**10 melhores negócios**

| ativo     |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:----------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| IPC202608 |      1 | 2020-03-19 00:00:00 | 2020-04-14 00:00:00 |     18 |        5.95 |         5.69 |
| IPC202408 |      1 | 2012-06-06 00:00:00 | 2012-07-18 00:00:00 |     30 |        4.25 |         3.32 |
| IPC203505 |      1 | 2020-09-30 00:00:00 | 2020-11-10 00:00:00 |     28 |        3.3  |         3.1  |
| IPC202408 |      1 | 2013-02-13 00:00:00 | 2013-03-08 00:00:00 |     18 |        3.51 |         3.05 |
| IPC202408 |      1 | 2015-12-22 00:00:00 | 2016-02-26 00:00:00 |     45 |        5.21 |         2.87 |
| IPC202408 |      1 | 2014-09-30 00:00:00 | 2014-10-07 00:00:00 |      6 |        2.97 |         2.76 |
| IPC202408 |      1 | 2017-05-19 00:00:00 | 2017-05-24 00:00:00 |      4 |        2.68 |         2.55 |
| IPC201505 |      1 | 2008-04-08 00:00:00 | 2008-05-06 00:00:00 |     19 |        3.24 |         2.47 |
| IPC202408 |      1 | 2016-11-14 00:00:00 | 2016-12-01 00:00:00 |     13 |        2.95 |         2.32 |
| IPC203505 |      1 | 2026-06-09 00:00:00 | 2026-06-16 00:00:00 |      6 |        1.63 |         1.36 |

**10 piores negócios**

| ativo     |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:----------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| IPC202608 |      1 | 2020-03-17 00:00:00 | 2020-03-18 00:00:00 |      2 |       -2.5  |        -2.52 |
| IPC202408 |      1 | 2018-05-21 00:00:00 | 2018-08-17 00:00:00 |     64 |        0.53 |        -1    |
| IPC202608 |      1 | 2020-03-13 00:00:00 | 2020-03-16 00:00:00 |      2 |       -0.42 |        -0.43 |
| IPC202408 |      1 | 2017-06-16 00:00:00 | 2017-07-18 00:00:00 |     23 |        1.2  |         0.36 |
| IPC203505 |      1 | 2023-09-28 00:00:00 | 2023-11-20 00:00:00 |     35 |        2.44 |         0.84 |
| IPC201505 |      1 | 2009-04-23 00:00:00 | 2009-05-14 00:00:00 |     15 |        1.76 |         1.21 |
| IPC201505 |      1 | 2008-03-26 00:00:00 | 2008-04-07 00:00:00 |      9 |        1.64 |         1.3  |
| IPC203505 |      1 | 2026-06-09 00:00:00 | 2026-06-16 00:00:00 |      6 |        1.63 |         1.36 |
| IPC202408 |      1 | 2016-11-14 00:00:00 | 2016-12-01 00:00:00 |     13 |        2.95 |         2.32 |
| IPC201505 |      1 | 2008-04-08 00:00:00 | 2008-05-06 00:00:00 |     19 |        3.24 |         2.47 |

**Quem trouxe o retorno (soma por ativo, pp)**

| ativo     |   sum |   count |
|:----------|------:|--------:|
| IPC202408 | 16.23 |       8 |
| IPC203505 |  5.3  |       3 |
| IPC201505 |  4.98 |       3 |
| IPC202608 |  2.74 |       3 |

### Euro x dólar na B3 (WEU vs WDO) pelo ciclo Fed x BCE  (`jx_weu_wdo`)

**Tese:** Compro euro contra dólar (WEU comprado, WDO vendido) quando o Fed corta relativo ao BCE e vendo no contrário, confirmado pela tendência; tudo na B3 em R$, sem remessa nem saldo na IBKR

**Instrumentos:** [{'onde': 'B3', 'ticker': 'WEU (mini-euro, EUR 10 mil)', 'lote': '1 contrato', 'custo': 'R$ 6 por lado (livro raso), rolagem mensal'}, {'onde': 'B3', 'ticker': 'WDO (mini-dólar, USD 10 mil)', 'lote': '1 contrato', 'custo': 'R$ 3,70 por lado, rolagem mensal'}]

**Aplicável:** True — 1 par WEU/WDO = ~R$ 60–65 mil de EUR/USD: com R$ 20 mil é 3x o capital (vol ~20% a.a. do capital); com R$ 50 mil, ~1,2x. WEU tem pouca liquidez (poucos contratos/dia): ordem limitada no meio do livro.

| métrica | valor |
|---|---|
| OOS desde | 2021-01 |
| retorno OOS a.a. (R$ 20 mil) | 6.3% vs CDI 11.4% |
| ativo OOS pp (R$ 20 mil / R$ 50 mil) | -5.15 / -0.95 |
| depois do IR (classe futuros_b3) pp, 20k / 50k | -5.79 / -1.23 |
| IR OOS / Sharpe | -0.00 / -0.00 |
| pior queda | -30.4% |
| PBO / Sharpe deflacionado | 12% / +11% |
| leque de parâmetros p5 / mediana / p95 | -11.13 / -7.13 / +1.18 |
| custo 2x / execução t+2 | -6.29 / -3.77 |
| walk-forward | -5.15 |
| sem os 10 melhores negócios | -6.12 |
| placebo p | 0.71 |
| look-ahead (truncamento) | passou |

**10 melhores negócios**

| ativo             |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:------------------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| EUR/USD (WEU-WDO) |      1 | 2019-09-30 00:00:00 | 2021-03-18 00:00:00 |    367 |       25.57 |        25.57 |
| EUR/USD (WEU-WDO) |     -1 | 2022-03-17 00:00:00 | 2023-06-20 00:00:00 |    315 |       24.02 |        24.02 |
| EUR/USD (WEU-WDO) |     -1 | 2009-03-17 00:00:00 | 2010-05-14 00:00:00 |    290 |       20.53 |        20.53 |
| EUR/USD (WEU-WDO) |      1 | 2024-07-30 00:00:00 | 2024-08-05 00:00:00 |      4 |        6.8  |         6.8  |
| EUR/USD (WEU-WDO) |     -1 | 2024-09-18 00:00:00 | 2025-12-18 00:00:00 |    315 |        5.77 |         5.77 |
| EUR/USD (WEU-WDO) |     -1 | 2015-12-17 00:00:00 | 2019-09-19 00:00:00 |    941 |        2.54 |         2.54 |
| EUR/USD (WEU-WDO) |     -1 | 2025-12-19 00:00:00 | 2026-02-05 00:00:00 |     32 |        1.67 |         1.67 |
| EUR/USD (WEU-WDO) |     -1 | 2012-04-13 00:00:00 | 2014-11-13 00:00:00 |    652 |       -1.36 |        -1.36 |
| EUR/USD (WEU-WDO) |     -1 | 2023-07-28 00:00:00 | 2023-07-31 00:00:00 |      1 |       -2.21 |        -2.21 |
| EUR/USD (WEU-WDO) |      1 | 2023-06-20 00:00:00 | 2023-07-28 00:00:00 |     28 |       -3.17 |        -3.17 |

**10 piores negócios**

| ativo             |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:------------------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| EUR/USD (WEU-WDO) |      1 | 2026-03-12 00:00:00 | 2026-10-13 00:00:00 |    147 |      -16.65 |       -16.65 |
| EUR/USD (WEU-WDO) |      1 | 2011-04-13 00:00:00 | 2011-12-14 00:00:00 |    168 |       -9.38 |        -9.38 |
| EUR/USD (WEU-WDO) |      1 | 2008-12-30 00:00:00 | 2009-03-17 00:00:00 |     52 |       -7.35 |        -7.35 |
| EUR/USD (WEU-WDO) |      1 | 2023-09-20 00:00:00 | 2024-06-24 00:00:00 |    188 |       -5.35 |        -5.35 |
| EUR/USD (WEU-WDO) |      1 | 2023-07-31 00:00:00 | 2023-09-15 00:00:00 |     33 |       -5.29 |        -5.29 |
| EUR/USD (WEU-WDO) |      1 | 2023-06-20 00:00:00 | 2023-07-28 00:00:00 |     28 |       -3.17 |        -3.17 |
| EUR/USD (WEU-WDO) |     -1 | 2023-07-28 00:00:00 | 2023-07-31 00:00:00 |      1 |       -2.21 |        -2.21 |
| EUR/USD (WEU-WDO) |     -1 | 2012-04-13 00:00:00 | 2014-11-13 00:00:00 |    652 |       -1.36 |        -1.36 |
| EUR/USD (WEU-WDO) |     -1 | 2025-12-19 00:00:00 | 2026-02-05 00:00:00 |     32 |        1.67 |         1.67 |
| EUR/USD (WEU-WDO) |     -1 | 2015-12-17 00:00:00 | 2019-09-19 00:00:00 |    941 |        2.54 |         2.54 |

**Quem trouxe o retorno (soma por ativo, pp)**

| ativo             |   sum |   count |
|:------------------|------:|--------:|
| EUR/USD (WEU-WDO) | 36.12 |      15 |

### Tesouro Renda+/Educa+ contra a curva de NTN-B  (`jx_renda_educa`)

**Tese:** Compro Renda+/Educa+ (títulos só de pessoa física) quando pagam prêmio sobre a NTN-B de mesma duration e vendo quando o prêmio some — hedge em DAP é grande demais para o PF

**Instrumentos:** [{'onde': 'Tesouro Direto', 'ticker': 'Tesouro Renda+ 20XX / Tesouro Educa+ 20XX', 'lote': '0,01 título; mínimo R$ 30', 'custo': 'spread de compra/recompra 0,4% (Educa+ curto) a 5% (Renda+ 2084) do PU; custódia 0,20% a.a. (isenção de custódia só para quem leva Renda+/Educa+ até a conversão)'}]

**Aplicável:** True — Títulos acessíveis a qualquer CPF a partir de R$ 30; o hedge em DAP não cabe (ver docstring).

| métrica | valor |
|---|---|
| OOS desde | 2025-01 |
| retorno OOS a.a. (R$ 20 mil) | 13.8% vs CDI 14.3% |
| ativo OOS pp (R$ 20 mil / R$ 50 mil) | -0.58 / -0.58 |
| depois do IR (classe renda_fixa) pp, 20k / 50k | -0.57 / -0.57 |
| IR OOS / Sharpe | -0.07 / -0.07 |
| pior queda | -4.0% |
| PBO / Sharpe deflacionado | 91% / +8% |
| leque de parâmetros p5 / mediana / p95 | -2.43 / -0.17 / -0.17 |
| custo 2x / execução t+2 | -1.43 / -1.74 |
| walk-forward | -0.58 |
| sem os 10 melhores negócios | -0.89 |
| placebo p | 0.16 |
| look-ahead (truncamento) | passou |

**10 melhores negócios**

| ativo      |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:-----------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| Renda+2064 |      1 | 2023-01-31 00:00:00 | 2024-02-05 00:00:00 |    253 |       32.57 |        18.17 |
| Renda+2049 |      1 | 2026-09-10 00:00:00 | 2026-10-01 00:00:00 |     16 |        1.32 |         0.55 |
| Renda+2049 |      1 | 2024-12-18 00:00:00 | 2025-03-12 00:00:00 |     57 |       -2.86 |        -5.4  |
| Renda+2079 |      1 | 2024-07-08 00:00:00 | 2024-09-30 00:00:00 |     61 |       -4.53 |        -6.98 |
| Renda+2079 |      1 | 2024-05-16 00:00:00 | 2024-07-03 00:00:00 |     34 |      -15.58 |       -16.82 |
| Renda+2079 |      1 | 2024-02-05 00:00:00 | 2024-05-03 00:00:00 |     61 |      -18.15 |       -20.45 |

**10 piores negócios**

| ativo      |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:-----------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| Renda+2079 |      1 | 2024-02-05 00:00:00 | 2024-05-03 00:00:00 |     61 |      -18.15 |       -20.45 |
| Renda+2079 |      1 | 2024-05-16 00:00:00 | 2024-07-03 00:00:00 |     34 |      -15.58 |       -16.82 |
| Renda+2079 |      1 | 2024-07-08 00:00:00 | 2024-09-30 00:00:00 |     61 |       -4.53 |        -6.98 |
| Renda+2049 |      1 | 2024-12-18 00:00:00 | 2025-03-12 00:00:00 |     57 |       -2.86 |        -5.4  |
| Renda+2049 |      1 | 2026-09-10 00:00:00 | 2026-10-01 00:00:00 |     16 |        1.32 |         0.55 |
| Renda+2064 |      1 | 2023-01-31 00:00:00 | 2024-02-05 00:00:00 |    253 |       32.57 |        18.17 |

**Quem trouxe o retorno (soma por ativo, pp)**

| ativo      |    sum |   count |
|:-----------|-------:|--------:|
| Renda+2064 |  18.17 |       1 |
| Renda+2049 |  -4.85 |       2 |
| Renda+2079 | -44.24 |       3 |

### Debêntures boas na onda de resgates (lote pequeno, secundário)  (`jx_deb_evento`)

**Tese:** Compro em lote de R$ 1 mil debêntures que estavam no par e caíram 2–3 pts enquanto o mercado todo caía (fundos de crédito vendendo o que tem liquidez), sem RJ; vendo quando o preço volta

**Instrumentos:** [{'onde': 'XP/BTG/Inter/Rico (prateleira de secundário) ou mesa/assessor', 'ticker': 'debêntures DI / incentivadas IPCA+', 'lote': '1 debênture (PU ~R$ 1 mil)', 'custo': 'markup max(0,2%; 0,40% x duration) na compra, max(0,15%; 0,15% x duration) na venda'}]

**Aplicável:** parcial — Os papéis bons seguem na prateleira, mas no pico do estresse a corretora alarga o markup e parte dos papéis é ICVM 476 (só qualificado). Lote de R$ 1 mil é o edge; o preço de referência é o negócio >= R$ 100 mil do SND (o varejo paga o markup medido).

| métrica | valor |
|---|---|
| OOS desde | 2023-01 |
| retorno OOS a.a. (R$ 20 mil) | 10.9% vs CDI 13.1% |
| ativo OOS pp (R$ 20 mil / R$ 50 mil) | -2.22 / -2.71 |
| depois do IR (classe isento) pp, 20k / 50k | -2.18 / -2.66 |
| IR OOS / Sharpe | -0.16 / -0.16 |
| pior queda | -5.8% |
| PBO / Sharpe deflacionado | 61% / +13% |
| leque de parâmetros p5 / mediana / p95 | -6.21 / -3.38 / -1.45 |
| custo 2x / execução t+2 | -4.26 / -2.56 |
| walk-forward | -3.44 |
| sem os 10 melhores negócios | -2.75 |
| placebo p | 0.00 |
| look-ahead (truncamento) | passou |

**10 melhores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| TOME12  |      1 | 2019-08-13 00:00:00 | 2020-08-25 00:00:00 |    262 |       12.12 |         1.48 |
| CCROB6  |      1 | 2023-02-09 00:00:00 | 2024-02-14 00:00:00 |    251 |       19.93 |         1.39 |
| COCE18  |      1 | 2023-02-09 00:00:00 | 2024-02-16 00:00:00 |    253 |       19.14 |         1.18 |
| CTEE29  |      1 | 2023-02-09 00:00:00 | 2024-02-16 00:00:00 |    253 |       16.06 |         0.7  |
| OMNG12  |      1 | 2019-07-24 00:00:00 | 2020-07-27 00:00:00 |    255 |        7.88 |         0.58 |
| CCLS11  |      1 | 2025-01-13 00:00:00 | 2025-09-01 00:00:00 |    160 |       11.34 |         0.47 |
| PETR17  |      1 | 2021-05-14 00:00:00 | 2021-07-27 00:00:00 |     52 |        1.83 |         0.17 |
| MRSAB2  |      1 | 2025-01-10 00:00:00 | 2025-10-02 00:00:00 |    184 |       10.32 |         0.12 |
| TAEE17  |      1 | 2025-01-09 00:00:00 | 2025-08-01 00:00:00 |    141 |        6    |        -0.14 |
| TAEE17  |      1 | 2022-08-05 00:00:00 | 2023-08-08 00:00:00 |    253 |       11.12 |        -0.2  |

**10 piores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| CMIN12  |      1 | 2025-11-12 00:00:00 | 2026-10-08 00:00:00 |    227 |      -16.25 |        -4.14 |
| SUMI19  |      1 | 2025-11-12 00:00:00 | 2026-10-08 00:00:00 |    227 |       -2.35 |        -2.62 |
| JTEE12  |      1 | 2021-12-01 00:00:00 | 2022-12-05 00:00:00 |    255 |       -3.5  |        -2.47 |
| RUMOB5  |      1 | 2021-05-17 00:00:00 | 2022-05-16 00:00:00 |    252 |       -3.69 |        -2.08 |
| PETR28  |      1 | 2025-11-12 00:00:00 | 2026-10-08 00:00:00 |    227 |        1.89 |        -1.57 |
| ARTR19  |      1 | 2021-12-01 00:00:00 | 2022-12-01 00:00:00 |    253 |        2.37 |        -1.46 |
| EGIE27  |      1 | 2019-07-24 00:00:00 | 2020-07-23 00:00:00 |    253 |       -2.98 |        -1.28 |
| EGIE19  |      1 | 2021-12-01 00:00:00 | 2022-12-01 00:00:00 |    253 |        4.18 |        -1.2  |
| RUMOB6  |      1 | 2025-11-14 00:00:00 | 2026-10-08 00:00:00 |    225 |        5.23 |        -0.98 |
| RUMOB5  |      1 | 2025-01-09 00:00:00 | 2025-09-26 00:00:00 |    181 |        5.94 |        -0.68 |

**Quem trouxe o retorno (soma por ativo, pp)**

| ativo   |   sum |   count |
|:--------|------:|--------:|
| TOME12  |  1.48 |       1 |
| CCROB6  |  1.39 |       1 |
| COCE18  |  1.18 |       1 |
| CTEE29  |  0.7  |       1 |
| OMNG12  |  0.58 |       1 |
| CCLS11  |  0.47 |       1 |
| PETR17  |  0.17 |       1 |
| MRSAB2  |  0.12 |       1 |
| PPTE11  | -0.21 |       1 |
| EQSP21  | -0.22 |       1 |

### Tesouro Selic com deságio (LFT longa acima da Selic)  (`jx_lft_desagio`)

**Tese:** Compro a LFT longa no Tesouro Direto quando ela paga Selic + spread (bancos vendendo por limite de risco) e vendo de volta ao Tesouro quando o deságio fecha; carry + fechamento sem risco de crédito

**Instrumentos:** [{'onde': 'Tesouro Direto (qualquer corretora, taxa zero)', 'ticker': 'Tesouro Selic 20XX (LFT) mais longo', 'lote': '0,01 título (~R$ 170); mínimo R$ 30', 'custo': 'spread compra/recompra ~0,01–0,03 pp de taxa; custódia 0,20% a.a. acima de R$ 10 mil'}]

**Aplicável:** True — Tesouro Direto aceita qualquer valor e recompra todo dia útil ao PU de venda publicado.

| métrica | valor |
|---|---|
| OOS desde | 2021-01 |
| retorno OOS a.a. (R$ 20 mil) | 11.3% vs CDI 11.4% |
| ativo OOS pp (R$ 20 mil / R$ 50 mil) | -0.15 / -0.21 |
| depois do IR (classe renda_fixa) pp, 20k / 50k | -0.14 / -0.20 |
| IR OOS / Sharpe | -1.27 / -1.27 |
| pior queda | -0.0% |
| PBO / Sharpe deflacionado | 17% / +0% |
| leque de parâmetros p5 / mediana / p95 | -0.08 / -0.08 / -0.08 |
| custo 2x / execução t+2 | -0.29 / -0.14 |
| walk-forward | -0.08 |
| sem os 10 melhores negócios | -0.16 |
| placebo p | 0.00 |
| look-ahead (truncamento) | passou |

**10 melhores negócios**

| ativo     |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:----------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| LFT202903 |      1 | 2025-09-03 00:00:00 | 2026-08-11 00:00:00 |    236 |       12.84 |         0.05 |
| LFT202303 |      1 | 2020-09-30 00:00:00 | 2022-09-05 00:00:00 |    486 |       12.49 |         0.05 |
| LFT202603 |      1 | 2023-04-17 00:00:00 | 2025-09-03 00:00:00 |    599 |       27.79 |         0.02 |
| LFT202503 |      1 | 2022-09-05 00:00:00 | 2022-12-09 00:00:00 |     66 |        3.31 |         0    |

**10 piores negócios**

| ativo     |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:----------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| LFT202503 |      1 | 2022-09-05 00:00:00 | 2022-12-09 00:00:00 |     66 |        3.31 |         0    |
| LFT202603 |      1 | 2023-04-17 00:00:00 | 2025-09-03 00:00:00 |    599 |       27.79 |         0.02 |
| LFT202303 |      1 | 2020-09-30 00:00:00 | 2022-09-05 00:00:00 |    486 |       12.49 |         0.05 |
| LFT202903 |      1 | 2025-09-03 00:00:00 | 2026-08-11 00:00:00 |    236 |       12.84 |         0.05 |

**Quem trouxe o retorno (soma por ativo, pp)**

| ativo     |   sum |   count |
|:----------|------:|--------:|
| LFT202903 |  0.05 |       1 |
| LFT202303 |  0.05 |       1 |
| LFT202603 |  0.02 |       1 |
| LFT202503 |  0    |       1 |

### Treasury 10 anos hedgeado para CDI (T10R11) com regra de prêmio  (`jx_treasury_cdi`)

**Tese:** Carrego o ETF de Treasury com hedge para CDI da B3 só quando o prêmio de prazo americano tende a pagar: curva inclinada, Fed cortando ou depois de venda forte de 10 anos sem o Fed subir

**Instrumentos:** [{'onde': 'B3 (qualquer corretora)', 'ticker': 'T10R11 (Treasury 10 anos com hedge para R$)', 'lote': '1 cota', 'custo': 'spread ~0,2–0,4% + emolumentos 0,03% por lado; taxa de administração (premissa 0,30% a.a.)'}]

**Aplicável:** parcial — O ETF existe desde 2025 (o histórico é sintético: IEF/IEI - T-bill + CDI). Liquidez ainda baixa; T-bill com hedge = CDI - custos (não testado: perde por construção); IBKR com WDO não fecha o hedge com R$ 20 mil.

| métrica | valor |
|---|---|
| OOS desde | 2021-01 |
| retorno OOS a.a. (R$ 20 mil) | 7.7% vs CDI 11.4% |
| ativo OOS pp (R$ 20 mil / R$ 50 mil) | -3.75 / -3.75 |
| depois do IR (classe etf_b3) pp, 20k / 50k | -3.70 / -3.70 |
| IR OOS / Sharpe | -1.41 / -1.41 |
| pior queda | -5.5% |
| PBO / Sharpe deflacionado | 52% / +0% |
| leque de parâmetros p5 / mediana / p95 | -4.01 / -3.55 / -3.17 |
| custo 2x / execução t+2 | -4.50 / -3.94 |
| walk-forward | -6.06 |
| sem os 10 melhores negócios | -2.80 |
| placebo p | 0.33 |
| look-ahead (truncamento) | passou |

**10 melhores negócios**

| ativo                  |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:-----------------------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| T10R11 (IEI sintético) |      1 | 2008-01-02 00:00:00 | 2018-12-04 00:00:00 |   2744 |       22.9  |        22.9  |
| T10R11 (IEI sintético) |      1 | 2020-03-17 00:00:00 | 2020-04-09 00:00:00 |     17 |        1.92 |         1.92 |
| T10R11 (IEI sintético) |      1 | 2022-07-20 00:00:00 | 2022-07-21 00:00:00 |      1 |        0.43 |         0.43 |
| T10R11 (IEI sintético) |      1 | 2020-04-27 00:00:00 | 2020-07-09 00:00:00 |     51 |        0.1  |         0.1  |
| T10R11 (IEI sintético) |      1 | 2020-04-13 00:00:00 | 2020-04-15 00:00:00 |      2 |        0.09 |         0.09 |
| T10R11 (IEI sintético) |      1 | 2026-01-16 00:00:00 | 2026-02-10 00:00:00 |     17 |        0.07 |         0.07 |
| T10R11 (IEI sintético) |      1 | 2025-12-12 00:00:00 | 2025-12-24 00:00:00 |      8 |       -0.05 |        -0.05 |
| T10R11 (IEI sintético) |      1 | 2022-09-30 00:00:00 | 2022-10-03 00:00:00 |      1 |       -0.07 |        -0.07 |
| T10R11 (IEI sintético) |      1 | 2020-07-27 00:00:00 | 2020-07-28 00:00:00 |      1 |       -0.18 |        -0.18 |
| T10R11 (IEI sintético) |      1 | 2020-07-16 00:00:00 | 2020-07-20 00:00:00 |      2 |       -0.19 |        -0.19 |

**10 piores negócios**

| ativo                  |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:-----------------------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| T10R11 (IEI sintético) |      1 | 2020-08-11 00:00:00 | 2022-07-18 00:00:00 |    485 |      -11.38 |       -11.38 |
| T10R11 (IEI sintético) |      1 | 2026-03-18 00:00:00 | 2026-10-13 00:00:00 |    143 |       -4.6  |        -4.6  |
| T10R11 (IEI sintético) |      1 | 2022-09-27 00:00:00 | 2022-09-28 00:00:00 |      1 |       -0.57 |        -0.57 |
| T10R11 (IEI sintético) |      1 | 2020-04-17 00:00:00 | 2020-04-24 00:00:00 |      4 |       -0.5  |        -0.5  |
| T10R11 (IEI sintético) |      1 | 2025-12-31 00:00:00 | 2026-01-14 00:00:00 |      9 |       -0.42 |        -0.42 |
| T10R11 (IEI sintético) |      1 | 2020-03-12 00:00:00 | 2020-03-16 00:00:00 |      2 |       -0.31 |        -0.31 |
| T10R11 (IEI sintético) |      1 | 2026-03-11 00:00:00 | 2026-03-17 00:00:00 |      4 |       -0.29 |        -0.29 |
| T10R11 (IEI sintético) |      1 | 2020-07-10 00:00:00 | 2020-07-14 00:00:00 |      2 |       -0.27 |        -0.27 |
| T10R11 (IEI sintético) |      1 | 2020-07-16 00:00:00 | 2020-07-20 00:00:00 |      2 |       -0.19 |        -0.19 |
| T10R11 (IEI sintético) |      1 | 2020-07-27 00:00:00 | 2020-07-28 00:00:00 |      1 |       -0.18 |        -0.18 |

**Quem trouxe o retorno (soma por ativo, pp)**

| ativo                  |   sum |   count |
|:-----------------------|------:|--------:|
| T10R11 (IEI sintético) |  6.69 |      18 |

### CDB de banco médio com FGC (premissa — não testável)  (`jx_cdb_fgc`)

**Tese:** Escada de CDB de 2 anos de 4–5 bancos médios pagando 110–115% do CDI, garantidos pelo FGC (até R$ 250 mil por CPF/instituição)

**Instrumentos:** [{'onde': 'XP/BTG/Inter/Rico/Nubank (prateleira de bancários)', 'ticker': 'CDB 2 anos de banco médio (BS2, Pine, Daycoval, BMG...)', 'lote': 'R$ 1 mil (às vezes R$ 100)', 'custo': 'sem taxa explícita; sem liquidez até o vencimento; FGC até R$ 250 mil'}]

**Aplicável:** False — Sem histórico público de taxas por emissor (BCB/B3/ANBIMA/Yubb); o 'resultado' abaixo é só a premissa de taxa.

| métrica | valor |
|---|---|
| OOS desde | 2021-01 |
| retorno OOS a.a. (R$ 20 mil) | 12.5% vs CDI 11.4% |
| ativo OOS pp (R$ 20 mil / R$ 50 mil) | +1.04 / +1.04 |
| depois do IR (classe renda_fixa) pp, 20k / 50k | +0.87 / +0.87 |
| IR OOS / Sharpe | +44.12 / +44.12 |
| pior queda | 0.0% |
| PBO / Sharpe deflacionado | nan% / +100% |
| leque de parâmetros p5 / mediana / p95 | +0.46 / +1.20 / +1.61 |
| custo 2x / execução t+2 | +1.04 / +1.04 |
| walk-forward | +1.65 |
| sem os 10 melhores negócios | -0.04 |
| placebo p | 0.42 |
| look-ahead (truncamento) | passou |

**10 melhores negócios**

| ativo           |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:----------------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| escada CDB 2025 |      1 | 2025-01-02 00:00:00 | 2025-12-31 00:00:00 |    252 |        1.34 |         1.34 |
| escada CDB 2016 |      1 | 2016-01-04 00:00:00 | 2016-12-30 00:00:00 |    251 |        1.31 |         1.31 |
| escada CDB 2015 |      1 | 2015-01-02 00:00:00 | 2015-12-31 00:00:00 |    250 |        1.24 |         1.24 |
| escada CDB 2023 |      1 | 2023-01-02 00:00:00 | 2023-12-29 00:00:00 |    249 |        1.23 |         1.23 |
| escada CDB 2022 |      1 | 2022-01-03 00:00:00 | 2022-12-30 00:00:00 |    251 |        1.17 |         1.17 |
| escada CDB 2026 |      1 | 2026-01-02 00:00:00 | 2026-10-13 00:00:00 |    195 |        1.04 |         1.04 |
| escada CDB 2024 |      1 | 2024-01-02 00:00:00 | 2024-12-31 00:00:00 |    253 |        1.03 |         1.03 |
| escada CDB 2014 |      1 | 2014-01-02 00:00:00 | 2014-12-31 00:00:00 |    253 |        1.03 |         1.03 |
| escada CDB 2017 |      1 | 2017-01-02 00:00:00 | 2017-12-29 00:00:00 |    249 |        0.95 |         0.95 |
| escada CDB 2012 |      1 | 2012-01-02 00:00:00 | 2012-12-31 00:00:00 |    251 |        0.8  |         0.8  |

**10 piores negócios**

| ativo           |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:----------------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| escada CDB 2020 |      1 | 2020-01-02 00:00:00 | 2020-12-31 00:00:00 |    251 |        0.27 |         0.27 |
| escada CDB 2021 |      1 | 2021-01-04 00:00:00 | 2021-12-31 00:00:00 |    251 |        0.43 |         0.43 |
| escada CDB 2019 |      1 | 2019-01-02 00:00:00 | 2019-12-31 00:00:00 |    253 |        0.58 |         0.58 |
| escada CDB 2018 |      1 | 2018-01-02 00:00:00 | 2018-12-31 00:00:00 |    250 |        0.62 |         0.62 |
| escada CDB 2013 |      1 | 2013-01-02 00:00:00 | 2013-12-31 00:00:00 |    253 |        0.77 |         0.77 |
| escada CDB 2012 |      1 | 2012-01-02 00:00:00 | 2012-12-31 00:00:00 |    251 |        0.8  |         0.8  |
| escada CDB 2017 |      1 | 2017-01-02 00:00:00 | 2017-12-29 00:00:00 |    249 |        0.95 |         0.95 |
| escada CDB 2014 |      1 | 2014-01-02 00:00:00 | 2014-12-31 00:00:00 |    253 |        1.03 |         1.03 |
| escada CDB 2024 |      1 | 2024-01-02 00:00:00 | 2024-12-31 00:00:00 |    253 |        1.03 |         1.03 |
| escada CDB 2026 |      1 | 2026-01-02 00:00:00 | 2026-10-13 00:00:00 |    195 |        1.04 |         1.04 |

**Quem trouxe o retorno (soma por ativo, pp)**

| ativo           |   sum |   count |
|:----------------|------:|--------:|
| escada CDB 2025 |  1.34 |       1 |
| escada CDB 2016 |  1.31 |       1 |
| escada CDB 2015 |  1.24 |       1 |
| escada CDB 2023 |  1.23 |       1 |
| escada CDB 2022 |  1.17 |       1 |
| escada CDB 2026 |  1.04 |       1 |
| escada CDB 2024 |  1.03 |       1 |
| escada CDB 2014 |  1.03 |       1 |
| escada CDB 2017 |  0.95 |       1 |
| escada CDB 2012 |  0.8  |       1 |

### Mini-dólar vendido após pânico cambial (vendedor forçado)  (`jx_wdo_panico`)

**Tese:** Vendo WDO (compro real) por 2–4 semanas depois que o dólar sobe >= 2 desvios em 10 pregões (stop de carry, resgates EM, hedge às pressas), fora de pânico global; zerado no resto do tempo

**Instrumentos:** [{'onde': 'B3 (Clear/Rico/XP/BTG)', 'ticker': 'WDO (mini-dólar, vencimento mais curto)', 'lote': '1 contrato = US$ 10 mil', 'custo': 'R$ 3,70 por contrato e lado (emolumentos + meio tick); margem ~12% em Tesouro Selic'}]

**Aplicável:** True — Com R$ 50 mil, 1 WDO ~ 1x o capital. Com R$ 20 mil, 1 contrato = ~2,5x o capital em dólar durante a janela (não há micro-dólar na B3) — aplicável, mas o risco por negócio é ~2,5x maior.

| métrica | valor |
|---|---|
| OOS desde | 2021-01 |
| retorno OOS a.a. (R$ 20 mil) | 18.2% vs CDI 11.4% |
| ativo OOS pp (R$ 20 mil / R$ 50 mil) | +6.77 / +2.83 |
| depois do IR (classe futuros_b3) pp, 20k / 50k | +5.57 / +2.72 |
| IR OOS / Sharpe | +0.49 / +0.49 |
| pior queda | -14.3% |
| PBO / Sharpe deflacionado | 39% / +56% |
| leque de parâmetros p5 / mediana / p95 | +2.98 / +5.13 / +9.75 |
| custo 2x / execução t+2 | +6.60 / +7.11 |
| walk-forward | +6.87 |
| sem os 10 melhores negócios | -2.52 |
| placebo p | 0.04 |
| look-ahead (truncamento) | passou |

**10 melhores negócios**

| ativo       |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:------------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| WDO vendido |     -1 | 2020-04-24 00:00:00 | 2020-05-26 00:00:00 |     21 |       27.38 |        27.38 |
| WDO vendido |     -1 | 2022-05-04 00:00:00 | 2022-06-02 00:00:00 |     21 |       17.4  |        17.4  |
| WDO vendido |     -1 | 2023-10-02 00:00:00 | 2023-11-01 00:00:00 |     21 |       12.86 |        12.86 |
| WDO vendido |     -1 | 2013-08-21 00:00:00 | 2013-09-19 00:00:00 |     21 |       12.65 |        12.65 |
| WDO vendido |     -1 | 2023-08-14 00:00:00 | 2023-09-13 00:00:00 |     21 |        8.41 |         8.41 |
| WDO vendido |     -1 | 2015-03-12 00:00:00 | 2015-04-13 00:00:00 |     21 |        8.28 |         8.28 |
| WDO vendido |     -1 | 2025-10-14 00:00:00 | 2025-11-12 00:00:00 |     21 |        8.23 |         8.23 |
| WDO vendido |     -1 | 2019-11-14 00:00:00 | 2019-12-16 00:00:00 |     21 |        7.18 |         7.18 |
| WDO vendido |     -1 | 2016-11-10 00:00:00 | 2016-12-12 00:00:00 |     21 |        6.75 |         6.75 |
| WDO vendido |     -1 | 2021-07-07 00:00:00 | 2021-08-05 00:00:00 |     21 |        4.74 |         4.74 |

**10 piores negócios**

| ativo       |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:------------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| WDO vendido |     -1 | 2015-02-06 00:00:00 | 2015-03-11 00:00:00 |     21 |      -15.29 |       -15.29 |
| WDO vendido |     -1 | 2022-06-15 00:00:00 | 2022-07-15 00:00:00 |     21 |      -12.76 |       -12.76 |
| WDO vendido |     -1 | 2008-08-15 00:00:00 | 2008-09-15 00:00:00 |     21 |       -9.72 |        -9.72 |
| WDO vendido |     -1 | 2018-05-02 00:00:00 | 2018-06-01 00:00:00 |     21 |       -9.24 |        -9.24 |
| WDO vendido |     -1 | 2015-07-28 00:00:00 | 2015-08-26 00:00:00 |     21 |       -8.99 |        -8.99 |
| WDO vendido |     -1 | 2024-11-29 00:00:00 | 2024-12-31 00:00:00 |     21 |       -8.66 |        -8.66 |
| WDO vendido |     -1 | 2020-01-16 00:00:00 | 2020-02-14 00:00:00 |     21 |       -7.15 |        -7.15 |
| WDO vendido |     -1 | 2013-05-28 00:00:00 | 2013-06-27 00:00:00 |     21 |       -5.8  |        -5.8  |
| WDO vendido |     -1 | 2012-05-02 00:00:00 | 2012-05-31 00:00:00 |     21 |       -4.83 |        -4.83 |
| WDO vendido |     -1 | 2019-08-06 00:00:00 | 2019-09-04 00:00:00 |     21 |       -3.49 |        -3.49 |

**Quem trouxe o retorno (soma por ativo, pp)**

| ativo       |   sum |   count |
|:------------|------:|--------:|
| WDO vendido | 39.57 |      40 |
