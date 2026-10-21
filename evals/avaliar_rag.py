"""Coleta resultados REAIS; fallback por anotação humana 0 / 0.5 / 1.

Nenhum score é criado automaticamente a partir de uma resposta simulada.
"""
import argparse
import hashlib
from datetime import datetime,timezone
import json
from pathlib import Path
import statistics
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
EVALS=ROOT/'evals'
CASES=json.loads((EVALS/'rag_eval_set.json').read_text(encoding='utf-8'))
EDITION='original'

def set_edition(name):
    """Separa avaliações pós-importação HCA das coletas e notas históricas."""
    global CASES, EDITION
    EDITION = name
    CASES = json.loads((EVALS/'rag_eval_set.json').read_text(encoding='utf-8'))
    if name in ('hca', 'hca_safety'):
        CASES.extend(json.loads((EVALS/'rag_eval_hca_g2.json').read_text(encoding='utf-8')))

def annotation_file():
    return EVALS/({'hca': 'rubrica_anotacoes_hca.json', 'hca_safety': 'rubrica_anotacoes_hca_safety.json'}.get(EDITION, 'rubrica_anotacoes.json'))

def score_file():
    return EVALS/({'hca': 'resultado_sprint4_hca.json', 'hca_safety': 'resultado_sprint4_hca_safety.json'}.get(EDITION, 'resultado_sprint4.json'))

def path_for(profile,model=None):
    model_suffix=('__'+model.replace('/','_').replace(':','_')) if model else ''
    edition_prefix = {'hca': 'hca_', 'hca_safety': 'hca_safety_'}.get(EDITION, '')
    return EVALS/f'coleta_{edition_prefix}{profile}{model_suffix}.json'

def _guardrail_hash():
    arquivo = ROOT/'src'/'guardrails'/'moderation.py'
    return hashlib.sha256(arquivo.read_bytes()).hexdigest()


def _verificar_perfil_experimental(profile):
    if EDITION == 'hca_safety' and profile != 'iter2':
        raise ValueError('A edição hca_safety avalia somente a configuração iter2, sem alterar o índice.')


def _verificar_versao_guardrail(coleta):
    if EDITION == 'hca_safety' and coleta.get('guardrail_revision_sha256') != _guardrail_hash():
        raise RuntimeError('A política de segurança mudou após a coleta. Preserve o experimento; crie uma nova edição se mudar o código.')

def collect(profile,model=None):
    _verificar_perfil_experimental(profile)
    from src.rag.service import answer_question
    from src.rag.vector_store import corpus_fingerprint
    from src.rag.settings import get_profile
    fp=corpus_fingerprint(get_profile(profile))
    if EDITION in ('hca','hca_safety'):
        from src.rag.settings import CORPUS, STORE_DIR
        docs=CORPUS/'hca_g2_local'
        for required in ('GW_HCA-G2_Datasheet-PT.pdf','GW_HCA-G2_User-Manual-PT.pdf','Mapa MODBUS_HCA G2.pdf'):
            if not (docs/required).is_file():
                raise RuntimeError(f'Documento local HCA G2 ausente: {required}. Importe os três PDFs antes da coleta.')
        manifest=STORE_DIR/profile/'manifest.json'
        if not manifest.exists() or json.loads(manifest.read_text(encoding='utf-8')).get('fingerprint')!=fp:
            raise RuntimeError('Índice HCA ausente ou desatualizado. Execute python -m src.rag.vector_store --profile all --force.')
    destination=path_for(profile,model)
    if destination.exists():
        raise FileExistsError(f'Coleta {destination.name} já existe. Protegida contra sobrescrita: use a edição HCA para uma nova base, ou arquive e remova manualmente os arquivos antes de refazer.')
    outputs=[]
    for case in CASES:
        try:
            r=answer_question(case['pergunta'],session_id=f'eval-{profile}-{case["id"]}',
                              profile_name=profile,model_name=model,preserve_history=False)
            outputs.append({'id':case['id'],'pergunta':case['pergunta'],'tipo':case['tipo'],
                            'esperado':case['esperado'],'resposta':r['answer'],
                            'contextos_recuperados':r['contextos_recuperados'],
                            'fontes':r['fontes'],'status':r['status'],
                            'latencia_ms':r['latency_ms'],'modelo':r['model'],
                            'prompt':r['prompt_version']})
            print(case['id'],r['status'],r['latency_ms'],'ms')
        except Exception as exc:
            outputs.append({'id':case['id'],'erro':str(exc),'tipo':case['tipo']})
            print(case['id'],'ERRO',type(exc).__name__)
    dest=path_for(profile,model)
    dest.write_text(json.dumps({'profile':profile,'edition':EDITION,'corpus_fingerprint':fp,
                    'guardrail_revision_sha256':_guardrail_hash() if EDITION == 'hca_safety' else None,
                    'eval_set_cases':len(CASES),'timestamp':datetime.now(timezone.utc).isoformat(),
                    'results':outputs},ensure_ascii=False,indent=2),encoding='utf-8')
    print('Coleta salva:',dest)

