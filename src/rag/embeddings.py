"""Embeddings gratuitos Nomic Embed v1.5 em Python (sem Ollama desktop/API Nomic).

O modelo oficial é baixado pelo Hugging Face no PRIMEIRO uso e mantido em cache.
Os textos dos documentos não são enviados a nenhuma API de embeddings.
A geração de respostas continua pela Ollama Cloud (configuração Sprint 3).

Fonte: https://huggingface.co/nomic-ai/nomic-embed-text-v1.5
"""
import math
import os
from functools import lru_cache

from src.rag.settings import EMBED_MODEL

# Mesmo modelo em consultas e documentos; nomes de tarefas diferentes evitam
# misturar vetores com significados de treinamento diferentes.
MODEL_ID = "nomic-ai/nomic-embed-text-v1.5"

@lru_cache(maxsize=1)
def _load_model():
    try:
        from sentence_transformers import SentenceTransformer
    except ImportError as exc:
        raise RuntimeError(
            "Falta sentence-transformers. Execute: python -m pip install -r requirements.txt"
        ) from exc
    try:
        # A partir de transformers 5.5 / sentence-transformers 5.3, o modelo
        # tem suporte nativo sem executar código remoto do repositório.
        return SentenceTransformer(MODEL_ID, device="cpu", trust_remote_code=False)
    except Exception as exc:
        raise RuntimeError(
            "Não foi possível carregar o Nomic local. Na primeira execução é "
            "necessária internet para baixar o modelo Hugging Face (uma vez). "
            "Confira a conexão, espaço livre e as versões de "
            "sentence-transformers/transformers em requirements.txt. "
            f"Detalhe técnico: {type(exc).__name__}: {str(exc)[:250]}"
        ) from exc

class NomicLocalEmbeddings:
    """Interface de embeddings esperada por LangChain/ChromaDB.

    Tanto documentos quanto perguntas utilizam 768 dimensões e prefixos
    explícitos recomendados pela documentação oficial do Nomic Embed.
    """
    def __init__(self, model: str = EMBED_MODEL, batch_size: int = 8):
        if model not in ("nomic-embed-text", "nomic-embed-text-v1.5", MODEL_ID):
            raise ValueError("Use o modelo oficial nomic-ai/nomic-embed-text-v1.5.")
        if not 1 <= batch_size <= 64:
            raise ValueError("batch_size deve ser de 1 a 64.")
        self.model = "nomic-embed-text-v1.5"
        self.model_id = MODEL_ID
        self.batch_size = batch_size

    def _encode(self, texts: list[str], prefix: str) -> list[list[float]]:
        if not texts:
            return []
        if any(not isinstance(t, str) or not t.strip() for t in texts):
            raise ValueError("Todos os textos para embedding devem ser strings não vazias.")
        samples = [f"{prefix}: {t}" for t in texts]
        model = _load_model()
        result = model.encode(
            samples, batch_size=self.batch_size,
            show_progress_bar=False, normalize_embeddings=True,
            convert_to_numpy=True,
        )
        vectors = result.tolist() if hasattr(result, "tolist") else list(result)
        if len(vectors) != len(texts):
            raise RuntimeError("Modelo Nomic retornou quantidade inesperada de vetores.")
        for vector in vectors:
            if len(vector) != 768 or not all(
                isinstance(x, (int, float)) and math.isfinite(x) for x in vector
            ):
                raise RuntimeError("Modelo Nomic retornou embedding inválido (esperado 768 dimensões).")
        return [[float(x) for x in vector] for vector in vectors]

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return self._encode(texts, "search_document")

    def embed_query(self, text: str) -> list[float]:
        return self._encode([text], "search_query")[0]


def build_embeddings():
    # A chave Ollama serve SOMENTE para o LLM; nenhuma segunda chave é exigida.
    return NomicLocalEmbeddings(os.getenv("EMBED_MODEL", EMBED_MODEL).strip())
