"use client";

import Link from "next/link";
import { useState } from "react";

const CHANNELS = [
  {
    label: "Genel sorular",
    email: "hello@assistantai.app",
    description: "Demo, ortaklık ve genel konular.",
  },
  {
    label: "Teknik destek",
    email: "support@assistantai.app",
    description: "Mevcut işletme hesabınızla ilgili sorunlar.",
  },
  {
    label: "Satış",
    email: "sales@assistantai.app",
    description: "Fiyatlandırma ve kurumsal planlar.",
  },
  {
    label: "Gizlilik ve KVKK",
    email: "privacy@assistantai.app",
    description: "Veri talepleri ve gizlilik soruları.",
  },
  {
    label: "Hukuk",
    email: "legal@assistantai.app",
    description: "Sözleşme ve uyum soruları.",
  },
];

export default function ContactPage() {
  const [form, setForm] = useState({ name: "", email: "", subject: "", message: "" });
  const [sent, setSent] = useState(false);

  const mailtoHref = () => {
    const subject = encodeURIComponent(form.subject || "AssistantAI iletişim");
    const body = encodeURIComponent(
      `${form.message}\n\n— ${form.name}\n${form.email}`,
    );
    return `mailto:hello@assistantai.app?subject=${subject}&body=${body}`;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    window.location.href = mailtoHref();
    setSent(true);
  };

  return (
    <div className="min-h-screen bg-relate-canvas text-relate-ink">
      <header className="sticky top-0 z-10 bg-relate-canvas/90 backdrop-blur-sm border-b border-relate-border">
        <div className="max-w-relate mx-auto px-6 lg:px-10 h-14 flex items-center justify-between">
          <Link
            href="/"
            className="text-[15px] font-medium text-relate-ink hover:text-relate-signal transition-colors"
          >
            AssistantAI
          </Link>
          <Link
            href="/status"
            className="text-[13px] text-relate-graphite hover:text-relate-signal transition-colors"
          >
            Sistem durumu →
          </Link>
        </div>
      </header>

      <main className="max-w-relate mx-auto px-6 lg:px-10 py-16">
        <div className="max-w-[720px]">
          <h1 className="text-[32px] sm:text-[40px] font-semibold tracking-[-0.022em] text-relate-ink mb-3">
            İletişim
          </h1>
          <p className="text-relate-ash text-[15px] leading-[1.7] mb-12">
            Sorularınız, demo talepleri veya geri bildirimleriniz için bize
            ulaşın. Genellikle 1 iş günü içinde yanıt veriyoruz.
          </p>
        </div>

        <div className="grid lg:grid-cols-[1fr_360px] gap-10">
          {/* Form */}
          <section className="card p-6 sm:p-8">
            <h2 className="text-[20px] font-semibold tracking-[-0.015em] text-relate-ink mb-1">
              Bize yazın
            </h2>
            <p className="text-[13px] text-relate-graphite mb-6">
              Form gönderildiğinde varsayılan e-posta uygulamanız açılır.
            </p>

            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="grid sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-[13px] font-medium text-relate-ink mb-1.5">
                    Ad Soyad
                  </label>
                  <input
                    required
                    value={form.name}
                    onChange={(e) => setForm({ ...form, name: e.target.value })}
                    className="input-field"
                    placeholder="Adınız Soyadınız"
                  />
                </div>
                <div>
                  <label className="block text-[13px] font-medium text-relate-ink mb-1.5">
                    E-posta
                  </label>
                  <input
                    required
                    type="email"
                    value={form.email}
                    onChange={(e) => setForm({ ...form, email: e.target.value })}
                    className="input-field"
                    placeholder="siz@ornek.com"
                  />
                </div>
              </div>

              <div>
                <label className="block text-[13px] font-medium text-relate-ink mb-1.5">
                  Konu
                </label>
                <input
                  required
                  value={form.subject}
                  onChange={(e) => setForm({ ...form, subject: e.target.value })}
                  className="input-field"
                  placeholder="Demo talebi, soru, geri bildirim..."
                />
              </div>

              <div>
                <label className="block text-[13px] font-medium text-relate-ink mb-1.5">
                  Mesaj
                </label>
                <textarea
                  required
                  rows={6}
                  value={form.message}
                  onChange={(e) => setForm({ ...form, message: e.target.value })}
                  className="input-field resize-y min-h-[140px]"
                  placeholder="Bize neden ulaştığınızı kısaca anlatın..."
                />
              </div>

              <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 pt-2">
                <p className="text-[12px] text-relate-ash">
                  Gönderim ile birlikte{" "}
                  <Link href="/privacy-policy" className="text-relate-signal underline underline-offset-2">
                    Gizlilik Politikamızı
                  </Link>{" "}
                  kabul etmiş olursunuz.
                </p>
                <button type="submit" className="btn-primary">
                  E-posta uygulamasını aç
                </button>
              </div>

              {sent && (
                <p className="text-[13px] text-relate-emerald">
                  E-posta uygulamanız açıldı. Açılmadıysa{" "}
                  <a
                    href="mailto:hello@assistantai.app"
                    className="underline underline-offset-2"
                  >
                    hello@assistantai.app
                  </a>{" "}
                  adresine doğrudan yazabilirsiniz.
                </p>
              )}
            </form>
          </section>

          {/* Aside: kanallar */}
          <aside className="space-y-6">
            <section className="card p-6">
              <h3 className="text-[16px] font-semibold text-relate-ink mb-4">
                Telefon
              </h3>
              <a
                href="tel:+905454999667"
                className="text-[18px] font-semibold text-relate-signal hover:opacity-80 num-mono"
              >
                +90 545 499 96 67
              </a>
              <p className="text-[12px] text-relate-ash mt-2">
                Hafta içi 09:00–18:00 (UTC+3). WhatsApp üzerinden de yazılabilir.
              </p>
            </section>

            <section className="card p-6">
              <h3 className="text-[16px] font-semibold text-relate-ink mb-4">
                Doğrudan kanallar
              </h3>
              <ul className="space-y-4">
                {CHANNELS.map((c) => (
                  <li key={c.email}>
                    <div className="text-[13px] text-relate-graphite">
                      {c.label}
                    </div>
                    <a
                      href={`mailto:${c.email}`}
                      className="text-[14px] font-medium text-relate-signal hover:opacity-80 underline underline-offset-2"
                    >
                      {c.email}
                    </a>
                    <div className="text-[12px] text-relate-ash mt-0.5">
                      {c.description}
                    </div>
                  </li>
                ))}
              </ul>
            </section>

            <section className="card-gray p-6 rounded-lg">
              <h3 className="text-[15px] font-semibold text-relate-ink mb-2">
                Yardım merkezi
              </h3>
              <p className="text-[13px] text-relate-graphite leading-[1.65]">
                Sıkça sorulan sorular, entegrasyon adımları ve sürüm notları
                için panelinizdeki <strong>Bilgi Tabanı</strong> bölümünü ve{" "}
                <Link href="/status" className="text-relate-signal underline underline-offset-2">
                  durum sayfasını
                </Link>{" "}
                takip edin.
              </p>
            </section>
          </aside>
        </div>
      </main>

      <footer className="border-t border-relate-border mt-16 py-8">
        <div className="max-w-relate mx-auto px-6 lg:px-10 text-center text-[13px] text-relate-ash">
          © {new Date().getFullYear()} AssistantAI. Tüm hakları saklıdır.
        </div>
      </footer>
    </div>
  );
}
