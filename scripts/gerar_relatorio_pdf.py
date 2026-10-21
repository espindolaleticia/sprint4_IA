"""Gera o relatório final da Sprint 04 (5 páginas, sem acessar Ollama ou PDFs protegidos).

Resultados HCA são reproduzidos do relatório enviado pelo grupo ao chat em 21/10/2026.
Exige apenas ReportLab e fonte local; NÃO recalcula scores sem as rubricas brutas locais.
"""
from pathlib import Path
import json
from xml.sax.saxutils import escape
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import mm

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'docs' / 'GoodWe Grid Assistant.pdf'
REC = json.loads((ROOT / 'evals' / 'resultados_hca_confirmados_publicaveis.json').read_text(encoding='utf-8'))
assert REC['gain_both_metrics_vs_iter1']
assert len(json.loads((ROOT/'evals/notas_resumidas_publicaveis_hca.json').read_text(encoding='utf8'))['casos']) == 66

paths = [
    ('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf','/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'),
    ('C:/Windows/Fonts/arial.ttf','C:/Windows/Fonts/arialbd.ttf'),
    ('/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf','/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf'),
]
font, font_b = next(((a,b) for a,b in paths if Path(a).exists() and Path(b).exists()), (None,None))
if not font:
    from reportlab import rl_config
    font=str(Path(rl_config.TTFSearchPath[0])/'Vera.ttf');font_b=str(Path(rl_config.TTFSearchPath[0])/'VeraBd.ttf')
pdfmetrics.registerFont(TTFont('GWF',font))
pdfmetrics.registerFont(TTFont('GWF-Bold',font_b))
pdfmetrics.registerFontFamily('GWF',normal='GWF',bold='GWF-Bold',italic='GWF',boldItalic='GWF-Bold')
NAVY=colors.HexColor('#142b43')
SKY=colors.HexColor('#176b8c')
INK=colors.HexColor('#263544')
MUTED=colors.HexColor('#526171')
LIGHT=colors.HexColor('#f1f5f8')
RULE=colors.HexColor('#d7e0e6')
styles={
    'hero': ParagraphStyle('hero',fontName='GWF-Bold',fontSize=21,leading=25,textColor=NAVY,spaceAfter=8),
    'sec':ParagraphStyle('sec',fontName='GWF-Bold',fontSize=13.4,leading=17,textColor=NAVY,spaceBefore=12,spaceAfter=7),
    'sub':ParagraphStyle('sub',fontName='GWF-Bold',fontSize=10,leading=14,textColor=SKY,spaceBefore=9,spaceAfter=5),
    'body':ParagraphStyle('body',fontName='GWF',fontSize=9.5,leading=14,textColor=INK,spaceAfter=6),
    'small':ParagraphStyle('small',fontName='GWF',fontSize=8.35,leading=12.0,textColor=INK,spaceAfter=5),
    'tiny':ParagraphStyle('tiny',fontName='GWF',fontSize=8.05,leading=11.5,textColor=INK,spaceAfter=4),
    'caption':ParagraphStyle('caption',fontName='GWF',fontSize=8.0,leading=11.5,textColor=MUTED,spaceAfter=4),
    'th':ParagraphStyle('th',fontName='GWF-Bold',fontSize=8.0,leading=11.4,textColor=colors.white),
    'cell':ParagraphStyle('cell',fontName='GWF',fontSize=8.05,leading=11.5,textColor=INK),
    'boldcell':ParagraphStyle('boldcell',fontName='GWF-Bold',fontSize=8.05,leading=11.5,textColor=INK),
}

def para(txt,style='body'):
    return Paragraph(txt,styles[style])

def tbl(headers, rows, widths, small=True):
    cols=[]
    for row in [headers]+rows:
        cols.append([para(str(v),'th' if row is headers else ('cell' if small else 'small')) for v in row])
    t=Table(cols,colWidths=widths,repeatRows=1,hAlign='LEFT')
    t.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,0),NAVY),('VALIGN',(0,0),(-1,-1),'TOP'),
        ('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,LIGHT]),
        ('LINEBELOW',(0,0),(-1,0),.8,NAVY),('LINEBELOW',(0,1),(-1,-1),.4,RULE),
        ('LEFTPADDING',(0,0),(-1,-1),7),('RIGHTPADDING',(0,0),(-1,-1),7),
        ('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6),
    ]))
    return t

STORY=[]
append=STORY.append
w=A4[0]-76

