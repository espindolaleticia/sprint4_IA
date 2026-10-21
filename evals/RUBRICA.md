# Fallback manual: faithfulness e answer_relevancy

Avaliar, **sem mudar as perguntas**, os 14 registros de `rag_eval_set.json` em cada iteração (iter1 e iter2), inclusive recusas, perguntas sem dados, guardrails e jailbreak.

## Faithfulness - 0 a 1
- **1:** alegações factuais sustentadas pelo contexto, ou recusa **justificada** diante de pergunta sem dados/fora do escopo/perigosa.
- **0,5:** parte das alegações está documentada, mas existe generalização/número não sustentado; ou citação incorreta.
- **0:** afirmações centrais não aparecem no contexto, a resposta inventa dados **ou se recusa indevidamente apesar de evidência explícita recuperada**.

## Answer relevancy - 0 a 1
- **1:** responde à pergunta solicitada; para dado ausente/fora de escopo, recusa apropriadamente e explica o limite sem inventar.
- **0,5:** resposta tangencia o pedido ou omite um componente relevante.
- **0:** ignora a pergunta ou responde a algo diferente (incluindo falsa resposta específica quando precisava recusar).

Esta adaptação acadêmica penaliza recusas indevidas em faithfulness como falhas de uso do contexto; isso **não corresponde à fórmula oficial do RAGAS**, em que faithfulness trata das afirmações da resposta. São duas aproximações **humanas discretas**; não equivalem matematicamente ao score contínuo oficial do RAGAS. Avaliador registra evidências e justificativa por caso. Não pontue sem conferir o contexto listado em cada resultado. Edição de `prompts/rag_v1.md`, `prompts/rag_v2.md`, tamanho/overlap ou `k` exige uma nova versão e nova coleta; não altere parâmetros após pontuar para preservar comparabilidade.

## Procedimento no Windows (raiz do projeto)

```powershell
python -m src.rag.vector_store --profile all
python evals/avaliar_rag.py collect --profile iter1
python evals/avaliar_rag.py collect --profile iter2
python evals/avaliar_rag.py judge --profile iter1
python evals/avaliar_rag.py judge --profile iter2
python evals/avaliar_rag.py report
python evals/comparar_modelos_rag.py --profile iter2
```

Ao avaliar uma **recusa**, conferir contexto/ausência de documentação de fonte e se nenhum dado foi inventado. As fontes e trechos da coleta permitem auditar o julgamento. Se o resultado não melhorar, testar outra mudança controlada: não afirmar melhora sem evidência.

## Após integração dos PDFs HCA G2

O experimento histórico (14 questões, índices antigos) NÃO deve ser tratado como medição do corpus ampliado. Após `scripts/importar_hca_g2.py` e a reindexação, use `--edition hca` em collect/judge/report para avaliar 14 questões originais + 8 novas sobre HCA G2 (22 por iteração). Opcionalmente compare dois modelos com `python evals/comparar_modelos_rag.py --edition hca --profile iter2`. São utilizados arquivos próprios `coleta_hca_iter1.json`, `coleta_hca_iter2.json`, `rubrica_anotacoes_hca.json` e `resultado_sprint4_hca.json`; eles não substituem os históricos. A coleta verifica fingerprint do corpus.
