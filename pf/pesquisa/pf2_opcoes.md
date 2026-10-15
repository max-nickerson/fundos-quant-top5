# Frente pf2_opcoes: opções com risco definido para PF (R$ 20–50 mil)

Oito fundos novos em `pf/fundos/op_*.py`. As peças comuns ficam em `op_base.py`, que estende o `db3_base.py` com painel bruto de 24
ativos-objeto, índice rápido de séries, saída antecipada no bid/ask, perda máxima genérica e teto de perda na saída. Cada fundo foi
rodado com `python pf/rodar_pf.py um op_<nome>`, e o truncamento passou em todos (diferença máxima 0). O resumo está em
`pf/resultados/pf2_opcoes.pkl` e as análises extras em `pf/pesquisa/_op_analises.py`.

Dados novos, em `pf/dados/pf2_opcoes/`:
- `copom.csv`: datas e decisões do Copom, da API do BCB `historicotaxasjuros`.
- `pr_opcoes.parquet`: opções de DOL, WDO, IDI e CPM do BVBG.086 (PriceReport) da B3, do 2º ao 4º pregão de cada mês, de 2018 a
  2026. O script de download é `baixa_pr.py`. O histórico público começa em 2018.

## Resultado (OOS, excesso sobre o CDI em pp a.a.; IR = information ratio OOS com 20k)

| Fundo | Aplicável? | OOS desde | 20k antes / depois do IR | 50k antes / depois do IR | IR | PBO | P(bater 3a) | sem 10 melhores |
|---|---|---|---|---|---|---|---|---|
| 1 Travas em 24 papéis (condor, regime) | sim | 2021 | −12,2 / −12,0 | −12,8 / −12,6 | −1,32 | 13% | 0% | −14,1 |
| 2 Vol de evento (Copom/eleição, vende) | sim | 2021 | −4,9 / −4,8 | −5,8 / −5,7 | −1,87 | 33% | 0% | −4,8 |
| 3 Wheel PETR/VALE/ITUB | sim | 2021 | **+6,2 / +5,1** | +3,1 / +2,5 | 0,64 | 54% | 87% | −1,9 |
| 4 XSP trava de put (proxy Cboe) | parcial | 2021 | −1,3 / −1,9 | −5,9 / −7,8 | 0,12 | 0% | 50% | −17,0 |
| 5 Hedge de cauda (put BOVA11 com vol baixa) | é hedge | 2021 | −2,1 / −2,0 | −1,7 / −1,7 | −0,61 | 8% | 6% | −2,4 |
| 6 Opções de dólar (trava de put, tamanho WDO) | parcial | 2023 | −1,5 / −1,5 | −1,7 / −1,6 | −0,17 | 43% | 37% | −4,3 |
| 7 Opção de Copom (vende caudas); IDI só documentado | parcial | 2023 | +4,4 / +3,7 | −3,1 / −3,1 | 1,02 | 40% | 98% | +0,4 |
| 8 Doador de aluguel (taxa alta) | sim | 2021 | −30,2 / −29,8 | −30,2 / −29,8 | −0,91 | 24% | 6% | −45 |

O CDI no OOS foi de 11,4% a.a. a partir de 2021 e de 13,1% a.a. a partir de 2023. Todos os parâmetros são a variante de maior IR
dentro da amostra. Onde todas as variantes do IS eram negativas, isso está dito no módulo. Custo 2x e t+2 com 20k, em pp:
- travas: −14,0 e −10,2;
- eventos: −7,0 e −4,6;
- wheel: +6,0 e +9,9;
- XSP: −3,9 e −11,8;
- hedge: −2,3 e −2,5;
- dólar: −3,4 e +0,9;
- Copom: +3,4 e +4,3;
- aluguel: −35 e −31.

**Nenhum dos oito é um edge de PF aprovado.** O único positivo robusto, o wheel, é beta disfarçado (seção 3). O positivo do Copom são
8 negócios, todos ganhos, em 12 meses (seção 7).

## 1. Travas vendidas em 24 papéis com IV > RV (`op_travas_multi.py`)
**Tese.** Em cada vencimento vendo uma trava de risco definido nos N papéis com maior IV ATM / vol realizada de 21 dias. A ideia é
vender a call de "bilhete de loteria" do varejo e a put de proteção onde elas estão mais caras naquele mês. Há três estruturas:
- direcional: trava de alta com put se o papel está acima da média de 100 dias, e de baixa com call se está abaixo;
- iron butterfly;
- iron condor.

