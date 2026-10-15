# Frente b3_acoes — resultados da bateria final (gerado automaticamente)

Gerado por `pf/gerar_cadernos.py` a partir de `pf/resultados/bateria/`. IR de pessoa física por `pf/ir.py` (mensal na B3 com isenção de ações ≤ R$ 20 mil/mês, anual no exterior). Ordem: nota do ranking.

### OPA até o leilão em lote pequeno (PF)  (`b3_opa_leilao`)

**Tese:** Compro o alvo de OPA em dinheiro depois do fato relevante e entrego no leilão: o preço do FR é piso (Selic, melhora para o quórum, concorrente); R$ 2-6 mil cabem até em alvos que giram R$ 20 mil/dia

**Instrumentos:** [{'onde': 'Clear/Rico/XP/BTG (à vista + habilitação no leilão de OPA pela corretora)', 'ticker': 'alvos de OPA em dinheiro', 'lote': '1 ação', 'custo': 'emolumentos 0,03% + meio spread real na compra; leilão sem spread'}]

**Aplicável:** True — pessoa física se habilita no leilão pela corretora (formulário + ações na custódia até a véspera); OPAs são poucas (5-10/ano)

| métrica | valor |
|---|---|
| OOS desde | 2021-01 |
| retorno OOS a.a. (R$ 20 mil) | 15.5% vs CDI 11.4% |
| ativo OOS pp (R$ 20 mil / R$ 50 mil) | +4.10 / +4.11 |
| depois do IR (classe acoes_isentas) pp, 20k / 50k | +4.03 / +4.04 |
| IR OOS / Sharpe | +0.54 / +0.54 |
| pior queda | -7.0% |
| PBO / Sharpe deflacionado | 36% / +85% |
| leque de parâmetros p5 / mediana / p95 | +1.18 / +1.95 / +4.55 |
| custo 2x / execução t+2 | +3.97 / +3.42 |
| walk-forward | +4.10 |
| sem os 10 melhores negócios | -2.25 |
| placebo p | 0.04 |
| look-ahead (truncamento) | passou |

**10 melhores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| CGAS5   |      1 | 2019-06-03 00:00:00 | 2020-08-10 00:00:00 |    300 |      131.33 |        19.7  |
| CMIG4   |      1 | 2015-12-21 00:00:00 | 2017-03-02 00:00:00 |    300 |       94.88 |        14.21 |
| AALR3   |      1 | 2021-08-17 00:00:00 | 2022-10-26 00:00:00 |    300 |       80.37 |        12.05 |
| ELPL3   |      1 | 2018-04-18 00:00:00 | 2018-06-04 00:00:00 |     31 |       61.78 |         9.22 |
| HBOR3   |      1 | 2026-07-06 00:00:00 | 2026-10-13 00:00:00 |     69 |       48.26 |         7.24 |
| ALPA4   |      1 | 2015-11-24 00:00:00 | 2017-02-01 00:00:00 |    300 |       30.64 |         4.59 |
| CPRE3   |      1 | 2017-02-17 00:00:00 | 2018-05-07 00:00:00 |    300 |       26.03 |         3.89 |
| MEAL3   |      1 | 2018-12-04 00:00:00 | 2020-02-11 00:00:00 |    300 |       24.61 |         3.69 |
| PRML3   |      1 | 2017-03-31 00:00:00 | 2018-03-09 00:00:00 |    233 |       23.1  |         3.46 |
| NGRD3   |      1 | 2025-12-23 00:00:00 | 2026-05-27 00:00:00 |    104 |       22.77 |         3.41 |

**10 piores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| KEPL3   |      1 | 2017-02-10 00:00:00 | 2018-04-27 00:00:00 |    300 |      -39.35 |        -5.9  |
| PRML3   |      1 | 2015-12-08 00:00:00 | 2017-02-15 00:00:00 |    300 |      -24.41 |        -3.66 |
| CMIG4   |      1 | 2019-03-22 00:00:00 | 2020-06-01 00:00:00 |    300 |      -16.81 |        -2.51 |
| ALPA4   |      1 | 2017-07-13 00:00:00 | 2018-09-24 00:00:00 |    300 |      -15.63 |        -2.34 |
| FHER3   |      1 | 2022-12-26 00:00:00 | 2023-06-27 00:00:00 |    125 |      -14.75 |        -2.2  |
| BKBR3   |      1 | 2022-08-02 00:00:00 | 2022-12-08 00:00:00 |     88 |       -0.49 |        -0.07 |
| PRML3   |      1 | 2018-03-12 00:00:00 | 2018-06-13 00:00:00 |     64 |        0.54 |         0.08 |
| DASA3   |      1 | 2014-01-31 00:00:00 | 2014-02-10 00:00:00 |      6 |        0.88 |         0.13 |
| CIEL3   |      1 | 2024-07-11 00:00:00 | 2024-08-14 00:00:00 |     24 |        1.45 |         0.22 |
| IDVL3   |      1 | 2020-08-14 00:00:00 | 2020-12-10 00:00:00 |     81 |        3.73 |         0.56 |

**Quem trouxe o retorno (soma por ativo, pp)**

| ativo   |   sum |   count |
|:--------|------:|--------:|
| CGAS5   | 19.7  |       1 |
| AALR3   | 12.05 |       1 |
| CMIG4   | 11.69 |       2 |
| ELPL3   |  9.22 |       1 |
| HBOR3   |  7.24 |       1 |
| CPRE3   |  5.81 |       2 |
| MEAL3   |  3.69 |       1 |
| NGRD3   |  3.41 |       1 |
| BRAV3   |  3.12 |       1 |
| ALPA4   |  2.25 |       2 |

### Noite nos leilões após queda forte (PF) — AUDITADA (8 bps ida e volta)  (`b3_leilao_noite_aud`)

**Tese:** Compro no leilão de fechamento as ações líquidas que caíram >= 2-4% abaixo do mercado no dia anterior e vendo no leilão de abertura: o prêmio da B3 está na noite (o pregão devolve), e é maior depois de vendas forçadas; no leilão o pequeno não paga spread

**Instrumentos:** [{'onde': 'Clear/Rico/XP/BTG (B3 à vista, ordens nos leilões de fechamento e abertura)', 'ticker': 'ações líquidas do Ibovespa', 'lote': '1 ação (fracionário também tem leilão) / 100', 'custo': 'emolumentos 0,03% por lado; sem spread (preço único do leilão)'}]

**Aplicável:** True — ordens a mercado no call de fechamento (16h55-17h) e de abertura (9h45-10h) em qualquer home broker; exige operar todo dia

