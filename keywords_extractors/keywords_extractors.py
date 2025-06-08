from typing import List
from abc import ABC, abstractmethod

class AbstractKeywordExtractor(ABC):
    @abstractmethod
    def extract(self, text: str, num_keywords: int = 10) -> List[str]:
        """Extract a list of keywords from the text provided."""
        pass

import yake

class YakeKeywordExtractor(AbstractKeywordExtractor):
    def __init__(self, language: str = "en"):
        self.extractor = yake.KeywordExtractor(lan=language)

    def extract(self, text: str, num_keywords: int = 10) -> List[str]:
        keywords = self.extractor.extract_keywords(text)
        return [kw[0] for kw in keywords][:num_keywords]