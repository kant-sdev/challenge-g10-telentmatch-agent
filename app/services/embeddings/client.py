from google import genai
from app.core.config import settings

class EmbeddingClient:
    def __init__(self):
        # Cliente unificado oficial
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
        # Modelo unificado aceito na v1beta
        self.model = "gemini-embedding-001"

    def embed(self, text: str) -> list[float]:
        """Gera o embedding para uma única string (usado na Busca/Search)."""
        if not text.strip():
            return []
            
        response = self.client.models.embed_content(
            model=self.model,
            contents=text,
        )
        # CORREÇÃO: response.embeddings é uma lista. Acessamos o índice [0] primeiro!
        return response.embeddings[0].values

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Gera embeddings para múltiplos textos de uma vez (usado no Indexador/Service)."""
        if not texts:
            return []
            
        response = self.client.models.embed_content(
            model=self.model,
            contents=texts,
        )
        # No lote, iteramos por cada item da lista extraindo o seu respectivo .values
        return [emb.values for emb in response.embeddings]
