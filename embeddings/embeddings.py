from abc import ABC, abstractmethod
from typing import List

class AbstractEmbeddingModel(ABC):
    @abstractmethod
    def encode(self, text: str) -> List[float]:
        """Encodes text into an embedding vector."""
        pass

from sentence_transformers import SentenceTransformer

class SentenceTransformerEmbeddingModel(AbstractEmbeddingModel):
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)

    def encode(self, text: str) -> List[float]:
        return self.model.encode(text).tolist()