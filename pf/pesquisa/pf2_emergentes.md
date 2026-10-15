# Frente PF2 — emergentes e fronteira (ETFs/ADRs na IBKR, só o necessário fora)

Rodada PF2 ("testa tudo"). 8 estratégias novas, todas em `pf/fundos/em_*.py`, motor comum em `pf/fundos/em_comum.py`, dados em
`pf/dados/pf2_emergentes/yahoo.parquet` (Yahoo, OHLC bruto + Adj Close + volume, 2005–14/10/2026, 15 MB). Cada fundo rodou com
`python pf/rodar_pf.py um <arquivo>`, e o truncamento passou em todos. Os resultados estão em `pf/resultados/bateria/em_*.pkl` e em
`pf/resultados/pf2_emergentes.pkl`, e as tabelas são geradas por `pf/pesquisa/_em_relatorio.py`.

## Resumo em uma frase

**Nenhum dos 8 gera alfa para pessoa física.** O único positivo é a Argentina no pânico, com +1,5 pp a.a. OOS (+1,4 depois do IR), mas
isso é beta Argentina (contra o ARGT o beta é 0,27 e o alfa −1,0 pp; o placebo dá p = 0,38). O pânico de país **funciona nos papéis**
(+6,9 pp a.a. OOS antes dos custos da conta), porém a estrutura da conta lá fora come tudo: IOF da remessa a cada negócio, CDI perdido
no saldo da IBKR, câmbio aberto nesse saldo e a Rússia em 2022.

## O que a conta lá fora custa (a descoberta da frente)

Decomposição do excesso OOS em pp a.a., com R$ 20 mil (detalhe por fundo na tabela grande abaixo):

| fundo | papéis (P&L dos ativos já com corretagem/spread) | remessa (IOF + spread) | câmbio do saldo | CDI perdido | Rússia sintética |
|---|---|---|---|---|---|
| Argentina no pânico | +10,9 | −2,2 | −3,1 | −3,0 | — |
| Pânico de país | +6,9 | −4,1 | −3,0 | −4,7 | −3,9 |
| Fronteira (ETF x bolsa local) | −0,6 | −4,3 | −2,1 | −1,9 | — |
| ADR China x HK | −8,3 | −1,7 | −0,4 | −11,2 | — |

- **Remessa:** cada negócio de evento manda o dinheiro e traz de volta. A ida custa 1,1% de IOF + 0,5% de spread, a volta 0,38% + 0,5%,
  ou seja, ~2,5% da posição por ida e volta. Com 25% do capital por negócio e ~10 negócios por ano, isso dá ~4 pp a.a. No institucional
  esse custo não existia.
- **CDI perdido:** o saldo na IBKR não rende e fica lá pelo menos até a revisão mensal (`pf.custo_conta_exterior`). Nos livros L/S que
  ficam sempre ativos (China, Índia) usei `conta="anual"`, que guarda o maior exigido em 12 meses para não pagar IOF todo mês, e o
  custo vira CDI perdido. No caso China/HK, o Reg T de duas pernas mais o mínimo de US$ 2.000 deixam ~90% do capital parado em dólar.
- **Câmbio:** o saldo em dólar oscila com o real. Com R$ 50 mil, o hedge com WDO vendido (`hedge_fx="wdo"`, a partir de US$ 8 mil, sem
  sobre-hedge) compensa a perda cambial: no pânico de país, câmbio −3,0 e WDO +3,3. Com R$ 20 mil não cabe nem um contrato.

## Tabela final (OOS; capital R$ 20 mil salvo indicação)

| fundo | OOS desde | antes IR 20k | antes IR 50k | depois IR 20k | depois IR 50k | IR | PBO | P(bater 3a) | sem 10 melhores | beta EEM / alfa |
|---|---|---|---|---|---|---|---|---|---|---|
| em_argentina — ADRs no pânico (CCL) | 2021 | +1,46 | +1,52 | +1,43 | +1,49 | 0,16 | 21% | 53% | −5,2 | 0,12 / +2,9 |
| em_panico_pais — ETF de país após −15% em 21d | 2021 | −10,83 | −7,35 | −10,66 | −7,24 | −0,58 | 12% | 13% | −20,8 | 0,29 / −8,1 |
| em_eleicoes — ETF após pânico eleitoral | 2021 | −2,50 | −3,55 | −2,46 | −3,50 | −0,53 | 71% | 13% | −2,4 | 0,03 / −2,1 |
| em_china_adr_hk — ADR x HK | 2023 | −23,46 | −20,56 | −23,06 | −20,21 | −1,27 | 49% | 1% | −40,6 | 0,11 / −22,3 |
| em_india_adr — prêmio do ADR x NSE | 2021 | −9,75 | −9,03 | −9,60 | −8,89 | −0,90 | 44% | 4% | −15,0 | 0,13 / −8,3 |
| em_latam_commod — EC/SCCO/BVN/ECH/EPU x commodity | 2021 | −2,82 | −1,72 | −2,78 | −1,70 | −0,39 | 55% | 20% | −6,8 | 0,07 / −2,2 |
| em_fx_exportadoras — exportador x país no pânico cambial | 2021 | −15,61 | −11,59 | −15,37 | −11,42 | −1,17 | 42% | 0% | −23,6 | 0,10 / −14,0 |
| em_fronteira — ETF x bolsa local (VNM/TUR/EIDO/EWM/EZA) | 2021 | −9,62 | −9,58 | −9,48 | −9,43 | −2,13 | 31% | 0% | −11,0 | 0,05 / −8,8 |

"beta EEM / alfa" é a regressão do excesso diário OOS (R$ 20 mil) no excesso do EEM em R$ sem hedge: beta e alfa em pp a.a. Todos os
parâmetros foram escolhidos pelo maior IR **dentro da amostra** na grade. Em vários casos (latam_commod, fronteira) todas as variantes
eram negativas já no IS, e o "escolhido" é só o menos ruim.

## Tese, implementação e resultado por fundo

