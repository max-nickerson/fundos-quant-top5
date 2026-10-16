# Frente pf2_leilao_global — resultados da bateria final (gerado automaticamente)

Gerado por `pf/gerar_cadernos.py` a partir de `pf/resultados/bateria/`. IR de pessoa física por `pf/ir.py` (mensal na B3 com isenção de ações ≤ R$ 20 mil/mês, anual no exterior). Ordem: nota do ranking.

### Noite após ALTA forte (vendido) ou após GAP de baixa (comprado) — ETFs/S&P 100 (IBKR)  (`lg_alta_gap`)

**Tese:** Vendo no MOC o que subiu forte no dia e recompro no MOO (espelho da compra forçada), ou compro no MOC o que abriu com gap de baixa e não recuperou (vendedor atrasado) e vendo no MOO

**Instrumentos:** [{'onde': 'IBKR (NYSE/Nasdaq)', 'ticker': 'SPY/QQQ/XL*/... e S&P 100', 'lote': '1 ação', 'custo': 'US$ 0,0035/ação mín. US$ 0,35 + 1 bp; vendido: aluguel ~0,3% a.a. por 1 dia; margem 1 dia'}]

**Aplicável:** True — MOC/MOO na IBKR; venda a descoberto só em papel 'easy to borrow' (todos os ETFs e S&P 100); regra de uptick não se aplica na alta

| métrica | valor |
|---|---|
| OOS desde | 2021-01 |
| retorno OOS a.a. (R$ 20 mil) | 5.0% vs CDI 11.4% |
| ativo OOS pp (R$ 20 mil / R$ 50 mil) | -6.47 / -4.48 |
| depois do IR (classe exterior) pp, 20k / 50k | -6.84 / -4.96 |
| IR OOS / Sharpe | -0.58 / -0.58 |
| pior queda | -16.5% |
| PBO / Sharpe deflacionado | 4% / +0% |
| leque de parâmetros p5 / mediana / p95 | -9.21 / -8.48 / -3.50 |
| custo 2x / execução t+2 | -8.34 / -3.57 |
| walk-forward | -6.47 |
| sem os 10 melhores negócios | -9.37 |
| placebo p | 0.33 |
| look-ahead (truncamento) | passou |

**10 melhores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| XOP     |      1 | 2020-03-09 00:00:00 | 2020-03-10 00:00:00 |      1 |       28.14 |         9.35 |
| OIH     |      1 | 2020-03-12 00:00:00 | 2020-03-13 00:00:00 |      1 |       10.42 |         3.46 |
| KRE     |      1 | 2023-03-13 00:00:00 | 2023-03-14 00:00:00 |      1 |       10.52 |         3.43 |
| XRT     |      1 | 2021-01-28 00:00:00 | 2021-01-29 00:00:00 |      1 |       10.53 |         3.32 |
| OIH     |      1 | 2020-03-09 00:00:00 | 2020-03-10 00:00:00 |      1 |        9.97 |         3.29 |
| XOP     |      1 | 2020-03-12 00:00:00 | 2020-03-13 00:00:00 |      1 |        9.15 |         3.02 |
| XLE     |      1 | 2020-03-09 00:00:00 | 2020-03-10 00:00:00 |      1 |        7.97 |         2.63 |
| XLE     |      1 | 2020-03-23 00:00:00 | 2020-03-24 00:00:00 |      1 |        7.68 |         2.55 |
| XOP     |      1 | 2016-11-29 00:00:00 | 2016-11-30 00:00:00 |      1 |        7.58 |         2.52 |
| OIH     |      1 | 2020-06-11 00:00:00 | 2020-06-12 00:00:00 |      1 |        8.14 |         2.52 |

**10 piores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| XOP     |      1 | 2020-03-06 00:00:00 | 2020-03-09 00:00:00 |      1 |      -24.31 |        -7.88 |
| KRE     |      1 | 2023-03-10 00:00:00 | 2023-03-13 00:00:00 |      1 |      -12.64 |        -4.15 |
| XOP     |      1 | 2020-03-11 00:00:00 | 2020-03-12 00:00:00 |      1 |      -11.66 |        -3.86 |
| XLF     |      1 | 2020-03-06 00:00:00 | 2020-03-09 00:00:00 |      1 |      -10.05 |        -3.34 |
| OIH     |      1 | 2020-03-11 00:00:00 | 2020-03-12 00:00:00 |      1 |       -9.67 |        -3.18 |
| KRE     |      1 | 2020-03-06 00:00:00 | 2020-03-09 00:00:00 |      1 |       -9.44 |        -3.08 |
| KRE     |      1 | 2020-03-11 00:00:00 | 2020-03-12 00:00:00 |      1 |       -8.22 |        -2.7  |
| GDX     |      1 | 2026-03-18 00:00:00 | 2026-03-19 00:00:00 |      1 |       -8.31 |        -2.67 |
| SMH     |      1 | 2024-08-02 00:00:00 | 2024-08-05 00:00:00 |      1 |       -8.07 |        -2.53 |
| GDX     |      1 | 2013-04-12 00:00:00 | 2013-04-15 00:00:00 |      1 |       -6.19 |        -2.05 |

**Quem trouxe o retorno (soma por ativo, pp)**

