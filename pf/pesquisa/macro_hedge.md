# Frente PF "macro_hedge": macro e ações com hedge de commodity/índice (R$ 20–50 mil)

Código: `pf/fundos/mh_base.py` (dados + motor PF) e 7 fundos `pf/fundos/mh_*.py`; runner `pf/rodar_macro_hedge.py`
(`python pf/rodar_macro_hedge.py mh_petroleo ...` e `--juntar`). Resultados: `pf/resultados/macro_hedge.pkl` (lista de dicts com nome,
excesso 20k/50k antes e depois do IR, métricas, bateria, alavancagem, negócios, diagnóstico) e `pf/resultados/macro_hedge/<fundo>.txt`
(saída completa: grade, custo, atraso, truncamento, ano a ano, 10 melhores/piores negócios, por ativo, concentração).

> Pesquisa, não recomendação. Resultados simulados com custos de varejo estimados.

## Resumo (OOS = 2021+, agro 2023+; ativo = pp a.a. sobre o CDI; "depois do IR" = fundo líquido de IR contra CDI líquido de 15%)

| Fundo | Aplicável? | 20k antes | 20k depois IR | 50k antes | 50k depois IR | IR (inf.) 20k/50k | PBO 20k/50k | P(bater 3a) 20k/50k |
|---|---|---|---|---|---|---|---|---|
| mh_petroleo — PETR4/PRIO3 em pânico x MCL | Sim (MCL só sai do zero com 50k) | **+3,0** | **+2,8** | **+3,9** | **+3,4** | 0,36 / 0,47 | 10% / 20% | 76% / 79% |
| mh_real_tatico — juro real BR-EUA em WDO (+ pânico BR) | Só com 50k | −2,3 | −2,3 | **+4,8** | **+3,7** | −0,08 / 0,34 | 45% / 46% | 40% / 71% |
| mh_exportadoras — SUZB3/KLBN11/VALE3 atrasadas x WDO+WIN | Ações sim; hedge não cabe | −0,3 | −0,2 | −0,9 | −0,9 | −0,04 / −0,18 | 38% / 51% | 45% / 36% |
| mh_pares — pares intra-setor sem notícia, aluguel PF | Sim | −2,1 | −2,1 | −2,1 | −2,0 | −0,26 / −0,26 | 28% / 29% | 32% / 32% |
| mh_agro — margem nos futuros agro -> frigoríficos/SLC/SMTO | Sim (BGI nunca cabe) | −13,3 | −11,9 | −13,3 | −11,9 | −0,15 / −0,15 | 14% / 19% | 25% / 25% |
| mh_fuso_ewz — EWZ/ADR pós-B3, leilão de abertura (day trade) | Sim | −12,6 | −12,4 | −12,6 | −12,4 | −0,81 / −0,81 | 9% / 9% | 6% / 6% |
| mh_evento_beta — fato relevante não-balanço, beta em WIN | Sim (WIN só com 50k) | −14,6 | −14,4 | −12,5 | −12,6 | −0,67 / −0,59 | 48% / 42% | 8% / 11% |

Todos passam no teste de truncamento (3 datas, diferença 0). Parâmetros escolhidos pelo maior IR no IS com R$ 20 mil (grade de 8–12
variantes; script de escolha fora do repositório) — inclusive quando o OOS da escolha ficou pior que o de outras variantes (agro, fuso, real tático).

## Convenções e premissas PF (mh_base.py)
- Decisão no fechamento de t, execução no fechamento de t+1 (+lag), resultado a partir de t+2 (igual a `comum.carteira`). Fuso EWZ: decisão
  à noite, execução no leilão de abertura de t+1 e saída no leilão de fechamento do mesmo dia.
- Ações: nº **inteiro** = trunc(alvo x capital / preço de t), recalculado só quando o alvo muda; o que passa do lote de 100 vai ao
  fracionário (spread 2x). A posição é carregada em VALOR pelo retorno total (painel COTAHIST ajustado por proventos/desdobramentos da
  pesquisa de eventos), então renomeações (VVAR3→VIIA3→BHIA3, ELET3→AXIA3, TRPL4→ISAE4, MRFG3→MBRF3, CPLE6→CPLE3, ARZZ3→AZZA3, BTOW3→AMER3,
  PETZ3→AUAU3) viram uma série só. Ação comprada = valor x (R − CDI); vendida = −valor x (R − CDI) (produto da venda em Tesouro Selic).
