"""
file_storage_manager.py
Handles local file storage operations (or could be extended to other storages).
"""

import os
import requests
from typing import Optional

class FileStorageManager:
    """Handles local file storage operations and retrieval of file content."""

    def __init__(self, base_storage_path: str, base_url: str):
        """
        Initializes the FileStorageManager.

        Args:
            base_storage_path (str): The root directory where files are stored locally.
            base_url (str): The base URL for serving files over HTTP.
        """
        self.base_storage_path = os.path.abspath(base_storage_path)
        self.base_url = base_url

        # Ensure the base storage directory exists
        os.makedirs(self.base_storage_path, exist_ok=True)

    def store_file_content(self, content: str, repo: str, reference_id: str, filename: str) -> str:
        """
        Stores file content locally and returns an accessible URL.

        Args:
            content (str): The raw text content to store.
            repo (str): The repository name or identifier.
            reference_id (str): Typically a commit SHA, branch name, or unique ID.
            filename (str): The name of the file.

        Returns:
            str: The external URL where the file can be accessed.
        """
        sanitized_repo = self._sanitize_repo_name(repo)
        sanitized_filename = self._sanitize_filename(filename)

        # Construct the local file path
        local_file_path = os.path.join(self.base_storage_path, sanitized_repo, reference_id, sanitized_filename)

        # Ensure the directory exists
        os.makedirs(os.path.dirname(local_file_path), exist_ok=True)

        # Write the content to the file
        with open(local_file_path, 'w', encoding='utf-8') as f:
            f.write(content)

        # Generate the accessible URL
        relative_path = os.path.join(sanitized_repo, reference_id, sanitized_filename).replace(os.sep, "/")
        external_url = f"{self.base_url}/{relative_path}"

        return external_url

    def fetch_file_content(self, file_path: str) -> Optional[str]:
        """
        Fetches file content from a local path or URL.

        Args:
            file_path (str): The local file path or external URL.

        Returns:
            Optional[str]: The file content if successful, otherwise None.
        """
        if file_path.startswith("http"):
            return self._fetch_remote_file(file_path)
        return self._fetch_local_file(file_path)

    def _fetch_remote_file(self, url: str) -> Optional[str]:
        """
        Fetches file content from a remote URL.

        Args:
            url (str): The URL of the file.

        Returns:
            Optional[str]: The content of the file if successful, otherwise None.
        """
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                return response.text
        except Exception as e:
            print(f"[FileStorageManager] Error fetching file from {url}: {e}")
        return None

    def _fetch_local_file(self, file_path: str) -> Optional[str]:
        """
        Reads file content from a local path.

        Args:
            file_path (str): The absolute path of the file.

        Returns:
            Optional[str]: The file content if successful, otherwise None.
        """
        try:
            if not file_path.startswith(self.base_storage_path):
                print(f"[Security Warning] Attempt to access unauthorized path: {file_path}")
                return None

            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"[FileStorageManager] Error reading file {file_path}: {e}")
        return None

    def delete_file(self, repo: str, reference_id: str, filename: str) -> bool:
        """
        Deletes a file from local storage.

        Args:
            repo (str): The repository name or identifier.
            reference_id (str): Typically a commit SHA, branch name, or unique ID.
            filename (str): The name of the file to delete.

        Returns:
            bool: True if the file was successfully deleted, False otherwise.
        """
        sanitized_repo = self._sanitize_repo_name(repo)
        sanitized_filename = self._sanitize_filename(filename)

        local_file_path = os.path.join(self.base_storage_path, sanitized_repo, reference_id, sanitized_filename)

        try:
            if os.path.exists(local_file_path):
                os.remove(local_file_path)
                return True
        except Exception as e:
            print(f"[FileStorageManager] Error deleting file {local_file_path}: {e}")
        return False

    def get_file_url(self, repo: str, reference_id: str, filename: str) -> str:
        """
        Returns the accessible URL of a stored file.

        Args:
            repo (str): The repository name or identifier.
            reference_id (str): Typically a commit SHA, branch name, or unique ID.
            filename (str): The name of the file.

        Returns:
            str: The constructed URL where the file can be accessed.
        """
        sanitized_repo = self._sanitize_repo_name(repo)
        sanitized_filename = self._sanitize_filename(filename)

        relative_path = os.path.join(sanitized_repo, reference_id, sanitized_filename).replace(os.sep, "/")
        return f"{self.base_url}/{relative_path}"

    def _sanitize_repo_name(self, repo: str) -> str:
        """
        Replace forward slashes in repo names with underscores
        so that we have a flat folder structure.
        """
        return repo.replace("/", "_")

    def _sanitize_filename(self, filename: str) -> str:
        """
        Sanitizes the filename to avoid directory traversal, etc.
        """
        # Minimal example: remove any '..', etc.
        return os.path.basename(filename)
