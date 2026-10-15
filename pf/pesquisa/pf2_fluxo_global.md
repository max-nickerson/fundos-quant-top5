# PF2 — frente "fluxo global": fluxos forçados e eventos fora do Brasil em tamanho de PF (out/2026)

Código: `pf/fundos/fg_*.py` (8 fundos) + `fg_comum.py` (motor de livro de eventos na IBKR, preço não ajustado, dados) + `_fg_nport.py`
(carteiras do IWM no N-PORT da SEC, CUSIP→ticker) + `fg_rodar.py` (junta as baterias, roda as variantes, grava
`pf/resultados/pf2_fluxo_global.pkl` e o anexo `pf/pesquisa/pf2_fluxo_global_tabelas.md` com as tabelas completas, variantes e os
**10 melhores/piores negócios de cada fundo**). Cada fundo passou por `python pf/rodar_pf.py um <arquivo>` sem erro e com o
truncamento (look-ahead) passando. Cache dos dados novos: `pf/dados/pf2_fluxo_global/`.

## Resultado (fora da amostra, ativo sobre o CDI, pp a.a.)

| fundo | aplicável | OOS desde | 20k antes IR | 20k depois IR | 50k antes IR | 50k depois IR | IR | PBO | P(bater 3a) | sem 10 melhores |
|---|---|---|---|---|---|---|---|---|---|---|
| fg_fim_mes (balanceados no IVVB11, B3) | sim | 2021 | −0,06 | −0,12 | −0,06 | −0,13 | 0,00 | 5% | 51% | −2,4 |
| fg_indices_exclusao (S&P/Nasdaq/DAX/CAC) | sim | 2021 | −16,1 | −15,8 | −9,2 | −9,1 | −0,79 | 24% | 4% | −23,2 |
| fg_taxloss (dezembro→janeiro) | sim | 2021 | −11,3 | −11,1 | −7,4 | −7,3 | −0,90 | 87% | 5% | −14,8 |
| fg_russell (saídas na reconstituição) | sim | 2023 | −4,1 | −4,0 | −0,8 | −0,8 | −0,05 | 0% | 33% | −17,3 |
| fg_dividendo_b3 (dividendo isento) | sim | 2021 | −6,9 | −6,8 | −6,9 | −6,8 | −2,26 | 29% | 0% | −7,4 |
| fg_merger_arb (tender offers) | **não** (piso) | 2021 | −11,5 | −11,3 | −11,5 | −11,3 | −1,48 | 64% | 0% | −13,3 |
| fg_ipo_quiet (fim do quiet period) | sim | 2021 | −27,5 | −27,1 | −25,0 | −24,6 | −0,59 | 37% | 1% | −31,2 |
| fg_spinoff_pequeno | sim | 2021 | −6,5 | −6,4 | −4,2 | −4,2 | −0,40 | 13% | 21% | −14,2 |

Nenhum dos 8 bate o CDI fora da amostra depois de custos. Custo x2, execução t+2, leque e walk-forward no anexo; nenhum Sharpe > 1,5.

## A conclusão de mesa que vale para a frente inteira: comprar EUA custa o CDI

Todo livro comprado na IBKR é pago à vista em dólar; conta pequena não rende juros, a venda a descoberto do hedge não remunera e o
saldo precisa ficar parado (Reg T + US$ 2 mil para vender). Esse dinheiro deixa de render CDI (11–15% a.a. no OOS) e paga IOF 1,1% +
spread na ida e 0,38% + spread na volta a cada ajuste mensal (`pf.custo_conta_exterior`). Decomposição OOS com R$ 20 mil (% do capital
por ano, soma aritmética):

| fundo | eventos (líq. de custos) | hedge | CDI perdido | remessas | câmbio do saldo | total | saldo médio IBKR | livro médio |
|---|---|---|---|---|---|---|---|---|
| índices | +8,6 | −6,8 | −8,6 | −3,6 | −3,0 | −13,9 | R$ 15,8 mil | R$ 9,1 mil |
| tax-loss | +0,6 | −2,4 | −2,3 | −3,3 | −2,7 | −9,9 | R$ 4,4 mil | R$ 1,0 mil |
| Russell | +8,2 | −1,2 | −5,4 | −4,1 | +1,3 | −1,1 | R$ 8,8 mil | R$ 5,4 mil |
| merger arb | −1,9 | 0 | −5,1 | −2,9 | −0,6 | −10,5 | R$ 9,5 mil | R$ 6,7 mil |
| IPO quiet | −10,7 | −2,6 | −6,6 | −2,4 | 0,0 | −21,8 | R$ 12,4 mil | R$ 2,4 mil |
| spin-offs | +5,7 | −4,1 | −6,5 | −1,3 | −0,2 | −5,1 | R$ 11,9 mil | R$ 6,4 mil |

