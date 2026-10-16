# Frente pf3_mecanismos: transferir os mecanismos dos vencedores para outros modelos

Data: out/2026. O dono não quer combinar modelos. Ele quer saber **por que** cada vencedor funcionou e usar essa hipótese para consertar
os modelos que falharam ou ficaram marginais.

Para isso, fiz 12 fundos `pf/fundos/mx_*.py`. Todos usam o mesmo contrato, o mesmo motor (`b3_base.carteira_pf`, `bb_base.episodios`,
`mh_base.livro`, `_ev_pf.simula`), os mesmos custos de varejo e o mesmo IR.

**Regra de escolha, igual para todos.** Cada fundo tem uma grade pequena. A variante escolhida é a de **maior IR dentro da amostra**,
desde que tenha pelo menos 10 negócios no IS (`_mx_comum.escolhe_is`). O OOS aparece nas tabelas só para este caderno: nenhum parâmetro
foi escolhido por ele. Houve uma única exceção à ordem dos passos: em mx_crise_dividendo, a variante de maior IR tinha 2 negócios no IS.
O piso de 10 negócios foi criado nesse momento, já com a tabela da grade na tela (o OOS também estava nela). Ele vale para todos e não
muda nenhuma outra escolha. Mesmo assim, trate o +1,8 desse fundo com essa ressalva.

**Como rodar.** `PYTHONIOENCODING=utf-8 python -W ignore pf/rodar_pf.py um mx_<nome>`. As baterias estão em
`pf/resultados/bateria/mx_*.pkl` e os logs em `pf/resultados/pf3_mecanismos/`. O resumo está em `pf/resultados/pf3_mecanismos.pkl`
(nome, excesso de 20k, excesso de 50k e métricas). O truncamento passou nos 12.

**Bug encontrado e corrigido.** No `mx_fii_panico_vp`, a classificação "FII de papel" era um conjunto fixo montado com todos os informes,
inclusive os futuros. Isso fazia o truncamento falhar. Agora a classificação vem do último informe ENTREGUE até a data. A escolha no IS
não mudou.

## Resultado (pp a.a. sobre o CDI, OOS 2021–26)

| fundo | mecanismo | modelo-base (OOS antes do IR) | IS | 20k antes / depois do IR | 50k antes / depois do IR | IR | PBO | P(bater 3a) | custo 2x | t+2 | sem 10 melhores | hipótese |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| mx_noite_isenta | 4 + 3 | b3_leilao_noite_aud +7,1 (depois do IR +5,6) | +3,4 | **+2,2 / +2,2** | +0,8 / +0,8 | **1,10** | 33% | **98%** | **+1,1** | +1,8 | **+0,9** | **confirmada (robustez, não retorno)** |
| mx_ofertas_desconto | 3 | b3_ofertas_varejo_aud +2,6 | 0,0 | +2,9 / +2,9 | +2,9 / +2,8 | 0,71 | 0% | 92% | +2,9 | +3,2 | 0,0 | rejeitada (o filtro de desconto não ajudou no IS) |
| mx_opa_desconto | 3 | b3_opa_leilao +4,1; rev_opa ≈ +0,5 | +4,3 | +2,6 / +2,6 | +2,6 / +2,6 | 0,38 | 7% | 79% | +2,5 | +0,5 | −2,7 | **rejeitada (o sinal é invertido)** |
| mx_noite_adr | 2 | b3_leilao_noite_aud +7,1 | +17,0 | +6,7 / +5,4 | +6,7 / +5,4 | 0,46 | 1% | 83% | −9,3 | +6,5 | +1,7 | rejeitada (a âncora não acrescenta nada) |
| mx_crise_dividendo | 2 | rev_crise +0,5 (contrarian institucional −15) | +0,4 | +1,8 / +1,8 | +2,3 / +2,1 | 0,23 | 30% | 64% | −0,4 | +1,7 | −3,9 | parcial (pequena e frágil) |
| mx_mineradoras_panico | 2 | rev_mineradoras −12,8 (mh_petroleo +3,0) | −0,5 | +1,3 / +1,3 | +1,3 / +1,2 | 0,17 | 83% | 60% | +1,1 | −0,2 | −4,6 | não confirmada (IS negativo) |
| mx_rebal_pequeno | 3 + 4 | rev_rebal_ibovespa +1,0 | +0,6 | +0,1 / +0,1 | +0,2 / +0,2 | 0,09 | 38% | 57% | −0,1 | −0,3 | −1,0 | rejeitada |
| mx_fii_datacom | 1 + 3 | bb_fii_datacom −2,0 | +7,3 | +0,1 / −0,1 | 0,0 / −0,1 | 0,04 | 69% | 52% | −3,5 | +1,0 | −0,9 | magnitude só no IS |
| mx_vencimento_queda | 1 + 3 | bb_vencimento_opcoes +1,3 | +2,9 | −0,9 / −0,9 | −0,7 / −0,7 | −0,19 | 62% | 37% | −2,3 | −1,2 | −3,4 | magnitude só no IS |
| mx_fii_panico_vp | 2 | bb_fii_panico −1,0 | +5,1 | −1,5 / −1,5 | −1,6 / −1,6 | −0,36 | 19% | 25% | −2,2 | −1,4 | −3,0 | rejeitada (o VP não separa) |
| mx_jcp_dezembro | 1 | bb_dividendo_extra_aud +17,6 (só acima de 2%) | +4,0 | −2,6 / −2,7 | −2,2 / −2,3 | −0,51 | 18% | 16% | −4,3 | −2,6 | −4,6 | **rejeitada (calendário sem tamanho)** |
| mx_followon_tamanho | 3 | rev_followon +3,3 | −3,7 | −3,6 / −3,6 | −3,5 / −3,4 | −0,40 | 41% | 23% | −8,7 | −2,8 | −11,0 | **rejeitada (o sinal é invertido)** |