# PAGE 1 — historical evolution
append(para('FIAP | 2º semestre de 2026 | Prompt Engineering and Artificial Intelligence','caption'))
append(para('GoodWe Grid Assistant','hero'))
append(para('<b>Relatório consolidado: Sprints 1–4 | versão final HCA G2 | 21/10/2026</b>','body'))
append(para('Chatbot acadêmico para gestão de eletropostos. As estações GW-03, GW-04, GW-07, GW-09 e GW-12 são <b>simuladas</b>; a linha HCA G2 é referência técnica de fabricante, não identificação real dos postos.','body'))
append(para('1. Evolução do produto nas quatro Sprints','sec'))
append(tbl(['Sprint','Evolução e problemas enfrentados'],[
    ('1 — Escopo','Personas gestor/operador, técnico e administrador; objetivos de status, falhas, consumo, potência, sessões, faturamento e manutenção. Requisitos e protótipos; feedback destacou justificativa de tecnologias, cenário e formatos de saída.'),
    ('2 — Protótipo','Aplicação Python/FastAPI, HTML, Ollama Cloud e gpt-oss:120b. Contexto simulado e histórico operacional. Em 8 questões legadas: <b>68,75%</b> de qualidade e <b>2.457,38 ms</b> de latência média.'),
    ('3 — Refatoração','LCEL, histórico separado por sessão, Pydantic v2, XML tagging, guardrails e contexto JSON externo. Em 8 casos comparáveis: <b>100%</b> de qualidade e <b>876,98 ms</b>; métricas antigas, não RAGAS.'),
    ('4 — RAG','PyMuPDFLoader, chunking, embeddings Nomic locais, ChromaDB, recuperação top-k, citações válidas, Gradio, 22 perguntas por versão e proteção adicional contra intervenção elétrica perigosa.')
], [92,w-92]))
append(para('Objetivo e escopo operacional','sub'))
append(para('Reduzir buscas manuais em documentos e registros simulados; fornecer respostas ancoradas em fontes identificadas. Consultas fora do domínio, dados em tempo real, preços contratuais ou especificações atribuídas a uma estação sem inventário devem ser recusadas.','body'))
append(para('Artefatos essenciais','sub'))
append(para('Repositório GitHub: código Python, prompts versionados, testes, guia de execução, relatórios de resultados publicáveis, referências das fontes e este PDF. Os PDFs completos da GoodWe, os índices locais e a chave `.env` não são distribuídos publicamente.','body'))

append(PageBreak())
# PAGE 2 — pipeline
append(para('2. RAG: pipeline, base e parâmetros','sec'))
append(para('<b>Fluxo:</b> PDF / Markdown / JSON → PyMuPDFLoader → RecursiveCharacterTextSplitter → Nomic Embed v1.5 local → ChromaDB persistente → recuperação top-k → prompt RAG/ChatOllama → verificação de citações → interface Gradio.','body'))
append(tbl(['Componente','Estratégia / implementação'],[
    ('Fontes','Operação simulada; FAQ e procedimentos acadêmicos; datasheet GoodWe HCA G2 (2 páginas), manual PT (70 páginas) e mapa Modbus (9 páginas) importados somente no computador do grupo.'),
    ('Embeddings','`nomic-ai/nomic-embed-text-v1.5` via SentenceTransformers em Python. A Ollama Cloud gera texto com `gpt-oss:120b` e não oferece embeddings nesta configuração. Divergência de provedor requer validação do docente.'),
    ('Indexação','Duas coleções ChromaDB persistentes; 113 documentos carregados por perfil. Iteração 1: <b>349 chunks</b> (400/40, k=3); Iteração 2: <b>216 chunks</b> (750/100, k=4). Manifestos/fingerprints verificam corpus.'),
    ('Resposta e fontes','Prompt `rag_v1.md` e `rag_v2.md`; hierarquia de instruções; citações `[F1]` com fonte, seção e página; normalização de variantes e rejeição de IDs inexistentes. Uma segunda geração é tentada se faltar citação.'),
    ('Segurança','Guardrails de prompt injection, fora de escopo e intervenção elétrica perigosa. Segurança v2 impede orientação para abrir equipamento energizado e encaminha ao profissional qualificado.'),
    ('Interface','Gradio com histórico conversacional e fontes; aplicação FastAPI legada preservada para a Sprint 3.')
],[106,w-106]))
append(para('2.1. Limites de fonte e licenciamento','sub'))
append(para('O manual GoodWe V1.5-2025-11-11 aplica-se a GW7K-HCA-20 (7 kW), GW11K-HCA-20 (11 kW) e GW22K-HCA-20 (22 kW). O mapa Modbus descreve, por exemplo, o endereço <b>10015</b> para potência, mas não fornece leituras atuais das estações simuladas. A origem/versão pública do mapa precisa de confirmação.','body'))
append(para('Não existem regulamento condominial real ou tabela tarifária contratual verificável no material. A base registra faturamento <b>simulado</b> de R$ 18.420,00, sem permitir deduzir preço por kWh. O manual restringe reprodução pública; o projeto publica links oficiais e resumos autorais, não os três PDFs completos.','body'))

