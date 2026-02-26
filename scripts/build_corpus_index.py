from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Dict, List, Tuple

import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer


# ----- CONFIG -----

PROJECT_ROOT = Path(__file__).resolve().parent.parent
APP_DIR = PROJECT_ROOT / "app"
DATA_DIR = PROJECT_ROOT / "data"

CORPUS_DB_DIR = DATA_DIR / "corpus_db"
CORPUS_DB_DIR.mkdir(parents=True, exist_ok=True)

# Collection name for semantic corpus
CORPUS_COLLECTION_NAME = "prime_corpus"

# We’ll include these directories as semantic corpus sources
INCLUDE_PY_DIRS = [
    APP_DIR / "prime" / "curriculum",
    APP_DIR / "prime" / "history" / "philosophy",
    APP_DIR / "prime" / "humanities" / "philosophy",
]

EXTERNAL_TEXT_DIR = PROJECT_ROOT / "external_corpus"

# JSON semantic/episodic seeds at project root
INCLUDE_JSON_FILES = [
    PROJECT_ROOT / "k8_ethics_planner_response.json",
    PROJECT_ROOT / "k8_logic_planner_response.json",
    PROJECT_ROOT / "k8_main_planner_mind_response.json",
    PROJECT_ROOT / "k8_main_planner_world_response.json",
    PROJECT_ROOT / "k8_mind_planner_response.json",
    PROJECT_ROOT / "k8_world_planner_response.json",
    PROJECT_ROOT / "k8_teacher_mind_response.json",
    PROJECT_ROOT / "k8_teacher_world_response.json",
    PROJECT_ROOT / "k8_ethics_values_lesson.json",
    PROJECT_ROOT / "k8_logic_seeds_lesson.json",
    PROJECT_ROOT / "k8_mind_self_lesson.json",
    PROJECT_ROOT / "k8_world_reality_lesson.json",
    PROJECT_ROOT / "logic_argument_structure_lesson.json",
    PROJECT_ROOT / "manual_memory_save.json",
    PROJECT_ROOT / "metaphysics_adapt_response.json",
]

EXTERNAL_TEXT_DIR = PROJECT_ROOT / "external_corpus"

INCLUDE_TXT_DIRS = [
    EXTERNAL_TEXT_DIR / "textbooks",
    EXTERNAL_TEXT_DIR / "nonfiction",
    EXTERNAL_TEXT_DIR / "fiction",
    EXTERNAL_TEXT_DIR / "info_texts",
]

# Embedding model (local, no external calls)
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


# ----- HELPERS -----

def load_embedding_model() -> SentenceTransformer:
    print(f"[build_corpus_index] Loading embedding model: {EMBEDDING_MODEL_NAME}")
    return SentenceTransformer(EMBEDDING_MODEL_NAME)


def create_chroma_client() -> chromadb.Client:
    print(f"[build_corpus_index] Using Chroma DB at {CORPUS_DB_DIR}")
    client = chromadb.PersistentClient(
        path=str(CORPUS_DB_DIR),
        settings=Settings(anonymized_telemetry=False),
    )
    return client


def chunk_text(text: str, max_chars: int = 1500, overlap: int = 200) -> List[str]:
    """
    Very simple character-based chunking.
    You can refine this later to be token/semantic based.
    """
    text = text.strip()
    if not text:
        return []

    chunks: List[str] = []
    start = 0
    n = len(text)

    while start < n:
        end = min(start + max_chars, n)
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end == n:
            break
        start = end - overlap

    return chunks


