# Frente deriv_b3: derivativos da B3 para pessoa física com garantia em Tesouro Selic

Sete fundos novos (`pf/fundos/db3_*.py`). Peças comuns ficam em `db3_base.py` e o runner é `db3_rodar.py`. Os resultados estão em
`pf/resultados/deriv_b3.pkl`, um por fundo em `pf/resultados/deriv_b3/*.pkl`, e os logs em `pf/resultados/log_db3_*.txt`. Toda a
garantia fica em Tesouro Selic, que rende o CDI (o benchmark). Por isso o excesso é o P&L dos derivativos dividido pelo capital.
A exceção é o dinheiro aplicado em ação ou ETF, que deixa de render o CDI e é contado como custo de oportunidade. As posições são
sempre em contratos e lotes inteiros, com decisão em t e execução em t+1. O teste de truncamento passou nos 7 fundos (20k e 50k).

## Resultado (fora da amostra, líquido de custos de varejo)

| Fundo | Aplicável? | OOS desde | Ativo vs CDI 20k (antes / depois do IR) | Ativo vs CDI 50k (antes / depois do IR) | IR 20k / 50k | PBO 20k / 50k | P(bater 3a) 20k / 50k | Pior queda OOS 20k |
|---|---|---|---|---|---|---|---|---|
| Put coberta por Selic (PETR/VALE/ITUB/BOVA) | sim | 2021 | −1,1 / −1,1 | −0,5 / −0,5 | −0,11 / −0,04 | 5% / 6% | 41% / 46% | −11% |
| Trava de alta com put em BOVA11 | sim | 2021 | **+1,9 / +1,5** | **+2,0 / +1,7** | 0,67 / 0,64 | 4% / 2% | 96% / 95% | −3% |
| WDO vendido (carry do real) | 20k: 2,7x | 2023 | **+19,4 / +14,8** | **+8,7 / +7,0** | 0,66 / 0,65 | 46% / 44% | 84% / 88% | **−42%** |
| Milho CCM comprado | 20k: 1,5x | 2023 | −32,8 / −32,2 | −19,4 / −19,1 | −1,56 / −1,38 | 27% / 18% | 1% / 2% | −64% |
| WIN reversão/tendência | sim | 2021 | −12,1 / −11,9 | −5,5 / −5,5 | −0,50 / −0,30 | 37% / 55% | 14% / 24% | −41% |
| Covered call em ações isentas | sim | 2021 | +11,8 / **+12,9** | +10,0 / +10,1 | 0,85 / 0,59 | 52% / 49% | 91% / 83% | −14% |
| Base WIN x BOVA11 no vencimento | não | 2023 | −0,2 / −0,2 (não opera) | −1,3 / −1,6 | n/d / −1,31 | 48% / 39% | 0% / 0% | 0% |

O CDI no período OOS foi de 11,4% a.a. (a partir de 2021) e 13,1% a.a. (a partir de 2023). Depois do IR, a comparação é com o CDI
depois de 15% de IR (9,7% e 11,1%). Custo 2x e t+2 com R$ 20 mil: put −2,2 e −1,4; trava +1,3 e +1,2; WDO +18,8 e +19,4; CCM −33 e −33;
WIN −12 e −9; covered call +11,4 e +12,2; base −0,2 e −0,2. Leque 50k (p5 / mediana / p95): put −1,1 / 0,0 / +0,5; trava −3,4 / +1,7 / +2,8;
WDO 8,7 nos três (o filtro de juro real ficou ligado o OOS inteiro: a vizinhança não muda nada); CCM −20 / −18 / −11; WIN −8 / −5,5 / +0,5;
covered call +9,4 / +10,5 / +11,1; base −1,4 / −1,0 / −0,9.

## 1. Put coberta por Tesouro Selic (`db3_put_selic.py`)
**Tese.** Vender seguro (put de 1 mês, 3% OTM) a quem quer proteção, deixando o strike inteiro em Selic. Só vendo quando a IV ATM
está acima da vol realizada de 21 dias. A alocação é gulosa, por lote inteiro de 100 ações: começa no papel de maior prêmio
(IV − RV), com no máximo 50% do capital por papel.

