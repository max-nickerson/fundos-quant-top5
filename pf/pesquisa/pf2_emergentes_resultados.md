# Frente pf2_emergentes — resultados da bateria final (gerado automaticamente)

Gerado por `pf/gerar_cadernos.py` a partir de `pf/resultados/bateria/`. IR de pessoa física por `pf/ir.py` (mensal na B3 com isenção de ações ≤ R$ 20 mil/mês, anual no exterior). Ordem: nota do ranking.

### Argentina no pânico: cesta de ADRs (CCL implícito testado na grade) (IBKR)  (`em_argentina`)

**Tese:** Compro a cesta de ADRs argentinos quando ela cai > 20% em 21 pregões (estrangeiro vendendo à força); a escolha pelo CCL implícito (ADR barato contra a ação em pesos) perdeu no IS; saio em 63 pregões

**Instrumentos:** IBKR: ADRs YPF, GGAL, BMA, PAM, CEPU (compra fracionária, US$ 0,0035/ação mín. US$ 0,35). Na B3 não há BDR desses ADRs (ver COTAHIST). Ações locais (.BA) só como DADO para o CCL implícito (PF brasileiro não opera BYMA).

**Aplicável:** True — Operável: R$ 10 mil (20k) / 25 mil (50k) em 2–5 ADRs líquidos (YPF/GGAL > US$ 50 mi/dia). Custo fixo = remessa (IOF) por pânico.

| métrica | valor |
|---|---|
| OOS desde | 2021-01 |
| retorno OOS a.a. (R$ 20 mil) | 12.9% vs CDI 11.4% |
| ativo OOS pp (R$ 20 mil / R$ 50 mil) | +1.46 / +1.52 |
| depois do IR (classe exterior) pp, 20k / 50k | +1.43 / +1.49 |
| IR OOS / Sharpe | +0.16 / +0.16 |
| pior queda | -27.0% |
| PBO / Sharpe deflacionado | 21% / +0% |
| leque de parâmetros p5 / mediana / p95 | -0.02 / +5.08 / +8.99 |
| custo 2x / execução t+2 | -1.22 / +2.71 |
| walk-forward | +1.46 |
| sem os 10 melhores negócios | -5.18 |
| placebo p | 0.38 |
| look-ahead (truncamento) | passou |

**10 melhores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| PAM     |      1 | 2014-12-16 00:00:00 | 2015-03-13 00:00:00 |     63 |       76.83 |        10.19 |
| PAM     |      1 | 2014-01-24 00:00:00 | 2014-04-23 00:00:00 |     63 |       70.6  |         8.38 |
| GGAL    |      1 | 2009-03-03 00:00:00 | 2009-05-29 00:00:00 |     63 |       56.97 |         8.37 |
| GGAL    |      1 | 2014-12-16 00:00:00 | 2015-03-13 00:00:00 |     63 |       63.07 |         8.33 |
| GGAL    |      1 | 2014-01-24 00:00:00 | 2014-04-23 00:00:00 |     63 |       69.33 |         8.12 |
| CEPU    |      1 | 2023-09-27 00:00:00 | 2023-12-26 00:00:00 |     64 |       75.64 |         7.58 |
| BMA     |      1 | 2014-01-24 00:00:00 | 2014-04-23 00:00:00 |     63 |       60.65 |         6.97 |
| GGAL    |      1 | 2015-10-02 00:00:00 | 2015-12-30 00:00:00 |     63 |       53.04 |         6.59 |
| BMA     |      1 | 2015-10-02 00:00:00 | 2015-12-30 00:00:00 |     63 |       53.22 |         6.56 |
| BMA     |      1 | 2014-12-16 00:00:00 | 2015-03-13 00:00:00 |     63 |       49.28 |         6.56 |

**10 piores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| GGAL    |      1 | 2008-10-13 00:00:00 | 2009-01-08 00:00:00 |     63 |      -39.04 |        -6.84 |
| PAM     |      1 | 2012-04-17 00:00:00 | 2012-07-13 00:00:00 |     63 |      -45.73 |        -6.1  |
| GGAL    |      1 | 2011-08-09 00:00:00 | 2011-11-04 00:00:00 |     63 |      -33.82 |        -4.83 |
| BMA     |      1 | 2011-08-09 00:00:00 | 2011-11-04 00:00:00 |     63 |      -33.85 |        -4.76 |
| BMA     |      1 | 2019-08-13 00:00:00 | 2019-11-08 00:00:00 |     63 |      -36.7  |        -3.91 |
| GGAL    |      1 | 2019-08-13 00:00:00 | 2019-11-08 00:00:00 |     63 |      -27.97 |        -2.99 |
| GGAL    |      1 | 2018-05-09 00:00:00 | 2018-08-06 00:00:00 |     63 |      -25.82 |        -2.87 |
| BMA     |      1 | 2008-10-13 00:00:00 | 2009-01-08 00:00:00 |     63 |      -16.39 |        -2.51 |
| PAM     |      1 | 2018-05-09 00:00:00 | 2018-08-06 00:00:00 |     63 |      -21.75 |        -2.51 |
| BMA     |      1 | 2012-04-17 00:00:00 | 2012-07-13 00:00:00 |     63 |      -19.48 |        -2.46 |

**Quem trouxe o retorno (soma por ativo, pp)**