def human_score(profile,model=None):
    _verificar_perfil_experimental(profile)
    dest=path_for(profile,model)
    if not dest.exists(): raise FileNotFoundError(f'Primeiro rode collect: {dest}')
    data=json.loads(dest.read_text(encoding='utf-8'))
    _verificar_versao_guardrail(data)
    if any('erro' in item for item in data['results']):
        raise RuntimeError('Há erros de execução na coleta. Não pontue erros de API/modelo como respostas; corrija-os e refaça uma coleta arquivada.')
    ann=annotation_file()
    saved=json.loads(ann.read_text(encoding='utf-8')) if ann.exists() else {}
    key=profile+('::'+model if model else '')
    entries=saved.setdefault(key,{})
    if EDITION in ('hca', 'hca_safety'):
        fingerprints=saved.setdefault('_corpus_fingerprints',{})
        old=fingerprints.get(key)
        if old and old!=data.get('corpus_fingerprint'):
            raise RuntimeError('Anotações HCA pertencem a corpus anterior. Arquive e remova rubrica_anotacoes_hca.json para iniciar outra avaliação.')
        fingerprints[key]=data.get('corpus_fingerprint')
    if EDITION == 'hca_safety':
        previous = saved.setdefault('_guardrail_hashes', {}).get(key)
        current = data['guardrail_revision_sha256']
        if previous and previous != current:
            raise RuntimeError('As notas pertencem a outra revisão do guardrail.')
        saved['_guardrail_hashes'][key] = current
    judge=input('Nome/identificação do avaliador humano: ').strip()
    if not judge: raise ValueError('Identifique o avaliador para auditoria.')
    print('Pontue faithfulness: proporção de afirmações sustentadas; relevancy: aderência à pergunta, incluindo recusa correta.')
    print('Escala manual 0 (falha), 0.5 (parcial), 1 (adequado). Mesmo eval set em ambas as iterações.')
    if EDITION in ('hca', 'hca_safety'):
        from src.rag.vector_store import corpus_fingerprint
        from src.rag.settings import get_profile
        if data.get('corpus_fingerprint') != corpus_fingerprint(get_profile(profile)):
            raise RuntimeError('Coleta HCA não corresponde ao corpus atual. Reindexe/refaça a coleta antes de avaliar.')
    for item in data['results']:
        print('\n'+'-'*55+'\n',item['id'],item.get('pergunta',''), '\nRESPOSTA:',item.get('resposta',item.get('erro')))
        print('EVIDÊNCIAS (resumo por fonte):')
        for evidence in item.get('contextos_recuperados', []):
            snippet=' '.join(evidence['text'].split())
            print(f'  {evidence["id"]} | {evidence["source"]} | {evidence["section"]}')
            print('    '+snippet[:260]+('...' if len(snippet)>260 else ''))
        if item['id'] in entries and input('Já avaliado. Pular? [S/n] ').lower().strip()!='n': continue
        def score(metric):
            while True:
                raw=input(metric+' [0 / 0.5 / 1]: ').strip()
                if raw in ('0','0.5','1'):return float(raw)
                print('Use apenas 0, 0.5 ou 1.')
        faith=score('faithfulness')
        relev=score('answer_relevancy')
        justification=input('Justificativa baseada na evidência: ').strip()
        if not justification:raise ValueError('Justificativa obrigatória')
        entries[item['id']]={'faithfulness':faith,'answer_relevancy':relev,
                             'justificativa':justification,'avaliador':judge,
                             'data_utc':datetime.now(timezone.utc).isoformat()}
        ann.write_text(json.dumps(saved,ensure_ascii=False,indent=2),encoding='utf-8')
    print('Anotações em',ann)

