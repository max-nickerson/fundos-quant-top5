# Frente pf2_futuros — futuros do mundo que cabem em R$ 20–50 mil (micro/mini), só a margem fora

Rodada PF2 (BRIEF_PF.md). 8 estratégias novas em `pf/fundos/fu_*.py` + peças comuns em `pf/fundos/fu_comum.py`; dados em `pf/dados/pf2_futuros/`;
baterias em `pf/resultados/bateria/fu_*.pkl` (`python pf/rodar_pf.py um <arquivo>`), resumo em `pf/resultados/pf2_futuros.pkl`.

## Tabela (OOS, pp a.a. sobre o CDI)

| Fundo | Aplicável | OOS desde | R$ 20 mil antes / depois do IR | R$ 50 mil antes / depois do IR | IR (20k) | PBO % | P(bater 3a) % | custo 2x | t+2 | sem 10 melhores | placebo p | truncamento |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Eurex micro (FSXE/FDXS): pânico europeu, reversão ou tendência (`fu_eurex_micro`) | sim | 2021-01 | +1.7 / +1.7 | +2.2 / +2.2 | 0.22 | 14 | 69 | +1.5 | +3.0 | -2.1 | 0.04 | ok |
| Nikkei 225 Micro (OSE): pânico com iene forte (carry + margem do varejo) (`fu_asia_nikkei`) | sim | 2021-01 | -3.2 / -3.2 | -2.0 / -2.0 | -0.34 | 74 | 22 | -3.3 | +3.0 | -1.6 | 0.94 | ok |
| Energia micro (MNG/MCL): curva (quem rola paga o contango) e sazonalidade do gás (`fu_energia_curva`) | sim | 2021-01 | -5.6 / -5.5 | +1.4 / +1.3 | -0.41 | 82 | 16 | -6.4 | -7.6 | -2.0 | 0.72 | ok |
| Bitcoin B3 (BIT) na liquidação dos perpétuos: funding negativo + queda (`fu_b3_cripto_panico`) | sim | 2023-01 | -6.5 / -6.4 | -5.2 / -5.1 | -0.49 | 58 | 14 | -6.9 | -3.3 | -1.5 | 0.97 | ok |
| Agro B3: spread safra x entressafra (milho: vende setembro, compra março+1) (`fu_agro_spread`) | sim | 2023-01 | +11.7 / +9.6 | +4.7 / +3.9 | 0.84 | 17 | 96 | +11.5 | +11.6 | +0.8 | 0.14 | ok |
| Brasil x S&P: WIN no pânico relativo (resíduo do Ibovespa em US$) (`fu_brasil_relativo`) | sim | 2021-01 | -0.3 / -0.2 | +0.7 / +0.7 | 0.02 | 10 | 48 | -0.3 | -2.9 | -6.2 | 0.51 | ok |
| Micro Treasury Yield: concessão de leilão (30Y/10Y) e curva 2s10s (`fu_treasury_micro`) | sim | 2021-01 | -7.4 / -7.3 | -2.9 / -2.8 | -0.43 | 48 | 21 | -10.0 | -15.9 | -18.6 | 0.79 | ok |
| Peso mexicano e rande na B3 (MEX/AFS, US$ 10 mil): carry e compra depois do pânico (`fu_moedas_em`) | NÃO | 2021-01 | -0.2 / -0.2 | -5.2 / -5.2 | n/d | 64 | 0 | -0.2 | -0.2 | -5.1 | 0.50 | ok |

Parâmetros sempre os de maior excesso DENTRO da amostra (mesmo quando outra variante foi melhor fora). IR do moedas_em = n/d (quase sem posição no OOS).

## Premissas comuns (fu_comum.py)

- Retorno de 1 contrato sem salto de rolagem: índice de retorno total (DAX, Ibovespa) ou de preço + dividendos assumidos (SX5E 3%, Nikkei 1,8%) menos o juro
  de política da moeda (BIS); ETFs que rolam (UNG/USO) − T-bill + taxa; yields (US$ 10/bp − carregamento); boletim B3 por vencimento (agro, BIT).
  O contínuo do Yahoo (CL=F, NG=F, ^N225...) entra só para o NOCIONAL. Decisão no fechamento de t, execução em t+1, contratos inteiros.
- IBKR: só a margem fora (folga 1,5x; perde o CDI, fica no dólar, IOF+spread a cada ajuste) e P&L trazido/levado todo mês com IOF;
  B3: garantia em Tesouro Selic (rende CDI). IR: exterior 15% anual; futuros B3 15% mensal (pf/ir.py).
- Tamanho: 1 contrato por sinal (ou exposição-alvo arredondada); não opera se 1 contrato > 2,5x o capital (nocional) ou, em gás e moedas,
  se a vol anual de 1 contrato > 35% do capital (a versão do gás sem essa régua QUEBROU até 2019). Micros simulados antes do lançamento são
  hipotéticos (mesmo subjacente); depois do corte só operam depois de lançados.

## Contratos confirmados (tamanho / margem / custo usado)

| Contrato | Bolsa | Tamanho | Nocional hoje | Margem | Custo/lado usado | Cabe? |
|---|---|---|---|---|---|---|
| FSXE Micro-Euro STOXX 50 | Eurex (IBKR) | EUR 1 x índice | ≈ R$ 38 mil | ~8% (≈ EUR 500) | EUR 1,10 | sim (1,9x R$ 20 mil) |
| FDXS Micro-DAX | Eurex (IBKR) | EUR 1 x índice | ≈ R$ 160 mil | ~8% | EUR 1,60 | não |
| Nikkei 225 Micro | OSE (IBKR) | ¥10 x índice | ≈ R$ 25 mil | ¥63,5 mil | ¥57 | sim |
| Mini-KOSPI 200 | KRX / Eurex-KRX Link (IBKR) | KRW 50 mil x índice | ≈ R$ 170 mil | — | — | não |
| MNG Micro Henry Hub | NYMEX (IBKR) | 1.000 MMBtu | ≈ R$ 18 mil | ~15% | US$ 3,15 | nocional sim; vol só com R$ 50 mil |
| MCL Micro WTI | NYMEX (IBKR) | 100 bbl | ≈ R$ 53 mil | ~12% | US$ 1,85 | só R$ 50 mil |
| BIT Bitcoin B3 | B3 | 0,01 BTC (0,1 até jun/2025) | ≈ R$ 4,1 mil | Tesouro Selic | 0,10% | sim |
| CCM/BGI/ICF spread de calendário | B3 | 450 sc / 330 @ / 100 sc | R$ 30 / 105 / 190 mil por perna | margem de spread | R$ 6 / 18 / 29 por perna | sim (spread) |
| WIN | B3 | R$ 0,20 x Ibov | ≈ R$ 41 mil | Tesouro Selic | R$ 1,10 | sim |
| MES | CME (IBKR) | US$ 5 x S&P | ≈ R$ 210 mil | ~7% | US$ 1,25 | não |
| 30Y/10Y/2YY Micro Yield | CBOT (IBKR) | US$ 10/bp | DV01 US$ 10 | US$ 290-400 | US$ 1,62 | sim |
| MEX / AFS (MXN, ZAR em USD) | B3 | US$ 10 mil | ≈ R$ 55 mil | Tesouro Selic | 0,30% + R$ 2 (sem livro) | nocional 2,75x; sem liquidez |

