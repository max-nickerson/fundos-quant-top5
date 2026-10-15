# Versão "pessoa física com R$ 20 mil" — instruções para cada fundo

Repositório: a raiz do repositório. Leia `README.md`, `CONTRATO_FUNDO.md`, `comum.py`,
`robustez.py`, o fundo institucional em `fundos/<nome>.py` e o modelo de varejo `varejo/varejo.py` (premissas de custo, câmbio, IR).

Pergunta: o que um grupo de amigos com **R$ 20.000 no total** consegue de fato operar, com corretoras de custo mínimo — IBKR (EUA, acesso
de brasileiro), Clear, Rico, XP, Inter, BTG, Nu (B3), e outras de custo zero/mínimo acessíveis a residente no Brasil — e quanto sobra de cada
estratégia. Se algo só é operável com milhões (lote mínimo, contrato grande demais, instrumento só institucional), diga "não aplicável"
e proponha/teste o substituto de varejo mais próximo.

Para cada fundo de varejo `varejo/fundos/<nome>_varejo.py`:
- Siga o CONTRATO_FUNDO.md (NOME, TESE, BENCHMARK="CDI", INICIO, CORTE iguais ao institucional sempre que os dados permitirem, REGIME,
  PARAMS, GRADE, VIZINHANCA, carrega, excesso, posicoes, negocios) e acrescente:
  - `CAPITAL` padrão R$ 20.000 e parâmetro `capital=` em `excesso(...)` (o motor da carteira vai rodar cada fundo com a fatia dele, ex. R$ 4 mil);
  - `INSTRUMENTOS`: texto curto com o que comprar/vender, em qual corretora, ticker, lote/ação mínima, margem exigida;
  - `APLICAVEL`: True/False e `MOTIVO` (uma frase).
- `excesso(d, capital=CAPITAL, ...)` devolve o excesso diário sobre o CDI em R$, ANTES do IR, já com: custos de varejo (`varejo.py`),
  arredondamento para lotes/ações inteiras com o capital dado (patrimônio nominal constante = capital, em R$), caixa de conta pequena (não
  rende, salvo ETF de T-bill), juros de margem, aluguel, câmbio SEM hedge para dinheiro no exterior (`excesso_brl_sem_hedge`) e o custo de
  remessa (`remessa_diaria`). Se um hedge cambial for viável no tamanho, mostre a variante.
- Os mesmos testes de look-ahead (truncamento) precisam passar: só dados até t.
- Dados novos em `varejo/dados/<nome>/` (só o necessário; fontes públicas; yfinance ok). Scripts de download não fazem parte do repositório (dados já vêm prontos)
.
- Verifique as premissas de custo/regra que forem críticas para o seu fundo (pode pesquisar na web: comissões IBKR para não residentes,
  juros IBKR em contas < US$ 10 mil, tamanhos de contrato CME micro, VXM, XSP, lote mínimo de eurobonds, IOF de remessa vigente em 2026,
  aluguel de BOVA11 para pessoa física, margem/garantia de mini-índice na Clear/Rico). Se a premissa de `varejo.py` estiver errada, NÃO
  altere `varejo.py`: anote no seu módulo, use o valor certo no seu fundo e cite a fonte no relatório final.
- Valide: rodando com capital enorme e custos institucionais o resultado deve se aproximar do institucional (diga quanto).
- Resposta final ≤ 250 palavras: aplicável?, instrumentos, resultado OOS a.a. vs CDI (antes do IR) com R$ 20 mil e com R$ 4 mil,
  o que mais pesou (custo mínimo? câmbio? caixa sem juros? lote?), premissas corrigidas com fonte.

Nota técnica: os módulos de varejo são carregados pelo caminho do arquivo (não como `fundos.x`), com a raiz do repositório e `varejo/` no
`sys.path`; então dentro deles use `import comum`, `import varejo as V` e, se quiser reaproveitar o institucional, `from fundos import mineradoras`.

## ALAVANCAGEM (pedido adicional)
Cada fundo de varejo testa alavancagem 1x, 1,5x, 2x e 5x, sempre do jeito mais realista possível:
- Defina `ALAVANCAGENS` (subconjunto viável de [1, 1.5, 2, 5]) e `MOTIVO_ALAV` (por que as outras não são viáveis), e aceite `alavancagem=` em `excesso`.
- Como alavancar de verdade: futuros (B3: mini-índice WIN, mini-dólar WDO; CME micro: MES, MNQ, M6E, M6A, MGC, MHG, SIL, VXM...) ou
  margem de ações na IBKR (Reg T: até 2x overnight; portfolio margin exige ≥ US$ 110 mil → não disponível). ETFs alavancados (2x/3x) só se
  forem o veículo natural — e aí modele o decaimento real (use o preço do ETF).
- Custos da alavancagem: juros de margem IBKR (T-bill + 1,5% a.a. na faixa pequena), financiamento embutido no futuro, garantia na B3
  depositada em Tesouro Selic/CDB rende CDI (na IBKR, margem em dinheiro de conta pequena não rende).
- Contratos/ações INTEIROS com o capital dado (ex.: 1 WIN ≈ R$ 25–28 mil de nocional; MES ≈ US$ 30 mil) — se a alavancagem pedida não cabe
  em contratos inteiros, use o mais próximo e reporte a alavancagem efetiva média.
- Chamada de margem: se o patrimônio cair abaixo da margem de manutenção, a posição é reduzida à força no fechamento (perda realizada,
  com custo); se o patrimônio zerar, o fundo QUEBRA e fica em caixa/CDI dali em diante (o retorno de −100% entra na série). Use as margens
  de manutenção reais (CME/B3/IBKR) — cite a fonte.
- Reporte por alavancagem: ativo OOS a.a., vol, pior queda, nº de chamadas de margem, se quebrou (e quando).
