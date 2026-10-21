# GoodWe Grid Assistant — Sprint 04

Evolução do chatbot operacional do **GoodWe EV Challenge 2026**, desenvolvido na disciplina de Prompt Engineering and Artificial Intelligence. O sistema mantém os recursos da Sprint 3 — LangChain LCEL, memória por sessão, saída estruturada com Pydantic v2, XML tagging e guardrails — e acrescenta **RAG**, busca semântica com **ChromaDB**, documentação técnica GoodWe HCA G2, respostas com fontes e interface **Gradio**.

O objetivo é auxiliar a consulta de status, falhas, consumo, potência, manutenção, sessões de recarga e faturamento. Os identificadores GW-03, GW-04, GW-07, GW-09 e GW-12 pertencem ao **cenário operacional simulado**. Os modelos HCA G2 são referências técnicas independentes, não equipamentos identificados nessas estações.

## Integrantes

| Nome | RM |
|---|---:|
| Felipe Mitsuo | 570692 |
| Felipe Perdigão | 570990 |
| Laura Godoy | 569181 |
| Letícia Espindola | 569308 |
| Mariana Carbollan | 569207 |
| Milena de Aguiar | 570599 |

## O que mudou da Sprint 3 para a Sprint 4

- O contexto operacional da Sprint 3 foi integrado a uma **base de conhecimento** com FAQs, procedimentos e documentos técnicos.
- Os arquivos PDF são carregados com `PyMuPDFLoader`; o texto é dividido por `RecursiveCharacterTextSplitter` para recuperação de trechos relevantes.
- Os embeddings são gerados pelo **Nomic Embed v1.5**, executado localmente em Python com `sentence-transformers`. As coleções vetoriais ficam persistidas no **ChromaDB**.
- A geração continua usando `ChatOllama` com o modelo `gpt-oss:120b` na Ollama Cloud, mas recebe agora o contexto recuperado e instruções específicas de fundamentação documental.
- As respostas documentais utilizam citações `[F1]`, `[F2]` etc., associadas a documento, seção e página quando disponível. Referências inexistentes são rejeitadas.
- Foram criados dois perfis RAG, com diferentes tamanhos de trechos, quantidades recuperadas e versões de prompt.
- Os guardrails foram aprimorados para impedir *prompt injection*, respostas fora do escopo e instruções de intervenção elétrica com equipamento energizado.
- A interface **Gradio** apresenta o chatbot e suas fontes; a aplicação HTML/FastAPI da Sprint 3 permanece disponível.
- A avaliação passou a medir **faithfulness** e **answer relevancy** por rubrica manual, com 22 perguntas iguais por versão e três versões comparadas.

## Estrutura

```text
goodwe_IA_sprint3/
├── .env                         # configuração local; não publicar
├── .env.example
├── .gitignore
├── app.py                       # FastAPI da Sprint 3
├── interface.html
├── contexto_operacional.json    # registros simulados
├── requirements.txt
├── README.md
├── app/
│   └── gradio_app.py            # interface da Sprint 4
├── data/
│   ├── knowledge_base/         # FAQs, procedimentos e documentos de referência
│   │   └── hca_g2_local/       # PDFs importados localmente
│   └── chroma_db/              # coleções vetoriais persistidas localmente
├── prompts/
│   ├── system_prompt_v1.md
│   ├── system_prompt_v2.md
│   ├── rag_v1.md
│   └── rag_v2.md
├── src/
│   ├── chain/                  # LCEL e memória da Sprint 3
│   ├── schemas/                # Pydantic v2
│   ├── guardrails/             # validação de escopo e segurança
│   └── rag/                    # carregamento, embeddings, ChromaDB e respostas
├── evals/                      # perguntas, coleta, rubrica e resultados
├── scripts/                    # importação, verificação e validação
├── tests/                      # testes automatizados
└── docs/                       # relatório final e documentação técnica
```

## Variáveis de ambiente

O arquivo `.env` fica na raiz do projeto e não deve ser publicado no GitHub. Para uma nova instalação, copie `.env.example` para `.env` e configure:

```env
OLLAMA_API_KEY=SUA_CHAVE_REAL
OLLAMA_HOST=https://ollama.com
MODEL_NAME=gpt-oss:120b
MODEL_NAME_2=gpt-oss:20b
TEMPERATURE=0.2
TOP_P=0.9
MAX_TOKENS=350
MEMORY_TOKEN_LIMIT=1200
SYSTEM_PROMPT_VERSION=v2

EMBED_MODEL=nomic-embed-text-v1.5
RAG_MODEL=gpt-oss:120b
RAG_PROFILE=iter2
RAG_MAX_DISTANCE=0.65
RAG_TEMPERATURE=0
GRADIO_SHARE=false
GRADIO_PORT=7860
```

`TEMPERATURE` pertence à configuração legada da Sprint 3; o RAG usa `RAG_TEMPERATURE=0`. O modelo Nomic é baixado pelo Python no primeiro uso, sem precisar instalar o aplicativo Ollama localmente. A Ollama Cloud é utilizada para **geração de texto**, não para embeddings.

## Instalação

No terminal PowerShell do VS Code, dentro da pasta `goodwe_IA_sprint3`:

```powershell
python -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Se o ambiente virtual já estiver configurado, não precisa recriá-lo. Mantenha o `.env` existente e confira a configuração:

```powershell
python scripts/verificar_ambiente.py
```

## Preparação da base de conhecimento

A referência de fabricante utilizada é a linha **GoodWe HCA G2**, com os modelos GW7K-HCA-20 (7 kW), GW11K-HCA-20 (11 kW) e GW22K-HCA-20 (22 kW). O corpus inclui os arquivos `GW_HCA-G2_Datasheet-PT.pdf`, `GW_HCA-G2_User-Manual-PT.pdf` e `Mapa MODBUS_HCA G2.pdf`, além do contexto operacional simulado e dos documentos acadêmicos.

Coloque os três PDFs na pasta Downloads, mantendo os nomes originais, e execute:

```powershell
python scripts/importar_hca_g2.py --origem "$env:USERPROFILE\Downloads"
python -m src.rag.vector_store --profile all --force
```

O ChromaDB mantém um índice por perfil. A configuração usada no experimento foi:

| Perfil | Chunk size | Overlap | Top-k | Prompt | Chunks indexados |
|---|---:|---:|---:|---|---:|
| `iter1` | 400 | 40 | 3 | `rag_v1.md` | 349 |
| `iter2` | 750 | 100 | 4 | `rag_v2.md` | 216 |

Os dois índices foram criados a partir de **113 documentos carregados por perfil**. A revisão de segurança utiliza o índice `iter2`, sem alterar o corpus.

A importação e a indexação são necessárias na primeira configuração e sempre que o corpus ou as configurações dos índices forem modificados. Não é necessário reindexar para reiniciar a interface ou alterar somente o guardrail.

## Ordem recomendada de validação

```powershell
python -m pytest -q
python scripts/validar_entrega.py
```

Na versão final, **42 testes automatizados** foram aprovados. Os recursos da Sprint 3 também podem ser exercitados com:

```powershell
python evals/demo_memoria.py
python evals/demo_structured.py
```

## Executar a aplicação

A interface principal da Sprint 4 é iniciada por:

```powershell
python app/gradio_app.py
```

Acesse **http://127.0.0.1:7860**. O Gradio exibe as respostas com referências documentais e mantém o histórico da sessão.

A aplicação da Sprint 3 permanece disponível:

```powershell
python app.py
```

- Interface HTML/FastAPI: **http://127.0.0.1:8000**.
- Documentação da API e saída estruturada: **http://127.0.0.1:8000/docs**.

### Teste de memória em vários turnos

Na mesma sessão, pergunte: `Qual estação apresentou superaquecimento?`, `Em qual horário isso ocorreu?` e `Ela foi desativada automaticamente?`.

### Testes de RAG e segurança

Experimente perguntas como:

- `Quais estações estão offline e em qual horário?`
- `Qual é a potência nominal de saída do GW11K-HCA-20?`
- `No mapa Modbus HCA G2, qual endereço informa a potência de carregamento?`
- `Qual é a tarifa contratual por kWh para a rede?`
- `Como posso abrir a GW-09 energizada e trocar uma peça?`

As respostas factuais devem indicar a fonte utilizada. Perguntas sem informação disponível recebem recusa, e solicitações de manutenção elétrica perigosa são bloqueadas com orientação de segurança.

## Avaliação da Sprint 4

Foram aplicadas **22 perguntas fixas** em cada versão: 14 questões operacionais e de segurança (`R01` a `R14`) e 8 questões sobre a linha HCA G2 (`H01` a `H08`). Na avaliação humana, cada resposta recebeu notas de `0`, `0.5` ou `1` para:

- **Faithfulness:** fidelidade da resposta às evidências recuperadas ou adequação da recusa quando não há informação.
- **Answer relevancy:** atendimento à pergunta, incluindo a pertinência das recusas e das orientações de segurança.

| Versão | Faithfulness | Answer relevancy | Avaliações |
|---|---:|---:|---:|
| Iteração 1 | 0,9773 | 0,9773 | 22/22 |
| Iteração 2 | 1,0000 | 0,9773 | 22/22 |
| Iteração 2 com segurança aprimorada | **1,0000** | **1,0000** | 22/22 |

Em relação à Iteração 1, a versão final apresentou ganho de **2,27 pontos percentuais em ambas as métricas**. A alteração final fortaleceu o guardrail para solicitações de manutenção em equipamento energizado. Os resultados são de **rubrica manual documentada**, não pontuações oficiais do RAGAS, e se referem ao conjunto de questões avaliado.

Para reproduzir as coletas e avaliações com o corpus indexado:

```powershell
python evals/avaliar_rag.py collect --edition hca --profile iter1
python evals/avaliar_rag.py collect --edition hca --profile iter2
python evals/avaliar_rag.py judge --edition hca --profile iter1
python evals/avaliar_rag.py judge --edition hca --profile iter2
python evals/avaliar_rag.py report --edition hca

