"use client";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import Link from "next/link";

interface AppStats {
  total_all_time: number;
  this_month: number;
  last_month: number;
  cancelled_this_month: number;
  cancel_rate_percent: number;
  upcoming_7_days: number;
  monthly_trend: { month: string; count: number }[];
  top_services: { name: string; count: number }[];
}

// Simple bar chart — no external lib needed
function MiniBarChart({ data }: { data: { month: string; count: number }[] }) {
  if (!data.length) return null;
  const max = Math.max(...data.map((d) => d.count), 1);
  return (
    <div className="flex items-end gap-2 h-20 mt-2">
      {data.map((d) => {
        const pct = Math.round((d.count / max) * 100);
        const label = d.month.slice(5); // MM
        const months = [
          "",
          "Oca",
          "Şub",
          "Mar",
          "Nis",
          "May",
          "Haz",
          "Tem",
          "Ağu",
          "Eyl",
          "Eki",
          "Kas",
          "Ara",
        ];
        return (
          <div
            key={d.month}
            className="flex flex-col items-center gap-1 flex-1"
          >
            <span className="text-[10px] text-relate-graphite">{d.count}</span>
            <div
              className="w-full rounded-t-md bg-relate-signal transition-all"
              style={{ height: `${pct}%`, minHeight: 4 }}
            />
            <span className="text-[10px] text-relate-graphite">
              {months[parseInt(label)]}
            </span>
          </div>
        );
      })}
    </div>
  );
}

