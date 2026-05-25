"use client";

import { useEffect, useRef, useState } from "react";
import { api, RestaurantTable, DiningShift } from "@/lib/api";
import toast from "react-hot-toast";
import { SelectField } from "@/components/ui/SelectField";

type Tab = "list" | "floor" | "shifts" | "config";

interface RestaurantConfig {
  enabled: boolean;
  reservation_duration: number;
  max_party_size: number;
  reservation_window_days: number;
  tables: RestaurantTable[];
  shifts: DiningShift[];
}

const SHAPES = ["rect", "round"] as const;
const SECTIONS = ["iç", "dış", "vip", "teras", "bar"];

const DAYS_TR: Record<string, string> = {
  monday: "Pzt",
  tuesday: "Sal",
  wednesday: "Çar",
  thursday: "Per",
  friday: "Cum",
  saturday: "Cmt",
  sunday: "Paz",
};
const ALL_DAYS = Object.keys(DAYS_TR);

// ------ Table Modal ------

function TableModal({
  initial,
  onSave,
  onClose,
}: {
  initial?: Partial<RestaurantTable>;
  onSave: (d: Partial<RestaurantTable>) => Promise<void>;
  onClose: () => void;
}) {
  const [form, setForm] = useState<Partial<RestaurantTable>>({
    number: 1,
    name: "",
    capacity: 4,
    section: "iç",
    shape: "rect",
    is_active: true,
    ...initial,
  });
  const [saving, setSaving] = useState(false);

  const set = (k: keyof RestaurantTable, v: unknown) =>
    setForm((f) => ({ ...f, [k]: v }));

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
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-relate-ink/20 backdrop-blur-sm">
      <div className="card-modal w-full max-w-md p-6">
        <h3 className="text-[15px] font-semibold text-relate-ink mb-5">
          {initial?.id ? "Masa Düzenle" : "Yeni Masa"}
        </h3>
        <form onSubmit={submit} className="space-y-4">
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-[12px] text-relate-graphite mb-1">
                Masa No
              </label>
              <input
                type="number"
                min={1}
                required
                className="input-field w-full"
                value={form.number ?? ""}
                onChange={(e) => set("number", parseInt(e.target.value))}
              />
            </div>
            <div>
              <label className="block text-[12px] text-relate-graphite mb-1">
                Kapasite
              </label>
              <input
                type="number"
                min={1}
                max={50}
                required
                className="input-field w-full"
                value={form.capacity ?? ""}
                onChange={(e) => set("capacity", parseInt(e.target.value))}
              />
            </div>
          </div>
          <div>
            <label className="block text-[12px] text-relate-graphite mb-1">
              İsim (isteğe bağlı)
            </label>
            <input
              type="text"
              className="input-field w-full"
              placeholder="ör. Pencere Kenarı"
              value={form.name ?? ""}
              onChange={(e) => set("name", e.target.value)}
            />
          </div>
          <div className="grid grid-cols-2 gap-3">
            <SelectField
              label="Bölüm"
              value={form.section ?? "iç"}
              options={SECTIONS.map((s) => ({ value: s, label: s }))}
              onChange={(v) => set("section", v)}
            />
            <SelectField
              label="Şekil"
              value={form.shape ?? "rect"}
              options={SHAPES.map((s) => ({ value: s, label: s === "rect" ? "Dikdörtgen" : "Yuvarlak" }))}
              onChange={(v) => set("shape", v)}
            />
          </div>
          <label className="flex items-center gap-2 cursor-pointer select-none">
            <input
              type="checkbox"
              className="w-4 h-4 rounded accent-relate-signal"
              checked={form.is_active ?? true}
              onChange={(e) => set("is_active", e.target.checked)}
            />
            <span className="text-[13px] text-relate-ink">Aktif</span>
          </label>

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

// ------ Shift Modal ------

function ShiftModal({
  initial,
  onSave,
  onClose,
}: {
  initial?: Partial<DiningShift>;
  onSave: (d: Partial<DiningShift>) => Promise<void>;
  onClose: () => void;
}) {
  const [form, setForm] = useState<Partial<DiningShift>>({
    name: "",
    start_time: "12:00",
    end_time: "15:00",
    is_active: true,
    days: [...ALL_DAYS],
    ...initial,
  });
  const [saving, setSaving] = useState(false);

  const set = (k: keyof DiningShift, v: unknown) =>
    setForm((f) => ({ ...f, [k]: v }));

  const toggleDay = (d: string) => {
    const days = form.days ?? [];
    set("days", days.includes(d) ? days.filter((x) => x !== d) : [...days, d]);
  };

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
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-relate-ink/20 backdrop-blur-sm">
      <div className="card-modal w-full max-w-md p-6">
        <h3 className="text-[15px] font-semibold text-relate-ink mb-5">
          {initial?.id ? "Vardiyayı Düzenle" : "Yeni Vardiya"}
        </h3>
        <form onSubmit={submit} className="space-y-4">
          <div>
            <label className="block text-[12px] text-relate-graphite mb-1">
              Vardiya Adı
            </label>
            <input
              type="text"
              required
              className="input-field w-full"
              placeholder="ör. Öğle, Akşam"
              value={form.name ?? ""}
              onChange={(e) => set("name", e.target.value)}
            />
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-[12px] text-relate-graphite mb-1">
                Başlangıç
              </label>
              <input
                type="time"
                required
                className="input-field w-full"
                value={form.start_time ?? ""}
                onChange={(e) => set("start_time", e.target.value)}
              />
            </div>
            <div>
              <label className="block text-[12px] text-relate-graphite mb-1">
                Bitiş
              </label>
              <input
                type="time"
                required
                className="input-field w-full"
                value={form.end_time ?? ""}
                onChange={(e) => set("end_time", e.target.value)}
              />
            </div>
          </div>
          <div>
            <label className="block text-[12px] text-relate-graphite mb-2">
              Günler
            </label>
            <div className="flex flex-wrap gap-1.5">
              {ALL_DAYS.map((d) => (
                <button
                  key={d}
                  type="button"
                  onClick={() => toggleDay(d)}
                  className={`px-2.5 py-1 rounded-md text-[12px] font-medium border transition-colors ${
                    (form.days ?? []).includes(d)
                      ? "bg-relate-signal/10 border-relate-signal/30 text-relate-signal"
                      : "bg-relate-wash border-relate-border text-relate-graphite"
                  }`}
                >
                  {DAYS_TR[d]}
                </button>
              ))}
            </div>
          </div>
          <label className="flex items-center gap-2 cursor-pointer select-none">
            <input
              type="checkbox"
              className="w-4 h-4 rounded accent-relate-signal"
              checked={form.is_active ?? true}
              onChange={(e) => set("is_active", e.target.checked)}
            />
            <span className="text-[13px] text-relate-ink">Aktif</span>
          </label>
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

// ------ Floor Plan Editor ------

function FloorPlanEditor({
  tables,
  onChange,
}: {
  tables: RestaurantTable[];
  onChange: (tables: RestaurantTable[]) => void;
}) {
  const canvasRef = useRef<HTMLDivElement>(null);
  const dragging = useRef<{
    id: string;
    startX: number;
    startY: number;
    origX: number;
    origY: number;
  } | null>(null);
  const [localTables, setLocalTables] = useState(tables);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    setLocalTables(tables);
  }, [tables]);

  const onMouseDown = (
    e: React.MouseEvent,
    table: RestaurantTable
  ) => {
    e.preventDefault();
    const rect = canvasRef.current!.getBoundingClientRect();
    dragging.current = {
      id: table.id!,
      startX: e.clientX,
      startY: e.clientY,
      origX: ((table.x ?? 10) / 100) * rect.width,
      origY: ((table.y ?? 10) / 100) * rect.height,
    };
  };

  const onMouseMove = (e: React.MouseEvent) => {
    if (!dragging.current || !canvasRef.current) return;
    const rect = canvasRef.current.getBoundingClientRect();
    const dx = e.clientX - dragging.current.startX;
    const dy = e.clientY - dragging.current.startY;
    const newXpx = Math.max(0, Math.min(rect.width - 64, dragging.current.origX + dx));
    const newYpx = Math.max(0, Math.min(rect.height - 40, dragging.current.origY + dy));
    const newX = Math.round((newXpx / rect.width) * 100);
    const newY = Math.round((newYpx / rect.height) * 100);
    setLocalTables((prev) =>
      prev.map((t) =>
        t.id === dragging.current!.id ? { ...t, x: newX, y: newY } : t
      )
    );
  };

  const onMouseUp = () => {
    dragging.current = null;
  };

  const saveLayout = async () => {
    setSaving(true);
    try {
      const payload = localTables.map((t) => ({
        id: t.id,
        x: t.x ?? 10,
        y: t.y ?? 10,
      }));
      await api.saveTableLayout(payload);
      onChange(localTables);
      toast.success("Plan kaydedildi");
    } catch {
      toast.error("Kaydedilemedi");
    } finally {
      setSaving(false);
    }
  };

  const sectionColor: Record<string, string> = {
    iç: "bg-azure/10 border-azure/30 text-azure-700",
    dış: "bg-emerald-50 border-emerald-200 text-emerald-700",
    vip: "bg-amber-50 border-amber-200 text-amber-700",
    teras: "bg-relate-signal/10 border-relate-signal/30 text-relate-signal",
    bar: "bg-coral/10 border-coral/30 text-coral-700",
  };

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <p className="text-[13px] text-relate-graphite">
          Masaları sürükleyerek konumlandırın
        </p>
        <button
          onClick={saveLayout}
          disabled={saving}
          className="btn-primary text-[13px] px-4 py-2"
        >
          {saving ? "Kaydediliyor…" : "Planı Kaydet"}
        </button>
      </div>
      <div
        ref={canvasRef}
        className="relative w-full bg-relate-wash border border-relate-border rounded-xl overflow-hidden select-none"
        style={{ height: 480 }}
        onMouseMove={onMouseMove}
        onMouseUp={onMouseUp}
        onMouseLeave={onMouseUp}
      >
        {/* Grid lines */}
        <svg
          className="absolute inset-0 w-full h-full pointer-events-none opacity-30"
          xmlns="http://www.w3.org/2000/svg"
        >
          <defs>
            <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
              <path d="M 40 0 L 0 0 0 40" fill="none" stroke="#cfcfcf" strokeWidth="0.5" />
            </pattern>
          </defs>
          <rect width="100%" height="100%" fill="url(#grid)" />
        </svg>

        {localTables.map((t) => {
          const xPct = t.x ?? 10;
          const yPct = t.y ?? 10;
          const isRound = t.shape === "round";
          const colorClass =
            sectionColor[t.section ?? "iç"] ??
            "bg-relate-card border-relate-border text-relate-ink";

          return (
            <div
              key={t.id}
              className={`absolute flex flex-col items-center justify-center border cursor-grab active:cursor-grabbing shadow-relate-sm text-[11px] font-medium transition-shadow hover:shadow-relate-md ${colorClass} ${
                isRound ? "rounded-full" : "rounded-lg"
              } ${t.is_active ? "" : "opacity-40"}`}
              style={{
                left: `${xPct}%`,
                top: `${yPct}%`,
                width: isRound ? 56 : 72,
                height: isRound ? 56 : 44,
              }}
              onMouseDown={(e) => onMouseDown(e, t)}
            >
              <span className="font-semibold leading-none">#{t.number}</span>
              <span className="leading-none mt-0.5 opacity-70">{t.capacity}k</span>
            </div>
          );
        })}
        {localTables.length === 0 && (
          <div className="absolute inset-0 flex items-center justify-center text-[13px] text-relate-graphite">
            Henüz masa eklenmedi
          </div>
        )}
      </div>
      <div className="flex flex-wrap gap-3 text-[12px] text-relate-graphite">
        {Object.entries(sectionColor).map(([sec, cls]) => (
          <span
            key={sec}
            className={`px-2 py-0.5 rounded border ${cls}`}
          >
            {sec}
          </span>
        ))}
      </div>
    </div>
  );
}

