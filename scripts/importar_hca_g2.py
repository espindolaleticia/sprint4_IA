"""Importa documentos HCA G2 fornecidos pelo grupo, APENAS para a base LOCAL.

Uso Windows (PowerShell):
 python scripts/importar_hca_g2.py --origem "C:/Users/usuario/Downloads"
 python -m src.rag.vector_store --profile all --force

NÃO publica/reexporta PDFs protegidos. A documentação do fabricante permanece
propriedade de seus titulares. Dados das estações GW-XX são simulados.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / 'data' / 'knowledge_base' / 'hca_g2_local'
DOCUMENTS = {
    'datasheet': ('GW_HCA-G2_Datasheet-PT.pdf', 'Ficha de dados técnicos, linha HCA G2'),
    'manual': ('GW_HCA-G2_User-Manual-PT.pdf', 'Manual de usuário, linha HCA G2 (V1.5 2025-11-11)'),
    'modbus': ('Mapa MODBUS_HCA G2.pdf', 'Mapa MODBUS HCA G2 fornecido pelo grupo; origem oficial não verificada'),
}
GOODWE_SOURCE = 'https://br.goodwe.com/download-hca-g2-series'


def _validate_pdf(file: Path, kind: str) -> int:
    import fitz
    if not file.is_file():
        raise FileNotFoundError(f'PDF não encontrado: {file}')
    with file.open('rb') as stream:
        signature=stream.read(5)
    if file.suffix.lower() != '.pdf' or signature != b'%PDF-':
        raise ValueError(f'Arquivo não parece PDF: {file}')
    with fitz.open(file) as pdf:
        if pdf.is_encrypted or len(pdf) == 0:
            raise ValueError(f'PDF vazio ou protegido: {file}')
        pages = len(pdf)
        # Apenas checagem simples de plausibilidade; nunca certificação de autenticidade.
        sample = ' '.join(pdf[i].get_text() for i in range(min(pages, 3))).lower()
        expected = ('hca',) if kind in {'datasheet','manual'} else ('modbus',)
        if not any(x in sample for x in expected):
            raise ValueError(f'O conteúdo de {file.name} não parece corresponder a {kind}.')
        return pages


def import_documents(files: dict[str, Path], destination: Path = DEST) -> dict:
    """Valida TODOS antes de copiar, para não criar uma base parcialmente importada."""
    validated = {kind: _validate_pdf(source, kind) for kind, source in files.items()}
    destination.mkdir(parents=True, exist_ok=True)
    records = []
    for kind, source in files.items():
        target = destination / DOCUMENTS[kind][0]
        if source.resolve() != target.resolve():
            shutil.copy2(source, target)
        sha = hashlib.sha256(target.read_bytes()).hexdigest()
        records.append({
            'tipo':kind, 'arquivo':target.name, 'paginas':validated[kind],
            'sha256':sha, 'descricao':DOCUMENTS[kind][1],
            'proveniencia':GOODWE_SOURCE if kind != 'modbus' else 'Documento fornecido pelo grupo; verificar origem e compatibilidade',
            'publicar_pdf_no_github':False,
        })
    manifest = {
        'linha_referencia':'GoodWe HCA G2, 7/11/22 kW',
        'estacoes_gw_xx':'IDs operacionais SIMULADOS; nenhuma associação com um modelo específico',
        'criado_utc':datetime.now(timezone.utc).isoformat(),
        'documentos':records,
        'observacao':'Uso acadêmico local; original de terceiro não deve ser redistribuído no GitHub sem autorização.',
    }
    (destination / 'procedencia_local.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
    return manifest


def main():
    p=argparse.ArgumentParser(description='Importar três PDFs da HCA G2 para o RAG local. NÃO publica cópias no GitHub.')
    p.add_argument('--origem', type=Path, default=Path.home()/'Downloads', help='Pasta com os três PDFs')
    for kind in DOCUMENTS:
        p.add_argument('--'+kind, type=Path, help=f'Caminho alternativo para o PDF {kind}')
    args=p.parse_args()
    files = {kind: (getattr(args,kind) or (args.origem/filename)).expanduser()
             for kind,(filename,_) in DOCUMENTS.items()}
    result=import_documents(files)
    for record in result['documentos']:
        print(f"{record['tipo']}: OK | {record['paginas']} páginas | {record['arquivo']}")
    print('Documentos salvos SOMENTE na pasta local ignorada pelo GitHub:', DEST)
    print('PRÓXIMO: python -m src.rag.vector_store --profile all --force')
    print('ATENÇÃO: após atualizar a base, os scores históricos NÃO medem esta nova versão. Refaça as duas avaliações.')

if __name__=='__main__': main()
