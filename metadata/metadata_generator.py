"""
metadata_generator.py
Generates metadata for files: chunking, embeddings, summarization, etc.
"""

from typing import Dict, Any
from pymongo.collection import Collection
from core.database_manager import DatabaseManager
from core.file_storage_manager import FileStorageManager
from embeddings.embeddings import AbstractEmbeddingModel
from summarizers.summarizers import AbstractSummarizer
from metadata.metadata_utils import compute_file_hash_md5, detect_file_type, detect_programming_language, detect_natural_language
from keywords_extractors.keywords_extractors import AbstractKeywordExtractor
from chunks.chunking_strategy_factory import ChunkingStrategyFactory
from chunks.abstract_chunking_strategy import AbstractChunkingStrategy
import datetime

class MetadataGenerator:
    """Generates or updates metadata (chunks, embeddings, etc.) for files in the database."""

    def __init__(self, db_manager : DatabaseManager, file_storage_manager : FileStorageManager,
                 embedding_model: AbstractEmbeddingModel,
                 summarizer: AbstractSummarizer,
                 keyword_extractor: AbstractKeywordExtractor):
        """
        Args:
            db_manager (DatabaseManager): Provides access to the database.
            file_storage_manager (FileStorageManager): For retrieving file content.
            embedding_model (AbstractEmbeddingModel): Instance implementing the embedding interface.
            summarizer (AbstractSummarizer): Instance implementing the summarization interface.
            keyword_extractor (AbstractKeywordExtractor): Instance implementing the keyword extraction interface.
        """
        self.db_manager = db_manager
        self.file_storage = file_storage_manager
        self.embedding_model = embedding_model
        self.summarizer = summarizer
        self.keyword_extractor = keyword_extractor

    def extract_text_from_document(self, collection_item: Dict[str, Any], collection: str) -> str:
        """
        Extracts relevant textual content from a document based on its collection.

        Args:
            data (Dict): Document information from the database.
            collection (str): The MongoDB collection of the document.

        Returns:
            str: Extracted text for metadata processing.
        """
        # Files: Retrieve text from external storage or fallback to patch
        if collection in ["files", "main_files", "last_release_files"]:
            return self._extract_text_from_files(collection_item)
        # Commits: Combine commit message, patch, and list of impacted files
        elif collection == "commits":
            return self._extract_text_from_commits(collection_item)
        # Issues: Retrieve text from title and body
        elif collection == "issues":
            return self._extract_text_from_issues(collection_item)
        # Pull Requests: Retrieve text from title and body or external storage
        elif collection == "pull_requests":
            return self._extract_text_from_pull_requests(collection_item)

        return ""

    def update_metadata_for_collection(self, repo : str, db_collection: Collection, collection_src: str) -> None:
        """
        Updates metadata for all documents in a given collection, filtering by repo if needed.
        
        Args:
            repo (str): The repository name to filter on.
            db_collection (Dict): The MongoDB collection name (ex. files, main_files, last_release_files, commits, pull_requests, issues).
            collection_src (str): The name of the collection source
        """

        collection_items = db_collection.find({"repo": repo})
        for collection_item in collection_items:
            text = self.extract_text_from_document(collection_item, collection_src)
            if text:
                self._generate_metadata_for_document(collection_item, collection_src, text)

    def _compute_metadata_id(self, repo: str, collection_src: str, collection_id: str) -> str:
        """
        Builds the metadata identifier in the format: meta_{repo}_{collection_src}_{collection_id}.

        Args:
            repo (str): Repository name.
            collection_src (str): Source collection name.
            collection_id (str): Document identifier from the source collection.

        Returns:
            str: Computed metadata identifier.
        """
        return f"meta_{repo}_{collection_src}_{collection_id}"

    def _extract_text_from_files(self, collection_item: Dict[str, Any]) -> str:
        """
        Extracts relevant textual content from a document based on files, main_files or last_release_files collections.

        Args:
            collection_item (Dict[str, Any]): Document information from the database.

        Returns:
            str: Extracted text for metadata processing.
        """
        file_url = collection_item.get("external_url")
        if file_url:
            return self.file_storage.fetch_file_content(file_url) or ""
        return collection_item.get("patch", "").strip()  # Fallback if no external file is available

    def _extract_text_from_commits(self, collection_item: Dict[str, Any]) -> str:
        """
        Extracts relevant textual content from a document based on commits collection.

        Args:
            collection_item (DicDict[str, Any]t): Document information from the database.

        Returns:
            str: Extracted text for metadata processing.
        """
        # TODO: In future, use LLM to generate a better summary of commit changes.
        commit_message = collection_item.get("message", "").strip()
        files_changed = "\n".join(collection_item.get("files_changed", []))  # List impacted files
        return f"Commit Message:\n{commit_message}\n\nFiles Changed:\n{files_changed}".strip()
    
    def _extract_text_from_issues(self, collection_item: Dict[str, Any]) -> str:
        """
        Extracts relevant textual content from a document based on issues collection.

        Args:
            collection_item (Dict): Document information from the database.

        Returns:
            str: Extracted text for metadata processing.
        """
        issue_title = collection_item.get("title", "").strip()
        issue_body = collection_item.get("body", "").strip()
        
        # Fetch comments if available
        comments = self.db_manager.db.issues_comments.find({"issue_id": collection_item["_id"]})
        comments_text = "\n".join([c["comment_body"] for c in comments])
        return f"{issue_title}\n\n{issue_body}\n\nComments:\n{comments_text}".strip()

    def _extract_text_from_pull_requests(self, collection_item: Dict) -> str:
        """
        Extracts relevant textual content from a document based on pull_requests collection.

        Args:
            collection_item (Dict): Document information from the database.

        Returns:
            str: Extracted text for metadata processing.
        """
        pr_title = collection_item.get("title", "").strip()
        pr_body_url = collection_item.get("body_url")
        pr_body = self.file_storage.fetch_file_content(pr_body_url) if pr_body_url else collection_item.get("body", "").strip()

        # Fetch comments if available
        comments = self.db_manager.db.pull_requests_comments.find({"pr_id": collection_item["_id"]})
        comments_text = "\n".join([c["comment_body"] for c in comments])

        return f"{pr_title}\n\n{pr_body}\n\nComments:\n{comments_text}".strip()

    def _generate_metadata_for_document(self, collection_item: Dict[str, Any], collection_src: str, content : str) -> None:
        """
        Generates metadata for a single document and updates the corresponding chunks.
        Handles both new metadata creation and update of existing metadata.
        Also updates the metadata_id field in related collections.

        Args:
            collection_item (Dict[str, Any]): Document information from the database.
            collection_src (str): Source collection name.
            content (str): The text content extracted from the document.
        """

        if not content:
            return
        
        collection_id = str(collection_item.get("_id"))
        metadata_id = self._compute_metadata_id(collection_item["repo"], collection_src, collection_id)
        file_hash =  compute_file_hash_md5(content)

        # Check if metadata already exists
        existing_metadata = self.db_manager.db.metadata.find_one({"_id": metadata_id})
        current_metadata_version = 0  # Define current metadata version

        if existing_metadata is None:
            # New metadata document to be created.
            metadata_obj = self._create_metadata(collection_item, metadata_id, collection_src, collection_id, file_hash, content, current_metadata_version)
        else:
            # Update is needed if the file_hash differs or if metadata_version is outdated.
            metadata_obj = self._update_existing_metadata(existing_metadata, collection_item, file_hash, content, current_metadata_version)

        if metadata_obj is None:
            # No update
            return
        
        # Log metadata details before update to help trace potential size issues.
        num_chunks = len(metadata_obj.get("chunk_ids", []))
        content_length = len(content)
        print(f"[DEBUG] Updating metadata with id: {metadata_id}")
        print(f"[DEBUG] Repo: {collection_item['repo']}, Collection: {collection_src}, Document _id: {collection_id}")
        print(f"[DEBUG] File hash: {file_hash}, Content length: {content_length}, Number of chunks: {num_chunks}")

        # Update or insert the metadata document.
        self.db_manager.db.metadata.update_one({"_id": metadata_id}, {"$set": metadata_obj}, upsert=True)
        print(f"✅ Metadata {metadata_id} updated")

        # Update the source document with the metadata_id.
        self.db_manager.db[collection_src].update_one({"_id": collection_item["_id"]}, {"$set": {"metadata_id": metadata_id}})
        print(f"✅ collection {collection_src} with id {collection_id} is linked to metadata_id {metadata_id}")

    def _create_metadata(self, collection_item, metadata_id, collection_src, collection_id, file_hash, content, current_metadata_version):
        
        created_at = datetime.datetime.now(datetime.timezone.utc)
        has_filename = collection_src in ["files", "main_files", "last_release_files"]
        is_binary = False
        ext = "txt"
        file_type="doc"
        if has_filename:
            file_type = detect_file_type(collection_item["filename"])
            is_binary = file_type == "binary"
            ext = collection_item["filename"].split(".")[-1].lower()
        
        if is_binary:
            # TODO Currently the system doesn't handle binary files
            return None

        language = self._detect_language(collection_item, has_filename, content)
        settings = {
            "extension": ext,
            "language": language,
            "min_chunk_size": 300,
            "chunk_size": 1000,
            "overlap": 200
        }
        strategy = ChunkingStrategyFactory.get_strategy(file_type, settings)
        chunks_ids = self._create_chunks(metadata_id, strategy, content)
        tags = self.keyword_extractor.extract(content)
        description = ""
        if not is_binary and current_metadata_version != 0:
            # TODO not use description currently and try to accelerate process to create chunk and embeddings
            # TODO think how description can be use to improve the RAG system
            # that mean the content contains something that can be understood by the model
            description = self.summarizer.summarize(content)

        # Store the content of chunk in local_storage and get url to this content
        external_url = self.file_storage.store_file_content(content=content, repo=collection_item["repo"], reference_id="meta", filename=metadata_id)

        metadata_obj = {
                "_id": metadata_id,
                "repo": collection_item["repo"],
                "collection_src": collection_src,
                "collection_id": collection_id,
                "language": language,
                "description": description,
                "tags": tags,
                "chunk_ids": chunks_ids,
                "created_at": created_at,
                "updated_at": created_at,
                "source_url": external_url,
                "metadata_version": current_metadata_version,
                "file_hash": file_hash
            }
        
        return metadata_obj

    def _detect_language(self, collection_item, has_filename=False, content=None):
        language = "undefined"
        if (has_filename):
            file_type = detect_file_type(collection_item["filename"])
            ext = collection_item["filename"].split(".")[-1].lower()
            if file_type == "code":
                language = detect_programming_language(ext)
            elif file_type == "binary":
                language = "binary"
            else:
                language = detect_natural_language(content)
        return language

    def _update_existing_metadata(self, existing_metadata, collection_item, file_hash, content, current_metadata_version):
        previous_metadata_version = existing_metadata.get("metadata_version", 1)
        if (existing_metadata.get("file_hash") != file_hash or previous_metadata_version != current_metadata_version):
            # Remove obsolete chunks
            self.db_manager.db.chunks.delete_many({"metadata_id": existing_metadata.get("_id")})

            return self._create_metadata(collection_item=collection_item,
                                        metadata_id=existing_metadata.get("_id"),
                                        collection_src=existing_metadata.get("collection_src"),
                                        collection_id=existing_metadata.get("collection_id"),
                                        file_hash=file_hash,
                                        content=content,
                                        current_metadata_version=current_metadata_version)
        else:
            metadata_id = existing_metadata.get("_id")
            print(f"⏩ Skipping {metadata_id} (hash and metadata version unchanged)")
            return None

    def _create_chunks(self, metadata_id : str,
                       strategy: AbstractChunkingStrategy,
                       content: str):
        chunks = strategy.chunk(content)
        chunk_ids = []
        for i, chunk_text in enumerate(chunks):
            vector = self.embedding_model.encode(chunk_text)
            chunk_id = f"{metadata_id}_chunk_{i}"  # Format: meta_id_chunk_index
            chunk_doc = {
                "_id": chunk_id,
                "metadata_id": metadata_id,
                "chunk_index": i,
                "chunk_src": chunk_text,
                "embedding": vector
            }
            self.db_manager.db.chunks.update_one({"_id": chunk_id}, {"$set": chunk_doc}, upsert=True)
            chunk_ids.append(chunk_id)
        return chunk_ids
