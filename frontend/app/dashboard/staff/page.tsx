"use client";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import toast from "react-hot-toast";

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

interface StaffMember {
  id: string;
  name: string;
  email: string;
  phone?: string;
  bio?: string;
  service_names: string[];
  working_schedule: WorkingSchedule;
  google_connected: boolean;
  is_active: boolean;
  created_at: string;
}

const DEFAULT_SCHEDULE: WorkingSchedule = {
  monday: { start: "09:00", end: "18:00", is_open: true },
  tuesday: { start: "09:00", end: "18:00", is_open: true },
  wednesday: { start: "09:00", end: "18:00", is_open: true },
  thursday: { start: "09:00", end: "18:00", is_open: true },
  friday: { start: "09:00", end: "18:00", is_open: true },
  saturday: { start: "09:00", end: "18:00", is_open: false },
  sunday: { start: "09:00", end: "18:00", is_open: false },
};

const DAY_LABELS: Record<string, string> = {
  monday: "Pazartesi",
  tuesday: "Salı",
  wednesday: "Çarşamba",
  thursday: "Perşembe",
  friday: "Cuma",
  saturday: "Cumartesi",
  sunday: "Pazar",
};

const DAY_KEYS = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"] as const;

// ── Schedule Editor ──────────────────────────────────────────────────────────
function ScheduleEditor({
  schedule,
  onChange,
}: {
  schedule: WorkingSchedule;
  onChange: (s: WorkingSchedule) => void;
}) {
  const update = (day: string, field: keyof WorkingHours, value: string | boolean) => {
    onChange({
      ...schedule,
      [day]: { ...schedule[day as keyof WorkingSchedule], [field]: value },
    });
  };

  return (
    <div className="space-y-2">
      {DAY_KEYS.map((day) => {
        const h = schedule[day];
        return (
          <div key={day} className="flex items-center gap-3">
            <label className="flex items-center gap-2 w-28 cursor-pointer">
              <input
                type="checkbox"
                checked={h.is_open}
                onChange={(e) => update(day, "is_open", e.target.checked)}
                className="rounded"
              />
              <span className={`text-sm ${h.is_open ? "text-apple-ink" : "text-apple-secondary"}`}>
                {DAY_LABELS[day]}
              </span>
            </label>
            {h.is_open ? (
              <div className="flex items-center gap-2">
                <input
                  type="time"
                  value={h.start}
                  onChange={(e) => update(day, "start", e.target.value)}
                  className="border border-apple-border rounded-lg px-2 py-1 text-sm"
                />
                <span className="text-apple-secondary text-sm">–</span>
                <input
                  type="time"
                  value={h.end}
                  onChange={(e) => update(day, "end", e.target.value)}
                  className="border border-apple-border rounded-lg px-2 py-1 text-sm"
                />
              </div>
            ) : (
              <span className="text-sm text-apple-secondary italic">Kapalı</span>
            )}
          </div>
        );
      })}
    </div>
  );
}