**Dados.** Opções mensais do COTAHIST com bid/ask (2014+), ação bruta do COTAHIST e BOVA11 bruto do Yahoo.

**Resultado.** Dentro da amostra deu +11,6 pp. Fora da amostra deu −1,1 pp com 20k e −0,5 pp com 50k. Nenhuma variante da grade
bate o CDI com 20k. O PBO baixo (5%) só confirma que a escolha dentro da grade não foi overfitting; quem morre é a estratégia
inteira. Com custo zero o resultado OOS fica em +0,0 / +0,7 pp: o spread das opções come o prêmio. Esse é o mesmo achado da pesquisa
A4.

**Quem trouxe o retorno.** Todo o ganho dentro da amostra veio de 2015–16, com puts de VALE e PETR vendidas com IV de 60–250% no
fundo do ciclo das commodities. Por ativo, em pp: VALE +61, BOVA +8, ITUB +5, PETR −1,5.

- 10 melhores: VALE 2015-05 +6,6 pp; VALE 2016-01 +6,0; VALE 2015-08 +3,8; VALE 2014-03 +3,2; VALE 2016-07 +3,2; PETR 2016-01 +3,2;
  VALE 2016-02 +3,1; VALE 2015-09 +3,0; VALE 2016-12 +2,9; PETR 2016-04 +2,9.
- 10 piores: PETR fev/2020 (Covid, 3 lotes, −24,2 pp); VALE dez/2015 −6,7; PETR fev/2021 (troca do CEO) −5,0; VALE jul/2021 −5,0;
  PETR fev/2024 −4,4; PETR set/2014 −4,2; PETR fev/2014 −3,5; PETR fev/2017 −3,4; VALE jul/2023 −3,0; PETR mar/2019 −2,8.

**O que deu errado e por quê.** Depois de 2021 a IV de PETR e VALE caiu para 25–35%. Nesse nível o prêmio de 1–2 pontos de vol
é menor que o meio spread de bid na venda mais o exercício. O filtro de tendência (só vender put com o papel acima da média de 100
dias) PIORA o resultado dentro da amostra: o prêmio mais gordo está justamente no papel em queda. Ele foi descartado pelo IS.

## 2. Trava de alta com put em BOVA11 (`db3_trava_bova.py`)
**Tese.** Vender a put 5% OTM e comprar a put 10% OTM de 1 mês. A perda máxima é conhecida e limitada a 10% do capital por ciclo.
Só monto com IV > RV e BOVA11 acima da média de 100 dias.

**Resultado.** Fora da amostra deu +1,9 pp com 20k e +2,0 pp com 50k, com IR 0,67, vol de 2,5% e acerto de 96% (23 negócios). O
resultado sobrevive a custo 2x (+1,3) e t+2 (+1,2), e o placebo dá p = 0,00.

**Ressalvas.**
- Antes de 2019 não há ciclo negociável: as opções de BOVA11 tinham spread acima de 25% do meio. A amostra efetiva é 2019–2026,
  e o "IS" é na prática 2019–2020, apenas 7 ciclos.
- É venda de cauda. Nenhuma trava chegou perto da perda máxima (pior −1,4 pp em fev/2021), mas um único mês de −10% apaga cerca de
  5 anos de ganho.
- O leque p5 é −3,4 pp: com strikes mais próximos (2–3% OTM) o resultado vira perda.

**Por que funciona.** O skew de índice paga (IV da put 90% bem acima da ATM). A trava vende a parte cara do skew e compra a
cauda, e o filtro IV > RV evita os meses em que o prêmio não existe.

**Negócios.**
- Melhores: jun/2020 +1,6 pp (IV 39% no pós-Covid); set/2026 +1,3; set/2022 +1,2; jan/2022 +1,1; ago/2020 +1,0; ago/2022 +1,0;
  dez/2020 +1,0; abr/2021 +0,9; jul/2020 +0,9; set/2020 +0,9.
