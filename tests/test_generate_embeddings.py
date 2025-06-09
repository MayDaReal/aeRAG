from core.database_manager import DatabaseManager
from core.file_storage_manager import FileStorageManager
from metadata.metadata_manager import MetadataManager
from bson.objectid import ObjectId

def test_embedding_generation_commits():
    """
    Test that inserting a commit triggers:
    - automatic metadata creation,
    - chunk generation,
    - embedding generation.
    """
    db = DatabaseManager("mongodb://localhost:27017", "archethic_github_test_data")
    file_storage = FileStorageManager(base_storage_path="local_storage", base_url="http://localhost:8000")
    manager = MetadataManager(db_manager=db, file_storage=file_storage)

    repo = "archethic-foundation/archethic-node"
    collection = "commits"
    dummy_commit_id = ObjectId()

    # Insert a dummy commit with required structure
    db.db.commits.insert_one({
        "_id": dummy_commit_id,
        "repo": repo,
        "collection_src": collection,
        "commit_sha": "testsha123",
        "files": [
            {
                "filename": "demo.py",
                "status": "modified",
                "patch": "def test_fn():\n    return 42"
            }
        ],
        "files_changed": ["demo.py"]
    })

    # Act: run metadata and embedding generation
    manager.update_metadata_for_specific_data(repo, [{"collection_src": collection}])

    # Lookup metadata_id injected into the updated commit
    updated_commit = db.db.commits.find_one({"_id": dummy_commit_id})
    assert updated_commit and "metadata_id" in updated_commit, "metadata_id not injected in commit"
    metadata_id = updated_commit["metadata_id"]

    # Check that a chunk with embedding was created
    chunk = db.db.chunks.find_one({"metadata_id": metadata_id})
    assert chunk is not None, "Chunk not found"
    assert "embedding" in chunk, "Embedding missing"
    assert isinstance(chunk["embedding"], list)
    assert len(chunk["embedding"]) > 0

    # Cleanup: remove test documents
    db.db.commits.delete_one({"_id": dummy_commit_id})
    db.db.metadata.delete_one({"_id": metadata_id})
    db.db.chunks.delete_many({"metadata_id": metadata_id})
    db.db.metadata_chunks.delete_many({"metadata_id": metadata_id})

