# PF3 — frente internacional B: vencedores institucionais que morreram no varejo, refeitos com a conta em dólar v2

Pergunta: as estratégias institucionais que o varejo matou "por causa do câmbio/da conta" voltam a viver quando o dinheiro MORA na IBKR
em SGOV, só a 1ª remessa paga IOF e o saldo é hedgeado com WDO (`pf.conta_usd`)?

**Resposta curta: não por causa da conta.** A conta v2 não cria edge, e com R$ 20–50 mil ela custa caro. Manter R$ 5/10/15 mil fora custa
**−2,3/−4,5/−6,8 pp a.a.** do fundo no OOS 2021+, já que o CDI de ~11% vira T-bill de ~4–5% e o real se valorizou. O hedge com WDO
arredonda para **zero contrato** em todo sleeve abaixo de ~R$ 27 mil (US$ 5 mil). No único caso em que entra 1 WDO (R$ 50 mil com
R$ 37,5 mil fora), a conta sozinha dá +1,6 pp. Isso é **sobre-hedge** (vendido em US$ 10 mil contra US$ 7 mil): um short de dólar que
carrega CDI − cupom. Não é a estratégia. Para separar as duas coisas, a coluna que importa é **"estratégia sobre a conta"**: o excesso
com a estratégia menos o excesso da mesma conta sem nenhuma posição.

| fundo (`pf/fundos/`) | institucional | o que o livro em US$ entrega sobre a conta (pp a.a. do fundo, OOS) | veredito |
|---|---|---|---|
| `mineradoras_v2` | +11,7 | −0,3 a +1,1 (≈ 0) | morre na execução (custos, Reg T, ações inteiras), não no câmbio |
| `variancia_v2` (SVXY + SH) | +7,6 | 0,0 a +0,7 (≈ 0) | o substituto não carrega o prêmio do swap de variância |
| `credito_em_v2` (HYEM no pânico) | +3,6 | ≈ 0 (4 negócios OOS) | pânico com âncora: poucos eventos, nada fora da amostra |
| `carry_g10_v2` (micro FX) | — | **+5,8 (20k) / +2,7 (50k)** | o livro rende, mas é 1 negócio (iene vendido 2023–24) e PBO 83% |
| `eurex_panico_v2` (FSXE) | — | **+3,8** | rende, mas são 10 negócios OOS e ago/2024 é metade (auditoria PF2) |

## Tabela capital × sleeve × hedge (OOS 2021+, pp a.a. vs CDI; depois do IR vs CDI líquido)

Arquivo completo: `pf/resultados/pf3_internacional_B_tabela.csv` (gerado por `pf/pesquisa/_pf3B_tabelas.py`). Com hedge "inteiro" o
resultado é igual a "nenhum" em todos os sleeves, menos R$ 50 mil com R$ 25 mil fora (0 ou 1 WDO conforme o câmbio, média 0,14) e
R$ 50 mil com R$ 37,5 mil fora (1 WDO). Formato: **antes / depois do IR**.

| fundo | 20k·5k | 20k·10k | 20k·15k | 50k·12,5k | 50k·25k nenhum | 50k·25k inteiro | 50k·37,5k nenhum | 50k·37,5k inteiro | margem* |
|---|---|---|---|---|---|---|---|---|---|
| só a conta (sem estratégia) | −2,3 / −1,9 | −4,5 / −3,8 | −6,8 / −5,8 | −2,3 / −1,9 | −4,5 / −3,8 | −8,5 / −7,8 | −6,8 / −5,8 | +1,6 / +2,3 | — |
| mineradoras_v2 | −2,3 / −1,9 | −4,3 / −3,7 | −7,1 / −6,7 | −1,2 / −1,0 | −4,8 / −4,3 | −8,2 / −7,7 | −7,1 / −6,7 | +1,4 / +1,7 | — |
| variancia_v2 | −1,6 / −1,3 | −4,5 / −3,9 | −6,8 / −6,0 | −2,3 / −2,0 | −4,4 / −3,8 | −8,0 / −7,4 | −6,6 / −5,8 | +1,7 / +2,4 | — |
| credito_em_v2 | −2,3 / −1,9 | −4,5 / −3,8 | −6,8 / −5,8 | −2,3 / −1,9 | −4,5 / −3,8 | −8,5 / −7,8 | −6,8 / −5,8 | +1,5 / +2,3 | — |
| carry_g10_v2 | **+3,5 / +2,4** | +1,1 / +0,2 | −1,4 / −2,0 | +0,4 / +0,2 | −1,9 / −1,8 | −4,6 / −4,6 | −4,2 / −3,9 | +4,4 / +4,5 | 20k: +3,5 / +2,4; 50k (R$ 5 mil): +1,8 / +1,4 |
| eurex_panico_v2 | **+1,5 / +1,6** | −0,7 / −0,7 | −3,1 / −2,9 | +1,5 / +1,7 | −0,8 / −0,6 | −4,9 / −4,7 | −3,1 / −2,9 | +5,4 / +5,5 | 20k: +1,5 / +1,6; 50k (R$ 7,5 mil): +2,4 / +2,5 |

