# Frente pf2_opcoes — resultados da bateria final (gerado automaticamente)

Gerado por `pf/gerar_cadernos.py` a partir de `pf/resultados/bateria/`. IR de pessoa física por `pf/ir.py` (mensal na B3 com isenção de ações ≤ R$ 20 mil/mês, anual no exterior). Ordem: nota do ranking.

### XSP (mini-SPX) iron condor / borboleta / trava de put mensal — proxy índices Cboe  (`op_xsp_cboe`)

**Tese:** Vendo o prêmio de variância do S&P em XSP com risco definido; só a perda máxima fica na IBKR, o resto em CDI

**Instrumentos:** [{'onde': 'IBKR (Cboe)', 'ticker': 'XSP (opções mensais, US$ 100 x XSP = S&P/10)', 'lote': '1 contrato (~US$ 66 mil de nocional)', 'custo': 'US$ 0,65 + meio spread ~US$ 6 por perna'}, {'onde': 'IBKR', 'ticker': 'margem = perda máxima da estrutura', 'lote': '-', 'custo': 'sem CDI + câmbio + IOF 1,1%'}]

**Aplicável:** parcial: com R$ 20 mil quase nunca cabe 1 estrutura (perda máxima de 1 XSP ~ US$ 1,5–2,5 mil = 40–60% do capital) — 1 XSP tem ~US$ 66 mil de nocional; a perda máxima de 1 condor/borboleta é ~2,5–4% disso (US$ 1,6–2,6 mil ~ R$ 9–14 mil). Com 25% de risco por mês: 20k -> 0 contratos quase sempre; 50k -> 0–1. O PF só consegue com asas estreitas (fora do proxy).

| métrica | valor |
|---|---|
| OOS desde | 2021-01 |
| retorno OOS a.a. (R$ 20 mil) | 10.1% vs CDI 11.4% |
| ativo OOS pp (R$ 20 mil / R$ 50 mil) | -1.33 / -5.85 |
| depois do IR (classe exterior) pp, 20k / 50k | -1.94 / -7.76 |
| IR OOS / Sharpe | +0.12 / +0.12 |
| pior queda | -48.3% |
| PBO / Sharpe deflacionado | 0% / +0% |
| leque de parâmetros p5 / mediana / p95 | -7.94 / -1.39 / +0.85 |
| custo 2x / execução t+2 | -3.88 / -11.75 |
| walk-forward | -1.33 |
| sem os 10 melhores negócios | -16.96 |
| placebo p | 0.45 |
| look-ahead (truncamento) | passou |

**10 melhores negócios**

| ativo         |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| XSP_trava_put |     -1 | 2020-03-20 00:00:00 | 2020-04-17 00:00:00 |     20 |       36.56 |        36.56 |
| XSP_trava_put |     -1 | 2011-08-19 00:00:00 | 2011-09-16 00:00:00 |     20 |       25.62 |        25.62 |
| XSP_trava_put |     -1 | 2009-03-20 00:00:00 | 2009-04-17 00:00:00 |     20 |       24.04 |        24.04 |
| XSP_trava_put |     -1 | 2008-01-18 00:00:00 | 2008-02-15 00:00:00 |     20 |       22.51 |        22.51 |
| XSP_trava_put |     -1 | 2011-11-18 00:00:00 | 2011-12-16 00:00:00 |     20 |       21.25 |        21.25 |
| XSP_trava_put |     -1 | 2012-05-18 00:00:00 | 2012-06-15 00:00:00 |     20 |       21.19 |        21.19 |
| XSP_trava_put |     -1 | 2009-06-19 00:00:00 | 2009-07-17 00:00:00 |     20 |       18.87 |        18.87 |
| XSP_trava_put |     -1 | 2009-05-15 00:00:00 | 2009-06-19 00:00:00 |     25 |       18.57 |        18.57 |
| XSP_trava_put |     -1 | 2011-12-16 00:00:00 | 2012-01-20 00:00:00 |     25 |       18.37 |        18.37 |
| XSP_trava_put |     -1 | 2022-02-18 00:00:00 | 2022-03-18 00:00:00 |     20 |       18.07 |        18.07 |

**10 piores negócios**

| ativo         |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| XSP_trava_put |     -1 | 2008-09-19 00:00:00 | 2008-10-17 00:00:00 |     20 |      -45.17 |       -45.17 |
| XSP_trava_put |     -1 | 2011-07-15 00:00:00 | 2011-08-19 00:00:00 |     25 |      -38.36 |       -38.36 |
| XSP_trava_put |     -1 | 2022-05-20 00:00:00 | 2022-06-17 00:00:00 |     20 |      -36.01 |       -36.01 |
| XSP_trava_put |     -1 | 2022-09-16 00:00:00 | 2022-10-21 00:00:00 |     25 |      -35.69 |       -35.69 |
| XSP_trava_put |     -1 | 2009-01-16 00:00:00 | 2009-02-20 00:00:00 |     25 |      -34.62 |       -34.62 |
| XSP_trava_put |     -1 | 2020-02-21 00:00:00 | 2020-03-20 00:00:00 |     20 |      -31.93 |       -31.93 |
| XSP_trava_put |     -1 | 2012-04-20 00:00:00 | 2012-05-18 00:00:00 |     20 |      -31.5  |       -31.5  |
| XSP_trava_put |     -1 | 2008-05-16 00:00:00 | 2008-06-20 00:00:00 |     25 |      -31.16 |       -31.16 |
| XSP_trava_put |     -1 | 2008-06-20 00:00:00 | 2008-07-18 00:00:00 |     20 |      -29.96 |       -29.96 |
| XSP_trava_put |     -1 | 2015-07-17 00:00:00 | 2015-08-21 00:00:00 |     25 |      -29.87 |       -29.87 |

