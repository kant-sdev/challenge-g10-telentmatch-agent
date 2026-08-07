from pydantic_settings import BaseSettings


class Settings(BaseSettings):

    APP_NAME: str = "TalentMatch AI Agent"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"

    GEMINI_API_KEY: str = ""

    CHROMA_HOST: str = "localhost"
    CHROMA_PORT: int = 8000
    CHROMA_PATH: str = "./data/chroma"
    CHROMA_COLLECTION: str = "talentmatch_candidates"

    ALLOWED_ORIGINS: str = "*"

    JAVA_BACKEND_URL: str = ""
    JAVA_BACKEND_CALLBACK_ENABLED: bool = False

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()