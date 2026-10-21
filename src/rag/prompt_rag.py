"""Prompt LCEL versionado. Contexto recuperado nunca vira mensagem system nova."""
from src.config import BASE_DIR

def prompt_text(version: str):
    if version not in {'v1','v2'}:
        raise ValueError(f'Versão desconhecida: {version}')
    return (BASE_DIR/'prompts'/f'rag_{version}.md').read_text(encoding='utf-8')

def build_chain(profile, model_name=None):
    from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
    from langchain_core.output_parsers import StrOutputParser
    from langchain_ollama import ChatOllama
    from src.config import OLLAMA_API_KEY, OLLAMA_HOST, TOP_P, MAX_TOKENS
    from src.rag.settings import RAG_MODEL, RAG_TEMPERATURE
    instructions=prompt_text(profile.prompt_version)
    # A sintaxe do ChatPromptTemplate interpreta chaves: escapa exemplos JSON no prompt.
    instructions=instructions.replace('{','{{').replace('}','}}')
    template=ChatPromptTemplate.from_messages([
        ('system',instructions+'\n\n<base_nao_confiavel>\n{context}\n</base_nao_confiavel>'),
        MessagesPlaceholder(variable_name='history'),
        ('human','{pergunta}'),
    ])
    llm_config={'model':model_name or RAG_MODEL,'base_url':OLLAMA_HOST,
                'temperature':RAG_TEMPERATURE,'top_p':TOP_P,'num_predict':MAX_TOKENS}
    if OLLAMA_API_KEY:
        llm_config['client_kwargs']={'headers':{'Authorization':f'Bearer {OLLAMA_API_KEY}'}}
    elif 'ollama.com' in OLLAMA_HOST:
        raise RuntimeError('OLLAMA_API_KEY ausente. Configure-a no .env local.')
    return template | ChatOllama(**llm_config) | StrOutputParser()
