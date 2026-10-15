# Correções finais — 4 fundos PF que quebravam na bateria

Reproduzir: `PYTHONIOENCODING=utf-8 python -W ignore pf/rodar_pf.py um <nome>` (os 4 terminam sem erro; truncamento passa nas 3 datas).
Baterias em `pf/resultados/bateria/<nome>.pkl`. "IR" abaixo = information ratio OOS contra o CDI; "depois do IR" = depois do imposto
(regra única do `rodar_pf.apos_ir`, alíquota pela `CLASSE_IR`, que agora está declarada nos 4 módulos).

## 1. Causa comum dos 3 erros de índice (fracionário, OPA, units)
`robustez.teste_truncamento` passa `corta(d, T)`: os painéis (P, R, BID, ASK, V...) ficam **mais curtos** que `B.DIAS`, mas os módulos
indexavam por posição (`P.values[ie, j]`, `R[t].iloc[j]`) usando o tamanho de `B.DIAS`. Com t+1 ou um prazo de saída depois do corte,
o índice passava do fim → `index 3476 is out of bounds` / `single positional indexer is out-of-bounds`. **Correção:** os painéis são
reindexados para `B.DIAS` no início de `_eventos`/`roda`. Depois do corte os preços viram NaN e o negócio não é executado/marcado.
Não houve try/except. Em `gl_cripto_premio` o erro `argmax of an empty sequence` vinha de `bit_continuo` com o futuro BIT ainda não
listado no corte (tabela sem colunas). **Correção:** sem contrato listado → sem hedge (série NaN → P&L de hedge zero), o que é o fato real.

Com isso a bateria rodou, mas a auditoria dos negócios mostrou que 2 dos 4 tinham uma falha de **desenho**, não só de código:

## 2. b3_fracionario — falha de desenho, marcado APLICAVEL=False
- **O que estava errado:** a venda limitada no fracionário executava "em algum momento" de t+1 (máxima do dia acima do limite), e a
  recompra do lote saía no **fechamento**. As pernas não eram simultâneas: o P&L era o movimento intradiário de small caps, não o prêmio.
  Melhores negócios da versão original: AZEV3 +104% em 28/08/2026 (a ação caiu 50% no dia), SIMH3 -50%, MMXM3 ±25%. O lado
  "vendo fracionário" ganhava e o lado "compro fracionário" perdia: era uma aposta vendida intradiária. Sinal de bug: IR OOS 1,47 com
  IS 0,26, e t+2 = -27 pp a.a.
- **Correção:** `perna="abertura"` (padrão): a ordem só conta se o fracionário **abriu** além do limite (executa no limite) e o lote é
  comprado/vendido na **abertura do lote** (único instante em que o COTAHIST dá preço dos dois livros) pagando o meio spread de t.
  A versão original continua como `perna="fechamento"`.
- **Por que não é testável honestamente:** com execução no limite, o edge fica perto de zero (média por negócio de -0,6% no universo
  sem filtros; +0,94 pp a.a. com os filtros do fundo; placebo p = 1,0). Se o fracionário tiver leilão de abertura e a execução for
  no preço do leilão, a média vai para +1,7% por negócio, mas com sinal atrasado ela ainda dá +0,5% (viés de seleção do primeiro negócio de um livro fino).
  E com a minha ordem dentro do leilão, o preço seria outro. O COTAHIST não tem horário nem quantidade das ofertas. Fica **APLICAVEL=False**
  até haver dados intradiários (tick-by-tick dos dois livros).

| | antes (só truncamento corrigido) | depois (pernas simultâneas) |
|---|---|---|
| OOS vs CDI 20k / 50k (pp a.a.) | +9,72 / +7,71 | +0,94 / +0,72 |
| depois do IR 20k / 50k | +8,42 / +6,69 | +0,92 / +0,71 |
| IR OOS | 1,47 (suspeito) | 0,65 |
| PBO / P(bater 3a) | 0,4% / 99,8% | 17% / 86% |
| custo 2x / t+2 / sem 10 melhores | +8,5 / -26,6 / +6,1 | +0,68 / -24,9* / +0,31 |
| truncamento | passa | passa |

*t+2 é artefato da execução conservadora no limite velho (se o papel subiu, vende-se no limite antigo e recompra-se mais caro). A
corretora cancelaria a ordem num evento corporativo (o pior negócio, SIMH3 -49% em 18/02/2026, é o papel dobrando de preço com limite velho).

