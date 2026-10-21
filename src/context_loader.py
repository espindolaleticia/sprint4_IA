import json
from pathlib import Path

import tiktoken

from src.config import CONTEXT_PATH, prompt_path


def carregar_prompt(version: str | None = None) -> str:
    caminho = prompt_path(version)
    if not caminho.exists():
        raise FileNotFoundError(f"System prompt não encontrado: {caminho}")
    return caminho.read_text(encoding="utf-8").strip()


def carregar_contexto_dict(caminho: Path = CONTEXT_PATH) -> dict:
    if not caminho.exists():
        raise FileNotFoundError(f"Contexto operacional não encontrado: {caminho}")
    with caminho.open("r", encoding="utf-8") as arquivo:
        dados = json.load(arquivo)
    if not isinstance(dados, dict):
        raise ValueError("O contexto operacional precisa ser um objeto JSON.")
    return dados


def carregar_contexto_texto() -> str:
    
    return json.dumps(
        carregar_contexto_dict(), ensure_ascii=False, indent=2
    )


def contar_tokens(texto: str, modelo_aproximado: str = "gpt-4") -> int:
    """Contagem aproximada, conforme a prática da Aula 04 com tiktoken."""
    try:
        encoding = tiktoken.encoding_for_model(modelo_aproximado)
    except KeyError:
        encoding = tiktoken.get_encoding("cl100k_base")
    return len(encoding.encode(texto))