### 1. em_argentina — ADRs argentinos no pânico, escolhidos pelo CCL implícito
- **Tese.** Quem vende o ADR no pânico (PASO 2019, Guzmán 2022, Buenos Aires set/2025) é o estrangeiro que precisa sair, e o argentino
  que compra via CCL chega depois. O CCL implícito de cada ação (preço em pesos × razão / ADR) mostra qual ADR foi mais vendido. Ao
  contrário do G7 institucional, que operava o desvio todo dia em L/S, aqui o CCL serve só para escolher **dentro** do pânico.
- **Regra.** A cesta igual de YPF, GGAL, BMA, PAM e CEPU cai mais de 20% do topo de 21 pregões. Compro 50% do capital e seguro 63 pregões.
  No IS, a escolha pela cesta (IR 0,22) ganhou da escolha pelo CCL (0,18), então **o CCL não acrescentou nada**. Os fechamentos de BA e
  NY são quase simultâneos, e as razões ficaram estáveis em todo o período. O YPFD.BA do Yahoo vem em escala 1/10, o que é corrigido
  por constante.
- **Resultado.** +1,46 pp (20k) e +1,52 pp (50k), +1,4 depois do IR, PBO 21%. Porém o placebo dá p = 0,38, sem os 10 melhores o
  resultado vai a −5,2 pp, e contra o ARGT o beta é 0,27 com alfa −1,0. Os ganhos vieram de ter ficado comprado na alta argentina de
  2023 (CEPU +76% de set a dez/2023), de 2014–15 e de 2025. As perdas, de 2008, 2011, 2012, 2018 e PASO 2019. **É beta Argentina com
  timing de pânico, não alfa.**

### 2. em_panico_pais — pânico de país (TUR, EWZ, ARGT, EZA, EWW, ECH, EPU, INDA, EIDO, VNM, KSA)
- **Tese.** Quando um país cai mais de 15–25% em 3–6 semanas, o varejo estrangeiro resgata o ETF, e o AP vende a cesta local sem olhar
  preço. Compro 25% do capital por país e saio em 21–42 pregões.
- **Sobrevivência.** RSX/ERUS (Rússia) foram congelados em 03/2022 e não estão no Yahoo. Uma regra de "−15% em 21 dias" teria comprado a
  Rússia em 24–25/02/2022, então lancei uma perda sintética de 90% do peso em 04/03/2022 (−22,5 pp de uma vez, −3,9 pp a.a. no OOS).
  Os ganhos russos de 2014–15 não entram, o que torna o viés conservador. EGPT, NGE e PAK também morreram, mas estão fora da lista pedida.
- **Resultado.** −10,8 pp (20k) e −7,4 pp (50k, com o WDO protegendo o saldo). Sem a Rússia, −6,3 pp (20k) e −2,6 pp (50k). Nos papéis o OOS é positivo
  (+6,9 pp a.a.): TUR set/2022 +55%, EZA/ARGT/VNM abr/2025 +17–32%, ARGT out/2023 +29%, ARGT set/2025 +26%. As perdas vieram de
  continuações como EPU/EWZ/VNM/ARGT em abr–mai/2022 (−11 a −14%) e EWW jun/2024 (−11%). PBO 12%: a grade é coerente, e todas as 24
  variantes ficam negativas no OOS.

### 3. em_eleicoes — eleições EM com regra fechada
- **Tese e regra (definidas antes).** A lista fechada de 16 emergentes 2009–2026 vem do IM9, acrescida das eleições já realizadas em
  2025–26: Polônia, Chile nov/2025, Peru abr–jun/2026 e Brasil 04/10/2026. Pânico é a queda do ETF de mais de 3% ou 6% entre a véspera
  e o 1º pregão. O filtro "moeda" (o "próximo passo" do IM9) não compra quando a moeda caiu mais que metade da queda do ETF, porque isso
  indica fuga de capital, ou seja, uma mudança de política. O IS escolheu queda de 3%, 21 dias e filtro moeda.
- **Bug corrigido.** O "Close" de moedas do Yahoo no dia t é a cotação do **início** de t. O México em 03/06/2024 aparecia com o peso
  estável, quando na verdade caiu 4%. Para o filtro passei a usar a linha seguinte, publicada por volta de 20h ET, antes da execução.
- **Resultado.** −2,5 pp, com só 7 negócios no OOS. Ganhou com Chile dez/2021 (+17%) e Índia jun/2024. Perdeu com Chile set/2022
  (−12%), Peru jun/2021 (−9%), México jun/2024 e Argentina set/2025 (com 21 dias, saiu antes da alta de outubro). O filtro de moeda
  não mudou nenhum negócio do OOS. É uma loteria de poucos eventos, e não dá para separar ruído de mudança de regime com regra.

### 4. em_china_adr_hk — ADRs chineses x Hong Kong (12 pares)
- **Tese.** O prêmio do ADR sobre a linha de HK desvia por fluxo forçado (HFCAA 2022, Southbound, MSCI). O PF não converte, então
  aposta na volta do desvio comprando a listagem barata e vendendo a cara, com no máximo 2 pares e lotes inteiros de HK.
- **Execução honesta de fuso.** A execução é no próximo fechamento de cada praça, então a parte do desvio que é só fuso não é
  capturada. O prêmio bruto fica em ~0 em todos os anos, o que confirma as razões (BABA 8, JD 2, BIDU 8, NTES 5, LI/XPEV 2, BEKE 3).
- **Bugs corrigidos.** (a) O filtro de salto de razão (`pre_corrigido`) acumulava como "degrau" os dias de fuso de mar/2022, com prêmio
  de −23% num dia e +53% no seguinte. Ele foi desligado, porque as razões são estáveis. (b) Sem limite de pares, o livro chegava a
  US$ 13 mil brutos com R$ 20 mil de capital. Agora são no máximo 2 pares.
- **Resultado.** −23 pp. Mesmo sem custo algum dá −13,8 pp: o desvio medido no fechamento é fuso, e o HK já abre ajustado. O selo de
  HK (0,1–0,13% por lado), a corretagem mínima de HK$ 18 em lotes de US$ 600–1.700 e o Reg T ainda pioram o resultado.

### 5. em_india_adr — ADRs indianos x NSE
- **Tese.** A conversão é de mão única (headroom de capital estrangeiro), o que gera um prêmio estrutural. O prêmio medido confere com
  o que se conhece: HDB +5–20%, WIT +40–65% até 2018 e depois ~0, INFY/IBN ~0 desde 2016. O PF só opera o ADR, comprando quando o prêmio
  está anormalmente baixo e vendendo INDA no mesmo valor. São no máximo 2 ADRs.
