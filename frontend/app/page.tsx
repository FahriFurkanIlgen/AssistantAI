"use client";
import Link from "next/link";
import { MouseEvent, ReactNode } from "react";
import { LogoLockup, LogoMark } from "@/components/brand/Logo";

/* ─── Spotlight wrapper ───────────────────────────────── */
function Spotlight({
  children,
  className = "",
}: {
  children: ReactNode;
  className?: string;
}) {
  const onMove = (e: MouseEvent<HTMLDivElement>) => {
    const r = e.currentTarget.getBoundingClientRect();
    e.currentTarget.style.setProperty("--mouse-x", `${e.clientX - r.left}px`);
    e.currentTarget.style.setProperty("--mouse-y", `${e.clientY - r.top}px`);
  };
  return (
    <div className={`cyber-spotlight ${className}`} onMouseMove={onMove}>
      {children}
    </div>
  );
}

/* ─── Lightweight inline icons (Lucide-style) ─────────── */
const Ico = {
  brain: (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" className="w-5 h-5">
      <path d="M12 5a3 3 0 1 0-5.997.125 4 4 0 0 0-2.526 5.77 4 4 0 0 0 .556 6.588A4 4 0 1 0 12 18Z" />
      <path d="M12 5a3 3 0 1 1 5.997.125 4 4 0 0 1 2.526 5.77 4 4 0 0 1-.556 6.588A4 4 0 1 1 12 18Z" />
    </svg>
  ),
  sparkle: (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" className="w-5 h-5">
      <path d="M9.94 4.66a.5.5 0 0 1 .94 0l1.07 2.86a3 3 0 0 0 1.76 1.76l2.86 1.07a.5.5 0 0 1 0 .94l-2.86 1.07a3 3 0 0 0-1.76 1.76l-1.07 2.86a.5.5 0 0 1-.94 0l-1.07-2.86a3 3 0 0 0-1.76-1.76L4.25 11.29a.5.5 0 0 1 0-.94l2.86-1.07a3 3 0 0 0 1.76-1.76Z" />
      <path d="M18 4v3M19.5 5.5h-3M18 17v3M19.5 18.5h-3" />
    </svg>
  ),
  calendar: (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" className="w-5 h-5">
      <rect x="3" y="4.5" width="18" height="16" rx="2" />
      <path d="M16 3v3M8 3v3M3 10h18" />
    </svg>
  ),
  chart: (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" className="w-5 h-5">
      <path d="M3 3v18h18" />
      <path d="M7 15l4-4 3 3 5-6" />
    </svg>
  ),
  shield: (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" className="w-5 h-5">
      <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10Z" />
    </svg>
  ),
  zap: (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" className="w-5 h-5">
      <path d="M13 2L4 14h7l-1 8 9-12h-7l1-8Z" />
    </svg>
  ),
  globe: (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" className="w-5 h-5">
      <circle cx="12" cy="12" r="9" />
      <path d="M3 12h18M12 3a14 14 0 0 1 0 18M12 3a14 14 0 0 0 0 18" />
    </svg>
  ),
  arrow: (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" className="w-4 h-4">
      <path d="M5 12h14M13 5l7 7-7 7" />
    </svg>
  ),
};

