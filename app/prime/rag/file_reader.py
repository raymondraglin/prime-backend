"""
PRIME RAG File Reader
File: app/prime/rag/file_reader.py

Gives PRIME the ability to read files from the actual codebase at runtime.
This closes the RAG gap -- PRIME is no longer blind to files not in his prompt.

Security:
  - All paths are resolved and validated against PROJECT_ROOT
  - Path traversal is blocked
  - Only allowed file extensions are readable
  - Max file size enforced
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Dict, List

# Project root = prime-backend directory
PROJECT_ROOT = Path(os.environ.get(
    "PROJECT_ROOT",
    Path(__file__).resolve().parent.parent.parent.parent,
)).resolve()

ALLOWED_EXTENSIONS = {
    ".py", ".ts", ".tsx", ".js", ".jsx",
    ".json", ".yaml", ".yml", ".toml", ".cfg", ".ini",
    ".md", ".txt", ".sql", ".ps1", ".sh",
    ".env.example", ".gitignore", ".dockerignore",
}

MAX_FILE_SIZE = 60_000  # 60KB per file


def _safe_resolve(path: str) -> Path | None:
    """Resolve path relative to PROJECT_ROOT. Returns None if unsafe."""
    try:
        full = (PROJECT_ROOT / path).resolve()
        if not str(full).startswith(str(PROJECT_ROOT)):
            return None
        return full
    except Exception:
        return None


def read_file(path: str) -> Dict:
    """
    Read a file from the codebase.
    Returns {content, path, size, lines} or {error, path}.
    """
    full = _safe_resolve(path)
    if full is None:
        return {"error": "Path traversal blocked.", "path": path}
    if not full.exists():
        return {"error": f"File not found: {path}", "path": path}
    if full.is_dir():
        return {"error": f"{path} is a directory. Use list_directory instead.", "path": path}
    if full.suffix not in ALLOWED_EXTENSIONS:
        return {"error": f"Extension '{full.suffix}' not allowed.", "path": path}

    size = full.stat().st_size
    if size > MAX_FILE_SIZE:
        return {"error": f"File too large ({size:,} bytes). Max {MAX_FILE_SIZE:,}.", "path": path}

    try:
        content = full.read_text(encoding="utf-8", errors="replace")
        return {
            "content": content,
            "path": path,
            "size": size,
            "lines": content.count("\n") + 1,
        }
    except Exception as e:
        return {"error": str(e), "path": path}


def list_directory(path: str = ".") -> Dict:
    """
    List files and subdirectories at the given path.
    Returns {path, files: [...], directories: [...]} or {error}.
    """
    full = _safe_resolve(path)
    if full is None:
        return {"error": "Path traversal blocked."}
    if not full.exists():
        return {"error": f"Directory not found: {path}"}
    if not full.is_dir():
        return {"error": f"{path} is a file. Use read_file instead."}

    try:
        files: List[Dict] = []
        directories: List[Dict] = []

        for item in sorted(full.iterdir()):
            if item.name.startswith(".") or item.name == "__pycache__":
                continue
            rel = str(item.relative_to(PROJECT_ROOT))
            if item.is_file() and item.suffix in ALLOWED_EXTENSIONS:
                files.append({"name": item.name, "path": rel, "size": item.stat().st_size})
            elif item.is_dir():
                directories.append({"name": item.name, "path": rel})

        return {"path": path, "files": files, "directories": directories}
    except Exception as e:
        return {"error": str(e)}


def search_codebase(query: str, directory: str = "app", file_extension: str = ".py") -> Dict:
    """
    Search all files under directory for lines containing query.
    Returns top 10 matching files with matching line previews.
    """
    full = _safe_resolve(directory)
    if full is None:
        return {"error": "Path traversal blocked."}
    if not full.exists():
        return {"error": f"Directory not found: {directory}"}

    results = []
    query_lower = query.lower()

    for file_path in sorted(full.rglob(f"*{file_extension}")):
        if "__pycache__" in str(file_path):
            continue
        if file_path.stat().st_size > MAX_FILE_SIZE:
            continue
        try:
            content = file_path.read_text(encoding="utf-8", errors="replace")
            if query_lower not in content.lower():
                continue
            matching_lines = []
            for i, line in enumerate(content.splitlines(), 1):
                if query_lower in line.lower():
                    matching_lines.append({"line": i, "content": line.strip()})
                    if len(matching_lines) >= 6:
                        break
            results.append({
                "path": str(file_path.relative_to(PROJECT_ROOT)),
                "match_count": len(matching_lines),
                "lines": matching_lines,
            })
            if len(results) >= 10:
                break
        except Exception:
            continue

    return {"query": query, "directory": directory, "results": results}