Fontes: Eurex (circular 025/21 e contract specifications), JPX (Nikkei 225 Micro), IBKR (margens OSE/KRX, comissões), CME Group (MNG fact card,
Micro Treasury Yield), B3 (páginas de MEX/AFS, boletim BVBG.086), TreasuryDirect (leilões), EIA (curvas NYMEX até abr/2024).

## Fundo a fundo

### Eurex micro (FSXE/FDXS): pânico europeu, reversão ou tendência (`fu_eurex_micro`)

**Tese.** Bancos emissores de autocalls/reverse convertibles sobre o Euro STOXX 50 ficam vendidos em gama perto das barreiras e vendem
futuro na queda, junto com fundos de vol-alvo quando o V2X dispara. Compro 1 Micro-Euro STOXX 50 (FSXE, EUR 1 x índice ≈ R$ 38 mil)
depois de queda de k desvios em 5 dias com o V2X no decil de cima de 1 ano e seguro H dias.

**Contratos.** FSXE e FDXS = EUR 1 por ponto (Eurex, circular 025/21, lançados em mar/2021); IBKR ~EUR 0,35 + taxas; custo usado EUR 1,10/lado
(FSXE) com meio spread de 1 tick; margem ~8%. FDXS (≈ R$ 160 mil) não cabe e saiu da grade (com o DAX barato de 2008-12 teria IS +6-7 pp,
OOS zero porque nunca opera).

**Resultado.** IS escolheu pânico k=2/H=5 (as 4 variantes de pânico são positivas no IS e no OOS; reversão e tendência perdem). OOS +1,7 pp
(R$ 20 mil) / +2,2 pp (R$ 50 mil). Placebo p = 0,04 (o timing importa), custo 2x +1,5, t+2 +3,0, mas sem os 10 melhores −2,1 pp e pior
queda −26% (fev-mar/2020: comprou o "pânico" no começo do Covid e perdeu 18 pp). Ago/2024 (desmonte do carry do iene) fez +8 pp.
**Por que funcionou:** os ganhos são rebotes de 5-9 dias depois de capitulações (out/2008, ago/2015, fev/2016, jun/2016 Brexit,
ago/2024) — quando o hedge de gama dos emissores e o corte de vol-alvo terminam. **O que falha:** pânico que vira crise (ago/2011,
mar/2020): 1 contrato = 1,9x o capital, não há como diluir.

Parâmetros (IS): `{'modo': 'panico', 'k': 2.0, 'H': 5, 'inst': 'FSXE'}`. Grade (ativo pp, R$ 20 mil):

| variante | IS | OOS |
|---|---|---|
| {'modo': 'tendencia', 'k': 2.0, 'H': 10} | -7.4 | -11.4 |
| {'modo': 'tendencia', 'k': 2.0, 'H': 5} | -7.4 | -11.4 |
| {'modo': 'tendencia', 'k': 1.5, 'H': 10} | -7.4 | -11.4 |
| {'modo': 'tendencia', 'k': 1.5, 'H': 5} | -7.4 | -11.4 |
| {'modo': 'reversao', 'k': 1.5, 'H': 10} | -0.4 | -6.4 |
| {'modo': 'reversao', 'k': 2.0, 'H': 10} | +0.3 | -6.2 |
| {'modo': 'reversao', 'k': 1.5, 'H': 5} | +0.7 | -5.3 |
| {'modo': 'reversao', 'k': 2.0, 'H': 5} | -0.9 | -2.3 |
| {'modo': 'panico', 'k': 2.0, 'H': 5} | +2.0 | +1.7 |
| {'modo': 'panico', 'k': 2.0, 'H': 10} | +0.7 | +1.8 |
| {'modo': 'panico', 'k': 1.5, 'H': 5} | +1.2 | +4.1 |
| {'modo': 'panico', 'k': 1.5, 'H': 10} | +1.1 | +6.1 |

10 melhores negócios (R$ 20 mil; contribuição em pp do PL):

| ativo | lado | entrada | saída | dias | contratos | retorno % | contrib pp |
|---|---|---|---|---|---|---|---|
| FSXE | +1 | 2008-10-29 | 2008-11-04 | 5 | 3 | +15.7 | +15.4 |
| FSXE | +1 | 2024-08-06 | 2024-08-16 | 9 | 1 | +5.8 | +8.1 |
| FSXE | +1 | 2015-08-25 | 2015-09-03 | 8 | 2 | +6.5 | +8.0 |
| FSXE | +1 | 2011-09-26 | 2011-09-30 | 5 | 4 | +7.6 | +7.7 |
| FSXE | +1 | 2014-12-16 | 2014-12-23 | 6 | 2 | +7.1 | +7.0 |
| FSXE | +1 | 2016-02-10 | 2016-02-19 | 8 | 2 | +5.0 | +6.1 |
| FSXE | +1 | 2016-06-16 | 2016-06-22 | 5 | 2 | +5.3 | +5.7 |
| FSXE | +1 | 2010-05-10 | 2010-05-17 | 6 | 3 | +5.5 | +5.0 |
| FSXE | +1 | 2022-01-26 | 2022-02-01 | 5 | 1 | +3.6 | +4.5 |
| FSXE | +1 | 2008-09-19 | 2008-09-26 | 6 | 2 | +5.2 | +4.4 |

10 piores negócios (R$ 20 mil; contribuição em pp do PL):

| ativo | lado | entrada | saída | dias | contratos | retorno % | contrib pp |
|---|---|---|---|---|---|---|---|
| FSXE | +1 | 2020-02-26 | 2020-03-26 | 22 | 1 | -20.1 | -18.0 |
| FSXE | +1 | 2011-08-04 | 2011-08-19 | 12 | 4 | -13.5 | -15.4 |
| FSXE | +1 | 2015-07-02 | 2015-07-08 | 5 | 2 | -4.8 | -5.8 |
| FSXE | +1 | 2008-11-13 | 2008-12-01 | 13 | 3 | -4.7 | -4.6 |
| FSXE | +1 | 2026-03-05 | 2026-03-17 | 9 | 1 | -1.7 | -3.1 |
| FSXE | +1 | 2011-09-08 | 2011-09-19 | 8 | 4 | -2.5 | -2.5 |
| FSXE | +1 | 2022-02-28 | 2022-03-16 | 13 | 1 | -1.9 | -2.3 |
| FSXE | +1 | 2008-03-06 | 2008-03-12 | 5 | 2 | -1.0 | -1.0 |
| FSXE | +1 | 2018-02-06 | 2018-02-20 | 11 | 1 | -1.1 | -0.8 |
| FSXE | +1 | 2015-09-28 | 2015-10-02 | 5 | 1 | -0.7 | -0.5 |

