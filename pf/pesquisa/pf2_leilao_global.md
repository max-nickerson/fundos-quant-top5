# Frente pf2_leilao_global — a noite do leilão de fechamento fora da B3 (8 estratégias)

Pergunta: o edge nº 1 da rodada PF (comprar no leilão de fechamento depois de queda forte e vender no leilão de abertura, B3, +5,7 pp)
existe em outros mercados/ativos que uma PF brasileira com R$ 20–50 mil consegue operar (IBKR com só o necessário, ou B3)?

Resposta curta: **a reversão bruta existe em quase todo lugar (5–25 bps por noite), mas fora da B3 ela não paga o custo de varejo**:
conta na IBKR (~7–8 pp a.a. de CDI perdido + remessas sobre o saldo de margem), comissão mínima por ordem, impostos de transação
(UK 0,5%, França 0,2–0,4%, HK 0,1% por lado). O que sobra positivo é **dentro da B3** (ETFs da B3; blue chips sem a noite de sexta) e
mesmo isso morreu a partir de 2022.

Arquivos: `pf/fundos/lg_comum.py` (motor), `lg_baixar.py` (download único), fundos `lg_eua_etf`, `lg_europa`, `lg_asia`, `lg_adr_br`,
`lg_b3_etf_bdr`, `lg_small_eua`, `lg_alta_gap`, `lg_combo_regime`. Dados: `pf/dados/pf2_leilao_global/` (Yahoo OHLC 2010–2026,
S&P 600/100, DAX/CAC/FTSE/HSI pela Wikipedia, COTAHIST CODBDI 14). Resultados: `pf/resultados/bateria/lg_*.pkl`,
`pf/resultados/pf2_leilao_global.pkl` e `.csv`.

## Hipótese de execução (documentada em lg_comum.py)
- Sinal = retorno até o **fechamento de t**; compra **no próprio leilão de fechamento de t** (lag=0), venda no leilão de abertura de t+1
  (Open do Yahoo/COTAHIST = preço oficial de abertura). Na prática a ordem MOC/LOC tem prazo antes do fim do leilão (NYSE 15h50 ET,
  Nasdaq 15h55; Xetra/Euronext/LSE call de 5 min; TSE 15h25–15h30; HKEX CAS 16h00–16h10): decide-se com o **preço indicativo do call**,
  que é o proxy do fechamento. O erro é só na margem do limiar. O "t+2" da bateria (compra no fechamento SEGUINTE, convenção do
  b3_leilao_noite_aud) é o limite conservador e está na tabela.
- Noite = (abertura t+1 + dividendo ex × (1 − retenção)) / fechamento t − 1; inválida se a abertura sai do [mín, máx] do dia, se não
  houve negócio ou |noite| > 40% (15% em ETF/BDR B3 sem ajuste de desdobramento).
- Mercados com fechamento em horas diferentes no mesmo dia: quem fecha primeiro escolhe primeiro (Tóquio → HK → Europa → B3/NY), sem
  usar informação de quem fecha depois.

## Custos reais (por lado) e conta no exterior
- IBKR Pro: EUA US$ 0,0035/ação, mín. US$ 0,35 (numa ordem de US$ 1.300 = 2,7 bps; ADR de US$ 3 = ~10 bps por causa do por-ação);
  Europa 0,05% mín. € 1,25/£ 1; Japão 0,08% mín. ¥ 80, lote 100; HK 0,08% mín. HK$ 18 + stamp 0,1% (0,13% ago/21–nov/23) + taxas.
  Stamp duty UK 0,5% e FTT França (0,2% 2012–16, 0,3% 2017–mar/25, 0,4% desde abr/25) na compra. Derrapagem de leilão 1 bp; small
  caps: meio spread Abdi–Ranaldo (250 pregões, 2–50 bps).
- B3: emolumentos 0,03% + 1 bp; BDR: metade do meio spread mediano no fechamento (1–30 bps).
- Conta IBKR: margem Reg T (50%) → saldo = max(50% da posição, US$ 2.000) × 1,1, revisto mês a mês (`pf.custo_conta_exterior`);
  empréstimo de margem por 1 dia por noite a T-bill + 1,5%. **Custo medido da conta: 2021–26 = 7,9 pp a.a. com R$ 20 mil e 6,9 pp
  com R$ 50 mil** (CDI perdido 6,4 pp + remessas 1,3 pp). 2012–20: −1,0 pp (o real perdeu ~55% e o saldo em dólar "ganhou" 6,8 pp a.a.
  de câmbio — beta, não estratégia; por isso o IS das versões IBKR é inflado e no combo a escolha foi feita sem esse ganho).

