from fastapi import APIRouter, Depends
from app.schemas.search import SearchRequest, SearchResponse
from app.services.search.service import SearchService

router = APIRouter(
    prefix="/search",
    tags=["Search"]
)


@router.post("/", response_model=SearchResponse)
def search(
    request: SearchRequest,
    service: SearchService = Depends(SearchService)
):
    return service.execute(request)