- **Resultado.** −9,8 pp. Nos papéis dá −0,4 pp, ou seja, sem edge. O CDI perdido (−6,7 pp) vem do Reg T e do mínimo de US$ 2.000
  parados (R$ 11 mil = 55% de um capital de R$ 20 mil). Uma versão anterior, que permitia 5 ADRs (bruto de 200%), tinha excesso bruto
  com placebo p = 0,03, mas não sobreviveu ao limite de 2 ADRs, que é um dimensionamento de risco e não um ajuste ao resultado.

### 6. em_latam_commod — "petróleo em pânico" andino (EC x Brent, SCCO/ECH/EPU x cobre, BVN x ouro)
- **Tese.** É o análogo do mh_petroleo: no pânico, o ativo cai mais do que a commodity justifica. Compro o ativo e vendo o ETF da
  commodity no beta (BNO, CPER, GLD), porque o micro futuro é grande demais para posições de US$ 1–2 mil.
- **Resultado.** −2,8 pp (20k) e −1,7 pp (50k). Todas as variantes são negativas no IS. Sem custo dá ~0 (−0,1). O BVN sozinho custou
  −33 pp no período: ouro e prata não salvam a Buenaventura de problemas próprios (2020, 2022). A variante "pânico de mercado" foi
  melhor no OOS (+0,9 com z = 2 e queda de 20%), mas é pior no IS, então não é escolhível. **No Brasil o caso funciona porque a
  PETR4 é muito líquida e o vendedor forçado é o estrangeiro do Ibovespa. Aqui os ativos são pequenos e o resíduo é notícia própria.**

### 7. em_fx_exportadoras — pânico cambial EM: exportadores (ADR) contra o país
- **Tese.** Rand, peso mexicano, rupia, peso chileno e peso colombiano caem mais de 2 desvios em 21 dias. Compro quem tem custo local e
  receita em dólar (mineradoras SA, Sasol, aeroportos MX, INFY/WIT, SQM, EC) e vendo o ETF do país. A Turquia ficou fora por não ter
  ADR exportador líquido (TKC é doméstica).
- **Resultado.** −15,6 pp. Ainda negativo sem custo (−10,7). No OOS, perdeu com EC mai/2022 (−33%, Petro eleito: o choque cambial era
  político e atingiu o exportador estatal) e EWW vendido em out–dez/2023 (México +29%). O SQM pegou o ciclo do lítio em 2022.
  Exportador contra o país é, na prática, uma aposta de setor, e a moeda não é o que move o preço no prazo de semanas.

### 8. em_fronteira — o que ainda tem dado e liquidez, e o ETF descolado da bolsa local
- **Inventário.** NGE, EGPT, PAK, FM, FRN, GXG/ICOL, RSX/ERUS, EMFM e AFTY **não existem mais** no Yahoo, porque foram fechados ou
  congelados. Vivos com volume em 252 dias: KSA US$ 25 mi/dia, ARGT 22, FRDM 22, VNM 14, EIDO 14, TUR 9, UAE 8, EPU 7, AFK 1,9,
  ECNS 0,6, QAT 0,5, VNAM 0,35, KWT 0,24. Para R$ 5–10 mil por ordem, todos são líquidos o bastante. O problema é o dado: sem NAV
  histórico gratuito, e sem índice local no Yahoo para Arábia, Catar, Emirados, Kuwait, Filipinas e Tailândia (PSEI, SET e WIG20 vêm
  com 1 linha).
- **Regra.** O ETF dos EUA cai muito mais que a bolsa local em dólar (proxy do desconto ao NAV num resgate forçado). Compro e saio quando
  o desvio fecha. Pares: VNM x VN30 (E1VFVN30.VN), TUR x BIST100, EIDO x JCI, EWM x KLCI, EZA x Top40 (desde 2017). Erros de dados do
  Yahoo foram limpos só com o passado: IDR e VND com dias ×10/÷10, VN30 com picos de 25% num dia.
- **Resultado.** −9,6 pp, IR −2,1, e todas as variantes negativas no IS e no OOS. O "desconto" é fuso: a bolsa local cai no dia
  seguinte até o ETF, e o ETF não volta.

## O que deu certo e por quê

- Os **papéis** do pânico de país (+6,9 pp a.a. OOS antes dos custos de conta) e da Argentina no pânico (+10,9) existem, e têm o vendedor
  forçado clássico. Os negócios que pagaram foram TUR set/2022, ARGT out/2023 e set/2025, e EZA/ARGT/VNM no tarifaço de abr/2025:
  pânicos curtos de fluxo, sem mudança de regime.
- A medição está limpa. Truncamento ok em todos, Sharpe nenhum acima de 1,5, PBO baixo nos fundos de pânico (12–21%). A grade não é
  overfitting, simplesmente não há edge líquido.

## O que deu errado e por quê

1. **Os custos de ser PF lá fora são do tamanho do edge.** O IOF de remessa por negócio, o CDI perdido no saldo, o mínimo de US$ 2.000
   para vender e o câmbio aberto somam 5–15 pp a.a. O institucional não paga nada disso.
2. **A cauda é de sobrevivência.** Em 2022 a Rússia virou zero, e Egito, Nigéria e Paquistão sumiram. A regra "compra o país que caiu"
   compra justamente esses.
3. **Fuso não é desvio.** Nos ADRs China x HK e nos ETFs de fronteira x bolsa local, o "prêmio" medido em fechamentos não
   simultâneos é informação que a outra praça incorpora na abertura seguinte.
4. **Exportador contra país e ADR contra commodity** são apostas de empresa e de setor disfarçadas, com notícia própria (Petro/EC,
   BVN), sem vendedor forçado identificável.

## Bugs e premissas registrados nos módulos

- Yahoo FX: o "Close" de t é a cotação do início de t (MXN, ARS, CLP, TRY conferidos). Os sinais usam a de t, defasada, e o filtro
  eleitoral usa a linha seguinte.