| métrica | valor |
|---|---|
| OOS desde | 2021-01 |
| retorno OOS a.a. (R$ 20 mil) | 18.5% vs CDI 11.4% |
| ativo OOS pp (R$ 20 mil / R$ 50 mil) | +7.06 / +7.07 |
| depois do IR (classe acoes) pp, 20k / 50k | +5.66 / +5.67 |
| IR OOS / Sharpe | +0.47 / +0.47 |
| pior queda | -13.6% |
| PBO / Sharpe deflacionado | 10% / +24% |
| leque de parâmetros p5 / mediana / p95 | -1.73 / +7.91 / +17.12 |
| custo 2x / execução t+2 | -9.79 / +7.76 |
| walk-forward | +20.65 |
| sem os 10 melhores negócios | +1.89 |
| placebo p | 0.00 |
| look-ahead (truncamento) | passou |

**10 melhores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| PRIO3   |      1 | 2020-03-09 00:00:00 | 2020-03-10 00:00:00 |      1 |       23.53 |         5.87 |
| GOLL4   |      1 | 2020-03-12 00:00:00 | 2020-03-13 00:00:00 |      1 |       21.79 |         5.44 |
| AZUL4   |      1 | 2020-03-12 00:00:00 | 2020-03-13 00:00:00 |      1 |       20.46 |         5.11 |
| BRKM5   |      1 | 2020-03-12 00:00:00 | 2020-03-13 00:00:00 |      1 |       20.04 |         5.01 |
| AMER3   |      1 | 2023-01-20 00:00:00 | 2023-01-23 00:00:00 |      1 |       19.64 |         4.91 |
| AMBP3   |      1 | 2024-08-15 00:00:00 | 2024-08-16 00:00:00 |      1 |       18.61 |         4.63 |
| OIBR4   |      1 | 2014-07-15 00:00:00 | 2014-07-16 00:00:00 |      1 |       17.87 |         4.47 |
| BBAS3   |      1 | 2016-03-16 00:00:00 | 2016-03-17 00:00:00 |      1 |       17.17 |         4.29 |
| CSNA3   |      1 | 2020-03-12 00:00:00 | 2020-03-13 00:00:00 |      1 |       16.18 |         4.04 |
| OIBR3   |      1 | 2019-08-27 00:00:00 | 2019-08-28 00:00:00 |      1 |       15.71 |         3.93 |

**10 piores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| AZUL4   |      1 | 2020-03-13 00:00:00 | 2020-03-16 00:00:00 |      1 |      -29.66 |        -7.4  |
| PRIO3   |      1 | 2020-03-13 00:00:00 | 2020-03-16 00:00:00 |      1 |      -25.2  |        -6.28 |
| IRBR3   |      1 | 2020-03-03 00:00:00 | 2020-03-04 00:00:00 |      1 |      -24.72 |        -6.16 |
| AMER3   |      1 | 2023-01-13 00:00:00 | 2023-01-16 00:00:00 |      1 |      -23.89 |        -5.97 |
| BEEF3   |      1 | 2025-04-29 00:00:00 | 2025-04-30 00:00:00 |      1 |      -22.36 |        -5.58 |
| GOLL4   |      1 | 2020-03-13 00:00:00 | 2020-03-16 00:00:00 |      1 |      -20.4  |        -5.09 |
| CVCB3   |      1 | 2020-03-13 00:00:00 | 2020-03-16 00:00:00 |      1 |      -20.15 |        -5.02 |
| HAPV3   |      1 | 2023-02-28 00:00:00 | 2023-03-01 00:00:00 |      1 |      -19.23 |        -4.81 |
| TCSA3   |      1 | 2020-03-18 00:00:00 | 2020-03-19 00:00:00 |      1 |      -18.54 |        -4.64 |
| AMER3   |      1 | 2023-01-18 00:00:00 | 2023-01-19 00:00:00 |      1 |      -15.02 |        -3.75 |

**Quem trouxe o retorno (soma por ativo, pp)**

| ativo   |   sum |   count |
|:--------|------:|--------:|
| VALE3   | 16.93 |     165 |
| MGLU3   | 16.29 |     229 |
| VVAR3   | 16.1  |      40 |
| BRKM5   | 14.27 |     128 |
| OIBR3   | 11.99 |      85 |
| CSNA3   | 11.57 |     226 |
| VALE5   |  9.8  |      81 |
| USIM5   |  9.66 |     163 |
| GGBR4   |  9.63 |     138 |
| BTOW3   |  9.61 |      69 |

### Ofertas de ações pela tranche de varejo (PF) — AUDITADA (rateio 15% + pedido bloqueado)  (`b3_ofertas_varejo_aud`)

**Tese:** Peço R$ 3-10 mil em toda oferta de ações com tranche de varejo e vendo no 1º pregão (ou em k pregões): o coordenador dá desconto para fechar o livro institucional e o pequeno pega o mesmo preço sem corretagem, recebendo tudo ou a parcela igualitária do rateio

**Instrumentos:** [{'onde': 'XP/BTG/Itaú/Clear/Rico/Inter (pedido de reserva na oferta)', 'ticker': 'IPO/follow-on ICVM 400 / Res. 160 público geral', 'lote': 'pedido mínimo ~R$ 1-3 mil', 'custo': 'compra sem custo na oferta; venda: emolumentos 0,03% + meio spread real'}]

**Aplicável:** True — qualquer corretora coordenadora/consorciada aceita pedido de reserva de pessoa física; desde 2023 quase só ofertas restritas (sem varejo)

| métrica | valor |
|---|---|
| OOS desde | 2021-01 |
| retorno OOS a.a. (R$ 20 mil) | 14.0% vs CDI 11.4% |
| ativo OOS pp (R$ 20 mil / R$ 50 mil) | +2.57 / +2.55 |
| depois do IR (classe acoes) pp, 20k / 50k | +2.53 / +2.51 |
| IR OOS / Sharpe | +0.56 / +0.56 |
| pior queda | -3.3% |
| PBO / Sharpe deflacionado | 41% / +20% |
| leque de parâmetros p5 / mediana / p95 | +1.97 / +4.05 / +7.88 |
| custo 2x / execução t+2 | +2.46 / +3.20 |
| walk-forward | +3.01 |
| sem os 10 melhores negócios | -1.25 |
| placebo p | 0.05 |
| look-ahead (truncamento) | passou |

**10 melhores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| SBSP3   |      1 | 2024-07-19 00:00:00 | 2024-07-19 00:00:00 |      1 |       26.62 |         6.6  |
| CSAN3   |      1 | 2025-11-04 00:00:00 | 2025-11-04 00:00:00 |      1 |       17.86 |         4.47 |
| CSMG3   |      1 | 2026-06-12 00:00:00 | 2026-06-12 00:00:00 |      1 |       16.73 |         4.14 |
| SOJA3   |      1 | 2021-04-29 00:00:00 | 2021-04-29 00:00:00 |      1 |       46.37 |         1.72 |
| SMFT3   |      1 | 2021-07-14 00:00:00 | 2021-07-14 00:00:00 |      1 |       34.72 |         1.28 |
| PRNR3   |      1 | 2020-02-17 00:00:00 | 2020-02-17 00:00:00 |      1 |       33.91 |         1.27 |
| MBLY3   |      1 | 2021-02-05 00:00:00 | 2021-02-05 00:00:00 |      1 |       25.65 |         0.94 |
| INTB3   |      1 | 2021-02-04 00:00:00 | 2021-02-04 00:00:00 |      1 |       25.26 |         0.94 |
| CXSE3   |      1 | 2025-03-20 00:00:00 | 2025-03-20 00:00:00 |      1 |        3.19 |         0.8  |
| PGMN3   |      1 | 2020-09-02 00:00:00 | 2020-09-02 00:00:00 |      1 |       21.08 |         0.79 |

