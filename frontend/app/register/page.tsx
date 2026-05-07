"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import toast from "react-hot-toast";
import { api } from "@/lib/api";

const SECTORS = [
  { value: "tattoo", label: "🎨 Dövme Stüdyosu" },
  { value: "doctor", label: "🏥 Klinik / Doktor" },
  { value: "beauty", label: "💅 Güzellik Merkezi" },
  { value: "general", label: "🏢 Diğer" },
];

export default function RegisterPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [form, setForm] = useState({
    name: "",
    slug: "",
    email: "",
    password: "",
    sector: "tattoo",
    city: "",
    phone: "",
  });

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>,
  ) => {
    const { name, value } = e.target;
    setForm((prev) => ({
      ...prev,
      [name]: value,
      // Auto-generate slug from name
      ...(name === "name"
        ? {
            slug: value
              .toLowerCase()
              .replace(/ğ/g, "g")
              .replace(/ü/g, "u")
              .replace(/ş/g, "s")
              .replace(/ı/g, "i")
              .replace(/ö/g, "o")
              .replace(/ç/g, "c")
              .replace(/[^a-z0-9]/g, "-")
              .replace(/-+/g, "-")
              .replace(/^-|-$/g, ""),
          }
        : {}),
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      const data = await api.register(form);
      if (typeof window !== "undefined") {
        localStorage.setItem("token", data.access_token);
        localStorage.setItem("business_slug", data.slug);
      }
      toast.success("Kayıt başarılı! Hoş geldiniz 🎉");
      router.push("/dashboard");
    } catch (err: any) {
      toast.error(
        err.response?.data?.detail || "Kayıt sırasında bir hata oluştu",
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-apple-gray flex flex-col items-center justify-center px-4 py-12">
      {/* Brand */}
      <Link href="/" className="font-display font-semibold text-[21px] text-apple-ink tracking-tight mb-10">
        AssistantAI
      </Link>

      <div className="w-full max-w-[420px] bg-white rounded-apple-lg border border-apple-border p-8">
        <h1 className="font-display font-semibold text-[24px] text-apple-ink tracking-tight mb-1">
          İşletmenizi Kaydedin
        </h1>
        <p className="text-[15px] text-apple-secondary mb-7">
          Ücretsiz hesap oluşturun, hemen başlayın.
        </p>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-[13px] font-medium text-apple-ink mb-1.5">
              İşletme Adı <span className="text-apple-blue">*</span>
            </label>
            <input
              name="name"
              value={form.name}
              onChange={handleChange}
              required
              placeholder="Örn: Black Ink Tattoo"
              className="input-field"
            />
          </div>

          <div>
            <label className="block text-[13px] font-medium text-apple-ink mb-1.5">
              URL Adresi <span className="text-apple-blue">*</span>{" "}
              <span className="text-apple-secondary font-normal">
                (/chat/<strong>{form.slug || "..."}</strong>)
              </span>
            </label>
            <input
              name="slug"
              value={form.slug}
              onChange={handleChange}
              required
              placeholder="black-ink-tattoo"
              pattern="[a-z0-9-]+"
              className="input-field"
            />
          </div>

          <div>
            <label className="block text-[13px] font-medium text-apple-ink mb-1.5">
              Sektör <span className="text-apple-blue">*</span>
            </label>
            <select
              name="sector"
              value={form.sector}
              onChange={handleChange}
              className="input-field"
            >
              {SECTORS.map((s) => (
                <option key={s.value} value={s.value}>
                  {s.label}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-[13px] font-medium text-apple-ink mb-1.5">
              E-posta <span className="text-apple-blue">*</span>
            </label>
            <input
              type="email"
              name="email"
              value={form.email}
              onChange={handleChange}
              required
              className="input-field"
            />
          </div>

          <div>
            <label className="block text-[13px] font-medium text-apple-ink mb-1.5">
              Şifre <span className="text-apple-blue">*</span>
            </label>
            <input
              type="password"
              name="password"
              value={form.password}
              onChange={handleChange}
              required
              minLength={8}
              className="input-field"
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-[13px] font-medium text-apple-ink mb-1.5">
                Şehir
              </label>
              <input
                name="city"
                value={form.city}
                onChange={handleChange}
                placeholder="İstanbul"
                className="input-field"
              />
            </div>
            <div>
              <label className="block text-[13px] font-medium text-apple-ink mb-1.5">
                Telefon
              </label>
              <input
                name="phone"
                value={form.phone}
                onChange={handleChange}
                placeholder="+90 5xx..."
                className="input-field"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="btn-primary w-full py-3 text-[15px] mt-2"
          >
            {loading ? "Kaydediliyor..." : "Devam Et"}
          </button>
        </form>

        <div className="apple-divider mt-6 pt-5">
          <p className="text-center text-[13px] text-apple-secondary">
            Zaten hesabınız var mı?{" "}
            <Link href="/login" className="text-apple-blueLink hover:underline font-medium">
              Giriş Yap
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