Alavancagem: 1x R$ 20 mil: +1.7 pp, pior queda -26%; 1x R$ 50 mil: +2.2 pp, pior queda -32%; 2x R$ 20 mil: +2.3 pp, pior queda -57%; 2x R$ 50 mil: +2.5 pp, pior queda -56%

### Nikkei 225 Micro (OSE): pânico com iene forte (carry + margem do varejo) (`fu_asia_nikkei`)

**Tese.** Varejo japonês alavancado (conta margem, liquidação em D+2) + carry em iene: queda forte do Nikkei COM o iene subindo =
desmonte forçado; compro 1 Nikkei 225 Micro (OSE, ¥10 x índice ≈ R$ 25 mil, desde mai/2023; IBKR margem ~¥63,5 mil) e seguro H dias.

**Acesso à Ásia.** Mini-KOSPI 200 (KRX, KRW 50 mil x índice ≈ R$ 170 mil) é acessível pela IBKR (Eurex/KRX Link; exceto residentes da
Coreia/Japão/Índia), mas não cabe; mini Nikkei (¥100) e CME NKD/NIY também não. Só o micro do Nikkei serve.

**Resultado.** Todas as variantes perdem no IS (a melhor, pânico com iene k=2/H=5, −1 pp). OOS −3,2 / −2,0 pp; placebo p = 0,94.
**Por que falhou:** no Japão o rebote depois do desmonte do carry é rápido demais para fechamento diário com execução t+1 (5/ago/2024
caiu 12% e subiu 10% no dia seguinte: o sinal entra DEPOIS do rebote), e os pânicos de 2008/2010/2025 continuaram caindo. O BoJ, que
comprava ETF nas quedas, parou em 2024.

Parâmetros (IS): `{'modo': 'panico_iene', 'k': 2.0, 'H': 5}`. Grade (ativo pp, R$ 20 mil):

| variante | IS | OOS |
|---|---|---|
| {'modo': 'reversao', 'k': 2.0, 'H': 10} | -3.8 | -8.8 |
| {'modo': 'reversao', 'k': 2.0, 'H': 5} | -0.8 | -7.1 |
| {'modo': 'reversao', 'k': 1.5, 'H': 10} | -8.3 | -5.3 |
| {'modo': 'reversao', 'k': 1.5, 'H': 5} | -6.1 | -4.2 |
| {'modo': 'panico_iene', 'k': 2.0, 'H': 5} | -1.3 | -3.2 |
| {'modo': 'panico_iene', 'k': 2.0, 'H': 10} | -3.2 | -2.3 |
| {'modo': 'panico_iene', 'k': 1.5, 'H': 5} | -3.6 | -1.6 |
| {'modo': 'panico_iene', 'k': 1.5, 'H': 10} | -2.7 | -1.5 |
| {'modo': 'tendencia', 'k': 1.5, 'H': 5} | -4.9 | +3.5 |
| {'modo': 'tendencia', 'k': 1.5, 'H': 10} | -4.9 | +3.5 |
| {'modo': 'tendencia', 'k': 2.0, 'H': 5} | -4.9 | +3.5 |
| {'modo': 'tendencia', 'k': 2.0, 'H': 10} | -4.9 | +3.5 |

10 melhores negócios (R$ 20 mil; contribuição em pp do PL):

| ativo | lado | entrada | saída | dias | contratos | retorno % | contrib pp |
|---|---|---|---|---|---|---|---|
| N225MC | +1 | 2008-10-28 | 2008-11-04 | 6 | 12 | +27.3 | +25.8 |
| N225MC | +1 | 2016-01-22 | 2016-01-29 | 6 | 4 | +9.4 | +9.9 |
| N225MC | +1 | 2024-08-07 | 2024-08-16 | 8 | 2 | +9.8 | +9.8 |
| N225MC | +1 | 2011-03-16 | 2011-03-28 | 9 | 11 | +10.2 | +8.9 |
| N225MC | +1 | 2020-04-03 | 2020-04-13 | 7 | 2 | +6.9 | +6.0 |
| N225MC | +1 | 2014-12-18 | 2014-12-24 | 5 | 5 | +6.2 | +5.9 |
| N225MC | +1 | 2023-10-06 | 2023-10-12 | 5 | 2 | +4.6 | +4.9 |
| N225MC | +1 | 2015-10-01 | 2015-10-07 | 5 | 3 | +5.4 | +4.6 |
| N225MC | +1 | 2014-04-15 | 2014-04-21 | 5 | 7 | +4.4 | +4.5 |
| N225MC | +1 | 2016-04-07 | 2016-04-13 | 5 | 4 | +4.3 | +4.4 |

10 piores negócios (R$ 20 mil; contribuição em pp do PL):

| ativo | lado | entrada | saída | dias | contratos | retorno % | contrib pp |
|---|---|---|---|---|---|---|---|
| N225MC | +1 | 2020-03-02 | 2020-03-23 | 16 | 3 | -20.0 | -19.1 |
| N225MC | +1 | 2024-07-22 | 2024-08-05 | 11 | 1 | -21.4 | -16.3 |
| N225MC | +1 | 2008-10-07 | 2008-10-20 | 10 | 11 | -14.0 | -11.5 |
| N225MC | +1 | 2013-05-29 | 2013-06-17 | 14 | 7 | -8.8 | -9.3 |
| N225MC | +1 | 2025-04-07 | 2025-04-17 | 9 | 2 | +1.8 | -8.7 |
| N225MC | +1 | 2008-01-09 | 2008-01-16 | 6 | 9 | -7.0 | -7.3 |
| N225MC | +1 | 2016-01-11 | 2016-01-20 | 8 | 3 | -7.2 | -6.5 |
| N225MC | +1 | 2018-02-01 | 2018-02-08 | 6 | 3 | -5.2 | -5.3 |
| N225MC | +1 | 2015-08-25 | 2015-09-04 | 9 | 4 | -4.0 | -4.6 |
| N225MC | +1 | 2008-03-05 | 2008-03-13 | 7 | 10 | -4.3 | -4.4 |

Alavancagem: 1x R$ 20 mil: -3.2 pp, pior queda -27%; 1x R$ 50 mil: -2.0 pp, pior queda -27%; 2x R$ 20 mil: -6.3 pp, pior queda -53%; 2x R$ 50 mil: -6.4 pp, pior queda -53%

### Energia micro (MNG/MCL): curva (quem rola paga o contango) e sazonalidade do gás (`fu_energia_curva`)

**Tese.** UNG/USO/índices rolam por regra e pagam o contango a quem tem estocagem; vender gás natural micro (MNG, 1.000 MMBtu ≈
R$ 18 mil, desde nov/2023) quando o contango estimado passa do limite, ou na estação de injeção (mar-set); MCL pela mesma regra.

**Curva e rolagem.** Retornos de UNG/USO (ETFs que rolam) − T-bill + taxa: sem salto. A curva da EIA (RNGC1/2, RCLC1/2) só vai até
05/abr/2024; estimador causal = salto do contínuo do Yahoo no dia da troca − retorno do ETF (corr. 0,91 com a EIA no gás, 0,79 no
petróleo), usado só no mês seguinte. **Contratos.** MNG US$ 3,15/lado (meio spread de 2 ticks), margem ~15%; MCL (100 bbl ≈ R$ 53 mil)
só cabe com R$ 50 mil.