- O YPFD.BA do Yahoo vem em escala 1/10, e IDR/VND têm dias ×10/÷10. PSEI.PS, ^SET.BK, WIG20.WA, ^TASI.SR e ^IPSA vêm sem histórico.
- O filtro de salto de razão (`pre_corrigido`) confundia fuso com troca de razão e foi desligado. As razões foram conferidas ano a ano.
- WDO: a 1ª versão arredondava `round(saldo/US$ 10 mil)`, e US$ 5 mil viravam 1 contrato. Isso é metade aposta vendida em dólar (o
  carry do real, já reprovado). Com esse erro, a Argentina com 50k ia de +1,5 para +12,7 pp. Corrigido para
  `piso(saldo/10 mil + 0,2)`, sem sobre-hedge acima de 25%.
- Limites de risco que faltavam: China sem limite de pares, Índia com 5 ADRs (bruto de 200%). Ambos corrigidos por dimensionamento,
  não pelo resultado.
- O IR do fundo é tratado inteiro como "exterior". A perna de WDO (50k) seria futuros B3, também 15%. A diferença é mensal contra
  anual, e o efeito é pequeno.
- Os lotes de HK (9988 = 100, 9618/9888 = 50 etc.) não foram confirmados um a um, e o aluguel de HK (1,5% a.a.) é premissa.

## Próximos passos

- **Pânico de país sem o custo da remessa.** Os papéis dão +6,9 pp. Se o grupo já tiver uma "manga" permanente em dólar na IBKR
  para outras estratégias (spin-offs, MCL), protegida com WDO a partir de R$ 50 mil, a remessa por negócio some. Vale rodar a variante
  com o saldo compartilhado, cobrando só o câmbio protegido e o CDI do período do negócio. Também vale excluir países com sanção ou
  controle de capital iminente (regra ex-ante: país com moeda em regime de câmbio múltiplo ou ETF com fluxo de resgate > X% do
  patrimônio).
- **Argentina:** só faz sentido como alocação tática (beta) e não entra como alfa.
- Comprar o NAV histórico (iNAV/IOPV) dos ETFs de fronteira para testar o desconto de verdade em vez do proxy de bolsa local.

---

# Tabelas geradas (`python pf/pesquisa/_em_relatorio.py`)

Métricas (pp a.a. OOS; "papéis/remessa/câmbio/CDI perdido/WDO" = decomposição do excesso, soma simples):

|                                  | em_argentina   | em_panico_pais   | em_eleicoes   | em_china_adr_hk   | em_india_adr   | em_latam_commod   | em_fx_exportadoras   | em_fronteira   |
|:---------------------------------|:---------------|:-----------------|:--------------|:------------------|:---------------|:------------------|:---------------------|:---------------|
| OOS desde                        | 2021-01        | 2021-01          | 2021-01       | 2023-01           | 2021-01        | 2021-01           | 2021-01              | 2021-01        |
| ativo 20k pp                     | 1.46           | -10.83           | -2.5          | -23.46            | -9.75          | -2.82             | -15.61               | -9.62          |
| ativo 50k pp                     | 1.52           | -7.35            | -3.55         | -20.56            | -9.03          | -1.72             | -11.59               | -9.58          |
| depois IR 20k pp                 | 1.43           | -10.66           | -2.46         | -23.06            | -9.6           | -2.78             | -15.37               | -9.48          |
| depois IR 50k pp                 | 1.49           | -7.24            | -3.5          | -20.21            | -8.89          | -1.7              | -11.42               | -9.43          |
| IR OOS                           | 0.16           | -0.58            | -0.53         | -1.27             | -0.9           | -0.39             | -1.17                | -2.13          |
| PBO %                            | 21.03          | 11.9             | 71.43         | 48.81             | 44.05          | 54.76             | 42.06                | 30.95          |
| P(bater 3a) %                    | 53.18          | 12.94            | 12.82         | 0.9               | 3.66           | 20.02             | 0.18                 | 0.0            |
| sem 10 melhores                  | -5.18          | -20.84           | -2.4          | -40.57            | -15.0          | -6.75             | -23.64               | -10.96         |
| custo 2x                         | -1.22          | -15.29           | -4.08         | -32.2             | -11.47         | -5.5              | -20.3                | -14.18         |
| custo 0x                         | 4.2            | -6.18            | -0.91         | -13.79            | -7.99          | -0.1              | -10.71               | -4.87          |
| t+2                              | 2.71           | -12.01           | -2.75         | -15.59            | -9.17          | -2.25             | -15.97               | -8.76          |
| leque p5                         | -0.02          | -16.81           | -3.09         | -24.12            | -10.75         | -5.63             | -20.93               | -16.93         |
| leque mediana                    | 5.08           | -11.96           | -1.52         | -20.53            | -8.13          | -1.63             | -14.82               | -11.45         |
| placebo p                        | 0.38           | 0.12             | 0.41          | 0.87              | 0.36           | 0.37              | 0.89                 | 0.64           |
| excesso bruto OOS (placebo real) | 6.24           | 2.67             | 0.19          | -1.02             | -0.08          | 0.87              | -2.94                | -0.92          |
| truncamento ok                   | True           | True             | True          | True              | True           | True              | True                 | True           |
| beta EEM                         | 0.12           | 0.29             | 0.03          | 0.11              | 0.13           | 0.07              | 0.1                  | 0.05           |
| alfa EEM pp                      | 2.86           | -8.05            | -2.09         | -22.33            | -8.28          | -2.16             | -14.03               | -8.8           |
| negócios OOS                     | 30             | 36               | 7             | 238               | 57             | 30                | 83                   | 29             |
| 20k papéis                       | 10.9           | 6.92             | -0.1          | -8.32             | -0.44          | 0.75              | -1.36                | -0.58          |
| 20k remessa                      | -2.19          | -4.08            | -1.37         | -1.73             | -1.19          | -2.12             | -4.06                | -4.25          |
| 20k câmbio do saldo              | -3.13          | -3.04            | 0.47          | -0.36             | -0.21          | 1.21              | -3.97                | -2.05          |
| 20k CDI perdido                  | -2.97          | -4.7             | -1.03         | -11.21            | -6.69          | -2.06             | -4.81                | -1.92          |
| 20k WDO                          | 0.0            | 0.0              | 0.0           | 0.0               | 0.0            | 0.0               | 0.0                  | 0.0            |
| 20k Rússia sint.                 | 0.0            | -3.91            | 0.0           | 0.0               | 0.0            | 0.0               | 0.0                  | 0.0            |
| 20k saldo IBKR médio R$          | 4971.97        | 8063.67          | 2059.62       | 18178.86          | 12302.89       | 4107.0            | 8478.65              | 3322.02        |
| 50k papéis                       | 10.95          | 7.0              | -0.09         | -6.59             | -0.32          | 0.83              | -1.22                | -0.53          |
| 50k remessa                      | -2.19          | -4.08            | -1.37         | -1.63             | -1.25          | -1.61             | -3.97                | -4.25          |
| 50k câmbio do saldo              | -3.13          | -3.04            | 0.47          | -0.41             | -0.35          | 0.78              | -3.51                | -2.05          |
| 50k CDI perdido                  | -2.97          | -4.7             | -1.03         | -10.78            | -5.98          | -1.28             | -4.63                | -1.92          |
| 50k WDO                          | 0.0            | 3.29             | -1.01         | 0.88              | 0.0            | 0.0               | 3.15                 | 0.0            |
| 50k Rússia sint.                 | 0.0            | -3.91            | 0.0           | 0.0               | 0.0            | 0.0               | 0.0                  | 0.0            |
| 50k saldo IBKR médio R$          | 12429.93       | 20159.17         | 5149.06       | 43688.91          | 27245.99       | 6337.05           | 20231.73             | 8305.04        |