| ativo   |   sum |   count |
|:--------|------:|--------:|
| GDX     | 11.56 |     179 |
| SMH     | 10.19 |      71 |
| XOP     |  8.93 |     108 |
| XME     |  7.52 |      60 |
| OIH     |  7.02 |     117 |
| XLE     |  4.87 |      49 |
| XLK     |  4.7  |      24 |
| XRT     |  3.56 |      16 |
| QQQ     |  1.71 |      10 |
| XBI     |  1.51 |      18 |

### Noite após queda forte — Japão/Hong Kong (IBKR) ou ETFs de país  (`lg_asia`)

**Tese:** Compro no leilão de fechamento de Tóquio/HK as large caps que caíram forte (margem de varejo 'shinyo', Southbound) e vendo no leilão de abertura; Coreia/Taiwan só como diagnóstico (inacessíveis para PF brasileira)

**Instrumentos:** [{'onde': 'IBKR (TSE, SEHK)', 'ticker': 'large caps do Nikkei/Hang Seng (ou EWJ/EWH/... em NY)', 'lote': '100 ações (Japão); lote do papel (HK)', 'custo': '0,08% mín. JPY 80/HKD 18; HK stamp 0,1%/lado; 1 bp; margem 1 dia'}]

**Aplicável:** True — MOC de Tóquio às 3h25 de Brasília e de HK às 5h: só com ordem programada pela API da IBKR (decide com o preço indicativo do call); Coreia/Taiwan não são acessíveis

| métrica | valor |
|---|---|
| OOS desde | 2021-01 |
| retorno OOS a.a. (R$ 20 mil) | 3.1% vs CDI 11.4% |
| ativo OOS pp (R$ 20 mil / R$ 50 mil) | -8.30 / -7.09 |
| depois do IR (classe exterior) pp, 20k / 50k | -8.20 / -7.02 |
| IR OOS / Sharpe | -0.74 / -0.74 |
| pior queda | -18.3% |
| PBO / Sharpe deflacionado | 0% / +0% |
| leque de parâmetros p5 / mediana / p95 | -8.62 / -6.28 / -1.35 |
| custo 2x / execução t+2 | -8.80 / -6.94 |
| walk-forward | -8.20 |
| sem os 10 melhores negócios | -12.31 |
| placebo p | 0.36 |
| look-ahead (truncamento) | passou |

**10 melhores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| EWA     |      1 | 2020-03-12 00:00:00 | 2020-03-13 00:00:00 |      1 |       13.75 |         6.85 |
| EWA     |      1 | 2015-08-24 00:00:00 | 2015-08-25 00:00:00 |      1 |       10.2  |         5.09 |
| EWA     |      1 | 2020-03-09 00:00:00 | 2020-03-10 00:00:00 |      1 |        9.57 |         4.78 |
| EWA     |      1 | 2020-03-23 00:00:00 | 2020-03-24 00:00:00 |      1 |        8.35 |         4.16 |
| MCHI    |      1 | 2015-08-24 00:00:00 | 2015-08-25 00:00:00 |      1 |        7.68 |         3.84 |
| EWY     |      1 | 2020-03-12 00:00:00 | 2020-03-13 00:00:00 |      1 |        7.4  |         3.62 |
| EWY     |      1 | 2026-06-05 00:00:00 | 2026-06-08 00:00:00 |      1 |        6.61 |         3.27 |
| EWY     |      1 | 2020-03-19 00:00:00 | 2020-03-20 00:00:00 |      1 |        6.48 |         3.18 |
| EWA     |      1 | 2020-03-27 00:00:00 | 2020-03-30 00:00:00 |      1 |        6.27 |         3.11 |
| MCHI    |      1 | 2015-07-08 00:00:00 | 2015-07-09 00:00:00 |      1 |        6.27 |         3.11 |

**10 piores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| EWY     |      1 | 2020-03-11 00:00:00 | 2020-03-12 00:00:00 |      1 |       -8.99 |        -4.48 |
| EWA     |      1 | 2020-03-11 00:00:00 | 2020-03-12 00:00:00 |      1 |       -8.82 |        -4.39 |
| EWJ     |      1 | 2011-03-14 00:00:00 | 2011-03-15 00:00:00 |      1 |       -7.3  |        -3.64 |
| EWY     |      1 | 2026-06-04 00:00:00 | 2026-06-05 00:00:00 |      1 |       -7.33 |        -3.39 |
| FXI     |      1 | 2025-04-04 00:00:00 | 2025-04-07 00:00:00 |      1 |       -6.63 |        -3.26 |
| EWJ     |      1 | 2024-08-02 00:00:00 | 2024-08-05 00:00:00 |      1 |       -6.07 |        -2.92 |
| FXI     |      1 | 2015-07-07 00:00:00 | 2015-07-08 00:00:00 |      1 |       -5.5  |        -2.72 |
| MCHI    |      1 | 2015-07-07 00:00:00 | 2015-07-08 00:00:00 |      1 |       -5.41 |        -2.66 |
| MCHI    |      1 | 2015-07-06 00:00:00 | 2015-07-07 00:00:00 |      1 |       -5.32 |        -2.65 |
| FXI     |      1 | 2015-07-06 00:00:00 | 2015-07-07 00:00:00 |      1 |       -5.34 |        -2.65 |

**Quem trouxe o retorno (soma por ativo, pp)**

| ativo   |    sum |   count |
|:--------|-------:|--------:|
| EWA     |  32.07 |      30 |
| EWY     |  18.02 |      56 |
| EWH     |   4.06 |       6 |
| EWS     |   3.13 |       7 |
| MCHI    |   1.91 |      30 |
| EWT     |   1.6  |      15 |
| FXI     |  -2.3  |      42 |
| EWJ     | -12.38 |       9 |

