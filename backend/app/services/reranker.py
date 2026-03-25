import structlog
from pathlib import Path

from app.core.config import settings

logger = structlog.get_logger()


class RerankerService:
    """CrossEncoder re-ranker: re-scores retrieval candidates for higher precision."""

    _instance: "RerankerService | None" = None
    _model = None

    @classmethod
    def get_instance(cls) -> "RerankerService":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def load_model(self) -> None:
        if self._model is not None:
            return
        if not settings.reranker_enabled or not settings.reranker_model_path:
            logger.info("reranker_disabled")
            return

        model_path = settings.reranker_model_path
        if not Path(model_path).exists():
            logger.warning("reranker_model_not_found", path=model_path)
            return

        from sentence_transformers import CrossEncoder

        logger.info("loading_reranker", model=model_path, device=settings.reranker_device)
        self._model = CrossEncoder(model_path, device=settings.reranker_device)
        logger.info("reranker_loaded")

    def rerank(self, query: str, documents: list[dict], top_k: int = 5) -> list[dict]:
        """Re-rank retrieved chunks by cross-encoder relevance score."""
        if self._model is None or not documents:
            return documents[:top_k]

        pairs = [(query, doc["content"]) for doc in documents]
        scores = self._model.predict(pairs)

        for doc, score in zip(documents, scores):
            doc["rerank_score"] = float(score)

        reranked = sorted(documents, key=lambda d: d["rerank_score"], reverse=True)
        return reranked[:top_k]

    @property
    def is_loaded(self) -> bool:
        return self._model is not None