### em_argentina — 10 melhores

| ativo   |   lado | entrada    | saida      |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:-----------|:-----------|-------:|------------:|-------------:|
| PAM     |      1 | 2014-12-16 | 2015-03-13 |     63 |       76.83 |        10.19 |
| PAM     |      1 | 2014-01-24 | 2014-04-23 |     63 |       70.6  |         8.38 |
| GGAL    |      1 | 2009-03-03 | 2009-05-29 |     63 |       56.97 |         8.37 |
| GGAL    |      1 | 2014-12-16 | 2015-03-13 |     63 |       63.07 |         8.33 |
| GGAL    |      1 | 2014-01-24 | 2014-04-23 |     63 |       69.33 |         8.12 |
| CEPU    |      1 | 2023-09-27 | 2023-12-26 |     64 |       75.64 |         7.58 |
| BMA     |      1 | 2014-01-24 | 2014-04-23 |     63 |       60.65 |         6.97 |
| GGAL    |      1 | 2015-10-02 | 2015-12-30 |     63 |       53.04 |         6.59 |
| BMA     |      1 | 2015-10-02 | 2015-12-30 |     63 |       53.22 |         6.56 |
| BMA     |      1 | 2014-12-16 | 2015-03-13 |     63 |       49.28 |         6.56 |

### em_argentina — 10 piores

| ativo   |   lado | entrada    | saida      |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:-----------|:-----------|-------:|------------:|-------------:|
| GGAL    |      1 | 2008-10-13 | 2009-01-08 |     63 |      -39.04 |        -6.84 |
| PAM     |      1 | 2012-04-17 | 2012-07-13 |     63 |      -45.73 |        -6.1  |
| GGAL    |      1 | 2011-08-09 | 2011-11-04 |     63 |      -33.82 |        -4.83 |
| BMA     |      1 | 2011-08-09 | 2011-11-04 |     63 |      -33.85 |        -4.76 |
| BMA     |      1 | 2019-08-13 | 2019-11-08 |     63 |      -36.7  |        -3.91 |
| GGAL    |      1 | 2019-08-13 | 2019-11-08 |     63 |      -27.97 |        -2.99 |
| GGAL    |      1 | 2018-05-09 | 2018-08-06 |     63 |      -25.82 |        -2.87 |
| BMA     |      1 | 2008-10-13 | 2009-01-08 |     63 |      -16.39 |        -2.51 |
| PAM     |      1 | 2018-05-09 | 2018-08-06 |     63 |      -21.75 |        -2.51 |
| BMA     |      1 | 2012-04-17 | 2012-07-13 |     63 |      -19.48 |        -2.46 |

### em_panico_pais — 10 melhores

| ativo   |   lado | entrada    | saida      |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:-----------|:-----------|-------:|------------:|-------------:|
| TUR     |      1 | 2022-09-30 | 2022-11-30 |     42 |       55.34 |        10.52 |
| EWZ     |      1 | 2007-08-14 | 2007-10-12 |     42 |       40.83 |         9.76 |
| EWZ     |      1 | 2020-05-14 | 2020-07-15 |     42 |       38.75 |         9.08 |
| EWZ     |      1 | 2008-03-20 | 2008-05-20 |     42 |       34.35 |         8.49 |
| EZA     |      1 | 2025-04-07 | 2025-06-06 |     42 |       32.3  |         7.98 |
| EIDO    |      1 | 2020-09-24 | 2020-11-23 |     42 |       29.4  |         7.24 |
| TUR     |      1 | 2009-02-19 | 2009-04-21 |     42 |       29.33 |         6.96 |
| ARGT    |      1 | 2023-10-03 | 2023-12-01 |     42 |       28.66 |         6.64 |
| EZA     |      1 | 2007-08-15 | 2007-10-15 |     42 |       26.92 |         6.46 |
| ARGT    |      1 | 2018-12-26 | 2019-02-27 |     42 |       25.84 |         6.45 |

### em_panico_pais — 10 piores

| ativo            |   lado | entrada    | saida      |   dias |   retorno_% |   contrib_pp |
|:-----------------|-------:|:-----------|:-----------|-------:|------------:|-------------:|
| RSX* (sintético) |      1 | 2022-02-25 | 2022-03-04 |      5 |      -90    |       -22.5  |
| EWZ              |      1 | 2008-09-24 | 2008-11-21 |     42 |      -50.05 |       -14.45 |
| EWW              |      1 | 2008-09-18 | 2008-11-17 |     42 |      -38.86 |        -9.74 |
| EZA              |      1 | 2008-09-18 | 2008-11-17 |     42 |      -36.83 |        -9.12 |
| TUR              |      1 | 2008-09-17 | 2008-11-14 |     42 |      -39.45 |        -8.1  |
| EWZ              |      1 | 2008-07-10 | 2008-09-09 |     42 |      -28.92 |        -7.77 |
| ECH              |      1 | 2008-09-30 | 2008-11-28 |     42 |      -25.77 |        -7.18 |
| EWZ              |      1 | 2020-02-28 | 2020-04-29 |     42 |      -32.4  |        -6.7  |
| EWZ              |      1 | 2015-07-28 | 2015-09-25 |     42 |      -24.15 |        -5.89 |
| TUR              |      1 | 2018-08-07 | 2018-10-05 |     42 |      -15.51 |        -4.11 |

