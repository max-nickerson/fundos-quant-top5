# Frente pf2_juros_fx — juros, câmbio e renda fixa para PF (rodada PF2)

8 estratégias novas (nenhuma em `pf/ja_testados.txt`), módulos `pf/fundos/jx_*.py` + auxiliar `pf/fundos/jx_comum.py`.
Dados em cache: `pf/dados/pf2_juros_fx/` (Tesouro Direto completo com Renda+/Educa+, vitrine de vendas, mercado diário: PTAX, EUR/USD,
IEF/IEI/SHY/TLT/BIL, FRED, juros de política BIS, DOL rolado da B3; SGS 28663). Cada fundo rodado com `python pf/rodar_pf.py um <arquivo>`;
consolidação em `pf/pesquisa/_pf2_juros_fx_junta.py` -> `pf/resultados/pf2_juros_fx.pkl`. Parâmetros escolhidos pelo **maior IR no IS**.

## Resultado (fora da amostra, excesso a.a. sobre o CDI)

| fundo | aplicável | OOS desde | 20k antes | 20k depois IR | 50k antes | 50k depois IR | IR | PBO % | P(bater 3a) % | custo 2x | t+2 | sem 10 melhores | trunc. |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| jx_td_copom (TD após abertura forte, regime Copom) | sim | 2021 | +0,24 | +0,19 | +0,24 | +0,19 | 0,11 | 7 | 59 | −0,24 | −0,24 | −0,15 | ok |
| jx_renda_educa (Renda+/Educa+ x curva NTN-B) | sim | 2025 | −0,58 | −0,57 | −0,58 | −0,57 | −0,07 | 91 | 35 | −1,43 | −1,74 | −0,89 | ok |
| jx_lft_desagio (LFT longa com deságio) | sim | 2021 | −0,15 | −0,14 | −0,21 | −0,20 | −1,27 | 17 | 1 | −0,29 | −0,14 | −0,16 | ok |
| jx_cdb_fgc (CDB banco médio, premissa) | **não** | 2021 | +1,04* | +0,87* | +1,04* | +0,87* | — | — | — | — | — | — | ok |
| jx_wdo_panico (vende WDO após pânico cambial) | sim | 2021 | **+6,77** | **+5,57** | **+2,83** | **+2,72** | 0,49 | 39 | 81 | +6,60 | +7,11 | **−2,52** | ok |
| jx_weu_wdo (EUR/USD via WEU x WDO) | sim | 2021 | −5,15 | −5,79 | −0,95 | −1,23 | 0,00 | 12 | 33 | −6,29 | −3,77 | −6,12 | ok |
| jx_treasury_cdi (T10R11 sintético) | parcial | 2021 | −3,75 | −3,70 | −3,75 | −3,70 | −1,41 | 52 | 0 | −4,50 | −3,94 | −2,80 | ok |
| jx_deb_evento (debêntures boas na onda de resgates) | parcial | 2023 | −2,22 | −2,18 | −2,71 | −2,66 | −0,16 | 61 | 28 | −4,26 | −2,56 | −2,75 | ok |

\* premissa de taxa (110% do CDI), não é backtest.

## 1. jx_td_copom — Tesouro Direto depois de abertura forte de taxa, com regime do Copom
**Tese.** Abertura de ≥ 0,5 pp em 21 pregões = stop de tesourarias/multimercados, resgate de fundos de RF, estrangeiro saindo da NTN-B
(vendedor forçado). Com o Copom subindo, a abertura é informação (segue abrindo); parado/cortando, é prêmio que devolve. O PF compra do
próprio Tesouro ao PU de compra (spread de 0,12 pp de taxa = ~1% do PU no IPCA+ 10 anos) e revende ao Tesouro.
**Implementação.** IPCA+ (NTN-B principal) ~10 anos, taxa de venda da manhã; entra em t+1; sai quando metade do choque devolve ou 63 pregões;
IR regressivo (quase tudo a 22,5%). Grade tipo × limiar × filtro (8). **O filtro do Copom ajuda nos 4 pares da grade** (IS e OOS) — é o
único "regime" com sentido econômico e ele funciona.
**Negócios.** 17 em 18 anos (14 positivos). Melhores: mar/2020 Covid (+5,7 pp; a taxa foi de 4,36% a 3,47% em 26 dias), jun/2012, set/2020
(fura-teto), fev/2013, dez/2015. Piores: 2 entradas de 1–2 dias em 13–18/mar/2020 (−2,5 e −0,4 pp: o pânico continuou) e mai/2018 (greve
dos caminhoneiros, −1,0 pp). OOS só 2 negócios (set/2023 +0,8 pp; jun/2026 +1,4 pp; set/2020 ainda é IS).
**Leitura.** Positivo, PBO 7%, mas raro (2% do tempo no OOS) e o custo de 1% do PU come metade de cada negócio: custo 2x e t+2 ficam
negativos. É um "plugin" de oportunidade, não um fundo.
**Variante pedida** ("vender NTN-B após fechamento forte e recomprar"): é carregar duration quase sempre — OOS −6,0 pp (IPCA+) e −3,3 pp
(pré) contra o CDI: é beta de juro real, e 2021/2024 destruíram.

