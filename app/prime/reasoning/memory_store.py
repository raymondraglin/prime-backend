from __future__ import annotations

from pathlib import Path
from typing import Iterable, List, Dict, Any
import json
from fastapi.encoders import jsonable_encoder
from app.prime.curriculum.models import ReasoningMemoryEntry, ReasoningTask


# --- Paths ---
PROJECT_ROOT = Path(__file__).resolve().parents[3]
APP_DIR = PROJECT_ROOT / "app"
DATA_DIR = PROJECT_ROOT / "data"

MEMORY_DIR = APP_DIR / "primelogs"
MEMORY_DIR.mkdir(parents=True, exist_ok=True)
REASONING_MEMORY_FILE = MEMORY_DIR / "reasoning_memory.jsonl"

CORPUS_DB_DIR = DATA_DIR / "corpus_db"
CORPUS_COLLECTION_NAME = "prime_corpus"
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


def append_memory_entry(entry: ReasoningMemoryEntry) -> None:
    try:
        data = jsonable_encoder(entry)
        with REASONING_MEMORY_FILE.open("a", encoding="utf-8") as f:
            f.write(json.dumps(data, ensure_ascii=False) + "\n")
    except Exception as e:
        print("[memory_store] append_memory_entry error:", repr(e))


def load_memory_entries(limit: int = 200) -> List[ReasoningMemoryEntry]:
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


# ---------------------------------------------------------------------------
# Lazy singletons — only loaded when search_corpus() is first called.
# sentence-transformers pulls in PyTorch (2GB). Never import at module level.
# ---------------------------------------------------------------------------

_chroma_client = None
_corpus_collection = None
_embedding_model = None


def _get_embedding_model():
    global _embedding_model
    if _embedding_model is None:
        try:
            from sentence_transformers import SentenceTransformer
            print(f"[memory_store] Loading embedding model: {EMBEDDING_MODEL_NAME}")
            _embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME)
        except ImportError:
            raise RuntimeError(
                "sentence-transformers not installed. "
                "Run: pip install sentence-transformers"
            )
    return _embedding_model


def _get_corpus_collection():
    global _chroma_client, _corpus_collection
    if _corpus_collection is not None:
        return _corpus_collection
    try:
        import chromadb
        from chromadb.config import Settings
        print(f"[memory_store] Connecting to Chroma at {CORPUS_DB_DIR}")
        _chroma_client = chromadb.PersistentClient(
            path=str(CORPUS_DB_DIR),
            settings=Settings(anonymized_telemetry=False),
        )
        _corpus_collection = _chroma_client.get_collection(name=CORPUS_COLLECTION_NAME)
        return _corpus_collection
    except Exception as e:
        raise RuntimeError(f"[memory_store] Chroma unavailable: {e}")


def list_any_corpus_docs(limit: int = 3) -> List[Dict[str, Any]]:
    try:
        collection = _get_corpus_collection()
        docs: List[Dict[str, Any]] = []
        for i in range(limit):
            doc_id = f"doc-{i}"
            try:
                res = collection.get(ids=[doc_id])
                if not res or not res.get("documents"):
                    continue
                docs.append({
                    "id": doc_id,
                    "text": res["documents"][0],
                    "metadata": res.get("metadatas", [{}])[0],
                })
            except Exception:
                continue
        return docs
    except Exception as e:
        print(f"[memory_store] list_any_corpus_docs error: {e!r}")
        return []


def search_corpus(query: str, top_k: int = 5) -> List[Dict[str, Any]]:
    """
    Semantic search over the PRIME corpus.
    Returns [] gracefully if corpus not yet built or packages not installed.
    """
    try:
        import numpy as np
        model = _get_embedding_model()
        collection = _get_corpus_collection()
        query_embedding = model.encode(query).tolist()
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
        )
        docs = results.get("documents", [[]])[0]
        metas = results.get("metadatas", [[]])[0]
        return [{"text": text, "metadata": meta} for text, meta in zip(docs, metas)]
    except Exception as e:
        print(f"[memory_store] search_corpus error (returning empty): {e!r}")
        return []


def search_corpus_for_task(
    task: ReasoningTask,
    top_k: int = 5,
) -> List[Dict[str, Any]]:
    try:
        import numpy as np
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
        return [{"text": text, "metadata": meta} for text, meta in zip(docs, metas)]
    except Exception as e:
        print(f"[memory_store] search_corpus_for_task error: {e!r}")
        return []
