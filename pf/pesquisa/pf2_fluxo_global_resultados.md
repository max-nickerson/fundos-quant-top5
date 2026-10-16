# Frente pf2_fluxo_global — resultados da bateria final (gerado automaticamente)

Gerado por `pf/gerar_cadernos.py` a partir de `pf/resultados/bateria/`. IR de pessoa física por `pf/ir.py` (mensal na B3 com isenção de ações ≤ R$ 20 mil/mês, anual no exterior). Ordem: nota do ranking.

### Fim de mês dos balanceados + reversão dos ETFs alavancados no IVVB11 (B3)  (`fg_fim_mes`)

**Tese:** Comprado em IVVB11 nos 4 últimos pregões do mês quando as ações apanharam dos títulos (os balanceados compram); day trade contra o rebalanceamento dos ETFs alavancados depois de dias de movimento forte do S&P.

**Instrumentos:** {'IVVB11': {'onde': 'B3', 'ticker': 'IVVB11', 'lote': '1 cota (~R$ 440)', 'custo': 'meio spread real + 0,03% emolumentos'}, 'caixa': {'onde': 'Tesouro Selic / LFTS11', 'ticker': 'LFT', 'lote': 'R$ ~150', 'custo': '0'}}

**Aplicável:** True — Operável em qualquer corretora (IVVB11 líquido, cota de R$ 440, sem remessa). A perna vendida do fim de mês exigiria aluguel por 4 dias (0,5% por contrato na Clear/Rico) e ficou de fora.

| métrica | valor |
|---|---|
| OOS desde | 2021-01 |
| retorno OOS a.a. (R$ 20 mil) | 11.4% vs CDI 11.4% |
| ativo OOS pp (R$ 20 mil / R$ 50 mil) | -0.06 / -0.06 |
| depois do IR (classe etf_b3) pp, 20k / 50k | -0.12 / -0.13 |
| IR OOS / Sharpe | +0.00 / +0.00 |
| pior queda | -4.8% |
| PBO / Sharpe deflacionado | 5% / +0% |
| leque de parâmetros p5 / mediana / p95 | -1.65 / +0.26 / +0.98 |
| custo 2x / execução t+2 | -0.58 / -0.21 |
| walk-forward | +0.46 |
| sem os 10 melhores negócios | -2.35 |
| placebo p | 0.29 |
| look-ahead (truncamento) | passou |

**10 melhores negócios**

| ativo                   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:------------------------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| IVVB11 fim de trimestre |      1 | 2020-03-25 00:00:00 | 2020-03-31 00:00:00 |      4 |        7.8  |         7.31 |
| IVVB11 fim de trimestre |      1 | 2020-09-24 00:00:00 | 2020-09-30 00:00:00 |      4 |        5.68 |         5.4  |
| IVVB11 fim de mês       |      1 | 2024-08-26 00:00:00 | 2024-08-30 00:00:00 |      4 |        3.18 |         2.9  |
| IVVB11 fim de trimestre |      1 | 2019-03-25 00:00:00 | 2019-03-29 00:00:00 |      4 |        2.84 |         2.42 |
| IVVB11 fim de trimestre |      1 | 2021-06-24 00:00:00 | 2021-06-30 00:00:00 |      4 |        2.56 |         2.29 |
| IVVB11 fim de mês       |      1 | 2017-11-24 00:00:00 | 2017-11-30 00:00:00 |      4 |        2.84 |         2.15 |
| IVVB11 fim de trimestre |      1 | 2022-12-26 00:00:00 | 2022-12-30 00:00:00 |      4 |        2.47 |         2.13 |
| IVVB11 fim de mês       |      1 | 2015-07-27 00:00:00 | 2015-07-31 00:00:00 |      4 |        3.61 |         2.02 |
| IVVB11 fim de mês       |      1 | 2022-05-25 00:00:00 | 2022-05-31 00:00:00 |      4 |        2.05 |         1.71 |
| IVVB11 fim de mês       |      1 | 2015-08-25 00:00:00 | 2015-08-31 00:00:00 |      4 |        4.43 |         1.66 |

**10 piores negócios**

| ativo                   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:------------------------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| IVVB11 fim de mês       |      1 | 2019-05-27 00:00:00 | 2019-05-31 00:00:00 |      4 |       -5.31 |        -5.61 |
| IVVB11 fim de trimestre |      1 | 2022-06-24 00:00:00 | 2022-06-30 00:00:00 |      4 |       -3.9  |        -4.2  |
| IVVB11 fim de trimestre |      1 | 2015-09-24 00:00:00 | 2015-09-30 00:00:00 |      4 |       -0.6  |        -4.15 |
| IVVB11 fim de mês       |      1 | 2014-10-27 00:00:00 | 2014-10-31 00:00:00 |      4 |        0.85 |        -3.39 |
| IVVB11 fim de mês       |      1 | 2022-11-24 00:00:00 | 2022-11-30 00:00:00 |      4 |       -2.6  |        -2.96 |
| IVVB11 fim de mês       |      1 | 2015-01-26 00:00:00 | 2015-01-30 00:00:00 |      4 |        1.67 |        -2.6  |
| IVVB11 fim de trimestre |      1 | 2015-03-25 00:00:00 | 2015-03-31 00:00:00 |      4 |        0.12 |        -2.08 |
| IVVB11 fim de trimestre |      1 | 2021-09-24 00:00:00 | 2021-09-30 00:00:00 |      4 |       -1.54 |        -1.86 |
| IVVB11 fim de trimestre |      1 | 2022-09-26 00:00:00 | 2022-09-30 00:00:00 |      4 |       -1.32 |        -1.67 |
| IVVB11 fim de trimestre |      1 | 2017-06-26 00:00:00 | 2017-06-30 00:00:00 |      4 |       -0.12 |        -1.22 |

