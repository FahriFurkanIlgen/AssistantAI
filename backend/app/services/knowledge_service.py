"""
Knowledge Service - RAG (retrieval augmented generation) over business docs.

Pipeline:
  1) ingest()        — chunk + embed + persist
  2) search()        — embed query, HYBRID (cosine + keyword) top-k
  3) delete()        — remove a document

Also exposes:
  - build_business_facts(business) — virtual "ground-truth" block injected
    into every system prompt so the AI can answer factual questions about
    the business even before any KB doc is uploaded.
  - Knowledge gap logging — questions the assistant could not confidently
    answer are recorded for the owner to fill in.
"""
from __future__ import annotations

import math
import re
from datetime import datetime
from typing import List, Optional

from openai import AsyncOpenAI

from app.config import settings
from app.models.business import Business
from app.models.knowledge import KnowledgeDocument, KnowledgeChunk, KnowledgeGap

_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

EMBED_MODEL = "text-embedding-3-small"
CHUNK_SIZE = 700      # ~ characters per chunk
CHUNK_OVERLAP = 120

# Hybrid score weights (same-language). For cross-language queries we lean
# almost entirely on the multilingual embedding (keyword overlap is meaningless
# when the query and the passage are in different languages).
W_VECTOR = 0.7
W_KEYWORD = 0.3
W_VECTOR_XLING = 1.0
W_KEYWORD_XLING = 0.0

# Compact multilingual stopword list (TR + EN + RU + DE). Kept small on
# purpose so we don't accidentally drop signal-bearing terms.
_STOPWORDS = {
    # Turkish
    "ve", "veya", "ile", "için", "de", "da", "mi", "mı", "mu", "mü",
    "bir", "bu", "şu", "o", "ne", "ki", "ya", "ya da",
    # English
    "the", "a", "an", "is", "are", "of", "to", "and", "or", "for",
    "in", "on", "at", "do", "does", "you", "your", "my", "i",
    # Russian (и, в, на, с, по, я, вы, мне etc.)
    "и", "в", "на", "с", "по", "я", "ты", "вы", "он", "она", "это", "этот", "эта",
    "не", "да", "нет", "как", "или", "у", "о", "из", "к", "при",
    # German
    "der", "die", "das", "den", "dem", "des", "ein", "eine", "einen", "einem",
    "und", "oder", "ist", "sind", "war", "ich", "du", "sie", "er", "es",
    "für", "mit", "von", "zu", "auf", "im", "in", "als", "auch", "nicht",
    # Arabic (common particles + pronouns)
    "في", "من", "إلى", "على", "عن", "مع", "أو", "و", "لا", "لم", "لن",
    "هو", "هي", "هم", "أنت", "أنا", "نحن", "هذا", "هذه", "ذلك", "تلك",
    "أن", "إن", "قد", "كان", "ليس", "بعد", "قبل", "ال",
}


# ── Chunking ────────────────────────────────────────────────────────────────