### Noite após queda forte — ADRs brasileiros (NYSE, IBKR) x mesmas ações na B3  (`lg_adr_br`)

**Tese:** Compro no MOC de Nova York o ADR brasileiro que caiu forte (resgate de fundos emergentes vende no fechamento) e vendo no MOO; comparo com a mesma noite das ações-objeto na B3 (leilão de fechamento -> abertura)

**Instrumentos:** [{'onde': 'IBKR (NYSE) ou B3 (home broker)', 'ticker': 'PBR, PBR-A, VALE, ITUB, BBD, ABEV, GGB, SID, EMBJ, SBS, ... / PETR4, VALE3, ...', 'lote': '1 ADR / 1 ação (fracionário)', 'custo': 'IBKR US$ 0,35 mín. + 1 bp; B3: emolumentos 0,03% + 1 bp por lado'}]

**Aplicável:** True — MOC até 15h50 ET (16h50/17h50 de Brasília) e MOO; na B3, ordem no call de fechamento (16h55-17h) e de abertura

| métrica | valor |
|---|---|
| OOS desde | 2021-01 |
| retorno OOS a.a. (R$ 20 mil) | -0.8% vs CDI 11.4% |
| ativo OOS pp (R$ 20 mil / R$ 50 mil) | -12.27 / -12.29 |
| depois do IR (classe acoes) pp, 20k / 50k | -12.25 / -12.27 |
| IR OOS / Sharpe | -0.69 / -0.69 |
| pior queda | -25.6% |
| PBO / Sharpe deflacionado | 4% / +0% |
| leque de parâmetros p5 / mediana / p95 | -13.38 / -2.77 / -1.02 |
| custo 2x / execução t+2 | -24.93 / -0.85 |
| walk-forward | -11.37 |
| sem os 10 melhores negócios | -18.27 |
| placebo p | 0.66 |
| look-ahead (truncamento) | passou |

**10 melhores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| BRKM5   |      1 | 2020-03-12 00:00:00 | 2020-03-13 00:00:00 |      1 |       20.03 |        10.02 |
| PETR4   |      1 | 2020-03-09 00:00:00 | 2020-03-10 00:00:00 |      1 |       16.11 |         8.06 |
| EMBR3   |      1 | 2020-03-12 00:00:00 | 2020-03-13 00:00:00 |      1 |       15.31 |         7.65 |
| PETR3   |      1 | 2020-03-09 00:00:00 | 2020-03-10 00:00:00 |      1 |       14.87 |         7.43 |
| SANB11  |      1 | 2026-07-30 00:00:00 | 2026-07-31 00:00:00 |      1 |       13.78 |         6.89 |
| BBDC4   |      1 | 2016-03-16 00:00:00 | 2016-03-17 00:00:00 |      1 |       10.31 |         5.14 |
| BRKM5   |      1 | 2020-03-23 00:00:00 | 2020-03-24 00:00:00 |      1 |       10.14 |         5.07 |
| ITUB4   |      1 | 2016-03-16 00:00:00 | 2016-03-17 00:00:00 |      1 |        9.17 |         4.58 |
| PETR3   |      1 | 2021-08-04 00:00:00 | 2021-08-05 00:00:00 |      1 |        8.76 |         4.37 |
| BRKM5   |      1 | 2022-01-27 00:00:00 | 2022-01-28 00:00:00 |      1 |        8.19 |         4.1  |

**10 piores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| PETR4   |      1 | 2020-03-06 00:00:00 | 2020-03-09 00:00:00 |      1 |      -22.06 |       -11.03 |
| PETR3   |      1 | 2020-03-06 00:00:00 | 2020-03-09 00:00:00 |      1 |      -21.1  |       -10.54 |
| BRKM5   |      1 | 2020-03-11 00:00:00 | 2020-03-12 00:00:00 |      1 |      -20.44 |       -10.2  |
| CSNA3   |      1 | 2020-03-11 00:00:00 | 2020-03-12 00:00:00 |      1 |      -20.15 |       -10.07 |
| BRKM5   |      1 | 2019-06-03 00:00:00 | 2019-06-04 00:00:00 |      1 |      -19.95 |        -9.95 |
| PETR3   |      1 | 2021-02-19 00:00:00 | 2021-02-22 00:00:00 |      1 |      -17.05 |        -8.52 |
| PETR4   |      1 | 2021-02-19 00:00:00 | 2021-02-22 00:00:00 |      1 |      -16.65 |        -8.3  |
| PETR4   |      1 | 2018-05-23 00:00:00 | 2018-05-24 00:00:00 |      1 |      -13.91 |        -6.94 |
| BBAS3   |      1 | 2025-05-15 00:00:00 | 2025-05-16 00:00:00 |      1 |      -13.17 |        -6.58 |
| BRFS3   |      1 | 2020-03-13 00:00:00 | 2020-03-16 00:00:00 |      1 |      -12.14 |        -6.07 |

**Quem trouxe o retorno (soma por ativo, pp)**

| ativo   |   sum |   count |
|:--------|------:|--------:|
| GGBR4   | 38.31 |     255 |
| CMIG4   | 32.65 |     207 |
| CSNA3   | 21.3  |     522 |
| EMBR3   | 18.88 |     358 |
| UGPA3   | 16.4  |     242 |
| BBDC4   | 12.41 |      80 |
| ITUB4   | 11.15 |      59 |
| BBAS3   |  8.48 |     170 |
| SANB11  |  7.58 |     144 |
| PETR3   |  7.34 |     212 |

