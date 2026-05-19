"""
Customer Service - durable memory across conversations.

Responsibilities:
  - Normalize phone numbers (Turkish-friendly canonical form).
  - Find/upsert Customer documents per business + phone.
  - Render a "TEKRAR MÜŞTERİ" memory block injected into the system prompt.
  - Generate/refresh a rolling LLM-based memory summary + structured
    preferences from a conversation transcript (fire-and-forget).
"""
from __future__ import annotations

import json
import logging
import re
from datetime import datetime, timedelta
from typing import Optional

from openai import AsyncOpenAI

from app.config import settings
from app.models.customer import Customer, CustomerPreferences
from app.models.conversation import Conversation

logger = logging.getLogger(__name__)
_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

SUMMARY_MODEL = "gpt-4o-mini"
SUMMARY_THROTTLE_SECONDS = 60       # don't re-summarize the same customer more often
SUMMARY_MIN_USER_MESSAGES = 3       # need at least this many user turns to summarize
TRANSCRIPT_CHAR_BUDGET = 3500


# ── Phone normalization ─────────────────────────────────────────────────────

_PHONE_RE = re.compile(r"(?:\+?\d[\s\-().]*){9,15}")


def normalize_phone(phone: Optional[str]) -> str:
    """Canonical form: digits only, no Turkish country prefix, no leading 0."""
    digits = re.sub(r"\D", "", phone or "")
    if not digits:
        return ""
    # +90 / 90 prefix
    if digits.startswith("90") and len(digits) >= 12:
        digits = digits[2:]
    # leading 0 prefix
    if digits.startswith("0") and len(digits) >= 11:
        digits = digits[1:]
    return digits


def detect_phone_in_text(text: str) -> Optional[str]:
    """Extract a phone-like substring from arbitrary user text."""
    if not text:
        return None
    for m in _PHONE_RE.finditer(text):
        candidate = m.group(0)
        digits = re.sub(r"\D", "", candidate)
        if 10 <= len(digits) <= 13:
            return candidate
    return None


# ── Lookup & upsert ─────────────────────────────────────────────────────────

async def find_by_phone(business_id: str, phone: str) -> Optional[Customer]:
    norm = normalize_phone(phone)
    if not norm:
        return None
    return await Customer.find_one(
        Customer.business_id == business_id,
        Customer.phone == norm,
    )


async def upsert_customer(
    *,
    business_id: str,
    name: str,
    phone: str,
    email: Optional[str] = None,
    language: Optional[str] = None,
    increment_appointments: bool = False,
) -> Customer:
    """Create or update a Customer. Returns the persisted document."""
    norm = normalize_phone(phone)
    if not norm:
        raise ValueError("Geçersiz telefon numarası")

    existing = await find_by_phone(business_id, norm)
    now = datetime.utcnow()

    if existing:
        if name and name != existing.name:
            existing.name = name
        if email and email != existing.email:
            existing.email = email
        if language and language != existing.language_preference:
            existing.language_preference = language
        if phone and phone != existing.phone_display:
            existing.phone_display = phone
        if increment_appointments:
            existing.total_appointments += 1
        existing.last_seen_at = now
        existing.updated_at = now
        await existing.save()
        return existing

    customer = Customer(
        business_id=business_id,
        name=name or "İsimsiz",
        phone=norm,
        phone_display=phone,
        email=email,
        language_preference=language or "tr",
        total_appointments=1 if increment_appointments else 0,
        last_seen_at=now,
    )
    await customer.insert()
    return customer


# ── Memory rendering for the system prompt ──────────────────────────────────

def format_memory_block(customer: Customer) -> str:
    lines = ["=== TEKRAR MÜŞTERİ TANIMLANDI ==="]
    lines.append(f"- Ad: {customer.name}")
    if customer.phone_display:
        lines.append(f"- Telefon: {customer.phone_display}")
    if customer.email:
        lines.append(f"- E-posta: {customer.email}")
    lines.append(f"- Dil tercihi: {customer.language_preference.upper()}")
    lines.append(f"- Geçmiş randevu sayısı: {customer.total_appointments}")
    if customer.last_seen_at:
        lines.append(f"- Son ziyaret: {customer.last_seen_at.strftime('%Y-%m-%d')}")

    prefs = customer.preferences
    pref_lines = []
    if prefs.preferred_staff:
        pref_lines.append(f"  • Tercih ettiği personel: {prefs.preferred_staff}")
    if prefs.preferred_times:
        pref_lines.append(f"  • Tercih ettiği zaman: {prefs.preferred_times}")
    if prefs.favorite_services:
        pref_lines.append(f"  • Sık aldığı hizmetler: {', '.join(prefs.favorite_services)}")
    if prefs.allergies:
        pref_lines.append(f"  • Alerjiler / dikkat: {prefs.allergies}")
    if prefs.notes:
        pref_lines.append(f"  • Notlar: {prefs.notes}")
    if pref_lines:
        lines.append("TERCİHLER:")
        lines.extend(pref_lines)

    if customer.tags:
        lines.append(f"ETİKETLER: {', '.join(customer.tags)}")

    if customer.memory_summary:
        lines.append(f"ÖNCEKİ KONUŞMA ÖZETİ:\n  {customer.memory_summary}")

    lines.append(
        "DAVRANIŞ KURALLARI:\n"
        "- Müşteriyi adıyla 'Tekrar hoş geldiniz [ad]!' diye karşıla.\n"
        "- Tekrar isim/telefon SORMA — bilgiler zaten elinde.\n"
        "- Uygunsa tercihlerine atıfta bulun (örn. 'Yine Ahmet Usta ile mi?').\n"
        "- Memory'deki bilgileri müşteriyle DOĞRULAMADAN faktüel iddia olarak söyleme; "
        "kibarca teyit ettir."
    )
    return "\n".join(lines)