**Quem trouxe o retorno (soma por ativo, pp)**

| ativo                   |   sum |   count |
|:------------------------|------:|--------:|
| IVVB11 fim de trimestre |  6.09 |      16 |
| IVVB11 fim de mês       |  2.4  |      22 |

### Reconstituição do Russell 2000: quem cai para micro cap comprado no leilão de junho (PF IBKR)  (`fg_russell`)

**Tese:** Compro no leilão de fechamento da reconstituição (última sexta de junho) as ações que saem do Russell 2000 para baixo — vendidas por todos os indexados — e seguro algumas semanas com IWM vendido; R$ 1 mil por nome.

**Instrumentos:** {'saídas/entradas do Russell 2000': {'onde': 'IBKR', 'ticker': 'até 20 por ano', 'lote': 'fração', 'custo': 'US$ 0,0035/ação mín. 0,35 + 0,4%'}, 'IWM': {'onde': 'IBKR (vendido)', 'ticker': 'IWM', 'lote': 'ações inteiras', 'custo': 'aluguel 0,3% a.a.'}}

**Aplicável:** True — Operável (ordem MOC na IBKR no dia da reconstituição, lista preliminar pública desde maio). Só 7 reconstituições com a composição real (N-PORT do IWM) -> amostra pequena.

| métrica | valor |
|---|---|
| OOS desde | 2023-01 |
| retorno OOS a.a. (R$ 20 mil) | 9.0% vs CDI 13.1% |
| ativo OOS pp (R$ 20 mil / R$ 50 mil) | -4.07 / -0.81 |
| depois do IR (classe exterior) pp, 20k / 50k | -4.00 / -0.80 |
| IR OOS / Sharpe | -0.05 / -0.05 |
| pior queda | -30.8% |
| PBO / Sharpe deflacionado | 0% / +1% |
| leque de parâmetros p5 / mediana / p95 | -9.60 / -6.65 / -2.52 |
| custo 2x / execução t+2 | -10.29 / -5.11 |
| walk-forward | -4.07 |
| sem os 10 melhores negócios | -17.28 |
| placebo p | 0.08 |
| look-ahead (truncamento) | passou |

**10 melhores negócios**

| ativo               |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------------------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| VTGN                |      1 | 2023-06-30 00:00:00 | 2023-09-26 00:00:00 |     60 |      186.63 |        11.36 |
| RCEL                |      1 | 2026-06-26 00:00:00 | 2026-09-22 00:00:00 |     60 |      189.42 |         9.92 |
| STIM                |      1 | 2026-06-26 00:00:00 | 2026-09-22 00:00:00 |     60 |      117.16 |         6.41 |
| hedge (resíduo) IWM |     -1 | 2022-01-03 00:00:00 | 2022-12-30 00:00:00 |    251 |      nan    |         4.66 |
| GALT                |      1 | 2025-06-27 00:00:00 | 2025-09-23 00:00:00 |     60 |      106.44 |         4.23 |
| LUNG                |      1 | 2026-06-26 00:00:00 | 2026-09-22 00:00:00 |     60 |       64.8  |         3.39 |
| hedge (resíduo) IWM |     -1 | 2026-01-02 00:00:00 | 2026-10-15 00:00:00 |    198 |      nan    |         3.13 |
| MYO                 |      1 | 2026-06-26 00:00:00 | 2026-09-22 00:00:00 |     60 |       59.22 |         2.98 |
| VIP                 |      1 | 2023-06-30 00:00:00 | 2023-09-26 00:00:00 |     60 |       42.2  |         2.81 |
| EXFY                |      1 | 2026-06-26 00:00:00 | 2026-09-22 00:00:00 |     60 |       45.06 |         2.81 |

**10 piores negócios**

| ativo               |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------------------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| hedge (resíduo) IWM |     -1 | 2020-01-02 00:00:00 | 2020-12-31 00:00:00 |    253 |      nan    |        -2.86 |
| ORBS                |      1 | 2023-06-30 00:00:00 | 2023-09-26 00:00:00 |     60 |      -56.81 |        -2.74 |
| BKKT                |      1 | 2024-06-28 00:00:00 | 2024-09-24 00:00:00 |     60 |      -50.58 |        -2.74 |
| RENT                |      1 | 2024-06-28 00:00:00 | 2024-09-24 00:00:00 |     60 |      -45.19 |        -2.56 |
| OTLK                |      1 | 2025-06-27 00:00:00 | 2025-09-23 00:00:00 |     60 |      -39.31 |        -2.45 |
| hedge (resíduo) IWM |     -1 | 2021-01-04 00:00:00 | 2021-12-31 00:00:00 |    252 |      nan    |        -2.41 |
| TZOO                |      1 | 2026-06-26 00:00:00 | 2026-09-22 00:00:00 |     60 |      -49.19 |        -2.41 |
| AMPY                |      1 | 2020-06-26 00:00:00 | 2020-09-22 00:00:00 |     60 |      -39.85 |        -2.36 |
| DTI                 |      1 | 2025-06-27 00:00:00 | 2025-09-23 00:00:00 |     60 |      -37.66 |        -2.32 |
| CIRC                |      1 | 2026-06-26 00:00:00 | 2026-09-22 00:00:00 |     60 |      -53.41 |        -2.11 |

**Quem trouxe o retorno (soma por ativo, pp)**

| ativo               |   sum |   count |
|:--------------------|------:|--------:|
| VTGN                | 11.36 |       1 |
| RCEL                |  9.92 |       1 |
| STIM                |  6.41 |       1 |
| hedge (resíduo) IWM |  4.26 |       7 |
| GALT                |  4.23 |       1 |
| LUNG                |  3.39 |       1 |
| MYO                 |  2.98 |       1 |
| TUSK                |  2.93 |       2 |
| VIP                 |  2.81 |       1 |
| EXFY                |  2.81 |       1 |