/* ──────────────────────────────────────────────────────── */
export default function HomePage() {
  return (
    <main className="dark-cyber min-h-screen relative overflow-x-hidden">
      {/* faint background grid */}
      <div className="absolute inset-0 cyber-grid-bg opacity-40 pointer-events-none" aria-hidden />
      {/* hero radial emerald wash */}
      <div className="absolute top-0 inset-x-0 h-[900px] bg-cyber-emerald-glow pointer-events-none" aria-hidden />

      {/* ── NAV ─────────────────────────────────────────── */}
      <nav className="cyber-nav fixed top-0 inset-x-0 z-40">
        <div className="max-w-relate mx-auto h-full px-6 lg:px-10 flex items-center justify-between">
          <LogoLockup href="/" size={36} />
          <div className="hidden md:flex items-center gap-8">
            {[
              { label: "Platform", id: "platform" },
              { label: "Mantık", id: "logic" },
              { label: "Fiyatlandırma", id: "pricing" },
              { label: "Dokümanlar", id: "docs" },
            ].map((l) => (
              <a
                key={l.id}
                href={`#${l.id}`}
                className="font-grotesk text-[12px] uppercase tracking-[0.2em] text-cyber-ink/60 hover:text-cyber-emerald transition-colors duration-500 ease-cyber"
              >
                {l.label}
              </a>
            ))}
          </div>
          <div className="flex items-center gap-3">
            <Link
              href="/login"
              className="hidden sm:inline-flex font-grotesk text-[11px] uppercase tracking-[0.2em] text-cyber-ink/60 hover:text-cyber-ink transition-colors duration-500 ease-cyber"
            >
              Giriş yap
            </Link>
            <Link href="/register" className="cyber-btn-outline h-10 px-5 text-[12px]">
              Demo iste
              <span className="text-cyber-emerald">{Ico.arrow}</span>
            </Link>
          </div>
        </div>
      </nav>

      {/* ── HERO ────────────────────────────────────────── */}
      <section className="relative pt-[160px] pb-32">
        <div className="max-w-relate mx-auto px-6 lg:px-10 grid lg:grid-cols-12 gap-12 items-center">
          {/* Left */}
          <div className="lg:col-span-7">
            <span className="cyber-badge mb-8">GPT-4o · Canlı ajan</span>
            <h1 className="font-serif font-light text-cyber-ink text-[56px] sm:text-[72px] lg:text-[88px] leading-[0.98] tracking-[-0.02em]">
              Akıllı
              <br />
              <span className="italic bg-gradient-to-br from-cyber-emerald via-cyber-emerald/80 to-cyber-ink bg-clip-text text-transparent">
                randevu
              </span>{" "}
              <span className="italic text-cyber-ink/85">katmanı.</span>
            </h1>
            <p className="mt-8 max-w-[520px] text-[16px] leading-[1.7] text-cyber-ink/60 font-light">
              Niyeti anlayan, müsaitliği yöneten ve siz uyurken bile randevu
              alan bir yapay zekâ resepsiyonist. Zamanı envanter gibi yöneten
              stüdyolar, klinikler ve işletmeler için tasarlandı.
            </p>
            <div className="mt-10 flex flex-wrap items-center gap-4">
              <Link href="/register" className="cyber-btn-primary">
                Ücretsiz başla
                {Ico.arrow}
              </Link>
              <Link href="/login" className="cyber-btn-outline">
                Demoyu izle
              </Link>
            </div>

            {/* tiny metrics strip */}
            <div className="mt-14 grid grid-cols-3 gap-8 max-w-[480px]">
              {[
                { k: "Aylık randevu", v: "284K+" },
                { k: "Ort. yanıt", v: "1.2s" },
                { k: "Doğruluk", v: "%98.4" },
              ].map((m) => (
                <div key={m.k}>
                  <p className="cyber-num text-[26px]">{m.v}</p>
                  <p className="cyber-label mt-1 text-[10px]">{m.k}</p>
                </div>
              ))}
            </div>
          </div>

          {/* Right — floating tilted AI card */}
          <div className="lg:col-span-5 relative">
            <div
              className="cyber-glass p-6 transition-transform duration-700 ease-cyber hover:rotate-0"
              style={{ transform: "rotate(2deg)" }}
            >
              {/* header */}
              <div className="flex items-center justify-between pb-4 border-b border-cyber-rule">
                <div className="flex items-center gap-3">
                  <span className="relative flex w-2.5 h-2.5">
                    <span className="absolute inset-0 rounded-full bg-cyber-emerald animate-ping opacity-60" />
                    <span className="relative w-2.5 h-2.5 rounded-full bg-cyber-emerald" />
                  </span>
                  <span className="cyber-label text-[10px]">Oturum · 04:21</span>
                </div>
                <span className="cyber-label text-cyber-emerald text-[10px]">Aktıf</span>
              </div>

              {/* chat lines */}
              <div className="py-5 space-y-4">
                <div className="text-[13px] text-cyber-ink/70 font-light leading-relaxed">
                  <span className="cyber-label text-cyber-emerald mr-2 text-[10px]">Müşteri</span>
                  Kol dövmesi yaptırmak istiyorum, yaklaşık 6 saat. Perşembe uygun saat var mı?
                </div>
                <div className="text-[13px] text-cyber-ink/90 font-light leading-relaxed border-l border-cyber-emerald/50 pl-3">
                  <span className="cyber-label text-cyber-emerald mr-2 text-[10px]">Ajan</span>
                  Evet — Perşembe 14:00 Marco ile, ya da 11:00 Luna ile. İkisi de 6 saatlik seans ve referans stilinize uygun.
                </div>
                <div className="flex items-center gap-3 pt-1">
                  <span className="cyber-label text-cyber-emerald text-[10px]">Düşünüyor</span>
                  <span className="cyber-typing">
                    <span /><span /><span />
                  </span>
                </div>
              </div>

              {/* candidate avatars */}
              <div className="flex items-center gap-2 pt-3 border-t border-cyber-rule">
                {["MR", "LU", "AK", "DN"].map((n, i) => (
                  <div
                    key={n}
                    className="w-9 h-9 rounded-full border border-cyber-rule bg-cyber-glass flex items-center justify-center font-grotesk text-[10px] tracking-[0.15em] text-cyber-ink/60"
                    style={{ filter: "grayscale(1)" }}
                  >
                    {n}
                  </div>
                ))}
                <span className="cyber-label ml-auto text-[10px]">+12 personel</span>
              </div>

              {/* scoring dashboard */}
              <div className="mt-5 grid grid-cols-3 gap-3 pt-5 border-t border-cyber-rule">
                {[
                  { k: "Niyet", v: "0.97" },
                  { k: "Eşleşme", v: "0.91" },
                  { k: "Risk", v: "0.04" },
                ].map((s) => (
                  <div key={s.k}>
                    <p className="cyber-label text-[9px]">{s.k}</p>
                    <p className="cyber-num text-[20px] mt-1 text-cyber-emerald">
                      {s.v}
                    </p>
                  </div>
                ))}
              </div>
            </div>

            {/* floating tag behind */}
            <div className="absolute -top-4 -left-6 cyber-glass px-3 py-2 hidden lg:flex items-center gap-2" style={{ borderRadius: 12 }}>
              <span className="text-cyber-emerald">{Ico.zap}</span>
              <span className="cyber-label text-[10px]">240ms'de yönlendirildi</span>
            </div>
          </div>
        </div>
      </section>

      {/* ── FEATURE BENTO ───────────────────────────────── */}
      <section id="platform" className="relative py-32 border-t border-cyber-ruleSoft">
        <div className="max-w-relate mx-auto px-6 lg:px-10">
          <div className="max-w-[640px] mb-16">
            <span className="cyber-badge mb-6">Platform</span>
            <h2 className="font-serif font-light text-[44px] lg:text-[56px] leading-[1.05] tracking-[-0.015em] text-cyber-ink">
              Her konuşma için{" "}
              <span className="italic text-cyber-emerald">muhakeme motoru.</span>
            </h2>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
            {/* wide card with bar chart */}
            <Spotlight className="md:col-span-2 min-h-[300px]">
              <div className="text-cyber-emerald mb-6">{Ico.chart}</div>
              <h3 className="font-serif font-light text-[24px] text-cyber-ink leading-snug mb-3">
                Talep gelmeden öngörün.
              </h3>
              <p className="text-[14px] font-light text-cyber-ink/50 leading-relaxed max-w-[460px]">
                Arama, mesaj ve niyet verilerinden gelen canlı sinyal; personeli
                ve uygun saatleri gerçek zamanlı yeniden dengeleyen tahmin
                modelini besler.
              </p>
              {/* micro bar chart */}
              <div className="mt-8 flex items-end gap-1.5 h-24">
                {[28, 42, 35, 58, 71, 49, 64, 82, 76, 90, 68, 54].map((h, i) => (
                  <div
                    key={i}
                    className={`flex-1 rounded-sm transition-all duration-700 ease-cyber ${i % 3 === 0 ? "bg-cyber-emerald" : "bg-cyber-ink/30"}`}
                    style={{ height: `${h}%` }}
                  />
                ))}
              </div>
            </Spotlight>

            <Spotlight>
              <div className="text-cyber-emerald mb-6">{Ico.brain}</div>
              <h3 className="font-serif font-light text-[22px] text-cyber-ink leading-snug mb-3">
                Çok dilli muhakeme.
              </h3>
              <p className="text-[14px] font-light text-cyber-ink/50 leading-relaxed">
                Yerel Türkçe ve İngilizce. Konuşma ortasında dili
                değiştirir; bağlam ve tonu kaybetmez.
              </p>
            </Spotlight>

            <Spotlight>
              <div className="text-cyber-emerald mb-6">{Ico.calendar}</div>
              <h3 className="font-serif font-light text-[22px] text-cyber-ink leading-snug mb-3">
                Takvim altyapısı.
              </h3>
              <p className="text-[14px] font-light text-cyber-ink/50 leading-relaxed">
                Google Takvim ile çift yönlü senkron; çakışma çözümü ve
                süre öngörüleri kutudan çıkar çıkmaz hazır.
              </p>
            </Spotlight>

            <Spotlight>
              <div className="text-cyber-emerald mb-6">{Ico.shield}</div>
              <h3 className="font-serif font-light text-[22px] text-cyber-ink leading-snug mb-3">
                Tasarım gereği uyumlu.
              </h3>
              <p className="text-[14px] font-light text-cyber-ink/50 leading-relaxed">
                AB'de tutulan veriler, denetim seviyesinde kayıtlar, müşteri
                onayı ve silme tek tıkla.
              </p>
            </Spotlight>

            <Spotlight>
              <div className="text-cyber-emerald mb-6">{Ico.globe}</div>
              <h3 className="font-serif font-light text-[22px] text-cyber-ink leading-snug mb-3">
                Kanaldan bağımsız.
              </h3>
              <p className="text-[14px] font-light text-cyber-ink/50 leading-relaxed">
                Web widget, WhatsApp, Instagram DM. Tek beyin, her yüzey.
              </p>
            </Spotlight>
          </div>
        </div>
      </section>

      {/* ── LOGIC / CHAT INTERFACE ──────────────────────── */}
      <section id="logic" className="relative py-32 border-t border-cyber-ruleSoft">
        <div className="max-w-relate mx-auto px-6 lg:px-10 grid lg:grid-cols-2 gap-16 items-center">
          {/* Left — terminal */}
          <Spotlight className="!p-0 overflow-hidden">
            <div className="flex items-center justify-between px-5 py-3 border-b border-cyber-rule">
              <div className="flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-cyber-ink/20" />
                <span className="w-2 h-2 rounded-full bg-cyber-ink/20" />
                <span className="w-2 h-2 rounded-full bg-cyber-emerald" />
              </div>
              <span className="cyber-label text-[10px]">terminal · ajan.v2</span>
              <div className="flex items-center gap-2">
                <span className="w-1.5 h-1.5 rounded-full bg-cyber-coral animate-pulse" style={{ background: "#ef4444" }} />
                <span className="cyber-label text-[9px] text-cyber-ink/50">KAYIT</span>
              </div>
            </div>
            <div className="p-6 space-y-5 min-h-[360px]">
              {[
                { role: "MÜŞTERİ", text: "Mehmet — perşembe 14:00 boş mu?", emerald: false },
                { role: "AJAN", text: "Marco'nun kolonu 14:00–20:00 açık. 30 dk tamponla rezerve ediliyor.", emerald: true },
                { role: "MÜŞTERİ", text: "Onaylıyorum. Bana hatırlatma kur.", emerald: false },
                { role: "AJAN", text: "Tamam. 24 saat öncesinde WhatsApp hatırlatması ayarlandı.", emerald: true },
              ].map((m, i) => (
                <div
                  key={i}
                  className={`text-[13px] font-light leading-relaxed pl-3 ${m.emerald ? "border-l border-cyber-emerald/50 text-cyber-ink/90" : "border-l border-cyber-rule text-cyber-ink/65"}`}
                >
                  <span className={`cyber-label mr-3 text-[9px] ${m.emerald ? "text-cyber-emerald" : "text-cyber-ink/50"}`}>
                    {m.role}
                  </span>
                  {m.text}
                </div>
              ))}
              <div className="flex items-center gap-3 pt-1 pl-3">
                <span className="cyber-label text-cyber-emerald text-[10px]">Yazıyor</span>
                <span className="cyber-typing"><span /><span /><span /></span>
              </div>
            </div>
          </Spotlight>

          {/* Right — feature list */}
          <div>
            <span className="cyber-badge mb-6">Muhakeme</span>
            <h2 className="font-serif font-light text-[44px] lg:text-[56px] leading-[1.05] tracking-[-0.015em] text-cyber-ink mb-10">
              Cevap vermeden{" "}
              <span className="italic text-cyber-emerald">dinleyen</span> mantık.
            </h2>
            <ul className="divide-y divide-cyber-ruleSoft">
              {[
                {
                  t: "Niyet sınıflandırması",
                  d: "Randevu, erteleme, iptal, bilgi — hepsi tek geçişte yönlendirilir.",
                },
                {
                  t: "Kısıt çözücü",
                  d: "Süre, personel yetkinliği, oda müsaitliği ve yol süresini paralel çözer.",
                },
                {
                  t: "Ton adaptasyonu",
                  d: "Manuel komut olmadan markanızın sesini diller arası korur.",
                },
                {
                  t: "Hata bilinci",
                  d: "Güven düştüğünde tüm yazışmayla birlikte insana devreder.",
                },
              ].map((f) => (
                <li key={f.t} className="group flex items-start gap-5 py-5">
                  <span className="mt-0.5 w-10 h-10 rounded-full border border-cyber-rule bg-cyber-glass flex items-center justify-center text-cyber-ink/50 group-hover:text-cyber-emerald group-hover:border-cyber-emerald/40 transition-all duration-500 ease-cyber">
                    {Ico.sparkle}
                  </span>
                  <div>
                    <h4 className="font-serif font-light text-[20px] text-cyber-ink leading-snug">
                      {f.t}
                    </h4>
                    <p className="text-[13px] font-light text-cyber-ink/50 leading-relaxed mt-1">
                      {f.d}
                    </p>
                  </div>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </section>

      {/* ── ANALYTICS DASHBOARD ─────────────────────────── */}
      <section className="relative py-32 border-t border-cyber-ruleSoft">
        <div className="max-w-relate mx-auto px-6 lg:px-10">
          <div className="flex items-end justify-between mb-12">
            <div>
              <span className="cyber-badge mb-6">Konsol</span>
              <h2 className="font-serif font-light text-[44px] lg:text-[56px] leading-[1.05] tracking-[-0.015em] text-cyber-ink max-w-[640px]">
                Operasyon, bir{" "}
                <span className="italic text-cyber-emerald">sinyal akışı.</span>
              </h2>
            </div>
            <span className="cyber-label hidden md:inline text-[10px]">son 30 gün</span>
          </div>

          <div className="cyber-glass grid grid-cols-12 overflow-hidden">
            {/* sidebar */}
            <aside className="col-span-12 md:col-span-3 border-b md:border-b-0 md:border-r border-cyber-rule p-6 space-y-1">
              {["Genel bakış", "Randevular", "Görüşmeler", "Personel", "Gelir", "Denetim kaydı"].map((s, i) => (
                <div
                  key={s}
                  className={`flex items-center justify-between px-3 py-2 rounded-lg font-grotesk text-[11px] uppercase tracking-[0.2em] cursor-pointer transition-colors duration-500 ease-cyber ${i === 0 ? "bg-cyber-emerald/10 text-cyber-emerald" : "text-cyber-ink/55 hover:text-cyber-ink"}`}
                >
                  <span>{s}</span>
                  {i === 0 && <span className="w-1.5 h-1.5 rounded-full bg-cyber-emerald" />}
                </div>
              ))}
            </aside>

            {/* main */}
            <div className="col-span-12 md:col-span-9 p-8">
              {/* stats grid */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-px bg-cyber-rule mb-8">
                {[
                  { k: "Ort. Skor",      v: "0.94" },
                  { k: "Zaman Tasarrufu", v: "1.284s" },
                  { k: "Dönüşüm",        v: "%37.2" },
                  { k: "Bekleyen",        v: "0" },
                ].map((m) => (
                  <div key={m.k} className="bg-cyber-bg p-5">
                    <p className="cyber-label text-[10px]">{m.k}</p>
                    <p className="cyber-num text-[28px] mt-2">{m.v}</p>
                  </div>
                ))}
              </div>

              {/* table */}
              <div className="border border-cyber-rule rounded-2xl overflow-hidden">
                <div className="grid grid-cols-12 px-5 py-3 border-b border-cyber-rule">
                  {["Müşteri", "Hizmet", "Yönlendirme", "Skor"].map((h, i) => (
                    <div
                      key={h}
                      className={`cyber-label text-[10px] ${i === 0 ? "col-span-4" : i === 1 ? "col-span-4" : i === 2 ? "col-span-2" : "col-span-2 text-right"}`}
                    >
                      {h}
                    </div>
                  ))}
                </div>
                {[
                  { c: "Ayşe Kaya",    s: "Saç Boyama",         t: "Marco",  v: 0.97 },
                  { c: "Mehmet Demir", s: "Dövme — Kol",         t: "Luna",   v: 0.91 },
                  { c: "Zeynep Aslan", s: "Konsültasyon",       t: "Otomatik", v: 0.84 },
                  { c: "Burak Yıldız", s: "Botoks",             t: "Otomatik", v: 0.78 },
                  { c: "Selin Acar",   s: "Lazer epilasyon",    t: "Daniel", v: 0.95 },
                ].map((r, i) => (
                  <div
                    key={i}
                    className="grid grid-cols-12 items-center px-5 py-4 border-b border-cyber-ruleSoft last:border-b-0 hover:bg-cyber-emerald/[0.03] transition-colors duration-500 ease-cyber"
                  >
                    <div className="col-span-4 flex items-center gap-3">
                      <span className="w-7 h-7 rounded-full border border-cyber-rule bg-cyber-glass flex items-center justify-center font-grotesk text-[9px] tracking-[0.1em] text-cyber-ink/60" style={{ filter: "grayscale(1)" }}>
                        {r.c.split(" ").map((p) => p[0]).join("")}
                      </span>
                      <span className="text-[13px] font-light text-cyber-ink/85">{r.c}</span>
                    </div>
                    <div className="col-span-4 text-[12px] font-light text-cyber-ink/55">{r.s}</div>
                    <div className="col-span-2">
                      <span className="cyber-label text-[9px] text-cyber-ink/50">{r.t}</span>
                    </div>
                    <div className="col-span-2 flex items-center justify-end gap-3">
                      <div className="w-16 h-1 rounded-full bg-cyber-rule overflow-hidden hidden sm:block">
                        <div
                          className="h-full bg-cyber-emerald rounded-full transition-all duration-700 ease-cyber"
                          style={{ width: `${r.v * 100}%` }}
                        />
                      </div>
                      <span className="cyber-num text-[12px] text-cyber-emerald w-10 text-right">
                        {r.v.toFixed(2)}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ── CTA ─────────────────────────────────────────── */}
      <section className="relative py-40 border-t border-cyber-ruleSoft overflow-hidden">
        <div className="absolute inset-0 bg-cyber-emerald-glow pointer-events-none" aria-hidden />
        <div className="relative max-w-[820px] mx-auto px-6 text-center">
          <span className="cyber-badge mb-8">v2 · Şimdi yayında</span>
          <h2 className="font-serif font-light text-[56px] lg:text-[72px] leading-[1.02] tracking-[-0.018em] text-cyber-ink">
            Bir saatten az sürede{" "}
            <span className="italic text-cyber-emerald">daha akıllı</span>
            <br />
            randevu almaya başlayın.
          </h2>
          <p className="mt-6 text-[16px] font-light text-cyber-ink/60 max-w-[480px] mx-auto">
            Kart gerekmiyor. Takviminizi bağlayın, asistanınız canlı olsun.
          </p>
          <div className="mt-10 flex flex-wrap items-center justify-center gap-4">
            <Link href="/register" className="cyber-btn-primary">
              Ücretsiz başla {Ico.arrow}
            </Link>
            <Link href="/login" className="cyber-btn-outline">
              Satışla görüş
            </Link>
          </div>
        </div>
      </section>

      {/* ── FOOTER ──────────────────────────────────────── */}
      <footer className="relative border-t border-cyber-ruleSoft">
        <div className="max-w-relate mx-auto px-6 lg:px-10 py-10 flex flex-col sm:flex-row items-center justify-between gap-5">
          <div className="flex items-center gap-3">
            <LogoMark className="w-7 h-7" />
            <span className="font-serif text-[14px] text-cyber-ink/70">
              assistant<span className="text-cyber-emerald">AI</span> · © 2026
            </span>
          </div>
          <div className="flex items-center gap-6">
            {["Gizlilik", "Şartlar", "Durum", "İletişim"].map((l) => (
              <a key={l} href="#" className="cyber-label text-[10px] hover:text-cyber-emerald transition-colors duration-500 ease-cyber">
                {l}
              </a>
            ))}
          </div>
        </div>
      </footer>
    </main>
  );
}

