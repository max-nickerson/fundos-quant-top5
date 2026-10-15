# Auditoria red team: os 10 candidatos ao top 5 PF (R$ 20–50 mil)

Data: out/2026. Escopo: `pf/resultados/ranking_pf.csv`, posições 1 a 9 e mais `rev_debentures`.
Todos os números foram recalculados por código. Os scripts estão em `pf/pesquisa/_aud*.py` e o utilitário em `_aud_util.py`.
Métrica: excesso OOS sobre o CDI, em pp a.a. (`RB.cota`, com as despesas). "Depois do IR" usa a mesma regra do `rodar_pf.apos_ir`.

## Vereditos

| # | fundo | original antes IR 20k / 50k | original depois IR 20k / 50k | **corrigido antes IR 20k / 50k** | **corrigido depois IR 20k / 50k** | veredito |
|---|---|---|---|---|---|---|
| 1 | db3_cc_isenta | 11,8 / 10,0 | 9,6 / 8,0 | **−1,8 / −2,1** (só o overlay de calls) | **−1,7 / −2,1** | REPROVADO como alfa (é beta + PETR4) |
| 2 | db3_trava_bova | 1,9 / 2,0 | 1,6 / 1,7 | **0,1 / 0,2** (com 1 perda máxima) | **−0,1 / 0,0** | APROVADO COM CORREÇÃO (frágil) |
| 3 | gl_bdr_limite | 12,5 / 12,7 | 11,1 / 11,3 | **−12,6 / −11,8** (fill só se a mínima passar 0,5% do limite) | **−12,4 / −11,6** | REPROVADO (artefato de fill) |
| 4 | b3_leilao_noite | 11,7 / 11,7 | 9,4 / 9,4 | **7,1 / 7,1** (8 bps ida e volta) | **5,6 / 5,6** | APROVADO COM CORREÇÃO |
| 5 | cme_vxm | 19,8 / 21,7 | 13,9 / 15,8 | 2012–26: 14,8 / 8,2, com queda de −87% / −97% | — | REPROVADO (ruína) |
| 6 | rev_carry_moedas | 11,4 / 8,6 | 10,2 / 7,7 | só G10: **2,9 / 1,8** | **1,3 / 1,2** | REPROVADO (é o 7 alavancado + iene/franco) |
| 7 | db3_wdo_carry | 19,4 / 8,7 | 14,9 / 7,1 | 20k: inviável; **50k: 8,7** | **50k: 7,1** | REPROVADO com 20k; APROVADO COM CORREÇÃO com 50k (é beta de carry) |
| 8 | b3_ofertas_varejo | 4,2 / 4,2 | 3,5 / 3,5 | **2,6 / 2,6** | **2,1 / 2,1** | APROVADO COM CORREÇÃO |
| 9 | rev_pead | 7,5 / 7,7 | 6,0 / 6,2 | limiar 5%: **−0,2 / −0,7** | **−1,5 / −1,4** | REPROVADO |
| 10a | rev_opa | 1,4 / 1,4 | 1,4 / 1,4 | **~0,5 / ~0,5** (sem HBOR3) | **~0,5 / ~0,5** (isento) | APROVADO COM CORREÇÃO (pequeno) |
| 10b | rev_debentures | 1,9 / 2,1 | 1,6 / 1,7 | n=10: **0,5 / 0,8** | **0,3 / 0,6** | APROVADO COM CORREÇÃO (é carry de crédito) |

Versões corrigidas, com o mesmo contrato:
- `pf/fundos/gl_bdr_limite_aud.py`: ordem limitada com `fura` de 1%, opção de entrada no fechamento e opção de saída no fechamento.
- `pf/fundos/b3_leilao_noite_aud.py`: 1 bp de derrapagem por lado, ou 8 bps ida e volta. Passou no truncamento.
- `pf/fundos/b3_ofertas_varejo_aud.py`: rateio de 15% e pedido bloqueado. Passou no truncamento.

---

