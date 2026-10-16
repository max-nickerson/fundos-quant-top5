# Frente pf3_mecanismos — resultados da bateria final (gerado automaticamente)

Gerado por `pf/gerar_cadernos.py` a partir de `pf/resultados/bateria/`. IR de pessoa física por `pf/ir.py` (mensal na B3 com isenção de ações ≤ R$ 20 mil/mês, anual no exterior). Ordem: nota do ranking.

### Follow-on pela tranche de varejo só com desconto >= Y (pedido com preço máximo)  (`mx_ofertas_desconto`)

**Tese:** Peço R$ 5 mil em todo follow-on com tranche de varejo, com preço máximo = fechamento da véspera da precificação x (1 − Y): só recebo quando o coordenador dá desconto grande; vendo no 1º pregão

**Instrumentos:** [{'onde': 'XP/BTG/Itaú/Clear/Rico/Inter (pedido de reserva na oferta)', 'ticker': 'IPO/follow-on ICVM 400 / Res. 160 público geral', 'lote': 'pedido mínimo ~R$ 1-3 mil', 'custo': 'compra sem custo na oferta; venda: emolumentos 0,03% + meio spread real'}]

**Aplicável:** True — pedido de reserva com limite de preço em qualquer corretora consorciada; poucos follow-ons com varejo por ano

| métrica | valor |
|---|---|
| OOS desde | 2021-01 |
| retorno OOS a.a. (R$ 20 mil) | 14.4% vs CDI 11.4% |
| ativo OOS pp (R$ 20 mil / R$ 50 mil) | +2.92 / +2.88 |
| depois do IR (classe acoes) pp, 20k / 50k | +2.87 / +2.84 |
| IR OOS / Sharpe | +0.71 / +0.71 |
| pior queda | 0.0% |
| PBO / Sharpe deflacionado | 0% / +95% |
| leque de parâmetros p5 / mediana / p95 | +2.23 / +2.90 / +3.03 |
| custo 2x / execução t+2 | +2.87 / +3.21 |
| walk-forward | +2.92 |
| sem os 10 melhores negócios | -0.01 |
| placebo p | 0.03 |
| look-ahead (truncamento) | passou |

**10 melhores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| SBSP3   |      1 | 2024-07-19 00:00:00 | 2024-07-19 00:00:00 |      1 |       26.62 |         6.6  |
| CSAN3   |      1 | 2025-11-04 00:00:00 | 2025-11-04 00:00:00 |      1 |       17.86 |         4.47 |
| CSMG3   |      1 | 2026-06-12 00:00:00 | 2026-06-12 00:00:00 |      1 |       16.73 |         4.14 |
| CXSE3   |      1 | 2025-03-20 00:00:00 | 2025-03-20 00:00:00 |      1 |        3.19 |         0.8  |
| ENEV3   |      1 | 2017-10-06 00:00:00 | 2017-10-06 00:00:00 |      1 |       13.1  |         0.49 |
| ENGI11  |      1 | 2016-07-27 00:00:00 | 2016-07-27 00:00:00 |      1 |       11.31 |         0.42 |
| BRDT3   |      1 | 2021-07-01 00:00:00 | 2021-07-01 00:00:00 |      1 |        9.87 |         0.36 |
| BRDT3   |      1 | 2019-07-24 00:00:00 | 2019-07-24 00:00:00 |      1 |        7.23 |         0.27 |
| VIVT3   |      1 | 2015-04-28 00:00:00 | 2015-04-28 00:00:00 |      1 |        6.6  |         0.24 |
| VIVT4   |      1 | 2015-04-28 00:00:00 | 2015-04-28 00:00:00 |      1 |        5.71 |         0.2  |

**10 piores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| LINX3   |      1 | 2019-06-26 00:00:00 | 2019-06-26 00:00:00 |      1 |       -2.42 |        -0.6  |
| SAPR4   |      1 | 2016-12-20 00:00:00 | 2016-12-20 00:00:00 |      1 |       -0.19 |        -0.01 |
| SUZB3   |      1 | 2020-10-02 00:00:00 | 2020-10-02 00:00:00 |      1 |        0.68 |         0.02 |
| PETR3   |      1 | 2019-06-26 00:00:00 | 2019-06-26 00:00:00 |      1 |        0.93 |         0.03 |
| CCPR3   |      1 | 2019-10-29 00:00:00 | 2019-10-29 00:00:00 |      1 |        1.63 |         0.06 |
| OIBR3   |      1 | 2014-04-29 00:00:00 | 2014-04-29 00:00:00 |      1 |        2.96 |         0.11 |
| TTEN3   |      1 | 2022-02-01 00:00:00 | 2022-02-01 00:00:00 |      1 |        3.67 |         0.14 |
| VULC3   |      1 | 2017-10-25 00:00:00 | 2017-10-25 00:00:00 |      1 |        3.81 |         0.14 |
| PETR3   |      1 | 2020-02-06 00:00:00 | 2020-02-06 00:00:00 |      1 |        4.29 |         0.16 |
| BBAS3   |      1 | 2019-10-18 00:00:00 | 2019-10-18 00:00:00 |      1 |        4.51 |         0.17 |

**Quem trouxe o retorno (soma por ativo, pp)**

| ativo   |   sum |   count |
|:--------|------:|--------:|
| SBSP3   |  6.6  |       1 |
| CSAN3   |  4.47 |       1 |
| CSMG3   |  4.14 |       1 |
| CXSE3   |  0.8  |       1 |
| BRDT3   |  0.63 |       2 |
| ENEV3   |  0.49 |       1 |
| ENGI11  |  0.42 |       1 |
| VIVT3   |  0.24 |       1 |
| VIVT4   |  0.2  |       1 |
| OIBR4   |  0.2  |       1 |

### Noite nos leilões só nas maiores quedas, dentro da isenção de R$ 20 mil/mês  (`mx_noite_isenta`)

**Tese:** Gasto o orçamento de vendas isento (R$ 20 mil/mês) só nas noites depois das maiores quedas forçadas: compro no leilão de fechamento, vendo no de abertura, sem IR

**Instrumentos:** [{'onde': 'Clear/Rico/XP/BTG (B3 à vista, ordens nos leilões de fechamento e abertura)', 'ticker': 'ações líquidas do Ibovespa', 'lote': '1 ação (fracionário também tem leilão) / 100', 'custo': 'emolumentos 0,03% por lado; sem spread (preço único do leilão)'}]

**Aplicável:** True — ordens a mercado nos leilões; só alguns pregões por mês (até 4–8 noites)

| métrica | valor |
|---|---|
| OOS desde | 2021-01 |
| retorno OOS a.a. (R$ 20 mil) | 13.7% vs CDI 11.4% |
| ativo OOS pp (R$ 20 mil / R$ 50 mil) | +2.21 / +0.78 |
| depois do IR (classe acoes) pp, 20k / 50k | +2.18 / +0.77 |
| IR OOS / Sharpe | +1.10 / +1.10 |
| pior queda | -0.9% |
| PBO / Sharpe deflacionado | 33% / +31% |
| leque de parâmetros p5 / mediana / p95 | +1.28 / +2.07 / +3.27 |
| custo 2x / execução t+2 | +1.12 / +1.81 |
| walk-forward | +3.32 |
| sem os 10 melhores negócios | +0.93 |
| placebo p | 0.00 |
| look-ahead (truncamento) | passou |