**Resultado.** A primeira versão (que também comprava a backwardation) perdeu o capital inteiro até 2019 (picos de inverno de 2008/2018) —
trocada por "só vendido" + teto de vol (1 contrato não pode ter vol > 35% do capital). IS escolheu o sazonal; OOS −5,6 pp com R$ 20 mil
e +1,4 com R$ 50 mil. **Por que falhou:** o contango do gás é conhecido e já está no preço do 2º vencimento; o que sobra é a vol do gás
(60-80% a.a.) contra 1 contrato inteiro — 2024-25 (inverno frio, exportação de GNL) fizeram −14 e −12 pp.

Parâmetros (IS): `{'modo': 'gas_sazonal', 'lim': 0.02}`. Grade (ativo pp, R$ 20 mil):

| variante | IS | OOS |
|---|---|---|
| {'modo': 'gas_curva', 'lim': 0.02} | +0.5 | -6.3 |
| {'modo': 'gas_sazonal', 'lim': 0.02} | +2.0 | -5.6 |
| {'modo': 'gas_sazonal', 'lim': 0.05} | +2.0 | -5.6 |
| {'modo': 'gas_curva', 'lim': 0.05} | -0.1 | -2.6 |
| {'modo': 'petroleo_curva', 'lim': 0.05} | -0.7 | -0.2 |
| {'modo': 'petroleo_curva', 'lim': 0.02} | -2.1 | -0.2 |

10 melhores negócios (R$ 20 mil; contribuição em pp do PL):

| ativo | lado | entrada | saída | dias | contratos | retorno % | contrib pp |
|---|---|---|---|---|---|---|---|
| MNG | -1 | 2008-07-17 | 2008-09-18 | 46 | 1 | +45.4 | +31.3 |
| MNG | -1 | 2009-03-02 | 2009-09-30 | 153 | 1 | +16.7 | +14.0 |
| MNG | -1 | 2010-03-01 | 2010-09-30 | 154 | 1 | +27.9 | +11.8 |
| MNG | -1 | 2019-03-01 | 2019-09-30 | 152 | 1 | +19.2 | +10.0 |
| MNG | -1 | 2026-06-03 | 2026-09-30 | 86 | 1 | +7.2 | +8.1 |
| MNG | -1 | 2015-03-02 | 2015-09-30 | 153 | 1 | +10.4 | +7.3 |
| MNG | -1 | 2014-03-03 | 2014-09-30 | 152 | 1 | +10.1 | +5.9 |
| MNG | -1 | 2011-03-01 | 2011-09-30 | 154 | 1 | +12.1 | +5.3 |
| MNG | -1 | 2024-05-28 | 2024-05-31 | 4 | 1 | +7.6 | +4.9 |
| MNG | -1 | 2024-07-15 | 2024-07-15 | 1 | 1 | +6.6 | +4.1 |

10 piores negócios (R$ 20 mil; contribuição em pp do PL):

| ativo | lado | entrada | saída | dias | contratos | retorno % | contrib pp |
|---|---|---|---|---|---|---|---|
| MNG | -1 | 2016-03-01 | 2016-09-30 | 154 | 1 | -35.0 | -14.5 |
| MNG | -1 | 2024-07-26 | 2024-09-30 | 47 | 1 | -18.4 | -11.6 |
| MNG | -1 | 2008-03-03 | 2008-04-29 | 42 | 1 | -13.9 | -10.4 |
| MNG | -1 | 2026-05-04 | 2026-05-29 | 20 | 1 | -11.5 | -8.2 |
| MNG | -1 | 2024-03-01 | 2024-05-16 | 55 | 1 | -13.2 | -7.2 |
| MNG | -1 | 2018-03-01 | 2018-09-28 | 152 | 1 | -12.0 | -6.3 |
| MNG | -1 | 2020-09-23 | 2020-09-24 | 2 | 1 | -10.0 | -5.4 |
| MNG | -1 | 2008-05-02 | 2008-05-06 | 3 | 1 | -4.8 | -4.2 |
| MNG | -1 | 2025-08-27 | 2025-08-28 | 2 | 1 | -4.9 | -3.9 |
| MNG | -1 | 2025-09-22 | 2025-09-30 | 7 | 1 | -4.0 | -3.3 |

Alavancagem: 1x R$ 20 mil: -5.6 pp, pior queda -20%; 1x R$ 50 mil: +1.4 pp, pior queda -11%; 2x R$ 20 mil: +2.8 pp, pior queda -53%; 2x R$ 50 mil: +4.6 pp, pior queda -24%

### Bitcoin B3 (BIT) na liquidação dos perpétuos: funding negativo + queda (`fu_b3_cripto_panico`)

**Tese.** Cascata de liquidação dos perpétuos offshore (queda forte + funding negativo) = vendedor forçado; compro o BIT da B3
(0,01 BTC desde jun/2025 ≈ R$ 4,1 mil; antes 0,1 BTC) com garantia em Tesouro Selic, sem remessa, e seguro H dias.

**Dados.** BTC no fechamento da B3 (Binance 1h x PTAX), funding 8h da Binance (2019+), BIT real (boletim B3) desde abr/2024; antes,
sintético = BTC em R$ − CDI − 3% a.a. de base. Custo 0,10%/lado. (WSP e mini euro WEU: sem base explorável com dado diário; ETR/SOL
só desde jun/2025.)

**Resultado.** IS (2019-22) escolheu "liquidação" k=1,5/H=5; OOS −6,5 / −5,2 pp, só 4 negócios OOS; placebo p = 0,97.
**Por que falhou:** depois de 2023 as cascatas viraram ponto de PARTIDA de quedas maiores (ago/2024, fev/2026), não o fundo: com ETFs
à vista dominando, o resgate continua por dias. Poucos eventos: estatisticamente nada.

Parâmetros (IS): `{'modo': 'liquidacao', 'k': 1.5, 'H': 5}`. Grade (ativo pp, R$ 20 mil):

| variante | IS | OOS |
|---|---|---|
| {'modo': 'liquidacao', 'k': 1.5, 'H': 5} | +9.1 | -6.5 |
| {'modo': 'liquidacao', 'k': 2.0, 'H': 5} | +8.2 | -6.4 |
| {'modo': 'liquidacao', 'k': 2.0, 'H': 10} | +0.1 | -4.5 |
| {'modo': 'queda', 'k': 2.0, 'H': 5} | +1.3 | -3.7 |
| {'modo': 'queda', 'k': 2.0, 'H': 10} | -9.2 | -3.2 |
| {'modo': 'liquidacao', 'k': 1.5, 'H': 10} | +2.6 | -3.1 |
| {'modo': 'queda', 'k': 1.5, 'H': 5} | -19.0 | +3.1 |
| {'modo': 'queda', 'k': 1.5, 'H': 10} | -7.3 | +30.1 |

