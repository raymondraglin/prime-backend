from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict, Iterable, List

import chromadb
from chromadb.config import Settings
from fastapi.encoders import jsonable_encoder
from openai import OpenAI

from app.prime.curriculum.models import ReasoningMemoryEntry, ReasoningTask

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[3]
APP_DIR      = PROJECT_ROOT / "app"
DATA_DIR     = PROJECT_ROOT / "data"

MEMORY_DIR = APP_DIR / "primelogs"
MEMORY_DIR.mkdir(parents=True, exist_ok=True)
REASONING_MEMORY_FILE = MEMORY_DIR / "reasoning_memory.jsonl"

CORPUS_DB_DIR           = DATA_DIR / "corpus_db"
CORPUS_COLLECTION_NAME  = "prime_corpus"
EMBEDDING_MODEL_NAME    = "text-embedding-3-small"  # OpenAI — no PyTorch needed

# ---------------------------------------------------------------------------
# Lazy singletons
# ---------------------------------------------------------------------------
_chroma_client:    chromadb.Client | None = None
_corpus_collection: Any                   = None
_openai_client:    OpenAI | None          = None


def _get_openai_client() -> OpenAI:
    global _openai_client
    if _openai_client is None:
        _openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    return _openai_client


def _embed(text: str) -> List[float]:
    """Return an embedding vector via OpenAI text-embedding-3-small."""
    client   = _get_openai_client()
    response = client.embeddings.create(model=EMBEDDING_MODEL_NAME, input=text)
    return response.data[0].embedding


def _get_corpus_collection():
    global _chroma_client, _corpus_collection
    if _corpus_collection is not None:
        return _corpus_collection
    print(f"[memory_store] Connecting to Chroma corpus DB at {CORPUS_DB_DIR}")
    _chroma_client = chromadb.PersistentClient(
        path=str(CORPUS_DB_DIR),
        settings=Settings(anonymized_telemetry=False),
    )
    _corpus_collection = _chroma_client.get_collection(name=CORPUS_COLLECTION_NAME)
    return _corpus_collection


# ---------------------------------------------------------------------------
# JSONL memory helpers
# ---------------------------------------------------------------------------

def append_memory_entry(entry: ReasoningMemoryEntry) -> None:
    try:
        data = jsonable_encoder(entry)
        with REASONING_MEMORY_FILE.open("a", encoding="utf-8") as f:
            f.write(json.dumps(data, ensure_ascii=False) + "\n")
    except Exception as exc:
        print("[memory_store] append_memory_entry error:", repr(exc))


def load_memory_entries(limit: int = 200) -> List[ReasoningMemoryEntry]:
    entries: List[ReasoningMemoryEntry] = []
    if not REASONING_MEMORY_FILE.exists():
        return entries
    try:
        lines = REASONING_MEMORY_FILE.read_text(encoding="utf-8").splitlines()
        for line in lines[-limit:]:
            line = line.strip()
            if not line:
                continue
            try:
                entries.append(ReasoningMemoryEntry(**json.loads(line)))
            except Exception:
                continue
    except Exception:
        pass
    return entries


def iter_memory_entries() -> Iterable[ReasoningMemoryEntry]:
    if not REASONING_MEMORY_FILE.exists():
        return
    try:
        with REASONING_MEMORY_FILE.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    yield ReasoningMemoryEntry(**json.loads(line))
                except Exception:
                    continue
    except Exception:
        return


# ---------------------------------------------------------------------------
# Corpus search
# ---------------------------------------------------------------------------

def debug_corpus_stats() -> None:
    try:
        collection = _get_corpus_collection()
        print(f"[memory_store] Corpus '{CORPUS_COLLECTION_NAME}' has {collection.count()} docs.")
    except Exception as exc:
        print(f"[memory_store] debug_corpus_stats: {exc!r}")


def list_any_corpus_docs(limit: int = 3) -> List[Dict[str, Any]]:
    try:
        collection = _get_corpus_collection()
        docs: List[Dict[str, Any]] = []
        for i in range(limit):
            try:
                res = collection.get(ids=[f"doc-{i}"])
                if res and res.get("documents"):
                    docs.append({"id": f"doc-{i}", "text": res["documents"][0],
                                  "metadata": res.get("metadatas", [{}])[0]})
            except Exception:
                continue
        return docs
    except Exception as exc:
        print(f"[memory_store] list_any_corpus_docs error: {exc!r}")
        return []


def search_corpus(query: str, top_k: int = 5) -> List[Dict[str, Any]]:
    try:
        collection     = _get_corpus_collection()
        query_embedding = _embed(query)
        results = collection.query(query_embeddings=[query_embedding], n_results=top_k)
        docs  = results.get("documents", [[]])[0]
        metas = results.get("metadatas", [[]])[0]
        return [{"text": t, "metadata": m} for t, m in zip(docs, metas)]
    except Exception as exc:
        print(f"[memory_store] search_corpus error: {exc!r}")
        return []


def search_corpus_for_task(task: ReasoningTask, top_k: int = 5) -> List[Dict[str, Any]]:
    try:
        collection = _get_corpus_collection()
        query_text = " ".join(filter(None, [
            task.domain_tag, task.subdomain_tag, task.natural_language_task
        ]))
        query_embedding = _embed(query_text)

        where: Dict[str, Any] = {}
        if task.domain_tag:
            where["domain"] = task.domain_tag
        if task.subdomain_tag:
            where["subdomain"] = task.subdomain_tag

        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            **(dict(where=where) if where else {}),
        )
        docs  = results.get("documents", [[]])[0]
        metas = results.get("metadatas", [[]])[0]
        return [{"text": t, "metadata": m} for t, m in zip(docs, metas)]
    except Exception as exc:
        print(f"[memory_store] search_corpus_for_task error: {exc!r}")
        return []


# Run a quick stats check when the module is imported
debug_corpus_stats()
