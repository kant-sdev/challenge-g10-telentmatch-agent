from pydantic import BaseModel


class ChunkEmbedding(BaseModel):

    chunk: str

    embedding: list[float]