10 melhores negócios (R$ 20 mil; contribuição em pp do PL):

| ativo | lado | entrada | saída | dias | contratos | retorno % | contrib pp |
|---|---|---|---|---|---|---|---|
| BIT | +1 | 2020-03-17 | 2020-03-24 | 6 | 8 | +38.8 | +33.0 |
| BIT | +1 | 2022-02-23 | 2022-03-03 | 5 | 1 | +10.3 | +9.7 |
| BIT | +1 | 2021-06-23 | 2021-06-30 | 6 | 1 | +6.7 | +5.3 |
| BIT | +1 | 2022-03-09 | 2022-03-15 | 5 | 1 | +3.7 | +3.5 |
| BIT | +1 | 2026-06-29 | 2026-07-03 | 5 | 7 | +2.9 | +3.1 |
| BIT | +1 | 2026-06-09 | 2026-06-15 | 5 | 6 | +2.4 | +2.2 |
| BIT | +1 | 2019-11-27 | 2019-12-03 | 5 | 7 | +1.3 | +2.0 |
| BIT | +1 | 2022-06-17 | 2022-06-27 | 7 | 2 | -1.9 | -2.3 |
| BIT | +1 | 2021-05-21 | 2021-05-27 | 5 | 1 | -3.6 | -4.0 |
| BIT | +1 | 2024-08-09 | 2024-08-15 | 5 | 1 | -5.9 | -10.2 |

10 piores negócios (R$ 20 mil; contribuição em pp do PL):

| ativo | lado | entrada | saída | dias | contratos | retorno % | contrib pp |
|---|---|---|---|---|---|---|---|
| BIT | +1 | 2026-02-04 | 2026-02-18 | 9 | 6 | -13.6 | -14.0 |
| BIT | +1 | 2022-11-11 | 2022-11-21 | 6 | 2 | -12.8 | -12.5 |
| BIT | +1 | 2024-08-09 | 2024-08-15 | 5 | 1 | -5.9 | -10.2 |
| BIT | +1 | 2021-05-21 | 2021-05-27 | 5 | 1 | -3.6 | -4.0 |
| BIT | +1 | 2022-06-17 | 2022-06-27 | 7 | 2 | -1.9 | -2.3 |
| BIT | +1 | 2019-11-27 | 2019-12-03 | 5 | 7 | +1.3 | +2.0 |
| BIT | +1 | 2026-06-09 | 2026-06-15 | 5 | 6 | +2.4 | +2.2 |
| BIT | +1 | 2026-06-29 | 2026-07-03 | 5 | 7 | +2.9 | +3.1 |
| BIT | +1 | 2022-03-09 | 2022-03-15 | 5 | 1 | +3.7 | +3.5 |
| BIT | +1 | 2021-06-23 | 2021-06-30 | 6 | 1 | +6.7 | +5.3 |

Alavancagem: 1x R$ 20 mil: -6.5 pp, pior queda -16%; 1x R$ 50 mil: -5.2 pp, pior queda -16%; 2x R$ 20 mil: -11.2 pp, pior queda -40%; 2x R$ 50 mil: -11.4 pp, pior queda -40%

### Agro B3: spread safra x entressafra (milho: vende setembro, compra março+1) (`fu_agro_spread`)

**Tese inicial (errada no IS).** Comprar o vencimento que o hedger natural vende (BGI out., CCM set., ICF set.) contra o vizinho.

**O que o IS (2018-22) escolheu.** CCM com lado −1: VENDIDO no milho de setembro (safrinha) e COMPRADO no março seguinte, de março a agosto.

**Negócio.** O spread H(+1) − U abre de ~R$ 7/saca em março para ~R$ 10-11 em agosto em 8 de 9 safras (2020 é a exceção). 1 spread =
450 sacas: R$ 3/saca = R$ 1.350 = 6,8% de R$ 20 mil. Quem paga: (i) o produtor de safrinha vende setembro AO LONGO da janela conforme a
lavoura se confirma (fluxo previsível que comprime o U), e (ii) o consumidor (integradoras de frango/suíno, usinas de etanol de milho)
paga prêmio de clima no setembro no plantio da safrinha, quando o risco de quebra é máximo; com safra normal o prêmio derrete até
agosto. Andamos junto com o vendedor do U e vendemos o seguro de clima; o milho da entressafra comprado protege da quebra.

**Robustez.** OOS +11,7 pp (R$ 20 mil) / +4,7 (R$ 50 mil com 1 spread; 2 spreads = +9,4); depois do IR +9,6 / +3,9; IR 0,84; PBO 17%;
P(bater 3a) 96%; custo 2x +11,5 (2 lados x 2 pernas por ano); t+2 +11,6; janela deslocada (abr-ago, mar-jul, fev-ago, mai-ago) sempre
positiva no OOS (+7,7 a +12,0). Fraquezas: só 9 safras (4 OOS: +16, +1, +7, +17 pp); sem os 3 melhores +1,2 pp; placebo p = 0,14 (o
deslocamento de 1+ ano preserva parte da sazonalidade); pior queda −25% com R$ 20 mil (2020). BGI e ICF: o spread é dominado por
choques (geada/seca do café em 2021, ciclo do boi) e perdem nos dois lados.

Parâmetros (IS): `{'produto': 'CCM', 'lado': -1}`. Grade (ativo pp, R$ 20 mil):

| variante | IS | OOS |
|---|---|---|
| {'produto': 'todos', 'lado': 1} | -11.1 | -38.3 |
| {'produto': 'ICF', 'lado': -1} | -6.2 | -25.8 |
| {'produto': 'todos', 'lado': -1} | -9.9 | -14.9 |
| {'produto': 'CCM', 'lado': 1} | -9.0 | -12.8 |
| {'produto': 'BGI', 'lado': 1} | +4.0 | -11.9 |
| {'produto': 'ICF', 'lado': 1} | -6.6 | -8.9 |
| {'produto': 'BGI', 'lado': -1} | -9.0 | +2.7 |
| {'produto': 'CCM', 'lado': -1} | +5.0 | +11.7 |

10 melhores negócios (R$ 20 mil; contribuição em pp do PL):

| ativo | lado | entrada | saída | dias | contratos | retorno % | contrib pp |
|---|---|---|---|---|---|---|---|
| CCM spread | -1 | 2022-03-04 | 2022-08-31 | 126 | 1 | +8.9 | +24.1 |
| CCM spread | -1 | 2026-03-04 | 2026-08-31 | 125 | 1 | +9.1 | +16.7 |
| CCM spread | -1 | 2023-03-03 | 2023-08-31 | 126 | 1 | +26.8 | +16.3 |
| CCM spread | -1 | 2021-03-03 | 2021-06-11 | 70 | 1 | +9.6 | +15.0 |
| CCM spread | -1 | 2025-03-07 | 2025-08-29 | 122 | 1 | +4.3 | +6.7 |
| CCM spread | -1 | 2018-03-05 | 2018-07-10 | 89 | 1 | +5.4 | +5.2 |
| CCM spread | -1 | 2019-03-28 | 2019-07-10 | 72 | 1 | +1.0 | +2.2 |
| CCM spread | -1 | 2024-03-05 | 2024-08-30 | 126 | 1 | -0.9 | +1.4 |
| CCM spread | -1 | 2021-07-14 | 2021-08-31 | 35 | 1 | +0.2 | +1.0 |
| CCM spread | -1 | 2019-07-12 | 2019-08-30 | 36 | 1 | -1.3 | -0.8 |

