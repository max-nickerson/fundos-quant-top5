# PF3 — internacional A: 5 estratégias internacionais refeitas com a conta em dólar v2

Tabelas completas (capital × sleeve × hedge, beta × alfa, variantes, 10 melhores e 10 piores negócios):
`pf/pesquisa/_pf3_internacional_A_tabelas.md`. Elas são geradas por `pf/pesquisa/_pf3_internacional_A.py`. As baterias estão em
`pf/resultados/bateria/<nome>_v2.pkl` e o resumo em `pf/resultados/pf3_internacional_A.pkl`.

## Resposta curta

Com a conta v2, **nenhuma das 5 vira alfa**. A conta nova trocou o custo da conta antiga (remessa por negócio, câmbio aberto e CDI
perdido só durante o negócio) por outro: **o sleeve parado deixa de render CDI e passa a render T-bill**. Isso custa ≈ (CDI − T-bill)
× sleeve/capital, cerca de **7,5% a.a. do sleeve** no OOS 2021+ (−1,9/−3,8/−5,6 pp do fundo com R$ 5/10/15 mil fora de R$ 20 mil).
Para valer a pena, uma estratégia precisa render mais que ~7,5% a.a. **sobre o sleeve inteiro**. Isso vale mesmo para as estratégias de
evento, que ficam investidas só uma fração do tempo.

- **Argentina** é a única que passa da conta, e por pouco: os papéis rendem ~11% a.a. sobre o sleeve. O resultado fica em +0,5/+1,0/+1,2 pp
  com R$ 20 mil (depois do IR, +0,45/+0,73/+0,76). Mas é **beta Argentina**: contra o ARGT, o alfa é −0,1 pp (t = −0,03), e o placebo
  dá p = 0,36.
- **Pânico de país com âncora (mecanismo 2):** a âncora **piorou** o resultado. A âncora de commodity/EEM baixou os papéis de +1,9 para
  +0,8 pp, e a de moeda para +1,2. A Rússia sozinha custa −11,25 pp do capital no evento (≈ −1,9 pp a.a.). Nenhuma âncora de preço a evita.
- **Russell (saídas) e spin-offs pequenos:** os papéis rendem 3–5 pp do fundo, menos que a conta. Os spin-offs dependem de um nome só
  (RHLD = 70% da contribuição OOS). Com "todos os tamanhos", o SNDK responde por 62 de 102 pp.
- **Noite em ETFs dos EUA:** os papéis já são negativos (−4,8 pp com R$ 20 mil/10 mil). No tamanho de PF, a comissão mínima da IBKR
  (US$ 0,35 por ordem em US$ 300–500) e a regra de liquidação da conta cash comem a reversão. O alfa é −8,3 pp com t = −3,2.
- **Sobre o "+3 a +10 pp" com R$ 50 mil, sleeve de R$ 37,5 mil e hedge inteiro:** é **sobre-hedge**. Um WDO de US$ 10 mil contra ~US$ 7 mil
  de sleeve deixa ~US$ 3 mil vendidos em dólar, ou seja, carry do real mais a apreciação de 2025–26. Isso dá **+2,7 pp de beta cambial**,
  o mesmo em todas as estratégias. Some-se a troca de T-bill por CDI − cupom no resto. Não é alfa da estratégia, e é a mesma razão do "+1,6"
  da conta vazia no BRIEF.

## Tabela principal: OOS 2021+ (2023+ no Russell), pp a.a. sobre o CDI, antes / depois do IR

Com R$ 20 mil e com R$ 50 mil/12,5 mil, o hedge "inteiro" arredonda para 0 WDO, então "nenhum" e "inteiro" dão o mesmo resultado.
O IR segue o executor: exterior a 15% ao ano, WDO a 15% na apuração mensal, e o CDI perdido também deixa de pagar os 15%.

| estratégia | 20k/5k | 20k/10k | 20k/15k | 50k/12,5k | 50k/25k nenhum | 50k/25k inteiro | 50k/37,5k nenhum | 50k/37,5k inteiro* |
|---|---|---|---|---|---|---|---|---|
| em_panico_pais_v2 (âncora moeda) | −1,8 / −1,4 | −3,4 / −2,9 | −5,3 / −4,6 | −1,7 / −1,3 | −3,4 / −2,8 | −6,9 / −6,3 | −5,2 / −4,5 | +3,0 / +3,7 |
| em_argentina_v2 | +0,5 / +0,5 | +1,0 / +0,7 | +1,2 / +0,8 | +0,5 / +0,5 | +1,0 / +0,8 | −1,7 / −1,9 | +1,2 / +0,8 | +10,1 / +9,5 |
| fg_russell_v2 | −0,7 / −0,4 | −1,3 / −1,0 | −3,1 / −2,7 | −0,8 / −0,6 | −1,8 / −1,5 | −3,5 / −3,1 | −3,1 / −2,7 | +6,3 / +5,6 |
| fg_spinoff_pequeno_v2 | −0,8 / −0,7 | −1,6 / −1,5 | −4,9 / −4,5 | −1,6 / −1,4 | −3,1 / −2,8 | −6,6 / −6,2 | −4,6 / −4,3 | +3,9 / +4,1 |
| lg_eua_etf_v2 | −7,0 / −6,4 | −9,4 / −8,3 | −10,2 / −8,8 | −3,8 / −3,2 | −5,2 / −4,4 | −9,2 / −8,4 | −6,6 / −5,6 | +1,5 / +2,5 |