| ativo   |   sum |   count |
|:--------|------:|--------:|
| PAM     | 32.86 |      18 |
| YPF     | 29.1  |      22 |
| BMA     | 29.07 |      21 |
| GGAL    | 28.76 |      22 |
| CEPU    | 19.67 |      12 |

### Commodity em pânico LatAm: EC/SCCO/BVN/ECH/EPU x Brent/cobre/ouro (IBKR)  (`em_latam_commod`)

**Tese:** Compro o ADR/ETF andino que caiu muito mais que a sua commodity num pânico (resíduo z <= −1,5/−2 e queda > 10–20%) e vendo o ETF da commodity no beta; saio quando o resíduo volta a zero

**Instrumentos:** IBKR: EC, SCCO, BVN (ADRs NYSE), ECH, EPU (ETFs) comprados com fração; BNO, CPER, GLD vendidos em ações inteiras (aluguel 0,3–0,5% a.a.). Conta margem >= US$ 2.000. Micro futuros (MCL/MHG/MGC) grandes demais para a posição.

**Aplicável:** True — Operável com R$ 20 mil (R$ 5 mil por ativo), mas o hedge em ETF vendido exige conta margem (US$ 2.000 parados durante o negócio) e o CPER tem pouco papel para alugar

| métrica | valor |
|---|---|
| OOS desde | 2021-01 |
| retorno OOS a.a. (R$ 20 mil) | 8.6% vs CDI 11.4% |
| ativo OOS pp (R$ 20 mil / R$ 50 mil) | -2.82 / -1.72 |
| depois do IR (classe exterior) pp, 20k / 50k | -2.78 / -1.70 |
| IR OOS / Sharpe | -0.39 / -0.39 |
| pior queda | -7.7% |
| PBO / Sharpe deflacionado | 55% / +2% |
| leque de parâmetros p5 / mediana / p95 | -5.63 / -1.63 / +0.34 |
| custo 2x / execução t+2 | -5.50 / -2.25 |
| walk-forward | -1.25 |
| sem os 10 melhores negócios | -6.75 |
| placebo p | 0.37 |
| look-ahead (truncamento) | passou |

**10 melhores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| EC      |      1 | 2020-05-29 00:00:00 | 2020-06-05 00:00:00 |      5 |       26.32 |         6.09 |
| BVN     |      1 | 2007-08-17 00:00:00 | 2007-09-06 00:00:00 |     13 |       20.34 |         5.35 |
| SCCO    |      1 | 2016-01-20 00:00:00 | 2016-02-04 00:00:00 |     11 |       18.84 |         4.72 |
| CPER    |     -1 | 2020-02-28 00:00:00 | 2020-03-26 00:00:00 |     19 |       13.85 |         4.41 |
| BVN     |      1 | 2006-03-28 00:00:00 | 2006-04-20 00:00:00 |     16 |       15.18 |         3.65 |
| SCCO    |      1 | 2026-03-25 00:00:00 | 2026-04-09 00:00:00 |     10 |       13.63 |         3.39 |
| EC      |      1 | 2019-08-26 00:00:00 | 2019-09-12 00:00:00 |     12 |       12.72 |         3.16 |
| GLD     |     -1 | 2008-08-05 00:00:00 | 2008-09-02 00:00:00 |     19 |        7.99 |         2.84 |
| ECH     |      1 | 2021-12-23 00:00:00 | 2022-01-13 00:00:00 |     14 |       11.43 |         2.82 |
| SCCO    |      1 | 2019-08-15 00:00:00 | 2019-09-06 00:00:00 |     15 |       11.03 |         2.72 |

**10 piores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| BVN     |      1 | 2020-01-29 00:00:00 | 2020-03-30 00:00:00 |     42 |      -46.54 |       -13.5  |
| EC      |      1 | 2014-10-28 00:00:00 | 2014-12-29 00:00:00 |     42 |      -37.61 |        -9.5  |
| BVN     |      1 | 2022-06-29 00:00:00 | 2022-08-29 00:00:00 |     42 |      -20.83 |        -5.29 |
| SCCO    |      1 | 2018-10-22 00:00:00 | 2018-12-21 00:00:00 |     42 |      -20.26 |        -5.23 |
| BVN     |      1 | 2008-10-20 00:00:00 | 2008-11-11 00:00:00 |     16 |      -13.51 |        -4.74 |
| BVN     |      1 | 2015-11-11 00:00:00 | 2016-01-13 00:00:00 |     42 |      -18.39 |        -4.72 |
| BVN     |      1 | 2021-07-06 00:00:00 | 2021-09-02 00:00:00 |     42 |      -17.6  |        -4.56 |
| SCCO    |      1 | 2020-02-28 00:00:00 | 2020-03-26 00:00:00 |     19 |      -14.6  |        -4.14 |
| BVN     |      1 | 2013-05-01 00:00:00 | 2013-06-18 00:00:00 |     33 |      -13.25 |        -3.53 |
| EC      |      1 | 2013-04-16 00:00:00 | 2013-06-14 00:00:00 |     42 |      -11.21 |        -3.08 |

**Quem trouxe o retorno (soma por ativo, pp)**

