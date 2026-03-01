# app/prime/ingest/router.py
from __future__ import annotations

import io
import os
import re
import traceback
from typing import Optional

import httpx
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user
from app.prime.context.database import get_db
from app.prime.models import PrimeNotebookEntry
from app.prime.llm.openai_vision_client import openai_vision_client

router = APIRouter(prefix="/prime/ingest", tags=["PRIME Ingest"])


def _clean_text(text: str) -> str:
    return re.sub(r'\x00', '', text).strip()


async def _extract_pdf_text(file: UploadFile) -> str:
    content = await file.read()
    if not content:
        raise HTTPException(status_code=422, detail="PDF file is empty.")

    try:
        from pypdf import PdfReader
        reader = PdfReader(io.BytesIO(content))
        pages = [page.extract_text() or "" for page in reader.pages]
        text = "\n\n".join(p for p in pages if p.strip()).strip()
        if text:
            return _clean_text(text)
    except Exception:
        pass

    try:
        from pdfminer.high_level import extract_text as pdfminer_extract
        text = pdfminer_extract(io.BytesIO(content))
        if text and text.strip():
            return _clean_text(text)
        return "[PDF contained no extractable text - may be scanned or image-based]"
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Could not read PDF: {str(e)}")


async def _transcribe_audio(file: UploadFile) -> str:
    api_key = os.environ.get("OPENAI_API_KEY", "")
    if not api_key:
        raise ValueError("OPENAI_API_KEY is not set.")
    audio_bytes = await file.read()
    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.post(
            "https://api.openai.com/v1/audio/transcriptions",
            headers={"Authorization": f"Bearer {api_key}"},
            data={"model": "whisper-1"},
            files={"file": (file.filename, audio_bytes, file.content_type)},
        )
        response.raise_for_status()
        return response.json().get("text", "").strip()


@router.get("/debug-pypdf")
async def debug_pypdf():
    import sys
    try:
        import pypdf
        return {"status": "ok", "version": pypdf.__version__, "python": sys.executable}
    except ImportError as e:
        return {"status": "missing", "error": str(e), "python": sys.executable}


# Trailing slashes on all POST routes match frontend fetch URLs exactly.
# Without them FastAPI fires a 307 redirect and the browser drops the
# Authorization header, causing a 401 before the handler is ever reached.

@router.post("/image/")
async def ingest_image(
    message: str = Form(default="What do you see in this image?"),
    image: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    try:
        allowed_types = {"image/jpeg", "image/png", "image/webp", "image/gif"}
        if image.content_type not in allowed_types:
            return JSONResponse(status_code=422, content={"detail": f"Bad type: {image.content_type}"})

        image_bytes = await image.read()
        description = await openai_vision_client.describe_image(
            image_bytes=image_bytes,
            mime_type=image.content_type,
            prompt=message,
        )

        entry = PrimeNotebookEntry(
            kind="image_observation",
            title=f"Image: {image.filename}",
            body=description,
        )
        db.add(entry)
        await db.commit()
        await db.refresh(entry)
        return {"status": "ok", "notebook_entry_id": entry.id, "filename": image.filename, "description": description}

    except Exception as e:
        tb = traceback.format_exc()
        print(f"[INGEST IMAGE ERROR]\n{tb}")
        return JSONResponse(status_code=500, content={"detail": str(e), "traceback": tb})


@router.post("/pdf/")
async def ingest_pdf(
    message: Optional[str] = Form(default=None),
    pdf: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    try:
        extracted_text = await _extract_pdf_text(pdf)
        body_for_notebook = extracted_text[:8000]
        if len(extracted_text) > 8000:
            body_for_notebook += "\n\n[... truncated - " + str(len(extracted_text)) + " total chars extracted]"

        entry = PrimeNotebookEntry(
            kind="document_summary",
            title=f"Document: {pdf.filename}",
            body=body_for_notebook,
        )
        db.add(entry)
        await db.commit()
        await db.refresh(entry)
        return {
            "status": "ok",
            "notebook_entry_id": entry.id,
            "filename": pdf.filename,
            "char_count": len(extracted_text),
            "extracted_text": extracted_text[:4000],
            "preview": extracted_text[:500],
        }

    except HTTPException:
        raise
    except Exception as e:
        tb = traceback.format_exc()
        print(f"[INGEST PDF ERROR]\n{tb}")
        return JSONResponse(status_code=500, content={"detail": str(e), "traceback": tb})


@router.post("/audio/")
async def ingest_audio(
    audio: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    try:
        allowed_types = {
            "audio/mpeg", "audio/mp3", "audio/wav", "audio/wave",
            "audio/x-wav", "audio/mp4", "audio/m4a", "audio/webm",
            "audio/ogg", "video/webm",
        }
        if audio.content_type not in allowed_types:
            return JSONResponse(status_code=422, content={"detail": f"Bad type: {audio.content_type}"})

        transcript = await _transcribe_audio(audio)
        if not transcript:
            return JSONResponse(status_code=422, content={"detail": "Whisper returned empty transcript."})

        entry = PrimeNotebookEntry(
            kind="audio_transcript",
            title=f"Audio: {audio.filename}",
            body=transcript,
        )
        db.add(entry)
        await db.commit()
        await db.refresh(entry)
        return {"status": "ok", "notebook_entry_id": entry.id, "filename": audio.filename, "transcript": transcript}

    except Exception as e:
        tb = traceback.format_exc()
        print(f"[INGEST AUDIO ERROR]\n{tb}")
        return JSONResponse(status_code=500, content={"detail": str(e), "traceback": tb})


@router.post("/document/")
async def ingest_document(
    message: Optional[str] = Form(default=None),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    try:
        allowed_types = {
            "text/plain", "text/markdown", "text/csv",
            "application/json", "text/html", "text/xml",
        }
        allowed_extensions = {".txt", ".md", ".csv", ".json", ".log", ".yaml", ".yml", ".toml", ".xml", ".html"}
        ext = os.path.splitext(file.filename or "")[1].lower()

        if file.content_type not in allowed_types and ext not in allowed_extensions:
            return JSONResponse(status_code=422, content={"detail": f"Unsupported type: {file.content_type} ({ext})"})

        raw_bytes = await file.read()
        try:
            content = raw_bytes.decode("utf-8")
        except UnicodeDecodeError:
            content = raw_bytes.decode("latin-1", errors="replace")

        content = _clean_text(content)
        if not content:
            return JSONResponse(status_code=422, content={"detail": "File is empty or contains no readable text."})

        body_for_notebook = content[:8000]
        if len(content) > 8000:
            body_for_notebook += f"\n\n[... truncated - {len(content)} total chars]"

        entry = PrimeNotebookEntry(
            kind="document_summary",
            title=f"Document: {file.filename}",
            body=body_for_notebook,
        )
        db.add(entry)
        await db.commit()
        await db.refresh(entry)

        return {
            "status": "ok",
            "notebook_entry_id": entry.id,
            "filename": file.filename,
            "char_count": len(content),
            "extracted_text": content[:4000],
            "preview": content[:500],
        }

    except HTTPException:
        raise
    except Exception as e:
        tb = traceback.format_exc()
        print(f"[INGEST DOCUMENT ERROR]\n{tb}")
        return JSONResponse(status_code=500, content={"detail": str(e), "traceback": tb})
