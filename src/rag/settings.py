"""Configuração dos experimentos; perfis imutáveis para comparação justa."""
from dataclasses import dataclass
from pathlib import Path
import os
from src.config import BASE_DIR, MODEL_NAME, MODEL_NAME_2, TOP_P, MAX_TOKENS, OLLAMA_API_KEY, OLLAMA_HOST

CORPUS = BASE_DIR / 'data' / 'knowledge_base'
STORE_DIR = BASE_DIR / 'data' / 'chroma_db'
# Alias da configuração antiga do Ollama, para facilitar migracao do .env.
EMBED_MODEL = os.getenv('EMBED_MODEL', 'nomic-embed-text-v1.5').strip()
if EMBED_MODEL == 'nomic-embed-text':
    EMBED_MODEL = 'nomic-embed-text-v1.5'
EMBED_PROVIDER = 'sentence_transformers_local'
RAG_MODEL = os.getenv('RAG_MODEL', MODEL_NAME)
RAG_PROMPT_VERSION = os.getenv('RAG_PROMPT_VERSION', 'v2')
RAG_PROFILE = os.getenv('RAG_PROFILE', 'iter2')
RAG_K = int(os.getenv('RAG_K', '4'))
RAG_MAX_DISTANCE = float(os.getenv('RAG_MAX_DISTANCE', '0.65'))
# Separate generation temperature from legacy Sprint-3 TEMPERATURE. Historical RAG used 0.
RAG_TEMPERATURE = float(os.getenv('RAG_TEMPERATURE', '0'))
# Quadro de testes: manter modelo e conjunto de perguntas fixos; alterar chunk/prompt.
@dataclass(frozen=True)
class Profile:
    name: str
    chunk_size: int
    overlap: int
    prompt_version: str
    k: int

PROFILES = {
    'iter1': Profile('iter1', 400, 40, 'v1', 3),
    'iter2': Profile('iter2', 750, 100, 'v2', 4),
}

def get_profile(name: str | None = None) -> Profile:
    key = name or RAG_PROFILE
    if key not in PROFILES:
        raise ValueError(f'Perfil desconhecido: {key}. Disponíveis: {list(PROFILES)}')
    return PROFILES[key]
