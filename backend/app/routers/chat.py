"""
Chat Router - SSE streaming chat endpoint for the AI assistant.
"""
import logging
import uuid
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional
import io
import json
import asyncio

from openai import AuthenticationError, APIError, RateLimitError, AsyncOpenAI

from app.config import settings
from app.models.business import Business
from app.models.conversation import Conversation, Message
from app.services.ai_service import AIService
from app.services.appointment_service import AppointmentService
from app.services.vision_service import is_instagram_url, extract_og_image, fetch_instagram_portfolio
from app.services import instagram_service
from app.services import knowledge_service
from app.services import customer_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/chat", tags=["chat"])

# Voices accepted by OpenAI tts-1 — 'nova' works well for Turkish.
_TTS_VOICES = {"alloy", "echo", "fable", "onyx", "nova", "shimmer"}
_TTS_MAX_CHARS = 1500  # safety cap (one TTS call ~ a minute of audio)
_tts_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    language: Optional[str] = "tr"
    image_base64: Optional[str] = None   # data:image/...;base64,... (file upload)
    image_url: Optional[str] = None      # Instagram post URL or direct image URL


class Citation(BaseModel):
    title: str
    score: float


class ChatResponse(BaseModel):
    session_id: str
    reply: str
    appointment_created: bool = False
    appointment_id: Optional[str] = None
    citations: list[Citation] = []


@router.post("/{business_slug}", response_model=ChatResponse)
async def chat(business_slug: str, request: ChatRequest):
    business = await Business.find_one(Business.slug == business_slug, Business.is_active == True)
    if not business:
        raise HTTPException(status_code=404, detail="İşletme bulunamadı")

    # Get or create conversation
    session_id = request.session_id or str(uuid.uuid4())
    conversation = await Conversation.find_one(
        Conversation.session_id == session_id,
        Conversation.status == "active",
    )

    if not conversation:
        conversation = Conversation(
            business_id=str(business.id),
            session_id=session_id,
            language=request.language or "tr",
        )
        await conversation.insert()

    # Build services
    appt_service = AppointmentService(business)

    async def tool_executor(fn_name: str, fn_args: dict, conv):
        if fn_name == "search_knowledge_base":
            results = await knowledge_service.search(
                business_id=str(business.id),
                query=fn_args.get("query", ""),
                top_k=fn_args.get("top_k", 4),
            )
            return {"results": results}
        return await appt_service.execute_tool(fn_name, fn_args, conv)

    # Pre-retrieval hook (called once per user turn by AIService); also logs
    # questions the KB could not confidently answer so the owner can fill gaps.
    # Captures the latest hits so we can surface them as citations in the reply.
    last_kb_hits: list[dict] = []

    async def kb_pre_retrieve(query: str):
        hits = await knowledge_service.search(
            business_id=str(business.id),
            query=query,
            top_k=4,
            min_score=0.30,
        )
        last_kb_hits.clear()
        last_kb_hits.extend(hits)
        try:
            best = max((h["score"] for h in hits), default=0.0)
            if best < 0.45 and knowledge_service.looks_like_question(query):
                await knowledge_service.log_gap(
                    business_id=str(business.id),
                    question=query,
                    language=conversation.language,
                    session_id=session_id,
                    best_score=best,
                )
        except Exception:
            pass
        return hits

    business_facts = await knowledge_service.build_business_facts(business)

    # ── Customer memory: try to identify a returning customer for this turn ─
    customer_memory = ""
    matched_customer = None
    candidate_phone = (
        conversation.customer_phone
        or customer_service.detect_phone_in_text(request.message)
    )
    if candidate_phone:
        matched_customer = await customer_service.find_by_phone(
            str(business.id), candidate_phone
        )
        if matched_customer:
            customer_memory = customer_service.format_memory_block(matched_customer)
            # Persist phone on conversation so subsequent turns short-circuit
            if not conversation.customer_phone:
                conversation.customer_phone = candidate_phone
                conversation.customer_name = (
                    conversation.customer_name or matched_customer.name
                )
                await conversation.save()

    ai_service = AIService(
        business,
        tool_executor,
        kb_search=kb_pre_retrieve,
        business_facts=business_facts,
        customer_memory=customer_memory,
    )

    # Resolve image: Instagram link → extract og:image; base64 → use as-is
    resolved_image: Optional[str] = None
    if request.image_base64:
        resolved_image = request.image_base64
    elif request.image_url:
        if is_instagram_url(request.image_url):
            resolved_image = await extract_og_image(request.image_url)
        else:
            resolved_image = request.image_url

    # Process message
    try:
        reply = await ai_service.process_message(
            conversation=conversation,
            user_message=request.message,
            language=request.language or conversation.language,
            image=resolved_image,
        )
    except AuthenticationError:
        logger.error("OpenAI API key is invalid or missing")
        raise HTTPException(
            status_code=503,
            detail="AI servisi şu anda kullanılamıyor. Lütfen daha sonra tekrar deneyin.",
        )
    except RateLimitError:
        logger.warning("OpenAI rate limit hit")
        raise HTTPException(
            status_code=429,
            detail="Çok fazla istek. Lütfen birkaç saniye sonra tekrar deneyin.",
        )
    except APIError as e:
        logger.error(f"OpenAI API error: {e}")
        raise HTTPException(
            status_code=502,
            detail="AI servisinde geçici bir sorun var. Lütfen tekrar deneyin.",
        )
    except Exception as e:
        logger.exception(f"Unexpected error in chat: {e}")
        raise HTTPException(
            status_code=500,
            detail="Bir hata oluştu. Lütfen tekrar deneyin.",
        )

    # ── Memory refresh (background, throttled) ──────────────────────────────
    # If a customer was identified for this turn, asynchronously update their
    # rolling summary + extracted preferences from the latest transcript.
    if matched_customer is not None:
        asyncio.create_task(
            customer_service.maybe_update_summary(matched_customer, conversation)
        )

    # ── Citations: unique sources of the KB chunks retrieved this turn ──────
    # We only surface them if at least one hit was reasonably confident, so we
    # don't flash a "source" badge for cosmetic small-talk answers.
    citations: list[Citation] = []
    seen_titles: set[str] = set()
    for h in last_kb_hits:
        if h.get("score", 0) < 0.35:
            continue
        title = h.get("document_title") or "Bilgi bankası"
        if title in seen_titles:
            continue
        seen_titles.add(title)
        citations.append(Citation(title=title, score=round(float(h["score"]), 2)))
        if len(citations) >= 3:
            break

    return ChatResponse(
        session_id=session_id,
        reply=reply,
        appointment_created=conversation.appointment_id is not None,
        appointment_id=conversation.appointment_id,
        citations=citations,
    )


