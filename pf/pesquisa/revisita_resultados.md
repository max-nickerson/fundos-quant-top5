# Frente revisita — resultados da bateria final (gerado automaticamente)

Gerado por `pf/gerar_cadernos.py` a partir de `pf/resultados/bateria/`. IR de pessoa física por `pf/ir.py` (mensal na B3 com isenção de ações ≤ R$ 20 mil/mês, anual no exterior). Ordem: nota do ranking.

### E1 Arbitragem de OPA e troca de controle (PF)  (`rev_opa`)

**Tese:** Compro no fracionário o alvo de OPA em dinheiro quando ainda negocia >= smin abaixo do preço da oferta (FR na CVM) e vendo no leilão ao preço da oferta: o prêmio de prazo/risco cobrado pelo mercado é maior que o risco real de uma OPA regulada; lote pequeno em alvo ilíquido é onde o institucional não escala

**Instrumentos:** Clear/Rico (corretagem zero): ação-alvo da OPA no fracionário/lote padrão, 1/8 do capital por OPA; habilitação no leilão via corretora; caixa em Tesouro Selic. Hedge opcional: BOVA11 vendido via aluguel (0,5% por contrato + 0,88% a.a. + B3)

**Aplicável:** True — Aplicável: compra de ação à vista em lote pequeno + venda no leilão (PF participa via corretora). Livro pequeno: em média ~1 OPA aberta (6–12% do capital); o resto rende CDI

| métrica | valor |
|---|---|
| OOS desde | 2021-01 |
| retorno OOS a.a. (R$ 20 mil) | 12.9% vs CDI 11.4% |
| ativo OOS pp (R$ 20 mil / R$ 50 mil) | +1.42 / +1.44 |
| depois do IR (classe acoes) pp, 20k / 50k | +1.40 / +1.42 |
| IR OOS / Sharpe | +0.40 / +0.40 |
| pior queda | -2.9% |
| PBO / Sharpe deflacionado | 13% / +64% |
| leque de parâmetros p5 / mediana / p95 | +0.95 / +1.19 / +1.23 |
| custo 2x / execução t+2 | +1.15 / +1.27 |
| walk-forward | +1.42 |
| sem os 10 melhores negócios | -0.35 |
| placebo p | 0.15 |
| look-ahead (truncamento) | passou |

**10 melhores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| HBOR3   |      1 | 2026-07-06 00:00:00 | 2026-10-08 00:00:00 |     67 |       50.86 |         5.59 |
| MEAL3   |      1 | 2018-12-04 00:00:00 | 2019-07-08 00:00:00 |    147 |       26.92 |         2.74 |
| BRAV3   |      1 | 2026-04-24 00:00:00 | 2026-08-05 00:00:00 |     71 |       20.99 |         2.09 |
| PRML3   |      1 | 2017-01-10 00:00:00 | 2017-07-03 00:00:00 |    118 |       19.74 |         1.59 |
| BKBR3   |      1 | 2022-08-02 00:00:00 | 2022-08-03 00:00:00 |      1 |        8.36 |         0.97 |
| KEPL3   |      1 | 2017-02-10 00:00:00 | 2017-03-30 00:00:00 |     32 |        9.95 |         0.77 |
| SEDU3   |      1 | 2019-05-08 00:00:00 | 2019-05-14 00:00:00 |      4 |        6.23 |         0.7  |
| ENBR3   |      1 | 2023-04-12 00:00:00 | 2023-07-03 00:00:00 |     55 |        7.71 |         0.56 |
| MPLU3   |      1 | 2018-10-26 00:00:00 | 2019-04-29 00:00:00 |    124 |        7.93 |         0.53 |
| CMIG4   |      1 | 2019-03-22 00:00:00 | 2019-04-11 00:00:00 |     14 |        4.93 |         0.52 |

**10 piores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| CMIG4   |      1 | 2015-12-21 00:00:00 | 2016-02-02 00:00:00 |     29 |      -12.24 |        -1.75 |
| BKBR3   |      1 | 2022-08-18 00:00:00 | 2022-11-01 00:00:00 |     51 |      -10.66 |        -1.65 |
| PRML3   |      1 | 2015-12-08 00:00:00 | 2015-12-17 00:00:00 |      7 |       -5.56 |        -0.87 |
| AALR3   |      1 | 2022-04-18 00:00:00 | 2022-07-29 00:00:00 |     72 |        4.15 |        -0.06 |
| ELPL3   |      1 | 2018-06-01 00:00:00 | 2018-06-04 00:00:00 |      1 |        0.7  |        -0.02 |
| CPRE3   |      1 | 2018-11-27 00:00:00 | 2019-10-24 00:00:00 |    230 |        7.95 |         0.03 |
| FHER3   |      1 | 2022-12-26 00:00:00 | 2023-06-27 00:00:00 |    125 |        8.2  |         0.09 |
| SRNA3   |      1 | 2025-05-15 00:00:00 | 2025-07-18 00:00:00 |     45 |        3.61 |         0.09 |
| CGAS5   |      1 | 2019-06-03 00:00:00 | 2019-08-12 00:00:00 |     49 |        4.44 |         0.09 |
| MILS3   |      1 | 2026-05-26 00:00:00 | 2026-09-23 00:00:00 |     84 |        5.91 |         0.09 |

**Quem trouxe o retorno (soma por ativo, pp)**

| ativo   |   sum |   count |
|:--------|------:|--------:|
| HBOR3   |  5.59 |       1 |
| MEAL3   |  2.74 |       1 |
| BRAV3   |  2.09 |       1 |
| KEPL3   |  0.77 |       1 |
| PRML3   |  0.72 |       2 |
| SEDU3   |  0.7  |       1 |
| ENBR3   |  0.56 |       1 |
| MPLU3   |  0.53 |       1 |
| PORT3   |  0.35 |       1 |
| ELPL3   |  0.29 |       2 |

### Debêntures PF em lotes de R$ 1 mil (carry / distressed / incentivadas isentas)  (`rev_debentures`)

**Tese:** CDI+spread paga o spread se o emissor não quebra: compro em lotes de R$ 1 mil, na prateleira das corretoras, as 5 debêntures DI de maior spread entre as líquidas (giro >= R$ 5 mi em 63 dias, PU >= 90% da curva) e seguro no mínimo 2 anos (ou até vencer) — o markup de varejo (1–3%) proíbe o giro do institucional; depois de 2 anos sai se cair fora do top 2n. Livros alternativos: distressed (comprar a 70–80% do par quem não pediu RJ, vender a 95%) e incentivadas IPCA+ isentas quando o mercado todo está largo contra a NTN-B (pós-Americanas, COVID).

**Instrumentos:** {'debêntures DI/IPCA+ (secundário)': {'onde': 'XP/BTG/Inter/Rico/Nubank (prateleira de renda fixa) ou mesa/assessor', 'lote': '1 debênture (PU ~R$ 1 mil)', 'custo': 'markup ~0,40% x duration na compra, ~0,15% x duration na venda; custódia 0'}, 'caixa': {'onde': 'Tesouro Selic / CDB liquidez diária', 'custo': '0'}}

**Aplicável:** parcial — Carry e incentivadas: rota real de varejo (prateleira das corretoras, lote de R$ 1 mil), mas o varejo paga 1–3% de markup e só vê papéis já fora do lock-up/oferta pública. Distressed: papel estressado sai da prateleira e boa parte (ICVM 476) só é negociável por investidor qualificado — rota só via mesa/assessor, com custo de 2%+ por lado.

| métrica | valor |
|---|---|
| OOS desde | 2023-01 |
| retorno OOS a.a. (R$ 20 mil) | 15.0% vs CDI 13.1% |
| ativo OOS pp (R$ 20 mil / R$ 50 mil) | +1.92 / +2.06 |
| depois do IR (classe renda_fixa) pp, 20k / 50k | +1.58 / +1.70 |
| IR OOS / Sharpe | +0.43 / +0.43 |
| pior queda | -2.1% |
| PBO / Sharpe deflacionado | 9% / +0% |
| leque de parâmetros p5 / mediana / p95 | -2.84 / +2.08 / +3.89 |
| custo 2x / execução t+2 | +1.92 / +1.85 |
| walk-forward | +2.74 |
| sem os 10 melhores negócios | +1.66 |
| placebo p | 0.01 |
| look-ahead (truncamento) | passou |

**10 melhores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| ALMC12  |      1 | 2024-10-09 00:00:00 | 2026-10-07 00:00:00 |    500 |       42.46 |         1.78 |
| GJAI12  |      1 | 2022-07-26 00:00:00 | 2024-12-02 00:00:00 |    591 |       42.67 |         1.63 |
| OCEA14  |      1 | 2024-10-15 00:00:00 | 2026-10-07 00:00:00 |    496 |       40.38 |         1.61 |
| IRJS12  |      1 | 2022-09-19 00:00:00 | 2025-07-31 00:00:00 |    718 |       52.81 |         1.6  |
| OCNP13  |      1 | 2022-05-25 00:00:00 | 2024-06-03 00:00:00 |    506 |       39.71 |         1.59 |
| VAMO22  |      1 | 2020-07-16 00:00:00 | 2022-07-22 00:00:00 |    507 |       20.83 |         1.44 |
| TIET19  |      1 | 2020-05-04 00:00:00 | 2022-05-05 00:00:00 |    504 |       18.81 |         1.44 |
| PETR36  |      1 | 2020-04-13 00:00:00 | 2022-04-20 00:00:00 |    507 |       17.61 |         1.36 |
| ELET32  |      1 | 2020-04-24 00:00:00 | 2022-05-03 00:00:00 |    507 |       17.24 |         1.25 |
| MVLV19  |      1 | 2025-07-31 00:00:00 | 2026-10-07 00:00:00 |    299 |       24.65 |         1.13 |