// ------ Main Page ------

export default function TablesPage() {
  const [tab, setTab] = useState<Tab>("list");
  const [config, setConfig] = useState<RestaurantConfig | null>(null);
  const [loading, setLoading] = useState(true);

  // Modals
  const [tableModal, setTableModal] = useState<{
    open: boolean;
    data?: Partial<RestaurantTable>;
  }>({ open: false });
  const [shiftModal, setShiftModal] = useState<{
    open: boolean;
    data?: Partial<DiningShift>;
  }>({ open: false });

  // Config form
  const [cfgForm, setCfgForm] = useState({
    enabled: false,
    reservation_duration: 90,
    max_party_size: 20,
    reservation_window_days: 30,
  });
  const [cfgSaving, setCfgSaving] = useState(false);

  const load = async () => {
    setLoading(true);
    try {
      const [cfg, tables, shifts] = await Promise.all([
        api.getRestaurantConfig(),
        api.getTables(),
        api.getShifts(),
      ]);
      const full: RestaurantConfig = { ...cfg, tables, shifts };
      setConfig(full);
      setCfgForm({
        enabled: cfg.enabled ?? false,
        reservation_duration: cfg.reservation_duration ?? 90,
        max_party_size: cfg.max_party_size ?? 20,
        reservation_window_days: cfg.reservation_window_days ?? 30,
      });
    } catch {
      toast.error("Veriler yüklenemedi");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  // ---- Table CRUD ----
  const handleSaveTable = async (data: Partial<RestaurantTable>) => {
    try {
      if (data.id) {
        await api.updateTable(data.id, data);
        toast.success("Masa güncellendi");
      } else {
        await api.createTable(data);
        toast.success("Masa eklendi");
      }
      setTableModal({ open: false });
      await load();
    } catch {
      toast.error("İşlem başarısız");
    }
  };

  const handleDeleteTable = async (id: string) => {
    if (!confirm("Bu masayı silmek istediğinizden emin misiniz?")) return;
    try {
      await api.deleteTable(id);
      toast.success("Masa silindi");
      await load();
    } catch {
      toast.error("Silinemedi");
    }
  };

  // ---- Shift CRUD ----
  const handleSaveShift = async (data: Partial<DiningShift>) => {
    try {
      if (data.id) {
        await api.updateShift(data.id, data);
        toast.success("Vardiya güncellendi");
      } else {
        await api.createShift(data);
        toast.success("Vardiya eklendi");
      }
      setShiftModal({ open: false });
      await load();
    } catch {
      toast.error("İşlem başarısız");
    }
  };

  const handleDeleteShift = async (id: string) => {
    if (!confirm("Bu vardiyayı silmek istediğinizden emin misiniz?")) return;
    try {
      await api.deleteShift(id);
      toast.success("Vardiya silindi");
      await load();
    } catch {
      toast.error("Silinemedi");
    }
  };

  // ---- Config save ----
  const saveConfig = async () => {
    setCfgSaving(true);
    try {
      await api.updateRestaurantConfig(cfgForm);
      toast.success("Ayarlar kaydedildi");
      await load();
    } catch {
      toast.error("Kaydedilemedi");
    } finally {
      setCfgSaving(false);
    }
  };

  const TABS: { id: Tab; label: string }[] = [
    { id: "list", label: "Masa Listesi" },
    { id: "floor", label: "Yer Planı" },
    { id: "shifts", label: "Vardiyalar" },
    { id: "config", label: "Ayarlar" },
  ];

  if (loading) {
    return (
      <div className="p-6 md:p-8 max-w-5xl mx-auto">
        <div className="h-8 w-48 bg-relate-rule rounded animate-pulse mb-6" />
        <div className="h-64 bg-relate-rule rounded-xl animate-pulse" />
      </div>
    );
  }

  const tables = config?.tables ?? [];
  const shifts = config?.shifts ?? [];

  return (
    <div className="p-6 md:p-8 max-w-5xl mx-auto space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-[22px] font-semibold text-relate-ink tracking-tight">
          Masa Yönetimi
        </h1>
        <p className="text-[13px] text-relate-graphite mt-0.5">
          Masaları, yer planını ve vardiyaları yönetin
        </p>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 bg-relate-wash border border-relate-border rounded-xl p-1 w-fit">
        {TABS.map((t) => (
          <button
            key={t.id}
            onClick={() => setTab(t.id)}
            className={`px-4 py-1.5 rounded-lg text-[13px] font-medium transition-colors ${
              tab === t.id
                ? "bg-relate-signal/15 text-relate-signal border border-relate-signal/30"
                : "text-relate-graphite hover:text-relate-ink"
            }`}
          >
            {t.label}
          </button>
        ))}
      </div>

      {/* ---- List Tab ---- */}
      {tab === "list" && (
        <div className="card p-6 space-y-4">
          <div className="flex items-center justify-between">
            <p className="text-[14px] font-medium text-relate-ink">
              {tables.length} masa
            </p>
            <button
              onClick={() => setTableModal({ open: true })}
              className="btn-primary text-[13px] px-4 py-2"
            >
              + Masa Ekle
            </button>
          </div>

          {tables.length === 0 ? (
            <div className="py-12 text-center text-[13px] text-relate-graphite">
              Henüz masa eklenmedi
            </div>
          ) : (
            <div className="divide-y divide-relate-rule">
              {tables
                .slice()
                .sort((a, b) => (a.number ?? 0) - (b.number ?? 0))
                .map((t) => (
                  <div
                    key={t.id}
                    className="flex items-center justify-between py-3"
                  >
                    <div className="flex items-center gap-3">
                      <div
                        className={`w-9 h-9 flex items-center justify-center text-[12px] font-semibold border ${
                          t.shape === "round" ? "rounded-full" : "rounded-lg"
                        } ${
                          t.is_active
                            ? "bg-relate-signal/10 border-relate-signal/30 text-relate-signal"
                            : "bg-relate-wash border-relate-border text-relate-graphite"
                        }`}
                      >
                        {t.number}
                      </div>
                      <div>
                        <p className="text-[13px] font-medium text-relate-ink">
                          {t.name ? `${t.name} (${t.number})` : `Masa ${t.number}`}
                        </p>
                        <p className="text-[12px] text-relate-graphite">
                          {t.section} · {t.capacity} kişilik ·{" "}
                          {t.shape === "round" ? "Yuvarlak" : "Dikdörtgen"}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <span
                        className={`badge ${t.is_active ? "badge-emerald" : "badge-coral"}`}
                      >
                        {t.is_active ? "Aktif" : "Pasif"}
                      </span>
                      <button
                        onClick={() =>
                          setTableModal({ open: true, data: t })
                        }
                        className="text-[12px] text-relate-graphite hover:text-relate-ink px-2 py-1 rounded hover:bg-relate-wash transition-colors"
                      >
                        Düzenle
                      </button>
                      <button
                        onClick={() => handleDeleteTable(t.id!)}
                        className="text-[12px] text-coral-600 hover:text-coral-700 px-2 py-1 rounded hover:bg-coral/5 transition-colors"
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

      {/* ---- Floor Plan Tab ---- */}
      {tab === "floor" && (
        <div className="card p-6">
          <FloorPlanEditor
            tables={tables}
            onChange={(updated) =>
              setConfig((c) => (c ? { ...c, tables: updated } : c))
            }
          />
        </div>
      )}

      {/* ---- Shifts Tab ---- */}
      {tab === "shifts" && (
        <div className="card p-6 space-y-4">
          <div className="flex items-center justify-between">
            <p className="text-[14px] font-medium text-relate-ink">
              {shifts.length} vardiya
            </p>
            <button
              onClick={() => setShiftModal({ open: true })}
              className="btn-primary text-[13px] px-4 py-2"
            >
              + Vardiya Ekle
            </button>
          </div>

          {shifts.length === 0 ? (
            <div className="py-12 text-center text-[13px] text-relate-graphite">
              Henüz vardiya eklenmedi
            </div>
          ) : (
            <div className="divide-y divide-relate-rule">
              {shifts.map((s) => (
                <div
                  key={s.id}
                  className="flex items-center justify-between py-3"
                >
                  <div>
                    <p className="text-[13px] font-medium text-relate-ink">
                      {s.name}
                    </p>
                    <p className="text-[12px] text-relate-graphite">
                      {s.start_time} – {s.end_time} ·{" "}
                      {(s.days ?? []).map((d) => DAYS_TR[d]).join(", ")}
                    </p>
                  </div>
                  <div className="flex items-center gap-2">
                    <span
                      className={`badge ${s.is_active ? "badge-emerald" : "badge-coral"}`}
                    >
                      {s.is_active ? "Aktif" : "Pasif"}
                    </span>
                    <button
                      onClick={() => setShiftModal({ open: true, data: s })}
                      className="text-[12px] text-relate-graphite hover:text-relate-ink px-2 py-1 rounded hover:bg-relate-wash transition-colors"
                    >
                      Düzenle
                    </button>
                    <button
                      onClick={() => handleDeleteShift(s.id!)}
                      className="text-[12px] text-coral-600 hover:text-coral-700 px-2 py-1 rounded hover:bg-coral/5 transition-colors"
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

      {/* ---- Config Tab ---- */}
      {tab === "config" && (
        <div className="card p-6 space-y-5 max-w-lg">
          <label className="flex items-center justify-between cursor-pointer">
            <div>
              <p className="text-[14px] font-medium text-relate-ink">
                Rezervasyon Sistemi
              </p>
              <p className="text-[12px] text-relate-graphite mt-0.5">
                AI asistan üzerinden rezervasyon alınabilsin
              </p>
            </div>
            <input
              type="checkbox"
              className="w-5 h-5 accent-relate-signal"
              checked={cfgForm.enabled}
              onChange={(e) =>
                setCfgForm((f) => ({ ...f, enabled: e.target.checked }))
              }
            />
          </label>

          <div>
            <label className="block text-[12px] text-relate-graphite mb-1">
              Rezervasyon Süresi (dakika)
            </label>
            <input
              type="number"
              min={30}
              max={360}
              step={15}
              className="input-field w-full"
              value={cfgForm.reservation_duration}
              onChange={(e) =>
                setCfgForm((f) => ({
                  ...f,
                  reservation_duration: parseInt(e.target.value),
                }))
              }
            />
          </div>

          <div>
            <label className="block text-[12px] text-relate-graphite mb-1">
              Maksimum Kişi Sayısı
            </label>
            <input
              type="number"
              min={1}
              max={100}
              className="input-field w-full"
              value={cfgForm.max_party_size}
              onChange={(e) =>
                setCfgForm((f) => ({
                  ...f,
                  max_party_size: parseInt(e.target.value),
                }))
              }
            />
          </div>

          <div>
            <label className="block text-[12px] text-relate-graphite mb-1">
              Rezervasyon Penceresi (gün)
            </label>
            <input
              type="number"
              min={1}
              max={365}
              className="input-field w-full"
              value={cfgForm.reservation_window_days}
              onChange={(e) =>
                setCfgForm((f) => ({
                  ...f,
                  reservation_window_days: parseInt(e.target.value),
                }))
              }
            />
          </div>

          <button
            onClick={saveConfig}
            disabled={cfgSaving}
            className="btn-primary w-full"
          >
            {cfgSaving ? "Kaydediliyor…" : "Ayarları Kaydet"}
          </button>
        </div>
      )}

      {/* Modals */}
      {tableModal.open && (
        <TableModal
          initial={tableModal.data}
          onSave={handleSaveTable}
          onClose={() => setTableModal({ open: false })}
        />
      )}
      {shiftModal.open && (
        <ShiftModal
          initial={shiftModal.data}
          onSave={handleSaveShift}
          onClose={() => setShiftModal({ open: false })}
        />
      )}
    </div>
  );
}
