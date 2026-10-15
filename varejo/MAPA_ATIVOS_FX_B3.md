# Mapa de ativos para varejo: carry de moedas e rebalanceamento do Ibovespa

Pesquisa de 15/10/2026 para pessoa física residente no Brasil com R$ 20 mil (≈ US$ 3,95 mil a 5,064 R$/US$).
Tabela completa, ativo por ativo, com fontes: `mapa_ativos_fx_b3.csv` (130 linhas). Quando algo não pôde ser verificado, está escrito
"não confirmado". Volumes vêm do TradingView (média de 20 pregões ou do último pregão). As margens CME são as de manutenção da tabela oficial.

---

## 1. Carry de moedas

### O ponto principal: só o **futuro** entrega o carry para uma conta pequena

| Instrumento | Carry recebido? | Por quê |
|---|---|---|
| Futuro (CME, B3) | **Sim** | O diferencial de juros vem embutido no preço do futuro (pontos a termo). Na B3, a garantia pode ficar em Tesouro Selic e rende CDI. Na CME/IBKR, o caixa parado em USD rende 0% abaixo de US$ 10 mil. |
| Câmbio à vista com margem na IBKR | **Não** | A IBKR não paga juros sobre o primeiro saldo de cada moeda (USD 10k, EUR 10k, MXN 200k, ZAR 150k, TRY 250k, HUF 3,5M, PLN 400k, CZK 250k, NOK 100k, SEK 110k, CHF 100k…). ILS e INR rendem 0% em qualquer saldo. Com NAV < US$ 100 mil, a taxa ainda é pró-rata (NAV/100k). Já o saldo **negativo** (a moeda vendida) paga juros de margem de BM+1,5% (USD 5,38%, JPY 2,57%, EUR 3,97%) até BM+5% (HUF 10,5%, ILS 7,9%, TRY 34,7%). Resultado: a perna comprada rende zero e a perna vendida paga juros. O carry fica negativo. |
| ETFs de moeda (FXY, FXF, FXE…) | Parcial | Pagam o juro do depósito menos ~0,40% a.a. Não dá para vender a descoberto nas contas de varejo, e a exposição é fixa (não seleciona as 3 maiores e as 3 menores). CEW e UDN embutem o carry via forwards/futuros, mas são cestas fixas. CYB não foi encontrado (provavelmente encerrado, não confirmado). |

Câmbio à vista na IBKR, outros detalhes: comissão de 0,20 bp com mínimo de US$ 2 por ordem. Abaixo do lote mínimo (US$ 25k, 20k EUR,
2,5M JPY, 300k MXN, 350k ZAR…) a ordem vira *odd lot* e sai com preço pior. Não há câmbio à vista de THB, IDR, COP nem INR negociável.
O BRL aparece na lista de moedas, mas não confirmei o uso por residente no Brasil. A margem de câmbio à vista é de ~5% nas moedas da
Europa Central e ~10% em MXN/ZAR. Esses números vieram de busca, porque a página de margem da IBKR carrega por JavaScript e não abriu: não confirmado.

### Futuros disponíveis

**CME (via IBKR, conta de não residente):** existem micros de EUR (M6E 12,5k ≈ US$14k, margem US$210), JPY (MJY ≈ US$7,9k, US$280),
CHF (MSF ≈ US$15,2k, US$360), AUD (M6A ≈ US$6,9k, US$175), CAD (MCD ≈ US$7,1k, US$80), GBP (M6B ≈ US$8,3k, US$170) e INR (MIR ≈ US$10,5k, US$200).
Sem micro, o lote é grande: NZD 6N (US$56k), MXN 6M (US$27k), BRL 6L (US$19,7k), ZAR 6Z (US$30k). CZK, HUF, PLN, ILS, SEK, NOK e TRY
estão listados, mas são enormes (US$92k–324k) e quase não negociam (0–40 contratos/dia). THB e IDR estão listados, sem liquidez confirmada.
COP não existe.

**B3 (confirmado no Ofício Circular 022/2025-VPC):** há duas famílias de contratos.
- **Moeda contra USD, liquidada em reais**, todos de **US$ 10 mil** (ou 10 mil da moeda): EUP (EUR), GBR, AUS, NZL, JAP, SWI, CAN, MEX, AFS (ZAR),
  TUQ (TRY), SEK, NOK, CNH, CHL, ARS, RUB. É a estrutura ideal para o fundo: a exposição é exatamente moeda vs USD, o carry vem no preço
  e a garantia em Tesouro Selic rende CDI. O problema é a liquidez. Média de 20 pregões: EUP ~1.860/dia, JAP ~360, SWI ~275, MEX ~270,
  AUS ~190, AFS ~81, CAN ~67, GBR ~44, SEK ~26, NOK ~25, NZL ~6, TUQ 0.