### em_eleicoes — 10 melhores

| ativo   |   lado | entrada    | saida      |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:-----------|:-----------|-------:|------------:|-------------:|
| ECH     |      1 | 2021-12-21 | 2022-01-19 |     21 |       17.02 |         4.74 |
| INDA    |      1 | 2024-06-05 | 2024-07-05 |     22 |        6.66 |         3.5  |
| GREK    |      1 | 2015-01-27 | 2015-02-25 |     21 |       13.35 |         2.98 |
| EWZ     |      1 | 2014-10-28 | 2014-11-26 |     21 |        4.75 |         1.49 |
| GREK    |      1 | 2015-09-22 | 2015-10-21 |     21 |        9.73 |         1.42 |
| TUR     |      1 | 2015-06-09 | 2015-07-08 |     21 |        4.23 |         1.18 |
| EWM     |      1 | 2018-05-10 | 2018-06-08 |     21 |        1.76 |         0.73 |
| TUR     |      1 | 2014-08-12 | 2014-09-10 |     21 |        0.83 |         0.24 |
| TUR     |      1 | 2023-05-16 | 2023-06-14 |     21 |       -1.56 |        -0.35 |
| EWW     |      1 | 2024-06-04 | 2024-07-03 |     21 |       -2.1  |        -0.91 |

### em_eleicoes — 10 piores

| ativo   |   lado | entrada    | saida      |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:-----------|:-----------|-------:|------------:|-------------:|
| GREK    |      1 | 2012-05-08 | 2012-06-06 |     21 |      -27.01 |        -5.03 |
| ECH     |      1 | 2022-09-07 | 2022-10-06 |     21 |      -11.97 |        -3.3  |
| EPU     |      1 | 2021-06-08 | 2021-07-07 |     21 |       -8.96 |        -3.29 |
| GREK    |      1 | 2015-07-07 | 2015-08-05 |     21 |       -8.54 |        -1.34 |
| ARGT    |      1 | 2025-09-09 | 2025-10-08 |     21 |       -3.36 |        -0.99 |
| EPU     |      1 | 2011-06-07 | 2011-07-06 |     21 |       -2.75 |        -0.95 |
| EWW     |      1 | 2024-06-04 | 2024-07-03 |     21 |       -2.1  |        -0.91 |
| TUR     |      1 | 2023-05-16 | 2023-06-14 |     21 |       -1.56 |        -0.35 |
| TUR     |      1 | 2014-08-12 | 2014-09-10 |     21 |        0.83 |         0.24 |
| EWM     |      1 | 2018-05-10 | 2018-06-08 |     21 |        1.76 |         0.73 |

### em_china_adr_hk — 10 melhores

| ativo   |   lado | entrada    | saida      |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:-----------|:-----------|-------:|------------:|-------------:|
| 9626.HK |      1 | 2024-09-25 | 2024-10-02 |      5 |       73.28 |        20.71 |
| JD      |      1 | 2022-03-11 | 2022-03-18 |      5 |       35.72 |        12.47 |
| 9618.HK |      1 | 2024-09-25 | 2024-10-02 |      5 |       47.34 |        10.11 |
| XPEV    |      1 | 2023-07-26 | 2023-07-28 |      2 |       20.2  |         9.98 |
| 9868.HK |      1 | 2022-12-01 | 2022-12-06 |      3 |       23.23 |         8.56 |
| 9961.HK |      1 | 2022-11-29 | 2022-12-06 |      5 |       15.41 |         5.58 |
| 9868.HK |     -1 | 2024-10-02 | 2024-10-09 |      5 |       14.85 |         5.52 |
| BILI    |      1 | 2022-12-06 | 2022-12-08 |      2 |       13.81 |         4.91 |
| XPEV    |     -1 | 2022-10-26 | 2022-10-28 |      2 |       15.87 |         4.71 |
| 2423.HK |     -1 | 2022-12-06 | 2022-12-16 |      8 |       16.3  |         4.7  |

### em_china_adr_hk — 10 piores

| ativo   |   lado | entrada    | saida      |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:-----------|:-----------|-------:|------------:|-------------:|
| 9868.HK |     -1 | 2023-07-26 | 2023-07-28 |      2 |      -40.81 |       -15.23 |
| BILI    |     -1 | 2024-09-25 | 2024-10-01 |      4 |      -46.31 |       -12.5  |
| 9626.HK |     -1 | 2022-12-06 | 2022-12-08 |      2 |      -17.78 |        -6.01 |
| JD      |     -1 | 2024-09-25 | 2024-10-01 |      4 |      -29.27 |        -5.99 |
| 9868.HK |      1 | 2022-10-26 | 2022-10-28 |      2 |      -17.59 |        -5.9  |
| 9618.HK |     -1 | 2022-03-11 | 2022-03-18 |      5 |      -15.5  |        -5.62 |
| XPEV    |     -1 | 2022-12-01 | 2022-12-06 |      3 |      -17.25 |        -5.42 |
| BEKE    |      1 | 2022-12-06 | 2022-12-16 |      8 |      -15.09 |        -5.25 |
| TCOM    |     -1 | 2022-11-29 | 2022-12-06 |      5 |      -13.39 |        -4.77 |
| 9866.HK |      1 | 2022-10-26 | 2022-10-28 |      2 |      -12.02 |        -3.64 |

### em_india_adr — 10 melhores