def _normalize(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def chunk_text(text: str, size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> List[str]:
    """Naive character-based chunker that prefers paragraph boundaries."""
    text = _normalize(text)
    if not text:
        return []

    # Split by blank lines first so we don't tear paragraphs apart aggressively
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks: List[str] = []
    buf = ""

    for para in paragraphs:
        if len(buf) + len(para) + 2 <= size:
            buf = f"{buf}\n\n{para}".strip()
            continue

        if buf:
            chunks.append(buf)
            # carry tail as overlap context
            buf = buf[-overlap:] if overlap else ""

        # Paragraph itself longer than size — hard-split
        while len(para) > size:
            chunks.append((buf + "\n\n" + para[:size]).strip())
            para = para[size - overlap:]
            buf = ""

        buf = f"{buf}\n\n{para}".strip() if buf else para

    if buf:
        chunks.append(buf)

    # Deduplicate consecutive identical chunks just in case
    deduped: List[str] = []
    for c in chunks:
        if not deduped or deduped[-1] != c:
            deduped.append(c)
    return deduped


# ── Embeddings ──────────────────────────────────────────────────────────────

async def embed_batch(texts: List[str]) -> List[List[float]]:
    if not texts:
        return []
    # OpenAI accepts up to 2048 inputs per request; chunk to be safe
    out: List[List[float]] = []
    batch_size = 64
    for i in range(0, len(texts), batch_size):
        batch = texts[i : i + batch_size]
        resp = await _client.embeddings.create(model=EMBED_MODEL, input=batch)
        out.extend(item.embedding for item in resp.data)
    return out


def cosine(a: List[float], b: List[float]) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = 0.0
    na = 0.0
    nb = 0.0
    for x, y in zip(a, b):
        dot += x * y
        na += x * x
        nb += y * y
    if na == 0 or nb == 0:
        return 0.0
    return dot / (math.sqrt(na) * math.sqrt(nb))


# ── File parsing ────────────────────────────────────────────────────────────

def extract_text_from_bytes(filename: str, data: bytes) -> str:
    """Best-effort plain-text extraction. Supports .txt, .md, .pdf (if pypdf)."""
    name = (filename or "").lower()

    if name.endswith(".pdf"):
        try:
            from pypdf import PdfReader  # type: ignore
            from io import BytesIO
            reader = PdfReader(BytesIO(data))
            parts = [page.extract_text() or "" for page in reader.pages]
            return "\n\n".join(p.strip() for p in parts if p.strip())
        except Exception as exc:  # pragma: no cover
            raise ValueError(f"PDF okunamadı: {exc}") from exc

    # Default: treat as utf-8 text (txt/md/csv...)
    for enc in ("utf-8", "utf-8-sig", "cp1254", "latin-1"):
        try:
            return data.decode(enc)
        except UnicodeDecodeError:
            continue
    raise ValueError("Desteklenmeyen dosya kodlaması")


# ── Ingest & search ─────────────────────────────────────────────────────────

async def ingest_document(
    business_id: str,
    title: str,
    raw_content: str,
    *,
    source_type: str = "text",
    filename: Optional[str] = None,
    mime_type: Optional[str] = None,
) -> KnowledgeDocument:
    """Chunk + embed + persist a new knowledge document."""
    pieces = chunk_text(raw_content)
    if not pieces:
        raise ValueError("Boş içerik — eklenemedi")

    vectors = await embed_batch(pieces)
    chunks = [
        KnowledgeChunk(text=t, embedding=v, language=detect_language(t))
        for t, v in zip(pieces, vectors)
    ]

    doc = KnowledgeDocument(
        business_id=business_id,
        title=title.strip() or (filename or "Adsız belge"),
        source_type=source_type,
        filename=filename,
        mime_type=mime_type,
        raw_content=raw_content,
        chunks=chunks,
        embedding_model=EMBED_MODEL,
    )
    await doc.insert()
    return doc


async def _translate_query(query: str, target: str) -> Optional[str]:
    """Translate a short query to the target language using gpt-4o-mini.

    Used to boost cross-lingual retrieval: we embed both the original and
    the translation, then take the max similarity per chunk. Returns None
    on any failure so the caller can fall back gracefully.
    """
    if not query or not target:
        return None
    try:
        resp = await _client.chat.completions.create(
            model="gpt-4o-mini",
            temperature=0,
            max_tokens=120,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You translate short customer questions for a service "
                        "business assistant. Reply with ONLY the translation, "
                        "no quotes, no commentary."
                    ),
                },
                {
                    "role": "user",
                    "content": f"Translate to {target}:\n{query}",
                },
            ],
        )
        out = (resp.choices[0].message.content or "").strip()
        # Strip surrounding quotes if the model added any
        return out.strip("\"'`") or None
    except Exception:
        return None