## 2. jx_renda_educa — Renda+/Educa+ contra a NTN-B
**Pesquisa.** Há histórico: o arquivo do Tesouro Transparente traz Renda+ (8 vencimentos 2049–2084, desde jan/2023) e Educa+ (19 vencimentos
2030–2048, desde ago/2023). Calculei a duration de Macaulay do fluxo de parcelas (240 / 60 parcelas mensais reais) e o spread contra a curva
real do Tesouro na mesma duration.
**Achado.** O Tesouro precifica pela curva da NTN-B: spread mediano −0,02 pp (Renda+) e −0,01 pp (Educa+), p5–p95 de −0,22/+0,09 pp — ruído
de interpolação. O custo de compra/recompra é 0,4% (Educa+ curto) a 5% do PU (Renda+ 2079/2084). Não há prêmio de varejo; o hedge em DAP
(DV01 ~R$ 75–95/bp por contrato vs R$ 15–30/bp de R$ 20 mil no título) arredonda a zero. Os 6 negócios são beta de juro real longo
(Renda+ 2079 em 2024: −20 pp). **Reprovado por construção.**

## 3. jx_lft_desagio — LFT com deságio
**Tese.** 2020–22: Tesouro emitindo LFT recorde, bancos com limite de risco de spread vendendo; LFT longa a Selic + 0,25–0,38%.
**Resultado.** O deságio é real, mas pequeno demais: 4 negócios, contribuição de +0,005 a +0,05 pp cada; a custódia (0,20% acima de
R$ 10 mil) e a marcação (o spread abriu mais em 2021 antes de fechar) comem o carry. OOS −0,15 pp. Lição: "carry sem risco" de 0,2–0,3%
a.a. não paga custódia de PF. O caixa do fundo já deve ficar em LFT curta (isenta até R$ 10 mil), não longa.

## 4. jx_cdb_fgc — CDB de banco médio (não testável)
Não existe série pública de taxa por emissor (BCB/B3/ANBIMA; Yubb só mostra a prateleira do dia; SGS 28663 é média de mercado e acabou em
jan/2024; LF no balcão B3 vem sem taxa). O módulo é a conta: 110% do CDI por 2 anos (IR 15%) = +1,0 pp antes e +0,87 pp depois do IR por
ano. Risco não modelado: liquidação (ex.: Master, nov/2025) — FGC devolve principal + juros até a liquidação, com o dinheiro parado
1–3 meses. Com 4–5 bancos e ≤ R$ 250 mil por instituição é o prêmio mais "limpo" de PF, mas sem backtest é premissa.

## 5. jx_wdo_panico — mini-dólar vendido depois de pânico cambial (o único promissor)
**Tese.** Alta do dólar ≥ 2 desvios em 10 pregões = fluxo forçado (stop de carry, resgates de fundos EM, hedge às pressas, overhedge); o BC
reage (swaps/leilões) e o diferencial de juro passa a pagar a quem vende o futuro. Fico vendido 21 pregões, zerado 82% do tempo — oposto
do carry permanente reprovado. Filtro: não entro em pânico GLOBAL (VIX acima do p90 de 1 ano), que continua (2008, mar/2020).
**Negócios** (40; OOS 14). Melhores: abr/2020 (+27 pp com R$ 20 mil = 2,5x), mai/2022 (+17), out/2023 (+13), ago/2013 (+13), out/2025 (+8).
Piores: fev/2015 (−15: Dilma/Petrobras, o real seguiu caindo), jun/2022 (−13), ago/2008 (−10), mai/2018 (−9), nov/2024 (−9: pacote fiscal).
**Quem trouxe o retorno.** Decomposição: carry (CDI − cupom) +1,7 pp/ano no IS e +2,5 no OOS; reversão do câmbio −1,7 pp/ano no IS e
+4,6 pp/ano no OOS. Ou seja: a reversão pós-pânico só pagou em 2021–26 (Selic de 10–15%, BC com reservas e swaps); em 2008–2020
(Selic baixa, crises domésticas longas) o real continuou caindo. **IS ≈ 0 (−0,7 pp), sem os 10 melhores −2,5 pp, PBO 39%** — é carry
condicional de regime de juro alto, com cauda grande por negócio. Com R$ 20 mil, 1 WDO = 2,5x o capital (não há micro-dólar na B3).
**Próximo passo honesto:** condicionar ao juro real ex-ante alto (Selic − IPCA esperado ≥ 5%) — hipótese com sentido (o carry precisa pagar
a espera e atrai o fluxo que reverte), testar com corte novo; e reduzir para R$ 50 mil (1x).

