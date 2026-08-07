import os

import httpx
from fastapi import UploadFile

from app.core.config import settings
from app.core.logger import logger
from app.models.processed_resume import ProcessedResume
from app.repositories.chroma_repository import ChromaRepository
from app.services.embeddings.service import EmbeddingService
from app.services.gemini.extractor import GeminiExtractor
from app.services.ingestion.chunker import Chunker
from app.services.pdf.normalizer import TextNormalizer
from app.services.pdf.reader import extract_text
from app.services.pdf.validator import validate_pdf


class IngestionPipeline:

    def __init__(self):
        self.chunker = Chunker()
        self.extractor = GeminiExtractor()
        self.embedding_service = EmbeddingService()
        self.chroma_repository = ChromaRepository()
        self.java_backend_url = settings.JAVA_BACKEND_URL.strip().rstrip("/") if settings.JAVA_BACKEND_URL else ""
        self.java_callback_enabled = os.getenv("JAVA_BACKEND_CALLBACK_ENABLED", "false").lower() in {"1", "true", "yes", "on"}

    async def execute(
        self,
        file: UploadFile,
        user_id: str,
        group_id: str
    ):
        # 1. Validação
        validate_pdf(file)

        # 2. Leitura do PDF
        content = await file.read()
        text = extract_text(content)

        # 3. Normalização
        normalized_text = TextNormalizer.normalize(text)

        # 4. Extração estruturada (Gemini)
        candidate = self.extractor.extract(normalized_text)

        # 5. Chunking
        chunks = self.chunker.split(normalized_text)
        logger.info(f"Chunks gerados: {len(chunks)} para o arquivo {file.filename}")

        # 6. Embeddings
        embeddings = self.embedding_service.generate(chunks)

        # 7. Organização de metadados para indexação vetorial
        metadata = {
            "user_id": user_id,
            "group_id": group_id,
            "filename": file.filename or "unknown.pdf"
        }

        # 8. Documento processado
        processed_resume = ProcessedResume(
            filename=file.filename or "unknown.pdf",
            candidate=candidate,
            chunks=chunks,
            embeddings=embeddings,
            metadata=metadata
        )

        # 9. Persistência Vetorial (Salva no ChromaDB com metadados escalares)
        self.chroma_repository.save(processed_resume)

        # 10. Callback Java opcional e configurável
        await self._send_java_callback(processed_resume, user_id, group_id)

        # 11. Resposta
        return {
            "message": "Currículo processado com sucesso.",
            "filename": processed_resume.filename,
            "user_id": user_id,
            "group_id": group_id,
            "candidate": processed_resume.candidate.model_dump(),
            "chunks": len(processed_resume.chunks),
            "embeddings": len(processed_resume.embeddings)
        }

    async def _send_java_callback(self, processed_resume: ProcessedResume, user_id: str, group_id: str):
        """Envia o perfil estruturado ao backend somente quando o callback estiver habilitado."""
        if not self.java_callback_enabled or not self.java_backend_url:
            logger.info("Callback para o backend desativado; o agente retornará o JSON processado sem persistência automática.")
            return

        payload = {
            "user_id": user_id,
            "group_id": group_id,
            "filename": processed_resume.filename,
            "candidate": processed_resume.candidate.model_dump()
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(f"{self.java_backend_url}/api/v1/candidates/callback", json=payload, timeout=10.0)
                if response.status_code in [200, 201]:
                    logger.info(f"Callback enviado com sucesso para o backend (User: {user_id})")
                else:
                    logger.warning(f"Backend recusou o callback com status {response.status_code}: {response.text}")
        except Exception as exc:
            logger.warning(f"Falha de comunicação no callback para o backend: {exc}")