\* 1 WDO contra ~US$ 7 mil: inclui +2,7 pp de câmbio aberto vendido em dólar, que é beta do real. Com 50k/25k, o hedge oscila entre 0 e 1
contrato (média de 0,14–0,22), e o câmbio aberto custou −2,4 a −4,2 pp: arredondar para 1 contrato com US$ 4,7 mil é uma aposta, não um hedge.

## Bateria (R$ 20 mil, sleeve padrão R$ 10 mil, hedge inteiro)

| fundo | IR OOS | PBO | P(bater 3a) | custo 2x | t+2 | sem 10 melhores | placebo p | walk-forward | truncamento |
|---|---|---|---|---|---|---|---|---|---|
| em_panico_pais_v2 | −0,31 | 6% | 28% | −3,7 | −3,8 | −8,3 | 0,21 | −2,7 | ok |
| em_argentina_v2 | 0,14 | 7% | 54% | +0,8 | +1,7 | −2,4 | 0,36 | +1,0 | ok |
| fg_russell_v2 | −0,03 | 1% | 41% | −2,2 | −2,1 | −7,4 | 0,11 | −1,1 | ok |
| fg_spinoff_pequeno_v2 | −0,12 | 0% | 39% | −1,8 | −1,6 | −6,4 | 0,50 | −1,6 | ok |
| lg_eua_etf_v2 | −1,37 | 0% | 1% | −14,8 | −8,5 | −10,2 | 0,98 | −5,2 | ok |

## Decomposição: papéis × conta × câmbio aberto (OOS, pp a.a. do fundo)

"Papéis" é o P&L do livro em US$ com os custos da IBKR, convertido pela PTAX do dia. "Conta" é o resto: CDI perdido sobre o sleeve,
T-bill do caixa, câmbio do saldo, WDO e IOF (o IOF só aparece no 1º dia de 2008, fora do OOS).

| R$ 20 mil, sleeve 10 mil | papéis | conta | papéis / sleeve (a.a.) |
|---|---|---|---|
| em_panico_pais_v2 (âncora moeda) | +1,18 | −3,76 | 2,4% |
| … sem âncora (sinal original) | +1,93 | −3,77 | 3,9% |
| … sem Rússia (filtro de sanção) | +3,13 | −3,90 | 6,3% |
| em_argentina_v2 | +5,41 | −3,95 | 10,8% |
| fg_russell_v2 | +3,98 | −4,17 | 8,0% |
| fg_spinoff_pequeno_v2 | +2,87 | −3,78 | 5,7% |
| lg_eua_etf_v2 | −4,79 | −3,72 | −9,6% |

Para empatar com o CDI, "papéis / sleeve" precisa passar de ~7,5% (CDI − T-bill). O Russell chega a 8,0%, mas com 7 reconstituições
e com IWM só a partir de R$ 11 mil.

## Beta × alfa (excesso diário OOS do fundo contra o ETF em US$ sobre o T-bill)

| fundo (20k/10k) | fator | beta | parte do beta (pp a.a.) | alfa pp a.a. | t |
|---|---|---|---|---|---|
| em_panico_pais_v2 | EEM | 0,02 | +0,1 | −2,7 | −0,7 |
| em_argentina_v2 | EEM | −0,04 | −0,2 | +1,7 | +0,4 |
| em_argentina_v2 | **ARGT** | 0,07 | **+1,6** | **−0,1** | −0,0 |
| fg_russell_v2 | IWM | 0,07 | +0,4 | −2,6 | −0,5 |
| fg_spinoff_pequeno_v2 | IWM | 0,11 | +0,7 | −1,6 | −0,5 |
| lg_eua_etf_v2 | SPY | −0,01 | −0,2 | −8,3 | −3,2 |

Os betas médios são baixos porque os livros ficam investidos só parte do tempo. O alfa já inclui o custo fixo da conta. Na Argentina, o
ARGT explica todo o resultado. Com 50k/37,5k e hedge inteiro, os "alfas" de +2 a +9 pp contra EEM/IWM/SPY são o câmbio vendido em dólar
(fator que não está na regressão). Contra o ARGT, o alfa cai a +4,7 com t = 1,1.

## Por estratégia

