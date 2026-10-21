"""Indexação reproduzível; ChromaDB persistente com coleção por iteração."""
import argparse
import hashlib
import json
import shutil
from pathlib import Path
from src.config import CONTEXT_PATH
from src.rag.settings import CORPUS, STORE_DIR, EMBED_MODEL, EMBED_PROVIDER, get_profile
from src.rag.chunking import split_documents
from src.rag.embeddings import build_embeddings
from src.rag.loader import load_knowledge_base

def corpus_fingerprint(profile):
    h = hashlib.sha256(f'v3:{EMBED_PROVIDER}:{EMBED_MODEL}:{profile.chunk_size}:{profile.overlap}'.encode())
    paths = sorted(p for p in CORPUS.rglob('*') if p.is_file() and p.suffix.lower() in {'.pdf','.txt','.md'} and not p.name.startswith('_'))
    if CONTEXT_PATH.exists(): paths.append(CONTEXT_PATH)
    for p in paths:
        h.update(p.relative_to(CORPUS.parent if p != CONTEXT_PATH else CONTEXT_PATH.parent).as_posix().encode())
        h.update(p.read_bytes())
    return h.hexdigest()

def index_path(profile):
    return STORE_DIR / profile.name

def open_store(profile):
    from langchain_chroma import Chroma
    path = index_path(profile)
    manifest = path / 'manifest.json'
    if not manifest.exists():
        raise RuntimeError(f'Índice {profile.name} ausente. Rode: python -m src.rag.vector_store --profile {profile.name}')
    data = json.loads(manifest.read_text(encoding='utf-8'))
    if data.get('fingerprint') != corpus_fingerprint(profile):
        raise RuntimeError(f'Índice {profile.name} desatualizado. Reindexe com --force antes de consultar.')
    return Chroma(collection_name=f'goodwe_{profile.name}',
                  persist_directory=str(path), embedding_function=build_embeddings(),
                  collection_metadata={'hnsw:space':'cosine'})

def build_index(profile, force=False):
    from langchain_chroma import Chroma
    path = index_path(profile)
    manifest = path / 'manifest.json'
    fp = corpus_fingerprint(profile)
    if manifest.exists() and not force:
        old = json.loads(manifest.read_text(encoding='utf-8'))
        if old.get('fingerprint') == fp:
            print(f'Índice {profile.name} já atualizado ({old.get("chunks")} chunks).')
            return old
        raise RuntimeError(f'Índice {profile.name} desatualizado. Use --force.')
    if path.exists(): shutil.rmtree(path)
    path.mkdir(parents=True,exist_ok=True)
    try:
        docs, quarantined = load_knowledge_base()
        chunks = split_documents(docs,profile)
        db = Chroma(collection_name=f'goodwe_{profile.name}',
                    persist_directory=str(path), embedding_function=build_embeddings(),
                    collection_metadata={'hnsw:space':'cosine'})
        # IDs determinísticos: elimina duplicados idênticos sem trocar provenance.
        unique = {c.metadata['chunk_id']: c for c in chunks}
        db.add_documents(list(unique.values()), ids=list(unique))
        result = {'profile':profile.name,'fingerprint':fp,'embedding_model':EMBED_MODEL,'embedding_provider':EMBED_PROVIDER,
                  'chunk_size':profile.chunk_size,'chunk_overlap':profile.overlap,
                  'documents':len(docs),'chunks':len(unique), 'quarantined':quarantined}
        manifest.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
        print(json.dumps(result,ensure_ascii=False,indent=2))
        return result
    except Exception:
        # Não deixar manifesto de sucesso quando falhar parcial/externamente.
        if manifest.exists(): manifest.unlink()
        raise

if __name__ == '__main__':
    parser=argparse.ArgumentParser(description='Indexar documentos no ChromaDB local persistente')
    parser.add_argument('--profile',choices=['iter1','iter2','all'],default='all')
    parser.add_argument('--force',action='store_true')
    args=parser.parse_args()
    for profile in ([get_profile(x) for x in ('iter1','iter2')] if args.profile=='all' else [get_profile(args.profile)]):
        build_index(profile,force=args.force)
