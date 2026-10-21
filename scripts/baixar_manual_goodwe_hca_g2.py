"""Baixar manual oficial GoodWe HCA G2 (opcional, diferente de ChargeGrid).

Fonte de download publicada no domínio oficial br.goodwe.com, verificada na página oficial GoodWe em 2026-10.
Verifique se este modelo é realmente relevante ao projeto antes de indexá-lo.
"""
from pathlib import Path
from urllib.request import Request, urlopen
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1]
FOLDER = ROOT / 'data' / 'knowledge_base'
URL = 'https://en.goodwe.com/Ftp/EN/Downloads/User%20Manual/GW_HCA-G2_User%20Manual-EN.pdf'
DEST = FOLDER / 'GoodWe_HCA_G2_User_Manual_EN.pdf'

def main():
    FOLDER.mkdir(parents=True,exist_ok=True)
    if DEST.exists():
        raise SystemExit(f'O arquivo já existe: {DEST}. Remova-o manualmente para baixar novamente.')
    request=Request(URL,headers={'User-Agent':'Mozilla/5.0 (academic-document-download)'})
    with urlopen(request,timeout=40) as response:
        mime=response.headers.get_content_type()
        data=response.read(35_000_001)
    if len(data)>35_000_000 or len(data)<1_000 or not data.startswith(b'%PDF'):
        raise RuntimeError(f'Conteúdo não é um PDF esperado (MIME={mime}). Nenhum arquivo foi salvo.')
    DEST.write_bytes(data)
    details={
        'arquivo':DEST.name,
        'url_oficial':URL,
        'produto':'GoodWe HCA G2 - não presumir equivalência com ChargeGrid/EV ChargeOps',
        'sha256':hashlib.sha256(data).hexdigest(),
        'tamanho_bytes':len(data),
        'observacao':'Validar edição e aplicabilidade ao domínio antes da reindexação.'
    }
    (FOLDER/'download_hca_g2_procedencia.json').write_text(json.dumps(details,ensure_ascii=False,indent=2),encoding='utf-8')
    print('Baixado manual oficial em:',DEST)
    print('Agora execute: python -m src.rag.vector_store --profile all --force')

if __name__=='__main__': main()
