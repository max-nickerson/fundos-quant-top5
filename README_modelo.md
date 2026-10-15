# Fundos quant — top 5 (com dados, código e robustez)

Cinco estratégias que sobreviveram a uma pesquisa com **109 estratégias** (Brasil, EUA, Europa, Ásia, fronteira; ações, juros, moedas,
crédito, commodities, opções e eventos) e a **três auditorias** de bugs e vieses. Tudo aqui roda **sem internet**: os dados já estão em
`dados/`, o código é curto e comentado, e um comando reproduz todos os números e gráficos.

> Pesquisa, não recomendação de investimento. Resultados simulados com custos estimados; o passado não garante o futuro.

## Como rodar

```bash
pip install -r requirements.txt
python rodar.py              # os 5 fundos + carteira combinada (~10–20 min)
python rodar.py --rapido     # leque de parâmetros com 20 sorteios
python rodar.py mineradoras  # um fundo só
```

Saídas em `resultados/`: um painel `.png` por fundo, `carteira.png` e uma pasta por fundo com todos os números em CSV
(métricas, ano a ano, grade, leque, custo/atraso, Monte Carlo, testes de look-ahead, negócios, contribuição por ativo, concentração,
regime, walk-forward).

## Os 5 fundos

| Fundo | Tese de mesa | Benchmark | Fora da amostra desde |
|---|---|---|---|
{FUNDOS}

## Resultado e robustez (fora da amostra, líquido de custos; sem taxa de gestão/performance; despesas de 0,15% a.a.)

{TABELA}

**Como ler:**
- *ativo* = retorno acima do benchmark (pp ao ano). *IR* = ativo / tracking error.
- *PBO* = probabilidade de a escolha de parâmetros ser overfitting (CSCV, Bailey et al.). Abaixo de 30% é bom.
- *Sharpe deflacionado* = probabilidade de o IR verdadeiro ser > 0 descontando quantas coisas foram testadas — na grade do fundo e,
  mais duro, considerando as 109 estratégias da pesquisa inteira.
- *Leque* = 60 sorteios contínuos dos parâmetros ao redor dos escolhidos (ex.: janela 63 → 45–90 dias): faixa 5%–95% do ativo.
- *Monte Carlo* = bootstrap em blocos de 21 dias do excesso fora da amostra: chance de bater o benchmark em 3 anos.
- *Placebo* = as mesmas posições deslocadas no tempo; p baixo = o *timing* do sinal importa. Em estratégias que ficam sempre
  posicionadas (carry, venda de vol) o p alto é esperado: o retorno vem de estar posicionado, não do timing.
- *Walk-forward* = re-escolhe a variante da grade todo 1º de janeiro usando só o passado.
- *Sem os 10 melhores* = ativo fora da amostra tirando os 10 negócios que mais ganharam.

### Carteira combinada
Pesos pelo inverso da volatilidade de cada fundo no **seu** período de calibração, alavancada para 6% de vol (medida antes do corte).
{CARTEIRA}

## Painéis

Cada painel mostra: cota vs benchmark com o **leque de parâmetros** (faixas 5–95% e mín–máx) e a grade original; queda; ativo ano a ano;
distribuição do leque; custo (0–3x) e atraso (t+1 a t+6); Monte Carlo de 3 anos; ativo em 12 meses móveis; placebo; 10 melhores e
10 piores negócios; contribuição por ativo.

![carteira](resultados/carteira.png)
{PAINEIS}

## Checagens de viés e look-ahead

- **Truncamento**: cada fundo é rodado com TODOS os dados apagados depois de uma data T (3 datas); o excesso até T−1 tem de ser idêntico.
  Os regimes (VIX, S&P, HYG/IEF, Ibovespa, stop) passam pelo mesmo teste com os dados comuns cortados. Resultado em
  `resultados/*/teste_lookahead_truncamento.csv` e `resultados/teste_lookahead_regimes.csv` (todos com diferença 0).
- **Execução**: decisão no fechamento de t, execução no fechamento de t+1 (+ atraso testado até t+6); regimes de mercado com sinal de t−2.
- **Sobrevivência**: ações BR do COTAHIST completo (inclui empresas em recuperação judicial e deslistadas); ETFs e índices sem esse viés;
  eurobonds com preço "vivo" e filtro de liquidez.
- **Limpezas de dado que olham o futuro** (só para corrigir erros de cotação, não para sinal), feitas na exportação e documentadas no
  topo de cada módulo: câmbio do Yahoo (erros de 100x que se desfazem em até 8 dias), CPER (prints errados em 2014–15), proventos/desdobramentos B3.
- **Premissas conhecidas** (documentadas nos módulos): carry do real antes de 2019 = Selic − Fed funds − 1,07 pp (spread medido depois de
  2019); swap de variância sintético vendido a VIX−1 (com VIX−2 a estratégia morre); hedge cambial dos eurobonds pelo dólar futuro da B3.

## O que NÃO funcionou na pesquisa (para não repetir)
Box/conversão (≈ CDI), arbitragem ADR/BDR/units/ETF com execução no dia seguinte, captura de dividendos/JCP, venda de put sem hedge de beta
(é só beta), carry agro B3 vendido, contrarian CFTC, prever juros (Brasil e EUA), ML semanal em ações, collar, recompra, lock-up, insiders e
merger arb com dados gratuitos (viés de sobrevivência), PEAD EUA/Ásia, base cripto (risco de contraparte e margem zeram o alfa).

## Estrutura

```
comum.py        CDI, calendário, carteira (execução t+1), vol-alvo, regimes, métricas
robustez.py     toda a bateria de robustez (genérica para qualquer fundo)
graficos.py     painéis
rodar.py        roda tudo e imprime
fundos/         um arquivo por fundo (tese, parâmetros, sinal, negócios)
dados/          dados prontos (fontes públicas: B3, BCB, Yahoo Finance, CBOE, FINRA/TradingView, BIS)
resultados/     saídas
CONTRATO_FUNDO.md  como escrever um fundo novo que roda na mesma bateria
```

Fontes dos dados: B3 (COTAHIST, ajustes de futuros), Banco Central (SGS), BIS (juros de política), Yahoo Finance (ETFs, índices, câmbio),
CBOE (VIX), FINRA/TradingView (preços de eurobonds). Verifique os termos de uso de cada fonte antes de redistribuir.
