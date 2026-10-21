import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parents[1]
PROMPTS_DIR = BASE_DIR / "prompts"
CONTEXT_PATH = BASE_DIR / "contexto_operacional.json"

OLLAMA_API_KEY = os.getenv("OLLAMA_API_KEY", "").strip()
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "https://ollama.com").strip()
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-oss:120b").strip()
MODEL_NAME_2 = os.getenv("MODEL_NAME_2", "qwen3:8b").strip()
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.2"))
TOP_P = float(os.getenv("TOP_P", "0.9"))
MAX_TOKENS = int(os.getenv("MAX_TOKENS", "350"))
MEMORY_TOKEN_LIMIT = int(os.getenv("MEMORY_TOKEN_LIMIT", "1200"))
SYSTEM_PROMPT_VERSION = os.getenv("SYSTEM_PROMPT_VERSION", "v2").strip()


def prompt_path(version: str | None = None) -> Path:
    versao = version or SYSTEM_PROMPT_VERSION
    return PROMPTS_DIR / f"system_prompt_{versao}.md"