**10 piores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| WEST3   |      1 | 2021-02-11 00:00:00 | 2021-02-11 00:00:00 |      1 |       -8.6  |        -2.15 |
| FIQE3   |      1 | 2021-07-27 00:00:00 | 2021-07-27 00:00:00 |      1 |       -8.28 |        -2.07 |
| MODL11  |      1 | 2021-04-30 00:00:00 | 2021-04-30 00:00:00 |      1 |       -7.42 |        -1.85 |
| ONCO3   |      1 | 2021-08-10 00:00:00 | 2021-08-10 00:00:00 |      1 |       -3.45 |        -0.86 |
| MOVI3   |      1 | 2017-02-08 00:00:00 | 2017-02-08 00:00:00 |      1 |       -3.23 |        -0.81 |
| BMOB3   |      1 | 2021-02-10 00:00:00 | 2021-02-10 00:00:00 |      1 |       -2.89 |        -0.72 |
| MDNE3   |      1 | 2020-02-13 00:00:00 | 2020-02-13 00:00:00 |      1 |       -2.77 |        -0.69 |
| LINX3   |      1 | 2019-06-26 00:00:00 | 2019-06-26 00:00:00 |      1 |       -2.42 |        -0.6  |
| HBSA3   |      1 | 2020-09-25 00:00:00 | 2020-09-25 00:00:00 |      1 |       -2.01 |        -0.5  |
| ELMD3   |      1 | 2021-02-17 00:00:00 | 2021-02-17 00:00:00 |      1 |       -1.8  |        -0.45 |

**Quem trouxe o retorno (soma por ativo, pp)**

| ativo   |   sum |   count |
|:--------|------:|--------:|
| SBSP3   |  6.6  |       1 |
| CSAN3   |  4.47 |       1 |
| CSMG3   |  4.14 |       1 |
| SOJA3   |  1.72 |       1 |
| SMFT3   |  1.28 |       1 |
| PRNR3   |  1.27 |       1 |
| MBLY3   |  0.94 |       1 |
| INTB3   |  0.94 |       1 |
| CXSE3   |  0.93 |       2 |
| PGMN3   |  0.79 |       1 |

### Micro caps perto da máxima de 52 semanas (PF)  (`b3_microcap_maxima`)

**Tese:** Compro R$ 2-6 mil das micro caps (giro R$ 30 mil-3 mi/dia) mais perto da máxima do ano: notícia boa se espalha devagar onde não há analista nem fundo grande; as que despencam são crises sem vendedor a descoberto e continuam caindo

**Instrumentos:** [{'onde': 'Clear/Rico/XP/BTG (B3 à vista + fracionário)', 'ticker': 'micro caps (ADV R$ 30 mil-3 mi)', 'lote': '1 ação', 'custo': 'emolumentos 0,03% + meio spread real do fechamento + 0,2% na parte fracionária'}]

**Aplicável:** True — ações à vista em qualquer corretora; R$ 2-6 mil por papel cabem no volume diário (compra só se o volume do dia >= 10x a ordem)

| métrica | valor |
|---|---|
| OOS desde | 2021-01 |
| retorno OOS a.a. (R$ 20 mil) | 12.6% vs CDI 11.4% |
| ativo OOS pp (R$ 20 mil / R$ 50 mil) | +1.16 / +1.86 |
| depois do IR (classe acoes) pp, 20k / 50k | +1.14 / +1.83 |
| IR OOS / Sharpe | +0.14 / +0.14 |
| pior queda | -33.5% |
| PBO / Sharpe deflacionado | 69% / +9% |
| leque de parâmetros p5 / mediana / p95 | -5.20 / +0.09 / +4.97 |
| custo 2x / execução t+2 | -2.89 / +6.81 |
| walk-forward | -5.43 |
| sem os 10 melhores negócios | -10.00 |
| placebo p | 0.01 |
| look-ahead (truncamento) | passou |

**10 melhores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| CARD3   |      1 | 2017-01-09 00:00:00 | 2017-03-10 00:00:00 |     42 |      105.3  |        12.5  |
| SAPR4   |      1 | 2016-06-10 00:00:00 | 2016-10-07 00:00:00 |     84 |       96.83 |        11.48 |
| CLSC4   |      1 | 2023-08-21 00:00:00 | NaT                 |    789 |      195.75 |        10.7  |
| CRPG5   |      1 | 2020-12-16 00:00:00 | 2021-08-18 00:00:00 |    168 |      192.03 |        10.25 |
| FJTA4   |      1 | 2018-09-13 00:00:00 | 2018-10-15 00:00:00 |     21 |      102.69 |         9.66 |
| TAEE4   |      1 | 2020-03-17 00:00:00 | 2021-05-20 00:00:00 |    294 |       74.81 |         8.85 |
| UNIP6   |      1 | 2016-01-08 00:00:00 | 2017-05-12 00:00:00 |    336 |      127.85 |         8.6  |
| TRIS3   |      1 | 2019-05-20 00:00:00 | 2019-08-16 00:00:00 |     63 |       68.97 |         8.19 |
| BMEB4   |      1 | 2023-11-22 00:00:00 | 2024-03-25 00:00:00 |     84 |       69.06 |         8.18 |
| PINE4   |      1 | 2025-07-25 00:00:00 | 2026-01-22 00:00:00 |    126 |      134.26 |         7.93 |

**10 piores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| COCE5   |      1 | 2021-12-20 00:00:00 | 2022-11-21 00:00:00 |    231 |      -32.28 |        -3.79 |
| SNSL3   |      1 | 2015-02-04 00:00:00 | 2016-02-10 00:00:00 |    252 |      -29.08 |        -3.45 |
| ALUP3   |      1 | 2020-02-13 00:00:00 | 2020-10-16 00:00:00 |    168 |      -29.09 |        -3.44 |
| BPAC5   |      1 | 2022-10-19 00:00:00 | 2022-12-20 00:00:00 |     42 |      -27.26 |        -3.23 |
| BMEB4   |      1 | 2020-01-15 00:00:00 | 2020-04-16 00:00:00 |     63 |      -25.15 |        -2.98 |
| ENJU3   |      1 | 2024-05-24 00:00:00 | 2024-06-25 00:00:00 |     21 |      -23.78 |        -2.82 |
| VIVT3   |      1 | 2015-02-04 00:00:00 | 2015-12-08 00:00:00 |    210 |      -23.71 |        -2.79 |
| TFCO4   |      1 | 2021-08-18 00:00:00 | 2021-12-20 00:00:00 |     84 |      -22.63 |        -2.68 |
| CTNM4   |      1 | 2019-04-17 00:00:00 | 2019-05-20 00:00:00 |     21 |      -22.53 |        -2.67 |
| CEBR5   |      1 | 2024-04-24 00:00:00 | 2024-06-25 00:00:00 |     42 |      -22.5  |        -2.66 |