- **Real contra moeda** (EUR 50k, JPY 5M, GBP 35k, CHF 50k, CAD 60k, AUD 60k, NZD 75k, MXN 750k, ZAR 350k, TRY 75k, CNY 350k, CLP 25M)
  e os minis **WDO** (US$10k) e **WEU** (10k EUR). Com exceção de DOL e WDO, o volume é praticamente nulo (WEU ~115/dia, EUR ~20).
  Esses contratos misturam a exposição ao BRL, então não servem para o "moeda vs USD".
- Não há contratos B3 de CZK, HUF, PLN, ILS, INR, IDR, COP nem THB.
- **Acesso:** a Clear divulga WIN, WDO, IND, DOL, WEU e agrícolas. Se Clear, Rico, XP ou Nubank liberam EUP, MEX, JAP etc.: **não confirmado**.
  Provavelmente só por mesa ou plataforma profissional (BTG/Genial via Profit, também não confirmado). Custos B3 desses contratos: não confirmados.

### Melhor caminho por moeda

| Moeda | Melhor caminho de varejo | Nocional de 1 contrato vs capital | Carry recebido | Edge |
|---|---|---|---|---|
| BRL | vender WDO (Clear/Rico, corretagem zero) | US$10k = 2,5x | sim | parcial |
| EUR | M6E (CME) ou EUP (B3) | 2,8–3,6x | sim | parcial |
| JPY | MJY (CME) | 2x | sim | parcial |
| CHF | MSF (CME) ou SWI (B3) | 2,5–3,8x | sim | parcial |
| CAD | MCD (CME) | 1,8x | sim | parcial |
| GBP / AUD | M6B / M6A (CME) | 1,7–2,1x | sim | parcial |
| MXN | MEX (B3) ou 6M (CME, 6,8x) | 2,5x | sim | parcial |
| ZAR | AFS (B3) ou 6Z (CME, 7,6x) | 2,5x | sim | parcial |
| NZD | NZL (B3, ~6/dia) | 1,4x | sim | parcial |
| SEK / NOK | SEK / NOK (B3, ~25/dia) | 2,5x | sim | parcial |
| INR | MIR (CME, liquidez não confirmada) | ~2,7x | sim | parcial |
| CZK, HUF, PLN, ILS | só câmbio à vista na IBKR | odd lot | **não** (juros da conta pequena) | não |
| TRY | nenhum (futuros sem negócios; à vista paga 34,7% se vendido) | — | não | não |
| THB, IDR, COP | nenhum (NDF de balcão) | — | — | não |

### O que se perde
1. **Tamanho.** O fundo carrega 3 moedas compradas e 3 vendidas, com vol-alvo de 8%. Com US$ 4 mil, cada perna deveria ter algumas centenas
   a ~US$ 1 mil de nocional. O menor contrato que existe tem US$ 7–15 mil. Com 1 contrato por perna, a alavancagem bruta fica em ~10–15x
   em vez de ~1–1,5x. Ou se opera 1 ou 2 pernas (concentração), ou não se replica o fundo.
2. **Universo.** CZK, HUF, PLN, ILS, TRY, THB, IDR e COP ficam de fora, ou entram sem carry. Várias delas costumam estar no topo ou no fundo do ranking.
3. **Liquidez e acesso na B3.** Os contratos de lote certo (US$10k) quase não negociam, e o acesso pela Clear/Rico não foi confirmado.
4. **Câmbio e caixa.** Na IBKR, o caixa da margem rende 0% e há o custo de remessa. Na B3, a garantia rende CDI (é a vantagem dela).

**Conclusão:** com R$ 20 mil, o carry de 6 pernas **não preserva o edge**. O mais próximo é uma versão reduzida só com futuros
(micros da CME para EUR/JPY/CHF/CAD/AUD/GBP, mais MEX/AFS na B3 se a corretora liberar). Mesmo assim, fica bem mais alavancada e concentrada que o original.

---

## 2. Rebalanceamento do Ibovespa

**Ações:** operáveis em qualquer corretora de varejo (Clear, Rico, XP, BTG, Inter, Nubank, Toro, Genial, C6). A corretagem é zero na Clear e na Rico (Rico com RLP).
O mercado fracionário (sufixo F) aceita 1 ação. Emolumentos B3 de pessoa física: **0,030%** em operação normal (negociação 0,005% + liquidação 0,0224% + TTA 0,0026%)
e 0,023% em day trade, na faixa até R$0,2 mi/dia. O edge (comprar antes do fluxo dos ETFs) **não depende do tamanho**. Neste fundo, o varejo não perde nada nas ações.