### Spin-offs pequenos dos EUA após a venda forçada (PF: IBKR, sobrevivência tratada)  (`fg_spinoff_pequeno`)

**Tese:** Compro a separada PEQUENA (giro < US$ 10 mi/dia) no fim do 1º mês, quando os indexados da controladora já venderam; seguro 6–12 meses com IWM vendido; R$ 1–2,5 mil por nome; sintéticos para quem sumiu do Yahoo.

**Instrumentos:** {'spin-offs': {'onde': 'IBKR', 'ticker': '~5–10 pequenos por ano', 'lote': 'fração', 'custo': 'US$ 0,0035/ação mín. 0,35 + 0,4%'}, 'IWM': {'onde': 'IBKR (vendido)', 'ticker': 'IWM', 'lote': 'ações inteiras', 'custo': 'aluguel 0,3% a.a.'}, 'WDO': {'onde': 'B3', 'ticker': 'WDO (vendido)', 'lote': '1 contrato = US$ 10 mil', 'custo': 'R$ 3,70/lado, rola todo mês'}}

**Aplicável:** True — Operável na IBKR com fração (R$ 1–2,5 mil por nome); hedge em ações inteiras de IWM (~R$ 1,3 mil) e conta margem com US$ 2 mil. Poucos nomes por ano: carteira concentrada.

| métrica | valor |
|---|---|
| OOS desde | 2021-01 |
| retorno OOS a.a. (R$ 20 mil) | 4.9% vs CDI 11.4% |
| ativo OOS pp (R$ 20 mil / R$ 50 mil) | -6.54 / -4.22 |
| depois do IR (classe exterior) pp, 20k / 50k | -6.44 / -4.15 |
| IR OOS / Sharpe | -0.40 / -0.40 |
| pior queda | -20.6% |
| PBO / Sharpe deflacionado | 13% / +7% |
| leque de parâmetros p5 / mediana / p95 | -8.94 / -5.89 / -3.11 |
| custo 2x / execução t+2 | -8.72 / -6.67 |
| walk-forward | -6.54 |
| sem os 10 melhores negócios | -14.16 |
| placebo p | 0.34 |
| look-ahead (truncamento) | passou |

**10 melhores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| PRTA    |      1 | 2013-02-22 00:00:00 | 2014-02-24 00:00:00 |    252 |      373.67 |        17.97 |
| CRNC    |      1 | 2019-11-12 00:00:00 | 2020-11-11 00:00:00 |    252 |      316.85 |        15.96 |
| RHLD    |      1 | 2025-04-23 00:00:00 | 2026-04-24 00:00:00 |    252 |      435.84 |        15.1  |
| CLW     |      1 | 2009-02-05 00:00:00 | 2010-02-05 00:00:00 |    252 |      352.67 |        12.68 |
| VRTS    |      1 | 2009-03-04 00:00:00 | 2010-03-04 00:00:00 |    252 |      409.65 |        10.31 |
| MPTI    |      1 | 2022-11-30 00:00:00 | 2023-12-01 00:00:00 |    252 |      227.03 |        10.29 |
| XPEL    |      1 | 2019-08-28 00:00:00 | 2020-08-27 00:00:00 |    252 |      151.01 |         9    |
| ASIX    |      1 | 2016-11-11 00:00:00 | 2017-11-13 00:00:00 |    252 |      159.31 |         6.62 |
| TRAX    |      1 | 2026-06-03 00:00:00 | 2026-10-14 00:00:00 |     92 |      122.78 |         6.41 |
| VAC     |      1 | 2012-01-09 00:00:00 | 2013-01-10 00:00:00 |    252 |      142.3  |         5.8  |

**10 piores negócios**

| ativo       |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:------------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| FEAM        |      1 | 2022-05-12 00:00:00 | 2023-05-15 00:00:00 |    252 |      -84.36 |        -5.1  |
| ENVA        |      1 | 2015-01-14 00:00:00 | 2016-01-14 00:00:00 |    252 |      -72.26 |        -4.97 |
| MDIA        |      1 | 2020-03-05 00:00:00 | 2021-03-05 00:00:00 |    252 |      -51.61 |        -4.27 |
| KLXE        |      1 | 2018-10-26 00:00:00 | 2019-10-29 00:00:00 |    252 |      -70.79 |        -3.96 |
| WBDG*200806 |      1 | 2009-03-16 00:00:00 | 2010-03-16 00:00:00 |    252 |      -23.55 |        -3.48 |
| BXRX*201910 |      1 | 2020-01-13 00:00:00 | 2021-01-12 00:00:00 |    252 |      -23.55 |        -3.26 |
| CFRI*200811 |      1 | 2009-04-16 00:00:00 | 2010-04-16 00:00:00 |    252 |      -23.55 |        -2.73 |
| DRTT*201909 |      1 | 2019-12-05 00:00:00 | 2020-12-04 00:00:00 |    252 |      -23.55 |        -2.72 |
| SGD*202212  |      1 | 2023-11-14 00:00:00 | 2024-11-14 00:00:00 |    252 |      -23.55 |        -2.69 |
| ERA*201210  |      1 | 2013-03-15 00:00:00 | 2014-03-17 00:00:00 |    252 |      -23.55 |        -2.52 |

**Quem trouxe o retorno (soma por ativo, pp)**

| ativo   |   sum |   count |
|:--------|------:|--------:|
| PRTA    | 17.97 |       1 |
| CRNC    | 15.96 |       1 |
| RHLD    | 15.1  |       1 |
| CLW     | 12.68 |       1 |
| VRTS    | 10.31 |       1 |
| MPTI    | 10.29 |       1 |
| XPEL    |  9    |       1 |
| ASIX    |  6.62 |       1 |
| TRAX    |  6.41 |       1 |
| VAC     |  5.8  |       1 |