A conta da IBKR custa 8–12 pp do capital por ano — mais que o alfa bruto de qualquer evento americano medido. O saldo fica 1,5–5x o
livro médio porque os eventos são irregulares e a regra do motor dimensiona pelo maior exigido do mês anterior. O hedge cambial com
WDO só entra quando o saldo passa de ~US$ 8 mil (0,8 contrato): com R$ 20 mil quase nunca. Testei manter o saldo estável (máximo de
6 meses) para fugir das remessas: perde mais CDI do que economiza (−17,0 vs −15,8 pp na 1ª versão do fundo de índices). **Edge de PF nos EUA só existe se o
alfa por real-tempo de saldo parado passar de ~12% a.a.** — nenhum dos 8 passou.

## Os 8 fundos

**1. fg_fim_mes — rebalanceamento dos balanceados e dos ETFs alavancados, no IVVB11 (B3, sem remessa).** Tese: quando as ações apanham
dos títulos no mês (SPY − TLT até D−5 < −1%), os 60/40 compram ações nos 4 últimos pregões; os LETFs compram/vendem no fechamento na
direção do dia e o preço volta no dia seguinte. Execução: IVVB11 comprado do fechamento de D−4 ao último pregão (100% do capital, caixa
fora do CDI só nesses dias); LETF = day trade da abertura ao fechamento da B3 contra dias de |S&P| > 2% (vendido no day trade não
precisa de aluguel). Custos reais do COTAHIST (meio spread do fechamento: 1,5–3% em 2014–16, 0,03–0,1% hoje). Resultado: escolhido no
IS "pensão, limiar 1%" (IS +0,9; OOS −0,1; PBO 5%); sem limiar o OOS é +1,4. **Deu certo** nos meses de pânico: mar/2020 (+7,8% em 4
pregões), set/2020 (+5,7%), ago/2024 (+3,2%) — os balanceados compraram o que tinha caído. **Deu errado**: LETF. Bruto (sem custo) +1,3
OOS, mas o spread do IVVB11 de 2014–16 e os 2 lados de custo comem tudo (LETF 1%: −48 pp IS); a reversão "da madrugada" já está na
abertura da B3 (o IVVB11 abre às 10h com o futuro do S&P). O lado vendedor do fim de mês exigiria alugar IVVB11 por 4 dias (0,5% por
contrato na Clear/Rico) — fora.

**2. fg_indices_exclusao — excluídos do S&P 500, Nasdaq-100, DAX e CAC comprados no leilão da véspera da efetiva.** Só exclusão por
valor de mercado/revisão regular (fora aquisição, cisão, falência, conservatorship). Sobrevivência: 29% dos excluídos dos EUA não têm
preço no Yahoo depois da efetiva; os que pediram recuperação judicial (8-K item 1.03 em até 5 anos: FTR, MNK, WIN, RSH, DNR, SHLD...)
entram com −30% em 166 pregões, os outros andam com o ETF de hedge. O evento ainda paga um pouco (retorno médio menos o hedge +5,5%
IS → +0,9% OOS por negócio de 60 pregões — a anomalia foi arbitrada), mas a conta da IBKR leva 15 pp. Melhores: SIRI dez/2008 (+183%),
COTY set/2020 (+134%), NFLX dez/2012 (+103%); piores: ILMN dez/2024 (−37%), LCID dez/2023 (−37%), ENR.DE mar/2022 (−30%). FTSE 100,
STOXX 600, Nikkei e KOSPI: sem histórico gratuito de mudanças com data (ja.wiki só tem o ano); NIFTY: PF brasileiro não compra Índia.

**3. fg_taxloss — small caps perdedoras de 20/dez ao 5º pregão de janeiro**, 20 piores do ano (≤ −50%, preço da época ≥ US$ 5, giro
US$ 1–50 mi), hedge IWM. Contribuição dos negócios (já com hedge e custos de ordem, antes da conta da IBKR), por dezembro: IS
misturado (2008 +10, 2011 +7, 2018 +9 contra 2007 −12, 2015 −13 pp) e OOS 2021 −11, 2022 +3, 2023 +5, 2024 0, 2025 −4 pp — os
perdedores de dez/2021 (o estouro das growth/SPACs) continuaram caindo em janeiro. Média por negócio menos o hedge: +1,7% IS → −0,3% OOS.
A conta da IBKR (remeter em dezembro, trazer em fevereiro/março, 2–3 meses sem CDI) custa ~5 pp/ano sozinha. A variante sem seleção
de ações (IWC − SPY) também perde (−8,7). PBO 87%. O universo só tem quem está vivo no Yahoo (perdedores que quebraram depois faltam
-> o número ainda é otimista).