O regime de risco global (VIX, S&P e crédito) só deixa abrir estrutura nova com o regime ligado.

**Implementação.** Orçamento de 10% do capital de perda máxima por mês, lotes de 100. Agride bid e ask do COTAHIST e exige spread
de até 25% do meio, com asa a pelo menos metade da largura-alvo. Segura até o vencimento. No exercício, as pernas se compensam e só
o saldo de ações paga desmontagem.

**Resultado.** As 12 variantes perdem no IS e no OOS. A menos ruim no IS foi condor com 6 papéis e regime: −1,2 pp no IS e
−12,2 pp no OOS. A melhor no OOS seria a direcional com regime, com −6,1 pp. Com custo zero o OOS ainda dá −7 pp. Então não é só o
spread: o prêmio de vol de ação brasileira não paga a cauda depois de 2021.

**Por que perde.** O crédito médio é 21% da largura, então o ponto de equilíbrio exige acertar 79% das vezes. O acerto real foi
cerca de 70%, e 20–25% das travas chegam à perda máxima. Ser "IV alta / RV" seleciona justamente o papel com notícia pendente (COGN,
VIIA, MGLU, BBAS em 2023–25).

**Negócios.**
- Por papel, todos negativos, exceto BOVA +1,0, CSNA +0,8 e PRIO +0,6 pp.
- 10 melhores: PETR mai/2016 +2,3; VVAR jan/2020 +2,1; BBAS jul/2025 +1,6; PETR jul/2023 +1,4; PETR mai/2015 +1,4; PRIO set/2023
  +1,4; PETR ago/2016 +1,3; B3SA jul/2026 +1,1; VALE fev/2021 +1,1; MGLU fev/2024 +1,1.
- 10 piores, todos na perda máxima de cerca de −1,7 pp: ITSA set/2026 e ago/2025; COGN jul/2020 e jan/2021; VIIA jan/2023 e
  ago/2023; PETR jul/2015; VVAR set/2020; ABEV abr/2021; MGLU jun/2023.

## 2. Vol de evento: Copom, eleição e resultado (`op_eventos.py`)
**Tese.** Antes de um evento agendado, o formador sobe a IV curta. Extraio o salto implícito da estrutura a termo das IVs ATM:

`salto² = IV1²·T1 − var_dia·T1`, com `var_dia = (IV2²T2 − IV1²T1)/(T2 − T1)`

e comparo com o salto histórico do tipo de evento, usando só eventos passados. Se o salto implícito é maior que k x o histórico,
vendo iron butterfly. Se é menor que o histórico / k, compro straddle. Entro na véspera e saio no dia seguinte, no bid/ask.
- Copom: entro no dia da decisão, que sai depois do fechamento.
- Eleição: entro na sexta antes do domingo.
- Resultado: entro na véspera da entrega do ITR/DFP à CVM, que pode sair antes da abertura.

**Resultado.** Todas as 9 variantes perdem no IS. A escolhida (macro, só vender) dá −4,9 pp no OOS. A versão completa, com
resultado e a regra, dá −14 pp. Vender vol de balanço dá −35 pp. Com custo zero, a regra completa ficaria em +8 pp OOS. Em 2 dias,
4 pernas cruzando o spread duas vezes custam mais do que o prêmio de evento.

**Negócios.**
- Melhores: Copom dez/2025 +0,26; ago/2023 +0,11; jul/2025 +0,05 pp. Os demais "melhores" já são negativos.
- Piores: eleição de out/2026 −3,1; Copom jun/2020 −2,9; mai/2022 −2,0; fev/2020 −1,7; mar/2021 −1,6; set/2026 −1,6; mai/2025 −1,5;
  eleição de out/2022 −1,5; set/2022 −1,4; set/2020 −1,2.

**Bugs achados e corrigidos.**
- Oferta de saída abaixo do intrínseco, uma oferta velha: o bid de 0,17 numa put que valia 1,72 gerava perda de 850% da perda
  máxima. Agora a oferta é descartada, e o preço é limitado ao intrínseco, porque a perna comprada pode ser exercida.
