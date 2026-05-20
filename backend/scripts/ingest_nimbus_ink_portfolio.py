"""
Nimbus Ink — Portfolio (görsel) ingest seed.

Ne yapar:
  1. @nimbus_ink Instagram profilinden son post'ları çeker
     (vision_service.fetch_instagram_portfolio).
  2. Her post için GPT-4o Vision ile yapılandırılmış Türkçe analiz üretir
     (tarz, çizgi tipi, kompozisyon, önerilen boyut/bölge, ipucu).
  3. Tüm girdileri tek bir markdown bilgi bankası dokümanı olarak derler
     ve `ingest_document` ile chunk + embed eder.
  4. Asistan `search_knowledge_base` aracı ile kullanıcının fikrine en yakın
     çalışmayı bulup Instagram linkiyle gösterebilir.

Manuel fallback:
  Instagram scraping başarısız olursa (IG sık sık 403 verir),
  `backend/scripts/data/nimbus_ink/portfolio.json` dosyasındaki liste
  kullanılır. Format:
    [{ "shortcode": "...", "url": "...", "thumbnail": "...",
       "caption": "(opsiyonel)" }]

Kullanım (backend/ klasöründen):
    .\\venv\\Scripts\\python.exe -m scripts.ingest_nimbus_ink_portfolio
    # IG fetch'i atlamak istersen:
    .\\venv\\Scripts\\python.exe -m scripts.ingest_nimbus_ink_portfolio --manual

Önkoşullar:
    - Önce `scripts.seed_nimbus_ink` çalıştırılmış olmalı (Business
      kaydı slug="nimbus-ink" ile mevcut olmalı).
    - `.env` içinde `OPENAI_API_KEY` ve `MONGODB_URL` ayarlı olmalı.

Idempotent: Bu işletmeye ait, başlığı "[SEED-PORTFOLIO] " ile başlayan
tüm dokümanlar önce silinir.
"""

from __future__ import annotations

import argparse
import asyncio
import base64
import json
import mimetypes
import re
from pathlib import Path
from typing import List, Optional

import httpx
from openai import AsyncOpenAI
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie

from app.config import settings
from app.models.business import Business
from app.models.staff_member import StaffMember
from app.models.customer import Customer
from app.models.appointment import Appointment
from app.models.conversation import Conversation
from app.models.otp_code import OtpCode
from app.models.knowledge import KnowledgeDocument, KnowledgeGap
from app.services.knowledge_service import ingest_document
from app.services.vision_service import (
    extract_og_image,
    extract_instagram_url,
    fetch_instagram_portfolio,
)
from app.services import instagram_service


BUSINESS_SLUG = "nimbus-ink"
INSTAGRAM_HANDLE = "nimbus_ink"
DATA_DIR = Path(__file__).parent / "data" / "nimbus_ink"
MANUAL_FILE = DATA_DIR / "portfolio.json"
TITLE_PREFIX = "[SEED-PORTFOLIO] "
DOC_TITLE = f"{TITLE_PREFIX}Instagram Portfolyo (@{INSTAGRAM_HANDLE})"
MAX_POSTS = 9
VISION_MODEL = "gpt-4o-mini"

_openai = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

# IG post HTML'inden display_url çekmek için (og:image artık servis edilmiyor).
_BROWSER_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}
_DISPLAY_URL_RE = re.compile(r'"display_url"\s*:\s*"(https?://[^"]+)"')


def _unescape_json_url(s: str) -> str:
    """JSON-escaped URL'i decode et (\\u0026 → &, \\/ → /)."""
    try:
        # JSON string literal trick'i: bir JSON string'i içine yerleştirip yükle
        return json.loads(f'"{s}"')
    except Exception:
        return s.replace("\\u0026", "&").replace("\\/", "/")


async def _extract_display_url(post_url: str) -> Optional[str]:
    """IG post sayfasının HTML'inden ilk `display_url`'i çek."""
    try:
        async with httpx.AsyncClient(follow_redirects=True, timeout=15) as client:
            resp = await client.get(post_url, headers=_BROWSER_HEADERS)
        if resp.status_code != 200:
            return None
        m = _DISPLAY_URL_RE.search(resp.text)
        if not m:
            return None
        return _unescape_json_url(m.group(1))
    except Exception:
        return None


