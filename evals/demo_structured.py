import json
import sys
from pathlib import Path

from langchain_core.exceptions import OutputParserException
from pydantic import ValidationError

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.service import processar_estruturado

try:
    resultado = processar_estruturado(
        "Qual estação apresentou maior consumo energético hoje?"
    )
    print("Objeto Pydantic validado:")
    print(json.dumps(resultado.model_dump(), ensure_ascii=False, indent=2))
except (ValidationError, OutputParserException) as erro:
    print("Erro de validação do structured output:")
    print(erro)
