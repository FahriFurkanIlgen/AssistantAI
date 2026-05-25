"use client";

import { useEffect, useState } from "react";
import { api, Reservation, RestaurantTable, DiningShift } from "@/lib/api";
import toast from "react-hot-toast";
import { SelectField } from "@/components/ui/SelectField";

type ViewMode = "floor" | "list";

const STATUS_LABELS: Record<string, string> = {
  confirmed: "Onaylı",
  seated: "Masada",
  completed: "Tamamlandı",
  cancelled: "İptal",
  no_show: "Gelmedi",
};

const STATUS_BADGE: Record<string, string> = {
  confirmed: "badge-azure",
  seated: "badge-emerald",
  completed: "badge-amber",
  cancelled: "badge-coral",
  no_show: "badge-coral",
};

// ---- Status dot for floor plan ----
function statusColor(tableId: string, reservations: Reservation[]) {
  const res = reservations.filter((r) => r.table_id === tableId && r.status !== "cancelled" && r.status !== "no_show");
  if (res.length === 0) return "available";
  const hasSeated = res.some((r) => r.status === "seated");
  if (hasSeated) return "seated";
  return "confirmed";
}

const floorColor: Record<string, string> = {
  available: "bg-emerald-50 border-emerald-200 text-emerald-700",
  confirmed: "bg-amber-50 border-amber-300 text-amber-800",
  seated: "bg-coral/10 border-coral/40 text-coral-700",
};

// ---- Add Reservation Modal ----
interface AddResModalProps {
  tables: RestaurantTable[];
  shifts: DiningShift[];
  selectedDate: string;
  selectedShift: string;
  reservations: Reservation[];
  onSave: (d: Partial<Reservation>) => Promise<void>;
  onClose: () => void;
}

