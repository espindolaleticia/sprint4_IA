
"""RAG end-to-end, com manutenção do histórico por session_id da Sprint 03."""

import re
import time

from src.rag.settings import RAG_MODEL, EMBED_MODEL

try:
    from src.context_loader import contar_tokens
except ImportError:
    def contar_tokens(text: str) -> int:
        return max(1, len(text) // 4) if text else 0

from src.guardrails.moderation import aplicar_guardrails
from src.rag.settings import get_profile, RAG_MAX_DISTANCE
from src.rag.retriever import fetch_context, format_context, cited_sources
from src.rag.prompt_rag import build_chain


REFUSAL = 'Não encontrei essa informação na base documental disponível.'

_chains = {}
_sessions = {}
MAX_HISTORY_PAIRS = 5


# Normaliza diferentes formatos de citações
def _normalizar_citacoes(resposta):
    resposta = str(resposta).strip()

    # [Referência: F1] ou [Fonte: F1] -> [F1]
    resposta = re.sub(
        r'\[\s*(?:Referência|Referencia|Fonte)\s*:\s*(F\d+)\s*\]',
        r'[\1]',
        resposta,
        flags=re.IGNORECASE,
    )

    # 【F1】【F4】 -> [F1][F4]
    resposta = re.sub(
        r'【\s*(F\d+)\s*】',
        r'[\1]',
        resposta,
    )

    return resposta


# Gerenciamento do histórico
def reset_session(session_id):
    _sessions.pop(session_id, None)


def memory_snapshot(session_id):
    return list(_sessions.get(session_id, []))


def _save(session_id, question, answer):
    history = _sessions.setdefault(session_id, [])

    history.extend([
        {'tipo': 'human', 'conteudo': question},
        {'tipo': 'ai', 'conteudo': answer}
    ])

    del history[:-2 * MAX_HISTORY_PAIRS]


def _question_for_retrieval(question, session_id):
    # Resolve referências simples utilizando o histórico
    if re.search(
        r'\b(ela|ele|isso|essa|esse|dela|dele|naquele|nessa)\b',
        question,
        re.I
    ):
        history = memory_snapshot(session_id)

        previous = next(
            (
                x['conteudo']
                for x in reversed(history)
                if x['tipo'] == 'human'
            ),
            ''
        )

        if previous:
            return previous + '\nPergunta complementar: ' + question

    return question


def answer_question(
    question,
    session_id='default',
    *,
    profile_name=None,
    model_name=None,
    max_distance=None,
    preserve_history=True
):
    from langchain_core.messages import HumanMessage, AIMessage

    started = time.perf_counter()
    question = question.strip()

    if not question or len(question) > 1200:
        raise ValueError(
            'Informe uma pergunta entre 1 e 1200 caracteres.'
        )

    if not session_id or len(session_id) > 120:
        raise ValueError('session_id inválido.')

    profile = get_profile(profile_name)
    model = model_name or RAG_MODEL

    blocked = aplicar_guardrails(question)

    retrieved = []
    status = 'respondido'

    if blocked:
        answer = blocked
        status = 'recusa_guardrail'

    else:
        lookup = (
            _question_for_retrieval(question, session_id)
            if preserve_history
            else question
        )

        retrieved = fetch_context(
            lookup,
            profile,
            max_distance=max_distance
        )

        if not retrieved:
            answer = REFUSAL
            status = 'recusa_sem_contexto'

        else:
            key = (profile.name, model)

            if key not in _chains:
                _chains[key] = build_chain(profile, model)

            h = []

            if preserve_history:
                for item in memory_snapshot(session_id):
                    if item['tipo'] == 'human':
                        h.append(
                            HumanMessage(content=item['conteudo'])
                        )
                    else:
                        h.append(
                            AIMessage(content=item['conteudo'])
                        )

            chain_inputs = {
                'pergunta': question,
                'context': format_context(retrieved),
                'history': h
            }

            # Primeira tentativa
            answer = _normalizar_citacoes(
                _chains[key].invoke(chain_inputs)
            )

            refs = cited_sources(answer, retrieved)

            # Segunda tentativa quando não há citação válida
            if answer != REFUSAL and not refs:
                segunda = _normalizar_citacoes(
                    _chains[key].invoke(chain_inputs)
                )

                novas_refs = cited_sources(
                    segunda,
                    retrieved
                )

                if segunda != REFUSAL and novas_refs:
                    answer = segunda
                    refs = novas_refs

            # Define o status final da resposta
            if answer == REFUSAL:
                status = 'recusa_modelo'

            elif not refs:
                answer = REFUSAL
                status = 'recusa_sem_citacao_valida'

    referenced = (
        cited_sources(answer, retrieved)
        if status == 'respondido'
        else []
    )

    if preserve_history:
        _save(session_id, question, answer)

    return {
        'answer': answer,
        'fontes': [
            {
                'id': r['id'],
                'documento': r['source'],
                'secao': r['section'],
                'pagina': r['page'],
                'origem': r['origin'],
                'distancia': r['distance']
            }
            for r in referenced
        ],
        'contextos_recuperados': retrieved,
        'status': status,
        'blocked_by_guardrail': bool(blocked),
        'model': model,
        'prompt_version': profile.prompt_version,
        'profile': profile.name,
        'embedding_model': EMBED_MODEL,
        'latency_ms': round(
            (time.perf_counter() - started) * 1000,
            2
        ),
        'output_tokens_approx': contar_tokens(answer),
        'memory_tokens_approx': (
            contar_tokens(
                ' '.join(
                    x['conteudo']
                    for x in memory_snapshot(session_id)
                )
            )
            if preserve_history
            else 0
        ),
    }