VISION_SYSTEM_PROMPT = (
    "Sen Nimbus Ink minimal dövme stüdyosunun portfolyo etiketleyicisisin. "
    "Sana stüdyonun bir dövme çalışmasının fotoğrafı verilecek. "
    "Çalışmayı analiz edip kısa, yapılandırılmış Türkçe bir kart üret. "
    "Asistan bu kartı daha sonra müşterinin fikriyle eşleştirip benzer "
    "çalışma olarak Instagram linkini gösterecek. "
    "Asla uydurma; sadece görselde gerçekten gördüklerini yaz. "
    "Çıktıyı şu sabit alan başlıkları ile ver (her biri tek satır):\n"
    "Konu: <çalışmanın temel motifi, örn. 'minimal ay ve dağ silüeti'>\n"
    "Tarz: <fineline / dotwork / lettering / geometric / micro / mixed>\n"
    "Çizgi tipi: <single needle / ince / orta / kalın>\n"
    "Boyut tahmini: <yaklaşık X-Y cm>\n"
    "Bölge: <görseldeki vücut bölgesi ya da 'belirsiz/flash'>\n"
    "Detay yoğunluğu: <düşük / orta / yüksek>\n"
    "Renk: <siyah / siyah+gri / renkli>\n"
    "Kime uygun: <kısa cümle — örn. 'ilk dövmesi olanlar için ideal'>\n"
    "Anahtar kelimeler: <virgüllü 4-8 etiket, TR + EN karışık>\n"
)


def _load_manual() -> List[dict]:
    if not MANUAL_FILE.exists():
        return []
    try:
        data = json.loads(MANUAL_FILE.read_text(encoding="utf-8"))
        if not isinstance(data, list):
            return []
        cleaned: List[dict] = []
        for p in data:
            if not isinstance(p, dict):
                continue
            url = (p.get("url") or "").strip()
            thumb = (p.get("thumbnail") or "").strip()
            image_file = (p.get("image_file") or "").strip()
            if "example.com" in url or "example.com" in thumb:
                continue
            # En az url / thumbnail / image_file biri olmalı
            if not (url or thumb or image_file):
                continue
            cleaned.append(p)
        return cleaned
    except Exception as exc:
        print(f"⚠ Manuel JSON okunamadı: {exc}")
        return []


def _load_local_image_as_data_url(rel_or_abs: str) -> Optional[str]:
    """Lokal dosyayı base64 data URL'e çevir (Vision API dokuümanlanmış format)."""
    p = Path(rel_or_abs)
    if not p.is_absolute():
        # data/nimbus_ink/ klasörüne göre göreceli
        p = DATA_DIR / rel_or_abs
    if not p.exists() or not p.is_file():
        return None
    mime, _ = mimetypes.guess_type(p.name)
    if not mime:
        mime = "image/jpeg"
    try:
        b = p.read_bytes()
    except Exception as exc:
        print(f"     ⚠ dosya okunamadı ({p}): {exc}")
        return None
    b64 = base64.b64encode(b).decode("ascii")
    return f"data:{mime};base64,{b64}"


async def _hydrate_post(post: dict) -> dict:
    """Bir post kaydını normalize et:
      - shortcode çıkar
      - thumbnail önceliği: image_file (lokal) > thumbnail (URL) > IG sayfasından dene
      - public_thumbnail: kullanıcıya/UI'a gösterilebilir asıl URL (IG permalink veya thumb)
    """
    url = (post.get("url") or "").strip()
    shortcode = (post.get("shortcode") or "").strip()
    thumbnail = (post.get("thumbnail") or "").strip()
    image_file = (post.get("image_file") or "").strip()

    if not url and shortcode:
        url = f"https://www.instagram.com/p/{shortcode}/"
    if url and not shortcode:
        ig = extract_instagram_url(url)
        if ig:
            parts = ig.rstrip("/").split("/")
            if parts:
                shortcode = parts[-1]

    # Vision'a gönderilecek görsel kaynağı
    vision_src: Optional[str] = None
    if image_file:
        vision_src = _load_local_image_as_data_url(image_file)
        if not vision_src:
            print(f"     ⚠ image_file yüklenemedi: {image_file}")
    if not vision_src and thumbnail:
        vision_src = thumbnail
    if not vision_src and url:
        try:
            og = await extract_og_image(url)
        except Exception as exc:
            og = None
            print(f"     ⚠ og:image alınamadı ({url}): {exc}")
        if not og:
            og = await _extract_display_url(url)
        if og:
            vision_src = og
            thumbnail = thumbnail or og

    return {
        "shortcode": shortcode or None,
        "url": url or None,
        "thumbnail": thumbnail or None,
        "image_file": image_file or None,
        "vision_src": vision_src,
        "caption": post.get("caption") or "",
    }


