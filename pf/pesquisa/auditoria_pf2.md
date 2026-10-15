# Auditoria red team PF2: os candidatos novos ao top 5 (R$ 20–50 mil)

Data: out/2026. Escopo: os candidatos novos de `pf/resultados/ranking_pf.csv` (rodada PF2) e o bug do VLMO.
Todos os números saem de código. Os scripts estão em `pf/pesquisa/_aud2_*.py`, com os utilitários de `_aud_util.py`.
Métrica: excesso OOS sobre o CDI, em pp a.a. "Depois do IR" segue a regra do `rodar_pf` (para ações, conta a isenção de R$ 20 mil de vendas no mês).
Versões corrigidas (mesmo contrato, rodadas com `rodar_pf.py um`, truncamento ok):
- `fundos/bb_dividendo_extra_aud.py`
- `fundos/fu_agro_spread_aud.py`
- `fundos/bb_insider_small_aud.py`, junto com o utilitário `fundos/_texto_cvm.py`

Os vereditos entraram no dicionário `AUDITORIA` de `rodar_pf.py`, e o ranking foi refeito.

## Vereditos

| fundo | original antes IR 20k / 50k | original depois IR 20k / 50k | **corrigido antes IR 20k / 50k** | **corrigido depois IR 20k / 50k** | veredito |
|---|---|---|---|---|---|
| bb_dividendo_extra | 10,9 / 12,3 | 9,8 / 10,3 | **17,6 / 19,1** (universo completo, ADV ≥ R$ 5 mi); conservador ADV ≥ R$ 20 mi: 10,1 / 11,3 | **14,4 / 15,5**; conservador **8,3 / 9,3** | APROVADO COM CORREÇÃO |
| fu_agro_spread | 11,7 / 4,7 | 9,6 / 3,9 | **9,4 / 3,8** (entra só com o H+1 negociando; meio spread de R$ 0,20/saca) | **7,6 / 3,1** | APROVADO COM CORREÇÃO (frágil, satélite) |
| jx_wdo_panico | 6,8 / 2,8 | 5,6 / 2,7 | IS −0,9; as 8 variantes da grade perdem no IS | expectativa ≈ 0 | REPROVADO |
| fu_eurex_micro | 1,7 / 2,2 | 1,7 / 2,2 | sem ago/2024: ≈ +0,3 | ≈ +0,3 | REPROVADO |
| lg_combo_regime | 2,9 / 2,9 | 2,1 / 2,1 | custo 2x: −2,5; t+2: −1,6 | < 0 | REPROVADO |
| lg_b3_etf_bdr | 1,6 / 1,6 | 1,4 / 1,4 | sem XINA11: **+0,3** (custo 2x −0,2) | ≈ +0,2 | REPROVADO |
| op_wheel | 6,2 / 3,1 | 5,1 / 2,5 | opções sozinhas: −0,3 pp **no total** do OOS | ≈ 0 | BETA |
| op_copom | 4,4 / −3,1 | 3,6 / −3,1 | 8 negócios, walk-forward −56 | — | REPROVADO |
| cr_eventos | 19,5 / 19,5 | 15,2 / 15,2 | OOS sem 2025: **−4,2** | < 0 | REPROVADO |
| cr_panico | 0,5 / 0,5 | 0,5 / 0,5 | — | 0,5 | REPROVADO (irrelevante) |
| bb_insider_small | −1,6 / −2,2 | −1,6 / −2,2 | **idêntico** (o bug não existia) | −1,6 / −2,2 | REPROVADO |

---

## 1. bb_dividendo_extra (`_aud2_div.py`, `_aud2_div_b.py`, `_aud2_div_c.py`, `_aud2_div_d.py`)

### (a) Sobrevivência: reconstruída, e o viés é para baixo, não para cima

**Como o universo foi reconstruído:**
- As 103 companhias do `arb_proventos` são membros do Ibovespa, atuais e alguns antigos: SULA, ENBR, BRML, LAME, BTOW, KROT e outros.
- Busquei na mesma API da B3 (`GetListedCashDividends`) os proventos de **todas** as 527 raízes do COTAHIST. A API devolve também as companhias deslistadas.
- Resultado: **302 companhias a mais** e 16.418 proventos, salvos em `pf/dados/auditoria/proventos_b3_extra.parquet`.
- 123 raízes ficaram sem resposta. A maioria trocou de código: ESTC→YDUQ, TIMP→TIMS, DTEX→DXCO, ALSO→ALOS.
  - Esses casos foram tratados pelo CNPJ (`mapa_cnpj`): o provento vai para o ticker do mesmo CNPJ que tinha preço na data-com.
  - Também pelo CNPJ, a entrega IPE é casada com qualquer raiz da companhia.
  - Ficaram de fora casos como CESP e LIGT.

