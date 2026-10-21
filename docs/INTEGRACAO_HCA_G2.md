# Como integrar os três PDFs HCA G2 no VS Code

## O que é o quê

- **Família técnica**: GoodWe HCA G2, modelos GW7K-HCA-20 (7 kW), GW11K-HCA-20 (11 kW), GW22K-HCA-20 (22 kW).
- **Estações simuladas**: GW-03, GW-04, GW-07, GW-09, GW-12. Não há associação com um modelo da família.
- **Manuais**: os PDFs do fabricante e o mapa Modbus fornecidos pelo grupo são usados localmente para resposta com fonte e página. Não há conexão ao equipamento físico ou ao Modbus.

## Instalação dos documentos (PowerShell, raiz `goodwe_IA_sprint3`)

Guarde os três PDFs originais na mesma pasta (por exemplo, `Downloads`) com estes nomes exatos:

- `GW_HCA-G2_Datasheet-PT.pdf`
- `GW_HCA-G2_User-Manual-PT.pdf`
- `Mapa MODBUS_HCA G2.pdf`

Execute (ajuste o caminho para a pasta dos arquivos):

```powershell
python scripts/importar_hca_g2.py --origem "$env:USERPROFILE\Downloads"
python scripts/verificar_ambiente.py
python -m src.rag.vector_store --profile all --force
python scripts/verificar_ambiente.py
python app/gradio_app.py
```

O script valida que os arquivos são PDFs, registra quantidade de páginas e SHA-256 e os copia para `data/knowledge_base/hca_g2_local/` (ignorados pelo `.gitignore`). O `PyMuPDFLoader` carrega cada página e preserva o número da página no metadado. Ao enviar ao Gradio perguntas de fabricante, o modelo deve citar os trechos recuperados. **Atenção:** páginas do PDF na interface são contadas desde 1; a numeração impressa do manual pode ser diferente.

Se os PDFs estiverem em lugares diferentes, passe os caminhos individualmente:

```powershell
python scripts/importar_hca_g2.py --manual "C:\caminho\GW_HCA-G2_User-Manual-PT.pdf" --datasheet "C:\caminho\GW_HCA-G2_Datasheet-PT.pdf" --modbus "C:\caminho\Mapa MODBUS_HCA G2.pdf"
```

## Teste rápido de recuperação

Pergunte no Gradio:

1. `Quais modelos HCA G2 existem e quais suas potências nominais?` (7, 11, 22 kW com citação da ficha técnica).
2. `O HCA G2 tem partida por cartão RFID?` (sim, conforme o manual).
3. `Segundo o mapa Modbus, o que representa o registrador 10015?` (potência de carregamento no mapa; **não** valor atual).
4. `Qual é a potência nominal da GW-09?` (deve reconhecer ausência de associação à família).
5. `Posso abrir a GW-09 energizada?` (não; deve priorizar segurança).

Se houver um erro de citação ou recusa indevida, não atribua nota positiva: documente o problema.

## Avaliação atualizada (necessária para a nova base)

A avaliação histórica NÃO deve ser reaproveitada. Execute:

```powershell
python evals/avaliar_rag.py collect --edition hca --profile iter1
python evals/avaliar_rag.py collect --edition hca --profile iter2
python evals/avaliar_rag.py judge --edition hca --profile iter1
python evals/avaliar_rag.py judge --edition hca --profile iter2
python evals/avaliar_rag.py report --edition hca
python evals/comparar_modelos_rag.py --edition hca --profile iter2
python scripts/gerar_relatorio_pdf.py
```

Cada perfil tem **22 questões** (as 14 históricas + 8 novas HCA), na mesma ordem e com respostas esperadas. Os dados são salvos em arquivos diferentes (`coleta_hca_iter1.json`, `coleta_hca_iter2.json`, `rubrica_anotacoes_hca.json`, `resultado_sprint4_hca.json`). Os históricos originais continuam intactos.

Se mudar documentos novamente, preserve/arquive as coletas HCA anteriores antes de repetir. O script impede sobrescrever coletas sem aviso. Não declare ganho até ambos os resultados serem avaliados e comparados.

## Direitos autorais e GitHub

A página 2 do manual HCA G2 V1.5 restringe sua transmissão pública sem autorização. O ZIP GitHub **não inclui PDFs integrais**. O avaliador pode obtê-los no fabricante ou importar suas próprias cópias. Isso implica que a expansão com os PDFs só fica disponível após a importação local; o repositório público contém um resumo autoral básico, não os documentos integrais. O mapa Modbus não tem procedência pública confirmada.

O arquivo `procedencia_local.json` fica na pasta excluída do Git. A base simulada GW-XX segue completamente separada das especificações nominais.
