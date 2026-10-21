"""Interface Gradio obrigatória da Sprint 04 - usa exatamente o RAG da API."""
import os
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import gradio as gr
from src.rag.service import answer_question


def chat(message, history, request: gr.Request):
    session_id=f'gradio-{request.session_hash}' if request and request.session_hash else 'gradio-standalone'
    try:
        result=answer_question(message,session_id=session_id)
        citations=[]
        for source in result['fontes']:
            page=f', pág. {source["pagina"]}' if source['pagina'] else ''
            citations.append(f'- [{source["id"]}] `{source["documento"]}` - {source["secao"]}{page}')
        if citations:
            return result['answer']+'\n\n**Fontes consultadas**\n'+'\n'.join(citations)
        return result['answer']+'\n\n*Sem citação: resposta de recusa; não há informação documental afirmada.*'
    except Exception as ex:
        # Não exibir credenciais, endpoints privados ou stack traces no navegador.
        print(f'[erro Gradio] {type(ex).__name__}: {ex}',file=sys.stderr)
        return ('Índice ou conexão indisponível. Confira o terminal, as chaves Ollama/Nomic em .env '
                'e execute `python -m src.rag.vector_store --profile all`.')

with gr.Blocks(title='GoodWe Grid Assistant | Sprint 04') as demo:
    gr.Markdown('## GoodWe Grid Assistant - RAG com fontes')
    gr.Markdown('**Base acadêmica simulada.** Os dados não representam telemetria em tempo real. '
                'Respostas documentais têm citações como [F1], [F2].')
    gr.ChatInterface(fn=chat, examples=[
        'Quais estações estão offline?',
        'O que aconteceu com a GW-09?',
        'Qual foi o faturamento semanal simulado?',
        'Qual é a tarifa contratual por kWh?',
    ])
if __name__=='__main__':
    demo.launch(server_name='127.0.0.1',server_port=int(os.getenv('GRADIO_PORT','7860')),
                share=os.getenv('GRADIO_SHARE','false').lower()=='true')