**4. fg_russell — saídas do Russell 2000 compradas no leilão da reconstituição (última sexta de junho), 60 pregões, hedge IWM.**
Composição REAL: carteiras do IWM no N-PORT da SEC (31/mar vs 30/jun e 30/set), CUSIP→ticker pelos fails-to-deliver da SEC; só a metade
de menor valor (as que viram micro cap). É o único com alfa de evento grande no OOS: +6,1% por negócio menos o hedge, +8,2 pp/ano do
capital antes da conta da IBKR; com R$ 50 mil fica em −0,8 pp. Mas é loteria de micro cap: acerto 29%, melhores VTGN jun/2023 (+187%),
RCEL jun/2026 (+189%), STIM (+117%); sem os 10 melhores −17 pp; IS 2020–22 negativo (−0,95% por negócio); só 7 reconstituições (o N-PORT
público começa no fim de 2019). Sobrevivência: saídas sem preço no Yahoo entram neutras (andam com o IWM); se todas fossem a −30%, −11,5
pp. A perna "entra antes" (comprar quem sobe da micro cap depois da lista preliminar) perde −22 pp: a lista é pública e arbitrada.

**5. fg_dividendo_b3 — dividendo isento na data-com (ações B3; FIIs como variante).** Nos EUA o PF paga 30% retido sobre dividendo
(compensa no máximo 15%): comprar antes da data-ex lá é perder dinheiro, então a ideia virou "B3 vs EUA". Na B3: compra no fechamento
da data-com (dividendo já aprovado, yield ≥ 2%), vende na abertura da data-ex. Resultado: a ação cai MAIS que o dividendo — queda/
dividendo mediana 0,8–0,9 em 2014–17 e 1,05–1,2 em 2022–26 — e o spread completa o prejuízo (−6,9 pp, PBO 29%). FIIs (proventos do
Yahoo só de 2022 em diante, data-ex prevista pelo dia útil do provento anterior): queda/rendimento mediana 0,9–1,0, ≈ CDI (−0,2 pp).
Desdobramento/redução de capital em espécie no mesmo dia (CSAN3 mai/2021 1:4, BRAP dez/2021) foram removidos (filtro simétrico de
variação noturna > 25%).

**6. fg_merger_arb — tender offers em dinheiro (SC 14D9) — NÃO APLICÁVEL.** O Yahoo não tem preço de ~75% dos alvos (os concluídos);
os que têm preço são fracassos, ofertas parciais e tickers reaproveitados (filtro: se o EDGAR diz que deslistou, o preço tem de acabar
até 30 dias depois). O fundo roda com o concluído rendendo 0% (piso: −11,5 pp); com 2%, 4% e 6% de spread hipotético nos concluídos o
OOS é −8,5, −5,5 e −2,4 pp — mesmo com 6% por negócio não paga a conta da IBKR. Os alvos com preço perdem −2,1 pp (F/SQNS/REPX −60 a
−80%: ofertas que fracassaram).

**7. fg_ipo_quiet — fim do quiet period (dia 25) de IPOs, comprado 8 pregões antes.** Pagou de 2012 a 2020 (retorno médio menos o
IWM de +2 a +4% por IPO em 2012–13, 2016, 2019) e virou o pior fundo da frente: em 2022–26 os IPOs caíram na janela (−7% em 2022, −2 a
−4% em 2023–26; −28 pp/ano com 5% por IPO e ~10 simultâneos). Bug importante encontrado aqui: o Yahoo ajusta o passado pelos grupamentos futuros — um IPO de US$ 4 que fez grupamento
1:20 aparece a US$ 80 — então o filtro "preço ≥ US$ 10" selecionava justamente os fracassos; corrigido com o preço da época
(`fg_comum.preco_bruto`, desdobramentos do Yahoo). O lock-up vendido (variante) perde −15 pp (aluguel 10% a.a., squeeze).

**8. fg_spinoff_pequeno — separadas pequenas (giro < US$ 10 mi) 40 pregões depois do 1º preço, 12 meses, hedge IWM.** Sobrevivência
pelo EDGAR: das 158 separadas que sumiram do Yahoo, 24 pediram recuperação judicial e 34 sumiram sem compra (−30% em 166 pregões); 100
com proxy de fusão/oferta andam com o IWM. As pequenas reais são ótimas na média (+17,7% por negócio menos o hedge no OOS, 32
negócios), mas o livro "pequeno" tem mais sintéticos que reais e a conta da IBKR leva 6,5 pp: −6,5 pp. Todos os tamanhos dá +15 pp OOS
— um único negócio (SNDK abr/2025, +2.640%) responde por 115 pp de contribuição: loteria, não fundo.

## O que deu certo e por quê
- O **fluxo forçado existe** onde o tamanho do vendedor é grande frente ao papel: Russell (micro caps vendidas por todos os indexados no
  mesmo leilão: +6% por negócio OOS), spin-offs pequenos (+18% por negócio), excluídos do S&P em pânicos (SIRI 2008, COTY 2020).
