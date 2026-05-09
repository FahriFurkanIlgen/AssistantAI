"use client";
import { useEffect, useRef, useState } from "react";
import { api } from "@/lib/api";
import toast from "react-hot-toast";
import { QRCodeSVG } from "qrcode.react";

const SECTORS = [
  { value: "tattoo", label: "🎨 Dövme Stüdyosu" },
  { value: "doctor", label: "🏥 Klinik / Doktor" },
  { value: "beauty", label: "💅 Güzellik Merkezi" },
  { value: "general", label: "🏢 Diğer" },
];

export default function SettingsPage() {
  const [profile, setProfile] = useState<any>(null);
  const [saving, setSaving] = useState(false);
  const [form, setForm] = useState({
    ai_persona_name: "",
    ai_welcome_message_tr: "",
    ai_welcome_message_en: "",
    custom_ai_instructions: "",
    default_appointment_duration: 60,
    phone: "",
    address: "",
    city: "",
    instagram_handle: "",
  });

  useEffect(() => {
    api.getProfile().then((p) => {
      setProfile(p);
      setForm({
        ai_persona_name: p.ai_persona_name || "",
        ai_welcome_message_tr: p.ai_welcome_message_tr || "",
        ai_welcome_message_en: p.ai_welcome_message_en || "",
        custom_ai_instructions: p.custom_ai_instructions || "",
        default_appointment_duration: p.default_appointment_duration || 60,
        phone: p.phone || "",
        address: p.address || "",
        city: p.city || "",
        instagram_handle: p.instagram_handle || "",
      });
    });
  }, []);

  const handleSave = async () => {
    setSaving(true);
    try {
      await api.updateProfile(form);
      toast.success("Ayarlar kaydedildi ✅");
    } catch {
      toast.error("Kayıt başarısız");
    } finally {
      setSaving(false);
    }
  };

  const handleGoogleConnect = async () => {
    try {
      const data = await api.connectGoogle();
      window.location.href = data.auth_url;
    } catch {
      toast.error("Google bağlantısı başlatılamadı");
    }
  };

  const handleGoogleDisconnect = async () => {
    if (
      !confirm(
        "Google Takvim bağlantısını kaldırmak istediğinizden emin misiniz?",
      )
    )
      return;
    try {
      await api.disconnectGoogle();
      toast.success("Bağlantı kaldırıldı");
      setProfile((p: any) => ({ ...p, google_connected: false }));
    } catch {
      toast.error("Bağlantı kaldırılamadı");
    }
  };

  if (!profile) {
    return <div className="p-8 text-gray-400">Yükleniyor...</div>;
  }

  return (
    <div className="p-8 max-w-2xl">
      <h2 className="text-2xl font-bold text-gray-900 mb-6">Ayarlar</h2>

      {/* Google Calendar */}
      <div className="card mb-6">
        <h3 className="font-semibold text-gray-900 mb-4">📅 Google Takvim</h3>
        {profile.google_connected ? (
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="w-3 h-3 bg-green-500 rounded-full" />
              <p className="text-sm text-green-700 font-medium">Bağlandı</p>
            </div>
            <button
              onClick={handleGoogleDisconnect}
              className="text-sm text-red-500 hover:underline"
            >
              Bağlantıyı Kaldır
            </button>
          </div>
        ) : (
          <div>
            <p className="text-sm text-gray-500 mb-3">
              Google Takvim bağlayarak randevular otomatik olarak takviminize
              eklensin.
            </p>
            <button onClick={handleGoogleConnect} className="btn-primary">
              Google ile Bağlan
            </button>
          </div>
        )}
      </div>

      {/* AI Settings */}
      <div className="card mb-6 space-y-4">
        <h3 className="font-semibold text-gray-900">🤖 AI Asistan Ayarları</h3>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Asistan Adı
          </label>
          <input
            value={form.ai_persona_name}
            onChange={(e) =>
              setForm({ ...form, ai_persona_name: e.target.value })
            }
            className="input-field"
            placeholder="Örn: Mia, Alex, Randevu Asistanı"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Karşılama Mesajı (Türkçe)
          </label>
          <textarea
            value={form.ai_welcome_message_tr}
            onChange={(e) =>
              setForm({ ...form, ai_welcome_message_tr: e.target.value })
            }
            rows={2}
            className="input-field resize-none"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Karşılama Mesajı (İngilizce)
          </label>
          <textarea
            value={form.ai_welcome_message_en}
            onChange={(e) =>
              setForm({ ...form, ai_welcome_message_en: e.target.value })
            }
            rows={2}
            className="input-field resize-none"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Özel AI Talimatları{" "}
            <span className="text-gray-400 font-normal">(isteğe bağlı)</span>
          </label>
          <textarea
            value={form.custom_ai_instructions}
            onChange={(e) =>
              setForm({ ...form, custom_ai_instructions: e.target.value })
            }
            rows={3}
            placeholder="Örn: Minimum randevu süresi 2 saattir. Kapora alınmadan randevu kesinleşmez."
            className="input-field resize-none"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Varsayılan Randevu Süresi (dakika)
          </label>
          <input
            type="number"
            min={15}
            step={15}
            value={form.default_appointment_duration}
            onChange={(e) =>
              setForm({
                ...form,
                default_appointment_duration: parseInt(e.target.value),
              })
            }
            className="input-field w-32"
          />
        </div>
      </div>

      {/* Contact */}
      <div className="card mb-6 space-y-4">
        <h3 className="font-semibold text-gray-900">📍 İletişim Bilgileri</h3>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Telefon
            </label>
            <input
              value={form.phone}
              onChange={(e) => setForm({ ...form, phone: e.target.value })}
              className="input-field"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Şehir
            </label>
            <input
              value={form.city}
              onChange={(e) => setForm({ ...form, city: e.target.value })}
              className="input-field"
            />
          </div>
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Adres
          </label>
          <input
            value={form.address}
            onChange={(e) => setForm({ ...form, address: e.target.value })}
            className="input-field"
          />
        </div>
      </div>

      {/* Instagram Portfolio */}
      <div className="card mb-6 space-y-4">
        <h3 className="font-semibold text-gray-900">📷 Instagram Portfolyo</h3>
        <p className="text-sm text-gray-500">
          Instagram hesabınız public olmalıdır. AI asistan, müşterilere stil
          sorarken bu hesaptaki örnekleri referans olarak gösterir.
        </p>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Instagram Kullanıcı Adı
          </label>
          <div className="flex items-center gap-2">
            <span className="text-gray-400 text-sm font-medium">@</span>
            <input
              value={form.instagram_handle}
              onChange={(e) =>
                setForm({
                  ...form,
                  instagram_handle: e.target.value.replace("@", ""),
                })
              }
              placeholder="blackinktattoo"
              className="input-field"
            />
          </div>
          {form.instagram_handle && (
            <a
              href={`https://www.instagram.com/${form.instagram_handle}/`}
              target="_blank"
              rel="noreferrer"
              className="text-xs text-brand-600 hover:underline mt-1 inline-block"
            >
              instagram.com/{form.instagram_handle} ↗
            </a>
          )}
        </div>
      </div>

      {/* Chat link + QR */}
      <div className="card mb-6 bg-brand-50 border-brand-200">
        <h3 className="font-semibold text-gray-900 mb-2">
          🔗 Müşteri Chat Linkiniz
        </h3>
        <p className="text-sm text-gray-600 mb-2">
          Bu linki müşterilerinizle paylaşın:
        </p>
        <code className="text-sm bg-white border border-brand-200 rounded-lg px-3 py-2 block text-brand-700 break-all">
          {typeof window !== "undefined" ? window.location.origin : ""}/chat/
          {profile.slug}
        </code>

        {/* QR Code */}
        {typeof window !== "undefined" &&
          (() => {
            const chatUrl = `${window.location.origin}/chat/${profile.slug}`;
            return (
              <div className="mt-5 flex flex-col items-center gap-3">
                <QRCodeSVG
                  id="chat-qr-code"
                  value={chatUrl}
                  size={160}
                  bgColor="#ffffff"
                  fgColor="#1d1d1f"
                  level="M"
                  style={{ borderRadius: 8, padding: 8, background: "#fff" }}
                />
                <p className="text-xs text-gray-500">
                  QR kodu taratarak sohbete ulaşabilirler
                </p>
                <button
                  onClick={() => {
                    const svg = document.getElementById("chat-qr-code");
                    if (!svg) return;
                    const data = new XMLSerializer().serializeToString(svg);
                    const canvas = document.createElement("canvas");
                    canvas.width = 256;
                    canvas.height = 256;
                    const ctx = canvas.getContext("2d");
                    const img = new Image();
                    img.onload = () => {
                      ctx!.drawImage(img, 0, 0, 256, 256);
                      const a = document.createElement("a");
                      a.href = canvas.toDataURL("image/png");
                      a.download = `qr-${profile.slug}.png`;
                      a.click();
                    };
                    img.src =
                      "data:image/svg+xml;base64," +
                      btoa(unescape(encodeURIComponent(data)));
                  }}
                  className="text-xs text-brand-600 hover:underline"
                >
                  PNG olarak indir ↓
                </button>
              </div>
            );
          })()}
      </div>

      {/* OTP Email Info */}
      <div className="card mb-6 border-yellow-200 bg-yellow-50">
        <h3 className="font-semibold text-gray-900 mb-2">
          ✉️ Randevu İptal OTP E-postası
        </h3>
        <p className="text-sm text-gray-600 mb-2">
          Müşteriler chatbot üzerinden randevu iptali istediğinde, kayıtlı
          e-postalarına 6 haneli doğrulama kodu gönderilir.
        </p>
        <p className="text-sm text-gray-500">
          SMTP ayarları (host, kullanıcı adı, şifre) sunucudaki{" "}
          <code className="font-mono bg-white px-1 rounded border">.env</code>{" "}
          dosyasından yapılandırılır. Gmail kullanıyorsanız{" "}
          <strong>App Password</strong> oluşturup{" "}
          <code className="font-mono bg-white px-1 rounded border">
            SMTP_USER
          </code>{" "}
          ve{" "}
          <code className="font-mono bg-white px-1 rounded border">
            SMTP_PASSWORD
          </code>{" "}
          alanlarına ekleyin.
        </p>
      </div>

      <button
        onClick={handleSave}
        disabled={saving}
        className="btn-primary px-8 py-3 text-base"
      >
        {saving ? "Kaydediliyor..." : "Kaydet"}
      </button>
    </div>
  );
}
