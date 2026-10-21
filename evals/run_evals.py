import json
import sys
import unicodedata
import uuid
from pathlib import Path

from langchain_core.exceptions import OutputParserException
from pydantic import ValidationError

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.service import limpar_sessao, processar_chat, processar_estruturado

EVAL_PATH = ROOT / "evals" / "eval_set.json"
OUT_PATH = ROOT / "evals" / "sprint3_results.json"


def normalizar(texto: str) -> str:
    texto = unicodedata.normalize("NFKD", texto.lower())

    caracteres = []

    for c in texto:
        if unicodedata.combining(c):
            continue

        if unicodedata.category(c) == "Pd":
            caracteres.append("-")
        else:
            caracteres.append(c)

    texto = "".join(caracteres)

    texto = " ".join(texto.split())

    texto = texto.replace(" %", "%")

    return texto.strip()


def avaliar_resposta(resposta: str, criterios: list[dict]) -> tuple[float, str, str]:
    texto = normalizar(resposta)
    detalhes = []
    atendidos = 0

    for criterio in criterios:
        achou = any(normalizar(termo) in texto for termo in criterio["termos"])
        if achou:
            atendidos += 1
            detalhes.append(f"OK: {criterio['descricao']}")
        else:
            detalhes.append(f"FALTOU: {criterio['descricao']}")

    score = atendidos / len(criterios) if criterios else 0.0
    if score >= 0.75:
        classe = "Adequada"
    elif score >= 0.50:
        classe = "Parcialmente adequada"
    else:
        classe = "Inadequada"

    justificativa = f"Atendeu {atendidos}/{len(criterios)} critérios. " + "; ".join(detalhes)
    return score, classe, justificativa


def comparar_esperado(valor_obtido, valor_esperado) -> bool:
    if isinstance(valor_esperado, list):
        return sorted(valor_obtido or []) == sorted(valor_esperado)
    if isinstance(valor_esperado, float):
        if valor_obtido is None:
            return False
        return abs(float(valor_obtido) - valor_esperado) < 0.01
    return valor_obtido == valor_esperado


def avaliar_structured(caso: dict) -> dict:
    if not caso.get("structured"):
        return {"executado": False}

    try:
        objeto = processar_estruturado(caso["pergunta"])
        dados = objeto.model_dump()
        esperado = caso.get("structured_expect", {})
        verificacoes = {
            chave: comparar_esperado(dados.get(chave), valor)
            for chave, valor in esperado.items()
        }
        passou = all(verificacoes.values())
        return {
            "executado": True,
            "schema_valido": True,
            "passou_campos_esperados": passou,
            "verificacoes": verificacoes,
            "saida": dados,
        }
    except (ValidationError, OutputParserException, ValueError) as erro:
        return {
            "executado": True,
            "schema_valido": False,
            "passou_campos_esperados": False,
            "erro": str(erro),
        }
    except Exception as erro:
        return {
            "executado": True,
            "schema_valido": False,
            "passou_campos_esperados": False,
            "erro": f"Erro inesperado: {erro}",
        }


def resumir(resultados: list[dict], ids: set[int]) -> dict:
    subset = [r for r in resultados if r["id"] in ids]
    structured = [r for r in subset if r["structured"].get("executado")]

    return {
        "casos": len(subset),
        "quality_percent": round(
            sum(r["score"] for r in subset) / len(subset) * 100, 2
        ) if subset else 0.0,
        "latency_avg_ms": round(
            sum(r["latency_ms"] for r in subset) / len(subset), 2
        ) if subset else 0.0,
        "input_tokens_avg_approx": round(
            sum(r["input_tokens_approx"] for r in subset) / len(subset), 2
        ) if subset else 0.0,
        "structured_output_accuracy_percent": round(
            sum(1 for r in structured if r["structured"].get("passou_campos_esperados"))
            / len(structured)
            * 100,
            2,
        ) if structured else 0.0,
        "adequadas": sum(r["classificacao"] == "Adequada" for r in subset),
        "parciais": sum(r["classificacao"] == "Parcialmente adequada" for r in subset),
        "inadequadas": sum(r["classificacao"] == "Inadequada" for r in subset),
    }


def main():
    casos = json.loads(EVAL_PATH.read_text(encoding="utf-8"))
    resultados = []

    for caso in casos:
        session_id = f"eval-{caso['id']}-{uuid.uuid4()}"
        limpar_sessao(session_id)
        saida = processar_chat(caso["pergunta"], session_id)
        score, classe, justificativa = avaliar_resposta(saida["answer"], caso["criterios"])
        estruturado = avaliar_structured(caso)

        resultado = {
            "id": caso["id"],
            "categoria": caso["categoria"],
            "pergunta": caso["pergunta"],
            "esperado": caso["esperado"],
            "resposta": saida["answer"],
            "score": round(score, 4),
            "classificacao": classe,
            "justificativa": justificativa,
            "latency_ms": saida["latency_ms"],
            "input_tokens_approx": saida["input_tokens_approx"],
            "output_tokens_approx": saida["output_tokens_approx"],
            "blocked_by_guardrail": saida["blocked_by_guardrail"],
            "structured": estruturado,
        }
        resultados.append(resultado)
        print(f"[{caso['id']:02d}] {classe} — {caso['categoria']}")

    pacote = {
        "metodologia": {
            "qualidade": "Percentual de critérios explícitos atendidos. Adequada >=75%; Parcial >=50%; Inadequada <50%.",
            "tokens": "Estimativa tiktoken para comparação antes/depois.",
            "structured_output": "Schema Pydantic válido + correspondência dos campos esperados definidos no eval set.",
        },
        "summary": {
            "sprint2_comparable_ids_1_8": resumir(resultados, set(range(1, 9))),
            "overall_ids_1_12": resumir(resultados, set(range(1, 13))),
        },
        "results": resultados,
    }

    OUT_PATH.write_text(json.dumps(pacote, ensure_ascii=False, indent=2), encoding="utf-8")
    print("\nResumo comparável (casos 1–8):")
    print(json.dumps(pacote["summary"]["sprint2_comparable_ids_1_8"], ensure_ascii=False, indent=2))
    print(f"\nArquivo gerado: {OUT_PATH}")


if __name__ == "__main__":
    main()
