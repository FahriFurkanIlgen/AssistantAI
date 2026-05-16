# AssistantAI — Copilot Instructions

## Tasarım Sistemi (Relate)

Tüm yeni veya değiştirilen frontend ekranları **`DESIGN.md`** içindeki
"Relate" tasarım sistemine uymalıdır. Tam token referansı: [DESIGN.md](../DESIGN.md).

### Zorunlu kurallar

- **Font:** Sadece `Inter` (sans + display). Mono sayılar için `Roboto Mono`
  (`.num-mono` sınıfı). SF Pro veya Helvetica kullanma.
- **Başlık tracking:** `-0.022em` (heading), display boyutlarda `-0.027em`
  ila `-0.04em`. Heading max font-weight = `600`. Asla 700/800 kullanma.
- **Zemin:** Sayfa arka planı `bg-relate-canvas` (`#fcfcfc`). Saf beyaz
  (`#ffffff`) sadece kart yüzeyi olarak. Saf siyah/beyaz metin kullanma —
  `text-relate-graphite` / `text-relate-ink`.
- **Renk paleti:** Sadece `relate.*` token'larını kullan
  (`canvas, wash, card, ink, graphite, slate, ash, fog, steel, border,
  rule, signal, glow, fade, action, emerald, coral, azure, amber`).
  Eski `apple.*` isimleri Relate'e alias'lı; **yeni kodda kullanma**.
- **Accent mavi (`#145aff` / `relate-signal`):** Sadece metin, kenarlık,
  focus ring olarak. **Asla** dolgu buton arkaplanı yapma.
- **Butonlar:**
  - Tek birincil dolgu CTA → `.btn-primary` (mavi gradient). Sayfa başına
    en fazla bir tane vurgulu konum.
  - İkincil aksiyon → `.btn-outline` / `.btn-secondary` (outlined `#0f1f3d`).
  - Bağlantı/ghost → `.btn-ghost`.
- **Kartlar:**
  - Kompakt UI kartı → `.card` (radius **8px**, `shadow-relate-sm`).
  - Tinted bölüm kartı → `.card-gray` (wash zemin).
  - Büyük marketing/feature kartı → `.card-feature` (radius **40px**,
    `shadow-relate-feature`).
  - **Kart radius'unda 8 ile 40 arası değer kullanma** (16/20/24px kart
    radius'u yasak — sistem ritmini bozar). Resim için 16px, input/buton
    için 12px (`rounded-xl`) tamamdır.
- **Input:** `.input-field` — beyaz, `#cfcfcf` border, 12px radius, focus
  ring azure (`#0099ff`) 3px box-shadow.
- **Status badge:** `.badge` + `.badge-{emerald|coral|azure|amber}`
  (renk %10 opacity zemin + tam renk metin, 4px radius).
- **Gölge:** Yalnızca kart/elevated yüzeylerde. Nav ve sidebar
  öğelerinde shadow kullanma.
- **Spacing:** Kompakt UI'da 8–12px gap; marketing bölümleri arasında
  80px vertical (`py-20`/`py-24`).
- **Layout:** Marketing içerikleri için `max-w-relate` (1200px), dashboard
  için mevcut genişlikler.

### Hero / marketing pattern

Açık zeminde radial blue wash kullanılır:

```tsx
<section className="relative overflow-hidden">
  <div className="absolute inset-0 hero-wash pointer-events-none" aria-hidden />
  <div className="relative max-w-relate mx-auto px-6 lg:px-10 ...">
    {/* trust pill → display headline → subtext → btn-primary + btn-outline */}
  </div>
</section>
```

### Yapılmayacaklar

- Solid `#000000` veya `#ffffff` metin/zemin.
- Heading'lerde `font-bold` (700+).
- Mavi gradient'i ana CTA dışında dekoratif olarak kullanmak.
- Kartlarda `border` ile `shadow`'u birlikte vurgu olarak kullanmak —
  Relate kartı border'sız, hafif shadow'lu.
- Semantik renkleri (emerald/coral/amber) status badge dışında dekoratif
  amaçla kullanmak.
- Bölüm zeminlerine ekstra dekoratif gradient. Sadece hero'da wash var.

## Backend ve genel

- Python 3.11, FastAPI, SQLAlchemy 2.x. Mevcut router/service yapısını
  koru; iş mantığını `services/`, IO'yu `routers/` katmanında tut.
- Tüm yeni API endpoint'leri Türkçe domain'e uygun pydantic şemalar
  döndürür; `app/models/` modellerini doğrudan response olarak verme.

## Workflow

- Yeni sayfa eklerken önce `globals.css` / `tailwind.config.js` içinde
  hazır olan sınıfları kullan; tasarım sistemine yeni token eklenmesi
  gerekiyorsa önce config'i güncelle, sonra kullan.
- Tasarım kuralı bilinçli olarak ihlal ediliyorsa PR/commit
  mesajında gerekçesini belirt.