**10 piores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| CBRDB8  |      1 | 2024-06-03 00:00:00 | 2026-10-07 00:00:00 |    592 |        0.27 |        -4.64 |
| CBAN22  |      1 | 2020-03-13 00:00:00 | 2022-03-17 00:00:00 |    504 |        7.55 |        -0.12 |
| MOVI34  |      1 | 2022-09-14 00:00:00 | 2024-10-14 00:00:00 |    523 |       34.22 |         1.04 |
| MGLUA0  |      1 | 2024-12-03 00:00:00 | 2026-10-07 00:00:00 |    463 |       34.66 |         1.08 |
| KLAS12  |      1 | 2022-09-19 00:00:00 | 2024-10-08 00:00:00 |    516 |       34.08 |         1.08 |
| MVLV19  |      1 | 2025-07-31 00:00:00 | 2026-10-07 00:00:00 |    299 |       24.65 |         1.13 |
| ELET32  |      1 | 2020-04-24 00:00:00 | 2022-05-03 00:00:00 |    507 |       17.24 |         1.25 |
| PETR36  |      1 | 2020-04-13 00:00:00 | 2022-04-20 00:00:00 |    507 |       17.61 |         1.36 |
| TIET19  |      1 | 2020-05-04 00:00:00 | 2022-05-05 00:00:00 |    504 |       18.81 |         1.44 |
| VAMO22  |      1 | 2020-07-16 00:00:00 | 2022-07-22 00:00:00 |    507 |       20.83 |         1.44 |

**Quem trouxe o retorno (soma por ativo, pp)**

| ativo   |   sum |   count |
|:--------|------:|--------:|
| ALMC12  |  1.78 |       1 |
| GJAI12  |  1.63 |       1 |
| OCEA14  |  1.61 |       1 |
| IRJS12  |  1.6  |       1 |
| OCNP13  |  1.59 |       1 |
| VAMO22  |  1.44 |       1 |
| TIET19  |  1.44 |       1 |
| PETR36  |  1.36 |       1 |
| ELET32  |  1.25 |       1 |
| MVLV19  |  1.13 |       1 |

### E7 Rebalanceamento do Ibovespa (PF)  (`rev_rebal_ibovespa`)

**Tese:** Compro no fracionário os prováveis entrantes do Ibovespa (regra da B3 reconstruída só com dados até a data) 10 pregões antes da troca e vendo no fechamento do último pregão da carteira velha para os fundos passivos; com R$ 20–50 mil as vendas do mês ficam abaixo de R$ 20 mil e o ganho é isento de IR

**Instrumentos:** Clear/Rico/Inter (corretagem zero): entrantes prováveis no fracionário (XXXX3F, 1 ação mínima; lote de 100 no padrão), 1/15 do capital por papel; caixa em Tesouro Selic/LFTS11. Variantes de hedge: WIN (R$ 0,20 x pontos ≈ R$ 41 mil, margem em Tesouro Selic) ou BOVA11 vendido via aluguel (0,5% por contrato + 0,88% a.a. ao doador + B3 20% da taxa)

**Aplicável:** True — Aplicável: mid caps no fracionário com corretagem zero; posição média ~R$ 5 mil com R$ 20 mil; vendas por revisão < R$ 20 mil -> isento de IR. Sem hedge (WIN não cabe; BOVA11 alugado come o ativo)

| métrica | valor |
|---|---|
| OOS desde | 2021-01 |
| retorno OOS a.a. (R$ 20 mil) | 12.4% vs CDI 11.4% |
| ativo OOS pp (R$ 20 mil / R$ 50 mil) | +1.00 / +1.17 |
| depois do IR (classe acoes) pp, 20k / 50k | +0.99 / +1.15 |
| IR OOS / Sharpe | +0.42 / +0.42 |
| pior queda | -1.8% |
| PBO / Sharpe deflacionado | 13% / +31% |
| leque de parâmetros p5 / mediana / p95 | -0.35 / +0.31 / +1.13 |
| custo 2x / execução t+2 | +0.53 / +0.55 |
| walk-forward | +1.00 |
| sem os 10 melhores negócios | -0.73 |
| placebo p | 0.01 |
| look-ahead (truncamento) | passou |

**10 melhores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| IRBR3   |      1 | 2023-04-14 00:00:00 | 2023-04-28 00:00:00 |      9 |       29.45 |         1.85 |
| BEEF3   |      1 | 2020-04-16 00:00:00 | 2020-04-30 00:00:00 |      9 |       23.84 |         1.55 |
| OIBR3   |      1 | 2019-08-19 00:00:00 | 2019-08-30 00:00:00 |      9 |       19    |         1.24 |
| AMER3   |      1 | 2022-08-18 00:00:00 | 2022-08-31 00:00:00 |      9 |       19.88 |         1.23 |
| GNDI3   |      1 | 2019-08-19 00:00:00 | 2019-08-30 00:00:00 |      9 |       18.71 |         1.18 |
| BIDI11  |      1 | 2021-04-16 00:00:00 | 2021-04-30 00:00:00 |      9 |       20.95 |         1.16 |
| NATU3   |      1 | 2026-08-18 00:00:00 | 2026-08-31 00:00:00 |      9 |       16.69 |         1.05 |
| MGLU3   |      1 | 2017-12-15 00:00:00 | 2017-12-28 00:00:00 |      8 |       16.23 |         1.01 |
| SANB11  |      1 | 2017-04-13 00:00:00 | 2017-04-28 00:00:00 |      9 |       15.36 |         0.95 |
| VVAR3   |      1 | 2019-08-19 00:00:00 | 2019-08-30 00:00:00 |      9 |       14.86 |         0.95 |

**10 piores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| YDUQ3   |      1 | 2020-08-18 00:00:00 | 2020-08-31 00:00:00 |      9 |      -14.17 |        -0.98 |
| TEND3   |      1 | 2026-04-16 00:00:00 | 2026-04-30 00:00:00 |      9 |      -13.86 |        -0.97 |
| CMIN3   |      1 | 2022-04-14 00:00:00 | 2022-04-29 00:00:00 |      9 |      -10.65 |        -0.77 |
| POMO4   |      1 | 2024-12-17 00:00:00 | 2024-12-30 00:00:00 |      8 |      -10.11 |        -0.72 |
| SOMA3   |      1 | 2022-04-14 00:00:00 | 2022-04-29 00:00:00 |      9 |       -9.51 |        -0.69 |
| GOLL4   |      1 | 2018-08-20 00:00:00 | 2018-08-31 00:00:00 |      9 |       -9.3  |        -0.66 |
| PETZ3   |      1 | 2021-12-20 00:00:00 | 2021-12-30 00:00:00 |      8 |       -8.5  |        -0.62 |
| SMLE3   |      1 | 2015-04-16 00:00:00 | 2015-04-30 00:00:00 |      9 |       -7.45 |        -0.57 |
| STBP3   |      1 | 2024-08-19 00:00:00 | 2024-08-30 00:00:00 |      9 |       -7.74 |        -0.57 |
| BPAC11  |      1 | 2019-08-19 00:00:00 | 2019-08-30 00:00:00 |      9 |       -8.18 |        -0.57 |

**Quem trouxe o retorno (soma por ativo, pp)**

| ativo   |   sum |   count |
|:--------|------:|--------:|
| IRBR3   |  2.41 |       2 |
| OIBR3   |  1.72 |       2 |
| BEEF3   |  1.55 |       1 |
| AMER3   |  1.23 |       1 |
| GNDI3   |  1.18 |       1 |
| BIDI11  |  1.16 |       1 |
| NATU3   |  1.05 |       1 |
| SANB11  |  1.03 |       2 |
| MGLU3   |  1.01 |       1 |
| VVAR3   |  0.95 |       1 |

### Venda de opções B3 com garantia em Tesouro Selic (put-write / covered call)  (`rev_opcoes_b3`)

**Tese:** O brasileiro paga caro por proteção de 1 mês em BOVA11/PETR4/VALE3: vendo put ~3% OTM no bid depois de cada vencimento, com o caixa inteiro em Tesouro Selic como garantia (rende CDI), e seguro até o vencimento; filtro de IV alta (IV ATM acima da mediana dos 12 ciclos anteriores). Variante covered call (A6): ação em lote de 100 + call OTM vendida.

**Instrumentos:** [{'onde': 'B3 (Clear/Rico/XP)', 'ticker': 'opções mensais BOVA11/PETR4/VALE3 (séries BOVAxNNN, PETRxNNN, VALExNNN)', 'lote': 100, 'custo': 'bid/ask real do fechamento + 0,134% do prêmio (tarifas B3); exercício 0,03% do strike x qtd'}, {'onde': 'Tesouro Direto / B3', 'ticker': 'Tesouro Selic (LFT) como garantia', 'lote': '~R$ 170 (fração de título)', 'custo': 'rende CDI; custódia 0,20% a.a. acima de R$ 10 mil'}, {'onde': 'B3', 'ticker': 'PETR4, VALE3, BOVA11 (lote de 100 no covered call; ações recebidas no exercício)', 'lote': 100, 'custo': '0,03% emolumentos + meio spread'}, {'onde': 'B3 (BTC)', 'ticker': 'BOVA11 alugado (hedge opcional)', 'lote': 1, 'custo': '0,5% do volume por contrato novo + 0,5% a.a. renovação + 1% a.a. doador'}]

**Aplicável:** True — Sim com R$ 20 mil e R$ 50 mil: 1 put de PETR4 = 100 ações (~R$ 3–4 mil de strike), VALE3 ~R$ 6–9 mil, BOVA11 ~R$ 12–17 mil; com R$ 20 mil cabe ~1 BOVA + 1–2 PETR + 1 VALE totalmente cobertos por caixa. Garantia em Tesouro Selic rende CDI.