**10 melhores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| OIBR4   |      1 | 2014-07-15 00:00:00 | 2014-07-16 00:00:00 |      1 |       17.87 |         2.23 |
| GNDI3   |      1 | 2020-04-06 00:00:00 | 2020-04-07 00:00:00 |      1 |       15.65 |         1.95 |
| VVAR3   |      1 | 2020-03-09 00:00:00 | 2020-03-10 00:00:00 |      1 |       14.22 |         1.77 |
| AMER3   |      1 | 2023-02-03 00:00:00 | 2023-02-06 00:00:00 |      1 |       11.58 |         1.45 |
| BTOW3   |      1 | 2019-08-08 00:00:00 | 2019-08-09 00:00:00 |      1 |       10.85 |         1.34 |
| VVAR3   |      1 | 2020-04-03 00:00:00 | 2020-04-06 00:00:00 |      1 |        8.46 |         1.06 |
| CASH3   |      1 | 2021-09-09 00:00:00 | 2021-09-10 00:00:00 |      1 |        7.78 |         0.97 |
| VALE3   |      1 | 2016-02-03 00:00:00 | 2016-02-04 00:00:00 |      1 |        6.25 |         0.78 |
| PRIO3   |      1 | 2026-04-01 00:00:00 | 2026-04-02 00:00:00 |      1 |        6.36 |         0.77 |
| AMER3   |      1 | 2023-02-09 00:00:00 | 2023-02-10 00:00:00 |      1 |        5.98 |         0.75 |

**10 piores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| JBSS3   |      1 | 2017-05-17 00:00:00 | 2017-05-18 00:00:00 |      1 |      -14.82 |        -1.85 |
| MGLU3   |      1 | 2017-09-11 00:00:00 | 2017-09-12 00:00:00 |      1 |      -11.96 |        -1.45 |
| GOLL4   |      1 | 2020-03-06 00:00:00 | 2020-03-09 00:00:00 |      1 |       -7.44 |        -0.92 |
| FIBR3   |      1 | 2016-03-03 00:00:00 | 2016-03-04 00:00:00 |      1 |       -6.08 |        -0.76 |
| PRIO3   |      1 | 2020-03-10 00:00:00 | 2020-03-11 00:00:00 |      1 |       -6.07 |        -0.75 |
| AMER3   |      1 | 2023-02-08 00:00:00 | 2023-02-09 00:00:00 |      1 |       -4.75 |        -0.59 |
| SUZB3   |      1 | 2018-10-05 00:00:00 | 2018-10-08 00:00:00 |      1 |       -4.81 |        -0.59 |
| OIBR4   |      1 | 2014-06-30 00:00:00 | 2014-07-01 00:00:00 |      1 |       -4.7  |        -0.59 |
| CSAN3   |      1 | 2026-03-02 00:00:00 | 2026-03-03 00:00:00 |      1 |       -4.63 |        -0.58 |
| CVCB3   |      1 | 2023-08-08 00:00:00 | 2023-08-09 00:00:00 |      1 |       -4.59 |        -0.57 |

**Quem trouxe o retorno (soma por ativo, pp)**

| ativo   |   sum |   count |
|:--------|------:|--------:|
| VVAR3   |  3.99 |       7 |
| AZUL4   |  2.61 |      29 |
| AMER3   |  2.03 |       8 |
| GNDI3   |  1.95 |       1 |
| OIBR4   |  1.91 |      19 |
| IRBR3   |  1.9  |      22 |
| VALE3   |  1.85 |      29 |
| BEEF3   |  1.82 |      15 |
| OIBR3   |  1.79 |      14 |
| BTOW3   |  1.75 |      12 |

### OPA até o leilão só com desconto grande (magnitude)  (`mx_opa_desconto`)

**Tese:** Compro o alvo de OPA em dinheiro só quando o desconto contra o preço da oferta é >= smin (e <= 30%) na decisão e na execução, e entrego no leilão

**Instrumentos:** [{'onde': 'Clear/Rico/XP/BTG (à vista + habilitação no leilão de OPA pela corretora)', 'ticker': 'alvos de OPA em dinheiro', 'lote': '1 ação', 'custo': 'emolumentos 0,03% + meio spread real na compra; leilão sem spread'}]

**Aplicável:** True — pessoa física se habilita no leilão pela corretora (formulário + ações na custódia até a véspera); OPAs são poucas (5-10/ano)

| métrica | valor |
|---|---|
| OOS desde | 2021-01 |
| retorno OOS a.a. (R$ 20 mil) | 14.0% vs CDI 11.4% |
| ativo OOS pp (R$ 20 mil / R$ 50 mil) | +2.61 / +2.61 |
| depois do IR (classe acoes_isentas) pp, 20k / 50k | +2.56 / +2.57 |
| IR OOS / Sharpe | +0.38 / +0.38 |
| pior queda | -7.0% |
| PBO / Sharpe deflacionado | 7% / +36% |
| leque de parâmetros p5 / mediana / p95 | +0.32 / +1.17 / +2.94 |
| custo 2x / execução t+2 | +2.47 / +0.49 |
| walk-forward | +2.61 |
| sem os 10 melhores negócios | -2.68 |
| placebo p | 0.07 |
| look-ahead (truncamento) | passou |

**10 melhores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| CGAS5   |      1 | 2019-06-03 00:00:00 | 2020-08-10 00:00:00 |    300 |      131.33 |        19.7  |
| CMIG4   |      1 | 2015-12-21 00:00:00 | 2017-03-02 00:00:00 |    300 |       94.88 |        14.21 |
| AALR3   |      1 | 2021-08-17 00:00:00 | 2022-10-26 00:00:00 |    300 |       80.37 |        12.05 |
| ELPL3   |      1 | 2018-04-18 00:00:00 | 2018-06-04 00:00:00 |     31 |       61.78 |         9.22 |
| CPRE3   |      1 | 2017-02-17 00:00:00 | 2018-05-07 00:00:00 |    300 |       26.03 |         3.89 |
| MEAL3   |      1 | 2018-12-04 00:00:00 | 2020-02-11 00:00:00 |    300 |       24.61 |         3.69 |
| PRML3   |      1 | 2017-03-31 00:00:00 | 2018-03-09 00:00:00 |    233 |       23.1  |         3.46 |
| NGRD3   |      1 | 2025-12-23 00:00:00 | 2026-05-27 00:00:00 |    104 |       22.77 |         3.41 |
| BRAV3   |      1 | 2026-04-24 00:00:00 | 2026-08-05 00:00:00 |     71 |       20.93 |         3.12 |
| CRFB3   |      1 | 2025-02-13 00:00:00 | 2025-07-14 00:00:00 |    101 |       14.81 |         2.22 |

**10 piores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| KEPL3   |      1 | 2017-02-10 00:00:00 | 2018-04-27 00:00:00 |    300 |      -39.35 |        -5.9  |
| PRML3   |      1 | 2015-12-08 00:00:00 | 2017-02-15 00:00:00 |    300 |      -24.41 |        -3.66 |
| CMIG4   |      1 | 2019-03-22 00:00:00 | 2020-06-01 00:00:00 |    300 |      -16.81 |        -2.51 |
| FHER3   |      1 | 2022-12-26 00:00:00 | 2023-06-27 00:00:00 |    125 |      -14.75 |        -2.2  |
| BKBR3   |      1 | 2022-08-18 00:00:00 | 2022-12-08 00:00:00 |     76 |      -10.8  |        -1.62 |
| PRML3   |      1 | 2018-03-12 00:00:00 | 2018-06-13 00:00:00 |     64 |        0.54 |         0.08 |
| DASA3   |      1 | 2014-01-31 00:00:00 | 2014-02-10 00:00:00 |      6 |        0.88 |         0.13 |
| CIEL3   |      1 | 2024-07-11 00:00:00 | 2024-08-14 00:00:00 |     24 |        1.45 |         0.22 |
| HBOR3   |      1 | 2026-10-06 00:00:00 | 2026-10-13 00:00:00 |      4 |        3.37 |         0.5  |
| IDVL3   |      1 | 2020-08-14 00:00:00 | 2020-12-10 00:00:00 |     81 |        3.73 |         0.56 |

**Quem trouxe o retorno (soma por ativo, pp)**