- Piores: fev/2021 −1,4 (intervenção na Petrobras). Os outros 9 "piores" foram todos levemente positivos, entre +0,1 e +0,3: a
  trava expirou sem valor e o crédito era pequeno.

## 3. Mini-dólar vendido, o carry do real (`db3_wdo_carry.py`)
**Tese.** Vender WDO deixando a garantia em Selic rende CDI − cupom cambial (8–11% a.a. de 2022 a 2026), pago pelo hedger que
compra dólar futuro.

**Filtros (escolhidos no IS 2019–2022).**
- O escolhido foi só juro real ex-ante (Selic − IPCA 12m do Focus) acima de 4%.
- O filtro de VIX e o de CFTC (especuladores aumentando a posição em real) pioraram o IS e ficaram fora.
- Sem o filtro de juro real, o IS é −17,6 pp: em 2019–2021 o carry era de 2–4% e o real caiu 30%.

**Resultado e risco.**
- Fora da amostra deu +19,4 pp com 20k e +8,7 pp com 50k, com IR 0,65 nos dois.
- Com 20k o fundo carrega 1 contrato (US$ 10 mil, cerca de 2,7x o capital). A vol é de 32% e a pior queda é −42%.
- Ano a ano (20k, pp): 2022 +38, 2023 +43, 2024 **−52**, 2025 +81, 2026 +50. Com 50k a pior queda é −14%.
- O resultado é o carry mais um real que se valorizou em 2023 e 2025. Sem os 5 melhores meses, o ganho com 20k cai para +1,2 pp.
- PBO de 46%: o "filtro" só decide se 2019–2021 entra ou não. Isso é risco de regime, não alfa.

**Negócios (1 por contrato mensal).**
- Melhores: mar/2022 +22 pp (Selic 11,75%, fluxo para commodities); jan/2025 +17 (reversão do pânico fiscal de dez/2024);
  jan/2026 +15; jan/2022 +15; ago/2022 +14,5; mai/2022 +13; abr/2026 +13; jun/2025 +11,5; out/2026 +11; fev/2022 +11.
- Piores: jun/2022 −25 (Fed acelerando); jun/2024 −15 (fiscal e Copom dividido); out/2024 −15; set/2022 −14 (eleição);
  dez/2024 −12,5 (pacote fiscal); set/2023 −9; abr/2022 −8; nov/2024 −7; dez/2025 −6; abr/2024 −6.

## 4. Milho B3 comprado, o prêmio de hedge (`db3_agro_ccm.py`)
**Tese.** Ficar do outro lado do produtor que vende futuro para travar a safra (pesquisa C5: comprado em agro B3 rendeu 8–15% a.a.
em 2018–2026). Só o milho cabe no capital: 1 CCM ≈ R$ 25–35 mil. BGI, ICF, SJC e ETH custam de R$ 55 mil a R$ 200 mil por
contrato.

**Resultado.** Dentro da amostra, 2018–2022 (a alta do milho de R$ 40 para R$ 90), deu +17 a +20 pp. Fora da amostra deu −33 pp
com 20k e −19 pp com 50k, com pior queda de −64% e −39%. A safra recorde de 2023 derrubou a saca de R$ 88 para R$ 55.

**O que aprendi.** O "prêmio de 8–15%" medido na pesquisa era a alta de 2020–21, e não um prêmio estrutural. Com um único mercado
não há diversificação que dilua a quebra de 2023. A variante de tendência (preço acima da média de 100 dias) foi a única quase
neutra no OOS (−4 / +2 pp). O filtro de curva, escolhido no IS, ficou comprado justamente na curva invertida do pico de 2022–23.

**Negócios.**
- Melhores: ago–nov/2020 +69 pp; jun/2021 +23; jan–jun/2021 +22; jan–jul/2018 +13; jan–jul/2020 +13; jan–mai/2025 +10;
  out/2019 +10; mai/2019 +7 e +5; nov/2018 +4.