# ── Summarization (fire-and-forget) ─────────────────────────────────────────

def _build_transcript(conversation: Conversation) -> str:
    parts = []
    total = 0
    for msg in conversation.messages[-40:]:
        if msg.role not in ("user", "assistant"):
            continue
        content = (msg.content or "").strip()
        if not content:
            continue
        line = f"{msg.role.upper()}: {content}"
        if total + len(line) > TRANSCRIPT_CHAR_BUDGET:
            break
        parts.append(line)
        total += len(line)
    return "\n".join(parts)


def _count_user_messages(conversation: Conversation) -> int:
    return sum(1 for m in conversation.messages if m.role == "user" and (m.content or "").strip())


async def maybe_update_summary(customer: Customer, conversation: Conversation) -> bool:
    """
    Refresh the customer's rolling memory summary + preferences based on the
    given conversation. Throttled & safe — returns True if an update happened.
    Designed to be called as a background task.
    """
    try:
        if _count_user_messages(conversation) < SUMMARY_MIN_USER_MESSAGES:
            return False
        if customer.last_summary_at and (
            datetime.utcnow() - customer.last_summary_at
        ) < timedelta(seconds=SUMMARY_THROTTLE_SECONDS):
            return False

        transcript = _build_transcript(conversation)
        if not transcript:
            return False

        existing = customer.memory_summary or "YOK"
        existing_prefs = customer.preferences.model_dump(exclude_none=True)
        existing_tags = customer.tags

        system = (
            "Sen bir CRM özet asistanısın. Bir müşterinin işletmeyle yaptığı son "
            "konuşmayı oku ve mevcut özetiyle birleştirip 2-3 cümlelik kısa, faktüel "
            "Türkçe özet üret. Kişisel bilgileri (isim/telefon) yazma — zaten kayıtlı. "
            "Sadece müşteri tercihleri, sorduğu sorular, dikkat gerektiren detaylar, "
            "randevu bilgileri. ÇIKTIN YALNIZCA aşağıdaki JSON şemasında olsun, başka "
            "hiçbir şey yazma:\n"
            "{\n"
            '  "summary": "2-3 cümle (string)",\n'
            '  "tags": ["kısa etiketler (string[])"],\n'
            '  "preferences": {\n'
            '    "preferred_staff": "string|null",\n'
            '    "preferred_times": "string|null",\n'
            '    "favorite_services": ["string"],\n'
            '    "allergies": "string|null",\n'
            '    "notes": "string|null"\n'
            "  }\n"
            "}\n"
            "Yeni bilgi yoksa mevcut değerleri koru. Hiçbir alan uydurma — "
            "konuşmada açıkça geçmeyenleri null veya boş bırak."
        )
        user_msg = (
            f"Mevcut özet:\n{existing}\n\n"
            f"Mevcut tercihler (JSON):\n{json.dumps(existing_prefs, ensure_ascii=False)}\n\n"
            f"Mevcut etiketler: {existing_tags}\n\n"
            f"Son konuşma:\n{transcript}"
        )

        resp = await _client.chat.completions.create(
            model=SUMMARY_MODEL,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user_msg},
            ],
            response_format={"type": "json_object"},
            temperature=0.2,
        )
        raw = resp.choices[0].message.content or "{}"
        data = json.loads(raw)

        summary = (data.get("summary") or "").strip()
        if summary:
            customer.memory_summary = summary[:1000]

        tags = data.get("tags") or []
        if isinstance(tags, list):
            customer.tags = [str(t).strip() for t in tags if str(t).strip()][:10]

        prefs = data.get("preferences") or {}
        if isinstance(prefs, dict):
            current = customer.preferences.model_dump()
            for k in (
                "preferred_staff",
                "preferred_times",
                "allergies",
                "notes",
            ):
                v = prefs.get(k)
                if v and isinstance(v, str):
                    current[k] = v.strip()[:500]
            fs = prefs.get("favorite_services")
            if isinstance(fs, list) and fs:
                # merge, dedupe, cap
                merged = list(dict.fromkeys([*current.get("favorite_services", []), *map(str, fs)]))
                current["favorite_services"] = [s.strip() for s in merged if str(s).strip()][:10]
            customer.preferences = CustomerPreferences(**current)

        customer.last_summary_at = datetime.utcnow()
        customer.updated_at = datetime.utcnow()
        await customer.save()
        return True
    except Exception as exc:  # pragma: no cover
        logger.exception("maybe_update_summary failed: %s", exc)
        return False


async def increment_conversation_count(customer: Customer) -> None:
    """Bump conversation counter (called once per new session)."""
    try:
        customer.total_conversations += 1
        customer.last_seen_at = datetime.utcnow()
        customer.updated_at = datetime.utcnow()
        await customer.save()
    except Exception:
        pass