| ativo   |   lado | entrada    | saida      |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:-----------|:-----------|-------:|------------:|-------------:|
| INDA    |     -1 | 2020-02-19 | 2020-03-27 |     27 |       32.73 |        12.95 |
| IBN     |      1 | 2006-09-26 | 2006-12-22 |     63 |       31.64 |         8.09 |
| HDB     |      1 | 2014-01-27 | 2014-03-28 |     44 |       28.84 |         6.76 |
| INFY    |      1 | 2008-04-10 | 2008-05-16 |     26 |       26.92 |         6.66 |
| INFY    |      1 | 2009-05-19 | 2009-07-24 |     48 |       29.36 |         6.39 |
| INDA    |     -1 | 2012-02-22 | 2012-05-22 |     64 |       22.38 |         5.92 |
| HDB     |      1 | 2007-04-12 | 2007-06-22 |     51 |       23.42 |         5.79 |
| RDY     |      1 | 2020-04-03 | 2020-04-20 |     11 |       21.9  |         5.44 |
| INDA    |     -1 | 2018-01-23 | 2018-06-13 |    101 |       10.88 |         5.16 |
| INDA    |     -1 | 2022-04-13 | 2022-07-11 |     63 |       10.95 |         4.91 |

### em_india_adr — 10 piores

| ativo   |   lado | entrada    | saida      |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:-----------|:-----------|-------:|------------:|-------------:|
| IBN     |      1 | 2008-11-11 | 2008-12-01 |     14 |      -26.97 |        -6.5  |
| WIT     |      1 | 2012-02-22 | 2012-05-21 |     63 |      -23.06 |        -6.47 |
| IBN     |      1 | 2015-10-16 | 2016-01-13 |     63 |      -24.32 |        -6.3  |
| INDA    |     -1 | 2016-10-26 | 2017-05-22 |    148 |      -10.35 |        -6.24 |
| INDA    |     -1 | 2024-01-18 | 2024-08-12 |    147 |      -13.43 |        -5.28 |
| INDA    |     -1 | 2020-04-03 | 2020-04-20 |     11 |      -15.72 |        -4.61 |
| WIT     |      1 | 2007-11-13 | 2008-02-08 |     63 |      -16.03 |        -4.29 |
| RDY     |      1 | 2015-11-12 | 2016-02-09 |     63 |      -15.92 |        -4.09 |
| INDA    |     -1 | 2014-01-27 | 2014-03-28 |     44 |      -13.18 |        -3.97 |
| WIT     |      1 | 2022-01-13 | 2022-04-12 |     63 |      -15.61 |        -3.7  |

### em_latam_commod — 10 melhores

| ativo   |   lado | entrada    | saida      |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:-----------|:-----------|-------:|------------:|-------------:|
| EC      |      1 | 2020-05-29 | 2020-06-05 |      5 |       26.32 |         6.09 |
| BVN     |      1 | 2007-08-17 | 2007-09-06 |     13 |       20.34 |         5.35 |
| SCCO    |      1 | 2016-01-20 | 2016-02-04 |     11 |       18.84 |         4.72 |
| CPER    |     -1 | 2020-02-28 | 2020-03-26 |     19 |       13.85 |         4.41 |
| BVN     |      1 | 2006-03-28 | 2006-04-20 |     16 |       15.18 |         3.65 |
| SCCO    |      1 | 2026-03-25 | 2026-04-09 |     10 |       13.63 |         3.39 |
| EC      |      1 | 2019-08-26 | 2019-09-12 |     12 |       12.72 |         3.16 |
| GLD     |     -1 | 2008-08-05 | 2008-09-02 |     19 |        7.99 |         2.84 |
| ECH     |      1 | 2021-12-23 | 2022-01-13 |     14 |       11.43 |         2.82 |
| SCCO    |      1 | 2019-08-15 | 2019-09-06 |     15 |       11.03 |         2.72 |

### em_latam_commod — 10 piores

| ativo   |   lado | entrada    | saida      |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:-----------|:-----------|-------:|------------:|-------------:|
| BVN     |      1 | 2020-01-29 | 2020-03-30 |     42 |      -46.54 |       -13.5  |
| EC      |      1 | 2014-10-28 | 2014-12-29 |     42 |      -37.61 |        -9.5  |
| BVN     |      1 | 2022-06-29 | 2022-08-29 |     42 |      -20.83 |        -5.29 |
| SCCO    |      1 | 2018-10-22 | 2018-12-21 |     42 |      -20.26 |        -5.23 |
| BVN     |      1 | 2008-10-20 | 2008-11-11 |     16 |      -13.51 |        -4.74 |
| BVN     |      1 | 2015-11-11 | 2016-01-13 |     42 |      -18.39 |        -4.72 |
| BVN     |      1 | 2021-07-06 | 2021-09-02 |     42 |      -17.6  |        -4.56 |
| SCCO    |      1 | 2020-02-28 | 2020-03-26 |     19 |      -14.6  |        -4.14 |
| BVN     |      1 | 2013-05-01 | 2013-06-18 |     33 |      -13.25 |        -3.53 |
| EC      |      1 | 2013-04-16 | 2013-06-14 |     42 |      -11.21 |        -3.08 |

### em_fx_exportadoras — 10 melhores

| ativo   |   lado | entrada    | saida      |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:-----------|:-----------|-------:|------------:|-------------:|
| EWW     |     -1 | 2008-09-02 | 2008-10-30 |     42 |       39.56 |        19.98 |
| SQM     |      1 | 2008-05-13 | 2008-07-10 |     42 |       49.56 |        18.91 |
| WIT     |      1 | 2009-03-10 | 2009-05-07 |     42 |       71.07 |        14.44 |
| HMY     |      1 | 2015-11-17 | 2016-01-14 |     42 |      175.93 |        12.7  |
| EWW     |     -1 | 2020-03-03 | 2020-04-30 |     42 |       31.98 |        12.01 |
| SQM     |      1 | 2008-10-09 | 2008-12-08 |     42 |       50.51 |        11.35 |
| SQM     |      1 | 2022-07-18 | 2022-09-14 |     42 |       32.23 |        10.61 |
| EZA     |     -1 | 2015-11-17 | 2016-01-14 |     42 |       22.78 |         9.04 |
| SQM     |      1 | 2015-08-28 | 2015-10-27 |     42 |       23.56 |         6.94 |
| SQM     |      1 | 2014-01-28 | 2014-03-27 |     42 |       17.51 |         6.68 |

### em_fx_exportadoras — 10 piores