- Custos: emolumentos 0,03% (day trade 0,023%) + meio spread por ADV (5/10/25/50 bps); aluguel PF 0,5% do volume por contrato
  aberto/renovado (renova a cada 63 pregões) + taxa ao doador (1% a.a. blue chip, 2–3% varejo/agro) x 1,2.
- Futuros inteiros: round(alvo x capital / nocional de 1 contrato), recalculado só quando o alvo muda; o hedge usa o beta **congelado na
  entrada** (sem isso o MCL era refeito todo dia e perdia no vai-e-volta — bug 1). WIN = Ibovespa (retorno total) − CDI; WDO = DOL rolado da
  B3 (2019+), antes PTAX − (CDI − cupom) com cupom = Fed funds + 1,07 pp; BGI/CCM rolados do boletim B3 (contrato de maior OI após o mês
  corrente, retorno do MESMO contrato); MCL = BNO − T-bill em US$ x PTAX, nocional 100 barris x Brent (MCL só existe desde 12/07/2021: antes
  a perna é hipotética). Custo por contrato e lado = tarifa + meio tick (WIN R$ 1,10; WDO R$ 3,70; BGI R$ 10; CCM R$ 4; MCL US$ 1,35) +
  rolagem. Margem MCL na IBKR via `pf.custo_conta_exterior` (perde CDI, IOF 1,1%/0,38% + spread, câmbio).
- Garantia (diagnóstico): Tesouro livre + 70% das ações compradas ≥ margens B3 + 25% do vendido + saldo IBKR. Nenhum fundo ficou sem garantia.
- IR: ações swing com isenção se vendas ≤ R$ 20 mil no mês; futuros B3 15%; BOVA11 15% sem isenção; day trade 20%; exterior 15%; CDI perdido
  pelas ações compradas sai do caixa tributado a 15% (`_cdi_perdido`).

## Dados
`pf/dados/macro_hedge/` (montado uma vez por `mh_base.prepara()` a partir de quant/fundos/dados e quant/dados): `acoes_{P,R,O,V}.parquet`
(260 ações com ADV ≥ R$ 20 mi em algum momento, 2014–2026, inclui deslistadas e em RJ), `eventos.parquet` (fatos relevantes e ITR/DFP da CVM
por ticker, data de ENTREGA), `br.parquet` (BOVA11 abertura/fechamento, Ibovespa, DOL/BGI/CCM/SJC/ETH rolados, cupom, Selic meta, Focus IPCA
12m com 1 dia de defasagem), `eua.parquet` (EWZ, BNO, USO, SPY, Brent, WTI, BRL=X, PBR, VALE, VIX, Fed funds, breakeven 5a).

---