**Quem trouxe o retorno (soma por ativo, pp)**

| ativo   |   sum |   count |
|:--------|------:|--------:|
| CRPG5   | 17.34 |       4 |
| CLSC4   | 16.98 |       7 |
| UNIP6   | 16.13 |       2 |
| CESP3   | 12.51 |       3 |
| CARD3   | 12.51 |       2 |
| SAPR4   | 11.48 |       1 |
| PINE4   | 11.47 |       4 |
| TAEE3   | 11.1  |       4 |
| BMEB4   | 10.42 |       7 |
| AGRO3   |  9.8  |       3 |

### Units x componentes com conversão no escriturador (PF)  (`b3_units`)

**Tese:** Compro o lado barato (unit ou cesta ON+PN) e converto no escriturador em vez de vender a descoberto: o desvio que sobra está nos componentes ilíquidos, onde R$ 5-10 mil cabem e o institucional não escala

**Instrumentos:** [{'onde': 'Clear/Rico/XP/BTG + escriturador (Itaú/Bradesco) via corretora', 'ticker': 'TAEE11, KLBN11, SAPR11, ENGI11, ALUP11, SANB11, BPAC11, TIET11, IGTI11, SULA11, CPLE11, BIDI11, MODL11, RNEW11', 'lote': '1 unit / 1 ação', 'custo': 'emolumentos 0,03% + meio spread real nas duas pontas; conversão sem custo (premissa) em `prazo` pregões'}]

**Aplicável:** True — desmembramento de units é pedido padrão no escriturador (3-5 dias úteis); a composição de unit nem sempre está aberta (algumas companhias suspendem) — a variante 'unit_barata' usa só o desmembramento

| métrica | valor |
|---|---|
| OOS desde | 2021-01 |
| retorno OOS a.a. (R$ 20 mil) | -1.1% vs CDI 11.4% |
| ativo OOS pp (R$ 20 mil / R$ 50 mil) | -12.51 / -8.08 |
| depois do IR (classe acoes) pp, 20k / 50k | -12.32 / -7.96 |
| IR OOS / Sharpe | -1.25 / -1.25 |
| pior queda | -40.2% |
| PBO / Sharpe deflacionado | 4% / +0% |
| leque de parâmetros p5 / mediana / p95 | -19.10 / -8.94 / -2.82 |
| custo 2x / execução t+2 | -12.84 / -7.50 |
| walk-forward | -9.29 |
| sem os 10 melhores negócios | -16.63 |
| placebo p | 0.86 |
| look-ahead (truncamento) | passou |

**10 melhores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| BIDI11  |      1 | 2020-06-22 00:00:00 | 2020-06-29 00:00:00 |      5 |       15.38 |         7.66 |
| BIDI11  |      1 | 2019-11-27 00:00:00 | 2019-12-04 00:00:00 |      5 |        8.97 |         4.46 |
| RNEW11  |      1 | 2017-04-27 00:00:00 | 2017-05-05 00:00:00 |      5 |        8.12 |         4.04 |
| BIDI11  |      1 | 2020-03-12 00:00:00 | 2020-03-19 00:00:00 |      5 |        7.72 |         3.85 |
| BPAC11  |      1 | 2026-08-31 00:00:00 | 2026-09-08 00:00:00 |      5 |        8.19 |         3.78 |
| RNEW11  |      1 | 2021-11-30 00:00:00 | 2021-12-07 00:00:00 |      5 |        6.72 |         3.35 |
| RNEW11  |      1 | 2022-07-29 00:00:00 | 2022-08-05 00:00:00 |      5 |        7.82 |         2.76 |
| BPAC11  |      1 | 2021-06-30 00:00:00 | 2021-07-07 00:00:00 |      5 |        5.21 |         2.56 |
| BPAC11  |      1 | 2026-08-20 00:00:00 | 2026-08-27 00:00:00 |      5 |        4.99 |         2.34 |
| TIET11  |      1 | 2020-04-23 00:00:00 | 2020-04-30 00:00:00 |      5 |        4.55 |         2.26 |

**10 piores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| BIDI11  |      1 | 2022-05-02 00:00:00 | 2022-05-09 00:00:00 |      5 |      -15.94 |        -7.99 |
| RNEW11  |      1 | 2021-02-24 00:00:00 | 2021-03-03 00:00:00 |      5 |      -15.87 |        -7.94 |
| RNEW11  |      1 | 2021-09-13 00:00:00 | 2021-09-20 00:00:00 |      5 |      -14.01 |        -7.02 |
| RNEW11  |      1 | 2022-08-22 00:00:00 | 2022-08-29 00:00:00 |      5 |      -13.9  |        -6.97 |
| ENGI11  |      1 | 2020-03-13 00:00:00 | 2020-03-20 00:00:00 |      5 |      -19.16 |        -5.41 |
| SAPR11  |      1 | 2020-03-18 00:00:00 | 2020-03-25 00:00:00 |      5 |       -9.93 |        -4.95 |
| BPAC11  |      1 | 2026-03-02 00:00:00 | 2026-03-09 00:00:00 |      5 |       -9.79 |        -4.89 |
| BIDI11  |      1 | 2022-05-26 00:00:00 | 2022-06-02 00:00:00 |      5 |       -9.53 |        -4.78 |
| SANB11  |      1 | 2022-11-08 00:00:00 | 2022-11-16 00:00:00 |      5 |       -9.19 |        -4.61 |
| BPAC11  |      1 | 2021-08-12 00:00:00 | 2021-08-19 00:00:00 |      5 |       -8.17 |        -4.1  |

**Quem trouxe o retorno (soma por ativo, pp)**

| ativo   |   sum |   count |
|:--------|------:|--------:|
| CPLE11  |  3.53 |       3 |
| BIDI11  |  1.94 |       8 |
| TIET11  |  1.01 |       3 |
| TAEE11  |  0.57 |       3 |
| IGTI11  | -0.97 |       5 |
| SULA11  | -1.14 |       2 |
| ENGI11  | -2.53 |       4 |
| ALUP11  | -2.97 |       4 |
| KLBN11  | -3.54 |       4 |
| SAPR11  | -6.41 |       6 |