| ativo   |   sum |   count |
|:--------|------:|--------:|
| CGAS5   | 19.7  |       1 |
| AALR3   | 12.05 |       1 |
| CMIG4   | 11.69 |       2 |
| ELPL3   |  9.22 |       1 |
| CPRE3   |  5.81 |       2 |
| MEAL3   |  3.69 |       1 |
| NGRD3   |  3.41 |       1 |
| BRAV3   |  3.12 |       1 |
| CRFB3   |  2.22 |       1 |
| PORT3   |  2.16 |       1 |

### Noite nos leilões após queda — só com âncora (ADR que não caiu / sem fato relevante)  (`mx_noite_adr`)

**Tese:** Compro no leilão de fechamento a ação que caiu forte só quando a âncora diverge — o ADR em NY caiu menos (venda local forçada) ou não houve fato relevante — e vendo no leilão de abertura

**Instrumentos:** [{'onde': 'Clear/Rico/XP/BTG (B3 à vista, ordens nos leilões de fechamento e abertura)', 'ticker': 'ações líquidas do Ibovespa', 'lote': '1 ação (fracionário também tem leilão) / 100', 'custo': 'emolumentos 0,03% por lado; sem spread (preço único do leilão)'}]

**Aplicável:** True — ordens a mercado no call de fechamento (16h55-17h) e de abertura (9h45-10h) em qualquer home broker; exige operar todo dia

| métrica | valor |
|---|---|
| OOS desde | 2021-01 |
| retorno OOS a.a. (R$ 20 mil) | 18.1% vs CDI 11.4% |
| ativo OOS pp (R$ 20 mil / R$ 50 mil) | +6.69 / +6.70 |
| depois do IR (classe acoes) pp, 20k / 50k | +5.35 / +5.37 |
| IR OOS / Sharpe | +0.46 / +0.46 |
| pior queda | -13.8% |
| PBO / Sharpe deflacionado | 1% / +0% |
| leque de parâmetros p5 / mediana / p95 | +5.03 / +6.12 / +9.33 |
| custo 2x / execução t+2 | -9.30 / +6.51 |
| walk-forward | +6.69 |
| sem os 10 melhores negócios | +1.73 |
| placebo p | 0.00 |
| look-ahead (truncamento) | passou |

**10 melhores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| PRIO3   |      1 | 2020-03-09 00:00:00 | 2020-03-10 00:00:00 |      1 |       23.53 |         5.87 |
| AZUL4   |      1 | 2020-03-12 00:00:00 | 2020-03-13 00:00:00 |      1 |       20.46 |         5.11 |
| AMBP3   |      1 | 2024-08-15 00:00:00 | 2024-08-16 00:00:00 |      1 |       18.61 |         4.63 |
| OIBR4   |      1 | 2014-07-15 00:00:00 | 2014-07-16 00:00:00 |      1 |       17.87 |         4.47 |
| BBAS3   |      1 | 2016-03-16 00:00:00 | 2016-03-17 00:00:00 |      1 |       17.17 |         4.29 |
| CSNA3   |      1 | 2020-03-12 00:00:00 | 2020-03-13 00:00:00 |      1 |       16.18 |         4.04 |
| OIBR3   |      1 | 2019-08-27 00:00:00 | 2019-08-28 00:00:00 |      1 |       15.71 |         3.93 |
| RRRP3   |      1 | 2023-03-16 00:00:00 | 2023-03-17 00:00:00 |      1 |       15.69 |         3.91 |
| GNDI3   |      1 | 2020-04-06 00:00:00 | 2020-04-07 00:00:00 |      1 |       15.65 |         3.89 |
| BRML3   |      1 | 2020-03-12 00:00:00 | 2020-03-13 00:00:00 |      1 |       14.96 |         3.74 |

**10 piores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| PRIO3   |      1 | 2020-03-13 00:00:00 | 2020-03-16 00:00:00 |      1 |      -25.2  |        -6.28 |
| IRBR3   |      1 | 2020-03-03 00:00:00 | 2020-03-04 00:00:00 |      1 |      -24.72 |        -6.16 |
| BEEF3   |      1 | 2025-04-29 00:00:00 | 2025-04-30 00:00:00 |      1 |      -22.36 |        -5.58 |
| GOLL4   |      1 | 2020-03-13 00:00:00 | 2020-03-16 00:00:00 |      1 |      -20.4  |        -5.09 |
| CVCB3   |      1 | 2020-03-13 00:00:00 | 2020-03-16 00:00:00 |      1 |      -20.15 |        -5.02 |
| HAPV3   |      1 | 2023-02-28 00:00:00 | 2023-03-01 00:00:00 |      1 |      -19.23 |        -4.81 |
| TCSA3   |      1 | 2020-03-18 00:00:00 | 2020-03-19 00:00:00 |      1 |      -18.54 |        -4.64 |
| HAPV3   |      1 | 2026-03-18 00:00:00 | 2026-03-19 00:00:00 |      1 |      -14.82 |        -3.7  |
| JBSS3   |      1 | 2017-05-17 00:00:00 | 2017-05-18 00:00:00 |      1 |      -14.82 |        -3.7  |
| PETR3   |      1 | 2014-10-24 00:00:00 | 2014-10-27 00:00:00 |      1 |      -14.67 |        -3.66 |

**Quem trouxe o retorno (soma por ativo, pp)**

| ativo   |   sum |   count |
|:--------|------:|--------:|
| MGLU3   | 19.28 |     232 |
| VVAR3   | 17.11 |      43 |
| VALE3   | 14.87 |     146 |
| AZUL4   | 13.25 |     152 |
| BTOW3   | 13.16 |      74 |
| CSNA3   | 11.56 |     242 |
| GGBR4   | 10.01 |     135 |
| USIM5   |  9.89 |     150 |
| OIBR3   |  9.85 |      71 |
| BRKM5   |  9.56 |     109 |

### Queda forte com provento declarado pendente (pânico + âncora de caixa)  (`mx_crise_dividendo`)

**Tese:** Compro a ação que caiu forte contra o mercado quando há um provento já aprovado (âncora de caixa) com data-com à frente; vendo na data-com ao investidor de renda

**Instrumentos:** [{'onde': 'Clear/Rico/XP (corretagem zero)', 'ticker': 'pagadoras de provento extraordinário (103 companhias)', 'lote': '1 ação', 'custo': 'emolumentos 0,03% + meio spread real do fechamento + 0,2% no fracionário'}]

**Aplicável:** True — pagadoras com ADV >= R$ 5 mi; poucos eventos por ano

| métrica | valor |
|---|---|
| OOS desde | 2021-01 |
| retorno OOS a.a. (R$ 20 mil) | 13.3% vs CDI 11.4% |
| ativo OOS pp (R$ 20 mil / R$ 50 mil) | +1.82 / +2.25 |
| depois do IR (classe acoes) pp, 20k / 50k | +1.79 / +2.09 |
| IR OOS / Sharpe | +0.23 / +0.23 |
| pior queda | -14.2% |
| PBO / Sharpe deflacionado | 30% / +54% |
| leque de parâmetros p5 / mediana / p95 | +0.61 / +2.39 / +4.41 |
| custo 2x / execução t+2 | -0.38 / +1.67 |
| walk-forward | +3.64 |
| sem os 10 melhores negócios | -3.92 |
| placebo p | 0.06 |
| look-ahead (truncamento) | passou |

