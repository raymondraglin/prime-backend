# app/prime/citations/extractor.py
"""
PRIME Citation Extractor

Parses [CITE: source | title | snippet] markers from PRIME's response text.

PRIME is instructed (via prompt_builder.py) to embed citations inline:
  [CITE: source_path | Human Title | brief snippet or finding]

This extractor:
  1. Finds all [CITE: ...] markers in raw LLM output
  2. Builds Citation objects with auto-incremented indices
  3. Replaces each marker with a numbered reference [N]
  4. Returns (clean_text, citations_list)

The clean text is what gets returned to the user.
The citations list is returned alongside as structured metadata.

Examples of valid PRIME citations:
  [CITE: app/prime/ingest/router.py | Ingest Router | pdfminer fallback on line 87]
  [CITE: external_corpus/cs_ict/textbooks/think_python.txt | Think Python | recursion p.142]
  [CITE: GOAL:abc123 | Goal: Close Gap 7 | runner_with_tools.py needed]
  [CITE: MEMORY:session-xyz | Session Memory | Raymond prefers Postgres over Redis]
"""
from __future__ import annotations

import re
from app.prime.citations.models import Citation

# Matches: [CITE: source | title | snippet]
# Allows whitespace around pipes; snippet may contain spaces and punctuation
_CITE_PATTERN = re.compile(
    r'\[CITE:\s*([^|\]]+?)\s*\|\s*([^|\]]+?)\s*\|\s*([^\]]+?)\s*\]',
    re.IGNORECASE,
)


def _infer_type(source: str) -> str:
    """Infer citation type from source string prefix or path."""
    s = source.lower()
    if s.startswith("goal:"):
        return "goal"
    if s.startswith("memory:"):
        return "memory"
    if s.startswith("http://") or s.startswith("https://"):
        return "web"
    if "external_corpus" in s or "textbook" in s:
        return "corpus"
    return "file"


def extract_citations(text: str) -> tuple[str, list[Citation]]:
    """
    Parse [CITE: ...] markers out of raw LLM response text.

    Returns:
        clean_text -- original text with [CITE:...] replaced by [N]
        citations  -- list of Citation objects in order of first appearance
    """
    citations: list[Citation] = []
    index = 1

    def _replace(match: re.Match) -> str:
        nonlocal index
        source  = match.group(1).strip()
        title   = match.group(2).strip()
        snippet = match.group(3).strip()
        citations.append(Citation(
            index         = index,
            source        = source,
            title         = title,
            snippet       = snippet,
            citation_type = _infer_type(source),
        ))
        ref = f"[{index}]"
        index += 1
        return ref

    clean_text = _CITE_PATTERN.sub(_replace, text)
    return clean_text, citations


def strip_citations(text: str) -> str:
    """Remove all [CITE: ...] markers from text without numbering."""
    return _CITE_PATTERN.sub("", text).strip()
