"""
github_commits.py
Handles fetching and storing GitHub commits, file changes, and contributor updates.
"""

import pymongo
from datetime import datetime
from typing import List
from core.database_manager import DatabaseManager
from core.file_storage_manager import FileStorageManager
from collectors.github_request import github_request


def fetch_commits(db_manager: DatabaseManager, repo: str) -> None:
    """
    Fetches commits from a repository and stores them in MongoDB.

    Args:
        db_manager (DatabaseManager): Instance to interact with MongoDB.
        repo (str): The GitHub repository (e.g., 'org/repo').
        github_token (str): GitHub API token.
    """
    last_commit = db_manager.db.commits.find_one({"repo": repo}, sort=[("date", -1)])
    last_commit_date = last_commit["date"] if last_commit else None
    page = 1

    while True:
        url = f"https://api.github.com/repos/{repo}/commits?per_page=100&page={page}"
        data = github_request(url)

        if not data:
            break

        commits = []
        for commit in data:
            commit_sha = commit["sha"]
            commit_date = datetime.strptime(commit["commit"]["committer"]["date"], "%Y-%m-%dT%H:%M:%SZ")

            if last_commit_date and commit_date <= last_commit_date:
                return  # Stop fetching if commits are already stored

            if db_manager.db.commits.find_one({"_id": commit_sha}):
                continue  # Skip existing commits

            # Retrieve file details for each commit
            files_changed = fetch_commit_files(db_manager, repo, commit_sha)
            if not files_changed:
                continue

            commit_entry = {
                "_id": commit_sha,
                "repo": repo,
                "message": commit["commit"]["message"],
                "author": commit["commit"]["author"]["name"] if commit["commit"]["author"] else None,
                "author_email": commit["commit"]["author"]["email"] if commit["commit"]["author"] else None,
                "committer": commit["commit"]["committer"]["name"] if commit["commit"]["committer"] else None,
                "committer_email": commit["commit"]["committer"]["email"] if commit["commit"]["committer"] else None,
                "date": commit_date,
                'metadata_id': None,
                "files_changed": files_changed
            }
            commits.append(commit_entry)

        if commits:
            db_manager.db.commits.insert_many(commits)
            print(f"✅ {len(commits)} new commits added for {repo}")

        page += 1

def fetch_commit_files(db_manager: DatabaseManager, repo: str, commit_sha: str) -> List[str]:
    """
    Fetches details (files changed) for a commit.

    Args:
        db_manager (DatabaseManager): Instance to interact with MongoDB.
        repo (str): The GitHub repository.
        commit_sha (str): The commit SHA.
        github_token (str): GitHub API token.

    Returns:
        List[str]: List of file paths changed in the commit.
    """
    url = f"https://api.github.com/repos/{repo}/commits/{commit_sha}"
    data = github_request(url)

    if not data or "files" not in data:
        return []

    files_info = []
    files_to_insert = []

    for file in data["files"]:
        file_id = f"{commit_sha}_{file['filename']}"
        if db_manager.db.files.find_one({"_id": file_id}):
            files_info.append(file_id)
            continue

        file_obj = {
            "_id": file_id,
            "commit_id": commit_sha,
            "repo": repo,
            "filename": file["filename"],
            "status": file["status"],
            "patch": file.get("patch", ""),
            "metadata_id": None,
            "lfs_pointer_id": None,
            "external_url": None
        }

        # Handle added files (download or detect LFS)
        if file["status"] == "added":
            raw_url = file.get("raw_url")
            if raw_url:
                file_content = fetch_large_file(raw_url)
                if isinstance(file_content, dict):  # Git LFS pointer case
                    lfs_pointer_id = f"{commit_sha}_{file['filename']}_lfs"
                    lfs_pointer = {
                        "_id": lfs_pointer_id,
                        "file_id": file_id,
                        "oid": file_content["oid"],
                        "size": file_content["size"],
                        "external_url": raw_url
                    }
                    db_manager.db.lfs_pointers.update_one({"_id": lfs_pointer_id}, {"$set": lfs_pointer}, upsert=True)
                    file_obj["lfs_pointer_id"] = lfs_pointer_id
                elif file_content:
                    external_url = FileStorageManager("local_storage", "http://localhost:8000").store_file_content(
                        file_content, repo, commit_sha, file["filename"]
                    )
                    file_obj["external_url"] = external_url

        files_info.append(file_id)
        files_to_insert.append(file_obj)

    if files_to_insert:
        db_manager.db.files.insert_many(files_to_insert)

    return files_info

def fetch_large_file(raw_url: str):
    """
    Fetches file content from its raw URL.
    If it's a Git LFS pointer file, parse and return pointer metadata.
    Otherwise, return the full file content.

    Args:
        raw_url (str): The direct URL to fetch the file content.

    Returns:
        dict or str: If it's a Git LFS pointer file, returns a dictionary with metadata.
                     Otherwise, returns the raw content of the file as a string.
    """
    response = github_request(raw_url, return_json=False)
    if not response:
        return None

    content = response.text

    # Check if it's a Git LFS pointer file
    if content.startswith("version https://git-lfs.github.com/spec/v1"):
        pointer_info = {}
        for line in content.splitlines():
            if line.startswith("version"):
                pointer_info["version"] = line.split(" ", 1)[1].strip()
            elif line.startswith("oid"):
                parts = line.split(" ", 1)[1].strip().split(":", 1)
                if len(parts) == 2:
                    pointer_info["oid_type"] = parts[0]
                    pointer_info["oid"] = parts[1]
            elif line.startswith("size"):
                pointer_info["size"] = line.split(" ", 1)[1].strip()

        return pointer_info  # Return structured metadata for Git LFS pointer files

    return content  # Otherwise, return full file content

def update_contributors(db_manager: DatabaseManager) -> None:
    """
    Aggregates commit data to update the `contributors` collection.

    Args:
        db_manager (DatabaseManager): Instance to interact with MongoDB.
    """
    contributors_map = {}

    # Fetch all commits and extract contributor information
    for commit in db_manager.db.commits.find({}, {"author": 1, "author_email": 1, "repo": 1, "_id": 1}):
        author_email = commit.get("author_email")
        author_name = commit.get("author")

        if not author_email:
            continue  # Ignore commits with no valid author email

        # Initialize contributor entry if not already in the map
        if author_email not in contributors_map:
            contributors_map[author_email] = {
                "name": author_name,
                "email": author_email,
                "repos": set(),
                "commits": [],
                "total_commits": 0
            }

        # Add repository and commit information
        contributors_map[author_email]["repos"].add(commit["repo"])
        contributors_map[author_email]["commits"].append(commit["_id"])
        contributors_map[author_email]["total_commits"] += 1

    # Bulk update contributors collection
    bulk_operations = []
    for email, data in contributors_map.items():
        bulk_operations.append(
            pymongo.UpdateOne(
                {"_id": email},
                {"$set": {
                    "name": data["name"],
                    "email": data["email"],
                    "repos": list(data["repos"]),
                    "total_commits": data["total_commits"],
                    "commits": data["commits"][-10:]  # Store only the last 10 commits for efficiency
                }},
                upsert=True  # Insert new contributor if not exists
            )
        )

    if bulk_operations:
        db_manager.db.contributors.bulk_write(bulk_operations)
        print(f"✅ Contributors updated successfully. {len(bulk_operations)} contributors modified.")
    else:
        print("ℹ️ No new contributors to update.")