### Reversão semanal em micro caps ilíquidas (PF)  (`b3_microcap_reversao`)

**Tese:** Compro R$ 1-3 mil dos maiores perdedores da semana entre papéis que giram R$ 30 mil-3 mi/dia: vendedores forçados sem contraparte institucional derrubam o preço além do valor; o pequeno fornece liquidez e devolve quando o preço volta

**Instrumentos:** [{'onde': 'Clear/Rico/XP/BTG (B3 à vista + fracionário)', 'ticker': 'small/micro caps (ADV R$ 30 mil-3 mi)', 'lote': '1 ação (fracionário) / 100', 'custo': 'emolumentos 0,03% + meio spread real do fechamento + 0,2% na parte fracionária'}]

**Aplicável:** True — ações à vista em qualquer corretora de varejo; ordens limitadas de R$ 1-3 mil; capacidade limitada pelo volume dos papéis (é o edge)

| métrica | valor |
|---|---|
| OOS desde | 2021-01 |
| retorno OOS a.a. (R$ 20 mil) | -55.7% vs CDI 11.4% |
| ativo OOS pp (R$ 20 mil / R$ 50 mil) | -67.13 / -63.23 |
| depois do IR (classe acoes) pp, 20k / 50k | -66.10 / -62.26 |
| IR OOS / Sharpe | -3.06 / -3.06 |
| pior queda | -99.2% |
| PBO / Sharpe deflacionado | 0% / +0% |
| leque de parâmetros p5 / mediana / p95 | -54.10 / -37.94 / -21.95 |
| custo 2x / execução t+2 | -88.51 / -62.04 |
| walk-forward | -30.67 |
| sem os 10 melhores negócios | -79.92 |
| placebo p | 0.94 |
| look-ahead (truncamento) | passou |

**10 melhores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| IGBR3   |      1 | 2022-01-20 00:00:00 | 2022-01-27 00:00:00 |      5 |      183.1  |        21.64 |
| FJTA3   |      1 | 2018-10-01 00:00:00 | 2018-10-08 00:00:00 |      5 |      102.71 |        12.19 |
| RNEW11  |      1 | 2018-07-13 00:00:00 | 2018-07-20 00:00:00 |      5 |       75.55 |         8.97 |
| AZEV3   |      1 | 2026-08-13 00:00:00 | 2026-08-20 00:00:00 |      5 |       66.53 |         7.9  |
| WEST3   |      1 | 2023-08-03 00:00:00 | 2023-08-10 00:00:00 |      5 |       62.59 |         7.43 |
| PDGR3   |      1 | 2026-03-13 00:00:00 | 2026-03-27 00:00:00 |     10 |       61.37 |         7.28 |
| OGXP3   |      1 | 2016-06-30 00:00:00 | 2016-07-07 00:00:00 |      5 |       51.97 |         6.16 |
| CEDO4   |      1 | 2023-05-10 00:00:00 | 2023-05-17 00:00:00 |      5 |       50.12 |         5.95 |
| OIBR4   |      1 | 2023-01-18 00:00:00 | 2023-01-25 00:00:00 |      5 |       42.47 |         5.04 |
| INEP4   |      1 | 2025-04-30 00:00:00 | 2025-05-08 00:00:00 |      5 |       41.9  |         4.98 |

**10 piores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| BPHA3   |      1 | 2015-12-01 00:00:00 | 2015-12-30 00:00:00 |     20 |      -69.3  |        -8.21 |
| SEQL3   |      1 | 2026-01-21 00:00:00 | 2026-02-11 00:00:00 |     15 |      -64.71 |        -7.68 |
| REAG3   |      1 | 2025-10-06 00:00:00 | 2025-10-24 00:00:00 |     14 |      -60.56 |        -7.19 |
| VTLM3   |      1 | 2016-09-01 00:00:00 | 2016-10-17 00:00:00 |     30 |      -60.35 |        -7.16 |
| PDGR3   |      1 | 2023-12-06 00:00:00 | 2023-12-13 00:00:00 |      5 |      -54.36 |        -6.45 |
| BRIN3   |      1 | 2014-11-17 00:00:00 | 2014-12-30 00:00:00 |     30 |      -51.24 |        -6.07 |
| DOTZ3   |      1 | 2021-09-27 00:00:00 | 2021-11-03 00:00:00 |     25 |      -50.5  |        -5.98 |
| TCNO4   |      1 | 2021-12-09 00:00:00 | 2021-12-16 00:00:00 |      5 |      -48.82 |        -5.79 |
| FRTA3   |      1 | 2020-02-13 00:00:00 | 2020-03-05 00:00:00 |     13 |      -48.14 |        -5.71 |
| BPHA3   |      1 | 2015-01-07 00:00:00 | 2015-02-04 00:00:00 |     20 |      -47.96 |        -5.69 |

**Quem trouxe o retorno (soma por ativo, pp)**

| ativo   |   sum |   count |
|:--------|------:|--------:|
| FJTA3   | 10.5  |       4 |
| IGBR3   |  7.98 |      35 |
| OIBR4   |  6.01 |      18 |
| BBRK3   |  5.52 |      37 |
| OGXP3   |  4.63 |       9 |
| MDNE3   |  4.34 |       5 |
| JSLG3   |  4.15 |      18 |
| BMEB4   |  3.97 |      21 |
| DMMO3   |  3.94 |       4 |
| WEST3   |  3.9  |      18 |

### Fracionário x lote padrão em day trade (PF)  (`b3_fracionario`)

**Tese:** Vendo 100 ações no fracionário quando o varejo ali paga mais do que o lote padrão pede (e recompro 1 lote), ou o inverso: prêmio entre dois livros da mesma ação que só existe em lotes de 100 ações, pequeno demais para o institucional

**Instrumentos:** [{'onde': 'Clear/Rico/XP (conta com day trade)', 'ticker': 'ações com fracionário ativo', 'lote': '100 ações (fracionário 1-99 + 1 ordem)', 'custo': 'emolumentos de day trade 0,023% por perna; corretagem zero'}]

**Aplicável:** False — NÃO TESTÁVEL HONESTAMENTE com o COTAHIST (auditoria final, ver pf/pesquisa/correcoes_finais.md): o arquivo não tem horário nem quantidade das ofertas dos dois livros. A versão original (+9,7 pp OOS) vendia no fracionário a qualquer hora e recomprava o lote no FECHAMENTO: o P&L era o movimento intradiário de small caps (AZEV3 +104% num dia), não o prêmio. Com as duas pernas simultâneas na abertura (único instante comum) e execução no limite, o edge fica perto de zero e o resultado depende de premissa não verificável (preço do leilão de abertura do fracionário com a minha ordem dentro). Além disso: exige conta de day trade e venda a descoberto intradiária no fracionário (permitida em Clear/Rico para papéis líquidos; restrita em papéis pequenos) e automação (MetaTrader/Profit) para deixar várias ordens por dia

