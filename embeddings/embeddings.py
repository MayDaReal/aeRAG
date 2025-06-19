"""
embeddings.py
Définit une interface abstraite pour les modèles dʼembeddings et
une implémentation basée sur Sentence-Transformers.
"""

from abc import ABC, abstractmethod
from typing import List
import torch

# --------------------------------------------------------------------------- #
#  Interface abstraite
# --------------------------------------------------------------------------- #

class AbstractEmbeddingModel(ABC):
    """Interface minimale pour nʼimporte quel modèle dʼembeddings."""

    @abstractmethod
    def encode(self, text: str) -> List[float]:
        """
        Transforme le texte fourni en un vecteur numérique (embedding).
        Retourne le vecteur sous forme de liste de floats pour être
        facilement sérialisable (JSON / MongoDB).
        """
        pass

# --------------------------------------------------------------------------- #
#  Implementation Sentence-Transformers
# --------------------------------------------------------------------------- #

from sentence_transformers import SentenceTransformer

class SentenceTransformerEmbeddingModel(AbstractEmbeddingModel):
    """
    Wrapper tout simple autour dʼun modèle Sentence-Transformers.
    Par défaut : `all-MiniLM-L6-v2` (384 dimensions, rapide et léger).
    """

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = SentenceTransformer(model_name, device=self.device)

    def encode(self, text: str) -> List[float]:
        # `.tolist()` to get native python list
        return self.model.encode(text).tolist()