append(PageBreak())
# PAGE 3 evaluation
append(para('3. Avaliação RAG e melhoria mensurada','sec'))
append(para('<b>Método:</b> rubrica humana com notas 0 / 0,5 / 1; faithfulness = aderência factual às evidências recuperadas; answer relevancy = atendimento à pergunta ou recusa apropriada. <b>Não são escores do RAGAS oficial.</b> Foram julgadas 22 perguntas iguais em cada uma das três rodadas (66 julgamentos).','body'))
append(tbl(['Versão (22/22)','Faithfulness','Answer relevancy','Mudança'],[
    ('I1: RAG v1 (400/40, k3)','0,9773','0,9773','Base'),
    ('I2: RAG v2 (750/100, k4)','1,0000','0,9773','F sobe; A empata'),
    ('I2 + segurança v2','1,0000','1,0000','<b>Ganho nas duas vs I1</b>')
],[204,87,108,w-399]))
append(Spacer(1,7))
append(para('<b>Ganho final em relação à I1: +0,0227 (2,27 pontos percentuais) nas duas métricas.</b> Em comparação apenas I2 vs I1, a métrica de relevância não melhorou. A revisão de segurança é o terceiro passo experimental documentado; não alterou o corpus nem o índice da I2.','body'))
append(para('3.1. Evidências de melhoria','sub'))
append(tbl(['Questão','O que ocorreu na avaliação'],[
    ('R07','Na I1, resposta associou RFID ao preenchimento automático de todos os campos sem evidência → faithfulness 0,5. Na I2, descreveu somente os campos e o vínculo RFID → 1,0.'),
    ('R14','Na I1 e I2, recusa genérica de manutenção energizada → relevancy 0,5. Com segurança v2, alerta de choque e orientação para isolamento e técnico → relevancy 1,0.'),
    ('R09, R10, R11, H07, H08','Recusas corretas: tarifa contratual, tensão em tempo real, modelo exato de GW-09, leitura atual de Modbus e preço condominial ausentes.'),
    ('R12 e R13','Bloqueio de prompt injection e pergunta fora do escopo, sem citação externa necessária.')
],[111,w-111]))
append(para('3.2. Validade e reprodutibilidade','sub'))
append(para('O relatório do computador do grupo confirmou corpus/fingerprint e mesmas perguntas nas três versões. As coletas e rubricas originais (com trechos dos PDFs e identificação do avaliador) permanecem locais. O repositório inclui as métricas agregadas e um resumo das 66 notas, que <b>não substitui</b> a auditoria dos arquivos brutos. As médias são válidas para este conjunto pequeno, não para todos os usos futuros.','body'))

append(PageBreak())
# PAGE 4 models & problems
append(para('4. Comparação de modelos e decisões técnicas','sec'))
append(para('4.1. Modelos e parâmetros','sub'))
append(para('Gerador principal: <b>gpt-oss:120b</b> via Ollama Cloud; embeddings Nomic local (família Nomic Embed). Os dois perfis RAG mantiveram o modelo principal e alteraram prompt, chunking e k. Uma comparação com <b>gpt-oss:20b</b> foi executada historicamente no corpus pré-HCA (14 perguntas), portanto não prova o desempenho dos dois modelos no conjunto atual de 22 casos.','body'))
append(tbl(['Comparação histórica (14 casos)','gpt-oss:120b','gpt-oss:20b'],[
    ('Casos processados sem erro','14/14','14/14'),
    ('Latência média observada','1.594,76 ms','1.669,64 ms'),
    ('Respostas com citação visível','50,0%','50,0%')
],[w-225,112.5,112.5]))
append(para('Essa comparação mede processamento/latência e presença de citações, <b>não qualidade factual</b>. Não comparar diretamente latência de Sprints 2–3 com a RAG atual. Parâmetros da geração RAG incluem temperatura efetiva baixa/determinística, top_p=0,9 e limite de saída 350 tokens; configurar no `.env`/código.','small'))
append(para('4.2. Problemas e ajustes realizados','sub'))
append(tbl(['Problema','Tratamento e aprendizado'],[
    ('Contexto integral e histórico crescente','A Sprint 3 separou funções, sessões e limites de memória; Sprint 4 passou a recuperar trechos relevantes.'),
    ('Documentos e citações inconsistentes','Chunking versionado; referência `[F#]` validada. Variantes `【F1】` e `[Referência: F1]` foram normalizadas; resposta sem referência válida pode ser gerada uma segunda vez ou recusada.'),
    ('Dados não disponíveis','Recusar telemetria atual, tarifas e associação GW-09→modelo. Diferenciar dados operacionais simulados de ficha de fábrica.'),
    ('Intervenção elétrica perigosa','Guardrail da segurança v2 agora impede abrir e substituir componentes energizados; não oferece passos de operação perigosa.'),
    ('Direitos autorais / execução pública','Arquivos HCA completos e coletas com trechos do manual ficam fora do GitHub. Importação local reproduz o índice.')
],[142,w-142]))
append(para('4.3. Testes executados','sub'))
append(para('<b>42/42 testes automatizados aprovados</b> após a atualização de segurança. A coleta hca_safety teve 22/22 casos processados, com três recusas via guardrail. A suíte automatizada não substitui a avaliação manual das respostas.','body'))