\* "margem" = sleeve igual à margem necessária com folga, como pedido para os futuros: R$ 5 mil para 1 par de micro FX; R$ 5 mil
(20k) / R$ 7,5 mil (50k, até 2 FSXE em 2021) para o Euro STOXX.
As colunas 50k·37,5k inteiro parecem boas, mas +1,6 pp delas é a própria conta sobre-hedgeada (aposta vendida em dólar). Não conte isso
como estratégia.

Baterias (padrão do BRIEF: sleeve = metade do capital, hedge inteiro; R$ 20 mil): `pf/resultados/pf3_internacional_B_baterias.csv`.

| fundo | OOS 20k / 50k | depois do IR 20k / 50k | IR | PBO | P(bater 3a) | custo 2x | t+2 | sem 10 melhores | truncamento |
|---|---|---|---|---|---|---|---|---|---|
| mineradoras_v2 | −4,3 / −8,2 | −3,7 / −7,7 | −0,57 | 72% | 12% | −4,5 | −4,4 | −4,5 | ok |
| variancia_v2 | −4,5 / −8,0 | −3,9 / −7,4 | −0,57 | 52% | 13% | −4,9 | −3,8 | −8,2 | ok |
| credito_em_v2 | −4,5 / −8,5 | −3,8 / −7,8 | −0,59 | 80% | 10% | −4,6 | −4,5 | −4,6 | ok |
| carry_g10_v2 | +1,1 / −4,6 | +0,2 / −4,6 | 0,15 | 83% | 53% | −1,4 | +0,1 | −21,9 | ok |
| eurex_panico_v2 | −0,7 / −4,9 | −0,7 / −4,7 | −0,01 | 20% | 44% | −0,9 | +0,5 | −4,5 | ok |

Melhor configuração de cada um que ainda vale olhar: carry com R$ 20 mil e R$ 5 mil fora tem IS +2,9, OOS +3,5, pior queda −29%,
vol 18%, custo 2x +0,8 e t+2 +2,1. Eurex com R$ 20 mil e R$ 5 mil fora tem IS +2,8, OOS +1,5, pior queda −25%, custo 2x +1,4 e
t+2 +2,8. Com R$ 50 mil e R$ 7,5 mil fora: OOS +2,4, pior queda −33%.

## 1. Mineradoras vs metal (`mineradoras_v2.py`)
**Implementação:** usa o sinal do institucional e o motor de pares PF (`_rev_pares_pf.py`) sem alterá-los. Todas as pernas ficam em
ETF/ação na IBKR. A ponta vendida é em ações inteiras, com aluguel do arquivo de short da IBKR, comissão mínima de US$ 0,35, Reg T 50%
e US$ 2 mil mínimos para vender a descoberto. O tamanho do par segue o risco do fundo, mas o dinheiro Reg T tem que caber em 95% do
sleeve; se não couber, o par não abre. A conta antiga do motor fica desligada e é trocada pela `conta_usd`. O livro vai em excesso do
T-bill: a parte comprada não fica em SGOV.

