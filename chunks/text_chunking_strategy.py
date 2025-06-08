from .abstract_chunking_strategy import AbstractChunkingStrategy
from typing import List, Dict, Any

class TextChunkingStrategy(AbstractChunkingStrategy):
    """Splits text into overlapping chunks of a certain size."""
    def __init__(self, chunk_size: int = 500, overlap: int = 50):
        self.chunk_size = chunk_size
        self.overlap = overlap

    def __init__(self, settings: Dict[str, Any] = {}):
        self.chunk_size = settings.get("chunkz_size", 500)
        self.overlap = settings.get("overlap", 50)

    def chunk(self, content: str) -> List[str]:
        chunks = []
        step = self.chunk_size - self.overlap
        for i in range(0, len(content), step):
            chunks.append(content[i:i + self.chunk_size])
        return chunks