## 1. mh_petroleo — PETR4/PRIO3 em pânico x micro petróleo (o melhor da frente)
**Tese.** PETR4 é Brent em reais + risco Petrobras. Em pânico (venda forçada de estrangeiro, margem, resgate) a ação cai muito mais do que o
petróleo em reais justifica. Compro no fracionário quando o resíduo de 21 dias contra o Brent em R$ (beta de 1 ano) está ≤ −1,5 desvio
**e** a ação caiu ≥ 10% do topo de 63 dias; vendo MCL no beta (congelado); saio quando o resíduo volta a zero ou em 42 pregões. Só comprado
(vender PETR4/PRIO "cara" perdeu na pesquisa anterior: PRIO é compounder, governança da PETR4 reprecifica e não volta).
**Resultado.** OOS +3,0 pp (20k) / +3,9 pp (50k), depois do IR +2,8/+3,4; IS +4,3; vol 8%; pior queda OOS −7,8%; PBO 10%/20%; **100% das
variantes da grade batem o CDI no OOS**; custo 2x +2,7; t+2 +3,4 (não depende de execução rápida); placebo p = 0,14 (20k) e 0,07 (50k);
walk-forward +0,4/+1,3; leque p5–p95 −0,2 a +5,8. Alavancagem 2x: +5,3/+6,4 pp com vol 14–16% (pior queda total −42/−45%).
**Hedge na prática.** Com R$ 20 mil o MCL arredonda para **zero** sempre (hedge pedido ~R$ 5–10 mil contra 1 MCL de R$ 17–50 mil) — o fundo é
PETR4/PRIO3 comprado nos pânicos. Com R$ 50 mil, 1 MCL em 2,2% dos dias (2018 e mar/2020); a variante sem hedge dá o mesmo (+3,0).
**Melhores (20k).** PRIO3 ago/2019 (+16,9%, +8,7 pp do PL), PETR4 jun/2016 (+16,5%, +7,9), PRIO3 mar/2020 (+22,3%, +6,9 — fundo do Covid),
PETR4 set/2015 (+14,0%), PRIO3 mai/2024 (+11,5%), PETR4 mar/2024 (+11,1% — a queda dos dividendos extraordinários retidos), PRIO3/PETR4
jun/2022 (+10,7%/+8,1% — pânico da intervenção nos combustíveis), PETR4 mar/2021 (+8,2% — depois da troca de CEO).
**Piores.** PETR4 mai/2026 (−11,6%), PETR4 mai/2018 (−9,3% — greve dos caminhoneiros + fim da política de preços: governança, não fluxo),
PRIO3 mar/2023 (−6,6%), PRIO3 out/2024 (−2,2%). Só 22 negócios em 12 anos; **sem os 5 melhores o ativo OOS vai a −0,8 pp** — é um livro
de poucas apostas grandes.
**Por que funciona.** Quem vende PETR4 no pânico (fundos de índice/ETFs estrangeiros, chamadas de margem) não está precificando petróleo; o
petróleo em reais é a âncora do valor e a ação volta para ela em 2–6 semanas. Falha quando o pânico É a governança (2018, 2026).
**Gatilho de mercado (VIX/Ibovespa) como regime:** piorou no IS e no OOS — o desconto aparece também em pânicos só da empresa.
**Próximo.** Filtro de evento de governança (FR de troca de CEO / política de preços nos 10 dias anteriores = não comprar); PRIO só via
momentum do resíduo; vender put de PETR4 no lugar da compra (prêmio de vol no pânico).

## 2. mh_real_tatico — real tático por juro real (WDO) + Brasil após pânico
**Tese.** Diferencial de juro real = (Selic meta − Focus IPCA 12m) − (Fed funds − breakeven 5a). z de 5 anos > 1: vendo WDO (compro real); < −1:
compro WDO; saio quando o z cruza zero. Livro de pânico: Ibovespa −≥8% (ou 5%) em 5 pregões com S&P > −2% (pânico brasileiro, não global)
→ compro BOVA11 por 42 pregões. A regra escolhe os eventos.
**PF: o WDO não cabe em R$ 20 mil.** Alvo de 1x o capital em dólar: 1 WDO = R$ 23 mil (2014) a R$ 50 mil (2026). Com R$ 20 mil o fundo teve
posição só em 2016–2021 (o 0,5–0,9 contrato arredondou para 1) e **zero contrato desde 2021** (21,6% dos dias com sinal e sem contrato) →
OOS −2,3 (a perda é o fim do ciclo comprado em dólar em 2021). Com R$ 50 mil 1–2 contratos sempre: **OOS +4,8 pp, +3,7 depois do IR**, IR 0,34,
P(bater) 71%, placebo p = 0,00, walk-forward +5,9, leque p5–p95 +3,6 a +6,5, custo 2x +4,6, t+2 +5,4; mas vol 16% e pior queda −31% no OOS
(−34% no período). A variante "1 contrato sempre" com R$ 20 mil (= 2,5x o capital em dólar) daria +11,6 pp com vol ~32%.
**Negócios (50k) — só 4, um ciclo cada:** vendido em real (comprado WDO) jun/2017 → ago/2021 (dólar 3,3 → 5,2, Selic a 2%): +59,6 pp do PL;
comprado em real mar/2016 → abr/2017 (+19,5); nov/2021 → mai/2024 (Selic 13,75%: +17,9); mar/2025 → hoje (+19,1). z hoje = 0,39 (posição
comprada em real ainda aberta pela regra de saída em zero).
**Livro de pânico.** IS negativo (2014–15: −10, −9, −11 pp do PL em pânicos que continuaram — Dilma/rebaixamento), OOS positivo: nov/2020
(+21,7), mar/2023 (+9,8), ago/2026 (+21,0 — eleição). Sozinho, OOS +4,9 pp; "ambos" com queda de 5%: +9,9 pp com 50k. O IS escolheu só o juro.
**Por que funciona.** O real anda anos na direção do carry real: quando o BC corta para juro real baixo (2017–20), o estrangeiro sai e o
dólar sobe por anos; quando o juro real é dos maiores do mundo (2016, 2022–24, 2025–26), o fluxo vem. É um prêmio de regime, lento —
4 negócios em 12 anos não provam nada estatisticamente (PBO 45%).
**Próximo.** Dimensionar para R$ 50 mil (1 WDO) e juntar com o livro de pânico; usar DI1 (juro real implícito) no lugar do Focus.