| métrica | valor |
|---|---|
| OOS desde | 2021-01 |
| retorno OOS a.a. (R$ 20 mil) | 12.4% vs CDI 11.4% |
| ativo OOS pp (R$ 20 mil / R$ 50 mil) | +0.94 / +0.72 |
| depois do IR (classe day_trade) pp, 20k / 50k | +0.92 / +0.71 |
| IR OOS / Sharpe | +0.65 / +0.65 |
| pior queda | -1.7% |
| PBO / Sharpe deflacionado | 17% / +5% |
| leque de parâmetros p5 / mediana / p95 | -2.18 / +0.63 / +1.10 |
| custo 2x / execução t+2 | +0.68 / -24.92 |
| walk-forward | +1.08 |
| sem os 10 melhores negócios | +0.31 |
| placebo p | 1.00 |
| look-ahead (truncamento) | passou |

**10 melhores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| PARD3   |      1 | 2020-03-27 00:00:00 | 2020-03-27 00:00:00 |      0 |        7.32 |         0.75 |
| MPLU3   |      1 | 2017-03-01 00:00:00 | 2017-03-01 00:00:00 |      0 |        3.79 |         0.71 |
| ARML3   |      1 | 2023-05-10 00:00:00 | 2023-05-10 00:00:00 |      0 |        7.51 |         0.53 |
| RSID3   |      1 | 2020-01-31 00:00:00 | 2020-01-31 00:00:00 |      0 |        9.44 |         0.47 |
| SHUL4   |      1 | 2020-02-27 00:00:00 | 2020-02-27 00:00:00 |      0 |        6.17 |         0.46 |
| IFCM3   |      1 | 2021-08-18 00:00:00 | 2021-08-18 00:00:00 |      0 |        5.19 |         0.45 |
| OMGE3   |      1 | 2020-11-12 00:00:00 | 2020-11-12 00:00:00 |      0 |        2.51 |         0.44 |
| BKBR3   |      1 | 2020-03-06 00:00:00 | 2020-03-06 00:00:00 |      0 |        6.2  |         0.43 |
| INEP4   |     -1 | 2021-04-29 00:00:00 | 2021-04-29 00:00:00 |      0 |        1.94 |         0.43 |
| MDIA3   |      1 | 2018-05-21 00:00:00 | 2018-05-21 00:00:00 |      0 |        1.97 |         0.42 |

**10 piores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| CRPG5   |     -1 | 2019-04-30 00:00:00 | 2019-04-30 00:00:00 |      0 |      -19.38 |        -3.22 |
| MGLU3   |      1 | 2016-05-06 00:00:00 | 2016-05-06 00:00:00 |      0 |      -12.54 |        -1.82 |
| JPSA3   |     -1 | 2020-03-09 00:00:00 | 2020-03-09 00:00:00 |      0 |      -10.56 |        -1.74 |
| SIMH3   |      1 | 2026-02-18 00:00:00 | 2026-02-18 00:00:00 |      0 |      -48.89 |        -1.63 |
| AZUL4   |     -1 | 2017-05-18 00:00:00 | 2017-05-18 00:00:00 |      0 |      -12.39 |        -1.62 |
| TELB4   |      1 | 2019-08-26 00:00:00 | 2019-08-26 00:00:00 |      0 |       -6.84 |        -1.49 |
| MMXM3   |     -1 | 2020-10-15 00:00:00 | 2020-10-15 00:00:00 |      0 |      -16.84 |        -1.41 |
| VIVA3   |     -1 | 2020-03-16 00:00:00 | 2020-03-16 00:00:00 |      0 |      -12.15 |        -1.22 |
| FJTA4   |     -1 | 2018-10-30 00:00:00 | 2018-10-30 00:00:00 |      0 |      -25.2  |        -1    |
| MMXM3   |      1 | 2020-10-22 00:00:00 | 2020-10-22 00:00:00 |      0 |      -12.18 |        -0.86 |

**Quem trouxe o retorno (soma por ativo, pp)**

| ativo   |   sum |   count |
|:--------|------:|--------:|
| HGTX3   |  1.96 |      15 |
| GRND3   |  1.31 |      18 |
| SHUL4   |  1.21 |      13 |
| PSSA3   |  1.16 |       5 |
| CARD3   |  1.07 |      12 |
| EGIE3   |  1.04 |       5 |
| PARD3   |  0.95 |       2 |
| QUAL3   |  0.87 |      12 |
| TIET11  |  0.75 |       8 |
| ARML3   |  0.71 |       6 |

### Noite nos leilões após queda forte (PF)  (`b3_leilao_noite`)

**Tese:** Compro no leilão de fechamento as ações líquidas que caíram >= 2-4% abaixo do mercado no dia anterior e vendo no leilão de abertura: o prêmio da B3 está na noite (o pregão devolve), e é maior depois de vendas forçadas; no leilão o pequeno não paga spread

**Instrumentos:** [{'onde': 'Clear/Rico/XP/BTG (B3 à vista, ordens nos leilões de fechamento e abertura)', 'ticker': 'ações líquidas do Ibovespa', 'lote': '1 ação (fracionário também tem leilão) / 100', 'custo': 'emolumentos 0,03% por lado; sem spread (preço único do leilão)'}]

**Aplicável:** True — ordens a mercado no call de fechamento (16h55-17h) e de abertura (9h45-10h) em qualquer home broker; exige operar todo dia

| métrica | valor |
|---|---|
| OOS desde | 2021-01 |
| retorno OOS a.a. (R$ 20 mil) | 23.1% vs CDI 11.4% |
| ativo OOS pp (R$ 20 mil / R$ 50 mil) | +11.69 / +11.71 |
| depois do IR (classe acoes) pp, 20k / 50k | +9.48 / +9.49 |
| IR OOS / Sharpe | +0.71 / +0.71 |
| pior queda | -12.5% |
| PBO / Sharpe deflacionado | 9% / +42% |
| leque de parâmetros p5 / mediana / p95 | +2.90 / +10.42 / +22.01 |
| custo 2x / execução t+2 | -1.68 / +12.40 |
| walk-forward | +27.26 |
| sem os 10 melhores negócios | +6.52 |
| placebo p | 0.00 |
| look-ahead (truncamento) | passou |

