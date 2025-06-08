"""
llm_interface.py
Defines a unified interface for different LLM implementations.
"""

from abc import ABC, abstractmethod
from typing import Optional, List

class ILLM(ABC):
    """
    A unified interface for various LLM backends: local, API-based, etc.
    """

    @abstractmethod
    def chat(self, user_input: str, context: Optional[str] = None) -> str:
        """
        Returns a response to the user's input in a chat-like format.
        Optionally uses the provided context for better answers.
        """
        pass

    @abstractmethod
    def summarize(self, text: str) -> str:
        """
        Generates a summary of the given text.
        """
        pass

    @abstractmethod
    def run_agent(self, instructions: str) -> str:
        """
        Runs an AI "agent" that can perform multi-step reasoning or actions.
        The implementation depends on the model's capabilities.
        """
        pass

    @abstractmethod
    def analyze_logs(self, logs: List[str]) -> str:
        """
        Analyzes a list of log strings and proposes improvements or insights.
        """
        pass
