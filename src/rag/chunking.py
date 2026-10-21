"""Divisão recursiva mantendo metadados de procedência."""
import hashlib

def split_documents(documents, profile):
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=profile.chunk_size, chunk_overlap=profile.overlap,
        separators=['\n\n', '\n', '. ', ' ', ''],
    )
    chunks = splitter.split_documents(documents)
    for i, chunk in enumerate(chunks):
        provenance = f'{chunk.metadata.get("source")}:{chunk.metadata.get("section")}:{chunk.metadata.get("page", "")}'
        chunk.metadata['chunk_id'] = hashlib.sha256(
            (provenance + '|' + chunk.page_content).encode('utf-8')
        ).hexdigest()[:20]
    return chunks