def extract_text_from_py(path: Path) -> str:
    """
    Naive extraction: we just read the whole file and keep it as text.
    Later, you can refine this to focus on docstrings, constant strings, etc.
    """
    try:
        with path.open("r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        print(f"[build_corpus_index] Failed to read {path}: {e!r}")
        return ""


def extract_text_from_json(path: Path) -> str:
    """
    Flatten JSON by pulling out all string values concatenated.
    Robust to minor encoding problems by ignoring bad bytes.
    """
    try:
        with path.open("r", encoding="utf-8", errors="ignore") as f:
            data = json.load(f)
    except Exception as e:
        print(f"[build_corpus_index] Failed to read JSON {path}: {e!r}")
        return ""

    pieces: List[str] = []

    def walk(obj):
        if isinstance(obj, dict):
            for v in obj.values():
                walk(v)
        elif isinstance(obj, list):
            for v in obj:
                walk(v)
        elif isinstance(obj, str):
            pieces.append(obj)

    walk(data)
    return "\n".join(pieces)

def infer_domain_subdomain_from_txt_path(path: Path) -> tuple[str | None, str | None]:
    rel = str(path).replace("\\", "/").lower()

    # Math
    if "/external_corpus/math/textbooks/" in rel:
        return "mathematics_and_formal_sciences", "textbook"
    if "/external_corpus/math/nonfiction/" in rel:
        return "mathematics_and_formal_sciences", "nonfiction"

    # Science (natural sciences)
    if "/external_corpus/science/textbooks/" in rel:
        return "natural_sciences", "textbook"
    if "/external_corpus/science/nonfiction/" in rel:
        return "natural_sciences", "nonfiction"

    # Computer science / ICT
    if "/external_corpus/cs_ict/textbooks/" in rel:
        return "computer_science_and_information_systems", "textbook"

    # Engineering & technology
    if "/external_corpus/engineering_tech/textbooks/" in rel:
        return "engineering_and_technology", "textbook"

    # Humanities: textbooks / nonfiction / fiction
    if "/external_corpus/humanities/textbooks/" in rel:
        return "humanities", "textbook"
    if "/external_corpus/humanities/nonfiction/" in rel:
        return "humanities", "nonfiction"
    if "/external_corpus/humanities/fiction/" in rel:
        return "humanities", "fiction"

    # Social sciences
    if "/external_corpus/social_sciences/textbooks/" in rel:
        return "social_and_behavioral_sciences", "textbook"
    if "/external_corpus/social_sciences/nonfiction/" in rel:
        return "social_and_behavioral_sciences", "nonfiction"

    # Business / economics
    if "/external_corpus/business_econ/textbooks/" in rel:
        return "business_economics_and_management", "textbook"

    # Health & life sciences
    if "/external_corpus/health_life/textbooks/" in rel:
        return "health_medicine_and_biological_systems", "textbook"

    # Education & study skills
    if "/external_corpus/education_study/info/" in rel:
        return "education_pedagogy_and_human_development", "info"

    # Arts, media, design
    if "/external_corpus/arts_media/textbooks/" in rel:
        return "arts_design_and_communication", "textbook"

    # Law, policy, governance
    if "/external_corpus/law_policy/textbooks/" in rel:
        return "law_governance_and_public_administration", "textbook"

    # Environment, earth, agriculture
    if "/external_corpus/environment_earth/textbooks/" in rel:
        return "environment_and_earth_systems", "textbook"  # or a custom string you use consistently

    # Life skills, careers
    if "/external_corpus/life_skills_careers/info/" in rel:
        return "life_skills_and_careers", "info"

    # Interdisciplinary
    if "/external_corpus/interdisciplinary/textbooks/" in rel:
        return "interdisciplinary", "textbook"

    return None, None


def collect_corpus_items() -> List[Tuple[str, Dict[str, str]]]:
    """
    Return list of (text, metadata) for all corpus items.
    """
    items: List[Tuple[str, Dict[str, str]]] = []

    # From Python files
    for dir_path in INCLUDE_PY_DIRS:
        if not dir_path.exists():
            continue
        for py_file in dir_path.rglob("*.py"):
            if py_file.name == "__init__.py":
                continue
            text = extract_text_from_py(py_file)
            if not text.strip():
                continue
            meta = {
                "source_type": "python",
                "source_path": str(py_file.relative_to(PROJECT_ROOT)),
                "module": py_file.stem,
            }
            items.append((text, meta))

    # From JSON files (temporarily disabled until encoding issues are fixed)
    # for json_path in INCLUDE_JSON_FILES:
    #     if not json_path.exists():
    #         continue
    #     text = extract_text_from_json(json_path)
    #     if not text.strip():
    #         continue
    #
    #     domain, subdomain = infer_domain_subdomain_from_json_name(json_path)
    #     meta = {
    #         "source_type": "json",
    #         "source_path": str(json_path.relative_to(PROJECT_ROOT)),
    #         "module": json_path.stem,
    #     }
    #     if domain:
    #         meta["domain"] = domain
    #     if subdomain:
    #         meta["subdomain"] = subdomain
    #
    #     items.append((text, meta))

    # From plain text books (Project Gutenberg, OpenStax converted, etc.)
    for txt_dir in INCLUDE_TXT_DIRS:
        if not txt_dir.exists():
            continue
        for txt_file in txt_dir.rglob("*.txt"):
            try:
                with txt_file.open("r", encoding="utf-8", errors="ignore") as f:
                    text = f.read()
            except Exception as e:
                print(f"[build_corpus_index] Failed to read TXT {txt_file}: {e!r}")
                continue

            if not text.strip():
                continue

            domain, subdomain = infer_domain_subdomain_from_txt_path(txt_file)
            meta = {
                "source_type": "txt",
                "source_path": str(txt_file.relative_to(PROJECT_ROOT)),
                "module": txt_file.stem,
            }
            if domain:
                meta["domain"] = domain
            if subdomain:
                meta["subdomain"] = subdomain

            items.append((text, meta))

    print(f"[build_corpus_index] Collected {len(items)} raw items before chunking.")
    return items


def main():
    model = load_embedding_model()
    client = create_chroma_client()

    # Drop and recreate collection each time for now.
    try:
        client.delete_collection(CORPUS_COLLECTION_NAME)
        print(f"[build_corpus_index] Deleted existing collection {CORPUS_COLLECTION_NAME}")
    except Exception:
        pass

    collection = client.create_collection(name=CORPUS_COLLECTION_NAME)
    print(f"[build_corpus_index] Created collection {CORPUS_COLLECTION_NAME}")

    items = collect_corpus_items()

    # Chunk and embed
    doc_ids: List[str] = []
    texts: List[str] = []
    metadatas: List[Dict[str, str]] = []

    idx = 0
    for text, meta in items:
        chunks = chunk_text(text)
        for chunk in chunks:
            doc_id = f"doc-{idx}"
            idx += 1
            doc_ids.append(doc_id)
            texts.append(chunk)
            metadatas.append(meta)

    print(f"[build_corpus_index] Total chunks: {len(texts)}")

    if not texts:
        print("[build_corpus_index] No text to index; exiting.")
        return

    print("[build_corpus_index] Computing embeddings...")
    embeddings = model.encode(texts, show_progress_bar=True)

    print("[build_corpus_index] Adding to Chroma collection...")
    collection.add(
        ids=doc_ids,
        documents=texts,
        metadatas=metadatas,
        embeddings=embeddings,
    )

    print("[build_corpus_index] Done. Corpus indexed.")

    # --- DEBUG: inspect what was actually stored ---
    try:
        total = collection.count()
        print(f"[build_corpus_index] Collection '{CORPUS_COLLECTION_NAME}' count after add: {total}")
        # Print first 3 ids and short previews
        sample_ids = doc_ids[:3]
        print(f"[build_corpus_index] Sample stored ids: {sample_ids}")
        if sample_ids:
            res = collection.get(ids=sample_ids)
            print("[build_corpus_index] Sample get() documents lengths:",
                  len(res.get('documents', [])))
            for i, doc in enumerate(res.get("documents", [])):
                preview = doc.replace("\n", " ")
                if len(preview) > 120:
                    preview = preview[:117] + "..."
                print(f"[build_corpus_index] DOC {i}: {preview}")
            print("[build_corpus_index] Sample metadatas:", res.get("metadatas", []))
    except Exception as e:
        print(f"[build_corpus_index] DEBUG inspection error: {e!r}")

if __name__ == "__main__":
    main()