**Resultado:** o livro ganha ≈ US$ 30–80 por ano. Com R$ 10 mil fora (US$ 1,85 mil < US$ 2 mil) não há venda a descoberto, e só 6
negócios abrem no OOS. Com R$ 37,5 mil abrem 144, mas 343 "não couberam". Decomposição com R$ 50 mil e R$ 37,5 mil fora:
- execução institucional (validação: frações, sem custos, todos os pares): **+9,7 pp OOS**;
- execução PF com custo zero: estratégia ≈ +2,3 pp sobre a conta;
- com custos: −0,2 pp.

**Por que morreu:** o tamanho fica fixo na entrada e o Reg T limita a capacidade. Cada um dos 144 negócios paga spread + comissão +
aluguel nas duas pernas, cerca de 2,5 pp a.a. de R$ 50 mil. VALE x BHP/RIO e GDXJ x GDX perdem. **Não é câmbio.** A conta v2 não salva.

## 2. Variância / prêmio de vol com beta neutro (`variancia_v2.py`)
**Implementação:** é a simulação diária da conta de `variancia_varejo.py` (SVXY comprado com frações + SH no beta, vol-alvo 8% do fundo,
teto de choque de fev/2018, regime risco_global, banda de 50%, chamada de margem). A diferença é que a conta tem o tamanho do sleeve e
o P&L entra na `conta_usd` em excesso do T-bill.

**Resultado:** sobre a conta, +0,7 pp (R$ 5 mil fora) e ≈ 0 nos demais. No acumulado, SVXY +44 pp e hedge S&P −26 pp. O "+0,7 pp com
hedge" do varejo antigo era o efeito de tirar o câmbio e o CDI − T-bill de cima de 30% do capital, não prêmio de vol. A validação
institucional do varejo já mostrava SVXY ≈ 0 em escala: futuro de VIX com hedge de beta não carrega o prêmio de variância implícita −
realizada do swap. **Morre no instrumento, não na conta.**

## 3. Crédito EM high yield via ETF, comprado no pânico com âncora (`credito_em_v2.py`)
**Tese de mesa:** fundos de EM/HY com resgate diário vendem o que tem liquidez (o ETF) quando o fluxo vira. Quem compra sem pressa
recebe o prêmio de liquidez.
- **Mecanismo 2 (âncora):** a queda tem que ser de crédito. Usa retorno do ETF − beta × IEF, com beta de 1 ano em retornos de 5 dias,
  sempre com o passado. Além disso, o "spread" do ETF (dividendos de 12 meses / preço − Treasury de 5 anos) tem que estar no quintil
  de cima do ano.
- **Mecanismo 3 (magnitude):** entra se a queda de crédito em 10 dias passar de k desvios (k = 1,5 ou 2,5). Segura H dias.
- Opcional: vender IEF em ações inteiras para ficar só com o spread. Os dados são de 2012+, então o corte é 2021.

**Premissa corrigida:** os dividendos do HYEM pagos a brasileiro (sem tratado) sofrem **30% de retenção nos EUA**. A isenção do IRC
871(k) só cobre juro de fonte americana. O crédito no IR brasileiro não foi modelado, o que é conservador. O varejo antigo ignorava isso.

**Resultado:**
- IS 2013–20: +1 a +3 pp sobre a conta, escolhido k = 1,5 e H = 84.
- OOS: 4 negócios. 2022-03 dá −4,2 pp do capital (comprou o 1º pânico do ciclo de alta de juros); 2025-04 dá +3,1. Estratégia sobre a
  conta ≈ 0.
- A âncora funciona como filtro: "só magnitude" fica IS +4,0 / OOS −5,2, contra IS +3,4 / OOS −4,5 com âncora (R$ 20 mil, R$ 10 mil
  fora). Mas há poucos eventos.
- k = 2,5 (evento maior) não melhorou: o mecanismo 3 não se confirma aqui.
- dur = True quase não muda nada: o beta do HYEM ao IEF em estresse vai a ≈ 0, porque crédito e juro andam em sentidos opostos, e o
  short de IEF arredonda para 0.
- Carregar sempre (o institucional), com R$ 50 mil e R$ 37,5 mil fora e 1 WDO: OOS −4,4 (−1,5 sem retenção), ou seja, −6 pp sobre a
  conta. 2022 destrói o carry de HY.

O "+4,0 com hedge" do varejo vinha de um OOS 2024+ sem 2022 e sem retenção.