function AddResModal({
  tables,
  shifts,
  selectedDate,
  selectedShift,
  reservations,
  onSave,
  onClose,
}: AddResModalProps) {
  const [form, setForm] = useState<Partial<Reservation>>({
    date: selectedDate,
    shift_name: selectedShift || shifts[0]?.name || "",
    party_size: 2,
    customer_name: "",
    customer_phone: "",
    customer_email: "",
    special_requests: "",
    channel: "manual",
    status: "confirmed",
  });
  const [saving, setSaving] = useState(false);

  const set = (k: keyof Reservation, v: unknown) =>
    setForm((f) => ({ ...f, [k]: v }));

  // Find occupied table IDs for selected date+shift
  const occupiedTableIds = new Set(
    reservations
      .filter(
        (r) =>
          r.date === form.date &&
          r.shift_name === form.shift_name &&
          r.status !== "cancelled" &&
          r.status !== "no_show"
      )
      .map((r) => r.table_id)
  );

  const availableTables = tables.filter(
    (t) => t.is_active && !occupiedTableIds.has(t.id) && (t.capacity ?? 0) >= (form.party_size ?? 1)
  );

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    try {
      await onSave(form);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-relate-ink/20 backdrop-blur-sm overflow-y-auto">
      <div className="card-modal w-full max-w-md p-6 my-4">
        <h3 className="text-[15px] font-semibold text-relate-ink mb-5">
          Rezervasyon Ekle
        </h3>
        <form onSubmit={submit} className="space-y-4">
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-[12px] text-relate-graphite mb-1">
                Tarih
              </label>
              <input
                type="date"
                required
                className="input-field w-full"
                value={form.date ?? ""}
                onChange={(e) => set("date", e.target.value)}
              />
            </div>
            <SelectField
              label="Vardiya"
              value={form.shift_name ?? ""}
              options={shifts.map((s) => ({ value: s.name, label: s.name }))}
              onChange={(v) => set("shift_name", v)}
            />
          </div>

          <div>
            <label className="block text-[12px] text-relate-graphite mb-1">
              Kişi Sayısı
            </label>
            <input
              type="number"
              min={1}
              max={50}
              required
              className="input-field w-full"
              value={form.party_size ?? ""}
              onChange={(e) => set("party_size", parseInt(e.target.value))}
            />
          </div>

          <SelectField
            label="Masa"
            value={form.table_id ?? ""}
            options={[
              { value: "", label: "Otomatik ata" },
              ...availableTables.map((t) => ({
                value: t.id,
                label: `Masa ${t.number} (${t.capacity}k, ${t.section})`,
              })),
            ]}
            onChange={(v) => {
              const t = tables.find((t) => t.id === v);
              set("table_id", v);
              if (t) set("table_number", t.number);
            }}
          />
          {availableTables.length === 0 && (
            <p className="text-[11px] text-coral-600 mt-1">
              Bu tarih/vardiya için uygun müsait masa yok
            </p>
          )}

          <div>
            <label className="block text-[12px] text-relate-graphite mb-1">
              Müşteri Adı
            </label>
            <input
              type="text"
              required
              className="input-field w-full"
              value={form.customer_name ?? ""}
              onChange={(e) => set("customer_name", e.target.value)}
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-[12px] text-relate-graphite mb-1">
                Telefon
              </label>
              <input
                type="tel"
                className="input-field w-full"
                value={form.customer_phone ?? ""}
                onChange={(e) => set("customer_phone", e.target.value)}
              />
            </div>
            <div>
              <label className="block text-[12px] text-relate-graphite mb-1">
                E-posta
              </label>
              <input
                type="email"
                className="input-field w-full"
                value={form.customer_email ?? ""}
                onChange={(e) => set("customer_email", e.target.value)}
              />
            </div>
          </div>

          <div>
            <label className="block text-[12px] text-relate-graphite mb-1">
              Özel İstekler
            </label>
            <textarea
              rows={2}
              className="input-field w-full resize-none"
              value={form.special_requests ?? ""}
              onChange={(e) => set("special_requests", e.target.value)}
            />
          </div>

          <div className="flex gap-2 pt-2">
            <button
              type="button"
              onClick={onClose}
              className="btn-outline flex-1"
            >
              İptal
            </button>
            <button
              type="submit"
              disabled={saving}
              className="btn-primary flex-1"
            >
              {saving ? "Kaydediliyor…" : "Kaydet"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

// ---- Edit Reservation Modal ----
interface EditResModalProps {
  reservation: Reservation;
  tables: RestaurantTable[];
  reservations: Reservation[];
  onSave: (id: string, d: Partial<Reservation>) => Promise<void>;
  onClose: () => void;
}

function EditResModal({ reservation, tables, reservations, onSave, onClose }: EditResModalProps) {
  const [tableId, setTableId] = useState(reservation.table_id ?? "");
  const [partySize, setPartySize] = useState(reservation.party_size ?? 2);
  const [status, setStatus] = useState(reservation.status ?? "confirmed");
  const [specialRequests, setSpecialRequests] = useState(reservation.special_requests ?? "");
  const [notes, setNotes] = useState(reservation.notes ?? "");
  const [saving, setSaving] = useState(false);

  // Tables that are free OR already assigned to this reservation, filtered by party size
  const occupiedTableIds = new Set(
    reservations
      .filter(
        (r) =>
          r.date === reservation.date &&
          r.shift_name === reservation.shift_name &&
          r.status !== "cancelled" &&
          r.status !== "no_show" &&
          r.id !== reservation.id
      )
      .flatMap((r) => r.table_ids?.length ? r.table_ids : [r.table_id])
  );
  const availableTables = tables.filter(
    (t) =>
      t.is_active &&
      (!occupiedTableIds.has(t.id) || t.id === reservation.table_id) &&
      (t.capacity ?? 0) >= partySize
  );

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    try {
      const tbl = tables.find((t) => t.id === tableId);
      await onSave(reservation.id!, {
        table_id: tableId,
        table_number: tbl?.number,
        table_section: tbl?.section,
        party_size: partySize,
        status,
        special_requests: specialRequests,
        notes,
      });
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-relate-ink/20 backdrop-blur-sm">
      <div className="card-modal w-full max-w-md p-6">
        <h3 className="text-[15px] font-semibold text-relate-ink mb-5">Rezervasyonu Düzenle</h3>
        <form onSubmit={submit} className="space-y-4">
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-[12px] text-relate-graphite mb-1">Kişi Sayısı</label>
              <input
                type="number"
                min={1}
                max={50}
                className="input-field w-full"
                value={partySize}
                onChange={(e) => {
                  const v = parseInt(e.target.value);
                  setPartySize(v);
                  // Reset table if it can no longer fit the new party size
                  const current = tables.find((t) => t.id === tableId);
                  if (current && (current.capacity ?? 0) < v) setTableId("");
                }}
              />
            </div>
            <SelectField
              label="Durum"
              value={status}
              options={[
                { value: "confirmed", label: "Onaylı" },
                { value: "seated", label: "Masada" },
                { value: "completed", label: "Tamamlandı" },
                { value: "cancelled", label: "İptal" },
                { value: "no_show", label: "Gelmedi" },
              ]}
              onChange={setStatus}
            />
          </div>
          <div>
            <SelectField
              label="Masa"
              value={tableId}
              options={availableTables.map((t) => ({
                value: t.id,
                label: `Masa ${t.number} (${t.capacity}k · ${t.section})${t.id === reservation.table_id ? " — mevcut" : ""}`,
              }))}
              onChange={setTableId}
            />
            {availableTables.length === 0 && (
              <p className="text-[11px] text-relate-coral mt-1">
                {partySize} kişi için uygun müsait masa yok.
              </p>
            )}
          </div>
          <div>
            <label className="block text-[12px] text-relate-graphite mb-1">Özel İstekler</label>
            <input
              type="text"
              className="input-field w-full"
              value={specialRequests}
              onChange={(e) => setSpecialRequests(e.target.value)}
            />
          </div>
          <div>
            <label className="block text-[12px] text-relate-graphite mb-1">Notlar (dahili)</label>
            <textarea
              rows={2}
              className="input-field w-full resize-none"
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
            />
          </div>
          <div className="flex gap-2 pt-1">
            <button type="button" onClick={onClose} className="btn-outline flex-1">İptal</button>
            <button type="submit" disabled={saving} className="btn-primary flex-1">
              {saving ? "Kaydediliyor…" : "Kaydet"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

// ---- Main Page ----
export default function ReservationsPage() {
  const today = new Date().toISOString().split("T")[0];

  const [selectedDate, setSelectedDate] = useState(today);
  const [selectedShift, setSelectedShift] = useState("");
  const [view, setView] = useState<ViewMode>("list");
  const [loading, setLoading] = useState(true);
  const [slug, setSlug] = useState("");

  const [reservations, setReservations] = useState<Reservation[]>([]);
  const [tables, setTables] = useState<RestaurantTable[]>([]);
  const [shifts, setShifts] = useState<DiningShift[]>([]);
  const [stats, setStats] = useState<Record<string, number>>({});

  const [addModal, setAddModal] = useState(false);
  const [editModal, setEditModal] = useState<Reservation | null>(null);
  const [detailRes, setDetailRes] = useState<Reservation | null>(null);

  const load = async () => {
    setLoading(true);
    try {
      const [res, tbls, shfts, st] = await Promise.all([
        api.getReservations({ date: selectedDate, shift_name: selectedShift || undefined }),
        api.getTables(),
        api.getShifts(),
        api.getReservationStats(),
      ]);
      setReservations(res);
      setTables(tbls);
      setShifts(shfts);
      setStats(st);
      if (!selectedShift && shfts.length > 0) setSelectedShift(shfts[0].name);
      // fetch slug for public link
      if (!slug) {
        api.getMe().then((d) => setSlug(d.slug)).catch(() => {});
      }
    } catch {
      toast.error("Veriler yüklenemedi");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedDate, selectedShift]);

  const handleSave = async (data: Partial<Reservation>) => {
    try {
      await api.createReservation(data);
      toast.success("Rezervasyon oluşturuldu");
      setAddModal(false);
      await load();
    } catch {
      toast.error("Oluşturulamadı");
    }
  };

  const handleEdit = async (id: string, data: Partial<Reservation>) => {
    try {
      await api.updateReservation(id, data as Parameters<typeof api.updateReservation>[1]);
      toast.success("Güncellendi");
      setEditModal(null);
      await load();
    } catch {
      toast.error("Güncellenemedi");
    }
  };

  const handleStatusChange = async (id: string, status: string) => {
    try {
      await api.updateReservation(id, { status });
      toast.success("Güncellendi");
      await load();
    } catch {
      toast.error("Güncellenemedi");
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm("Bu rezervasyonu silmek istiyor musunuz?")) return;
    try {
      await api.deleteReservation(id);
      toast.success("Silindi");
      setDetailRes(null);
      await load();
    } catch {
      toast.error("Silinemedi");
    }
  };

  // Filter reservations for selected shift
  const filteredRes = selectedShift
    ? reservations.filter((r) => r.shift_name === selectedShift)
    : reservations;

  const totalCovers = filteredRes
    .filter((r) => r.status !== "cancelled" && r.status !== "no_show")
    .reduce((sum, r) => sum + (r.party_size ?? 0), 0);

  const confirmedCount = filteredRes.filter((r) => r.status === "confirmed").length;
  const seatedCount = filteredRes.filter((r) => r.status === "seated").length;

  return (
    <div className="p-6 md:p-8 max-w-6xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between gap-4">
        <div>
          <h1 className="text-[22px] font-semibold text-relate-ink tracking-tight">
            Rezervasyonlar
          </h1>
          <p className="text-[13px] text-relate-graphite mt-0.5">
            Masa rezervasyonlarını yönetin
          </p>
          {slug && (
            <a
              href={`/reservations/${slug}`}
              target="_blank"
              rel="noreferrer"
              className="text-[12px] text-relate-signal hover:underline mt-1 inline-block"
            >
              /reservations/{slug} ↗ müşteri formu
            </a>
          )}
        </div>
        <button
          onClick={() => setAddModal(true)}
          className="btn-primary text-[13px] px-4 py-2 shrink-0"
        >
          + Rezervasyon Ekle
        </button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        {[
          { label: "Toplam Kapak", value: totalCovers, sub: "bu tarih/vardiya" },
          { label: "Onaylı", value: confirmedCount, sub: "bekliyor" },
          { label: "Masada", value: seatedCount, sub: "şu an" },
          { label: "Bu Ay", value: stats.total ?? 0, sub: "toplam rezervasyon" },
        ].map((s) => (
          <div key={s.label} className="card p-4">
            <p className="text-[11px] text-relate-graphite uppercase tracking-wide">
              {s.label}
            </p>
            <p className="text-[24px] font-semibold text-relate-ink num-mono mt-1">
              {s.value}
            </p>
            <p className="text-[11px] text-relate-ash mt-0.5">{s.sub}</p>
          </div>
        ))}
      </div>

      {/* Filters */}
      <div className="flex flex-wrap items-center gap-3">
        <input
          type="date"
          className="input-field"
          value={selectedDate}
          onChange={(e) => setSelectedDate(e.target.value)}
        />
        <div className="flex gap-1 bg-relate-wash border border-relate-border rounded-xl p-1">
          <button
            onClick={() => setSelectedShift("")}
            className={`px-3 py-1 rounded-lg text-[12px] font-medium transition-colors ${
              !selectedShift
                ? "bg-relate-signal/15 text-relate-signal border border-relate-signal/30"
                : "text-relate-graphite hover:text-relate-ink"
            }`}
          >
            Tümü
          </button>
          {shifts.map((s) => (
            <button
              key={s.id}
              onClick={() => setSelectedShift(s.name)}
              className={`px-3 py-1 rounded-lg text-[12px] font-medium transition-colors ${
                selectedShift === s.name
                  ? "bg-relate-signal/15 text-relate-signal border border-relate-signal/30"
                  : "text-relate-graphite hover:text-relate-ink"
              }`}
            >
              {s.name}
            </button>
          ))}
        </div>

        <div className="ml-auto flex gap-1 bg-relate-wash border border-relate-border rounded-xl p-1">
          {(["list", "floor"] as ViewMode[]).map((v) => (
            <button
              key={v}
              onClick={() => setView(v)}
              className={`px-3 py-1 rounded-lg text-[12px] font-medium transition-colors ${
                view === v
                  ? "bg-relate-signal/15 text-relate-signal border border-relate-signal/30"
                  : "text-relate-graphite hover:text-relate-ink"
              }`}
            >
              {v === "list" ? "Liste" : "Yer Planı"}
            </button>
          ))}
        </div>
      </div>

      {loading ? (
        <div className="h-64 bg-relate-rule rounded-xl animate-pulse" />
      ) : (
        <>
          {/* ---- Floor Plan View ---- */}
          {view === "floor" && (
            <div className="card p-6">
              <div
                className="relative w-full bg-relate-wash border border-relate-border rounded-xl overflow-hidden"
                style={{ height: 440 }}
              >
                <svg
                  className="absolute inset-0 w-full h-full pointer-events-none opacity-30"
                  xmlns="http://www.w3.org/2000/svg"
                >
                  <defs>
                    <pattern id="grid2" width="40" height="40" patternUnits="userSpaceOnUse">
                      <path d="M 40 0 L 0 0 0 40" fill="none" stroke="#cfcfcf" strokeWidth="0.5" />
                    </pattern>
                  </defs>
                  <rect width="100%" height="100%" fill="url(#grid2)" />
                </svg>

                {tables.map((t) => {
  const sc = statusColor(t.id!, filteredRes);
  const colorClass = floorColor[sc];
  const isRound = t.shape === "round";
  const xPct = t.x ?? 10;
  const yPct = t.y ?? 10;
  const res = filteredRes.find(
    (r) =>
      r.table_id === t.id &&
      r.status !== "cancelled" &&
      r.status !== "no_show"
  );
  return (
    <button
      key={t.id}
      onClick={() => res && setDetailRes(res)}
      className={`absolute flex flex-col items-center justify-center border text-[11px] font-medium transition-all hover:scale-105 ${colorClass} ${
        isRound ? "rounded-full" : "rounded-lg"
      } ${sc !== "available" ? "cursor-pointer shadow-relate-sm" : "cursor-default"}`}
      style={{
        left: `${xPct}%`,
        top: `${yPct}%`,
        width: isRound ? 56 : 72,
        height: isRound ? 56 : 44,
      }}
    >
      <span className="font-semibold leading-none">#{t.number}</span>
      {res ? (
        <span className="leading-none mt-0.5 text-[10px] opacity-80">
          {res.party_size}k
        </span>
      ) : (
        <span className="leading-none mt-0.5 opacity-50">{t.capacity}k</span>
      )}
    </button>
  );
})}
              </div>
              {/* Legend */}
              <div className="flex gap-4 mt-3 text-[12px]">
                {Object.entries(floorColor).map(([s, cls]) => (
                  <span key={s} className={`px-2 py-0.5 rounded border ${cls}`}>
                    {s === "available" ? "Müsait" : s === "confirmed" ? "Rezerveli" : "Masada"}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* ---- List View ---- */}
          {view === "list" && (
            <div className="card">
              {filteredRes.length === 0 ? (
                <div className="py-16 text-center text-[13px] text-relate-graphite">
                  Bu tarih ve vardiya için rezervasyon bulunamadı
                </div>
              ) : (
                <div className="divide-y divide-relate-rule">
                  {filteredRes
                    .slice()
                    .sort((a, b) => (a.shift_start ?? "").localeCompare(b.shift_start ?? ""))
                    .map((r) => (
                      <div key={r.id} className="px-6 py-4 flex items-center gap-4">
                        <div className="shrink-0 w-10 h-10 rounded-lg bg-relate-wash border border-relate-border flex flex-col items-center justify-center">
                          <span className="text-[11px] font-semibold text-relate-ink leading-none">
                            #{r.table_number ?? "–"}
                          </span>
                          <span className="text-[10px] text-relate-graphite leading-none mt-0.5">
                            {r.party_size}k
                          </span>
                        </div>
                        <div className="flex-1 min-w-0">
                          <p className="text-[13px] font-medium text-relate-ink truncate">
                            {r.customer_name}
                          </p>
                          <p className="text-[12px] text-relate-graphite truncate">
                            {r.customer_phone}
                            {r.special_requests
                              ? ` · ${r.special_requests}`
                              : ""}
                          </p>
                        </div>
                        <div className="shrink-0 flex items-center gap-2">
                          <span className="text-[11px] text-relate-graphite">
                            {r.shift_name} · {r.shift_start}–{r.shift_end}
                          </span>
                          <span
                            className={`badge ${STATUS_BADGE[r.status ?? "confirmed"]}`}
                          >
                            {STATUS_LABELS[r.status ?? "confirmed"]}
                          </span>
                        </div>
                        <div className="shrink-0 flex gap-1">
                          <button
                            onClick={() => setEditModal(r)}
                            className="text-[11px] px-2 py-1 rounded text-relate-graphite hover:bg-relate-wash border border-relate-border transition-colors"
                          >
                            Düzenle
                          </button>
                          {r.status === "confirmed" && (
                            <button
                              onClick={() => handleStatusChange(r.id!, "seated")}
                              className="text-[11px] px-2 py-1 rounded bg-emerald-50 text-emerald-700 hover:bg-emerald-100 border border-emerald-200 transition-colors"
                            >
                              Oturt
                            </button>
                          )}
                          {r.status === "seated" && (
                            <button
                              onClick={() => handleStatusChange(r.id!, "completed")}
                              className="text-[11px] px-2 py-1 rounded bg-amber-50 text-amber-700 hover:bg-amber-100 border border-amber-200 transition-colors"
                            >
                              Tamamla
                            </button>
                          )}
                          {(r.status === "confirmed" || r.status === "seated") && (
                            <button
                              onClick={() => handleStatusChange(r.id!, "cancelled")}
                              className="text-[11px] px-2 py-1 rounded bg-coral/5 text-coral-600 hover:bg-coral/10 border border-coral/20 transition-colors"
                            >
                              İptal
                            </button>
                          )}
                          <button
                            onClick={() => handleDelete(r.id!)}
                            className="text-[11px] px-2 py-1 rounded text-relate-graphite hover:bg-relate-wash transition-colors"
                          >
                            Sil
                          </button>
                        </div>
                      </div>
                    ))}
                </div>
              )}
            </div>
          )}
        </>
      )}

      {/* Add Modal */}
      {addModal && (
        <AddResModal
          tables={tables}
          shifts={shifts}
          selectedDate={selectedDate}
          selectedShift={selectedShift}
          reservations={reservations}
          onSave={handleSave}
          onClose={() => setAddModal(false)}
        />
      )}

      {/* Edit Modal */}
      {editModal && (
        <EditResModal
          reservation={editModal}
          tables={tables}
          reservations={reservations}
          onSave={handleEdit}
          onClose={() => setEditModal(null)}
        />
      )}

      {/* Detail drawer */}
      {detailRes && (
        <div className="fixed inset-0 z-50 flex items-end md:items-center justify-center p-4 bg-relate-ink/20 backdrop-blur-sm">
          <div className="card-modal w-full max-w-sm p-6">
            <div className="flex items-start justify-between mb-4">
              <div>
                <p className="text-[15px] font-semibold text-relate-ink">
                  {detailRes.customer_name}
                </p>
                <p className="text-[12px] text-relate-graphite">
                  Masa {detailRes.table_number} · {detailRes.party_size} kişi
                </p>
              </div>
              <span className={`badge ${STATUS_BADGE[detailRes.status ?? "confirmed"]}`}>
                {STATUS_LABELS[detailRes.status ?? "confirmed"]}
              </span>
            </div>
            <div className="space-y-2 text-[13px] text-relate-graphite mb-5">
              {detailRes.customer_phone && (
                <p>📞 {detailRes.customer_phone}</p>
              )}
              {detailRes.customer_email && (
                <p>✉️ {detailRes.customer_email}</p>
              )}
              {detailRes.special_requests && (
                <p>💬 {detailRes.special_requests}</p>
              )}
              <p>
                🗓️ {detailRes.date} · {detailRes.shift_name} (
                {detailRes.shift_start}–{detailRes.shift_end})
              </p>
              <p>📡 Kanal: {detailRes.channel}</p>
            </div>
            <div className="flex gap-2">
              <button
                onClick={() => setDetailRes(null)}
                className="btn-outline flex-1"
              >
                Kapat
              </button>
              {detailRes.status === "confirmed" && (
                <button
                  onClick={() => {
                    handleStatusChange(detailRes.id!, "seated");
                    setDetailRes(null);
                  }}
                  className="btn-primary flex-1"
                >
                  Oturt
                </button>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
