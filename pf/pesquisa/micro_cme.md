# Frente micro_cme: 7 fundos com futuros micro da CME/Cboe via IBKR (só a margem vai para fora)

Código: `pf/fundos/cme_*.py` (peças comuns em `cme_comum.py`, bateria em `cme_rodar.py`). Dados: `pf/dados/micro_cme/`.
Resultados: `pf/resultados/micro_cme.pkl` (lista de dicts: nome, `excesso 20k`, `excesso 50k`, `metricas`, e para `20k`/`50k` tudo da bateria
resumido) e `micro_cme_<fundo>.pkl`. Rodar: `python pf/fundos/cme_rodar.py` (~11 min em paralelo; tendência é o mais lento).

## Como o dinheiro se move (igual para os 7)
- Capital em R$ no CDI (Tesouro Selic). Na IBKR fica só a **margem inicial x folga** (1,5x o maior mês anterior; 2x em VXM e cripto),
  via `pf.custo_conta_exterior`: esse saldo perde o CDI, fica exposto ao dólar e paga IOF+spread a cada ajuste.
- O P&L dos futuros é liquidado em R$ todo mês (perda: remessa com IOF 1,1% + 0,5%; ganho volta com 0,38% + 0,5%) — conservador.
- Contratos INTEIROS sempre. Custo por lado = comissão IBKR + taxas + meio spread (1 tick; 2 ticks em micro FX e VXM). Rolagem: 2 lados por
  contrato em cada vencimento (VXM: nas datas reais).
- IR: P&L dos futuros 15% ao ano com compensação (Lei 14.754/2023); variação cambial do saldo não remunerado isenta; CDI perdido entra x0,85;
  comparado ao CDI depois de 15%.
- Antes do corte OOS os micros lançados depois (MES/MNQ/M2K 2019, VXM 2020, MBT/MHG/MCL/10Y/2YY 2021, MET dez/2021, 1OZ jan/2023) são
  simulados com o mesmo subjacente (hipotético). **Depois do corte o fundo só negocia o contrato a partir do lançamento.**

## Saltos de rolagem — como foram tratados
Nenhum retorno vem do contínuo do Yahoo. Ações/metais/petróleo: ETF com proventos (SPY, QQQ, IWM, GLD, SLV, CPER, USO) − T-bill + taxa do
ETF; o nível do índice/futuro (^GSPC, GC=F...) só dá o TAMANHO. Moedas: spot + diferencial de juros de política do BIS (é o que o futuro paga
pela paridade coberta). Yield: Δ yield do FRED x US$ 10/bp − carregamento (yield − Fed funds)/duração. VIX: o próprio vencimento VX da Cboe
carregado até 5 pregões antes do vencimento. Cripto: spot − base anualizada (futuro trimestral da Binance, mesmo horário de fechamento do
spot, +1 p.p.; o BTC=F do Yahoo fecha 4h antes do spot e gera ±2%/dia de ruído — inútil para medir base de 0,3-1%/mês).

## Resultado (fora da amostra; corte 2021-01 — cripto 2023-01). pp a.a. vs CDI; "depois" = vs CDI líquido, depois do IR

| Fundo | Aplicável? | R$ 20 mil antes / depois | R$ 50 mil antes / depois | IR OOS 20k / 50k | PBO 20k / 50k | P(bater 3a) 20k / 50k |
|---|---|---|---|---|---|---|
| VXM vendido (prêmio do futuro de VIX) | sim, com cauda | **+19,8 / +13,1** | **+21,7 / +15,0** | 0,59 / 0,61 | 15% / 0% | 80% / 77% |
| Tendência multiativos (contratos inteiros) | sim, concentrado | +4,6 / +3,1 | **+8,3 / +6,6** | 0,29 / 0,41 | 85% / 13% | 62% / 68% |
| Metais: sazonal do ouro com 1OZ (pares não cabem) | sim (só o sazonal) | +5,4 / +4,2 | +7,8 / +6,3 | 0,45 / 0,75 | 50% / 29% | 78% / 89% |
| Carry G10 micro FX (1 contrato/perna) | sim | +1,0 / +0,3 | +0,7 / +0,5 | 0,14 / 0,13 | 69% / 72% | 53% / 56% |
| Micro BTC/ETH: tendência pagando a base | sim (só MET) | −1,0 / −0,9 | −2,0 / −1,7 | 0,00 / −0,05 | 46% / 32% | 44% / 41% |
| Juros EUA pelo ciclo do Fed (2YY) | sim | −2,1 / −3,0 | −2,6 / −3,3 | −0,01 / −0,11 | 67% / 64% | 41% / 36% |
| Sazonalidade de índice (MES virada do mês) | **não** (10x o capital) | −8,8 / −8,9 | −3,8 / −3,8 | −0,16 / −0,04 | 70% / 9% | 31% / 39% |

