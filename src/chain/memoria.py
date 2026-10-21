from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_classic.memory import ConversationTokenBufferMemory

from src.chain.builder import criar_llm
from src.config import MEMORY_TOKEN_LIMIT
from src.context_loader import contar_tokens

_memorias: dict[str, ConversationTokenBufferMemory] = {}
_llm_memoria = None


def _obter_llm_memoria():
    global _llm_memoria
    if _llm_memoria is None:
        _llm_memoria = criar_llm()
    return _llm_memoria


def obter_memoria(session_id: str) -> ConversationTokenBufferMemory:
    if session_id not in _memorias:
        _memorias[session_id] = ConversationTokenBufferMemory(
            llm=_obter_llm_memoria(),
            memory_key="history",
            return_messages=True,
            max_token_limit=MEMORY_TOKEN_LIMIT,
        )
    return _memorias[session_id]


def obter_historico(session_id: str):
    return obter_memoria(session_id).chat_memory


def criar_chain_com_memoria(chain_base):
    return RunnableWithMessageHistory(
        chain_base,
        obter_historico,
        input_messages_key="pergunta",
        history_messages_key="history",
    )


def tokens_memoria(session_id: str) -> int:
    mensagens = obter_memoria(session_id).chat_memory.messages
    texto = "\n".join(str(m.content) for m in mensagens)
    return contar_tokens(texto)


def podar_memoria(session_id: str) -> None:
    """
    RunnableWithMessageHistory grava diretamente no chat_memory. Por isso,
    fazemos a poda explícita pelo limite de tokens configurado na
    ConversationTokenBufferMemory, preservando pares recentes usuário/IA.
    """
    memoria = obter_memoria(session_id)
    mensagens = memoria.chat_memory.messages

    while mensagens and tokens_memoria(session_id) > memoria.max_token_limit:
        if len(mensagens) >= 2:
            del mensagens[:2]
        else:
            del mensagens[:1]


def registrar_interacao_guardrail(session_id: str, pergunta: str, resposta: str) -> None:
    memoria = obter_memoria(session_id)
    memoria.chat_memory.add_message(HumanMessage(content=pergunta))
    memoria.chat_memory.add_message(AIMessage(content=resposta))
    podar_memoria(session_id)


def resetar_memoria(session_id: str) -> None:
    _memorias.pop(session_id, None)


def snapshot_memoria(session_id: str) -> list[dict]:
    if session_id not in _memorias:
        return []
    return [
        {"tipo": mensagem.type, "conteudo": str(mensagem.content)}
        for mensagem in _memorias[session_id].chat_memory.messages
    ]
