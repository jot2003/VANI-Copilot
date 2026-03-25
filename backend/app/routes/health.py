from fastapi import APIRouter

from app.core.config import settings
from app.services.embedding import EmbeddingService
from app.services.retriever import Retriever

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check():
    retriever = Retriever.get_instance()
    embedding = EmbeddingService.get_instance()

    return {
        "status": "ok",
        "llm_provider": settings.llm_provider,
        "agent_enabled": settings.agent_enabled,
        "faiss_index_loaded": retriever.is_loaded,
        "faiss_num_vectors": retriever.index.ntotal if retriever.index else 0,
        "embedding_model_loaded": embedding.is_loaded,
        "embedding_model": settings.resolved_embedding_model,
        "reranker_enabled": settings.reranker_enabled,
    }