| métrica | valor |
|---|---|
| OOS desde | 2021-01 |
| retorno OOS a.a. (R$ 20 mil) | 12.6% vs CDI 11.4% |
| ativo OOS pp (R$ 20 mil / R$ 50 mil) | +1.13 / +1.98 |
| depois do IR (classe opcoes_b3) pp, 20k / 50k | +0.76 / +1.56 |
| IR OOS / Sharpe | +0.21 / +0.21 |
| pior queda | -8.6% |
| PBO / Sharpe deflacionado | 17% / +12% |
| leque de parâmetros p5 / mediana / p95 | +1.03 / +1.40 / +1.79 |
| custo 2x / execução t+2 | +0.63 / +0.58 |
| walk-forward | +1.13 |
| sem os 10 melhores negócios | -1.17 |
| placebo p | 0.54 |
| look-ahead (truncamento) | passou |

**10 melhores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| PETR4   |     -1 | 2020-03-18 00:00:00 | 2020-04-20 00:00:00 |     22 |       17.69 |         5.99 |
| BOVA11  |     -1 | 2020-03-18 00:00:00 | 2020-04-20 00:00:00 |     22 |        9.68 |         3.15 |
| PETR4   |     -1 | 2020-09-23 00:00:00 | 2020-10-19 00:00:00 |     17 |        5.62 |         2.84 |
| PETR4   |     -1 | 2016-03-23 00:00:00 | 2016-04-18 00:00:00 |     17 |        8.22 |         2.56 |
| PETR4   |     -1 | 2020-04-23 00:00:00 | 2020-05-18 00:00:00 |     16 |        5.3  |         2.25 |
| PETR4   |     -1 | 2014-08-20 00:00:00 | 2014-09-15 00:00:00 |     18 |        6.87 |         2.2  |
| PETR4   |     -1 | 2015-02-11 00:00:00 | 2015-03-16 00:00:00 |     21 |        6.64 |         2.1  |
| PETR4   |     -1 | 2016-01-20 00:00:00 | 2016-02-15 00:00:00 |     16 |        6.31 |         2.1  |
| PETR4   |     -1 | 2014-12-17 00:00:00 | 2015-01-19 00:00:00 |     21 |        5.59 |         1.89 |
| PETR4   |     -1 | 2016-02-17 00:00:00 | 2016-03-21 00:00:00 |     23 |        5.76 |         1.89 |

**10 piores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| PETR4   |     -1 | 2020-02-19 00:00:00 | 2020-03-16 00:00:00 |     16 |      -53.11 |       -16.23 |
| PETR4   |     -1 | 2018-05-23 00:00:00 | 2018-06-18 00:00:00 |     17 |      -28.69 |        -6.68 |
| PETR4   |     -1 | 2014-11-19 00:00:00 | 2014-12-15 00:00:00 |     18 |      -18.47 |        -5.9  |
| PETR4   |     -1 | 2014-09-17 00:00:00 | 2014-10-20 00:00:00 |     23 |      -15.19 |        -5.04 |
| VALE3   |     -1 | 2020-02-19 00:00:00 | 2020-03-16 00:00:00 |     16 |      -16.81 |        -4.44 |
| PETR4   |     -1 | 2026-05-19 00:00:00 | 2026-06-19 00:00:00 |     22 |       -8.87 |        -4.09 |
| VALE3   |     -1 | 2019-01-23 00:00:00 | 2019-02-18 00:00:00 |     18 |      -13.32 |        -3.71 |
| PETR4   |     -1 | 2021-01-20 00:00:00 | 2021-02-22 00:00:00 |     21 |       -8.54 |        -3.61 |
| VALE3   |     -1 | 2026-02-24 00:00:00 | 2026-03-20 00:00:00 |     18 |       -7.29 |        -3.2  |
| VALE3   |     -1 | 2026-06-23 00:00:00 | 2026-07-17 00:00:00 |     18 |       -5.47 |        -2.17 |

**Quem trouxe o retorno (soma por ativo, pp)**

| ativo   |   sum |   count |
|:--------|------:|--------:|
| PETR4   | 21.78 |      57 |
| BOVA11  |  6.66 |       4 |
| VALE3   | -3.79 |      31 |

### E3 Follow-on vendido (PF, aluguel real)  (`rev_followon`)

**Tese:** Vendo a descoberto (BTC de PF) a ação que anuncia oferta subsequente — emissor e acionista vendedor sabem mais e vendem caro, e a oferta adiciona papel com desconto — por 20 pregões, comprado em BOVA11 contra; o custo dominante é o aluguel real do papel

**Instrumentos:** Clear/Rico/XP/BTG: venda a descoberto via aluguel tomador (BTC), ações inteiras, 1/5 do capital por nome; garantia e produto da venda em Tesouro Selic; hedge BOVA11 comprado (cotas inteiras). Aluguel: 0,5% do volume por contrato + taxa ao doador (B3/estimada) + B3 20% da taxa

**Aplicável:** True — Aplicável operacionalmente (PF aluga e vende a descoberto na B3), mas o edge depende da taxa de aluguel dos emissores; os papéis mais lucrativos (oferta de empresa alavancada) são os de aluguel caro/indisponível

| métrica | valor |
|---|---|
| OOS desde | 2021-01 |
| retorno OOS a.a. (R$ 20 mil) | 14.7% vs CDI 11.4% |
| ativo OOS pp (R$ 20 mil / R$ 50 mil) | +3.30 / +3.55 |
| depois do IR (classe acoes) pp, 20k / 50k | +3.25 / +3.49 |
| IR OOS / Sharpe | +0.35 / +0.35 |
| pior queda | -13.6% |
| PBO / Sharpe deflacionado | 24% / +14% |
| leque de parâmetros p5 / mediana / p95 | +1.03 / +2.28 / +3.13 |
| custo 2x / execução t+2 | -4.05 / +2.15 |
| walk-forward | +3.30 |
| sem os 10 melhores negócios | -6.93 |
| placebo p | 0.00 |
| look-ahead (truncamento) | passou |

**10 melhores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| IRBR3   |     -1 | 2022-08-25 00:00:00 | 2022-09-23 00:00:00 |     20 |      -45.63 |         9.01 |
| HEDGE   |      0 | 2023-11-01 00:00:00 | 2023-11-30 00:00:00 |     21 |      nan    |         8.24 |
| VIIA3   |     -1 | 2023-09-01 00:00:00 | 2023-09-26 00:00:00 |     16 |      -41.86 |         8.21 |
| HEDGE   |      0 | 2020-07-01 00:00:00 | 2020-07-31 00:00:00 |     21 |      nan    |         7.73 |
| AZUL4   |     -1 | 2025-03-25 00:00:00 | 2025-04-24 00:00:00 |     20 |      -34.26 |         6.81 |
| BBAS3   |     -1 | 2020-02-11 00:00:00 | 2020-03-12 00:00:00 |     20 |      -38.16 |         6.09 |
| GFSA3   |     -1 | 2016-10-20 00:00:00 | 2016-11-21 00:00:00 |     20 |      -30.38 |         6    |
| HEDGE   |      0 | 2016-10-01 00:00:00 | 2016-10-31 00:00:00 |     21 |      nan    |         5.64 |
| HEDGE   |      0 | 2019-12-01 00:00:00 | 2019-12-31 00:00:00 |     21 |      nan    |         5.63 |
| OIBR4   |     -1 | 2014-04-03 00:00:00 | 2014-05-06 00:00:00 |     20 |      -27.51 |         5.32 |

**10 piores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| BRBI11  |     -1 | 2022-01-05 00:00:00 | 2022-02-02 00:00:00 |     20 |       34.21 |        -7.25 |
| PRIO3   |     -1 | 2020-12-16 00:00:00 | 2021-01-15 00:00:00 |     20 |       32.29 |        -7.09 |
| CASH3   |     -1 | 2021-06-22 00:00:00 | 2021-07-20 00:00:00 |     20 |       46.9  |        -6.11 |
| LCAM3   |     -1 | 2019-12-10 00:00:00 | 2020-01-09 00:00:00 |     20 |       29.57 |        -6.09 |
| PINE4   |     -1 | 2026-03-05 00:00:00 | 2026-04-02 00:00:00 |     20 |       25.54 |        -5.75 |
| MDNE3   |     -1 | 2026-01-14 00:00:00 | 2026-02-11 00:00:00 |     20 |       25.77 |        -5.15 |
| ELPL3   |     -1 | 2018-04-18 00:00:00 | 2018-05-17 00:00:00 |     20 |       22.27 |        -4.97 |
| HEDGE   |      0 | 2014-12-01 00:00:00 | 2014-12-31 00:00:00 |     21 |      nan    |        -4.76 |
| TRIS3   |     -1 | 2019-08-15 00:00:00 | 2019-09-12 00:00:00 |     20 |       21.42 |        -4.75 |
| CCRO3   |     -1 | 2017-01-30 00:00:00 | 2017-03-01 00:00:00 |     20 |       21.92 |        -4.45 |

**Quem trouxe o retorno (soma por ativo, pp)**

| ativo   |   sum |   count |
|:--------|------:|--------:|
| HEDGE   | 26.5  |     127 |
| GFSA3   | 11.44 |       3 |
| CVCB3   | 10.33 |       4 |
| IRBR3   |  8.62 |       3 |
| VIIA3   |  8.21 |       1 |
| BPAN4   |  7.99 |       3 |
| BBAS3   |  6.79 |       3 |
| MEAL3   |  6.4  |       2 |
| PCAR3   |  5.88 |       2 |
| COGN3   |  5.87 |       2 |

### Tesouro IPCA+ longo quando o juro real passa de 6,5% (Tesouro Direto)  (`rev_tesouro_juro_real`)

**Tese:** IPCA+6,5% numa NTN-B de 10 anos é prêmio fiscal/político extremo (o neutro do Focus é 4,3–6,3%): compro Tesouro IPCA+ ~15 anos no Tesouro Direto pagando o PU de compra e seguro até o juro real voltar a < 5,5% (ganhos de 2008, 2013, 2015–17, 2022–23 vieram de choques fiscais/políticos que se desfizeram em 6–24 meses). O resto fica em Tesouro Selic.

