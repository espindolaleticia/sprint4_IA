# Versões do System Prompt

| Versão | O que mudou | Por quê | Tokens aproximados | Ganho medido |
|---|---|---|---:|---:|
| v1 | Prompt legado da Sprint 2, organizado em seções Markdown. | Preservar o baseline para comparação. | 931 | Baseline |
| v2 | XML tagging, regras críticas compactadas, guardrails jurídico/financeiro/elétrico e prioridade explícita. | Reduzir ambiguidade, facilitar manutenção e reforçar aderência de escopo. | 472 | 49.30% de redução de tokens do prompt |

> Medição feita com `tiktoken` usando `gpt-4` como aproximação, conforme a Aula 04. O valor serve para comparação antes/depois, não como contagem nativa do Ollama.
