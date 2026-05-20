"use client";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import toast from "react-hot-toast";

interface Appointment {
  id: string;
  customer_name: string;
  customer_phone: string;
  customer_email?: string;
  service_name: string;
  start_time: string;
  status: string;
}

interface Customer {
  phone: string;
  name: string;
  email?: string;
  appointments: Appointment[];
  totalCount: number;
  lastVisit: string;
}

interface MemoryRecord {
  id: string;
  name: string;
  memory_summary: string | null;
  tags: string[];
  preferences: {
    preferred_staff: string | null;
    preferred_times: string | null;
    favorite_services: string[];
    allergies: string | null;
    notes: string | null;
  };
  total_conversations: number;
  last_summary_at: string | null;
}

export default function CustomersPage() {
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [selected, setSelected] = useState<Customer | null>(null);
  const [memoryByPhone, setMemoryByPhone] = useState<Record<string, MemoryRecord | null>>({});
  const [editingPhone, setEditingPhone] = useState<string | null>(null);
  const [editForm, setEditForm] = useState<{
    memory_summary: string;
    tags: string;
    preferred_staff: string;
    preferred_times: string;
    allergies: string;
    notes: string;
  } | null>(null);

  useEffect(() => {
    api.getAppointments().then((appts: Appointment[]) => {
      // Group by phone
      const map = new Map<string, Customer>();
      for (const a of appts) {
        if (!map.has(a.customer_phone)) {
          map.set(a.customer_phone, {
            phone: a.customer_phone,
            name: a.customer_name,
            email: a.customer_email,
            appointments: [],
            totalCount: 0,
            lastVisit: a.start_time,
          });
        }
        const c = map.get(a.customer_phone)!;
        c.appointments.push(a);
        c.totalCount++;
        if (new Date(a.start_time) > new Date(c.lastVisit)) {
          c.lastVisit = a.start_time;
        }
      }
      setCustomers(
        Array.from(map.values()).sort(
          (a, b) =>
            new Date(b.lastVisit).getTime() - new Date(a.lastVisit).getTime(),
        ),
      );
      setLoading(false);
    });
  }, []);

  const filtered = customers.filter(
    (c) =>
      c.name.toLowerCase().includes(search.toLowerCase()) ||
      c.phone.includes(search) ||
      (c.email ?? "").toLowerCase().includes(search.toLowerCase()),
  );

  const toggleSelect = async (c: Customer) => {
    if (selected?.phone === c.phone) {
      setSelected(null);
      setEditingPhone(null);
      return;
    }
    setSelected(c);
    setEditingPhone(null);
    if (memoryByPhone[c.phone] === undefined) {
      try {
        const data = await api.getCustomerByPhone(c.phone);
        setMemoryByPhone((m) => ({ ...m, [c.phone]: data.customer }));
      } catch {
        setMemoryByPhone((m) => ({ ...m, [c.phone]: null }));
      }
    }
  };

  const startEdit = (rec: MemoryRecord) => {
    setEditingPhone(selected?.phone || null);
    setEditForm({
      memory_summary: rec.memory_summary || "",
      tags: (rec.tags || []).join(", "),
      preferred_staff: rec.preferences.preferred_staff || "",
      preferred_times: rec.preferences.preferred_times || "",
      allergies: rec.preferences.allergies || "",
      notes: rec.preferences.notes || "",
    });
  };

  const saveEdit = async (rec: MemoryRecord) => {
    if (!editForm) return;
    try {
      const updated = await api.updateCustomer(rec.id, {
        memory_summary: editForm.memory_summary.trim() || null,
        tags: editForm.tags
          .split(",")
          .map((t) => t.trim())
          .filter(Boolean),
        preferences: {
          preferred_staff: editForm.preferred_staff.trim() || null,
          preferred_times: editForm.preferred_times.trim() || null,
          favorite_services: rec.preferences.favorite_services || [],
          allergies: editForm.allergies.trim() || null,
          notes: editForm.notes.trim() || null,
        },
      });
      setMemoryByPhone((m) => ({
        ...m,
        [selected!.phone]: { ...rec, ...updated },
      }));
      setEditingPhone(null);
      toast.success("Hafıza güncellendi");
    } catch {
      toast.error("Kayıt başarısız");
    }
  };

  const resetMemory = async (rec: MemoryRecord) => {
    if (!confirm("Bu müşterinin AI hafızasını sıfırlamak istediğinize emin misiniz?")) return;
    try {
      await api.resetCustomerMemory(rec.id);
      setMemoryByPhone((m) => ({
        ...m,
        [selected!.phone]: {
          ...rec,
          memory_summary: null,
          tags: [],
          preferences: {
            preferred_staff: null,
            preferred_times: null,
            favorite_services: [],
            allergies: null,
            notes: null,
          },
        },
      }));
      setEditingPhone(null);
      toast.success("Hafıza sıfırlandı");
    } catch {
      toast.error("Sıfırlama başarısız");
    }
  };

  return (
    <div className="p-4 sm:p-6 md:p-8 max-w-[960px]">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-2xl font-semibold text-relate-ink">Müşteriler</h2>
          <p className="text-sm text-relate-graphite mt-1">
            {customers.length} kayıtlı müşteri
          </p>
        </div>
        <input
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="İsim, telefon veya e-posta ara..."
          className="input-field w-64"
        />
      </div>

      {loading ? (
        <div className="text-center py-20 text-relate-graphite">
          Yükleniyor...
        </div>
      ) : filtered.length === 0 ? (
        <div className="text-center py-20 text-relate-graphite">
          Müşteri bulunamadı.
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-3">
          {filtered.map((c) => (
            <div
              key={c.phone}
              onClick={() => toggleSelect(c)}
              className="card cursor-pointer hover:shadow-md transition-shadow"
            >
              <div className="flex items-center gap-4">
                {/* Avatar */}
                <div className="w-10 h-10 rounded-full bg-relate-signal/10 flex items-center justify-center text-relate-signal font-semibold text-[15px] shrink-0">
                  {c.name.charAt(0).toUpperCase()}
                </div>
                <div className="flex-1 min-w-0">
                  <p className="font-semibold text-relate-ink">{c.name}</p>
                  <div className="flex gap-3 mt-0.5 text-xs text-relate-graphite">
                    <span>📞 {c.phone}</span>
                    {c.email && <span>✉️ {c.email}</span>}
                  </div>
                </div>
                <div className="text-right shrink-0">
                  <p className="text-sm font-semibold text-relate-ink">
                    {c.totalCount} randevu
                  </p>
                  <p className="text-xs text-relate-graphite mt-0.5">
                    Son: {new Date(c.lastVisit).toLocaleDateString("tr-TR")}
                  </p>
                </div>
                <span className="text-relate-graphite text-sm ml-2">
                  {selected?.phone === c.phone ? "▲" : "▼"}
                </span>
              </div>

              {/* Expanded appointment history */}
              {selected?.phone === c.phone && (
                <div
                  className="mt-4 border-t border-relate-border pt-4 space-y-4"
                  onClick={(e) => e.stopPropagation()}
                >
                  {/* AI memory section */}
                  {(() => {
                    const rec = memoryByPhone[c.phone];
                    if (rec === undefined) {
                      return (
                        <p className="text-xs text-relate-graphite">
                          Hafıza yükleniyor…
                        </p>
                      );
                    }
                    if (rec === null) {
                      return (
                        <div className="bg-relate-wash/60 rounded-lg p-3">
                          <p className="text-xs text-relate-graphite">
                            🤖 Bu müşteri için henüz AI hafızası oluşmamış.
                            İlk konuşma/randevudan sonra otomatik üretilecek.
                          </p>
                        </div>
                      );
                    }
                    const isEditing = editingPhone === c.phone && editForm;
                    return (
                      <div className="bg-blue-50/50 border border-blue-100 rounded-lg p-4 space-y-3">
                        <div className="flex items-center justify-between">
                          <p className="text-xs font-semibold text-relate-graphite uppercase tracking-wide">
                            🤖 AI Hafızası
                            {rec.last_summary_at && (
                              <span className="ml-2 text-[10px] font-normal text-relate-graphite normal-case tracking-normal">
                                son güncelleme:{" "}
                                {new Date(rec.last_summary_at).toLocaleString("tr-TR")}
                              </span>
                            )}
                          </p>
                          {!isEditing && (
                            <div className="flex items-center gap-3">
                              <button
                                onClick={() => startEdit(rec)}
                                className="text-[12px] text-relate-signal hover:underline"
                              >
                                Düzenle
                              </button>
                              <button
                                onClick={() => resetMemory(rec)}
                                className="text-[12px] text-red-600 hover:underline"
                              >
                                Sıfırla
                              </button>
                            </div>
                          )}
                        </div>

                        {isEditing ? (
                          <div className="space-y-2">
                            <div>
                              <label className="block text-[11px] font-medium text-relate-graphite mb-1">
                                Özet
                              </label>
                              <textarea
                                value={editForm!.memory_summary}
                                onChange={(e) =>
                                  setEditForm({
                                    ...editForm!,
                                    memory_summary: e.target.value,
                                  })
                                }
                                rows={3}
                                className="input-field text-[13px]"
                              />
                            </div>
                            <div className="grid grid-cols-2 gap-2">
                              <div>
                                <label className="block text-[11px] font-medium text-relate-graphite mb-1">
                                  Tercih ettiği personel
                                </label>
                                <input
                                  value={editForm!.preferred_staff}
                                  onChange={(e) =>
                                    setEditForm({
                                      ...editForm!,
                                      preferred_staff: e.target.value,
                                    })
                                  }
                                  className="input-field text-[13px]"
                                />
                              </div>
                              <div>
                                <label className="block text-[11px] font-medium text-relate-graphite mb-1">
                                  Tercih ettiği zaman
                                </label>
                                <input
                                  value={editForm!.preferred_times}
                                  onChange={(e) =>
                                    setEditForm({
                                      ...editForm!,
                                      preferred_times: e.target.value,
                                    })
                                  }
                                  className="input-field text-[13px]"
                                />
                              </div>
                            </div>
                            <div>
                              <label className="block text-[11px] font-medium text-relate-graphite mb-1">
                                Alerji / dikkat
                              </label>
                              <input
                                value={editForm!.allergies}
                                onChange={(e) =>
                                  setEditForm({
                                    ...editForm!,
                                    allergies: e.target.value,
                                  })
                                }
                                className="input-field text-[13px]"
                              />
                            </div>
                            <div>
                              <label className="block text-[11px] font-medium text-relate-graphite mb-1">
                                Notlar (sadece sahip görür)
                              </label>
                              <textarea
                                value={editForm!.notes}
                                onChange={(e) =>
                                  setEditForm({
                                    ...editForm!,
                                    notes: e.target.value,
                                  })
                                }
                                rows={2}
                                className="input-field text-[13px]"
                              />
                            </div>
                            <div>
                              <label className="block text-[11px] font-medium text-relate-graphite mb-1">
                                Etiketler (virgülle ayır)
                              </label>
                              <input
                                value={editForm!.tags}
                                onChange={(e) =>
                                  setEditForm({
                                    ...editForm!,
                                    tags: e.target.value,
                                  })
                                }
                                placeholder="örn. vegan, hassas cilt"
                                className="input-field text-[13px]"
                              />
                            </div>
                            <div className="flex gap-2 pt-1">
                              <button
                                onClick={() => saveEdit(rec)}
                                className="btn-primary px-4 py-1.5 text-[13px]"
                              >
                                Kaydet
                              </button>
                              <button
                                onClick={() => setEditingPhone(null)}
                                className="text-[13px] text-relate-graphite hover:underline px-2"
                              >
                                İptal
                              </button>
                            </div>
                          </div>
                        ) : (
                          <div className="space-y-2 text-[13px] text-relate-ink">
                            <p>
                              <span className="text-relate-graphite">Özet:</span>{" "}
                              {rec.memory_summary || (
                                <span className="text-relate-graphite italic">
                                  Henüz özet yok
                                </span>
                              )}
                            </p>
                            {(rec.preferences.preferred_staff ||
                              rec.preferences.preferred_times ||
                              rec.preferences.allergies ||
                              rec.preferences.notes ||
                              (rec.preferences.favorite_services || []).length >
                                0) && (
                              <div className="grid grid-cols-2 gap-x-4 gap-y-1 text-[12px]">
                                {rec.preferences.preferred_staff && (
                                  <p>
                                    <span className="text-relate-graphite">Personel:</span>{" "}
                                    {rec.preferences.preferred_staff}
                                  </p>
                                )}
                                {rec.preferences.preferred_times && (
                                  <p>
                                    <span className="text-relate-graphite">Zaman:</span>{" "}
                                    {rec.preferences.preferred_times}
                                  </p>
                                )}
                                {rec.preferences.allergies && (
                                  <p>
                                    <span className="text-relate-graphite">Alerji:</span>{" "}
                                    {rec.preferences.allergies}
                                  </p>
                                )}
                                {rec.preferences.favorite_services?.length > 0 && (
                                  <p>
                                    <span className="text-relate-graphite">
                                      Sık aldığı:
                                    </span>{" "}
                                    {rec.preferences.favorite_services.join(", ")}
                                  </p>
                                )}
                                {rec.preferences.notes && (
                                  <p className="col-span-2">
                                    <span className="text-relate-graphite">Not:</span>{" "}
                                    {rec.preferences.notes}
                                  </p>
                                )}
                              </div>
                            )}
                            {(rec.tags || []).length > 0 && (
                              <div className="flex flex-wrap gap-1 pt-1">
                                {rec.tags.map((t) => (
                                  <span
                                    key={t}
                                    className="text-[11px] bg-white border border-blue-200 text-blue-700 rounded-full px-2 py-0.5"
                                  >
                                    {t}
                                  </span>
                                ))}
                              </div>
                            )}
                            <p className="text-[11px] text-relate-graphite pt-1">
                              {rec.total_conversations} konuşma
                            </p>
                          </div>
                        )}
                      </div>
                    );
                  })()}

                  <div>
                    <p className="text-xs font-semibold text-relate-graphite uppercase tracking-wide mb-2">
                      Randevu Geçmişi
                    </p>
                  {c.appointments
                    .sort(
                      (a, b) =>
                        new Date(b.start_time).getTime() -
                        new Date(a.start_time).getTime(),
                    )
                    .map((a) => (
                      <div
                        key={a.id}
                        className="flex items-center justify-between text-sm"
                      >
                        <div>
                          <span className="font-medium text-relate-ink">
                            {a.service_name}
                          </span>
                          <span
                            className={`ml-2 text-xs px-1.5 py-0.5 rounded-full ${
                              a.status === "confirmed"
                                ? "bg-green-100 text-green-700"
                                : a.status === "cancelled"
                                  ? "bg-red-100 text-red-600"
                                  : a.status === "completed"
                                    ? "bg-gray-100 text-gray-600"
                                    : "bg-yellow-100 text-yellow-700"
                            }`}
                          >
                            {a.status === "confirmed"
                              ? "Onaylı"
                              : a.status === "cancelled"
                                ? "İptal"
                                : a.status === "completed"
                                  ? "Tamamlandı"
                                  : "Bekliyor"}
                          </span>
                        </div>
                        <span className="text-relate-graphite text-xs">
                          {new Date(a.start_time).toLocaleDateString("tr-TR", {
                            day: "2-digit",
                            month: "long",
                            year: "numeric",
                          })}{" "}
                          {new Date(a.start_time).toLocaleTimeString("tr-TR", {
                            hour: "2-digit",
                            minute: "2-digit",
                          })}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
