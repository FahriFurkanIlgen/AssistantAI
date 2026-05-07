import Link from "next/link";

export default function HomePage() {
  return (
    <main className="min-h-screen bg-apple-black text-white">
      {/* ── Nav ────────────────────────────────────────── */}
      <nav className="flex items-center justify-between px-8 py-4 max-w-[980px] mx-auto">
        <span className="font-display font-semibold text-[17px] tracking-tight">
          AssistantAI
        </span>
        <div className="flex items-center gap-6">
          <Link href="/login" className="text-sm text-apple-secondary hover:text-white transition-colors">
            Giriş Yap
          </Link>
          <Link href="/register" className="btn-primary text-sm px-4 py-2">
            Ücretsiz Başla
          </Link>
        </div>
      </nav>

      {/* ── Hero ───────────────────────────────────────── */}
      <section className="text-center px-6 pt-24 pb-32 max-w-[740px] mx-auto">
        <p className="text-apple-blue text-[17px] font-medium mb-4 tracking-tight">
          Yapay Zeka Destekli Randevu
        </p>
        <h1 className="font-display font-semibold text-[56px] leading-[1.07] tracking-[-0.028em] text-white mb-6">
          Müşterileriniz 7/24<br />randevu alabilsin.
        </h1>
        <p className="text-[19px] text-apple-secondary leading-[1.47] mb-10 max-w-[500px] mx-auto">
          GPT-4o destekli zeki asistan, Google Takvim entegrasyonu
          ve otomatik randevu yönetimi tek platformda.
        </p>
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Link href="/register" className="btn-primary text-base px-8 py-3">
            Ücretsiz Başla
          </Link>
          <Link
            href="/login"
            className="inline-flex items-center justify-center text-apple-blueDark hover:text-white text-base font-medium transition-colors gap-1"
          >
            Giriş Yap <span aria-hidden>›</span>
          </Link>
        </div>
      </section>

      {/* ── Sector chips ───────────────────────────────── */}
      <section className="flex flex-wrap justify-center gap-3 pb-24 px-6">
        {[
          { icon: "🎨", label: "Dövme Stüdyoları" },
          { icon: "🏥", label: "Klinikler" },
          { icon: "💅", label: "Güzellik Merkezleri" },
          { icon: "✂️", label: "Kuaförler" },
        ].map((s) => (
          <span
            key={s.label}
            className="flex items-center gap-2 px-4 py-2 rounded-pill bg-white/10 border border-white/10 text-sm text-white/80 backdrop-blur-sm"
          >
            <span>{s.icon}</span>
            {s.label}
          </span>
        ))}
      </section>

      {/* ── Feature band — pale gray ────────────────────── */}
      <section className="bg-apple-gray py-24 px-6">
        <div className="max-w-[980px] mx-auto">
          <p className="text-center text-apple-secondary text-[17px] mb-16 font-medium">
            Her şey dahil, sıfır kurulum.
          </p>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            {[
              {
                icon: "✦",
                title: "GPT-4o Asistan",
                desc: "Müşterileri anlayan, Türkçe ve İngilizce konuşabilen zeki chatbot. Görsel analiz ve stil önerisi.",
              },
              {
                icon: "⊕",
                title: "Google Takvim",
                desc: "Randevular otomatik takvime eklenir. Müsaitlik kontrolü ve çakışma önleme otomatik.",
              },
              {
                icon: "◈",
                title: "Dashboard",
                desc: "Tüm randevularınızı, müşterilerinizi ve istatistiklerinizi tek ekrandan yönetin.",
              },
            ].map((f) => (
              <div key={f.title} className="card-gray rounded-apple-lg p-8">
                <div className="text-apple-blue text-2xl font-light mb-5">{f.icon}</div>
                <h3 className="font-display font-semibold text-[19px] text-apple-ink mb-3 tracking-tight">
                  {f.title}
                </h3>
                <p className="text-[15px] text-apple-secondary leading-[1.5]">{f.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── CTA footer ─────────────────────────────────── */}
      <section className="bg-apple-black py-24 text-center px-6">
        <h2 className="font-display font-semibold text-[40px] text-white tracking-tight mb-4">
          Hemen başlayın.
        </h2>
        <p className="text-apple-secondary text-[17px] mb-8">
          Kredi kartı gerekmez.
        </p>
        <Link href="/register" className="btn-primary text-base px-8 py-3">
          Ücretsiz Hesap Oluştur
        </Link>
      </section>

      <footer className="bg-apple-gray border-t border-apple-border py-8 px-6">
        <p className="text-center text-apple-secondary text-[12px]">
          © 2026 AssistantAI · Tüm hakları saklıdır.
        </p>
      </footer>
    </main>
  );
}