**Instrumentos:** {'Tesouro IPCA+ (NTN-B principal) ~15 anos': {'onde': 'Tesouro Direto (qualquer corretora; B3)', 'lote': '0,01 título, mín. R$ 30', 'custo': 'PU compra - PU venda (0,12 pp de taxa desde 2017) + custódia B3 0,20% a.a.'}, 'caixa': {'onde': 'Tesouro Selic / CDB liquidez diária 100% CDI', 'custo': '0 (Selic isento de custódia até R$ 10 mil)'}}

**Aplicável:** True — Rota 100% varejo: Tesouro Direto vende NTN-B principal de 10–25 anos em frações de 0,01; o spread de compra/venda e a custódia estão no arquivo oficial. Só não dá para alavancar (o institucional usava DAP, 1 contrato ~R$ 90 mil).

| métrica | valor |
|---|---|
| OOS desde | 2021-01 |
| retorno OOS a.a. (R$ 20 mil) | 11.3% vs CDI 11.4% |
| ativo OOS pp (R$ 20 mil / R$ 50 mil) | -0.13 / -0.13 |
| depois do IR (classe renda_fixa) pp, 20k / 50k | -0.23 / -0.23 |
| IR OOS / Sharpe | -0.01 / -0.01 |
| pior queda | -4.7% |
| PBO / Sharpe deflacionado | 37% / +20% |
| leque de parâmetros p5 / mediana / p95 | -1.32 / -0.69 / +0.03 |
| custo 2x / execução t+2 | -0.42 / -0.16 |
| walk-forward | -0.13 |
| sem os 10 melhores negócios | -0.24 |
| placebo p | 0.04 |
| look-ahead (truncamento) | passou |

**10 melhores negócios**

| ativo              |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:-------------------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| Tesouro IPCA+ 2024 |      1 | 2013-12-04 00:00:00 | 2014-09-03 00:00:00 |    187 |       24.16 |         7.43 |
| Tesouro IPCA+ 2035 |      1 | 2015-03-10 00:00:00 | 2017-02-13 00:00:00 |    486 |       58.91 |         6.47 |
| Tesouro IPCA+ 2024 |      1 | 2008-01-03 00:00:00 | 2011-09-05 00:00:00 |    924 |       74.64 |         6.27 |
| Tesouro IPCA+ 2035 |      1 | 2022-12-15 00:00:00 | 2023-06-07 00:00:00 |    119 |       17.07 |         4.36 |
| Tesouro IPCA+ 2035 |      1 | 2024-06-14 00:00:00 | 2026-10-13 00:00:00 |    586 |       23.22 |        -3.75 |

**10 piores negócios**

| ativo              |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:-------------------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| Tesouro IPCA+ 2035 |      1 | 2024-06-14 00:00:00 | 2026-10-13 00:00:00 |    586 |       23.22 |        -3.75 |
| Tesouro IPCA+ 2035 |      1 | 2022-12-15 00:00:00 | 2023-06-07 00:00:00 |    119 |       17.07 |         4.36 |
| Tesouro IPCA+ 2024 |      1 | 2008-01-03 00:00:00 | 2011-09-05 00:00:00 |    924 |       74.64 |         6.27 |
| Tesouro IPCA+ 2035 |      1 | 2015-03-10 00:00:00 | 2017-02-13 00:00:00 |    486 |       58.91 |         6.47 |
| Tesouro IPCA+ 2024 |      1 | 2013-12-04 00:00:00 | 2014-09-03 00:00:00 |    187 |       24.16 |         7.43 |

**Quem trouxe o retorno (soma por ativo, pp)**

| ativo              |   sum |   count |
|:-------------------|------:|--------:|
| Tesouro IPCA+ 2024 | 13.71 |       2 |
| Tesouro IPCA+ 2035 |  7.08 |       3 |

### Spin-offs EUA após a venda forçada (PF: IBKR com só o necessário fora)  (`rev_spinoffs`)

**Tese:** A separada é vendida por fundos de índice e gestores da controladora nas 1as semanas; compro 40 pregões depois do 1º preço na IBKR (fração), seguro 6 meses, hedge com SPY/IWM vendidos em ações inteiras; caixa no CDI.

**Instrumentos:** IBKR Pro: ações dos spin-offs (compra fracionária, US$ 0,0035/ação mín. US$ 0,35, ~R$ 1.000 por nome com R$ 20 mil); hedge: SPY e IWM vendidos em ações inteiras (aluguel 0,25–0,30% a.a.; conta margem >= US$ 2.000). Caixa em Tesouro Selic; na IBKR só o comprado + Reg T do vendido.

**Aplicável:** True — Operável: compra fracionária na IBKR resolve o lote (R$ 1–2,5 mil por nome); o hedge em ações inteiras de SPY/IWM fica grosseiro (1 SPY = R$ 3,4 mil) e exige US$ 2.000 parados para vender a descoberto; sem hedge cambial (WDO não cabe).

| métrica | valor |
|---|---|
| OOS desde | 2021-01 |
| retorno OOS a.a. (R$ 20 mil) | 8.1% vs CDI 11.4% |
| ativo OOS pp (R$ 20 mil / R$ 50 mil) | -3.34 / -1.46 |
| depois do IR (classe exterior) pp, 20k / 50k | -3.29 / -1.44 |
| IR OOS / Sharpe | -0.25 / -0.25 |
| pior queda | -15.0% |
| PBO / Sharpe deflacionado | 92% / +13% |
| leque de parâmetros p5 / mediana / p95 | -6.67 / -2.13 / +2.22 |
| custo 2x / execução t+2 | -5.74 / -2.90 |
| walk-forward | -7.39 |
| sem os 10 melhores negócios | -15.23 |
| placebo p | 0.06 |
| look-ahead (truncamento) | passou |

**10 melhores negócios**

| ativo         |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| hedge SPY+IWM |     -1 | 2008-01-02 00:00:00 | 2008-12-31 00:00:00 |    253 |      nan    |        20.76 |
| SNDK          |      1 | 2025-04-14 00:00:00 | 2025-10-14 00:00:00 |    126 |      279.4  |        13.39 |
| CLW           |      1 | 2009-02-05 00:00:00 | 2009-08-06 00:00:00 |    126 |      270.68 |        12.2  |
| VRTS          |      1 | 2009-03-04 00:00:00 | 2009-09-01 00:00:00 |    126 |      265.1  |        11.84 |
| hedge SPY+IWM |     -1 | 2022-01-03 00:00:00 | 2022-12-30 00:00:00 |    251 |      nan    |        11.42 |
| PRTA          |      1 | 2013-02-22 00:00:00 | 2013-08-22 00:00:00 |    126 |      169.71 |         9.63 |
| RHLD          |      1 | 2025-04-23 00:00:00 | 2025-10-22 00:00:00 |    126 |      201.28 |         9.46 |
| GRAL          |      1 | 2024-08-12 00:00:00 | 2025-02-12 00:00:00 |    126 |      155.43 |         7.81 |
| TREE          |      1 | 2008-10-09 00:00:00 | 2009-04-13 00:00:00 |    126 |      142.29 |         7.49 |
| CARR          |      1 | 2020-05-18 00:00:00 | 2020-11-13 00:00:00 |    126 |      119.51 |         5.91 |

**10 piores negócios**

| ativo         |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| hedge SPY+IWM |     -1 | 2019-01-02 00:00:00 | 2019-12-31 00:00:00 |    252 |         nan |       -11.2  |
| hedge SPY+IWM |     -1 | 2013-01-02 00:00:00 | 2013-12-31 00:00:00 |    252 |         nan |       -10.21 |
| hedge SPY+IWM |     -1 | 2009-01-02 00:00:00 | 2009-12-31 00:00:00 |    252 |         nan |        -7.78 |
| hedge SPY+IWM |     -1 | 2017-01-03 00:00:00 | 2017-12-29 00:00:00 |    251 |         nan |        -7.72 |
| hedge SPY+IWM |     -1 | 2024-01-02 00:00:00 | 2024-12-31 00:00:00 |    252 |         nan |        -7.35 |
| hedge SPY+IWM |     -1 | 2010-01-04 00:00:00 | 2010-12-31 00:00:00 |    252 |         nan |        -7.06 |
| hedge SPY+IWM |     -1 | 2023-01-03 00:00:00 | 2023-12-29 00:00:00 |    250 |         nan |        -6.76 |
| hedge SPY+IWM |     -1 | 2020-01-02 00:00:00 | 2020-12-31 00:00:00 |    253 |         nan |        -6.35 |
| hedge SPY+IWM |     -1 | 2014-01-02 00:00:00 | 2014-12-31 00:00:00 |    252 |         nan |        -5.99 |
| hedge SPY+IWM |     -1 | 2021-01-04 00:00:00 | 2021-12-31 00:00:00 |    252 |         nan |        -5.86 |

**Quem trouxe o retorno (soma por ativo, pp)**

| ativo   |   sum |   count |
|:--------|------:|--------:|
| SNDK    | 13.39 |       1 |
| CLW     | 12.2  |       1 |
| VRTS    | 11.84 |       1 |
| PRTA    |  9.63 |       1 |
| RHLD    |  9.46 |       1 |
| GRAL    |  7.81 |       1 |
| TREE    |  7.49 |       1 |
| CARR    |  5.91 |       1 |
| TRAX    |  5.84 |       1 |
| GEV     |  5.81 |       1 |

### Base do Futuro de Bitcoin B3 x ETF BITH11 (cash-and-carry em R$)  (`rev_base_cripto`)

**Tese:** vendo o BIT do mês e compro BITH11 quando a base anualizada do BIT paga mais que CDI + limiar; recebo a base até a rolagem, sem risco de preço; garantia em Tesouro Selic

