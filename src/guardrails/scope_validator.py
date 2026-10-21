import unicodedata


def normalizar(texto: str) -> str:
    texto = unicodedata.normalize("NFD", texto.lower())
    return "".join(c for c in texto if unicodedata.category(c) != "Mn")


FORA_ESCOPO_EXPLICITO = [
    "capital do brasil",
    "receita de bolo",
    "resultado do futebol",
    "placar do jogo",
    "horoscopo",
    "horóscopo",
    "diagnostico medico",
    "diagnóstico médico",
]


def pergunta_fora_escopo_explicita(pergunta: str) -> bool:
    texto = normalizar(pergunta)
    return any(normalizar(item) in texto for item in FORA_ESCOPO_EXPLICITO)