## 1. db3_cc_isenta: covered call isenta (`_aud1_cc.py`, `_aud1b.py`, `_aud_final2.py`)
- **Decomposição OOS (2021–26):** o total dá +10,8 pp. As ações menos o CDI dão **+12,4 pp** e as calls vendidas dão **−1,6 pp**. No IS a perna de calls deu −4,7 pp.
- **O overlay destrói valor.** Comparando no mesmo motor, sem call fica +13,6 e com call fica +11,8. A pesquisa A6 já avisava isso.
- **Regressão OOS contra o Ibovespa (BOVA11 − CDI, HAC):** beta 0,51 (t=21), R² 0,55, "alfa" de 10,6 pp (t=3,1).
- **O "alfa" vem da escolha das 3 ações.** No OOS, PETR4 rendeu 41% a.a. de retorno total: o preço foi de 28,9 para 56,9 e pagou R$ 42 de proventos. VALE3 rendeu 5,6% e ITUB4, 16,6%.
- **Por fatia de tempo:** a carteira equiponderada das 3 menos o CDI dá +10,4 pp, contra −0,9 pp do Ibovespa. Ninguém escolheu essas ações por um sinal: elas são simplesmente as raízes de opção mais líquidas.
- **Veredito:** REPROVADO como alfa. Resta uma carteira de 3 ações (beta e risco idiossincrático de PETR4) com um overlay que custa cerca de 2 pp a.a.
- **Ressalva de dado:** ITUB4 aparece com −18% em 04/10/2021 (cisão XPart sem provento no Yahoo). É conservador.

## 2. db3_trava_bova: trava de alta em BOVA11 (`_aud2_bova.py`, `_aud2b.py`)
- **Preços executáveis:** sim. A perna vendida sai no bid e a comprada no ask, ambos do COTAHIST, com o spread no fechamento.
  - Spread relativo mediano de 13%, com máximo de 25% (o filtro).
  - Volume na data de entrada: mediana de R$ 148 mil. As pernas negociaram em 100% dos pregões até o vencimento.
  - Com 2 a 10 travas (prêmio de R$ 50 a 1 mil), a liquidez não é limitação de 2019 a 2026.
- **Marcação:** diária, pelo meio, limitada entre o intrínseco e o teto. Vale o intrínseco no vencimento. Não há marca parada.
- **Risco de cauda:**
  - Crédito/largura mediano de 0,073, então a taxa de acerto de empate é **92,7%**.
  - Foram 23 negócios OOS com 1 perda.
  - A perda máxima típica é de 8,8% do capital. **Uma única perda máxima no OOS leva o fundo a +0,1 / −0,1 pp depois do IR.**
- **O filtro é o que segura o resultado.** As variantes da grade perdem: iron condor −2,5 pp, "sempre" +1,35 pp.
  - O filtro evitou fev–mar/2020 (sem negócio entre 17/02 e 17/06/2020), mas isso aconteceu no IS.
- **Veredito:** APROVADO COM CORREÇÃO. A execução está correta, mas o edge equivale a uma perda máxima em 6 anos. Esperar de 0 a +1 pp. Não é top 5.

## 3. gl_bdr_limite: BDR com ordem limitada (`_aud3_bdr.py`, `_aud3b.py`, `fundos/gl_bdr_limite_aud.py`)
O resultado inteiro é seleção de fila em dado diário.

| regra de execução da compra (saída original) | 20k antes / depois IR | 50k antes / depois IR |
|---|---|---|
| mínima < limite − 0,25% (original) | +12,5 / +11,1 | +12,7 / +11,3 |
| mínima < limite − 0,4% | −5,4 / −5,3 | −4,7 / −4,6 |
| mínima < limite − 0,5% | **−12,6 / −12,4** | **−11,8 / −11,6** |
| mínima < limite − 1% | −42,5 / −41,7 | −42,9 / −42,1 |
| mínima < limite − 2% | −66,1 / −64,9 | −66,6 / −65,4 |
| compra no fechamento de t+1 (+ meio spread) se fechou abaixo do limite | −15,0 / −14,8 | −15,9 / −15,6 |
| fura 1% e sem hedge | −45,8 / −45,0 | −46,2 / −45,4 |

- **Prova direta da seleção adversa:**
  - Com fura de 0,25% há 4.220 negócios OOS (+66,8 pp no total). Com 0,5% há 3.966 (−20,7 pp).
  - Os **687 negócios que só existem com 0,25%** são aqueles em que a mínima mal encostou no limite e o preço voltou. Eles rendem +1,05% cada e somam **+62,9 pp, ou 94% do resultado**.
  - Na vida real, esses são justamente os negócios em que a ordem não executa: o lote de 1 ação fica atrás na fila e o negócio na mínima é isolado.
