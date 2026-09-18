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
    Uses MD5 term and char n-gram hashing for robust semantic keyword matching.
    """

    def __init__(self, dimension: int = 384):
        self._dim = dimension
        self._stopwords = {
            "a", "an", "the", "in", "on", "at", "to", "for", "of", "and", "or",
            "is", "are", "was", "were", "what", "which", "how", "i", "want", "my",
            "me", "should", "use", "make", "do", "so"
        }

    def _generate_vector(self, text: str) -> List[float]:
        import hashlib
        import re
        vec = np.zeros(self._dim, dtype=np.float32)
        words = re.findall(r'\b[a-zA-Z0-9_\u0900-\u097F\u0B80-\u0BFF]+\b', text.lower())
        
        for word in words:
            weight = 0.5 if word in self._stopwords else 2.0
            # Word level hash
            h_val = int(hashlib.md5(word.encode("utf-8")).hexdigest(), 16)
            pos = h_val % self._dim
            vec[pos] += weight

            # 3-gram and 4-gram subword hashing for stem matching
            if len(word) >= 4 and word not in self._stopwords:
                for n in (3, 4):
                    for i in range(len(word) - n + 1):
                        sub = word[i:i+n]
                        sub_h = int(hashlib.md5(sub.encode("utf-8")).hexdigest(), 16)
                        sub_pos = sub_h % self._dim
                        vec[sub_pos] += 0.4

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
