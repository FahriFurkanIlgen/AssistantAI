"use client";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import Link from "next/link";

interface Stats {
  total: number;
  today: number;
  upcoming: number;
  cancelled: number;
}

export default function DashboardPage() {
  const [profile, setProfile] = useState<any>(null);
  const [appointments, setAppointments] = useState<any[]>([]);

  useEffect(() => {
    api.getProfile().then(setProfile);
    const now = new Date();
    const startOfDay = new Date(
      now.getFullYear(),
      now.getMonth(),
      now.getDate(),
    ).toISOString();
    api.getAppointments({ start: startOfDay }).then(setAppointments);
  }, []);

  const todayCount = appointments.filter((a) => {
    const d = new Date(a.start_time);
    const today = new Date();
    return (
      d.getDate() === today.getDate() &&
      d.getMonth() === today.getMonth() &&
      d.getFullYear() === today.getFullYear() &&
      a.status !== "cancelled"
    );
  }).length;

  const upcomingCount = appointments.filter(
    (a) => new Date(a.start_time) > new Date() && a.status !== "cancelled",
  ).length;

  const stats = [
    {
      label: "Bugünkü Randevular",
      value: todayCount,
      color: "text-blue-600",
      bg: "bg-blue-50",
    },
    {
      label: "Yaklaşan Randevular",
      value: upcomingCount,
      color: "text-green-600",
      bg: "bg-green-50",
    },
    {
      label: "Google Takvim",
      value: profile?.google_connected ? "Bağlı ✅" : "Bağlı Değil ❌",
      color: profile?.google_connected ? "text-green-600" : "text-red-500",
      bg: profile?.google_connected ? "bg-green-50" : "bg-red-50",
    },
  ];

  const nextAppts = appointments
    .filter(
      (a) => new Date(a.start_time) > new Date() && a.status !== "cancelled",
    )
    .slice(0, 5);

  return (
    <div className="p-8">
      <div className="mb-8">
        <h2 className="text-2xl font-bold text-gray-900">
          Hoş geldiniz{profile?.name ? `, ${profile.name}` : ""} 👋
        </h2>
        <p className="text-gray-500 mt-1">İşletmenizin özet görünümü</p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-5 mb-8">
        {stats.map((s) => (
          <div key={s.label} className={`card ${s.bg}`}>
            <p className="text-sm text-gray-500">{s.label}</p>
            <p className={`text-3xl font-bold mt-1 ${s.color}`}>{s.value}</p>
          </div>
        ))}
      </div>

      {/* Upcoming appointments */}
      <div className="card">
        <div className="flex items-center justify-between mb-4">
          <h3 className="font-semibold text-gray-900">Yaklaşan Randevular</h3>
          <Link
            href="/dashboard/appointments"
            className="text-sm text-brand-600 hover:underline"
          >
            Tümünü gör →
          </Link>
        </div>
        {nextAppts.length === 0 ? (
          <p className="text-sm text-gray-400 text-center py-8">
            Henüz yaklaşan randevu yok.
          </p>
        ) : (
          <div className="space-y-3">
            {nextAppts.map((a) => (
              <div
                key={a.id}
                className="flex items-center justify-between py-3 px-4 bg-gray-50 rounded-lg border border-gray-100"
              >
                <div>
                  <p className="font-medium text-gray-900 text-sm">
                    {a.customer_name}
                  </p>
                  <p className="text-xs text-gray-500">{a.service_name}</p>
                </div>
                <div className="text-right">
                  <p className="text-sm font-medium text-gray-700">
                    {new Date(a.start_time).toLocaleDateString("tr-TR")}
                  </p>
                  <p className="text-xs text-gray-500">
                    {new Date(a.start_time).toLocaleTimeString("tr-TR", {
                      hour: "2-digit",
                      minute: "2-digit",
                    })}
                  </p>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Quick links */}
      {!profile?.google_connected && (
        <div className="mt-5 card bg-amber-50 border-amber-200">
          <p className="text-sm font-medium text-amber-800">
            💡 Google Takvim bağlamadınız. Randevular takvime otomatik eklensin.{" "}
            <Link href="/dashboard/settings" className="underline">
              Şimdi Bağla →
            </Link>
          </p>
        </div>
      )}
    </div>
  );
}
