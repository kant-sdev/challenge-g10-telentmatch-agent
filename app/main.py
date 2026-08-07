from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.exceptions import TalentMatchException
from app.api.routes import upload
from app.api.routes import search


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION
)

# Configuração dinâmica de CORS via variável de ambiente ALLOWED_ORIGINS
raw_origins = settings.ALLOWED_ORIGINS.split(",")
allowed_origins = [origin.strip() for origin in raw_origins if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins if allowed_origins else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(TalentMatchException)
async def talentmatch_exception_handler(request: Request, exc: TalentMatchException):
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc), "error_type": exc.__class__.__name__}
    )


@app.get("/health", tags=["Health"])
def health_check():
    return {
        "status": "healthy"
    }


@app.get("/", tags=["Health"])
def root():
    return {
        "status": "online",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION
    }


app.include_router(upload.router)
app.include_router(search.router)