### Fim do quiet period de IPOs nos EUA (compra antes das coberturas) — PF IBKR  (`fg_ipo_quiet`)

**Tese:** Compro o IPO alguns pregões antes do dia 25 (fim do quiet period, quando os bancos do sindicato iniciam cobertura em bloco) e vendo logo depois; hedge IWM; R$ 1 mil por IPO; caixa no CDI.

**Instrumentos:** {'IPOs': {'onde': 'IBKR', 'ticker': '~100–200/ano', 'lote': 'fração', 'custo': 'US$ 0,0035/ação mín. 0,35 + 0,3%'}, 'IWM': {'onde': 'IBKR (vendido)', 'ticker': 'IWM', 'lote': 'ações inteiras', 'custo': 'aluguel 0,3% a.a.'}, 'WDO': {'onde': 'B3', 'ticker': 'WDO (vendido)', 'lote': 'US$ 10 mil', 'custo': 'R$ 3,70/lado'}}

**Aplicável:** True — Operável: data do fim do quiet period é conhecida desde o IPO; IBKR compra fração (R$ 1 mil por IPO). A perna vendida do lock-up depende de haver ação para alugar na IBKR, o que em IPO pequeno muitas vezes não há (ou a taxa explode).

| métrica | valor |
|---|---|
| OOS desde | 2021-01 |
| retorno OOS a.a. (R$ 20 mil) | -16.1% vs CDI 11.4% |
| ativo OOS pp (R$ 20 mil / R$ 50 mil) | -27.53 / -25.03 |
| depois do IR (classe exterior) pp, 20k / 50k | -27.10 / -24.64 |
| IR OOS / Sharpe | -0.59 / -0.59 |
| pior queda | -78.7% |
| PBO / Sharpe deflacionado | 37% / +2% |
| leque de parâmetros p5 / mediana / p95 | -41.74 / -24.26 / -18.58 |
| custo 2x / execução t+2 | -33.24 / -28.39 |
| walk-forward | -27.53 |
| sem os 10 melhores negócios | -31.18 |
| placebo p | 1.00 |
| look-ahead (truncamento) | passou |

**10 melhores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| ANPA    |      1 | 2025-07-23 00:00:00 | 2025-08-04 00:00:00 |      8 |       62.13 |         5.02 |
| CMRC    |      1 | 2020-08-19 00:00:00 | 2020-08-31 00:00:00 |      8 |       79.71 |         3.71 |
| EDIT    |      1 | 2016-02-17 00:00:00 | 2016-02-29 00:00:00 |      8 |       73.35 |         3.55 |
| NRIX    |      1 | 2020-08-06 00:00:00 | 2020-08-18 00:00:00 |      8 |       57.38 |         2.84 |
| DLO     |      1 | 2021-06-16 00:00:00 | 2021-06-28 00:00:00 |      8 |       56.03 |         2.78 |
| BDSX    |      1 | 2020-11-11 00:00:00 | 2020-11-23 00:00:00 |      8 |       50.21 |         2.26 |
| SDGR    |      1 | 2020-02-19 00:00:00 | 2020-03-02 00:00:00 |      8 |       25.28 |         2.17 |
| ATAT    |      1 | 2022-11-23 00:00:00 | 2022-12-06 00:00:00 |      8 |       38.45 |         2.05 |
| ANGI    |      1 | 2011-11-30 00:00:00 | 2011-12-12 00:00:00 |      8 |       42.65 |         1.96 |
| ZNTL    |      1 | 2020-04-16 00:00:00 | 2020-04-28 00:00:00 |      8 |       45.9  |         1.96 |

**10 piores negócios**

| ativo               |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------------------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| CCTG                |      1 | 2024-01-31 00:00:00 | 2024-02-12 00:00:00 |      8 |      -83.06 |        -4.95 |
| TNON                |      1 | 2022-05-11 00:00:00 | 2022-05-23 00:00:00 |      8 |      -88.7  |        -4.8  |
| FOFO                |      1 | 2025-09-25 00:00:00 | 2025-10-07 00:00:00 |      8 |      -59.76 |        -4.76 |
| JDZG                |      1 | 2024-05-29 00:00:00 | 2024-06-10 00:00:00 |      8 |      -91.76 |        -4.74 |
| MNDR                |      1 | 2024-04-24 00:00:00 | 2024-05-06 00:00:00 |      8 |      -89.28 |        -4.71 |
| SHPH                |      1 | 2022-09-14 00:00:00 | 2022-09-26 00:00:00 |      8 |      -83.07 |        -3.81 |
| MEGL                |      1 | 2022-08-18 00:00:00 | 2022-08-30 00:00:00 |      8 |      -57.23 |        -2.83 |
| VAXX                |      1 | 2021-11-23 00:00:00 | 2021-12-06 00:00:00 |      8 |      -55.64 |        -2.55 |
| hedge (resíduo) IWM |     -1 | 2021-01-04 00:00:00 | 2021-12-31 00:00:00 |    252 |      nan    |        -2.07 |
| DIDIY               |      1 | 2021-07-14 00:00:00 | 2021-07-26 00:00:00 |      8 |      -36.29 |        -2    |

**Quem trouxe o retorno (soma por ativo, pp)**

| ativo   |   sum |   count |
|:--------|------:|--------:|
| ANPA    |  5.02 |       1 |
| CMRC    |  3.71 |       1 |
| EDIT    |  3.55 |       1 |
| NRIX    |  2.84 |       1 |
| DLO     |  2.78 |       1 |
| BDSX    |  2.26 |       1 |
| SDGR    |  2.17 |       1 |
| ATAT    |  2.05 |       1 |
| ANGI    |  1.96 |       1 |
| ZNTL    |  1.96 |       1 |