export default function DashboardPage() {
  const [profile, setProfile] = useState<any>(null);
  const [stats, setStats] = useState<AppStats | null>(null);
  const [appointments, setAppointments] = useState<any[]>([]);

  useEffect(() => {
    api.getProfile().then(setProfile);
    api
      .getAppointmentStats()
      .then(setStats)
      .catch(() => null);
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

  const nextAppts = appointments
    .filter(
      (a) => new Date(a.start_time) > new Date() && a.status !== "cancelled",
    )
    .slice(0, 5);

  const monthChange = stats
    ? stats.last_month > 0
      ? Math.round(
          ((stats.this_month - stats.last_month) / stats.last_month) * 100,
        )
      : null
    : null;

  return (
    <div className="p-8 max-w-[960px]">
      <div className="mb-8">
        <h2 className="font-display font-semibold text-[28px] text-relate-ink tracking-tight">
          {profile?.name ?? "Dashboard"}
        </h2>
        <p className="text-[15px] text-relate-graphite mt-1">
          İşletmenizin özet görünümü
        </p>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-8">
        <div className="card">
          <p className="text-[10px] text-relate-fog uppercase tracking-[0.13px]">
            Bugün
          </p>
          <p className="num-mono text-[32px] text-relate-graphite mt-1">
            {todayCount}
          </p>
          <p className="text-[11px] text-relate-ash mt-1">randevu</p>
        </div>
        <div className="card">
          <p className="text-[10px] text-relate-fog uppercase tracking-[0.13px]">
            Bu Ay
          </p>
          <p className="num-mono text-[32px] text-relate-signal mt-1">
            {stats?.this_month ?? "—"}
          </p>
          {monthChange !== null && (
            <p
              className={`text-[11px] mt-1 ${monthChange >= 0 ? "text-relate-emerald" : "text-relate-coral"}`}
            >
              {monthChange >= 0 ? "▲" : "▼"} {Math.abs(monthChange)}% geçen ay
            </p>
          )}
        </div>
        <div className="card">
          <p className="text-[10px] text-relate-fog uppercase tracking-[0.13px]">
            7 Gün
          </p>
          <p className="num-mono text-[32px] text-relate-graphite mt-1">
            {stats?.upcoming_7_days ?? "—"}
          </p>
          <p className="text-[11px] text-relate-ash mt-1">yaklaşan</p>
        </div>
        <div className="card">
          <p className="text-[10px] text-relate-fog uppercase tracking-[0.13px]">
            İptal Oranı
          </p>
          <p
            className={`num-mono text-[32px] mt-1 ${(stats?.cancel_rate_percent ?? 0) > 20 ? "text-relate-coral" : "text-relate-graphite"}`}
          >
            {stats?.cancel_rate_percent ?? "—"}
            {stats ? "%" : ""}
          </p>
          <p className="text-[11px] text-relate-ash mt-1">bu ay</p>
        </div>
      </div>

      {/* Charts row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-8">
        {/* Monthly trend */}
        <div className="card">
          <p className="text-[14px] font-semibold text-relate-ink">
            Aylık Trend
          </p>
          <p className="text-[12px] text-relate-graphite">
            Son 6 ay (onaylı randevular)
          </p>
          {stats?.monthly_trend?.length ? (
            <MiniBarChart data={stats.monthly_trend} />
          ) : (
            <p className="text-[13px] text-relate-graphite text-center py-8">
              Yeterli veri yok
            </p>
          )}
        </div>

        {/* Top services */}
        <div className="card">
          <p className="text-[14px] font-semibold text-relate-ink">
            Popüler Hizmetler
          </p>
          <p className="text-[12px] text-relate-graphite mb-3">Tüm zamanlar</p>
          {stats?.top_services?.length ? (
            <div className="space-y-2">
              {stats.top_services.map((s, i) => {
                const max = stats.top_services[0].count;
                const pct = Math.round((s.count / max) * 100);
                return (
                  <div key={s.name}>
                    <div className="flex justify-between text-[12px] mb-0.5">
                      <span className="text-relate-ink truncate max-w-[70%]">
                        {s.name}
                      </span>
                      <span className="text-relate-graphite">{s.count}</span>
                    </div>
                    <div className="h-1.5 bg-relate-wash rounded-full overflow-hidden">
                      <div
                        className="h-full bg-relate-signal rounded-full"
                        style={{ width: `${pct}%` }}
                      />
                    </div>
                  </div>
                );
              })}
            </div>
          ) : (
            <p className="text-[13px] text-relate-graphite text-center py-8">
              Henüz veri yok
            </p>
          )}
        </div>
      </div>

      {/* Upcoming appointments */}
      <div className="card p-6">
        <div className="flex items-center justify-between mb-5">
          <h3 className="font-display font-semibold text-[17px] text-relate-ink tracking-tight">
            Yaklaşan Randevular
          </h3>
          <Link
            href="/dashboard/appointments"
            className="text-[13px] text-relate-signal hover:underline"
          >
            Tümünü gör
          </Link>
        </div>
        {nextAppts.length === 0 ? (
          <p className="text-[14px] text-relate-graphite text-center py-10">
            Henüz yaklaşan randevu yok.
          </p>
        ) : (
          <div className="divide-y divide-relate-border">
            {nextAppts.map((a) => (
              <div
                key={a.id}
                className="flex items-center justify-between py-3.5"
              >
                <div>
                  <p className="font-medium text-relate-ink text-[14px]">
                    {a.customer_name}
                  </p>
                  <p className="text-[12px] text-relate-graphite mt-0.5">
                    {a.service_name}
                  </p>
                </div>
                <div className="text-right">
                  <p className="text-[13px] font-medium text-relate-ink">
                    {new Date(a.start_time).toLocaleDateString("tr-TR")}
                  </p>
                  <p className="text-[12px] text-relate-graphite mt-0.5">
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
        <div className="mt-4 card px-6 py-4 flex items-center gap-4">
          <div className="w-8 h-8 bg-emerald-50 border border-emerald-200 rounded-full flex items-center justify-center text-[16px] shrink-0">
            📅
          </div>
          <div className="flex-1">
            <p className="text-[14px] text-relate-ink font-medium">
              Google Takvim bağlı değil
            </p>
            <p className="text-[12px] text-relate-graphite">
              Randevular otomatik takvime eklensin.
            </p>
          </div>
          <Link
            href="/dashboard/settings"
            className="text-[13px] text-relate-signal hover:underline shrink-0"
          >
            Bağla
          </Link>
        </div>
      )}
    </div>
  );
}
