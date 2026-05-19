"use client";
import { useEffect, useState } from "react";
import { useRouter, usePathname } from "next/navigation";
import Link from "next/link";
import { api } from "@/lib/api";
import { LogoLockup } from "@/components/brand/Logo";

const NAV = [
  { href: "/dashboard", label: "Genel Bakış" },
  { href: "/dashboard/appointments", label: "Randevular" },
  { href: "/dashboard/services", label: "Hizmetler" },
  { href: "/dashboard/customers", label: "Müşteriler" },
  { href: "/dashboard/staff", label: "Personel" },
  { href: "/dashboard/knowledge", label: "Bilgi Bankası" },
  { href: "/dashboard/settings", label: "Ayarlar" },
];

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const router = useRouter();
  const pathname = usePathname();
  const [businessName, setBusinessName] = useState("");
  const [slug, setSlug] = useState("");

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) {
      router.push("/login");
      return;
    }
    api
      .getMe()
      .then((data) => {
        setBusinessName(data.name);
        setSlug(data.slug);
      })
      .catch(() => router.push("/login"));
  }, [router]);

  const logout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("business_slug");
    router.push("/login");
  };

  return (
    <div className="min-h-screen flex bg-relate-canvas">
      {/* Sidebar */}
      <aside className="w-60 bg-white border-r border-relate-border flex flex-col shrink-0">
        {/* Brand */}
        <div className="px-6 py-5 border-b border-relate-border">
          <LogoLockup href="/dashboard" size={28} />
          {businessName && (
            <p className="text-[12px] text-relate-graphite mt-1 truncate">
              {businessName}
            </p>
          )}
        </div>

        {/* Nav */}
        <nav className="flex-1 px-3 py-4 space-y-0.5">
          {NAV.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className={`flex items-center px-3 py-2 rounded-lg text-[14px] font-medium transition-colors ${
                pathname === item.href
                  ? "bg-relate-wash text-relate-ink"
                  : "text-relate-graphite hover:bg-relate-wash hover:text-relate-ink"
              }`}
            >
              {item.label}
            </Link>
          ))}
        </nav>

        {/* Chat link */}
        {slug && (
          <div className="px-6 py-4 border-t border-relate-border">
            <p className="text-[11px] text-relate-graphite mb-1.5">
              Müşteri linki
            </p>
            <a
              href={`/chat/${slug}`}
              target="_blank"
              rel="noreferrer"
              className="text-[12px] text-relate-signal hover:underline break-all"
            >
              /chat/{slug}
            </a>
          </div>
        )}

        {/* Logout */}
        <div className="px-6 py-4 border-t border-relate-border">
          <button
            onClick={logout}
            className="text-[13px] text-relate-graphite hover:text-relate-ink transition-colors"
          >
            Çıkış Yap
          </button>
        </div>
      </aside>

      {/* Main */}
      <main className="flex-1 overflow-auto">{children}</main>
    </div>
  );
}
