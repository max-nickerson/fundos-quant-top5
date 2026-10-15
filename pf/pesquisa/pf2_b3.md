# Frente pf2_b3 — mais edges na B3 com vendedor/comprador forçado (rodada PF2)

Módulos: `pf/fundos/bb_*.py` (auxiliar `bb_base.py`). Bateria: `python pf/rodar_pf.py um <arquivo>` (todos rodaram até o fim, truncamento
passou nos 9). Resultados: `pf/resultados/pf2_b3.pkl`, baterias em `pf/resultados/bateria/bb_*.pkl`, melhores/piores negócios, grade,
custo, atraso e alavancagem de cada fundo em `pf/resultados/pf2_b3/detalhes.txt`.

## Dados novos (cache em `pf/dados/pf2_b3/`)
- `fii_cotas.parquet`, `fii_direitos.parquet` — extraídos do COTAHIST bruto (CODBDI 12/14, lote padrão) por `exportar_fii.py`; o painel
  de ações da rodada 1 não tinha FIIs. ESPECI "CI" também é ETF (BOVA11, HASH11, ETHE11): o universo de FII é só quem entrega informe
  mensal à CVM (bug encontrado e corrigido — antes, os ETFs de cripto dominavam o pânico de FII).
- `fii_rend.parquet` — rendimento por cota = DY do mês x VP da cota (informe mensal CVM, 2017+), pago no 1º pregão do mês seguinte
  (calibrado contra o Yahoo do HGLG11: R$ 1,10 = R$ 1,10, ex no 1º pregão). O Yahoo tem só ~6 rendimentos/ano por FII antes de 2022 — inútil.
- `ewz_yahoo.parquet` (EWZ/EWZS OHLCV 2005+), `controle_eventos.parquet` (IPE), `ipe_proventos.parquet` (avisos/FR de proventos na CVM),
  `vlmo_liquido.parquet` (VLMO líquido por companhia/mês).

## Resultado (OOS, excesso sobre o CDI em pp a.a.)

| fundo | OOS desde | 20k antes | 20k depois IR | 50k antes | 50k depois IR | IR | PBO | P(bater 3a) | sem 10 melhores | custo 2x | t+2 | placebo p |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| bb_dividendo_extra | 2021 | **+10,9** | **+9,8** | **+12,3** | **+10,3** | 1,04 | 2% | 97% | +5,3 | +5,6 | +9,4 | 0,00 |
| bb_vencimento_opcoes | 2021 | +1,3 | +1,3 | +2,1 | +1,7 | 0,18 | 26% | 60% | −3,9 | −1,3 | +0,7 | 0,14 |
| bb_fii_panico | 2021 | −1,0 | −1,0 | −1,0 | −1,0 | −0,15 | 3% | 35% | −4,5 | −2,0 | −2,1 | 0,10 |
| bb_fii_emissao | 2021 | −1,1 | −1,1 | −1,1 | −1,1 | −0,42 | 22% | 17% | −2,2 | −2,1 | −2,0 | 0,44 |
| bb_insider_small | 2023 | −1,6 | −1,6 | −2,2 | −2,2 | 0,02 | 15% | 43% | −11,3 | −4,0 | −2,8 | 0,19 |
| bb_fii_datacom | 2021 | −2,0 | −2,0 | −1,7 | −1,8 | −0,44 | 43% | 23% | −3,3 | −5,9 | +1,9 | 0,07 |
| bb_rebal_indices | 2021 | −2,4 | −2,4 | −2,3 | −2,2 | −0,21 | 57% | 35% | −7,4 | −3,1 | −2,9 | 0,61 |
| bb_estrangeiro | 2021 | −2,7 | −2,7 | −2,7 | −2,7 | −0,27 | 46% | 23% | −0,8 | −2,9 | −3,0 | 0,76 |
| bb_tag_along | 2021 | −8,6 | −8,5 | −8,5 | −8,4 | −0,57 | 53% | 10% | −14,8 | −10,0 | −8,6 | 0,98 |

IR: CLASSE_IR declarada (ações: mensal com isenção de R$ 20 mil de vendas; FII 20% sobre todo o excesso — conservador, o rendimento é
isento; BOVA11 = etf_b3 15%).

## Por fundo

