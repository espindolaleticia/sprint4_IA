import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.context_loader import carregar_prompt, contar_tokens

v1 = carregar_prompt("v1")
v2 = carregar_prompt("v2")
t1 = contar_tokens(v1)
t2 = contar_tokens(v2)
reducao = (1 - t2 / t1) * 100 if t1 else 0

dados = {
    "v1_tokens": t1,
    "v2_tokens": t2,
    "reducao_percentual": round(reducao, 2),
}
(ROOT / "prompts" / "versoes.json").write_text(
    json.dumps(dados, ensure_ascii=False, indent=2), encoding="utf-8"
)

md = f"""# Versões do System Prompt

| Versão | O que mudou | Por quê | Tokens aproximados | Ganho medido |
|---|---|---|---:|---:|
| v1 | Prompt legado da Sprint 2, organizado em seções Markdown. | Preservar o baseline para comparação. | {t1} | Baseline |
| v2 | XML tagging, regras críticas compactadas, guardrails jurídico/financeiro/elétrico e prioridade explícita. | Reduzir ambiguidade, facilitar manutenção e reforçar aderência de escopo. | {t2} | {reducao:.2f}% de redução de tokens do prompt |

> Medição feita com `tiktoken` usando `gpt-4` como aproximação, conforme a Aula 04. O valor serve para comparação antes/depois, não como contagem nativa do Ollama.
"""
(ROOT / "prompts" / "versoes.md").write_text(md, encoding="utf-8")

print(f"v1: {t1} tokens")
print(f"v2: {t2} tokens")
print(f"Redução: {reducao:.2f}%")
print("Arquivos gerados: prompts/versoes.json e prompts/versoes.md")