- **No Brasil (IVVB11) não há custo de carregar dólar**: o fim de mês dos balanceados empata com o CDI com 38 negócios em 12 anos e
  ganha nos meses de pânico (mar/2020, set/2020, ago/2024) — o mesmo padrão "comprar depois de queda forte com vendedor forçado" que
  sobreviveu na rodada PF1.

## O que deu errado e por quê
- **Conta no exterior**: 8–12 pp/ano do capital (CDI − 0% em dólar, IOF + spread nas remessas). Em R$ 20–50 mil nenhum evento americano
  paga isso. O hedge cambial com WDO não cabe (1 contrato = US$ 10 mil).
- **Anomalias arbitradas ou invertidas no OOS**: exclusão de índice (+5,5% → +0,9% por negócio), tax-loss (+1,7% → −0,3%), quiet
  period (IPOs 2022+ caem na janela), dividendo (queda ≥ dividendo).
- **Sobrevivência domina tudo que é small cap**: spin-offs (+5,7 IS sem sintéticos → −3,2 com), merger arb (intestável), Russell
  (−4,1 neutro → −11,5 duro). Os números com tratamento são os honestos; sem tratamento, todos parecem melhores.

## Bugs/armadilhas encontrados (não repetir)
1. **Preço ajustado do Yahoo em filtros de preço** olha o futuro (grupamentos posteriores): corrigido com `preco_bruto` (IPO, tax-loss,
   Russell). O tax-loss caiu de −1,2 para −3,9 pp no IS com a correção.
2. **Datas de evento calculadas sobre o índice truncado** (fim do quiet period, saída em janeiro): o truncamento acusou (diferença 0,4%);
   corrigido usando o calendário da NYSE (`C.DIAS_US`), sabido de antemão.
3. **P&L do hedge como "negócio" anual** distorcia "sem os 10 melhores" (o ano de 2022 do hedge virava o melhor negócio): o hedge agora é
   rateado entre os negócios abertos da região pelo valor de cada um (`fg_comum.livro`), sobra só o resíduo de arredondamento.
4. **WDO arredondado para o contrato mais próximo** fazia sobre-hedge de 2x (vendido em dólar sem lastro em 2021–24): agora só com ≥ 0,8
   contrato de saldo (como `_rev_pares_pf`).
5. **N-PORT do IWM de 30/jun/2024 e 2025** ainda não mostra a reconstituição inteira (41 e 81 saídas contra 200–330 nos outros anos):
   "saiu" = fora em junho ou em setembro.
6. **Cache de spin-offs da auditoria** (`pf/dados/rev_spinoffs`, usado por `rev_spinoffs`): a trajetória sintética continua caindo depois
   do pregão 166 (−47% em 300 pregões, não os −30% da docstring) e trata as 100 separadas compradas depois como quebradas; aqui os
   sintéticos foram refeitos com a classe do EDGAR.
7. Dividendos: dias de desdobramento/redução de capital (CSAN3, BRAP3/4) apareciam como −58% a −75% "de queda".

## Dados novos (pf/dados/pf2_fluxo_global/)
`universo_extra` (Yahoo, 3,6 mil ações a mais), `splits` (desdobramentos de 6,5 mil tickers), `sec_frames_acoes` (ações em circulação
SEC XBRL 2009–2026), `iwm_nport` (carteiras trimestrais do IWM 2019–2026), `cusip_ticker` (fails-to-deliver SEC), `fii_div` (proventos
de FIIs, Yahoo, 2022+), `spin_volume`, `etfs_extra` (IWC/IWN/VTWO), `ipos_eventos`, `alvos_ofertas` + caches por fundo.
Tentativas que não deram: histórico de posições do IWM no site da iShares (bloqueia robôs); ranking do Russell por valor de mercado com
SEC + Yahoo (o universo do Yahoo em 2012 tinha < 3.000 ações vivas: inviável); preço de alvos comprados (não existe grátis).

## Próximos passos
1. **Russell com R$ 50 mil+ e conta IBKR compartilhada**: o alfa do evento (+8 pp/ano do capital) existe; o que mata é a conta. Se a
   mesma conta servir a outros livros (saldo já parado), o custo marginal cai para a remessa — vale testar a carteira conjunta e esperar
   mais reconstituições (só 7; FTSE Russell passa a reconstituir em junho E dezembro a partir de 2026).
2. **Fim de mês/trimestre na B3 com o lado vendedor via WSP quando couber (R$ 100 mil+)** e com o sinal de pânico (queda do mês > 5%).
3. Spin-offs: só faz sentido como livro de "opções" (poucos nomes, 12 meses) dentro de uma conta IBKR que já exista.
4. Merger arb e Russell pré-2020 precisam de preço de deslistadas (CRSP/Norgate, pagos) para sair do campo das hipóteses.
