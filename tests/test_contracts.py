import pytest
from pydantic import ValidationError

from app.models.candidate import CandidateProfile
from app.schemas.search import SearchRequest


def test_candidate_profile_rejects_unexpected_fields():
    with pytest.raises(ValidationError):
        CandidateProfile(
            name="Ana",
            email="ana@example.com",
            phone="11999999999",
            summary="Resumo",
            skills=["Python"],
            experience_level="Pleno",
            years_experience=5,
            education=["Engenharia"],
            certifications=[],
            languages=["Português"],
            full_name="Ana Silva",
        )


def test_search_request_accepts_flexible_group_id():
    req = SearchRequest(query="dev backend", group_id="global", limit=5)
    assert req.group_id == "global"

    req_uuid = SearchRequest(query="dev backend", group_id="3fa85f64-5717-4562-b3fc-2c963f66af44", limit=5)
    assert req_uuid.group_id == "3fa85f64-5717-4562-b3fc-2c963f66af44"
