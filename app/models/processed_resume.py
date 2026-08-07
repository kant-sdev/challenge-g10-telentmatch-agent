from pydantic import BaseModel
from app.models.candidate import CandidateProfile
from app.services.embeddings.model import ChunkEmbedding


class ProcessedResume(BaseModel):
    filename: str
    candidate: CandidateProfile
    chunks: list[str]
    embeddings: list[ChunkEmbedding]
    metadata: dict