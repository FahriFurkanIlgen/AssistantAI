"use client";
import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { api } from "@/lib/api";
import { LogoLockup } from "@/components/brand/Logo";

interface WorkingHours {
  start: string;
  end: string;
  is_open: boolean;
}

interface WorkingSchedule {
  monday: WorkingHours;
  tuesday: WorkingHours;
  wednesday: WorkingHours;
  thursday: WorkingHours;
  friday: WorkingHours;
  saturday: WorkingHours;
  sunday: WorkingHours;
}

interface ServiceItem {
  name: string;
  name_tr: string;
  duration_minutes: number;
  price: number;
  description?: string;
}

interface PublicBusiness {
  name: string;
  slug: string;
  sector: string;
  city: string;
  ai_persona_name: string;
  instagram_handle?: string;
  services: ServiceItem[];
  working_schedule?: WorkingSchedule;
}

const DAY_LABELS: Record<string, string> = {
  monday: "Pazartesi",
  tuesday: "Salı",
  wednesday: "Çarşamba",
  thursday: "Perşembe",
  friday: "Cuma",
  saturday: "Cumartesi",
  sunday: "Pazar",
};

const DAY_ORDER = [
  "monday",
  "tuesday",
  "wednesday",
  "thursday",
  "friday",
  "saturday",
  "sunday",
];

export default function PublicBusinessPage() {
  const params = useParams();
  const router = useRouter();
  const slug = params.slug as string;

  const [business, setBusiness] = useState<PublicBusiness | null>(null);
  const [loading, setLoading] = useState(true);
  const [notFound, setNotFound] = useState(false);

  useEffect(() => {
    if (!slug) return;
    api
      .getPublicBusiness(slug)
      .then(setBusiness)
      .catch(() => setNotFound(true))
      .finally(() => setLoading(false));
  }, [slug]);

  if (loading) {
    return (
      <div className="min-h-screen bg-apple-gray flex items-center justify-center">
        <p className="text-apple-secondary text-sm">Yükleniyor...</p>
      </div>
    );
  }

  if (notFound || !business) {
    return (
      <div className="min-h-screen bg-apple-gray flex flex-col items-center justify-center gap-3">
        <p className="text-2xl font-bold text-apple-ink">İşletme bulunamadı</p>
        <p className="text-apple-secondary text-sm">
          Bu bağlantı geçersiz veya süresi dolmuş olabilir.
        </p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-cyber-bg relative">
      <div className="absolute top-0 inset-x-0 h-[400px] bg-cyber-emerald-glow pointer-events-none" aria-hidden />
      {/* Hero */}
      <div className="relative px-6 pt-20 pb-12 text-center border-b border-cyber-rule">
        <div className="w-16 h-16 bg-cyber-glass border border-cyber-rule rounded-full flex items-center justify-center text-3xl mx-auto mb-5 text-cyber-emerald font-serif">
          {business.name.charAt(0)}
        </div>
        <h1 className="font-serif font-light text-[40px] leading-tight tracking-tight text-cyber-ink">{business.name}</h1>
        <p className="text-cyber-ink/55 mt-2 text-sm capitalize font-light">
          {business.sector}
          {business.city ? ` · ${business.city}` : ""}
        </p>
        {business.instagram_handle && (
          <a
            href={`https://instagram.com/${business.instagram_handle}`}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-block mt-3 text-cyber-emerald/80 hover:text-cyber-emerald text-sm transition-colors"
          >
            @{business.instagram_handle}
          </a>
        )}
      </div>

      <div className="relative max-w-lg mx-auto px-4 py-10 space-y-6">
        {/* CTA */}
        <button
          onClick={() => router.push(`/chat/${slug}`)}
          className="btn-primary w-full py-4 text-[15px]"
        >
          Randevu Al
        </button>

        {/* Services */}
        {business.services.length > 0 && (
          <section className="card !p-0 overflow-hidden">
            <div className="px-5 py-3 border-b border-cyber-rule">
              <h2 className="cyber-label text-[11px]">Hizmetler</h2>
            </div>
            <ul className="divide-y divide-cyber-ruleSoft">
              {business.services.map((s, i) => (
                <li
                  key={i}
                  className="px-5 py-4 flex items-center justify-between gap-4"
                >
                  <div>
                    <p className="font-light text-cyber-ink text-[14px]">
                      {s.name_tr || s.name}
                    </p>
                    {s.description && (
                      <p className="text-xs text-cyber-ink/50 mt-0.5 font-light">
                        {s.description}
                      </p>
                    )}
                    <p className="cyber-label text-[9px] mt-1.5">
                      ⏱ {s.duration_minutes} dk
                    </p>
                  </div>
                  {s.price > 0 && (
                    <span className="num-mono text-cyber-emerald shrink-0 text-[14px]">
                      {s.price.toLocaleString("tr-TR")} ₺
                    </span>
                  )}
                </li>
              ))}
            </ul>
          </section>
        )}

        {/* Working Hours */}
        {business.working_schedule && (
          <section className="card !p-0 overflow-hidden">
            <div className="px-5 py-3 border-b border-cyber-rule">
              <h2 className="cyber-label text-[11px]">Çalışma Saatleri</h2>
            </div>
            <ul className="divide-y divide-cyber-ruleSoft">
              {DAY_ORDER.map((day) => {
                const hours = (business.working_schedule as WorkingSchedule)[
                  day as keyof WorkingSchedule
                ];
                return (
                  <li
                    key={day}
                    className="px-5 py-3 flex items-center justify-between text-sm font-light"
                  >
                    <span className="text-cyber-ink/85">{DAY_LABELS[day]}</span>
                    {hours.is_open ? (
                      <span className="num-mono text-cyber-ink/60 text-[13px]">
                        {hours.start} – {hours.end}
                      </span>
                    ) : (
                      <span className="badge badge-coral">Kapalı</span>
                    )}
                  </li>
                );
              })}
            </ul>
          </section>
        )}

        {/* Footer */}
        <p className="text-center text-xs text-apple-secondary pb-4 inline-flex items-center justify-center gap-1.5">
          Powered by <LogoLockup size={14} wordmark />
        </p>
      </div>
    </div>
  );
}