### Noite após queda forte — ETFs/large caps dos EUA (IBKR, MOC->MOO)  (`lg_eua_etf`)

**Tese:** Compro no leilão de fechamento (MOC) os ETFs/large caps americanos que caíram forte no dia e vendo no leilão de abertura (MOO): vendedores forçados do fechamento (ETFs alavancados, vol-alvo, margin call) pressionam o leilão e a abertura devolve

**Instrumentos:** [{'onde': 'IBKR (conta de margem Reg T, só o necessário: ~50% da posição)', 'ticker': 'SPY/QQQ/XL*/... ou S&P 100', 'lote': '1 ação', 'custo': 'US$ 0,0035/ação mín. US$ 0,35 por ordem + 1 bp de derrapagem no leilão; margem T-bill+1,5% por 1 dia'}]

**Aplicável:** True — MOC até 15h50 ET (16h50/17h50 de Brasília) e MOO no dia seguinte: dá para fazer à mão ou com a API da IBKR; exige decidir com o preço das 15h50 (o sinal usa o fechamento -> ver t+2)

| métrica | valor |
|---|---|
| OOS desde | 2021-01 |
| retorno OOS a.a. (R$ 20 mil) | -0.7% vs CDI 11.4% |
| ativo OOS pp (R$ 20 mil / R$ 50 mil) | -12.13 / -7.90 |
| depois do IR (classe exterior) pp, 20k / 50k | -11.95 / -7.88 |
| IR OOS / Sharpe | -0.89 / -0.89 |
| pior queda | -35.3% |
| PBO / Sharpe deflacionado | 62% / +0% |
| leque de parâmetros p5 / mediana / p95 | -13.46 / -12.30 / -11.51 |
| custo 2x / execução t+2 | -19.27 / -8.96 |
| walk-forward | -12.74 |
| sem os 10 melhores negócios | -15.51 |
| placebo p | 0.95 |
| look-ahead (truncamento) | passou |

**10 melhores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| XOP     |      1 | 2020-03-09 00:00:00 | 2020-03-10 00:00:00 |      1 |       28.14 |         9.35 |
| XOP     |      1 | 2020-11-06 00:00:00 | 2020-11-09 00:00:00 |      1 |       10.83 |         3.53 |
| OIH     |      1 | 2020-03-12 00:00:00 | 2020-03-13 00:00:00 |      1 |       10.42 |         3.46 |
| KRE     |      1 | 2023-03-13 00:00:00 | 2023-03-14 00:00:00 |      1 |       10.52 |         3.43 |
| XRT     |      1 | 2021-01-28 00:00:00 | 2021-01-29 00:00:00 |      1 |       10.53 |         3.32 |
| OIH     |      1 | 2020-03-09 00:00:00 | 2020-03-10 00:00:00 |      1 |        9.97 |         3.29 |
| XLE     |      1 | 2020-03-12 00:00:00 | 2020-03-13 00:00:00 |      1 |        8.37 |         2.77 |
| XLE     |      1 | 2020-03-09 00:00:00 | 2020-03-10 00:00:00 |      1 |        7.97 |         2.63 |
| XLE     |      1 | 2020-03-23 00:00:00 | 2020-03-24 00:00:00 |      1 |        7.68 |         2.55 |
| OIH     |      1 | 2020-06-11 00:00:00 | 2020-06-12 00:00:00 |      1 |        8.14 |         2.52 |

**10 piores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| XOP     |      1 | 2020-03-06 00:00:00 | 2020-03-09 00:00:00 |      1 |      -24.31 |        -7.88 |
| OIH     |      1 | 2020-03-06 00:00:00 | 2020-03-09 00:00:00 |      1 |      -24.29 |        -7.47 |
| XLE     |      1 | 2020-03-06 00:00:00 | 2020-03-09 00:00:00 |      1 |      -17.55 |        -5.81 |
| KRE     |      1 | 2023-03-10 00:00:00 | 2023-03-13 00:00:00 |      1 |      -12.64 |        -4.15 |
| GDX     |      1 | 2020-03-13 00:00:00 | 2020-03-16 00:00:00 |      1 |      -11.91 |        -3.97 |
| OIH     |      1 | 2020-06-10 00:00:00 | 2020-06-11 00:00:00 |      1 |      -10.88 |        -3.54 |
| OIH     |      1 | 2020-03-11 00:00:00 | 2020-03-12 00:00:00 |      1 |       -9.67 |        -3.18 |
| GDX     |      1 | 2020-03-11 00:00:00 | 2020-03-12 00:00:00 |      1 |       -8.73 |        -2.88 |
| XOP     |      1 | 2020-06-10 00:00:00 | 2020-06-11 00:00:00 |      1 |       -8.41 |        -2.79 |
| GDX     |      1 | 2026-03-18 00:00:00 | 2026-03-19 00:00:00 |      1 |       -8.31 |        -2.67 |

**Quem trouxe o retorno (soma por ativo, pp)**

| ativo   |   sum |   count |
|:--------|------:|--------:|
| SMH     |  8.35 |     247 |
| GDX     |  7.57 |     561 |
| IBB     |  3.46 |     132 |
| XRT     |  2.4  |     110 |
| XLV     |  2.32 |      21 |
| XLK     |  2.22 |      62 |
| XHB     |  1.56 |     145 |
| XLC     |  1.33 |      35 |
| QQQ     |  1.15 |      36 |
| XLY     |  0.81 |      37 |