**Quem trouxe o retorno (soma por ativo, pp)**

| ativo         |    sum |   count |
|:--------------|-------:|--------:|
| XSP_trava_put | 412.13 |     168 |

### Opções de dólar B3: trava vendida de call/put ou condor (IV dos negócios de DOL, tamanho WDO)  (`op_dolar`)

**Tese:** Vendo a trava de call de dólar OTM (o skew que o importador paga) com risco definido e garantia em Tesouro Selic, só com IV > RV

**Instrumentos:** [{'onde': 'B3', 'ticker': 'opções de WDO/DOL (dólar comercial, vencimento no 1º pregão do mês)', 'lote': '1 contrato WDO = US$ 10 mil', 'custo': 'meio spread ~max(1,5 pt; 5% do prêmio) + R$ 0,30 por contrato'}, {'onde': 'Tesouro Direto / B3', 'ticker': 'Tesouro Selic (garantia)', 'lote': '-', 'custo': 'igual ao benchmark'}]

**Aplicável:** parcial: as opções de WDO quase não negociam (2/dia, sem oferta no fechamento); o teste usa preços de DOL (institucional) — Cabe no capital: trava de 3% (≈160 pontos) em WDO perde no máximo ~R$ 1,2–1,4 mil; 10% de risco = 1 trava com 20k, 3 com 50k. Não cabe na LIQUIDEZ: a PF dependeria de achar contraparte em WDO (book vazio) — premissa otimista.

| métrica | valor |
|---|---|
| OOS desde | 2023-01 |
| retorno OOS a.a. (R$ 20 mil) | 11.6% vs CDI 13.1% |
| ativo OOS pp (R$ 20 mil / R$ 50 mil) | -1.49 / -1.66 |
| depois do IR (classe futuros_b3) pp, 20k / 50k | -1.47 / -1.63 |
| IR OOS / Sharpe | -0.17 / -0.17 |
| pior queda | -6.5% |
| PBO / Sharpe deflacionado | 43% / +0% |
| leque de parâmetros p5 / mediana / p95 | -4.94 / -1.55 / -0.17 |
| custo 2x / execução t+2 | -3.44 / +0.89 |
| walk-forward | -1.49 |
| sem os 10 melhores negócios | -4.34 |
| placebo p | 0.21 |
| look-ahead (truncamento) | passou |

**10 melhores negócios**

| ativo          |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:---------------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| WDO_put_spread |     -1 | 2020-05-05 00:00:00 | 2020-06-01 00:00:00 |     19 |       28.8  |         1.96 |
| WDO_put_spread |     -1 | 2020-04-02 00:00:00 | 2020-05-04 00:00:00 |     22 |       28.62 |         1.95 |
| WDO_put_spread |     -1 | 2022-11-03 00:00:00 | 2022-12-01 00:00:00 |     20 |       28.24 |         1.93 |
| WDO_put_spread |     -1 | 2020-10-02 00:00:00 | 2020-11-03 00:00:00 |     22 |       27.18 |         1.87 |
| WDO_put_spread |     -1 | 2020-08-04 00:00:00 | 2020-09-01 00:00:00 |     20 |       33.07 |         1.86 |
| WDO_put_spread |     -1 | 2022-10-04 00:00:00 | 2022-11-01 00:00:00 |     20 |       26.56 |         1.84 |
| WDO_put_spread |     -1 | 2020-06-02 00:00:00 | 2020-07-01 00:00:00 |     21 |       31    |         1.77 |
| WDO_put_spread |     -1 | 2021-03-02 00:00:00 | 2021-04-01 00:00:00 |     22 |       24.5  |         1.72 |
| WDO_put_spread |     -1 | 2022-12-02 00:00:00 | 2023-01-02 00:00:00 |     21 |       24.49 |         1.72 |
| WDO_put_spread |     -1 | 2020-07-02 00:00:00 | 2020-08-03 00:00:00 |     22 |       28.95 |         1.68 |

**10 piores negócios**

| ativo          |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:---------------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| WDO_put_spread |     -1 | 2025-01-03 00:00:00 | 2025-02-03 00:00:00 |     21 |     -100.04 |        -7.59 |
| WDO_put_spread |     -1 | 2022-01-04 00:00:00 | 2022-02-01 00:00:00 |     20 |     -100.04 |        -7.54 |
| WDO_put_spread |     -1 | 2023-01-03 00:00:00 | 2023-02-01 00:00:00 |     21 |     -100.04 |        -7.19 |
| WDO_put_spread |     -1 | 2020-11-04 00:00:00 | 2020-12-01 00:00:00 |     19 |      -95.31 |        -6.75 |
| WDO_put_spread |     -1 | 2022-03-03 00:00:00 | 2022-04-01 00:00:00 |     21 |     -100.05 |        -6.47 |
| WDO_put_spread |     -1 | 2022-05-03 00:00:00 | 2022-06-01 00:00:00 |     21 |      -75.52 |        -4.45 |
| WDO_put_spread |     -1 | 2021-04-05 00:00:00 | 2021-05-03 00:00:00 |     20 |      -45.71 |        -3.31 |
| WDO_put_spread |     -1 | 2026-10-02 00:00:00 | 2026-10-13 00:00:00 |      7 |      -35.81 |        -2.05 |
| WDO_put_spread |     -1 | 2019-12-03 00:00:00 | 2020-01-02 00:00:00 |     22 |      -32.95 |        -1.98 |
| WDO_put_spread |     -1 | 2026-01-05 00:00:00 | 2026-02-02 00:00:00 |     20 |      -22.52 |        -1.89 |