| ativo   |    sum |   count |
|:--------|-------:|--------:|
| ECH     |  10.52 |       7 |
| EPU     |   7.16 |       6 |
| SCCO    |   4.84 |       8 |
| GLD     |   0.6  |      22 |
| CPER    |   0.47 |      15 |
| BNO     |  -0.58 |      11 |
| EC      |  -5.41 |      11 |
| BVN     | -32.62 |      22 |

### Eleições EM: ETF do país depois do pânico eleitoral (regra fechada)  (`em_eleicoes`)

**Tese:** Lista fechada de eleições de 16 emergentes; se o ETF cai > 3–6% da véspera ao 1º pregão pós-eleição, compro (sem comprar quando a moeda cai junto — fuga de capital), seguro 1–3 meses

**Instrumentos:** IBKR: EWZ, EWW, ARGT, TUR, INDA, EZA, EIDO, EWY, EWT, EWM, THD, EPHE, ECH, EPU, EPOL, GREK (fração). Caixa em Tesouro Selic; dinheiro na IBKR só durante o negócio.

**Aplicável:** True — Operável (R$ 5–10 mil por evento, ETFs líquidos), mas são ~1–3 negócios por ano: o resultado é uma loteria de poucos eventos.

| métrica | valor |
|---|---|
| OOS desde | 2021-01 |
| retorno OOS a.a. (R$ 20 mil) | 8.9% vs CDI 11.4% |
| ativo OOS pp (R$ 20 mil / R$ 50 mil) | -2.50 / -3.55 |
| depois do IR (classe exterior) pp, 20k / 50k | -2.46 / -3.50 |
| IR OOS / Sharpe | -0.53 / -0.53 |
| pior queda | -6.5% |
| PBO / Sharpe deflacionado | 71% / +1% |
| leque de parâmetros p5 / mediana / p95 | -3.09 / -1.52 / -0.79 |
| custo 2x / execução t+2 | -4.08 / -2.75 |
| walk-forward | -0.99 |
| sem os 10 melhores negócios | -2.40 |
| placebo p | 0.41 |
| look-ahead (truncamento) | passou |

**10 melhores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| ECH     |      1 | 2021-12-21 00:00:00 | 2022-01-19 00:00:00 |     21 |       17.02 |         4.74 |
| INDA    |      1 | 2024-06-05 00:00:00 | 2024-07-05 00:00:00 |     22 |        6.66 |         3.5  |
| GREK    |      1 | 2015-01-27 00:00:00 | 2015-02-25 00:00:00 |     21 |       13.35 |         2.98 |
| EWZ     |      1 | 2014-10-28 00:00:00 | 2014-11-26 00:00:00 |     21 |        4.75 |         1.49 |
| GREK    |      1 | 2015-09-22 00:00:00 | 2015-10-21 00:00:00 |     21 |        9.73 |         1.42 |
| TUR     |      1 | 2015-06-09 00:00:00 | 2015-07-08 00:00:00 |     21 |        4.23 |         1.18 |
| EWM     |      1 | 2018-05-10 00:00:00 | 2018-06-08 00:00:00 |     21 |        1.76 |         0.73 |
| TUR     |      1 | 2014-08-12 00:00:00 | 2014-09-10 00:00:00 |     21 |        0.83 |         0.24 |
| TUR     |      1 | 2023-05-16 00:00:00 | 2023-06-14 00:00:00 |     21 |       -1.56 |        -0.35 |
| EWW     |      1 | 2024-06-04 00:00:00 | 2024-07-03 00:00:00 |     21 |       -2.1  |        -0.91 |

**10 piores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| GREK    |      1 | 2012-05-08 00:00:00 | 2012-06-06 00:00:00 |     21 |      -27.01 |        -5.03 |
| ECH     |      1 | 2022-09-07 00:00:00 | 2022-10-06 00:00:00 |     21 |      -11.97 |        -3.3  |
| EPU     |      1 | 2021-06-08 00:00:00 | 2021-07-07 00:00:00 |     21 |       -8.96 |        -3.29 |
| GREK    |      1 | 2015-07-07 00:00:00 | 2015-08-05 00:00:00 |     21 |       -8.54 |        -1.34 |
| ARGT    |      1 | 2025-09-09 00:00:00 | 2025-10-08 00:00:00 |     21 |       -3.36 |        -0.99 |
| EPU     |      1 | 2011-06-07 00:00:00 | 2011-07-06 00:00:00 |     21 |       -2.75 |        -0.95 |
| EWW     |      1 | 2024-06-04 00:00:00 | 2024-07-03 00:00:00 |     21 |       -2.1  |        -0.91 |
| TUR     |      1 | 2023-05-16 00:00:00 | 2023-06-14 00:00:00 |     21 |       -1.56 |        -0.35 |
| TUR     |      1 | 2014-08-12 00:00:00 | 2014-09-10 00:00:00 |     21 |        0.83 |         0.24 |
| EWM     |      1 | 2018-05-10 00:00:00 | 2018-06-08 00:00:00 |     21 |        1.76 |         0.73 |

**Quem trouxe o retorno (soma por ativo, pp)**

| ativo   |   sum |   count |
|:--------|------:|--------:|
| INDA    |  3.5  |       1 |
| EWZ     |  1.49 |       1 |
| ECH     |  1.44 |       2 |
| TUR     |  1.06 |       3 |
| EWM     |  0.73 |       1 |
| EWW     | -0.91 |       1 |
| ARGT    | -0.99 |       1 |
| GREK    | -1.97 |       4 |
| EPU     | -4.24 |       2 |

