"""
github_pull_requests.py
Handles fetching and storing GitHub Pull Requests into MongoDB.
"""

from typing import List
import pymongo
from collectors.github_request import github_request
from core.database_manager import DatabaseManager
from core.file_storage_manager import FileStorageManager


def fetch_pull_requests(db_manager: DatabaseManager, repo: str, storage_manager: FileStorageManager) -> None:
    """
    Fetches GitHub Pull Requests for a repository and stores them in MongoDB.

    Args:
        db_manager (DatabaseManager): Instance of DatabaseManager for MongoDB access.
        repo (str): The GitHub repository (e.g., 'org/repo').
        storage_manager (FileStorageManager): Manages the storage of large PR bodies.
    """
    page = 1

    while True:
        url = f"https://api.github.com/repos/{repo}/pulls?state=all&per_page=100&page={page}"
        data = github_request(url)

        if not data:
            break  # Stop if an error occurs or there are no more PRs

        prs = []
        bulk_operations = []
        inserted_pr_ids = set()

        for pr in data:
            pr_id = f"{repo}_{pr['number']}"
            existing_pr = db_manager.db.pull_requests.find_one({'_id': pr_id})

            # Stocke le corps du PR en local (évite de surcharger MongoDB)
            body_url = None
            if pr.get("body"):
                body_url = storage_manager.store_file_content(
                    pr["body"], repo, f"pr_{pr['number']}", "_body.txt"
                )

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
                'commits': fetch_pr_commits(db_manager, repo, pr['number']),
                'metadata_id': None,
                'body_url': body_url,
                'labels': [label['name'] for label in pr.get('labels', [])],
                'url': pr['html_url']
            }

            if pr.get("comments", 0) > 0:  # Only fetch comments if they exist
                fetch_pull_request_comments(db_manager, repo, pr["number"])

            if not existing_pr and pr_id not in inserted_pr_ids:
                prs.append(pr_data)
                inserted_pr_ids.add(pr_id)
            elif existing_pr and existing_pr['updated_at'] != pr['updated_at']:
                bulk_operations.append(({'_id': pr_data['_id']}, {'$set': pr_data}))

        # Bulk insert for new PRs
        if prs:
            db_manager.db.pull_requests.insert_many(prs)

        # Bulk update existing PRs
        if bulk_operations:
            db_manager.db.pull_requests.bulk_write(
                [pymongo.UpdateOne(q, u) for q, u in bulk_operations]
            )

        print(f"✅ Pull Requests fetched and stored for {repo} (Page {page})")
        page += 1


def fetch_pr_commits(db_manager: DatabaseManager, repo: str, pr_number: int) -> List[str]:
    """
    Retrieves commits linked to a Pull Request (PR) by checking only those present in the `commits` collection.
    If a commit is not in the database, it is assumed not to be part of the `main` branch.

    Args:
        db_manager (DatabaseManager): Instance to interact with MongoDB.
        repo (str): The GitHub repository (e.g., 'org/repo').
        pr_number (int): The pull request number.

    Returns:
        List[str]: A list of commit SHAs associated with the PR.
    """
    url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}/commits?per_page=100"
    pr_commits = github_request(url)

    if not pr_commits:
        return []

    commit_shas = [commit["sha"] for commit in pr_commits]

    existing_commits = set(
        doc["_id"] for doc in db_manager.db.commits.find({"_id": {"$in": commit_shas}}, {"_id": 1})
    )

    valid_commit_ids = [sha for sha in commit_shas if sha in existing_commits]

    return valid_commit_ids

def fetch_pull_request_comments(db_manager, repo: str, pr_number: int):
    """
    Fetches all comments for a given pull request and stores or updates them in MongoDB.

    Args:
        db_manager (DatabaseManager): MongoDB database manager.
        repo (str): Repository name.
        pr_number (int): Pull request number.
        github_token (str): GitHub API token.
    """
    url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}/comments"
    comments_data = github_request(url)

    if not comments_data:
        print(f"⚠️ No comments found or failed request for PR {repo}#{pr_number}.")
        return

    comments_to_insert = []
    for comment in comments_data:
        comment_id = comment["id"]

        # Check if comment already exists in the database
        existing_comment = db_manager.db.pull_requests_comments.find_one({"_id": comment_id})

        # If comment exists, check if an update is needed
        if existing_comment:
            if existing_comment["comment_body"] != comment["body"]:
                db_manager.db.pull_requests_comments.update_one(
                    {"_id": f"{repo}_{pr_number}_{comment_id}"},
                    {"$set": {"comment_body": comment["body"], "updated_at": comment["updated_at"]}}
                )
                print(f"🔄 Updated comment {comment_id} for PR {repo}#{pr_number}.")
        else:
            # If comment does not exist, prepare for insertion
            comment_obj = {
                "_id": f"{repo}_{pr_number}_{comment_id}",
                "repo": repo,
                "pr_id": f"{pr_number}",
                "comment_body": comment["body"],
                "author": comment["user"]["login"],
                "created_at": comment["created_at"],
                "updated_at": comment.get("updated_at", comment["created_at"])  # Use created_at if updated_at is missing
            }
            comments_to_insert.append(comment_obj)

    # Bulk insert new comments
    if comments_to_insert:
        db_manager.db.pull_requests_comments.insert_many(comments_to_insert)
        print(f"✅ Stored {len(comments_to_insert)} new comments for PR {repo}#{pr_number}.")