### Noite após queda forte — Europa (DAX/CAC/FTSE ou ETFs, IBKR)  (`lg_europa`)

**Tese:** Compro no leilão de fechamento europeu (ou MOC em NY nos ETFs de país) o que caiu forte no dia e vendo no leilão de abertura; custos reais de varejo: comissão mínima IBKR, stamp duty 0,5% (UK), FTT 0,2-0,4% (França)

**Instrumentos:** [{'onde': 'IBKR (Xetra/Euronext/LSE ou NYSE Arca)', 'ticker': 'ações DAX/CAC/FTSE; EWG/EWU/...; EXS1/ISF/CAC', 'lote': '1 ação', 'custo': '0,05% mín. EUR 1,25/GBP 1; stamp 0,5% UK; FTT 0,2-0,4% FR; 1 bp de derrapagem; margem 1 dia'}]

**Aplicável:** True — ordens no leilão de fechamento (Xetra/Euronext/LSE aceitam MOC/LOC na IBKR) às 12h25-13h25 de Brasília e MOO às 4h-5h: precisa de API/ordem programada; impostos de transação matam a versão em ações UK/FR

| métrica | valor |
|---|---|
| OOS desde | 2021-01 |
| retorno OOS a.a. (R$ 20 mil) | 1.8% vs CDI 11.4% |
| ativo OOS pp (R$ 20 mil / R$ 50 mil) | -9.69 / -8.16 |
| depois do IR (classe exterior) pp, 20k / 50k | -9.71 / -8.28 |
| IR OOS / Sharpe | -0.89 / -0.89 |
| pior queda | -14.7% |
| PBO / Sharpe deflacionado | 2% / +0% |
| leque de parâmetros p5 / mediana / p95 | -9.89 / -9.48 / -8.51 |
| custo 2x / execução t+2 | -11.32 / -6.86 |
| walk-forward | -9.69 |
| sem os 10 melhores negócios | -12.44 |
| placebo p | 0.87 |
| look-ahead (truncamento) | passou |

**10 melhores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| EWI     |      1 | 2020-03-12 00:00:00 | 2020-03-13 00:00:00 |      1 |       14.26 |         7.1  |
| EWP     |      1 | 2020-03-12 00:00:00 | 2020-03-13 00:00:00 |      1 |        8.12 |         4.03 |
| EWL     |      1 | 2020-03-23 00:00:00 | 2020-03-24 00:00:00 |      1 |        6.56 |         3.25 |
| EWD     |      1 | 2011-08-04 00:00:00 | 2011-08-05 00:00:00 |      1 |        6.46 |         3.22 |
| EWI     |      1 | 2012-08-02 00:00:00 | 2012-08-03 00:00:00 |      1 |        5.79 |         2.89 |
| EWI     |      1 | 2011-08-19 00:00:00 | 2011-08-22 00:00:00 |      1 |        5.68 |         2.84 |
| EWD     |      1 | 2022-11-09 00:00:00 | 2022-11-10 00:00:00 |      1 |        5.68 |         2.83 |
| EWP     |      1 | 2012-08-02 00:00:00 | 2012-08-03 00:00:00 |      1 |        4.81 |         2.4  |
| EWD     |      1 | 2011-09-28 00:00:00 | 2011-09-29 00:00:00 |      1 |        4.71 |         2.35 |
| EWI     |      1 | 2011-11-09 00:00:00 | 2011-11-10 00:00:00 |      1 |        4.58 |         2.29 |

**10 piores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| EWU     |      1 | 2020-03-11 00:00:00 | 2020-03-12 00:00:00 |      1 |       -8.22 |        -4.08 |
| EWQ     |      1 | 2020-03-11 00:00:00 | 2020-03-12 00:00:00 |      1 |       -7.7  |        -3.82 |
| EWI     |      1 | 2011-10-31 00:00:00 | 2011-11-01 00:00:00 |      1 |       -7.38 |        -3.68 |
| EWI     |      1 | 2011-09-02 00:00:00 | 2011-09-06 00:00:00 |      1 |       -6.9  |        -3.45 |
| FEZ     |      1 | 2011-09-02 00:00:00 | 2011-09-06 00:00:00 |      1 |       -6.74 |        -3.36 |
| EWQ     |      1 | 2020-03-06 00:00:00 | 2020-03-09 00:00:00 |      1 |       -6.64 |        -3.3  |
| EWG     |      1 | 2011-10-31 00:00:00 | 2011-11-01 00:00:00 |      1 |       -6.23 |        -3.11 |
| EWI     |      1 | 2018-05-25 00:00:00 | 2018-05-29 00:00:00 |      1 |       -4.88 |        -2.43 |
| EWG     |      1 | 2026-03-02 00:00:00 | 2026-03-03 00:00:00 |      1 |       -4.91 |        -2.41 |
| EWI     |      1 | 2011-07-08 00:00:00 | 2011-07-11 00:00:00 |      1 |       -4.73 |        -2.36 |

**Quem trouxe o retorno (soma por ativo, pp)**

| ativo   |   sum |   count |
|:--------|------:|--------:|
| EWI     | 26.52 |     246 |
| EWD     | 12.8  |     188 |
| EWU     |  7.5  |      54 |
| EWG     |  5.05 |      77 |
| EWN     |  4.66 |      82 |
| EWL     |  1.86 |      18 |
| VGK     |  0.55 |       1 |
| EWP     | -4.26 |     185 |
| FEZ     | -4.73 |      46 |
| EWQ     | -5.45 |      43 |