**Tickers que mudaram ou deixaram de existir** (detalhe e fontes no CSV; 34 dos 103 do backtest):
BTOW3→AMER3; BIDI11/BIDI4→INBR32 (BDR); VVAR11→VVAR3→VIIA3→BHIA3; ARZZ3 e SOMA3→AZZA3; BRDT3→VBBR3; IGTA3→IGTI11;
NATU3→NTCO3→NATU3 (de novo desde 07/2025); TIMP3→TIMS3; TBLE3→EGIE3; TRPL4→ISAE4; RUMO3→RAIL3; BBTG11→BPAC11; ALSO3→ALOS3; RRRP3→BRAV3;
ELET3/ELET6→AXIA3/AXIA6 (11/2025); CPLE6→CPLE3 (Novo Mercado, 11/2025); PETZ3→AUAU3 (01/2026); MRFG3→MBRF3 (09/2025);
GOLL4→GOLL54 (2025); AZUL4→AZUL54→AZUL53→AZUL3 (2025–26).
**Deslistadas:** ENBR3 (2023), GNDI3 (→HAPV3, 2022), HGTX3 (2021), LCAM3 (→RENT3, 2022), SMLS3/SMLE3 (2021), SULA11 (→RDOR3, 2022),
CRFB3 (05/2025, trocada por dinheiro ou BDR do Carrefour). OIBR3: situação não confirmada.

**Hedge (o fundo faz hedge 1:1 em Ibovespa).** Este é o ponto fraco do varejo.

| Opção | Viável? | Custo | Problema |
|---|---|---|---|
| WIN vendido | sim (Clear/Rico, corretagem zero) | B3 ≈ R$0,21–0,39 por contrato (tarifa do IND × 0,2) + R$0,30 de liquidação; margem mínima de day trade R$155 (fev/2026); margem overnight não confirmada (~R$2–7 mil segundo busca) | 1 WIN ≈ **R$41,7 mil** (208.460 pts × R$0,20), ou 2,1x o capital inteiro, enquanto as posições são de R$1–3 mil. O hedge fica em 0 ou em 2x. |
| BOVA11 vendido com aluguel | sim (Clear e Rico como tomador; Rico abre o aluguel tomador automático em D+1) | corretora **0,5% do volume por contrato novo ou renovado**; taxa ao doador ~0,4–0,7% a.a. (BTG 0,70% em 09/10/2026); B3 20% da taxa | Acerta o tamanho (1 cota ≈ R$200), mas 0,5% por abertura × 3 rebalanceamentos por ano ≈ 1,5 pp a.a., quase todo o ativo do fundo (+1,8 pp a.a.). |
| ETF inverso de Ibovespa | **não encontrado** na B3 (não confirmado) | — | Alternativas: put de BOVA11/IBOV, ou BZQ na NYSE (existência atual não confirmada). |

**Lado vendido** (só na variante "ambos"; o fundo escolhido usa `lado="compra"`): pessoa física pode vender a descoberto via BTC na Clear, Rico, XP ou BTG,
com garantia (~125% segundo busca). O custo é de 0,5% por contrato mais a taxa do papel, que costuma ser alta justamente nos que saem do índice (não medido).

**Conclusão:** o lado comprado **preserva o edge**. O hedge preserva só **parcialmente**. O caminho mais barato é usar WIN
quando a carteira comprada passa de ~R$20 mil (hedge de 0,5 a 1x). Com menos que isso, as alternativas são ficar sem hedge (risco de beta
por ~10 pregões) ou pagar o aluguel de BOVA11, que consome quase todo o ativo.

---

### Fontes principais
- IBKR juros pagos/cobrados, comissão e lotes de câmbio: interactivebrokers.com/en/accounts/fees/pricing-interest-rates.php,
  /en/trading/margin-rates.php, /en/pricing/commissions-spot-currencies.php, /en/trading/forexOrderSize.php, /en/trading/products-spot-currencies.php
- Margens CME (oficial): cmegroup.com/CmeWS/mvc/Margins/OUTRIGHT.csv?sector=FX&exchange=CME; micros: cmegroup.com/markets/microsuite/fx.html
- Contratos de moedas B3: Ofício Circular 022/2025-VPC e "Valor dos Pontos de Contratos" (b3.com.br)
- Tarifas B3 de ações e IND/WIN e margem mínima (OC 059/2025-VPC); custos da Clear (corretora.clear.com.br/custos); aluguel na Rico (atendimento.rico.com.vc)
- Volumes: TradingView, consultado em 15/10/2026
