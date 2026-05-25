"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Image from "next/image";
import { publicReservationApi } from "@/lib/api";
import { SelectField } from "@/components/ui/SelectField";

const DAY_MAP: Record<string, number> = {
  sunday: 0, monday: 1, tuesday: 2, wednesday: 3,
  thursday: 4, friday: 5, saturday: 6,
};

type Step = "form" | "confirm" | "done";

interface Config {
  business_name: string;
  logo_url?: string | null;
  phone?: string | null;
  address?: string | null;
  shifts: { id: string; name: string; start_time: string; end_time: string; days: string[] }[];
  sections: string[];
  max_party_size: number;
  reservation_window_days: number;
}

interface AvailableTable {
  id: string;
  number: string;
  capacity: number;
  section: string;
  shape: string;
}

function dateRange(windowDays: number): string[] {
  const dates: string[] = [];
  const today = new Date();
  for (let i = 0; i < windowDays; i++) {
    const d = new Date(today);
    d.setDate(today.getDate() + i);
    dates.push(d.toISOString().split("T")[0]);
  }
  return dates;
}

function formatDateTR(dateStr: string) {
  const d = new Date(dateStr + "T00:00:00");
  return d.toLocaleDateString("tr-TR", { day: "numeric", month: "long", year: "numeric", weekday: "long" });
}