**10 melhores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| JHSF3   |      1 | 2023-04-26 00:00:00 | 2023-06-19 00:00:00 |     36 |       34.07 |         6.81 |
| BRAP3   |      1 | 2021-11-09 00:00:00 | 2021-12-16 00:00:00 |     26 |       23.36 |         4.66 |
| BRAP4   |      1 | 2021-11-09 00:00:00 | 2021-12-16 00:00:00 |     26 |       21.24 |         4.23 |
| SLCE3   |      1 | 2020-04-14 00:00:00 | 2020-05-07 00:00:00 |     15 |       17.64 |         3.51 |
| PNVL3   |      1 | 2022-12-16 00:00:00 | 2022-12-26 00:00:00 |      6 |       15.41 |         3.08 |
| CIEL3   |      1 | 2016-02-12 00:00:00 | 2016-03-11 00:00:00 |     20 |       15.17 |         3.02 |
| PETR3   |      1 | 2021-11-04 00:00:00 | 2021-12-01 00:00:00 |     18 |       13.56 |         2.69 |
| MRVE3   |      1 | 2020-06-01 00:00:00 | 2020-10-13 00:00:00 |     93 |       12.73 |         2.54 |
| POMO4   |      1 | 2015-03-02 00:00:00 | 2015-06-22 00:00:00 |     76 |       12.64 |         2.53 |
| CAML3   |      1 | 2022-05-20 00:00:00 | 2022-05-24 00:00:00 |      2 |       12.28 |         2.45 |

**10 piores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| CIEL3   |      1 | 2019-04-25 00:00:00 | 2019-06-11 00:00:00 |     32 |      -17.08 |        -3.41 |
| VIVT3   |      1 | 2026-04-20 00:00:00 | 2026-05-22 00:00:00 |     22 |      -15.51 |        -3.09 |
| UGPA3   |      1 | 2020-02-20 00:00:00 | 2020-02-27 00:00:00 |      3 |      -13.75 |        -2.74 |
| INTB3   |      1 | 2025-02-27 00:00:00 | 2025-03-05 00:00:00 |      2 |      -11.12 |        -2.22 |
| PETR3   |      1 | 2025-03-06 00:00:00 | 2025-04-16 00:00:00 |     29 |      -10.7  |        -2.14 |
| ITUB4   |      1 | 2021-10-15 00:00:00 | 2021-11-19 00:00:00 |     23 |      -10.25 |        -2.04 |
| PETR4   |      1 | 2025-03-06 00:00:00 | 2025-04-16 00:00:00 |     29 |       -9.65 |        -1.92 |
| BBSE3   |      1 | 2021-06-25 00:00:00 | 2021-08-11 00:00:00 |     33 |       -9.53 |        -1.9  |
| CXSE3   |      1 | 2025-05-09 00:00:00 | 2025-08-01 00:00:00 |     59 |       -9.23 |        -1.84 |
| MPLU3   |      1 | 2017-03-01 00:00:00 | 2017-03-09 00:00:00 |      6 |       -8.76 |        -1.74 |

**Quem trouxe o retorno (soma por ativo, pp)**

| ativo   |   sum |   count |
|:--------|------:|--------:|
| JHSF3   |  6.42 |       2 |
| BRAP3   |  4.66 |       1 |
| BRAP4   |  4.23 |       1 |
| POMO4   |  4.09 |       4 |
| CAML3   |  3.91 |       4 |
| SLCE3   |  3.51 |       1 |
| GRND3   |  3.13 |       7 |
| PNVL3   |  3.08 |       1 |
| VALE3   |  2.54 |       6 |
| SEER3   |  2.44 |       1 |

### Mineradoras/siderúrgicas em pânico vs minério/aço em reais  (`mx_mineradoras_panico`)

**Tese:** Compro VALE3/BRAP4/CMIN3 (âncora minério SGX) e GGBR4/GOAU4/CSNA3/USIM5 (âncora SLX) no fracionário quando a ação cai muito mais que a commodity em reais justificaria; saio quando o resíduo volta a zero

**Instrumentos:** B3 (Clear/Rico, corretagem zero): VALE3, BRAP4, CMIN3, GGBR4, GOAU4, CSNA3, USIM5 no fracionário, até 35% do capital por nome e 100% no total; caixa em Tesouro Selic

**Aplicável:** True — ações líquidas no fracionário; âncora só como sinal (não há hedge de minério/aço que caiba em R$ 20–50 mil)

| métrica | valor |
|---|---|
| OOS desde | 2021-01 |
| retorno OOS a.a. (R$ 20 mil) | 12.7% vs CDI 11.4% |
| ativo OOS pp (R$ 20 mil / R$ 50 mil) | +1.30 / +1.31 |
| depois do IR (classe acoes) pp, 20k / 50k | +1.28 / +1.22 |
| IR OOS / Sharpe | +0.17 / +0.17 |
| pior queda | -15.9% |
| PBO / Sharpe deflacionado | 83% / +31% |
| leque de parâmetros p5 / mediana / p95 | -4.45 / -0.02 / +2.40 |
| custo 2x / execução t+2 | +1.06 / -0.23 |
| walk-forward | +0.50 |
| sem os 10 melhores negócios | -4.56 |
| placebo p | 0.18 |
| look-ahead (truncamento) | passou |

**10 melhores negócios**

| ativo   |   lado | entrada    | saida      |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:-----------|:-----------|-------:|------------:|-------------:|
| USIM5   |      1 | 2015-09-01 | 2015-09-10 |      7 |       36.77 |        13.14 |
| CSNA3   |      1 | 2020-03-25 | 2020-04-30 |     25 |       36.79 |         9.46 |
| GOAU4   |      1 | 2016-01-29 | 2016-02-05 |      6 |       35.92 |         9.19 |
| USIM5   |      1 | 2015-02-06 | 2015-03-04 |     17 |       25.42 |         8.56 |
| CSNA3   |      1 | 2015-08-14 | 2015-09-08 |     17 |       23.84 |         7.6  |
| CSNA3   |      1 | 2022-05-13 | 2022-05-24 |      8 |       16.96 |         5.98 |
| BRAP4   |      1 | 2021-12-21 | 2022-01-25 |     26 |       14.98 |         5.11 |
| CSNA3   |      1 | 2022-07-05 | 2022-08-12 |     29 |       13.85 |         5.05 |
| USIM5   |      1 | 2021-11-04 | 2021-11-30 |     18 |       10.49 |         3.4  |
| USIM5   |      1 | 2020-03-18 | 2020-05-20 |     43 |       10.73 |         3.19 |

**10 piores negócios**

| ativo   |   lado | entrada    | saida      |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:-----------|:-----------|-------:|------------:|-------------:|
| USIM5   |      1 | 2015-12-21 | 2016-02-23 |     43 |      -39.22 |       -15.54 |
| GOAU4   |      1 | 2015-07-03 | 2015-09-01 |     43 |      -43.8  |       -15.23 |
| CSNA3   |      1 | 2021-09-03 | 2021-11-05 |     43 |      -38.98 |       -14.17 |
| BRAP4   |      1 | 2015-12-10 | 2016-02-12 |     43 |      -29.94 |       -11.47 |
| CSNA3   |      1 | 2026-03-03 | 2026-04-15 |     31 |      -16.06 |        -5.62 |
| CSNA3   |      1 | 2024-04-15 | 2024-06-14 |     43 |      -11.82 |        -4.76 |
| GGBR4   |      1 | 2020-03-10 | 2020-04-22 |     30 |      -18.41 |        -4.56 |
| GOAU4   |      1 | 2020-03-10 | 2020-05-11 |     42 |      -16.94 |        -3.15 |
| USIM5   |      1 | 2018-05-29 | 2018-07-09 |     29 |       -6.07 |        -2.08 |
| USIM5   |      1 | 2026-07-03 | 2026-07-23 |     15 |       -3.19 |        -1.45 |

**Quem trouxe o retorno (soma por ativo, pp)**

| ativo   |   sum |   count |
|:--------|------:|--------:|
| USIM5   | 11.14 |       8 |
| CSNA3   |  9.79 |      10 |
| VALE3   |  5.39 |       2 |
| CMIN3   |  1.58 |       2 |
| GGBR4   |  1.21 |       5 |
| BRAP4   | -3.56 |       4 |
| GOAU4   | -4.14 |       7 |

### Rebalanceamento do Ibovespa só nos entrantes de giro baixo / pequenos (magnitude + tamanho)  (`mx_rebal_pequeno`)

**Tese:** Compro no fracionário só os prováveis entrantes do Ibovespa em que a demanda passiva vale mais dias de volume (giro baixo) ou os menores, e vendo aos fundos de índice no último pregão da carteira velha

