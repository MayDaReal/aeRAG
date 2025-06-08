from abc import ABC, abstractmethod

class AbstractSummarizer(ABC):
    @abstractmethod
    def summarize(self, text: str, max_length: int = 150, min_length: int = 50) -> str:
        """Summarize test provided"""
        pass

from transformers import pipeline

class T5Summarizer(AbstractSummarizer):
    def __init__(self, model_name: str = "t5-small"):
        self.pipeline = pipeline("summarization", model=model_name)

    def summarize(self, text: str, max_length: int = 150, min_length: int = 50) -> str:
        # Truncated the text to avoid exceeding the model's capacity
        truncated_text = text[:2000]
        result = self.pipeline(truncated_text, max_length=max_length, min_length=min_length, do_sample=False)
        return result[0]['summary_text']