# Relatório do RAG - Sprint 04 — experimento histórico antes de HCA G2

## Método

Avaliação manual equivalente (fallback permitido pelo enunciado): para cada questão, um avaliador humano identifica as afirmações e verifica se são sustentadas **exclusivamente pelos trechos recuperados** (faithfulness, 0/0,5/1); verifica se a resposta atende à pergunta ou recusa corretamente dados ausentes (answer_relevancy, 0/0,5/1). Valores são médias simples dos 14 casos fixos. A escala discretizada é uma aproximação de rubrica, **não se confunde com os algoritmos do RAGAS**. Justificativas e identidade são salvas em `evals/rubrica_anotacoes.json`.

## Avaliação por iteração

| Perfil | Tamanho / overlap | Prompt | faithfulness | answer_relevancy | Avaliados |
|---|---|---|---|---|---|
| iter1 | 400 / 40 | v1 | 0.714 | 0.679 | 14/14 |
| iter2 | 750 / 100 | v2 | 0.857 | 0.821 | 14/14 |

Ganho nas duas métricas: **comprovado**. Não inserir números fictícios; caso falhe, ajustar um aspecto e repetir a coleta com o mesmo conjunto.

## Contexto e fontes

Fonte por seção e página (PDF) retornada no payload e visível em Gradio. O campo `distancia` é distância cosseno (menor é mais próximo); limiar configurável, sujeito a calibração. Este score foi obtido **antes da inclusão da referência HCA G2**. Para a base ampliada com PDFs locais, reindexar e executar `--edition hca`. Não atribuir as notas históricas ao novo corpus.

## Segurança

Documentos são carregados em espaço de dados, não como instruções; blocos com padrões explícitos de injection são colocados em quarentena; referências inexistentes levam à recusa. Essas medidas **reduzem** o risco, não oferecem garantia absoluta contra injection ou alucinação. Evals R12-R14 testam segurança e fora de escopo.
