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
  notes?: string;
  start_time: string;
  end_time: string;
  status: string;
  google_event_id?: string;
}

const STATUS_LABELS: Record<string, string> = {
  confirmed: "Onaylı",
  pending: "Bekliyor",
  cancelled: "İptal",
  completed: "Tamamlandı",
};

const STATUS_COLORS: Record<string, string> = {
  confirmed: "bg-green-100 text-green-700",
  pending: "bg-yellow-100 text-yellow-700",
  cancelled: "bg-red-100 text-red-600",
  completed: "bg-gray-100 text-gray-600",
};

const STATUS_BAR_COLORS: Record<string, string> = {
  confirmed: "bg-green-500",
  pending: "bg-yellow-400",
  cancelled: "bg-red-400",
  completed: "bg-gray-400",
};

const DAY_NAMES = ["Pzt", "Sal", "Çar", "Per", "Cum", "Cmt", "Paz"];

function getWeekDays(baseDate: Date): Date[] {
  const d = new Date(baseDate);
  const day = d.getDay(); // 0=Sun
  const monday = new Date(d);
  monday.setDate(d.getDate() - ((day + 6) % 7));
  return Array.from({ length: 7 }, (_, i) => {
    const x = new Date(monday);
    x.setDate(monday.getDate() + i);
    return x;
  });
}

function isSameDay(a: Date, b: Date) {
  return (
    a.getFullYear() === b.getFullYear() &&
    a.getMonth() === b.getMonth() &&
    a.getDate() === b.getDate()
  );
}

// ── Weekly Calendar ─────────────────────────────────────────────────────────
function WeeklyCalendar({
  appointments,
  onCancel,
}: {
  appointments: Appointment[];
  onCancel: (id: string) => void;
}) {
  const [weekBase, setWeekBase] = useState(new Date());
  const days = getWeekDays(weekBase);
  const HOURS = Array.from({ length: 13 }, (_, i) => i + 8); // 08–20

  const apptsByDay = days.map((day) =>
    appointments.filter((a) => isSameDay(new Date(a.start_time), day))
  );

  const prevWeek = () => {
    const d = new Date(weekBase);
    d.setDate(d.getDate() - 7);
    setWeekBase(d);
  };
  const nextWeek = () => {
    const d = new Date(weekBase);
    d.setDate(d.getDate() + 7);
    setWeekBase(d);
  };

  const monthLabel = days[0].toLocaleDateString("tr-TR", {
    month: "long",
    year: "numeric",
  });

  return (
    <div className="bg-white rounded-2xl border border-relate-border overflow-hidden">
      {/* Week nav */}
      <div className="flex items-center justify-between px-5 py-3 border-b border-relate-border bg-relate-wash">
        <button onClick={prevWeek} className="text-relate-graphite hover:text-relate-ink px-2 py-1 rounded-lg hover:bg-relate-border transition-colors">‹ Önceki</button>
        <span className="font-semibold text-relate-ink capitalize">{monthLabel}</span>
        <button onClick={nextWeek} className="text-relate-graphite hover:text-relate-ink px-2 py-1 rounded-lg hover:bg-relate-border transition-colors">Sonraki ›</button>
      </div>

      {/* Day headers */}
      <div className="grid grid-cols-8 border-b border-relate-border">
        <div className="py-2" /> {/* time col */}
        {days.map((day, i) => {
          const isToday = isSameDay(day, new Date());
          return (
            <div key={i} className={`py-2 text-center border-l border-relate-border ${isToday ? "bg-blue-50" : ""}`}>
              <p className="text-xs text-relate-graphite">{DAY_NAMES[i]}</p>
              <p className={`text-sm font-semibold ${isToday ? "text-relate-signal" : "text-relate-ink"}`}>
                {day.getDate()}
              </p>
            </div>
          );
        })}
      </div>

      {/* Grid */}
      <div className="overflow-y-auto max-h-[520px]">
        {HOURS.map((hour) => (
          <div key={hour} className="grid grid-cols-8 border-b border-relate-border" style={{ minHeight: 56 }}>
            {/* Hour label */}
            <div className="px-2 pt-1">
              <span className="text-[11px] text-relate-graphite">{hour}:00</span>
            </div>
            {days.map((day, di) => {
              const dayAppts = apptsByDay[di].filter((a) => {
                const h = new Date(a.start_time).getHours();
                return h === hour;
              });
              return (
                <div key={di} className="border-l border-relate-border p-0.5 relative">
                  {dayAppts.map((a) => (
                    <div
                      key={a.id}
                      className={`rounded-md px-1.5 py-1 mb-0.5 ${STATUS_BAR_COLORS[a.status]} text-white text-[10px] leading-tight cursor-pointer group relative`}
                      title={`${a.customer_name} — ${a.service_name}`}
                    >
                      <p className="font-semibold truncate">{a.customer_name}</p>
                      <p className="opacity-80 truncate">{a.service_name}</p>
                      <p className="opacity-70">
                        {new Date(a.start_time).toLocaleTimeString("tr-TR", { hour: "2-digit", minute: "2-digit" })}
                      </p>
                      {a.status === "confirmed" && (
                        <button
                          onClick={() => onCancel(a.id)}
                          className="absolute top-0.5 right-0.5 hidden group-hover:block text-white/80 hover:text-white leading-none text-[10px]"
                        >
                          ✕
                        </button>
                      )}
                    </div>
                  ))}
                </div>
              );
            })}
          </div>
        ))}
      </div>
    </div>
  );
}

