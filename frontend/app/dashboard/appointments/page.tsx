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

export default function AppointmentsPage() {
  const [appointments, setAppointments] = useState<Appointment[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState("all");

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
    if (!confirm("Bu randevuyu iptal etmek istediğinizden emin misiniz?"))
      return;
    try {
      await api.cancelAppointment(id);
      toast.success("Randevu iptal edildi");
      loadAppointments();
    } catch {
      toast.error("İptal işlemi başarısız");
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
          <p className="text-gray-500 text-sm mt-1">
            {filtered.length} randevu
          </p>
        </div>
        {/* Filter */}
        <div className="flex gap-2">
          {["all", "confirmed", "pending", "cancelled", "completed"].map(
            (s) => (
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
            ),
          )}
        </div>
      </div>

      {loading ? (
        <div className="text-center py-20 text-gray-400">Yükleniyor...</div>
      ) : filtered.length === 0 ? (
        <div className="text-center py-20 text-gray-400">
          Randevu bulunamadı.
        </div>
      ) : (
        <div className="space-y-3">
          {filtered
            .sort(
              (a, b) =>
                new Date(a.start_time).getTime() -
                new Date(b.start_time).getTime(),
            )
            .map((a) => (
              <div
                key={a.id}
                className="card hover:shadow-md transition-shadow"
              >
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <p className="font-semibold text-gray-900">
                        {a.customer_name}
                      </p>
                      <span
                        className={`text-xs px-2 py-0.5 rounded-full font-medium ${STATUS_COLORS[a.status]}`}
                      >
                        {STATUS_LABELS[a.status]}
                      </span>
                      {a.google_event_id && (
                        <span className="text-xs bg-blue-50 text-blue-600 px-2 py-0.5 rounded-full">
                          📅 Takvimde
                        </span>
                      )}
                    </div>
                    <p className="text-sm text-brand-600 font-medium">
                      {a.service_name}
                    </p>
                    <div className="flex flex-wrap gap-4 mt-2 text-xs text-gray-500">
                      <span>📞 {a.customer_phone}</span>
                      {a.customer_email && <span>✉️ {a.customer_email}</span>}
                      {a.notes && <span>📝 {a.notes}</span>}
                    </div>
                  </div>
                  <div className="text-right shrink-0">
                    <p className="text-sm font-semibold text-gray-800">
                      {new Date(a.start_time).toLocaleDateString("tr-TR", {
                        day: "2-digit",
                        month: "long",
                        year: "numeric",
                      })}
                    </p>
                    <p className="text-sm text-gray-500">
                      {new Date(a.start_time).toLocaleTimeString("tr-TR", {
                        hour: "2-digit",
                        minute: "2-digit",
                      })}{" "}
                      –{" "}
                      {new Date(a.end_time).toLocaleTimeString("tr-TR", {
                        hour: "2-digit",
                        minute: "2-digit",
                      })}
                    </p>
                    {a.status === "confirmed" && (
                      <button
                        onClick={() => handleCancel(a.id)}
                        className="mt-2 text-xs text-red-500 hover:text-red-700 hover:underline"
                      >
                        İptal Et
                      </button>
                    )}
                  </div>
                </div>
              </div>
            ))}
        </div>
      )}
    </div>
  );
}
