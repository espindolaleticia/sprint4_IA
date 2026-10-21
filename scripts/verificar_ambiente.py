"""Inspeciona dependências e status do índice sem ler/imprimir chaves."""
import importlib.util
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.config import OLLAMA_API_KEY, OLLAMA_HOST
from src.rag.settings import CORPUS, STORE_DIR, EMBED_MODEL, EMBED_PROVIDER, RAG_MODEL, get_profile
from src.rag.vector_store import corpus_fingerprint

print('Ambiente Sprint 04 | credenciais nunca exibidas')
required = ['langchain_core','langchain_community','langchain_ollama','langchain_chroma',
            'langchain_text_splitters','chromadb','gradio','fitz','tiktoken','reportlab',
            'sentence_transformers','transformers','torch']
missing=[]
for name in required:
    installed = importlib.util.find_spec(name) is not None
    print(f'  {name}: {"instalado" if installed else "AUSENTE"}')
    if not installed:
        missing.append(name)
print('Ollama host (chat):', OLLAMA_HOST)
print('Chave da Ollama configurada?', bool(OLLAMA_API_KEY))
print('Embeddings:', EMBED_PROVIDER, '(grátis, após download automático do modelo)')
print('Modelo de embeddings:', EMBED_MODEL)
print('Modelo RAG:', RAG_MODEL)
print('Documentos na base:',len([x for x in CORPUS.rglob('*') if x.is_file() and x.suffix.lower() in ('.pdf','.md','.txt') and not x.name.startswith('_')]))
local=CORPUS/'hca_g2_local'
files=('GW_HCA-G2_Datasheet-PT.pdf','GW_HCA-G2_User-Manual-PT.pdf','Mapa MODBUS_HCA G2.pdf')
print('HCA G2: arquivos locais instalados:',sum((local/x).is_file() for x in files),'de 3')
print('Referência HCA G2 ≠ ID de estação simulada GW-XX.')
for name in ('iter1','iter2'):
    profile=get_profile(name)
    manifest=STORE_DIR/name/'manifest.json'
    if not manifest.exists():
        print(name, ': PENDENTE de indexação')
    else:
        info=json.loads(manifest.read_text(encoding='utf-8'))
        print(name, ':', 'atualizado' if info.get('fingerprint')==corpus_fingerprint(profile) else 'DESATUALIZADO', '-',info.get('chunks'),'chunks')
if missing: print('AÇÃO: python -m pip install -r requirements.txt')
print('ATENÇÃO: esta verificação não baixa o modelo nem testa Ollama Cloud; execute scripts/testar_embeddings.py.')