async def _analyze_image(post: dict) -> Optional[str]:
    """GPT-4o Vision ile tek bir görseli yapılandırılmış metne çevir."""
    src = post.get("vision_src") or post.get("thumbnail")
    if not src:
        return None

    user_caption = (post.get("caption") or "").strip()
    user_content: List[dict] = [
        {
            "type": "text",
            "text": (
                "Aşağıdaki Nimbus Ink dövme çalışmasını analiz et ve "
                "talimatına göre yapılandırılmış kart üret."
                + (f"\n\nMüşteri/işletme notu: {user_caption}" if user_caption else "")
            ),
        },
        {"type": "image_url", "image_url": {"url": src, "detail": "low"}},
    ]

    try:
        resp = await _openai.chat.completions.create(
            model=VISION_MODEL,
            messages=[
                {"role": "system", "content": VISION_SYSTEM_PROMPT},
                {"role": "user", "content": user_content},
            ],
            temperature=0.2,
            max_tokens=300,
        )
        return (resp.choices[0].message.content or "").strip() or None
    except Exception as exc:
        print(f"   ✗ Vision hatası ({post.get('shortcode')}): {exc}")
        return None


def _format_entry(idx: int, post: dict, analysis: str) -> str:
    sc = post.get("shortcode") or "—"
    url = post.get("url") or (
        f"https://www.instagram.com/p/{sc}/" if sc != "—" else "—"
    )
    thumb = post.get("thumbnail") or post.get("image_file") or "—"
    return (
        f"### Portfolyo #{idx:02d} — {sc}\n"
        f"- Instagram: {url}\n"
        f"- Görsel: {thumb}\n\n"
        f"{analysis}\n"
    )


