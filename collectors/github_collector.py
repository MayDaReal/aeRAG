"""
github_collector.py
Handles high-level orchestration of GitHub data collection.
This module delegates specific tasks to specialized submodules:
- github_commits.py (commits and contributors)
- github_pull_requests.py (pull requests)
- github_issues.py (issues)
- github_files.py (file management: branches & releases)
"""

from typing import List, Dict
from core.database_manager import DatabaseManager
from core.file_storage_manager import FileStorageManager
from collectors.github_commits import fetch_commits, update_contributors
from collectors.github_pull_requests import fetch_pull_requests
from collectors.github_issues import fetch_issues
from collectors.github_files import fetch_files_from_branch, fetch_latest_release_files
from collectors.github_request import github_request


class GitHubCollector:
    """
    Main orchestrator for GitHub data collection.
    """

    def __init__(self, db_manager: DatabaseManager, github_token: str, github_org: str, storage_manager: FileStorageManager):
        """
        Initializes the GitHubCollector with required dependencies.

        Args:
            db_manager (DatabaseManager): MongoDB manager instance.
            github_token (str): GitHub API token.
            github_org (str): GitHub organization to fetch data from.
            storage_manager (FileStorageManager): Storage manager for large files.
        """
        self.db_manager = db_manager
        self.github_token = github_token
        self.github_org = github_org
        self.storage_manager = storage_manager

    def update_all_repos(self):
        """
        Updates all repositories within the GitHub organization.
        """
        repos = self.fetch_repositories()
        self.update_selected_repos(repos)

    def update_selected_repos(self, repos: List[str]):
        """
        Updates all data for a selected list of repositories.

        Args:
            repos (List[str]): List of repositories to update.
        """
        for repo in repos:
            print(f"🔄 Updating all data for {repo}...")
            self.update_specific_data(repo, ["repository info", "commits", "pull requests", "issues"])
        print("✅ Repository updates completed.")

    def update_specific_data(self, repo: str, selected_data: List[str]):
        """
        Updates only selected parts of a repository's data.

        Args:
            repo (str): GitHub repository to update.
            selected_data (List[str]): List of data types to update.
        """
        if "repository info" in selected_data:
            self.fetch_repository_info(repo)
        if "commits" in selected_data:
            fetch_commits(self.db_manager, repo)
            update_contributors(self.db_manager)
        if "pull requests" in selected_data:
            fetch_pull_requests(self.db_manager, repo, self.storage_manager)
        if "issues" in selected_data:
            fetch_issues(self.db_manager, repo)
        # TODO manage main_files and last_release_files !!!

    def update_multiple_repos_specific_data(self, repos: List[str], selected_data: List[str]):
        """
        Updates selected data types for multiple repositories.

        Args:
            repos (List[str]): List of repositories to update.
            selected_data (List[str]): Data types to update.
        """
        for repo in repos:
            print(f"🔄 Updating {selected_data} for {repo}...")
            self.update_specific_data(repo, selected_data)
        
        print("✅ Multi-repo updates completed.")

    def fetch_repositories(self) -> List[str]:
        """
        Retrieves a list of repositories for the GitHub organization.

        Returns:
            List[str]: List of repository names.
        """
        url = f"https://api.github.com/orgs/{self.github_org}/repos?per_page=100"
        data = github_request(url)

        if not data:
            print(f"❌ Failed to fetch repositories for {self.github_org}")
            return []

        return [repo["full_name"] for repo in data]

    def fetch_repository_info(self, repo: str):
        """
        Fetches repository metadata.

        Args:
            repo (str): GitHub repository to fetch metadata for.
        """
        url = f"https://api.github.com/repos/{repo}"
        data = github_request(url)

        if not data:
            print(f"❌ Failed to fetch repository info for {repo}")
            return

        repo_entry = {
            "_id": repo,
            "description": data.get("description", ""),
            "language": data.get("language", ""),
            "url": data.get("html_url", ""),
            "last_commit_date": data.get("updated_at", ""),
        }

        self.db_manager.db.repositories.update_one({"_id": repo}, {"$set": repo_entry}, upsert=True)
        print(f"✅ Repository info updated for {repo}.")