// ── Main Page ────────────────────────────────────────────────────────────────
export default function AppointmentsPage() {
  const [appointments, setAppointments] = useState<Appointment[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState("all");
  const [view, setView] = useState<"list" | "week">("list");

  const loadAppointments = async () => {
    setLoading(true);
    try {
      const data = await api.getAppointments();
      setAppointments(data);
    } catch {
      toast.error("Randevular yüklenemedi");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAppointments();
  }, []);

  const handleCancel = async (id: string) => {
    if (!confirm("Bu randevuyu iptal etmek istediğinizden emin misiniz?")) return;
    try {
      await api.cancelAppointment(id);
      toast.success("Randevu iptal edildi");
      loadAppointments();
    } catch {
      toast.error("İptal işlemi başarısız");
    }
  };

  const handleStatusChange = async (id: string, status: string) => {
    try {
      await api.updateAppointmentStatus(id, status);
      toast.success("Durum güncellendi");
      loadAppointments();
    } catch {
      toast.error("Güncelleme başarısız");
    }
  };

  const filtered =
    filter === "all"
      ? appointments
      : appointments.filter((a) => a.status === filter);

  return (
    <div className="p-8">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Randevular</h2>
          <p className="text-gray-500 text-sm mt-1">{filtered.length} randevu</p>
        </div>
        <div className="flex items-center gap-3">
          {/* View toggle */}
          <div className="flex bg-relate-wash rounded-lg border border-relate-border p-0.5">
            <button
              onClick={() => setView("list")}
              className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${view === "list" ? "bg-white shadow-sm text-relate-ink" : "text-relate-graphite"}`}
            >
              ☰ Liste
            </button>
            <button
              onClick={() => setView("week")}
              className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${view === "week" ? "bg-white shadow-sm text-relate-ink" : "text-relate-graphite"}`}
            >
              📅 Hafta
            </button>
          </div>
          {/* Filter — only in list mode */}
          {view === "list" && (
            <div className="flex gap-2">
              {["all", "confirmed", "pending", "cancelled", "completed"].map((s) => (
                <button
                  key={s}
                  onClick={() => setFilter(s)}
                  className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                    filter === s
                      ? "bg-brand-600 text-white"
                      : "bg-white text-gray-600 border border-gray-200 hover:bg-gray-50"
                  }`}
                >
                  {s === "all" ? "Tümü" : STATUS_LABELS[s]}
                </button>
              ))}
            </div>
          )}
        </div>
      </div>

      {loading ? (
        <div className="text-center py-20 text-gray-400">Yükleniyor...</div>
      ) : view === "week" ? (
        <WeeklyCalendar appointments={appointments} onCancel={handleCancel} />
      ) : filtered.length === 0 ? (
        <div className="text-center py-20 text-gray-400">Randevu bulunamadı.</div>
      ) : (
        <div className="space-y-3">
          {filtered
            .sort((a, b) => new Date(a.start_time).getTime() - new Date(b.start_time).getTime())
            .map((a) => (
              <div key={a.id} className="card hover:shadow-md transition-shadow">
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <p className="font-semibold text-gray-900">{a.customer_name}</p>
                      <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${STATUS_COLORS[a.status]}`}>
                        {STATUS_LABELS[a.status]}
                      </span>
                      {a.google_event_id && (
                        <span className="text-xs bg-blue-50 text-blue-600 px-2 py-0.5 rounded-full">
                          📅 Takvimde
                        </span>
                      )}
                    </div>
                    <p className="text-sm text-brand-600 font-medium">{a.service_name}</p>
                    <div className="flex flex-wrap gap-4 mt-2 text-xs text-gray-500">
                      <span>📞 {a.customer_phone}</span>
                      {a.customer_email && <span>✉️ {a.customer_email}</span>}
                      {a.notes && <span>📝 {a.notes}</span>}
                    </div>
                  </div>
                  <div className="text-right shrink-0">
                    <p className="text-sm font-semibold text-gray-800">
                      {new Date(a.start_time).toLocaleDateString("tr-TR", { day: "2-digit", month: "long", year: "numeric" })}
                    </p>
                    <p className="text-sm text-gray-500">
                      {new Date(a.start_time).toLocaleTimeString("tr-TR", { hour: "2-digit", minute: "2-digit" })}
                      {" – "}
                      {new Date(a.end_time).toLocaleTimeString("tr-TR", { hour: "2-digit", minute: "2-digit" })}
                    </p>
                    <div className="flex gap-2 justify-end mt-2">
                      {a.status === "pending" && (
                        <button
                          onClick={() => handleStatusChange(a.id, "confirmed")}
                          className="text-xs text-green-600 hover:text-green-800 hover:underline"
                        >
                          ✓ Onayla
                        </button>
                      )}
                      {a.status === "confirmed" && (
                        <button
                          onClick={() => handleStatusChange(a.id, "completed")}
                          className="text-xs text-blue-600 hover:text-blue-800 hover:underline"
                        >
                          ✓ Tamamlandı
                        </button>
                      )}
                      {(a.status === "confirmed" || a.status === "pending") && (
                        <button
                          onClick={() => handleCancel(a.id)}
                          className="text-xs text-red-500 hover:text-red-700 hover:underline"
                        >
                          İptal
                        </button>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            ))}
        </div>
      )}
    </div>
  );
}
