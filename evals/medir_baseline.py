import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.context_loader import carregar_prompt, contar_tokens

EVAL_PATH = ROOT / "evals" / "eval_set.json"
LEGACY_CONTEXT_PATH = ROOT / "evals" / "contexto_legado_sprint2.txt"
OUT = ROOT / "evals" / "sprint2_baseline.json"

casos = json.loads(EVAL_PATH.read_text(encoding="utf-8"))[:8]
system_v1 = carregar_prompt("v1")
legacy_context = LEGACY_CONTEXT_PATH.read_text(encoding="utf-8")

system_content = f"""{system_v1}

## CONTEXTO OPERACIONAL RECUPERADO
Use exclusivamente os dados abaixo para responder perguntas operacionais.

{legacy_context}
"""

tokens = [contar_tokens(system_content + "\n" + caso["pergunta"]) for caso in casos]

# Dados observados no resultados_testes.md da Sprint 2.
latencias_ms = [2672, 3368, 2027, 2087, 2847, 2796, 2265, 1597]
classificacoes = [
    "Adequada",
    "Adequada",
    "Adequada",
    "Adequada",
    "Parcialmente adequada",
    "Adequada",
    "Inadequada",
    "Inadequada",
]

peso = {"Adequada": 1.0, "Parcialmente adequada": 0.5, "Inadequada": 0.0}
qualidade = sum(peso[c] for c in classificacoes) / len(classificacoes) * 100

baseline = {
    "fonte": "evals/resultados_testes_sprint2.md",
    "casos_comparaveis": 8,
    "quality_method": "Adequada=1.0; Parcialmente adequada=0.5; Inadequada=0.0",
    "quality_percent": round(qualidade, 2),
    "latency_avg_ms": round(sum(latencias_ms) / len(latencias_ms), 2),
    "input_tokens_avg_approx": round(sum(tokens) / len(tokens), 2),
    "structured_output_accuracy_percent": 0.0,
    "observacao_tokens": "Estimativa tiktoken reconstruindo o system prompt, contexto hardcoded e pergunta da Sprint 2; o projeto legado não registrava tokens.",
    "observacao_structured": "A Sprint 2 não possuía schema Pydantic/structured output validado.",
}
OUT.write_text(json.dumps(baseline, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(baseline, ensure_ascii=False, indent=2))
print(f"Arquivo gerado: {OUT}")
