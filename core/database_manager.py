"""
database_manager.py
Manages MongoDB connection and allows direct access to the db object.
Indexes can be created here if needed.
"""

import pymongo
from typing import List

class DatabaseManager:
    """Provides direct access to MongoDB database and optionally creates indexes."""

    def __init__(self, mongo_uri: str, db_name: str, create_indexes: bool = True):
        """
        Initializes the MongoDB client and optionally creates indexes.
        
        Args:
            mongo_uri (str): MongoDB connection URI.
            db_name (str): Name of the database to use.
            create_indexes (bool): If True, call self._create_indexes() at init.
        """
        self._client = pymongo.MongoClient(mongo_uri)
        self._db = self._client[db_name]

        if create_indexes:
            self._create_indexes()

    @property
    def db(self):
        """
        Returns the pymongo Database instance so other code can perform 
        any operations they need (insert, update, etc.)
        """
        return self._db

    def _create_indexes(self) -> None:
        """
        Define indexes for all collections and create them only if they do not already exist.
        Optimized for query performance and data retrieval.
        """
        indexes = {
            "commits": [
                ("repo", pymongo.ASCENDING),
                ("date", pymongo.DESCENDING)
            ],
            "repositories": [
                ("_id", pymongo.ASCENDING)  # Unique repository identifier
            ],
            "contributors": [
                ("email", pymongo.ASCENDING, {"unique": True})
            ],
            "files": [
                ("commit_id", pymongo.ASCENDING),
                ("repo", pymongo.ASCENDING)
            ],
            "metadata": [
                ("file_id", pymongo.ASCENDING),
                ("file_source", pymongo.ASCENDING)
            ],
            "metadata_chunks": [
                (("metadata_id", pymongo.ASCENDING), {}),
                (("file_id", pymongo.ASCENDING), {}),
                (("chunk_index", pymongo.ASCENDING), {}),
                (("embedding", pymongo.ASCENDING), {"sparse": True})
            ],
            "lfs_pointers": [
                ("file_id", pymongo.ASCENDING)
            ],
            "issues": [
                (("repo", pymongo.ASCENDING), {}),
                (("updated_at", pymongo.DESCENDING), {}),
                (("state", pymongo.ASCENDING), {}),  # Optimized filtering by state
                (("labels", pymongo.ASCENDING), {}),  # Allows searching by labels
                (("repo", pymongo.ASCENDING), ("state", pymongo.ASCENDING)),  # Optimisation pour filtrage rapide
            ],
            "pull_requests": [
                (("repo", pymongo.ASCENDING), {}),
                (("updated_at", pymongo.DESCENDING), {}),
                (("state", pymongo.ASCENDING), {}),  # Optimized filtering by state
                (("labels", pymongo.ASCENDING), {}),  # Allows searching by labels
                (("repo", pymongo.ASCENDING), ("state", pymongo.ASCENDING)),  # Index composite pour filtrer PRs ouvertes/fermées
            ],
            "main_files": [
                (("repo", pymongo.ASCENDING), {}),
                (("filename", pymongo.ASCENDING), {}),
                (("commit_id", pymongo.DESCENDING), {}),  # Track the latest version
                (("metadata_id", pymongo.ASCENDING), {}),  # Link to metadata
            ],
            "last_release_files": [
                (("repo", pymongo.ASCENDING), {}),
                (("filename", pymongo.ASCENDING), {}),
                (("commit_id", pymongo.DESCENDING), {}),  # Track the latest release version
                (("metadata_id", pymongo.ASCENDING), {}),  # Link to metadata
            ],
            "issues_comments": [
            ("repo", pymongo.ASCENDING),
            ("issue_id", pymongo.ASCENDING)
            ],
            "pull_requests_comments": [
                ("repo", pymongo.ASCENDING),
                ("pr_id", pymongo.ASCENDING)
            ]
            # TODO In near futur, add new collection to manage user feedback and logs of the RAG engine
        }

        for collection, index_list in indexes.items():
            for index in index_list:
                keys = index[:-1] if isinstance(index[-1], dict) else index
                keys = [keys] if isinstance(keys[0], str) else keys  # Ensure it's a list of tuples
                options = index[-1] if isinstance(index[-1], dict) else {}
                self.db[collection].create_index(keys, **options)

    def list_collections(self) -> List[str]:
        """
        Lists all collections in the database.
        
        Returns:
            List[str]: A list of collection names.
        """
        return self.db.list_collection_names()

    def close_connection(self) -> None:
        """Close the MongoDB client connection."""
        self._client.close()