- Zerar uma trava ilíquida pelo ask/bid custava mais que a largura. Exemplo: VALE com ask/bid de 10,80/4,67 numa largura de 4.
  Agora a perda é limitada à perda máxima + 3%, porque ninguém zera acima da largura: segura até o vencimento.
- Perda máxima com put vendida acima da call vendida (strikes ajustados por provento) passou a ser calculada no resultado em todos
  os strikes.

## 3. Wheel em ações isentas (`op_wheel.py`)
**Tese.** Vendo put com o caixa em Tesouro Selic. Se for exercida, fico com a ação (isenta até R$ 20 mil de vendas por mês) e vendo
call acima do preço de compra. Se a call for chamada, volto para a put.

**Resultado.** O OOS dá +6,2 pp com 20k (+5,1 depois do IR, com tudo tributado a 15%) e +3,1 pp com 50k. Placebo p = 0,00,
P(bater) 87%, mas PBO de 54%. Sem os 10 melhores dá −1,9 pp.

**Contra a ação, para separar o beta** (análise em `_op_analises.py`):

| | Wheel | Opções | Ações | Comprar e segurar os 3 papéis | Beta | Alfa (wheel − beta x ação) |
|---|---|---|---|---|---|---|
| IS | +7,5 | +1,2 | +6,3 | +17,6 | 0,23 | +3,5 |
| OOS | +6,0 | +0,3 | +5,7 | +12,3 | 0,29 | +2,4 |

O fundo fica com a ação em 75–85% dos dias. Por papel, em pp: ação PETR +38, VALE +23, ITUB +15; puts PETR +10,5; calls PETR −1,7.

**O que deu certo e por quê.** Quase tudo é a ação: dividendos da PETR em 2021–23 e VALE em 2025–26. O "alfa" de +2,4 pp é o efeito
de comprar depois da queda (a put é exercida no fundo) e vender depois da alta. É o mesmo beta de três blue chips, com timing, e
continua bem abaixo de simplesmente segurar as ações.

Com 6 papéis (+BBDC, BBAS, ABEV) o resultado cai para +1,4 pp OOS e o alfa para −0,5. Com a perna em ações isenta, o depois do IR
melhora cerca de 0,7 pp.

**Veredito: BETA**, como `db3_cc_isenta`.

**Negócios.**
- Melhores: VALE ação ago/2025–fev/2026 +16; PETR ação jun–out/2018 +11; PETR out/2020–abr/2021 +8; VALE 2019–20 +7; PETR set/2022
  +6,5; put PETR mar/2020 (IV de 100%) +6; ITUB 2017–18 +5,6.
- Piores: put PETR mai/2018 (greve dos caminhoneiros) −7,6; call PETR set/2022 −4,2; put VALE jan/2019 (Brumadinho) −3,8;
  calls PETR 2018 −3,0 e −2,6.

## 4. XSP iron condor, borboleta e trava de put (`op_xsp_cboe.py`)
**Dados.** Não existe histórico gratuito de opções de SPX ou XSP. O P&L por unidade de nocional vem dos índices Cboe:
- CNDR = condor;
- BFLY = iron butterfly;
- PUT + (PPUT − S&P) = trava de put ATM/−5%.

**Tamanho.** 1 XSP tem cerca de US$ 66 mil de nocional hoje, e a perda máxima é de 2–4% disso (US$ 1,5–2,5 mil, ou R$ 9–14 mil).
Com 25% de risco, a carteira de 20k só opera quando o S&P estava baixo (2008–2012) ou o VIX alto. **No OOS, com 20k, quase não
há contratos.**

**Resultado.**
- A trava de put, escolhida no IS (+24,7 pp, mas com 5–13 contratos em 2008–12), dá −1,3 pp no OOS com 20k e −5,9 com 50k.
- Condor: −42 pp no IS.
- Borboleta: −97 pp no IS.
- O CNDR rendeu 0,4% a.a. desde 2010, abaixo do T-bill, e o BFLY −3,3% a.a.

O prêmio de variância do S&P existe, mas, nas estruturas de asa curta, o custo de varejo (US$ 6,65 por perna) e a cauda comem tudo.

**Limite do proxy.** A perda do proxy não fica limitada como numa trava real. Em out/2008 o negócio perdeu −45% do capital contra o
orçamento de 25%, por causa do PPUT − S&P aproximado, do câmbio e do dimensionamento com o VIX do dia anterior. **APLICÁVEL só como
"não cabe".**