## Resultado (bateria `rodar_pf.py um`, OOS desde 2021-01-01; truncamento passou em todos)

| fundo | PARAMS (melhor IS) | ativo OOS 20k / 50k (pp) | depois do IR 20k / 50k | IR | PBO | P(bater 3a) | sem 10 melhores | custo 2x | t+2 |
|---|---|---|---|---|---|---|---|---|---|
| lg_eua_etf | ETFs, queda abs ≥2%, n=3 | −12,1 / −7,9 | −12,0 / −7,9 | −0,89 | 62% | 7% | −15,5 | −19,3 | −9,0 |
| lg_europa | EWG/EWU/... em NY ≥2%, n=2 | −9,7 / −8,2 | −9,7 / −8,3 | −0,89 | 2% | 4% | −12,4 | −11,3 | −6,9 |
| lg_asia | EWJ/EWY/... em NY ≥4%, n=2 | −8,3 / −7,1 | −8,2 / −7,0 | −0,74 | 0% | 8% | −12,3 | −8,8 | −6,9 |
| lg_adr_br | perna B3, rel ≥2%, n=2 | −12,3 / −12,3 | −12,3 / −12,3 | −0,69 | 4% | 5% | −18,3 | −24,9 | −0,9 |
| **lg_b3_etf_bdr** | ETFs B3, queda ≥4%, n=2 | **+1,6 / +1,6** | **+1,4 / +1,4** | 0,57 | 36% | 88% | −0,3 | +0,9 | −0,2 |
| lg_small_eua | S&P 600 ≥8%, n=6 | −36,5 / −32,6 | −36,0 / −32,1 | −2,73 | 0% | 0% | −40,9 | −59,5 | −32,8 |
| lg_alta_gap | gap de baixa ETFs ≥2%, n=3 | −6,5 / −4,5 | −6,8 / −5,0 | −0,58 | 4% | 14% | −9,4 | −8,3 | −3,6 |
| **lg_combo_regime** | B3 blue chips+ETFs, sem sexta | **+2,9 / +2,9** | **+2,1 / +2,1** | 0,40 | 24% | 75% | −0,3 | −2,5 | −1,6 |

(OOS a.a. do fundo vs CDI 11,4%: lg_b3_etf_bdr 13,0%; lg_combo_regime 14,4%. Alavancagem 2x: +3,3 pp e +5,5 pp, pior queda −26%/−36%.)

## O que cada teste mostrou (negócios)

1. **EUA ETFs/large caps** — reversão bruta pequena e instável: ETFs depois de queda ≥4% −10 bps OOS (+18 bps comprando no fechamento
   seguinte); S&P 100 depois de queda ≥4%: +15 bps bruto, +7 bps líquido com R$ 20 mil (+10 com R$ 50 mil), mas IS ≈ −4 bps líquido.
   Melhores negócios: KRE em 13/03/2023 (+10,6%, dia seguinte à quebra do SVB), XRT 28/01/2021 (GameStop); piores: KRE 10/03/2023
   (−12,6%). O placebo (mesmas posições em datas aleatórias) rende mais que o sinal (p = 0,95): o prêmio é o da noite incondicional, não
   da queda. A conta na IBKR (7,9 pp) mata tudo.
2. **Europa** — ações locais: bruto +4 a +14 bps, líquido −10 a −69 bps. Reino Unido (stamp 0,5%) −58 a −69 bps; França (FTT) −14/−56;
   Alemanha −9/−19 com R$ 20 mil e −6/−7 com R$ 50 mil (a comissão mínima de € 1,25 é 11 bps numa ordem de € 1.100). ETFs de país em NY
   foram os "melhores" no IS (+20 bps bruto) por causa da manhã européia dentro da noite americana, OOS +4 bps. UCITS: poucas noites.
