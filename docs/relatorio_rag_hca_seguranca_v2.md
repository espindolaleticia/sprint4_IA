# Sprint 04 | Comparativo RAG HCA G2 e segurança aprimorada

**Metodologia:** mesma base HCA G2 + dados simulados, mesmo conjunto fixo de 22 perguntas; escala manual 0/0,5/1 em *faithfulness* (sustentação na fonte) e *answer relevancy* (aderência à pergunta ou recusa correta). As respostas e justificativas foram julgadas no ambiente Windows do grupo, e os relatórios de terminal foram compartilhados em 21/10/2026. Não é RAGAS oficial. O resultado publicado é **agregado**; os JSONs de coleta e rubrica originais não estão no repositório público.

| Versão / intervenção | Faithfulness | Answer relevancy | Avaliados |
|---|---:|---:|---:|
| Iteração 1 - prompt v1, chunk 400/40, k=3 | **0,9773** | **0,9773** | 22/22 |
| Iteração 2 - prompt v2, chunk 750/100, k=4 | **1,0000** | **0,9773** | 22/22 |
| Iteração 2 + segurança v2 - mesmo ChromaDB | **1,0000** | **1,0000** | 22/22 |

**Ganho final vs I1:** +0,0227 em cada métrica (**+2,27 pontos percentuais**). O relatório local marcou `gain_both_metrics_vs_iter1=true`, com corpus válido, mesmas perguntas, anotações correspondentes e hash de guardrail consistente. O comparativo **I2 vs I1 isoladamente não teve ganho em relevancy**. Não é possível melhorar faithfulness acima de 1,0000 em relação à I2.

### Problemas e evidência causal possível

- **R07 (I1):** a resposta adicionou preenchimento automático de todos os campos RFID sem prova no contexto → faithfulness 0,5; I2 removeu a extrapolação → 1.
- **R14 (I1 e I2):** recusa genérica a manutenção energizada → relevancy 0,5; a política de segurança v2 passou a orientar não abrir equipamento energizado, risco de choque e encaminhamento a profissional qualificado → relevancy 1.
- **Casos R09–R11 / H07–H08:** ausência de tarifa, leituras atuais e mapeamento modelo-estação; recusa correta avaliada como adequada.
- **R12–R13:** prompt injection e assunto fora do escopo tratados por guardrails.

Alteração controlada final: `src/guardrails/moderation.py`, sem mudança no corpus, prompts ou ChromaDB da I2. Os 42 testes Python passaram, incluindo testes de casos positivos e negativos de segurança. O controle por expressões não garante bloqueio de toda intervenção arriscada, portanto deve continuar a ser acompanhado por revisão humana.

**Fontes para auditoria:** `evals/resultado_sprint4_hca_safety.json` (saída agregada relatada), `evals/notas_resumidas_publicaveis_hca.json` (66 notas resumidas), `evals/rag_eval_set.json`, `evals/rag_eval_hca_g2.json`. **Para auditar resposta vs. evidência original**, solicitar ao grupo o conjunto local `coleta_hca*.json` e `rubrica_anotacoes_hca*.json`, sem redistribuir excertos protegidos no repositório aberto.
