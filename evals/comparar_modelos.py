import json
import sys
import time
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.chain.builder import criar_chain_conversa
from src.config import MAX_TOKENS, MODEL_NAME, MODEL_NAME_2, TEMPERATURE, TOP_P
from src.context_loader import carregar_contexto_texto

EVAL_PATH = ROOT / "evals" / "eval_set.json"
OUT_JSON = ROOT / "evals" / "model_prompt_comparison.json"
OUT_MD = ROOT / "docs" / "relatorio_modelos.md"


def normalizar(texto: str) -> str:
    texto = unicodedata.normalize("NFD", texto.lower())
    return "".join(c for c in texto if unicodedata.category(c) != "Mn")


def score_criterios(resposta: str, criterios: list[dict]) -> float:
    texto = normalizar(resposta)
    acertos = 0
    for criterio in criterios:
        if any(normalizar(t) in texto for t in criterio["termos"]):
            acertos += 1
    return acertos / len(criterios) if criterios else 0.0


def main():
    casos = json.loads(EVAL_PATH.read_text(encoding="utf-8"))
    # 4 casos representativos para manter a comparação executável em tempo razoável.
    casos = [c for c in casos if c["id"] in {1, 3, 4, 5}]
    contexto = carregar_contexto_texto()
    modelos = [MODEL_NAME, MODEL_NAME_2]
    prompts = ["v1", "v2"]
    resultados = []

    for modelo in modelos:
        for versao in prompts:
            try:
                chain = criar_chain_conversa(prompt_version=versao, model_name=modelo)
                scores = []
                latencias = []
                amostras = []
                for caso in casos:
                    inicio = time.perf_counter()
                    resposta = chain.invoke(
                        {
                            "pergunta": caso["pergunta"],
                            "contexto_operacional": contexto,
                            "history": [],
                        }
                    )
                    latencia = (time.perf_counter() - inicio) * 1000
                    score = score_criterios(resposta, caso["criterios"])
                    scores.append(score)
                    latencias.append(latencia)
                    amostras.append({"id": caso["id"], "resposta": resposta, "score": score})

                resultados.append(
                    {
                        "modelo": modelo,
                        "prompt": versao,
                        "quality_percent": round(sum(scores) / len(scores) * 100, 2),
                        "latency_avg_ms": round(sum(latencias) / len(latencias), 2),
                        "status": "ok",
                        "amostras": amostras,
                    }
                )
            except Exception as erro:
                resultados.append(
                    {
                        "modelo": modelo,
                        "prompt": versao,
                        "status": "erro",
                        "erro": str(erro),
                    }
                )

    OUT_JSON.write_text(json.dumps(resultados, ensure_ascii=False, indent=2), encoding="utf-8")

    linhas = [
        "# Relatório de modelos e parâmetros — Sprint 03",
        "",
        "## Parâmetros controlados",
        "",
        f"- `temperature`: `{TEMPERATURE}`",
        f"- `top_p`: `{TOP_P}`",
        f"- `max_tokens` / `num_predict`: `{MAX_TOKENS}`",
        f"- Modelo principal: `{MODEL_NAME}`",
        f"- Modelo comparativo: `{MODEL_NAME_2}`",
        "- Prompts comparados: `v1` e `v2`",
        "",
        "## Comparativo executado",
        "",
        "| Modelo | Prompt | Qualidade no mini-eval | Latência média | Status |",
        "|---|---|---:|---:|---|",
    ]
    for item in resultados:
        if item["status"] == "ok":
            linhas.append(
                f"| {item['modelo']} | {item['prompt']} | {item['quality_percent']:.2f}% | {item['latency_avg_ms']:.2f} ms | OK |"
            )
        else:
            erro_curto = item["erro"].replace("|", "/").replace("\n", " ")[:120]
            linhas.append(f"| {item['modelo']} | {item['prompt']} | — | — | ERRO: {erro_curto} |")

    linhas += [
        "",
        "## Leitura dos resultados",
        "",
        "Use a combinação com maior aderência ao eval e latência aceitável como justificativa do modelo/prompt principal. "
        "Se o segundo modelo não estiver disponível na conta Ollama, altere `MODEL_NAME_2` no `.env` para outro modelo acessível e execute novamente.",
        "",
        "## Evidência para o bônus",
        "",
        "O script executa mais de um modelo e mais de um prompt sobre as mesmas perguntas. Guarde `evals/model_prompt_comparison.json` no repositório como evidência reproduzível.",
    ]
    OUT_MD.write_text("\n".join(linhas), encoding="utf-8")
    print(f"Gerados: {OUT_JSON} e {OUT_MD}")


if __name__ == "__main__":
    main()
