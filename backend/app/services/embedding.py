import numpy as np
import structlog
from sentence_transformers import SentenceTransformer

from app.core.config import settings

logger = structlog.get_logger()


class EmbeddingService:
    _instance: "EmbeddingService | None" = None
    _model: SentenceTransformer | None = None

    @classmethod
    def get_instance(cls) -> "EmbeddingService":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def load_model(self) -> None:
        if self._model is not None:
            return
        model_id = settings.resolved_embedding_model
        device = settings.embedding_device
        logger.info("loading_embedding_model", model=model_id, device=device)
        self._model = SentenceTransformer(model_id, device=device)
        logger.info(
            "embedding_model_loaded",
            dim=self._model.get_sentence_embedding_dimension(),
            device=device,
        )

    @property
    def model(self) -> SentenceTransformer:
        if self._model is None:
            self.load_model()
        return self._model

    @property
    def dimension(self) -> int:
        return self.model.get_sentence_embedding_dimension()

    def encode(self, texts: list[str], prefix: str = "query: ") -> np.ndarray:
        """Encode texts into embeddings. E5 models need 'query: ' or 'passage: ' prefix."""
        prefixed = [f"{prefix}{t}" for t in texts]
        return self.model.encode(prefixed, normalize_embeddings=True, show_progress_bar=False)

    def encode_query(self, query: str) -> np.ndarray:
        return self.encode([query], prefix="query: ")[0]

    def encode_documents(self, docs: list[str]) -> np.ndarray:
        return self.encode(docs, prefix="passage: ")

    @property
    def is_loaded(self) -> bool:
        return self._model is not None