## Por que os vencedores funcionaram (as 4 hipóteses testadas)

1. **Calendário obriga.** Data-com do dividendo extraordinário, leilão da OPA, carteira do índice.
2. **Pânico + âncora.** O Brent em reais para a PETR4; o preço da OPA para a ação-alvo.
3. **Tamanho do evento.** O dividendo só paga acima de 3–5%.
4. **Ser pequeno.** A tranche de varejo, a small cap na OPA e a isenção de R$ 20 mil.

## Fundo a fundo

### 1. mx_jcp_dezembro (mecanismo 1). Inspiração: bb_dividendo_extra_aud
- **Hipótese.** Em dezembro o calendário fiscal obriga a empresa a declarar o JCP. Se o que paga no vencedor é o calendário, então
  proventos pequenos de dezembro (0,5–3%, abaixo do limiar do vencedor) também deveriam render até a data-com.
- **IS.** JCP com limiar de 0,5% dá IR de 0,98, +4,2 pp e 97 negócios. O IS sobe quando o limiar cai, porque há mais eventos de
  2017–2020.
- **OOS.** −2,6 pp, com 44% de acerto. Em 2024–25 foi de −13 e −6. Os piores negócios são de JCP de 0,7–1,6% (RENT3, DXCO3, AZZA3), em que
  a ação caiu mais que o provento.
- **Lição.** O calendário sozinho não paga. O JCP de dezembro é recorrente e conhecido com meses de antecedência, então ninguém é
  surpreendido e não aparece comprador marginal. O vencedor depende da **surpresa e do tamanho** do provento extraordinário. A data-com
  é só o prazo em que esse comprador aparece.

### 2. mx_fii_datacom (mecanismos 1 + 3). Base: bb_fii_datacom (−2,0)
- **Hipótese.** O comprador da data-com de FII é o varejo de renda, que deveria se concentrar nos FIIs de **maior rendimento mensal**.
  Também testei a pista "k = 3, saída no ex" (+4,1 OOS no caderno pf2_b3), agora decidida no IS.