**Instrumentos:** [{'onde': 'B3 (Clear/XP/BTG...)', 'ticker': 'BIT<mês><ano>', 'lote': '1 contrato = 0,1 BTC até 13/06/2025; 0,01 BTC desde 16/06/2025', 'custo': '~0,04% do nocional/lado + meio spread (boletim)'}, {'onde': 'B3', 'ticker': 'BITH11', 'lote': '1 cota', 'custo': 'emolumentos 0,03% + meio spread (boletim); adm 0,70% a.a. no preço'}, {'onde': 'Tesouro Direto / B3', 'ticker': 'Tesouro Selic (LFT)', 'lote': 'fração', 'custo': 'garantia, rende CDI'}]

**Aplicável:** True — tudo na B3 em R$ (BIT + BITH11 + Tesouro Selic como garantia); com 0,01 BTC por contrato desde jun/2025 cabem 2 (R$ 20 mil) a 6 (R$ 50 mil) contratos; antes disso 1 contrato (0,1 BTC) era maior que o capital

| métrica | valor |
|---|---|
| OOS desde | 2025-07 |
| retorno OOS a.a. (R$ 20 mil) | 14.5% vs CDI 14.6% |
| ativo OOS pp (R$ 20 mil / R$ 50 mil) | -0.13 / -0.12 |
| depois do IR (classe exterior) pp, 20k / 50k | -0.13 / -0.12 |
| IR OOS / Sharpe | -0.08 / -0.08 |
| pior queda | -0.7% |
| PBO / Sharpe deflacionado | 37% / +47% |
| leque de parâmetros p5 / mediana / p95 | -1.02 / -0.17 / -0.06 |
| custo 2x / execução t+2 | -0.43 / -0.41 |
| walk-forward | -0.97 |
| sem os 10 melhores negócios | -0.18 |
| placebo p | 0.00 |
| look-ahead (truncamento) | passou |

**10 melhores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| BITV26  |      1 | 2026-09-24 00:00:00 | 2026-10-13 00:00:00 |     12 |        0.08 |         0.05 |

**10 piores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| BITV26  |      1 | 2026-09-24 00:00:00 | 2026-10-13 00:00:00 |     12 |        0.08 |         0.05 |

**Quem trouxe o retorno (soma por ativo, pp)**

| ativo   |   sum |   count |
|:--------|------:|--------:|
| BITV26  |  0.05 |       1 |

### Mineradoras vs metal (PF: micro futuros de metal + ETFs na IBKR, caixa em CDI)  (`rev_mineradoras`)

**Tese:** Mineradora é opção alavancada no metal: compro a mineradora que ficou para trás do metal e vendo o metal no micro futuro (1 oz de ouro) ou no ETF (e o inverso); só a margem/Reg T vai para a IBKR, o resto fica no CDI.

**Instrumentos:** IBKR (EUA): GDX, GDXJ, SIL, COPX, FCX, VALE, BHP, RIO (ETF/ação; compra fracionária, venda em ações inteiras, Reg T, US$ 0,0035/ação mín. US$ 0,35; aluguel 0,25–0,63% a.a.); perna do metal: 1OZ (1 oz ouro, ~US$ 4,2 mil, margem ~12%, ~US$ 0,80/lado), MGC (10 oz, ~US$ 42 mil), micro prata (1.000 oz, ~US$ 56 mil), MHG (2.500 lb, ~US$ 16,5 mil) em contratos inteiros — se não couber, GLD/SLV/CPER em ações. Caixa: Tesouro Selic/CDB no Brasil; na IBKR só margem + Reg T.

**Aplicável:** True — Operável: o ouro cabe no 1OZ (1 oz) com R$ 20–50 mil; cobre (MHG) e prata (micro) não cabem em contratos inteiros e vão para CPER/SLV em ações na IBKR; GDXJ x GDX e VALE x BHP/RIO só com ações. Só margem/Reg T fora (não o capital inteiro).

| métrica | valor |
|---|---|
| OOS desde | 2021-01 |
| retorno OOS a.a. (R$ 20 mil) | -1.4% vs CDI 11.4% |
| ativo OOS pp (R$ 20 mil / R$ 50 mil) | -12.80 / -4.35 |
| depois do IR (classe exterior) pp, 20k / 50k | -12.59 / -4.27 |
| IR OOS / Sharpe | -0.53 / -0.53 |
| pior queda | -47.3% |
| PBO / Sharpe deflacionado | 18% / +4% |
| leque de parâmetros p5 / mediana / p95 | -16.86 / -15.36 / -12.02 |
| custo 2x / execução t+2 | -19.31 / -14.30 |
| walk-forward | -12.77 |
| sem os 10 melhores negócios | -18.16 |
| placebo p | 0.00 |
| look-ahead (truncamento) | passou |

**10 melhores negócios**

| ativo          |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:---------------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| GDXJ x GDX     |     -1 | 2022-06-06 00:00:00 | 2022-06-27 00:00:00 |     14 |       14.81 |         6.02 |
| GDXJ x GDX     |      1 | 2020-03-02 00:00:00 | 2020-05-25 00:00:00 |     57 |        9.2  |         4.64 |
| GDXJ x GDX     |      1 | 2014-12-15 00:00:00 | 2015-03-30 00:00:00 |     71 |       24.96 |         4.62 |
| GDXJ x GDX     |     -1 | 2019-11-11 00:00:00 | 2020-03-02 00:00:00 |     75 |        9.7  |         4.58 |
| COPX x CPER    |     -1 | 2015-04-27 00:00:00 | 2015-06-29 00:00:00 |     43 |       29.36 |         4.01 |
| SIL x SLV      |     -1 | 2019-07-22 00:00:00 | 2019-08-12 00:00:00 |     15 |       17.11 |         3.97 |
| VALE x BHP/RIO |     -1 | 2011-07-04 00:00:00 | 2011-08-08 00:00:00 |     25 |       15.77 |         3.96 |
| GDX x GLD      |     -1 | 2015-02-09 00:00:00 | 2015-03-30 00:00:00 |     33 |       22.29 |         3.76 |
| FCX x CPER     |     -1 | 2012-11-26 00:00:00 | 2012-12-10 00:00:00 |     10 |       24.2  |         3.48 |
| GDXJ x GDX     |     -1 | 2026-05-11 00:00:00 | 2026-06-08 00:00:00 |     19 |        6.73 |         3.42 |

**10 piores negócios**

| ativo          |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:---------------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| SIL x SLV      |     -1 | 2016-02-22 00:00:00 | 2016-08-11 00:00:00 |    120 |     -137.23 |       -16.56 |
| GDXJ x GDX     |     -1 | 2016-03-07 00:00:00 | 2016-08-25 00:00:00 |    120 |      -54.87 |       -16.08 |
| VALE x BHP/RIO |     -1 | 2025-09-15 00:00:00 | 2026-03-09 00:00:00 |    120 |      -43.71 |       -11.05 |
| GDXJ x GDX     |     -1 | 2010-08-02 00:00:00 | 2011-01-21 00:00:00 |    120 |      -39.93 |        -9.43 |
| COPX x CPER    |      1 | 2024-12-23 00:00:00 | 2025-05-05 00:00:00 |     88 |      -37.42 |        -9.04 |
| FCX x CPER     |      1 | 2024-12-09 00:00:00 | 2025-05-05 00:00:00 |     98 |      -43.14 |        -7.98 |
| SIL x SLV      |      1 | 2022-01-03 00:00:00 | 2022-04-04 00:00:00 |     63 |      -34.04 |        -7.82 |
| SIL x SLV      |      1 | 2025-11-10 00:00:00 | 2026-03-02 00:00:00 |     75 |      -38.12 |        -7.68 |
| GDXJ x GDX     |      1 | 2021-03-15 00:00:00 | 2021-06-21 00:00:00 |     67 |      -21.47 |        -7.16 |
| VALE x BHP/RIO |     -1 | 2020-10-13 00:00:00 | 2021-02-17 00:00:00 |     86 |      -41.1  |        -6.78 |

**Quem trouxe o retorno (soma por ativo, pp)**

| ativo          |    sum |   count |
|:---------------|-------:|--------:|
| FCX x CPER     |   2.45 |      68 |
| COPX x CPER    |  -5.85 |      71 |
| SIL x SLV      | -15.54 |      90 |
| GDXJ x GDX     | -19.28 |      50 |
| GDX x GLD      | -26.33 |      86 |
| VALE x BHP/RIO | -33.67 |      89 |

### Petróleo: PETR4/PRIO3 vs petróleo (PF: fracionário B3 + BNO/MCL na IBKR)  (`rev_petroleo`)

**Tese:** A ação de petroleira é petróleo em reais + risco da empresa: quando PETR4/PRIO3 ficam para trás do Brent x dólar, compro a ação no fracionário (isenta até R$ 20 mil de vendas/mês) e vendo petróleo (BNO na IBKR; MCL se coubesse); quando andam demais, o inverso.

**Instrumentos:** B3 (Clear/Rico/XP/BTG): PETR4 e PRIO3 no fracionário (1 ação, emolumentos 0,03% + spread), venda via aluguel BTC (0,5% do volume por contrato + 0,5–1,5% a.a. ao doador); IBKR: BNO (ETF de Brent, ~US$ 30–40/cota; vendido em cotas inteiras, Reg T 50% + mínimo US$ 2.000) ou MCL (micro WTI, 100 barris ~US$ 9,4 mil, margem ~US$ 1.625) se coubesse. Caixa em Tesouro Selic.

**Aplicável:** True — Operável no varejo: as ações cabem no fracionário (isenção de R$ 20 mil/mês) e o hedge de petróleo vai em BNO na IBKR; o MCL (R$ ~35–47 mil de nocional) é 4–10x a perna de petróleo de um par e não cabe. O custo fixo de ter conta margem na IBKR (US$ 2.000 parados para poder vender BNO) pesa muito em R$ 20 mil.

