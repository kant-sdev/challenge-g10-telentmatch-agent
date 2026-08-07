from app.repositories.chroma_repository import ChromaRepository
from app.schemas.search import SearchRequest
from app.services.embeddings.client import EmbeddingClient
from app.services.gemini.client import GeminiClient


class SearchService:

    def __init__(self):
        self.embedding_client = EmbeddingClient()
        self.repository = ChromaRepository()
        self.gemini_client = GeminiClient()

    def execute(self, request: SearchRequest):
        """Executa a busca semântica híbrida com RAG."""
        embedding = self.embedding_client.embed(request.query)

        chroma_result = self.repository.search(
            embedding=embedding,
            group_id=request.group_id,
            n_results=15
        )

        return self.gemini_client.generate_search_results(
            query=request.query,
            chroma_result=chroma_result,
            group_id=request.group_id,
            limit=request.limit
        )
