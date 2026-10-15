# Rodada pessoa física: R$ 20–50 mil, todas as contas como um fundo

Um grupo com R$ 20 a 50 mil opera como UM fundo em todas as contas de pessoa física (IBKR, Clear, Rico, XP, Tesouro Direto,
plataformas de renda fixa). **Caixa sempre em R$ no CDI** (inclusive a garantia na B3); na IBKR fica só a margem necessária.
Contratos e ações inteiros, custos e aluguel de varejo, IR por classe (benchmark: CDI e CDI depois de 15% de IR).
Motor: [`pf.py`](pf.py) · regras das frentes: [`BRIEF_PF.md`](BRIEF_PF.md) · executor: [`rodar_pf.py`](rodar_pf.py).

```bash
python pf/rodar_pf.py top5 b3_leilao_noite_aud b3_opa_leilao mh_petroleo b3_ofertas_varejo_aud rev_rebal_ibovespa   # usa as baterias salvas
python pf/rodar_pf.py um b3_leilao_noite_aud     # refaz a bateria completa de um fundo (os dados do top 5 estão no repositório)
```

## O que foi testado
**52 estratégias** de pessoa física: as 39 que tiveram alfa na pesquisa institucional (revisitadas com R$ 20–50 mil) e ~40 novas, em
6 frentes (ações B3 e eventos; renda fixa PF; derivativos B3 com garantia em Tesouro Selic; micro futuros CME com só a margem fora;
global via B3 e cripto; macro e ações com hedge). 27 bateram o CDI depois do IR antes da auditoria. Ranking completo:
[`resultados/ranking_pf.csv`](resultados/ranking_pf.csv). Cadernos: [`pesquisa/`](pesquisa/).

## Auditoria ([`pesquisa/auditoria_pf.md`](pesquisa/auditoria_pf.md))
Os três primeiros do ranking caíram:
| Fundo | Por quê |
|---|---|
| Covered call em ações isentas (+11,8 pp) | era carteira de 3 ações (beta); as calls sozinhas perdem 1,8 pp a.a. |
| BDR x EUA com ordem limitada (+12,5 pp) | 94% do ganho vinha de fills "quando a mínima encostou no limite" (seleção adversa); conservador: −12,6 pp |
| VXM vendido (+19,8 pp) | em mar/2020 1 VXM perdeu ~R$ 31 mil (> R$ 20 mil): a IBKR liquidaria no pico |
| Carry PF micro FX + WDO (+11,4 pp) | o grosso era a perna do real (WDO); só G10: +1,2 pp depois do IR |
| WDO vendido (carry do real) | com R$ 20 mil = 2,6x alavancado (−57 pp em 2024); com R$ 50 mil é **beta de carry do real** (+7,1 pp depois do IR), não alfa |
| PEAD B3 em lote pequeno | sem os 10 melhores negócios: −3,8 pp; ponta vendida perde |
| Spin-offs com hedge, small caps valor | reprovados no teste de look-ahead (truncamento) |

## Top 5 final (pós-auditoria, IR de pessoa física correto) — fora da amostra desde 2021, pp a.a. sobre o CDI

IR por `ir.py`: renda variável B3 apurada **mensalmente** com compensação de prejuízo e **isenção de ações quando as vendas do mês ≤ R$ 20 mil**
(somando todos os fundos do mesmo CPF na carteira); exterior 15% sobre o ganho anual; renda fixa 15%; isentos 0%; o CDI do caixa paga 15%
(igual ao benchmark "CDI depois do IR").

| # | Fundo | Tese de mesa | R$ 20 mil antes / depois do IR | R$ 50 mil depois do IR | IR | PBO | P(bater 3a) | Sem os 10 melhores | Ressalva |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Noite nos leilões após queda forte | compra no leilão de fechamento ações líquidas que caíram forte no dia, vende no leilão de abertura (quem vende no pânico do fim do dia paga a liquidez) | **+7,1 / +5,7** | +5,7 | 0,47 | 10% | 81% | +1,9 | **muito sensível a custo**: custo 2x = −9,8 pp; giro alto → só 33% dos meses isentos |
| 2 | OPA até o leilão (lote pequeno) | compra a small cap abaixo do preço da OPA/fechamento de capital e entrega no leilão; vendas de R$ 3–7,5 mil por OPA ficam isentas | **+4,1 / +4,0** | +4,0 | 0,54 | 36% | 88% | −2,3 | só 18 negócios fora da amostra |
| 3 | Petróleo em pânico (PETR4/PRIO3 x petróleo) | compra a petroleira que caiu muito mais que o Brent em R$ (vendedor forçado) e sai na reconvergência | +3,0 / +2,9 | +3,4 | 0,36 | 10% | 76% | −2,4 | 22 negócios em 12 anos; perde em pânico de governança |
| 4 | Ofertas de ações pela tranche de varejo | pede na oferta (desconto de lançamento) com rateio de 15% e dinheiro bloqueado, vende em poucos dias | +2,6 / +2,5 | +2,5 | 0,56 | 41% | 86% | −1,3 | 3 ofertas dão boa parte do ganho |
| 5 | Rebalanceamento do Ibovespa | compra os prováveis entrantes antes do fundo de índice | +1,0 / +1,0 | +1,2 | 0,42 | 13% | 80% | −0,7 | pequeno e concentrado |

