# PF2 — frente cripto (`pf/fundos/cr_*.py`)

Rodada "testa tudo" para cripto de pessoa física brasileira com R$ 20–50 mil. Oito estratégias novas, todas pela bateria
(`python pf/rodar_pf.py um cr_<x>`, truncamento passou em todas). Diagnósticos e alfa vs BTC: `python pf/fundos/cr_rodar.py`
(saída em `pf/resultados/pf2_cripto/cr_rodar.txt`; resultados em `pf/resultados/pf2_cripto.pkl` e `pf2_cripto_diag.pkl`).
Sempre separo **beta de cripto** (subir porque o BTC/ETH subiu) de **alfa** (benchmark CDI; e regressão do excesso diário contra o BTC em R$:
"alfa vs BTC" e "beta").

## 1. Onde o PF pode operar cripto (verificado em out/2026)

| rota | o que dá | IR | situação 2025–26 |
|---|---|---|---|
| Corretora brasileira (Mercado Bitcoin, Foxbit, Binance BR, Bitso) | à vista em R$/USDT, staking de ETH | 15% sobre o ganho, **isento se as vendas de cripto do mês ≤ R$ 35 mil** | a MP 1.303/2025 (17,5% sem isenção) **caducou em 08/10/2025**: regra antiga vale em 2026. Marco do BCB (Res. 519/520/521, vigência 02/02/2026): SPSAV pede autorização até 30/10/2026; stablecoin em moeda estrangeira, transferência internacional e autocustódia viram **câmbio**. IOF de 3,5% na compra de cripto (isento até R$ 10 mil/mês) só em consulta pública. |
| Derivativos (perpétuos) na Binance/Bybit/OKX | perpétuo, margem | exterior (Lei 14.754/2023, 15% anual) | **Não para residente pela entidade brasileira**: CVM proibiu a Binance de ofertar futuros (AD 17.961/2020). Em 2026 a Binance migrou brasileiros para a entidade local, deixou derivativos só numa "conta internacional" (Abu Dhabi), fora de CVM/BCB, e cortou margem/empréstimos/launchpool a partir de 27/10/2026 (e deslistou 22 tokens). A Bybit encerrou derivativos para brasileiros (migração 24/09/2026). OKX ainda opera sem confirmar pedido de SPSAV. => perpétuo = offshore, risco de contraparte e regulatório. |
| B3 | BIT (R$, 0,01 BTC desde 16/06/2025), ETR (0,25 ETH, em US$), SOL (5 SOL, em US$) desde 16/06/2025; ETFs HASH11/QBTC11/BITH11/ETHE11/QETH11/SOLH11/QSOL11 | 15%, sem isenção; ETF e futuro se compensam | contratos cabem em R$ 20 mil só desde 06/2025 |
| IBKR | MBT/MET (0,1 BTC/ETH) | exterior | já testado (cme_cripto) |