## 3. mh_exportadoras — exportadoras atrasadas vs dólar, hedge WDO+WIN
**Tese.** A receita da Suzano/Klabin/Vale é em dólar; o lucro em reais sobe junto com o dólar, a ação reage com atraso. Compro quando o
resíduo de 42 dias contra dólar (WDO) e Ibovespa (WIN) está ≤ −2 desvios; vendo WDO e WIN nos betas; saio no zero ou em 63 pregões.
FIBR3 até 2019 (sobrevivência).
**"1 WDO com R$ 50 mil cabe?"** Não como hedge: o pedido é beta_dólar (0,3–0,8) x R$ 7–17 mil = R$ 2–14 mil de dólar contra R$ 25–55 mil de 1
WDO. Com R$ 20 mil: 0 contrato em 100% dos dias. Com R$ 50 mil: 0 contrato em 70% dos dias em posição e, quando dá 1, o hedge é 2–5x o
pedido (vira aposta vendida em dólar; perdeu R$ 5,4 mil no período). WIN: 0 contrato em 41% dos dias (50k).
**Resultado.** OOS −0,3 (20k) / −0,9 (50k); IS +3,1; vol 4% (pouco tempo posicionado: 16 negócios em 12 anos); PBO 38–51%; placebo p 0,5.
**Melhores.** VALE3 abr/2015 (+29%, +9,8 pp), SUZB3 jul/2020 (+29%, +9,6 — dólar a 5,4 com a ação parada), VALE3 ago/2024 (+13,7%),
FIBR3 jul/2016 (+13,8%). **Piores.** SUZB3 abr/2026 (−12,6%), KLBN11 mar/2025 (−5,3%), SUZB3 jun/2019 (−6,9% — preço da celulose
caindo: o resíduo contra o dólar era a celulose, não atraso).
**Por que falha.** O fator que falta é o preço da commodity (celulose/minério). Sem ele o "atraso" muitas vezes é o preço da celulose
caindo (2019, 2025–26). **Próximo:** incluir minério (SGX) e celulose (FOEX/índice Suzano) como fator e repetir.

## 4. mh_pares — pares intra-setor sem notícia, aluguel PF
**Tese.** Itaú x Bradesco, Taesa x ISA, Renner x Guararapes...: divergência de 21 dias ≥ 2 desvios SEM fato relevante nem ITR de nenhum dos
dois (e só conhecido no pregão seguinte) é fluxo e volta. 19 pares escolhidos pelo negócio; até 2 pares de 40% por perna; saída no zero,
30 pregões ou |z| ≥ 3,5.
**Resultado.** OOS −2,1 (20k e 50k), IS +0,9; nenhuma variante bate o CDI no OOS; custo 2x −3,5. Pouco tempo posicionado (perna vendida em
6,7% dos dias).
**O que se aprendeu.** O filtro de notícia melhora as 4 comparações no OOS e as 2 de janela de 21 dias no IS (ex.: 21d/2,0: IS +1,2 vs −5,6; OOS −0,5 vs −11,3); com janela de 10 dias piora um pouco no IS —
confirma que divergência com notícia é informação. Mas mesmo sem notícia o que sobra não paga aluguel de PF (0,5% por contrato) + spread
do fracionário. **Melhores:** GUAR3 vendida x LREN3 fev/2022 (+9,7 pp), CEAB3 vendida jan/2023 (+8,3), ITUB4 vendido x BBDC4 out/2022
(+6,8). **Piores:** ITUB4 comprado out/2021 (−8,4), CEAB3 comprada fev/2022 (−8,2), BBDC4 comprado nov/2022 (−6,3 em 3 dias — eleição),
ITUB4 vendido set/2026 (−6,5).
**Próximo.** Só pares de mesma regulação e receita (transmissoras, bancos grandes) com prazo maior; custo do aluguel por papel (BTC B3).

