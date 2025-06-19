"""
faiss_index_manager.py
Utility class to build, persist and query a Faiss index from the
`chunks` collection stored in MongoDB.

Usage (quick example) :

    from core.database_manager import DatabaseManager
    from core.faiss_index_manager import FaissIndexManager

    db   = DatabaseManager("mongodb://localhost:27017",
                           "archethic_github_test_data")
    fim  = FaissIndexManager(db)

    # Build & save index for one repo / collection
    fim.build_index(
        repo="archethic-foundation/archethic-node",
        collection_src="commits"
    )

    # Later ...
    fim.load_index("archethic-foundation/archethic-node", "commits")
    D, I, docs, meta_infos = fim.query("how to deploy multisig ?", top_k=3)
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Any

import numpy as np
import faiss  # type: ignore

from core.database_manager import DatabaseManager
from embeddings.embeddings import SentenceTransformerEmbeddingModel

class FaissIndexManager:
    """Handles Faiss index creation, persistence, and similarity queries."""

    def __init__(
        self,
        db: DatabaseManager,
        embedding_model: SentenceTransformerEmbeddingModel | None = None,
        index_root: str | Path = "local_storage/indexes",
    ):
        """
        Initialize the index manager with MongoDB access and an embedding model.

        Args:
            db (DatabaseManager): Connection to MongoDB.
            embedding_model (SentenceTransformerEmbeddingModel, optional): Model to embed queries.
            index_root (str, optional):  base directory used to store indexes.
        """
        self.db = db
        self.embedding_model = embedding_model or SentenceTransformerEmbeddingModel()
        self.index_root = Path(index_root)
        self.index: faiss.Index | None = None
        self.id_map: Dict[int, str] = {}  # Faiss idx -> chunk ObjectId

    def _paths(self, repo: str, index_name: str) -> tuple[Path, Path]:
        """
        Compute the path for the FAISS .faiss and the mapping .json files.
        - index_name: e.g. 'commits', 'main_files', 'global'
        """
        safe_repo = repo.replace("/", "_")
        base = self.index_root / safe_repo / safe_repo
        return (
            base / f"{index_name}.faiss",
            base / f"{index_name}_mapping.json",
        )

    def build_index(
    self, repo: str, collections: list[str] | None = None,
    force: bool = False, global_index: bool = False
    ) -> None:
        """
        Build or rebuild a Faiss index for all chunks with embeddings in a repo,
        for one or several collections (global_index=True = fusion multi-collections).
        """
        if global_index:
            index_name = "global"
        elif collections and len(collections) == 1:
            index_name = collections[0]
        else:
            raise ValueError("Specify one collection for legacy mode, or global_index=True for multi.")

        index_path, mapping_path = self._paths(repo, index_name)
        if not force and index_path.exists() and mapping_path.exists():
            print(f"[FaissIndex] Index already exists for {index_name} – use force=True to overwrite")
            return

        # 1. Find relevant metadata_id
        meta_query: dict[str, Any] = {"repo": repo}
        if global_index and collections:
            meta_query["collection_src"] = {"$in": collections}
        elif not global_index:
            meta_query["collection_src"] = index_name

        print(f"[FaissIndex][DEBUG] Querying metadata with: {meta_query}")
        meta_cursor = self.db.db.metadata.find(meta_query, {"_id": 1})
        metadata_ids = [m["_id"] for m in meta_cursor]
        print(f"[FaissIndex][DEBUG] Found {len(metadata_ids)} metadata entries.")

        if not metadata_ids:
            print("[FaissIndex] No metadata found – index not built.")
            return

        # 2. Find the chunks corresponding to the metadata_id
        chunk_query = {
            "metadata_id": {"$in": metadata_ids},
            "embedding": {"$exists": True}
        }
        print(f"[FaissIndex][DEBUG] Querying chunks with: {chunk_query}")
        projection = {"_id": 1, "embedding": 1, "metadata_id": 1}
        chunks_found = self.db.db.chunks.find(chunk_query, projection)

        vectors, ids, meta_info = [], [], []
        for doc in chunks_found:
            vec = doc["embedding"]
            if isinstance(vec, list) and vec:
                vectors.append(vec)
                ids.append(str(doc["_id"]))
                # Retrieve collection_src and metadata_version via metadata_id
                meta_id = doc["metadata_id"]
                meta = self.db.db.metadata.find_one({"_id": meta_id}, {"collection_src": 1, "metadata_version": 1})
                meta_info.append({
                    "collection_src": meta.get("collection_src", "") if meta else "",
                    "metadata_version": meta.get("metadata_version", None) if meta else None
                })

        print(f"[FaissIndex][DEBUG] Found {len(ids)} embedding vectors for index '{index_name}'.")
        if not vectors:
            print("[FaissIndex] No usable embeddings found – index not built.")
            return

        mat = np.asarray(vectors, dtype=np.float32)
        dim = mat.shape[1]
        self.index = faiss.IndexFlatL2(dim)
        self.index.add(mat)  # type: ignore

        self.id_map = {i: oid for i, oid in enumerate(ids)}
        self.meta_map = {i: meta for i, meta in enumerate(meta_info)}

        index_path.parent.mkdir(parents=True, exist_ok=True)
        faiss.write_index(self.index, str(index_path))
        with open(mapping_path, "w", encoding="utf-8") as f:
            json.dump({
                "id_map": self.id_map,
                "meta_map": self.meta_map
            }, f)
        self._current_mapping_path = mapping_path
        print(f"[FaissIndex] Built & saved index ({index_name}) – {len(ids)} vectors.")



    def load_index(self, repo: str, index_name: str) -> None:
        """
        Load a previously-saved index and mapping (for 'commits', 'global', etc).
        """
        index_path, mapping_path = self._paths(repo, index_name)
        if not index_path.exists() or not mapping_path.exists():
            raise FileNotFoundError("Index or mapping file not found.")

        self.index = faiss.read_index(str(index_path))
        self._current_mapping_path = mapping_path 

        mapping = self._load_mapping()
        self.id_map = mapping["id_map"]
        self.meta_map = mapping.get("meta_map", {})

    def query(self, query_text: str, top_k: int = 5) -> tuple[np.ndarray, np.ndarray, list[dict], list[dict]]:
        """
        Perform a similarity search. Returns distances, indices, chunk docs, meta-info for each.
        """
        if self.index is None:
            raise RuntimeError("Faiss index not loaded. Call load_index() or build_index() first.")

        query_vec = np.asarray([self.embedding_model.encode(query_text)], dtype=np.float32)
        D, I = self.index.search(query_vec, top_k) # type: ignore  # faiss types are not well defined

        # Retrieves _id and meta-info for each returned chunk
        mapping = self._load_mapping()  # reads the associated .json file (see below)
        id_map = mapping["id_map"]
        meta_map = mapping.get("meta_map", {})

        chunk_ids = [id_map[str(idx)] for idx in I[0] if str(idx) in id_map]
        chunk_metas = [meta_map.get(str(idx), {}) for idx in I[0]]

        # Search for chunks in Mongo
        docs = list(self.db.db.chunks.find({"_id": {"$in": chunk_ids}}))

        return D, I, docs, chunk_metas

    def _load_mapping(self):
        """
        Reload the mapping file currently in use (called by query()).
        """
        with open(self._current_mapping_path, "r", encoding="utf-8") as f:
            return json.load(f)
