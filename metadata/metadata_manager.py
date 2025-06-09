"""
metadata_manager.py
Handles the orchestration of metadata extraction, generation, and storage.
"""

from typing import List, Dict
from core.database_manager import DatabaseManager
from core.file_storage_manager import FileStorageManager
from metadata.metadata_generator import MetadataGenerator
from embeddings.embeddings import SentenceTransformerEmbeddingModel
from summarizers.summarizers import T5Summarizer
from keywords_extractors.keywords_extractors import YakeKeywordExtractor

class MetadataManager:
    """
    High-level controller for metadata updates across repositories.
    """

    def __init__(self, db_manager: DatabaseManager, file_storage: FileStorageManager):
        """
        Initializes MetadataManager with database and file storage access.

        Args:
            db_manager (DatabaseManager): Handles MongoDB interactions.
            file_storage (FileStorageManager): Manages file retrieval/storage.
        """
        self.db_manager = db_manager
        embedding_model = SentenceTransformerEmbeddingModel()
        summarizer = T5Summarizer()
        keywords_extractor = YakeKeywordExtractor()
        self.metadata_generator = MetadataGenerator(db_manager, file_storage, embedding_model, summarizer, keywords_extractor)

    def update_metadata_multiple_repos_specific_data(self, repos: List[str], selected_data: List[str]):
        """
        Updates metadata for all elements in a given repository.

        Args:
            repos (List[str]): List of gitHub repositories to update.
            selected_data (List[str]): Collections to update (e.g., ['files', 'main_files', 'last_release_files', 'commits', 'pull_requests', 'issues']).
        """
        formatted_data = [{"collection_src": c} for c in selected_data]
        for repo in repos:
            self.update_metadata_for_specific_data(repo, formatted_data)

    def update_metadata_for_specific_data(self, repo: str, selected_data: List[Dict]):
        """
        Updates metadata for all elements in a given repository.

        Args:
            repo (str): GitHub repository name.
            collections (List[str]): Collections to update (e.g., ['files', 'commits', 'issues']).
        """
        
        for entry in selected_data:
            collection_name = entry["collection_src"]
            print(f"🔄 Updating metadata for '{repo}', collection '{collection_name}'...")
            self.metadata_generator.update_metadata_for_collection(
                repo,
                self.db_manager.db[collection_name],
                collection_name
            )
            print(f"✅ Metadata update completed for {collection_name} in {repo}.")