### 1. em_panico_pais_v2: pânico de país com âncora (mecanismo 2)
- **Implementação.** O sinal original é: o ETF cai ≥ 15% do topo de 21 pregões, compro 25% do sleeve por país, até 4 países, e seguro
  42 pregões. A ele somei uma âncora, testada na grade (âncora × queda 15/20% × 21/42 pregões):
  - *commod:* o resíduo do ETF contra a commodity do país tem que ser ≤ −10% em 21 pregões. As âncoras são petróleo (BNO) para EWZ/KSA,
    cobre (COPX) para ECH/EPU e ouro (GLD) para EZA. Os demais países usam o irmão EEM. O beta vem de 252 pregões e usa só o passado.
  - *moeda:* o câmbio real como âncora. O ETF caiu, mas a moeda local depreciou no máximo 5% em 21 pregões. Isso indica fluxo de resgate,
    não crise de balanço de pagamentos.
- **Escolha no IS.** O maior IR IS foi o **sem âncora** (0,51 com 15%/42). Entre as âncoras, a de moeda (0,45) venceu a de commodity
  (0,31). Usei a de moeda como PARAMS, porque o pedido era aplicar o mecanismo; o controle sem âncora está nas variantes. No OOS, todas
  as 12 variantes da grade são negativas com R$ 20 mil/10 mil (−1,8 a −4,2 pp).
- **Por que a âncora não ajudou.** Os negócios que pagaram foram pânicos *com* a âncora andando junto: TUR em set/2022 (+53%, com a lira
  caindo), EZA/ARGT/VNM no tarifaço de abr/2025 (EEM e commodities caíram juntos) e ARGT em out/2023 e set/2025 (o peso desabando). Nos
  emergentes, o pânico de fluxo e o de fundamento chegam juntos. Uma âncora que "divergiu" é rara e, quando aparece, costuma ser
  sanção ou controle de capital, o caso da Rússia. Isso é o contrário de PETR4 × Brent, em que a âncora é um preço negociável que
  continua de pé.
- **Rússia.** Conferi com dados da época: em 24/02/2022 o petróleo subia, então a âncora "commod" diverge ao máximo e compra. O rublo
  tinha depreciado só 3,5% em 21 pregões (78,65 → 81,41), então a âncora "moeda" também compra. A perda sintética de 90% do peso
  (25/02 → 04/03/2022) fica **ligada em todas as variantes**: −11,25 pp do capital com R$ 20 mil/10 mil. O "filtro de sanção" (não
  comprar país sob sanção ocidental vigente, a Rússia desde 2014) é uma regra ex-ante legítima. Mesmo com ele o resultado fica em −1,3 pp
  (papéis +3,1, abaixo da conta). Os ganhos russos de 2014–15 não entram, o que torna o viés conservador.
- **Negócios.** Melhores: TUR set/2022 (+6,4 pp), EZA abr/2025 (+4,0), ARGT out/2023 (+3,3), set/2025 e abr/2025. Piores: RSX sintético
  (−11,3), EPU/EWZ/VNM/ARGT abr–mai/2022 (−1,2 a −1,9, continuação da queda), EIDO 2026.

### 2. em_argentina_v2
- Mesmo sinal (cesta de 5 ADRs após −20% em 21 pregões, 50% do sleeve, 63 pregões) e mesmos custos. Os papéis rendem +5,4 pp com
  20k/10k (≈ 10,8% a.a. sobre o sleeve) e superam a conta por ~1 pp. 90% dos 30 negócios OOS ganharam, mas são 6 episódios correlacionados:
  CEPU/BMA/YPF em set/2023 (eleição de Milei: +3,8/+2,1/+1,9 pp), mar/2023, ago/2025 e abr/2025.
- **É beta Argentina.** Contra o ARGT, o alfa é −0,1 pp (t ≈ 0). Sem os 10 melhores, dá −2,4. O placebo dá p = 0,36. O ganho sobre a
  conta antiga (+1,5 → +1,0 com 20k/10k) não muda o diagnóstico da PF2.

### 3. fg_russell_v2
- Mesmo sinal: saídas para micro cap compradas no leilão da reconstituição, 60 pregões, 5% do livro por nome, até 20 nomes. A
  composição real vem do N-PORT do IWM, e a sobrevivência é neutra. O IWM vendido só entra com sleeve ≥ R$ 11 mil, porque a conta
  margem exige US$ 2 mil.
- Os papéis rendem +4,0 pp com 20k/10k (8% sobre o sleeve), contra uma conta de −4,2. O OOS tem só 4 reconstituições (2023–26) e 80
  negócios, com 56% de acerto. O retorno vem de poucos nomes: VTGN +4,8, RCEL +4,7, STIM +3,0, GALT +2,6. Sem os 10 melhores, −7,4.
  Com sleeve de R$ 5 mil, cada nome vale R$ 250, e a comissão mínima de US$ 0,35 pesa ~0,8% por lado.