### Excluídos de índice após a venda forçada (S&P 500, Nasdaq-100, DAX, CAC) — PF IBKR  (`fg_indices_exclusao`)

**Tese:** Compro no leilão de fechamento o papel que os indexados vendem na véspera da exclusão (só exclusão por valor de mercado), seguro algumas semanas com hedge em SPY/QQQ/EWG/EWQ vendidos; caixa no CDI.

**Instrumentos:** {'ações excluídas': {'onde': 'IBKR (NYSE/Nasdaq/Xetra/Euronext)', 'ticker': '~25/ano', 'lote': 'fração (EUA), inteira (Europa)', 'custo': 'US$ 0,0035/ação mín. 0,35; Europa 0,05% mín. € 1,75; TTF 0,4% (FR)'}, 'hedge': {'onde': 'IBKR', 'ticker': 'SPY/QQQ/EWG/EWQ vendidos', 'lote': 'ações inteiras', 'custo': 'aluguel 0,25–0,5% a.a.'}, 'caixa': {'onde': 'Tesouro Selic', 'ticker': 'LFT', 'lote': 'R$ ~150', 'custo': '0'}}

**Aplicável:** True — Operável: a exclusão é anunciada 1–4 semanas antes (S&P/Nasdaq) e o PF manda ordem MOC na IBKR no dia da venda dos indexados; 10% por nome = R$ 2 mil com R$ 20 mil (0,2% de comissão mínima). Vender SPY exige conta margem com US$ 2 mil parados.

| métrica | valor |
|---|---|
| OOS desde | 2021-01 |
| retorno OOS a.a. (R$ 20 mil) | -4.6% vs CDI 11.4% |
| ativo OOS pp (R$ 20 mil / R$ 50 mil) | -16.06 / -9.23 |
| depois do IR (classe exterior) pp, 20k / 50k | -15.81 / -9.09 |
| IR OOS / Sharpe | -0.79 / -0.79 |
| pior queda | -40.1% |
| PBO / Sharpe deflacionado | 24% / +0% |
| leque de parâmetros p5 / mediana / p95 | -21.63 / -18.84 / -12.35 |
| custo 2x / execução t+2 | -20.38 / -16.18 |
| walk-forward | -22.21 |
| sem os 10 melhores negócios | -23.16 |
| placebo p | 0.18 |
| look-ahead (truncamento) | passou |

**10 melhores negócios**

| ativo                   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:------------------------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| SIRI                    |      1 | 2008-12-19 00:00:00 | 2009-03-17 00:00:00 |     60 |      183.33 |        14.78 |
| COTY                    |      1 | 2020-09-18 00:00:00 | 2020-12-10 00:00:00 |     60 |      133.77 |        11.54 |
| FMCC                    |      1 | 2008-09-11 00:00:00 | 2008-12-04 00:00:00 |     60 |       49.15 |        11.24 |
| NFLX                    |      1 | 2012-12-21 00:00:00 | 2013-03-18 00:00:00 |     60 |      103.19 |         9.05 |
| FNMA                    |      1 | 2008-09-11 00:00:00 | 2008-12-04 00:00:00 |     60 |       11.54 |         7.11 |
| hedge (resíduo) SPY+QQQ |     -1 | 2018-01-01 00:00:00 | 2018-12-31 00:00:00 |    259 |      nan    |         6.74 |
| MBI                     |      1 | 2009-12-17 00:00:00 | 2010-03-15 00:00:00 |     60 |       72.56 |         6.59 |
| UAL                     |      1 | 2008-07-18 00:00:00 | 2008-10-10 00:00:00 |     60 |       10.46 |         6.29 |
| KSS                     |      1 | 2020-09-18 00:00:00 | 2020-12-10 00:00:00 |     60 |       68.03 |         5.72 |
| ILMN                    |      1 | 2011-12-16 00:00:00 | 2012-03-09 00:00:00 |     60 |       86.25 |         5.65 |

**10 piores negócios**

| ativo                   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:------------------------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| hedge (resíduo) SPY+QQQ |     -1 | 2023-01-02 00:00:00 | 2023-12-29 00:00:00 |    258 |      nan    |        -7.98 |
| hedge (resíduo) SPY+QQQ |     -1 | 2009-01-02 00:00:00 | 2009-12-31 00:00:00 |    258 |      nan    |        -6.27 |
| LAMR                    |      1 | 2008-12-19 00:00:00 | 2009-03-17 00:00:00 |     60 |      -48.45 |        -4.83 |
| HAS                     |      1 | 2019-12-20 00:00:00 | 2020-03-13 00:00:00 |     60 |      -46.54 |        -4.48 |
| WYNN                    |      1 | 2019-12-20 00:00:00 | 2020-03-13 00:00:00 |     60 |      -47.03 |        -4.48 |
| hedge (resíduo) SPY+QQQ |     -1 | 2012-01-02 00:00:00 | 2012-12-31 00:00:00 |    259 |      nan    |        -4.07 |
| LCID                    |      1 | 2023-12-15 00:00:00 | 2024-03-11 00:00:00 |     60 |      -37.32 |        -3.89 |
| MAC                     |      1 | 2019-12-20 00:00:00 | 2020-03-13 00:00:00 |     60 |      -47.59 |        -3.73 |
| LUMN                    |      1 | 2023-03-17 00:00:00 | 2023-06-12 00:00:00 |     60 |      -26.21 |        -3.45 |
| TRIP                    |      1 | 2019-12-20 00:00:00 | 2020-03-13 00:00:00 |     60 |      -43.18 |        -3.37 |

