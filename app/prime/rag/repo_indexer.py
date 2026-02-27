"""
PRIME Repo Indexer
File: app/prime/rag/repo_indexer.py

Builds a complete map of the entire codebase.
Once indexed, PRIME knows every file that exists -- its path, size,
language, and full contents -- without being told.

Index is stored at: primelogs/repo_index.json
PRIME's system prompt is enriched with the repo map on every call.

Usage:
    POST /prime/repo/index   -- Build or rebuild the index
    GET  /prime/repo/status  -- Check index status
    GET  /prime/repo/map     -- Get the full file tree
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any

# Project root
PROJECT_ROOT = Path(os.environ.get(
    "PROJECT_ROOT",
    Path(__file__).resolve().parent.parent.parent.parent,
)).resolve()

# Index storage
INDEX_PATH = Path(os.environ.get(
    "PRIME_INDEX_PATH",
    PROJECT_ROOT / "primelogs" / "repo_index.json",
))
INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)

# What to index
INDEXED_EXTENSIONS = {
    ".py", ".ts", ".tsx", ".js", ".jsx",
    ".json", ".yaml", ".yml", ".toml",
    ".md", ".txt", ".sql", ".ps1", ".sh",
    ".env.example", ".gitignore", ".dockerignore",
}

SKIP_DIRS = {
    "__pycache__", ".git", ".venv", "venv", "node_modules",
    ".next", "dist", "build", ".mypy_cache", ".pytest_cache",
    "primelogs", "data", ".ruff_cache",
}

MAX_FILE_SIZE = 80_000  # 80KB per file
MAX_CONTENT_IN_INDEX = 6_000  # Store first 6KB of content per file in index

EXTENSION_LANGUAGE_MAP = {
    ".py": "Python", ".ts": "TypeScript", ".tsx": "TypeScript/React",
    ".js": "JavaScript", ".jsx": "JavaScript/React",
    ".json": "JSON", ".yaml": "YAML", ".yml": "YAML",
    ".toml": "TOML", ".sql": "SQL", ".md": "Markdown",
    ".ps1": "PowerShell", ".sh": "Bash", ".txt": "Text",
}


# ---------------------------------------------------------------------------
# INDEXING
# ---------------------------------------------------------------------------

def build_index(verbose: bool = False) -> Dict[str, Any]:
    """
    Walk the entire codebase and build a file index.
    Returns the index dict and saves it to disk.
    """
    files: Dict[str, Dict] = {}
    skipped: List[str] = []
    errors: List[str] = []

    for file_path in sorted(PROJECT_ROOT.rglob("*")):
        # Skip directories
        if file_path.is_dir():
            continue

        # Skip unwanted dirs
        parts = set(file_path.relative_to(PROJECT_ROOT).parts)
        if parts & SKIP_DIRS:
            continue

        # Skip unwanted extensions
        if file_path.suffix not in INDEXED_EXTENSIONS:
            continue

        rel_path = str(file_path.relative_to(PROJECT_ROOT))

        try:
            size = file_path.stat().st_size
            if size > MAX_FILE_SIZE:
                skipped.append(f"{rel_path} (too large: {size:,} bytes)")
                continue

            content = file_path.read_text(encoding="utf-8", errors="replace")
            line_count = content.count("\n") + 1
            language = EXTENSION_LANGUAGE_MAP.get(file_path.suffix, file_path.suffix)

            # Extract key symbols (def, class, function, const, interface)
            symbols = _extract_symbols(content, file_path.suffix)

            files[rel_path] = {
                "path": rel_path,
                "language": language,
                "size": size,
                "lines": line_count,
                "symbols": symbols,
                "preview": content[:MAX_CONTENT_IN_INDEX],
                "truncated": len(content) > MAX_CONTENT_IN_INDEX,
            }

            if verbose:
                print(f"  Indexed: {rel_path} ({line_count} lines)")

        except Exception as e:
            errors.append(f"{rel_path}: {e}")

    index = {
        "built_at": datetime.now(timezone.utc).isoformat(),
        "project_root": str(PROJECT_ROOT),
        "file_count": len(files),
        "skipped_count": len(skipped),
        "error_count": len(errors),
        "skipped": skipped,
        "errors": errors,
        "files": files,
    }

    INDEX_PATH.write_text(json.dumps(index, indent=2), encoding="utf-8")
    return index


def load_index() -> Dict[str, Any] | None:
    """Load the index from disk. Returns None if not built yet."""
    if not INDEX_PATH.exists():
        return None
    try:
        return json.loads(INDEX_PATH.read_text(encoding="utf-8"))
    except Exception:
        return None


def index_status() -> Dict[str, Any]:
    """Return index metadata without loading all file contents."""
    idx = load_index()
    if not idx:
        return {"status": "not_built", "message": "Run POST /prime/repo/index to build the index."}
    return {
        "status": "ready",
        "built_at": idx["built_at"],
        "file_count": idx["file_count"],
        "skipped_count": idx["skipped_count"],
        "error_count": idx["error_count"],
        "index_path": str(INDEX_PATH),
    }


def get_file_map() -> List[Dict]:
    """Return the file tree without content (just paths, languages, sizes)."""
    idx = load_index()
    if not idx:
        return []
    return [
        {
            "path": f["path"],
            "language": f["language"],
            "lines": f["lines"],
            "symbols": f["symbols"],
        }
        for f in idx["files"].values()
    ]


def search_index(query: str, top_k: int = 8) -> List[Dict]:
    """
    Keyword search over the indexed codebase.
    Returns the top_k most relevant files based on term frequency.
    """
    idx = load_index()
    if not idx:
        return [{"error": "Index not built. Run POST /prime/repo/index first."}]

    query_terms = query.lower().split()
    scored: List[tuple] = []

    for path, file_data in idx["files"].items():
        content = file_data.get("preview", "").lower()
        symbols_text = " ".join(file_data.get("symbols", [])).lower()
        combined = content + " " + symbols_text

        score = sum(combined.count(term) for term in query_terms)
        if score > 0:
            scored.append((score, path, file_data))

    scored.sort(key=lambda x: x[0], reverse=True)

    results = []
    for score, path, file_data in scored[:top_k]:
        results.append({
            "path": path,
            "language": file_data["language"],
            "lines": file_data["lines"],
            "symbols": file_data["symbols"],
            "score": score,
            "preview": file_data["preview"][:2000],  # First 2KB in search results
        })

    return results


def build_repo_context_for_prime() -> str:
    """
    Build a compact repo map string to inject into PRIME's system prompt.
    PRIME gets a full picture of what exists before answering.
    """
    idx = load_index()
    if not idx:
        return "[REPO INDEX NOT BUILT -- run POST /prime/repo/index]"

    lines = [
        f"CODEBASE MAP (indexed {idx['built_at'][:10]}, {idx['file_count']} files):",
        "Use read_file(path) to read any of these files in full.",
        "",
    ]

    # Group by top-level directory
    by_dir: Dict[str, List[str]] = {}
    for path, file_data in idx["files"].items():
        top_dir = path.split("/")[0] if "/" in path else "root"
        if top_dir not in by_dir:
            by_dir[top_dir] = []
        symbols = ", ".join(file_data["symbols"][:5])
        symbol_hint = f" [{symbols}]" if symbols else ""
        by_dir[top_dir].append(f"  {path} ({file_data['language']}, {file_data['lines']} lines){symbol_hint}")

    for dir_name in sorted(by_dir):
        lines.append(f"{dir_name}/")
        lines.extend(by_dir[dir_name])
        lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# SYMBOL EXTRACTION
# ---------------------------------------------------------------------------

def _extract_symbols(content: str, ext: str) -> List[str]:
    """Extract top-level function/class names from file content."""
    symbols = []
    try:
        if ext == ".py":
            for line in content.splitlines()[:200]:
                s = line.strip()
                if s.startswith("def ") or s.startswith("async def "):
                    name = s.split("def ", 1)[-1].split("(")[0].strip()
                    symbols.append(name)
                elif s.startswith("class "):
                    name = s.split("class ", 1)[-1].split("(")[0].split(":")[0].strip()
                    symbols.append(f"class:{name}")
        elif ext in (".ts", ".tsx", ".js", ".jsx"):
            for line in content.splitlines()[:200]:
                s = line.strip()
                if "function " in s or "const " in s or "export default" in s:
                    if "(" in s:
                        part = s.split("function ")[-1].split("const ")[-1]
                        name = part.split("(")[0].split("=")[0].strip()
                        if name and len(name) < 40:
                            symbols.append(name)
    except Exception:
        pass
    return symbols[:15]  # Cap at 15 symbols per file
