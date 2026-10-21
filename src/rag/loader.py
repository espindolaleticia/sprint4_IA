"""Documentos de conhecimento, com origem explícita e isolamento de instruções maliciosas."""
from pathlib import Path
import json
import re
from src.config import BASE_DIR, CONTEXT_PATH
from src.rag.settings import CORPUS

# Não é um antivírus nem uma defesa completa; remove tentativas diretas conhecidas.
ATTACK_PATTERNS = re.compile(
    r'(ignore (todas? )?(as )?instru[cç][oõ]es|ignore previous instructions|'
    r'\bsystem prompt\b|\bdeveloper message\b|\brole\s*:\s*system\b|'
    r'\brevele (as )?instru[cç][oõ]es\b|\bdesconsidere as regras\b)',
    re.IGNORECASE,
)

def suspicious(text: str) -> bool:
    return bool(ATTACK_PATTERNS.search(text))

def _safe_source(path: Path) -> str:
    return path.resolve().relative_to(BASE_DIR.resolve()).as_posix()

def load_knowledge_base():
    """Suporta PDFs com PyMuPDFLoader, markdown, TXT e snapshot operacional JSON."""
    from langchain_core.documents import Document
    from langchain_community.document_loaders import PyMuPDFLoader
    documents = []
    quarantined = []
    for path in sorted(CORPUS.rglob('*')):
        if not path.is_file() or path.suffix.lower() not in {'.pdf','.md','.txt'}:
            continue
        if path.name.startswith('_'):
            continue
        source = _safe_source(path)
        if path.suffix.lower() == '.pdf':
            for doc in PyMuPDFLoader(str(path)).load():
                if not doc.page_content.strip():
                    continue
                if suspicious(doc.page_content):
                    quarantined.append(f'{source} - página {doc.metadata.get("page", 0)+1}')
                    continue
                doc.metadata = {'source':source, 'section':'Página do PDF',
                                'page': int(doc.metadata.get('page',0)), 'origin':'documento'}
                documents.append(doc)
        else:
            content = path.read_text(encoding='utf-8-sig')
            section = 'Introdução'
            block = []
            def flush():
                txt = '\n'.join(block).strip()
                if txt:
                    if suspicious(txt): quarantined.append(f'{source} - {section}')
                    else: documents.append(Document(page_content=txt,
                        metadata={'source':source,'section':section,'origin':'documento'}))
            for line in content.splitlines():
                if re.match(r'^#{1,3}\s+',line):
                    flush();block.clear();section=line.lstrip('# ').strip()[:120]
                else:
                    block.append(line)
            flush()
    if CONTEXT_PATH.exists():
        data = json.loads(CONTEXT_PATH.read_text(encoding='utf-8'))
        for key, value in data.items():
            if key in {'versao','tipo','descricao'}: continue
            text = f'BASE OPERACIONAL SIMULADA (não representa medições em tempo real). Categoria: {key}.\n'
            text += json.dumps(value,ensure_ascii=False,indent=2)
            if suspicious(text):
                quarantined.append(f'contexto_operacional.json - {key}')
                continue
            documents.append(Document(page_content=text,
                metadata={'source':'contexto_operacional.json','section':key.replace('_',' ').title(),
                          'origin':'simulacao'}))
    if not documents:
        raise RuntimeError('Base vazia. Adicione documentação validada em data/knowledge_base/.')
    return documents, quarantined