**O que o universo completo mostra:**
- **Sem filtro de liquidez, o OOS vai a +31,6 pp**, mas é frágil: custo 2x dá +1,7 e t+2 dá +9,0.
- Esse ganho vem de micro caps com "febre de dividendo" do varejo e fechamentos de 1 a 30 negócios:
  - MERC4: +48% em 2 pregões até a data-com e −20% no ex.
  - CEEB3: +27%.
  - BMIN3: −37% em 1 pregão.
  - BOAS3: +51%, com um salto de +48% em 19/12/2022 sem relação com o provento.
- Preço executável (compra no ask, venda no bid do COTAHIST): corrige só −1,65 pp a.a. no universo sem filtro, quase todo no grupo de ADV < R$ 1 mi. No original, a correção é de −0,18.

**Versão auditada (ADV ≥ R$ 5 mi na véspera da aprovação):**

| teste | 20k | 50k |
|---|---|---|
| OOS antes do IR | **+17,6** | **+19,1** |
| depois do IR (ranking) | **+14,4** | **+15,5** |

Outros testes da bateria:
- IR 1,25; PBO 0,4%; placebo p = 0.
- Custo 2x: +11,4. t+2: +9,9. Walk-forward: +15,8. Sem os 10 melhores: +10,4.
- Truncamento ok.

**Deslistadas contra listadas (OOS, 20k):**

| grupo | negócios | retorno médio |
|---|---|---|
| deslistadas | 18 + 32 | +1,3% e +2,4% |
| listadas | 130 + 222 | +1,0% e +1,5% |

As que morreram rendem **igual ou mais**. A sobrevivência não inflou o original: a restrição às 103 companhias *subestimou* o resultado.

**Ressalva:** o filtro de R$ 5 mi foi escolhido por mim depois de ver o universo sem filtro. Faixa honesta:
- ADV ≥ R$ 20 mi (≈ blue chips, como o original): **+10,1 / +11,3 antes do IR e +8,3 / +9,3 depois do IR**.
- ADV ≥ R$ 5 mi: +17,6 / +19,1.

### (b) Data do sinal
- O IPE/CVM não tem hora, só a `Data_Entrega`. O sinal é a 1ª entrega sobre proventos entre a aprovação − 3 dias e a data-com.
- A execução é no **fechamento de t+1**. Um aviso entregue à noite em t é executado no fechamento do dia seguinte, sem look-ahead.
- Teste estrito, exigindo entrega ≥ aprovação: a diferença soma 0,018 em 12 anos, ou seja, nula.
- Dos 3.972 eventos: 3.346 têm entrega no dia da aprovação, 533 depois (mediana de 1 dia) e 93 antes.

### (c) Data-com e provento
**Regra B3:** a data-com é o último pregão em que quem **compra** tem direito. Quem vende nesse pregão, inclusive no leilão de fechamento, entrega a ação "com" e **não recebe** o provento. A liquidação em D+2 não muda isso: o direito segue o negócio.

**O código está certo:**
- `fim = data-com − 1` decide a venda, que é executada no fechamento de t+1, ou seja, **no fechamento da data-com**.
- A PF vende pelo preço "com" e não credita o provento.
- Conferido negócio a negócio: o retorno acumulado (R) bate com o preço bruto em 99% dos negócios. Diferença média de 0,03%; 8 de 1.071 negócios com diferença > 0,5%, porque o Yahoo antecipou o provento (TIMS3, PFRM3, VULC3).
- Limite superior desse resíduo: 0,13 pp a.a. no original e 0,6 pp no universo completo.

**JCP:** na versão "com" a PF não recebe, então não há IR na fonte. Na variante "ex", o código já desconta 15% do JCP.

### (d) Concentração e custos (versão auditada)
- Capital investido: médio 34%, p95 100%, máximo 105% (o motor limita ao caixa). Em 27% dos dias há 3 ou mais posições.
- Lucro OOS concentrado em poucos papéis: BOAS3 10,3, MRFG3 9,0, BRAP4 8,1, PETR4 7,9 e PETR3 6,0, de 111 pp ao todo em 122 papéis.
- **Decaimento por ano:** 2021 +23,5, 2022 +15,8, 2023 +30,7, 2024 +8,5, 2025 +8,8, 2026 +2,6 (até out).
- Vendas acima de R$ 20 mil no mês: em 49% dos meses OOS com 20k e em 77% com 50k. A isenção é parcial.

