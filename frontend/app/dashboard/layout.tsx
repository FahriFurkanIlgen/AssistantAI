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
  const [open, setOpen] = useState(false);

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

  // Sayfa değişince drawer'ı kapat
  useEffect(() => {
    setOpen(false);
  }, [pathname]);

  const logout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("business_slug");
    router.push("/login");
  };

  const sidebarContent = (
    <>
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
      <nav className="flex-1 px-3 py-4 space-y-0.5 overflow-y-auto">
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
    </>
  );

  return (
    <div className="min-h-[100dvh] md:flex bg-relate-canvas">
      {/* Mobile top bar */}
      <header
        className="md:hidden sticky top-0 z-30 flex items-center justify-between gap-3 px-4 h-14 bg-relate-canvas/90 backdrop-blur border-b border-relate-border"
        style={{ paddingTop: "env(safe-area-inset-top)" }}
      >
        <button
          onClick={() => setOpen(true)}
          aria-label="Menüyü aç"
          className="w-9 h-9 -ml-1 flex items-center justify-center rounded-lg text-relate-ink hover:bg-relate-wash"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.8} d="M4 6h16M4 12h16M4 18h16" />
          </svg>
        </button>
        <div className="flex-1 min-w-0">
          <LogoLockup href="/dashboard" size={22} />
        </div>
        {slug && (
          <a
            href={`/chat/${slug}`}
            target="_blank"
            rel="noreferrer"
            className="text-[12px] text-relate-signal hover:underline shrink-0"
          >
            Chat
          </a>
        )}
      </header>

      {/* Mobile drawer backdrop */}
      {open && (
        <button
          aria-label="Kapat"
          onClick={() => setOpen(false)}
          className="md:hidden fixed inset-0 z-40 bg-relate-ink/30 backdrop-blur-sm animate-in fade-in"
        />
      )}

      {/* Sidebar — drawer on mobile, static on desktop */}
      <aside
        className={`fixed md:static inset-y-0 left-0 z-50 w-72 md:w-60 bg-relate-canvas md:bg-transparent border-r border-relate-border flex flex-col shrink-0 transform transition-transform duration-300 ease-out md:transform-none ${
          open ? "translate-x-0" : "-translate-x-full md:translate-x-0"
        }`}
        style={{ paddingTop: "env(safe-area-inset-top)" }}
      >
        {sidebarContent}
      </aside>

      {/* Main */}
      <main className="flex-1 min-w-0 overflow-x-hidden">{children}</main>
    </div>
  );
}