## 4. Micro FX G10 / carry (`carry_g10_v2.py`) e micro Euro STOXX no pânico (`eurex_panico_v2.py`)
**Implementação:** sinal e contratos idênticos a `cme_carry_g10` e `fu_eurex_micro`. Só a margem fica fora (sleeve "margem"). Se a
margem exigida passar de 90% do saldo do mês, os contratos são cortados (inteiros). O P&L dos futuros já é excesso do juro.

**Carry: o livro é o melhor da frente (+5,6 a +5,8 pp sobre a conta com R$ 20 mil)**, mas:
- é 1 contrato por perna, de 2–4x o capital (vol 18%, pior queda −29%);
- quem trouxe o retorno foi **iene vendido** (MJY +84 pp acumulados; 1 negócio de 2023-03 a 2024-07 = +47 pp). O regime saiu em
  30/07/2024, antes do desmonte de 05/08;
- franco vendido +45; AUD/CAD/GBP comprados −59;
- PBO 83%, sem os 10 melhores −22, e a grade OOS é dominada por variantes que o IS não escolheria.

O negócio é real: o comprador de proteção paga carry e o carry desmonta em crise. Mas com R$ 20 mil é uma aposta concentrada no
diferencial do iene, não um livro diversificado.

**Eurex pânico (+3,8 pp sobre a conta):** são 10 negócios OOS. Ago/2024 vale +8 pp e é a melhor. A ressalva da auditoria PF2 continua:
sem os 10 melhores dá −4,5.

**A conta v2 ajuda esses dois** porque o P&L deixa de ir e voltar todo mês com IOF e a margem rende T-bill. Mas o ganho só sobra com o
sleeve mínimo (R$ 5 mil). Cada R$ 5 mil a mais lá fora custa ~2,3 pp com R$ 20 mil, e o WDO não hedgeia saldos abaixo de ~US$ 5 mil.

## O que deu certo e por quê
- Separar "conta" de "estratégia" mostrou que nenhuma das três institucionais morreu pelo câmbio. Mineradoras morreu na execução de
  varejo; variância, no instrumento; crédito EM, em 2022 e na retenção americana.
- A conta v2 melhora os futuros (margem pequena, P&L sem remessa mensal). O sleeve ótimo é sempre o mínimo que cobre a margem.

## O que deu errado / riscos
- O hedge com WDO é binário (US$ 10 mil). Com R$ 25 mil fora (US$ 4,6 mil), 1 WDO aparece em alguns meses e a conta perde −8,5 pp
  (sobre-hedge em 2024, com o dólar subindo). Só há hedge decente com o sleeve perto de múltiplos de US$ 10 mil (≥ R$ 55 mil fora).
- O carry G10 depende de 1–2 negócios em iene. Eurex: 10 negócios. Crédito EM: 4 negócios. Nenhum passa no "sem os 10 melhores".

## Bugs / premissas anotadas nos módulos
- `pf.conta_usd` credita T-bill sobre o saldo inteiro, então os livros entram em excesso do T-bill. Na mineradora, o T-bill da parte
  comprada é subtraído; a venda a descoberto não rende juro (conta < US$ 100 mil).
- `_rev_pares_pf.motor` monkeypatcha (só durante a chamada) `pf.custo_conta_exterior` → 0 e `TETO_CAIXA` → 0,95 × sleeve / capital.
  Os arquivos não foram alterados.
- `variancia_varejo._simula` multiplica "exterior" pela alavancagem. Aqui é passado sleeve / capital / alavancagem para manter o sleeve
  fixo.
- Retenção de 30% em dividendos de ETF americano: nova premissa (variante retencao = 0 ≈ UCITS irlandês, não verificado).

## Próximos passos
1. Carry G10 com o sleeve mínimo, exigindo 2 pares (diversificar o iene) só com R$ 50 mil, e medir a perda num desmonte tipo ago/2024
   sem o filtro de regime.
2. Futuros com conta v2 juntos (carry + Eurex + outros micros) dividindo o MESMO sleeve de R$ 5 mil: a margem é compartilhada e o custo
   da conta é pago uma vez só.
3. Crédito EM: testar UCITS de acumulação (sem retenção) e um gatilho de fluxo (desconto do ETF ao NAV) como âncora mais direta.
