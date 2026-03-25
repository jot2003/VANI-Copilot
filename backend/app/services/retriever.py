import json
from pathlib import Path

import faiss
import numpy as np
import structlog

from app.core.config import settings
from app.services.embedding import EmbeddingService

logger = structlog.get_logger()


class Retriever:
    """FAISS-based retriever with optional re-ranking."""

    _instance: "Retriever | None" = None

    def __init__(self):
        self.index: faiss.Index | None = None
        self.chunks: list[dict] = []
        self.embedding_service = EmbeddingService.get_instance()

    @classmethod
    def get_instance(cls) -> "Retriever":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def load_index(self) -> None:
        index_dir = settings.faiss_index_dir
        index_path = index_dir / "index.faiss"
        meta_path = index_dir / "chunks.json"

        if not index_path.exists() or not meta_path.exists():
            logger.warning("faiss_index_not_found", path=str(index_dir))
            return

        self.index = faiss.read_index(str(index_path))
        self.chunks = json.loads(meta_path.read_text(encoding="utf-8"))
        logger.info("faiss_index_loaded", num_vectors=self.index.ntotal, num_chunks=len(self.chunks))

    def search(self, query: str, top_k: int | None = None) -> list[dict]:
        """Search for relevant chunks given a query string."""
        if self.index is None or not self.chunks:
            logger.warning("retriever_not_ready")
            return []

        k = top_k or settings.top_k_retrieval
        k = min(k, self.index.ntotal)

        query_vec = self.embedding_service.encode_query(query)
        query_vec = np.array([query_vec], dtype=np.float32)

        distances, indices = self.index.search(query_vec, k)

        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx < 0 or idx >= len(self.chunks):
                continue
            chunk = self.chunks[idx].copy()
            chunk["score"] = float(1 / (1 + dist))  # convert L2 distance to similarity
            results.append(chunk)

        return results

    def build_index(self, chunks: list[dict]) -> None:
        """Build FAISS index from chunks and save to disk."""
        if not chunks:
            logger.warning("no_chunks_to_index")
            return

        self.embedding_service.load_model()
        texts = [c["content"] for c in chunks]
        embeddings = self.embedding_service.encode_documents(texts)

        dim = embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dim)
        self.index.add(embeddings.astype(np.float32))
        self.chunks = chunks

        index_dir = settings.faiss_index_dir
        Path(index_dir).mkdir(parents=True, exist_ok=True)

        faiss.write_index(self.index, str(Path(index_dir) / "index.faiss"))
        (Path(index_dir) / "chunks.json").write_text(
            json.dumps(chunks, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        logger.info("faiss_index_built", num_vectors=self.index.ntotal)

    @property
    def is_loaded(self) -> bool:
        return self.index is not None and len(self.chunks) > 0