**10 melhores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| PRIO3   |      1 | 2020-03-09 00:00:00 | 2020-03-10 00:00:00 |      1 |       23.55 |         5.88 |
| GOLL4   |      1 | 2020-03-12 00:00:00 | 2020-03-13 00:00:00 |      1 |       21.81 |         5.45 |
| AZUL4   |      1 | 2020-03-12 00:00:00 | 2020-03-13 00:00:00 |      1 |       20.48 |         5.11 |
| BRKM5   |      1 | 2020-03-12 00:00:00 | 2020-03-13 00:00:00 |      1 |       20.06 |         5.01 |
| AMER3   |      1 | 2023-01-20 00:00:00 | 2023-01-23 00:00:00 |      1 |       19.66 |         4.91 |
| AMBP3   |      1 | 2024-08-15 00:00:00 | 2024-08-16 00:00:00 |      1 |       18.63 |         4.64 |
| OIBR4   |      1 | 2014-07-15 00:00:00 | 2014-07-16 00:00:00 |      1 |       17.89 |         4.47 |
| BBAS3   |      1 | 2016-03-16 00:00:00 | 2016-03-17 00:00:00 |      1 |       17.19 |         4.29 |
| CSNA3   |      1 | 2020-03-12 00:00:00 | 2020-03-13 00:00:00 |      1 |       16.2  |         4.05 |
| OIBR3   |      1 | 2019-08-27 00:00:00 | 2019-08-28 00:00:00 |      1 |       15.73 |         3.93 |

**10 piores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| AZUL4   |      1 | 2020-03-13 00:00:00 | 2020-03-16 00:00:00 |      1 |      -29.64 |        -7.4  |
| PRIO3   |      1 | 2020-03-13 00:00:00 | 2020-03-16 00:00:00 |      1 |      -25.18 |        -6.28 |
| IRBR3   |      1 | 2020-03-03 00:00:00 | 2020-03-04 00:00:00 |      1 |      -24.7  |        -6.16 |
| AMER3   |      1 | 2023-01-13 00:00:00 | 2023-01-16 00:00:00 |      1 |      -23.87 |        -5.97 |
| BEEF3   |      1 | 2025-04-29 00:00:00 | 2025-04-30 00:00:00 |      1 |      -22.34 |        -5.58 |
| GOLL4   |      1 | 2020-03-13 00:00:00 | 2020-03-16 00:00:00 |      1 |      -20.38 |        -5.09 |
| CVCB3   |      1 | 2020-03-13 00:00:00 | 2020-03-16 00:00:00 |      1 |      -20.13 |        -5.02 |
| HAPV3   |      1 | 2023-02-28 00:00:00 | 2023-03-01 00:00:00 |      1 |      -19.21 |        -4.8  |
| TCSA3   |      1 | 2020-03-18 00:00:00 | 2020-03-19 00:00:00 |      1 |      -18.52 |        -4.63 |
| AMER3   |      1 | 2023-01-18 00:00:00 | 2023-01-19 00:00:00 |      1 |      -15    |        -3.75 |

**Quem trouxe o retorno (soma por ativo, pp)**

| ativo   |   sum |   count |
|:--------|------:|--------:|
| VALE3   | 17.75 |     165 |
| MGLU3   | 17.43 |     229 |
| VVAR3   | 16.3  |      40 |
| BRKM5   | 14.91 |     128 |
| CSNA3   | 12.69 |     226 |
| OIBR3   | 12.42 |      85 |
| USIM5   | 10.47 |     163 |
| GGBR4   | 10.32 |     138 |
| VALE5   | 10.21 |      81 |
| BTOW3   |  9.96 |      69 |

### Valor + qualidade em small/micro caps, isento de IR (PF)  (`b3_microcap_valor`)

**Tese:** Compro R$ 2-5 mil das small/micro caps lucrativas mais baratas (lucro e PL sobre valor de mercado, dados da CVM na data de entrega): baratas porque nenhum fundo grande consegue comprá-las; vendas do mês limitadas a R$ 20 mil para o ganho ser isento

**Instrumentos:** [{'onde': 'Clear/Rico/XP/BTG (B3 à vista + fracionário)', 'ticker': 'small/micro caps lucrativas', 'lote': '1 ação', 'custo': 'emolumentos 0,03% + meio spread real do fechamento + 0,2% na parte fracionária'}]

**Aplicável:** True — ações à vista; R$ 2-5 mil por papel; vendas do mês até R$ 20 mil (isenção de IR)

| métrica | valor |
|---|---|
| OOS desde | 2021-01 |
| retorno OOS a.a. (R$ 20 mil) | 17.3% vs CDI 11.4% |
| ativo OOS pp (R$ 20 mil / R$ 50 mil) | +5.90 / +8.90 |
| depois do IR (classe acoes) pp, 20k / 50k | +5.80 / +8.76 |
| IR OOS / Sharpe | +0.37 / +0.37 |
| pior queda | -27.7% |
| PBO / Sharpe deflacionado | 25% / +20% |
| leque de parâmetros p5 / mediana / p95 | +2.88 / +6.90 / +9.83 |
| custo 2x / execução t+2 | +3.58 / +3.64 |
| walk-forward | +5.61 |
| sem os 10 melhores negócios | -5.12 |
| placebo p | 0.00 |
| look-ahead (truncamento) | FALHOU |

**10 melhores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| GPCP3   |      1 | 2020-07-17 00:00:00 | 2021-07-19 00:00:00 |    251 |      431.01 |        19.11 |
| JHSF3   |      1 | 2019-01-16 00:00:00 | 2020-01-15 00:00:00 |    252 |      386.73 |        14.73 |
| LCAM3   |      1 | 2017-07-12 00:00:00 | 2018-01-12 00:00:00 |    126 |      140.13 |        13.25 |
| CRPG5   |      1 | 2017-04-10 00:00:00 | 2017-10-10 00:00:00 |    126 |      127.38 |        12.06 |
| TECN3   |      1 | 2023-01-18 00:00:00 | 2024-04-24 00:00:00 |    315 |      115.54 |        10.98 |
| FESA4   |      1 | 2017-04-10 00:00:00 | 2018-01-12 00:00:00 |    189 |      174.33 |        10.51 |
| CRPG5   |      1 | 2020-10-16 00:00:00 | 2021-07-20 00:00:00 |    189 |      382.26 |         8.99 |
| SAPR4   |      1 | 2016-04-11 00:00:00 | 2017-01-09 00:00:00 |    189 |      215.74 |         8.82 |
| JHSF3   |      1 | 2019-01-16 00:00:00 | 2019-10-15 00:00:00 |    189 |      147.19 |         8.38 |
| CARD3   |      1 | 2017-01-09 00:00:00 | 2017-04-10 00:00:00 |     63 |       84.7  |         8.03 |

