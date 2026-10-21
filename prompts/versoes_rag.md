# Versões do prompt e dos perfis RAG — Sprint 04

| Experimento | Corpus | Chunk / overlap | k | Mudanças | faithfulness | answer relevancy |
|---|---|---:|---:|---|---:|---:|
| Histórico pré-HCA I1 | documentos acadêmicos | 400/40 | 3 | RAG v1 | 0,7143 | 0,6786 |
| Histórico pré-HCA I2 | documentos acadêmicos | 750/100 | 4 | RAG v2; XML/citações/recusa | 0,8571 | 0,8214 |
| HCA I1 | HCA G2 + simulados | 400/40 | 3 | RAG v1 | **0,9773** | **0,9773** |
| HCA I2 | HCA G2 + simulados | 750/100 | 4 | RAG v2 | **1,0000** | **0,9773** |
| HCA I2 + segurança v2 | mesmo índice da HCA I2 | 750/100 | 4 | só proteção contra manutenção energizada | **1,0000** | **1,0000** |

**Método:** rubrica humana, 22 perguntas em cada rodada HCA, 0/0,5/1, não RAGAS oficial. Ganho nas duas métricas em relação à HCA I1 = +0,0227. Os resultados anteriores (14 perguntas) **não são comparáveis com os valores HCA (22 perguntas + novos documentos)**; permanecem históricos. I1 vs I2 altera ao mesmo tempo chunking, top-k e prompt; não atribuir ganho a um fator individual. I2 vs I2 segurança altera somente o guardrail.

**Rastreabilidade:** `docs/relatorio_rag_hca_seguranca_v2.md`; resultados agregados e notas públicas em `evals/`; coleta e rubrica completas somente no ambiente local do grupo devido a trechos dos PDFs.
