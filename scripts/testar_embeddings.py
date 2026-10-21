"""Teste gratuito de embeddings locais (o primeiro uso baixa o modelo Nomic)."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.rag.embeddings import build_embeddings

if __name__ == '__main__':
    try:
        client = build_embeddings()
        vetor_pergunta = client.embed_query('Como consultar o estado de um eletroposto?')
        vetor_documento = client.embed_documents(['Registro operacional acadêmico de um eletroposto.'])[0]
        assert len(vetor_pergunta) == len(vetor_documento) == 768
        print('Embeddings locais Nomic: OK')
        print('Modelo:', client.model_id)
        print('Dimensões: 768 | query e documento: OK')
        print('Não foi utilizada uma API de embeddings nem uma chave adicional.')
    except (RuntimeError, ValueError, ImportError, OSError) as exc:
        print('Falha ao iniciar Nomic local:', exc)
        raise SystemExit(1)