Fontes: [Exame — MP 1.303 rejeitada](https://exame.com/future-of-money/mp-1-303-com-rejeicao-na-camara-tributacao-de-criptos-nao-vai-subir-em-2026-veja-regras-atuais/),
[MB — fim da MP 1303](https://www.mb.com.br/economia-digital/criptos/entenda-o-fim-da-mp-1303/),
[Machado Meyer — BCB regulamenta ativos virtuais](https://www.machadomeyer.com.br/pt/inteligencia-juridica/publicacoes-ij/bancario-seguros-e-financeiro-ij/bcb-regulamenta-o-mercado-de-ativos-virtuais-no-brasil),
[Blue Consult — Res. 520/521](https://blueconsult.com.br/resolucoes-bcb-520-521-o-que-muda/),
[ASA — proposta de IOF sobre cripto](https://www.asa.com.br/central-de-conteudos/investimentos/receita-federal-propoe-iof-sobre-compra-de-criptoativos-entenda-o-projeto),
[Raphael Souza — Binance proibida de oferecer derivativos](https://raphaelsouza.com.br/binance-proibida-derivativos-cvm/),
[BPMoney — Binance restringe 8 serviços e 22 tokens](https://bpmoney.com.br/mercado/cripto/binance-restringe-8-servicos-retira-22-criptomoedas-brasil-regras-bc/),
[Fábio Pesavento — Binance Brasil 2026](https://fabiopesavento.com.br/blog/2026/10/11/binance-brasil-2026-novas-regras/),
[Livecoins — Bybit migra brasileiros e restringe produtos](https://livecoins.com.br/bybit-vai-migrar-usuarios-brasileiros-para-entidade-local-e-restringir-produtos-com-novas-regras-no-brasil/),
[Symplexia — situação de cada exchange na autorização do BCB](https://news.symplexia.com/pt-br/2026/10/nova-economia/cryptomoedas/regulacao-cripto-veja-a-situacao-de-cada-exchange-no-processo-de-autorizacao-do-banco-central/),
[B3 — futuros de Ethereum e Solana](https://www.b3.com.br/pt_br/noticias/futuros-de-ethereum-e-solana.htm),
[InfoMoney — ETR/SOL cotados em dólar](https://www.infomoney.com.br/mercados/b3-lanca-futuros-de-eth-e-sol-com-cotacao-em-dolar-conheca-os-detalhes-dos-contratos/).

## 2. Dados (`pf/dados/pf2_cripto/`, `python pf/fundos/cr_comum.py baixa`)

- `binance_1h.parquet` (40 MB): candles de 1h de ~85 pares USDT da Binance **inclusive os que morreram ou mudaram de nome** (LUNA, FTT, SRM,
  BTT, HNT, WAVES, XMR, EOS, MATIC→POL, FTM→S, RNDR→RENDER, BCC/BCHABC, VEN), 2017-08 a 15/10/2026, do arquivo público data.binance.vision.
  Índice = hora de FECHAMENTO do candle. Buraco > 48h (deslistagem/relançamento: LUNA 05/2022) = saída no último preço.
- `funding.parquet` / `spot_perp_d.parquet`: financiamento 8h e fechamento diário à vista/perpétuo (mesma corretora, mesmo instante) de BTC,
  ETH, SOL, BNB, XRP, DOGE (2019-09+), da pesquisa anterior.
- `listagens.parquet`: os primeiros 125 dias de todo par USDT listado na Binance desde 2019 (654 pares, inclusive deslistados).
- `perps_listagens.parquet`: preço diário e **financiamento real** do perpétuo USDT-M dessas moedas (415 têm perpétuo; arquivo da Binance,
  inclusive 1000PEPE etc.).
- `lido_apy.csv`: APY do stETH (DefiLlama, 05/2022+).
- Reaproveitados: `global_cripto/cripto_br.parquet` (Mercado Bitcoin 1h desde 2019, Binance BTCBRL/ETHBRL/USDTBRL desde 10/2020),
  `b3_etf_bdr.parquet` (ETFs com melhores ofertas), `futuros_b3.parquet` (BIT/ETR/SOL, ajuste e quantidade).
- Calendário: o P&L cripto (24x7, UTC) entra no 1º pregão da B3 cujo fechamento é ≥ a hora do candle (fim de semana → segunda). Câmbio:
  USDTBRL da Binance hora a hora (PTAX antes de 10/2020). Motor comum `cr_comum.motor`: compra e segura (o valor flutua), rebalanceia só
  quando pedido, execução t+1 (próxima hora para sinais horários; próximo fechamento diário para sinais diários), dinheiro em cripto não
  rende CDI.

## 3. Resultado (OOS desde 2023-01, exceto ETF x futuro: 2026-01)

| fundo | aplicável? | 20k antes / depois do IR (pp a.a. vs CDI) | 50k antes / depois | IR | PBO | P(bater 3a) | sem 10 melhores | alfa vs BTC / beta |
|---|---|---|---|---|---|---|---|---|
| cr_funding — carry de perpétuos (offshore) | parcial | −2,9 / −2,9 | −2,9 / −2,9 | −0,97 | 62% | 1% | −3,2 | −2,5 / 0,00 |
| cr_premio_br — MB x Binance BR / triangular | sim | −2,5 / −2,4 | −2,5 / −2,4 | −55 | 0% | 0% | −2,5 | −2,2 / 0,00 |
| cr_panico — queda ≥ 20% em 24h, BTC/ETH | sim | +0,6 / +0,5 | +0,6 / +0,5 | 0,47 | 18% | 90% | −0,1 | +0,5 / 0,00 |
| cr_fds — ETH só no fim de semana | sim | −2,1 / −2,0 | −2,1 / −2,0 | 0,11 | 0% | 47% | −23,9 | −7,5 / 0,28 |
| cr_etf_futuro — ETF B3 x BIT/ETR/SOL | sim | −13,6 / −13,3 | −15,1 / −14,8 | −2,14 | 30% | 0% | −21,7 | −12,1 / 0,01 |
| cr_alts — momentum top 20 (long-only) | parcial | −2,9 / −2,9 | −2,9 / −3,5 | 0,14 | 7% | 45% | −30,1 | −2,4 / 0,20 |
| **cr_eventos — vende perpétuo de moeda recém-listada (offshore)** | parcial | **+19,5 / +15,2** | **+19,5 / +15,2** | **0,75** | 35% | 85% | **+10,4** | **+20,4 / −0,03** |
| cr_staking — staking ETH + perpétuo vendido (offshore) | parcial | −3,4 / −3,4 | −3,4 / −3,4 | −0,53 | 19% | 16% | −4,8 | −3,0 / 0,00 |

Fora da tabela (variante, NÃO escolhida no IS — ver §4.3): **pânico no top 20 (queda ≥ 20%, 2 dias)**: OOS +22,1 pp antes / +21,3 depois do IR,
IR 1,04, 103 negócios, 63% de acerto, sem os 10 melhores +10,5, alfa vs BTC +18,6 (beta 0,03), custo 2x +17,0, **t+2 só +3,3**.

## 4. Estratégia por estratégia

### 4.1 cr_funding — carry de financiamento (à vista comprado x perpétuo vendido)
**Tese.** O comprado alavancado no perpétuo paga ao vendido; quem faz o "banco" (à vista + perpétuo vendido na mesma corretora) recebe sem
correr preço. **Implementação.** 6 moedas; liga quando o financiamento médio de 14 dias anualizado > CDI + 20% (escolhido no IS entre
5/10/20% e 3/7/14 dias); nocional = capital/(1+1/2)/6 por moeda; liquidação do vendido se a máxima horária passa +42,5%; custos 0,15–0,20%
por lado; saldo offshore por `pf.custo_conta_exterior` (sem CDI, câmbio, IOF 1,1%/0,38% + spread) e contraparte 2,5% a.a.
**Resultado.** IS +6,4 pp (2020–21), OOS −2,9 pp. **Por quê.** O financiamento médio caiu de 22–48% a.a. (2021) para 4–14% (2023–24) e
2–5% (2025–26) — abaixo do CDI de 10–15%: a regra quase não liga depois de 2022 (15 negócios OOS, todos em 2024, contribuição ≈ 0). O que
pesa é a conta no exterior: em 2024 o carry líquido deu +1,0 pp e a conta (CDI perdido + câmbio + IOF do dinheiro parado um mês) −7,9 pp; em
2020 a mesma conta deu +11,5 pp (o real desvalorizou: beta de dólar, não carry). Para o PF brasileiro o carry precisa pagar o **CDI**, não a
T-bill — o que um fundo em dólar ganha (T-bill + 5–10%) aqui é negativo. **Aplicável** só offshore (sem CVM/BCB).

### 4.2 cr_premio_br — "prêmio brasileiro" e arbitragem doméstica
**Medição do prêmio** (BTC-BRL sobre BTCUSDT x dólar, fechamento da B3): MB 1,6% (2019) → 0,9% (2020–21) → 0,5–0,6% (2022–24) → 0,3% (2025)
→ 0,25% (2026); Binance BR e o próprio USDT/BRL contra o dólar têm o MESMO prêmio (correlação quase 1): o "kimchi" brasileiro é o custo de
IOF/remessa que o brasileiro evita comprando em R$. **Quando aparece:** sobe em pânico de cripto — prêmio médio de 2,1% nos dias de BTC
≤ −8% (contra 0,7% na média; correlação Δprêmio x retorno do BTC −0,32) — e NÃO em alta do dólar (0,6% nos dias de dólar ≥ +1,5%;
correlação −0,16): no pânico o varejo brasileiro corre para o USDT/BTC em R$ e as mesas não arbitram porque a perna de câmbio custa IOF e,
desde a Res. BCB 521, é câmbio regulado. Arbitrar contra o mundo exige offshore + câmbio: não cabe.
**Estratégia doméstica** (MB x Binance BR, e triangular BTCBRL x BTCUSDT x USDTBRL na Binance), estoque nas duas pontas, 25% do capital nas
corretoras, sinal por hora com mediana de 30 dias, execução na hora seguinte. **Resultado.** Negativo em toda a grade (IS e OOS). Desvios
> 2% entre MB e Binance BR existiram em 2020–21 (149–311 horas/ano) e quase sumiram (0–2 h/ano desde 2023); com MB a 0,70% taker o custo de
ida e volta (~2% do lote) come o desvio, e o candle de 1h do MB (1,5 BTC/hora) é último negócio, não oferta. Sobra o custo do estoque
parado (−2,5 pp/ano). A triangular dentro da Binance nunca passa de 1% (formadores fecham em segundos).

### 4.3 cr_panico — comprar a liquidação em cascata
**Tese.** Queda ≥ 15–20% em 24h em cripto é cascata de liquidação dos perpétuos (vendedor forçado a mercado); quando acaba, o livro reabre
acima — o análogo do leilão de fechamento após queda forte da B3. Compra em R$ na corretora brasileira (isenção de R$ 35 mil/mês).
**Implementação.** Sinal horário (retorno de 24h ≤ −queda), compra no fechamento da hora seguinte, segura `dias`, 20% do PL por posição,
universo ponto no tempo (BTC/ETH, ou 20 maiores por volume de 30 dias **com os mortos**). Custos 0,15% (BTC/ETH) e 0,35% (alts).
**Resultado escolhido no IS** (BTC/ETH, queda 20%, 2 dias — IS IR 0,73, o maior): OOS +0,55 pp, só 3 negócios OOS (ETH em 05/08/2024,
03/02/2025, 07/04/2025, todos ganhos): BTC/ETH raramente caem 20% em 24h. É honesto mas pequeno.
**A variante top 20 (IS IR 0,65, 2ª da grade)** é o resultado mais forte da frente e coerente com a tese: OOS +22,1 pp (IS +24,6), 103
negócios, alfa vs BTC +18,6 pp com beta ~0 (fica posicionado 2 dias, poucas vezes), ganha em 2018, 2019, 2020, 2021, 2023, 2024, 2025;
perde −46 pp em 2022 (LUNA −97% em 2 dias: −19,5 pp; FTT −79%: −15,7 pp — os mortos estão no teste). Quem trouxe o retorno OOS: WIF,
PEPE, DOGE, ADA, WLD, ARB (memes/alts de alta beta, as mais alavancadas nos perpétuos). **O alerta:** com t+2
(entrar 24h depois) cai para +3,3 pp — o repique é de horas; precisa de alerta/robô e ordem a mercado na hora seguinte (viável para PF,
Binance BR tem API). E não foi o escolhido no IS: tratar como hipótese para validação prospectiva, não como resultado.

### 4.4 cr_fds — fim de semana / horário
**Tese.** Sem ETF/futuro/CME no fim de semana, livro mais raso → prêmio de liquidez em janelas "fechadas". **Medição bruta** (log-retorno
por ano dentro da janela): fim de semana BTC +9%/+21% (IS/OOS), ETH +31%/+16%; noite −17%/+31%; horário dos EUA +10%/−9%; Ásia −23%/+2%.
Nenhuma janela é estável entre IS e OOS. **Resultado.** ETH no fim de semana (escolhido no IS): OOS −2,1 pp, beta 0,28, alfa −7,5; o giro
semanal (0,3% x 52 = 15% a.a. de custo) e o 05/08/2024 (−26% num fim de semana = −23 pp) matam. Janelas diárias (noite/EUA/Ásia) perdem
75%+ a.a. só de custo. **É beta parcial (fica 38% do tempo em ETH), não alfa.**

### 4.5 cr_etf_futuro — ETF B3 x futuro B3 (market-neutral)
**Tese.** gl_cripto_premio mostrou que o "desconto do ETF" contra o BTC era beta; aqui o hedge é o futuro da mesma bolsa no mesmo fechamento
(BIT 0,01 BTC, ETR 0,25 ETH, SOL 5 SOL — cabem desde 16/06/2025). **Resultado.** −13,6 pp OOS (2026), todas as variantes do IS negativas.
Desvio médio de entrada −0,8% (BTC), −0,8% (ETH), −1,0% (SOL): os desvios de 0,5–1% são o SPREAD do formador (SOLH11 tem 0,5–1% de spread)
e o descasamento ajuste x leilão do ETF + câmbio de ETR/SOL (cotados em US$), não preço errado; executado em t+1 pela oferta de venda, o
desvio já voltou e eu pago o spread inteiro. Placebo p = 1,0. **Morreu:** não existe desconto negociável com dado diário.

### 4.6 cr_alts — momentum/reversão de altcoins (top 20, semanal)
**Resultado.** Momentum de 28 dias sem hedge (o escolhido no IS, IR 0,78) é beta: IS +32 pp com ganhos de 80–257 pp em 2020–21, OOS −2,9
pp, beta 0,20, vol 41%, pior queda −65%. Com BTC vendido contra (o alfa de seleção): OOS −21,3 pp, alfa −19,3. Reversão de 7 dias: −25 pp
(sem hedge) e −40 pp (hedge). **Por quê:** custo de 0,35%/lado x 52 semanas e a seleção de alts que "andaram" pega exatamente os tokens que
depois são despejados por desbloqueio (DASH −57%, WLD −48%, BONK −39%). Não há alfa de seleção entre as 20 maiores para o PF long-only.

### 4.7 cr_eventos — listagens (vende a recém-listada) e halving
**Medição.** Das ~450 moedas listadas em US$ na Binance desde 2019 com volume > US$ 5 mi no 1º dia (inclusive as deslistadas depois), a
mediana do retorno do 1º ao 30º dia é −13% a −33% em TODOS os anos (−19% a −50% até o 60º). **Negócio:** a listagem é o evento de liquidez
de quem tem a moeda barata (fundos de venture, equipe, airdrop/launchpool) — o insider destrava; o comprador é o varejo da "listou na
Binance". O comprador forçado do lado vendido inexiste, o vendedor desejoso é o insider. Comprar a novidade (o que o PF faz em corretora
brasileira) perdeu −41,9 pp OOS. **Estratégia:** vender o perpétuo (REAL: preço e financiamento do arquivo da Binance; só se o perpétuo
negociava até 3 dias depois do à vista) 5% do PL por moeda por 30 dias; margem isolada 1x — liquidado quando o fechamento passa +60%
(proxy de máxima +85%) perdendo 86% do nocional; offshore (conta exterior + contraparte 2,5%).
**Resultado.** OOS +19,5 pp antes / +15,2 pp depois do IR (exterior 15%), IR 0,75, P(bater 3a) 85%, sem os 10 melhores +10,4, custo 2x +9,3,
t+2 +21,3, placebo p 0,0, beta ~0 (alfa vs BTC +20,4). **Mas:** por ano 2023 −11,5, 2024 −5,9, **2025 +120,8**, 2026 +4,4; walk-forward −6,1;
PBO 35%. É UM ano: em 2025 a Binance listou ~96 moedas com volume (concorrência média de 7,6 posições, máx. 16) e quase todas caíram
30–70% em 30 dias (BIO, SOLV, MIRA, XPL, 2Z, HEMI...). 2023–24 (memes TIA, ORDI, WIF, PIXEL, NOT, PNUT) liquidaram várias vendas (a perda
é sempre 86% do lote = −4,35 pp do PL). Sensibilidade: +30% a.a. de custo de aluguel/financiamento extra → +13,3 pp; +100% a.a. → 0.
Halving (2 eventos): −1,3 pp, anedota.
**Aplicável?** Só offshore (conta internacional fora de CVM/BCB, a rota que a Binance oferece "por conta e risco" do cliente).

### 4.8 cr_staking — staking de ETH vs CDI
**Medição.** APY do stETH: 4,5% (2022), 4,3% (2023), 3,2% (2024), 2,8% (2025), 2,4% (2026) — em ETH. **Neutro** (staking + perpétuo vendido,
offshore, liga quando staking + financiamento > CDI + 5%): OOS −3,4 pp (sem contraparte −2,8): staking + financiamento de 6–17% a.a. não
paga o CDI de 11–15% + IOF + câmbio do dinheiro parado. **Beta** (ETH em staking numa corretora brasileira): OOS +7,4 pp, beta 0,25 — é o
preço do ETH; o staking é um cupom de 2–4% sobre o beta, não alfa. Rota B3 (ETH em staking em R$ + ETR vendido): o ETR é cotado em US$, então
o hedge deixa exposição cambial sobre o nocional e paga a base em dólar, não o CDI; precisaria de WDO (US$ 10 mil, grande demais). Não testado
além da medição.

## 5. O que deu certo e por quê / o que deu errado

- **Deu certo (com ressalvas):** os dois casos em que há um **vendedor forçado ou desejoso** do outro lado — a liquidação em cascata
  (pânico top 20, onshore, isento) e o insider destravando na listagem (venda offshore). É o mesmo padrão da rodada 1.
- **Deu errado:** tudo que depende de carregar um prêmio pequeno com o dinheiro fora do CDI (financiamento, staking, arbitragem com estoque):
  o benchmark do PF é CDI de 10–15%, não T-bill de 4–5%; o que é carry para um fundo em dólar é perda para o brasileiro. E tudo que gira
  muito (fim de semana, alts semanais) morre no custo de 0,15–0,35%/lado.
- **Beta disfarçado identificado:** cr_alts (momentum) e cr_fds e o staking "beta": ganham porque cripto subiu.

## 6. Bugs encontrados e corrigidos

1. Motor com peso fixo rebalanceado a cada hora: um vendido/comprado em LUNA perdia 371% do lote (rebalanceava para 20% a cada hora).
   Corrigido para "compra e segura" (valor flutua) com rebalanceamento só quando pedido.
2. Hedge de BTC nas alts nunca rebalanceado (o vendido crescia 10x com o BTC): adicionado `rebal` no motor.
3. cr_funding multiplicava o nocional em R$ pelo câmbio de novo (saldo de R$ 33 mil com capital de R$ 20 mil).
4. cr_eventos com o à vista como proxy do perpétuo e financiamento fixo: trocado por perpétuo e financiamento reais; sem teto de perda o
   vendido em PNUT perdia 298% do lote — agora a margem isolada 1x limita a perda a 86%.
5. Vendas de cripto para a isenção de R$ 35 mil: o peso de fim de pregão não mostra giro intradiário (fim de semana, arbitragem) —
   colunas técnicas `_vendas_a/_b` em `posicoes()` levam as vendas reais ao motor de IR.

## 7. Próximos passos

1. **Pânico top 20**: transformar em módulo próprio e validar prospectivamente (paper trading com alerta horário na Binance BR); medir o
   repique com candles de 1 minuto (o t+2 diário destrói o resultado); filtro anti-colapso de emissor (LUNA/FTT: queda + saque em massa).
2. **Venda de listagens**: medir com hora do anúncio, financiamento intradiário e taxa de liquidação com máxima de 1 minuto; testar o tamanho
   que a conta internacional aceita; decidir se o risco regulatório (conta fora de CVM/BCB) é aceitável para o grupo.
3. Prêmio brasileiro: monitorar se a Res. BCB 521 + IOF de stablecoin abrem o prêmio (o desvio voltaria a 1–2%).

## 8. Negócios (10 melhores / 10 piores fora da amostra, R$ 20 mil)

Gerado por `cr_rodar.py` (`pf/resultados/pf2_cripto/negocios.md`); contrib_pp = contribuição ao PL em pp.


#### cr_funding — 10 melhores negócios OOS

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| XRP     |      1 | 2024-03-01 00:00:00 | 2024-03-27 00:00:00 |     26 |        3.16 |         0.3  |
| SOL     |      1 | 2024-02-29 00:00:00 | 2024-03-28 00:00:00 |     28 |        3.92 |         0.23 |
| ETH     |      1 | 2024-03-05 00:00:00 | 2024-03-27 00:00:00 |     22 |        2.13 |         0.2  |
| BTC     |      1 | 2024-03-05 00:00:00 | 2024-03-26 00:00:00 |     21 |        2    |         0.19 |
| DOGE    |      1 | 2024-03-04 00:00:00 | 2024-03-27 00:00:00 |     25 |        3.01 |         0.13 |
| XRP     |      1 | 2024-01-02 00:00:00 | 2024-01-11 00:00:00 |     12 |        0.71 |         0.03 |
| SOL     |      1 | 2024-01-02 00:00:00 | 2024-01-12 00:00:00 |     10 |        0.52 |         0.01 |
| ETH     |      1 | 2024-01-02 00:00:00 | 2024-01-09 00:00:00 |      7 |        0.41 |         0.01 |
| DOGE    |      1 | 2024-04-01 00:00:00 | 2024-04-11 00:00:00 |     10 |        0.5  |         0.01 |
| XRP     |      1 | 2024-04-02 00:00:00 | 2024-04-12 00:00:00 |     10 |        0.46 |         0.01 |


#### cr_funding — 10 piores negócios OOS

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| DOGE    |      1 | 2024-12-10 00:00:00 | 2024-12-11 00:00:00 |      1 |        0.05 |        -0.04 |
| BNB     |      1 | 2024-03-15 00:00:00 | 2024-03-18 00:00:00 |      2 |        0.1  |        -0.03 |
| BTC     |      1 | 2024-01-04 00:00:00 | 2024-01-08 00:00:00 |      2 |        0.07 |        -0.03 |
| SOL     |      1 | 2024-04-02 00:00:00 | 2024-04-08 00:00:00 |      6 |        0.21 |        -0.02 |
| DOGE    |      1 | 2024-01-02 00:00:00 | 2024-01-09 00:00:00 |      7 |        0.41 |         0    |
| XRP     |      1 | 2024-04-02 00:00:00 | 2024-04-12 00:00:00 |     10 |        0.46 |         0.01 |
| DOGE    |      1 | 2024-04-01 00:00:00 | 2024-04-11 00:00:00 |     10 |        0.5  |         0.01 |
| ETH     |      1 | 2024-01-02 00:00:00 | 2024-01-09 00:00:00 |      7 |        0.41 |         0.01 |
| SOL     |      1 | 2024-01-02 00:00:00 | 2024-01-12 00:00:00 |     10 |        0.52 |         0.01 |
| XRP     |      1 | 2024-01-02 00:00:00 | 2024-01-11 00:00:00 |     12 |        0.71 |         0.03 |


#### cr_premio_br — 10 melhores negócios OOS

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| BTC     |      1 | 2023-03-14 00:00:00 | 2023-03-15 00:00:00 |      0 |        0.27 |        -0.05 |
| ETH     |     -1 | 2024-08-05 00:00:00 | 2024-08-05 00:00:00 |      0 |       -0.1  |        -0.07 |


#### cr_premio_br — 10 piores negócios OOS

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| ETH     |     -1 | 2024-08-05 00:00:00 | 2024-08-05 00:00:00 |      0 |       -0.1  |        -0.07 |
| BTC     |      1 | 2023-03-14 00:00:00 | 2023-03-15 00:00:00 |      0 |        0.27 |        -0.05 |


#### cr_panico — 10 melhores negócios OOS

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| ETH     |      1 | 2025-02-03 00:00:00 | 2025-02-05 00:00:00 |      2 |       10.17 |         1.34 |
| ETH     |      1 | 2025-04-07 00:00:00 | 2025-04-09 00:00:00 |      2 |        1.59 |         0.6  |
| ETH     |      1 | 2024-08-05 00:00:00 | 2024-08-07 00:00:00 |      2 |        6.87 |         0.51 |


#### cr_panico — 10 piores negócios OOS

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| ETH     |      1 | 2024-08-05 00:00:00 | 2024-08-07 00:00:00 |      2 |        6.87 |         0.51 |
| ETH     |      1 | 2025-04-07 00:00:00 | 2025-04-09 00:00:00 |      2 |        1.59 |         0.6  |
| ETH     |      1 | 2025-02-03 00:00:00 | 2025-02-05 00:00:00 |      2 |       10.17 |         1.34 |


#### cr_fds — 10 melhores negócios OOS

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| ETH     |      1 | 2023-03-10 00:00:00 | 2023-03-13 00:00:00 |      2 |       11.59 |        10.87 |
| ETH     |      1 | 2025-05-09 00:00:00 | 2025-05-12 00:00:00 |      2 |        9.35 |         9.7  |
| ETH     |      1 | 2024-11-08 00:00:00 | 2024-11-11 00:00:00 |      2 |        8.1  |         9.02 |
| ETH     |      1 | 2024-04-05 00:00:00 | 2024-04-08 00:00:00 |      2 |        9.74 |         8.8  |
| ETH     |      1 | 2023-01-13 00:00:00 | 2023-01-16 00:00:00 |      2 |        7.87 |         7.91 |
| ETH     |      1 | 2023-12-01 00:00:00 | 2023-12-04 00:00:00 |      2 |        7.76 |         7.6  |
| ETH     |      1 | 2024-07-12 00:00:00 | 2024-07-15 00:00:00 |      2 |        7.3  |         7.54 |
| ETH     |      1 | 2026-06-05 00:00:00 | 2026-06-08 00:00:00 |      2 |        7.72 |         7.25 |
| ETH     |      1 | 2026-03-13 00:00:00 | 2026-03-16 00:00:00 |      2 |        8.41 |         6.95 |
| ETH     |      1 | 2025-04-11 00:00:00 | 2025-04-14 00:00:00 |      2 |        7.15 |         6.62 |


#### cr_fds — 10 piores negócios OOS

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| ETH     |      1 | 2024-08-02 00:00:00 | 2024-08-05 00:00:00 |      2 |      -26.01 |       -23.11 |
| ETH     |      1 | 2025-01-31 00:00:00 | 2025-02-03 00:00:00 |      2 |      -22.18 |       -21.89 |
| ETH     |      1 | 2025-04-04 00:00:00 | 2025-04-07 00:00:00 |      2 |      -15.97 |       -15.71 |
| ETH     |      1 | 2026-01-30 00:00:00 | 2026-02-02 00:00:00 |      2 |      -13.77 |       -14.43 |
| ETH     |      1 | 2025-11-28 00:00:00 | 2025-12-01 00:00:00 |      2 |       -7.7  |        -7.92 |
| ETH     |      1 | 2025-05-16 00:00:00 | 2025-05-19 00:00:00 |      2 |       -7.35 |        -7.4  |
| ETH     |      1 | 2024-06-21 00:00:00 | 2024-06-24 00:00:00 |      2 |       -6.12 |        -6.92 |
| ETH     |      1 | 2025-01-10 00:00:00 | 2025-01-13 00:00:00 |      2 |       -6.52 |        -6.86 |
| ETH     |      1 | 2023-05-05 00:00:00 | 2023-05-08 00:00:00 |      2 |       -6.82 |        -6.68 |
| ETH     |      1 | 2025-01-24 00:00:00 | 2025-01-27 00:00:00 |      2 |       -6.79 |        -6.63 |


#### cr_etf_futuro — 10 melhores negócios OOS

| ativo      |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |   desvio_entrada_% |
|:-----------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|-------------------:|
| ETHE11xETR |      1 | 2026-07-01 00:00:00 | 2026-07-09 00:00:00 |      6 |        9.47 |         1.94 |              -0.52 |
| SOLH11xSOL |      1 | 2026-07-01 00:00:00 | 2026-07-03 00:00:00 |      2 |        3.29 |         0.95 |              -2.15 |
| BITH11xBIT |      1 | 2026-06-30 00:00:00 | 2026-07-08 00:00:00 |      6 |        5.31 |         0.8  |              -1.47 |
| SOLH11xSOL |      1 | 2026-08-25 00:00:00 | 2026-08-31 00:00:00 |      4 |        2.04 |         0.52 |              -2.55 |
| ETHE11xETR |      1 | 2026-06-03 00:00:00 | 2026-06-09 00:00:00 |      3 |        2.09 |         0.48 |              -0.53 |
| SOLH11xSOL |      1 | 2026-04-17 00:00:00 | 2026-04-20 00:00:00 |      1 |        1.72 |         0.38 |              -0.8  |
| ETHE11xETR |      1 | 2026-07-22 00:00:00 | 2026-07-27 00:00:00 |      3 |        1.54 |         0.37 |              -0.77 |
| SOLH11xSOL |      1 | 2026-09-25 00:00:00 | 2026-09-29 00:00:00 |      2 |        2.12 |         0.34 |              -0.55 |
| ETHE11xETR |      1 | 2026-09-14 00:00:00 | 2026-09-18 00:00:00 |      4 |        2    |         0.33 |              -0.72 |
| SOLH11xSOL |      1 | 2026-06-17 00:00:00 | 2026-06-18 00:00:00 |      1 |        0.66 |         0.18 |              -0.57 |


#### cr_etf_futuro — 10 piores negócios OOS

| ativo      |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |   desvio_entrada_% |
|:-----------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|-------------------:|
| SOLH11xSOL |      1 | 2026-05-29 00:00:00 | 2026-06-01 00:00:00 |      1 |       -6.59 |        -1.37 |              -0.55 |
| SOLH11xSOL |      1 | 2026-10-02 00:00:00 | 2026-10-05 00:00:00 |      1 |       -6.67 |        -1.04 |              -0.59 |
| ETHE11xETR |      1 | 2026-04-01 00:00:00 | 2026-04-02 00:00:00 |      1 |       -3.56 |        -0.98 |              -0.66 |
| SOLH11xSOL |      1 | 2026-07-09 00:00:00 | 2026-07-16 00:00:00 |      5 |       -3.19 |        -0.96 |              -0.67 |
| ETHE11xETR |      1 | 2026-10-02 00:00:00 | 2026-10-07 00:00:00 |      3 |       -5.5  |        -0.96 |              -0.75 |
| SOLH11xSOL |      1 | 2026-06-29 00:00:00 | 2026-06-30 00:00:00 |      1 |       -2.67 |        -0.79 |              -1.09 |
| SOLH11xSOL |      1 | 2026-07-27 00:00:00 | 2026-07-28 00:00:00 |      1 |       -2.54 |        -0.74 |              -0.72 |
| SOLH11xSOL |      1 | 2026-03-09 00:00:00 | 2026-03-11 00:00:00 |      2 |       -2.98 |        -0.67 |              -0.89 |
| SOLH11xSOL |      1 | 2026-07-17 00:00:00 | 2026-07-21 00:00:00 |      2 |       -2.28 |        -0.66 |              -0.55 |
| SOLH11xSOL |      1 | 2026-06-23 00:00:00 | 2026-06-24 00:00:00 |      1 |       -2.4  |        -0.65 |              -1.16 |


#### cr_alts — 10 melhores negócios OOS

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| DOGE    |      1 | 2024-10-28 00:00:00 | 2024-12-09 00:00:00 |     42 |      230.27 |        15.61 |
| SEI     |      1 | 2023-12-04 00:00:00 | 2024-02-05 00:00:00 |     63 |      154.53 |        12.16 |
| RUNE    |      1 | 2023-10-30 00:00:00 | 2023-12-11 00:00:00 |     42 |      168.6  |        11.89 |
| SOL     |      1 | 2023-10-16 00:00:00 | 2023-12-04 00:00:00 |     49 |      173.58 |        10.88 |
| PEPE    |      1 | 2024-03-04 00:00:00 | 2024-04-08 00:00:00 |     35 |       64.66 |         9.88 |
| APT     |      1 | 2023-01-16 00:00:00 | 2023-02-27 00:00:00 |     42 |       88.58 |         9.42 |
| SUI     |      1 | 2024-09-16 00:00:00 | 2024-11-04 00:00:00 |     49 |       93.67 |         8.19 |
| LINK    |      1 | 2023-09-25 00:00:00 | 2023-11-20 00:00:00 |     56 |       96.92 |         8.19 |
| ZEC     |      1 | 2026-04-06 00:00:00 | 2026-06-08 00:00:00 |     63 |       66.13 |         8.05 |
| ENA     |      1 | 2026-08-10 00:00:00 | 2026-09-21 00:00:00 |     42 |       84.25 |         8.04 |


#### cr_alts — 10 piores negócios OOS

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| DASH    |      1 | 2026-01-19 00:00:00 | 2026-02-18 00:00:00 |     28 |      -56.77 |        -7.68 |
| DASH    |      1 | 2025-11-10 00:00:00 | 2025-12-08 00:00:00 |     28 |      -53.56 |        -6.72 |
| WLD     |      1 | 2025-09-15 00:00:00 | 2025-10-13 00:00:00 |     28 |      -47.69 |        -5.31 |
| BONK    |      1 | 2026-01-19 00:00:00 | 2026-02-09 00:00:00 |     21 |      -39.44 |        -4.9  |
| TON     |      1 | 2026-05-11 00:00:00 | 2026-06-08 00:00:00 |     28 |      -39.69 |        -4.25 |
| SOL     |      1 | 2025-01-27 00:00:00 | 2025-02-24 00:00:00 |     28 |      -33.32 |        -4.08 |
| ICP     |      1 | 2025-11-17 00:00:00 | 2025-12-08 00:00:00 |     21 |      -35.43 |        -3.85 |
| AXS     |      1 | 2026-02-02 00:00:00 | 2026-02-23 00:00:00 |     21 |      -35.48 |        -3.82 |
| SUI     |      1 | 2026-01-12 00:00:00 | 2026-02-02 00:00:00 |     21 |      -29.7  |        -3.5  |
| XLM     |      1 | 2024-12-02 00:00:00 | 2024-12-23 00:00:00 |     21 |      -31.53 |        -3.38 |


#### cr_eventos — 10 melhores negócios OOS

| ativo    |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:---------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| BIOUSDT  |     -1 | 2025-01-06 00:00:00 | 2025-02-04 00:00:00 |     30 |       77.04 |         3.83 |
| MIRAUSDT |     -1 | 2025-09-29 00:00:00 | 2025-10-28 00:00:00 |     30 |       72.89 |         3.62 |
| SOLVUSDT |     -1 | 2025-01-20 00:00:00 | 2025-02-18 00:00:00 |     30 |       69.19 |         3.44 |
| XPLUSDT  |     -1 | 2025-09-29 00:00:00 | 2025-10-27 00:00:00 |     30 |       68.75 |         3.41 |
| EDENUSDT |     -1 | 2025-10-02 00:00:00 | 2025-11-03 00:00:00 |     30 |       67.49 |         3.35 |
| 2ZUSDT   |     -1 | 2025-10-06 00:00:00 | 2025-11-03 00:00:00 |     30 |       66.42 |         3.3  |
| HOLOUSDT |     -1 | 2025-09-15 00:00:00 | 2025-10-13 00:00:00 |     30 |       66.24 |         3.29 |
| BMTUSDT  |     -1 | 2025-03-20 00:00:00 | 2025-04-22 00:00:00 |     30 |       65.97 |         3.27 |
| ZKCUSDT  |     -1 | 2025-09-17 00:00:00 | 2025-10-17 00:00:00 |     30 |       65.65 |         3.26 |
| HEMIUSDT |     -1 | 2025-09-25 00:00:00 | 2025-10-27 00:00:00 |     30 |       65.38 |         3.25 |


#### cr_eventos — 10 piores negócios OOS

| ativo     |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:----------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| BEAMXUSDT |     -1 | 2023-11-20 00:00:00 | 2023-12-07 00:00:00 |     18 |         -86 |        -4.35 |
| PIXELUSDT |     -1 | 2024-02-21 00:00:00 | 2024-03-12 00:00:00 |     20 |         -86 |        -4.35 |
| TIAUSDT   |     -1 | 2023-11-03 00:00:00 | 2023-11-14 00:00:00 |     12 |         -86 |        -4.35 |
| BARDUSDT  |     -1 | 2025-09-22 00:00:00 | 2025-09-25 00:00:00 |      5 |         -86 |        -4.35 |
| A2ZUSDT   |     -1 | 2025-08-01 00:00:00 | 2025-08-11 00:00:00 |      8 |         -86 |        -4.35 |
| ORDIUSDT  |     -1 | 2023-11-09 00:00:00 | 2023-11-14 00:00:00 |      5 |         -86 |        -4.35 |
| KAITOUSDT |     -1 | 2025-02-24 00:00:00 | 2025-02-28 00:00:00 |      6 |         -86 |        -4.35 |
| AVNTUSDT  |     -1 | 2025-09-17 00:00:00 | 2025-09-23 00:00:00 |      6 |         -86 |        -4.35 |
| WIFUSDT   |     -1 | 2024-03-07 00:00:00 | 2024-03-18 00:00:00 |      9 |         -86 |        -4.35 |
| SENTUSDT  |     -1 | 2026-01-26 00:00:00 | 2026-02-02 00:00:00 |      9 |         -86 |        -4.35 |


#### cr_staking — 10 melhores negócios OOS

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| ETH     |      1 | 2024-02-27 00:00:00 | 2024-04-18 00:00:00 |     51 |        4.97 |         2.73 |
| ETH     |      1 | 2023-12-14 00:00:00 | 2024-01-18 00:00:00 |     35 |        2.45 |         1.27 |
| ETH     |      1 | 2024-11-14 00:00:00 | 2024-12-23 00:00:00 |     37 |        2.27 |         1.16 |
| ETH     |      1 | 2024-06-03 00:00:00 | 2024-06-17 00:00:00 |     14 |        0.71 |         0.25 |
| ETH     |      1 | 2023-11-13 00:00:00 | 2023-11-27 00:00:00 |     14 |        0.7  |         0.24 |
| ETH     |      1 | 2023-01-24 00:00:00 | 2023-01-25 00:00:00 |      1 |        0.08 |        -0.13 |
| ETH     |      1 | 2023-01-27 00:00:00 | 2023-01-30 00:00:00 |      3 |        0.04 |        -0.16 |
| ETH     |      1 | 2023-12-12 00:00:00 | 2023-12-13 00:00:00 |      1 |        0.01 |        -0.18 |


#### cr_staking — 10 piores negócios OOS

| ativo   |   lado | entrada             | saida               |   dias |   retorno_% |   contrib_pp |
|:--------|-------:|:--------------------|:--------------------|-------:|------------:|-------------:|
| ETH     |      1 | 2023-12-12 00:00:00 | 2023-12-13 00:00:00 |      1 |        0.01 |        -0.18 |
| ETH     |      1 | 2023-01-27 00:00:00 | 2023-01-30 00:00:00 |      3 |        0.04 |        -0.16 |
| ETH     |      1 | 2023-01-24 00:00:00 | 2023-01-25 00:00:00 |      1 |        0.08 |        -0.13 |
| ETH     |      1 | 2023-11-13 00:00:00 | 2023-11-27 00:00:00 |     14 |        0.7  |         0.24 |
| ETH     |      1 | 2024-06-03 00:00:00 | 2024-06-17 00:00:00 |     14 |        0.71 |         0.25 |
| ETH     |      1 | 2024-11-14 00:00:00 | 2024-12-23 00:00:00 |     37 |        2.27 |         1.16 |
| ETH     |      1 | 2023-12-14 00:00:00 | 2024-01-18 00:00:00 |     35 |        2.45 |         1.27 |
| ETH     |      1 | 2024-02-27 00:00:00 | 2024-04-18 00:00:00 |     51 |        4.97 |         2.73 |