**Negócios.**
- Melhores: abr/2020 +37 pp; set/2011 +26; abr/2009 +24; fev/2008 +23.
- Piores: out/2008 −45; ago/2011 −38; jun/2022 −36; out/2022 −36; fev/2009 −35; mar/2020 −32.

## 5. Hedge de cauda: VIX call spread x put/collar de BOVA11 (`op_vix_hedge.py`)
**Implementação.**
- Trava de call de VIX (K1 = 1,2 x o futuro, K1 + 10), modelada com Black-76 sobre o VX do mesmo vencimento, IV = VVIX com sorriso
  de +0,4·ln(K/F) e custo de US$ 5,65 por perna.
- Put 8% OTM e collar (call 6% OTM) de BOVA11, com dados reais da B3.

O excesso é só o overlay. Carteira BOVA11 de R$ 20 mil, desde jun/2019:

| | Retorno a.a. | Queda máxima | fev–mar/2020 |
|---|---|---|---|
| Sem hedge | 11,2% | −46,9% | −37% |
| Trava de VIX todo mês | −12,7% | −73,5% | −22% |
| Trava de VIX só com vol baixa | −3,2% | −53% | −37% |
| Put BOVA só com vol baixa (o escolhido) | 15,2% | −26% | −6% |
| Put BOVA todo mês | 11,4% | −29% | −12% |
| Collar todo mês | 10,6% | −24,5% | −10% |

**O que funciona e por quê.**
- O seguro com o próprio BOVA11 é barato e eficaz, sobretudo comprado quando a IV está abaixo da mediana: custa cerca de 2 pp a.a.
  no OOS sem crise e corta a queda máxima pela metade. Em fev/2020 a put de 2 lotes rendeu +35 pp do capital.
- A trava de VIX é cara demais para R$ 20 mil: 1 contrato custa US$ 50–110 por mês (US$ 107 em média com o modelo), mais de 13%
  do capital por ano. Além disso, o salto do VIX de mar/2020 caiu num vencimento em que a trava já estava no teto.

**Veredito.** Como "fundo" perde −2,1 pp. Como hedge da carteira de ações isentas, a put de BOVA11 comprada com vol baixa é a melhor
ferramenta de proteção desta frente.

## 6. Opções de dólar B3 (`op_dolar.py`)
**Dados.** As opções de DOL têm de 10 a 30 séries negociadas por dia, mediana de 200 contratos por série negociada, e oferta no
fechamento em menos de 5 séries por dia. As de WDO, que são as que cabem na PF, têm cerca de 2 séries negociadas por dia, com
mediana de 10 contratos.

**Método.** IV de cada negócio de DOL do mês seguinte, com Black-76 sobre o futuro DOL. Sorriso linear em log(K/F). Pernas pelo
sorriso ± meio spread de varejo de max(1,5 ponto; 5% do prêmio). Tamanho de WDO (R$ 10 por ponto). Liquidação na PTAX x 1000.

**Resultado.** A escolha no IS foi a trava de put 3% OTM (IS +1,9): OOS −1,5 pp. A trava de call ("vender o skew do importador")
foi a melhor no OOS (+4,2), mas perdeu no IS (−3,5). O PBO de 43% confirma que não há escolha estável.

Com custo zero, +0,6 pp. A trava de put perde nos meses de real forte: jan/2025 −7,6, jan/2022 −7,5, jan/2023 −7,2 e nov/2020 −6,7
pp. Os ganhos são todos de cerca de +1,7–2 pp, com o crédito inteiro.

**APLICÁVEL: parcial.** Mesmo com edge, a PF dependeria do livro vazio do WDO.

## 7. Opção de Copom (CPM) e IDI (`op_copom.py`)
**IDI.** 17 séries negociadas por dia, mediana de 1.156 contratos por série negociada, **nenhuma oferta no fechamento** em 2018–26
e sem índice IDI no dado. Inacessível para PF. Documentado, sem teste.

**CPM.** É uma digital sobre a decisão do Copom. Até jun/2025 valia R$ 100 por ponto (paga R$ 10 mil); desde jul/2025 vale R$ 1 por
ponto. O multiplicador é lido do próprio dado.