## 5. mh_agro — margem da cadeia nos futuros agro B3
**Tese.** Margem implícita = dólar − boi (frigoríficos), dólar − milho (BRF), milho + soja + dólar (SLC), etanol + dólar (São Martinho), variação de
63 dias; compro a ação de maior melhora de margem (k = 1), mensal.
**Resultado.** IS +23,5 (2019–22), **OOS −13,3** (2023+), vol 38%: com k = 1 é uma ação só, vol de ação. PBO 14–19% mas o leque vai de
−10 a +27 pp — é ruído. Melhores: BRFS3 abr/2023 (+63%, +55 pp do PL), SLCE3 nov/2019 (+41%), SLCE3 fev/2021 (+34%). Piores: BRFS3 fev/2023
(−24%), SMTO3 mai/2022 (−18%), SMTO3 2026 (−15%). SMTO3 sozinha perdeu 48 pp (etanol subindo ≠ margem: o custo da cana sobe junto).
**Hedge na commodity: não existe para PF.** 1 BGI = 330 @ x R$ 150–400 = R$ 50–130 mil → 0 contrato em 100% dos dias com 20k e 50k.
1 CCM (R$ 15–40 mil) só com 50k e em 7% dos dias. Os futuros agro servem como SINAL, não como hedge.
**Próximo.** Preço de exportação real (Comex Stat), CEPEA; k ≥ 3 com hedge de Ibovespa (a variante k = 3 perdeu menos: −6,3).

## 6. mh_fuso_ewz — EWZ/ADR depois da B3, no leilão de abertura
**Pergunta: o EWZ depois das 17h prevê a abertura?** Quase nada. Regressão do gap (fechamento → abertura de t+1) contra o descasamento
s = EWZ em US$ − BOVA11 convertido pelo dólar: beta 0,02 (IS) / 0,00 (OOS) para BOVA11; PETR4 x PBR 0,04/0,01; VALE3 x VALE 0,11/−0,02.
O motivo é físico: desde que a B3 passou a acompanhar o horário de verão americano, o leilão de fechamento termina junto (ou até 1h antes)
do fechamento de NY; o descasamento medido é quase todo ruído de câmbio (fechamento do BRL do Yahoo ≠ 17h). E o pregão de t+1 não continua o
movimento (beta −0,06 em BOVA11; quando |s| ≥ 1%, o pregão vai −7 a −10 bps contra).
**Resultado.** Escolha do IS (segue, 1%, BOVA11+ADRs): IS +0,4, OOS −12,6 com 816 day trades no OOS; custo 2x −19; PBO 9% (a grade toda
perde). A variante "reverte só BOVA11" fica em ~0. Igual à pesquisa anterior (ADR com execução t+1): **não há arbitragem de fuso no
Brasil para quem não opera o after-market do WIN/WDO** (o WIN negocia até 18h25 e abre às 9h — esse seria o único veículo, sem dado intradiário).

## 7. mh_evento_beta — fato relevante fora de balanço, beta em WIN
**Tese.** Subreação a FR que não é balanço (FR com ITR/DFP de 2 pregões antes até a decisão é descartado — o PEAD/insiders ficam com b3_acoes)
em large caps (ADV ≥ R$ 50 mi, aluguel barato): reação ≥ 5% vs Ibovespa em 2 dias → sigo a reação por 40 pregões, até 5 eventos de 20%,
beta líquido em WIN inteiro (~44 eventos/ano).
**Resultado.** OOS −14,6 (20k) / −12,5 (50k); IS −5,3; vol 18%; P(bater) 8–11%. **A perna comprada é a que destrói** (só comprado: −22,6);
só vendido +2,4/+6,9 e "contra a reação" +5,5/+3,6 no OOS — em large caps brasileiras o FR positivo é vendido depois (o mercado sobre-reage),
o oposto do que a pesquisa anterior viu no universo inteiro (dominado por small caps). Não escolhido porque o IS de ambas as direções é ruim.
**Hedge WIN.** Com R$ 20 mil, 57% dos dias com exposição ficam sem contrato; com 50k, 22%. O WIN ajudou (IS −5 vs −14 sem hedge) e chegou a
8 contratos em 2016 (índice a 40 mil pontos → WIN de R$ 8 mil).
**Piores:** SUZB3 vendida mar/2018 (fusão com a Fibria, ação +86%: −17,4 pp), MRVE3 vendida abr/2023 (+71%), VALE3 e **VALE5** vendidas
fev/2016 (o mesmo FR mapeado para as duas classes = posição dobrada — bug 3), COGN3/GOLL4/PETR3 compradas jan–fev/2020 (Covid).
**Melhores:** WIN comprado 2016 (+23 pp), AMBP3/BHIA3 compradas 2019–20, IRBR3 vendida mar/2020 (+44%).

