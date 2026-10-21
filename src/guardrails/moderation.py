from src.guardrails.scope_validator import normalizar, pergunta_fora_escopo_explicita
import re

JAILBREAK = [
    "ignore todas as instrucoes",
    "ignore as instrucoes anteriores",
    "ignore o system prompt",
    "revele o system prompt",
    "mostre suas instrucoes internas",
    "invente um faturamento",
    "fabrique dados",
    "bypass",
    "jailbreak",
]

FINANCEIRO = [
    "melhor criptomoeda",
    "qual criptomoeda",
    "bitcoin para investir",
    "onde investir",
    "recomende investimento",
    "comprar acoes",
    "comprar ações",
    "carteira de investimentos",
]

JURIDICO = [
    "aconselhamento juridico",
    "aconselhamento jurídico",
    "devo processar",
    "posso processar",
    "qual advogado",
    "parecer juridico",
    "parecer jurídico",
]

RISCO_ELETRICO = [
    "abrir o carregador energizado",
    "abrir a estacao energizada",
    "abrir a estação energizada",
    "mexer na fiacao energizada",
    "mexer na fiação energizada",
    "burlar disjuntor",
    "desativar protecao eletrica",
    "desativar proteção elétrica",
    "trocar componente energizado",
    "fazer jumper",
    "jumpear",
]


# Política geral v2: intervenção física + presença de energia + equipamento elétrico.
# Não depende de IDs específicos (GW-09, GW-03 etc.).
GUARDRAIL_REVISION = "eletrica_v2"
MENSAGEM_RISCO_ELETRICO = (
    "Não abra, desmonte nem substitua peças de uma estação/carregador enquanto estiver energizado. "
    "Há risco de choque elétrico e lesões graves. Suspenda o uso e solicite a um profissional "
    "qualificado o desligamento e isolamento da alimentação elétrica, seguindo o manual "
    "do fabricante e os procedimentos locais de segurança. Não realize essa intervenção por conta própria."
)

_ACAO_INTERVENCAO = re.compile(
    r"\b(?:abrir|abro|abra|abertura|trocar|troca|substituir|substituicao|substitua|"
    r"desmontar|desmontagem|remover|retirar|mexer|manutencao|reparo|reparar|consertar|"
    r"intervir|intervencao|manipular|acessar\s+o\s+interior)\b"
)
_EQUIPAMENTO_ELETRICO = re.compile(
    r"\b(?:gw[- ]?\d{1,4}|estacao|eletroposto|carregador|wallbox|equipamento|"
    r"modulo|painel|quadro|disjuntor|fio|fiacao|cabo|circuito|tomada)\b"
)
_SOB_ENERGIA = re.compile(
    r"\b(?:energizad[oa]s?|sob\s+tensao|com\s+(?:a\s+)?energia\s+ligada|"
    r"com\s+(?:o\s+)?equipamento\s+ligado|sem\s+desligar|sem\s+desenergizar|"
    r"sem\s+cortar\s+(?:a\s+)?energia|com\s+tensao|ligad[oa]s?)\b"
)


def _intervencao_com_energia(pergunta: str) -> bool:
    texto = normalizar(pergunta)
    return bool(
        _ACAO_INTERVENCAO.search(texto)
        and _EQUIPAMENTO_ELETRICO.search(texto)
        and _SOB_ENERGIA.search(texto)
    )


def _contem(pergunta: str, padroes: list[str]) -> bool:
    texto = normalizar(pergunta)
    return any(normalizar(padrao) in texto for padrao in padroes)


def aplicar_guardrails(pergunta: str) -> str | None:
    if _contem(pergunta, JAILBREAK):
        return (
            "Não posso ignorar ou revelar instruções internas nem inventar dados. "
            "Vou responder somente com base no contexto operacional disponível do GoodWe Grid Assistant."
        )

    if _contem(pergunta, FINANCEIRO):
        return (
            "Esse pedido está fora do escopo do GoodWe Grid Assistant. Não forneço aconselhamento financeiro "
            "ou recomendações de investimento. Procure um profissional financeiro habilitado. "
            "Posso ajudar com a operação de eletropostos GoodWe."
        )

    if _contem(pergunta, JURIDICO):
        return (
            "Esse pedido está fora do escopo do GoodWe Grid Assistant. Não forneço aconselhamento jurídico. "
            "Consulte um profissional jurídico habilitado. Posso ajudar com informações operacionais de eletropostos GoodWe."
        )

    if _contem(pergunta, RISCO_ELETRICO) or _intervencao_com_energia(pergunta):
        return MENSAGEM_RISCO_ELETRICO

    if pergunta_fora_escopo_explicita(pergunta):
        return (
            "Esse tema está fora do escopo do GoodWe Grid Assistant. "
            "Posso ajudar com operação de eletropostos GoodWe, incluindo status, falhas, consumo, potência, manutenção e faturamento."
        )

    return None