**Instrumentos:** Clear/Rico/Inter (corretagem zero): entrantes prováveis no fracionário (XXXX3F, 1 ação mínima; lote de 100 no padrão), 1/15 do capital por papel; caixa em Tesouro Selic/LFTS11. Variantes de hedge: WIN (R$ 0,20 x pontos ≈ R$ 41 mil, margem em Tesouro Selic) ou BOVA11 vendido via aluguel (0,5% por contrato + 0,88% a.a. ao doador + B3 20% da taxa)

**Aplicável:** True — Aplicável: mid caps no fracionário com corretagem zero; posição média ~R$ 5 mil com R$ 20 mil; vendas por revisão < R$ 20 mil -> isento de IR. Sem hedge (WIN não cabe; BOVA11 alugado come o ativo)

| métrica | valor |
|---|---|
| OOS desde | 2021-01 |
| retorno OOS a.a. (R$ 20 mil) | 11.6% vs CDI 11.4% |
| ativo OOS pp (R$ 20 mil / R$ 50 mil) | +0.12 / +0.23 |
| depois do IR (classe acoes) pp, 20k / 50k | +0.12 / +0.22 |
| IR OOS / Sharpe | +0.09 / +0.09 |
| pior queda | -1.2% |
| PBO / Sharpe deflacionado | 38% / +10% |
| leque de parâmetros p5 / mediana / p95 | -0.42 / -0.19 / +0.29 |
| custo 2x / execução t+2 | -0.13 / -0.31 |
| walk-forward | +0.75 |
| sem os 10 melhores negócios | -0.99 |
| placebo p | 0.07 |
| look-ahead (truncamento) | passou |

**10 melhores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| GNDI3   |      1 | 2019-08-19 00:00:00 | 2019-08-30 00:00:00 |      9 |       18.71 |         1.18 |
| BIDI11  |      1 | 2021-04-16 00:00:00 | 2021-04-30 00:00:00 |      9 |       20.95 |         1.16 |
| SANB11  |      1 | 2017-04-13 00:00:00 | 2017-04-28 00:00:00 |      9 |       15.36 |         0.95 |
| BRAV3   |      1 | 2025-12-17 00:00:00 | 2025-12-30 00:00:00 |      8 |       15.34 |         0.94 |
| AZUL4   |      1 | 2018-12-17 00:00:00 | 2018-12-28 00:00:00 |      8 |       13.03 |         0.79 |
| MOTV3   |      1 | 2026-08-18 00:00:00 | 2026-08-31 00:00:00 |      9 |       12.93 |         0.78 |
| SMTO3   |      1 | 2023-08-18 00:00:00 | 2023-08-31 00:00:00 |      9 |       12.55 |         0.75 |
| BRDT3   |      1 | 2018-12-17 00:00:00 | 2018-12-28 00:00:00 |      8 |       12.13 |         0.75 |
| TRPL4   |      1 | 2023-12-15 00:00:00 | 2023-12-28 00:00:00 |      8 |       12.1  |         0.73 |
| SULA11  |      1 | 2019-12-17 00:00:00 | 2019-12-30 00:00:00 |      8 |       10.35 |         0.62 |

**10 piores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| TEND3   |      1 | 2026-04-16 00:00:00 | 2026-04-30 00:00:00 |      9 |      -13.86 |        -0.97 |
| CMIN3   |      1 | 2022-04-14 00:00:00 | 2022-04-29 00:00:00 |      9 |      -10.65 |        -0.77 |
| POMO4   |      1 | 2024-12-17 00:00:00 | 2024-12-30 00:00:00 |      8 |      -10.11 |        -0.72 |
| SOMA3   |      1 | 2022-04-14 00:00:00 | 2022-04-29 00:00:00 |      9 |       -9.51 |        -0.69 |
| SMTO3   |      1 | 2022-08-18 00:00:00 | 2022-08-31 00:00:00 |      9 |       -6.16 |        -0.48 |
| SMFT3   |      1 | 2024-08-19 00:00:00 | 2024-08-30 00:00:00 |      9 |       -5.73 |        -0.45 |
| ECOR3   |      1 | 2020-08-18 00:00:00 | 2020-08-31 00:00:00 |      9 |       -5.62 |        -0.42 |
| RAIZ4   |      1 | 2022-08-18 00:00:00 | 2022-08-31 00:00:00 |      9 |       -4.91 |        -0.39 |
| PRIO3   |      1 | 2020-08-18 00:00:00 | 2020-08-31 00:00:00 |      9 |       -4.9  |        -0.37 |
| EGIE3   |      1 | 2022-08-18 00:00:00 | 2022-08-31 00:00:00 |      9 |       -4.32 |        -0.35 |

**Quem trouxe o retorno (soma por ativo, pp)**

| ativo   |   sum |   count |
|:--------|------:|--------:|
| GNDI3   |  1.18 |       1 |
| BIDI11  |  1.16 |       1 |
| SANB11  |  1.03 |       2 |
| BRAV3   |  0.94 |       1 |
| AZUL4   |  0.79 |       1 |
| MOTV3   |  0.78 |       1 |
| BRDT3   |  0.75 |       1 |
| TRPL4   |  0.73 |       1 |
| SULA11  |  0.62 |       1 |
| SLCE3   |  0.58 |       1 |

### FII na data-com só nos de maior rendimento (calendário + magnitude)  (`mx_fii_datacom`)

**Tese:** O comprador da data-com do FII é o varejo de renda: compro os FIIs líquidos de MAIOR rendimento mensal k pregões antes do último pregão do mês e vendo para ele (data-com) ou recebo o rendimento isento (ex); regra escolhida no IS

**Instrumentos:** [{'onde': 'Clear/Rico/XP/Inter (corretagem zero)', 'ticker': 'FIIs líquidos (XXXX11), os n maiores ADV', 'lote': '1 cota', 'custo': 'emolumentos 0,03% + meio spread real do fechamento'}]

**Aplicável:** True — FIIs líquidos, 1 cota mínima; 12 ciclos por ano

| métrica | valor |
|---|---|
| OOS desde | 2021-01 |
| retorno OOS a.a. (R$ 20 mil) | 11.5% vs CDI 11.4% |
| ativo OOS pp (R$ 20 mil / R$ 50 mil) | +0.07 / -0.02 |
| depois do IR (classe fii) pp, 20k / 50k | -0.05 / -0.15 |
| IR OOS / Sharpe | +0.04 / +0.04 |
| pior queda | -4.5% |
| PBO / Sharpe deflacionado | 69% / +1% |
| leque de parâmetros p5 / mediana / p95 | -1.37 / -0.13 / +0.45 |
| custo 2x / execução t+2 | -3.48 / +1.03 |
| walk-forward | +1.72 |
| sem os 10 melhores negócios | -0.94 |
| placebo p | 0.01 |
| look-ahead (truncamento) | passou |

**10 melhores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| KNHY11  |      1 | 2020-03-25 00:00:00 | 2020-03-31 00:00:00 |      4 |       14.81 |         1.31 |
| CVBI11  |      1 | 2020-03-25 00:00:00 | 2020-03-31 00:00:00 |      4 |       12.23 |         1.07 |
| TRXF11  |      1 | 2026-08-25 00:00:00 | 2026-08-31 00:00:00 |      4 |       11.69 |         1.04 |
| BTCR11  |      1 | 2020-03-25 00:00:00 | 2020-03-31 00:00:00 |      4 |       10.48 |         0.91 |
| MXRF11  |      1 | 2020-03-25 00:00:00 | 2020-03-31 00:00:00 |      4 |        9.97 |         0.9  |
| UBSR11  |      1 | 2020-03-25 00:00:00 | 2020-03-31 00:00:00 |      4 |        9.95 |         0.87 |
| VRTA11  |      1 | 2019-08-26 00:00:00 | 2019-08-30 00:00:00 |      4 |        9.9  |         0.85 |
| XPCI11  |      1 | 2020-04-24 00:00:00 | 2020-04-30 00:00:00 |      4 |        8.56 |         0.76 |
| RBRR11  |      1 | 2020-03-25 00:00:00 | 2020-03-31 00:00:00 |      4 |        8.48 |         0.76 |
| HGRU11  |      1 | 2019-11-25 00:00:00 | 2019-11-29 00:00:00 |      4 |        8.78 |         0.74 |

