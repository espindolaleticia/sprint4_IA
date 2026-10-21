"""Auditoria OFFLINE do pacote público: nunca chama Ollama nem requer PDFs privados.

Não substitui verificação de coletas e rubricas completas no computador do grupo.
"""
from pathlib import Path
import json, sys, math

ROOT=Path(__file__).resolve().parents[1]
E=ROOT/'evals'; DOC=ROOT/'docs'

checks=[]
def ck(ok,msg):
    checks.append(bool(ok))
    print(('OK  ' if ok else 'ERRO')+' '+msg)
    return ok

def get(file):
    return json.loads(file.read_text(encoding='utf8'))

for rel in ['README.md','src/rag/service.py','src/rag/vector_store.py', 'src/guardrails/moderation.py',
            'app/gradio_app.py','scripts/importar_hca_g2.py','prompts/rag_v1.md','prompts/rag_v2.md',
            'docs/GUIA_ENTREGA_FINAL.md','docs/GoodWe Grid Assistant.pdf']:
    ck((ROOT/rel).exists(),rel)

report=get(E/'resultados_hca_confirmados_publicaveis.json')
marks=get(E/'notas_resumidas_publicaveis_hca.json')
caseids={x['id'] for x in get(E/'rag_eval_set.json')+get(E/'rag_eval_hca_g2.json')}
ck(len(caseids)==22, '22 IDs únicos no conjunto de teste HCA')
ck(len(marks['casos'])==66, '66 pontuações resumidas de 3 versões')

for ver in ('iter1','iter2','iter2_seguranca_v2'):
    subset=[x for x in marks['casos'] if x['versao']==ver]
    ck(len(subset)==22 and {x['id'] for x in subset}==caseids,f'22 notas por caso da versão {ver}')
    if len(subset)==22:
        for metric in ('faithfulness','answer_relevancy'):
            average=round(sum(x[metric] for x in subset)/22,4)
            recorded=report['scores'][ver][metric]
            ck(math.isclose(average,recorded,abs_tol=.00005),f'Notas de {metric} batem com resultado de {ver}: {average}')

ck(report['gain_both_metrics_vs_iter1'] is True,'ganho estrito verificado vs iter1')
prev=get(E/'resultado_sprint4_hca.json')
fin=get(E/'resultado_sprint4_hca_safety.json')
ck(prev['profiles']['iter1']['complete'] and prev['profiles']['iter2']['complete'],'relatório HCA intermediário completo (saída relatada pelo grupo)')
ck(prev['gain_both_metrics'] is False,'I2 empatou na relevância com I1')
ck(fin['profiles']['iter2_seguranca_v2']['complete'] and fin['gain_both_metrics_vs_iter1'] is True,
   'relatório HCA safety completo (saída relatada pelo grupo)')
ck(not (ROOT/'.env').is_file(),'pacote público não inclui credencial .env')
ck(not (ROOT/'data/chroma_db').exists(),'pacote público não inclui ChromaDB local')
ck(not (ROOT/'data/knowledge_base/hca_g2_local').exists(),'pacote público não inclui PDFs GoodWe')
ck(not list(E.glob('coleta_hca_*.json')),'pacote público não inclui coletas HCA com excertos protegidos')
ck(not list(E.glob('rubrica_anotacoes_hca*.json')),'pacote público não inclui rubricas originais identificadas')
try:
    import pymupdf
    pdf=pymupdf.open(str(DOC/'GoodWe Grid Assistant.pdf'))
    ck(len(pdf)==5,'relatório PDF possui 5 páginas')
    text=' '.join(p.get_text() for p in pdf)
    ck('0,9773' in text and '1,0000' in text,'PDF contém as métricas HCA atualizadas')
except ImportError:
    print('AVISO PyMuPDF não instalado; contagem de páginas não verificada nesta execução.')

print('\nATENÇÃO: coletas/rubricas ORIGINAIS não são incluídas neste pacote público.')
print('Para auditoria humana integral, utilize os arquivos locais do grupo e os fingerprints do corpus.')
print('ATENÇÃO: faltam regimento condominial/tarifa verificáveis e aprovação docente do provedor Nomic local.')
if all(checks):
    print('\nPACOTE PÚBLICO: validações estáticas aprovadas. Não comprova execução da Ollama no clone.');sys.exit(0)
print('\nPACOTE PÚBLICO: há verificações com erro.');sys.exit(1)
