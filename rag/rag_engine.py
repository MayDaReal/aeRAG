"""
rag_engine.py
~~~~~~~~~~~~~
High level Retrieval Augmented Generation engine.

The class orchestrates three steps:
1. **Retrieve:** find the top k most relevant chunks through a *FaissIndexManager*.
2. **Assemble context:** concatenate chunk texts (optionally trim to a token budget).
3. **Generate:** feed the context + user query to a generative LLM backend and
   return an answer.

This implementation is *minimal* but production ready: it enforces clean
separation of concerns, graceful fallbacks, and is easy to extend
(summarisation, re ranking, prompt templates, etc.).
"""
from __future__ import annotations

from typing import List, Sequence, Optional
from textwrap import dedent
import time

import numpy as np

from core.faiss_index_manager import FaissIndexManager
from embeddings.embeddings import SentenceTransformerEmbeddingModel
from LLMs.llm_interface import ILLM  # Unified interface (chat, summarise, etc.)
from rag.query_recorder import RAGQueryRecorder

# ---------------------------------------------------------------------------
# Default prompt template
# ---------------------------------------------------------------------------

_DEFAULT_PROMPT = dedent(
    """
    ### System
    You are an expert assistant answering questions about the Archethic codebase. Use the
    provided context strictly — do not invent information outside of it.

    ### Context
    {context}

    ### Question
    {question}

    ### Answer (concise and precise)
    """
)

# ---------------------------------------------------------------------------
# Core engine
# ---------------------------------------------------------------------------

class RAGEngine:
    """Minimal yet robust RAG engine using Faiss for retrieval."""

    def __init__(
        self,
        index_mgr: FaissIndexManager,
        embedding_model: SentenceTransformerEmbeddingModel,
        generative_llm: ILLM,
        *,
        repo: str,
        collection_src: str,
        max_context_tokens: int = 2_000,
        query_recorder: Optional[RAGQueryRecorder] = None
    ) -> None:
        self.index_mgr = index_mgr
        self.embedding_model = embedding_model
        self.llm = generative_llm
        self.repo = repo
        self.collection_src = collection_src
        self.max_context_tokens = max_context_tokens
        self.query_recorder = query_recorder

        # Load (or lazily build) the index on startup.
        self._ensure_index()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def answer_query(self, question: str, *, top_k: int = 5) -> str:
        """Retrieve, assemble context and generate an answer."""
        t0 = time.perf_counter()
        chunks = self._retrieve_chunks(question, top_k=top_k)
        if not chunks:
            return "I could not find relevant context in the knowledge base."

        context_text = self._build_context_text([c["chunk_src"] for c in chunks])
        prompt = _DEFAULT_PROMPT.format(context=context_text, question=question)
        answer = self.llm.chat(prompt)

        elapsed_time = time.perf_counter() - t0
        print(f"[RAG] Total query time: {elapsed_time:.2f} seconds") 

        if self.query_recorder:
            self.query_recorder.record(
                question=question,
                repo=self.repo,
                collections=[self.collection_src],
                chunks=chunks,  # ou context_chunks selon ton pipeline
                answer=answer,
                top_k=top_k,
                duration_s=elapsed_time)

        return answer

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _ensure_index(self) -> None:
        """Load the Faiss index if it exists; otherwise build it on the fly."""
        try:
            self.index_mgr.load_index(self.repo, self.collection_src)
        except FileNotFoundError:
            print("[RAGEngine] No index found building a fresh one …")
            self.index_mgr.build_index(self.repo, [self.collection_src])

    def _retrieve_chunks(self, question: str, *, top_k: int) -> List[dict]:
        """Return top k chunk documents for a user query."""
        D, I, docs, meta_infos = self.index_mgr.query(question, top_k=top_k)
        # metas already contains chunk docs in the same order as I.
        return docs

    def _build_context_text(self, chunk_texts: Sequence[str]) -> str:
        """Concatenate chunk texts while respecting *max_context_tokens*."""
        # Naïve token counting: 1 token ≈ 4 chars (works okay for 7 B LLMs)
        token_budget = self.max_context_tokens
        context_parts: List[str] = []
        current_tokens = 0

        for txt in chunk_texts:
            est_tokens = len(txt) // 4 + 1
            if current_tokens + est_tokens > token_budget:
                break
            context_parts.append(txt)
            current_tokens += est_tokens

        # Separator improves model's understanding of chunk boundaries
        return "\n---\n".join(context_parts)