### 4. fg_spinoff_pequeno_v2
- Mesmo sinal: a separada com giro < US$ 10 mi/dia entra 40 pregões depois do 1º preço e fica 12 meses, com 5% por nome e sintéticos
  pela classe do EDGAR.
- **SNDK não está no livro "pequeno"** (giro acima de US$ 10 mi). A concentração do livro pequeno é **RHLD**: +10,35 de +14,7 pp de
  contribuição OOS (70%), seguido de MPTI (+5,5). Sem RHLD, os papéis caem para +1,1 pp e o resultado para −3,5 pp.
- Variante "todos os tamanhos": +15,5 pp com 20k/10k, e o SNDK sozinho dá +61,7 pp de contribuição. **Sem SNDK fica em +3,75 pp**
  (depois do IR, +2,9; papéis +7,9), com RHLD e GEV no topo. Essa variante teria IR IS maior (IS +4,8 contra +3,9), mas ficou fora da
  grade original e é sensível a um ou dois nomes por ano. Vale como próximo teste, com limite de peso por nome e sem confiar no SNDK.

### 5. lg_eua_etf_v2
- Mesmo sinal: ETF dos EUA que caiu ≥ 2% no dia, comprado no MOC e vendido no MOO, até 3 por noite, com comissão IBKR e 1 bp de
  derrapagem.
- Com sleeve < R$ 11 mil, a conta é cash. Girar o mesmo caixa toda noite seria "good faith violation", porque a venda na abertura só
  liquida em D+1. Por isso usei metade do sleeve por noite.
- Os papéis são negativos em quase todos os tamanhos: −4,8 pp com 20k/10k e +0,15 só com R$ 37,5 mil. A PF2 já tinha mostrado que a
  reversão bruta é de poucos bps e que o placebo bate o sinal (aqui, p = 0,98). Com R$ 300–500 por ETF, a comissão mínima custa
  0,07–0,11% por lado. Os piores ETFs são XOP (−5,3), XBI (−3,6), OIH (−3,5), GDX (−3,2) e XME (−3,0): ETFs de commodity/biotech que
  continuam caindo à noite.

## O que deu certo / errado

- **Certo:** a conta v2 elimina a remessa por negócio e a revisão mensal do saldo. Sem hedge, o custo da conta ficou previsível
  (≈ 7,5% do sleeve ao ano) e linear no tamanho do sleeve. Truncamento ok nos 5. PBO ≤ 7%: as grades são pequenas e coerentes.
- **Errado:** o custo deixou de ser "por negócio" e virou "por real parado". Estratégias de evento que ficam investidas 20–40% do tempo
  não pagam 7,5% sobre o sleeve inteiro. O hedge em WDO inteiro só existe a partir de ~R$ 50 mil com sleeve ≥ R$ 27 mil, e mesmo assim
  vira aposta (sub ou sobre-hedge de 30–40%).
- **Mecanismo 2 nos emergentes:** reprovado. A âncora divergente é rara e, quando aparece, é sinal de sanção ou controle de capital (a
  Rússia), não de vendedor forçado.

## Premissas, limitações, bugs

- O livro é dimensionado pelo sleeve (conta cash não passa do saldo). O original dimensionava pelo capital, o que concentrava mais.
- A conta margem (US$ 2 mil) é decidida com um câmbio fixo de R$ 5,5 (`pf3a_comum.tem_margem`), para não depender do câmbio futuro.
  Abaixo disso não há IWM vendido (Russell/spin) e as noites usam metade do sleeve.
- O P&L em US$ é extraído dos motores antigos pela identidade ext − câmbio + remessa (`pf3a_comum.usd_de_ext`). O custo de conta antigo
  é descartado e os custos dos papéis ficam intactos.
- A `pf.conta_usd` cobra o IOF no 1º dia do calendário (2008). No OOS a conta já está montada.
- O `classes_ir` devolve o dict da `conta_usd` ('exterior', 'futuros_b3', 'cdi_perdido'), com `CONTA_USD_V2 = True`.

## Próximos passos

1. **Um sleeve para várias estratégias.** O custo é por real parado, então o mesmo sleeve precisa servir a eventos de calendários
   diferentes, como Russell em junho, pânicos e spin-offs. Isso é engenharia de utilização, não combinação de sinais. Medir a
   utilização média de cada livro e o pico simultâneo.
2. Spin-offs "todos os tamanhos" com teto de peso por nome e sem SNDK. Validar fora de 2025 (RHLD/GEV).
3. Russell semestral (FTSE passa a reconstituir em dezembro a partir de 2026): dobra os eventos com o mesmo sleeve.
4. Abandonar `lg_eua_etf` em tamanho de PF: comissão mínima e liquidação D+1.