10 melhores OOS (depois): ARML3 10/05/23 +0,53 pp; IFCM3 18/08/21 +0,45; INEP4 29/04/21 +0,43; SMFT3 19/02/25 +0,40; ORVR3 06/10/23 +0,39;
CYRE4 21/01/26 +0,29; CARD3 11/05/21 +0,29; CPLE11 08/06/22 +0,29; VBBR3 19/07/24 +0,27; DEXP3 26/07/21 +0,27.
10 piores: SIMH3 18/02/26 -1,63; ENAT3 27/04/22 -0,51; MMXM3 30/03/21 -0,46; TEND3 26/11/21 -0,45; RCSL3 27/06/22 -0,42;
BRAV3 06/05/25 -0,39; DEXP3 29/06/21 -0,37; KEPL3 31/03/21 -0,37; AMOB3 05/10/26 -0,32; AMAR3 13/12/21 -0,30.
**Veredito:** o edge original era bug (as pernas não eram simultâneas). Não há edge comprovado.

## 3. b3_opa_leilao — só o erro de índice
| | 20k | 50k |
|---|---|---|
| OOS vs CDI (pp a.a.) | +4,10 (15,5% vs 11,4%) | +4,11 |
| depois do IR (isento: vendas < R$ 20 mil/mês) | +4,03 | +4,04 |
| IR OOS / PBO / P(bater 1-3-5a) | 0,54 / 36% / 75-88-93% | 0,54 |
| custo 2x / t+2 / sem 10 melhores / placebo p | +3,97 / +3,42 / **-2,25** / 0,045 | |
| truncamento | passa | |

18 negócios OOS. 10 melhores: AALR3 (Alliar, 300 pregões, +80%) +12,05 pp; HBOR3 (aberta, +48%) +7,24; NGRD3 (leilão R$ 33,82) +3,41;
BRAV3 (leilão R$ 23) +3,12; CRFB3 (incorporação, parou) +2,22; PORT3 (leilão R$ 18,53) +2,16; IGBR3 (leilão) +1,76; CBAV3 (aberta) +1,70;
SRNA3 (leilão) +1,68; ENBR3 (leilão) +1,21. Piores: FHER3 (leilão R$ 14,99, -15%) -2,20; BKBR3 -0,07; CIEL3 +0,22; EUCA4 +0,59;
NEOE3 +0,71; ZAMP3 +0,79; APER3 +0,80; MILS3 +1,11.
**Veredito:** plausível (prêmio de OPA + melhora do preço até o leilão, Sharpe 0,54), sem sinal de bug. Mas a amostra é pequena e o
resultado depende de 2 negócios longos (AALR3, HBOR3 ainda aberta), e fica negativo sem os 10 melhores. Ressalvas para o caderno da
frente: no IS há eventos que não são OPA do papel comprado (CMIG4 +95%, ALPA4 PN em troca de controle), e "prazo" vira posição direcional de 300 pregões.

## 4. b3_units — só o erro de índice; resultado negativo e honesto
| | 20k | 50k |
|---|---|---|
| OOS vs CDI (pp a.a.) | -12,51 (-1,1% vs 11,4%) | -8,08 |
| depois do IR | -12,32 | -7,96 |
| IR OOS / PBO / P(bater 1-3-5a) | -1,25 / 4% / 12-2-0% | -1,13 |
| custo 2x / t+2 / sem 10 melhores / placebo p | -12,8 / -7,5 / -16,6 / 0,86 | |
| truncamento | passa | |

87 negócios OOS. Melhores: BPAC11 31/08/26 +3,78 pp; RNEW11 30/11/21 +3,35; RNEW11 29/07/22 +2,76; BPAC11 30/06/21 +2,56; BPAC11 20/08/26 +2,34;
CPLE11 20/09/21 +1,91; CPLE11 01/12/21 +1,85; BPAC11 02/08/21 +1,76; BIDI11 13/06/22 +1,71; BPAC11 10/02/26 +1,66.
Piores: BIDI11 02/05/22 -7,99; RNEW11 24/02/21 -7,94; RNEW11 13/09/21 -7,02; RNEW11 22/08/22 -6,97; BPAC11 02/03/26 -4,89; BIDI11 26/05/22 -4,78;
SANB11 08/11/22 -4,61; BPAC11 12/08/21 -4,10; BPAC11 29/09/21 -3,58; BPAC11 10/11/21 -3,26.
**Veredito:** não há edge. O "desvio" de 2-10% vem de ofertas de fechamento dos componentes ilíquidos (BPAC5, RNEW4) que não são
executáveis. A operação vira ação comprada sem hedge por 5 pregões (desvio-padrão por negócio de 6,4%) e paga dois meios spreads largos (média de -1,6% por negócio).