| ativo   |   lado | entrada    | saida      |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:-----------|:-----------|-------:|------------:|-------------:|
| EC      |      1 | 2022-05-05 | 2022-07-05 |     43 |      -32.72 |       -13.45 |
| EWW     |     -1 | 2023-10-20 | 2023-12-19 |     42 |      -29.19 |       -11.12 |
| SQM     |      1 | 2015-06-16 | 2015-08-13 |     42 |      -26.58 |       -10.7  |
| WIT     |      1 | 2008-09-03 | 2008-10-31 |     42 |      -33.56 |        -8.96 |
| INDA    |     -1 | 2013-08-21 | 2013-10-18 |     42 |      -23.44 |        -7.55 |
| OMAB    |      1 | 2008-09-02 | 2008-10-30 |     42 |      -45.06 |        -7.55 |
| EZA     |     -1 | 2007-08-22 | 2007-10-19 |     42 |      -17.27 |        -7.36 |
| INFY    |      1 | 2008-09-03 | 2008-10-31 |     42 |      -27.29 |        -7.24 |
| EWW     |     -1 | 2012-05-31 | 2012-07-30 |     42 |      -16.96 |        -6.74 |
| EWW     |     -1 | 2006-06-09 | 2006-08-08 |     42 |      -19    |        -6.62 |

### em_fronteira — 10 melhores

| ativo   |   lado | entrada    | saida      |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:-----------|:-----------|-------:|------------:|-------------:|
| TUR     |      1 | 2018-08-13 | 2018-08-15 |      2 |       15.78 |         4.17 |
| EIDO    |      1 | 2015-08-24 | 2015-08-28 |      4 |       14.32 |         4.11 |
| EIDO    |      1 | 2011-09-22 | 2011-09-28 |      4 |       12.99 |         3.37 |
| EIDO    |      1 | 2013-08-28 | 2013-09-09 |      8 |       10.54 |         3.03 |
| TUR     |      1 | 2008-10-10 | 2008-10-13 |      1 |        8.84 |         2.58 |
| TUR     |      1 | 2010-05-07 | 2010-05-11 |      2 |        9.04 |         2.53 |
| EIDO    |      1 | 2016-06-27 | 2016-06-29 |      2 |        8.57 |         2.47 |
| TUR     |      1 | 2016-06-27 | 2016-07-11 |     10 |        6.69 |         1.92 |
| EIDO    |      1 | 2011-10-04 | 2011-10-07 |      3 |        6.62 |         1.9  |
| EWM     |      1 | 2021-12-14 | 2021-12-28 |     10 |        5.39 |         1.56 |

### em_fronteira — 10 piores

| ativo   |   lado | entrada    | saida      |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:-----------|:-----------|-------:|------------:|-------------:|
| TUR     |      1 | 2008-09-30 | 2008-10-07 |      5 |      -24.48 |        -8.35 |
| TUR     |      1 | 2008-11-07 | 2008-11-12 |      3 |      -14.57 |        -4.79 |
| VNM     |      1 | 2020-02-26 | 2020-03-11 |     10 |      -11.98 |        -3.94 |
| TUR     |      1 | 2011-08-03 | 2011-08-04 |      1 |       -8.15 |        -2.55 |
| EWM     |      1 | 2020-03-17 | 2020-03-18 |      1 |       -7.29 |        -2.54 |
| EIDO    |      1 | 2013-06-03 | 2013-06-14 |      9 |       -7.4  |        -2.3  |
| TUR     |      1 | 2023-06-08 | 2023-06-22 |     10 |       -7.05 |        -2.13 |
| TUR     |      1 | 2008-10-16 | 2008-10-17 |      1 |       -6.06 |        -1.87 |
| VNM     |      1 | 2020-01-22 | 2020-02-04 |      9 |       -5.86 |        -1.85 |
| EIDO    |      1 | 2020-02-25 | 2020-02-27 |      2 |       -5.64 |        -1.76 |

### liquidez

| ETF   | desde                         |   volume médio 252d US$ mi |   pregões sem negócio 252d |
|:------|:------------------------------|---------------------------:|---------------------------:|
| VNM   | 2009-08-14                    |                      13.92 |                          0 |
| VNAM  | 2021-12-10                    |                       0.35 |                          0 |
| AFK   | 2008-07-14                    |                       1.89 |                          0 |
| KSA   | 2015-09-17                    |                      24.9  |                          0 |
| QAT   | 2014-05-01                    |                       0.52 |                          0 |
| UAE   | 2014-05-01                    |                       7.76 |                          0 |
| KWT   | 2020-09-03                    |                       0.24 |                          0 |
| EPU   | 2009-06-22                    |                       6.8  |                          0 |
| ARGT  | 2011-03-03                    |                      21.94 |                          0 |
| ECNS  | 2010-09-29                    |                       0.61 |                          0 |
| EPHE  | 2010-09-29                    |                       3.68 |                          0 |
| THD   | 2008-04-01                    |                       6.8  |                          0 |
| GREK  | 2011-12-08                    |                       6.76 |                          0 |
| TUR   | 2008-03-28                    |                       9.47 |                          0 |
| EIDO  | 2010-05-07                    |                      13.66 |                          0 |
| EZA   | 2005-01-03                    |                      17.6  |                          0 |
| FRDM  | 2019-06-14                    |                      21.84 |                          0 |
| RSX   | sem dado (deslistado/fechado) |                     nan    |                        nan |
| ERUS  | sem dado (deslistado/fechado) |                     nan    |                        nan |
| EGPT  | sem dado (deslistado/fechado) |                     nan    |                        nan |
| NGE   | sem dado (deslistado/fechado) |                     nan    |                        nan |
| PAK   | sem dado (deslistado/fechado) |                     nan    |                        nan |
| FM    | sem dado (deslistado/fechado) |                     nan    |                        nan |
| FRN   | sem dado (deslistado/fechado) |                     nan    |                        nan |
| GXG   | sem dado (deslistado/fechado) |                     nan    |                        nan |
| ICOL  | sem dado (deslistado/fechado) |                     nan    |                        nan |
| EMFM  | sem dado (deslistado/fechado) |                     nan    |                        nan |
| AFTY  | sem dado (deslistado/fechado) |                     nan    |                        nan |