// ── Staff Card ───────────────────────────────────────────────────────────────
function StaffCard({
  staff,
  businessServices,
  onUpdate,
  onDeactivate,
  onConnectCalendar,
  onDisconnectCalendar,
}: {
  staff: StaffMember;
  businessServices: string[];
  onUpdate: () => void;
  onDeactivate: (id: string) => void;
  onConnectCalendar: (id: string) => void;
  onDisconnectCalendar: (id: string) => void;
}) {
  const [editing, setEditing] = useState(false);
  const [editingSchedule, setEditingSchedule] = useState(false);
  const [form, setForm] = useState({
    name: staff.name,
    phone: staff.phone || "",
    bio: staff.bio || "",
    service_names: staff.service_names,
    is_active: staff.is_active,
  });
  const [schedule, setSchedule] = useState<WorkingSchedule>(staff.working_schedule);
  const [saving, setSaving] = useState(false);

  const toggleService = (svc: string) => {
    setForm((f) => ({
      ...f,
      service_names: f.service_names.includes(svc)
        ? f.service_names.filter((s) => s !== svc)
        : [...f.service_names, svc],
    }));
  };

  const save = async () => {
    setSaving(true);
    try {
      await api.updateStaff(staff.id, {
        name: form.name,
        phone: form.phone || undefined,
        bio: form.bio || undefined,
        service_names: form.service_names,
      });
      toast.success("Personel güncellendi");
      setEditing(false);
      onUpdate();
    } catch {
      toast.error("Güncelleme başarısız");
    } finally {
      setSaving(false);
    }
  };

  const saveSchedule = async () => {
    setSaving(true);
    try {
      await api.updateStaffSchedule(staff.id, schedule as unknown as Record<string, unknown>);
      toast.success("Takvim güncellendi");
      setEditingSchedule(false);
      onUpdate();
    } catch {
      toast.error("Takvim güncellenemedi");
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className={`bg-white rounded-apple-lg border border-apple-border p-5 ${!staff.is_active ? "opacity-60" : ""}`}>
      <div className="flex items-start justify-between gap-4">
        {/* Avatar + info */}
        <div className="flex items-start gap-3">
          <div className="w-10 h-10 rounded-full bg-brand-100 flex items-center justify-center shrink-0">
            <span className="text-brand-600 font-semibold text-sm">
              {staff.name.charAt(0).toUpperCase()}
            </span>
          </div>
          <div>
            <div className="flex items-center gap-2">
              <p className="font-semibold text-apple-ink">{staff.name}</p>
              {!staff.is_active && (
                <span className="text-xs bg-red-100 text-red-600 px-2 py-0.5 rounded-full">Pasif</span>
              )}
              {staff.google_connected && (
                <span className="text-xs bg-blue-50 text-blue-600 px-2 py-0.5 rounded-full">📅 Takvim bağlı</span>
              )}
            </div>
            <p className="text-sm text-apple-secondary">{staff.email}</p>
            {staff.phone && <p className="text-xs text-apple-secondary mt-0.5">{staff.phone}</p>}
            {staff.bio && <p className="text-xs text-apple-secondary italic mt-1">{staff.bio}</p>}
            {staff.service_names.length > 0 && (
              <div className="flex flex-wrap gap-1 mt-2">
                {staff.service_names.map((s) => (
                  <span key={s} className="text-xs bg-brand-50 text-brand-600 px-2 py-0.5 rounded-full border border-brand-200">
                    {s}
                  </span>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Actions */}
        <div className="flex items-center gap-2 shrink-0">
          <button
            onClick={() => { setEditing(!editing); setEditingSchedule(false); }}
            className="text-xs text-apple-secondary hover:text-apple-ink border border-apple-border px-2.5 py-1.5 rounded-lg hover:bg-apple-gray transition-colors"
          >
            {editing ? "İptal" : "Düzenle"}
          </button>
          <button
            onClick={() => { setEditingSchedule(!editingSchedule); setEditing(false); }}
            className="text-xs text-apple-secondary hover:text-apple-ink border border-apple-border px-2.5 py-1.5 rounded-lg hover:bg-apple-gray transition-colors"
          >
            {editingSchedule ? "İptal" : "Takvim"}
          </button>
          {staff.is_active && (
            <button
              onClick={() => onDeactivate(staff.id)}
              className="text-xs text-red-500 hover:text-red-700 border border-red-200 px-2.5 py-1.5 rounded-lg hover:bg-red-50 transition-colors"
            >
              Deaktif
            </button>
          )}
        </div>
      </div>

      {/* Edit form */}
      {editing && (
        <div className="mt-4 pt-4 border-t border-apple-border space-y-3">
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="text-xs text-apple-secondary mb-1 block">İsim</label>
              <input
                className="input-field w-full"
                value={form.name}
                onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))}
              />
            </div>
            <div>
              <label className="text-xs text-apple-secondary mb-1 block">Telefon</label>
              <input
                className="input-field w-full"
                value={form.phone}
                onChange={(e) => setForm((f) => ({ ...f, phone: e.target.value }))}
              />
            </div>
          </div>
          <div>
            <label className="text-xs text-apple-secondary mb-1 block">Biyografi</label>
            <textarea
              className="input-field w-full resize-none"
              rows={2}
              value={form.bio}
              onChange={(e) => setForm((f) => ({ ...f, bio: e.target.value }))}
            />
          </div>
          {businessServices.length > 0 && (
            <div>
              <label className="text-xs text-apple-secondary mb-2 block">Sunduğu Hizmetler</label>
              <div className="flex flex-wrap gap-2">
                {businessServices.map((svc) => (
                  <button
                    key={svc}
                    type="button"
                    onClick={() => toggleService(svc)}
                    className={`text-xs px-3 py-1.5 rounded-full border transition-colors ${
                      form.service_names.includes(svc)
                        ? "bg-brand-600 text-white border-brand-600"
                        : "text-apple-secondary border-apple-border hover:bg-apple-gray"
                    }`}
                  >
                    {svc}
                  </button>
                ))}
              </div>
            </div>
          )}
          {/* Google Calendar */}
          <div className="flex items-center gap-2 pt-1">
            <span className="text-xs text-apple-secondary">Google Calendar:</span>
            {staff.google_connected ? (
              <button
                onClick={() => onDisconnectCalendar(staff.id)}
                className="text-xs text-red-500 hover:underline"
              >
                Bağlantıyı kes
              </button>
            ) : (
              <button
                onClick={() => onConnectCalendar(staff.id)}
                className="text-xs text-apple-blue hover:underline"
              >
                Bağla
              </button>
            )}
          </div>
          <button
            onClick={save}
            disabled={saving}
            className="btn-primary text-sm px-4 py-2"
          >
            {saving ? "Kaydediliyor..." : "Kaydet"}
          </button>
        </div>
      )}

      {/* Schedule editor */}
      {editingSchedule && (
        <div className="mt-4 pt-4 border-t border-apple-border">
          <h4 className="text-sm font-medium text-apple-ink mb-3">Çalışma Saatleri</h4>
          <ScheduleEditor schedule={schedule} onChange={setSchedule} />
          <button
            onClick={saveSchedule}
            disabled={saving}
            className="btn-primary text-sm px-4 py-2 mt-4"
          >
            {saving ? "Kaydediliyor..." : "Takvimi Kaydet"}
          </button>
        </div>
      )}
    </div>
  );
}

// ── Main Page ────────────────────────────────────────────────────────────────
export default function StaffPage() {
  const [staff, setStaff] = useState<StaffMember[]>([]);
  const [businessServices, setBusinessServices] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [showAdd, setShowAdd] = useState(false);
  const [adding, setAdding] = useState(false);
  const [form, setForm] = useState({
    name: "",
    email: "",
    password: "",
    phone: "",
    bio: "",
    service_names: [] as string[],
  });
  const [schedule, setSchedule] = useState<WorkingSchedule>(DEFAULT_SCHEDULE);

  const load = async () => {
    setLoading(true);
    try {
      const [staffData, profile] = await Promise.all([api.getStaff(), api.getProfile()]);
      setStaff(staffData);
      setBusinessServices((profile.services || []).map((s: { name: string }) => s.name));
    } catch {
      toast.error("Veriler yüklenemedi");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, []);

  const handleAdd = async () => {
    if (!form.name || !form.email || !form.password) {
      toast.error("İsim, e-posta ve şifre zorunludur");
      return;
    }
    setAdding(true);
    try {
      await api.createStaff({
        name: form.name,
        email: form.email,
        password: form.password,
        phone: form.phone || undefined,
        bio: form.bio || undefined,
        service_names: form.service_names,
        working_schedule: schedule as unknown as Record<string, unknown>,
      });
      toast.success("Personel eklendi");
      setShowAdd(false);
      setForm({ name: "", email: "", password: "", phone: "", bio: "", service_names: [] });
      setSchedule(DEFAULT_SCHEDULE);
      load();
    } catch (e: unknown) {
      const msg = (e as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
      toast.error(msg || "Ekleme başarısız");
    } finally {
      setAdding(false);
    }
  };

  const handleDeactivate = async (id: string) => {
    if (!confirm("Bu personeli deaktif etmek istediğinizden emin misiniz?")) return;
    try {
      await api.deactivateStaff(id);
      toast.success("Personel deaktif edildi");
      load();
    } catch {
      toast.error("İşlem başarısız");
    }
  };

  const handleConnectCalendar = async (id: string) => {
    try {
      const data = await api.connectStaffGoogle(id);
      window.open(data.auth_url, "_blank");
    } catch {
      toast.error("Google Calendar bağlanamadı");
    }
  };

  const handleDisconnectCalendar = async (id: string) => {
    try {
      await api.disconnectStaffGoogle(id);
      toast.success("Bağlantı kaldırıldı");
      load();
    } catch {
      toast.error("İşlem başarısız");
    }
  };

  const toggleFormService = (svc: string) => {
    setForm((f) => ({
      ...f,
      service_names: f.service_names.includes(svc)
        ? f.service_names.filter((s) => s !== svc)
        : [...f.service_names, svc],
    }));
  };

  const activeStaff = staff.filter((s) => s.is_active);
  const inactiveStaff = staff.filter((s) => !s.is_active);

  return (
    <div className="p-8">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Personel</h2>
          <p className="text-gray-500 text-sm mt-1">
            {activeStaff.length} aktif personel
          </p>
        </div>
        <button
          onClick={() => setShowAdd(!showAdd)}
          className="btn-primary text-sm px-4 py-2"
        >
          {showAdd ? "İptal" : "+ Personel Ekle"}
        </button>
      </div>

      {/* Add form */}
      {showAdd && (
        <div className="bg-white rounded-apple-lg border border-apple-border p-6 mb-6">
          <h3 className="font-semibold text-apple-ink mb-4">Yeni Personel</h3>
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="text-xs text-apple-secondary mb-1 block">İsim *</label>
                <input
                  className="input-field w-full"
                  placeholder="Ad Soyad"
                  value={form.name}
                  onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))}
                />
              </div>
              <div>
                <label className="text-xs text-apple-secondary mb-1 block">E-posta *</label>
                <input
                  type="email"
                  className="input-field w-full"
                  placeholder="personel@ornek.com"
                  value={form.email}
                  onChange={(e) => setForm((f) => ({ ...f, email: e.target.value }))}
                />
              </div>
              <div>
                <label className="text-xs text-apple-secondary mb-1 block">Şifre *</label>
                <input
                  type="password"
                  className="input-field w-full"
                  placeholder="En az 6 karakter"
                  value={form.password}
                  onChange={(e) => setForm((f) => ({ ...f, password: e.target.value }))}
                />
              </div>
              <div>
                <label className="text-xs text-apple-secondary mb-1 block">Telefon</label>
                <input
                  className="input-field w-full"
                  placeholder="05XX XXX XX XX"
                  value={form.phone}
                  onChange={(e) => setForm((f) => ({ ...f, phone: e.target.value }))}
                />
              </div>
            </div>
            <div>
              <label className="text-xs text-apple-secondary mb-1 block">Biyografi</label>
              <textarea
                className="input-field w-full resize-none"
                rows={2}
                placeholder="Kısa tanıtım..."
                value={form.bio}
                onChange={(e) => setForm((f) => ({ ...f, bio: e.target.value }))}
              />
            </div>
            {businessServices.length > 0 && (
              <div>
                <label className="text-xs text-apple-secondary mb-2 block">Sunduğu Hizmetler</label>
                <div className="flex flex-wrap gap-2">
                  {businessServices.map((svc) => (
                    <button
                      key={svc}
                      type="button"
                      onClick={() => toggleFormService(svc)}
                      className={`text-xs px-3 py-1.5 rounded-full border transition-colors ${
                        form.service_names.includes(svc)
                          ? "bg-brand-600 text-white border-brand-600"
                          : "text-apple-secondary border-apple-border hover:bg-apple-gray"
                      }`}
                    >
                      {svc}
                    </button>
                  ))}
                </div>
              </div>
            )}
            <div>
              <label className="text-xs text-apple-secondary mb-2 block">Çalışma Saatleri</label>
              <ScheduleEditor schedule={schedule} onChange={setSchedule} />
            </div>
            <button
              onClick={handleAdd}
              disabled={adding}
              className="btn-primary text-sm px-5 py-2"
            >
              {adding ? "Ekleniyor..." : "Personel Ekle"}
            </button>
          </div>
        </div>
      )}

      {loading ? (
        <div className="text-center py-20 text-gray-400">Yükleniyor...</div>
      ) : staff.length === 0 ? (
        <div className="text-center py-20">
          <p className="text-gray-400 mb-2">Henüz personel eklenmemiş.</p>
          <p className="text-sm text-gray-400">
            "+ Personel Ekle" butonuna tıklayarak başlayın.
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {activeStaff.map((s) => (
            <StaffCard
              key={s.id}
              staff={s}
              businessServices={businessServices}
              onUpdate={load}
              onDeactivate={handleDeactivate}
              onConnectCalendar={handleConnectCalendar}
              onDisconnectCalendar={handleDisconnectCalendar}
            />
          ))}
          {inactiveStaff.length > 0 && (
            <div className="mt-6">
              <h3 className="text-sm font-medium text-apple-secondary mb-3">Pasif Personel</h3>
              <div className="space-y-3">
                {inactiveStaff.map((s) => (
                  <StaffCard
                    key={s.id}
                    staff={s}
                    businessServices={businessServices}
                    onUpdate={load}
                    onDeactivate={handleDeactivate}
                    onConnectCalendar={handleConnectCalendar}
                    onDisconnectCalendar={handleDisconnectCalendar}
                  />
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