### 1. bb_dividendo_extra — Dividendo/JCP extraordinário até a data-com (o único que passou)
**Tese.** Provento aprovado >= 2% do preço (várias vezes o normal) cria um comprador previsível — o investidor de renda (PF, fundos de
dividendos) que só age quando vê o aviso e quer estar na base na data-com. Compro no fechamento seguinte à divulgação e VENDO para ele no
fechamento da data-com (não recebo o provento; não carrego a queda ex). Mediana de 4 pregões por negócio, ~40 negócios/ano, 20% do capital
por negócio, exposição média 21% do capital, beta 0,13 ao Ibovespa.
**Dados.** Proventos B3 (`arb_proventos`: valor, tipo, data-com; 103 pagadoras). **Bug crítico encontrado:** a "data de aprovação" da B3
nem sempre é a divulgação — BBSE3 aparece aprovado em 17/12/2021, mas o aviso com o valor só saiu na CVM em 07/02/2022. Com a data da B3 o
fundo "sabia" o dividendo 7 semanas antes. Correção: o sinal é a 1ª entrega na CVM (Aviso aos Acionistas ou Fato Relevante sobre
proventos) entre aprovação − 3 dias e a data-com; sem entrega, o evento sai. Isso cortou ~8% dos eventos e quase nada do resultado
(IS 8,7 -> 6,8; OOS 11,3 -> 10,0 no limiar 2%).
**Resultado.** IS 2014–20 +7,3 pp; OOS 2021–26 +10,9 pp (20k) / +12,3 pp (50k); depois do IR +9,8/+10,3. Monotônico no tamanho do
provento (retorno médio por negócio OOS: < 3% −0,2%; 3–5% +1,5%; > 5% +3,5%). Placebo p = 0, PBO 2%, leque 100% positivo, custo 2x +5,6,
t+2 +9,4 (t+3 cai a +1,7: metade dos eventos tem 2–4 pregões até a data-com). Alfa depois de tirar o beta: IS +5,7, OOS +9,9 pp.
**Melhores:** ALPA3 ago/2015 (+44%, 80 pregões), MRVE3 2019 e 2020 (+38%/+30%, 120–160 pregões: aprovação em abril com data-com em
jun/dez), BRAP3/BRAP4 nov/2021 (+23%/+21%, dividendo de 13% + redução de capital em VALE3), PETR4/PETR3 mai/2023 (JCP 7%, +20%/+17%),
BRAP/VALE out/2023. **Piores:** MRVE3 2018 (−16%, 162 pregões), VIVT3 mar/2026 (−14%), BBSE3 jun/2021 (−12%), QUAL3 nov/2016 (−11% em 3
pregões), GGBR4/GOAU4 out/2021 (−10%, JCP de 6–12% com o aço caindo), ENGI3 dez/2021, SANB3 jan/2019, PETR3/PETR4 mai/2024 (−9%: troca
do CEO).
**Por que funciona (negócio):** o comprador do provento é forçado pelo calendário (precisa estar na base até a data-com), é pessoa física
(dividendo isento) e compra a mercado; a PF que já está posicionada vende a ele no fechamento da data-com. Grande provento = mais
compradores marginais — por isso cresce com o tamanho do provento.
**Riscos / o que pode ser artefato:** (i) sobrevivência: a tabela de proventos da B3 só tem as 103 companhias listadas hoje (as que
morreram no meio não entram) — o viés é pequeno em janelas de 4 pregões, mas existe; (ii) 2023 (+34 pp) e 2020 (+25 pp) pesam: sem os 10
melhores +5,3 pp; (iii) a variante "sai no dia ex" foi prejudicada por proventos que o Yahoo perde (ALPA3, QUAL3) — corrigi trocando o
provento do Yahoo pelo da B3 no dia ex, mas redução de capital em ações (BRAP dez/2021) continua fora. A variante escolhida (sai na
data-com) não carrega o dia ex. (iv) 10 negócios com > 40 pregões (aprovação muito antes da data-com) somam +18,8 pp no IS e −0,6 no OOS:
não é deles que vem o OOS.
**Próximos passos:** universo completo de proventos (IPE "Aviso aos Acionistas" com valor lido do texto) para eliminar a sobrevivência;
preço de abertura do dia seguinte (o aviso sai à noite) para medir quanto do ganho já está no t+1; limitar a 40 pregões a priori.