export default function PublicReservationPage() {
  const params = useParams();
  const slug = params.businessSlug as string;

  const [config, setConfig] = useState<Config | null>(null);
  const [error, setError] = useState("");
  const [step, setStep] = useState<Step>("form");

  // Form state
  const [date, setDate] = useState("");
  const [shift, setShift] = useState<Config["shifts"][0] | null>(null);
  const [partySize, setPartySize] = useState(2);
  const [section, setSection] = useState("");
  const [tables, setTables] = useState<AvailableTable[]>([]);
  const [combinations, setCombinations] = useState<{
    tables: AvailableTable[];
    combined_capacity: number;
    table_ids: string[];
    label: string;
  }[]>([]);
  const [selectedTable, setSelectedTable] = useState<AvailableTable | null>(null);
  const [selectedCombo, setSelectedCombo] = useState<typeof combinations[0] | null>(null);
  const [loadingTables, setLoadingTables] = useState(false);
  const [tableError, setTableError] = useState("");

  // Guest info
  const [name, setName] = useState("");
  const [phone, setPhone] = useState("");
  const [email, setEmail] = useState("");
  const [requests, setRequests] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState("");

  // Done
  const [confirmation, setConfirmation] = useState<{ table_number: string; shift_name: string; shift_start: string; shift_end: string } | null>(null);

  useEffect(() => {
    publicReservationApi
      .getConfig(slug)
      .then((cfg) => {
        setConfig(cfg);
        // Default: today if valid or next valid date
        const today = new Date().toISOString().split("T")[0];
        setDate(today);
        if (cfg.shifts.length > 0) setShift(cfg.shifts[0]);
        if (cfg.sections.length > 0) setSection(cfg.sections[0]);
      })
      .catch(() => setError("Rezervasyon sayfası bulunamadı veya bu işletmede rezervasyon aktif değil."));
  }, [slug]);

  // Load available tables whenever date/shift/partySize/section changes
  useEffect(() => {
    if (!date || !shift || !config) return;
    setSelectedTable(null);
    setSelectedCombo(null);
    setTables([]);
    setCombinations([]);
    setTableError("");
    setLoadingTables(true);
    publicReservationApi
      .getAvailability(slug, { date, shift_name: shift.name, party_size: partySize, section: section || undefined })
      .then((data) => {
        setTables(data.available_tables);
        setCombinations(data.combinations ?? []);
      })
      .catch(() => setTableError("Uygunluk bilgisi alınamadı."))
      .finally(() => setLoadingTables(false));
  }, [date, shift, partySize, section, config, slug]);

  const availableDates = config
    ? dateRange(config.reservation_window_days)
    : [];

  const shiftsForDate = config && date
    ? config.shifts.filter((s) => s.days.includes(
        Object.keys(DAY_MAP).find((k) => DAY_MAP[k] === new Date(date + "T00:00:00").getDay()) ?? ""
      ))
    : [];

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedTable && !selectedCombo) return;
    if (!shift) return;
    setSubmitting(true);
    setSubmitError("");
    try {
      const payload = selectedCombo
        ? {
            table_ids: selectedCombo.table_ids,
            customer_name: name,
            customer_phone: phone,
            customer_email: email || undefined,
            party_size: partySize,
            date,
            shift_name: shift.name,
            shift_start: shift.start_time,
            shift_end: shift.end_time,
            special_requests: requests || undefined,
          }
        : {
            table_id: selectedTable!.id,
            customer_name: name,
            customer_phone: phone,
            customer_email: email || undefined,
            party_size: partySize,
            date,
            shift_name: shift.name,
            shift_start: shift.start_time,
            shift_end: shift.end_time,
            special_requests: requests || undefined,
          };
      const res = await publicReservationApi.createReservation(slug, payload);
      setConfirmation({
        table_number: res.table_number ?? (selectedCombo?.label ?? selectedTable!.number),
        shift_name: shift.name,
        shift_start: shift.start_time,
        shift_end: shift.end_time,
      });
      setStep("done");
    } catch (err: unknown) {
      const msg = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
      setSubmitError(msg ?? "Rezervasyon oluşturulamadı. Lütfen tekrar deneyin.");
    } finally {
      setSubmitting(false);
    }
  };

  // ── Error state ──
  if (error) {
    return (
      <div className="min-h-screen bg-relate-canvas flex items-center justify-center p-6">
        <div className="card p-8 max-w-sm w-full text-center">
          <p className="text-[15px] font-medium text-relate-ink mb-2">Sayfa Bulunamadı</p>
          <p className="text-[13px] text-relate-graphite">{error}</p>
        </div>
      </div>
    );
  }

  if (!config) {
    return (
      <div className="min-h-screen bg-relate-canvas flex items-center justify-center">
        <div className="w-8 h-8 border-2 border-relate-signal border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  // ── Done / Confirmation ──
  if (step === "done" && confirmation) {
    return (
      <div className="min-h-screen bg-relate-canvas flex items-center justify-center p-6">
        <div className="card p-8 max-w-sm w-full text-center space-y-4">
          <div className="w-12 h-12 rounded-full bg-emerald-50 border border-emerald-200 flex items-center justify-center mx-auto text-xl">
            ✓
          </div>
          <div>
            <p className="text-[17px] font-semibold text-relate-ink">Rezervasyonunuz Alındı!</p>
            <p className="text-[13px] text-relate-graphite mt-1">
              {config.business_name} · {formatDateTR(date)}
            </p>
          </div>
          <div className="bg-relate-wash rounded-xl p-4 text-left space-y-2 text-[13px]">
            <div className="flex justify-between">
              <span className="text-relate-graphite">Vardiya</span>
              <span className="font-medium text-relate-ink">{confirmation.shift_name} ({confirmation.shift_start}–{confirmation.shift_end})</span>
            </div>
            <div className="flex justify-between">
              <span className="text-relate-graphite">Masa</span>
              <span className="font-medium text-relate-ink">#{confirmation.table_number}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-relate-graphite">Kişi</span>
              <span className="font-medium text-relate-ink">{partySize} kişi</span>
            </div>
            <div className="flex justify-between">
              <span className="text-relate-graphite">İsim</span>
              <span className="font-medium text-relate-ink">{name}</span>
            </div>
          </div>
          {config.phone && (
            <p className="text-[12px] text-relate-graphite">
              Değişiklik için: <a href={`tel:${config.phone}`} className="text-relate-signal hover:underline">{config.phone}</a>
            </p>
          )}
          <button
            onClick={() => {
              setStep("form");
              setSelectedTable(null);
              setName(""); setPhone(""); setEmail(""); setRequests("");
              setConfirmation(null);
            }}
            className="btn-outline w-full text-[13px]"
          >
            Yeni Rezervasyon
          </button>
        </div>
      </div>
    );
  }

  // ── Main form ──
  return (
    <div className="min-h-screen bg-relate-canvas">
      {/* Header */}
      <header className="bg-relate-wash border-b border-relate-border">
        <div className="max-w-xl mx-auto px-5 py-4 flex items-center gap-3">
          {config.logo_url ? (
            <div className="w-10 h-10 rounded-lg bg-white border border-relate-border overflow-hidden flex items-center justify-center shrink-0">
              <Image src={config.logo_url} alt={config.business_name} width={40} height={40} className="object-contain p-0.5" />
            </div>
          ) : (
            <div className="w-10 h-10 rounded-lg bg-relate-signal/20 flex items-center justify-center text-relate-signal font-semibold shrink-0">
              {config.business_name[0]}
            </div>
          )}
          <div>
            <p className="text-[15px] font-semibold text-relate-ink">{config.business_name}</p>
            {config.address && <p className="text-[12px] text-relate-graphite truncate">{config.address}</p>}
          </div>
        </div>
      </header>

      <main className="max-w-xl mx-auto px-5 py-8 space-y-6">
        <div>
          <h1 className="text-[20px] font-semibold text-relate-ink tracking-tight">Masa Rezervasyonu</h1>
          <p className="text-[13px] text-relate-graphite mt-0.5">Tarih ve vardiyayı seçin, uygun masayı belirleyin</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-5">
          {/* Step 1: Date + Shift + Party + Section */}
          <div className="card p-5 space-y-4">
            <p className="text-[13px] font-medium text-relate-ink">Rezervasyon Detayları</p>

            <div>
              <label className="block text-[12px] text-relate-graphite mb-1">Tarih</label>
              <input
                type="date"
                required
                className="input-field w-full"
                min={availableDates[0]}
                max={availableDates[availableDates.length - 1]}
                value={date}
                onChange={(e) => {
                  setDate(e.target.value);
                  setShift(null);
                  setSelectedTable(null);
                }}
              />
            </div>

            <div>
              <label className="block text-[12px] text-relate-graphite mb-1">Vardiya</label>
              {shiftsForDate.length === 0 ? (
                <p className="text-[12px] text-coral-600 bg-coral/5 border border-coral/20 rounded-lg px-3 py-2">
                  Bu tarihte açık vardiya bulunmuyor.
                </p>
              ) : (
                <div className="flex gap-2 flex-wrap">
                  {shiftsForDate.map((s) => (
                    <button
                      key={s.id}
                      type="button"
                      onClick={() => { setShift(s); setSelectedTable(null); }}
                      className={`flex-1 px-4 py-2.5 rounded-xl border text-[13px] font-medium transition-colors ${
                        shift?.name === s.name
                          ? "bg-relate-signal/10 border-relate-signal/40 text-relate-signal"
                          : "bg-relate-wash border-relate-border text-relate-graphite hover:border-relate-signal/30"
                      }`}
                    >
                      <span className="block">{s.name}</span>
                      <span className="block text-[11px] opacity-70">{s.start_time}–{s.end_time}</span>
                    </button>
                  ))}
                </div>
              )}
            </div>

            <div className="grid grid-cols-2 gap-3">
              <SelectField
                label="Kişi Sayısı"
                value={partySize}
                options={Array.from({ length: config.max_party_size }, (_, i) => ({
                  value: i + 1,
                  label: `${i + 1} kişi`,
                }))}
                onChange={(v) => { setPartySize(parseInt(v)); setSelectedTable(null); }}
              />
              <SelectField
                label="Bölüm Tercihi"
                value={section}
                options={[
                  { value: "", label: "Fark etmez" },
                  ...config.sections.map((s) => ({ value: s, label: s })),
                ]}
                onChange={(v) => { setSection(v); setSelectedTable(null); }}
              />
            </div>
          </div>

          {/* Step 2: Table selection */}
          {shift && (
            <div className="card p-5 space-y-3">
              <p className="text-[13px] font-medium text-relate-ink">Masa Seçin</p>
              {loadingTables ? (
                <div className="flex gap-2">
                  {[1, 2, 3].map((i) => (
                    <div key={i} className="h-14 flex-1 bg-relate-rule rounded-xl animate-pulse" />
                  ))}
                </div>
              ) : tableError ? (
                <p className="text-[12px] text-coral-600">{tableError}</p>
              ) : tables.length === 0 && combinations.length === 0 ? (
                <p className="text-[12px] text-relate-graphite bg-relate-wash rounded-xl px-4 py-3">
                  Seçilen kriterlere uygun müsait masa bulunmuyor. Lütfen farklı tarih/vardiya veya kişi sayısı deneyin.
                </p>
              ) : (
                <>
                  {/* Single tables */}
                  {tables.length > 0 && (
                    <div className="grid grid-cols-3 gap-2">
                      {tables.map((t) => (
                        <button
                          key={t.id}
                          type="button"
                          onClick={() => { setSelectedTable(t); setSelectedCombo(null); }}
                          className={`py-3 px-2 rounded-xl border text-center transition-colors ${
                            selectedTable?.id === t.id
                            ? "bg-relate-signal/20 border-relate-signal/60 text-relate-signal"
                            : "bg-relate-wash border-relate-border text-relate-graphite hover:border-relate-signal/40 hover:text-relate-ink"
                          }`}
                        >
                          <p className="text-[13px] font-semibold">#{t.number}</p>
                          <p className="text-[11px] opacity-70">{t.capacity}k · {t.section}</p>
                        </button>
                      ))}
                    </div>
                  )}

                  {/* Combinations */}
                  {combinations.length > 0 && (
                    <div>
                      <p className="text-[11px] text-relate-graphite mb-2 mt-1">
                        {tables.length > 0 ? "— veya masa birleştirme" : "Birleştirilmiş masa seçenekleri"}
                      </p>
                      <div className="space-y-2">
                        {combinations.map((c, i) => (
                          <button
                            key={i}
                            type="button"
                            onClick={() => { setSelectedCombo(c); setSelectedTable(null); }}
                            className={`w-full flex items-center justify-between px-4 py-3 rounded-xl border text-left transition-colors ${
                              selectedCombo?.table_ids.join() === c.table_ids.join()
                              ? "bg-relate-signal/20 border-relate-signal/60 text-relate-signal"
                              : "bg-relate-wash border-relate-border text-relate-graphite hover:border-relate-signal/40 hover:text-relate-ink"
                            }`}
                          >
                            <span className="text-[13px] font-semibold">{c.label}</span>
                            <span className="text-[11px] opacity-70">
                              Toplam {c.combined_capacity} kişilik
                              {c.tables[0]?.section ? ` · ${c.tables[0].section}` : ""}
                            </span>
                          </button>
                        ))}
                      </div>
                    </div>
                  )}
                </>
              )}
            </div>
          )}

          {/* Step 3: Guest info */}
          {(selectedTable || selectedCombo) && (
            <div className="card p-5 space-y-4">
              <p className="text-[13px] font-medium text-relate-ink">İletişim Bilgileri</p>
              <div>
                <label className="block text-[12px] text-relate-graphite mb-1">Ad Soyad *</label>
                <input
                  required
                  type="text"
                  className="input-field w-full"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                />
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-[12px] text-relate-graphite mb-1">Telefon *</label>
                  <input
                    required
                    type="tel"
                    className="input-field w-full"
                    value={phone}
                    onChange={(e) => setPhone(e.target.value)}
                  />
                </div>
                <div>
                  <label className="block text-[12px] text-relate-graphite mb-1">E-posta</label>
                  <input
                    type="email"
                    className="input-field w-full"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                  />
                </div>
              </div>
              <div>
                <label className="block text-[12px] text-relate-graphite mb-1">Özel İstekler</label>
                <textarea
                  rows={2}
                  className="input-field w-full resize-none"
                  placeholder="Doğum günü, alerji, bebek sandalyesi…"
                  value={requests}
                  onChange={(e) => setRequests(e.target.value)}
                />
              </div>

              {/* Summary */}
              <div className="bg-relate-wash rounded-xl p-3 text-[12px] text-relate-graphite space-y-1">
                <div className="flex justify-between">
                  <span>Tarih</span>
                  <span className="font-medium text-relate-ink">{formatDateTR(date)}</span>
                </div>
                <div className="flex justify-between">
                  <span>Vardiya</span>
                  <span className="font-medium text-relate-ink">{shift?.name} ({shift?.start_time}–{shift?.end_time})</span>
                </div>
                <div className="flex justify-between">
                  <span>Masa</span>
                  <span className="font-medium text-relate-ink">
                    {selectedCombo
                      ? `${selectedCombo.label} · ${selectedCombo.combined_capacity} kişilik`
                      : selectedTable
                      ? `#${selectedTable.number} · ${selectedTable.capacity} kişilik · ${selectedTable.section}`
                      : "—"}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span>Kişi Sayısı</span>
                  <span className="font-medium text-relate-ink">{partySize} kişi</span>
                </div>
              </div>

              {submitError && (
                <p className="text-[12px] text-coral-600 bg-coral/5 border border-coral/20 rounded-lg px-3 py-2">
                  {submitError}
                </p>
              )}

              <button
                type="submit"
                disabled={submitting}
                className="btn-primary w-full"
              >
                {submitting ? "Rezervasyon Yapılıyor…" : "Rezervasyonu Onayla"}
              </button>
            </div>
          )}
        </form>

        {config.phone && (
          <p className="text-center text-[12px] text-relate-graphite">
            Yardım için:{" "}
            <a href={`tel:${config.phone}`} className="text-relate-signal hover:underline">
              {config.phone}
            </a>
          </p>
        )}
      </main>
    </div>
  );
}