**Quem trouxe o retorno (soma por ativo, pp)**

| ativo          |   sum |   count |
|:---------------|------:|--------:|
| WDO_put_spread |  7.21 |      92 |

### Hedge de cauda da carteira: call spread de VIX (IBKR) x collar/put de BOVA11  (`op_vix_hedge`)

**Tese:** Overlay de proteção de uma carteira Brasil: trava de call de VIX comprada todo mês (modelo VVIX) ou collar/put de BOVA11

**Instrumentos:** [{'onde': 'IBKR (Cboe)', 'ticker': 'opções de VIX (US$ 100 x VIX), trava K1/K1+10', 'lote': 1, 'custo': 'US$ 0,65 + ~US$ 5 por perna'}, {'onde': 'B3', 'ticker': 'puts/calls mensais de BOVA11', 'lote': 100, 'custo': 'bid/ask do fechamento + 0,10%'}]

**Aplicável:** como hedge (overlay): sim; como fundo de excesso: não (é custo de seguro) — 1 trava 20/30 de VIX paga até US$ 1.000 (~R$ 5,4 mil) e custa US$ 30–80/mês: com R$ 20 mil, 1 contrato protege ~25% da carteira e custa 2–4% do capital por ano mesmo comprando só com vol baixa. Collar de BOVA11: 1 lote por R$ 12–15 mil.

| métrica | valor |
|---|---|
| OOS desde | 2021-01 |
| retorno OOS a.a. (R$ 20 mil) | 9.4% vs CDI 11.4% |
| ativo OOS pp (R$ 20 mil / R$ 50 mil) | -2.07 / -1.73 |
| depois do IR (classe exterior) pp, 20k / 50k | -2.04 / -1.70 |
| IR OOS / Sharpe | -0.61 / -0.61 |
| pior queda | -5.2% |
| PBO / Sharpe deflacionado | 8% / +0% |
| leque de parâmetros p5 / mediana / p95 | -2.59 / -1.79 / -0.89 |
| custo 2x / execução t+2 | -2.31 / -2.54 |
| walk-forward | -2.07 |
| sem os 10 melhores negócios | -2.36 |
| placebo p | 0.99 |
| look-ahead (truncamento) | passou |

**10 melhores negócios**

| ativo    |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:---------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| BOVA_put |      1 | 2020-02-19 00:00:00 | 2020-03-16 00:00:00 |     18 |       35.16 |        35.16 |
| BOVA_put |      1 | 2017-05-17 00:00:00 | 2017-06-19 00:00:00 |     23 |        5.01 |         5.01 |
| BOVA_put |      1 | 2015-07-22 00:00:00 | 2015-08-17 00:00:00 |     18 |        4.45 |         4.45 |
| BOVA_put |      1 | 2017-02-22 00:00:00 | 2017-03-20 00:00:00 |     18 |        2.18 |         2.18 |
| BOVA_put |      1 | 2022-05-24 00:00:00 | 2022-06-17 00:00:00 |     18 |        1.21 |         1.21 |
| BOVA_put |      1 | 2022-04-19 00:00:00 | 2022-05-20 00:00:00 |     23 |        1.19 |         1.19 |
| BOVA_put |      1 | 2018-04-18 00:00:00 | 2018-05-21 00:00:00 |     23 |        0.47 |         0.47 |
| BOVA_put |      1 | 2025-09-23 00:00:00 | 2025-10-17 00:00:00 |     18 |       -0.06 |        -0.06 |
| BOVA_put |      1 | 2025-05-20 00:00:00 | 2025-06-20 00:00:00 |     23 |       -0.09 |        -0.09 |
| BOVA_put |      1 | 2025-12-23 00:00:00 | 2026-01-16 00:00:00 |     18 |       -0.09 |        -0.09 |

**10 piores negócios**

| ativo    |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:---------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| BOVA_put |      1 | 2016-07-20 00:00:00 | 2016-08-15 00:00:00 |     18 |       -2.12 |        -2.12 |
| BOVA_put |      1 | 2019-09-18 00:00:00 | 2019-10-21 00:00:00 |     23 |       -1.7  |        -1.7  |
| BOVA_put |      1 | 2017-08-23 00:00:00 | 2017-09-18 00:00:00 |     18 |       -1.46 |        -1.46 |
| BOVA_put |      1 | 2021-01-20 00:00:00 | 2021-02-22 00:00:00 |     23 |       -1.16 |        -1.16 |
| BOVA_put |      1 | 2021-03-17 00:00:00 | 2021-04-19 00:00:00 |     23 |       -1.13 |        -1.13 |
| BOVA_put |      1 | 2015-06-17 00:00:00 | 2015-07-20 00:00:00 |     23 |       -1.12 |        -1.12 |
| BOVA_put |      1 | 2020-11-18 00:00:00 | 2020-12-21 00:00:00 |     23 |       -1.05 |        -1.05 |
| BOVA_put |      1 | 2021-07-20 00:00:00 | 2021-08-20 00:00:00 |     23 |       -0.93 |        -0.93 |
| BOVA_put |      1 | 2019-06-19 00:00:00 | 2019-07-15 00:00:00 |     18 |       -0.73 |        -0.73 |
| BOVA_put |      1 | 2020-12-23 00:00:00 | 2021-01-18 00:00:00 |     18 |       -0.7  |        -0.7  |

