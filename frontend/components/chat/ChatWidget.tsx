"use client";
import { useEffect, useState, useRef } from "react";
import { api } from "@/lib/api";
import MessageBubble from "./MessageBubble";
import toast from "react-hot-toast";

const INSTAGRAM_RE = /https?:\/\/(?:www\.)?instagram\.com\/p\/[\w-]+/;

interface Message {
  role: "user" | "assistant";
  content: string;
  imagePreview?: string; // shown only in UI, not persisted
}

interface WelcomeInfo {
  business_name: string;
  persona_name: string;
  welcome_message: string;
  sector: string;
  instagram_handle?: string;
}

interface PortfolioPost {
  shortcode: string | null;
  url: string | null;
  thumbnail: string | null;
}

export default function ChatWidget({
  businessSlug,
  lang = "tr",
}: {
  businessSlug: string;
  lang?: "tr" | "en";
}) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string | undefined>();
  const [welcomeInfo, setWelcomeInfo] = useState<WelcomeInfo | null>(null);
  const [appointmentCreated, setAppointmentCreated] = useState(false);
  const [activeLang, setActiveLang] = useState<"tr" | "en">(lang);
  // Image state
  const [imagePreview, setImagePreview] = useState<string | null>(null);
  const [imageSendData, setImageSendData] = useState<string | null>(null); // base64 data URL
  // Portfolio state
  const [showPortfolio, setShowPortfolio] = useState(false);
  const [portfolioPosts, setPortfolioPosts] = useState<PortfolioPost[]>([]);
  const [portfolioLoading, setPortfolioLoading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const bottomRef = useRef<HTMLDivElement>(null);

  // Load welcome message
  useEffect(() => {
    api.getWelcome(businessSlug, activeLang).then((info) => {
      setWelcomeInfo(info);
      setMessages([{ role: "assistant", content: info.welcome_message }]);
    });
  }, [businessSlug, activeLang]);

  // Auto-scroll
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const sendMessage = async () => {
    const text = input.trim();
    if (!text || loading) return;

    // Detect Instagram URL in message text
    const igMatch = text.match(INSTAGRAM_RE);
    const instagramUrl = igMatch ? igMatch[0] : undefined;

    // Capture & clear image state before async ops
    const currentImageBase64 = imageSendData || undefined;
    const currentImageUrl = !currentImageBase64 ? instagramUrl : undefined;
    const currentPreview = imagePreview;

    setMessages((prev) => [
      ...prev,
      {
        role: "user",
        content: text,
        imagePreview: currentPreview || undefined,
      },
    ]);
    setInput("");
    setImagePreview(null);
    setImageSendData(null);
    setLoading(true);

    try {
      const data = await api.sendMessage(
        businessSlug,
        text,
        sessionId,
        activeLang,
        currentImageBase64,
        currentImageUrl,
      );
      setSessionId(data.session_id);
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: data.reply },
      ]);

      if (data.appointment_created && !appointmentCreated) {
        setAppointmentCreated(true);
        toast.success("Randevunuz oluşturuldu! 🎉");
      }
    } catch {
      toast.error("Bir hata oluştu, lütfen tekrar deneyin.");
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: "Üzgünüm, bir hata oluştu. Lütfen tekrar deneyin.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const openPortfolio = async () => {
    if (portfolioPosts.length > 0) {
      setShowPortfolio(true);
      return;
    }
    setPortfolioLoading(true);
    setShowPortfolio(true);
    try {
      const data = await api.getPortfolio(businessSlug);
      setPortfolioPosts(data.posts || []);
    } catch {
      toast.error("Portfolyo yüklenemedi.");
    } finally {
      setPortfolioLoading(false);
    }
  };

  const handlePortfolioImageClick = (post: PortfolioPost) => {
    if (post.thumbnail) {
      setImagePreview(post.thumbnail);
      setImageSendData(post.thumbnail);
    }
    if (post.url) {
      setInput(
        (prev) =>
          prev ||
          (activeLang === "tr"
            ? "Bu stili beğendim, benzer bir şey istiyorum."
            : "I like this style, I want something similar."),
      );
    }
    setShowPortfolio(false);
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    if (!file.type.startsWith("image/")) {
      toast.error(
        activeLang === "tr"
          ? "Lütfen bir görsel seçin."
          : "Please select an image.",
      );
      return;
    }
    if (file.size > 5 * 1024 * 1024) {
      toast.error(
        activeLang === "tr"
          ? "Görsel 5MB'dan küçük olmalı."
          : "Image must be under 5MB.",
      );
      return;
    }
    const reader = new FileReader();
    reader.onload = () => {
      const result = reader.result as string;
      setImagePreview(result);
      setImageSendData(result);
    };
    reader.readAsDataURL(file);
    e.target.value = "";
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const sectorEmoji: Record<string, string> = {
    tattoo: "🎨",
    doctor: "🏥",
    beauty: "💅",
    general: "🏢",
  };

  return (
    <div className="flex flex-col h-full bg-white rounded-apple-lg border border-apple-border overflow-hidden">
      {/* Header — Apple dark */}
      <div className="bg-apple-ink px-5 py-4 text-white">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 bg-white/10 rounded-full flex items-center justify-center text-[18px]">
            {welcomeInfo ? (sectorEmoji[welcomeInfo.sector] ?? "✦") : "✦"}
          </div>
          <div>
            <p className="font-display font-semibold text-[15px] leading-tight tracking-tight">
              {welcomeInfo?.persona_name ?? "Asistan"}
            </p>
            <p className="text-[12px] text-white/50 mt-0.5">
              {welcomeInfo?.business_name ?? ""}
            </p>
          </div>
          <div className="ml-auto flex items-center gap-3">
            {welcomeInfo?.instagram_handle && (
              <button
                onClick={openPortfolio}
                className="text-[12px] text-white/70 hover:text-white flex items-center gap-1 transition-colors"
                title="Portfolyomuzu gör"
              >
                <svg
                  className="w-3.5 h-3.5"
                  fill="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zm0 5.838c-3.403 0-6.162 2.759-6.162 6.162s2.759 6.163 6.162 6.163 6.162-2.759 6.162-6.163c0-3.403-2.759-6.162-6.162-6.162zm0 10.162c-2.209 0-4-1.79-4-4 0-2.209 1.791-4 4-4s4 1.791 4 4c0 2.21-1.791 4-4 4zm6.406-11.845c-.796 0-1.441.645-1.441 1.44s.645 1.44 1.441 1.44c.795 0 1.439-.645 1.439-1.44s-.644-1.44-1.439-1.44z" />
                </svg>
                Portfolyo
              </button>
            )}
            {/* TR / EN toggle */}
            <div className="flex bg-white/10 rounded-lg p-0.5 text-[11px] font-medium">
              {(["tr", "en"] as const).map((l) => (
                <button
                  key={l}
                  onClick={() => {
                    if (l !== activeLang) {
                      setActiveLang(l);
                      setSessionId(undefined);
                    }
                  }}
                  className={`px-2 py-0.5 rounded-md transition-colors ${
                    activeLang === l
                      ? "bg-white text-apple-ink"
                      : "text-white/60 hover:text-white"
                  }`}
                >
                  {l.toUpperCase()}
                </button>
              ))}
            </div>
            <div className="flex items-center gap-1.5">
              <span className="w-1.5 h-1.5 bg-green-400 rounded-full" />
              <span className="text-[11px] text-white/50">
                {activeLang === "tr" ? "Çevrimiçi" : "Online"}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Portfolio grid panel */}
      {showPortfolio && (
        <div className="absolute inset-0 z-10 bg-white flex flex-col rounded-apple-lg overflow-hidden">
          <div className="flex items-center justify-between px-5 py-4 border-b border-apple-border bg-apple-ink text-white">
            <div>
              <p className="font-display font-semibold text-[15px] tracking-tight">
                Portfolyo
              </p>
              {welcomeInfo?.instagram_handle && (
                <a
                  href={`https://www.instagram.com/${welcomeInfo.instagram_handle}/`}
                  target="_blank"
                  rel="noreferrer"
                  className="text-[12px] text-white/50 hover:text-white transition-colors"
                >
                  @{welcomeInfo.instagram_handle}
                </a>
              )}
            </div>
            <button
              onClick={() => setShowPortfolio(false)}
              className="text-white/60 hover:text-white text-xl leading-none"
            >
              ×
            </button>
          </div>
          <div className="flex-1 overflow-y-auto p-3 bg-apple-gray">
            {portfolioLoading ? (
              <div className="flex items-center justify-center h-full text-apple-secondary text-[14px]">
                Yükleniyor...
              </div>
            ) : portfolioPosts.length === 0 ? (
              <div className="flex flex-col items-center justify-center h-full gap-3 text-center px-6">
                <p className="text-apple-secondary text-[14px]">
                  Görseller yüklenemedi. Instagram'ı doğrudan ziyaret edin.
                </p>
                {welcomeInfo?.instagram_handle && (
                  <a
                    href={`https://www.instagram.com/${welcomeInfo.instagram_handle}/`}
                    target="_blank"
                    rel="noreferrer"
                    className="btn-primary text-[13px] px-5 py-2"
                  >
                    @{welcomeInfo.instagram_handle} ↗
                  </a>
                )}
              </div>
            ) : (
              <>
                <p className="text-[12px] text-apple-secondary mb-2 px-1">
                  {activeLang === "tr"
                    ? "Beğendiğinize tıklayın — asistana gönderin."
                    : "Tap one you like to send it to the assistant."}
                </p>
                <div className="grid grid-cols-3 gap-1.5">
                  {portfolioPosts.map((post, i) => (
                    <button
                      key={i}
                      onClick={() => handlePortfolioImageClick(post)}
                      className="aspect-square bg-apple-border rounded-lg overflow-hidden hover:opacity-80 transition-opacity"
                    >
                      {post.thumbnail ? (
                        <img
                          src={post.thumbnail}
                          alt={`post ${i + 1}`}
                          className="w-full h-full object-cover"
                        />
                      ) : (
                        <div className="w-full h-full flex items-center justify-center text-apple-secondary text-[10px]">
                          {post.shortcode ?? "—"}
                        </div>
                      )}
                    </button>
                  ))}
                </div>
              </>
            )}
          </div>
        </div>
      )}

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-4 py-4 space-y-2 bg-apple-gray">
        {messages.map((msg, i) => (
          <div key={i}>
            {msg.imagePreview && msg.role === "user" && (
              <div className="flex justify-end mb-1">
                <img
                  src={msg.imagePreview}
                  alt="paylaşılan görsel"
                  className="max-w-[180px] max-h-[180px] rounded-apple object-cover border border-apple-border"
                />
              </div>
            )}
            <MessageBubble role={msg.role} content={msg.content} />
          </div>
        ))}
        {loading && (
          <div className="flex justify-start">
            <div className="bg-white border border-apple-border rounded-apple px-4 py-3">
              <div className="flex gap-1 items-center h-4">
                <span className="w-1.5 h-1.5 bg-apple-secondary rounded-full animate-bounce [animation-delay:0ms]" />
                <span className="w-1.5 h-1.5 bg-apple-secondary rounded-full animate-bounce [animation-delay:150ms]" />
                <span className="w-1.5 h-1.5 bg-apple-secondary rounded-full animate-bounce [animation-delay:300ms]" />
              </div>
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* Appointment success banner */}
      {appointmentCreated && (
        <div className="bg-white border-t border-apple-border px-4 py-3 text-center text-[13px] text-apple-blue font-medium">
          Randevunuz başarıyla oluşturuldu.
        </div>
      )}

      {/* Input */}
      <div className="px-4 py-3 bg-white border-t border-apple-border">
        {/* Image preview strip */}
        {imagePreview && (
          <div className="flex items-center gap-2 mb-2.5">
            <div className="relative">
              <img
                src={imagePreview}
                alt="önizleme"
                className="h-14 w-14 rounded-lg object-cover border border-apple-border"
              />
              <button
                onClick={() => {
                  setImagePreview(null);
                  setImageSendData(null);
                }}
                className="absolute -top-1.5 -right-1.5 w-5 h-5 bg-apple-ink text-white rounded-full text-[11px] flex items-center justify-center hover:bg-apple-utility"
              >
                ×
              </button>
            </div>
            <span className="text-[12px] text-apple-secondary">
              {lang === "tr" ? "Görsel eklenecek" : "Image will be sent"}
            </span>
          </div>
        )}

        <div className="flex gap-2 items-end">
          {/* Hidden file input */}
          <input
            ref={fileInputRef}
            type="file"
            accept="image/*"
            className="hidden"
            onChange={handleFileChange}
          />

          {/* Upload button */}
          <button
            onClick={() => fileInputRef.current?.click()}
            disabled={loading || appointmentCreated}
            title={lang === "tr" ? "Görsel ekle" : "Attach image"}
            className="shrink-0 w-9 h-9 flex items-center justify-center rounded-full border border-apple-border text-apple-secondary hover:border-apple-blue hover:text-apple-blue transition-colors disabled:opacity-30"
          >
            <svg
              className="w-4 h-4"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={1.5}
                d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
              />
            </svg>
          </button>

          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={
              lang === "tr"
                ? "Mesajınızı yazın veya Instagram linki yapıştırın..."
                : "Type a message or paste an Instagram link..."
            }
            rows={1}
            disabled={loading || appointmentCreated}
            className="flex-1 resize-none bg-apple-gray border border-apple-border rounded-pill px-4 py-2 text-[14px] text-apple-ink placeholder-apple-secondary max-h-28 leading-snug focus:outline-none focus:border-apple-blue focus:ring-1 focus:ring-apple-blue/20 transition-colors"
          />
          <button
            onClick={sendMessage}
            disabled={
              loading || (!input.trim() && !imageSendData) || appointmentCreated
            }
            className="shrink-0 w-9 h-9 flex items-center justify-center bg-apple-blue hover:bg-apple-blueLink text-white rounded-full transition-colors disabled:opacity-30"
          >
            <svg
              className="w-4 h-4"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"
              />
            </svg>
          </button>
        </div>
        <p className="text-[11px] text-apple-secondary text-center mt-2">
          AssistantAI · GPT-4o Vision
        </p>
      </div>
    </div>
  );
}
