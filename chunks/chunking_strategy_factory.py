from .abstract_chunking_strategy import AbstractChunkingStrategy
from .text_chunking_strategy import TextChunkingStrategy
from .code_chunking_strategy import CodeChunkingStrategy

from typing import Dict, Any

class ChunkingStrategyFactory:
    """Returns appropriate strategy based on file type."""

    @staticmethod
    def get_strategy(file_type: str = "", settings: Dict[str, Any] = {}) -> AbstractChunkingStrategy:
        if file_type == "code":
            return CodeChunkingStrategy(settings)
        else:
            return TextChunkingStrategy(settings)  # default
        
        # TODO manage log and doc (in near future try to manage sepcific doc, config, image, video)
        # TODO manage mistral to summarize
        # TODO implement minimaliste rag_engine and try to chat with them
        # TODO on website repo
        # TODO on medium data