async def search(business_id: str, query: str, top_k: int = 4, min_score: float = 0.30) -> List[dict]:
    """Hybrid (vector + keyword) top-k retrieval across a business' KB.

    Multilingual handling:
      • Detect query language and per-chunk language.
      • If they differ, drop keyword weight to zero (lean on the
        multilingual embedding alone) — keyword overlap across scripts is
        meaningless.
      • For cross-lingual queries, also translate the query into the
        dominant KB language and embed both; final vector score is the
        max of the two cosines per chunk.
    """
    query = (query or "").strip()
    if not query:
        return []

    docs = await KnowledgeDocument.find(KnowledgeDocument.business_id == business_id).to_list()
    if not docs:
        return []

    q_lang = detect_language(query)

    # Determine the dominant language of this KB so we know whether to
    # translate. Falls back to "tr" when chunks have no language hint
    # (legacy data ingested before the field existed).
    lang_counts: dict[str, int] = {}
    for doc in docs:
        for chunk in doc.chunks:
            lang_counts[chunk.language or "other"] = lang_counts.get(chunk.language or "other", 0) + 1
    dominant_lang = max(lang_counts, key=lang_counts.get) if lang_counts else "tr"
    if dominant_lang == "other":
        dominant_lang = "tr"

    # Always embed the original query.
    q_vecs: list[list[float]] = []
    q_translations: list[str] = [query]
    q_vec_list = await embed_batch([query])
    if not q_vec_list:
        return []
    q_vecs.append(q_vec_list[0])

    # If cross-lingual, fetch a translation into the KB's dominant language
    # and embed that too. We keep this strictly opt-in by language mismatch
    # to control cost (~1 cheap LLM call per cross-lingual query).
    if q_lang != "other" and q_lang != dominant_lang:
        target_full = {
            "tr": "Turkish",
            "en": "English",
            "de": "German",
            "ru": "Russian",
            "ar": "Arabic",
        }.get(dominant_lang, "Turkish")
        translated = await _translate_query(query, target_full)
        if translated and translated.lower() != query.lower():
            t_vec_list = await embed_batch([translated])
            if t_vec_list:
                q_vecs.append(t_vec_list[0])
                q_translations.append(translated)

    # Tokenize every query variant so same-language chunks can still benefit
    # from keyword overlap against either the original or the translation.
    q_tokens_list = [_tokenize(t) for t in q_translations]

    scored: List[dict] = []
    for doc in docs:
        for chunk in doc.chunks:
            # Max cosine across all query variants
            v = 0.0
            for qv in q_vecs:
                v = max(v, cosine(qv, chunk.embedding))
            v = max(0.0, v)

            chunk_lang = chunk.language or "other"
            # Same-language pairing: full hybrid scoring with keyword overlap
            same_lang = (
                q_lang != "other"
                and chunk_lang != "other"
                and q_lang == chunk_lang
            ) or any(
                # the translated variant matches the chunk language
                t_lang == chunk_lang and chunk_lang != "other"
                for t_lang in (detect_language(t) for t in q_translations[1:])
            )

            if same_lang:
                # Best keyword score across query variants in this language
                k = 0.0
                for toks, t in zip(q_tokens_list, q_translations):
                    if detect_language(t) == chunk_lang or t == query:
                        k = max(k, _keyword_score(toks, chunk.text))
                w_vec, w_kw = W_VECTOR, W_KEYWORD
            else:
                k = 0.0
                w_vec, w_kw = W_VECTOR_XLING, W_KEYWORD_XLING

            combined = w_vec * v + w_kw * k
            if combined >= min_score:
                scored.append(
                    {
                        "score": round(combined, 4),
                        "vector_score": round(v, 4),
                        "keyword_score": round(k, 4),
                        "text": chunk.text,
                        "document_id": str(doc.id),
                        "document_title": doc.title,
                        "chunk_language": chunk_lang,
                        "query_language": q_lang,
                    }
                )

    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored[:top_k]


# ── Tokenization & keyword scoring ──────────────────────────────────────────

# Unicode-aware word regex: matches Latin (incl. äöüß), Turkish (çğıöşü),
# Cyrillic and digits. `[^\W_]` means "word char minus underscore".
_TOKEN_RE = re.compile(r"[^\W_]+", re.UNICODE)


def _tokenize(text: str) -> List[str]:
    return [
        t.lower()
        for t in _TOKEN_RE.findall(text or "")
        if len(t) >= 2 and t.lower() not in _STOPWORDS
    ]