@router.get("/{business_slug}/welcome")
async def get_welcome(business_slug: str, lang: str = "tr"):
    business = await Business.find_one(Business.slug == business_slug, Business.is_active == True)
    if not business:
        raise HTTPException(status_code=404, detail="İşletme bulunamadı")

    welcome_by_lang = {
        "tr": business.ai_welcome_message_tr,
        "en": business.ai_welcome_message_en,
        "ru": business.ai_welcome_message_ru,
        "de": business.ai_welcome_message_de,
        "ar": business.ai_welcome_message_ar,
    }
    message = welcome_by_lang.get(lang) or business.ai_welcome_message_tr

    # Instagram ikonunu sadece Graph API entegrasyonu aktifse göster.
    ig_cfg = business.instagram
    ig_handle = (
        (ig_cfg.ig_username or business.instagram_handle)
        if (ig_cfg and ig_cfg.enabled and ig_cfg.access_token and ig_cfg.ig_user_id)
        else None
    )

    return {
        "business_name": business.name,
        "persona_name": business.ai_persona_name,
        "welcome_message": message,
        "sector": business.sector,
        "instagram_handle": ig_handle,
        "logo_url": business.logo_url,
        "chat_theme": business.chat_theme or "light",
        "suggested_questions": list(business.suggested_questions or []),
    }


