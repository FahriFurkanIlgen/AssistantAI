import Link from "next/link";

const SECTORS = [
  { icon: "🎨", label: "Dövme Stüdyoları" },
  { icon: "🏥", label: "Klinikler" },
  { icon: "💅", label: "Güzellik Merkezleri" },
  { icon: "✂️", label: "Kuaförler" },
];

const FEATURES = [
  {
    tag: "AI",
    title: "GPT-4o Asistan",
    desc: "Müşterileri anlayan, Türkçe ve İngilizce konuşabilen zeki chatbot. Görsel analiz ve stil önerisi.",
  },
  {
    tag: "SYNC",
    title: "Google Takvim",
    desc: "Randevular otomatik takvime eklenir. Müsaitlik kontrolü ve çakışma önleme otomatik.",
  },
  {
    tag: "OPS",
    title: "Dashboard",
    desc: "Tüm randevularınızı, müşterilerinizi ve istatistiklerinizi tek ekrandan yönetin.",
  },
];

export default function HomePage() {
  return (
    <main className="min-h-screen bg-relate-canvas text-relate-graphite">
      {/* ── Nav ────────────────────────────────────────── */}
      <nav className="sticky top-0 z-30 backdrop-blur-md bg-relate-canvas/80 border-b border-relate-border/60">
        <div className="max-w-relate mx-auto flex items-center justify-between px-6 lg:px-10 h-[68px]">
          <Link href="/" className="font-semibold text-[17px] tracking-[-0.022em] text-relate-ink">
            AssistantAI
          </Link>
          <div className="hidden sm:flex items-center gap-1 text-[14px] text-relate-slate">
            <a href="#features" className="px-3 py-2 hover:text-relate-graphite transition-colors">
              Özellikler
            </a>
            <a href="#sectors" className="px-3 py-2 hover:text-relate-graphite transition-colors">
              Sektörler
            </a>
            <Link href="/login" className="px-3 py-2 hover:text-relate-graphite transition-colors">
              Giriş
            </Link>
          </div>
          <div className="flex items-center gap-3">
            <Link href="/login" className="btn-outline hidden sm:inline-flex">
              Demo iste
            </Link>
            <Link href="/register" className="btn-primary">
              Ücretsiz başla
            </Link>
          </div>
        </div>
      </nav>

      {/* ── Hero ───────────────────────────────────────── */}
      <section className="relative overflow-hidden">
        <div className="absolute inset-0 hero-wash pointer-events-none" aria-hidden />
        <div className="relative max-w-relate mx-auto px-6 lg:px-10 pt-24 pb-24 lg:pt-32 text-center">
          <div className="inline-flex items-center gap-2 mb-7">
            <span className="inline-flex items-center justify-center w-5 h-5 rounded-[4px] bg-relate-amber/15 text-relate-amber text-[11px] font-bold">
              ✦
            </span>
            <span className="text-[12px] font-medium text-relate-slate tracking-[0.06px]">
              GPT-4o destekli yapay zeka
            </span>
          </div>

          <h1 className="display font-semibold text-relate-ink text-[44px] sm:text-[64px] lg:text-[80px] leading-[1.02] tracking-[-0.04em] mb-6">
            Müşterileriniz 7/24
            <br />
            <span className="text-relate-signal">randevu</span> alabilsin.
          </h1>

          <p className="text-[17px] sm:text-[19px] leading-[1.5] text-relate-ash max-w-[560px] mx-auto mb-10">
            GPT-4o destekli zeki asistan, Google Takvim entegrasyonu ve
            otomatik randevu yönetimi tek bir sade platformda.
          </p>

          <div className="flex flex-col sm:flex-row items-center justify-center gap-3">
            <Link href="/register" className="btn-primary px-7 py-3.5 text-[15px]">
              Hemen başla — ücretsiz
            </Link>
            <Link href="/login" className="btn-outline px-6 py-3 text-[14px]">
              Demo izle
            </Link>
          </div>

          {/* Product preview */}
          <div className="mt-20">
            <div className="card-feature mx-auto max-w-[920px] text-left">
              <div className="rounded-2xl overflow-hidden bg-relate-wash border border-relate-border">
                <div className="flex items-center justify-between px-5 py-3 border-b border-relate-border/80 bg-white">
                  <div className="flex items-center gap-2">
                    <span className="w-2.5 h-2.5 rounded-full bg-relate-coral/60" />
                    <span className="w-2.5 h-2.5 rounded-full bg-relate-amber/60" />
                    <span className="w-2.5 h-2.5 rounded-full bg-relate-emerald/60" />
                  </div>
                  <span className="text-[11px] text-relate-fog font-mono">
                    assistant-ai.app/dashboard
                  </span>
                  <span className="badge badge-azure">Live</span>
                </div>
                <div className="grid grid-cols-3 gap-3 p-5">
                  {[
                    { k: "Bugün", v: "12", n: "randevu" },
                    { k: "Bu ay", v: "284", n: "▲ 18%" },
                    { k: "Yaklaşan", v: "47", n: "7 gün" },
                  ].map((c) => (
                    <div key={c.k} className="card">
                      <p className="text-[10px] uppercase text-relate-fog tracking-[0.13px]">
                        {c.k}
                      </p>
                      <p className="num-mono text-[28px] text-relate-graphite mt-1">
                        {c.v}
                      </p>
                      <p className="text-[11px] text-relate-ash mt-0.5">{c.n}</p>
                    </div>
                  ))}
                </div>
                <div className="px-5 pb-5 space-y-1.5">
                  {[
                    { n: "Ayşe K.", s: "Saç Boyama", t: "14:30", b: "emerald", st: "Onaylı" },
                    { n: "Mehmet D.", s: "Dövme — Sleeve", t: "16:00", b: "azure", st: "Yeni" },
                    { n: "Zeynep A.", s: "Konsültasyon", t: "17:15", b: "amber", st: "Bekliyor" },
                  ].map((r) => (
                    <div key={r.n} className="card flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <div className="w-7 h-7 rounded-full bg-relate-wash flex items-center justify-center text-[11px] font-semibold text-relate-slate">
                          {r.n.split(" ").map((p) => p[0]).join("")}
                        </div>
                        <div>
                          <p className="text-[14px] font-medium text-relate-graphite">{r.n}</p>
                          <p className="text-[12px] text-relate-steel">{r.s}</p>
                        </div>
                      </div>
                      <div className="flex items-center gap-3">
                        <span className={`badge badge-${r.b}`}>{r.st}</span>
                        <span className="num-mono text-[12px] text-relate-slate">{r.t}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ── Sectors ────────────────────────────────────── */}
      <section id="sectors" className="bg-relate-wash py-20">
        <div className="max-w-relate mx-auto px-6 lg:px-10">
          <p className="text-center text-[12px] font-medium uppercase tracking-[0.13px] text-relate-ash mb-8">
            Her sektör için
          </p>
          <div className="flex flex-wrap justify-center gap-3">
            {SECTORS.map((s) => (
              <span
                key={s.label}
                className="inline-flex items-center gap-2 px-4 py-2 rounded-pill bg-white border border-relate-border text-[14px] text-relate-slate shadow-relate-sm"
              >
                <span>{s.icon}</span>
                {s.label}
              </span>
            ))}
          </div>
        </div>
      </section>

      {/* ── Features ───────────────────────────────────── */}
      <section id="features" className="py-24">
        <div className="max-w-relate mx-auto px-6 lg:px-10">
          <div className="text-center mb-16">
            <h2 className="text-[40px] lg:text-[48px] font-semibold tracking-[-0.022em] text-relate-graphite leading-[1.08]">
              Her şey dahil,
              <br className="hidden sm:block" /> sıfır kurulum.
            </h2>
            <p className="text-[16px] text-relate-ash mt-4 max-w-[520px] mx-auto">
              Bir saat içinde canlıya alın. Karmaşık entegrasyon yok,
              gizli ücret yok.
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            {FEATURES.map((f) => (
              <div key={f.title} className="card p-7">
                <span className="badge badge-azure">{f.tag}</span>
                <h3 className="text-[18px] font-semibold text-relate-graphite tracking-[-0.016em] mt-4 mb-2">
                  {f.title}
                </h3>
                <p className="text-[14px] leading-[1.5] text-relate-ash">{f.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── CTA ────────────────────────────────────────── */}
      <section className="py-24">
        <div className="max-w-relate mx-auto px-6 lg:px-10">
          <div className="card-feature text-center max-w-[820px] mx-auto">
            <h2 className="text-[36px] lg:text-[44px] font-semibold tracking-[-0.022em] text-relate-ink mb-4">
              Hemen başlayın.
            </h2>
            <p className="text-[16px] text-relate-ash mb-8">
              Kredi kartı gerekmez. 14 gün ücretsiz.
            </p>
            <div className="flex flex-col sm:flex-row gap-3 justify-center">
              <Link href="/register" className="btn-primary px-7 py-3.5">
                Ücretsiz hesap oluştur
              </Link>
              <Link href="/login" className="btn-outline">
                Giriş yap
              </Link>
            </div>
          </div>
        </div>
      </section>

      <footer className="border-t border-relate-border bg-relate-canvas">
        <div className="max-w-relate mx-auto px-6 lg:px-10 py-8 flex flex-col sm:flex-row items-center justify-between gap-3">
          <p className="text-[12px] text-relate-ash">
            © 2026 AssistantAI · Tüm hakları saklıdır.
          </p>
          <div className="flex items-center gap-4 text-[12px] text-relate-ash">
            <a href="#" className="hover:text-relate-graphite transition-colors">Gizlilik</a>
            <a href="#" className="hover:text-relate-graphite transition-colors">Şartlar</a>
            <a href="#" className="hover:text-relate-graphite transition-colors">İletişim</a>
          </div>
        </div>
      </footer>
    </main>
  );
}
