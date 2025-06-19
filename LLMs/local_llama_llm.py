# LLMs/local_llama_llm.py
from __future__ import annotations
from typing import List
from llama_cpp import Llama
from .llm_interface import ILLM
import multiprocessing

class LocalLlamaLLM(ILLM):
    """
    Wrapper around llama.cpp (gguf) running locally.
    """

    def __init__(self, model_path: str, n_ctx: int = 4096, gpu_layers: int = 0):
        self.llm = Llama(
        model_path=model_path,
        n_ctx=n_ctx,
        n_gpu_layers=gpu_layers,
        n_threads=multiprocessing.cpu_count(),
        n_batch=512,                            # best pref les performances GPU
        offload_kqv=True,                       # offload K, Q, V tensors (par défaut true, mais on explicite)
        verbose=False
)

    # ------------- High-level API ------------ #

    def chat(self, user_input: str, context: str | None = None) -> str:  # type: ignore
        prompt = context or user_input
        out = self.llm(prompt, max_tokens=512, stop=["</s>"], stream=False)
        return out["choices"][0]["text"].strip()

    def summarize(self, text: str) -> str:  # very naïve use-case
        sys_prompt = "Summarize the following passage concisely:\n\n" + text
        return self.chat(sys_prompt)

    # (Optional) keep stubs for agent/log analysis
    def run_agent(self, instructions: str) -> str:
        return self.chat(instructions)

    def analyze_logs(self, logs: List[str]) -> str:  # type: ignore
        joined = "\n".join(logs)
        return self.summarize(joined)