**Quem trouxe o retorno (soma por ativo, pp)**

| ativo    |   sum |   count |
|:---------|------:|--------:|
| BOVA_put |  27.1 |      54 |

### Doador de aluguel: small caps com taxa alta emprestadas (com/sem hedge de Ibovespa)  (`op_aluguel`)

**Tese:** Compro as N ações com maior taxa de aluguel esperada e empresto (BTC); o teste mostra se a taxa paga a queda do papel

**Instrumentos:** [{'onde': 'B3 (Clear/XP/Rico)', 'ticker': 'small caps com taxa de aluguel alta, carteira doadora', 'lote': '1 ação (fracionário)', 'custo': 'emolumentos 0,03% + meio spread 0,08–0,8% + 0,2% fracionário; corretora fica com ~30% da taxa'}, {'onde': 'B3', 'ticker': 'BOVA11 vendido (hedge opcional)', 'lote': '1 cota', 'custo': 'aluguel 0,88% + 0,5% a.a.'}]

**Aplicável:** True — Cabe: R$ 2–4 mil por papel em 5–10 papéis, fracionário; doação automática em qualquer corretora grande.

| métrica | valor |
|---|---|
| OOS desde | 2021-01 |
| retorno OOS a.a. (R$ 20 mil) | -18.8% vs CDI 11.4% |
| ativo OOS pp (R$ 20 mil / R$ 50 mil) | -30.20 / -30.21 |
| depois do IR (classe acoes) pp, 20k / 50k | -29.75 / -29.76 |
| IR OOS / Sharpe | -0.91 / -0.91 |
| pior queda | -88.4% |
| PBO / Sharpe deflacionado | 24% / +0% |
| leque de parâmetros p5 / mediana / p95 | -43.65 / -36.76 / -24.91 |
| custo 2x / execução t+2 | -35.18 / -31.42 |
| walk-forward | -30.20 |
| sem os 10 melhores negócios | -45.15 |
| placebo p | 0.98 |
| look-ahead (truncamento) | passou |

**10 melhores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| FHER3   |      1 | 2021-04-05 00:00:00 | 2021-08-02 00:00:00 |     85 |      176.37 |        17.53 |
| VIVR3   |      1 | 2021-05-04 00:00:00 | 2021-09-01 00:00:00 |     86 |      144.73 |        14.47 |
| IGBR3   |      1 | 2020-11-04 00:00:00 | 2021-05-03 00:00:00 |    128 |      134.82 |        13.45 |
| OSXB3   |      1 | 2020-11-04 00:00:00 | 2021-02-01 00:00:00 |     63 |      130.38 |        12.98 |
| AMBP3   |      1 | 2024-08-02 00:00:00 | 2024-11-01 00:00:00 |     65 |      115.13 |        11.29 |
| MMXM3   |      1 | 2020-11-04 00:00:00 | 2021-02-01 00:00:00 |     63 |       79.21 |         7.88 |
| MLAS3   |      1 | 2023-04-04 00:00:00 | 2023-06-01 00:00:00 |     42 |       77.9  |         7.79 |
| OIBR4   |      1 | 2016-07-04 00:00:00 | 2016-09-01 00:00:00 |     43 |       72.25 |         7.22 |
| RCSL4   |      1 | 2025-12-02 00:00:00 | 2026-03-02 00:00:00 |     64 |       69.1  |         6.9  |
| OIBR3   |      1 | 2016-07-04 00:00:00 | 2016-10-03 00:00:00 |     65 |       67.83 |         6.78 |

**10 piores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| AMBP3   |      1 | 2025-10-02 00:00:00 | 2025-11-03 00:00:00 |     22 |     -145.87 |       -14.54 |
| INEP4   |      1 | 2021-05-04 00:00:00 | 2022-01-03 00:00:00 |    174 |     -136.86 |       -13.66 |
| GFSA3   |      1 | 2026-07-02 00:00:00 | 2026-08-03 00:00:00 |     22 |     -134.68 |       -13.46 |
| DMMO3   |      1 | 2020-01-03 00:00:00 | 2020-04-01 00:00:00 |     63 |     -110.95 |       -11.09 |
| PDGR3   |      1 | 2016-03-02 00:00:00 | 2016-07-01 00:00:00 |     87 |      -85.16 |        -8.51 |
| RCSL4   |      1 | 2020-03-03 00:00:00 | 2020-04-01 00:00:00 |     21 |      -65.03 |        -6.5  |
| GFSA3   |      1 | 2025-04-02 00:00:00 | 2025-06-02 00:00:00 |     43 |      -65.04 |        -6.5  |
| AMER3   |      1 | 2023-02-02 00:00:00 | 2023-04-03 00:00:00 |     42 |      -62.31 |        -6.23 |
| RCSL4   |      1 | 2024-11-04 00:00:00 | 2025-01-02 00:00:00 |     43 |      -61.33 |        -6.13 |
| AERI3   |      1 | 2024-09-03 00:00:00 | 2024-10-01 00:00:00 |     20 |      -60.74 |        -6.06 |

