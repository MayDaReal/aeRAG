"""
github_files.py
Handles fetching and storing GitHub files from branches and releases into MongoDB.
"""

from typing import Optional
from collectors.github_request import github_request
from core.database_manager import DatabaseManager
from core.file_storage_manager import FileStorageManager


def fetch_files_from_branch(db_manager: DatabaseManager, repo: str, storage_manager: FileStorageManager) -> None:
    """
    Retrieves all files from the main branch and updates the `main_files` collection.

    Args:
        db_manager (DatabaseManager): Instance of DatabaseManager for MongoDB access.
        repo (str): The GitHub repository (e.g., 'org/repo').
        storage_manager (FileStorageManager): Manages the storage of large files.
    """
    branch = get_default_branch(repo)
    url = f"https://api.github.com/repos/{repo}/git/trees/{branch}?recursive=1"
    data = github_request(url)

    if not data or "tree" not in data:
        print(f"❌ Failed to fetch files from branch {branch} in {repo}")
        return

    current_files = {doc["filename"]: doc for doc in db_manager.db.main_files.find({"repo": repo})}
    files_to_insert = []
    files_to_delete = set(current_files.keys())

    for item in data["tree"]:
        if item["type"] != "blob":
            continue

        file_id = f"{repo}_main_{item['path']}"
        existing_file = db_manager.db.main_files.find_one({"_id": file_id})

        file_entry = {
            "_id": file_id,
            "repo": repo,
            "filename": item["path"],
            "commit_id": item["sha"],
            "metadata_id": None,
            "external_url": None
        }

        if existing_file:
            if existing_file["commit_id"] == file_entry["commit_id"]:
                files_to_delete.discard(item["path"])
                continue
            db_manager.db.main_files.update_one({"_id": file_id}, {"$set": file_entry})
            files_to_delete.discard(item["path"])
        else:
            raw_url = f"https://raw.githubusercontent.com/{repo}/{branch}/{item['path']}"
            file_content = get_content(raw_url)

            if file_content:
                external_url = storage_manager.store_file_content(file_content, repo, branch, item["path"])
                file_entry["external_url"] = external_url

            files_to_insert.append(file_entry)

    if files_to_insert:
        db_manager.db.main_files.insert_many(files_to_insert)
        print(f"✅ {len(files_to_insert)} new files added to `main_files` for {repo}")

    if files_to_delete:
        db_manager.db.main_files.delete_many({"filename": {"$in": list(files_to_delete)}})
        print(f"🗑 {len(files_to_delete)} outdated files removed from `main_files` for {repo}")


def fetch_latest_release_files(db_manager: DatabaseManager, repo: str, storage_manager: FileStorageManager) -> None:
    """
    Retrieves all files from the latest release tag and updates the `last_release_files` collection.

    Args:
        db_manager (DatabaseManager): Instance of DatabaseManager for MongoDB access.
        repo (str): The GitHub repository (e.g., 'org/repo').
        storage_manager (FileStorageManager): Manages the storage of large files.
    """
    url = f"https://api.github.com/repos/{repo}/releases/latest"
    release_data = github_request(url)

    if not release_data or "tag_name" not in release_data:
        print(f"❌ No release found for {repo}")
        return

    latest_tag = release_data["tag_name"]
    print(f"🔖 Latest release for {repo}: {latest_tag}")

    url = f"https://api.github.com/repos/{repo}/git/trees/{latest_tag}?recursive=1"
    data = github_request(url)

    if not data or "tree" not in data:
        print(f"❌ Failed to fetch files from release {latest_tag} in {repo}")
        return

    current_files = {doc["filename"]: doc for doc in db_manager.db.last_release_files.find({"repo": repo})}
    files_to_insert = []
    files_to_delete = set(current_files.keys())

    for item in data["tree"]:
        if item["type"] != "blob":
            continue

        file_id = f"{repo}_last_release_{item['path']}"
        existing_file = db_manager.db.last_release_files.find_one({"_id": file_id})

        file_entry = {
            "_id": file_id,
            "repo": repo,
            "filename": item["path"],
            "commit_id": item["sha"],
            "metadata_id": None,
            "external_url": None
        }

        if existing_file:
            if existing_file["commit_id"] == file_entry["commit_id"]:
                files_to_delete.discard(item["path"])
                continue
            db_manager.db.last_release_files.update_one({"_id": file_id}, {"$set": file_entry})
            files_to_delete.discard(item["path"])
        else:
            raw_url = f"https://raw.githubusercontent.com/{repo}/{latest_tag}/{item['path']}"
            file_content = get_content(raw_url)

            if file_content:
                external_url = storage_manager.store_file_content(file_content, repo, latest_tag, item["path"])
                file_entry["external_url"] = external_url

            files_to_insert.append(file_entry)

    if files_to_insert:
        db_manager.db.last_release_files.insert_many(files_to_insert)
        print(f"✅ {len(files_to_insert)} new files added to `last_release_files` for {repo}")

    if files_to_delete:
        db_manager.db.last_release_files.delete_many({"filename": {"$in": list(files_to_delete)}})
        print(f"🗑 {len(files_to_delete)} outdated files removed from `last_release_files` for {repo}")


def get_default_branch(repo: str) -> str:
    """
    Retrieves the default branch of a GitHub repository.

    Args:
        repo (str): The GitHub repository.

    Returns:
        str: The default branch name (default: 'main').
    """
    url = f"https://api.github.com/repos/{repo}"
    data = github_request(url)

    if not data or "default_branch" not in data:
        print(f"⚠️ Could not determine default branch for {repo}, defaulting to 'main'")
        return "main"

    return data["default_branch"]


def get_content(raw_url: str) -> Optional[str]:
    """
    Fetches the content of a file from its raw GitHub URL.

    Args:
        raw_url (str): The direct URL to fetch the file content.

    Returns:
        Optional[str]: The file content if successfully retrieved.
    """
    response = github_request(raw_url, return_json=False)
    if not response:
        return None

    return response.text