**Veredito:** APROVADO COM CORREÇÃO. É o único candidato com efeito monotônico no tamanho do provento, um comprador forçado pelo calendário e robustez de custo e atraso. Planejar com a faixa conservadora (**+8 a +9 pp depois do IR**) e acompanhar o decaimento de 2024–26.

## 2. fu_agro_spread (`_aud2_agro.py`, `fundos/fu_agro_spread_aud.py`)

**Dados:** o boletim por vencimento é real: o P&L vem do ajuste menos o ajuste anterior de cada contrato, sem rolagem.

**Liquidez do março seguinte (H+1):**
- **O H+1 não negociou nenhum contrato nos 5 primeiros pregões de março em 2018–2025.** Só 49% dos dias de março têm negócio.
- Contratos em aberto no começo de março: 19 a 650.
- A entrada original é feita no ajuste **teórico** da curva B3. Na saída (fim de agosto) há negócio todos os anos.

**Correção:**
- Entrada só depois do 1º pregão da janela em que o H+1 negociou pelo menos 5 contratos.
- Custo por lado: H+1 com R$ 91,50/contrato (meio spread de R$ 0,20/saca); U com R$ 15. O boletim não traz bid/ask, então essa é uma hipótese conservadora.
- Ponto de empate: o ganho bruto médio é de 8,6 pp/ano com 20k. Meio spread de R$ 0,50/saca por perna custaria 4,5 pp.

**Resultado corrigido:**

| teste | 20k | 50k |
|---|---|---|
| OOS antes do IR | **+9,4** | **+3,8** |
| depois do IR | **+7,6** | **+3,1** |

- IR 0,69; **PBO 33%**; **walk-forward −1,9**; custo 2x +8,0; t+2 +9,8; placebo p = 0,15.

**Escolha depois do fato:**
- A tese inicial era o lado +1 (comprar o setembro): CCM +1 dá IS −9,0 e OOS −12,8.
- O IS inverteu o sinal, e a história do "produtor vende ao longo da janela" foi escrita depois.
- Safra a safra (versão corrigida, pp com 20k): 2018 +2,8, 2019 −3,2, 2020 −12,4, 2021 +14,9, 2022 +24,7, 2023 +12,5, 2024 +0,9, 2025 +6,2, 2026 +16,2.
- Média +7,0, desvio 11,3, **t = 1,8 com 9 safras**. Não é significativo depois de escolher entre 4 produtos e 2 lados.
- Entrando no mês 3 há 8/9 safras positivas. Entrando nos meses 4 a 8, a proporção cai para 8/9, 6/9, 6/9, 3/9 e 5/9. O efeito está no começo da janela, justamente onde o H+1 não negocia.

**Margem e risco:**
- A margem fica em Tesouro Selic, sem custo no modelo. Não consegui verificar a margem de spread no CORE da B3.
- O risco real é o ajuste diário dentro da safra: queda máxima do spread de R$ 1,1 mil a 5,6 mil por spread. Em 2022 foi −28% de R$ 20 mil.

**Veredito:** APROVADO COM CORREÇÃO, mas frágil. Entrar no máximo como satélite de 1 spread, nunca com peso cheio no top 5.

## 3. jx_wdo_panico (`_aud2_wdo.py`)

**A regra não foi validada no IS:**
- **As 8 variantes da grade são negativas no IS (2008–20)**, de −0,8 a −5,7, e todas positivas no OOS. Isso é regime, não regra.
- A escolhida (z 2, 21 dias, VIX) dá IS −0,9.

**A "dependência de Selic alta" não se sustenta:**

| período | negócios com Selic ≥ 10% | soma |
|---|---|---|
| IS | 12 | **−17,0 pp** |
| OOS | 8 | +33,4 pp |

**Risco do contrato inteiro:**
- 1 WDO ≈ 2,5x R$ 20 mil.
- Pior alta do dólar nos 21 pregões depois de um sinal: +28% (set/2008). Com o nocional de hoje, isso seria cerca de −70% de R$ 20 mil (−28% de R$ 50 mil).
- Fev/2015 (+12,7%): o negócio real perdeu −15,3 pp.