def _keyword_score(query_tokens: List[str], passage: str) -> float:
    """Fraction of unique query tokens that appear in the passage (case-insensitive)."""
    if not query_tokens:
        return 0.0
    q_set = set(query_tokens)
    p_set = set(_tokenize(passage))
    if not q_set:
        return 0.0
    hits = len(q_set & p_set)
    return hits / len(q_set)


# ── Language detection (lightweight, no extra dependency) ───────────────────

_TR_LETTERS = set("çğıİöşüÇĞÖŞÜ")
_DE_LETTERS = set("äöüßÄÖÜ")
_CYRILLIC_RE = re.compile(r"[\u0400-\u04ff]")
# Arabic script: covers Arabic, Arabic Supplement, and presentation forms
# common in WhatsApp/iOS keyboards.
_ARABIC_RE = re.compile(r"[\u0600-\u06ff\u0750-\u077f\ufb50-\ufdff\ufe70-\ufeff]")

_TR_HINTS = {"ve", "için", "bir", "merhaba", "randevu", "saat", "ücret", "fiyat", "adres", "çalışma", "açık", "kapalı"}
_EN_HINTS = {"the", "and", "hello", "price", "hours", "address", "appointment", "please", "thanks", "open", "closed"}
_DE_HINTS = {"und", "hallo", "preis", "adresse", "öffnungszeiten", "termin", "bitte", "danke", "sind", "geschlossen", "geöffnet"}


def detect_language(text: str) -> str:
    """Return one of: tr | en | de | ru | ar | other.

    Cheap heuristic for short user queries and KB chunks. We don't need
    ICU-level accuracy — just enough to (a) decide whether keyword scoring
    is meaningful and (b) decide whether to translate the query.
    """
    if not text:
        return "other"
    s = text.strip()
    if not s:
        return "other"
    # Script-based detection takes priority — unambiguous and free.
    if _ARABIC_RE.search(s):
        return "ar"
    if _CYRILLIC_RE.search(s):
        return "ru"
    lower = s.lower()
    tokens = set(_TOKEN_RE.findall(lower))
    has_tr = any(ch in _TR_LETTERS for ch in s) or bool(tokens & _TR_HINTS)
    has_de = any(ch in _DE_LETTERS for ch in s) or bool(tokens & _DE_HINTS)
    has_en = bool(tokens & _EN_HINTS)
    if has_tr:
        return "tr"
    if has_de:
        return "de"
    if has_en:
        return "en"
    return "other"

# ── Question detection (for gap logging) ────────────────────────────────────

_QUESTION_HINT_RE = re.compile(
    r"(\?|"
    # Turkish
    r"\b(ne|nasıl|nerede|nereden|nereye|kim|kaç|kaça|hangi|nedir|nedirler|niçin|niye|neden|"
    r"var\s*mı|olur\s*mu|yapıyor\s*musunuz|kabul\s*ediyor\s*musunuz|"
    r"fiyat|ücret|saat|adres|telefon|park|iade|garanti|açık|kapalı|çalışı|"
    # English
    r"what|where|when|why|how|who|which|do\s+you|are\s+you|is\s+there|"
    r"price|cost|address|phone|hours|policy|"
    # German
    r"was|wo|wann|warum|wieso|wie|wer|welch|gibt\s+es|haben\s+sie|"
    r"preis|adresse|telefon|öffnungszeiten|termin|"
    # Russian (basic question words + frequent service-domain terms)
    r"что|где|когда|почему|как|кто|сколько|какой|есть\s+ли|"
    r"цена|стоит|адрес|телефон|часы|работа|запись|"
    # Arabic (question words + frequent service-domain terms; also handles ؟)
    r"ما|ماذا|أين|متى|لماذا|كيف|من|كم|أي|هل|"
    r"سعر|ثمن|عنوان|هاتف|ساعات|عمل|موعد|حجز)\b|؟)",
    re.IGNORECASE,
)


def looks_like_question(text: str) -> bool:
    if not text or len(text.strip()) < 6:
        return False
    return bool(_QUESTION_HINT_RE.search(text))


# ── Business facts (virtual ground-truth doc) ───────────────────────────────