| métrica | valor |
|---|---|
| OOS desde | 2021-01 |
| retorno OOS a.a. (R$ 20 mil) | 2.8% vs CDI 11.4% |
| ativo OOS pp (R$ 20 mil / R$ 50 mil) | -8.62 / -5.06 |
| depois do IR (classe acoes) pp, 20k / 50k | -8.49 / -4.98 |
| IR OOS / Sharpe | -0.67 / -0.67 |
| pior queda | -14.3% |
| PBO / Sharpe deflacionado | 42% / +1% |
| leque de parâmetros p5 / mediana / p95 | -10.26 / -8.21 / -4.66 |
| custo 2x / execução t+2 | -13.64 / -8.82 |
| walk-forward | -7.22 |
| sem os 10 melhores negócios | -12.47 |
| placebo p | 0.20 |
| look-ahead (truncamento) | passou |

**10 melhores negócios**

| ativo         |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| PETR4 x BNO   |     -1 | 2018-01-29 00:00:00 | 2018-05-28 00:00:00 |     81 |       39.33 |         7.15 |
| PRIO3 x BNO   |      1 | 2024-05-27 00:00:00 | 2024-07-29 00:00:00 |     44 |       22.72 |         5.01 |
| PETR4 x BNO   |      1 | 2018-05-28 00:00:00 | 2018-07-23 00:00:00 |     39 |       46.33 |         4.87 |
| PETR4 x BNO   |      1 | 2019-08-19 00:00:00 | 2019-09-16 00:00:00 |     20 |       14.32 |         3.51 |
| PRIO3 x BNO   |      1 | 2020-03-23 00:00:00 | 2020-03-30 00:00:00 |      5 |       64.4  |         2.99 |
| PRIO3 x BNO   |     -1 | 2024-08-19 00:00:00 | 2024-09-09 00:00:00 |     15 |       15.02 |         2.81 |
| PETR4 x BNO   |      1 | 2013-06-24 00:00:00 | 2013-08-19 00:00:00 |     40 |       15.63 |         2.69 |
| PETR4 x BNO   |     -1 | 2025-02-24 00:00:00 | 2025-03-05 00:00:00 |      5 |        7.99 |         2.66 |
| PRIO3 x PETR4 |      1 | 2020-11-16 00:00:00 | 2020-11-23 00:00:00 |      5 |       20.38 |         2.29 |
| PETR4 x BNO   |      1 | 2017-03-20 00:00:00 | 2017-05-15 00:00:00 |     37 |       11.38 |         2.14 |

**10 piores negócios**

| ativo         |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| PRIO3 x BNO   |     -1 | 2017-08-14 00:00:00 | 2018-02-06 00:00:00 |    120 |      -99.34 |       -12.84 |
| PRIO3 x PETR4 |     -1 | 2016-12-12 00:00:00 | 2017-05-22 00:00:00 |    110 |     -102.57 |       -11.41 |
| PETR4 x BNO   |     -1 | 2023-05-15 00:00:00 | 2023-11-03 00:00:00 |    120 |      -46.96 |        -8.49 |
| PRIO3 x PETR4 |     -1 | 2017-08-14 00:00:00 | 2018-02-06 00:00:00 |    120 |      -57.34 |        -7.67 |
| PETR4 x BNO   |     -1 | 2026-08-31 00:00:00 | 2026-10-13 00:00:00 |     29 |      -22.59 |        -7.12 |
| PRIO3 x BNO   |     -1 | 2022-09-05 00:00:00 | 2023-02-27 00:00:00 |    119 |      -42.89 |        -6.58 |
| PRIO3 x BNO   |     -1 | 2020-11-23 00:00:00 | 2021-03-01 00:00:00 |     66 |      -87.8  |        -6.52 |
| PETR4 x BNO   |      1 | 2020-03-02 00:00:00 | 2020-03-09 00:00:00 |      5 |      -30.15 |        -6.44 |
| PRIO3 x BNO   |      1 | 2024-10-28 00:00:00 | 2025-03-17 00:00:00 |     94 |      -27.63 |        -5.66 |
| PETR4 x BNO   |      1 | 2011-03-21 00:00:00 | 2011-08-08 00:00:00 |     97 |      -19.41 |        -5.37 |

**Quem trouxe o retorno (soma por ativo, pp)**

| ativo         |    sum |   count |
|:--------------|-------:|--------:|
| PETR4 x BNO   | -11.88 |      41 |
| PRIO3 x BNO   | -25.84 |      25 |
| PRIO3 x PETR4 | -26.77 |      24 |

### Base WIN x BOVA11 no vencimento (caixa sintético)  (`rev_base_ind`)

**Tese:** Nos últimos pregões antes do vencimento, se a taxa implícita do índice futuro contra o Ibovespa passa do CDI + limiar, compro BOVA11 e vendo WIN do 1º vencimento e travo a taxa até a liquidação (média do Ibovespa das 3 últimas horas).

**Instrumentos:** [{'onde': 'B3 (Clear/Rico)', 'ticker': 'WIN (1º vencimento, meses pares)', 'lote': '1 contrato = R$ 0,20 x pontos (R$ 20–42 mil)', 'custo': 'R$ 0,39 por contrato + R$ 0,30 na liquidação; margem em BOVA11/Tesouro Selic'}, {'onde': 'B3', 'ticker': 'BOVA11 (e BOVA11F)', 'lote': 1, 'custo': '0,03% + meio spread (~0,03%) por lado; aluguel 0,5% + 0,4% a.a. no reverso'}]

**Aplicável:** R$ 20 mil: só em parte de 2019–2020 (1 WIN > patrimônio desde 2021); R$ 50 mil: sim (1 WIN) — 1 WIN = 0,2 x Ibovespa: R$ 20 mil em 2019 e ~R$ 34–42 mil em 2025–26. Contra 1 WIN é preciso ter o mesmo nocional em BOVA11 comprado com caixa (ou emprestado). Com R$ 20 mil o fundo fica parado (CDI) quase todo o tempo; com R$ 50 mil opera 1 WIN.

| métrica | valor |
|---|---|
| OOS desde | 2023-01 |
| retorno OOS a.a. (R$ 20 mil) | 12.9% vs CDI 13.1% |
| ativo OOS pp (R$ 20 mil / R$ 50 mil) | -0.17 / -0.20 |
| depois do IR (classe futuros_b3) pp, 20k / 50k | -0.17 / -0.19 |
| IR OOS / Sharpe | -3518534773078932.50 / -3518534773078932.50 |
| pior queda | 0.0% |
| PBO / Sharpe deflacionado | 50% / +0% |
| leque de parâmetros p5 / mediana / p95 | -0.17 / -0.17 / -0.17 |
| custo 2x / execução t+2 | -0.17 / -0.17 |
| walk-forward | -0.17 |
| sem os 10 melhores negócios | -0.17 |
| placebo p | 0.91 |
| look-ahead (truncamento) | passou |

**10 melhores negócios**

| ativo         |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| BOVA11/WING19 |      1 | 2019-01-31 00:00:00 | 2019-02-13 00:00:00 |      9 |       -0.27 |        -0.26 |

**10 piores negócios**

| ativo         |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| BOVA11/WING19 |      1 | 2019-01-31 00:00:00 | 2019-02-13 00:00:00 |      9 |       -0.27 |        -0.26 |

**Quem trouxe o retorno (soma por ativo, pp)**

| ativo         |   sum |   count |
|:--------------|------:|--------:|
| BOVA11/WING19 | -0.26 |       1 |

### Carry de moedas PF (micro FX CME + WDO)  (`rev_carry_moedas`)

**Tese:** Fim de mês: comprado na moeda de maior carry e vendido na de menor entre as que têm futuro de varejo (micro FX CME na IBKR, real via WDO), sem comprar moeda de juro real negativo; contratos inteiros, garantia B3 em Tesouro Selic, só margem na IBKR

**Instrumentos:** IBKR/CME (conta margem, mín. US$ 2.000): M6E € 12.500, M6B £ 6.250, M6A A$ 10.000, MCD C$ 10.000, MSF CHF 12.500, MJY ¥ 1,25 mi; margem manutenção US$ 80–360/contrato; custo ~US$ 1,6/lado (comissão 0,25 + taxas 0,26 + 1 tick). B3 (Clear/Rico): WDO US$ 10 mil, garantia em Tesouro Selic, R$ 3,70/lado, rolagem mensal. Variante: MEX/AFS (B3, US$ 10 mil, acesso de varejo não confirmado). Caixa em Tesouro Selic; na IBKR só max(US$ 2 mil, 1,5x margem), excedente em SGOV.

**Aplicável:** True — opera de verdade com R$ 20–50 mil (1–2 contratos por perna, margem < US$ 1 mil), mas cada contrato é 1,4–3x o capital: o livro é um par concentrado (tipicamente vendido WDO x vendido MJY = BRL/JPY), vol 15–35% do capital, não o carry diversificado

| métrica | valor |
|---|---|
| OOS desde | 2021-01 |
| retorno OOS a.a. (R$ 20 mil) | 22.8% vs CDI 11.4% |
| ativo OOS pp (R$ 20 mil / R$ 50 mil) | +11.38 / +8.64 |
| depois do IR (classe futuros_b3) pp, 20k / 50k | +10.41 / +7.82 |
| IR OOS / Sharpe | +0.46 / +0.46 |
| pior queda | -49.6% |
| PBO / Sharpe deflacionado | 18% / +60% |
| leque de parâmetros p5 / mediana / p95 | +0.36 / +11.39 / +18.51 |
| custo 2x / execução t+2 | +8.04 / +10.65 |
| walk-forward | +27.68 |
| sem os 10 melhores negócios | -6.37 |
| placebo p | 0.38 |
| look-ahead (truncamento) | passou |

**10 melhores negócios**

