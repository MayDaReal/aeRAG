"""
cli_helpers.py
~~~~~~~~~~~~~~
Utility functions to streamline interactive CLI prompts for
RAG commands and menu scripts.
"""

from typing import List, Dict

# Constants shared by all CLI commands
COLLECTION_CHOICES = {
        "1": "files",
        "2": "main_files",
        "3": "last_release_files",
        "4": "commits",
        "5": "pull_requests",
        "6": "issues"
    }

def select_collection_interactively() -> list[str]:
    """
    Prompt user to select one or more collections to operate on.
    Returns:
        A list like ["commits", ...]
    """
    print("\nAvailable collections:")
    for key, value in COLLECTION_CHOICES.items():
        print(f"{key}) {value}")

    choices = input("Enter numbers separated by spaces (e.g., '1 3'): ").split()

    selected_data = [COLLECTION_CHOICES[choice] for choice in choices if choice in COLLECTION_CHOICES]
    return selected_data

def ask_top_k(default: int = 5) -> int:
    """Prompt for top-K parameter, fallback to default if empty or invalid."""
    raw = input(f"Top-K (default {default}): ").strip()
    return int(raw) if raw.isdigit() else default

def ask_repo(default_repo: str = "") -> str:
    """Prompt for repo name unless default provided."""
    if default_repo:
        return default_repo
    return input("GitHub repo (e.g. org/repo): ").strip()

def ask_question() -> str:
    """Prompt the user to enter a free-form question."""
    return input("Your question: ").strip()
