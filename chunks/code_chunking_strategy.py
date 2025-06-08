from .abstract_chunking_strategy import AbstractChunkingStrategy
from typing import List, Dict, Any
import re

class CodeChunkingStrategy(AbstractChunkingStrategy):
    """Chooses the best chunking strategy based on the detected programming language."""
    def __init__(self, extension: str = ""
                , language: str = ""
                , min_chunk_size: int = 300
                , chunk_size: int = 1000
                , overlap: int = 200):
        
        self.extension = extension
        self.language = language
        self.min_chunk_size = min_chunk_size
        self.chunk_size = chunk_size
        self.overlap = overlap

    def __init__(self, settings: Dict[str, Any]):
        self.extension = settings.get("extension", "")
        self.language = settings.get("language", "")
        self.min_chunk_size = settings.get("min_chunk_size", 300)
        self.chunk_size = settings.get("chunk_size", 1000)
        self.overlap= settings.get("overlap", 200)
        
    def chunk(self, content: str) -> List[str]:
        """Chooses the best chunking strategy based on the detected programming language."""
        chunking_functions = {
            "python": self.chunk_python,
            "typescript": self.chunk_javascript,
            "javascript": self.chunk_javascript,
            "nodejs": self.chunk_javascript,
            "dart": self.chunk_dart,
            "elixir": self.chunk_elixir,
            "html": self.chunk_html_css,
            "css": self.chunk_html_css,
            "go": self.chunk_go,
            "c": self.chunk_c_cpp,
            "cpp": self.chunk_c_cpp,
            "ruby": self.chunk_ruby
        }
        
        if self.language in chunking_functions:
            return chunking_functions[self.language](content, self.min_chunk_size)
        
        # no programming langage managed, use default chunk_text
        return self.chunk_text(content, self.chunk_size, self.overlap)

    def chunk_text(self, text, chunk_size=1000, overlap=200):
        """Splits text into overlapping chunks for optimal retrieval."""
        chunks = []
        for i in range(0, len(text), chunk_size - overlap):
            chunks.append(text[i:i + chunk_size])
        return chunks

    def chunk_python(self, content, min_chunk_size=300):
        """Chunks Python code by function, class, and imports while keeping context."""
        lines = content.split("\n")
        chunks, chunk = [], []
        imports = []

        for line in lines:
            stripped = line.strip()

            if stripped.startswith(("import ", "from ")):
                imports.append(line)
                continue

            if re.match(r"^(class |def )", stripped):
                if chunk and len("\n".join(chunk)) > min_chunk_size:
                    chunks.append("\n".join(chunk))
                    chunk = []

            chunk.append(line)

        if chunk:
            chunks.append("\n".join(chunk))

        if chunks and imports:
            chunks[0] = "\n".join(imports) + "\n" + chunks[0]

        return chunks

    def chunk_javascript(self, content, min_chunk_size=300):
        """Chunks JavaScript, TypeScript, and Node.js while keeping imports at the top."""
        lines = content.split("\n")
        chunks, chunk = [], []
        imports = []

        for line in lines:
            stripped = line.strip()

            if re.match(r"^(import |export |require\()", stripped):
                imports.append(line)
                continue

            if re.match(r"^(export\s+)?(function|class)\s", stripped):
                if chunk and len("\n".join(chunk)) > min_chunk_size:
                    chunks.append("\n".join(chunk))
                    chunk = []

            chunk.append(line)

        if chunk:
            chunks.append("\n".join(chunk))

        if chunks and imports:
            chunks[0] = "\n".join(imports) + "\n" + chunks[0]

        return chunks

    def chunk_dart(self, content, min_chunk_size=300):
        """Chunks Dart code while keeping import statements at the top."""
        lines = content.split("\n")
        chunks, chunk = [], []
        imports = []

        for line in lines:
            stripped = line.strip()

            if stripped.startswith("import "):
                imports.append(line)
                continue

            if stripped.startswith("@override") or re.match(r"^(class |void |final |Future<)", stripped):
                if chunk and len("\n".join(chunk)) > min_chunk_size:
                    chunks.append("\n".join(chunk))
                    chunk = []

            chunk.append(line)

        if chunk:
            chunks.append("\n".join(chunk))

        if chunks and imports:
            chunks[0] = "\n".join(imports) + "\n" + chunks[0]

        return chunks

    def chunk_elixir(self, content, min_chunk_size=300):
        """Chunks Elixir code by modules and functions."""
        lines = content.split("\n")
        chunks, chunk = [], []

        for line in lines:
            stripped = line.strip()

            if stripped.startswith(("defmodule ", "def ", "defp ")):
                if chunk and len("\n".join(chunk)) > min_chunk_size:
                    chunks.append("\n".join(chunk))
                    chunk = []

            chunk.append(line)

        if chunk:
            chunks.append("\n".join(chunk))

        return chunks

    def chunk_html_css(self, content, min_chunk_size=300):
        """Chunks HTML and CSS files by sections and selectors."""
        lines = content.split("\n")
        chunks, chunk = [], []

        for line in lines:
            stripped = line.strip()

            if stripped.startswith("<") or stripped.startswith("{"):
                if chunk and len("\n".join(chunk)) > min_chunk_size:
                    chunks.append("\n".join(chunk))
                    chunk = []

            chunk.append(line)

        if chunk:
            chunks.append("\n".join(chunk))

        return chunks

    def chunk_go(self, content, min_chunk_size=300):
        """Chunks Go code while keeping package and import statements at the top."""
        lines = content.split("\n")
        chunks, chunk = [], []
        imports = []

        for line in lines:
            stripped = line.strip()

            if stripped.startswith("package "):
                imports.append(line)
                continue

            if stripped.startswith("import "):
                imports.append(line)
                continue

            if stripped.startswith("func "):
                if chunk and len("\n".join(chunk)) > min_chunk_size:
                    chunks.append("\n".join(chunk))
                    chunk = []

            chunk.append(line)

        if chunk:
            chunks.append("\n".join(chunk))

        if chunks and imports:
            chunks[0] = "\n".join(imports) + "\n" + chunks[0]

        return chunks

    def chunk_c_cpp(self, content, min_chunk_size=300):
        """Chunks C/C++ code while keeping #include statements at the top."""
        lines = content.split("\n")
        chunks, chunk = [], []
        includes = []

        for line in lines:
            stripped = line.strip()

            if stripped.startswith("#include"):
                includes.append(line)
                continue

            if re.match(r"^(void |int |char |float |double )", stripped):
                if chunk and len("\n".join(chunk)) > min_chunk_size:
                    chunks.append("\n".join(chunk))
                    chunk = []

            chunk.append(line)

        if chunk:
            chunks.append("\n".join(chunk))

        if chunks and includes:
            chunks[0] = "\n".join(includes) + "\n" + chunks[0]

        return chunks

    def chunk_ruby(self, content, min_chunk_size=300):
        """Chunks Ruby code while keeping require statements at the top."""
        lines = content.split("\n")
        chunks, chunk = [], []
        requires = []

        for line in lines:
            stripped = line.strip()

            if stripped.startswith("require "):
                requires.append(line)
                continue

            if re.match(r"^(class |module |def )", stripped):
                if chunk and len("\n".join(chunk)) > min_chunk_size:
                    chunks.append("\n".join(chunk))
                    chunk = []

            chunk.append(line)

        if chunk:
            chunks.append("\n".join(chunk))

        if chunks and requires:
            chunks[0] = "\n".join(requires) + "\n" + chunks[0]

        return chunks