# scripts/count_embeddings.py
from core.database_manager import DatabaseManager

db = DatabaseManager("mongodb://localhost:27017", "archethic_github_data")
count = db.db.chunks.count_documents({"embedding": {"$exists": True}})
print(f"{count} chunks already contain embeddings")