Robustez (R$ 20 mil): truncamento passou nos 7 (diferença 0). Sharpe OOS todos < 0,8 (nenhum alarme de bug > 1,5).

| Fundo | vol / pior queda OOS | leque p5/p50/p95 | custo 2x | t+2 | placebo p | walk-forward | sem 10 melhores | saldo médio IBKR |
|---|---|---|---|---|---|---|---|---|
| VXM | 48% / −57% | +15,1 / +19,8 / +19,8 | +14,0 | +19,8 | 0,06 | +19,8 | −15,2 | R$ 11,2 mil |
| Tendência | 23% / −30% | −5,0 / +7,4 / +20,3 | +0,6 | +1,7 | 0,10 | +5,3 | −24,3 | R$ 4,7 mil |
| Metais (sazonal) | 12% / −18% | +4,6 / +13,4 / +14,8 | +4,6 | +7,4 | 0,20 | +3,3 | −0,7 | R$ 1,0 mil |
| Carry G10 | 19% / −32% | −0,4 / +0,9 / +1,3 | −2,0 | −0,2 | 0,19 | +1,0 | −22,0 | R$ 3,9 mil |
| Cripto | 13% / −21% | −7,3 / +0,4 / +16,7 | −3,5 | −1,6 | 0,12 | +1,2 | −8,6 | R$ 4,0 mil |
| Juros Fed | 18% / −24% | −5,6 / −3,1 / −0,2 | −3,3 | −3,7 | 0,60 | −2,1 | −12,6 | R$ 1,2 mil |
| Sazonal índice | 27% / −45% | −21,6 / −8,9 / −1,7 | −9,9 | +3,9 | 0,72 | −7,4 | −28,0 | R$ 6,7 mil |

Alavancagem (OOS pp, R$ 20 mil): VXM 1x +19,8 / 1,5x +7,8 / 2x −3,6 (queda −90%: quebra); tendência +4,6 / −1,4 / +7,5 (quedas −30/−54/−59%);
metais +5,4 / +11,8 / +13,8; carry 1 contrato +1,0 / 2 contratos −1,8; cripto −1,0 / −3,8 / −8,0; juros −2,1 / −2,5 / −4,5. 5x não é viável em nenhum.

## Fundo a fundo

### 1. VXM vendido — `cme_vxm.py` (o único com prêmio de verdade, e com cauda de verdade)
**Tese.** O futuro de VIX embute prêmio: hedgers de carteira, ETNs (VXX/UVXY rolam comprando o 2º vencimento todo dia) e mesas vendidas em
opção pagam por vega; o futuro desce a curva até o VIX à vista. Vender 1 VXM (US$ 100 x VIX) rende ~1-3 pontos/mês em mercado calmo.
**Implementação.** Contratos = piso(perda_max x capital / (choque x US$ 100 x PTAX)), choque 10 pontos (1º venc.) / 7 (2º). Grade: regime
{nenhum, contango, contango+VVIX<p80 + stop de 5 dias} x venc {1,2} x perda_max {25%, 40%}. **No IS os filtros pioraram** (melhor filtro +7,5
IS vs +11,7 sem filtro): eles saem DEPOIS do pico e perdem a descida da curva — que é onde o prêmio é mais gordo. Escolhido: sempre vendido
no 1º vencimento, perda_max 40% -> **1 contrato com R$ 20 mil** (2 a 4 nos anos de dólar a R$ 2-4), 3 com R$ 50 mil.
**Quem trouxe o retorno.** Melhores: vendido em 09/04/2025 (dia do pico das tarifas, VX ~35) até 13/05 +50 pp; mar/2021 +26; mar/2022 +21;
mai, out/2022 +17/+16; mai/2023 +15. Piores: 11/03-08/04/2025 −47 pp (as tarifas); fev-mar/2022 (Ucrânia) −28; fev-mar/2025 −22; fev-mar/2026
−15; abr/2022 −14; jul-ago/2024 (iene) −11. Ano a ano: 2021 +97, 2022 −8, 2023 +58, 2024 +3, 2025 −11, 2026 +3.
**Por que funciona e o que preocupa.** O retorno é o prêmio de seguro (placebo p 0,06 — estar posicionado é o que paga), mas com R$ 20 mil 1
contrato é ~R$ 10 mil de nocional com vol de ~90%: vol do fundo 48%, queda de −57%, 1,5x já leva a −90%. 2021 (+97 pp) sozinho explica boa
parte da média. A grade mostra o problema do inteiro: perda_max 25% (1 contrato a menos em vários anos) dá −6,3 IS / +3,2 OOS. PBO baixo, mas o
número é uma loteria de tamanho + de 1 ano bom. Nos anos com choque (2022, 2025) o fundo perde.