- **IS.** A seleção por rendimento melhora o IS nas **6 combinações** (por exemplo, k = 5 na data-com: +4,6 → +7,4).
- **Escolha e OOS.** A variante escolhida foi k = 5, saída na data-com, por rendimento. No OOS deu **+0,1 antes do IR e −0,1 depois**.
- **A pista "k = 3 / ex".** No IS ela teve IR de 1,22 (por rendimento) ou 0,65 (por liquidez). Não seria escolhida, e o +4,3 do OOS foi
  sorte da escolha.
- **Lição.** O efeito do calendário no FII existe, mas cabe no spread: com custo 2x vai a −3,5. A magnitude do rendimento separa no IS,
  porque 2019–2020 foi um ciclo de alta de FII de alto rendimento. No OOS, os de maior rendimento foram os de crédito ruim: CACR11 −34%,
  DEVA11 −18%. Rendimento alto no FII é risco de crédito, não tamanho de evento. O "tamanho" certo seria o rendimento *extraordinário*
  contra o habitual do próprio FII.

### 3. mx_vencimento_queda (mecanismos 1 + 3). Base: bb_vencimento_opcoes (+1,3, sem os 10 melhores −3,9)
- **Hipótese.** A venda mecânica do vencimento só deixa marca quando foi grande. Por isso só compro os objetos que caíram 2, 4 ou 6% nos
  5 pregões até o vencimento.
- **IS.** O IR cresce com a queda: 0,31 → 0,25/0,37 → 0,49/0,44 → 0,56/0,55. Escolhida: queda ≥ 6% e k = 1.
- **OOS.** −0,9 pp. É melhor que a cesta inteira com o mesmo motor (−4,6), mas continua negativo.
- **Lição.** Tamanho ajuda dentro de um evento ruim. Ele melhora em 3,7 pp o OOS da regra, mas não cria edge, porque a "venda forçada" do
  vencimento é pequena perto do giro das blue chips. O padrão monotônico no IS e a inversão de nível no OOS mostram que o mecanismo
  certo, aplicado ao fluxo errado, só reduz o prejuízo.

### 4. mx_fii_panico_vp (mecanismo 2). Base: bb_fii_panico (−1,0)
- **Hipótese.** O caderno pf2_b3 diagnosticou que o pânico de FII compra crédito que piorou de verdade. A âncora seria o valor
  patrimonial (VP): só compro se o VP dos 3 últimos informes não caiu (≥ −2%) e, opcionalmente, se P/VP ≤ 0,85 ou 0,95.
- **IS.** Escolhida: queda ≥ 10% em 5 pregões, só FII de papel, sem teto de P/VP. IR de 1,04, mas com só 18 negócios.
- **OOS.** −1,5 pp (20 negócios).
- **Controle.** A mesma regra sem a âncora do VP dá IS +5,1 e OOS −1,5. Com a âncora: +5,3 / −1,3. **A âncora não separa nada.**
- **Exemplo.** HCTR11 e DEVA11 em 2023 tinham "VP 3m −0,8% a +2,3%" e P/VP de 0,43–0,61, e caíram mais 25–31%.
- **Lição.** O VP do FII de papel não é âncora. Ele é marcado pelo próprio gestor, com defasagem de 45 dias, e não reconhece a perda
  antes do mercado. Uma âncora precisa ser um preço que alguém **paga** (oferta, provento, contrato), não uma contabilidade.

### 5. mx_crise_dividendo (mecanismo 2). Base: crise corporativa (rev_crise; contrarian −15% a.a. no institucional)
- **Hipótese.** Um provento já declarado é uma âncora de caixa. A ação que desaba com um provento grande pendente deveria voltar até a
  data-com.
- **IS.** Quase nulo: queda ≥ 5% e provento ≥ 1% dá +0,4 e IR de 0,11. As variantes com menos de 10 negócios no IS ficaram fora.
- **OOS.** +1,8 / +2,3 pp, mas frágil: custo 2x −0,4, sem os 10 melhores −3,9, e 2024–25 em −6,6 e −7,6.
- **Melhores.** BRAP3/BRAP4 em nov/2021 (+23%/+21%, provento de 12,5–13%) e JHSF3 em 2023. É o mesmo negócio do vencedor
  bb_dividendo_extra_aud.