@router.get("/{business_slug}/portfolio")
async def get_portfolio(business_slug: str):
    """Return Instagram portfolio posts for the business.

    Öncelik: işletme Instagram Graph API ile yapılandırılmışsa
    resmi medya endpoint'i kullanılır. Yoksa public scrape fallback.
    """
    business = await Business.find_one(Business.slug == business_slug, Business.is_active == True)
    if not business:
        raise HTTPException(status_code=404, detail="İşletme bulunamadı")

    cfg = business.instagram
    handle = (cfg.ig_username if cfg and cfg.ig_username else business.instagram_handle) or None
    if handle:
        handle = handle.lstrip("@")
    instagram_url = f"https://www.instagram.com/{handle}/" if handle else None

    # 1) Graph API (resmi, güvenilir)
    if cfg and cfg.enabled and cfg.access_token and cfg.ig_user_id:
        try:
            posts = await instagram_service.fetch_media(business, limit=12)
            return {
                "instagram_handle": handle,
                "instagram_url": instagram_url,
                "posts": posts,
                "source": "graph_api",
            }
        except Exception:
            pass  # fallback'e düş

    # 2) Public scrape fallback
    if not handle:
        return {"instagram_handle": None, "posts": [], "instagram_url": None}
    posts = await fetch_instagram_portfolio(handle)
    return {
        "instagram_handle": handle,
        "instagram_url": instagram_url,
        "posts": posts,
        "source": "scrape",
    }


class TTSRequest(BaseModel):
    text: str
    voice: Optional[str] = "nova"


@router.post("/{business_slug}/tts")
async def synthesize_speech(business_slug: str, request: TTSRequest):
    """Synthesize an assistant reply to speech (MP3) via OpenAI tts-1."""
    business = await Business.find_one(
        Business.slug == business_slug, Business.is_active == True
    )
    if not business:
        raise HTTPException(status_code=404, detail="İşletme bulunamadı")

    text = (request.text or "").strip()
    if not text:
        raise HTTPException(status_code=400, detail="Boş metin seslendirilemez")
    if len(text) > _TTS_MAX_CHARS:
        text = text[:_TTS_MAX_CHARS]

    voice = (request.voice or business.tts_voice or "nova").lower()
    if voice not in _TTS_VOICES:
        voice = "nova"

    try:
        # OpenAI returns the full MP3; we relay it in one response.
        speech = await _tts_client.audio.speech.create(
            model="tts-1",
            voice=voice,
            input=text,
            response_format="mp3",
        )
        audio_bytes = speech.content  # type: ignore[attr-defined]
    except RateLimitError:
        raise HTTPException(status_code=429, detail="Ses servisi meşgul, biraz sonra deneyin")
    except (AuthenticationError, APIError) as e:
        logger.error(f"TTS error: {e}")
        raise HTTPException(status_code=502, detail="Ses servisi şu an kullanılamıyor")
    except Exception as e:
        logger.exception(f"Unexpected TTS error: {e}")
        raise HTTPException(status_code=500, detail="Sesli yanıt üretilemedi")

    return StreamingResponse(
        iter([audio_bytes]),
        media_type="audio/mpeg",
        headers={"Cache-Control": "no-store"},
    )


# ── Speech → Text (Whisper) ──────────────────────────────────────────────
_STT_MAX_BYTES = 8 * 1024 * 1024  # 8 MB cap (Whisper accepts up to 25 MB)


@router.post("/{business_slug}/stt")
async def transcribe_audio(
    business_slug: str,
    audio: UploadFile = File(...),
    language: Optional[str] = Form("tr"),
):
    """Transcribe a short user voice clip via OpenAI Whisper."""
    business = await Business.find_one(
        Business.slug == business_slug, Business.is_active == True
    )
    if not business:
        raise HTTPException(status_code=404, detail="İşletme bulunamadı")

    raw = await audio.read()
    if not raw:
        raise HTTPException(status_code=400, detail="Boş ses dosyası")
    if len(raw) > _STT_MAX_BYTES:
        raise HTTPException(status_code=413, detail="Ses dosyası çok büyük (max 8 MB)")

    # Whisper needs a file-like object with a filename hint for format detection.
    filename = audio.filename or "clip.webm"
    buf = io.BytesIO(raw)
    buf.name = filename

    try:
        result = await _tts_client.audio.transcriptions.create(
            model="whisper-1",
            file=buf,
            language=(language or "tr")[:2],
        )
        text = (result.text or "").strip()
    except RateLimitError:
        raise HTTPException(status_code=429, detail="Ses servisi meşgul, biraz sonra deneyin")
    except (AuthenticationError, APIError) as e:
        logger.error(f"STT error: {e}")
        raise HTTPException(status_code=502, detail="Ses tanıma servisi şu an kullanılamıyor")
    except Exception as e:
        logger.exception(f"Unexpected STT error: {e}")
        raise HTTPException(status_code=500, detail="Ses metne dönüştürülemedi")

    return {"text": text, "language": language or "tr"}
