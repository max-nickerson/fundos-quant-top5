# Mapa de ativos dos EUA para o varejo — variância, mineradoras e eurobonds

Pergunta: com **R$ 20 mil** (≈ US$ 3,5–4 mil) no total, pessoa física residente no Brasil, o que dá para operar de cada ativo em
Clear, Rico, IBKR (conta de não residente) e outras corretoras, e qual substituto preserva o edge. A tabela completa, ativo por ativo
e com as fontes, está em `mapa_ativos_eua.csv`. Data da pesquisa: 15/10/2026. Onde não deu para confirmar, está escrito "não confirmado".

**Dado mais sólido:** disponibilidade e taxa de aluguel na IBKR, lidas do arquivo público de short da IBKR
(`ftp2.interactivebrokers.com/usa.txt`, 15/10/2026). Níveis de preço: S&P 7.719 e VIX 16,9 (14/10/2026, `dados/`).

## Regras gerais

- **Clear e Rico** só dão acesso à B3: ações, BDRs, ETFs locais, opções de BOVA11/IBOV, WIN/WDO e (não confirmado na Clear) o micro
  S&P da B3 (WSP). Nenhuma das duas vende ativo americano a descoberto.
- **IBKR** é a única corretora de varejo acessível a brasileiros que oferece, na mesma conta, venda a descoberto de ETFs americanos,
  futuros CME/CFE e opções listadas com níveis 3–4. Para vender a descoberto é preciso conta margem (Reg T, patrimônio ≥ US$ 2 mil).
  Opção vendida descoberta exige o nível 4, que a IBKR concede pelo perfil (os critérios não são publicados); travas pedem o nível 3.
  Bonds Reg S/144A exigem 100% de margem.
- **Avenue, Nomad, Inter, C6 e XP Internacional** servem para comprar. A Avenue oferece opções (anunciadas para venda coberta) e uma
  lista de bonds brasileiros fracionados. Nenhuma dessas tem venda a descoberto ou futuros (não confirmado para todas).
- **BDR na B3:** BDRs, inclusive os de ETF, são elegíveis ao BTC (aluguel), mas não confirmamos oferta de aluguel em nenhum BDR de
  mineradora ou de metal. Na prática, na B3 eles só servem para a perna comprada.

## 1. Variância do S&P vendida (beta neutro)

**Instrumento institucional:** swap de variância OTC de 1 mês, vendido a VIX−1, com hedge de beta. Não existe no varejo.

**Melhor caminho no varejo (IBKR):**
1. **Vender 1 VXM** (mini VIX, US$ 100 × VIX, nocional ≈ US$ 1,7 mil; margem de 1/10 da do VX) e **neutralizar o beta** vendendo
   ~6–8 ações de SPY ou comprando SH. É a única venda de volatilidade "pura" que cabe na conta.
2. Alternativa sem futuros: **comprar SVXY (−0,5x) + comprar SH**, ou vender VIXY a descoberto (aluguel de 1,8% a.a.).
3. Se o grupo conseguir o nível 3: **iron condor de XSP de ~30 dias** (nocional de ≈ US$ 77 mil, risco definido de ~US$ 500 por
   condor), que é o mais próximo de "vender vol implícita de 30 dias do S&P".

**O que se perde:** o swap paga vol implícita menos vol **realizada**, com convexidade. VXM, SVXY e VIXY ganham com a **rolagem dos
futuros de VIX** (prêmio de prazo), que é parecido mas não é a mesma coisa: eles perdem mais em choques como fev/2018 e não
travam o strike de VIX−1. O condor corta a cauda, mas as asas compradas comem parte do prêmio. O teto de vega e o regime
`risco_global` do fundo são replicáveis, mas com 1 contrato não há granularidade. SPX (nocional de ≈ US$ 772 mil) e VX (≈ US$ 17 mil)
são grandes demais. Na B3 não há VIX nem BDR de ETF de VIX (não encontrado). Vender strangle de BOVA11 captura o prêmio de vol do
**Ibovespa**, que é outro ativo.

**Veredito:** **parcial**. O edge conceitual (prêmio de vol) sobrevive; o instrumento e o perfil de cauda mudam.

## 2. Mineradoras vs metal

**Melhor caminho no varejo: tudo na IBKR, em ações inteiras.** Os 11 ativos estão disponíveis e são alugáveis. Taxa anual de aluguel e
quantidade disponível em 15/10/2026:

| Ativo | Taxa | Disponível | BDR na B3 |
|---|---|---|---|
| GDX | 0,42% | >10 mi | GDXB39 |
| GDXJ | 0,55% | 1,7 mi | — (GOEX39 segue outro índice) |
| GLD | 0,43% | 7,9 mi | BIAU39 (IAU) / ABGD39 (SGOL) |
| SIL | 0,52% | 850 mil | BSIL39 |
| SLV | 0,42% | >10 mi | BSLV39 / SIVR39 |
| COPX | 0,45% | 500 mil | BCPX39 |
| CPER | 0,28% | **10 mil** | — |
| FCX | 0,41% | >10 mi | FCXO34 |
| VALE | 0,25% | >10 mi | VALE3 (ação local) |
| BHP | 0,63% | 550 mil | BHPG34 |
| RIO | 0,30% | 2,5 mi | RIOT34 |

As taxas são bem próximas da premissa do fundo (0,5% a.a. de aluguel na perna vendida).

**O que se perde:**
- **Granularidade.** Com ~US$ 3,7 mil para 6 pares (12 pernas), cada perna fica com ~US$ 300. GLD (US$ 376/ação) não cabe: use IAU.
  A IBKR compra frações, mas fração não pode ser vendida a descoberto (regra não confirmada nesta pesquisa). Por isso o hedge pelo
  beta fica arredondado.
