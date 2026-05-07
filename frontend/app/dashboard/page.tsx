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
      color: "text-apple-blue",
    },
    {
      label: "Yaklaşan Randevular",
      value: upcomingCount,
      color: "text-apple-ink",
    },
    {
      label: "Google Takvim",
      value: profile?.google_connected ? "Bağlı" : "Bağlı Değil",
      color: profile?.google_connected ? "text-apple-blue" : "text-apple-secondary",
    },
  ];

  const nextAppts = appointments
    .filter(
      (a) => new Date(a.start_time) > new Date() && a.status !== "cancelled",
    )
    .slice(0, 5);

  return (
    <div className="p-8 max-w-[900px]">
      <div className="mb-8">
        <h2 className="font-display font-semibold text-[28px] text-apple-ink tracking-tight">
          {profile?.name ? profile.name : "Dashboard"}
        </h2>
        <p className="text-[15px] text-apple-secondary mt-1">İşletmenizin özet görünümü</p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-8">
        {stats.map((s) => (
          <div key={s.label} className="bg-white border border-apple-border rounded-apple p-6">
            <p className="text-[13px] text-apple-secondary">{s.label}</p>
            <p className={`text-[32px] font-display font-semibold mt-1 tracking-tight ${s.color}`}>
              {s.value}
            </p>
          </div>
        ))}
      </div>

      {/* Upcoming appointments */}
      <div className="bg-white border border-apple-border rounded-apple p-6">
        <div className="flex items-center justify-between mb-5">
          <h3 className="font-display font-semibold text-[17px] text-apple-ink tracking-tight">
            Yaklaşan Randevular
          </h3>
          <Link
            href="/dashboard/appointments"
            className="text-[13px] text-apple-blueLink hover:underline"
          >
            Tümünü gör
          </Link>
        </div>
        {nextAppts.length === 0 ? (
          <p className="text-[14px] text-apple-secondary text-center py-10">
            Henüz yaklaşan randevu yok.
          </p>
        ) : (
          <div className="divide-y divide-apple-border">
            {nextAppts.map((a) => (
              <div
                key={a.id}
                className="flex items-center justify-between py-3.5"
              >
                <div>
                  <p className="font-medium text-apple-ink text-[14px]">
                    {a.customer_name}
                  </p>
                  <p className="text-[12px] text-apple-secondary mt-0.5">{a.service_name}</p>
                </div>
                <div className="text-right">
                  <p className="text-[13px] font-medium text-apple-ink">
                    {new Date(a.start_time).toLocaleDateString("tr-TR")}
                  </p>
                  <p className="text-[12px] text-apple-secondary mt-0.5">
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

      {/* Google Calendar warning */}
      {!profile?.google_connected && (
        <div className="mt-4 bg-white border border-apple-border rounded-apple px-6 py-4 flex items-center gap-4">
          <div className="w-8 h-8 bg-apple-gray rounded-full flex items-center justify-center text-[16px] shrink-0">
            📅
          </div>
          <div className="flex-1">
            <p className="text-[14px] text-apple-ink font-medium">Google Takvim bağlı değil</p>
            <p className="text-[12px] text-apple-secondary">Randevular otomatik takvime eklensin.</p>
          </div>
          <Link href="/dashboard/settings" className="text-[13px] text-apple-blueLink hover:underline shrink-0">
            Bağla
          </Link>
        </div>
      )}
    </div>
  );
}