### 2. bb_vencimento_opcoes — objetos comprados no fechamento do vencimento
**Tese.** Varejo é lançador coberto/financiamento em massa; no vencimento mensal há venda mecânica (exercício, rolagem, desmonte de
delta-hedge) que some no dia seguinte. **Pinning não existe** nos dados (comprar abaixo do strike de maior volume perde 0,25% no dia).
O padrão é "cai até o vencimento, sobe depois": 3 pregões antes −0,6% IS / −0,2% OOS; 3 depois +0,6% / +0,5% (6 papéis).
**Implementação.** Calendário de vencimento por regra (3ª segunda até abr/2021, 3ª sexta depois). Compra no fechamento do vencimento,
vende 3 pregões depois. A grade escolheu PETR4+VALE3 (IS +4,8) — a cesta de 6 deu OOS −2,7.
**Resultado.** OOS +1,3 (20k) / +2,1 (50k); frágil: sem os 10 melhores −3,9, custo 1,5x = 0, t+3 −5,1. Melhores: VALE3 abr/2015 (+31%),
PETR4 nov/2014 e jan/2015; piores: PETR4 fev/2021 (−28%, troca do CEO), PETR4 mai/2018 (greve dos caminhoneiros). O fracionário
(0,2% extra) come metade do ganho com R$ 20 mil. **Veredito:** efeito real e pequeno; não paga o custo do varejo de forma confiável.

### 3. bb_fii_panico — pânico de FII
Compra o FII que caiu > 15% a mais que o índice de FIIs em 5 pregões, segura 21. IS +5,9 (2020 inteiro: março/2020), OOS −1,0; nos
limiares menores o OOS é −5 a −12 (2021–23 o FII que caiu continuou caindo: crédito ruim de CRI, ciclo de juros). Melhores: HCTR11/DEVA11
abr/2023, SPTW11/VISC11/MALL11 mar/2020; piores: CACR11 2026 (−45%/−41%), DEVA11/HCTR11 mar/2023. O vendedor forçado existe (varejo), mas
o que ele vende muitas vezes é crédito que realmente piorou — sem a leitura da carteira do FII, o sinal de preço não separa.

### 4. bb_fii_emissao — cota de FII depois do fim do direito de preferência (ideias 2 e 3)
**Direito de subscrição em si (ações e FII): o edge NÃO existe para quem compra.** Comprado no 1º pregão, o direito perde mediana de 57%
(ações) / 28–62% (FII) até o último pregão; travado contra a ação perde 0,4–1,4% do nocional; meio spread mediano de 7–9% nas ações e
3–5% nos FIIs. O direito é negociado com PRÊMIO, não desconto (valor de opção + quem fica sem caixa não vende barato). Também não dá
para saber o último pregão do direito sem olhar o futuro (não está nos dados; o aviso está no PDF) — por isso o fundo usa o 1º pregão
SEM negócio do direito como sinal (causal).
**Cota depois do período:** o FII emissor sobe +1,2% (IS) / +1,3% (2021–26) acima do índice de FIIs nos 20 pregões seguintes — consistente
— mas sem hedge (não há futuro de IFIX; aluguel de FII é raro) o beta de FII em 2021–25 contra CDI de 11–15% leva o fundo a −1,1 pp.
Melhores: RBRF11 mar/2020 (+38%), MXRF11 nov/2019; piores: RBFF11/PORD11/MXRF11 fev–mar/2020. Ações (estudo): a ação depois do direito
continua caindo (−1,9% IS, −6,9% OOS em 20 pregões) — seria venda a descoberto em small cap em dificuldade, já testado em rev_followon.

### 5. bb_insider_small — insiders comprando small caps (VLMO)
Compra líquida de controlador/administradores >= 2% do giro mensal em papel com ADV de R$ 50 mil–2 mi, 126 pregões. IS (2019–22) −5,6,
OOS −1,6; sem os 10 melhores −11. Melhores MNPR3 (+175%), TECN3 (+189%), RDNI3; piores LLIS3 (−72%), AGXY3, ATMP3, ATOM3, DOTZ3 — o
controlador compra para sustentar o preço de empresa em dificuldade. **Bug do dado:** o VLMO baixado tem acentos corrompidos
("Compra � vista"); a busca por "Compra à vista" (código institucional `ideias_eventos_br.ev_insider`) não acha NENHUMA linha — o teste
institucional de insiders provavelmente rodou vazio; aqui casamos por prefixo. **Recompra executada não está no VLMO baixado** (o
consolidado não traz a tesouraria) — fica sem teste.

### 6. bb_fii_datacom — FII na data-com
Cesta dos 10 FIIs mais líquidos comprada k pregões antes da data-com (último pregão do mês). Estudo: os 3 últimos pregões do mês rendem
+0,27% acima do normal (IS) / +0,37% (OOS). A grade escolheu k = 10 (IS +8,4, IR 1,23 — março/2020) e o OOS foi −2,0; a variante
k = 3 saindo no dia ex deu OOS +4,1 (IR 1,4) — mas foi a PIOR no IS: escolher agora seria olhar o OOS. Meio spread real de FII líquido
~0,12% por lado: 12 ciclos por ano a 90% do capital custam ~3 pp (custo 0 = +2,0; custo 2x = −5,9). Lead honesto: k = 3 com ordem
limitada (meio spread) e só o rendimento isento — precisa de dado intradiário para não cair no erro dos fills (gl_bdr_limite).

