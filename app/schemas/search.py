from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class SearchRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    query: str = Field(
        ...,
        description="Consulta em linguagem natural."
    )

    group_id: Optional[str] = Field(
        default="global",
        description="ID do grupo onde a busca será realizada, ou 'global' para todos os grupos."
    )

    limit: int = Field(
        default=5,
        ge=1,
        le=20
    )


class CandidateMatch(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(description="Nome do candidato")
    linkedin_url: Optional[str] = Field(default=None, description="URL do perfil do LinkedIn")
    github_url: Optional[str] = Field(default=None, description="URL do perfil do GitHub")
    relevance: str = Field(description="Justificativa de aderência do candidato à busca")


class SearchResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    recommendation: str = Field(description="Texto da recomendação gerada pelo agente")
    matches: list[CandidateMatch] = Field(default_factory=list, description="Lista de candidatos encontrados")