- **Valor justo sem informação:** o desconto de entrada contra o justo da véspera é de −1,9%, mas o fechamento do dia da compra contra o justo do mesmo dia é de +0,01%. O BDR não estava barato; o justo é que estava velho, porque a ação lá fora e o dólar já tinham se mexido.
- **O preço dos EUA não é simultâneo** (EUA às 16h ET, BDR às 17h Brasília, DOL às 16h). Isso não precisou ser modelado: a fila sozinha já mata o fundo.
- **Veredito:** REPROVADO. Sharpe deflacionado de 0,01% e PBO de 0 são coerentes com uma única regra "certa" de fill.

## 4. b3_leilao_noite: noite nos leilões após queda (`_aud4_leilao.py`, `_aud4b.py`, `fundos/b3_leilao_noite_aud.py`)
- **Mecânica:** confirmada. A decisão é tomada no fechamento de t (queda de pelo menos 3% contra a média das líquidas). A compra é no **leilão de fechamento de t+1** e a venda no **leilão de abertura de t+2**.
  - Retorno da noite = (1 + R total)/(P/O) − 1, com P e O brutos do mesmo dia, sem misturar ajustado com bruto.
  - O ticket médio é de R$ 5 mil. Num leilão de papel com ADV acima de R$ 50 milhões, o preço é único e o pequeno não move nada. **Executável.**
- **Custo, onde está todo o risco:**
  - O retorno bruto médio é de 16 bps por noite (mediana de 5,6 bps), em 1.363 noites OOS.
  - **Cada 1 bp por lado custa cerca de 2,3 pp a.a.** O ponto de empate fica em cerca de 11,6 bps ida e volta.

| ida e volta | 20k antes / depois IR | 50k antes / depois IR |
|---|---|---|
| 6 bps (só emolumentos 0,03% x 2, original) | 11,7 / 9,4 | 11,7 / 9,4 |
| **8 bps (+1 bp/lado de derrapagem de leilão)** | **7,1 / 5,6** | **7,1 / 5,6** |
| 10 bps | 2,6 / 1,9 | 2,6 / 1,9 |
| 12 bps (custo 2x) | −1,7 / −2,1 | −1,7 / −2,1 |

- **Dado:** 8,7% das aberturas dos negócios são iguais ao fechamento anterior, o que é compatível com o tick. O resultado vem da cauda: os 15 melhores negócios incluem AMER3 (jan/2023), PETR3/4 (fev/2021) e AMBP3. São gaps reais.
  - **Sem o 1% melhor dos negócios, o total vai de 112 para 35 pp**, então o fundo depende de noites de pânico.
  - A variante "todos" (noite incondicional) dá −5,5 pp: o edge é a reversão após venda forçada, não o prêmio da noite.
- **IR:** swing trade, com vendas mensais muito acima de R$ 20 mil, então não há isenção e paga 15%. O IRRF de 0,005% é compensável.
- **Veredito:** APROVADO COM CORREÇÃO, em +7,1 / +5,6. Exige operar todos os dias nos dois leilões. Antes de pôr dinheiro, medir em papel 3 meses de preço de leilão contra o COTAHIST.

## 5. cme_vxm: VXM vendido (`_aud5_vxm.py`, `_aud5b.py`)
- **Dados corretos:**
  - Ajustes de todos os vencimentos VX da Cboe CFE, de 2010 a 2026.
  - Os vencimentos batem com a regra da Cboe (quarta-feira 30 dias antes da 3ª sexta) em 203 de 210 casos; os outros 7 caem 1 dia antes, em feriado.
  - O último ajuste fica a 0,63 pt do VIX no vencimento.
  - O P&L é do próprio contrato carregado, sem salto de rolagem.
- **Choques com 1 VXM vendido** (o fundo carrega 1 com R$ 20 mil e 3 a 4 com R$ 50 mil):
  - fev/2018: −US$ 2.100 por contrato, ou −64,6% do patrimônio com 20k.
  - **mar/2020: −US$ 6.282 por contrato** (março 15,8→46,4, rola, abril 38,6→70,5), cerca de **R$ 31 mil, mais que o capital de R$ 20 mil**. Com 50k e 4 contratos, a queda foi de −97%.
  - ago/2024: −US$ 1.503 (−43,6% com 20k).
  - abr/2025: −US$ 2.111.
