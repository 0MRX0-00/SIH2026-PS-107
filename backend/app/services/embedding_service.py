import logging
from abc import ABC, abstractmethod
from typing import List
import numpy as np

from app.core.config import settings

logger = logging.getLogger("ebis_sahayak.embedding")


class BaseEmbeddingService(ABC):
    @abstractmethod
    def embed_text(self, text: str) -> List[float]:
        pass

    @abstractmethod
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        pass

    @abstractmethod
    def embed_query(self, query: str) -> List[float]:
        pass

    @property
    @abstractmethod
    def dimension(self) -> int:
        pass


class FastEmbedService(BaseEmbeddingService):
    """
    Fast, CPU-optimized embedding generation using FastEmbed (ONNX runtime).
    Model default: BAAI/bge-small-en-v1.5 (384 dimensions) or BAAI/bge-m3 (1024 dimensions).
    """

    def __init__(self, model_name: str = "BAAI/bge-small-en-v1.5"):
        self.model_name = model_name
        self._model = None
        self._dimension = 384 if "small" in model_name else 1024

    def _get_model(self):
        if self._model is None:
            try:
                from fastembed import TextEmbedding
                logger.info(f"Initializing FastEmbed TextEmbedding model: {self.model_name}")
                self._model = TextEmbedding(model_name=self.model_name, threads=1)
            except Exception as e:
                logger.warning(f"FastEmbed initialization failed: {e}. Falling back to deterministic embedding.")
                self._model = FallbackDeterministicEmbeddingService(dimension=self._dimension)
        return self._model

    def embed_text(self, text: str) -> List[float]:
        model = self._get_model()
        if isinstance(model, FallbackDeterministicEmbeddingService):
            return model.embed_text(text)
        embeddings = list(model.embed([text]))
        return embeddings[0].tolist()

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []
        model = self._get_model()
        if isinstance(model, FallbackDeterministicEmbeddingService):
            return model.embed_documents(texts)
        embeddings = list(model.embed(texts))
        return [emb.tolist() for emb in embeddings]

    def embed_query(self, query: str) -> List[float]:
        model = self._get_model()
        if isinstance(model, FallbackDeterministicEmbeddingService):
            return model.embed_query(query)
        # FastEmbed has optimized query passage routing
        embeddings = list(model.embed([f"Represent this sentence for searching relevant passages: {query}"]))
        return embeddings[0].tolist()

    @property
    def dimension(self) -> int:
        return self._dimension


class FallbackDeterministicEmbeddingService(BaseEmbeddingService):
    """
    Fast, deterministic hash-based embedding service for unit tests and zero-dependency environments.
    """

    def __init__(self, dimension: int = 384):
        self._dim = dimension

    def _generate_vector(self, text: str) -> List[float]:
        vec = np.zeros(self._dim, dtype=np.float32)
        for idx, token in enumerate(text.lower().split()):
            pos = abs(hash(token) + idx) % self._dim
            vec[pos] += 1.0
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        return vec.tolist()

    def embed_text(self, text: str) -> List[float]:
        return self._generate_vector(text)

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return [self._generate_vector(t) for t in texts]

    def embed_query(self, query: str) -> List[float]:
        return self._generate_vector(query)

    @property
    def dimension(self) -> int:
        return self._dim


def get_embedding_service() -> BaseEmbeddingService:
    """Factory to instantiate the configured embedding service."""
    provider = settings.EMBEDDING_PROVIDER.lower()
    if provider in {"fastembed", "sentence-transformers"}:
        return FastEmbedService(model_name="BAAI/bge-small-en-v1.5")
    elif provider == "fallback":
        return FallbackDeterministicEmbeddingService(dimension=settings.EMBEDDING_DIMENSION)
    return FastEmbedService()