**Quem trouxe o retorno (soma por ativo, pp)**

| ativo   |   sum |   count |
|:--------|------:|--------:|
| SIRI    | 13.23 |       2 |
| COTY    | 11.54 |       1 |
| FMCC    | 11.24 |       1 |
| NFLX    |  9.05 |       1 |
| SOLS    |  7.86 |       2 |
| FNMA    |  7.11 |       1 |
| MBI     |  6.59 |       1 |
| KSS     |  5.72 |       1 |
| UAL     |  5.37 |       2 |
| RIVN    |  5.24 |       1 |

### Tax-loss selling de dezembro: small caps perdedoras dos EUA de dezembro a janeiro (PF IBKR)  (`fg_taxloss`)

**Tese:** Compro na 2ª quinzena de dezembro as small caps que mais caíram no ano (venda para abater imposto e window dressing) e vendo em janeiro; hedge IWM; R$ 1 mil por nome; o resto do ano o caixa fica no CDI.

**Instrumentos:** {'small caps perdedoras': {'onde': 'IBKR', 'ticker': 'até 20 por ano', 'lote': 'fração', 'custo': 'US$ 0,0035/ação mín. 0,35 + 0,4%'}, 'IWM': {'onde': 'IBKR (vendido)', 'ticker': 'IWM', 'lote': 'ações inteiras', 'custo': 'aluguel 0,3% a.a.'}, 'variante': {'onde': 'IBKR', 'ticker': 'IWC comprado / SPY vendido', 'lote': 'ações inteiras', 'custo': 'spread + aluguel'}}

**Aplicável:** True — Operável: 1 vez por ano, 20 ordens de compra e 20 de venda na IBKR com fração; precisa remeter em dezembro e trazer de volta.

| métrica | valor |
|---|---|
| OOS desde | 2021-01 |
| retorno OOS a.a. (R$ 20 mil) | 0.1% vs CDI 11.4% |
| ativo OOS pp (R$ 20 mil / R$ 50 mil) | -11.31 / -7.40 |
| depois do IR (classe exterior) pp, 20k / 50k | -11.14 / -7.29 |
| IR OOS / Sharpe | -0.90 / -0.90 |
| pior queda | -23.0% |
| PBO / Sharpe deflacionado | 87% / +1% |
| leque de parâmetros p5 / mediana / p95 | -14.67 / -11.41 / -7.43 |
| custo 2x / execução t+2 | -15.85 / -9.88 |
| walk-forward | -14.26 |
| sem os 10 melhores negócios | -14.80 |
| placebo p | 0.56 |
| look-ahead (truncamento) | passou |

**10 melhores negócios**

| ativo               |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------------------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| hedge (resíduo) IWM |     -1 | 2022-01-03 00:00:00 | 2022-12-30 00:00:00 |    251 |      nan    |         5.93 |
| hedge (resíduo) IWM |     -1 | 2009-01-02 00:00:00 | 2009-12-31 00:00:00 |    252 |      nan    |         4.19 |
| hedge (resíduo) IWM |     -1 | 2014-01-02 00:00:00 | 2014-12-31 00:00:00 |    252 |      nan    |         3.43 |
| WATT                |      1 | 2018-12-21 00:00:00 | 2019-01-10 00:00:00 |     12 |       69.79 |         2.32 |
| TREE                |      1 | 2022-12-21 00:00:00 | 2023-01-11 00:00:00 |     13 |       49.74 |         2.09 |
| OSK                 |      1 | 2008-12-22 00:00:00 | 2009-01-12 00:00:00 |     13 |       41.86 |         1.95 |
| ENTA                |      1 | 2023-12-21 00:00:00 | 2024-01-10 00:00:00 |     12 |       34.31 |         1.91 |
| ESTA                |      1 | 2023-12-21 00:00:00 | 2024-01-10 00:00:00 |     12 |       31.23 |         1.74 |
| HIPO                |      1 | 2022-12-21 00:00:00 | 2023-01-11 00:00:00 |     13 |       42.48 |         1.73 |
| hedge (resíduo) IWM |     -1 | 2020-01-02 00:00:00 | 2020-12-31 00:00:00 |    253 |      nan    |         1.59 |

**10 piores negócios**

| ativo               |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------------------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| hedge (resíduo) IWM |     -1 | 2023-01-03 00:00:00 | 2023-12-29 00:00:00 |    250 |      nan    |        -6.96 |
| hedge (resíduo) IWM |     -1 | 2012-01-03 00:00:00 | 2012-12-31 00:00:00 |    250 |      nan    |        -5.7  |
| hedge (resíduo) IWM |     -1 | 2019-01-02 00:00:00 | 2019-12-31 00:00:00 |    252 |      nan    |        -4.53 |
| hedge (resíduo) IWM |     -1 | 2025-01-02 00:00:00 | 2025-12-31 00:00:00 |    250 |      nan    |        -3.25 |
| SINT                |      1 | 2022-12-21 00:00:00 | 2023-01-11 00:00:00 |     13 |      -36.54 |        -3.25 |
| MTH                 |      1 | 2007-12-21 00:00:00 | 2008-01-10 00:00:00 |     12 |      -49.72 |        -2.48 |
| WVE                 |      1 | 2019-12-23 00:00:00 | 2020-01-10 00:00:00 |     12 |      -45.9  |        -2.34 |
| VJET                |      1 | 2020-12-21 00:00:00 | 2021-01-12 00:00:00 |     14 |      -24.94 |        -1.8  |
| KPTI                |      1 | 2015-12-21 00:00:00 | 2016-01-12 00:00:00 |     14 |      -39.82 |        -1.72 |
| MTUS                |      1 | 2015-12-21 00:00:00 | 2016-01-12 00:00:00 |     14 |      -40.76 |        -1.71 |