async def main(manual_only: bool = False) -> None:
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    await init_beanie(
        database=client[settings.MONGODB_DB_NAME],
        document_models=[
            Business,
            StaffMember,
            Customer,
            Appointment,
            Conversation,
            OtpCode,
            KnowledgeDocument,
            KnowledgeGap,
        ],
    )

    biz = await Business.find_one(Business.slug == BUSINESS_SLUG)
    if not biz:
        raise SystemExit(
            f"❌ Business bulunamadı (slug={BUSINESS_SLUG}). "
            f"Önce `python -m scripts.seed_nimbus_ink` çalıştırın."
        )

    business_id = str(biz.id)
    print(f"✓ Business: {biz.name} (id={business_id})")

    # ── Post listesi: önce manuel JSON, sonra Graph API, en son scrape ─
    posts: List[dict] = _load_manual()
    if posts:
        print(f"📁 Manuel portfolyo: {len(posts)} kayıt yüklendi")

    if not manual_only:
        # 1) Graph API (resmi, güvenilir) — Business.instagram konfigüre ise
        graph_posts: List[dict] = []
        try:
            graph_posts = await instagram_service.fetch_media(biz, limit=MAX_POSTS)
        except Exception as exc:
            print(f"⚠ Graph API media hatası: {exc}")
        if graph_posts:
            seen = {(p.get("shortcode"), p.get("thumbnail")) for p in posts}
            for p in graph_posts:
                key = (p.get("shortcode"), p.get("thumbnail"))
                if key not in seen:
                    posts.append(p)
                    seen.add(key)
            print(f"🔗 Graph API: {len(graph_posts)} medya bulundu "
                  f"(toplam {len(posts)})")
        else:
            # 2) Public scrape fallback (IG aggressive blocker; genelde boş döner)
            try:
                ig_posts = await fetch_instagram_portfolio(INSTAGRAM_HANDLE, MAX_POSTS)
            except Exception as exc:
                ig_posts = []
                print(f"⚠ Instagram scrape hatası: {exc}")
            if ig_posts:
                seen = {(p.get("shortcode"), p.get("thumbnail")) for p in posts}
                for p in ig_posts:
                    key = (p.get("shortcode"), p.get("thumbnail"))
                    if key not in seen:
                        posts.append(p)
                        seen.add(key)
                print(f"📷 Instagram scrape: {len(ig_posts)} post (toplam {len(posts)})")
            else:
                print("⚠ Graph API ve scrape başarısız — sadece manuel kayıtlar kullanılacak.")

    if not posts:
        raise SystemExit(
            "❌ İşlenecek görsel yok. Instagram engelliyor olabilir; "
            f"manuel olarak {MANUAL_FILE} dosyasına portfolio listesi ekleyin."
        )

    posts = posts[:MAX_POSTS]
    print(f"→ {len(posts)} kayıt için thumbnail hazırlanıyor…")

    # ── Eksik thumbnail'leri og:image ile doldur ──────────────────────
    hydrated: List[dict] = []
    for i, post in enumerate(posts, start=1):
        h = await _hydrate_post(post)
        if not h["vision_src"]:
            print(
                f"  · ({i}/{len(posts)}) {h['shortcode'] or h['url']} → "
                f"Vision için görsel bulunamadı, atlanıyor"
            )
            continue
        hydrated.append(h)

    if not hydrated:
        raise SystemExit(
            "❌ Hiçbir post için görsel kaynağı çıkarılamadı.\n"
            "Öneri: portfolio.json kayıtlarına 'image_file' alanı ile lokal dosya yolu ekle\n"
            f"  (örn. image_file: 'images/post1.jpg' — dosya {DATA_DIR}/images/ altında olmalı)."
        )

    print(f"→ {len(hydrated)} görsel analiz edilecek (model={VISION_MODEL})")

    # ── Vision analizi ─────────────────────────────────────────────────
    sections: List[str] = []
    for i, post in enumerate(hydrated, start=1):
        sc = post.get("shortcode") or f"manual-{i}"
        print(f"  · ({i}/{len(hydrated)}) {sc} analiz ediliyor…")
        analysis = await _analyze_image(post)
        if not analysis:
            print(f"     ⚠ atlandı (analiz boş)")
            continue
        sections.append(_format_entry(i, post, analysis))

    if not sections:
        raise SystemExit("❌ Hiçbir görsel analiz edilemedi. İşlem iptal.")

    # ── Markdown dokümanı derle ────────────────────────────────────────
    header = (
        f"# Nimbus Ink — Instagram Portfolyo Kataloğu\n\n"
        f"Bu belge stüdyonun @{INSTAGRAM_HANDLE} Instagram hesabındaki güncel "
        f"çalışmaların görsel analizini içerir. Asistan, müşteri bir fikir "
        f"anlattığında bu girdileri arayıp en yakın çalışmayı Instagram "
        f"linkiyle birlikte örnek olarak gösterir.\n\n"
        f"Kullanım kuralı (asistan için): Bir referans önerirken yalnızca "
        f"BURADA listelenen URL'leri kullan; uydurma link verme. Müşterinin "
        f"tarif ettiği tarz/konu ile en az 2 anahtar kelime eşleşmiyorsa "
        f"'tam birebir örneğimiz yok ama @{INSTAGRAM_HANDLE} hesabımızda "
        f"benzer çalışmalar var' de.\n\n"
        f"Toplam kayıt: {len(sections)}\n"
        f"---\n\n"
    )
    raw_content = header + "\n".join(sections)

    # ── Idempotent temizlik ────────────────────────────────────────────
    existing = await KnowledgeDocument.find(
        KnowledgeDocument.business_id == business_id
    ).to_list()
    old = [d for d in existing if (d.title or "").startswith(TITLE_PREFIX)]
    if old:
        print(f"↺ {len(old)} eski portfolyo dokümanı siliniyor…")
        for d in old:
            await d.delete()

    # ── Ingest ─────────────────────────────────────────────────────────
    print(f"→ Ingest: {DOC_TITLE} ({len(raw_content):,} char)")
    doc = await ingest_document(
        business_id,
        DOC_TITLE,
        raw_content,
        source_type="file",
        filename="portfolio.md",
        mime_type="text/markdown",
    )
    print(f"✓ {len(doc.chunks)} chunk gömüldü → {DOC_TITLE}")
    print()
    print(f"🎉 Tamamlandı. {len(sections)} portfolyo kaydı bilgi bankasında.")
    client.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--manual",
        action="store_true",
        help="Instagram fetch'i atla, sadece manuel JSON kullan",
    )
    args = parser.parse_args()
    asyncio.run(main(manual_only=args.manual))
