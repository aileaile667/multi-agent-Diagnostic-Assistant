"""Application configuration loaded from environment variables."""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # LLM
    deepseek_api_key: str = ""
    deepseek_model: str = "deepseek-v4-flash"
    deepseek_base_url: str = "https://api.deepseek.com"
    llm_timeout_seconds: float = 60.0
    llm_max_retries: int = 1

    # Legacy OpenAI env vars are kept as a fallback so older .env files do not
    # fail during startup while migrating to DeepSeek.
    openai_api_key: str = ""
    openai_model: str = ""

    # PostgreSQL
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "clinical_decision"
    postgres_user: str = "postgres"
    postgres_password: str = ""

    # Neo4j
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = ""
    graphrag_use_neo4j: bool = False

    # Redis
    redis_host: str = "localhost"
    redis_port: int = 6379

    # FHIR
    fhir_server_url: str = "http://localhost:8080/fhir"

    # App
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    log_level: str = "INFO"

    @property
    def postgres_dsn(self) -> str:
        return (
            f"postgresql://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def llm_api_key(self) -> str:
        return self.deepseek_api_key or self.openai_api_key

    @property
    def llm_model(self) -> str:
        return self.deepseek_model or self.openai_model

    @property
    def llm_base_url(self) -> str:
        return self.deepseek_base_url

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache
def get_settings() -> Settings:
    return Settings()
