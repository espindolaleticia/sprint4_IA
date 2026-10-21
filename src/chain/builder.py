import os

from langchain_core.output_parsers import PydanticOutputParser, StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_ollama import ChatOllama

from src.config import (
    MAX_TOKENS,
    MODEL_NAME,
    OLLAMA_API_KEY,
    OLLAMA_HOST,
    TEMPERATURE,
    TOP_P,
)
from src.context_loader import carregar_prompt
from src.schemas.consulta_recarga import ConsultaRecarga


def criar_llm(
    model_name: str | None = None,
    json_mode: bool = False,
    num_predict: int | None = None,
) -> ChatOllama:

    if not OLLAMA_API_KEY:
        raise RuntimeError(
            "OLLAMA_API_KEY não encontrada. Confira o arquivo .env na raiz do projeto."
        )

    os.environ["OLLAMA_HOST"] = OLLAMA_HOST
    os.environ["OLLAMA_API_KEY"] = OLLAMA_API_KEY

    parametros = {
        "model": model_name or MODEL_NAME,
        "base_url": OLLAMA_HOST,
        "temperature": TEMPERATURE,
        "top_p": TOP_P,
        "num_predict": num_predict if num_predict is not None else MAX_TOKENS,
        "client_kwargs": {
            "headers": {
                "Authorization": f"Bearer {OLLAMA_API_KEY}"
            }
        },
    }

    if json_mode:
        parametros["format"] = ConsultaRecarga.model_json_schema()

    return ChatOllama(**parametros)


def criar_chain_conversa(
    prompt_version: str | None = None,
    model_name: str | None = None,
):
    system_prompt = carregar_prompt(prompt_version)

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                system_prompt
                + "\n\n<operational_context>\n{contexto_operacional}\n</operational_context>",
            ),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{pergunta}"),
        ]
    )

    llm = criar_llm(model_name=model_name)
    parser = StrOutputParser()

    return prompt | llm | parser


def criar_chain_estruturada(
    prompt_version: str | None = None,
    model_name: str | None = None,
):
    system_prompt = carregar_prompt(prompt_version)
    parser = PydanticOutputParser(pydantic_object=ConsultaRecarga)

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                system_prompt
                + "\n\n<operational_context>\n{contexto_operacional}\n</operational_context>"
                + "\n\n<structured_output>\n{format_instructions}\n</structured_output>"
                + """
                    Retorne SOMENTE o JSON solicitado, sem markdown e sem texto fora do JSON.

                    REGRAS OBRIGATÓRIAS:
                    - Preencha TODOS os campos definidos no schema.
                    - Nunca omita o campo "resumo".
                    - Se um dado opcional não estiver disponível, use null.
                    - Para listas sem dados, use [].
                    - O campo "resumo" deve sempre conter uma frase curta com a conclusão da consulta.
                    """,
            ),
            ("human", "{pergunta}"),
        ]
    ).partial(format_instructions=parser.get_format_instructions())

    llm = criar_llm(
    model_name=model_name,
    json_mode=True,
    num_predict=1000,
)

    return prompt | llm | parser