**Quem trouxe o retorno (soma por ativo, pp)**

| ativo   |   sum |   count |
|:--------|------:|--------:|
| FHER3   | 24.15 |       6 |
| OSXB3   | 12.98 |       1 |
| MLAS3   |  9.46 |       2 |
| TPIS3   |  6.74 |       7 |
| GOLL4   |  6.67 |       4 |
| USIM5   |  6.26 |       2 |
| BMEB4   |  5.43 |       3 |
| ALPK3   |  5.42 |       1 |
| NINJ3   |  5.15 |       1 |
| RUMO3   |  5.02 |       2 |

### Travas vendidas em 24 papéis B3 onde IV > RV (direcional / borboleta / condor)  (`op_travas_multi`)

**Tese:** Todo vencimento vendo trava de risco definido nos N papéis com maior IV/RV (a call/put de varejo cara), no lado da tendência; perda máxima = orçamento de risco do mês

**Instrumentos:** [{'onde': 'B3 (Clear/Rico/XP)', 'ticker': 'opções mensais de 24 ações/ETFs (PETR, VALE, BBAS, MGLU, ...)', 'lote': 100, 'custo': 'bid/ask do fechamento por perna + ~0,10% do prêmio; exercício 0,14%'}, {'onde': 'Tesouro Direto / B3', 'ticker': 'Tesouro Selic (garantia)', 'lote': 'R$ ~170', 'custo': 'igual ao benchmark'}]

**Aplicável:** True — Cabe: trava de 5% em papel de R$ 10–60 perde no máximo R$ 30–250 por lote; com 10% de risco/mês (R$ 2 mil) são 1–10 lotes por papel. Limite real: liquidez das séries fora de PETR/VALE/BOVA (o filtro de spread <= 25% do meio descarta muitas).

| métrica | valor |
|---|---|
| OOS desde | 2021-01 |
| retorno OOS a.a. (R$ 20 mil) | -0.8% vs CDI 11.4% |
| ativo OOS pp (R$ 20 mil / R$ 50 mil) | -12.20 / -12.84 |
| depois do IR (classe opcoes_b3) pp, 20k / 50k | -12.01 / -12.64 |
| IR OOS / Sharpe | -1.32 / -1.32 |
| pior queda | -22.0% |
| PBO / Sharpe deflacionado | 13% / +0% |
| leque de parâmetros p5 / mediana / p95 | -16.88 / -7.44 / -3.64 |
| custo 2x / execução t+2 | -13.97 / -10.16 |
| walk-forward | -9.89 |
| sem os 10 melhores negócios | -14.11 |
| placebo p | 1.00 |
| look-ahead (truncamento) | passou |

**10 melhores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| PETR    |     -1 | 2016-05-18 00:00:00 | 2016-06-20 00:00:00 |     23 |      149.17 |         2.33 |
| VVAR    |     -1 | 2020-01-22 00:00:00 | 2020-02-17 00:00:00 |     18 |      126.46 |         2.09 |
| BBAS    |     -1 | 2025-07-22 00:00:00 | 2025-08-15 00:00:00 |     18 |      104.44 |         1.61 |
| PETR    |     -1 | 2023-07-25 00:00:00 | 2023-08-18 00:00:00 |     18 |       89.65 |         1.42 |
| PETR    |     -1 | 2015-05-20 00:00:00 | 2015-06-15 00:00:00 |     18 |       93.99 |         1.41 |
| PRIO    |     -1 | 2023-09-19 00:00:00 | 2023-10-20 00:00:00 |     23 |       88.34 |         1.4  |
| PETR    |     -1 | 2016-08-17 00:00:00 | 2016-09-19 00:00:00 |     23 |       81.56 |         1.35 |
| B3SA    |     -1 | 2026-07-21 00:00:00 | 2026-08-21 00:00:00 |     23 |       80.95 |         1.12 |
| VALE    |     -1 | 2021-02-24 00:00:00 | 2021-03-15 00:00:00 |     13 |       91.16 |         1.11 |
| MGLU    |     -1 | 2024-02-20 00:00:00 | 2024-03-15 00:00:00 |     18 |       66.17 |         1.09 |

**10 piores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| ITSA    |     -1 | 2026-09-22 00:00:00 | 2026-10-13 00:00:00 |     15 |     -113.08 |        -1.83 |
| COGN    |     -1 | 2020-07-22 00:00:00 | 2020-08-17 00:00:00 |     18 |     -107.35 |        -1.77 |
| ITSA    |     -1 | 2025-08-19 00:00:00 | 2025-09-19 00:00:00 |     23 |     -104.94 |        -1.73 |
| VIIA    |     -1 | 2023-01-24 00:00:00 | 2023-02-17 00:00:00 |     18 |     -103.88 |        -1.71 |
| PETR    |     -1 | 2015-07-22 00:00:00 | 2015-08-17 00:00:00 |     18 |     -103.35 |        -1.71 |
| VVAR    |     -1 | 2020-09-23 00:00:00 | 2020-10-19 00:00:00 |     18 |     -104.88 |        -1.7  |
| COGN    |     -1 | 2021-01-20 00:00:00 | 2021-02-22 00:00:00 |     23 |     -103.16 |        -1.7  |
| VIIA    |     -1 | 2023-08-22 00:00:00 | 2023-09-15 00:00:00 |     18 |     -103.06 |        -1.7  |
| ABEV    |     -1 | 2021-04-22 00:00:00 | 2021-05-21 00:00:00 |     21 |     -104.51 |        -1.7  |
| MGLU    |     -1 | 2023-06-20 00:00:00 | 2023-07-21 00:00:00 |     23 |     -102.74 |        -1.7  |

