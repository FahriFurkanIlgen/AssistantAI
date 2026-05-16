"use client";
import { useState, useEffect } from "react";
import { LogoLockup } from "@/components/brand/Logo";

export default function AdminLayout({ children }: { children: React.ReactNode }) {
  const [key, setKey] = useState("");
  const [authed, setAuthed] = useState(false);
  const [input, setInput] = useState("");
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
    const stored = localStorage.getItem("admin_key");
    if (stored) {
      setKey(stored);
      setAuthed(true);
    }
  }, []);

  if (!mounted) return null;

  if (!authed) {
    return (
      <div data-admin className="relative min-h-screen bg-relate-canvas flex flex-col items-center justify-center px-4">
        <div className="absolute inset-0 hero-wash pointer-events-none" aria-hidden />
        <div className="relative mb-8">
          <LogoLockup href="/" size={36} />
        </div>
        <div className="relative w-full max-w-sm card-feature !p-8">
          <h1 className="font-display font-semibold text-[22px] text-relate-ink tracking-tight mb-1">
            Admin Girişi
          </h1>
          <p className="text-[14px] text-relate-graphite mb-6">
            Devam etmek için admin anahtarını girin.
          </p>
          <div className="space-y-3">
            <input
              type="password"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter" && input.trim()) {
                  localStorage.setItem("admin_key", input.trim());
                  setKey(input.trim());
                  setAuthed(true);
                }
              }}
              placeholder="Admin anahtarı"
              className="input-field"
              autoFocus
            />
            <button
              onClick={() => {
                if (!input.trim()) return;
                localStorage.setItem("admin_key", input.trim());
                setKey(input.trim());
                setAuthed(true);
              }}
              className="btn-primary w-full"
            >
              Giriş
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div data-admin className="min-h-screen bg-relate-canvas">
      <header className="bg-white border-b border-relate-rule px-6 py-3 flex items-center justify-between">
        <LogoLockup href="/" size={32} />
        <div className="flex items-center gap-3">
          <span className="badge badge-azure text-[12px]">Admin</span>
          <button
            onClick={() => {
              localStorage.removeItem("admin_key");
              setAuthed(false);
              setKey("");
              setInput("");
            }}
            className="btn-ghost text-[13px] text-relate-graphite"
          >
            Çıkış
          </button>
        </div>
      </header>
      {children}
    </div>
  );
}
