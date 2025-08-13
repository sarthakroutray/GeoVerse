# Configuration management for GeoVerse backend
import os
from typing import List
from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_workers: int = 4
    
    # Database Configuration
    database_url: str = "postgresql://geoverse_user:geoverse_password@localhost:5432/geoverse"
    
    # Neo4j Configuration
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_username: str = "neo4j"
    neo4j_password: str = "geoverse_neo4j"
    
    # Redis Configuration
    redis_url: str = "redis://localhost:6379/0"
    
    # Security
    secret_key: str = "your-super-secret-key-change-this-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # LLM Configuration  
    llm_provider: str = "fallback"  # "gemini", "openrouter", "fallback", or "openai"
    llm_model: str = "deepseek/deepseek-v3"
    max_tokens: int = 4000
    fallback_context_chars: int = 5000  # Max characters of retrieved context to embed in fallback answers (increase for fuller responses)
    
    # Google Gemini Configuration
    gemini_api_key: str = ""
    gemini_model: str = "gemini-1.5-flash"
    gemini_max_tokens: int = 4000
    gemini_temperature: float = 0.7
    
    # OpenRouter Configuration
    openrouter_api_key: str = ""
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    
    # Vector Store Configuration
    vector_store_type: str = "faiss"  # or chromadb
    
    # Embedding Configuration - BGE-Large for best scientific content retrieval
    # Alternative options:
    # - "BAAI/bge-base-en-v1.5" (768 dim, balanced performance)
    # - "microsoft/e5-large-v2" (1024 dim, scientific focus)  
    # - "all-MiniLM-L12-v2" (384 dim, lightweight upgrade)
    # - "hkunlp/instructor-large" (768 dim, with domain instructions)
    embedding_model: str = "BAAI/bge-large-en-v1.5"
    vector_dimension: int = 1024  # BGE-Large dimensions
    
    # Web Scraping Configuration
    scraping_delay: float = 1.0
    scraping_user_agent: str = "GeoVerse-Bot/1.0"
    scraping_timeout: int = 30
    
    # File Storage
    upload_directory: str = "data/uploads"
    data_directory: str = "data"
    raw_data_directory: str = "data/raw"
    processed_data_directory: str = "data/processed"
    embeddings_directory: str = "backend/data/embeddings"
    
    # Additional Database Configuration
    test_database_url: str = "postgresql://username:password@localhost:5432/geoverse_test"
    
    # LangChain Configuration
    langchain_tracing: str = "false"
    langchain_api_key: str = "your_langchain_api_key"
    
    # File Upload Configuration
    max_file_size: str = "50MB"
    
    # Celery Configuration
    celery_broker_url: str = "redis://localhost:6379/1"
    celery_result_backend: str = "redis://localhost:6379/2"
    
    # CORS Configuration
    allowed_origins: List[str] = ["http://localhost:3000", "http://localhost:3001"]
    
    # Rate Limiting
    rate_limit_requests: int = 100
    rate_limit_window: int = 60
    
    # Logging
    log_level: str = "INFO"
    log_file: str = "logs/backend.log"
    
    # Environment
    environment: str = "development"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()

# --- Dynamic path adjustment -------------------------------------------------
# If the default relative 'data' directory does not exist at current working
# directory, but a backend-local data directory exists (backend/data), switch
# all data paths to that backend/data root. This solves cases where the app is
# started from the repo root while data actually lives in backend/data.

try:
    cwd = Path.cwd()
    backend_root = Path(__file__).resolve().parents[2]  # .../backend
    backend_data = backend_root / "data"
    current_data = Path(settings.data_directory)

    # Condition: configured path is the plain default 'data' (relative), it
    # does not exist at CWD, but backend/data exists.
    if (current_data.as_posix() == 'data' and not (cwd / current_data).exists() and backend_data.exists()):
        # Repoint directories
        settings.data_directory = str(backend_data)
        settings.upload_directory = str(backend_data / 'uploads')
        settings.raw_data_directory = str(backend_data / 'raw')
        settings.processed_data_directory = str(backend_data / 'processed')
        settings.embeddings_directory = str(backend_data / 'embeddings')
        # Ensure subdirs exist
        for p in [settings.upload_directory, settings.raw_data_directory, settings.processed_data_directory, settings.embeddings_directory]:
            Path(p).mkdir(parents=True, exist_ok=True)
        # Log (stdout print since logging config may not yet be initialized)
        print(f"[config] Auto-adjusted data directories to backend/data at {backend_data}")
except Exception as _e:
    # Silent fallback; path issues will surface later if critical.
    pass