Todos passam no teste de look-ahead (truncamento) e aguentam execução em t+2; o placebo (mesmas posições deslocadas no tempo) é
significativo em quatro dos cinco (p ≤ 0,05; petróleo p = 0,14). Cadernos com tese, robustez, 10 melhores e 10 piores negócios e quem trouxe o retorno de
cada fundo: `pesquisa/*_resultados.md` (todas as 58 estratégias).

### Carteira com os 5 (pesos pelo risco de cada fundo antes do corte; tudo em uma conta B3 + Tesouro Selic, sem remessa)
| Capital | Alavancagem | OOS a.a. | CDI | Ativo | **Depois do IR** | Sharpe | Pior queda |
|---|---|---|---|---|---|---|---|
| R$ 20 mil | 1x | 13,9% | 11,4% | +2,4 pp | **+2,4 pp** | 0,76 | −2,5% |
| R$ 20 mil | 2x | 14,5% | 11,4% | +3,1 pp | +3,0 pp | 0,86 | −4,7% |
| R$ 50 mil | 1x | 14,0% | 11,4% | +2,5 pp | +2,2 pp | 0,78 | −2,8% |
| R$ 50 mil | 2x | 14,6% | 11,4% | +3,2 pp | +2,8 pp | 0,89 | −5,2% |

Com R$ 20 mil: ≈ R$ 13,3 mil em ofertas, R$ 4,3 mil no rebalanceamento, ≈ R$ 1 mil em OPA, R$ 0,9 mil em petróleo, R$ 0,6 mil no leilão
(o leilão tem a maior vol, por isso o menor peso). Monte Carlo: 96% de chance de bater o CDI em 3 anos; nenhuma alavancagem quebrou.
Sem cada fundo a carteira fica entre +2,1 e +2,9 pp — nenhum fundo sozinho carrega o resultado. Detalhe: `resultados/carteira_pf.csv`.

### Não é alfa (beta), mas existe para quem quiser risco
Carry do real vendendo mini-dólar com R$ 50 mil (+7,4 pp depois do IR, quedas de 30%+), S&P via mini da B3 (+4,1 pp), ouro com micro
futuro (+4,3 pp), cripto (+2 a +4 pp). Rendem acima do CDI por estarem expostos a um mercado que subiu, não por habilidade.

### O que a auditoria derrubou (14 estratégias)
Covered call isenta (era carteira de ações), BDR com ordem limitada (fills impossíveis), VXM vendido (quebra em mar/2020), carry PF
(era a perna do real), PEAD (some sem os 10 melhores), fracionário x lote (pernas não simultâneas), cripto/S&P/ouro/tendência (beta).
Detalhe em `pesquisa/auditoria_pf.md` e `pesquisa/correcoes_finais.md`; ranking completo com o veredito em `resultados/ranking_pf.csv`.

## Painéis
![carteira 20k](resultados/carteira_20k.png)
![1](resultados/top1_b3_leilao_noite_aud.png)
![2](resultados/top2_b3_opa_leilao.png)
![3](resultados/top3_mh_petroleo.png)
![4](resultados/top4_b3_ofertas_varejo_aud.png)
![5](resultados/top5_rev_rebal_ibovespa.png)

## Limitações
- IR simplificado em dois pontos: o CDI de uma parcela aplicada em ativo isento paga 15% (conservador) e a renda fixa usa 15% fixo
  (tabela regressiva de 22,5% para prazos curtos não aplicada). A isenção de R$ 20 mil é por CPF: com amigos em vários CPFs ela seria maior.
- As vendas de ações para a isenção vêm dos pesos-alvo (aproximação).
- O título da figura da carteira menciona "vol-alvo 6%" por herança do gráfico institucional; a carteira PF não tem vol-alvo.