**Quem trouxe o retorno (soma por ativo, pp)**

| ativo   |   sum |   count |
|:--------|------:|--------:|
| WATT    |  2.32 |       1 |
| BMA     |  2.13 |       2 |
| TREE    |  2.09 |       1 |
| OSK     |  1.95 |       1 |
| ENTA    |  1.91 |       1 |
| ESTA    |  1.74 |       1 |
| HIPO    |  1.73 |       1 |
| PRDO    |  1.57 |       1 |
| DNTH    |  1.44 |       1 |
| MLTX    |  1.44 |       1 |

### Dividendo isento na data-com (ações B3 com dividendo; FIIs como variante)  (`fg_dividendo_b3`)

**Tese:** Compro na data-com ações com dividendo (isento para PF) já aprovado, yield >= 1%, e vendo na abertura da data-ex; ganho = dividendo − queda do preço − custos.

**Instrumentos:** {'ações com dividendo': {'onde': 'B3', 'ticker': '~100 eventos/ano com yield >= 1%', 'lote': 'fracionário (1 ação)', 'custo': 'meio spread real + 0,03%'}, 'FIIs (variante)': {'onde': 'B3', 'ticker': '~100 FIIs líquidos', 'lote': '1 cota', 'custo': 'meio spread real + 0,03%'}}

**Aplicável:** True — Operável em qualquer corretora; dividendo de ação e rendimento de FII são isentos para PF; ordem no fechamento e na abertura.

| métrica | valor |
|---|---|
| OOS desde | 2021-01 |
| retorno OOS a.a. (R$ 20 mil) | 4.5% vs CDI 11.4% |
| ativo OOS pp (R$ 20 mil / R$ 50 mil) | -6.91 / -6.92 |
| depois do IR (classe acoes) pp, 20k / 50k | -6.81 / -6.82 |
| IR OOS / Sharpe | -2.26 / -2.26 |
| pior queda | -4.5% |
| PBO / Sharpe deflacionado | 29% / +0% |
| leque de parâmetros p5 / mediana / p95 | -8.57 / -6.25 / -4.03 |
| custo 2x / execução t+2 | -8.61 / -2.95 |
| walk-forward | -7.98 |
| sem os 10 melhores negócios | -7.42 |
| placebo p | 1.00 |
| look-ahead (truncamento) | passou |

**10 melhores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| ECOR3   |      1 | 2016-11-09 00:00:00 | 2016-11-10 00:00:00 |      1 |        0.43 |         0.73 |
| EGIE3   |      1 | 2018-08-20 00:00:00 | 2018-08-21 00:00:00 |      1 |       -1.5  |         0.71 |
| CSNA3   |      1 | 2021-07-30 00:00:00 | 2021-08-02 00:00:00 |      1 |       -0.13 |         0.6  |
| CSNA3   |      1 | 2019-05-02 00:00:00 | 2019-05-03 00:00:00 |      1 |       -2.23 |         0.55 |
| CMIG4   |      1 | 2014-11-07 00:00:00 | 2014-11-10 00:00:00 |      1 |       -3.99 |         0.43 |
| SANB11  |      1 | 2021-11-04 00:00:00 | 2021-11-05 00:00:00 |      1 |       -0.34 |         0.42 |
| VALE3   |      1 | 2024-03-11 00:00:00 | 2024-03-12 00:00:00 |      1 |       -2.5  |         0.39 |
| BEEF3   |      1 | 2020-11-06 00:00:00 | 2020-11-09 00:00:00 |      1 |       -0.77 |         0.37 |
| ITUB4   |      1 | 2019-08-15 00:00:00 | 2019-08-16 00:00:00 |      1 |       -0.57 |         0.36 |
| MRVE3   |      1 | 2014-05-15 00:00:00 | 2014-05-16 00:00:00 |      1 |       -2.41 |         0.33 |

**10 piores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| BRAP4   |      1 | 2023-11-21 00:00:00 | 2023-11-22 00:00:00 |      1 |       -7.38 |        -1.35 |
| PETR4   |      1 | 2022-05-23 00:00:00 | 2022-05-24 00:00:00 |      1 |      -13.81 |        -1.25 |
| PETR3   |      1 | 2022-05-23 00:00:00 | 2022-05-24 00:00:00 |      1 |      -12.95 |        -1.21 |
| USIM3   |      1 | 2021-08-31 00:00:00 | 2021-09-01 00:00:00 |      1 |       -7.43 |        -1.06 |
| PETR4   |      1 | 2022-11-21 00:00:00 | 2022-11-22 00:00:00 |      1 |      -14.12 |        -1.03 |
| USIM5   |      1 | 2021-08-31 00:00:00 | 2021-09-01 00:00:00 |      1 |       -7.41 |        -0.94 |
| VALE3   |      1 | 2025-12-11 00:00:00 | 2025-12-12 00:00:00 |      1 |       -5.9  |        -0.83 |
| CPLE11  |      1 | 2021-09-30 00:00:00 | 2021-10-01 00:00:00 |      1 |       -8.42 |        -0.75 |
| BRAP4   |      1 | 2025-12-17 00:00:00 | 2025-12-18 00:00:00 |      1 |       -6.64 |        -0.74 |
| PETR3   |      1 | 2022-11-21 00:00:00 | 2022-11-22 00:00:00 |      1 |      -11.76 |        -0.74 |

**Quem trouxe o retorno (soma por ativo, pp)**

| ativo   |   sum |   count |
|:--------|------:|--------:|
| MRVE3   |  1.14 |      11 |
| BEEF3   |  0.7  |       5 |
| ECOR3   |  0.66 |       7 |
| CIEL3   |  0.63 |       3 |
| ALPA4   |  0.34 |       3 |
| CMIG4   |  0.26 |       2 |
| VIVT4   |  0.25 |       2 |
| YDUQ3   |  0.25 |       1 |
| MGLU3   |  0.2  |       1 |
| PETZ3   |  0.1  |       1 |

