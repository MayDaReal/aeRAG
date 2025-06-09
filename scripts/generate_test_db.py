"""
Generates a lightweight MongoDB test database ('archethic_github_test_data') 
by sampling a few documents from each relevant collection in the main DB.
"""

from pymongo import MongoClient

# Configuration
MONGO_URI = "mongodb://localhost:27017"
SOURCE_DB = "archethic_github_data"
TARGET_DB = "archethic_github_test_data"
SAMPLE_SIZE = 10

# Main entity collections
COLLECTIONS_DIRECT = [
    "repositories", "commits", "pull_requests", "issues",
    "files", "main_files", "last_release_files", "contributors"
]

# Secondary collections with foreign key references
LINKED_COLLECTIONS = [
    "pull_requests_comments", "issues_comments", "metadata", "chunks", "metadata_chunks"
]

# Init clients
client = MongoClient(MONGO_URI)
src = client[SOURCE_DB]
dst = client[TARGET_DB]

def reset_target(coll_name):
    """Wipe the destination collection before inserting."""
    dst[coll_name].delete_many({})

def insert_sample(coll_name):
    """Copy a limited sample from source to target."""
    print(f"⏩ Exporting {coll_name}")
    docs = list(src[coll_name].find().limit(SAMPLE_SIZE))
    if docs:
        reset_target(coll_name)
        dst[coll_name].insert_many(docs)
    return docs

def insert_linked(coll_name, field_name, ids):
    """Copy linked documents by foreign key."""
    print(f"⏩ Exporting {coll_name} (linked by {field_name})")
    docs = list(src[coll_name].find({field_name: {"$in": list(ids)}}))
    if docs:
        reset_target(coll_name)
        dst[coll_name].insert_many(docs)
    return docs

# Step 1: Export primary collections and track IDs
meta_ids = set()
chunk_meta_ids = set()
pr_ids = set()
issue_ids = set()

for coll in COLLECTIONS_DIRECT:
    docs = insert_sample(coll)
    for doc in docs:
        if coll == "pull_requests":
            pr_ids.add(doc["_id"])
        elif coll == "issues":
            issue_ids.add(doc["_id"])
        if "metadata_id" in doc:
            meta_ids.add(doc["metadata_id"])

# Step 2: Export comments and metadata
insert_linked("pull_requests_comments", "pr_id", pr_ids)
insert_linked("issues_comments", "issue_id", issue_ids)
metadata_docs = insert_linked("metadata", "_id", meta_ids)

# Step 3: Export chunks related to those metadata
if metadata_docs:
    for doc in metadata_docs:
        meta_ids.add(doc["_id"])  # ensure all metadata IDs are tracked
insert_linked("chunks", "metadata_id", meta_ids)

# Step 4: Export metadata_chunks table
insert_linked("metadata_chunks", "metadata_id", meta_ids)

print("✅ Test database 'archethic_github_test_data' successfully created.")
