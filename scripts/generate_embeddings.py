"""
CLI script: triggers embedding generation (if needed) for a given repo and collection.
It uses the existing MetadataManager pipeline and starts the local HTTP server required for file access.
"""

import argparse
import multiprocessing
from core.database_manager import DatabaseManager
from core.file_storage_manager import FileStorageManager
from metadata.metadata_manager import MetadataManager
from server.local_storage_server import LocalStorageServer

def start_server():
    """Start the local HTTP server required by FileStorageManager to access chunked files."""
    server = LocalStorageServer(port=8000, storage_directory="local_storage")
    server.start_server()

def main(repo: str, collection: str):
    # Start the HTTP server in a separate process
    server_process = multiprocessing.Process(target=start_server)
    server_process.start()

    try:
        # Initialize database and file storage managers
        db = DatabaseManager("mongodb://localhost:27017", "archethic_github_data")
        file_storage = FileStorageManager(base_storage_path="local_storage", base_url="http://localhost:8000")

        # Create and trigger metadata manager for the given repo/collection
        manager = MetadataManager(db_manager=db, file_storage=file_storage)
        manager.update_metadata_for_specific_data(repo, [{"collection_src": collection}])

    finally:
        # Ensure local server is stopped after processing
        server_process.terminate()
        server_process.join()
        print("🛑 Local server stopped.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", required=True, help="Repository name (e.g., archethic-foundation/archethic-node)")
    parser.add_argument("--collection", default="main_files", help="Collection to process (default: main_files)")
    args = parser.parse_args()

    main(args.repo, args.collection)