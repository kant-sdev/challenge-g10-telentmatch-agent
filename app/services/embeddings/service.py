from app.services.embeddings.client import EmbeddingClient
from app.services.embeddings.model import ChunkEmbedding

class EmbeddingService:
    def __init__(self):
        self.client = EmbeddingClient()

    def generate(self, chunks: list[str]) -> list[ChunkEmbedding]:
        if not chunks:
            return []

        # Envia todos os chunks de uma só vez para a API
        vectors = self.client.embed_batch(chunks)

        # Combina cada chunk com seu respectivo vetor gerado
        embeddings = [
            ChunkEmbedding(chunk=chunk, embedding=vector)
        	for chunk, vector in zip(chunks, vectors)
        ]

        return embeddings
