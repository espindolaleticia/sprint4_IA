# Checklist final da Sprint 04 (GoodWe Grid Assistant)

Este documento distingue entrega técnica, comprovação experimental e **pendências de fontes ou autorização**. Os resultados relatados pelo grupo foram verificados logicamente contra a rubrica (22 casos × 3 versões), mas não foi possível reproduzir chamadas Ollama Cloud ou consultar os três índices do computador do usuário neste ambiente.

| Requisito | Evidência no projeto | Situação |
|---|---|---|
| RAG com loading de PDF/documentos | `src/rag/loader.py`, `scripts/importar_hca_g2.py` | Implementado; PDFs requeridos localmente |
| Chunking estratégico e versionamento | `src/rag/chunking.py`, `src/rag/settings.py`, `prompts/rag_v1.md`, `prompts/rag_v2.md` | Implementado e testado |
| Embeddings Nomic e ChromaDB persistente | `src/rag/embeddings.py`, `src/rag/vector_store.py` | Implementado; I1=349/I2=216 chunks registrados localmente |
| Grounding com fontes e páginas | `src/rag/retriever.py`, `src/rag/service.py` | Implementado; normalização e verificação dos IDs |
| Defesa contra injection/fora de escopo | `src/guardrails/moderation.py`, `tests/` | 42 testes locais passaram; regra elétrica revisada |
| Interface web | `app/gradio_app.py` | Implementado; execução local Gradio |
| Duas iterações avaliadas + ganho documentado | `evals/resultado_sprint4_hca*.json`, `docs/relatorio_rag_hca_seguranca_v2.md` | 22 casos por versão; ganho em duas métricas vs I1 **após revisão de segurança** |
| Comparação de dois modelos/parâmetros | `evals/comparativo_modelos_iter2.json`, `docs/relatorio_modelos.md` | Dois modelos, **14 casos pré-HCA**; duas configurações atuais I1/I2 |
| Documentação de Sprints 1–4, antes/depois, equipe e problemas | `docs/GoodWe Grid Assistant.pdf` | 5 páginas; atribuições S4 ainda dependem de confirmação |
| Documentação real de fabricante | Resumo em `data/knowledge_base/06_hca_g2_referencia_tecnica.md` + três PDFs locais | HCA G2 coberto; PDF completo não redistribuído |
| Regimento de condomínio e tabela tarifária reais | `docs/PENDENCIAS_DOCUMENTAIS.md` | **Não fornecidos**; impossível inventar evidência real |
| Embeddings via **Ollama Cloud** literal | Usa SentenceTransformers local | **Desvio documentado**, precisa aceitação docente |

## Como publicar as evidências sem os PDFs protegidos

O ZIP disponibilizado contém **métricas agregadas e resumo de 66 notas** (22 I1 + 22 I2 + 22 I2 Segurança). O grupo possui os arquivos completos `evals/coleta_hca_*.json`, `evals/rubrica_anotacoes_hca*.json` e manifests no computador original, que permitem uma auditoria particular completa. **Não publique as coletas em repositório público**: elas contêm trechos copiados de manual de terceiros; considere apresentação privada ao docente, conforme permissões e política da instituição.

A nova comparação de dois modelos no corpus HCA (caso a rubrica exija exatamente isto) pode ser feita no computador com os PDFs e a Ollama configurados, com o comando:

```powershell
python evals/comparar_modelos_rag.py --edition hca --profile iter2 --models gpt-oss:120b gpt-oss:20b
```

Esse comando faz chamadas externas e produz coletas adicionais. Antes de usá-lo, confirme que **esses modelos estão disponíveis**, que os arquivos de destino ainda não existem e que há custo/limites adequados. O relatório antigo já traz comparação de dois modelos pré-HCA; **não atribuir a ele validade experimental para o novo corpus**.

## Instruções de entrega

1. **Preserve a pasta original** no Windows, que já inclui `.env`, PDFs importados, índices e rubricas; faça backup.
2. Use o novo ZIP público como referência de documentação e código. Para o projeto local já funcional, copie preferencialmente os arquivos de documentação atualizados; não substitua dados/índices locais por pastas vazias.
3. No ambiente original, rode `python -m pytest -q` e `python scripts/validar_entrega.py`, depois confira Gradio em `http://127.0.0.1:7860`.
4. Envie o PDF consolidado de cinco páginas e a URL do GitHub; o ZIP não contém token nem os PDFs protegidos.
5. Confirme **a divisão real de tarefas da Sprint 4** com os demais membros antes de declarar autoria. A tabela no PDF é sugestão de divisão e não prova de execução pessoal.

## Observações metodológicas

- Os resultados de 100% são limitados às 22 questões de rubrica manual; não demonstram ausência de falhas fora do conjunto.
- A métrica I2 (sem proteção v2) é 0,9773 em relevancy; somente a I2 + segurança v2 alcançou 1,0000.
- A política de segurança v2 melhora especificamente a recusa e encaminhamento de solicitações elétricas perigosas; não é uma garantia formal de segurança.
- Os valores das Sprints 2/3 refletem 8 testes legados e não podem ser tratados como RAGAS ou comparados diretamente com as 22 questões RAG.