- **Lição.** A âncora de caixa só funciona quando é grande perto do preço (BRAP). Com provento de 1–3%, a queda é a notícia (VIVT3 −16%,
  INTB3 −11%). O mecanismo 2 depende do 3: a âncora precisa ser grande o bastante para limitar a queda.

### 6. mx_noite_adr (mecanismo 2). Base: o vencedor b3_leilao_noite_aud (+7,1)
- **Hipótese.** A noite reverte quando quem vendeu foi forçado, e não informado. Testei duas âncoras:
  - o ADR em Nova York (em reais) caiu menos que a ação na B3, ou seja, venda local;
  - não houve fato relevante na CVM em t−1/t.
- **IS.**
  - Âncora ADR: **pior** que o próprio universo de ADR sem filtro (IS −3,2 e −4,4, contra +4,1).
  - "Sem fato relevante": IS +17,2, contra +18,3 sem âncora nenhuma. Foi a escolhida.
- **OOS.** +6,7 (+5,4 depois do IR), contra +7,2 sem âncora no mesmo código. Continua com a fragilidade do original: custo 2x −9,3.
- **Lição.**
  - A "divergência" ADR × B3 no fechamento de t é o **fuso** (anti-mecanismo): o ADR fecha 1h depois e a ação na B3 converge na abertura
    de t+1, antes da noite que o fundo carrega (t+1 → t+2). A informação já foi gasta.
  - A falta de fato relevante não separa, porque o vendedor forçado da noite reage ao pregão, não ao documento.
  - O edge da noite **não precisa** de âncora. É prêmio de liquidez de quem zera no dia.

### 7. mx_mineradoras_panico (mecanismo 2). Inspiração: mh_petroleo. Base: rev_mineradoras (−12,8)
- **Hipótese.** É o desenho do mh_petroleo transferido: compro VALE3/BRAP4/CMIN3 quando caem muito mais que o minério em reais (TIO=F,
  SGX), e GGBR4/GOAU4/CSNA3/USIM5 quando caem muito mais que o ETF global de aço (SLX).
- **IS.** Negativo nas **8 variantes** (−0,3 a −8,8 pp). A escolhida (z ≥ 2, queda ≥ 20%, só com pânico de mercado) tem IS −0,3.
- **OOS.** +1,3, com PBO de 83% e sem os 10 melhores −4,6. Os ganhos vieram de CSNA3/BRAP4 em 2021–22. O pior foi CSNA3 em set/2021
  (−39% no negócio, −14 pp no fundo): o grupo CSN tinha problema próprio, e não era pânico.
- **Controle sem o filtro de resíduo.** IS −1,9 / OOS +0,2.
- **Lição.** O mecanismo do petróleo não se transfere. O Brent é um preço global líquido e simultâneo, e a PETR4 tem um único fator
  dominante. Minério SGX (contínuo com rolagem, 4h de fuso) e SLX (aço dos EUA, não o aço vendido pela Gerdau/CSN) são âncoras ruidosas.
  As siderúrgicas têm risco de crédito e de controle próprios. Uma âncora só serve se for o preço que realmente determina o valor do
  ativo.

### 8. mx_opa_desconto (mecanismo 3). Base: b3_opa_leilao (+4,1) / rev_opa (≈ +0,5 corrigido)
- **Hipótese.** Na OPA, o tamanho do evento é o desconto contra o preço da oferta. A correção da auditoria foi incorporada: o desconto é
  checado também no preço de execução (limite no leilão de fechamento), com teto de 30%.
- **IS.** **Monotônico ao contrário**: desconto ≥ 0% dá +4,5 (IR 0,39); ≥ 2% dá +2,7; ≥ 4% dá +0,6; ≥ 7% dá 0,0.
- **Escolha e OOS.** Escolhida: ≥ 0%. OOS +2,6, isento. O teto de execução tira o HBOR3, e o número fica entre o rev_opa corrigido e o
  original. AALR3 em 2021 (+80%, 12 pp) carrega o resultado: sem os 10 melhores, −2,7.