### 7. bb_rebal_indices — SMLL e IBrX-100
Regra reconstruída (IN 12m, presença 95%, IBrX = 100 maiores, SMLL = IBrA menos 85% do valor de mercado pelo nº de ações do ITR/FRE),
sem os entrantes do Ibovespa. Estudo: entrantes SMLL −0,45% e IBrX −0,16% (IS) da decisão à troca; os SAINTES caem −1,2/−1,5% (a
pressão de venda é real, mas está do lado vendido, caro em small cap). A grade escolheu IBrX 42 pregões (IS +6,6: é beta de mid cap em
2016–19); OOS −2,4. O dinheiro passivo do SMLL/IBrX (SMAL11, BRAX11) é pequeno demais para mover os entrantes. IFIX (estudo): entrantes
−0,4%/−0,9%, sem efeito — o XFIX11 é minúsculo.

### 8. bb_estrangeiro — saída de estrangeiro (EWZ) -> BOVA11
Sem histórico gratuito de fluxo por investidor baixado; proxy EWZ (queda 5d < −8% com volume >= média de 120 dias). Comprar BOVA11 depois
perde: −1,7% em 5 pregões, −3,3% em 10 (2008–20). O estrangeiro sai em ondas — o vendedor forçado continua do outro lado. OOS −2,7;
melhores 2009/2011 (fundo de crise), piores fev/2020 (−23%), 2015, nov/2022. Contrário ao fluxo estrangeiro não funciona; seguir o fluxo
seria beta.

### 9. bb_tag_along — ON no anúncio de troca de controle
IPE "mudança de controle da companhia"/"transferência do controle acionário". OOS −8,6. Os eventos são sujos: controle de subsidiária
(Méliuz/Bankly), o VENDEDOR publicando (Petrobras/BR), e principalmente empresas em crise cujo "novo controlador" é credor ou comprador a
preço baixo (Gafisa, Bahema, Azevedo & Travassos, Alliança: −47% a −63%) — o tag along a 80% de um preço baixo não protege. O edge de
OPA já capturado em b3_opa_leilao (com o PREÇO no FR) não aparece sem o preço.

## O que deu certo e por quê
Só o dividendo extraordinário: comprador forçado pelo CALENDÁRIO (data-com), pessoa física, compra a mercado, e a saída é marcada
(data-com é pública) — o mesmo desenho dos sobreviventes da rodada 1 (leilão de fechamento, OPA até o leilão, rebalanceamento do Ibovespa).

## O que deu errado (padrões)
- Vendedor forçado sem limite de preço (pânico de FII, saída de estrangeiro, troca de controle em empresa em crise) = o preço continua
  caindo; a tese de "liquidez" só paga quando há um piso econômico (preço de OPA, provento, carteira do índice).
- Índices com pouco dinheiro passivo (SMLL, IBrX, IFIX) não têm comprador forçado relevante.
- Custos de varejo em giros curtos (vencimento, data-com de FII): o efeito existe (0,3–0,5% por evento) e o spread + fracionário levam metade.

## Bugs encontrados e corrigidos
1. Data de aprovação B3 ≠ divulgação (BBSE3): sinal passou a ser a entrega na CVM.
2. ESPECI "CI" inclui ETFs: o universo de FII agora exige informe mensal CVM.
3. Truncamento do bb_dividendo_extra falhava (coluna `data` = data-com cortava eventos já anunciados): `data` = aprovação, proventos
   pagos numa tabela separada.
4. Atraso t+2 empurrava a saída para o dia ex (onde faltam proventos no Yahoo): a ordem de venda na data-com é conhecida na entrada, só a
   entrada atrasa.
5. VLMO com acentos corrompidos (afeta também o código institucional).

## Próximos passos
- bb_dividendo_extra: universo completo de proventos pelo IPE (sem sobrevivência), auditoria independente, preço de abertura de t+1.
- FII data-com k = 3 com ordem limitada: só com dado intradiário (book) — não usar fills de dado diário.
- Recompra executada: baixar o VLMO de tesouraria (formulário "Companhia") ou o "Negociação de ações de própria emissão" do IPE.
- Fluxo estrangeiro: a B3 publica o saldo diário do estrangeiro (Bovespa) — com histórico, testar o lado "seguir o fluxo" contra CDI.