### Pânico de país: ETF após queda forte em semanas (IBKR)  (`em_panico_pais`)

**Tese:** Compro o ETF de país que caiu > 15% em 21 pregões (resgates forçam o AP a vender a cesta); 25% do capital por país, saio em semanas; Rússia 2022 entra como perda sintética

**Instrumentos:** IBKR: ETFs de país TUR, EWZ, ARGT, EZA, EWW, ECH, EPU, INDA, EIDO, VNM, KSA (compra fracionária, US$ 0,0035/ação, mín. US$ 0,35); hedge opcional EEM vendido (ações inteiras, aluguel ~0,25% a.a., conta margem >= US$ 2.000). Alternativa B3: BEWZ39/BEWW39/BEEM39 (BDRs de ETF) — negociam em menos da metade dos pregões, spread largo: não usados. Caixa em Tesouro Selic.

**Aplicável:** True — Operável: 25% do capital por país = R$ 5 mil (20k) / R$ 12,5 mil (50k), fração na IBKR; o custo fixo é a remessa (IOF) por negócio. Sem hedge cambial (1 WDO = US$ 10 mil > posição).

| métrica | valor |
|---|---|
| OOS desde | 2021-01 |
| retorno OOS a.a. (R$ 20 mil) | 0.6% vs CDI 11.4% |
| ativo OOS pp (R$ 20 mil / R$ 50 mil) | -10.83 / -7.35 |
| depois do IR (classe exterior) pp, 20k / 50k | -10.66 / -7.24 |
| IR OOS / Sharpe | -0.58 / -0.58 |
| pior queda | -42.7% |
| PBO / Sharpe deflacionado | 12% / +0% |
| leque de parâmetros p5 / mediana / p95 | -16.81 / -11.96 / -7.41 |
| custo 2x / execução t+2 | -15.29 / -12.01 |
| walk-forward | -10.83 |
| sem os 10 melhores negócios | -20.84 |
| placebo p | 0.12 |
| look-ahead (truncamento) | passou |

**10 melhores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| TUR     |      1 | 2022-09-30 00:00:00 | 2022-11-30 00:00:00 |     42 |       55.34 |        10.52 |
| EWZ     |      1 | 2007-08-14 00:00:00 | 2007-10-12 00:00:00 |     42 |       40.83 |         9.76 |
| EWZ     |      1 | 2020-05-14 00:00:00 | 2020-07-15 00:00:00 |     42 |       38.75 |         9.08 |
| EWZ     |      1 | 2008-03-20 00:00:00 | 2008-05-20 00:00:00 |     42 |       34.35 |         8.49 |
| EZA     |      1 | 2025-04-07 00:00:00 | 2025-06-06 00:00:00 |     42 |       32.3  |         7.98 |
| EIDO    |      1 | 2020-09-24 00:00:00 | 2020-11-23 00:00:00 |     42 |       29.4  |         7.24 |
| TUR     |      1 | 2009-02-19 00:00:00 | 2009-04-21 00:00:00 |     42 |       29.33 |         6.96 |
| ARGT    |      1 | 2023-10-03 00:00:00 | 2023-12-01 00:00:00 |     42 |       28.66 |         6.64 |
| EZA     |      1 | 2007-08-15 00:00:00 | 2007-10-15 00:00:00 |     42 |       26.92 |         6.46 |
| ARGT    |      1 | 2018-12-26 00:00:00 | 2019-02-27 00:00:00 |     42 |       25.84 |         6.45 |

**10 piores negócios**

| ativo            |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:-----------------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| RSX* (sintético) |      1 | 2022-02-25 00:00:00 | 2022-03-04 00:00:00 |      5 |      -90    |       -22.5  |
| EWZ              |      1 | 2008-09-24 00:00:00 | 2008-11-21 00:00:00 |     42 |      -50.05 |       -14.45 |
| EWW              |      1 | 2008-09-18 00:00:00 | 2008-11-17 00:00:00 |     42 |      -38.86 |        -9.74 |
| EZA              |      1 | 2008-09-18 00:00:00 | 2008-11-17 00:00:00 |     42 |      -36.83 |        -9.12 |
| TUR              |      1 | 2008-09-17 00:00:00 | 2008-11-14 00:00:00 |     42 |      -39.45 |        -8.1  |
| EWZ              |      1 | 2008-07-10 00:00:00 | 2008-09-09 00:00:00 |     42 |      -28.92 |        -7.77 |
| ECH              |      1 | 2008-09-30 00:00:00 | 2008-11-28 00:00:00 |     42 |      -25.77 |        -7.18 |
| EWZ              |      1 | 2020-02-28 00:00:00 | 2020-04-29 00:00:00 |     42 |      -32.4  |        -6.7  |
| EWZ              |      1 | 2015-07-28 00:00:00 | 2015-09-25 00:00:00 |     42 |      -24.15 |        -5.89 |
| TUR              |      1 | 2018-08-07 00:00:00 | 2018-10-05 00:00:00 |     42 |      -15.51 |        -4.11 |

**Quem trouxe o retorno (soma por ativo, pp)**