**Quem trouxe o retorno (soma por ativo, pp)**

| ativo   |   sum |   count |
|:--------|------:|--------:|
| BOVA    |  0.99 |       5 |
| CSNA    |  0.79 |       6 |
| PRIO    |  0.58 |       4 |
| ITUB    | -0.43 |       7 |
| USIM    | -0.89 |       5 |
| LREN    | -0.96 |       1 |
| GGBR    | -1.1  |       3 |
| JBSS    | -1.61 |       2 |
| VALE    | -3.17 |      26 |
| ITSA    | -4.02 |       6 |

### Vol de evento na B3: Copom/eleição (BOVA11) e resultado (opções do papel)  (`op_eventos`)

**Tese:** Compro straddle quando o salto embutido na estrutura a termo da IV é menor que o salto histórico do tipo de evento e vendo iron butterfly quando é maior; entra na véspera, sai no dia seguinte, no bid/ask

**Instrumentos:** [{'onde': 'B3', 'ticker': 'opções mensais de BOVA11 e das ações (vencimento mais curto com >= 3 pregões)', 'lote': 100, 'custo': 'bid/ask na entrada e na saída + ~0,10% do prêmio por lado'}, {'onde': 'Tesouro Direto / B3', 'ticker': 'Tesouro Selic (garantia)', 'lote': 'R$ ~170', 'custo': 'igual ao benchmark'}]

**Aplicável:** True — Cabe: iron butterfly de 5% em PETR (R$ 30) perde no máximo ~R$ 100 por lote; straddle de BOVA11 custa ~R$ 300–600 por lote. Com 3% de risco por evento (R$ 600) são 1–5 estruturas. Liquidez: BOVA11 só a partir de 2019.

| métrica | valor |
|---|---|
| OOS desde | 2021-01 |
| retorno OOS a.a. (R$ 20 mil) | 6.6% vs CDI 11.4% |
| ativo OOS pp (R$ 20 mil / R$ 50 mil) | -4.86 / -5.80 |
| depois do IR (classe opcoes_b3) pp, 20k / 50k | -4.78 / -5.71 |
| IR OOS / Sharpe | -1.87 / -1.87 |
| pior queda | -4.0% |
| PBO / Sharpe deflacionado | 33% / +0% |
| leque de parâmetros p5 / mediana / p95 | -10.88 / -5.08 / -1.40 |
| custo 2x / execução t+2 | -7.00 / -4.58 |
| walk-forward | -2.74 |
| sem os 10 melhores negócios | -4.82 |
| placebo p | 1.00 |
| look-ahead (truncamento) | passou |

**10 melhores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| BOVA    |     -1 | 2025-12-10 00:00:00 | 2025-12-11 00:00:00 |      1 |        9.24 |         0.26 |
| BOVA    |     -1 | 2023-08-02 00:00:00 | 2023-08-03 00:00:00 |      1 |        4.05 |         0.11 |
| BOVA    |     -1 | 2025-07-30 00:00:00 | 2025-07-31 00:00:00 |      1 |        2.93 |         0.05 |
| BOVA    |     -1 | 2025-06-18 00:00:00 | 2025-06-20 00:00:00 |      2 |       -1.61 |        -0.03 |
| BOVA    |     -1 | 2024-09-18 00:00:00 | 2024-09-19 00:00:00 |      1 |       -2.62 |        -0.05 |
| BOVA    |     -1 | 2023-12-13 00:00:00 | 2023-12-14 00:00:00 |      1 |       -3.8  |        -0.07 |
| BOVA    |     -1 | 2025-03-19 00:00:00 | 2025-03-20 00:00:00 |      1 |       -5.9  |        -0.11 |
| BOVA    |     -1 | 2024-01-31 00:00:00 | 2024-02-01 00:00:00 |      1 |       -4.53 |        -0.12 |
| BOVA    |     -1 | 2024-03-20 00:00:00 | 2024-03-21 00:00:00 |      1 |       -7.17 |        -0.13 |
| BOVA    |     -1 | 2024-06-19 00:00:00 | 2024-06-20 00:00:00 |      1 |       -9.25 |        -0.14 |

**10 piores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| BOVA    |     -1 | 2026-10-02 00:00:00 | 2026-10-05 00:00:00 |      1 |     -103    |        -3.08 |
| BOVA    |     -1 | 2020-06-17 00:00:00 | 2020-06-18 00:00:00 |      1 |     -103    |        -2.9  |
| BOVA    |     -1 | 2022-05-04 00:00:00 | 2022-05-05 00:00:00 |      1 |      -71.02 |        -1.98 |
| BOVA    |     -1 | 2020-02-05 00:00:00 | 2020-02-06 00:00:00 |      1 |      -64.07 |        -1.66 |
| BOVA    |     -1 | 2021-03-17 00:00:00 | 2021-03-18 00:00:00 |      1 |      -78.21 |        -1.62 |
| BOVA    |     -1 | 2026-09-16 00:00:00 | 2026-09-17 00:00:00 |      1 |      -90    |        -1.59 |
| BOVA    |     -1 | 2025-05-07 00:00:00 | 2025-05-08 00:00:00 |      1 |      -80.17 |        -1.54 |
| BOVA    |     -1 | 2022-09-30 00:00:00 | 2022-10-03 00:00:00 |      1 |      -56.3  |        -1.48 |
| BOVA    |     -1 | 2022-09-21 00:00:00 | 2022-09-22 00:00:00 |      1 |      -55.69 |        -1.45 |
| BOVA    |     -1 | 2020-09-16 00:00:00 | 2020-09-17 00:00:00 |      1 |      -44.93 |        -1.18 |

