"""
github_collector.py
Central controller for GitHub data collection.
This module delegates specific tasks to specialized submodules:
- github_commits.py (commits and contributors)
- github_pull_requests.py (pull requests)
- github_issues.py (issues)
- github_files.py (file management: branches & releases)
"""

import os
import requests
from dotenv import load_dotenv
from core.database_manager import DatabaseManager
from core.file_storage_manager import FileStorageManager
from collectors.github_commits import fetch_commits, update_contributors
from collectors.github_pull_requests import fetch_pull_requests
from collectors.github_issues import fetch_issues
from collectors.github_files import fetch_files_from_branch, fetch_latest_release_files


class GitHubCollector:
    """
    Main GitHub data collector that orchestrates interactions with GitHub APIs.
    It delegates specific operations to specialized modules.
    """

    github_token = None

    @staticmethod
    def github_request(url: str, params: Optional[Dict[str, Any]] = None, return_json: bool = True):
        """
        Makes a GitHub API request with rate limit handling.

        Args:
            url (str): The API endpoint URL.
            params (dict, optional): Additional query parameters.
            return_json (bool): Whether to return the response as JSON.

        Returns:
            dict or requests.Response: JSON response from GitHub API or full response object if return_json=False.
        """
        if not GitHubCollector.github_token:
            raise ValueError("GitHub token is not set. Initialize GitHubCollector with a valid token.")

        headers = {"Authorization": f"token {GitHubCollector.github_token}"}

        while True:
            try:
                response = requests.get(url, headers=headers, params=params, timeout=10)

                # Manage rate limit
                if response.status_code == 403 and 'X-RateLimit-Reset' in response.headers:
                    reset_time = int(response.headers["X-RateLimit-Reset"])
                    wait_time = max(0, reset_time - int(time.time())) + 1
                    print(f"⚠️ GitHub rate limit reached. Waiting {wait_time} seconds...")
                    time.sleep(wait_time)
                    continue 

                # Manage HTTP errors
                if response.status_code != 200:
                    print(f"❌ GitHub API Error ({response.status_code}): {response.text}")
                    return None

                return response.json() if return_json else response

            except requests.RequestException as e:
                print(f"⚠️ Network error while fetching {url}: {e}")
                return None

    def __init__(self, database_manager: DatabaseManager, github_token: str, github_org: str, storage_manager: FileStorageManager):
        """
        Initializes the GitHubCollector with required dependencies.

        Args:
            database_manager (DatabaseManager): Instance of DatabaseManager for MongoDB access.
            github_token (str): GitHub API token for authentication.
            github_org (str): GitHub organization or user whose data will be collected.
            storage_manager (FileStorageManager): Instance for handling file storage operations.
        """
        self.db_manager = database_manager
        GitHubCollector.github_token = github_token
        self.github_org = github_org
        self.storage_manager = storage_manager

    def collect_all_data(self):
        """
        Collects all relevant GitHub data for the organization/user.

        This method:
        - Retrieves repositories
        - Fetches commits, issues, pull requests, and files
        - Updates contributor information
        """
        print("🔍 Fetching repositories...")
        repositories = self.fetch_repositories()

        for repo in repositories:
            print(f"\n📡 Processing repository: {repo}")

            print("📥 Fetching commits...")
            fetch_commits(self.db_manager, repo)

            print("📥 Fetching issues...")
            fetch_issues(self.db_manager, repo)

            print("📥 Fetching pull requests...")
            fetch_pull_requests(self.db_manager, repo, self.storage_manager)

            print("📥 Fetching files from main branch...")
            fetch_files_from_branch(self.db_manager, repo, self.storage_manager)

            print("📥 Fetching latest release files...")
            fetch_latest_release_files(self.db_manager, repo, self.storage_manager)

        print("\n🔄 Updating contributor data...")
        update_contributors(self.db_manager)

        print("✅ GitHub data collection completed!")

    def fetch_repositories(self):
        """
        Retrieves a list of repositories for the GitHub organization/user.

        Returns:
            list: List of repository names (e.g., ['archethic-foundation/archethic-node']).
        """
        url = f"https://api.github.com/orgs/{self.github_org}/repos?per_page=100"
        repos = []
        page = 1

        while True:
            data = GitHubCollector.github_request(url + f"&page={page}")

            if not data:
                break  # Stop if an error occurs or no more repositories

            repos.extend([repo["full_name"] for repo in data])
            page += 1

        print(f"✅ Retrieved {len(repos)} repositories.")
        return repos
    
    def fetch_repository_info(self, repo: str) -> None:
        """
        Fetches repository metadata and README content.

        Args:
            repo (str): The GitHub repository (e.g., 'org/repo').
        """
        repo_url = f"https://api.github.com/repos/{repo}"
        readme_url = f"https://api.github.com/repos/{repo}/readme"

        repo_data = GitHubCollector.github_request(repo_url)
        if not repo_data or "message" in repo_data and repo_data["message"] == "Not Found":
            print(f"❌ Repository not found: {repo}")
            return

        readme_data = GitHubCollector.github_request(readme_url)
        readme_content = GitHubCollector.github_request(readme_data["download_url"], None) if "download_url" in readme_data else None

        repo_entry = {
            "_id": repo,
            "description": repo_data.get("description", ""),
            "language": repo_data.get("language", ""),
            "url": repo_data.get("html_url", ""),
            "last_commit_date": repo_data.get("updated_at", ""),
            "readme": readme_content
        }

        self.db_manager.db.repositories.update_one({"_id": repo}, {"$set": repo_entry}, upsert=True)
        print(f"✅ Repository {repo} added/updated.")