- Piores: fev–mai/2023 −59; jan–mai/2024 −33; jan–abr/2026 −14; jun/2021 −13; jan–mai/2019 −12; jan/2023 −11; jan–abr/2022 −11;
  nov/2024 −8; jul/2021 −8; jan/2018 −3.

## 5. Mini-índice WIN, 1 contrato (`db3_win_regime.py`)
**Implementação.** O WIN não está em `quant/dados/futuros.parquet`, que só tem DOL, WDO, DI1, DDI, FRC e DAP. Usei o ^BVSP
(índice de retorno total) como preço: P&L = n × 0,2 × Ibov × (r − CDI), com custo de rolagem bimestral.

**Resultado.**
- Grade de 12 variantes: tendência com e sem posição vendida, reversão de 5 dias, janelas de 50 e 200 dias, com e sem VIX.
- A melhor no IS foi a reversão com janela de 200 dias: IR 0,16 e +1,3 pp, ou seja, nada.
- Fora da amostra deu −12 pp com 20k e −5,5 pp com 50k.
- A tendência de 50 dias com posição vendida deu +11 pp no OOS, mas −1,5 pp no IS. Escolher essa variante agora seria olhar o
  futuro.
- 1 contrato é de 1 a 2x o capital de 20k, então os erros de timing aparecem inteiros no resultado.
- O efeito de vencimento está no fundo 7.

**Negócios.**
- Melhores: out/2008 +17 pp; dez/2008 +15; fev/2020 +12; nov/2020 +10; mar/2020 +8; out/2021 +8; abr/2020 +8; fev/2010 +8;
  nov/2014 +8; abr/2016 +8.
- Piores: mar/2020 −20 (comprado na reversão enquanto o pânico continuava); jun/2013 −17; jan/2026 −16; out/2008 −13,5; mai/2026 −12;
  mai/2018 (greve dos caminhoneiros) −12; ago/2022 −12; fev/2016 −12; jan/2017 −10; set/2026 −10.

## 6. Covered call em ações isentas (`db3_cc_isenta.py`)
**Tese.** Carregar lotes de 100 de PETR4, VALE3 e ITUB4. As vendas de até R$ 20 mil por mês são isentas de IR, assim como os
dividendos. Vendo a call 10% OTM quando a IV está acima da mediana dos 12 ciclos anteriores.

**Resultado.** Fora da amostra deu +11,8 pp com 20k e +10,0 pp com 50k. Depois do IR fica em **+12,9 pp**: a parte em ações é
isenta e o benchmark paga 15%. Essa é a vantagem genuína de PF.

**Mas não é alfa de opção.** Só as ações dariam +13,8 pp no OOS (+11,0 no IS). O overlay de calls tira −1,8 pp no OOS e −5,1 pp no
IS (−2,2 e −4,9 com 50k), e todas as variantes de overlay perdem. Por ativo, em pp: ação PETR +98, VALE +40, ITUB +31; call PETR −29,
ITUB −5, VALE −3.

**O que deu certo e por quê.** O fundo é beta de três blue chips mais a isenção. Os dividendos gigantes da PETR em 2021–23 e a
recuperação de 2016 dominam o resultado. O filtro de IV alta só reduz o estrago das calls. PBO de 50%: as variantes são
praticamente iguais.

**Negócios.**
- Melhores: PETR ação 2016 +32 pp; VALE 2016 +25; PETR 2018 +17; PETR 2026 +16; PETR 2022 +16; PETR 2023 +15; VALE 2017 +14;
  PETR 2020 +11; ITUB 2025 +10; VALE 2023 +9,5.
- Piores: call PETR fev/2016 −20 pp (PETR +60% num mês); VALE ação 2015 −16; ITUB 2021 −12; PETR 2015 −10,5; call PETR mar/2015 −9;
  PETR 2014 −9; VALE 2014 −8; ITUB 2015 −7; call PETR jul/2022 −6; call ITUB fev/2016 −5.

