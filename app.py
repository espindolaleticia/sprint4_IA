from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from src.service import (
    inspecionar_memoria,
    limpar_sessao,
    processar_chat,
    processar_estruturado,
)

BASE_DIR = Path(__file__).resolve().parent
HTML_PATH = BASE_DIR / "interface.html"

app = FastAPI(title="GoodWe Grid Assistant — Sprint 4 (RAG)")


class ChatRequest(BaseModel):
    message: str
    session_id: str = "default"


class ResetRequest(BaseModel):
    session_id: str = "default"


@app.get("/", response_class=HTMLResponse)
def home():
    if not HTML_PATH.exists():
        return HTMLResponse("Arquivo interface.html não encontrado.", status_code=500)
    return HTML_PATH.read_text(encoding="utf-8")


@app.post("/api/chat")
def chat(request: ChatRequest):
    try:
        return processar_chat(request.message, request.session_id)
    except ValueError as erro:
        raise HTTPException(status_code=400, detail=str(erro)) from erro
    except Exception as erro:
        # Evita devolver caminhos, erros do provedor ou credenciais para o cliente.
        print(f"Erro de execução: {type(erro).__name__}: {erro}")
        raise HTTPException(status_code=503, detail="RAG indisponível. Confira indexação, .env e conexões Ollama/Nomic.") from erro


@app.post("/api/structured")
def structured(request: ChatRequest):
    try:
        resultado = processar_estruturado(request.message)
        return resultado.model_dump()
    except ValueError as erro:
        raise HTTPException(status_code=400, detail=str(erro)) from erro
    except ValueError as erro:
        raise HTTPException(status_code=400, detail=str(erro)) from erro
    except Exception as erro:
        # Evita devolver caminhos, erros do provedor ou credenciais para o cliente.
        print(f"Erro de execução: {type(erro).__name__}: {erro}")
        raise HTTPException(status_code=503, detail="RAG indisponível. Confira indexação, .env e conexões Ollama/Nomic.") from erro


@app.post("/api/reset")
def reset(request: ResetRequest):
    limpar_sessao(request.session_id)
    return {"ok": True}


@app.get("/api/memory/{session_id}")
def memory(session_id: str):
    return inspecionar_memoria(session_id)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=False)