| ativo   |   sum |   count |
|:--------|------:|--------:|
| EZA     | 28.22 |      25 |
| ARGT    | 26.95 |      14 |
| EIDO    | 22.78 |      12 |
| TUR     | 21.32 |      32 |
| VNM     | 10.86 |      16 |
| EWZ     |  5.04 |      25 |
| EPU     |  4.52 |      11 |
| INDA    |  3.38 |       3 |
| KSA     |  1.68 |       2 |
| ECH     | -1.12 |      14 |

### ADRs indianos x NSE: prêmio fora do normal, hedge INDA (IBKR)  (`em_india_adr`)

**Tese:** O ADR indiano tem prêmio estrutural (conversão de mão única); quando o prêmio cai muito abaixo do normal compro o ADR e vendo INDA (e o contrário quando dispara); saio na volta do prêmio

**Instrumentos:** IBKR: ADRs INFY, HDB, IBN, WIT, RDY (NYSE) + INDA (hedge). Ações da NSE só como DADO (PF brasileiro não opera a NSE). B3: H1DB34/I1BN34 (BDRs) negociam em <15% dos pregões: não usados.

**Aplicável:** True — Operável: 1–3 ADRs líquidos de R$ 5 mil (20k) cada + INDA vendido; exige conta margem (US$ 2.000 parados) quando há vendido.

| métrica | valor |
|---|---|
| OOS desde | 2021-01 |
| retorno OOS a.a. (R$ 20 mil) | 1.7% vs CDI 11.4% |
| ativo OOS pp (R$ 20 mil / R$ 50 mil) | -9.75 / -9.03 |
| depois do IR (classe exterior) pp, 20k / 50k | -9.60 / -8.89 |
| IR OOS / Sharpe | -0.90 / -0.90 |
| pior queda | -18.8% |
| PBO / Sharpe deflacionado | 44% / +0% |
| leque de parâmetros p5 / mediana / p95 | -10.75 / -8.13 / -6.14 |
| custo 2x / execução t+2 | -11.47 / -9.17 |
| walk-forward | -9.41 |
| sem os 10 melhores negócios | -15.00 |
| placebo p | 0.36 |
| look-ahead (truncamento) | passou |

**10 melhores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| INDA    |     -1 | 2020-02-19 00:00:00 | 2020-03-27 00:00:00 |     27 |       32.73 |        12.95 |
| IBN     |      1 | 2006-09-26 00:00:00 | 2006-12-22 00:00:00 |     63 |       31.64 |         8.09 |
| HDB     |      1 | 2014-01-27 00:00:00 | 2014-03-28 00:00:00 |     44 |       28.84 |         6.76 |
| INFY    |      1 | 2008-04-10 00:00:00 | 2008-05-16 00:00:00 |     26 |       26.92 |         6.66 |
| INFY    |      1 | 2009-05-19 00:00:00 | 2009-07-24 00:00:00 |     48 |       29.36 |         6.39 |
| INDA    |     -1 | 2012-02-22 00:00:00 | 2012-05-22 00:00:00 |     64 |       22.38 |         5.92 |
| HDB     |      1 | 2007-04-12 00:00:00 | 2007-06-22 00:00:00 |     51 |       23.42 |         5.79 |
| RDY     |      1 | 2020-04-03 00:00:00 | 2020-04-20 00:00:00 |     11 |       21.9  |         5.44 |
| INDA    |     -1 | 2018-01-23 00:00:00 | 2018-06-13 00:00:00 |    101 |       10.88 |         5.16 |
| INDA    |     -1 | 2022-04-13 00:00:00 | 2022-07-11 00:00:00 |     63 |       10.95 |         4.91 |

**10 piores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| IBN     |      1 | 2008-11-11 00:00:00 | 2008-12-01 00:00:00 |     14 |      -26.97 |        -6.5  |
| WIT     |      1 | 2012-02-22 00:00:00 | 2012-05-21 00:00:00 |     63 |      -23.06 |        -6.47 |
| IBN     |      1 | 2015-10-16 00:00:00 | 2016-01-13 00:00:00 |     63 |      -24.32 |        -6.3  |
| INDA    |     -1 | 2016-10-26 00:00:00 | 2017-05-22 00:00:00 |    148 |      -10.35 |        -6.24 |
| INDA    |     -1 | 2024-01-18 00:00:00 | 2024-08-12 00:00:00 |    147 |      -13.43 |        -5.28 |
| INDA    |     -1 | 2020-04-03 00:00:00 | 2020-04-20 00:00:00 |     11 |      -15.72 |        -4.61 |
| WIT     |      1 | 2007-11-13 00:00:00 | 2008-02-08 00:00:00 |     63 |      -16.03 |        -4.29 |
| RDY     |      1 | 2015-11-12 00:00:00 | 2016-02-09 00:00:00 |     63 |      -15.92 |        -4.09 |
| INDA    |     -1 | 2014-01-27 00:00:00 | 2014-03-28 00:00:00 |     44 |      -13.18 |        -3.97 |
| WIT     |      1 | 2022-01-13 00:00:00 | 2022-04-12 00:00:00 |     63 |      -15.61 |        -3.7  |

**Quem trouxe o retorno (soma por ativo, pp)**

| ativo   |   sum |   count |
|:--------|------:|--------:|
| HDB     | 30.13 |      22 |
| INFY    | 16.87 |      25 |
| IBN     |  8.33 |      30 |
| INDA    |  4.45 |      46 |
| WIT     |  0.25 |      23 |
| RDY     | -1.86 |      18 |