3. **Ásia** — Japão local: bruto +1 (IS) / +11 bps (OOS), líquido −17/−7 (lote de 100 só deixa papéis de até ~¥ 2–3 mil com R$ 7–10
   mil por posição). HK: stamp come 20+ bps → −33/−55. Coreia/Taiwan (diagnóstico, inacessíveis na IBKR): bruto −5 a +9 bps, líquido
   −52 a −62. Os ETFs de país em NY (escolhidos no IS) são outra coisa: a noite deles contém o pregão asiático inteiro (EWY em 2026,
   FXI em abril/2025) — aposta direcional; OOS −8,3 pp.
4. **ADR x B3** — mesma empresa, duas noites: ADRs brutos +4 a +25 bps mas a comissão por ação em ADRs de US$ 2–5 (ITUB, BBD, ABEV,
   SID) leva 20 bps → −17 a −28 pp. As MESMAS 20 ações na B3: IS +14 pp, OOS −12 pp comprando no mesmo fechamento e −0,9 no seguinte —
   o efeito em blue chips com ADR desapareceu depois de 2021 (pior: PETR3/PETR4 19/02/2021, −17% na noite da troca do presidente).
5. **ETFs/BDRs da B3** — o único positivo "limpo" de custo. Quem trouxe: SMAL11 (+8,7 pp em 27 noites), XINA11 (+7,7), BOVV11/BOVA11
   (+14), SMAC11 (+5); quem tirou: PIBB11, SPXI11, NASD11. XINA11/EURP11 são noites com o pregão asiático/europeu dentro (direcional).
   BDRs: bruto +30–60 bps mas spread/leilão raso → negativo. **Bug pego**: a 1ª versão (CODBDI 14 inteiro, sem filtro de negócios) deu
   +130 bps por noite — eram FIAGRO/FIP/FNAM11 com fechamento "parado" (marca velha, reversão falsa); com lista de ETFs de ações/ouro e
   ≥ 30 negócios no dia do sinal, cai para 15–60 bps brutos.
6. **Small caps EUA** — bruto +2 a +23 bps; meio spread + comissão ≈ 50 bps ida e volta → −37 pp. Viés de sobrevivência (lista atual
   do S&P 600) é A FAVOR da estratégia e mesmo assim perde. Melhor noite: HE (Hawaiian Electric) +40% depois dos incêndios de Maui.
7. **Alta forte (vendido) / gap** — vender a noite depois de alta perde 6–17 bps brutos por noite (o vendido paga o prêmio da noite).
   Gap de baixa que não recupera: +17–33 bps brutos OOS em S&P 100/ETFs, mas a conta IBKR come.
8. **Combo com VIX e dia da semana (B3)** — o filtro de **VIX alto NÃO ajudou** (IS 7,7 → 4,1 pp): a reversão não é maior com estresse
   americano. **Dia da semana ajudou**: noites que começam na sexta −5 bps e na quarta −4 bps contra +54 bps na segunda; sem sexta,
   IS 11,2 pp e OOS +2,9 pp. Mas por ano: 2016–2021 +7 a +35 pp; **2022–2026: +0,9, +1,6, −3,4, +4,9, +2,2 pp** — o grosso do OOS é 2021.

## O que deu certo e POR QUÊ
- O edge mora onde a PF tem **custo quase zero e preço único**: leilão da B3 (emolumentos 0,03%, sem comissão mínima, sem remessa).
  O outro lado é o formador de mercado de ETF/varejo em pânico; em SMAL11/BOVA11 o formador fecha comprado e devolve na abertura.
- Fora da B3 a reversão bruta existe (Alemanha +5, Japão +11, S&P 100 +15 bps), mas é do tamanho do custo fixo de varejo.

## O que deu errado
- Conta no exterior: com Reg T 50% a PF deixa metade do capital fora do CDI o ano todo para usar a noite só ~1/3 dos dias.
- Impostos de transação europeus/HK e comissão mínima com ordens de US$ 1–2 mil.
- Seleção no IS contaminada pelo câmbio (2012–20) e pelo regime 2016–21 da B3 que não continuou.

## Próximos passos
- Se a conta IBKR já existir por outro motivo (custo de conta já pago), S&P 100 depois de queda ≥4% rende ~+5 pp a.a. bruto da conta
  OOS — mas IS negativo: não usar sem nova amostra.
- B3: juntar lg_combo_regime (sem sexta) ao b3_leilao_noite_aud como filtro de dia da semana, e testar se SMAL11/SMAC11 (ETF de small)
  é o canal limpo do edge; monitorar 2022+ (decaiu).
