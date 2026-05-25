"use client";
import { useState } from "react";
import Link from "next/link";
import toast from "react-hot-toast";
import { api } from "@/lib/api";
import { LogoLockup } from "@/components/brand/Logo";
import { SelectField } from "@/components/ui/SelectField";

const SECTORS = [
  { value: "tattoo", label: "🎨 Dövme Stüdyosu" },
  { value: "doctor", label: "🏥 Klinik / Doktor" },
  { value: "beauty", label: "💅 Güzellik Merkezi" },
  { value: "general", label: "🏢 Diğer" },
];

export default function RequestDemoPage() {
  const [loading, setLoading] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [kvkkAccepted, setKvkkAccepted] = useState(false);
  const [form, setForm] = useState({
    name: "",
    business_name: "",
    sector: "tattoo",
    phone: "",
    email: "",
    city: "",
    message: "",
  });

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>,
  ) => {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!kvkkAccepted) {
      toast.error(
        "Devam etmeden önce KVKK Aydınlatma Metnini okuyup onaylamanız gerekir.",
      );
      return;
    }
    setLoading(true);
    try {
      await api.submitDemoRequest(form);
      setSubmitted(true);
    } catch (err: any) {
      toast.error(err.response?.data?.detail || "Bir hata oluştu, lütfen tekrar deneyin.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="relative min-h-screen bg-relate-canvas flex flex-col items-center justify-center px-4 py-12">
      <div className="absolute inset-0 hero-wash pointer-events-none" aria-hidden />

      <div className="relative mb-10">
        <LogoLockup href="/" size={40} />
      </div>

      <div className="relative w-full max-w-[460px] card-feature !p-8">
        {submitted ? (
          <div className="text-center py-6">
            <div className="w-14 h-14 rounded-full bg-relate-emerald/10 flex items-center justify-center mx-auto mb-4">
              <svg className="w-7 h-7 text-relate-emerald" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
              </svg>
            </div>
            <h2 className="font-display font-semibold text-[22px] text-relate-ink tracking-tight mb-2">
              Talebiniz Alındı!
            </h2>
            <p className="text-[15px] text-relate-graphite leading-relaxed">
              En kısa sürede sizinle iletişime geçeceğiz. Teşekkür ederiz.
            </p>
            <Link
              href="/"
              className="inline-block mt-6 text-[14px] text-relate-signal hover:opacity-70 transition-opacity"
            >
              Ana sayfaya dön
            </Link>
          </div>
        ) : (
          <>
            <h1 className="font-display font-semibold text-[24px] text-relate-ink tracking-tight mb-1">
              Demo Talep Edin
            </h1>
            <p className="text-[15px] text-relate-graphite mb-7">
              Sizi tanımak ve size özel kurulum hakkında bilgi vermek için formu doldurun.
            </p>

            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-[13px] font-medium text-relate-ink mb-1.5">
                  Ad Soyad <span className="text-relate-signal">*</span>
                </label>
                <input
                  name="name"
                  value={form.name}
                  onChange={handleChange}
                  required
                  placeholder="Adınız Soyadınız"
                  className="input-field"
                />
              </div>

              <div>
                <label className="block text-[13px] font-medium text-relate-ink mb-1.5">
                  İşletme Adı <span className="text-relate-signal">*</span>
                </label>
                <input
                  name="business_name"
                  value={form.business_name}
                  onChange={handleChange}
                  required
                  placeholder="İşletmenizin adı"
                  className="input-field"
                />
              </div>

              <SelectField
                label="Sektör *"
                value={form.sector}
                options={SECTORS.map((s) => ({ value: s.value, label: s.label }))}
                onChange={(v) => setForm((f) => ({ ...f, sector: v }))}
              />

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-[13px] font-medium text-relate-ink mb-1.5">
                    Telefon <span className="text-relate-signal">*</span>
                  </label>
                  <input
                    name="phone"
                    value={form.phone}
                    onChange={handleChange}
                    required
                    placeholder="+90 5xx..."
                    className="input-field"
                  />
                </div>
                <div>
                  <label className="block text-[13px] font-medium text-relate-ink mb-1.5">
                    E-posta <span className="text-relate-signal">*</span>
                  </label>
                  <input
                    type="email"
                    name="email"
                    value={form.email}
                    onChange={handleChange}
                    required
                    placeholder="ornek@mail.com"
                    className="input-field"
                  />
                </div>
              </div>

              <div>
                <label className="block text-[13px] font-medium text-relate-ink mb-1.5">
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
                <label className="block text-[13px] font-medium text-relate-ink mb-1.5">
                  Notunuz
                </label>
                <textarea
                  name="message"
                  value={form.message}
                  onChange={handleChange}
                  rows={3}
                  placeholder="Bize iletmek istediğiniz bir şey var mı?"
                  className="input-field resize-none"
                />
              </div>

              <div className="rounded-xl border border-relate-border bg-relate-wash/60 px-4 py-3.5">
                <label className="flex items-start gap-3 cursor-pointer select-none">
                  <input
                    type="checkbox"
                    checked={kvkkAccepted}
                    onChange={(e) => setKvkkAccepted(e.target.checked)}
                    required
                    className="mt-0.5 w-4 h-4 rounded border-relate-border text-relate-signal focus:ring-2 focus:ring-relate-signal/40 cursor-pointer shrink-0"
                  />
                  <span className="text-[13px] leading-[1.55] text-relate-graphite">
                    Lütfen devam etmeden önce{" "}
                    <Link
                      href="/kvkk"
                      target="_blank"
                      className="text-relate-signal hover:opacity-70 transition-opacity font-medium underline underline-offset-2"
                    >
                      AssistantAI KVKK Aydınlatma Metnini
                    </Link>{" "}
                    okuyunuz. Kişisel verilerinizin metinde belirtilen amaçlar
                    doğrultusunda işlenmesini kabul ediyorum.
                    <span className="text-relate-signal ml-0.5">*</span>
                  </span>
                </label>
              </div>

              <button
                type="submit"
                disabled={loading || !kvkkAccepted}
                className="btn-primary w-full mt-2 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? "Gönderiliyor..." : "Demo Talep Et"}
              </button>
            </form>

            <p className="text-center text-[13px] text-relate-graphite mt-6">
              Hesabınız var mı?{" "}
              <Link href="/login" className="text-relate-signal hover:opacity-70 transition-opacity font-medium">
                Giriş yapın
              </Link>
            </p>
          </>
        )}
      </div>
    </div>
  );
}

