"""
Blossom-ic — Knowledge base ingest seed.

`backend/scripts/data/blossom_ic/*.md` altındaki tüm markdown
belgelerini OpenAI embeddings ile chunk'layıp Mongo
`knowledge_documents` koleksiyonuna yükler.

Idempotent: önce bu işletmeye ait, başlığı "[SEED] " ile başlayan
tüm dokümanları siler, sonra yenilerini ekler.

Kullanım (backend/ klasöründen):
    .\\venv\\Scripts\\python.exe -m scripts.ingest_blossom_ic

Önkoşullar:
    - Önce `scripts.seed_blossom_ic` çalıştırılmış olmalı
      (Business kaydı slug="blossom-ic" ile mevcut olmalı).
    - `.env` içinde `OPENAI_API_KEY` ve `MONGODB_URL` ayarlı olmalı.
"""

from __future__ import annotations

import asyncio
from pathlib import Path

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


BUSINESS_SLUG = "blossom-ic"
DATA_DIR = Path(__file__).parent / "data" / "blossom_ic"
TITLE_PREFIX = "[SEED] "

# (markdown dosya adı, görünen başlık)
DOCS: list[tuple[str, str]] = [
    (
        "01-genel-tanitim-ve-sistem.md",
        "Blossom-ic Genel Tanıtım, DHB Sistemi ve Ürün Ailesi",
    ),
    (
        "02-fan-coil-kontrol.md",
        "Hera Fan Coil Kontrol — Termostat, Kontrol Box, Actor ve BMS",
    ),
    (
        "03-bagimsiz-sertifikalar.md",
        "Bağımsız Sertifikalar — ITG Dresden, TÜV Rheinland, HLK Stuttgart",
    ),
]


async def main() -> None:
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
            f"Önce `python -m scripts.seed_blossom_ic` çalıştırın."
        )

    business_id = str(biz.id)
    print(f"✓ Business: {biz.name} (id={business_id})")

    # ── Idempotent temizlik: önceki SEED dokümanlarını sil ─────────────
    existing = await KnowledgeDocument.find(
        KnowledgeDocument.business_id == business_id
    ).to_list()
    seed_docs = [d for d in existing if (d.title or "").startswith(TITLE_PREFIX)]
    if seed_docs:
        print(f"↺ {len(seed_docs)} eski SEED dokümanı siliniyor…")
        for d in seed_docs:
            await d.delete()

    # ── Markdown dosyalarını oku ve ingest et ──────────────────────────
    total_chunks = 0
    for filename, title in DOCS:
        path = DATA_DIR / filename
        if not path.exists():
            print(f"⚠ Atlandı (dosya yok): {path}")
            continue

        raw = path.read_text(encoding="utf-8").strip()
        if not raw:
            print(f"⚠ Atlandı (boş): {filename}")
            continue

        display_title = f"{TITLE_PREFIX}{title}"
        print(f"→ Ingest: {filename}  ({len(raw):,} char)")
        doc = await ingest_document(
            business_id,
            display_title,
            raw,
            source_type="file",
            filename=filename,
            mime_type="text/markdown",
        )
        n = len(doc.chunks)
        total_chunks += n
        print(f"   ✓ {n} chunk gömüldü → {display_title}")

    print()
    print(f"🎉 Tamamlandı. {len(DOCS)} doküman, toplam {total_chunks} chunk.")


if __name__ == "__main__":
    asyncio.run(main())
