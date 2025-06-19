"""
llm_manager.py
A factory/manager that returns LLM instances based on user config.
"""

from typing import Optional, Dict
from .llm_interface import ILLM
from .local_llama_llm import LocalLlamaLLM
# Import other future classes here (MistralLLM, DeepSeekLLM, etc.)

class LLMManager:
    """
    A manager to create or retrieve an LLM object for a given "model_type".
    The interface remains consistent (ILLM).
    """

    @staticmethod
    def load_llm(model_type: str, config: Dict[str, str]) -> ILLM:
        """
        Creates and returns an instance of an LLM given a model_type and config.
        
        Args:
            model_type (str): Name of the model type (e.g. 'local-llama', 'mistral-7B', 'L5-small', "deepseek-R1" etc.)
            config (Dict[str, str]): Model-specific configuration or credentials.
        
        Returns:
            ILLM: An instance that implements the ILLM interface.
        """
        if model_type == "local-llama":
            return LocalLlamaLLM(
                model_path=config["model_path"],
                n_ctx=int(config.get("n_ctx", 4096)),
                gpu_layers=int(config.get("gpu_layers", 0)),
            )
        else:
            raise ValueError(f"Unknown model_type: {model_type}")