_DAY_NAMES = [
    ("monday", "Pazartesi"),
    ("tuesday", "Salı"),
    ("wednesday", "Çarşamba"),
    ("thursday", "Perşembe"),
    ("friday", "Cuma"),
    ("saturday", "Cumartesi"),
    ("sunday", "Pazar"),
]


async def build_business_facts(business: Business) -> str:
    """Construct a compact, structured fact sheet for the AI's system prompt."""
    lines: List[str] = ["İŞLETME GERÇEKLERİ (kesin doğru, asla değiştirme):"]
    lines.append(f"- Ad: {business.name}")
    if business.sector:
        lines.append(f"- Sektör: {business.sector}")
    if business.city:
        lines.append(f"- Şehir: {business.city}")
    if business.address:
        lines.append(f"- Adres: {business.address}")
    if business.phone:
        lines.append(f"- Telefon: {business.phone}")
    if business.email:
        lines.append(f"- E-posta: {business.email}")
    if getattr(business, "instagram_handle", None):
        handle = business.instagram_handle.lstrip("@")  # type: ignore[union-attr]
        lines.append(f"- Instagram: @{handle} (https://www.instagram.com/{handle}/)")

    ws = getattr(business, "working_schedule", None)
    if ws:
        sched_lines = []
        for key, tr in _DAY_NAMES:
            h = getattr(ws, key, None)
            if not h:
                continue
            if h.is_open:
                sched_lines.append(f"  • {tr}: {h.start}–{h.end}")
            else:
                sched_lines.append(f"  • {tr}: Kapalı")
        if sched_lines:
            lines.append("- Çalışma saatleri:")
            lines.extend(sched_lines)

    services = getattr(business, "services", None) or []
    if services:
        lines.append("- Hizmetler / fiyatlar:")
        for s in services:
            bits = [s.name_tr or s.name]
            if s.duration_minutes:
                bits.append(f"{s.duration_minutes} dk")
            if s.price is not None:
                bits.append(f"{s.price:g} TL")
            if s.description:
                bits.append(s.description)
            lines.append(f"  • {' — '.join(bits)}")

    # Canonical staff roster — critical for anti-hallucination on person names.
    try:
        from app.models.staff_member import StaffMember
        staff = await StaffMember.find(
            StaffMember.business_id == str(business.id),
            StaffMember.is_active == True,
        ).to_list()
    except Exception:
        staff = []
    if staff:
        lines.append(
            "- Aktif personel (BU LİSTE İŞLETMENİN TAM PERSONEL KADROSUDUR; "
            "burada olmayan bir kişi işletmede ÇALIŞMIYOR):"
        )
        for s in staff:
            specialties = ", ".join(s.service_names[:5]) if s.service_names else ""
            suffix = f" — uzmanlık: {specialties}" if specialties else ""
            lines.append(f"  • {s.name}{suffix}")
    else:
        lines.append(
            "- Aktif personel: Bu işletmede tanımlı ayrı personel kaydı yoktur. "
            "Müşteri bir kişi adı sorarsa varsayma; 'Bu isimde kayıtlı personelimiz "
            "bulunmuyor' diye yanıtla."
        )

    return "\n".join(lines)


def format_retrieved_context(hits: List[dict]) -> str:
    """Render retrieval hits as a system-prompt block."""
    if not hits:
        return ""
    blocks = []
    for i, h in enumerate(hits, 1):
        blocks.append(
            f"[{i}] Kaynak: {h['document_title']} (benzerlik {h['score']:.2f})\n"
            f"{h['text']}"
        )
    body = "\n\n".join(blocks)
    return (
        "İLGİLİ BİLGİ BANKASI PASAJLARI (kullanıcının son sorusu için önceden alındı — "
        "cevabını SADECE bu pasajlardan ve İŞLETME GERÇEKLERİ bloğundan üret):\n\n"
        f"{body}\n\n"
        "Eğer cevap bu pasajlarda ya da işletme gerçeklerinde net olarak yoksa "
        "'Bu konuda kesin bilgim yok, işletmeyle iletişime geçmenizi öneririm' de. "
        "Tahmin yürütme, dış bilgi kullanma."
    )


