"""
build_index.py
---------------
Small CLI helper to build (or rebuild) a Faiss index for a given
<repo, collection_src> pair.
It wraps *FaissIndexManager* so that you can trigger indexing from
terminal or CI without opening a Python shell.

Usage examples
~~~~~~~~~~~~~~
$ python build_index.py --repo archethic-foundation/archethic-node \
                        --collection commits

$ python build_index.py --repo archethic-foundation/archethic-node \
                        --collection main_files --force

Environment
~~~~~~~~~~~
The script relies on the same .env variables as the rest of the project:
- ``MONGO_URI``   : connection string (default: mongodb://localhost:27017)
- ``DB_NAME``     : database name      (default: archethic_github_test_data)

If you pass ``--verbose`` it prints a couple of progress messages.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
from typing import NoReturn

from dotenv import load_dotenv

# Local imports – project root must be in PYTHONPATH when running
from core.database_manager import DatabaseManager
from core.faiss_index_manager import FaissIndexManager

# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------

def _parse_args() -> argparse.Namespace:
    """
    Define and parse command-line arguments for the script.

    Returns:
        argparse.Namespace: Parsed arguments from sys.argv
    """
    parser = argparse.ArgumentParser(
        description="Build or rebuild a Faiss index for a given repo and collection.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        "--repo",
        required=True,
        help="Full GitHub repository name, e.g. archethic-foundation/archethic-node",
    )
    parser.add_argument(
        "--collection",
        required=True,
        choices=[
            "files",
            "main_files",
            "last_release_files",
            "commits",
            "pull_requests",
            "issues",
        ],
        help="Name of the source collection to index.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Rebuild index even if it already exists.",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable extra logging output.",
    )

    return parser.parse_args()

# ---------------------------------------------------------------------------
# Main logic
# ---------------------------------------------------------------------------

def _main() -> None:
    """
    Entry point executed when the script is run directly from CLI.
    """
    args = _parse_args()

    # Load environment variables from .env file (optional)
    load_dotenv()
    mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    db_name   = os.getenv("DB_NAME", "archethic_github_test_data")

    if args.verbose:
        print("[build_index] Connecting to MongoDB ...", file=sys.stderr)

    # Initialize database and index manager
    db = DatabaseManager(mongo_uri, db_name, create_indexes=False)
    idx_mgr = FaissIndexManager(db)

    if args.verbose:
        print(
            f"[build_index] Building index: repo={args.repo}, collection={args.collection}",
            file=sys.stderr,
        )

    # Build the index and close DB connection afterward
    try:
        idx_mgr.build_index(args.repo, args.collection, force=args.force)
    finally:
        db.close_connection()

    if args.verbose:
        print("[build_index] Done.", file=sys.stderr)

# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    _main()
