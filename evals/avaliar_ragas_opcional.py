"""RAGAS genuíno (opcional). Testar compatibilidade de versões no ambiente do grupo.

Necessita: pip install -r requirements-ragas.txt
Executar após `python evals/avaliar_rag.py collect --profile iter1` e iter2.
"""
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from src.chain.builder import criar_llm
from src.rag.embeddings import build_embeddings

def run(profile):
    from datasets import Dataset
    from ragas import evaluate
    from ragas.metrics import faithfulness, answer_relevancy
    from ragas.llms import LangchainLLMWrapper
    from ragas.embeddings import LangchainEmbeddingsWrapper
    path=ROOT/'evals'/f'coleta_{profile}.json'
    results=json.loads(path.read_text(encoding='utf-8'))['results']
    if any('erro' in x for x in results):
        raise ValueError('Coleta incompleta, resolva os erros antes de usar RAGAS.')
    ds=Dataset.from_dict({
        'question':[x['pergunta'] for x in results],
        'answer':[x['resposta'] for x in results],
        'contexts':[[c['text'] for c in x['contextos_recuperados']] for x in results],
    })
    judge=LangchainLLMWrapper(criar_llm(num_predict=1200))
    faithfulness.llm=judge
    answer_relevancy.llm=judge
    answer_relevancy.embeddings=LangchainEmbeddingsWrapper(build_embeddings())
    values=evaluate(ds,metrics=[faithfulness,answer_relevancy],raise_exceptions=False)
    df=values.to_pandas()
    output=ROOT/'evals'/f'ragas_{profile}.csv'
    df.to_csv(output,index=False)
    print('RAGAS real salvo:',output)
    print(df[['faithfulness','answer_relevancy']].mean().to_string())
if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--profile',choices=['iter1','iter2'],required=True)
    run(p.parse_args().profile)