## 7. Base WIN x BOVA11 no vencimento (`db3_base_win.py`)
**Tese.** É o A9 da pesquisa em tamanho de varejo: 1 WIN contra cerca de 200 cotas de BOVA11. A taxa implícita do WIN fica quase
sempre ABAIXO do CDI, então o lado útil é comprar WIN e vender BOVA11 alugado.

**Por que não funciona para PF.**
- Bruto (custo zero) o lado reverso deu +1 a +1,5 pp, igual ao institucional. Mas a corretora cobra 0,5% do volume por contrato
  de aluguel, contra um ganho médio de ~0,1% por vencimento. Líquido fica em −3 a −5 pp.
- O lado direto (comprar BOVA11 e vender WIN) exige R$ 25–41 mil em BOVA11. Com 20k só coube 5 vezes, todas antes de 2021, e
  perdeu.
- Escolhido no IS (o menos ruim): só o lado direto. Deu −0,2 pp com 20k (não opera no OOS) e −1,3 pp com 50k.
- **Não aplicável.**

**Negócios (20k).** Só 5, todos perdedores: WINM20 −0,8 pp; WINJ20 −0,5; WINM19 −0,4; WING19 −0,3; WINJ19 −0,0.

## Bugs e premissas corrigidas (anotados nos módulos)
- `b3_acoes_cotahist.parquet` tem só 92 dias de BOVA11 (codbdi 14 filtrado). A primeira versão do put e da trava praticamente não
  operava BOVA11. Agora o BOVA11 vem do Yahoo (`y_proventos`, preço bruto).
- Duplicatas nos dados:
  - `b3_futuros_agro.parquet` tem cada linha repetida até 6x;
  - `futuros.parquet` tem 84 mil pares data/ticker repetidos, um deles com ajuste vazio.
  Os dois foram deduplicados em `db3_base.futuros`.
- Um dia sem ajuste (feriado só na B3) zerava a posição e reabria no dia seguinte, pagando custo e perdendo o P&L. Corrigido com
  `ffill(limit=5)` do nocional.
- A posição de opção ainda aberta no fim dos dados era liquidada pelo intrínseco antes do vencimento. Agora fica marcada no meio.
- Os dias até o vencimento eram contados no calendário de `comum.DIAS`, que termina em out/2026. Os contratos que vencem depois
  sumiam e as posições paravam em ago/2026. Agora a contagem usa `np.busday_count`.
- O carry do WDO (sempre ligado no OOS) virava 1 negócio só, e a atribuição ficava vazia. Agora os negócios são quebrados por
  contrato.
- Custos premissados: opções 0,10% do prêmio por lado mais bid/ask real; exercício 0,14% do nocional; WDO R$ 4 por lado; WIN R$ 1,10;
  CCM R$ 6; ações 0,11% por lado; aluguel 0,5% do volume (corretora) + 1% a.a. (doador).
- JCP tratado como isento no covered call. É otimista em 0,1–0,2 pp a.a. para ITUB4.
- O IR (info ratio) da base com 20k é n/d: o desvio-padrão é zero porque ela não opera.

## Próximos passos
1. **Trava em BOVA11.** Testar opções semanais (2024+) e travas com largura fixa em pontos de vol. Medir a perda de um mês de −10%
   com simulação histórica 2008/2020 sobre o skew. Combinar com a venda de variância do S&P (dois prêmios de vol, mercados
   diferentes).
2. **WDO.** O tamanho mínimo de 1 contrato é o problema com 20k. Só faz sentido com R$ 50 mil+, ou com um stop por drawdown da cota.
   O regime de juro real é o que separa 2019–21 de 2022–26: testar com mais história (DOL desde 2008, via cupom DDI e PTAX).
3. **Agro.** Cesta comprada só é possível com capital de R$ 300 mil ou mais (BGI, ICF, SJC). Para PF, apenas como hedge de inflação
   de alimentos, não como alfa.
4. **Covered call isenta.** Ficar com a parte das ações (isenção) e trocar a call por venda de put coberta só nos picos de IV acima de
   60%, que foi o que funcionou em 2015–16.