### 2. Tendência multiativos — `cme_tendencia.py`
**Tese.** Hedgers que rolam por calendário, BC em passos de 25 bp, pensões que rebalanceiam devagar: preços em tendência. 11 micros
(MES, MNQ, M2K, MGC, 1OZ, SIL, MHG, MCL, M6E, MJY, 10Y). Sinal = retorno em excesso de `janela` / vol; toda sexta aloco contrato a contrato,
na ordem do |sinal|, enquanto a vol ex-ante da carteira (vol de 1 contrato em R$ + correlação de 1 ano) couber em alvo x capital.
**Realidade do inteiro.** Com R$ 20 mil o algoritmo carrega 1-4 contratos dos micros pequenos (1OZ, MJY, 10Y, M6E); MES/MNQ só entram quando a
vol cai. Melhores: 1OZ comprado jan-nov/2025 +43 pp; MJY vendido dez/2021-jun/2022 (Fed x BoJ) +42; 1OZ fev/2024-jan/2025 +26; 10Y comprado
em yield ago-out/2026 +12. Piores: MJY nov/2022 (CPI) −12; 10Y fev-mar/2025 −11; M6E 2021 −10; 1OZ vendido fev-abr/2023 −9.
**Leitura.** Com R$ 50 mil fica diversificado (163 negócios OOS, 2022 +92 pp) e o PBO cai para 13%; com R$ 20 mil o PBO é 85% e o leque vai
de −5 a +20: é um fundo de 2-3 apostas. O retorno vem de ouro e iene (as duas grandes tendências macro de 2022-2025), não do "momentum".

### 3. Metais — `cme_metais.py` (os pares não cabem; sobrou o sazonal do ouro)
Pares: 1 SIL ≈ US$ 56 mil e 1 MHG ≈ US$ 16 mil por perna: com R$ 20-50 mil o nº de pares arredonda para 0 no OOS (ouro/prata) ou só aparece com
vol-alvo de 25% (cobre/ouro, +6 a +8 OOS com pouquíssimos negócios). No IS (dólar a R$ 2-3) ouro/prata operou e perdeu. Escolhido no IS:
**ouro comprado de agosto a fevereiro com 1OZ** (temporada de casamentos/festivais na Índia + compras antes do Ano Novo Chinês). Mas o IS do
sazonal foi só +0,5 (comparação: ouro sempre comprado −2,0 IS / ago-fev +0,4 / mar-jul −3,0). O OOS (+5,4) é ouro comprado em 2024-2026:
ago-dez/2025 +27 pp, ago/2026 +12, ago/2024-fev/2025 +9. Só 10 negócios, e 1OZ só existe desde 2023. **É beta de ouro com calendário**,
não um edge comprovado — mas é o único jeito de ter ouro em contrato que cabe em R$ 20 mil (≈ US$ 4 mil, margem ~US$ 300).

### 4. Carry G10 — `cme_carry_g10.py`
Comprado no micro da moeda de maior juro (BIS), vendido no de menor, 1 contrato por perna, fora quando `regime_risco_global` < 2/3. O
excesso veio quase todo de **vender iene e franco** (MJY +84 pp acumulado, MSF +45): MJY vendido mar/2023-jul/2024 +47 pp. Perdeu em libra,
dólar canadense e australiano comprados, e no desmonte de out/2022-mar/2023 (MJY −21). 2021 zerado (nenhum par com diferencial ≥ 1,5 p.p.).
Cada perna é 2-4x o capital, então com R$ 20 mil é vol de 19% para ganhar +1 pp. PBO 69-72%, custo 2x vira −2,0. O carry institucional (+7 pp)
não chega: faltam as emergentes (sem micro) e o ganho dos cruzados (AUD/JPY) com 1 contrato/perna fica sem diversificação.

