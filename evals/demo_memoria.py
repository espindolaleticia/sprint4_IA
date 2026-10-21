import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.service import inspecionar_memoria, limpar_sessao, processar_chat

session_id = "demo-memoria-sprint3"
limpar_sessao(session_id)

perguntas = [
    "Qual estação apresentou superaquecimento?",
    "Em qual horário isso ocorreu?",
    "Ela foi desativada automaticamente?",
    "O que você recomenda para ela agora?",
]

for numero, pergunta in enumerate(perguntas, start=1):
    resultado = processar_chat(pergunta, session_id)
    print(f"\nTURNO {numero}")
    print("Usuário:", pergunta)
    print("Assistente:", resultado["answer"])
    print("Tokens aproximados da memória:", resultado["memory_tokens_approx"])

print("\n=== ESTADO FINAL DA MEMÓRIA ===")
print(json.dumps(inspecionar_memoria(session_id), ensure_ascii=False, indent=2))
