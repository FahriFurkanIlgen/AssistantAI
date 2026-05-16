"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import toast from "react-hot-toast";
import { api } from "@/lib/api";
import { LogoLockup } from "@/components/brand/Logo";

export default function LoginPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [form, setForm] = useState({ email: "", password: "" });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      const data = await api.login(form.email, form.password);
      if (typeof window !== "undefined") {
        localStorage.setItem("token", data.access_token);
        localStorage.setItem("business_slug", data.slug);
      }
      toast.success("Giriş başarılı!");
      router.push("/dashboard");
    } catch (err: any) {
      toast.error(err.response?.data?.detail || "E-posta veya şifre hatalı");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="relative min-h-screen bg-relate-canvas flex flex-col items-center justify-center px-4">
      <div className="absolute inset-0 hero-wash pointer-events-none" aria-hidden />
      {/* Brand */}
      <div className="relative mb-10">
        <LogoLockup href="/" size={40} />
      </div>

      <div className="relative w-full max-w-[380px] card-feature !p-8">
        <h1 className="font-display font-semibold text-[24px] text-apple-ink tracking-tight mb-1">
          Giriş Yap
        </h1>
        <p className="text-[15px] text-apple-secondary mb-7">
          Hesabınıza erişin
        </p>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-[13px] font-medium text-apple-ink mb-1.5">
              E-posta
            </label>
            <input
              type="email"
              value={form.email}
              onChange={(e) => setForm({ ...form, email: e.target.value })}
              required
              placeholder="ornek@sirket.com"
              className="input-field"
            />
          </div>
          <div>
            <label className="block text-[13px] font-medium text-apple-ink mb-1.5">
              Şifre
            </label>
            <input
              type="password"
              value={form.password}
              onChange={(e) => setForm({ ...form, password: e.target.value })}
              required
              className="input-field"
            />
          </div>
          <button
            type="submit"
            disabled={loading}
            className="btn-primary w-full py-3 text-[15px] mt-2"
          >
            {loading ? "Giriş yapılıyor..." : "Devam Et"}
          </button>
        </form>

        <div className="apple-divider mt-6 pt-5">
          <p className="text-center text-[13px] text-apple-secondary">
            Hesabınız yok mu?{" "}
            <Link href="/register" className="text-apple-blueLink hover:underline font-medium">
              Kayıt Ol
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