10 piores negócios (R$ 20 mil; contribuição em pp do PL):

| ativo | lado | entrada | saída | dias | contratos | retorno % | contrib pp |
|---|---|---|---|---|---|---|---|
| CCM spread | -1 | 2020-03-26 | 2020-08-31 | 109 | 1 | -2.2 | -9.8 |
| CCM spread | -1 | 2021-06-15 | 2021-07-12 | 20 | 1 | -3.3 | -2.5 |
| CCM spread | -1 | 2018-07-12 | 2018-08-31 | 37 | 1 | -2.3 | -2.0 |
| CCM spread | -1 | 2019-07-12 | 2019-08-30 | 36 | 1 | -1.3 | -0.8 |
| CCM spread | -1 | 2021-07-14 | 2021-08-31 | 35 | 1 | +0.2 | +1.0 |
| CCM spread | -1 | 2024-03-05 | 2024-08-30 | 126 | 1 | -0.9 | +1.4 |
| CCM spread | -1 | 2019-03-28 | 2019-07-10 | 72 | 1 | +1.0 | +2.2 |
| CCM spread | -1 | 2018-03-05 | 2018-07-10 | 89 | 1 | +5.4 | +5.2 |
| CCM spread | -1 | 2025-03-07 | 2025-08-29 | 122 | 1 | +4.3 | +6.7 |
| CCM spread | -1 | 2021-03-03 | 2021-06-11 | 70 | 1 | +9.6 | +15.0 |

Alavancagem: 1x R$ 20 mil: +11.7 pp, pior queda -25%; 1x R$ 50 mil: +4.7 pp, pior queda -10%; 2x R$ 20 mil: +22.6 pp, pior queda -45%; 2x R$ 50 mil: +9.4 pp, pior queda -20%

### Brasil x S&P: WIN no pânico relativo (resíduo do Ibovespa em US$) (`fu_brasil_relativo`)

**Tese.** Estrangeiro vendendo "Brasil" de uma vez: compro 1 WIN (R$ 0,20 x Ibov ≈ R$ 41 mil) quando o resíduo do Ibovespa em US$
contra beta x S&P cai k desvios em 5 dias, com hedge em MES. **O hedge não cabe:** 1 MES ≈ R$ 210 mil (5x 1 WIN, 10x R$ 20 mil) e o WSP
da B3 ≈ R$ 105 mil — o nº inteiro de MES arredonda para zero desde 2019.

**Resultado.** Todas as variantes perdem no IS; o "relativo" perde MAIS que o controle de queda absoluta (escolhido no IS). OOS −0,3 /
+0,7 pp, pior queda −38%. **Por que falhou:** sem hedge, é WIN comprado em quedas (beta de Brasil com 2x o capital); o "resíduo" do
Brasil é persistente (fiscal 2015, 2024) — o estrangeiro que sai não volta em 5 dias. Petróleo x PETR4 já é o mh_petroleo (top 5).

Parâmetros (IS): `{'modo': 'abs', 'k': 1.5, 'H': 5}`. Grade (ativo pp, R$ 20 mil):

| variante | IS | OOS |
|---|---|---|
| {'modo': 'rel', 'k': 1.5, 'H': 10} | -6.8 | -7.1 |
| {'modo': 'rel', 'k': 1.5, 'H': 5} | -3.3 | -5.9 |
| {'modo': 'rel', 'k': 2.0, 'H': 5} | -2.8 | -3.1 |
| {'modo': 'abs', 'k': 1.5, 'H': 10} | -5.6 | -2.2 |
| {'modo': 'abs', 'k': 2.0, 'H': 5} | -4.6 | -2.0 |
| {'modo': 'rel', 'k': 2.0, 'H': 10} | -6.8 | -1.5 |
| {'modo': 'abs', 'k': 1.5, 'H': 5} | -0.6 | -0.3 |
| {'modo': 'abs', 'k': 2.0, 'H': 10} | -10.3 | -0.2 |

10 melhores negócios (R$ 20 mil; contribuição em pp do PL):

| ativo | lado | entrada | saída | dias | contratos | retorno % | contrib pp |
|---|---|---|---|---|---|---|---|
| WIN | +1 | 2008-10-28 | 2008-11-05 | 7 | 3 | +27.9 | +24.7 |
| WIN | +1 | 2016-04-08 | 2016-04-14 | 5 | 2 | +7.8 | +7.5 |
| WIN | +1 | 2010-05-20 | 2010-05-31 | 8 | 2 | +5.3 | +6.4 |
| WIN | +1 | 2012-06-28 | 2012-07-05 | 6 | 2 | +6.0 | +6.3 |
| WIN | +1 | 2022-10-03 | 2022-10-07 | 5 | 1 | +5.5 | +6.0 |
| WIN | +1 | 2011-11-25 | 2011-12-01 | 5 | 2 | +5.0 | +5.5 |
| WIN | +1 | 2015-03-12 | 2015-03-18 | 5 | 2 | +5.1 | +5.0 |
| WIN | +1 | 2018-02-14 | 2018-02-20 | 5 | 1 | +5.9 | +4.8 |
| WIN | +1 | 2013-09-03 | 2013-09-09 | 5 | 2 | +4.5 | +4.6 |
| WIN | +1 | 2010-07-02 | 2010-07-13 | 8 | 2 | +3.7 | +4.5 |

10 piores negócios (R$ 20 mil; contribuição em pp do PL):

| ativo | lado | entrada | saída | dias | contratos | retorno % | contrib pp |
|---|---|---|---|---|---|---|---|
| WIN | +1 | 2020-02-28 | 2020-03-31 | 23 | 2 | -29.4 | -25.1 |
| WIN | +1 | 2013-06-04 | 2013-07-03 | 22 | 2 | -17.0 | -18.5 |
| WIN | +1 | 2008-10-01 | 2008-10-20 | 14 | 3 | -21.0 | -13.4 |
| WIN | +1 | 2018-05-23 | 2018-06-21 | 21 | 1 | -15.7 | -13.1 |
| WIN | +1 | 2016-01-11 | 2016-01-26 | 12 | 3 | -8.3 | -9.0 |
| WIN | +1 | 2022-06-13 | 2022-07-01 | 14 | 1 | -6.8 | -7.2 |
| WIN | +1 | 2024-12-18 | 2025-01-03 | 11 | 1 | -5.4 | -6.8 |
| WIN | +1 | 2026-03-05 | 2026-03-17 | 9 | 1 | -3.2 | -5.9 |
| WIN | +1 | 2022-04-26 | 2022-05-05 | 8 | 1 | -5.2 | -5.8 |
| WIN | +1 | 2014-10-20 | 2014-11-04 | 12 | 2 | -2.9 | -3.2 |