### Arbitragem de ofertas em dinheiro (tender offers) de small caps nos EUA — PF IBKR, sobrevivência explícita  (`fg_merger_arb`)

**Tese:** Compro o alvo de oferta pública em dinheiro no dia seguinte ao SC 14D9 e seguro até a liquidação; R$ 1–2 mil por alvo; concluídos sem preço no Yahoo entram com spread hipotético (0% no fundo, 2–4% nas variantes).

**Instrumentos:** {'alvos de oferta': {'onde': 'IBKR', 'ticker': '~40–100 por ano (SC 14D9)', 'lote': 'fração', 'custo': 'US$ 0,0035/ação mín. 0,35 + 0,2%'}, 'WDO': {'onde': 'B3', 'ticker': 'WDO (vendido)', 'lote': 'US$ 10 mil', 'custo': 'R$ 3,70/lado'}}

**Aplicável:** False — Intestável com dado gratuito: o Yahoo não tem preço dos alvos comprados (~75% dos casos); o número do fundo é um PISO (concluído rende 0%) e as variantes com spread de 2–4% são hipóteses, não medidas. A operação em si é viável na IBKR (fração).

| métrica | valor |
|---|---|
| OOS desde | 2021-01 |
| retorno OOS a.a. (R$ 20 mil) | -0.0% vs CDI 11.4% |
| ativo OOS pp (R$ 20 mil / R$ 50 mil) | -11.46 / -11.46 |
| depois do IR (classe exterior) pp, 20k / 50k | -11.28 / -11.28 |
| IR OOS / Sharpe | -1.48 / -1.48 |
| pior queda | -13.8% |
| PBO / Sharpe deflacionado | 64% / +0% |
| leque de parâmetros p5 / mediana / p95 | -21.32 / -17.64 / -10.43 |
| custo 2x / execução t+2 | -16.50 / -11.50 |
| walk-forward | -20.44 |
| sem os 10 melhores negócios | -13.34 |
| placebo p | 0.86 |
| look-ahead (truncamento) | passou |

**10 melhores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| PQEFF   |      1 | 2021-11-10 00:00:00 | 2022-02-10 00:00:00 |     63 |      111.23 |         5.84 |
| TGS     |      1 | 2017-01-17 00:00:00 | 2017-04-18 00:00:00 |     63 |       65.43 |         3.2  |
| EDN     |      1 | 2021-08-02 00:00:00 | 2021-10-29 00:00:00 |     63 |       49.66 |         2.48 |
| JOB     |      1 | 2009-04-01 00:00:00 | 2009-07-01 00:00:00 |     63 |       36.59 |         1.82 |
| SIEB    |      1 | 2016-09-07 00:00:00 | 2016-12-06 00:00:00 |     63 |       34.21 |         1.58 |
| USNA    |      1 | 2008-05-21 00:00:00 | 2008-08-20 00:00:00 |     63 |       31.33 |         1.43 |
| FSK     |      1 | 2026-05-13 00:00:00 | 2026-08-13 00:00:00 |     63 |       22.69 |         1.14 |
| PSHG    |      1 | 2023-10-26 00:00:00 | 2024-01-29 00:00:00 |     63 |       22.56 |         1    |
| CASY    |      1 | 2010-06-09 00:00:00 | 2010-09-08 00:00:00 |     63 |       21.17 |         0.96 |
| HAPN    |      1 | 2017-07-24 00:00:00 | 2017-10-20 00:00:00 |     63 |       18.11 |         0.85 |

**10 piores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| LU      |      1 | 2024-09-30 00:00:00 | 2024-12-30 00:00:00 |     63 |      -31.23 |        -1.76 |
| F       |      1 | 2008-05-23 00:00:00 | 2008-08-22 00:00:00 |     63 |      -34.93 |        -1.66 |
| EMMS    |      1 | 2010-06-03 00:00:00 | 2010-09-01 00:00:00 |     63 |      -33.77 |        -1.66 |
| MANU    |      1 | 2024-01-18 00:00:00 | 2024-04-18 00:00:00 |     63 |      -26.34 |        -1.37 |
| BSBR    |      1 | 2014-10-03 00:00:00 | 2015-01-05 00:00:00 |     63 |      -25.2  |        -1.32 |
| BXC     |      1 | 2010-07-23 00:00:00 | 2010-10-21 00:00:00 |     63 |      -22.25 |        -1.18 |
| PRGO    |      1 | 2015-09-18 00:00:00 | 2015-12-17 00:00:00 |     63 |      -18.02 |        -0.93 |
| AGRO    |      1 | 2025-04-01 00:00:00 | 2025-07-02 00:00:00 |     63 |      -17.37 |        -0.9  |
| MAX     |      1 | 2023-06-12 00:00:00 | 2023-09-12 00:00:00 |     63 |      -17.4  |        -0.9  |
| TXMD    |      1 | 2022-06-14 00:00:00 | 2022-09-14 00:00:00 |     63 |      -13.72 |        -0.85 |

**Quem trouxe o retorno (soma por ativo, pp)**

| ativo   |   sum |   count |
|:--------|------:|--------:|
| PQEFF   |  5.84 |       1 |
| TGS     |  3.2  |       1 |
| EDN     |  2.48 |       1 |
| JOB     |  1.82 |       1 |
| SIEB    |  1.58 |       1 |
| USNA    |  1.43 |       1 |
| FSK     |  1.14 |       1 |
| PSHG    |  1    |       1 |
| CASY    |  0.96 |       1 |
| HAPN    |  0.85 |       1 |