**Quem trouxe o retorno (soma por ativo, pp)**

| ativo   |    sum |   count |
|:--------|-------:|--------:|
| BOVA    | -31.83 |      45 |

### Opção de Copom (CPM): favorito x caudas (IDI documentado: sem livro para PF)  (`op_copom`)

**Tese:** Vendo as caudas caras (5–25 pontos) da opção digital de Copom ou compro o favorito, risco definido, liquidação na decisão

**Instrumentos:** [{'onde': 'B3', 'ticker': 'CPM<mês><ano>C<strike> (opção digital de Copom)', 'lote': '1 contrato (R$ 100/ponto até jun/2025; R$ 1/ponto depois)', 'custo': 'meio spread ~1,5 ponto + tarifa'}, {'onde': 'B3', 'ticker': 'IDI (opção sobre índice DI)', 'lote': '-', 'custo': 'sem oferta no fechamento: inacessível para PF'}]

**Aplicável:** parcial: CPM só cabe em R$ 20–50 mil desde jul/2025 (lote 100x menor); IDI não — Até jun/2025 1 contrato de CPM = R$ 100 por ponto: comprar o favorito a 60 = R$ 6 mil; vender uma cauda a 15 arrisca R$ 8,5 mil. Com R$ 20 mil e 25% de risco por reunião não cabe; com R$ 50 mil cabe 1. Depois de jul/2025 cabe qualquer tamanho.

| métrica | valor |
|---|---|
| OOS desde | 2023-01 |
| retorno OOS a.a. (R$ 20 mil) | 17.5% vs CDI 13.1% |
| ativo OOS pp (R$ 20 mil / R$ 50 mil) | +4.36 / -3.07 |
| depois do IR (classe futuros_b3) pp, 20k / 50k | +3.65 / -3.10 |
| IR OOS / Sharpe | +1.02 / +1.02 |
| pior queda | 0.0% |
| PBO / Sharpe deflacionado | 40% / +0% |
| leque de parâmetros p5 / mediana / p95 | +1.67 / +4.85 / +10.91 |
| custo 2x / execução t+2 | +3.44 / +4.26 |
| walk-forward | -55.97 |
| sem os 10 melhores negócios | +0.36 |
| placebo p | 0.00 |
| look-ahead (truncamento) | passou |

**10 melhores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| CPM     |     -1 | 2026-04-06 00:00:00 | 2026-04-30 00:00:00 |     18 |       21.22 |         5.25 |
| CPM     |     -1 | 2026-05-06 00:00:00 | 2026-06-18 00:00:00 |     31 |       13.5  |         3.33 |
| CPM     |     -1 | 2026-03-04 00:00:00 | 2026-03-19 00:00:00 |     11 |        6.95 |         1.72 |
| CPM     |     -1 | 2025-10-03 00:00:00 | 2025-12-11 00:00:00 |     49 |        5.26 |         1.3  |
| CPM     |     -1 | 2026-08-05 00:00:00 | 2026-09-17 00:00:00 |     31 |        5.12 |         1.27 |
| CPM     |     -1 | 2025-11-05 00:00:00 | 2025-12-11 00:00:00 |     26 |        4.83 |         1.2  |
| CPM     |     -1 | 2026-02-04 00:00:00 | 2026-03-19 00:00:00 |     31 |        4.69 |         0.58 |
| CPM     |     -1 | 2026-02-04 00:00:00 | 2026-03-19 00:00:00 |     31 |        3.52 |         0.43 |

**10 piores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| CPM     |     -1 | 2026-02-04 00:00:00 | 2026-03-19 00:00:00 |     31 |        3.52 |         0.43 |
| CPM     |     -1 | 2026-02-04 00:00:00 | 2026-03-19 00:00:00 |     31 |        4.69 |         0.58 |
| CPM     |     -1 | 2025-11-05 00:00:00 | 2025-12-11 00:00:00 |     26 |        4.83 |         1.2  |
| CPM     |     -1 | 2026-08-05 00:00:00 | 2026-09-17 00:00:00 |     31 |        5.12 |         1.27 |
| CPM     |     -1 | 2025-10-03 00:00:00 | 2025-12-11 00:00:00 |     49 |        5.26 |         1.3  |
| CPM     |     -1 | 2026-03-04 00:00:00 | 2026-03-19 00:00:00 |     11 |        6.95 |         1.72 |
| CPM     |     -1 | 2026-05-06 00:00:00 | 2026-06-18 00:00:00 |     31 |       13.5  |         3.33 |
| CPM     |     -1 | 2026-04-06 00:00:00 | 2026-04-30 00:00:00 |     18 |       21.22 |         5.25 |

**Quem trouxe o retorno (soma por ativo, pp)**

| ativo   |   sum |   count |
|:--------|------:|--------:|
| CPM     | 15.08 |       8 |

### Wheel em ações isentas (put coberta por Selic -> ação -> call coberta)  (`op_wheel`)

**Tese:** Vendo put com caixa em Tesouro Selic; exercido, fico com a ação (isenta) e vendo call acima do custo; chamado, volto à put

