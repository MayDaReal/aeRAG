from abc import ABC, abstractmethod
from typing import List

class AbstractChunkingStrategy(ABC):
    """Interface for chunking strategy."""
    
    @abstractmethod
    def chunk(self, content: str) -> List[str]:
        pass
    