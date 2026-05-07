"use client";
import { useEffect, useState } from "react";
import { useRouter, usePathname } from "next/navigation";
import Link from "next/link";
import { api } from "@/lib/api";

const NAV = [
  { href: "/dashboard", label: "Genel Bakış", icon: "📊" },
  { href: "/dashboard/appointments", label: "Randevular", icon: "📅" },
  { href: "/dashboard/settings", label: "Ayarlar", icon: "⚙️" },
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
    <div className="min-h-screen flex bg-gray-50">
      {/* Sidebar */}
      <aside className="w-64 bg-white border-r border-gray-200 flex flex-col">
        <div className="p-5 border-b border-gray-200">
          <h1 className="text-xl font-bold text-gray-900">
            Assistant<span className="text-brand-600">AI</span>
          </h1>
          {businessName && (
            <p className="text-sm text-gray-500 mt-1 truncate">
              {businessName}
            </p>
          )}
        </div>

        <nav className="flex-1 p-4 space-y-1">
          {NAV.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                pathname === item.href
                  ? "bg-brand-50 text-brand-700"
                  : "text-gray-600 hover:bg-gray-100"
              }`}
            >
              <span>{item.icon}</span>
              {item.label}
            </Link>
          ))}
        </nav>

        {/* Chat link */}
        {slug && (
          <div className="p-4 border-t border-gray-200">
            <p className="text-xs text-gray-500 mb-2">Müşteri chat linkiniz:</p>
            <a
              href={`/chat/${slug}`}
              target="_blank"
              rel="noreferrer"
              className="text-xs text-brand-600 hover:underline break-all"
            >
              /chat/{slug}
            </a>
          </div>
        )}

        <div className="p-4 border-t border-gray-200">
          <button
            onClick={logout}
            className="text-sm text-gray-500 hover:text-red-500 transition-colors"
          >
            🚪 Çıkış Yap
          </button>
        </div>
      </aside>

      {/* Main */}
      <main className="flex-1 overflow-auto">{children}</main>
    </div>
  );
}
