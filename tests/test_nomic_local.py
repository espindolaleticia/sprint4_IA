"""Testes isolados que simulam SentenceTransformer; nenhum download é feito."""
import pytest
from src.rag import embeddings
from src.rag.settings import EMBED_PROVIDER, get_profile

class Vectors:
    def __init__(self, n): self.n=n
    def tolist(self): return [[0.1]*768 for _ in range(self.n)]

class FakeSentenceTransformer:
    def __init__(self): self.calls=[]
    def encode(self, sentences, **kwargs):
        self.calls.append((sentences,kwargs))
        return Vectors(len(sentences))

@pytest.fixture
def fake_model(monkeypatch):
    model=FakeSentenceTransformer()
    monkeypatch.setattr(embeddings, '_load_model',lambda : model)
    return model

def test_query_and_document_prefixes(fake_model):
    client=embeddings.build_embeddings()
    assert len(client.embed_documents(['FAQ','Manual']))==2
    assert len(client.embed_query('Qual estação?'))==768
    assert fake_model.calls[0][0]==['search_document: FAQ','search_document: Manual']
    assert fake_model.calls[1][0]==['search_query: Qual estação?']
    assert fake_model.calls[0][1]['normalize_embeddings'] is True
    assert fake_model.calls[0][1]['convert_to_numpy'] is True

def test_no_additional_api_key_or_ollama_local(monkeypatch,fake_model):
    monkeypatch.delenv('NOMIC_API_KEY', raising=False)
    monkeypatch.delenv('OLLAMA_API_KEY', raising=False)
    monkeypatch.setenv('EMBED_OLLAMA_HOST','http://127.0.0.1:11434')
    assert embeddings.build_embeddings().embed_query('consulta')
    assert EMBED_PROVIDER=='sentence_transformers_local'
    assert not hasattr(embeddings,'NOMIC_URL')

def test_empty_documents_and_invalid_input(fake_model):
    client=embeddings.build_embeddings()
    assert client.embed_documents([])==[]
    with pytest.raises(ValueError,match='não vazias'):
        client.embed_documents(['valido',''])
    with pytest.raises(ValueError,match='não vazias'):
        client.embed_query('')
    with pytest.raises(ValueError,match='modelo oficial'):
        embeddings.NomicLocalEmbeddings(model='qualquer-outro')

def test_model_loaded_just_once_when_possible(monkeypatch):
    # A função de cache de modelo é guardada em um único módulo; os clientes
    # reutilizam o mesmo objeto até o processo finalizar.
    assert hasattr(embeddings._load_model,'cache_info')
    assert embeddings.MODEL_ID == 'nomic-ai/nomic-embed-text-v1.5'

def test_fingerprint_separates_indexes():
    from src.rag.vector_store import corpus_fingerprint
    assert len(corpus_fingerprint(get_profile('iter1')))==64
    assert corpus_fingerprint(get_profile('iter1'))!=corpus_fingerprint(get_profile('iter2'))