### Noite após queda forte — small caps dos EUA (S&P 600, spread estimado, IBKR)  (`lg_small_eua`)

**Tese:** Compro no MOC as small caps americanas que caíram forte no dia (resgates, ETFs de small caps e margin call vendem no fechamento) e vendo no MOO; pago meio spread estimado por lado

**Instrumentos:** [{'onde': 'IBKR (NYSE/Nasdaq)', 'ticker': 'componentes do S&P 600 (proxy do Russell 2000/IWM)', 'lote': '1 ação', 'custo': 'US$ 0,0035/ação mín. US$ 0,35 + meio spread estimado (Abdi-Ranaldo) por lado; margem 1 dia'}]

**Aplicável:** True — MOC até 15h50 ET (NYSE) / 15h55 (Nasdaq) e MOO no dia seguinte; precisa de rotina diária (API da IBKR ou à mão)

| métrica | valor |
|---|---|
| OOS desde | 2021-01 |
| retorno OOS a.a. (R$ 20 mil) | -25.1% vs CDI 11.4% |
| ativo OOS pp (R$ 20 mil / R$ 50 mil) | -36.53 / -32.60 |
| depois do IR (classe exterior) pp, 20k / 50k | -35.97 / -32.10 |
| IR OOS / Sharpe | -2.73 / -2.73 |
| pior queda | -83.2% |
| PBO / Sharpe deflacionado | 0% / +0% |
| leque de parâmetros p5 / mediana / p95 | -76.75 / -58.39 / -37.04 |
| custo 2x / execução t+2 | -59.52 / -32.76 |
| walk-forward | -36.53 |
| sem os 10 melhores negócios | -40.92 |
| placebo p | 1.00 |
| look-ahead (truncamento) | passou |

**10 melhores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| HE      |      1 | 2023-08-25 00:00:00 | 2023-08-28 00:00:00 |      1 |       39.6  |         6.53 |
| CZR     |      1 | 2020-03-12 00:00:00 | 2020-03-13 00:00:00 |      1 |       21.43 |         3.56 |
| NOG     |      1 | 2011-08-08 00:00:00 | 2011-08-09 00:00:00 |      1 |       18.56 |         2.95 |
| FUN     |      1 | 2020-03-12 00:00:00 | 2020-03-13 00:00:00 |      1 |       17.47 |         2.87 |
| AX      |      1 | 2015-10-14 00:00:00 | 2015-10-15 00:00:00 |      1 |       16.17 |         2.62 |
| ADMA    |      1 | 2026-03-26 00:00:00 | 2026-03-27 00:00:00 |      1 |       14.02 |         2.31 |
| CLSK    |      1 | 2023-12-29 00:00:00 | 2024-01-02 00:00:00 |      1 |       13.83 |         2.29 |
| MARA    |      1 | 2021-02-23 00:00:00 | 2021-02-24 00:00:00 |      1 |       13.81 |         2.26 |
| RITM    |      1 | 2020-03-23 00:00:00 | 2020-03-24 00:00:00 |      1 |       13.43 |         2.24 |
| MAC     |      1 | 2020-04-16 00:00:00 | 2020-04-17 00:00:00 |      1 |       13.49 |         2.23 |

**10 piores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| VIR     |      1 | 2021-03-02 00:00:00 | 2021-03-03 00:00:00 |      1 |      -29.15 |        -4.78 |
| HP      |      1 | 2020-03-06 00:00:00 | 2020-03-09 00:00:00 |      1 |      -27.94 |        -4.48 |
| ABG     |      1 | 2020-03-13 00:00:00 | 2020-03-16 00:00:00 |      1 |      -23.34 |        -3.66 |
| MARA    |      1 | 2017-12-21 00:00:00 | 2017-12-22 00:00:00 |      1 |      -17.66 |        -2.92 |
| MARA    |      1 | 2021-02-22 00:00:00 | 2021-02-23 00:00:00 |      1 |      -17.44 |        -2.85 |
| MARA    |      1 | 2021-01-20 00:00:00 | 2021-01-21 00:00:00 |      1 |      -15.68 |        -2.56 |
| CZR     |      1 | 2020-03-17 00:00:00 | 2020-03-18 00:00:00 |      1 |      -15.11 |        -2.5  |
| MARA    |      1 | 2021-05-10 00:00:00 | 2021-05-11 00:00:00 |      1 |      -15.32 |        -2.45 |
| SKYW    |      1 | 2020-06-10 00:00:00 | 2020-06-11 00:00:00 |      1 |      -14.28 |        -2.36 |
| SRPT    |      1 | 2025-05-06 00:00:00 | 2025-05-07 00:00:00 |      1 |      -14.62 |        -2.35 |

**Quem trouxe o retorno (soma por ativo, pp)**

| ativo   |   sum |   count |
|:--------|------:|--------:|
| HE      |  8.47 |      14 |
| CNK     |  4.14 |      22 |
| PMT     |  2.78 |       6 |
| NOG     |  2.66 |      10 |
| RITM    |  2.57 |       5 |
| VIR     |  2.56 |      37 |
| PTON    |  2.2  |      38 |
| AMR     |  2.13 |      17 |
| PENG    |  2.03 |      16 |
| CVSA    |  2    |      18 |

