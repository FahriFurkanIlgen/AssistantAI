"use client";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";

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

export default function CustomersPage() {
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [selected, setSelected] = useState<Customer | null>(null);

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

  return (
    <div className="p-8 max-w-[960px]">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-2xl font-bold text-apple-ink">Müşteriler</h2>
          <p className="text-sm text-apple-secondary mt-1">
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
        <div className="text-center py-20 text-apple-secondary">
          Yükleniyor...
        </div>
      ) : filtered.length === 0 ? (
        <div className="text-center py-20 text-apple-secondary">
          Müşteri bulunamadı.
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-3">
          {filtered.map((c) => (
            <div
              key={c.phone}
              onClick={() =>
                setSelected(selected?.phone === c.phone ? null : c)
              }
              className="card cursor-pointer hover:shadow-md transition-shadow"
            >
              <div className="flex items-center gap-4">
                {/* Avatar */}
                <div className="w-10 h-10 rounded-full bg-apple-blue/10 flex items-center justify-center text-apple-blue font-semibold text-[15px] shrink-0">
                  {c.name.charAt(0).toUpperCase()}
                </div>
                <div className="flex-1 min-w-0">
                  <p className="font-semibold text-apple-ink">{c.name}</p>
                  <div className="flex gap-3 mt-0.5 text-xs text-apple-secondary">
                    <span>📞 {c.phone}</span>
                    {c.email && <span>✉️ {c.email}</span>}
                  </div>
                </div>
                <div className="text-right shrink-0">
                  <p className="text-sm font-semibold text-apple-ink">
                    {c.totalCount} randevu
                  </p>
                  <p className="text-xs text-apple-secondary mt-0.5">
                    Son: {new Date(c.lastVisit).toLocaleDateString("tr-TR")}
                  </p>
                </div>
                <span className="text-apple-secondary text-sm ml-2">
                  {selected?.phone === c.phone ? "▲" : "▼"}
                </span>
              </div>

              {/* Expanded appointment history */}
              {selected?.phone === c.phone && (
                <div className="mt-4 border-t border-apple-border pt-4 space-y-2">
                  <p className="text-xs font-semibold text-apple-secondary uppercase tracking-wide mb-2">
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
                          <span className="font-medium text-apple-ink">
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
                        <span className="text-apple-secondary text-xs">
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
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