- **Lição.** No OPA o desconto mede o **risco do negócio**, não o presente. O ganho vem da correção e da melhora do preço no leilão, que
  todos os alvos recebem. É o caso em que o mecanismo 3 vale para a variável certa (o tamanho do fluxo forçado) e falha na errada (o
  prêmio de risco).

### 9. mx_ofertas_desconto (mecanismo 3). Base: b3_ofertas_varejo_aud (+2,6)
- **Hipótese.** No follow-on, o pedido de reserva com preço máximo (fechamento da véspera da precificação × (1 − Y)) só recebe quando o
  coordenador dá desconto grande. Não é fill de ordem limitada: o preço da oferta é único.
- **IS.** Só 15 follow-ons com varejo de 2014 a 2020 e quase zero de resultado em todas as variantes. Escolhida: sem limite (todos os
  follow-ons).
- **OOS.** +2,9 pp, PBO 0%, custo 2x +2,9 e acerto de 8/8. Mas **três ofertas fazem tudo** (SBSP3 em 2024 +27%, CSAN3 em 2025 +18% e
  CSMG3 em 2026 +17%) e, sem os 10 melhores, dá 0,0.
- **Lição.** O filtro de magnitude não teve amostra para ser testado. O resultado útil é outro: **só os follow-ons** fazem o mesmo que
  "todas as ofertas" (+2,9 contra +2,6) sem o risco de IPO. A tranche de varejo é o mecanismo 4 puro (o pequeno recebe o lote inteiro
  ou o igualitário). Em privatizações e grandes secundárias, o desconto vem do tamanho da oferta, e não é preciso filtrar.

### 10. mx_followon_tamanho (mecanismo 3). Base: rev_followon (+3,3)
- **Hipótese.** A pressão vendedora depois de um follow-on cresce com o overhang: valor da oferta ÷ ADV60, com eventos do dataset da CVM
  que inclui as ofertas restritas. O fundo vende a descoberto com aluguel real e BOVA11 contra.
- **IS.** Negativo em todas as combinações e **pior quanto maior a oferta**: IR de −0,43 (todas), −0,61 (≥ 15 dias) e −0,83 (≥ 30 dias).
- **OOS.** −3,6. O pior negócio é DASA3 em 2023, uma oferta de 632 dias de volume que subiu 57%.
- **Lição.** As ofertas grandes para o giro do papel são **recapitalizações de empresas em dificuldade**. O dinheiro novo tira o risco de
  quebra e a ação sobe. Tamanho de oferta não é tamanho de fluxo forçado: o "vendedor" aqui é a própria empresa, que não está forçada.

### 11. mx_rebal_pequeno (mecanismos 3 + 4). Base: rev_rebal_ibovespa (+1,0)
- **Hipótese.** O impacto da compra passiva é o valor de mercado ÷ giro. O fundo fica com a metade dos entrantes de menor giro (ações
  emitidas do último ITR entregue × preço) ou de menor ADV.
- **IS.** Na seleção por giro o IR foi de 0,52, contra 0,47 de todos (+0,8 contra +1,5 pp). Foi a escolhida.
- **OOS.** +0,1, contra +1,2 de todos os entrantes.
- **Lição.** Com 15 entrantes por ano e R$ 1,3 mil cada, a metade da amostra é ruído. O efeito do Ibovespa é pequeno e espalhado. Não há
  "evento grande" escondido nos entrantes ilíquidos, porque o mercado já antecipa a carteira prévia, que é pública.

### 12. mx_noite_isenta (mecanismos 4 + 3). Base: b3_leilao_noite_aud (+7,1 antes / +5,6 depois do IR)
- **Hipótese.** Se o edge da noite está nas quedas forçadas, um orçamento de **R$ 20 mil de vendas por mês** (isenção de IR da PF) gasto
  só nas maiores quedas captura o ganho por negócio sem IR e com 1/20 do giro.
- **IS.**
  - O limiar alto **não** foi melhor: queda ≥ 3% dá IR de 1,32; ≥ 5% dá 0,67; ≥ 7% dá 0,79.
  - O ticket menor (R$ 2,5 mil, até 8 noites por mês) foi melhor que R$ 5 mil, porque diversifica as noites.