### Pânico cambial EM: exportadores (ADR) contra o país (ETF) (IBKR)  (`em_fx_exportadoras`)

**Tese:** Quando o rand/peso/rupia cai > 2 desvios em 21 dias, compro os ADRs exportadores daquela moeda (custo local, receita em dólar) e vendo o ETF do país; saio em 3–6 semanas

**Instrumentos:** IBKR: GFI, HMY, SBSW, DRD, SSL (África do Sul), ASR, PAC, OMAB (México), INFY, WIT (Índia), SQM (Chile), EC (Colômbia) comprados; EZA, EWW, INDA, ECH vendidos (ações inteiras, aluguel 0,3–0,5% a.a.); conta margem >= US$ 2.000.

**Aplicável:** True — Operável (R$ 8 mil por moeda com 20k); perna vendida exige conta margem; Colômbia sem ETF vivo (só comprado).

| métrica | valor |
|---|---|
| OOS desde | 2021-01 |
| retorno OOS a.a. (R$ 20 mil) | -4.2% vs CDI 11.4% |
| ativo OOS pp (R$ 20 mil / R$ 50 mil) | -15.61 / -11.59 |
| depois do IR (classe exterior) pp, 20k / 50k | -15.37 / -11.42 |
| IR OOS / Sharpe | -1.17 / -1.17 |
| pior queda | -24.6% |
| PBO / Sharpe deflacionado | 42% / +0% |
| leque de parâmetros p5 / mediana / p95 | -20.93 / -14.82 / -9.22 |
| custo 2x / execução t+2 | -20.30 / -15.97 |
| walk-forward | -16.30 |
| sem os 10 melhores negócios | -23.64 |
| placebo p | 0.89 |
| look-ahead (truncamento) | passou |

**10 melhores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| EWW     |     -1 | 2008-09-02 00:00:00 | 2008-10-30 00:00:00 |     42 |       39.56 |        19.98 |
| SQM     |      1 | 2008-05-13 00:00:00 | 2008-07-10 00:00:00 |     42 |       49.56 |        18.91 |
| WIT     |      1 | 2009-03-10 00:00:00 | 2009-05-07 00:00:00 |     42 |       71.07 |        14.44 |
| HMY     |      1 | 2015-11-17 00:00:00 | 2016-01-14 00:00:00 |     42 |      175.93 |        12.7  |
| EWW     |     -1 | 2020-03-03 00:00:00 | 2020-04-30 00:00:00 |     42 |       31.98 |        12.01 |
| SQM     |      1 | 2008-10-09 00:00:00 | 2008-12-08 00:00:00 |     42 |       50.51 |        11.35 |
| SQM     |      1 | 2022-07-18 00:00:00 | 2022-09-14 00:00:00 |     42 |       32.23 |        10.61 |
| EZA     |     -1 | 2015-11-17 00:00:00 | 2016-01-14 00:00:00 |     42 |       22.78 |         9.04 |
| SQM     |      1 | 2015-08-28 00:00:00 | 2015-10-27 00:00:00 |     42 |       23.56 |         6.94 |
| SQM     |      1 | 2014-01-28 00:00:00 | 2014-03-27 00:00:00 |     42 |       17.51 |         6.68 |

**10 piores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| EC      |      1 | 2022-05-05 00:00:00 | 2022-07-05 00:00:00 |     43 |      -32.72 |       -13.45 |
| EWW     |     -1 | 2023-10-20 00:00:00 | 2023-12-19 00:00:00 |     42 |      -29.19 |       -11.12 |
| SQM     |      1 | 2015-06-16 00:00:00 | 2015-08-13 00:00:00 |     42 |      -26.58 |       -10.7  |
| WIT     |      1 | 2008-09-03 00:00:00 | 2008-10-31 00:00:00 |     42 |      -33.56 |        -8.96 |
| INDA    |     -1 | 2013-08-21 00:00:00 | 2013-10-18 00:00:00 |     42 |      -23.44 |        -7.55 |
| OMAB    |      1 | 2008-09-02 00:00:00 | 2008-10-30 00:00:00 |     42 |      -45.06 |        -7.55 |
| EZA     |     -1 | 2007-08-22 00:00:00 | 2007-10-19 00:00:00 |     42 |      -17.27 |        -7.36 |
| INFY    |      1 | 2008-09-03 00:00:00 | 2008-10-31 00:00:00 |     42 |      -27.29 |        -7.24 |
| EWW     |     -1 | 2012-05-31 00:00:00 | 2012-07-30 00:00:00 |     42 |      -16.96 |        -6.74 |
| EWW     |     -1 | 2006-06-09 00:00:00 | 2006-08-08 00:00:00 |     42 |      -19    |        -6.62 |

**Quem trouxe o retorno (soma por ativo, pp)**

| ativo   |   sum |   count |
|:--------|------:|--------:|
| SQM     | 50.38 |      15 |
| HMY     | 23.82 |      22 |
| WIT     | 22.63 |      22 |
| INFY    | 17.1  |      22 |
| DRD     | 15.96 |      22 |
| SBSW    | 14.92 |      15 |
| GFI     |  9.08 |      22 |
| ASR     |  8.31 |      23 |
| SSL     |  5.13 |      22 |
| PAC     | -1.11 |      23 |