- **Margem e conta:**
  - O modelo deixa na IBKR 2x a margem (45% do nocional, cerca de US$ 720 por contrato), em média R$ 11 mil, que já é mais da metade do capital fora do CDI.
  - Num choque de 30 a 60 pontos, a perda passa de 3 a 5 vezes esse saldo em dias. A remessa do Brasil leva D+1/D+2, então a IBKR **liquida a posição no pico, no intradiário** (pior que o ajuste).
  - O backtest "atravessa" o pico e recupera, o que não acontece na prática.
  - Saldo para atravessar mar/2020 com 1 contrato: mais de US$ 7 mil (≈ R$ 37 mil), ou seja, 185% do capital de R$ 20 mil.
- **O OOS de 2021–26 não teve evento do tamanho de 2020.** A amostra completa de 2012–26 dá +14,8 pp (20k) e +8,2 pp (50k), com quedas de −87% e −97%.
- **Veredito:** REPROVADO. O risco de ruína é estrutural no tamanho mínimo de 1 contrato.

## 6. rev_carry_moedas e 7. db3_wdo_carry (`_aud67.py`)
**6, carry PF (OOS, pp a.a. de soma simples por perna, 20k):**
- WDO (comprado em real) **+9,9**; MSF vendido +6,3; MJY vendido +5,5; **conta IBKR (CDI perdido, remessas) −6,5**. Total bruto 15,2.
- Com 50k: WDO +6,8; CHF/JPY +4,5; conta −2,7.
- **Sem o WDO (só G10): +2,9 / +1,8 antes do IR e +1,3 / +1,2 depois**, com vol de 28% e queda de −44%.
- O lado vendido em iene/franco ganhou com a alta do dólar de 2021–24; é carry de financiador, não diversificação.
- Contratos inteiros: confirmado. A alavancagem média OOS é de **4,9x** com 20k e 2,1x com 50k. O fundo fica vendido em WDO em 68% dos dias.
- **A perna BRL é sintética** (PTAX + CDI − cupom), não o WDO real:
  - Correlação diária de 0,69 com o WDO vendido real (ajustes).
  - Superestima o carry em cerca de 0,6 pp por 1x de nocional (1,79% contra 1,18% a.a.), ou cerca de −1,6 pp com 20k.
- Sem os 10 melhores dias, −6,4 pp.

**7, WDO vendido:**
- O filtro de juro real acima de 4 ficou **ligado 100% do OOS**: na prática é "vendido sempre". O filtro escolhido no IS (2019–22) é o que evitou 2020.
- Com 20k (1 contrato ≈ 2,6x):
  - vol 32%, pior mês −20%, pior dia −10,9%;
  - **2024: −57,5 pp**; pior queda de −42%;
  - 1 WDO vendido de fev a mai/2020 teria perdido R$ 15,4 mil (**−77% de R$ 20 mil**).
- Com 50k (1,1x): vol 13%, pior queda −14% (2020 seria cerca de −31%), **+8,7 / +7,1**.

**É o mesmo trade?** O núcleo é o mesmo: o real comprado contra o CDI menos o cupom é a maior perna do 6. A correlação diária dos excessos em 2023+ é de só 0,39, por causa das pernas de iene e franco. Não carregar os dois.

**Vereditos:**
- 6: REPROVADO. Tirando o WDO, sobra G10 fraco, e a conta IBKR come 6,5 pp.
- 7: REPROVADO com 20k. APROVADO COM CORREÇÃO com 50k, como **beta de carry do real** (prêmio de risco, não alfa), em +8,7 / +7,1.

## 8. b3_ofertas_varejo (`_aud8.py`, `fundos/b3_ofertas_varejo_aud.py`)
- **Fonte:** dataset aberto de ofertas da CVM (não o IPE).
  - A data usada é o início da oferta (ICVM 400) ou o registro (Res. 160, com +1 pregão).
  - O preço só é usado como preço de compra, e a decisão de pedir é tomada antes dele, em toda oferta ("todos"). Não há look-ahead.
- **Amostra:** 27 negócios OOS. Das ofertas com varejo, 24 são ICVM 400 de 2021–22, e só 5 são Res. 160 de 2023–26.
  - **3 follow-ons (SBSP3 2024, CSAN3 2025, CSMG3 2026) somam cerca de 15 dos 23 pp OOS.**
