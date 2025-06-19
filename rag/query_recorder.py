# rag/query_recorder.py

"""
RAGQueryRecorder
~~~~~~~~~~~~~~~~~
Utility to log all RAG queries, chunks used, and model answers.
Results are stored in JSONL (or CSV/minjson in future) for easy comparison.

Typical usage:
    recorder = RAGQueryRecorder("experiments/rag_benchmark.jsonl")
    recorder.record(
        question="Who wrote the last commit?",
        repo="archethic-foundation/archethic-node",
        collections=["commits"],
        chunks=chunks_used,
        answer=llm_answer,
        top_k=5,
        duration_s=2.3,
    )
"""

import json
import os
from datetime import datetime

class RAGQueryRecorder:
    def __init__(self, filepath: str):
        self.filepath = filepath
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

    def record(self, question: str, repo: str, collections: list[str], chunks: list[dict],
               answer: str, top_k: int, duration_s: float, format: str = "jsonl") -> None:
        """
        Record a RAG query and its result to file.
        :param question: Input question.
        :param repo: Repository name.
        :param collections: List of collections involved.
        :param chunks: List of chunk dicts used (must include chunk_id, text, metadata_version, ...).
        :param answer: LLM response.
        :param top_k: Number of retrieved chunks.
        :param duration_s: Duration in seconds.
        :param format: Output format ("jsonl", "csv", ... future-proof).
        """
        log = {
            "timestamp": datetime.utcnow().isoformat(),
            "question": question,
            "repo": repo,
            "collections": collections,
            "top_k": top_k,
            "chunks_used": [
                {
                    "chunk_id": c.get("_id", ""),
                    "text": c.get("chunk_src", ""),
                    "metadata_version": c.get("metadata_version", None)
                }
                for c in chunks
            ],
            "answer": answer,
            "duration_s": duration_s
        }
        if format == "jsonl":
            with open(self.filepath, "a", encoding="utf-8") as f:
                f.write(json.dumps(log, ensure_ascii=False) + "\n")
            # Debug print in console
            print("\n[RAG Recorder] --- RAG Query Log ---")
            print(json.dumps(log, indent=2, ensure_ascii=False))
            print("[RAG Recorder] ----------------------\n")
        else:
            # Placeholder for future formats
            raise NotImplementedError("Only jsonl and json supported for now.")

