import time

from src.chain.builder import criar_chain_conversa, criar_chain_estruturada
from src.chain.memoria import (
    criar_chain_com_memoria,
    podar_memoria,
    registrar_interacao_guardrail,
    resetar_memoria,
    snapshot_memoria,
    tokens_memoria,
)
from src.config import MODEL_NAME, SYSTEM_PROMPT_VERSION
from src.context_loader import carregar_contexto_texto, carregar_prompt, contar_tokens
from src.guardrails.moderation import aplicar_guardrails

_chain_base = None
_chain_memoria = None
_chain_estruturada = None


def _obter_chain_memoria():
    global _chain_base, _chain_memoria
    if _chain_memoria is None:
        _chain_base = criar_chain_conversa()
        _chain_memoria = criar_chain_com_memoria(_chain_base)
    return _chain_memoria


def _obter_chain_estruturada():
    global _chain_estruturada
    if _chain_estruturada is None:
        _chain_estruturada = criar_chain_estruturada()
    return _chain_estruturada


def _texto_historico(session_id: str) -> str:
    return "\n".join(
        f"{item['tipo']}: {item['conteudo']}" for item in snapshot_memoria(session_id)
    )


def processar_chat_legado(pergunta: str, session_id: str = "default") -> dict:
    pergunta = pergunta.strip()
    if not pergunta:
        raise ValueError("Digite uma pergunta operacional válida.")

    inicio = time.perf_counter()
    contexto = carregar_contexto_texto()
    system_prompt = carregar_prompt(SYSTEM_PROMPT_VERSION)
    historico_antes = _texto_historico(session_id)

    tokens_entrada = contar_tokens(
        f"{system_prompt}\n{contexto}\n{historico_antes}\n{pergunta}"
    )

    resposta_guardrail = aplicar_guardrails(pergunta)
    bloqueado = resposta_guardrail is not None

    if resposta_guardrail:
        resposta = resposta_guardrail
        registrar_interacao_guardrail(session_id, pergunta, resposta)
    else:
        resposta = _obter_chain_memoria().invoke(
            {
                "pergunta": pergunta,
                "contexto_operacional": contexto,
            },
            config={"configurable": {"session_id": session_id}},
        )
        podar_memoria(session_id)

    latencia_ms = round((time.perf_counter() - inicio) * 1000, 2)

    return {
        "answer": resposta,
        "model": MODEL_NAME,
        "prompt_version": SYSTEM_PROMPT_VERSION,
        "blocked_by_guardrail": bloqueado,
        "latency_ms": latencia_ms,
        "input_tokens_approx": tokens_entrada,
        "output_tokens_approx": contar_tokens(resposta),
        "memory_tokens_approx": tokens_memoria(session_id),
    }


def processar_estruturado(pergunta: str):
    pergunta = pergunta.strip()
    if not pergunta:
        raise ValueError("Digite uma pergunta operacional válida.")

    bloqueio = aplicar_guardrails(pergunta)
    if bloqueio:
        raise ValueError(bloqueio)

    return _obter_chain_estruturada().invoke(
        {
            "pergunta": pergunta,
            "contexto_operacional": carregar_contexto_texto(),
        }
    )


def limpar_sessao(session_id: str) -> None:
    resetar_memoria(session_id)


def inspecionar_memoria(session_id: str) -> dict:
    return {
        "session_id": session_id,
        "tokens_approx": tokens_memoria(session_id) if snapshot_memoria(session_id) else 0,
        "messages": snapshot_memoria(session_id),
    }


# Sprint 04: o endpoint /api/chat usa RAG; o pipeline Sprint 03 fica como legado
# apenas para experimentos históricos. A estrutura original permanece para auditoria.
from src.rag.service import answer_question, reset_session, memory_snapshot

def processar_chat(pergunta: str, session_id: str = "default") -> dict:
    return answer_question(pergunta, session_id)

_old_limpar_sessao = limpar_sessao
def limpar_sessao(session_id: str) -> None:
    reset_session(session_id)
    _old_limpar_sessao(session_id)

_old_inspecionar_memoria = inspecionar_memoria
def inspecionar_memoria(session_id: str) -> dict:
    messages = memory_snapshot(session_id)
    return {"session_id":session_id,"messages":messages,"total_messages":len(messages),
            "scope":"rag_session_in_memory"}