"""
github_collector.py
Handles interactions with the GitHub API to fetch repository data, commits, issues,
pull requests, and files for integration into MongoDB.
"""

import requests
import time
from datetime import datetime
from typing import List, Dict, Optional
from dotenv import load_dotenv
from core.database_manager import DatabaseManager  # Import DatabaseManager
from core.file_storage_manager import FileStorageManager  # Import FileStorageManager


class GitHubCollector:
    """
    Collects data from GitHub repositories and stores them in MongoDB.
    """

    def __init__(self, database_manager : DatabaseManager, mongo_uri: str, db_name: str, github_token: str, github_org: str, storage_manager: FileStorageManager):
        """
        Initializes the GitHubCollector with MongoDB and GitHub API credentials.

        Args:
            database_manager (DatabaseManager): Instance of the DatabaseManager class (already initialized).
            github_token (str): GitHub API token for authentication.
            github_org (str): Organization or user to monitor.
            storage_manager (FileStorageManager): Instance for file storage.
        """
        self.db_manager = database_manager
        self.github_token = github_token
        self.github_org = github_org
        self.headers = {"Authorization": f"token {self.github_token}"}
        self.storage_manager = storage_manager

    def github_request(self, url: str, params: dict = None, return_json : bool = True) -> dict:
        """
        Makes a GitHub API request with rate limit handling.

        Args:
            url (str): The API endpoint URL.
            params (dict, optional): Additional query parameters.

        Returns:
            dict: JSON response from GitHub API.
        """
        while True:
            response = requests.get(url, headers=self.headers, params=params)
            
            if response.status_code == 403 and 'X-RateLimit-Reset' in response.headers:
                reset_time = int(response.headers["X-RateLimit-Reset"])
                wait_time = max(0, reset_time - int(time.time())) + 1
                print(f"⚠️ GitHub rate limit reached. Waiting {wait_time} seconds...")
                time.sleep(wait_time)
                continue
            
            if response.status_code != 200:
                print(f"❌ GitHub API Error: {response.status_code} - {response.text}")
                return None
            
            return response.json() if return_json else response

    def fetch_repositories(self) -> list:
        """
        Fetches all repositories for the given GitHub organization.

        Returns:
            list: List of repository full names.
        """
        repos = []
        page = 1
        while True:
            url = f"https://api.github.com/orgs/{self.github_org}/repos?per_page=100&page={page}"
            data = self.github_request(url)
            if not data:
                break
            repos.extend([repo["full_name"] for repo in data])
            page += 1
        return repos

    

    def fetch_commits(self, repo: str) -> None:
        """
        Fetches commits from a repository and stores them in MongoDB.

        Args:
            repo (str): The GitHub repository (e.g., 'org/repo').
        """
        last_commit = self.db_manager.db.commits.find_one({"repo": repo}, sort=[("date", -1)])
        last_commit_date = last_commit["date"] if last_commit else None
        page = 1

        while True:
            url = f"https://api.github.com/repos/{repo}/commits?per_page=100&page={page}"
            data = self.github_request(url)
            if not data:
                break

            commits = []
            for commit in data:
                commit_sha = commit["sha"]
                commit_date = datetime.strptime(commit["commit"]["committer"]["date"], "%Y-%m-%dT%H:%M:%SZ")

                if last_commit_date and commit_date <= last_commit_date:
                    return

                if self.db_manager.db.commits.find_one({"_id": commit_sha}):
                    continue

                # Fetch file details
                files_changed = self.fetch_commit_files(repo, commit_sha)
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
                    "files_changed": files_changed
                }
                commits.append(commit_entry)

            if commits:
                self.db_manager.db.commits.insert_many(commits)
                print(f"✅ {len(commits)} new commits added for {repo}")
            page += 1

    def fetch_commit_files(self, repo: str, commit_sha: str) -> list:
        """
        Fetches details (files changed) for a commit.

        Args:
            repo (str): The GitHub repository.
            commit_sha (str): The commit SHA.

        Returns:
            list: List of file paths changed in the commit.
        """
        url = f"https://api.github.com/repos/{repo}/commits/{commit_sha}"
        data = self.github_request(url)
        if not data or "files" not in data:
            return []

        files_info = []
        files_to_insert = []

        for file in data["files"]:
            file_id = f"{commit_sha}_{file['filename']}"
            if self.db_manager.db.files.find_one({"_id": file_id}):
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

            if file["status"] == "added":
                raw_url = file.get("raw_url")
                if raw_url:
                    file_content = self.fetch_large_file(raw_url)
                    if isinstance(file_content, dict):  # Git LFS pointer case
                        lfs_pointer_id = f"{commit_sha}_{file['filename']}_lfs"
                        lfs_pointer = {
                            "_id": lfs_pointer_id,
                            "file_id": file_id,
                            "oid": file_content["oid"],
                            "size": file_content["size"],
                            "storage_url": raw_url
                        }
                        self.db_manager.db.lfs_pointers.update_one({"_id": lfs_pointer_id}, {"$set": lfs_pointer}, upsert=True)
                        file_obj["lfs_pointer_id"] = lfs_pointer_id
                    elif file_content:
                        external_url = self.storage_manager.store_file_content(file_content, repo, commit_sha, file["filename"])
                        file_obj["external_url"] = external_url

            files_info.append(file_id)
            files_to_insert.append(file_obj)

        if files_to_insert:
            self.db_manager.db.files.insert_many(files_to_insert)

        return files_info

    def fetch_large_file(self, raw_url: str):
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
        try:
            response = requests.get(raw_url, timeout=10)
            if response.status_code != 200:
                print(f"⚠️ Failed to fetch file: {raw_url} (HTTP {response.status_code})")
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

        except requests.RequestException as e:
            print(f"⚠️ Error fetching file from {raw_url}: {e}")
            return None

    def fetch_issues(self, repo: str) -> None:
        """
        Fetches GitHub issues for a repository and stores them in MongoDB.

        Args:
            repo (str): The GitHub repository (e.g., 'org/repo').
        """
        page = 1
        while True:
            url = f"https://api.github.com/repos/{repo}/issues?state=all&per_page=100&page={page}"
            data = self.github_request(url)
            if not data:
                break

            issues = []
            bulk_operations = []
            inserted_issue_ids = set()

            for issue in data:
                if 'pull_request' in issue:
                    continue  # Ignore PRs (only store actual issues)

                issue_id = f"{repo}#{issue['number']}"
                existing_issue = self.db_manager.db.issues.find_one({'_id': issue_id})

                issue_data = {
                    '_id': issue_id,
                    'repo': repo,
                    'number': issue['number'],
                    'title': issue['title'],
                    'body': issue.get('body', ''),  # Stocke le contenu de l'issue
                    'state': issue['state'],
                    'labels': [label['name'] for label in issue.get('labels', [])],
                    'comments': issue['comments'],
                    'created_at': issue['created_at'],
                    'updated_at': issue['updated_at'],
                    'url': issue['html_url']
                }

                if not existing_issue and issue_id not in inserted_issue_ids:
                    # Insert new issue
                    issues.append(issue_data)
                    inserted_issue_ids[issue_id] = issue_data
                elif (existing_issue and existing_issue['updated_at'] != issue['updated_at']):
                    bulk_operations.append(({'_id': issue_data['_id']}, {'$set': issue_data}))
                elif(issue_id in inserted_issue_ids):
                    bulk_operations.append(({'_id': issue_data['_id']}, {'$set': issue_data}))

            # Bulk insert for new issues
            if issues:
                self.db_manager.db.issues.insert_many(issues)

            # Bulk update existing issues
            if bulk_operations:
                self.db_manager.db.issues.bulk_write(
                    [pymongo.UpdateOne(q, u) for q, u in bulk_operations]
                )

            print(f"✅ Issues fetched and stored for {repo} (Page {page})")
            page += 1

    def fetch_pull_requests(self, repo: str) -> None:
        """
        Retrieves Pull Requests (PRs) from a repository and stores them in MongoDB.
        Large data (bodies) are stored locally with a reference in MongoDB.

        Args:
            repo (str): The GitHub repository (e.g., 'org/repo').
        """
        page = 1
        while True:
            url = f"https://api.github.com/repos/{repo}/pulls?state=all&per_page=100&page={page}"
            prs = self.github_request(url)
            if not prs:
                break

            prs_to_insert = []
            bulk_operations = []
            inserted_pr_ids = set()

            for pr in prs:
                pr_id = f"{repo}#{pr['number']}"
                existing_pr = self.db_manager.db.pull_requests.find_one({'_id': pr_id})

                # Store PR body content locally
                body_url, body_summary = None, None
                if pr.get("body"):
                    body_url = self.storage_manager.store_file_content(
                        pr["body"], repo, f"pr_{pr['number']}", "_body.txt"
                    )
                    body_summary = pr["body"][:500]  # Keep a short summary

                pr_data = {
                    '_id': pr_id,
                    'repo': repo,
                    'number': pr['number'],
                    'title': pr['title'],
                    'state': pr['state'],
                    'created_at': pr['created_at'],
                    'updated_at': pr['updated_at'],
                    'merged_at': pr.get('merged_at'),
                    'author': pr['user']['login'],
                    'commits': self.fetch_pr_commits(repo, pr['number']),
                    'metadata_id': None,
                    'body_url': body_url,
                    'body_summary': body_summary,
                    'body_metadata': None,
                    'labels': [label['name'] for label in pr.get('labels', [])],
                    'url': pr['html_url']
                }

                if not existing_pr and pr_id not in inserted_pr_ids:
                    prs_to_insert.append(pr_data)
                    inserted_pr_ids.add(pr_id)
                elif existing_pr and existing_pr['updated_at'] != pr['updated_at']:
                    bulk_operations.append(({'_id': pr_data['_id']}, {'$set': pr_data}))

            # Bulk insert for new PRs
            if prs_to_insert:
                self.db_manager.db.pull_requests.insert_many(prs_to_insert)

            # Bulk update existing PRs
            if bulk_operations:
                self.db_manager.db.pull_requests.bulk_write(
                    [pymongo.UpdateOne(q, u) for q, u in bulk_operations]
                )

            print(f"✅ Pull Requests fetched and stored for {repo} (Page {page})")
            page += 1

    def fetch_pr_commits(self, repo: str, pr_number: int) -> List[str]:
        """
        Retrieves commits linked to a Pull Request (PR) by checking only those present in the `commits` collection.
        If a commit is not in the database, it is assumed not to be part of the `main` branch.

        Args:
            repo (str): The GitHub repository (e.g., 'org/repo').
            pr_number (int): The pull request number.

        Returns:
            List[str]: A list of commit SHAs associated with the PR.
        """
        url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}/commits?per_page=100"
        pr_commits = self.github_request(url)

        if not pr_commits:
            return []

        commit_shas = [commit["sha"] for commit in pr_commits]

        existing_commits = set(
            doc["_id"] for doc in self.db_manager.db.commits.find({"_id": {"$in": commit_shas}}, {"_id": 1})
        )

        valid_commit_ids = [sha for sha in commit_shas if sha in existing_commits]

        return valid_commit_ids

    def update_contributors(self) -> None:
        """
        Aggregates commit data to update the `contributors` collection.
        Each contributor's total commits and last 10 commit references are stored.
        """
        contributors_map = {}

        for commit in self.db_manager.db.commits.find({}, {"author": 1, "author_email": 1, "repo": 1, "_id": 1}):
            author_email = commit.get("author_email")
            if not author_email:
                continue

            if author_email not in contributors_map:
                contributors_map[author_email] = {
                    "name": commit["author"],
                    "email": author_email,
                    "repos": set(),
                    "commits": [],
                    "total_commits": 0
                }

            contributors_map[author_email]["repos"].add(commit["repo"])
            contributors_map[author_email]["commits"].append(commit["_id"])
            contributors_map[author_email]["total_commits"] += 1

        for email, data in contributors_map.items():
            self.db_manager.db.contributors.update_one(
                {"_id": email},
                {
                    "$set": {
                        "name": data["name"],
                        "email": data["email"],
                        "repos": list(data["repos"]),
                        "total_commits": data["total_commits"],
                        "commits": data["commits"][-10:]
                    }
                },
                upsert=True
            )

        print("✅ Update contributors done!")

