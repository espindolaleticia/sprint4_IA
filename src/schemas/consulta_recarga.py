import re
from typing import Literal

from pydantic import BaseModel, Field, field_validator


class ConsultaRecarga(BaseModel):
    tipo_consulta: Literal[
        "status",
        "falha",
        "consumo",
        "faturamento",
        "potencia",
        "manutencao",
        "alerta",
        "ciclo_recarga",
        "rfid",
        "fora_escopo",
    ] = Field(description="Categoria principal da consulta do usuário.")

    estacoes: list[str] = Field(
        default_factory=list,
        description="Estações mencionadas ou encontradas, no padrão GW-XX.",
    )

    status: Literal[
        "online",
        "offline",
        "falha_critica",
        "alerta",
        "normal",
        "desconhecido",
        "nao_aplicavel",
    ] = Field(description="Estado operacional principal relacionado à consulta.")

    consumo_kwh: float | None = Field(
        default=None, ge=0, description="Consumo em kWh quando houver dado disponível."
    )
    potencia_percentual: float | None = Field(
        default=None,
        ge=0,
        le=100,
        description="Percentual de uso da capacidade da rede, quando aplicável.",
    )
    faturamento_reais: float | None = Field(
        default=None,
        ge=0,
        description="Faturamento em reais quando houver dado disponível.",
    )
    necessita_escalacao: bool = Field(
        description="Indica se o caso deve ser encaminhado a suporte técnico humano/profissional habilitado."
    )
    evidencias: list[str] = Field(
        default_factory=list,
        description="Fatos do contexto operacional que sustentam a resposta.",
    )
    resumo: str = Field(
        default="Resumo não informado pelo modelo.",
        min_length=3,
        description="Resumo objetivo da conclusão da consulta."
    )

    @field_validator("estacoes")
    @classmethod
    def validar_estacoes(cls, valores: list[str]) -> list[str]:
        normalizadas: list[str] = []
        for valor in valores:
            estacao = valor.strip().upper()
            if not re.fullmatch(r"GW-\d{2}", estacao):
                raise ValueError("Cada estação deve seguir o padrão GW-XX.")
            if estacao not in normalizadas:
                normalizadas.append(estacao)
        return normalizadas

    @field_validator("evidencias")
    @classmethod
    def limpar_evidencias(cls, valores: list[str]) -> list[str]:
        return [valor.strip() for valor in valores if valor and valor.strip()]