- **CPER** tem pouco estoque para alugar (risco de recall). O micro cobre MHG (2.500 lb, nocional ≈ US$ 12 mil, margem ≈ US$ 1,7 mil)
  cabe em 1 contrato, mas distorce o beta.
- **Micro futuros não cabem:** MGC (10 oz, nocional ≈ US$ 41 mil, margem ≈ US$ 2,3–2,6 mil) e micro prata SIL (1.000 oz, nocional
  ≈ US$ 55 mil, margem ≈ US$ 5,5 mil). O contrato de 1 onça de ouro da CME existe, mas a liquidez não foi confirmada.
- **Na B3** (Clear/Rico) só dá para montar a perna comprada (BDRs e VALE3). A vendida depende de aluguel de BDR, não confirmado e
  provavelmente indisponível. Dá para operar só o par VALE3 × BHPG34/RIOT34, e ainda assim sem confirmar o aluguel do BDR.

**Veredito:** **sim na IBKR**, que preserva o edge: os ativos são os mesmos, com aluguel barato. O que limita é o capital por perna.
**Não** em Clear/Rico/Avenue/Nomad/Inter.

## 3. Eurobonds high yield Brasil com hedge

**Bond por bond:** 7 dos 14 têm caminho de varejo.
- Na lista de bonds BR da **Avenue** (out/2025) aparecem, com mínimo de 5 unidades (provável US$ 5 mil; a Avenue fraciona o lote):
  **Movida 2031, Simpar 2031, BRF 2050, Natura 2029, Raízen 2034**, além da gêmea Reg S da **Raízen 2032**. A versão 144A dessa
  última é só para QIB.
- **Petrobras 2115** é registrado na SEC, com denominação de US$ 2 mil + múltiplos de US$ 1 mil (confirmado). É provável que apareça
  na IBKR (não confirmado).
- **Hidrovias** (65% recomprado em jun/2025), **B2W/Americanas** (reestruturado na recuperação judicial), **Acelen, Açu, Globo e
  Braskem Idesa** (emissor mexicano): nenhuma oferta de varejo encontrada. O mínimo é provavelmente o padrão Reg S/144A de US$ 200 mil
  (não confirmado por bond).

**O que se perde:** com US$ 3,7 mil cabe **no máximo 1 bond** de US$ 5 mil, e nem isso. O fundo carrega 15 bonds com **hedge de DOL
e de Treasury**. O WDO (≈ US$ 10 mil de nocional) é maior que a carteira e não há como fazer hedge de Treasury nesse tamanho, então o
bond direto vira aposta em dólar e em crédito de um emissor só. O markup do dealer de varejo é alto (não confirmado).

**Substitutos:**
- **HYBR11** (B3, Nu): 70% HYG + 30% soberano BR, com hedge em mini dólar. É o **formato** certo (HY em dólar trazido para
  CDI + spread, sem IOF e a partir de 1 cota), mas o crédito é **HY americano**, e o PL é pequeno (≈ R$ 15 mi em fev/2026).
- **EMHY / HYEM** (IBKR/Avenue): spread HY emergente, mas o Brasil pesa só ~5% (EMHY: 3–8% conforme a fonte; HYEM: 4,97%) e não há
  hedge cambial.
- **CEMB / EMB:** IG e soberano, Brasil ~5%. Não preservam o edge.
- **Fundos de bonds de varejo** (XP, BTG, Itaú): existem, mas **não confirmamos** nomes e aplicação mínima. Fundos de "bonds Brasil"
  costumam ser para investidor qualificado.

**Veredito:** **não** dá para replicar com R$ 20 mil. O mais próximo em espírito é HYBR11 (**parcial**: mesmo formato, outro crédito).
Para o crédito brasileiro, a única opção é 1 bond na Avenue sem hedge.

## Fontes principais
- IBKR, arquivo de aluguel: ftp://ftp2.interactivebrokers.com/usa.txt · níveis de opção: https://www.ibkrguides.com/kb/options-levels-1-4.htm · comissões: https://www.interactivebrokers.com/en/pricing/commissions-home.php
- Cboe Mini VIX: https://cdn.cboe.com/resources/futures/mini-vix-fact-sheet.pdf · XSP: https://www.cboe.com/tradable_products/sp_500/mini_spx_options/specifications
- CME micro metais: https://www.cmegroup.com/markets/microsuite/metals.html · margens: https://brokerchooser.com/best-brokers/lowest-margin-brokers-for-trading-micro-gold-futures · MES: https://lpfutures.com/micro-emini-mes-futures-contract/
- B3 BDR de ETF: https://finservices.b3.com.br/en/bdr-on-etf/program?delta=60 · BlackRock BDRs: https://www.blackrock.com/br/products/bdr · WSP: https://www.b3.com.br/pt_br/produtos-e-servicos/negociacao/renda-variavel/microcontrato-futuro-de-s-p-500.htm
- Avenue bonds BR: https://avenue.us/assets/pdf/bonds_list_br.pdf · Avenue opções: https://avenue.us/opcoes/
- Petrobras 2115: https://bondblox.com/bond-market/Petrobras-Global-Finance-B.V.-US71647NAN93 · Hidrovias tender: https://finance.yahoo.com/news/hidrovias-international-finance-r-l-012800666.html
- HYBR11: https://nuasset-files.mziq.com/fundos/arquivos/site/hgbr11/material-comercial/hgbr11-pt-apresentacao-latest.pdf · HYEM: https://www.vaneck.com/us/en/investments/emerging-markets-high-yield-bond-etf-hyem-fact-sheet.pdf · CEMB: https://www.blackrock.com/us/individual/products/239525/ishares-emerging-markets-corporate-bond-etf
