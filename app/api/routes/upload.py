import uuid
from typing import Optional

from fastapi import APIRouter, Depends, File, Form, UploadFile

from app.schemas.uploads import UploadResponse
from app.services.ingestion.pipeline import IngestionPipeline

router = APIRouter(
    prefix="/upload",
    tags=["Upload"]
)


@router.post("/cv", response_model=UploadResponse)
async def upload_cv(
    file: UploadFile = File(...),
    group_id: Optional[str] = Form(
        default="global",
        description="ID do grupo ou 'global' para escopo geral",
        examples=["bf034e06-cb53-44b9-a67d-ae15f6cde968"],
    ),
    user_id: Optional[str] = Form(
        default=None,
        description="ID do usuário dono do perfil (opcional, será gerado se não informado)",
        examples=["550e8400-e29b-41d4-a716-446655440000"],
    ),
    pipeline: IngestionPipeline = Depends(IngestionPipeline),
):
    effective_user_id = user_id.strip() if user_id and user_id.strip() else str(uuid.uuid4())
    effective_group_id = group_id.strip() if group_id and group_id.strip() else "global"

    result = await pipeline.execute(
        file=file,
        user_id=effective_user_id,
        group_id=effective_group_id,
    )
    return result