def report():
    if EDITION == 'hca_safety':
        return _report_safety()
    annpath=annotation_file()
    saved=json.loads(annpath.read_text(encoding='utf-8')) if annpath.exists() else {}
    metrics={}
    corpus_matches={}
    for profile in ('iter1','iter2'):
        rows=saved.get(profile,{})
        if EDITION == 'hca':
            from src.rag.vector_store import corpus_fingerprint
            from src.rag.settings import get_profile
            path = path_for(profile)
            collected=json.loads(path.read_text(encoding='utf-8')) if path.exists() else {}
            corpus_matches[profile] = bool(collected.get('corpus_fingerprint')) and collected.get('corpus_fingerprint') == corpus_fingerprint(get_profile(profile))
        else:
            # Coletas anteriores ao registro dos fingerprints permanecem históricas.
            corpus_matches[profile] = None
        # Só publicar score se TODOS os casos foram avaliados.
        collected=json.loads(path_for(profile).read_text(encoding='utf-8')) if path_for(profile).exists() else {}
        no_errors=bool(collected.get('results')) and not any('erro' in row for row in collected['results'])
        annotations_match = EDITION != 'hca' or saved.get('_corpus_fingerprints',{}).get(profile)==collected.get('corpus_fingerprint')
        all_done=all(c['id'] in rows for c in CASES) and (EDITION != 'hca' or (corpus_matches[profile] and no_errors and annotations_match))
        metrics[profile]={'count':len(rows),'expected':len(CASES),'complete':all_done,
                          'faithfulness':round(statistics.mean(rows[c['id']]['faithfulness'] for c in CASES),4) if all_done else None,
                          'answer_relevancy':round(statistics.mean(rows[c['id']]['answer_relevancy'] for c in CASES),4) if all_done else None}
    a,b=metrics['iter1'],metrics['iter2']
    improvement=(a['complete'] and b['complete'] and (EDITION != 'hca' or all(corpus_matches.values())) and
             b['faithfulness']>a['faithfulness'] and b['answer_relevancy']>a['answer_relevancy'])
    summary={'metodo':'rubrica manual documentada; NÃO é score oficial RAGAS',
             'timestamp_utc':datetime.now(timezone.utc).isoformat(),
             'edition':EDITION,'corpus_matches':corpus_matches,
             'profiles':metrics,'gain_both_metrics':bool(improvement),
             'observation':'Ganho requer avaliação humana integral no mesmo conjunto; não é pressuposto.'}
    score_file().write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
    fmt=lambda v:'PENDENTE' if v is None else f'{v:.3f}'
    md=f"""# Relatório do RAG - Sprint 04 ({EDITION})

## Método

Avaliação manual equivalente (fallback permitido pelo enunciado): para cada questão, um avaliador humano identifica as afirmações e verifica se são sustentadas **exclusivamente pelos trechos recuperados** (faithfulness, 0/0,5/1); verifica se a resposta atende à pergunta ou recusa corretamente dados ausentes (answer_relevancy, 0/0,5/1). Valores são médias simples dos {len(CASES)} casos fixos. A escala discretizada é uma aproximação de rubrica, **não se confunde com os algoritmos do RAGAS**. Justificativas e identidade são salvas em `evals/{annotation_file().name}`.

## Avaliação por iteração

| Perfil | Tamanho / overlap | Prompt | faithfulness | answer_relevancy | Avaliados |
|---|---|---|---|---|---|
| iter1 | 400 / 40 | v1 | {fmt(a['faithfulness'])} | {fmt(a['answer_relevancy'])} | {a['count']}/{a['expected']} |
| iter2 | 750 / 100 | v2 | {fmt(b['faithfulness'])} | {fmt(b['answer_relevancy'])} | {b['count']}/{b['expected']} |

Ganho nas duas métricas: {'**comprovado**' if improvement else '**não comprovado / pendente**'}. Não inserir números fictícios; caso falhe, ajustar um aspecto e repetir a coleta com o mesmo conjunto.

## Contexto e fontes

Fonte por seção e página (PDF) retornada no payload e visível em Gradio. O campo `distancia` é distância cosseno (menor é mais próximo); limiar configurável, sujeito a calibração. Base com dados simulados, referência técnica HCA G2 e, quando importados localmente, PDFs de fabricante. Estes não vinculam modelo à estação simulada, nem fornecem tarifa de condomínio.

## Segurança

Documentos são carregados em espaço de dados, não como instruções; blocos com padrões explícitos de injection são colocados em quarentena; referências inexistentes levam à recusa. Essas medidas **reduzem** o risco, não oferecem garantia absoluta contra injection ou alucinação. Evals R12-R14 testam segurança e fora de escopo.
"""
    (ROOT/'docs'/('relatorio_rag_hca.md' if EDITION == 'hca' else 'relatorio_rag.md')).write_text(md,encoding='utf-8')
    print(json.dumps(summary,ensure_ascii=False,indent=2))


