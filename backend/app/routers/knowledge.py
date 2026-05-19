"""
Knowledge Base Router - manage RAG documents for a business.
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from typing import Optional

from app.core.auth import get_current_user
from app.models.business import Business
from app.services import knowledge_service

router = APIRouter(prefix="/api/knowledge", tags=["knowledge"])

MAX_UPLOAD_BYTES = 2 * 1024 * 1024  # 2 MB
MAX_TEXT_CHARS = 200_000


class CreateTextDocumentRequest(BaseModel):
    title: str
    content: str


@router.get("/")
async def list_docs(current: Business = Depends(get_current_user)):
    return {"documents": await knowledge_service.list_documents(str(current.id))}


@router.post("/text")
async def create_text(
    req: CreateTextDocumentRequest,
    current: Business = Depends(get_current_user),
):
    if not req.content or not req.content.strip():
        raise HTTPException(status_code=400, detail="İçerik boş olamaz")
    if len(req.content) > MAX_TEXT_CHARS:
        raise HTTPException(status_code=400, detail=f"İçerik {MAX_TEXT_CHARS} karakteri aşamaz")
    try:
        doc = await knowledge_service.ingest_document(
            business_id=str(current.id),
            title=req.title or "Adsız belge",
            raw_content=req.content,
            source_type="text",
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"id": str(doc.id), "title": doc.title, "chunk_count": len(doc.chunks)}


@router.post("/file")
async def upload_file(
    file: UploadFile = File(...),
    title: Optional[str] = Form(None),
    current: Business = Depends(get_current_user),
):
    data = await file.read()
    if not data:
        raise HTTPException(status_code=400, detail="Dosya boş")
    if len(data) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=400, detail="Dosya 2 MB'tan büyük olamaz")

    try:
        text = knowledge_service.extract_text_from_bytes(file.filename or "", data)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    if not text.strip():
        raise HTTPException(status_code=400, detail="Dosyadan metin çıkarılamadı")

    try:
        doc = await knowledge_service.ingest_document(
            business_id=str(current.id),
            title=(title or file.filename or "Belge").strip(),
            raw_content=text,
            source_type="file",
            filename=file.filename,
            mime_type=file.content_type,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return {
        "id": str(doc.id),
        "title": doc.title,
        "chunk_count": len(doc.chunks),
        "char_count": len(doc.raw_content),
    }


@router.get("/{doc_id}")
async def get_doc(doc_id: str, current: Business = Depends(get_current_user)):
    doc = await knowledge_service.get_document(str(current.id), doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Belge bulunamadı")
    return {
        "id": str(doc.id),
        "title": doc.title,
        "source_type": doc.source_type,
        "filename": doc.filename,
        "raw_content": doc.raw_content,
        "chunk_count": len(doc.chunks),
        "created_at": doc.created_at.isoformat(),
        "updated_at": doc.updated_at.isoformat(),
    }


@router.delete("/{doc_id}")
async def delete_doc(doc_id: str, current: Business = Depends(get_current_user)):
    ok = await knowledge_service.delete_document(str(current.id), doc_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Belge bulunamadı")
    return {"ok": True}


class SearchRequest(BaseModel):
    query: str
    top_k: int = 4


@router.post("/search")
async def search_docs(req: SearchRequest, current: Business = Depends(get_current_user)):
    """Debug endpoint — same retrieval the AI uses."""
    return {"results": await knowledge_service.search(str(current.id), req.query, top_k=req.top_k)}


# ── Knowledge gaps (questions the AI could not answer) ─────────────────────

@router.get("/gaps/list")
async def list_gaps(
    status: Optional[str] = None,
    current: Business = Depends(get_current_user),
):
    return {"gaps": await knowledge_service.list_gaps(str(current.id), status)}


class UpdateGapRequest(BaseModel):
    status: str  # open | resolved | dismissed


@router.patch("/gaps/{gap_id}")
async def update_gap(
    gap_id: str,
    req: UpdateGapRequest,
    current: Business = Depends(get_current_user),
):
    ok = await knowledge_service.update_gap_status(str(current.id), gap_id, req.status)
    if not ok:
        raise HTTPException(status_code=404, detail="Kayıt bulunamadı veya geçersiz durum")
    return {"ok": True}


@router.delete("/gaps/{gap_id}")
async def delete_gap(gap_id: str, current: Business = Depends(get_current_user)):
    ok = await knowledge_service.delete_gap(str(current.id), gap_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Kayıt bulunamadı")
    return {"ok": True}


# ── Business facts preview (so the owner can see what the AI knows) ────────

@router.get("/facts/preview")
async def facts_preview(current: Business = Depends(get_current_user)):
    return {"facts": await knowledge_service.build_business_facts(current)}


# ── One-shot maintenance: backfill language on legacy chunks ───────────────

@router.post("/maintenance/backfill-languages")
async def backfill_chunk_languages(current: Business = Depends(get_current_user)):
    """Detect and persist the `language` field on existing knowledge chunks
    that were ingested before the multilingual upgrade. Idempotent."""
    updated = await knowledge_service.backfill_chunk_languages(str(current.id))
    return {"updated_chunks": updated}
