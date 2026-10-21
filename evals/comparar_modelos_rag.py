"""Gera coleta para mais de um modelo, com prompt constante em cada perfil.

Não confunde sucesso técnico com RAGAS ou qualidade factual.
"""
import argparse
import json
import statistics
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from evals import avaliar_rag as avaliacao
from src.rag.settings import RAG_TEMPERATURE
from src.config import MODEL_NAME, MODEL_NAME_2, TOP_P, MAX_TOKENS

def run(profile,models,edition="original"):
    avaliacao.set_edition(edition)
    rows=[]
    for model in models:
        avaliacao.collect(profile,model)
        values=json.loads(avaliacao.path_for(profile,model).read_text(encoding='utf-8'))['results']
        valid=[x for x in values if 'erro' not in x]
        rows.append({'modelo':model,'prompt':'v1' if profile=='iter1' else 'v2',
                     'casos_processados_sem_erro':len(valid),'casos_sucesso':len(valid),'total':len(values),
                     'latencia_media_ms':round(statistics.mean(x['latencia_ms'] for x in valid),2) if valid else None,
                     'citacao_visivel_percent':round(100*sum(bool(x['fontes']) for x in valid)/len(valid),1) if valid else None})
    path=Path(__file__).resolve().parents[1]/'evals'/f'comparativo_modelos_{"hca_" if edition=="hca" else ""}{profile}.json'
    path.write_text(json.dumps({'profile':profile,'edition':edition,'temperature':RAG_TEMPERATURE,'top_p':TOP_P,
                       'max_tokens':MAX_TOKENS,'models':rows},ensure_ascii=False,indent=2),encoding='utf8')
    report=Path(__file__).resolve().parents[1]/'docs'/('relatorio_modelos_hca.md' if edition=='hca' else 'relatorio_modelos.md')
    existing=report.read_text(encoding='utf-8') if report.exists() else '# Relatório de modelos - Sprint 04\n'
    marker='## Comparação efetiva Sprint 04 (gerada automaticamente)'
    existing=existing.split(marker)[0].rstrip()+'\n\n'
    lines=[marker,'',f'Perfil de comparação: {profile}; temperatura RAG = {RAG_TEMPERATURE}; top_p = {TOP_P}; max_tokens = {MAX_TOKENS}.',
           '','| Modelo | Prompt | Casos válidos | Latência média (ms) | Respostas com citação |',
           '|---|---|---:|---:|---:|']
    for item in rows:
        lat='PENDENTE' if item['latencia_media_ms'] is None else str(item['latencia_media_ms'])
        cit='PENDENTE' if item['citacao_visivel_percent'] is None else str(item['citacao_visivel_percent'])+'%'
        lines.append(f'| {item["modelo"]} | {item["prompt"]} | {item["casos_sucesso"]}/{item["total"]} | {lat} | {cit} |')
    lines+=['','**Atenção:** presença de citação não demonstra faithfulness; aplicar rubrica humana ou RAGAS para qualidade factual.']
    report.write_text(existing+'\n'.join(lines)+'\n',encoding='utf-8')
    print('Comparativo salvo em',path,'e',report)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--profile',choices=['iter1','iter2'],default='iter2')
    p.add_argument('--models',nargs='+',default=[MODEL_NAME,MODEL_NAME_2])
    p.add_argument('--edition',choices=['original','hca'],default='original');args=p.parse_args()
    if len(set(args.models))<2:raise ValueError('Informe pelo menos dois modelos distintos.')
    run(args.profile,args.models,args.edition)
