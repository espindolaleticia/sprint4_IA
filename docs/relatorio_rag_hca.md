# Sprint 04 | HCA G2 — avaliação original após importação

**Rubrica manual**, em 22 casos idênticos por configuração; não é RAGAS oficial. Resultados informados pelo grupo a partir do comando `python evals/avaliar_rag.py report --edition hca` executado no computador com PDFs e ChromaDB locais.

| Perfil | faithfulness | answer relevancy | Casos |
|---|---:|---:|---:|
| iter1 (400/40; k=3; v1) | 0,9773 | 0,9773 | 22/22 |
| iter2 (750/100; k=4; v2) | 1,0000 | 0,9773 | 22/22 |

**Resultado:** melhora em faithfulness, empate em relevancy. `gain_both_metrics=false` é correto para estas **duas** versões. Em iter1, R07 apresentou extrapolação sobre preenchimento automático por RFID (faithfulness=0,5). R14 apresentou recusa pouco útil para risco elétrico em ambas (answer relevancy=0,5). Respostas individuais permaneceram na coleta local do grupo. Esta versão intermediária é preservada para mostrar por que foi necessária a revisão da política.

Fonte dos números: `evals/resultado_sprint4_hca.json` (saída agregada enviada pelo usuário); avaliação por caso resumida em `evals/notas_resumidas_publicaveis_hca.json`. Reexecutar `report` somente na pasta local que possua a coleta e a rubrica originais, para não sobrescrever relatórios publicáveis com dados pendentes.