**10 piores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| VULC3   |      1 | 2020-01-15 00:00:00 | 2020-04-16 00:00:00 |     63 |      -55.3  |        -5.23 |
| SOJA3   |      1 | 2024-04-24 00:00:00 | 2024-10-21 00:00:00 |    126 |      -36.1  |        -3.42 |
| RSUL4   |      1 | 2026-04-27 00:00:00 | 2026-07-27 00:00:00 |     63 |      -33.69 |        -3.15 |
| JPSA3   |      1 | 2019-10-15 00:00:00 | 2020-04-16 00:00:00 |    126 |      -32.75 |        -3.1  |
| EALT4   |      1 | 2019-10-15 00:00:00 | 2020-04-16 00:00:00 |    126 |      -32.19 |        -3.05 |
| UCAS3   |      1 | 2021-04-20 00:00:00 | 2022-04-20 00:00:00 |    252 |      -34.43 |        -3.03 |
| CURY3   |      1 | 2021-01-18 00:00:00 | 2021-10-19 00:00:00 |    189 |      -30.99 |        -2.94 |
| CGRA4   |      1 | 2021-10-19 00:00:00 | 2022-10-19 00:00:00 |    252 |      -30.15 |        -2.85 |
| BAZA3   |      1 | 2026-04-27 00:00:00 | 2026-07-27 00:00:00 |     63 |      -29.6  |        -2.77 |
| MDNE3   |      1 | 2022-10-19 00:00:00 | 2023-04-20 00:00:00 |    126 |      -27.53 |        -2.61 |

**Quem trouxe o retorno (soma por ativo, pp)**

| ativo   |   sum |   count |
|:--------|------:|--------:|
| CRPG5   | 36.2  |       6 |
| GPCP3   | 27.34 |       3 |
| JHSF3   | 23.1  |       2 |
| TECN3   | 16.65 |       3 |
| SHUL4   | 15.24 |       7 |
| LAVV3   | 14.47 |       4 |
| FESA4   | 14.45 |       7 |
| LCAM3   | 14.42 |       2 |
| SAPR4   | 14.3  |       3 |
| AGRO3   | 13.28 |       3 |

### Ofertas de ações pela tranche de varejo (PF)  (`b3_ofertas_varejo`)

**Tese:** Peço R$ 3-10 mil em toda oferta de ações com tranche de varejo e vendo no 1º pregão (ou em k pregões): o coordenador dá desconto para fechar o livro institucional e o pequeno pega o mesmo preço sem corretagem, recebendo tudo ou a parcela igualitária do rateio

**Instrumentos:** [{'onde': 'XP/BTG/Itaú/Clear/Rico/Inter (pedido de reserva na oferta)', 'ticker': 'IPO/follow-on ICVM 400 / Res. 160 público geral', 'lote': 'pedido mínimo ~R$ 1-3 mil', 'custo': 'compra sem custo na oferta; venda: emolumentos 0,03% + meio spread real'}]

**Aplicável:** True — qualquer corretora coordenadora/consorciada aceita pedido de reserva de pessoa física; desde 2023 quase só ofertas restritas (sem varejo)

| métrica | valor |
|---|---|
| OOS desde | 2021-01 |
| retorno OOS a.a. (R$ 20 mil) | 15.7% vs CDI 11.4% |
| ativo OOS pp (R$ 20 mil / R$ 50 mil) | +4.25 / +4.21 |
| depois do IR (classe acoes) pp, 20k / 50k | +4.18 / +3.95 |
| IR OOS / Sharpe | +0.82 / +0.82 |
| pior queda | -3.3% |
| PBO / Sharpe deflacionado | 40% / +7% |
| leque de parâmetros p5 / mediana / p95 | +2.09 / +4.20 / +8.06 |
| custo 2x / execução t+2 | +4.09 / +5.12 |
| walk-forward | +3.32 |
| sem os 10 melhores negócios | -0.64 |
| placebo p | 0.04 |
| look-ahead (truncamento) | passou |

**10 melhores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| SBSP3   |      1 | 2024-07-19 00:00:00 | 2024-07-19 00:00:00 |      1 |       26.62 |         6.6  |
| CSAN3   |      1 | 2025-11-04 00:00:00 | 2025-11-04 00:00:00 |      1 |       17.86 |         4.47 |
| CSMG3   |      1 | 2026-06-12 00:00:00 | 2026-06-12 00:00:00 |      1 |       16.73 |         4.14 |
| SOJA3   |      1 | 2021-04-29 00:00:00 | 2021-04-29 00:00:00 |      1 |       46.37 |         3.47 |
| SMFT3   |      1 | 2021-07-14 00:00:00 | 2021-07-14 00:00:00 |      1 |       34.72 |         2.6  |
| PRNR3   |      1 | 2020-02-17 00:00:00 | 2020-02-17 00:00:00 |      1 |       33.91 |         2.54 |
| MBLY3   |      1 | 2021-02-05 00:00:00 | 2021-02-05 00:00:00 |      1 |       25.65 |         1.91 |
| INTB3   |      1 | 2021-02-04 00:00:00 | 2021-02-04 00:00:00 |      1 |       25.26 |         1.89 |
| PGMN3   |      1 | 2020-09-02 00:00:00 | 2020-09-02 00:00:00 |      1 |       21.08 |         1.58 |
| LWSA3   |      1 | 2020-02-06 00:00:00 | 2020-02-06 00:00:00 |      1 |       18.95 |         1.41 |

**10 piores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| WEST3   |      1 | 2021-02-11 00:00:00 | 2021-02-11 00:00:00 |      1 |       -8.6  |        -2.15 |
| FIQE3   |      1 | 2021-07-27 00:00:00 | 2021-07-27 00:00:00 |      1 |       -8.28 |        -2.07 |
| MODL11  |      1 | 2021-04-30 00:00:00 | 2021-04-30 00:00:00 |      1 |       -7.42 |        -1.85 |
| ONCO3   |      1 | 2021-08-10 00:00:00 | 2021-08-10 00:00:00 |      1 |       -3.45 |        -0.86 |
| MOVI3   |      1 | 2017-02-08 00:00:00 | 2017-02-08 00:00:00 |      1 |       -3.23 |        -0.81 |
| BMOB3   |      1 | 2021-02-10 00:00:00 | 2021-02-10 00:00:00 |      1 |       -2.89 |        -0.72 |
| MDNE3   |      1 | 2020-02-13 00:00:00 | 2020-02-13 00:00:00 |      1 |       -2.77 |        -0.69 |
| LINX3   |      1 | 2019-06-26 00:00:00 | 2019-06-26 00:00:00 |      1 |       -2.42 |        -0.6  |
| HBSA3   |      1 | 2020-09-25 00:00:00 | 2020-09-25 00:00:00 |      1 |       -2.01 |        -0.5  |
| ELMD3   |      1 | 2021-02-17 00:00:00 | 2021-02-17 00:00:00 |      1 |       -1.8  |        -0.45 |

**Quem trouxe o retorno (soma por ativo, pp)**

| ativo   |   sum |   count |
|:--------|------:|--------:|
| SBSP3   |  6.6  |       1 |
| CSAN3   |  4.47 |       1 |
| CSMG3   |  4.14 |       1 |
| SOJA3   |  3.47 |       1 |
| SMFT3   |  2.6  |       1 |
| PRNR3   |  2.54 |       1 |
| MBLY3   |  1.91 |       1 |
| INTB3   |  1.89 |       1 |
| PGMN3   |  1.58 |       1 |
| LWSA3   |  1.41 |       1 |
