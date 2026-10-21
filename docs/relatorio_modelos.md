# Escopo desta comparação: CORPUS PRÉ-HCA (14 perguntas), dois modelos, não equivalente às avaliações HCA 22 casos.

# Relatório de modelos e parâmetros — Sprint 04

## Configuração efetiva da avaliação

O RAG testado utilizou Nomic Embed v1.5 (`sentence-transformers`, local), ChromaDB persistente e `ChatOllama`. Valores de execução do RAG: `temperature=0`, `top_p=0,9`, `max_tokens/num_predict=350` e distância cosseno máxima 0,65. `k=3` em `iter1` e `k=4` em `iter2`. Parâmetros podem ser alterados por `.env`; mudanças futuras exigem nova coleta. Consulte `src/rag/prompt_rag.py` e `src/rag/settings.py`.

| Perfil | Chunk / overlap | k | Prompt | LLM das iterações | Temperature | Top-p | Max tokens |
|---|---|---:|---|---|---:|---:|---:|
| iter1 | 400 / 40 | 3 | `rag_v1.md` | `gpt-oss:120b` | 0 | 0,9 | 350 |
| iter2 | 750 / 100 | 4 | `rag_v2.md` | `gpt-oss:120b` | 0 | 0,9 | 350 |

## Comparação de geração da Sprint 04

A comparação separada foi executada sobre as mesmas 14 perguntas com o perfil `iter2` (prompt v2, k=4), sem atribuir qualidade factual a simples presença de citação.

| Modelo | Casos processados | Latência média | Citação visível |
|---|---:|---:|---:|
| `gpt-oss:120b` | 14/14 | **1.594,76 ms** | **50%** |
| `gpt-oss:20b` | 14/14 | **1.669,64 ms** | **50%** |

**Correção de auditoria:** o arquivo original `evals/comparativo_modelos_iter2.json` armazenou `temperature=0.2` lido do `.env` legado da Sprint 3, mas a cadeia de geração RAG fixava **temperature=0** no objeto `ChatOllama`. O número original foi preservado para auditoria; o campo `temperature_efetiva_verificada_codigo=0.0` esclarece o valor real. O comparador foi corrigido para futuras execuções. **Não foi necessário inventar/reexecutar medições para fazer essa correção de metadados.**

`casos_processados` significa que não houve exceção técnica; **não significa respostas corretas**. Recusas de segurança corretas também não exigem citar um documento. É necessário consultar a coleta caso a caso para avaliar a qualidade dos modelos.

## Avaliação das duas iterações (não confundir com comparação entre modelos)

| Métrica manual (0–1) | iter1 | iter2 | Ganho |
|---|---:|---:|---:|
| Faithfulness | 0,7143 | 0,8571 | +0,1428 |
| Answer relevancy | 0,6786 | 0,8214 | +0,1428 |

Notas por pergunta em `evals/rubrica_anotacoes.json`; coletas originais em `evals/coleta_iter*.json`. Fallback manual documentado em `evals/RUBRICA.md`, permitido pela Sprint 04, **não score oficial RAGAS**.

## Histórico medido na Sprint 03 (não comparar diretamente)

| Modelo | Prompt | Qualidade no mini-eval S3 | Latência S3 |
|---|---|---:|---:|
| gpt-oss:120b | v1 | 75,00% | 1.009,83 ms |
| gpt-oss:120b | v2 | 75,00% | 911,18 ms |
| gpt-oss:20b | v1 | 62,50% | 3.060,98 ms |
| gpt-oss:20b | v2 | 75,00% | 2.736,78 ms |

## Embeddings e bônus

O modelo `nomic-ai/nomic-embed-text-v1.5` (Apache 2.0) usa prefixos de tarefa `search_document` e `search_query` e vetores de 768 dimensões normalizados. Rodar localmente é grátis, mas **diverge do provedor Ollama Cloud indicado literalmente na aula**, pois não há serviço de embeddings ali. Dois modelos do mesmo provedor **não** concedem bônus multi-provider; bônus não reivindicado.


## Linha HCA G2 (novo corpus) — não mensurado ainda

Os valores acima são do corpus pré-HCA. Para comparação com os três PDFs HCA G2 localmente indexados, refaça `python evals/comparar_modelos_rag.py --edition hca --profile iter2`; o resultado fica isolado em `evals/comparativo_modelos_hca_iter2.json` e `docs/relatorio_modelos_hca.md`. Não reaproveitar latências/citações antigas como métricas da nova base.