---

## O que deu certo e por quê
1. **Comprar PETR4/PRIO3 no pânico** (mh_petroleo): o único com IS e OOS positivos, 100% das variantes positivas, robusto a custo e atraso.
   O negócio é concreto: quem vende no pânico não está precificando o petróleo; a âncora (Brent em reais) puxa a ação de volta. O "hedge
   de commodity" não é necessário (e não cabe) — o que protege é só comprar quando o desconto não tem notícia de governança.
2. **Real tático por juro real com 1 WDO** (mh_real_tatico, R$ 50 mil): ciclos de anos que pagam o carry e o câmbio na mesma direção;
   placebo p = 0, leque todo positivo. Mas são 4 negócios.
3. **Filtro "sem notícia"** nos pares: a parte certa da tese — divergência com FR/ITR não volta.

## O que deu errado
- Hedge de PF com contratos inteiros: WDO (US$ 10 mil), BGI (R$ 50–130 mil), MCL (R$ 17–50 mil) e WIN (R$ 8–42 mil) são grandes demais para
  posições de R$ 5–20 mil. Na prática ou o hedge é 0 ou é 2–5x o pedido. Só o WIN em 2014–2016 (índice baixo) e o WDO como posição
  principal (real tático com 50k) funcionam no tamanho certo.
- Aluguel de PF (0,5% por contrato) + fracionário matam a reversão de curto prazo (pares, eventos vendidos).
- Fuso EWZ: a premissa "EWZ fecha depois da B3" não vale mais (leilões quase simultâneos).
- Agro e eventos: escolhas de 1 ação / large caps viraram ruído de vol 20–40%.

## Bugs encontrados e corrigidos
1. Hedge refeito todo dia com o beta rolante: o MCL ia de 1 para 2 contratos no fundo do Covid e perdeu no repique do acordo da OPEP+
   (abr/2020, −8 pp do PL só no hedge). Corrigido: beta congelado na entrada (`mh_base.congela`).
2. Agro: dias sem ajuste no boletim B3 (feriados/sem negócio) quebravam a janela de "futuro vivo" e o fundo quase não operava; agora ffill de 5 dias.
3. Evento: **truncamento falhou** na 1ª rodada — `sort_values("i")` instável muda a ordem dos eventos do mesmo dia quando o tamanho dos dados
   muda e, com o limite de 5 eventos, troca qual entra. Corrigido com ordenação estável (dia, ticker). Também o filtro "FR perto de ITR"
   olhava ITR até 2 dias DEPOIS da decisão (look-ahead) — agora só ITR já entregue. Pendente: o mesmo FR gera posição nas duas classes
   (VALE3/VALE5, PETR3/PETR4) — deveria ser uma só.
4. Pares: FR entregue à noite contava no próprio dia; agora só no pregão seguinte.
5. Teste de sanidade do motor: livro 100% PETR4 de 2015 a 2026 sem rebalancear tem valor crescente sobre capital nominal constante — o
   excesso diário fica correto, mas fundos com posição de anos acumulam exposição (só afeta o real tático, que mede em contratos).

## Próximos passos
1. mh_petroleo com filtro de governança (FR de troca de CEO/política de preços) e com venda de put de PETR4 no pânico.
2. mh_real_tatico só para R$ 50 mil+, juntando o livro de pânico (variante "ambos, queda 5%": +9,9 pp OOS com 50k, não escolhida no IS).
3. Exportadoras com o preço da celulose/minério como fator; eventos só do lado vendido/contra a reação em large caps (testar com IS próprio).
4. WIN intradiário (abre 9h, fecha 18h25) para a pergunta do fuso — precisa de dado intradiário de futuros.
