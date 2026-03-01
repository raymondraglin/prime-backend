# app/prime/tasks/ingest_tasks.py
"""
PRIME Ingestion Tasks

Async Celery tasks for document processing.

Tasks:
  ingest_pdf_async      -- extract text from PDF, chunk, embed
  ingest_document_async -- extract text from DOCX/TXT, chunk, embed
"""
from __future__ import annotations

from app.prime.tasks.celery_app import celery_app


@celery_app.task(bind=True, name="prime.ingest.pdf")
def ingest_pdf_async(self, file_path: str, user_id: str = "raymond"):
    """
    Ingest a PDF file: extract text, chunk, embed.

    Args:
        file_path : path to PDF file
        user_id   : user identifier

    Returns:
        dict with page_count, chunk_count, embedded_count
    """
    from pathlib import Path
    from PyPDF2 import PdfReader
    from app.prime.academic.indexer import _chunk_text
    from app.prime.academic.embeddings import embed_chunks

    self.update_state(state="STARTED", meta={"stage": "reading_pdf", "progress": 0})

    try:
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"PDF not found: {file_path}")

        reader = PdfReader(str(path))
        page_count = len(reader.pages)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""

        self.update_state(state="STARTED", meta={"stage": "chunking", "progress": 30, "page_count": page_count})

        chunks = _chunk_text(text, path)
        self.update_state(state="STARTED", meta={"stage": "embedding", "progress": 60, "chunk_count": len(chunks)})

        embedded_count = embed_chunks(chunks)
        self.update_state(state="STARTED", meta={"stage": "complete", "progress": 100})

        return {
            "file_path": file_path,
            "page_count": page_count,
            "chunk_count": len(chunks),
            "embedded_count": embedded_count,
        }

    except Exception as exc:
        self.update_state(state="FAILURE", meta={"error": str(exc)})
        raise


@celery_app.task(bind=True, name="prime.ingest.document")
def ingest_document_async(self, file_path: str, user_id: str = "raymond"):
    """
    Ingest a text document (DOCX, TXT, MD): extract text, chunk, embed.

    Args:
        file_path : path to document file
        user_id   : user identifier

    Returns:
        dict with chunk_count, embedded_count
    """
    from pathlib import Path
    from docx import Document
    from app.prime.academic.indexer import _chunk_text
    from app.prime.academic.embeddings import embed_chunks

    self.update_state(state="STARTED", meta={"stage": "reading_document", "progress": 0})

    try:
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Document not found: {file_path}")

        if path.suffix == ".docx":
            doc = Document(str(path))
            text = "\n".join([para.text for para in doc.paragraphs])
        else:
            text = path.read_text(encoding="utf-8", errors="replace")

        self.update_state(state="STARTED", meta={"stage": "chunking", "progress": 30})

        chunks = _chunk_text(text, path)
        self.update_state(state="STARTED", meta={"stage": "embedding", "progress": 60, "chunk_count": len(chunks)})

        embedded_count = embed_chunks(chunks)
        self.update_state(state="STARTED", meta={"stage": "complete", "progress": 100})

        return {
            "file_path": file_path,
            "chunk_count": len(chunks),
            "embedded_count": embedded_count,
        }

    except Exception as exc:
        self.update_state(state="FAILURE", meta={"error": str(exc)})
        raise
