# Rodada PF — fundos para pessoa física com R$ 20–50 mil (leia tudo)

## O "fundo"
Um grupo de amigos com **R$ 20 mil a R$ 50 mil**, operando como UM fundo em todas as contas que pessoa física residente no Brasil abre:
IBKR (EUA; futuros CME micro, opções, ETFs, ações, FX), Clear, Rico, XP, BTG, Inter, Nubank, Genial, Toro (B3: ações, fracionário, ETFs,
FIIs, BDRs, opções, mini-índice WIN, mini-dólar WDO, agro CCM/BGI/ICF/SJC, DI1, aluguel), Tesouro Direto, debêntures/CRI/CRA/CDB/LCI/LCA
nas plataformas (lotes a partir de ~R$ 1 mil), cripto em corretoras brasileiras. **Caixa sempre em R$ no CDI** (Tesouro Selic/LFTS11/CDB
liquidez diária, inclusive como garantia na B3). Na IBKR fica **só o necessário** (margem ou patrimônio Reg T) — só esse saldo perde o CDI
e fica exposto ao dólar. Benchmark: **CDI** (e CDI depois de 15% de IR).

O que o dono pediu (vale para tudo): pensar como gestor de mesa com 30+ anos (tese concreta, hedge, venda a descoberto quando confiante,
"comprar o PU que vai subir", commodity como hedge da ação, ir contra a manada quando faz sentido, mercados pouco arbitrados — e aqui,
principalmente, **edges que só existem PORQUE o capital é pequeno**: papéis ilíquidos, lotes pequenos, fracionário, isenções de IR de pessoa
física, ofertas de varejo, prêmios que institucionais não conseguem pegar). Regime de mercado quando fizer sentido econômico para a
estratégia. Nada de "é porque é momentum/baixa vol": explicar com os NEGÓCIOS que geraram o retorno.

## Código e dados
- Repositório: a raiz do repositório. Leia `README.md`, `CONTRATO_FUNDO.md`, `comum.py`,
  `robustez.py`, `pf/pf.py` (motor PF: contratos inteiros, margem, conta no exterior só com o necessário, IR por classe) e
  `varejo/README.md` + `varejo/MAPA_ATIVOS_*.md` (o que dá e o que não dá no varejo, com fontes).
- Pesquisa anterior (109 estratégias): os cadernos da pesquisa institucional (fora deste repositório) (DIARIO.md primeiro) e código
  `quant/fundos/ideias_*.py`. Dados brutos já baixados: `quant/fundos/dados/` e `quant/dados/` (COTAHIST completo com RJ em
  `b3_acoes_cotahist.parquet`, opções B3 com bid/ask, futuros B3 financeiros e agro, Tesouro Direto com PU de compra e venda, debêntures SND,
  balcão B3, FII CVM, IPE/CVM, Focus, BIS, Yahoo ETFs/índices/FX/commodities, CFTC, cripto).
- Cada fundo novo: `pf/fundos/<frente>_<nome>.py` seguindo o CONTRATO_FUNDO.md + extras PF:
  - `excesso(d, capital=20000, custo_mult=1, lag=0, regime=REGIME, alavancagem=1, **params)` → excesso diário sobre o CDI (antes do IR),
    em R$, calendário `comum.DIAS`. **Dinheiro aplicado em ativo à vista (ações, FIIs, títulos) NÃO rende CDI** — use retorno do ativo
    menos CDI nessa parcela; margem em Tesouro Selic rende CDI; saldo na IBKR usa `pf.custo_conta_exterior`.
  - `classes_ir(d, capital=20000, **params)` → dict classe → P&L diário em R$ (para `pf.apos_ir_por_classe`), ou `CLASSE_IR = "acoes"` etc.
  - `INSTRUMENTOS` (onde, ticker, lote, custo), `APLICAVEL` + `MOTIVO`, `ALAVANCAGENS` (subconjunto viável de [1, 1.5, 2, 5]) + `MOTIVO_ALAV`.
  - Contratos/ações INTEIROS para o capital dado; custos de varejo reais (corretagem zero na B3 ≠ custo zero: emolumentos, spread, fracionário,
    aluguel 0,5% por contrato + taxa ao doador; IBKR US$ 0,35 mínimo; remessa IOF 1,1% ida / 0,38% volta + spread).
  - Datas de evento = data de DIVULGAÇÃO. Execução t+1. Teste de truncamento (sem look-ahead) tem que passar.
  - Corte OOS: 2021-01-01 (dados ≥ 2012) ou 2023-01-01 (dados 2019+). Grade pequena com sentido econômico; regime só se fizer sentido.
- Para cada fundo rode a bateria (`robustez.bateria` com `excesso` já fixado em capital=20000, ex. via lambda) e reporte: OOS a.a. vs CDI antes e
  depois do IR, IR, PBO, P(bater), leque, custo x2, t+2, truncamento, melhores/piores negócios, quem trouxe o retorno; e o mesmo com R$ 50 mil.
- Salve `pf/resultados/<frente>.pkl` (lista de dicts com nome, excesso 20k, excesso 50k, métricas) e escreva o caderno
  `pf/pesquisa/<frente>.md` (tese, implementação, dados, resultado, 10 melhores/piores negócios, o que deu certo e POR QUÊ, o que deu errado,
  bugs, próximos passos). Não altere `comum.py`, `robustez.py`, `pf/pf.py` (anote premissas corrigidas no seu módulo, com fonte).
- Regras anti-autoengano: Sharpe > 1,5 = bug até prova em contrário; sobrevivência; proventos; preços não simultâneos; marca parada;
  rolagem de futuros contínuos do Yahoo (use ETF ou trate o roll); posição não marcada a mercado (box/termo foram artefatos).
- Resposta final ≤ 350 palavras: tabela (fundo, aplicável?, OOS vs CDI antes/depois do IR com R$ 20 mil e R$ 50 mil, IR, PBO, P(bater)) e as
  2–3 ideias mais promissoras com a razão concreta (negócios).