Alavancagem: 1x R$ 20 mil: -0.3 pp, pior queda -38%; 1x R$ 50 mil: +0.7 pp, pior queda -42%; 2x R$ 20 mil: +0.3 pp, pior queda -78%; 2x R$ 50 mil: +0.5 pp, pior queda -75%

### Micro Treasury Yield: concessão de leilão (30Y/10Y) e curva 2s10s (`fu_treasury_micro`)

**Tese.** Concessão de leilão do Tesouro (Lou, Yan & Zhang 2013): dealers abrem balanço antes do leilão; comprado em yield do
micro de 30 anos (ou 10 anos) do anúncio até o leilão, opcionalmente vendido depois; "curva" 2s10s com 10Y x 2YY (ambos US$ 10/bp) pelo
ciclo do Fed. **Contratos.** Micro Treasury Yield 2YY/10Y/30Y (CME, ago/2021), US$ 10/bp, tick US$ 1, margem ~US$ 290-400, custo US$
1,62/lado; o Micro Ultra Bond (preço, mar/2024) ficou de fora (mesma exposição, histórico curto). Leilões: TreasuryDirect (data de ANÚNCIO).

**Resultado.** IS escolheu leilão de 10 anos + 3 dias de devolução; OOS −7,4 / −2,9 pp; placebo p = 0,79. A variante 30 anos sem
devolução foi +3,2 pp OOS mas não seria a escolhida. **Por que falhou:** a concessão é conhecida e arbitrada pelos próprios dealers;
em 2022-23 o yield subia todo dia (Fed) e a "devolução" pós-leilão virou perda (−14 e −20 pp). 2s10s pelo Fed: a curva já embute o ciclo.

Parâmetros (IS): `{'modo': 'leilao10', 'pos': 3}`. Grade (ativo pp, R$ 20 mil):

| variante | IS | OOS |
|---|---|---|
| {'modo': 'leilao10', 'pos': 3} | +4.5 | -7.4 |
| {'modo': 'curva', 'pos': 0} | +0.7 | -4.5 |
| {'modo': 'curva', 'pos': 3} | +0.7 | -4.5 |
| {'modo': 'leilao30', 'pos': 3} | +1.7 | -4.5 |
| {'modo': 'leilao10', 'pos': 0} | +1.8 | -0.9 |
| {'modo': 'leilao30', 'pos': 0} | +1.6 | +3.1 |

10 melhores negócios (R$ 20 mil; contribuição em pp do PL):

| ativo | lado | entrada | saída | dias | contratos | retorno % | contrib pp |
|---|---|---|---|---|---|---|---|
| 10Y | -1 | 2023-03-09 | 2023-03-13 | 3 | 1 | +3.5 | +11.0 |
| 10Y | +1 | 2025-04-07 | 2025-04-09 | 3 | 1 | +2.7 | +9.6 |
| 10Y | -1 | 2023-12-12 | 2023-12-14 | 3 | 1 | +2.5 | +7.6 |
| 10Y | -1 | 2022-11-10 | 2022-11-14 | 3 | 1 | +1.9 | +6.1 |
| 10Y | +1 | 2023-02-03 | 2023-02-08 | 4 | 1 | +1.9 | +5.7 |
| 10Y | +1 | 2024-02-02 | 2024-02-07 | 4 | 1 | +1.8 | +5.4 |
| 10Y | +1 | 2020-11-06 | 2020-11-10 | 3 | 1 | +1.5 | +5.1 |
| 10Y | -1 | 2024-06-12 | 2024-06-14 | 3 | 1 | +1.5 | +5.0 |
| 10Y | +1 | 2022-03-07 | 2022-03-09 | 3 | 1 | +1.6 | +4.9 |
| 10Y | +1 | 2025-02-07 | 2025-02-12 | 4 | 1 | +1.4 | +4.8 |

10 piores negócios (R$ 20 mil; contribuição em pp do PL):

| ativo | lado | entrada | saída | dias | contratos | retorno % | contrib pp |
|---|---|---|---|---|---|---|---|
| 10Y | -1 | 2022-06-09 | 2022-06-13 | 3 | 1 | -3.2 | -9.9 |
| 10Y | +1 | 2023-10-09 | 2023-10-11 | 3 | 1 | -1.6 | -5.2 |
| 10Y | -1 | 2022-03-10 | 2022-03-14 | 3 | 1 | -1.6 | -5.0 |
| 10Y | +1 | 2023-07-10 | 2023-07-12 | 3 | 1 | -1.6 | -4.9 |
| 10Y | +1 | 2023-08-04 | 2023-08-09 | 4 | 1 | -1.6 | -4.9 |
| 10Y | -1 | 2023-04-13 | 2023-04-17 | 3 | 1 | -1.5 | -4.8 |
| 10Y | -1 | 2023-08-10 | 2023-08-14 | 3 | 1 | -1.5 | -4.7 |
| 10Y | +1 | 2023-11-03 | 2023-11-08 | 4 | 1 | -1.4 | -4.5 |
| 10Y | +1 | 2025-08-01 | 2025-08-06 | 4 | 1 | -1.2 | -4.3 |
| 10Y | -1 | 2024-12-12 | 2024-12-16 | 3 | 1 | -1.0 | -4.0 |

Alavancagem: 1x R$ 20 mil: -7.4 pp, pior queda -28%; 1x R$ 50 mil: -2.9 pp, pior queda -9%; 2x R$ 20 mil: -15.9 pp, pior queda -53%; 2x R$ 50 mil: -5.8 pp, pior queda -22%; 5x R$ 20 mil: -45.7 pp, pior queda -93%; 5x R$ 50 mil: -15.9 pp, pior queda -53%

### Peso mexicano e rande na B3 (MEX/AFS, US$ 10 mil): carry e compra depois do pânico (`fu_moedas_em`)

**Tese.** MXN/ZAR apanham demais nas crises (stop de carry, hedge de carteiras EM); compro a moeda pelo futuro da B3 em USD depois
de alta de k desvios do dólar, carregando o juro.

**Contratos e custo REAL.** MEX e AFS (B3): US$ 10 mil, cotação em MXN/ZAR por US$ 1.000, tick 1,00. Boletim BVBG.086 de 4 datas
(mar/2025, jun, set e out/2026): MEX 0-7 negócios/dia em blocos de 40-720 contratos (rolagem institucional), AFS 0-1; NENHUMA oferta no
livro no fechamento. Para PF não há tela (RFQ/formador; a maioria das corretoras não habilita): custo assumido 0,30% do nocional + R$ 2
por lado, vencimento trimestral. CME 6M/6Z (500 mil MXN/ZAR ≈ R$ 150 mil, sem micro) não cabe. APLICAVEL = False.