- **OOS (20k).**
  - **+2,2 pp, isento (depois do IR igual).**
  - IR 1,10, P(bater em 3 anos) 98%, placebo p = 0.
  - **Custo 2x +1,1, t+2 +1,8 e sem os 10 melhores +0,9.**
  - Todos os anos foram positivos, menos 2017.
- **OOS com R$ 50 mil.** Os reais são os mesmos, então em pp o ganho cai para +0,8.
- **Lição.** "Ser pequeno" não aumenta o retorno do vencedor (+5,6 depois do IR é mais que +2,2), mas o torna **robusto**. O original
  morre com custo 2x (−1,7) e sem a cauda; a versão isenta sobrevive aos dois, porque cada real de giro vai para a noite de maior queda
  do dia e não paga IR. É o primeiro fundo da pesquisa em que a isenção de R$ 20 mil é o desenho do fundo, e não um acidente das vendas.

## O que a rodada ensina (síntese)

- **Calendário sem surpresa não paga** (mx_jcp_dezembro, mx_fii_datacom, mx_vencimento_queda).
  - O vencedor bb_dividendo_extra não é um efeito de calendário: é **surpresa grande + prazo curto**.
  - Eventos recorrentes (JCP anual, rendimento mensal de FII, vencimento mensal) estão no preço.
  - A magnitude melhora todos eles no IS e não se sustenta no OOS.
- **A âncora tem de ser um preço que alguém paga** (oferta, provento) **e simultâneo** (Brent × PETR4 no mesmo pregão).
  - VP de FII (contábil e defasado), ADR (fuso) e minério SGX/SLX (ruído e outro produto) não servem.
  - Com âncora de caixa grande (BRAP 2021) funciona, e aí o fundo é o vencedor de dividendo outra vez.
- **Magnitude só vale para o tamanho do FLUXO FORÇADO por unidade de liquidez.**
  - Nos casos em que o "tamanho" medido era prêmio de risco, o sinal se inverte: desconto de OPA = risco do negócio; tamanho do follow-on
    = recapitalização.
  - Antes de impor um limiar, perguntar: "o tamanho mede quem é obrigado a negociar, ou o quanto o mercado tem medo?"
- **Ser pequeno é o mecanismo que mais se transfere.**
  - A isenção de R$ 20 mil, como restrição de giro, transformou o fundo mais frágil do top (noite) num fundo menor e robusto
    (custo 2x > 0, sem os 10 melhores > 0, P(bater) 98%).
  - Os follow-ons de varejo (pequeno recebe o lote inteiro) continuam pagando.

## Recomendação
- **Promover a candidato:** mx_noite_isenta.
  - Rende +2,2 pp isento com R$ 20 mil e é o mais robusto da rodada.
  - O orçamento é por CPF. Com R$ 50 mil vale considerar dois CPFs/contas do grupo, o que é operacional e não de modelo.
  - Medir em papel o preço do leilão contra o COTAHIST por 3 meses, como pediu a auditoria do original.
- **Variante útil:** mx_ofertas_desconto com "só follow-ons" (+2,9, mas 3 ofertas fazem tudo). Não somar com b3_ofertas_varejo_aud, que
  é o mesmo negócio.
- **mx_opa_desconto:** confirma o b3_opa_leilao com a correção da auditoria (+2,6 isento) e mostra que filtrar por desconto piora.
- **Descartar:** mx_jcp_dezembro, mx_followon_tamanho, mx_fii_panico_vp, mx_vencimento_queda, mx_rebal_pequeno, mx_fii_datacom e
  mx_mineradoras_panico (IS negativo).
- **mx_noite_adr** é o vencedor de novo, sem ganho: não carregar junto.
- **Próximos testes:**
  - Rendimento *extraordinário* de FII contra o próprio histórico (o tamanho certo no FII).
  - JCP/dividendo de dezembro **acima** do habitual da empresa (surpresa).
  - Âncoras de caixa em outras crises: OPA pendente, recompra anunciada com preço.