### Noite após queda forte — ETFs e BDRs da B3 (leilão de fechamento -> abertura)  (`lg_b3_etf_bdr`)

**Tese:** Compro no leilão de fechamento da B3 os ETFs (BOVA11, SMAL11, IVVB11, ...) ou BDRs que caíram forte no dia e vendo no leilão de abertura: o formador de mercado e o varejo em pânico pressionam o fechamento; sem remessa, só emolumentos

**Instrumentos:** [{'onde': 'B3 (qualquer home broker)', 'ticker': 'ETFs (BOVA11, SMAL11, IVVB11, DIVO11, ...) e BDRs nível I/III', 'lote': '1 cota (ETF/BDR têm lote 1 ou fracionário)', 'custo': 'emolumentos 0,03%/lado + max(1 bp, 1/2 meio spread)'}]

**Aplicável:** True — ordem a mercado no call de fechamento (16h55-17h) e de abertura (9h45-10h) em qualquer corretora brasileira; sem remessa

| métrica | valor |
|---|---|
| OOS desde | 2021-01 |
| retorno OOS a.a. (R$ 20 mil) | 13.0% vs CDI 11.4% |
| ativo OOS pp (R$ 20 mil / R$ 50 mil) | +1.59 / +1.59 |
| depois do IR (classe etf_b3) pp, 20k / 50k | +1.42 / +1.42 |
| IR OOS / Sharpe | +0.57 / +0.57 |
| pior queda | -1.9% |
| PBO / Sharpe deflacionado | 36% / +15% |
| leque de parâmetros p5 / mediana / p95 | +1.08 / +2.39 / +11.36 |
| custo 2x / execução t+2 | +0.94 / -0.20 |
| walk-forward | +2.34 |
| sem os 10 melhores negócios | -0.31 |
| placebo p | 0.00 |
| look-ahead (truncamento) | passou |

**10 melhores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| BOVV11  |      1 | 2020-03-12 00:00:00 | 2020-03-13 00:00:00 |      1 |       10.46 |         5.22 |
| BOVA11  |      1 | 2020-03-23 00:00:00 | 2020-03-24 00:00:00 |      1 |        7.9  |         3.94 |
| SMAC11  |      1 | 2020-03-12 00:00:00 | 2020-03-13 00:00:00 |      1 |        7.33 |         3.65 |
| SMAL11  |      1 | 2020-03-16 00:00:00 | 2020-03-17 00:00:00 |      1 |        6.76 |         3.37 |
| SMAL11  |      1 | 2020-04-03 00:00:00 | 2020-04-06 00:00:00 |      1 |        6.57 |         3.28 |
| SMAL11  |      1 | 2020-03-09 00:00:00 | 2020-03-10 00:00:00 |      1 |        6.44 |         3.21 |
| XINA11  |      1 | 2022-10-31 00:00:00 | 2022-11-01 00:00:00 |      1 |        4.79 |         2.39 |
| PIBB11  |      1 | 2020-03-09 00:00:00 | 2020-03-10 00:00:00 |      1 |        4.41 |         2.18 |
| BOVA11  |      1 | 2014-10-10 00:00:00 | 2014-10-13 00:00:00 |      1 |        3.54 |         1.76 |
| SMAC11  |      1 | 2020-04-24 00:00:00 | 2020-04-27 00:00:00 |      1 |        3.13 |         1.56 |

**10 piores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| PIBB11  |      1 | 2020-03-11 00:00:00 | 2020-03-12 00:00:00 |      1 |      -14.3  |        -7.08 |
| PIBB11  |      1 | 2020-03-06 00:00:00 | 2020-03-09 00:00:00 |      1 |       -6.72 |        -3.36 |
| BOVA11  |      1 | 2020-03-06 00:00:00 | 2020-03-09 00:00:00 |      1 |       -6.49 |        -3.21 |
| SMAL11  |      1 | 2020-03-18 00:00:00 | 2020-03-19 00:00:00 |      1 |       -6.26 |        -3.12 |
| SMAL11  |      1 | 2020-04-30 00:00:00 | 2020-05-04 00:00:00 |      1 |       -4.8  |        -2.39 |
| SMAC11  |      1 | 2020-03-18 00:00:00 | 2020-03-19 00:00:00 |      1 |       -4.33 |        -2.16 |
| BOVB11  |      1 | 2020-03-11 00:00:00 | 2020-03-12 00:00:00 |      1 |       -3.88 |        -1.93 |
| XINA11  |      1 | 2021-07-26 00:00:00 | 2021-07-27 00:00:00 |      1 |       -3.77 |        -1.88 |
| SMAL11  |      1 | 2020-03-05 00:00:00 | 2020-03-06 00:00:00 |      1 |       -3.66 |        -1.82 |
| EURP11  |      1 | 2022-03-03 00:00:00 | 2022-03-04 00:00:00 |      1 |       -3.58 |        -1.79 |

**Quem trouxe o retorno (soma por ativo, pp)**

| ativo   |   sum |   count |
|:--------|------:|--------:|
| SMAL11  |  8.71 |      27 |
| XINA11  |  7.71 |      14 |
| BOVV11  |  7.45 |       5 |
| BOVA11  |  6.61 |      12 |
| SMAC11  |  5.12 |      19 |
| FIND11  |  1.12 |       6 |
| XBOV11  |  0.28 |       1 |
| TECK11  |  0.14 |       4 |
| ACWI11  | -0.04 |       1 |
| EURP11  | -0.12 |       6 |