Calibração (preço x frequência real, 868 cotações, 2020–26):

| Faixa de preço | Preço médio | Acerto |
|---|---|---|
| 0–5 | 2,0 | 2,1% |
| 5–10 | 7,6 | 10,7% |
| 10–25 | 16,7 | **9,2%** |
| 25–50 | 35,9 | 40,3% |
| 50–75 | 63,1 | **54,5%** |
| 75–90 | 81,2 | 83,3% |
| 90–100 | 93,6 | 92,3% |

As caudas de 10–25 e os favoritos de 50–75 saem caros, coerente com o hedger de DI comprando cauda.

**Resultado.**
- Vender caudas de 5–25 pontos: +4,4 pp com 20k. São só 8 negócios, de out/2025 a set/2026, todos ganhos, porque antes de jul/2025
  o contrato não cabia em 25% de 20k.
- Com 50k: −3,1 pp. Ali entram contratos grandes desde 2021, e 2 caudas acertadas (−50 bp em ago/2023 e −25 bp em mai/2024)
  custam −8,4 mil e −9,7 mil.
- Comprar ou vender o favorito: −26 e −73 pp no OOS.

**Veredito.** A calibração sugere viés, mas a amostra é minúscula (49 reuniões com preço, 8 negócios PF) e a posição não é marcada
a mercado entre a entrada e a decisão. Promissor só como monitoramento, agora que o lote é de R$ 1.

## 8. Doador de aluguel (`op_aluguel.py`)
**Dados.** Taxas reais da B3 só de dez/2025 a out/2026. Antes disso, o modelo de taxa da frente revisita, calibrado nessas taxas.
É uma **estimativa**: coeficientes do fim da amostra, embora só com dados até t.

**Tese.** Comprar as 10 ações com maior taxa esperada (≥ 8% a.a.) e doá-las, com repasse de 70% da taxa.

**Resultado.** −30 pp no OOS com e sem hedge. A taxa recebida rende +4 a +6 pp a.a., mas as ações perdem 35–40% ao ano. São
GFSA3, PDGR3, RCSL3, AMER3, INEP4, BHIA3, OIBR, AZUL: quem paga 10–30% para alugar está vendido porque sabe que a empresa está
quebrando.

Os 10 melhores são repiques de distressed: FHER3 2021 +17,5; VIVR3 +14,5; IGBR3 +13,5; OSXB3 +13. Os 10 piores: AMBP3 out/2025
−14,5; INEP4 2021 −13,7; GFSA3 jul/2026 −13,5; DMMO3 2020 −11.

**Lição.** A taxa de aluguel alta é o PREÇO da informação do vendido. Doar só faz sentido nas ações que a PF já quer ter (blue
chips a 0,1–1% a.a., dinheiro de graça). Nunca é motivo para comprar o papel.

## O que aprender desta frente
1. **Venda de vol de varejo na B3 não paga o spread.** Cinco testes independentes confirmam o achado da A4/deriv_b3: travas
   multi-papéis, eventos, dólar e trava XSP via proxy. O único prêmio robusto do round anterior (trava de BOVA11 5%/10%) é o do
   índice com asa longe.
2. **Nada aqui tem o "vendedor forçado + tamanho pequeno"** que marca os edges sobreviventes. Os compradores de opção da B3 (varejo
   e hedger) pagam spread, mas o formador come a diferença, não o PF.
3. **Hedge:** use put de BOVA11 com IV abaixo da mediana, não VIX: contrato grande demais e prêmio caro.
4. Promissor para monitorar: **CPM com lote de R$ 1**, vendendo caudas de 10–25 pontos. É mercado de previsão pequeno, com o hedger
   de DI do outro lado. É preciso baixar o BVBG.086 de todos os pregões a partir de jul/2025 e marcar diariamente.

## Próximos passos
- CPM: baixar o PR diário de 2024–26, marcar diariamente e testar só no lote novo.
- Opções de DOL: baixar todos os dias, para usar IV diária em vez de modelo, e checar se o sinal da trava de call (o melhor OOS) é
  estável.
- XSP: comprar ou obter um histórico real de opções XSP de 2021+ (CBOE DataShop) para testar asas estreitas, de US$ 5–10.
- Aluguel: repetir quando houver 2–3 anos de taxas reais da B3. Hoje são 10 meses, e o resto é modelo.
