"""
metadata_utils.py
Provides utility functions for metadata processing.
"""

import hashlib
from langdetect import detect

def detect_file_type(filename: str) -> str:
    """
    Detects the type of a file based on its extension.

    Args:
        filename (str): The filename with extension.

    Returns:
        str: The detected file type (e.g., "code", "doc", "config").
    """
    extension_mapping = {
        "code": ["py", "js", "ts", "java", "c", "cpp", "h", "hpp", "cs", "go", "rb", "rs", "php", "swift", "kt", "ex", "exs"],
        "doc": ["md", "rst", "txt", "pdf", "doc", "docx"],
        "config": ["json", "yaml", "yml", "toml", "ini", "xml"],
        "log": ["log", "csv"],
        "binary": ["png", "jpg", "jpeg", "gif", "bmp", "svg", "mp3", "mp4", "mov", "avi", "zip", "tar", "gz", "7z", "rar", "mmdb", ".ico"],
        "unknown": []
    }
    
    ext = filename.split(".")[-1].lower()
    for category, extensions in extension_mapping.items():
        if ext in extensions:
            return category
    return "unknown"

def detect_programming_language(extension: str) -> str:
    """
    Detects the programming language based on file extension.

    Args:
        extension (str): File extension.

    Returns:
        str: The programming language detected.
    """
    language_mapping = {
        "python": ["py"],
        "javascript": ["js", "ts"],
        "solidity": ["sol"],
        "java": ["java"],
        "c": ["c", "h"],
        "cpp": ["cpp", "hpp"],
        "csharp": ["cs"],
        "go": ["go"],
        "ruby": ["rb"],
        "rust": ["rs"],
        "php": ["php"],
        "swift": ["swift"],
        "kotlin": ["kt"],
        "json": ["json"],
        "yaml": ["yaml", "yml"],
        "toml": ["toml"],
        "xml": ["xml"],
        "markdown": ["md", "rst", "txt"],
        "elixir" : ["exs", "ex"]
    }
    
    # Check using file extension
    for lang, extensions in language_mapping.items():
        if extension in extensions:
            return lang
        
    return "unknown"
    
def detect_natural_language(text):
    """
    Detects the natural language of a given text (English, French, etc.).
    """
    try:
        return detect(text)
    except:
        return "unknown"

def compute_file_hash(content: str) -> str:
    """
    Computes a SHA-256 hash for a file based on its content.

    Args:
        content (str): The file content.

    Returns:
        str: The computed hash.
    """
    return hashlib.sha256(content.encode("utf-8")).hexdigest()

def compute_file_hash_md5(content: str) -> str:
    """
    Computes a MD5 hash for a file based on its content.

    Args:
        content (str): The file content.

    Returns:
        str: The computed hash md5.
    """
    return hashlib.md5(content.encode("utf-8")).hexdigest()
