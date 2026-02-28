"""
PRIME Web Tools
File: app/prime/tools/web_tools.py

Two primitives:
  search_web(query, k=5)   → search results from a configured provider
  fetch_url(url)           → fetched + cleaned text from a URL

Provider selection via env var WEB_SEARCH_PROVIDER:
  brave   → BRAVE_API_KEY required
  tavily  → TAVILY_API_KEY required
  none    → disabled (returns a clear error, does not crash)

Safety:
  - Blocks internal IPs, localhost, file://, data:// URLs
  - AWS/GCP metadata endpoints blocked
  - Response capped at 50KB before LLM sees it
  - Scripts + style tags stripped before returning HTML
  - Per-request connect + read timeouts enforced

Cache:
  Simple in-memory TTL cache (5 min) keyed by (query) and (url).
  Keeps repeat calls cheap during a single session.
"""

from __future__ import annotations

import os
import re
import time
from typing import Any
from urllib.parse import urlparse

import httpx

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

_MAX_RESPONSE_BYTES = 50 * 1024       # 50 KB
_MAX_CONTENT_FOR_LLM = 8_000          # chars sent to LLM
_CACHE_TTL = 300                      # seconds
_TIMEOUT = httpx.Timeout(connect=5.0, read=10.0, write=5.0, pool=5.0)

_BLOCKED_HOSTS = {
    "localhost", "127.0.0.1", "0.0.0.0",
    "169.254.169.254",           # AWS IMDS
    "metadata.google.internal",  # GCP metadata
}
_BLOCKED_SCHEMES = {"file", "ftp", "data"}
_PRIVATE_IP = re.compile(
    r"^(10\.|172\.(1[6-9]|2[0-9]|3[01])\.|192\.168\.|fc|fd)",
    re.IGNORECASE,
)


# ---------------------------------------------------------------------------
# Simple in-memory cache
# ---------------------------------------------------------------------------

_cache: dict[str, tuple[float, Any]] = {}


def _cache_get(key: str) -> Any | None:
    entry = _cache.get(key)
    if entry and time.monotonic() - entry[0] < _CACHE_TTL:
        return entry[1]
    _cache.pop(key, None)
    return None


def _cache_set(key: str, value: Any) -> None:
    _cache[key] = (time.monotonic(), value)


# ---------------------------------------------------------------------------
# Safety
# ---------------------------------------------------------------------------

def _validate_url(url: str) -> str | None:
    """Return an error string if URL is unsafe, None if OK."""
    try:
        parsed = urlparse(url)
    except Exception:
        return "Invalid URL format"
    if parsed.scheme in _BLOCKED_SCHEMES:
        return f"Blocked scheme: {parsed.scheme}"
    hostname = (parsed.hostname or "").lower()
    if hostname in _BLOCKED_HOSTS:
        return f"Blocked host: {hostname}"
    if _PRIVATE_IP.match(hostname):
        return f"Blocked private IP range: {hostname}"
    return None


# ---------------------------------------------------------------------------
# HTML extraction
# ---------------------------------------------------------------------------

def _strip_html(html: str) -> str:
    html = re.sub(
        r"<(script|style)[^>]*>.*?</(script|style)>",
        " ", html, flags=re.DOTALL | re.IGNORECASE,
    )
    html = re.sub(r"<(br|p|li|h[1-6]|tr|div|section|article)[^>]*>", "\n", html, flags=re.IGNORECASE)
    html = re.sub(r"<[^>]+>", " ", html)
    html = re.sub(r"[ \t]+", " ", html)
    html = re.sub(r"\n{3,}", "\n\n", html)
    return html.strip()


# ---------------------------------------------------------------------------
# Provider adapters
# ---------------------------------------------------------------------------

async def _brave_search(query: str, k: int) -> list[dict]:
    api_key = os.getenv("BRAVE_API_KEY", "")
    if not api_key:
        return [{"error": "BRAVE_API_KEY not set in environment"}]
    async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
        resp = await client.get(
            "https://api.search.brave.com/res/v1/web/search",
            headers={"Accept": "application/json", "X-Subscription-Token": api_key},
            params={"q": query, "count": k},
        )
        resp.raise_for_status()
        data = resp.json()
    return [
        {
            "title":   item.get("title", ""),
            "url":     item.get("url", ""),
            "snippet": item.get("description", ""),
        }
        for item in data.get("web", {}).get("results", [])[:k]
    ]


async def _tavily_search(query: str, k: int) -> list[dict]:
    api_key = os.getenv("TAVILY_API_KEY", "")
    if not api_key:
        return [{"error": "TAVILY_API_KEY not set in environment"}]
    async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
        resp = await client.post(
            "https://api.tavily.com/search",
            json={"api_key": api_key, "query": query, "max_results": k},
        )
        resp.raise_for_status()
        data = resp.json()
    return [
        {
            "title":   item.get("title", ""),
            "url":     item.get("url", ""),
            "snippet": item.get("content", "")[:400],
        }
        for item in data.get("results", [])[:k]
    ]


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

async def search_web(query: str, *, k: int = 5) -> dict[str, Any]:
    """
    Search the web. Provider selected via WEB_SEARCH_PROVIDER env var.
    Returns: {results: [{title, url, snippet}], provider, latency_ms}
    """
    cached = _cache_get(f"search:{query}:{k}")
    if cached:
        return {**cached, "cached": True}

    provider = os.getenv("WEB_SEARCH_PROVIDER", "none").lower()
    start = time.monotonic()
    try:
        if provider == "brave":
            results = await _brave_search(query, k)
        elif provider == "tavily":
            results = await _tavily_search(query, k)
        else:
            results = [{
                "error": (
                    "Web search disabled. Set WEB_SEARCH_PROVIDER=brave or tavily "
                    "and provide the corresponding API key."
                )
            }]
        latency_ms = round((time.monotonic() - start) * 1000, 1)
        out = {"results": results, "provider": provider, "latency_ms": latency_ms}
        _cache_set(f"search:{query}:{k}", out)
        return out
    except Exception as exc:
        return {"results": [], "provider": provider, "error": str(exc), "latency_ms": 0.0}


async def fetch_url(url: str) -> dict[str, Any]:
    """
    Fetch a URL and return cleaned text content.
    Returns: {url, status, content_text, content_type, extracted_title}
    """
    cached = _cache_get(f"fetch:{url}")
    if cached:
        return {**cached, "cached": True}

    err = _validate_url(url)
    if err:
        return {"url": url, "status": 0, "error": err, "content_text": ""}

    try:
        async with httpx.AsyncClient(
            timeout=_TIMEOUT,
            follow_redirects=True,
            headers={"User-Agent": "PRIME-Bot/1.0 (research assistant)"},
        ) as client:
            resp = await client.get(url)
            content_type = resp.headers.get("content-type", "")
            raw = resp.content[:_MAX_RESPONSE_BYTES]

        decoded = raw.decode("utf-8", errors="replace")
        if "text/html" in content_type or not content_type:
            text = _strip_html(decoded)
        else:
            text = decoded

        title_match = re.search(r"<title[^>]*>(.*?)</title>", decoded, re.IGNORECASE | re.DOTALL)
        title = title_match.group(1).strip() if title_match else ""

        out = {
            "url":             url,
            "status":          resp.status_code,
            "content_text":    text[:_MAX_CONTENT_FOR_LLM],
            "content_type":    content_type,
            "extracted_title": title,
        }
        _cache_set(f"fetch:{url}", out)
        return out
    except Exception as exc:
        return {"url": url, "status": 0, "error": str(exc), "content_text": ""}