**Veredito:** REPROVADO. É carry de real condicional ao regime de 2021–26, não a reversão de um vendedor forçado.

## 4. Checagens rápidas
- **fu_eurex_micro:** 10 negócios OOS. Ago/2024 sozinho vale 8,1 pp do total de 21,8. Sem esse negócio e descontado o custo da conta no exterior, fica em ≈ +0,3 pp a.a. Sem os 10 melhores: −2,1. **REPROVADO.**
- **lg_combo_regime:** custo 2x −2,5 e t+2 −1,6. O edge de noite cabe em 1 a 2 bps. **REPROVADO.**
- **lg_b3_etf_bdr:** XINA11 traz **1,33 de 1,59 pp a.a.** (14 noites, +1,1% cada). A "noite" do XINA11 contém o pregão chinês inteiro, então é direção, não leilão. Sem XINA11: +0,29, e com custo 2x: −0,19. ASIA11 não mexe. **REPROVADO.**

## 5. Vereditos já indicados pelos agentes (confirmados)
- **op_wheel:**
  - Por perna (OOS): ações +44,3 pp (PETR 20,1, VALE 16,1, ITUB 8,1), calls −2,6, puts +2,3. **As opções somam −0,3 pp em 6 anos.**
  - Regressão OOS contra Ibovespa − CDI: beta 0,28 (t = 8), "alfa" de 5,7 (t = 2,1). Esse alfa é a escolha de PETR/VALE/ITUB, igual ao db3_cc_isenta.
  - **BETA.**
- **op_copom:**
  - 8 vendas de opção de Copom de cauda, todas entre out/2025 e ago/2026, todas vencedoras (+0,4 a +5,3 pp).
  - Nenhum negócio no IS (IR IS indefinido), walk-forward −56.
  - Vender cauda com 8 acertos em 10 meses não mede o risco. **REPROVADO.**
- **cr_eventos:**
  - Por ano (pp): 2023 −9,6, 2024 −2,5, **2025 +80,2**, 2026 +4,6. **OOS sem 2025: −4,2.**
  - É a venda a descoberto offshore de listagens novas num único ano de altcoins caindo. **REPROVADO.**
- **cr_panico:**
  - A escolhida (btceth 20%/2 dias) dá +0,5 pp.
  - A "boa" (top20 15%/2 dias, +28 OOS) tem IS −4,6, e os vizinhos top20 vão de −8 a −32 no OOS. É beta de altcoin. **REPROVADO.**

## 6. "Bug" do VLMO (`fundos/_texto_cvm.py`, `fundos/bb_insider_small_aud.py`)
- **Não há corrupção no arquivo.** `cvm_vlmo.parquet` tem "Compra \xe0 vista", isto é, "Compra à vista" em Unicode correto:
  - zero caracteres U+FFFD;
  - zero mojibake em `Tipo_Movimentacao`.
- O "�" é o console do Windows (cp1252) imprimindo.
- O código PF casa por regex com curinga (`( . vista)?`, `A..es`), e o código institucional (`ideias_eventos_br.ev_insider`) casa pelo literal UTF-8 (116.598 linhas). Os dois **acham** os eventos.
- Mesmo assim, ficou o utilitário `_texto_cvm.normaliza`: desfaz mojibake latin-1/utf-8, troca U+FFFD e tira acentos. `ler_csv_cvm` tenta utf-8, depois cp1252 e depois latin-1.
- A versão `bb_insider_small_aud` usa casamento exato normalizado. Dá **as mesmas 11.048 companhias-mês (4.500 com compra líquida), com diferença 0,0**.
- `rodar_pf.py um bb_insider_small` e `um bb_insider_small_aud` dão o mesmo resultado:
  - **−1,60 / −2,22 pp antes do IR; −1,58 / −2,19 depois do IR.**
  - IR 0,02, PBO 15%, sem os 10 melhores −11,3.
- O fundo é ruim por si, não por bug. **REPROVADO.**

## Ranking depois da auditoria (nota do `rodar_pf.py ranking`)

| posição | fundo | depois do IR |
|---|---|---|
| 1 | **bb_dividendo_extra_aud** | +14,4 / +15,5 |
| 2 | db3_trava_bova | |
| 3 | b3_opa_leilao | |
| 4 | rev_opa | |
| 5 | **fu_agro_spread_aud** | +7,6 / +3,1 |
| 6 | rev_debentures | |
| 7 | b3_leilao_noite_aud | |

Os originais substituídos e os reprovados saíram da nota.