### Noites combinadas (blue chips + ETFs B3, opcional EUA) com filtro de VIX e dia da semana  (`lg_combo_regime`)

**Tese:** Compro no leilão de fechamento o que caiu forte no dia SÓ quando o VIX de ontem está acima da mediana de 1 ano (estresse = mais venda forçada no fechamento) e evito a noite de sexta (risco de fim de semana); vendo na abertura

**Instrumentos:** [{'onde': 'B3 (home broker); opcional IBKR', 'ticker': 'PETR4, VALE3, ITUB4, BBDC4, ... + BOVA11, SMAL11, IVVB11, ...; SPY/S&P 100', 'lote': '1 ação/cota (fracionário)', 'custo': 'B3: emolumentos 0,03% + 1 bp por lado; IBKR: US$ 0,35 mín. + 1 bp'}]

**Aplicável:** True — ordens nos leilões de fechamento/abertura da B3 (e MOC/MOO na IBKR na variante b3_eua); VIX de ontem é público

| métrica | valor |
|---|---|
| OOS desde | 2021-01 |
| retorno OOS a.a. (R$ 20 mil) | 14.4% vs CDI 11.4% |
| ativo OOS pp (R$ 20 mil / R$ 50 mil) | +2.93 / +2.93 |
| depois do IR (classe acoes) pp, 20k / 50k | +2.12 / +2.12 |
| IR OOS / Sharpe | +0.40 / +0.40 |
| pior queda | -6.1% |
| PBO / Sharpe deflacionado | 24% / +50% |
| leque de parâmetros p5 / mediana / p95 | +0.69 / +2.55 / +3.63 |
| custo 2x / execução t+2 | -2.47 / -1.63 |
| walk-forward | +2.93 |
| sem os 10 melhores negócios | -0.30 |
| placebo p | 0.00 |
| look-ahead (truncamento) | passou |

**10 melhores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| BRKM5   |      1 | 2020-03-12 00:00:00 | 2020-03-13 00:00:00 |      1 |       20.03 |         6.68 |
| PETR4   |      1 | 2020-03-09 00:00:00 | 2020-03-10 00:00:00 |      1 |       16.11 |         5.37 |
| EMBR3   |      1 | 2020-03-12 00:00:00 | 2020-03-13 00:00:00 |      1 |       15.31 |         5.1  |
| PETR3   |      1 | 2020-03-09 00:00:00 | 2020-03-10 00:00:00 |      1 |       14.87 |         4.96 |
| CSNA3   |      1 | 2020-03-09 00:00:00 | 2020-03-10 00:00:00 |      1 |       10.76 |         3.59 |
| UGPA3   |      1 | 2020-03-12 00:00:00 | 2020-03-13 00:00:00 |      1 |       10.73 |         3.57 |
| BRKM5   |      1 | 2020-03-23 00:00:00 | 2020-03-24 00:00:00 |      1 |       10.14 |         3.38 |
| PETR3   |      1 | 2021-08-04 00:00:00 | 2021-08-05 00:00:00 |      1 |        8.76 |         2.91 |
| CSNA3   |      1 | 2014-07-17 00:00:00 | 2014-07-18 00:00:00 |      1 |        8.06 |         2.69 |
| VIVT3   |      1 | 2020-05-07 00:00:00 | 2020-05-08 00:00:00 |      1 |        8.01 |         2.67 |

**10 piores negócios**

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| BRKM5   |      1 | 2020-03-11 00:00:00 | 2020-03-12 00:00:00 |      1 |      -20.44 |        -6.8  |
| CSNA3   |      1 | 2020-03-11 00:00:00 | 2020-03-12 00:00:00 |      1 |      -20.15 |        -6.71 |
| BRKM5   |      1 | 2019-06-03 00:00:00 | 2019-06-04 00:00:00 |      1 |      -19.95 |        -6.62 |
| CSNA3   |      1 | 2017-05-17 00:00:00 | 2017-05-18 00:00:00 |      1 |      -14.91 |        -4.97 |
| GGBR4   |      1 | 2020-03-11 00:00:00 | 2020-03-12 00:00:00 |      1 |      -14.02 |        -4.67 |
| PETR4   |      1 | 2018-05-23 00:00:00 | 2018-05-24 00:00:00 |      1 |      -13.91 |        -4.63 |
| PETR3   |      1 | 2018-05-23 00:00:00 | 2018-05-24 00:00:00 |      1 |      -12.05 |        -4.01 |
| SBSP3   |      1 | 2020-03-17 00:00:00 | 2020-03-18 00:00:00 |      1 |      -10.93 |        -3.62 |
| BBAS3   |      1 | 2014-10-20 00:00:00 | 2014-10-21 00:00:00 |      1 |       -8.24 |        -2.74 |
| EMBR3   |      1 | 2016-03-03 00:00:00 | 2016-03-04 00:00:00 |      1 |       -7.99 |        -2.66 |

**Quem trouxe o retorno (soma por ativo, pp)**

| ativo   |   sum |   count |
|:--------|------:|--------:|
| PETR3   | 17.76 |     142 |
| CSNA3   | 16.34 |     331 |
| PETR4   | 15.73 |     160 |
| BBAS3   | 12.85 |     123 |
| CMIG4   | 12.78 |     122 |
| BRFS3   | 12.06 |     156 |
| GGBR4   | 10.39 |     149 |
| EMBR3   |  9.79 |     128 |
| UGPA3   |  8.66 |     112 |
| BBDC4   |  5.84 |      57 |
