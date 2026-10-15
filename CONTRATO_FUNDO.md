# Contrato de um módulo de fundo (`fundos/<nome>.py`)

Objetivo do repositório: qualquer pessoa clona, roda `python rodar.py` e reproduz tudo, SEM internet, só com `dados/`.
Código SIMPLES e LEGÍVEL (português, comentários curtos explicando a tese de mesa), sem dependência de outros projetos.
Dependências permitidas: numpy, pandas, pyarrow, matplotlib, scipy.

Cada `fundos/<nome>.py` define:

```python
NOME = "Carry de moedas G10 + emergentes"
TESE = "uma frase de mesa: o que compramos/vendemos e por quê"
BENCHMARK = "CDI"              # chave de comum.BENCH
INICIO, CORTE = "2010-01-01", "2021-01-01"   # CORTE = início do fora da amostra
REGIME = "dd_stop"            # regime escolhido no IS (ou "nenhum"); aplicado com comum.aplica_regime
CUSTO_TROCA = .001            # custo de liga/desliga do regime
PARAMS = {...}                # parâmetros escolhidos no IS (os do fundo auditado)
GRADE = {...}                 # grade discreta original usada na escolha (para PBO / % de variantes)
VIZINHANCA = {...}            # para o "leque": cada parâmetro numérico -> (mínimo, máximo) contínuo plausível ao redor do escolhido
                              #   (ex.: janela 63 -> (45, 90)); inteiros são arredondados; não-numéricos ficam fixos

def carrega() -> dict          # lê dados/<nome>/... (csv ou parquet); todo DataFrame/Series indexado por data (DatetimeIndex)
                               #   ou com coluna "data" (formato longo). NADA de internet.
def excesso(d, custo_mult=1, lag=0, regime=REGIME, **params) -> pd.Series
                               # excesso diário sobre o CDI em R$, calendário comum.DIAS, líquido de custos (custo_mult multiplica
                               #   TODOS os custos), execução t+1+lag, regime aplicado no fim via comum.aplica_regime(e, regime, CUSTO_TROCA*custo_mult)
def posicoes(d, **params) -> (W, R)     # pesos-alvo (decididos em t) e retornos em excesso por ativo — para atribuição
def negocios(d, **params) -> pd.DataFrame
                               # um negócio por linha: ativo, lado (+1/-1), entrada, saida, dias, retorno_%, contrib_pp (contribuição ao PL em pp)
```

Regras:
- `carrega()` devolve só dados BRUTOS de mercado (preços, taxas, eventos com DATA DE DIVULGAÇÃO); todo sinal é calculado dentro de `excesso`
  só com dados até t (rolling, shift). O teste de look-ahead do repositório corta TODOS os dados numa data T e exige que o excesso até T−1
  não mude.
- Defaults de `excesso(d)` = PARAMS e REGIME (rodar `excesso(d)` reproduz o fundo).
- Se o fundo veio de outra base de código, valide que ele reproduz a série original (excesso bruto sobre o CDI): meta de correlação
  diária > 0,99 e diferença de excesso a.a. fora da amostra < 0,3 pp. Se não bater, explique por quê no topo do módulo.
- Dados em `dados/<nome>/`, só o necessário, idealmente < 30 MB por fundo (parquet com compressão para painéis grandes, csv para séries pequenas).
  Os scripts de exportação dos dados não fazem parte do repositório (os dados já vêm prontos).
- Use `comum.py` (carteira, vol_alvo, mensal, brl, aplica_regime, CDI, DIAS...). Não altere `comum.py`; se precisar de algo novo, coloque no seu módulo.