**10 piores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| CACR11  |      1 | 2026-05-25 00:00:00 | 2026-05-29 00:00:00 |      4 |      -33.7  |        -3.02 |
| DEVA11  |      1 | 2023-03-27 00:00:00 | 2023-03-31 00:00:00 |      4 |      -17.67 |        -1.55 |
| CPLG11  |      1 | 2025-04-25 00:00:00 | 2025-04-30 00:00:00 |      3 |      -13.75 |        -1.23 |
| XPCM11  |      1 | 2020-11-24 00:00:00 | 2020-11-30 00:00:00 |      4 |      -13.56 |        -1.2  |
| HCTR11  |      1 | 2023-03-27 00:00:00 | 2023-03-31 00:00:00 |      4 |      -11.01 |        -0.98 |
| IRDM11  |      1 | 2019-10-25 00:00:00 | 2019-10-31 00:00:00 |      4 |       -9.47 |        -0.8  |
| DEVA11  |      1 | 2023-11-24 00:00:00 | 2023-11-30 00:00:00 |      4 |       -7.91 |        -0.7  |
| MXRF11  |      1 | 2022-01-25 00:00:00 | 2022-01-31 00:00:00 |      4 |       -7.1  |        -0.64 |
| HCTR11  |      1 | 2024-02-23 00:00:00 | 2024-02-29 00:00:00 |      4 |       -5.97 |        -0.53 |
| FIGS11  |      1 | 2020-01-27 00:00:00 | 2020-01-31 00:00:00 |      4 |       -5.92 |        -0.52 |

**Quem trouxe o retorno (soma por ativo, pp)**

| ativo   |   sum |   count |
|:--------|------:|--------:|
| BBPO11  |  3.04 |      44 |
| HABT11  |  3.03 |      57 |
| RECR11  |  2.83 |      23 |
| UBSR11  |  2.45 |      12 |
| TGAR11  |  1.97 |      34 |
| KNHY11  |  1.78 |      20 |
| CVBI11  |  1.59 |      39 |
| RBRF11  |  1.59 |      14 |
| VRTA11  |  1.29 |       6 |
| URPR11  |  1.23 |      49 |

### Vencimento de opções só nos objetos que caíram forte (calendário + magnitude)  (`mx_vencimento_queda`)

**Tese:** Compro no fechamento do vencimento só os objetos de opção que caíram >= queda nos pregões anteriores (a venda mecânica foi grande) e vendo k pregões depois

**Instrumentos:** [{'onde': 'Clear/Rico/XP (corretagem zero)', 'ticker': 'PETR4, PETR3, VALE3, ITUB4, BBDC4, BBAS3, ABEV3, ITSA4, MGLU3, GGBR4, CSNA3, USIM5', 'lote': '1 ação (fracionário)', 'custo': 'emolumentos 0,03% + meio spread real + 0,2% no fracionário'}]

**Aplicável:** True — blue chips no fracionário; poucas entradas por mês

| métrica | valor |
|---|---|
| OOS desde | 2021-01 |
| retorno OOS a.a. (R$ 20 mil) | 10.5% vs CDI 11.4% |
| ativo OOS pp (R$ 20 mil / R$ 50 mil) | -0.91 / -0.68 |
| depois do IR (classe acoes) pp, 20k / 50k | -0.89 / -0.72 |
| IR OOS / Sharpe | -0.19 / -0.19 |
| pior queda | -4.4% |
| PBO / Sharpe deflacionado | 62% / +3% |
| leque de parâmetros p5 / mediana / p95 | -1.36 / -0.57 / +0.60 |
| custo 2x / execução t+2 | -2.30 / -1.17 |
| walk-forward | -0.65 |
| sem os 10 melhores negócios | -3.43 |
| placebo p | 0.28 |
| look-ahead (truncamento) | passou |

**10 melhores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| MGLU3   |      1 | 2015-07-20 00:00:00 | 2015-07-21 00:00:00 |      1 |       12.77 |         3.19 |
| MGLU3   |      1 | 2022-12-16 00:00:00 | 2022-12-19 00:00:00 |      1 |        9.64 |         2.41 |
| GGBR4   |      1 | 2020-06-15 00:00:00 | 2020-06-16 00:00:00 |      1 |        8.9  |         2.22 |
| USIM5   |      1 | 2026-08-21 00:00:00 | 2026-08-24 00:00:00 |      1 |        8.45 |         2.11 |
| MGLU3   |      1 | 2022-06-17 00:00:00 | 2022-06-20 00:00:00 |      1 |        7.92 |         1.98 |
| BBDC4   |      1 | 2020-03-16 00:00:00 | 2020-03-17 00:00:00 |      1 |        7.77 |         1.94 |
| CSNA3   |      1 | 2020-03-16 00:00:00 | 2020-03-17 00:00:00 |      1 |        7.31 |         1.83 |
| VALE3   |      1 | 2016-11-21 00:00:00 | 2016-11-22 00:00:00 |      1 |        7.13 |         1.78 |
| MGLU3   |      1 | 2022-11-18 00:00:00 | 2022-11-21 00:00:00 |      1 |        6.9  |         1.72 |
| BBAS3   |      1 | 2018-06-18 00:00:00 | 2018-06-19 00:00:00 |      1 |        6.86 |         1.71 |

**10 piores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| MGLU3   |      1 | 2017-10-16 00:00:00 | 2017-10-17 00:00:00 |      1 |       -8.48 |        -2.12 |
| USIM5   |      1 | 2014-02-17 00:00:00 | 2014-02-18 00:00:00 |      1 |       -8.21 |        -2.05 |
| CSNA3   |      1 | 2021-01-18 00:00:00 | 2021-01-19 00:00:00 |      1 |       -5.91 |        -1.47 |
| MGLU3   |      1 | 2015-09-21 00:00:00 | 2015-09-22 00:00:00 |      1 |       -5.31 |        -1.33 |
| CSNA3   |      1 | 2024-12-20 00:00:00 | 2024-12-23 00:00:00 |      1 |       -5.14 |        -1.28 |
| BBAS3   |      1 | 2016-05-16 00:00:00 | 2016-05-17 00:00:00 |      1 |       -5.06 |        -1.26 |
| MGLU3   |      1 | 2021-11-19 00:00:00 | 2021-11-22 00:00:00 |      1 |       -4.83 |        -1.21 |
| MGLU3   |      1 | 2024-12-20 00:00:00 | 2024-12-23 00:00:00 |      1 |       -4.76 |        -1.19 |
| CSNA3   |      1 | 2015-08-17 00:00:00 | 2015-08-18 00:00:00 |      1 |       -4.69 |        -1.17 |
| PETR4   |      1 | 2017-03-20 00:00:00 | 2017-03-21 00:00:00 |      1 |       -4.62 |        -1.15 |

**Quem trouxe o retorno (soma por ativo, pp)**

| ativo   |   sum |   count |
|:--------|------:|--------:|
| BBDC4   |  3.69 |       8 |
| MGLU3   |  3.05 |      35 |
| BBAS3   |  1.98 |      18 |
| ITUB4   |  1.71 |       5 |
| GGBR4   |  1.69 |      22 |
| PETR3   |  1.5  |      20 |
| PETR4   |  1.49 |      19 |
| ABEV3   |  1.48 |       2 |
| ITSA4   |  1.32 |       4 |
| USIM5   |  1.19 |      38 |

