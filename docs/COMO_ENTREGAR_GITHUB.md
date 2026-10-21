# Publicação GitHub — Sprint 04

O conteúdo completo da entrega e os pontos ainda pendentes estão em [`GUIA_ENTREGA_FINAL.md`](GUIA_ENTREGA_FINAL.md). A versão pública preserva código, testes, dados operacionais fictícios, manuais referenciados por endereço oficial, relatórios agregados e PDF de 5 páginas.

## Publicação segura (VS Code / PowerShell)

```powershell
python -m pytest -q
python scripts/validar_entrega.py
git init
git add .
git status --short
git commit -m "Sprint 04 - RAG HCA G2 avaliado e seguranca v2"
git branch -M main
git remote add origin URL_DO_REPOSITORIO
git push -u origin main
```

Revise `git status --short`. **Não publique** `.env`, `data/chroma_db/`, PDFs HCA completos, `data/knowledge_base/hca_g2_local/`, coletas HCA com trechos de documentos ou rubricas identificadas. Se alguns desses arquivos já tiverem sido rastreados anteriormente, `.gitignore` não os remove do Git automaticamente; execute `git rm --cached <caminho>` após conferir o arquivo, sem apagá-lo do computador.

O PDF é `docs/GoodWe Grid Assistant.pdf`, com resultados finais publicáveis e avisos dos requisitos não resolvidos. A documentação antiga da Sprint 3 está preservada em `docs/README_SPRINT3_HISTORICO.md`.
