from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class CandidateProfile(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(description="Nome completo do candidato")
    email: Optional[str] = Field(default=None, description="Email do candidato")
    phone: Optional[str] = Field(default=None, description="Telefone do candidato")
    linkedin_url: Optional[str] = Field(default=None, description="URL do LinkedIn do candidato, se constar no currículo")
    github_url: Optional[str] = Field(default=None, description="URL do GitHub do candidato, se constar no currículo")

    summary: str = Field(
        description="Resumo profissional em até 500 caracteres"
    )

    skills: list[str]

    experience_level: str = Field(
        description="Ex.: Estagiário, Júnior, Pleno ou Sênior"
    )

    years_experience: int

    education: list[str]

    certifications: list[str]

    languages: list[str]