## 5. gl_cripto_premio — erro de dados + falha de desenho corrigida
- **Erro:** BIT vazio no corte (ver item 1).
- **Falha de desenho:** a ordem era `justo de ONTEM x (1 - thr)`: todo desconto de entrada saía exatamente -2,47% (= e^-0,025 - 1), ou
  seja, só executava quando o próprio bitcoin/ether caía 2,5% no dia. Era comprar a queda do cripto, não o desconto do ETF.
- **Correção:** `_simula_fech` (padrão): desconto medido **no mesmo instante** (oferta de venda do ETF no fechamento contra BTC/ETH-BRL do
  candle de 1h que fecha no fechamento da B3 x razão mediana até a véspera). Execução em **t+1** na oferta de venda e saída na oferta
  de compra quando o desconto fecha (ou depois de `max_dias`). A versão antiga continua em `execucao="limite_vespera"`.
- Medição sem hedge: o desconto simultâneo existe e converge (+1,4% em 1 dia com thr 2,5%), mas **só no mesmo call**. Com t+1, a parte
  hedgeada (ETF menos cripto) cai para +0,0-0,6% por negócio, e o resto do retorno é beta de cripto (2021-22 negativo, 2023-24 positivo).

| | antes (só BIT corrigido) | depois (desconto simultâneo, t+1) |
|---|---|---|
| OOS vs CDI 20k / 50k (pp a.a.) | +4,32 / -2,04 | +2,28 / +2,28 |
| depois do IR 20k / 50k | +3,44 / — | +2,08 / +2,08 |
| IR OOS | 0,30 | 0,53 |
| PBO / P(bater 1-3-5a) | 1% / — | **66%** / 57-75-83% |
| custo 2x / t+2 / sem 10 melhores / placebo p | — | +2,19 / +3,08 / **-2,40** / 0,05 |
| truncamento | passa | passa |

24 negócios OOS. Melhores: QBTC11 23/02/24 +4,22 pp (+21%); QETH11 23/02/24 +3,23; QBTC11 14/03/23 +2,76; QETH11 13/01/23 +2,17; QBTC11 19/03/24 +1,35;
QBTC11 16/07/24 +1,08; QETH11 22/05/24 +1,02; QETH11 02/02/24 +0,98; QBTC11 15/02/24 +0,43; ETHE11 24/05/24 +0,37.
Piores: ETHE11 23/07/24 -1,85 (desconto de entrada -15%, provável quebra da razão); QETH11 09/04/24 -1,59; ETHE11 30/05/23 -1,47; QBTC11 09/04/24 -0,96;
ETHE11 14/03/23 -0,89; QBTC11 26/07/24 -0,88; QETH11 02/06/25 -0,84; QBTC11 23/01/23 -0,60; QBTC11 24/03/23 -0,23; BITH11 23/01/23 -0,20.
**Veredito:** não é edge de desconto. Os ganhos vêm das altas do cripto em 2023-24 (beta), com PBO de 66% e resultado negativo sem
os 10 melhores. O hedge com BIT só cabe na carteira desde 06/2025 (contrato de 0,01 BTC). O desconto real só seria capturável com uma ordem
atrelada ao NAV no próprio call de fechamento, e isso viola a regra de t+1 e não foi validado.

## Resumo
| fundo | aplicável | OOS 20k antes/depois IR | OOS 50k antes/depois IR | IR | PBO | P(bater 3a) | truncamento | edge |
|---|---|---|---|---|---|---|---|---|
| b3_fracionario | **não** | +0,94 / +0,92 | +0,72 / +0,71 | 0,65 | 17% | 86% | ok | não (o original era bug) |
| b3_opa_leilao | sim | +4,10 / +4,03 | +4,11 / +4,04 | 0,54 | 36% | 88% | ok | plausível, amostra pequena |
| b3_units | sim | -12,51 / -12,32 | -8,08 / -7,96 | -1,25 | 4% | 2% | ok | não |
| gl_cripto_premio | sim | +2,28 / +2,08 | +2,28 / +2,08 | 0,53 | 66% | 75% | ok | não (beta de cripto) |
Nenhum fundo tem Sharpe acima de 1,5 depois das correções.