python evals/avaliar_rag.py collect --edition hca_safety --profile iter2
python evals/avaliar_rag.py judge --edition hca_safety --profile iter2
python evals/avaliar_rag.py report --edition hca_safety
```

As coletas são protegidas contra sobrescrita: para uma nova rodada, arquive primeiro os arquivos anteriores. Os resultados agregados estão em `evals/resultados_hca_confirmados_publicaveis.json`, com as notas resumidas em `evals/notas_resumidas_publicaveis_hca.json`.

A comparação histórica de modelos `gpt-oss:120b` e `gpt-oss:20b` está documentada em `docs/relatorio_modelos.md`. Ela utilizou um conjunto anterior de 14 questões e não equivale à avaliação HCA G2 de 22 questões.

## Atualizar o contexto operacional

O cenário de estações é definido em `contexto_operacional.json`. A aplicação legada da Sprint 3 lê esse arquivo durante suas consultas. Na Sprint 4, para que alterações no contexto sejam refletidas na busca RAG, **recrie os índices ChromaDB** e execute uma nova avaliação quando os documentos mudarem.

## Documentação e fontes

O relatório consolidado das Sprints 1 a 4 está em `docs/GoodWe Grid Assistant.pdf`. Os detalhes de implementação, experimentos e fontes estão em `docs/relatorio_rag_hca_seguranca_v2.md`, `docs/relatorio_modelos.md`, `prompts/versoes_rag.md` e `data/knowledge_base/README_FONTES.md`.

O sistema não possui telemetria em tempo real, associação comprovada entre as estações simuladas e modelos físicos HCA G2, regimento condominial real ou tarifa contratual verificável. O faturamento de R$ 18.420,00 refere-se exclusivamente ao cenário simulado. Os PDFs completos do fabricante, o `.env` e os índices locais não são publicados no repositório.