### ADRs chineses x Hong Kong: prêmio/desconto com as duas pernas (IBKR)  (`em_china_adr_hk`)

**Tese:** Prêmio do ADR sobre a ação de HK (Adj Close, ajustado pela razão e pelo HKD) longe da média: compro a listagem barata e vendo a cara, executando no fechamento seguinte de cada praça (o fuso não é capturado)

**Instrumentos:** IBKR: ADRs BABA, JD, BIDU, NTES, BILI, TCOM, NIO, LI, XPEV, BEKE, ZTO, YUMC e as linhas de HK 9988, 9618, 9888, 9999, 9626, 9961, 9866, 2015, 9868, 2423, 2057, 9987 (SEHK, board lots). Vender HK exige papel 'designated for short selling'. Na B3: BABA34/JDCO34/BIDU34 — negociam em ~1/3 dos pregões, sem aluguel na prática: não usados.

**Aplicável:** True — Operável na IBKR com R$ 20 mil para os lotes pequenos (9888/9618/9626), mas é um livro L/S que exige conta margem (US$ 2.000 parados) e paga selo de HK nas duas pontas

| métrica | valor |
|---|---|
| OOS desde | 2023-01 |
| retorno OOS a.a. (R$ 20 mil) | -10.4% vs CDI 13.1% |
| ativo OOS pp (R$ 20 mil / R$ 50 mil) | -23.46 / -20.56 |
| depois do IR (classe exterior) pp, 20k / 50k | -23.06 / -20.21 |
| IR OOS / Sharpe | -1.27 / -1.27 |
| pior queda | -36.5% |
| PBO / Sharpe deflacionado | 49% / +0% |
| leque de parâmetros p5 / mediana / p95 | -24.12 / -20.53 / -16.49 |
| custo 2x / execução t+2 | -32.20 / -15.59 |
| walk-forward | -23.65 |
| sem os 10 melhores negócios | -40.57 |
| placebo p | 0.87 |
| look-ahead (truncamento) | passou |

**10 melhores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| 9626.HK |      1 | 2024-09-25 00:00:00 | 2024-10-02 00:00:00 |      5 |       73.28 |        20.71 |
| JD      |      1 | 2022-03-11 00:00:00 | 2022-03-18 00:00:00 |      5 |       35.72 |        12.47 |
| 9618.HK |      1 | 2024-09-25 00:00:00 | 2024-10-02 00:00:00 |      5 |       47.34 |        10.11 |
| XPEV    |      1 | 2023-07-26 00:00:00 | 2023-07-28 00:00:00 |      2 |       20.2  |         9.98 |
| 9868.HK |      1 | 2022-12-01 00:00:00 | 2022-12-06 00:00:00 |      3 |       23.23 |         8.56 |
| 9961.HK |      1 | 2022-11-29 00:00:00 | 2022-12-06 00:00:00 |      5 |       15.41 |         5.58 |
| 9868.HK |     -1 | 2024-10-02 00:00:00 | 2024-10-09 00:00:00 |      5 |       14.85 |         5.52 |
| BILI    |      1 | 2022-12-06 00:00:00 | 2022-12-08 00:00:00 |      2 |       13.81 |         4.91 |
| XPEV    |     -1 | 2022-10-26 00:00:00 | 2022-10-28 00:00:00 |      2 |       15.87 |         4.71 |
| 2423.HK |     -1 | 2022-12-06 00:00:00 | 2022-12-16 00:00:00 |      8 |       16.3  |         4.7  |

**10 piores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| 9868.HK |     -1 | 2023-07-26 00:00:00 | 2023-07-28 00:00:00 |      2 |      -40.81 |       -15.23 |
| BILI    |     -1 | 2024-09-25 00:00:00 | 2024-10-01 00:00:00 |      4 |      -46.31 |       -12.5  |
| 9626.HK |     -1 | 2022-12-06 00:00:00 | 2022-12-08 00:00:00 |      2 |      -17.78 |        -6.01 |
| JD      |     -1 | 2024-09-25 00:00:00 | 2024-10-01 00:00:00 |      4 |      -29.27 |        -5.99 |
| 9868.HK |      1 | 2022-10-26 00:00:00 | 2022-10-28 00:00:00 |      2 |      -17.59 |        -5.9  |
| 9618.HK |     -1 | 2022-03-11 00:00:00 | 2022-03-18 00:00:00 |      5 |      -15.5  |        -5.62 |
| XPEV    |     -1 | 2022-12-01 00:00:00 | 2022-12-06 00:00:00 |      3 |      -17.25 |        -5.42 |
| BEKE    |      1 | 2022-12-06 00:00:00 | 2022-12-16 00:00:00 |      8 |      -15.09 |        -5.25 |
| TCOM    |     -1 | 2022-11-29 00:00:00 | 2022-12-06 00:00:00 |      5 |      -13.39 |        -4.77 |
| 9866.HK |      1 | 2022-10-26 00:00:00 | 2022-10-28 00:00:00 |      2 |      -12.02 |        -3.64 |

**Quem trouxe o retorno (soma por ativo, pp)**

