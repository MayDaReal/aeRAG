"""
github_issues.py
Handles fetching and storing GitHub issues into MongoDB.
"""

import pymongo
from collectors.github_request import github_request
from core.database_manager import DatabaseManager


def fetch_issues(db_manager: DatabaseManager, repo: str) -> None:
    """
    Fetches GitHub issues for a repository and stores them in MongoDB.

    Args:
        db_manager (DatabaseManager): Instance of DatabaseManager for MongoDB access.
        repo (str): The GitHub repository (e.g., 'org/repo').
    """
    page = 1

    while True:
        url = f"https://api.github.com/repos/{repo}/issues?state=all&per_page=100&page={page}"
        data = github_request(url)

        if not data:
            break  # Stop if an error occurs or there are no more issues

        issues = []
        bulk_operations = []
        inserted_issue_ids = set()

        for issue in data:
            if 'pull_request' in issue:
                continue  # Ignore PRs, we only want actual issues

            issue_id = f"{repo}_{issue['number']}"
            existing_issue = db_manager.db.issues.find_one({'_id': issue_id})

            issue_data = {
                '_id': issue_id,
                'repo': repo,
                'number': issue['number'],
                'metadata_id': None,
                'title': issue['title'],
                'body': issue.get('body', ''),
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

        if issue.get("comments", 0) > 0:  # Only fetch comments if they exist
            fetch_issue_comments(db_manager, repo, issue["number"])

        # Bulk insert for new issues
        if issues:
            db_manager.db.issues.insert_many(issues)

        # Bulk update existing issues
        if bulk_operations:
            db_manager.db.issues.bulk_write(
                [pymongo.UpdateOne(q, u) for q, u in bulk_operations]
            )

        print(f"✅ Issues fetched and stored for {repo} (Page {page})")
        page += 1

def fetch_issue_comments(db_manager, repo: str, issue_number: int):
    """
    Fetches all comments for a given issue and stores them in MongoDB.

    Args:
        db_manager (DatabaseManager): MongoDB database manager.
        repo (str): Repository name.
        issue_number (int): Issue number.
        github_token (str): GitHub API token.
    """
    url = f"https://api.github.com/repos/{repo}/issues/{issue_number}/comments"
    comments_data = github_request(url)

    if not comments_data:
        print(f"⚠️ No comments found or failed request for PR {repo}_{issue_number}.")
        return

    comments_to_insert = []
    for comment in comments_data:
        comment_id = comment["id"]

        # Check if comment already exists in the database
        existing_comment = db_manager.db.issues_comments.find_one({"_id": comment_id})

        # If comment exists, check if an update is needed
        if existing_comment:
            if existing_comment["comment_body"] != comment["body"]:
                db_manager.db.issues_comments.update_one(
                    {"_id": f"{repo}_{issue_number}_{comment_id}"},
                    {"$set": {"comment_body": comment["body"], "updated_at": comment["updated_at"]}}
                )
                print(f"🔄 Updated comment {comment_id} for PR {repo}#{issue_number}.")
        else:
            # If comment does not exist, prepare for insertion
            comment_obj = {
                "_id": f"{repo}_{issue_number}_{comment_id}",
                "repo": repo,
                "issue_id": f"{issue_number}",
                "comment_body": comment["body"],
                "author": comment["user"]["login"],
                "created_at": comment["created_at"],
                "updated_at": comment.get("updated_at", comment["created_at"])  # Use created_at if updated_at is missing
            }
            comments_to_insert.append(comment_obj)

    # Bulk insert new comments
    if comments_to_insert:
        db_manager.db.issues_comments.insert_many(comments_to_insert)
        print(f"✅ Stored {len(comments_to_insert)} new comments for PR {repo}#{issue_number}.")
