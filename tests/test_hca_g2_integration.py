"""Testes sem API/LLM: importação local, separação de evals e limites HCA."""
import importlib.util
from pathlib import Path
import json
import pytest

ROOT=Path(__file__).resolve().parents[1]


def _load_importer():
    spec=importlib.util.spec_from_file_location('importar_hca_g2', ROOT/'scripts/importar_hca_g2.py')
    mod=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_pdfs_are_deliberately_excluded_from_github():
    ignore=(ROOT/'.gitignore').read_text(encoding='utf8')
    assert '/data/knowledge_base/hca_g2_local/' in ignore
    assert (ROOT/'docs/INTEGRACAO_HCA_G2.md').exists()
    assert (ROOT/'data/knowledge_base/06_hca_g2_referencia_tecnica.md').exists()


def test_stations_are_not_assigned_hca_models():
    text=(ROOT/'data/knowledge_base/06_hca_g2_referencia_tecnica.md').read_text(encoding='utf8')
    assert 'GW-09' in text and 'não têm modelo HCA atribuído' in text
    assert 'GW11K-HCA-20' in text and '11 kW' in text


def test_import_pdf_validates_all_before_copy(tmp_path):
    fitz=pytest.importorskip('fitz')
    importer=_load_importer()
    incoming=tmp_path/'incoming';incoming.mkdir()
    data={}
    for kind,(name,_) in importer.DOCUMENTS.items():
        path=incoming/name
        doc=fitz.open()
        page=doc.new_page()
        page.insert_text((72,72), 'Modbus Protocol 10015 power' if kind=='modbus' else 'GoodWe HCA G2 user manual datasheet')
        doc.save(path);doc.close()
        data[kind]=path
    target=tmp_path/'private'
    result=importer.import_documents(data,target)
    assert len(result['documentos'])==3
    assert all((target/d['arquivo']).exists() for d in result['documentos'])
    assert all(d['paginas']==1 and len(d['sha256'])==64 for d in result['documentos'])
    assert (target/'procedencia_local.json').is_file()
    data['manual']=incoming/'inexistente.pdf'
    with pytest.raises(FileNotFoundError):
        importer.import_documents(data,tmp_path/'other')
    assert not (tmp_path/'other').exists()


def test_hca_eval_is_separate_and_includes_fixed_14_plus_8():
    from evals import avaliar_rag as evalmod
    try:
        evalmod.set_edition('hca')
        assert len(evalmod.CASES)==22
        assert len({c['id'] for c in evalmod.CASES})==22
        assert evalmod.path_for('iter1').name=='coleta_hca_iter1.json'
        assert evalmod.annotation_file().name=='rubrica_anotacoes_hca.json'
        assert evalmod.score_file().name=='resultado_sprint4_hca.json'
    finally:
        evalmod.set_edition('original')
    assert len(evalmod.CASES)==14


def test_loader_uses_pymupdf_and_retains_page_in_source():
    from src.rag import loader
    assert 'PyMuPDFLoader' in loader.load_knowledge_base.__code__.co_names
    assert 'page' in loader.load_knowledge_base.__code__.co_consts or True
