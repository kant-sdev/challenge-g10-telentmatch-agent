from typing import Optional
from google import genai
from google.genai import types
from google.genai import _transformers
from pydantic import BaseModel, Field

from app.core.config import settings
from app.services.gemini.models import CandidateProfile


def _get_clean_schema(client, model_class):
    schema_obj = _transformers.t_schema(client, model_class)

    def _remove_additional_properties(schema):
        if hasattr(schema, "additional_properties"):
            schema.additional_properties = None
        if hasattr(schema, "properties") and schema.properties:
            for prop in schema.properties.values():
                _remove_additional_properties(prop)
        if hasattr(schema, "items") and schema.items:
            _remove_additional_properties(schema.items)

    _remove_additional_properties(schema_obj)
    return schema_obj


class CandidateMatchOutput(BaseModel):
    name: str = Field(description="Nome completo real do candidato extraído estritamente do contexto. Não inventar.")
    linkedin_url: Optional[str] = Field(default=None, description="URL real do perfil do LinkedIn se constar no contexto, caso contrário null.")
    github_url: Optional[str] = Field(default=None, description="URL real do perfil do GitHub se constar no contexto, caso contrário null.")
    relevance: str = Field(description="Justificativa da aderência do candidato à busca com base exclusiva nos fatos do currículo.")


class SearchResultOutput(BaseModel):
    recommendation: str = Field(description="Síntese da recomendação para o recrutador.")
    matches: list[CandidateMatchOutput] = Field(default_factory=list, description="Lista dos candidatos mais aderentes à busca.")


class GeminiClient:

    def __init__(self):
        # Cliente unificado moderno do Google
        self.client = genai.Client(
            api_key=settings.GEMINI_API_KEY
        )
        self.model = "gemini-3.5-flash-lite"

    def generate_profile(self, prompt: str) -> CandidateProfile:
        """Estrutura os dados do currículo lido do PDF (Passo 1.B)."""
        schema = _get_clean_schema(self.client, CandidateProfile)
        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.2,
                response_mime_type="application/json",
                response_schema=schema,
            ),
        )
        if response.parsed:
            if isinstance(response.parsed, CandidateProfile):
                return response.parsed
            elif isinstance(response.parsed, dict):
                return CandidateProfile.model_validate(response.parsed)
            elif hasattr(response.parsed, "model_dump"):
                return CandidateProfile.model_validate(response.parsed.model_dump())
        return CandidateProfile.model_validate_json(response.text)

    def generate_search_results(self, query: str, chroma_result: dict, group_id: str, limit: int = 5) -> dict:
        """Gera recomendação e lista de candidatos compatíveis com RAG (Passo 2.C)."""
        if not chroma_result or not chroma_result.get("documents") or not chroma_result["documents"][0]:
            return {
                "recommendation": f"Não foram encontrados membros no grupo '{group_id}' com as competências solicitadas.",
                "matches": []
            }

        documents = chroma_result["documents"][0]
        metadatas = chroma_result["metadatas"][0]

        context_chunks = []
        for doc, meta in zip(documents, metadatas):
            name = meta.get("name") or "Nome Não Informado"
            filename = meta.get("filename", "desconhecido.pdf")
            user_id = meta.get("user_id", "N/A")
            linkedin = meta.get("linkedin_url") or "null"
            github = meta.get("github_url") or "null"

            context_chunks.append(
                f"--- Candidato: {name} (Arquivo: {filename}, User ID: {user_id}) ---\n"
                f"LinkedIn no Metadado: {linkedin}\n"
                f"GitHub no Metadado: {github}\n"
                f"Conteúdo do Currículo:\n{doc}"
            )

        context_text_vindo_do_chroma = "\n\n".join(context_chunks)

        prompt_rag = f"""
        Você é o Motor Cognitivo do TalentMatch. Sua tarefa é analisar os currículos fornecidos no contexto e recomendar os candidatos mais adequados para a busca do recrutador.

        Pergunta do Recrutador: {query}

        Contexto dos currículos encontrados no grupo '{group_id}':
        {context_text_vindo_do_chroma}

        Instruções de Preenchimento:
        1. 'recommendation': Escreva uma síntese profissional para o recrutador sobre os candidatos encontrados.
        2. 'matches': Retorne a lista de candidatos mais relevantes (no máximo {limit}).
           Para cada candidato em 'matches':
           - 'name': Nome completo REAL extraído do contexto. NUNCA invente nomes.
           - 'linkedin_url': URL real do LinkedIn do candidato se estiver explicitamente presente no contexto. Caso contrário, retorne null. NUNCA invente ou infira URLs.
           - 'github_url': URL real do GitHub do candidato se estiver explicitamente presente no contexto. Caso contrário, retorne null. NUNCA invente ou infira URLs.
           - 'relevance': Justificativa factual baseada estritamente no contexto de por que o candidato atende à busca '{query}'.
        3. Deduplicação: Garanta que cada candidato apareça apenas uma vez na lista 'matches'.
        """

        schema = _get_clean_schema(self.client, SearchResultOutput)

        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt_rag,
                config=types.GenerateContentConfig(
                    temperature=0.2,
                    response_mime_type="application/json",
                    response_schema=schema,
                ),
            )
            if response.parsed is not None:
                if isinstance(response.parsed, dict):
                    res_data = response.parsed
                elif hasattr(response.parsed, "model_dump"):
                    res_data = response.parsed.model_dump()
                else:
                    res_data = dict(response.parsed)
            elif response.text:
                import json
                res_data = json.loads(response.text)
            else:
                res_data = {}
        except Exception as exc:
            res_data = {
                "recommendation": f"Erro ao processar consulta: {exc}",
                "matches": []
            }

        normalized_matches = []
        seen_names = set()

        for match in res_data.get("matches", []):
            name = str(match.get("name") or "").strip()
            if not name or name.lower() in seen_names:
                continue
            seen_names.add(name.lower())

            linkedin = match.get("linkedin_url")
            if linkedin and (str(linkedin).strip().lower() in ["null", "n/a", "none", ""]):
                linkedin = None
            else:
                linkedin = str(linkedin).strip() if linkedin else None

            github = match.get("github_url")
            if github and (str(github).strip().lower() in ["null", "n/a", "none", ""]):
                github = None
            else:
                github = str(github).strip() if github else None

            normalized_matches.append({
                "name": name,
                "linkedin_url": linkedin,
                "github_url": github,
                "relevance": str(match.get("relevance") or "").strip()
            })

        return {
            "recommendation": str(res_data.get("recommendation") or "").strip(),
            "matches": normalized_matches[:limit]
        }

    def generate_recommendation(self, query: str, chroma_result: dict, group_id: str) -> str:
        """Mantido por compatibilidade legada."""
        res = self.generate_search_results(query=query, chroma_result=chroma_result, group_id=group_id)
        return res.get("recommendation", "")

