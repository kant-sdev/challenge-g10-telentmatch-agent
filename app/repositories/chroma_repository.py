import uuid

import chromadb

from app.core.config import settings
from app.models.processed_resume import ProcessedResume


class ChromaRepository:

    def __init__(self):
        self.client = chromadb.PersistentClient(
            path=settings.CHROMA_PATH
        )
        self.collection = self.client.get_or_create_collection(
            name=settings.CHROMA_COLLECTION
        )

    def save(self, processed_resume: ProcessedResume):
        if not processed_resume.embeddings:
            return

        resume_id = uuid.uuid4().hex[:8]
        ids = [
            f"{processed_resume.filename}_{resume_id}_chunk_{idx}"
            for idx in range(len(processed_resume.embeddings))
        ]
        documents = [item.chunk for item in processed_resume.embeddings]
        embeddings = [item.embedding for item in processed_resume.embeddings]
        
        raw_metadata = dict(processed_resume.metadata or {})

        candidate_obj = getattr(processed_resume, "candidate", None)
        candidate_name = getattr(candidate_obj, "name", "") if candidate_obj else ""
        linkedin_url = getattr(candidate_obj, "linkedin_url", "") if candidate_obj else ""
        github_url = getattr(candidate_obj, "github_url", "") if candidate_obj else ""

        normalized_metadata = {
            "user_id": str(raw_metadata.get("user_id") or "").strip(),
            "group_id": str(raw_metadata.get("group_id") or raw_metadata.get("group_ids") or "").strip(),
            "filename": str(raw_metadata.get("filename") or "unknown.pdf").strip(),
            "name": str(candidate_name or "").strip(),
            "linkedin_url": str(linkedin_url or "").strip(),
            "github_url": str(github_url or "").strip()
        }

        if normalized_metadata["group_id"] and isinstance(raw_metadata.get("group_ids"), (list, tuple)):
            normalized_metadata["group_id"] = str(raw_metadata["group_ids"][0]).strip()
        elif normalized_metadata["group_id"].startswith("[") and normalized_metadata["group_id"].endswith("]"):
            normalized_metadata["group_id"] = normalized_metadata["group_id"].strip("[]")

        metadatas = [
            {
                **normalized_metadata,
                "chunk_index": idx
            }
            for idx in range(len(processed_resume.embeddings))
        ]

        self.collection.add(
            ids=ids,
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas
        )

    def search(
        self,
        embedding: list[float],
        group_id: str = None,
        n_results: int = 5
    ):
        query_args = {
            "query_embeddings": [embedding],
            "n_results": n_results,
            "include": ["documents", "metadatas", "distances"]
        }

        if not group_id or group_id.strip().lower() in ["global", "all", "global-pool"]:
            return self.collection.query(**query_args)

        target_group = group_id.strip()
        query_args["where"] = {"group_id": {"$eq": target_group}}

        return self.collection.query(**query_args)
