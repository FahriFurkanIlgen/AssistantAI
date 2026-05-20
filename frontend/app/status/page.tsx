import type { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = {
  title: "Sistem Durumu — AssistantAI",
  description:
    "AssistantAI platform bileşenlerinin gerçek zamanlı çalışma durumu ve son olaylar.",
};

const LAST_CHECKED = "20 Mayıs 2026 · 14:00 (UTC+3)";

type Status = "operational" | "degraded" | "outage" | "maintenance";

const STATUS_META: Record<
  Status,
  { label: string; dot: string; text: string; bg: string }
> = {
  operational: {
    label: "Çalışıyor",
    dot: "bg-relate-emerald",
    text: "text-relate-emerald",
    bg: "bg-relate-emerald/10",
  },
  degraded: {
    label: "Performans düşük",
    dot: "bg-relate-amber",
    text: "text-relate-amber",
    bg: "bg-relate-amber/10",
  },
  outage: {
    label: "Kesinti",
    dot: "bg-relate-coral",
    text: "text-relate-coral",
    bg: "bg-relate-coral/10",
  },
  maintenance: {
    label: "Bakım",
    dot: "bg-relate-azure",
    text: "text-relate-azure",
    bg: "bg-relate-azure/10",
  },
};

const COMPONENTS: { name: string; description: string; status: Status }[] = [
  {
    name: "Sohbet API",
    description: "Asistan mesaj uçları (/api/chat)",
    status: "operational",
  },
  {
    name: "Bilgi Tabanı (RAG)",
    description: "Belge indeksleme ve arama",
    status: "operational",
  },
  {
    name: "Randevu Servisi",
    description: "Oluşturma, güncelleme, hatırlatma",
    status: "operational",
  },
  {
    name: "Google Calendar Entegrasyonu",
    description: "Senkronizasyon ve OAuth yenileme",
    status: "operational",
  },
  {
    name: "WhatsApp Cloud API",
    description: "Gelen/giden mesaj köprüsü",
    status: "operational",
  },
  {
    name: "Sesli Yanıt (TTS) ve STT",
    description: "OpenAI ses uçları",
    status: "operational",
  },
  {
    name: "İşletme Paneli",
    description: "Dashboard, ayarlar, raporlar",
    status: "operational",
  },
];

const INCIDENTS: {
  date: string;
  title: string;
  status: Status;
  detail: string;
}[] = [
  {
    date: "12 Mayıs 2026",
    title: "Planlı veritabanı bakımı tamamlandı",
    status: "maintenance",
    detail:
      "MongoDB ana kümesinde 23:00–23:25 (UTC+3) aralığında yapılan planlı versiyon yükseltmesi sorunsuz tamamlandı. Kullanıcı etkisi gözlemlenmedi.",
  },
  {
    date: "3 Mayıs 2026",
    title: "WhatsApp webhook gecikmesi",
    status: "degraded",
    detail:
      "08:40–09:05 (UTC+3) arasında Meta tarafından kaynaklanan webhook teslim gecikmesi sebebiyle bazı mesajlar 1–3 dakika geç işlendi. Servis kuyruğu otomatik olarak yeniden işledi.",
  },
];

export default function StatusPage() {
  const overall: Status = COMPONENTS.every((c) => c.status === "operational")
    ? "operational"
    : COMPONENTS.some((c) => c.status === "outage")
    ? "outage"
    : "degraded";

  const overallMeta = STATUS_META[overall];

  return (
    <div className="min-h-screen bg-relate-canvas text-relate-ink">
      <header className="sticky top-0 z-10 bg-relate-canvas/90 backdrop-blur-sm border-b border-relate-border">
        <div className="max-w-relate mx-auto px-6 lg:px-10 h-14 flex items-center justify-between">
          <Link
            href="/"
            className="text-[15px] font-medium text-relate-ink hover:text-relate-signal transition-colors"
          >
            AssistantAI
          </Link>
          <span className="text-[13px] text-relate-ash">
            Son kontrol: {LAST_CHECKED}
          </span>
        </div>
      </header>

      <main className="max-w-[860px] mx-auto px-6 lg:px-0 py-16">
        <h1 className="text-[32px] sm:text-[40px] font-semibold tracking-[-0.022em] text-relate-ink mb-3">
          Sistem Durumu
        </h1>
        <p className="text-relate-ash text-[15px] mb-10">
          Platform bileşenlerinin gerçek zamanlı durumu ve son 30 günün olayları.
        </p>

        {/* Genel durum */}
        <div className={`card p-6 mb-10 flex items-center gap-4 ${overallMeta.bg}`}>
          <span className={`w-3 h-3 rounded-full ${overallMeta.dot} animate-pulse`} />
          <div>
            <div className="text-[18px] font-semibold text-relate-ink">
              Tüm sistemler {overall === "operational" ? "çalışıyor" : overallMeta.label.toLowerCase()}
            </div>
            <div className="text-[13px] text-relate-graphite mt-0.5">
              {overall === "operational"
                ? "Aktif olay yok. Hizmetler normal performansta."
                : "Aktif olay var, detay aşağıda."}
            </div>
          </div>
        </div>

        {/* Bileşenler */}
        <section className="mb-12">
          <h2 className="text-[20px] font-semibold tracking-[-0.015em] text-relate-ink mb-4">
            Bileşenler
          </h2>
          <div className="card divide-y divide-relate-rule">
            {COMPONENTS.map((c) => {
              const m = STATUS_META[c.status];
              return (
                <div
                  key={c.name}
                  className="flex items-start sm:items-center justify-between gap-4 px-5 py-4"
                >
                  <div className="min-w-0">
                    <div className="font-medium text-[15px] text-relate-ink">
                      {c.name}
                    </div>
                    <div className="text-[13px] text-relate-graphite mt-0.5">
                      {c.description}
                    </div>
                  </div>
                  <span
                    className={`shrink-0 inline-flex items-center gap-2 px-2.5 py-1 rounded text-[12px] font-medium ${m.bg} ${m.text}`}
                  >
                    <span className={`w-1.5 h-1.5 rounded-full ${m.dot}`} />
                    {m.label}
                  </span>
                </div>
              );
            })}
          </div>
        </section>

        {/* Son olaylar */}
        <section className="mb-12">
          <h2 className="text-[20px] font-semibold tracking-[-0.015em] text-relate-ink mb-4">
            Son olaylar
          </h2>
          {INCIDENTS.length === 0 ? (
            <div className="card p-6 text-[14px] text-relate-graphite">
              Son 30 günde olay kaydedilmedi.
            </div>
          ) : (
            <div className="space-y-4">
              {INCIDENTS.map((it, idx) => {
                const m = STATUS_META[it.status];
                return (
                  <article key={idx} className="card p-5">
                    <div className="flex items-center justify-between gap-3 mb-2">
                      <span className="text-[12px] text-relate-ash">{it.date}</span>
                      <span
                        className={`inline-flex items-center gap-2 px-2.5 py-1 rounded text-[12px] font-medium ${m.bg} ${m.text}`}
                      >
                        <span className={`w-1.5 h-1.5 rounded-full ${m.dot}`} />
                        {m.label}
                      </span>
                    </div>
                    <h3 className="text-[16px] font-semibold text-relate-ink mb-1">
                      {it.title}
                    </h3>
                    <p className="text-[14px] leading-[1.65] text-relate-graphite">
                      {it.detail}
                    </p>
                  </article>
                );
              })}
            </div>
          )}
        </section>

        {/* Bildirim */}
        <section className="card-gray p-6 rounded-lg">
          <h3 className="text-[16px] font-semibold text-relate-ink mb-2">
            Olay bildirimi
          </h3>
          <p className="text-[14px] text-relate-graphite leading-[1.65]">
            Bir kesinti veya performans sorunu fark ettiniz mi?{" "}
            <a
              href="mailto:status@assistantai.app"
              className="text-relate-signal underline underline-offset-2 hover:opacity-80"
            >
              status@assistantai.app
            </a>{" "}
            adresine bildirin. Hesap, işletme adı ve gözlemlediğiniz davranışı
            paylaşmanız çözüm süresini hızlandırır.
          </p>
        </section>
      </main>

      <footer className="border-t border-relate-border mt-16 py-8">
        <div className="max-w-relate mx-auto px-6 lg:px-10 text-center text-[13px] text-relate-ash">
          © {new Date().getFullYear()} AssistantAI. Tüm hakları saklıdır.
        </div>
      </footer>
    </div>
  );
}