### 5. Micro BTC/ETH — `cme_cripto.py`
Tendência de 50 dias, só comprado, pulando quando a base > 25% a.a. Com R$ 20 mil só cabe MET (0,1 ETH ≈ US$ 240); MBT (≈ US$ 8 mil) só com
R$ 50 mil. Melhores: MET out/2023-mar/2024 +27 pp (ETF spot), ago-out/2026 +11. Piores: jul-ago/2024 −10 e várias falsas partidas. A base
paga (5-13% a.a.) come o que a tendência dá; vendido (lado "ls") foi pior no IS e no OOS. −1 pp.

### 6. Juros pelo ciclo do Fed — `cme_juros_fed.py`
Comprado em yield (vendido no título) quando o Fed sobe ≥ 25 bp em 6 meses e o 2 anos está acima da média de 63 dias; o contrário nos cortes.
2022 deu +39 pp (2YY comprado em yield mar-dez/2022, três negócios, +45); depois perdeu todo ano (2023-2026: −10 a −13) — ciclo de alta virou platô
e cortes com o 2 anos subindo (set-out/2024 −12 pp). IS +6,3 vinha de 2015-2019. PBO 67%, placebo p 0,60: o "timing" não é melhor que acaso.

### 7. Sazonalidade de índice — `cme_sazonal.py` (não aplicável)
Virada do mês (último pregão + 3 primeiros), véspera de feriado NYSE e contra o rebalanceamento trimestral de pensões. O IS escolheu MES
(1 contrato ≈ R$ 200 mil = 10x R$ 20 mil): cada virada vira aposta alavancada de 4-5 dias. 31/07-05/08/2024 (desmonte do iene) −36 pp num
negócio; nov/2023 +24. Com M2K (cabe melhor) o IS já era negativo. O efeito virada do mês está fraco no S&P desde 2021.

## O que deu certo e por quê
1. **Vender o prêmio do futuro de VIX** é o único negócio aqui em que o dinheiro vem de alguém que paga para se proteger (ETNs/hedgers). O
   tamanho mínimo (1 VXM) é tolerável em R$ 20 mil, mas fica no limite: a pior queda (−57%) é a de um fundo alavancado.
2. **Tendência com R$ 50 mil**: com 3-6 posições o fundo capturou as duas tendências macro do período (Fed x BoJ no iene, ouro 2024-26).
3. **1OZ e MET** são os contratos que tornam "conta pequena" possível: US$ 4 mil e US$ 240 de nocional.

## O que deu errado
- **Tamanho do contrato é o problema central**: MES ≈ R$ 200 mil, MNQ ≈ R$ 310 mil, SIL ≈ R$ 300 mil, M6E ≈ R$ 75 mil contra R$ 20 mil. Os pares de
  metais e a sazonalidade com MES são inviáveis; carry e tendência ficam concentrados.
- **Custo da conta lá fora**: o saldo na IBKR (R$ 1-11 mil) perde CDI de 10-14% e paga IOF; as remessas mensais do P&L custam 1-1,6% do que
  transita. Em VXM o saldo médio é R$ 11 mil (55% do capital).
- **Filtros de regime em venda de vol**: pioraram no IS e no OOS; o prêmio está justamente depois dos picos.
- Juros pelo Fed: um ano bom (2022) e quatro ruins; o mercado de 2 anos precifica o Fed mais rápido do que a regra.

## Bugs e cuidados encontrados
- BTC=F do Yahoo x BTC-USD: horários diferentes (16h CT x 0h UTC) davam base anual de −14% a +12% aleatória; trocado pela Binance trimestral.
- Micro yield: "nocional" = yield x 1000 dava retorno infinito com juro zero (2012-2015); usado título equivalente em DV01 (US$ 10/bp).
- `pf.CONTRATOS` traz só comissão (sem meio spread) e margem de 30% "do nocional" para 10Y (sem sentido); corrigido no `cme_comum.py`.
- VXM: negócios separados por vencimento (antes saía 1 negócio de 14 anos).
- Pré-lançamento: sem a trava, a tendência usava 1OZ em 2021-22 (contrato inexistente).

## Próximos passos
1. VXM com R$ 50 mil+: testar tamanho por vol do próprio VX (não só choque) e hedge parcial com call de VIX/put XSP para cortar a cauda de 2025.
2. Tendência: rodar com 1OZ + MET + micro FX + 10Y + M2K apenas (o que cabe em R$ 20 mil) e comparar com ETF via IBKR.
3. Deixar o lucro lá fora até um teto (em vez de liquidar todo mês) e medir o ganho de IOF x exposição ao dólar.
4. Verificar se Micro Treasury Yield e micro FX seguem listados/líquidos (a CME delista micros pouco negociados).