### JCP/dividendo de dezembro (calendário fiscal) até a data-com  (`mx_jcp_dezembro`)

**Tese:** Em dezembro a empresa é obrigada pelo calendário fiscal a declarar o JCP; compro após o aviso e vendo na data-com ao investidor de renda, mesmo com provento pequeno (0,5–3% do preço)

**Instrumentos:** [{'onde': 'Clear/Rico/XP (corretagem zero)', 'ticker': 'pagadoras de provento extraordinário (103 companhias)', 'lote': '1 ação', 'custo': 'emolumentos 0,03% + meio spread real do fechamento + 0,2% no fracionário'}]

**Aplicável:** True — pagadoras com ADV >= R$ 5 mi; ~R$ 4 mil por evento com R$ 20 mil; concentra em dezembro

| métrica | valor |
|---|---|
| OOS desde | 2021-01 |
| retorno OOS a.a. (R$ 20 mil) | 8.8% vs CDI 11.4% |
| ativo OOS pp (R$ 20 mil / R$ 50 mil) | -2.64 / -2.24 |
| depois do IR (classe acoes) pp, 20k / 50k | -2.69 / -2.34 |
| IR OOS / Sharpe | -0.51 / -0.51 |
| pior queda | -9.1% |
| PBO / Sharpe deflacionado | 18% / +0% |
| leque de parâmetros p5 / mediana / p95 | -2.20 / -0.21 / +0.70 |
| custo 2x / execução t+2 | -4.33 / -2.62 |
| walk-forward | -2.64 |
| sem os 10 melhores negócios | -4.59 |
| placebo p | 0.72 |
| look-ahead (truncamento) | passou |

**10 melhores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| EMBR3   |      1 | 2017-12-15 00:00:00 | 2017-12-22 00:00:00 |      5 |       22.16 |         4.43 |
| JSLG3   |      1 | 2019-12-23 00:00:00 | 2020-01-03 00:00:00 |      7 |       13.67 |         2.73 |
| CIEL3   |      1 | 2022-12-16 00:00:00 | 2022-12-23 00:00:00 |      5 |       12.7  |         2.36 |
| HGTX3   |      1 | 2018-12-26 00:00:00 | 2019-01-03 00:00:00 |      5 |       10.14 |         2.02 |
| ASAI3   |      1 | 2026-01-02 00:00:00 | 2026-01-06 00:00:00 |      2 |        8.14 |         1.63 |
| GOAU4   |      1 | 2020-12-09 00:00:00 | 2020-12-21 00:00:00 |      8 |        7.64 |         1.53 |
| VALE3   |      1 | 2017-12-15 00:00:00 | 2017-12-21 00:00:00 |      4 |        7.54 |         1.5  |
| ISAE4   |      1 | 2025-12-22 00:00:00 | 2026-02-26 00:00:00 |     44 |        7.45 |         1.49 |
| GGBR4   |      1 | 2020-12-09 00:00:00 | 2020-12-21 00:00:00 |      8 |        7.34 |         1.46 |
| CIEL3   |      1 | 2020-12-23 00:00:00 | 2020-12-29 00:00:00 |      3 |        8.15 |         1.46 |

**10 piores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| RENT3   |      1 | 2025-12-15 00:00:00 | 2025-12-17 00:00:00 |      2 |       -9.21 |        -1.83 |
| DXCO3   |      1 | 2024-12-12 00:00:00 | 2024-12-18 00:00:00 |      4 |       -8.04 |        -1.61 |
| AZZA3   |      1 | 2024-12-03 00:00:00 | 2024-12-06 00:00:00 |      3 |       -7.87 |        -1.56 |
| TUPY3   |      1 | 2023-12-27 00:00:00 | 2024-01-22 00:00:00 |     17 |       -7.79 |        -1.55 |
| MODL3   |      1 | 2022-12-13 00:00:00 | 2022-12-15 00:00:00 |      2 |       -6.88 |        -1.38 |
| SIMH3   |      1 | 2022-12-26 00:00:00 | 2022-12-27 00:00:00 |      1 |       -6.78 |        -1.35 |
| CRFB3   |      1 | 2024-12-19 00:00:00 | 2024-12-23 00:00:00 |      2 |       -6.68 |        -1.33 |
| FLRY3   |      1 | 2024-12-11 00:00:00 | 2024-12-13 00:00:00 |      2 |       -4.99 |        -1    |
| SMFT3   |      1 | 2024-12-11 00:00:00 | 2024-12-13 00:00:00 |      2 |       -4.97 |        -0.99 |
| FLRY3   |      1 | 2021-01-04 00:00:00 | 2021-01-06 00:00:00 |      2 |       -4.26 |        -0.85 |

**Quem trouxe o retorno (soma por ativo, pp)**

| ativo   |   sum |   count |
|:--------|------:|--------:|
| CIEL3   |  4.54 |       4 |
| EMBR3   |  4.43 |       1 |
| MOVI3   |  3.33 |       6 |
| JSLG3   |  2.51 |       2 |
| NEOE3   |  2.32 |       4 |
| HGTX3   |  2.27 |       2 |
| ASAI3   |  1.63 |       1 |
| GOAU4   |  1.53 |       1 |
| VALE3   |  1.5  |       1 |
| ISAE4   |  1.49 |       1 |

### Pânico de FII com âncora no valor patrimonial (VP não caiu)  (`mx_fii_panico_vp`)

**Tese:** Compro o FII que caiu forte em 5 pregões só quando a carteira (VP do informe CVM) não caiu e a cota está abaixo do VP: venda de pânico do varejo contra uma âncora que divergiu

**Instrumentos:** [{'onde': 'Clear/Rico/XP/Inter (corretagem zero)', 'ticker': 'FII com queda forte (XXXX11)', 'lote': '1 cota', 'custo': 'emolumentos 0,03% + meio spread real do fechamento'}]

**Aplicável:** True — FIIs com ADV >= R$ 500 mil; R$ 2 mil por FII com R$ 20 mil

| métrica | valor |
|---|---|
| OOS desde | 2021-01 |
| retorno OOS a.a. (R$ 20 mil) | 9.9% vs CDI 11.4% |
| ativo OOS pp (R$ 20 mil / R$ 50 mil) | -1.50 / -1.62 |
| depois do IR (classe fii) pp, 20k / 50k | -1.48 / -1.59 |
| IR OOS / Sharpe | -0.36 / -0.36 |
| pior queda | -6.8% |
| PBO / Sharpe deflacionado | 19% / +0% |
| leque de parâmetros p5 / mediana / p95 | -2.82 / -1.21 / -0.27 |
| custo 2x / execução t+2 | -2.17 / -1.41 |
| walk-forward | -1.50 |
| sem os 10 melhores negócios | -3.00 |
| placebo p | 0.86 |
| look-ahead (truncamento) | passou |

**10 melhores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| FEXC11  |      1 | 2020-03-25 00:00:00 | 2020-04-27 00:00:00 |     21 |       31.81 |         3.06 |
| DEVA11  |      1 | 2023-04-13 00:00:00 | 2023-05-16 00:00:00 |     21 |       30.02 |         2.98 |
| HGFF11  |      1 | 2020-03-20 00:00:00 | 2020-04-22 00:00:00 |     21 |       25.15 |         2.51 |
| BCIA11  |      1 | 2020-03-20 00:00:00 | 2020-04-22 00:00:00 |     21 |       26.44 |         2.46 |
| BCFF11  |      1 | 2020-03-24 00:00:00 | 2020-04-24 00:00:00 |     21 |       24.33 |         2.37 |
| MGFF11  |      1 | 2019-12-03 00:00:00 | 2020-01-03 00:00:00 |     21 |       21.01 |         2.09 |
| HCTR11  |      1 | 2023-04-13 00:00:00 | 2023-05-16 00:00:00 |     21 |       20.85 |         2.08 |
| RBRF11  |      1 | 2020-03-24 00:00:00 | 2020-04-24 00:00:00 |     21 |       20.24 |         2.01 |
| CVBI11  |      1 | 2020-03-25 00:00:00 | 2020-04-27 00:00:00 |     21 |       15.99 |         1.57 |
| HCTR11  |      1 | 2020-03-26 00:00:00 | 2020-04-28 00:00:00 |     21 |       14.39 |         1.39 |

