from pydantic import BaseModel
from app.models.candidate import CandidateProfile


class UploadResponse(BaseModel):
    message: str
    filename: str
    user_id: str
    group_id: str
    candidate: CandidateProfile
    chunks: int
    embeddings: int
