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
  const [waStatus, setWaStatus] = useState<{
    enabled: boolean;
    phone_number_id?: string | null;
    display_phone?: string | null;
    access_token_preview?: string | null;
    verify_token_set?: boolean;
    webhook_path?: string;
  } | null>(null);
  const [waForm, setWaForm] = useState({
    enabled: false,
    phone_number_id: "",
    display_phone: "",
    access_token: "", // empty = keep existing
    verify_token: "", // empty = keep existing
  });
  const [waTestTo, setWaTestTo] = useState("");
  const [waSaving, setWaSaving] = useState(false);
  const [waTesting, setWaTesting] = useState(false);
  const [form, setForm] = useState({
    ai_persona_name: "",
    ai_welcome_message_tr: "",
    ai_welcome_message_en: "",
    ai_welcome_message_ru: "",
    ai_welcome_message_de: "",
    ai_welcome_message_ar: "",
    custom_ai_instructions: "",
    tts_voice: "nova",
    default_appointment_duration: 60,
    phone: "",
    address: "",
    city: "",
    instagram_handle: "",
    suggested_questions_text: "", // one question per line
  });

  useEffect(() => {
    api.getProfile().then((p) => {
      setProfile(p);
      setForm({
        ai_persona_name: p.ai_persona_name || "",
        ai_welcome_message_tr: p.ai_welcome_message_tr || "",
        ai_welcome_message_en: p.ai_welcome_message_en || "",
        ai_welcome_message_ru: p.ai_welcome_message_ru || "",
        ai_welcome_message_de: p.ai_welcome_message_de || "",
        ai_welcome_message_ar: p.ai_welcome_message_ar || "",
        custom_ai_instructions: p.custom_ai_instructions || "",
        tts_voice: p.tts_voice || "nova",
        default_appointment_duration: p.default_appointment_duration || 60,
        phone: p.phone || "",
        address: p.address || "",
        city: p.city || "",
        instagram_handle: p.instagram_handle || "",
        suggested_questions_text: Array.isArray(p.suggested_questions)
          ? p.suggested_questions.join("\n")
          : "",
      });
    });
    api
      .getWhatsAppStatus()
      .then((s) => {
        setWaStatus(s);
        setWaForm({
          enabled: !!s.enabled,
          phone_number_id: s.phone_number_id || "",
          display_phone: s.display_phone || "",
          access_token: "",
          verify_token: "",
        });
      })
      .catch(() => {});
  }, []);

  const handleSave = async () => {
    setSaving(true);
    try {
      const { suggested_questions_text, ...rest } = form;
      const suggested_questions = suggested_questions_text
        .split("\n")
        .map((s) => s.trim())
        .filter(Boolean)
        .slice(0, 8);
      await api.updateProfile({ ...rest, suggested_questions });
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

  const saveWhatsApp = async () => {
    setWaSaving(true);
    try {
      const payload: Record<string, unknown> = {
        whatsapp: {
          enabled: waForm.enabled,
          phone_number_id: waForm.phone_number_id || null,
          display_phone: waForm.display_phone || null,
          // Empty strings tell the backend to keep the stored secret.
          access_token: waForm.access_token,
          verify_token: waForm.verify_token,
        },
      };
      await api.updateProfile(payload);
      toast.success("WhatsApp ayarları kaydedildi ✅");
      const fresh = await api.getWhatsAppStatus();
      setWaStatus(fresh);
      setWaForm((f) => ({ ...f, access_token: "", verify_token: "" }));
    } catch {
      toast.error("WhatsApp ayarları kaydedilemedi");
    } finally {
      setWaSaving(false);
    }
  };

  const sendWhatsAppTest = async () => {
    if (!waTestTo.trim()) {
      toast.error("Hedef telefon numarası girin (örn. +905551112233)");
      return;
    }
    setWaTesting(true);
    try {
      await api.sendWhatsAppTest(waTestTo.trim());
      toast.success("Test mesajı gönderildi ✉️");
    } catch (e: any) {
      toast.error(e?.response?.data?.detail || "Test mesajı gönderilemedi");
    } finally {
      setWaTesting(false);
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

      {/* WhatsApp Cloud API */}
      <div className="card mb-6 space-y-4">
        <div className="flex items-start justify-between gap-3">
          <div>
            <h3 className="font-semibold text-gray-900">
              💬 WhatsApp Köprüsü
            </h3>
            <p className="text-xs text-gray-500 mt-1">
              Meta WhatsApp Cloud API ile müşterileriniz size WhatsApp&apos;tan
              yazdığında asistanınız otomatik cevap verir.
            </p>
          </div>
          <label className="inline-flex items-center gap-2 cursor-pointer shrink-0">
            <input
              type="checkbox"
              checked={waForm.enabled}
              onChange={(e) =>
                setWaForm({ ...waForm, enabled: e.target.checked })
              }
              className="w-4 h-4"
            />
            <span className="text-sm text-gray-700">Etkin</span>
          </label>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1">
              Phone Number ID
            </label>
            <input
              value={waForm.phone_number_id}
              onChange={(e) =>
                setWaForm({ ...waForm, phone_number_id: e.target.value })
              }
              placeholder="123456789012345"
              className="input-field"
            />
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1">
              Görünür Telefon
            </label>
            <input
              value={waForm.display_phone}
              onChange={(e) =>
                setWaForm({ ...waForm, display_phone: e.target.value })
              }
              placeholder="+90 555 111 22 33"
              className="input-field"
            />
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1">
              Access Token{" "}
              {waStatus?.access_token_preview && (
                <span className="text-gray-400 font-normal">
                  (kayıtlı: {waStatus.access_token_preview} — değiştirmek için
                  yeni token yapıştırın)
                </span>
              )}
            </label>
            <input
              type="password"
              value={waForm.access_token}
              onChange={(e) =>
                setWaForm({ ...waForm, access_token: e.target.value })
              }
              placeholder="EAAB...permanent token"
              className="input-field"
              autoComplete="new-password"
            />
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1">
              Verify Token{" "}
              {waStatus?.verify_token_set && (
                <span className="text-gray-400 font-normal">(kayıtlı)</span>
              )}
            </label>
            <input
              type="password"
              value={waForm.verify_token}
              onChange={(e) =>
                setWaForm({ ...waForm, verify_token: e.target.value })
              }
              placeholder="kendi belirlediğiniz rastgele string"
              className="input-field"
              autoComplete="new-password"
            />
          </div>
        </div>

        {waStatus?.webhook_path && (
          <div className="rounded-md bg-gray-50 border border-gray-200 px-3 py-2 text-xs text-gray-600">
            <p className="font-medium text-gray-700 mb-1">Meta&apos;ya gireceğiniz Webhook URL</p>
            <code className="font-mono text-[11px] break-all">
              {typeof window !== "undefined" ? window.location.origin : ""}
              {waStatus.webhook_path}
            </code>
            <p className="mt-2 text-[11px] text-gray-500">
              Meta App → WhatsApp → Configuration ekranında bu URL&apos;yi ve
              yukarıdaki <strong>Verify Token</strong>&apos;ı girin, sonra{" "}
              <code>messages</code> alanına abone olun.
            </p>
          </div>
        )}

        <div className="flex flex-wrap items-center gap-2">
          <button
            onClick={saveWhatsApp}
            disabled={waSaving}
            className="btn-primary"
          >
            {waSaving ? "Kaydediliyor…" : "WhatsApp Ayarlarını Kaydet"}
          </button>
        </div>

        {waStatus?.enabled && (
          <div className="border-t border-gray-100 pt-4">
            <p className="text-xs font-medium text-gray-700 mb-2">
              Test mesajı
            </p>
            <div className="flex flex-wrap gap-2">
              <input
                value={waTestTo}
                onChange={(e) => setWaTestTo(e.target.value)}
                placeholder="+905551112233"
                className="input-field flex-1 min-w-[180px]"
              />
              <button
                onClick={sendWhatsAppTest}
                disabled={waTesting}
                className="btn-secondary"
              >
                {waTesting ? "Gönderiliyor…" : "Test mesajı gönder"}
              </button>
            </div>
            <p className="text-[11px] text-gray-500 mt-1">
              Not: Hedef numaranın son 24 saat içinde işletme numaranıza mesaj
              atmış olması gerekir (Meta&apos;nın customer-service-window
              kuralı). Geliştirme için kendi telefonunuzdan WABA numaranıza
              önce bir &quot;merhaba&quot; gönderin.
            </p>
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
            Karşılama Mesajı (Rusça)
          </label>
          <textarea
            value={form.ai_welcome_message_ru}
            onChange={(e) =>
              setForm({ ...form, ai_welcome_message_ru: e.target.value })
            }
            rows={2}
            className="input-field resize-none"
            placeholder="Здравствуйте! Чем я могу вам помочь?"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Karşılama Mesajı (Almanca)
          </label>
          <textarea
            value={form.ai_welcome_message_de}
            onChange={(e) =>
              setForm({ ...form, ai_welcome_message_de: e.target.value })
            }
            rows={2}
            className="input-field resize-none"
            placeholder="Hallo! Wie kann ich Ihnen helfen?"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Karşılama Mesajı (Arapça)
          </label>
          <textarea
            value={form.ai_welcome_message_ar}
            onChange={(e) =>
              setForm({ ...form, ai_welcome_message_ar: e.target.value })
            }
            rows={2}
            dir="rtl"
            lang="ar"
            className="input-field resize-none"
            placeholder="مرحبًا! كيف يمكنني مساعدتك؟"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Önerilen Sorular{" "}
            <span className="text-gray-400 font-normal">
              (her satıra bir soru, en fazla 8)
            </span>
          </label>
          <textarea
            value={form.suggested_questions_text}
            onChange={(e) =>
              setForm({ ...form, suggested_questions_text: e.target.value })
            }
            rows={5}
            className="input-field resize-none font-mono text-sm"
            placeholder={"Hangi hizmetleri sunuyorsunuz?\nYarın için randevu alabilir miyim?\nFiyatlarınız nedir?\nÇalışma saatleriniz nedir?"}
          />
          <p className="text-xs text-gray-500 mt-1">
            Müşterinin sohbete başlarken görmesini istediğiniz örnek sorular. Boş bırakırsanız hiç gösterilmez.
          </p>
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
            Asistan Sesi (TTS){" "}
            <span className="text-gray-400 font-normal">
              – sesli yanıtlar bu sesle okunur
            </span>
          </label>
          <div className="flex flex-wrap items-center gap-2">
            <select
              value={form.tts_voice}
              onChange={(e) =>
                setForm({ ...form, tts_voice: e.target.value })
              }
              className="input-field max-w-xs"
            >
              <option value="nova">Nova (kadın, Türkçe öneri)</option>
              <option value="shimmer">Shimmer (kadın, yumuşak)</option>
              <option value="alloy">Alloy (nötr)</option>
              <option value="echo">Echo (erkek, sakin)</option>
              <option value="fable">Fable (erkek, anlatıcı)</option>
              <option value="onyx">Onyx (erkek, derin)</option>
            </select>
            <button
              type="button"
              onClick={async () => {
                if (!profile?.slug) return;
                try {
                  const url = await api.synthesizeSpeech(
                    profile.slug,
                    "Merhaba, ben asistanınız. Bu seçtiğiniz sesin örneğidir.",
                    form.tts_voice,
                  );
                  const audio = new Audio(url);
                  audio.play();
                } catch {
                  toast.error("Ses örneği alınamadı");
                }
              }}
              className="btn-secondary"
            >
              ▶ Test sesi
            </button>
          </div>
          <p className="text-xs text-gray-500 mt-1">
            “Test sesi” butonu seçili sesin nasıl duyulacağını hemen dinletir.
            Değişikliği kaydetmeyi unutmayın.
          </p>
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
