from __future__ import annotations

from pathlib import Path
from typing import Iterable, List, Dict, Any
import json
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from fastapi.encoders import jsonable_encoder
import numpy as np
from app.prime.curriculum.models import ReasoningMemoryEntry, ReasoningTask


# --- Paths: keep in sync with build_corpus_index.py ---

# memory_store.py is at:
#   ...\backend\prime-backend\app\prime\reasoning\memory_store.py
# So:
#   parents[0] = memory_store.py
#   parents[1] = reasoning
#   parents[2] = prime
#   parents[3] = app
#   parents[4] = prime-backend  <-- project root we want

PROJECT_ROOT = Path(__file__).resolve().parents[3]
APP_DIR = PROJECT_ROOT / "app"
DATA_DIR = PROJECT_ROOT / "data"

MEMORY_DIR = APP_DIR / "primelogs"
MEMORY_DIR.mkdir(parents=True, exist_ok=True)
REASONING_MEMORY_FILE = MEMORY_DIR / "reasoning_memory.jsonl"

print("DEBUG PROJECT_ROOT:", PROJECT_ROOT)
print("DEBUG DATA_DIR:", DATA_DIR)
print("DEBUG MEMORY_DIR:", MEMORY_DIR)
print("DEBUG REASONING_MEMORY_FILE:", REASONING_MEMORY_FILE)

CORPUS_DB_DIR = DATA_DIR / "corpus_db"
CORPUS_COLLECTION_NAME = "prime_corpus"
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


def append_memory_entry(entry: ReasoningMemoryEntry) -> None:
    """
    Append a single reasoning memory entry as one JSON line.
    Failures should not crash the main reasoning flow.
    """
    try:
        data = jsonable_encoder(entry)
        print("DEBUG append_memory_entry writing to:", REASONING_MEMORY_FILE)
        with REASONING_MEMORY_FILE.open("a", encoding="utf-8") as f:
            f.write(json.dumps(data, ensure_ascii=False) + "\n")
    except Exception as e:
        print("DEBUG append_memory_entry error:", repr(e))
        # Fail silently for now; you can add logging later.
        pass


def load_memory_entries(limit: int = 200) -> List[ReasoningMemoryEntry]:
    """
    Load up to 'limit' reasoning memory entries from the end of the JSONL file.
    """
    entries: List[ReasoningMemoryEntry] = []
    if not REASONING_MEMORY_FILE.exists():
        return entries
    try:
        with REASONING_MEMORY_FILE.open("r", encoding="utf-8") as f:
            lines = f.readlines()
        for line in lines[-limit:]:
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
                entries.append(ReasoningMemoryEntry(**data))
            except Exception:
                continue
    except Exception:
        return entries
    return entries


def iter_memory_entries() -> Iterable[ReasoningMemoryEntry]:
    """
    Iterate over all reasoning memory entries (used for more complex queries).
    """
    if not REASONING_MEMORY_FILE.exists():
        return
    try:
        with REASONING_MEMORY_FILE.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                    yield ReasoningMemoryEntry(**data)
                except Exception:
                    continue
    except Exception:
        return


# --- New: semantic corpus retrieval using Chroma + SentenceTransformer ---

# Lazy singletons
_chroma_client: chromadb.Client | None = None
_corpus_collection: Any = None
_embedding_model: SentenceTransformer | None = None


def _get_embedding_model() -> SentenceTransformer:
    global _embedding_model
    if _embedding_model is None:
        print(f"[memory_store] Loading embedding model: {EMBEDDING_MODEL_NAME}")
        _embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME)
    return _embedding_model


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

def list_any_corpus_docs(limit: int = 3) -> List[Dict[str, Any]]:
    """
    Debug helper: return up to `limit` arbitrary docs from the corpus.
    This does NOT use embeddings; it just reads whatever is there.
    """
    try:
        collection = _get_corpus_collection()
        # Chroma doesn't have a direct "get all", so we rely on selection by IDs.
        # We stored ids as "doc-0", "doc-1", ..., "doc-N" in the indexer.
        docs: List[Dict[str, Any]] = []
        for i in range(limit):
            doc_id = f"doc-{i}"
            try:
                res = collection.get(ids=[doc_id])
                if not res or not res.get("documents"):
                    continue
                docs.append(
                    {
                        "id": doc_id,
                        "text": res["documents"][0],
                        "metadata": res.get("metadatas", [{}])[0],
                    }
                )
            except Exception:
                continue
        return docs
    except Exception as e:
        print(f"[memory_store] list_any_corpus_docs error: {e!r}")
        return []

def debug_corpus_stats() -> None:
    """
    Print basic stats about the corpus collection at startup.
    """
    try:
        collection = _get_corpus_collection()
        count = collection.count()
        print(f"[memory_store] Corpus collection '{CORPUS_COLLECTION_NAME}' has {count} documents.")
    except Exception as e:
        print(f"[memory_store] debug_corpus_stats error: {e!r}")

def search_corpus(query: str, top_k: int = 5) -> List[Dict[str, Any]]:
    """
    Semantic search over the PRIME corpus (curriculum, philosophy, JSON lessons).
    Returns a list of {text, metadata} dicts.
    """
    try:
        model = _get_embedding_model()
        collection = _get_corpus_collection()

        # Encode to list-of-list for Chroma
        query_embedding = model.encode(query).tolist()
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
        )

        docs = results.get("documents", [[]])[0]
        metas = results.get("metadatas", [[]])[0]

        out: List[Dict[str, Any]] = []
        for text, meta in zip(docs, metas):
            out.append(
                {
                    "text": text,
                    "metadata": meta,
                }
            )
        return out
    except Exception as e:
        print(f"[memory_store] search_corpus error: {e!r}")
        return []


def search_corpus_for_task(
    task: ReasoningTask,
    top_k: int = 5,
) -> List[Dict[str, Any]]:
    """
    Domain-aware wrapper: consult PRIME's corpus for background relevant to this task.
    Uses task.domain_tag / subdomain_tag to bias which 'wing of the cathedral' to walk into.
    """
    try:
        model = _get_embedding_model()
        collection = _get_corpus_collection()

        domain_hint = task.domain_tag or ""
        subdomain_hint = task.subdomain_tag or ""
        base = task.natural_language_task or ""
        query_text = f"{domain_hint} {subdomain_hint} {base}".strip()

        query_embedding = model.encode(query_text).tolist()

        where: Dict[str, Any] = {}
        if task.domain_tag:
            where["domain"] = task.domain_tag
        if task.subdomain_tag:
            where["subdomain"] = task.subdomain_tag

        if where:
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                where=where,
            )
        else:
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
            )

        docs = results.get("documents", [[]])[0]
        metas = results.get("metadatas", [[]])[0]

        out: List[Dict[str, Any]] = []
        for text, meta in zip(docs, metas):
            out.append(
                {
                    "text": text,
                    "metadata": meta,
                }
            )
        return out
    except Exception as e:
        print(f"[memory_store] search_corpus_for_task error: {e!r}")
        return []

# Run a quick stats check when the module is imported
debug_corpus_stats()
