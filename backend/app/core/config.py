from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    # LLM — primary (Ollama for fine-tuned model) + fallback (Azure OpenAI)
    llm_provider: str = "azure"  # "ollama" | "azure" | "openai"
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "vani-copilot"
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"

    # Azure OpenAI
    azure_openai_api_key: str = ""
    azure_openai_endpoint: str = ""       # e.g. https://xxx.openai.azure.com/
    azure_openai_deployment: str = ""     # e.g. gpt-4o-mini
    azure_openai_api_version: str = "2024-08-01-preview"

    # Agent
    agent_enabled: bool = True
    confidence_threshold: float = 0.7

    # Embedding — local path overrides HuggingFace model ID
    embedding_model: str = "intfloat/multilingual-e5-small"
    embedding_model_path: str = ""
    embedding_device: str = "cpu"

    # Re-ranker
    reranker_enabled: bool = False
    reranker_model_path: str = ""
    reranker_device: str = "cpu"

    # FAISS
    faiss_index_path: str = "vectorstore/faiss_index"
    chunk_size: int = 500
    chunk_overlap: int = 100
    top_k_retrieval: int = 20
    top_k_rerank: int = 5

    # Database
    db_path: str = "data/copilot.db"

    # Security
    api_key: str = "vani-copilot-dev-key"
    cors_origins: str = "http://localhost:5173,http://localhost:3000,http://localhost:3001"

    # Server
    host: str = "0.0.0.0"
    port: int = 8000

    # Timeouts (seconds)
    llm_timeout: float = 120.0
    agent_timeout: float = 60.0

    # Rate limiting
    rate_limit: str = "30/minute"

    # Conversation memory
    max_history_messages: int = 5

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def db_url(self) -> str:
        return f"sqlite+aiosqlite:///{self.db_path}"

    @property
    def faiss_index_dir(self) -> Path:
        return Path(self.faiss_index_path)

    @property
    def resolved_embedding_model(self) -> str:
        if self.embedding_model_path and Path(self.embedding_model_path).exists():
            return self.embedding_model_path
        return self.embedding_model

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