| ativo   |   sum |   count |
|:--------|------:|--------:|
| 9626.HK | 10.63 |      21 |
| ZTO     |  8.95 |      17 |
| 9961.HK |  5.19 |       8 |
| XPEV    |  4.36 |      20 |
| 2423.HK |  3.24 |      16 |
| BILI    |  2.93 |      21 |
| BABA    |  2.25 |      10 |
| BIDU    |  2.23 |      24 |
| 9618.HK |  1.88 |      17 |
| NTES    |  0.05 |       2 |

### Fronteira/EM pequeno: ETF dos EUA com desconto contra a bolsa local (IBKR)  (`em_fronteira`)

**Tese:** Quando o ETF americano (VNM, TUR, EIDO, EWM, EZA) cai muito mais que a bolsa local em dólar, compro o ETF (resgate forçado cria desconto à cesta) e saio quando o desvio fecha ou em 10 dias

**Instrumentos:** IBKR: VNM, TUR, EIDO, EWM, EZA (fração); hedge opcional EEM vendido. Índices locais e moedas só como DADO.

**Aplicável:** True — Operável (R$ 6 mil por ETF com 20k); ETFs com US$ 5–100 mi/dia de volume — nosso tamanho é irrelevante para a liquidez.

| métrica | valor |
|---|---|
| OOS desde | 2021-01 |
| retorno OOS a.a. (R$ 20 mil) | 1.8% vs CDI 11.4% |
| ativo OOS pp (R$ 20 mil / R$ 50 mil) | -9.62 / -9.58 |
| depois do IR (classe exterior) pp, 20k / 50k | -9.48 / -9.43 |
| IR OOS / Sharpe | -2.13 / -2.13 |
| pior queda | -8.0% |
| PBO / Sharpe deflacionado | 31% / +0% |
| leque de parâmetros p5 / mediana / p95 | -16.93 / -11.45 / -5.79 |
| custo 2x / execução t+2 | -14.18 / -8.76 |
| walk-forward | -9.78 |
| sem os 10 melhores negócios | -10.96 |
| placebo p | 0.65 |
| look-ahead (truncamento) | passou |

**10 melhores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| TUR     |      1 | 2018-08-13 00:00:00 | 2018-08-15 00:00:00 |      2 |       15.78 |         4.17 |
| EIDO    |      1 | 2015-08-24 00:00:00 | 2015-08-28 00:00:00 |      4 |       14.32 |         4.11 |
| EIDO    |      1 | 2011-09-22 00:00:00 | 2011-09-28 00:00:00 |      4 |       12.99 |         3.37 |
| EIDO    |      1 | 2013-08-28 00:00:00 | 2013-09-09 00:00:00 |      8 |       10.54 |         3.03 |
| TUR     |      1 | 2008-10-10 00:00:00 | 2008-10-13 00:00:00 |      1 |        8.84 |         2.58 |
| TUR     |      1 | 2010-05-07 00:00:00 | 2010-05-11 00:00:00 |      2 |        9.04 |         2.53 |
| EIDO    |      1 | 2016-06-27 00:00:00 | 2016-06-29 00:00:00 |      2 |        8.57 |         2.47 |
| TUR     |      1 | 2016-06-27 00:00:00 | 2016-07-11 00:00:00 |     10 |        6.69 |         1.92 |
| EIDO    |      1 | 2011-10-04 00:00:00 | 2011-10-07 00:00:00 |      3 |        6.62 |         1.9  |
| EWM     |      1 | 2021-12-14 00:00:00 | 2021-12-28 00:00:00 |     10 |        5.39 |         1.56 |

**10 piores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| TUR     |      1 | 2008-09-30 00:00:00 | 2008-10-07 00:00:00 |      5 |      -24.48 |        -8.35 |
| TUR     |      1 | 2008-11-07 00:00:00 | 2008-11-12 00:00:00 |      3 |      -14.57 |        -4.79 |
| VNM     |      1 | 2020-02-26 00:00:00 | 2020-03-11 00:00:00 |     10 |      -11.98 |        -3.94 |
| TUR     |      1 | 2011-08-03 00:00:00 | 2011-08-04 00:00:00 |      1 |       -8.15 |        -2.55 |
| EWM     |      1 | 2020-03-17 00:00:00 | 2020-03-18 00:00:00 |      1 |       -7.29 |        -2.54 |
| EIDO    |      1 | 2013-06-03 00:00:00 | 2013-06-14 00:00:00 |      9 |       -7.4  |        -2.3  |
| TUR     |      1 | 2023-06-08 00:00:00 | 2023-06-22 00:00:00 |     10 |       -7.05 |        -2.13 |
| TUR     |      1 | 2008-10-16 00:00:00 | 2008-10-17 00:00:00 |      1 |       -6.06 |        -1.87 |
| VNM     |      1 | 2020-01-22 00:00:00 | 2020-02-04 00:00:00 |      9 |       -5.86 |        -1.85 |
| EIDO    |      1 | 2020-02-25 00:00:00 | 2020-02-27 00:00:00 |      2 |       -5.64 |        -1.76 |

**Quem trouxe o retorno (soma por ativo, pp)**

| ativo   |   sum |   count |
|:--------|------:|--------:|
| EIDO    |  9.98 |      29 |
| EWM     |  3.75 |      45 |
| EZA     |  0.73 |       7 |
| VNM     | -5.13 |       8 |
| TUR     | -7.67 |      45 |