## 6. jx_weu_wdo — euro x dólar na B3 (WEU comprado + WDO vendido)
**Pesquisa.** WEU existe: EUR 10 mil, cotação em R$/EUR 1.000, vencimento mensal, liquidação financeira (b3.com.br, "Futuro Mini de Euro").
Livro raso. Sem histórico baixado -> WEU sintético (EUR/USD Yahoo × PTAX − (CDI − BCE − 1,07 pp)); no par a PTAX quase cancela.
**Tese.** Ciclo relativo Fed × BCE (diferencial de política, BIS). **Resultado:** IR 0, OOS −5,2 pp com R$ 20 mil (1 par = 3x o capital) e
−0,95 com R$ 50 mil. O ciclo de política já está no preço; acertou 2009–10, 2019–21, 2022–23, errou 2011, 2023–24 e 2026 (−16,7 pp).
Vantagem do veículo (sem remessa/IOF, IR com compensação mensal) é real, mas não há sinal que pague 3x de alavancagem forçada.

## 7. jx_treasury_cdi — Treasury hedgeado para CDI
**Pesquisa.** Existe ETF de Treasury hedgeado na B3: **T10R11** (2025, futuros de Treasury 10 anos em reais com hedge cambial). BDRs BIYT39/
BTLT39 são sem hedge. T-bill financiado pelo CDI: com hedge rende CDI − custos (paridade coberta) e sem hedge é câmbio; pela IBKR soma IOF
1,1% + spreads e o hedge em WDO (US$ 10 mil) arredonda a zero com US$ 3,7 mil. Logo, só o prêmio de prazo hedgeado faz sentido.
**Resultado.** Sintético (IEI − T-bill − 0,30% a.a.). Regra escolhida no IS (curva 10a−3m ≥ 0,5 pp) ficou ligada 2008–2018 (beta do bull
market de bonds) e perdeu −11 pp em ago/2020–jul/2022 e −4,6 pp em 2026. OOS −3,75 pp; "sempre comprado" −4,5. Reprovado: o prêmio de
prazo americano não teve regra que o separasse do beta.

## 8. jx_deb_evento — debêntures boas na onda de resgates (lote pequeno)
**Tese.** Em ondas de resgate (Covid, Americanas), fundos vendem o que tem liquidez — papéis bons caem 2–5 pts por fluxo. Compro papel que
estava ≥ 98 (preço de crédito; IPCA+ = 100 − spread × duration para tirar o juro real), caiu ≥ 2 pts, mercado todo caindo (mediana de 21d
≤ −0,6), sem RJ; até 5 papéis; markup medido no balcão (0,40% × duration na compra).
**Negócios** (30). Melhores: Americanas fev/2023 — CCROB6 (+1,4 pp), COCE18 (+1,2), CTEE29 (+0,7): exatamente a tese. Piores: CMIN12
(−4,1 pp, nov/2025: CSN Mineração, estresse de crédito real do grupo CSN), SUMI19 (−2,6), JTEE12 (−2,5), RUMOB5 (−2,1).
**Leitura.** Os acertos são de contágio puro; os erros são crédito de verdade que o filtro "estava no par" não separa, e o carry das
incentivadas (IPCA + ~6%) fica abaixo do CDI de 13–15% enquanto espero. OOS −2,2 pp; variante DI (m 0,6, q 3) +0,65 pp OOS mas negativa no IS.

## O que deu certo e por quê
- **Vendedor forçado + quem paga a espera.** WDO pós-pânico e TD pós-abertura funcionaram quando o carry estava a favor (Selic alta no WDO;
  BC parado/cortando no TD). O filtro de regime do Copom é o resultado mais limpo da frente (melhora as 4 combinações).
- **Contágio em crédito (Americanas 2023)**: os papéis bons voltaram em 12 meses, como previsto — mas é 1 episódio.

## O que deu errado
- Prêmios "estruturais" que imaginávamos não existem ou são pequenos: Renda+/Educa+ têm preço de curva (Tesouro precifica pela NTN-B);
  deságio da LFT é menor que a custódia; prêmio de prazo dos EUA foi beta.
- Contrato grande para o capital de novo (WEU/WDO 3x, WDO 2,5x com R$ 20 mil): a variância por negócio decide o resultado.

## Bugs e cuidados
- Truncamento falhou no WDO/WEU: sem dado do DOL rolado (corte antes de 2019) o código usava série zerada em vez da sintética — corrigido em
  `jx_comum.wdo` (testes passam nos 8).
- Preços de manhã do Tesouro: sinal em t, execução no PU de t+1 (sem olhar o fechamento).
- WEU sintético (não há histórico baixado); T10R11 sintético (só existe desde 2025); CDB sem dados (premissa).
- Debêntures: preço de referência = negócio ≥ R$ 100 mil (SND); posições abertas no fim dos dados saem na última marca.

## Próximos passos
1. WDO pós-pânico com filtro de juro real ex-ante (sem reescolher em cima do OOS: novo corte 2024), e só com R$ 50 mil.
2. TD pós-abertura como sinal acoplado ao caixa do fundo (o caixa já está em Tesouro; trocar LFT por IPCA+ nesses dias custa só o spread).
3. Baixar o WEU real (COTAHIST/BVBG da B3) para medir spread e rolagem — se o par fosse usado como hedge de outra estratégia.