def _report_safety():
    """Compara iterações originais HCA e nova política sem tocar nos resultados anteriores."""
    from src.rag.settings import get_profile
    from src.rag.vector_store import corpus_fingerprint

    old_annotations = EVALS/'rubrica_anotacoes_hca.json'
    new_annotations = annotation_file()
    old = json.loads(old_annotations.read_text(encoding='utf-8')) if old_annotations.exists() else {}
    new = json.loads(new_annotations.read_text(encoding='utf-8')) if new_annotations.exists() else {}

    expected_ids = {c['id'] for c in CASES}
    results = {}
    checks = {}
    for label, profile, collection_file, annotations, key in (
        ('iter1', 'iter1', EVALS/'coleta_hca_iter1.json', old, 'iter1'),
        ('iter2', 'iter2', EVALS/'coleta_hca_iter2.json', old, 'iter2'),
        ('iter2_seguranca_v2', 'iter2', path_for('iter2'), new, 'iter2'),
    ):
        collection = json.loads(collection_file.read_text(encoding='utf-8')) if collection_file.exists() else {}
        rows = annotations.get(key, {})
        fp = collection.get('corpus_fingerprint')
        fp_ok = bool(fp) and fp == corpus_fingerprint(get_profile(profile))
        ids = {x.get('id') for x in collection.get('results', [])}
        samples_ok = (ids == expected_ids and len(collection.get('results', [])) == len(CASES)
                      and not any('erro' in r for r in collection.get('results', [])))
        provenance_ok = annotations.get('_corpus_fingerprints',{}).get(key) == fp
        guardrail_ok = True
        if label == 'iter2_seguranca_v2':
            guardrail_ok = (collection.get('guardrail_revision_sha256') == _guardrail_hash()
                            and annotations.get('_guardrail_hashes',{}).get(key) == _guardrail_hash())
        complete = bool(fp_ok and samples_ok and provenance_ok and guardrail_ok
                        and expected_ids.issubset(rows))
        results[label] = {
            'count':len(expected_ids & rows.keys()),
            'expected':len(CASES),
            'complete':complete,
            'faithfulness':round(statistics.mean(rows[c['id']]['faithfulness'] for c in CASES),4) if complete else None,
            'answer_relevancy':round(statistics.mean(rows[c['id']]['answer_relevancy'] for c in CASES),4) if complete else None,
        }
        checks[label] = {'corpus_valido':fp_ok,'mesmas_perguntas':samples_ok,
                         'anotacoes_do_corpus':provenance_ok,'guardrail_valido':guardrail_ok}

    a = results['iter1']
    b = results['iter2']
    c = results['iter2_seguranca_v2']
    improvement = bool(a['complete'] and c['complete'] and
                       c['faithfulness'] > a['faithfulness'] and
                       c['answer_relevancy'] > a['answer_relevancy'])
    summary = {
        'metodo':'rubrica manual documentada; NÃO é score oficial RAGAS',
        'edition':EDITION,
        'timestamp_utc':datetime.now(timezone.utc).isoformat(),
        'mesmo_corpus_e_perguntas':checks,
        'profiles':results,
        'gain_both_metrics_vs_iter1':improvement,
        'observacao':('A versão de segurança usa o índice iter2 existente; só muda o guardrail. '
                      'Scores históricos não foram alterados. Ganho depende de notas reais, não da expectativa.'),
    }
    score_file().write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
    fmt = lambda v: 'PENDENTE' if v is None else f'{v:.4f}'
    md = (
        '# Experimento de segurança — corpus HCA G2\n\n'
        'Mudança controlada: detecção geral de intervenção elétrica em estação energizada; '
        'mesmo índice, documentos e 22 questões. Não substitui os experimentos já concluídos.\n\n'
        '| Versão | Faithfulness | Answer relevancy | Completa |\n'
        '|---|---:|---:|---|\n'
        + ''.join(f'| {label} | {fmt(r["faithfulness"])} | {fmt(r["answer_relevancy"])} | {r["complete"]} |\n'
                  for label,r in results.items())
        + f'\nMelhoria estrita nas duas métricas frente à Iteração 1: **{improvement}**.\n'
        + '\nValores RAGAS: não calculados; avaliação humana documentada.\n'
    )
    (ROOT/'docs'/'relatorio_rag_hca_seguranca_v2.md').write_text(md, encoding='utf-8')
    print(json.dumps(summary,ensure_ascii=False,indent=2))
    return summary

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('command',choices=['collect','judge','report'])
    parser.add_argument('--profile',choices=['iter1','iter2'],default='iter1')
    parser.add_argument('--model',default=None)
    parser.add_argument('--edition',choices=['original','hca','hca_safety'],default='original',help='hca_safety: mesmo corpus e índice iter2, novo guardrail elétrico; arquivos separados')
    args=parser.parse_args()
    set_edition(args.edition)
    if args.command=='collect':collect(args.profile,args.model)
    elif args.command=='judge':human_score(args.profile,args.model)
    else:report()