**Resultado.** Tudo perde no IS (carry de MXN/ZAR em US$ 2008-20 ≈ 0 antes de custo; ZAR −16% em 2015-16, −28% em 2008). Com R$ 20 mil
o teto de vol quase nunca deixa operar no OOS (−0,2 pp); com R$ 50 mil −5,2 pp.

Parâmetros (IS): `{'modo': 'pos_panico', 'k': 2.0, 'H': 10}`. Grade (ativo pp, R$ 20 mil):

| variante | IS | OOS |
|---|---|---|
| {'modo': 'pos_panico', 'k': 1.5, 'H': 10} | -9.1 | -0.2 |
| {'modo': 'pos_panico', 'k': 1.5, 'H': 20} | -9.5 | -0.2 |
| {'modo': 'pos_panico', 'k': 2.0, 'H': 10} | -9.1 | -0.2 |
| {'modo': 'pos_panico', 'k': 2.0, 'H': 20} | -11.0 | -0.2 |
| {'modo': 'carry', 'k': 1.5, 'H': 10} | -10.3 | -0.2 |
| {'modo': 'carry', 'k': 1.5, 'H': 20} | -10.3 | -0.2 |
| {'modo': 'carry', 'k': 2.0, 'H': 10} | -10.3 | -0.2 |
| {'modo': 'carry', 'k': 2.0, 'H': 20} | -10.3 | -0.2 |

10 melhores negócios (R$ 20 mil; contribuição em pp do PL):

| ativo | lado | entrada | saída | dias | contratos | retorno % | contrib pp |
|---|---|---|---|---|---|---|---|
| MEX | +1 | 2022-03-10 | 2022-03-24 | 11 | 1 | +5.9 | +13.5 |
| MEX | +1 | 2017-12-27 | 2018-01-09 | 10 | 1 | +3.5 | +5.1 |
| AFS | +1 | 2011-09-22 | 2011-10-10 | 13 | 1 | +5.5 | +4.9 |
| MEX | +1 | 2021-11-29 | 2021-12-15 | 13 | 1 | +2.2 | +4.9 |
| MEX | +1 | 2016-06-16 | 2016-06-30 | 11 | 1 | +3.2 | +4.8 |
| MEX | +1 | 2019-06-05 | 2019-06-18 | 10 | 1 | +2.6 | +4.2 |
| MEX | +1 | 2013-06-21 | 2013-07-09 | 13 | 1 | +4.2 | +4.2 |
| AFS | +1 | 2011-03-21 | 2011-04-01 | 10 | 1 | +4.9 | +3.7 |
| MEX | +1 | 2022-06-15 | 2022-07-04 | 14 | 1 | +1.8 | +3.4 |
| AFS | +1 | 2014-11-11 | 2014-11-24 | 10 | 1 | +2.8 | +3.1 |

10 piores negócios (R$ 20 mil; contribuição em pp do PL):

| ativo | lado | entrada | saída | dias | contratos | retorno % | contrib pp |
|---|---|---|---|---|---|---|---|
| AFS | +1 | 2008-10-06 | 2008-10-22 | 13 | 1 | -21.3 | -23.8 |
| MEX | +1 | 2020-02-26 | 2020-03-10 | 10 | 1 | -8.3 | -20.3 |
| AFS | +1 | 2020-03-04 | 2020-03-13 | 8 | 1 | -6.9 | -17.5 |
| MEX | +1 | 2008-10-03 | 2008-10-16 | 10 | 1 | -12.5 | -12.5 |
| MEX | +1 | 2023-09-29 | 2023-10-24 | 18 | 1 | -3.5 | -10.0 |
| AFS | +1 | 2022-04-25 | 2022-05-06 | 10 | 1 | -3.7 | -9.8 |
| AFS | +1 | 2026-03-06 | 2026-03-13 | 6 | 1 | -2.6 | -7.5 |
| MEX | +1 | 2018-04-25 | 2018-05-23 | 21 | 1 | -3.7 | -7.5 |
| MEX | +1 | 2018-10-26 | 2018-11-29 | 25 | 1 | -3.4 | -7.0 |
| AFS | +1 | 2018-06-13 | 2018-06-28 | 12 | 1 | -3.2 | -6.9 |

Alavancagem: 1x R$ 20 mil: -0.2 pp, pior queda -42%; 1x R$ 50 mil: -5.2 pp, pior queda -37%; 2x R$ 20 mil: -0.2 pp, pior queda -67%; 2x R$ 50 mil: -0.2 pp, pior queda -46%

## O que deu certo e por quê
- **Spread safra x entressafra do milho (CCM)** é o único com cara de prêmio: não é beta (as duas pernas são milho), custo irrelevante,
  robusto a janela e a atraso, e tem um pagador concreto — o produtor de safrinha vendendo setembro ao longo da janela e o consumidor
  pagando seguro de clima no plantio. Mas são 9 safras: candidato, não fato. Com R$ 50 mil, 2 spreads.
- **Pânico europeu com micro Euro STOXX 50**: pequeno (+1,7/+2,2 pp), placebo significativo (p = 0,04), coerente com o top 5 (vendedor
  forçado + tamanho pequeno), mas depende de poucos rebotes e sofre em crises que continuam (mar/2020).

## O que deu errado
- Contrato grande demais continua matando: FDXS, mini-KOSPI, MES, MCL (com R$ 20 mil), CME 6M/6Z; o gás micro "cabe" em nocional mas não
  em vol (quebrou o capital sem teto de vol).
- Pânicos em mercados muito arbitrados (Nikkei, Bitcoin pós-ETF, Treasuries) não pagam com fechamento diário e execução t+1: o rebote
  acontece antes de entrarmos.
- Moedas EM na B3: o contrato existe, mas não há livro — o custo real é desconhecido e provavelmente maior que o assumido.
- A tese ex-ante do agro (comprar o vencimento hedgeado) estava ERRADA no IS; o que funcionou foi o lado oposto, e só no milho. Registrado.

## Bugs / cuidados
- A EIA parou de publicar os vencimentos da NYMEX em abr/2024: estimador causal da curva (salto do contínuo − ETF), validado 2007-24.
- Primeira versão do gás comprava a backwardation e quebrou (−100% do capital até 2019): lado comprado removido + teto de vol.
- Leilões do Tesouro: posição até o fim dos dados quando o leilão é depois do corte (senão o truncamento falhava); evento = data de anúncio.
- Agro: janela de calendário em t e t+2 dias úteis (sem olhar se o contrato terá ajuste); negócios agrupados por spread (as pernas
  separadas inflavam "melhores/piores").
- Micros antes do lançamento são hipotéticos; no OOS só operam depois de lançados (MNG nov/2023, Nikkei Micro mai/2023, BIT abr/2024...).

## Próximos passos
1. CCM: incluir 2010-2017 (boletins B3 antigos) para ter 16+ safras; testar soja (SJC/SOY) e o milho da CME na mesma janela.
2. Euro STOXX: usar o nível das barreiras de autocalls (emissões publicadas) em vez do V2X como gatilho.
3. Moedas EM: pedir cotação real (RFQ) de MEX/AFS em uma corretora antes de qualquer teste adicional.