| ativo      |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:-----------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| WDO        |      1 | 2025-07-01 00:00:00 | 2026-10-13 00:00:00 |    325 |       21.38 |        53.67 |
| MSF        |     -1 | 2015-05-04 00:00:00 | 2022-10-03 00:00:00 |   1863 |       15.11 |        46.01 |
| MJY        |     -1 | 2022-10-03 00:00:00 | 2025-04-01 00:00:00 |    625 |       13.8  |        31.57 |
| MSF        |     -1 | 2025-08-01 00:00:00 | 2026-10-13 00:00:00 |    302 |        6.41 |        26.52 |
| WDO        |      1 | 2016-01-04 00:00:00 | 2020-03-02 00:00:00 |   1043 |        9.72 |        23.18 |
| conta IBKR |      1 | 2020-01-02 00:00:00 | 2020-12-31 00:00:00 |    251 |      nan    |         8.92 |
| M6E        |     -1 | 2014-10-01 00:00:00 | 2015-01-02 00:00:00 |     65 |        4.26 |         8.65 |
| conta IBKR |      1 | 2024-01-02 00:00:00 | 2024-12-31 00:00:00 |    253 |      nan    |         8.59 |
| conta IBKR |      1 | 2015-01-02 00:00:00 | 2015-12-31 00:00:00 |    250 |      nan    |         5.12 |
| conta IBKR |      1 | 2018-01-02 00:00:00 | 2018-12-31 00:00:00 |    250 |      nan    |         2.81 |

**10 piores negócios**

| ativo      |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:-----------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| MSF        |     -1 | 2025-02-03 00:00:00 | 2025-05-02 00:00:00 |     59 |       -8.93 |       -37.28 |
| conta IBKR |      1 | 2025-01-02 00:00:00 | 2025-12-31 00:00:00 |    252 |      nan    |       -13.51 |
| conta IBKR |      1 | 2016-01-04 00:00:00 | 2016-12-30 00:00:00 |    251 |      nan    |       -12.97 |
| MSF        |     -1 | 2015-01-02 00:00:00 | 2015-02-02 00:00:00 |     21 |      -10.94 |       -12.79 |
| conta IBKR |      1 | 2022-01-03 00:00:00 | 2022-12-30 00:00:00 |    251 |      nan    |       -11    |
| conta IBKR |      1 | 2026-01-02 00:00:00 | 2026-10-13 00:00:00 |    195 |      nan    |       -10.89 |
| conta IBKR |      1 | 2023-01-02 00:00:00 | 2023-12-29 00:00:00 |    249 |      nan    |        -9.68 |
| conta IBKR |      1 | 2017-01-02 00:00:00 | 2017-12-29 00:00:00 |    249 |      nan    |        -3.24 |
| conta IBKR |      1 | 2010-01-04 00:00:00 | 2010-12-31 00:00:00 |    251 |      nan    |        -3.18 |
| conta IBKR |      1 | 2019-01-02 00:00:00 | 2019-12-31 00:00:00 |    253 |      nan    |        -1.19 |

**Quem trouxe o retorno (soma por ativo, pp)**

| ativo      |    sum |   count |
|:-----------|-------:|--------:|
| WDO        |  79.99 |       5 |
| MJY        |  31.57 |       1 |
| MSF        |  22.45 |       4 |
| M6E        |   8.65 |       1 |
| conta IBKR | -41.14 |      17 |

### E9 Crise corporativa — continuação vendida (PF, aluguel real)  (`rev_crise`)

**Tese:** Vendo a descoberto (BTC de PF) a ação que caiu > 20% em 3 pregões com fato na CVM: a notícia ruim é digerida devagar (institucional vende aos poucos, varejo compra a 'promoção'), por 20 pregões, comprado em BOVA11 contra; o custo é o aluguel caro dos papéis em crise

**Instrumentos:** Clear/Rico/XP/BTG: venda a descoberto via aluguel tomador (BTC), ações inteiras, 1/10 do capital por nome; garantia e produto da venda em Tesouro Selic; hedge BOVA11 comprado. Modo contrarian (grade): compra à vista no fracionário

**Aplicável:** True — Aplicável operacionalmente, mas só nos papéis em crise que ainda têm doador; a taxa real desses papéis é de 5–50% a.a. (B3) e a corretora cobra 0,5% por contrato

| métrica | valor |
|---|---|
| OOS desde | 2021-01 |
| retorno OOS a.a. (R$ 20 mil) | 11.9% vs CDI 11.4% |
| ativo OOS pp (R$ 20 mil / R$ 50 mil) | +0.47 / +0.61 |
| depois do IR (classe acoes) pp, 20k / 50k | +0.47 / +0.60 |
| IR OOS / Sharpe | +0.10 / +0.10 |
| pior queda | -23.1% |
| PBO / Sharpe deflacionado | 44% / +7% |
| leque de parâmetros p5 / mediana / p95 | -12.49 / -8.83 / +0.63 |
| custo 2x / execução t+2 | -5.26 / +1.04 |
| walk-forward | +0.47 |
| sem os 10 melhores negócios | -7.38 |
| placebo p | 0.04 |
| look-ahead (truncamento) | FALHOU |

**10 melhores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| HEDGE   |      0 | 2020-04-01 00:00:00 | 2020-04-30 00:00:00 |     21 |      nan    |        17.55 |
| AMBP3   |     -1 | 2025-09-25 00:00:00 | 2025-10-23 00:00:00 |     20 |      -85.81 |         8.49 |
| IRBR3   |     -1 | 2020-02-11 00:00:00 | 2020-03-12 00:00:00 |     20 |      -73.59 |         7.15 |
| AMER3   |     -1 | 2023-01-13 00:00:00 | 2023-02-10 00:00:00 |     20 |      -65.08 |         6.43 |
| AZUL4   |     -1 | 2025-04-25 00:00:00 | 2025-05-26 00:00:00 |     20 |      -44.1  |         4.32 |
| PCAR3   |     -1 | 2023-08-24 00:00:00 | 2023-09-22 00:00:00 |     20 |      -44.34 |         4.29 |
| BMGB4   |     -1 | 2020-02-19 00:00:00 | 2020-03-20 00:00:00 |     20 |      -44    |         4.27 |
| FJTA3   |     -1 | 2018-11-05 00:00:00 | 2018-12-04 00:00:00 |     20 |      -44.72 |         4.21 |
| OIBR3   |     -1 | 2018-11-16 00:00:00 | 2018-12-14 00:00:00 |     20 |      -41.36 |         4.03 |
| HEDGE   |      0 | 2022-03-01 00:00:00 | 2022-03-31 00:00:00 |     21 |      nan    |         3.98 |

**10 piores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| HEDGE   |      0 | 2020-03-01 00:00:00 | 2020-03-31 00:00:00 |     21 |      nan    |       -14.35 |
| OIBR4   |     -1 | 2016-06-20 00:00:00 | 2016-07-18 00:00:00 |     20 |      138.38 |       -14.21 |
| OIBR3   |     -1 | 2016-06-15 00:00:00 | 2016-07-13 00:00:00 |     20 |      125.17 |       -12.82 |
| LIGT3   |     -1 | 2023-04-06 00:00:00 | 2023-05-09 00:00:00 |     20 |      107.18 |       -10.98 |
| TRAD3   |     -1 | 2021-10-26 00:00:00 | 2021-11-25 00:00:00 |     20 |       53.99 |        -5.62 |
| FJTA4   |     -1 | 2018-12-21 00:00:00 | 2019-01-22 00:00:00 |     20 |       52.47 |        -5.52 |
| AZUL4   |     -1 | 2023-02-13 00:00:00 | 2023-03-15 00:00:00 |     20 |       53.26 |        -5.39 |
| PCAR3   |     -1 | 2021-03-02 00:00:00 | 2021-03-30 00:00:00 |     20 |       49.43 |        -5.29 |
| MLAS3   |     -1 | 2023-03-30 00:00:00 | 2023-05-02 00:00:00 |     20 |       49.29 |        -5.27 |
| LUPA3   |     -1 | 2021-04-05 00:00:00 | 2021-05-04 00:00:00 |     20 |       47.11 |        -5.04 |

**Quem trouxe o retorno (soma por ativo, pp)**

| ativo   |   sum |   count |
|:--------|------:|--------:|
| HEDGE   | 14.47 |     129 |
| GFSA3   | 12.23 |       7 |
| AMBP3   | 10.7  |       2 |
| IRBR3   | 10.58 |       4 |
| AMER3   |  7.98 |       3 |
| ONCO3   |  5.64 |       8 |
| RCSL4   |  5.02 |       3 |
| SEQL3   |  4.84 |       6 |
| BMGB4   |  4.27 |       1 |
| MEAL3   |  3.94 |       1 |

### PEAD B3 em lote pequeno (deriva pós-resultado)  (`rev_pead`)

**Tese:** Compro (no fracionário) a ação que reagiu >= 8% contra o BOVA11 nos 2 pregões em torno da entrega do ITR/DFP (e vendo alugado a líquida que caiu >= 8%) e seguro 60 pregões: o mercado sub-reage e a deriva continua; com R$ 2 mil por papel entro em small/mid caps que o institucional não pega, e com vendas <= R$ 20 mil/mês o ganho do comprado é isento. Hedge: WIN inteiro contra o líquido.

**Instrumentos:** [{'onde': 'B3 (Clear/Rico/XP/Inter/Nubank)', 'ticker': 'ações (lote padrão + fracionário F)', 'lote': 1, 'custo': '0,03% + meio spread real do fechamento (+0,2% na parte fracionária)'}, {'onde': 'B3 (BTC)', 'ticker': 'ação alugada (variante ambos)', 'lote': 1, 'custo': '0,5% do volume ao abrir + 1–8% a.a. ao doador'}, {'onde': 'B3', 'ticker': 'WIN (hedge opcional)', 'lote': '1 contrato = 0,2 x Ibovespa', 'custo': 'R$ 0,39 por contrato'}]

**Aplicável:** True — Sim: ações no fracionário a partir de 1 ação; R$ 2 mil por posição com R$ 20 mil (R$ 5 mil com R$ 50 mil). Vendido só em papel líquido com aluguel. Hedge com WIN só faz sentido com R$ 50 mil (1 WIN ~ R$ 35 mil).