**10 piores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| HCTR11  |      1 | 2023-08-15 00:00:00 | 2023-10-16 00:00:00 |     42 |      -31.42 |        -3.09 |
| HCTR11  |      1 | 2023-03-10 00:00:00 | 2023-04-11 00:00:00 |     21 |      -25.55 |        -2.5  |
| DEVA11  |      1 | 2023-03-09 00:00:00 | 2023-04-10 00:00:00 |     21 |      -21.73 |        -2.12 |
| JCCJ11  |      1 | 2024-05-28 00:00:00 | 2024-07-05 00:00:00 |     27 |      -16.49 |        -1.59 |
| KFOF11  |      1 | 2020-03-13 00:00:00 | 2020-04-14 00:00:00 |     21 |      -14.4  |        -1.38 |
| KISU11  |      1 | 2021-07-16 00:00:00 | 2021-08-16 00:00:00 |     21 |      -13.94 |        -1.36 |
| HCTR11  |      1 | 2025-02-12 00:00:00 | 2025-03-17 00:00:00 |     21 |       -7.39 |        -0.74 |
| KORE11  |      1 | 2024-11-07 00:00:00 | 2024-12-10 00:00:00 |     21 |       -6.76 |        -0.66 |
| VRTA11  |      1 | 2019-08-12 00:00:00 | 2019-09-10 00:00:00 |     21 |       -5.98 |        -0.59 |
| HCTR11  |      1 | 2024-02-19 00:00:00 | 2024-03-19 00:00:00 |     21 |       -4.57 |        -0.45 |

**Quem trouxe o retorno (soma por ativo, pp)**

| ativo   |   sum |   count |
|:--------|------:|--------:|
| BCIA11  |  3.41 |       3 |
| FEXC11  |  3.06 |       1 |
| HGFF11  |  2.51 |       1 |
| BCFF11  |  2.36 |       2 |
| MGFF11  |  2.09 |       1 |
| RBRF11  |  2.01 |       1 |
| DEVA11  |  1.96 |       5 |
| IRDM11  |  1.8  |       2 |
| CVBI11  |  1.57 |       1 |
| HABT11  |  0.87 |       1 |

### Follow-on vendido só nas ofertas grandes para o giro do papel (magnitude)  (`mx_followon_tamanho`)

**Tese:** Vendo a descoberto (BTC de PF) a ação que faz oferta subsequente só quando a oferta vale >= W dias de volume (overhang grande), com BOVA11 comprado contra

**Instrumentos:** Clear/Rico/XP/BTG: venda a descoberto via aluguel tomador (BTC), ações inteiras, 1/5 do capital por nome; garantia e produto da venda em Tesouro Selic; hedge BOVA11 comprado (cotas inteiras). Aluguel: 0,5% do volume por contrato + taxa ao doador (B3/estimada) + B3 20% da taxa

**Aplicável:** True — Aplicável operacionalmente (PF aluga e vende a descoberto na B3), mas o edge depende da taxa de aluguel dos emissores; os papéis mais lucrativos (oferta de empresa alavancada) são os de aluguel caro/indisponível

| métrica | valor |
|---|---|
| OOS desde | 2021-01 |
| retorno OOS a.a. (R$ 20 mil) | 7.8% vs CDI 11.4% |
| ativo OOS pp (R$ 20 mil / R$ 50 mil) | -3.61 / -3.48 |
| depois do IR (classe acoes) pp, 20k / 50k | -3.55 / -3.43 |
| IR OOS / Sharpe | -0.40 / -0.40 |
| pior queda | -14.3% |
| PBO / Sharpe deflacionado | 41% / +0% |
| leque de parâmetros p5 / mediana / p95 | -3.90 / -2.60 / -1.65 |
| custo 2x / execução t+2 | -8.71 / -2.83 |
| walk-forward | -2.82 |
| sem os 10 melhores negócios | -11.01 |
| placebo p | 0.25 |
| look-ahead (truncamento) | passou |

**10 melhores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| IRBR3   |     -1 | 2022-08-25 00:00:00 | 2022-09-23 00:00:00 |     20 |      -45.63 |         9.01 |
| PETR3   |     -1 | 2020-02-07 00:00:00 | 2020-03-10 00:00:00 |     20 |      -41.64 |         8.17 |
| POSI3   |     -1 | 2020-01-22 00:00:00 | 2020-02-19 00:00:00 |     20 |      -35.02 |         6.63 |
| TCSA3   |     -1 | 2019-07-08 00:00:00 | 2019-08-05 00:00:00 |     20 |      -30.9  |         5.66 |
| HEDGE   |      0 | 2020-07-01 00:00:00 | 2020-07-31 00:00:00 |     21 |      nan    |         4.94 |
| GOAU4   |     -1 | 2015-10-30 00:00:00 | 2015-11-30 00:00:00 |     20 |      -23.85 |         4.59 |
| FRAS3   |     -1 | 2022-03-31 00:00:00 | 2022-05-02 00:00:00 |     20 |      -22.66 |         4.25 |
| HEDGE   |      0 | 2019-12-01 00:00:00 | 2019-12-31 00:00:00 |     21 |      nan    |         4.21 |
| MEAL3   |     -1 | 2020-07-13 00:00:00 | 2020-08-10 00:00:00 |     20 |      -22.59 |         4.19 |
| PCAR3   |     -1 | 2024-03-14 00:00:00 | 2024-04-12 00:00:00 |     20 |      -22.26 |         4.17 |

**10 piores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| DASA3   |     -1 | 2023-04-19 00:00:00 | 2023-05-19 00:00:00 |     20 |       57.25 |       -12.13 |
| LCAM3   |     -1 | 2019-12-10 00:00:00 | 2020-01-09 00:00:00 |     20 |       29.57 |        -6.09 |
| MDNE3   |     -1 | 2026-01-23 00:00:00 | 2026-02-24 00:00:00 |     20 |       28.95 |        -5.83 |
| SAPR4   |     -1 | 2016-12-21 00:00:00 | 2017-01-18 00:00:00 |     20 |       27.22 |        -5.72 |
| PRIO3   |     -1 | 2021-01-20 00:00:00 | 2021-02-19 00:00:00 |     20 |       25.53 |        -5.52 |
| AMAR3   |     -1 | 2019-11-26 00:00:00 | 2019-12-26 00:00:00 |     21 |       23.99 |        -5.14 |
| CASH3   |     -1 | 2021-07-08 00:00:00 | 2021-08-05 00:00:00 |     20 |       21.37 |        -4.68 |
| RAIL3   |     -1 | 2017-09-22 00:00:00 | 2017-10-23 00:00:00 |     20 |       22.69 |        -4.65 |
| GNDI3   |     -1 | 2019-12-02 00:00:00 | 2020-01-02 00:00:00 |     21 |       21.07 |        -4.41 |
| JHSF3   |     -1 | 2019-11-05 00:00:00 | 2019-12-04 00:00:00 |     20 |       19.84 |        -4.34 |

**Quem trouxe o retorno (soma por ativo, pp)**

| ativo   |   sum |   count |
|:--------|------:|--------:|
| IRBR3   |  8.68 |       3 |
| PETR3   |  8.33 |       2 |
| MEAL3   |  7.48 |       2 |
| CVCB3   |  6.99 |       3 |
| POSI3   |  6.63 |       1 |
| FRAS3   |  6.12 |       2 |
| TCSA3   |  5.66 |       1 |
| BPAN4   |  4.7  |       2 |
| GOAU4   |  4.59 |       1 |
| PCAR3   |  4.17 |       1 |
