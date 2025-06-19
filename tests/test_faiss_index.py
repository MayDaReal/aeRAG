import os
import shutil
from pathlib import Path

import pytest
from bson import ObjectId

from core.database_manager import DatabaseManager
from core.faiss_index_manager import FaissIndexManager
from embeddings.embeddings import SentenceTransformerEmbeddingModel

@pytest.mark.integration
def test_faiss_index_creation_and_query():
    """
    Construit un petit index FAISS, vérifie qu’une requête fonctionne,
    puis nettoie STRICTEMENT ce qui a été ajouté pendant le test.
    """
    # ------------------------------------------------------------------ Préparation
    db = DatabaseManager("mongodb://localhost:27017",
                         "archethic_github_test_data")
    model = SentenceTransformerEmbeddingModel()
    fim = FaissIndexManager(db, embedding_model=model, index_root="local_storage/test_indexes")

    repo       = "archethic-foundation/archethic-node"
    collection = "commits"

    chunk_coll = db.db.chunks
    meta_coll  = db.db.metadata

    # Store what we insert so that we can remove it precisely at the end of the test.
    inserted_chunk_ids: list[str] = []
    inserted_meta_ids:  list[str] = []

    try:
        # ------------------------------------------------------ 1. Insert (5 couples)
        for i in range(5):
            txt = f"function test_{i}() {{ return {i}; }}"
            emb = model.encode(txt)               # deterministic vector

            chunk_id = str(ObjectId())
            meta_id  = f"test_meta_{chunk_id}"    # prefix “test_” -> no collision

            # 1-A  metadata
            meta_coll.insert_one({
                "_id": meta_id,
                "repo": repo,
                "collection_src": collection,
                "metadata_version": 0,
                "chunk_ids": [chunk_id],
                "test_tag": True                  # tracking tag
            })
            inserted_meta_ids.append(meta_id)

            # 1-B  chunk
            chunk_coll.insert_one({
                "_id": chunk_id,
                "repo": repo,
                "collection_src": collection,
                "chunk_src": txt,
                "embedding": emb,
                "metadata_id": meta_id,
                "test_tag": True                  # tracking tag
            })
            inserted_chunk_ids.append(chunk_id)

        # ------------------------------------------------------ 2. Build index
        fim.build_index(repo, [collection], force=True)

        # ------------------------------------------------------ 3. Query
        fim.load_index(repo, collection)
        D, I, docs, meta_infos = fim.query("function test_2", top_k=3)

        assert len(docs) >= 1
        assert any("test_2" in d["chunk_src"] for d in docs)

    finally:
        # ------------------------------------------------------ 4. Clean chunk and metadata added for testing only
        if inserted_chunk_ids:
            chunk_coll.delete_many({"_id": {"$in": inserted_chunk_ids},
                                    "test_tag": True})
        if inserted_meta_ids:
            meta_coll.delete_many({"_id": {"$in": inserted_meta_ids},
                                   "test_tag": True})

        db.close_connection()