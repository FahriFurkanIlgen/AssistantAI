"use client";
import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { api } from "@/lib/api";

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
    <div className="min-h-screen bg-apple-gray">
      {/* Hero */}
      <div className="bg-apple-ink text-white px-6 pt-16 pb-10 text-center">
        <div className="w-16 h-16 bg-white/10 rounded-full flex items-center justify-center text-3xl mx-auto mb-4">
          {business.name.charAt(0)}
        </div>
        <h1 className="text-3xl font-bold">{business.name}</h1>
        <p className="text-white/60 mt-1 text-sm capitalize">
          {business.sector}
          {business.city ? ` · ${business.city}` : ""}
        </p>
        {business.instagram_handle && (
          <a
            href={`https://instagram.com/${business.instagram_handle}`}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-block mt-3 text-white/70 hover:text-white text-sm transition-colors"
          >
            @{business.instagram_handle}
          </a>
        )}
      </div>

      <div className="max-w-lg mx-auto px-4 py-8 space-y-6">
        {/* CTA */}
        <button
          onClick={() => router.push(`/chat/${slug}`)}
          className="w-full py-4 rounded-apple bg-apple-blue text-white text-base font-semibold hover:bg-[#0077ed] transition-colors shadow-sm"
        >
          Randevu Al
        </button>

        {/* Services */}
        {business.services.length > 0 && (
          <section className="bg-white rounded-apple-lg border border-apple-border overflow-hidden">
            <div className="px-5 py-3 border-b border-apple-border">
              <h2 className="font-semibold text-apple-ink">Hizmetler</h2>
            </div>
            <ul className="divide-y divide-apple-border">
              {business.services.map((s, i) => (
                <li
                  key={i}
                  className="px-5 py-4 flex items-center justify-between gap-4"
                >
                  <div>
                    <p className="font-medium text-apple-ink">
                      {s.name_tr || s.name}
                    </p>
                    {s.description && (
                      <p className="text-xs text-apple-secondary mt-0.5">
                        {s.description}
                      </p>
                    )}
                    <p className="text-xs text-apple-secondary mt-1">
                      ⏱ {s.duration_minutes} dk
                    </p>
                  </div>
                  {s.price > 0 && (
                    <span className="text-apple-ink font-semibold shrink-0 text-sm">
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
          <section className="bg-white rounded-apple-lg border border-apple-border overflow-hidden">
            <div className="px-5 py-3 border-b border-apple-border">
              <h2 className="font-semibold text-apple-ink">Çalışma Saatleri</h2>
            </div>
            <ul className="divide-y divide-apple-border">
              {DAY_ORDER.map((day) => {
                const hours = (business.working_schedule as WorkingSchedule)[
                  day as keyof WorkingSchedule
                ];
                return (
                  <li
                    key={day}
                    className="px-5 py-3 flex items-center justify-between text-sm"
                  >
                    <span className="text-apple-ink">{DAY_LABELS[day]}</span>
                    {hours.is_open ? (
                      <span className="text-apple-secondary">
                        {hours.start} – {hours.end}
                      </span>
                    ) : (
                      <span className="text-red-500 text-xs font-medium">
                        Kapalı
                      </span>
                    )}
                  </li>
                );
              })}
            </ul>
          </section>
        )}

        {/* Footer */}
        <p className="text-center text-xs text-apple-secondary pb-4">
          Powered by AssistantAI
        </p>
      </div>
    </div>
  );
}