| métrica | valor |
|---|---|
| OOS desde | 2021-01 |
| retorno OOS a.a. (R$ 20 mil) | 19.0% vs CDI 11.4% |
| ativo OOS pp (R$ 20 mil / R$ 50 mil) | +7.52 / +7.68 |
| depois do IR (classe acoes) pp, 20k / 50k | +7.40 / +7.56 |
| IR OOS / Sharpe | +0.51 / +0.51 |
| pior queda | -17.1% |
| PBO / Sharpe deflacionado | 16% / +7% |
| leque de parâmetros p5 / mediana / p95 | -0.43 / +5.05 / +13.39 |
| custo 2x / execução t+2 | +4.20 / +6.68 |
| walk-forward | +4.92 |
| sem os 10 melhores negócios | -3.81 |
| placebo p | 0.00 |
| look-ahead (truncamento) | passou |

**10 melhores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| ETER3   |      1 | 2021-03-04 00:00:00 | 2021-05-31 00:00:00 |     60 |      138.24 |        13.58 |
| BIDI11  |      1 | 2020-11-16 00:00:00 | 2021-02-10 00:00:00 |     60 |      120.45 |        11.74 |
| PRIO3   |      1 | 2020-11-20 00:00:00 | 2021-02-18 00:00:00 |     60 |      104.61 |        10.24 |
| MRFG3   |      1 | 2025-02-28 00:00:00 | 2025-05-30 00:00:00 |     60 |       86.43 |         8.09 |
| GOLL4   |      1 | 2016-05-13 00:00:00 | 2016-08-08 00:00:00 |     60 |       81.82 |         7.74 |
| CEAB3   |      1 | 2025-02-28 00:00:00 | 2025-05-30 00:00:00 |     60 |       81.17 |         7.63 |
| MGLU3   |      1 | 2016-08-05 00:00:00 | 2016-11-01 00:00:00 |     60 |       73.77 |         6.71 |
| CEAB3   |      1 | 2023-03-03 00:00:00 | 2023-05-31 00:00:00 |     60 |       69.12 |         6.49 |
| CMIN3   |      1 | 2022-11-03 00:00:00 | 2023-01-27 00:00:00 |     60 |       64.35 |         5.99 |
| GOLL4   |     -1 | 2023-11-08 00:00:00 | 2024-02-05 00:00:00 |     60 |       51.3  |         5.28 |

**10 piores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| LIGT3   |     -1 | 2023-05-15 00:00:00 | 2023-08-08 00:00:00 |     60 |      -88.17 |        -8.51 |
| AZZA3   |     -1 | 2025-03-13 00:00:00 | 2025-06-10 00:00:00 |     60 |      -78.54 |        -7.56 |
| AZUL4   |      1 | 2025-02-26 00:00:00 | 2025-05-28 00:00:00 |     60 |      -72.75 |        -7.52 |
| PDGR3   |      1 | 2018-11-19 00:00:00 | 2019-02-13 00:00:00 |     60 |      -57.42 |        -5.93 |
| MGLU3   |      1 | 2015-08-03 00:00:00 | 2015-10-28 00:00:00 |     60 |      -55.49 |        -5.82 |
| LREN3   |     -1 | 2025-02-24 00:00:00 | 2025-05-26 00:00:00 |     60 |      -60.75 |        -5.8  |
| CSNA3   |     -1 | 2015-08-17 00:00:00 | 2015-11-12 00:00:00 |     60 |      -56.65 |        -5.45 |
| CBAV3   |     -1 | 2025-08-08 00:00:00 | 2025-10-31 00:00:00 |     60 |      -48.29 |        -4.63 |
| ALLD3   |      1 | 2021-08-12 00:00:00 | 2021-11-09 00:00:00 |     60 |      -42.12 |        -4.35 |
| RRRP3   |     -1 | 2022-02-24 00:00:00 | 2022-05-25 00:00:00 |     60 |      -45.31 |        -4.31 |

**Quem trouxe o retorno (soma por ativo, pp)**

| ativo   |   sum |   count |
|:--------|------:|--------:|
| GOLL4   | 16.7  |       6 |
| BIDI11  | 15.08 |       2 |
| CEAB3   | 13.51 |       3 |
| ETER3   | 12.99 |       4 |
| PRIO3   | 11.25 |       2 |
| MRFG3   | 10.01 |       3 |
| TGMA3   |  9.85 |       3 |
| VLID3   |  8.62 |       4 |
| FIBR3   |  7.94 |       4 |
| MILS3   |  7.3  |       3 |

### Prêmio de vol PF (VXM vendido, só margem na IBKR)  (`rev_variancia`)

**Tese:** Vende 1+ Mini VIX (VXM) do 1º vencimento na rolagem quando há contango (sai se virar backwardation); caixa em CDI, só a margem (alta: US$ 2,8 mil por VXM vendido) na IBKR; contratos inteiros com teto de perda num choque tipo fev/2018

**Instrumentos:** IBKR (conta margem, mín. US$ 2.000): VENDER VXM (Cboe CFE, US$ 100 x VIX, ~US$ 1,5–2 mil de nocional), 1º vencimento, rolagem mensal 5 dias antes; margem IBKR p/ vendido overnight US$ 2.767 inicial / 2.406 manutenção; custo ~US$ 5,50/lado. Sem hedge de beta (MES US$ 5 x S&P ~ US$ 33 mil não cabe); filtro de contango (sai em backwardation). Caixa em Tesouro Selic. Variante: SVXY comprado em conta cash (frações), só o valor da posição lá fora.

**Aplicável:** False — opera (1 VXM), mas não preserva o edge: a margem de VXM VENDIDO na IBKR (~US$ 2,8 mil) prende 76–85% do capital fora do CDI e no dólar; sem hedge de beta; o futuro de VIX vendido rende ~+1 pp a.a. no OOS mesmo em escala (o prêmio do IAC4 é do swap de variância)

| métrica | valor |
|---|---|
| OOS desde | 2021-01 |
| retorno OOS a.a. (R$ 20 mil) | -1.6% vs CDI 11.4% |
| ativo OOS pp (R$ 20 mil / R$ 50 mil) | -13.01 / -10.00 |
| depois do IR (classe exterior) pp, 20k / 50k | -12.90 / -9.85 |
| IR OOS / Sharpe | -0.82 / -0.82 |
| pior queda | -30.5% |
| PBO / Sharpe deflacionado | 63% / +0% |
| leque de parâmetros p5 / mediana / p95 | -23.35 / -14.37 / +0.58 |
| custo 2x / execução t+2 | -16.84 / -12.66 |
| walk-forward | -3.86 |
| sem os 10 melhores negócios | -22.58 |
| placebo p | 0.96 |
| look-ahead (truncamento) | passou |

**10 melhores negócios**

| ativo      |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:-----------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| conta IBKR |      1 | 2020-01-02 00:00:00 | 2020-12-31 00:00:00 |    251 |      nan    |        27.89 |
| conta IBKR |      1 | 2015-01-02 00:00:00 | 2015-12-31 00:00:00 |    250 |      nan    |        18.7  |
| conta IBKR |      1 | 2008-01-02 00:00:00 | 2008-12-31 00:00:00 |    254 |      nan    |        16.66 |
| conta IBKR |      1 | 2024-01-02 00:00:00 | 2024-12-31 00:00:00 |    253 |      nan    |        14.71 |
| VXM        |     -1 | 2009-04-08 00:00:00 | 2009-05-12 00:00:00 |     23 |       23.1  |        10.22 |
| VXM        |     -1 | 2016-03-09 00:00:00 | 2016-04-13 00:00:00 |     24 |       26.34 |         9.39 |
| conta IBKR |      1 | 2018-01-02 00:00:00 | 2018-12-31 00:00:00 |    250 |      nan    |         9.3  |
| VXM        |     -1 | 2023-11-08 00:00:00 | 2023-12-13 00:00:00 |     24 |       24.07 |         9.21 |
| VXM        |     -1 | 2012-06-13 00:00:00 | 2012-07-11 00:00:00 |     19 |       31.59 |         8.52 |
| VXM        |     -1 | 2023-08-09 00:00:00 | 2023-09-13 00:00:00 |     24 |       20.41 |         8.48 |

**10 piores negócios**

| ativo      |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:-----------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| conta IBKR |      1 | 2009-01-02 00:00:00 | 2009-12-31 00:00:00 |    250 |      nan    |       -34.83 |
| conta IBKR |      1 | 2016-01-04 00:00:00 | 2016-12-30 00:00:00 |    251 |      nan    |       -25.45 |
| conta IBKR |      1 | 2025-01-02 00:00:00 | 2025-12-31 00:00:00 |    252 |      nan    |       -24.59 |
| conta IBKR |      1 | 2026-01-02 00:00:00 | 2026-10-13 00:00:00 |    195 |      nan    |       -20.62 |
| conta IBKR |      1 | 2023-01-02 00:00:00 | 2023-12-29 00:00:00 |    249 |      nan    |       -20.58 |
| conta IBKR |      1 | 2022-01-03 00:00:00 | 2022-12-30 00:00:00 |    251 |      nan    |       -18.66 |
| conta IBKR |      1 | 2010-01-04 00:00:00 | 2010-12-31 00:00:00 |    251 |      nan    |       -13.14 |
| VXM        |     -1 | 2020-02-12 00:00:00 | 2020-02-24 00:00:00 |      7 |      -31    |       -10.55 |
| VXM        |     -1 | 2017-03-15 00:00:00 | 2017-04-12 00:00:00 |     20 |      -18.58 |        -8.41 |
| VXM        |     -1 | 2015-08-12 00:00:00 | 2015-08-21 00:00:00 |      7 |      -30.28 |        -8.15 |

**Quem trouxe o retorno (soma por ativo, pp)**

| ativo      |    sum |   count |
|:-----------|-------:|--------:|
| VXM        |  85.64 |     148 |
| conta IBKR | -73.25 |      19 |