# ── Knowledge gaps ──────────────────────────────────────────────────────────

async def log_gap(
    *,
    business_id: str,
    question: str,
    language: str = "tr",
    session_id: Optional[str] = None,
    best_score: float = 0.0,
) -> None:
    """Record an unanswered question. De-duplicates near-identical recent entries."""
    question = (question or "").strip()
    if not question:
        return

    # De-dup: if an OPEN gap with the same normalized question exists, bump it.
    norm = question.lower()
    existing = await KnowledgeGap.find(
        KnowledgeGap.business_id == business_id,
        KnowledgeGap.status == "open",
    ).to_list()
    for g in existing:
        if g.question.strip().lower() == norm:
            g.hit_count += 1
            g.last_seen_at = datetime.utcnow()
            g.best_score = max(g.best_score, best_score)
            await g.save()
            return

    gap = KnowledgeGap(
        business_id=business_id,
        question=question[:500],
        language=language,
        session_id=session_id,
        best_score=best_score,
        hit_count=1,
    )
    await gap.insert()


async def list_gaps(business_id: str, status: Optional[str] = None) -> List[dict]:
    q = KnowledgeGap.find(KnowledgeGap.business_id == business_id)
    if status:
        q = q.find(KnowledgeGap.status == status)
    gaps = await q.to_list()
    gaps.sort(key=lambda g: (g.status != "open", -g.hit_count, g.last_seen_at.timestamp()), reverse=False)
    return [
        {
            "id": str(g.id),
            "question": g.question,
            "language": g.language,
            "best_score": g.best_score,
            "hit_count": g.hit_count,
            "status": g.status,
            "created_at": g.created_at.isoformat(),
            "last_seen_at": g.last_seen_at.isoformat(),
        }
        for g in gaps
    ]


async def update_gap_status(business_id: str, gap_id: str, status: str) -> bool:
    if status not in ("open", "resolved", "dismissed"):
        return False
    g = await KnowledgeGap.get(gap_id)
    if not g or g.business_id != business_id:
        return False
    g.status = status
    g.resolved_at = datetime.utcnow() if status != "open" else None
    await g.save()
    return True


async def delete_gap(business_id: str, gap_id: str) -> bool:
    g = await KnowledgeGap.get(gap_id)
    if not g or g.business_id != business_id:
        return False
    await g.delete()
    return True


async def backfill_chunk_languages(business_id: str) -> int:
    """Detect and persist `language` on every chunk that's missing or "other".

    Returns the number of chunks that were updated. Safe to run repeatedly.
    """
    docs = await KnowledgeDocument.find(KnowledgeDocument.business_id == business_id).to_list()
    updated = 0
    for doc in docs:
        dirty = False
        for chunk in doc.chunks:
            if chunk.language and chunk.language != "other":
                continue
            new_lang = detect_language(chunk.text)
            if new_lang != chunk.language:
                chunk.language = new_lang
                dirty = True
                updated += 1
        if dirty:
            doc.updated_at = datetime.utcnow()
            await doc.save()
    return updated


async def list_documents(business_id: str) -> List[dict]:
    docs = await KnowledgeDocument.find(KnowledgeDocument.business_id == business_id).to_list()
    docs.sort(key=lambda d: d.created_at, reverse=True)
    return [
        {
            "id": str(d.id),
            "title": d.title,
            "source_type": d.source_type,
            "filename": d.filename,
            "chunk_count": len(d.chunks),
            "char_count": len(d.raw_content),
            "created_at": d.created_at.isoformat(),
            "updated_at": d.updated_at.isoformat(),
        }
        for d in docs
    ]


async def get_document(business_id: str, doc_id: str) -> Optional[KnowledgeDocument]:
    doc = await KnowledgeDocument.get(doc_id)
    if not doc or doc.business_id != business_id:
        return None
    return doc


async def delete_document(business_id: str, doc_id: str) -> bool:
    doc = await get_document(business_id, doc_id)
    if not doc:
        return False
    await doc.delete()
    return True
