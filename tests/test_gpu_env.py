"""
test_gpu_env.py
~~~~~~~~~~~~~~~~

Diagnostic complet de l'environnement GPU pour vérifier :
- torch + CUDA opérationnel
- SentenceTransformer sur GPU
- llama.cpp (mistral-7b) comparé entre CPU et GPU (temps d'inférence)

Usage :
$ python test_gpu_env.py
"""

import time
import torch
from sentence_transformers import SentenceTransformer
from LLMs.local_llama_llm import LocalLlamaLLM

from pathlib import Path

# Resolve absolute path to the root of the project
PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = PROJECT_ROOT / "models" / "mistral-7b-instruct-v0.2.Q4_K_M.gguf"

# -------------------------------
# Test Torch GPU availability
# -------------------------------
def test_torch_gpu():
    print("\n--- [ Torch + CUDA Check ] ---")
    print("Torch version:", torch.__version__)
    print("CUDA available:", torch.cuda.is_available())
    cuda_version = getattr(torch.version, "cuda", "Not found")
    print("CUDA version:", cuda_version)
    if torch.cuda.is_available():
        print("GPU detected:", torch.cuda.get_device_name(0))
    else:
        print("No GPU available for torch.")


# -------------------------------
# Test SentenceTransformer with GPU
# -------------------------------
def test_sentence_transformer():
    print("\n--- [ SentenceTransformer Test ] ---")
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print("Loading model on:", device)
    model = SentenceTransformer("all-MiniLM-L6-v2", device=device)

    t0 = time.time()
    emb = model.encode("This is a GPU test.", show_progress_bar=False)
    duration = time.time() - t0

    print("Embedding shape:", len(emb))
    print(f"Encoding took {duration:.3f} seconds on {device.upper()}")


# -------------------------------
# Compare LLM CPU vs GPU inference
# -------------------------------
def test_llama_cpu_vs_gpu():
    print("\n--- [ Mistral LLM: CPU vs GPU Test ] ---")
    prompt = "What is Archethic blockchain and what are its main innovations?"
    model_path=str(MODEL_PATH)

    print("\n[CPU only mode]")
    llm_cpu = LocalLlamaLLM(
        model_path=model_path,
        n_ctx=4096,
        gpu_layers=0
    )
    t0 = time.time()
    out_cpu = llm_cpu.chat(prompt)
    dt_cpu = time.time() - t0
    print(f"CPU inference time: {dt_cpu:.2f}s\nResponse: {out_cpu[:120]}...")

    print("\n[GPU accelerated mode (60 layers)]")
    llm_gpu = LocalLlamaLLM(
        model_path=model_path,
        n_ctx=4096,
        gpu_layers=60
    )
    t1 = time.time()
    out_gpu = llm_gpu.chat(prompt)
    dt_gpu = time.time() - t1
    print(f"GPU inference time: {dt_gpu:.2f}s\nResponse: {out_gpu[:120]}...")

    speedup = dt_cpu / dt_gpu if dt_gpu > 0 else 0
    print(f"\n✅ Speedup: {speedup:.2f}x faster on GPU")


if __name__ == "__main__":
    test_torch_gpu()
    test_sentence_transformer()
    test_llama_cpu_vs_gpu()
