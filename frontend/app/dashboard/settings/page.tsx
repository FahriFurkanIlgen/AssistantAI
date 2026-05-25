"use client";
import { useEffect, useRef, useState } from "react";
import { api } from "@/lib/api";
import toast from "react-hot-toast";
import { QRCodeSVG } from "qrcode.react";
import { SelectField } from "@/components/ui/SelectField";

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
  const [igStatus, setIgStatus] = useState<{
    enabled: boolean;
    ig_user_id?: string | null;
    page_id?: string | null;
    ig_username?: string | null;
    access_token_preview?: string | null;
    verify_token_set?: boolean;
    app_secret_set?: boolean;
    webhook_path?: string;
  } | null>(null);
  const [igForm, setIgForm] = useState({
    enabled: false,
    ig_user_id: "",
    page_id: "",
    ig_username: "",
    access_token: "", // empty = keep existing
    verify_token: "", // empty = keep existing
    app_secret: "",   // empty = keep existing
  });
  const [igTestTo, setIgTestTo] = useState("");
  const [igSaving, setIgSaving] = useState(false);
  const [igTesting, setIgTesting] = useState(false);
  const [igRefreshing, setIgRefreshing] = useState(false);
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
    logo_url: "",
    chat_theme: "light",
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
        logo_url: p.logo_url || "",
        chat_theme: p.chat_theme === "dark" ? "dark" : "light",
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
    api
      .getInstagramStatus()
      .then((s) => {
        setIgStatus(s);
        setIgForm({
          enabled: !!s.enabled,
          ig_user_id: s.ig_user_id || "",
          page_id: s.page_id || "",
          ig_username: s.ig_username || "",
          access_token: "",
          verify_token: "",
          app_secret: "",
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

  const saveInstagram = async () => {
    setIgSaving(true);
    try {
      const payload: Record<string, unknown> = {
        instagram: {
          enabled: igForm.enabled,
          ig_user_id: igForm.ig_user_id || null,
          ig_username: igForm.ig_username || null,
          // Empty string = backend keeps stored secret.
          access_token: igForm.access_token,
          verify_token: igForm.verify_token,
          app_secret: igForm.app_secret,
        },
      };
      await api.updateProfile(payload);
      toast.success("Instagram ayarları kaydedildi ✅");
      const fresh = await api.getInstagramStatus();
      setIgStatus(fresh);
      setIgForm((f) => ({
        ...f,
        access_token: "",
        verify_token: "",
        app_secret: "",
      }));
    } catch {
      toast.error("Instagram ayarları kaydedilemedi");
    } finally {
      setIgSaving(false);
    }
  };

  const sendInstagramTest = async () => {
    if (!igTestTo.trim()) {
      toast.error("Hedef IGSID (Instagram-scoped user ID) girin");
      return;
    }
    setIgTesting(true);
    try {
      await api.sendInstagramTest(igTestTo.trim());
      toast.success("Test DM gönderildi ✉️");
    } catch (e: any) {
      toast.error(e?.response?.data?.detail || "Test DM gönderilemedi");
    } finally {
      setIgTesting(false);
    }
  };

  const refreshInstagramMedia = async () => {
    setIgRefreshing(true);
    try {
      const res = await api.refreshInstagramMedia();
      toast.success(`Graph API ile ${res?.count ?? 0} medya çekildi ✅`);
    } catch (e: any) {
      toast.error(e?.response?.data?.detail || "Medya çekilemedi");
    } finally {
      setIgRefreshing(false);
    }
  };

  const [igConnecting, setIgConnecting] = useState(false);
  const connectInstagramOAuth = async () => {
    setIgConnecting(true);
    try {
      const { authorize_url } = await api.startInstagramOAuth();
      // Aynı sekmede tam-sayfa redirect — popup blocker by-pass
      window.location.href = authorize_url;
    } catch (e: any) {
      setIgConnecting(false);
      toast.error(
        e?.response?.data?.detail || "OAuth başlatılamadı",
      );
    }
  };

  // OAuth callback'ten dönüşte ?ig=connected&u=... veya ?ig=error&msg=... oku
  useEffect(() => {
    if (typeof window === "undefined") return;
    const params = new URLSearchParams(window.location.search);
    const ig = params.get("ig");
    if (!ig) return;
    const msg = params.get("msg") || "";
    const u = params.get("u") || "";
    if (ig === "connected") {
      toast.success(`Instagram bağlandı: @${u} ✅`);
      // Status'u yenile
      api.getInstagramStatus().then((fresh) => {
        setIgStatus(fresh);
        setIgForm((f) => ({
          ...f,
          enabled: true,
          ig_user_id: fresh.ig_user_id || f.ig_user_id,
          ig_username: fresh.ig_username || f.ig_username,
        }));
      }).catch(() => {});
    } else if (ig === "error") {
      toast.error(msg || "Instagram bağlantısı başarısız");
    }
    // Query'yi temizle
    const url = new URL(window.location.href);
    url.searchParams.delete("ig");
    url.searchParams.delete("msg");
    url.searchParams.delete("u");
    window.history.replaceState({}, "", url.toString());
  }, []);

  if (!profile) {
    return <div className="p-8 text-gray-400">Yükleniyor...</div>;
  }

  return (
    <div className="p-4 sm:p-6 md:p-8 max-w-2xl">
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

      {/* Instagram Graph API + DM */}
      <div className="card mb-6 space-y-4">
        <div className="flex items-start justify-between gap-3">
          <div>
            <h3 className="font-semibold text-gray-900">
              📸 Instagram Köprüsü
            </h3>
            <p className="text-xs text-gray-500 mt-1">
              Meta&apos;nın yeni <strong>Instagram API with Instagram Login</strong>
              {" "}akışı — Facebook Page gerekmez. Portfolyo otomatik çekilir,
              gelen DM&apos;lere asistanınız cevap verir.
            </p>
          </div>
          <label className="inline-flex items-center gap-2 cursor-pointer shrink-0">
            <input
              type="checkbox"
              checked={igForm.enabled}
              onChange={(e) =>
                setIgForm({ ...igForm, enabled: e.target.checked })
              }
              className="w-4 h-4"
            />
            <span className="text-sm text-gray-700">Etkin</span>
          </label>
        </div>

        {/* Tek tık Calendly-stili bağlantı */}
        <div className="rounded-md border border-relate-border bg-relate-wash p-3">
          <div className="flex items-center justify-between gap-3 flex-wrap">
            <div>
              <p className="text-sm font-medium text-relate-ink">
                Tek tıkla bağlan
              </p>
              <p className="text-[11px] text-gray-500">
                Instagram&apos;a gidip Allow tıklayın — token, kullanıcı ID
                ve webhook subscription otomatik kurulur.
              </p>
            </div>
            <button
              onClick={connectInstagramOAuth}
              disabled={igConnecting}
              className="btn-primary text-sm"
            >
              {igConnecting
                ? "Bağlanıyor…"
                : igStatus?.ig_username
                ? `Yeniden bağla (@${igStatus.ig_username})`
                : "📸 Instagram'a Bağlan"}
            </button>
          </div>
        </div>

        <details className="text-xs">
          <summary className="cursor-pointer text-gray-600 hover:text-gray-800">
            Manuel kurulum (gelişmiş)
          </summary>
          <div className="mt-3 grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div>
            <label className="block text-xs font-medium text-gray-600 mb-1">
              Instagram User Access Token{" "}
              {igStatus?.access_token_preview && (
                <span className="text-gray-400 font-normal">
                  (kayıtlı: {igStatus.access_token_preview})
                </span>
              )}
            </label>
            <input
              type="password"
              value={igForm.access_token}
              onChange={(e) =>
                setIgForm({ ...igForm, access_token: e.target.value })
              }
              placeholder="IGAA...kalıcı IG User token"
              className="input-field"
              autoComplete="new-password"
            />
            <p className="text-[11px] text-gray-500 mt-1">
              Meta App → Instagram → API setup → Generate Token. Token
              kaydedildiğinde <code>ig_user_id</code> ve kullanıcı adı otomatik
              doldurulur.
            </p>
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1">
              Instagram Kullanıcı Adı
            </label>
            <input
              value={igForm.ig_username}
              onChange={(e) =>
                setIgForm({ ...igForm, ig_username: e.target.value })
              }
              placeholder="nimbus_ink (otomatik doldurulur)"
              className="input-field"
            />
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1">
              Instagram Business Account ID
              <span className="text-gray-400 font-normal">
                {" "}(token kaydedilince otomatik)
              </span>
            </label>
            <input
              value={igForm.ig_user_id}
              onChange={(e) =>
                setIgForm({ ...igForm, ig_user_id: e.target.value })
              }
              placeholder="17841400000000000"
              className="input-field"
            />
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1">
              Verify Token{" "}
              {igStatus?.verify_token_set && (
                <span className="text-gray-400 font-normal">(kayıtlı)</span>
              )}
            </label>
            <input
              type="password"
              value={igForm.verify_token}
              onChange={(e) =>
                setIgForm({ ...igForm, verify_token: e.target.value })
              }
              placeholder="kendi belirlediğiniz rastgele string"
              className="input-field"
              autoComplete="new-password"
            />
          </div>
          <div className="sm:col-span-2">
            <label className="block text-xs font-medium text-gray-600 mb-1">
              App Secret{" "}
              {igStatus?.app_secret_set && (
                <span className="text-gray-400 font-normal">(kayıtlı)</span>
              )}
            </label>
            <input
              type="password"
              value={igForm.app_secret}
              onChange={(e) =>
                setIgForm({ ...igForm, app_secret: e.target.value })
              }
              placeholder="X-Hub-Signature-256 doğrulaması için (opsiyonel)"
              className="input-field"
              autoComplete="new-password"
            />
          </div>
        </div>
        </details>

        {igStatus?.webhook_path && (
          <div className="rounded-md bg-gray-50 border border-gray-200 px-3 py-2 text-xs text-gray-600">
            <p className="font-medium text-gray-700 mb-1">
              Meta&apos;ya gireceğiniz Webhook URL
            </p>
            <code className="font-mono text-[11px] break-all">
              {typeof window !== "undefined" ? window.location.origin : ""}
              {igStatus.webhook_path}
            </code>
            <p className="mt-2 text-[11px] text-gray-500">
              Meta App → Instagram → Webhooks ekranında bu URL&apos;yi ve
              yukarıdaki <strong>Verify Token</strong>&apos;ı girin, sonra{" "}
              <code>messages</code> ve <code>messaging_postbacks</code>{" "}
              alanlarına abone olun. Önce hesabınız <strong>Professional</strong>{" "}
              (Business/Creator) olmalı.
            </p>
          </div>
        )}

        <div className="flex flex-wrap items-center gap-2">
          <button
            onClick={saveInstagram}
            disabled={igSaving}
            className="btn-primary"
          >
            {igSaving ? "Kaydediliyor…" : "Instagram Ayarlarını Kaydet"}
          </button>
          {igStatus?.enabled && (
            <button
              onClick={refreshInstagramMedia}
              disabled={igRefreshing}
              className="btn-secondary"
            >
              {igRefreshing ? "Çekiliyor…" : "Portfolyoyu Test Et"}
            </button>
          )}
        </div>

        {igStatus?.enabled && (
          <div className="border-t border-gray-100 pt-4">
            <p className="text-xs font-medium text-gray-700 mb-2">Test DM</p>
            <div className="flex flex-wrap gap-2">
              <input
                value={igTestTo}
                onChange={(e) => setIgTestTo(e.target.value)}
                placeholder="IGSID (Instagram-scoped user ID)"
                className="input-field flex-1 min-w-[180px]"
              />
              <button
                onClick={sendInstagramTest}
                disabled={igTesting}
                className="btn-secondary"
              >
                {igTesting ? "Gönderiliyor…" : "Test DM gönder"}
              </button>
            </div>
            <p className="text-[11px] text-gray-500 mt-1">
              Not: Instagram&apos;da DM göndermek için karşı tarafın son 24 saat
              içinde size DM atmış olması gerekir. IGSID&apos;yi webhook
              loglarından alabilirsiniz.
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
            Asistan Logosu / Avatarı
          </label>
          <div className="flex items-start gap-4">
            <div className="w-16 h-16 rounded-full overflow-hidden border border-relate-border bg-relate-wash flex items-center justify-center shrink-0">
              {form.logo_url ? (
                // eslint-disable-next-line @next/next/no-img-element
                <img
                  src={form.logo_url}
                  alt="Logo önizleme"
                  className="w-full h-full object-cover"
                />
              ) : (
                <span className="text-relate-ash text-xs">Logo</span>
              )}
            </div>
            <div className="flex-1 space-y-2">
              <input
                type="file"
                accept="image/png,image/jpeg,image/webp,image/svg+xml"
                onChange={async (e) => {
                  const file = e.target.files?.[0];
                  if (!file) return;
                  if (file.size > 600_000) {
                    toast.error(
                      "Görsel 600 KB altında olmalı. Lütfen sıkıştırın.",
                    );
                    e.target.value = "";
                    return;
                  }
                  const reader = new FileReader();
                  reader.onload = () => {
                    setForm((f) => ({
                      ...f,
                      logo_url: String(reader.result || ""),
                    }));
                  };
                  reader.readAsDataURL(file);
                }}
                className="block text-sm text-gray-700 file:mr-3 file:px-3 file:py-1.5 file:rounded-lg file:border file:border-relate-border file:bg-white file:text-relate-ink file:text-xs file:font-medium file:cursor-pointer hover:file:bg-relate-wash"
              />
              <input
                value={form.logo_url}
                onChange={(e) =>
                  setForm({ ...form, logo_url: e.target.value })
                }
                className="input-field text-xs"
                placeholder="veya doğrudan https:// URL yapıştırın"
              />
              {form.logo_url && (
                <button
                  type="button"
                  onClick={() => setForm({ ...form, logo_url: "" })}
                  className="text-xs text-relate-coral hover:underline"
                >
                  Logoyu kaldır
                </button>
              )}
              <p className="text-[11px] text-gray-500">
                Kare görsel önerilir (PNG/JPG/WebP/SVG, max 600 KB). Chat
                karşılama dairesinde ve mesaj avatarlarında kullanılır.
              </p>
            </div>
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Chat Teması
          </label>
          <div className="grid grid-cols-2 gap-3">
            {(["light", "dark"] as const).map((opt) => {
              const active = form.chat_theme === opt;
              return (
                <button
                  key={opt}
                  type="button"
                  onClick={() => setForm({ ...form, chat_theme: opt })}
                  className={`text-left rounded-lg border px-4 py-3 transition-all ${
                    active
                      ? "border-relate-signal ring-2 ring-relate-signal/30 bg-relate-wash"
                      : "border-relate-border hover:border-relate-steel"
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <div
                      className={`w-10 h-10 rounded-md border ${
                        opt === "dark"
                          ? "bg-[#050505] border-white/10"
                          : "bg-white border-relate-border"
                      }`}
                      aria-hidden
                    />
                    <div>
                      <div className="font-medium text-sm text-relate-ink capitalize">
                        {opt === "dark" ? "Koyu (Cyber)" : "Açık (Relate)"}
                      </div>
                      <div className="text-[11px] text-relate-graphite">
                        {opt === "dark"
                          ? "Siyah zemin, emerald aksan"
                          : "Beyaz zemin, mavi aksan"}
                      </div>
                    </div>
                  </div>
                </button>
              );
            })}
          </div>
          <p className="mt-2 text-[11px] text-gray-500">
            Chat ekranının varsayılan teması. Ziyaretçiler widget içindeki
            butonla kendi tercihlerini geçici olarak değiştirebilir.
          </p>
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
          <div className="flex flex-wrap items-end gap-2">
            <SelectField
              value={form.tts_voice}
              options={[
                { value: "nova", label: "Nova (kadın, Türkçe öneri)" },
                { value: "shimmer", label: "Shimmer (kadın, yumuşak)" },
                { value: "alloy", label: "Alloy (nötr)" },
                { value: "echo", label: "Echo (erkek, sakin)" },
                { value: "fable", label: "Fable (erkek, anlatıcı)" },
                { value: "onyx", label: "Onyx (erkek, derin)" },
              ]}
              onChange={(v) => setForm({ ...form, tts_voice: v })}
              className="max-w-xs"
            />
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
