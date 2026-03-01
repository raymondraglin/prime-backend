# app/prime/academic/indexer.py
"""
PRIME Academic Corpus Indexer

Walks external_corpus/ and chunks all text files into retrievable passages.

Directory convention:
  external_corpus/
    {domain}/          -- e.g. cs_ict, math, healthcare, law
      textbooks/
        *.txt
      papers/
        *.txt
      notes/
        *.md

Chunking:
  - CHUNK_SIZE = 600 characters
  - OVERLAP    = 100 characters
  - Skips files > 5MB
  - Skips binary and non-text extensions

Index is built lazily on first call and cached in module memory.
Call get_corpus_chunks(rebuild=True) to force a fresh scan.

Each chunk carries:
  id           -- unique slug: {file_stem}_{chunk_index}
  text         -- the passage text
  source_path  -- path relative to PROJECT_ROOT (forward slashes)
  title        -- human-readable file name (underscores -> spaces, title case)
  domain       -- top-level folder under external_corpus/
  chunk_index  -- position within the source file
  citation_type -- always 'corpus' (used by extractor.py)
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Iterator

PROJECT_ROOT = Path(os.environ.get(
    "PROJECT_ROOT",
    Path(__file__).resolve().parent.parent.parent.parent,
)).resolve()

CORPUS_ROOT    = PROJECT_ROOT / "external_corpus"
CHUNK_SIZE     = 600
OVERLAP        = 100
MAX_FILE_BYTES = 5_000_000
ALLOWED_SUFFIXES = {".txt", ".md", ".rst", ".csv", ".tex"}


def _iter_corpus_files(domain: str | None = None) -> Iterator[Path]:
    """Yield readable text files from external_corpus/ (or a subdomain)."""
    if not CORPUS_ROOT.exists():
        return
    root = CORPUS_ROOT / domain if domain else CORPUS_ROOT
    if not root.exists():
        return
    for path in sorted(root.rglob("*")):
        if (
            path.is_file()
            and path.suffix.lower() in ALLOWED_SUFFIXES
            and not path.name.startswith(".")
            and path.stat().st_size < MAX_FILE_BYTES
        ):
            yield path


def _infer_domain(path: Path) -> str:
    """Infer the corpus domain from the path hierarchy."""
    try:
        parts = path.relative_to(CORPUS_ROOT).parts
        return parts[0] if len(parts) > 1 else "general"
    except ValueError:
        return "general"


def _chunk_text(text: str, path: Path) -> list[dict]:
    """Split file text into overlapping passages with full metadata."""
    text = text.strip()
    if not text:
        return []

    rel_path = str(path.relative_to(PROJECT_ROOT)).replace("\\", "/")
    title    = path.stem.replace("_", " ").replace("-", " ").title()
    domain   = _infer_domain(path)

    chunks: list[dict] = []
    start = 0
    idx   = 0

    while start < len(text):
        end     = min(start + CHUNK_SIZE, len(text))
        passage = text[start:end].strip()
        if passage:
            chunks.append({
                "id":            f"{path.stem}_{idx}",
                "text":          passage,
                "source_path":   rel_path,
                "title":         title,
                "domain":        domain,
                "chunk_index":   idx,
                "citation_type": "corpus",
            })
        start += CHUNK_SIZE - OVERLAP
        idx   += 1

    return chunks


# ---------------------------------------------------------------------------
# Module-level cache (lazy, rebuild-able)
# ---------------------------------------------------------------------------

_CACHE: list[dict] = []
_BUILT: bool       = False


def get_corpus_chunks(
    domain: str | None = None,
    rebuild: bool = False,
) -> list[dict]:
    """
    Return all indexed corpus chunks.

    Args:
        domain  : if set, only return chunks from that subdomain.
        rebuild : force a full re-scan of external_corpus/.
    """
    global _CACHE, _BUILT

    if not _BUILT or rebuild:
        chunks: list[dict] = []
        for path in _iter_corpus_files():
            try:
                text = path.read_text(encoding="utf-8", errors="replace")
                chunks.extend(_chunk_text(text, path))
            except Exception:
                continue
        _CACHE = chunks
        _BUILT = True

    if domain:
        return [c for c in _CACHE if c.get("domain") == domain]
    return _CACHE


def corpus_stats() -> dict:
    """Return chunk count and per-domain breakdown."""
    chunks  = get_corpus_chunks()
    domains: dict[str, int] = {}
    for c in chunks:
        d = c.get("domain", "general")
        domains[d] = domains.get(d, 0) + 1
    return {
        "total_chunks": len(chunks),
        "corpus_root":  str(CORPUS_ROOT),
        "corpus_exists": CORPUS_ROOT.exists(),
        "domains":      domains,
    }
