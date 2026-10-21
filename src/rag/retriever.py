"""Recuperação semântica, filtro de distância e referências auditáveis."""
import re
from xml.sax.saxutils import escape as escape_xml
from src.rag.vector_store import open_store
from src.rag.settings import RAG_MAX_DISTANCE

def fetch_context(question, profile, *, max_distance=None):
    store = open_store(profile)
    pairs = store.similarity_search_with_score(question,k=profile.k)
    limit = RAG_MAX_DISTANCE if max_distance is None else max_distance
    out=[]
    for document, distance in pairs:
        if float(distance)>limit: continue
        m=document.metadata
        out.append({'id':f'F{len(out)+1}', 'text':document.page_content,
                    'source':m.get('source','desconhecida'),
                    'section':m.get('section','Sem seção'),
                    'page':int(m['page'])+1 if m.get('page') is not None else None,
                    'origin':m.get('origin','documento'),
                    'distance':round(float(distance),4)})
    return out

def _attr(value):
    return escape_xml(str(value), {'"': '&quot;', "'": '&apos;'})

def format_context(items):
    # XML-escape document payloads: text from retrieval must not close wrapper tags.
    return '\n\n'.join(
        f'<trecho id="{_attr(item["id"])}" fonte="{_attr(item["source"])}" secao="{_attr(item["section"])}" pagina="{_attr(item["page"] or "-")}">\n'
        f'{escape_xml(item["text"])}\n</trecho>'
        for item in items
    )

def cited_sources(answer, chunks):
    identifiers = list(dict.fromkeys(re.findall(r'\[F\d+\]', answer)))
    valid={f'[{c["id"]}]':c for c in chunks}
    if any(ident not in valid for ident in identifiers): return []
    return [valid[ident] for ident in identifiers]