**Instrumentos:** [{'onde': 'B3', 'ticker': 'PETR4/VALE3/ITUB4 (+BBDC4/BBAS3/ABEV3) e suas opções mensais', 'lote': 100, 'custo': 'bid/ask do fechamento + 0,10% do prêmio; exercício 0,03%'}, {'onde': 'Tesouro Direto / B3', 'ticker': 'Tesouro Selic (garantia da put)', 'lote': 'R$ ~170', 'custo': 'igual ao benchmark'}]

**Aplicável:** True — Cabe: 1 lote de PETR4 a R$ 30 = R$ 3 mil de garantia; com R$ 20 mil, 1–2 lotes de 3 papéis. Com 6 papéis e R$ 20 mil alguns ficam sem lote (VALE3 a R$ 60–80 = R$ 6–8 mil por lote).

| métrica | valor |
|---|---|
| OOS desde | 2021-01 |
| retorno OOS a.a. (R$ 20 mil) | 17.6% vs CDI 11.4% |
| ativo OOS pp (R$ 20 mil / R$ 50 mil) | +6.20 / +3.13 |
| depois do IR (classe opcoes_b3) pp, 20k / 50k | +5.09 / +2.49 |
| IR OOS / Sharpe | +0.64 / +0.64 |
| pior queda | -14.8% |
| PBO / Sharpe deflacionado | 54% / +74% |
| leque de parâmetros p5 / mediana / p95 | +2.60 / +6.24 / +8.52 |
| custo 2x / execução t+2 | +5.95 / +9.90 |
| walk-forward | +3.40 |
| sem os 10 melhores negócios | -1.88 |
| placebo p | 0.00 |
| look-ahead (truncamento) | passou |

**10 melhores negócios**

| ativo     |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:----------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| VALE_acao |      1 | 2025-08-15 00:00:00 | 2026-02-20 00:00:00 |    135 |       58.04 |        16.12 |
| PETR_acao |      1 | 2018-06-18 00:00:00 | 2018-10-15 00:00:00 |     85 |       47.59 |        10.93 |
| PETR_acao |      1 | 2020-10-19 00:00:00 | 2021-04-19 00:00:00 |    130 |       27.16 |         7.96 |
| VALE_acao |      1 | 2019-02-18 00:00:00 | 2020-07-20 00:00:00 |    370 |       25.26 |         6.81 |
| PETR_acao |      1 | 2022-09-16 00:00:00 | 2022-10-21 00:00:00 |     25 |       20.14 |         6.55 |
| PETR_put  |     -1 | 2020-03-18 00:00:00 | 2020-04-20 00:00:00 |     23 |       17.84 |         5.99 |
| ITUB_acao |      1 | 2017-12-18 00:00:00 | 2018-02-19 00:00:00 |     45 |       26.06 |         5.56 |
| PETR_acao |      1 | 2026-05-15 00:00:00 | 2026-10-13 00:00:00 |    107 |       23.92 |         5.53 |
| PETR_acao |      1 | 2024-05-17 00:00:00 | 2026-03-20 00:00:00 |    480 |       23.37 |         4.7  |
| PETR_acao |      1 | 2022-03-18 00:00:00 | 2022-04-14 00:00:00 |     19 |       10.25 |         3.36 |

**10 piores negócios**

| ativo     |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:----------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| PETR_put  |     -1 | 2018-05-23 00:00:00 | 2018-06-18 00:00:00 |     18 |      -33.05 |        -7.59 |
| PETR_call |     -1 | 2022-09-20 00:00:00 | 2022-10-21 00:00:00 |     23 |      -13.48 |        -4.19 |
| VALE_put  |     -1 | 2019-01-23 00:00:00 | 2019-02-18 00:00:00 |     18 |      -14.1  |        -3.8  |
| PETR_call |     -1 | 2018-04-18 00:00:00 | 2018-05-21 00:00:00 |     23 |       -9.25 |        -3.03 |
| PETR_call |     -1 | 2018-09-19 00:00:00 | 2018-10-15 00:00:00 |     18 |      -13.1  |        -2.62 |
| ITUB_put  |     -1 | 2026-02-24 00:00:00 | 2026-03-20 00:00:00 |     18 |       -9.08 |        -2.11 |
| PETR_call |     -1 | 2026-02-24 00:00:00 | 2026-03-20 00:00:00 |     18 |      -10.17 |        -2.01 |
| ITUB_put  |     -1 | 2020-07-22 00:00:00 | 2020-08-17 00:00:00 |     18 |       -6.1  |        -1.61 |
| VALE_call |     -1 | 2026-01-20 00:00:00 | 2026-02-20 00:00:00 |     23 |       -3.59 |        -1.44 |
| PETR_put  |     -1 | 2022-02-22 00:00:00 | 2022-03-18 00:00:00 |     18 |       -3.79 |        -1.24 |

**Quem trouxe o retorno (soma por ativo, pp)**

| ativo     |   sum |   count |
|:----------|------:|--------:|
| PETR_acao | 38.3  |       7 |
| VALE_acao | 22.93 |       2 |
| ITUB_acao | 14.62 |       6 |
| PETR_put  | 10.45 |      22 |
| ITUB_call |  1.24 |      15 |
| ITUB_put  |  0.58 |      20 |
| VALE_call | -0.15 |       9 |
| VALE_put  | -0.52 |       9 |
| PETR_call | -1.69 |      16 |