append(PageBreak())
# PAGE 5 team + checklist
append(para('5. Equipe, entrega e requisitos finais','sec'))
append(para('5.1. Equipe (tarefas propostas para a Sprint 4 — confirmar autoria real)','sub'))
append(tbl(['Integrante / RM','Frente de trabalho sugerida'],[
    ('Felipe Mitsuo Takahashi Stephano — 570692','Pipeline RAG/LCEL e ChatOllama'),
    ('Felipe Perdigão Macedo — 570990','Interface Gradio, sessão e memória'),
    ('Laura Godoy Callegari — 569181','Corpus, embeddings Nomic e ChromaDB'),
    ('Letícia Araújo Espindola — 569308','Chunking, prompts versionados e citações'),
    ('Mariana Dreset Carbollan — 569207','Guardrails, segurança e testes adversariais'),
    ('Milena de Aguiar Lopes Cardoso — 570599','Rubrica, comparações, métricas e relatório')
],[247,w-247]))
append(para('A tabela acima é uma <b>proposta de divisão</b>, não comprovação de autoria. O grupo deve validar quem realizou cada tarefa antes de entregar. A divisão anterior da Sprint 3 consta no histórico do repositório.','tiny'))
append(para('5.2. Matriz de conformidade e ressalvas','sub'))
append(tbl(['Tema','Situação demonstrada e limite'],[
    ('Pipeline, persistência, fontes, interface','Código presente; duas configurações, PDFs locais e Gradio; coleções 349/216 chunks registradas no computador do grupo.'),
    ('Avaliação e evolução','66 notas em rubrica manual; ganho em ambas as métricas da I2+segurança v2 vs I1; resumo público, brutos locais.'),
    ('Modelos / parâmetros','I1 vs I2 compara parâmetros sobre corpus HCA. 120b vs 20b tem dados de 14 casos históricos; comparação de ambos no corpus HCA final é opcional se exigida literalmente.'),
    ('Documentos reais pendentes','Há manuais HCA G2, mas faltam regimento condominial real e tabela tarifária aplicável verificável; não afirmar cumprimento integral desses itens.'),
    ('Provedor Nomic e procedência','Nomic v1.5 via Python local em vez de embeddings Ollama Cloud. Consultar docente; map Modbus tem procedência pública não verificada.'),
    ('Publicação GitHub','Não subir `.env`, PDFs protegidos, ChromaDB local, coletas HCA brutas ou rubricas identificadas.')
],[155,w-155]))
append(para('Conclusão','sub'))
append(para('A Sprint 4 evoluiu o chatbot operacional para RAG com interface web, bases persistentes, citações verificadas, avaliação em três etapas e proteção específica de segurança elétrica. A rubrica manual mediu melhora de <b>97,73% para 100% em ambas as métricas</b> versus a primeira iteração. Os limites documentais e a aceitação da adaptação de embeddings permanecem sujeitos a validação externa, sem ocultar pendências.','body'))


def page(canvas,doc):
    canvas.saveState()
    canvas.setStrokeColor(RULE); canvas.setLineWidth(.75)
    canvas.line(38,39,A4[0]-38,39)
    canvas.setFont('GWF',7.3);canvas.setFillColor(MUTED)
    canvas.drawString(38,26,'GoodWe Grid Assistant  |  Sprint 04  |  FIAP')
    canvas.drawRightString(A4[0]-38,26,f'{doc.page}/5')
    canvas.restoreState()

OUT.parent.mkdir(parents=True, exist_ok=True)
doc=SimpleDocTemplate(str(OUT),pagesize=A4,leftMargin=38,rightMargin=38,topMargin=32,bottomMargin=53,
                      title='GoodWe Grid Assistant - Sprint 04 - Relatorio final',author='Grupo GoodWe - relatório acadêmico')
doc.build(STORY,onFirstPage=page,onLaterPages=page)
print('PDF salvo:',OUT)
