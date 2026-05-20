"""
Set business.logo_url from a local image file.

Kullanım (backend/ klasöründen):
    .\\venv\\Scripts\\python.exe -m scripts.set_business_logo blossom-ic scripts/data/blossom_ic/logo.png

Görseli base64 data URL'ye çevirir ve ilgili Business kaydının
`logo_url` alanına yazar. Chat ekranındaki avatar dairesinde anında
görünür (frontend `getWelcome` çağrısı `logo_url` döndürmeye başlamıştır).

Önerilen format: kare PNG / WebP, max ~300 KB.
"""

from __future__ import annotations

import asyncio
import base64
import mimetypes
import sys
from pathlib import Path

from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie

from app.config import settings
from app.models.business import Business


MAX_BYTES = 600_000  # 600 KB — frontend ile aynı limit


def to_data_url(image_path: Path) -> str:
    raw = image_path.read_bytes()
    if len(raw) > MAX_BYTES:
        raise SystemExit(
            f"❌ Görsel çok büyük: {len(raw):,} byte (max {MAX_BYTES:,}). "
            "Sıkıştırın veya yeniden ölçeklendirin."
        )
    mime, _ = mimetypes.guess_type(image_path.name)
    if not mime or not mime.startswith("image/"):
        # PNG varsay
        mime = "image/png"
    b64 = base64.b64encode(raw).decode("ascii")
    return f"data:{mime};base64,{b64}"


async def main(slug: str, image_path: Path) -> None:
    if not image_path.exists():
        raise SystemExit(f"❌ Görsel bulunamadı: {image_path}")

    data_url = to_data_url(image_path)
    print(f"✓ Data URL oluşturuldu ({len(data_url):,} char, {image_path.suffix})")

    client = AsyncIOMotorClient(settings.MONGODB_URL)
    await init_beanie(
        database=client[settings.MONGODB_DB_NAME],
        document_models=[Business],
    )

    biz = await Business.find_one(Business.slug == slug)
    if not biz:
        raise SystemExit(f"❌ Business bulunamadı (slug={slug}).")

    biz.logo_url = data_url
    await biz.save()
    print(f"🎉 Logo güncellendi → {biz.name} (slug={slug})")
    print(f"   Chat: http://localhost:3000/chat/{slug}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Kullanım: python -m scripts.set_business_logo <slug> <image_path>")
        sys.exit(1)
    asyncio.run(main(sys.argv[1], Path(sys.argv[2])))