- **Rateio:** a alocação Res. 160 usa 0,5x a média por pessoa física do próprio dado da CVM, o que é realista. A da ICVM 400 usa rateio de 30% quando a ação estreia em alta, o que é otimista para as ofertas quentes de 2021.

| ajuste | 20k antes / depois IR | 50k antes / depois IR |
|---|---|---|
| original (rateio 30%) | 4,2 / 3,5 | 4,2 / 3,5 |
| rateio 20% | 3,3 / 2,7 | 3,2 / 2,7 |
| rateio 10% | 2,3 / 1,9 | 2,2 / 1,8 |
| rateio 10% + fator 0,25 | 2,2 / 1,8 | 1,9 / 1,6 |
| **auditado: rateio 15% + pedido bloqueado 5 pregões** | **2,6 / 2,1** | **2,6 / 2,1** |

- O pedido bloqueado custa cerca de 0,27 pp a.a. Truncamento ok.
- **Veredito:** APROVADO COM CORREÇÃO. O edge é real, mas raro: depende de 1 a 2 ofertas grandes ao público geral por ano.

## 9. rev_pead (`_aud9.py`)
- **Datas:** DT_RECEB da 1ª versão de cada (CNPJ, período); 5.660 reapresentações foram descartadas. O intervalo mediano é de 45 dias após o trimestre.
  - Data de entrega posterior ao release só atrasa o sinal; não cria look-ahead.
- **Liquidez e custo:** ADV de pelo menos R$ 1 milhão, R$ 2 mil por papel, spread real mediano de 20 pregões, +0,2% no fracionário. Está ok.
  - Custo 2x: +4,2. ADV acima de R$ 5 milhões: +6,7. Execução t+2: +6,7.
- **Fragilidade:**
  - **limiar de 5% → −0,2 / −1,5**;
  - sem os 10 melhores, −3,8;
  - os 10 melhores dos 179 negócios OOS (ETER3 +138%, MRFG3, CEAB3...) somam cerca de 67 pp, contra 43,7 pp no total;
  - a perna vendida perdeu −8,5 pp;
  - 2024 e 2025 foram negativos;
  - Sharpe deflacionado de 7%.
- **Veredito:** REPROVADO. Só a compra dá +4,2 / +3,0 com 20k, mas não se distingue de sorte.

## 10. rev_opa e rev_debentures (`_aud10.py`, `_aud10b.py`, `_aud10c.py`)
**rev_opa:**
- 12 negócios OOS, sendo que **HBOR3 sozinho dá +5,6 pp dos 8,5 pp**.
- O FR da OPA saiu em 03/07/2026, com oferta de R$ 2,52 e preço de 2,36. No dia seguinte a ação caiu 26%, para 1,75, e o fundo comprou com spread de 44%, **acima do teto de 30% da própria regra**, que só é checado no preço da decisão. A posição saiu a 2,64.
- Com a regra checada no preço de execução, ou simplesmente sem HBOR3, o resultado é **~+0,5 pp a.a.** (isento).
- APROVADO COM CORREÇÃO, pequeno.

**rev_debentures:**
- São 5 debêntures de carry, todas ainda abertas e marcadas pelo último negócio do SND. Entre elas está CBRDB8 (Casas Bahia, −4,6 pp).
- Markup e haircut maiores (0,6 e 0,3): +1,8. Sem filtro de prateleira: +1,5. **n=10: +0,5 / +0,3** (50k +0,8 / +0,6).
- É carry de crédito com 5 nomes; o Sharpe deflacionado de 0,04% confirma que não há alfa.
- APROVADO COM CORREÇÃO, esperar cerca de +0,5 a +1.

## O que sobra para o top 5 PF (depois do IR, 20k / 50k)
1. b3_leilao_noite_aud: +5,6 / +5,6. Operacional e sensível ao custo.
2. db3_wdo_carry: só com 50k, +7,1. É beta de carry do real.
3. b3_ofertas_varejo_aud: +2,1 / +2,1.
4. rev_debentures e rev_opa: +0,3 a +0,5 cada.
5. db3_trava_bova: ~0.

Nenhum dos três primeiros do ranking original (cc_isenta, trava_bova, bdr_limite) sobrevive como alfa. Recomendo rodar de novo `rodar_pf.py um` para os três `_aud` e refazer o ranking antes do `top5`.
