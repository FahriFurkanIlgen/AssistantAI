"use client";
import { useEffect, useState, useRef, useCallback } from "react";
import { api } from "@/lib/api";
import MessageBubble from "./MessageBubble";
import toast from "react-hot-toast";

const INSTAGRAM_RE = /https?:\/\/(?:www\.)?instagram\.com\/p\/[\w-]+/;

interface Message {
  role: "user" | "assistant";
  content: string;
  imagePreview?: string;
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

type Lang = "tr" | "en" | "ru" | "de";

const SUGGESTIONS: Record<Lang, string[]> = {
  tr: [
    "Hangi hizmetleri sunuyorsunuz?",
    "Yarın için randevu alabilir miyim?",
    "Fiyatlarınız hakkında bilgi alabilir miyim?",
    "Çalışma saatleriniz nedir?",
  ],
  en: [
    "What services do you offer?",
    "Can I book an appointment tomorrow?",
    "Tell me about your prices.",
    "What are your working hours?",
  ],
  ru: [
    "Какие услуги вы предлагаете?",
    "Можно записаться на завтра?",
    "Расскажите о ваших ценах.",
    "Каковы ваши часы работы?",
  ],
  de: [
    "Welche Leistungen bieten Sie an?",
    "Kann ich morgen einen Termin buchen?",
    "Erzählen Sie mir von Ihren Preisen.",
    "Wie sind Ihre Öffnungszeiten?",
  ],
};

const T: Record<Lang, {
  online: string;
  newChat: string;
  assistant: string;
  here: string;
  suggested: string;
  you: string;
  apptOk: string;
  imgWillSend: string;
  attachImg: string;
  sendMsg: string;
  sendHint: string;
  loading: string;
  igFail: string;
  tapLiked: string;
  pickImage: string;
  imgTooLarge: string;
  likeStyle: string;
  portfolio: string;
}> = {
  tr: {
    online: "Çevrimiçi",
    newChat: "Yeni sohbet",
    assistant: "Asistan",
    here: "Yardımcı olmak için buradayım.",
    suggested: "Öneri",
    you: "Sen",
    apptOk: "Randevunuz oluşturuldu",
    imgWillSend: "Görsel eklenecek",
    attachImg: "Görsel ekle",
    sendMsg: "Bir mesaj yazın...",
    sendHint: "Enter ile gönder · Shift+Enter ile yeni satır",
    loading: "Yükleniyor...",
    igFail: "Görseller yüklenemedi. Instagram'ı doğrudan ziyaret edin.",
    tapLiked: "Beğendiğinize tıklayın",
    pickImage: "Lütfen bir görsel seçin.",
    imgTooLarge: "Görsel 5MB'dan küçük olmalı.",
    likeStyle: "Bu stili beğendim, benzer bir şey istiyorum.",
    portfolio: "Portfolyo",
  },
  en: {
    online: "Online",
    newChat: "New chat",
    assistant: "Assistant",
    here: "I'm here to help.",
    suggested: "Suggested",
    you: "You",
    apptOk: "Appointment confirmed",
    imgWillSend: "Image will be sent",
    attachImg: "Attach image",
    sendMsg: "Send a message...",
    sendHint: "Enter to send · Shift+Enter for new line",
    loading: "Loading...",
    igFail: "Images could not be loaded. Visit Instagram directly.",
    tapLiked: "Tap one you like",
    pickImage: "Please select an image.",
    imgTooLarge: "Image must be under 5MB.",
    likeStyle: "I like this style, I want something similar.",
    portfolio: "Portfolio",
  },
  ru: {
    online: "В сети",
    newChat: "Новый чат",
    assistant: "Ассистент",
    here: "Я здесь, чтобы помочь.",
    suggested: "Совет",
    you: "Вы",
    apptOk: "Запись подтверждена",
    imgWillSend: "Изображение будет отправлено",
    attachImg: "Прикрепить изображение",
    sendMsg: "Напишите сообщение...",
    sendHint: "Enter — отправить · Shift+Enter — новая строка",
    loading: "Загрузка...",
    igFail: "Не удалось загрузить изображения. Перейдите в Instagram напрямую.",
    tapLiked: "Нажмите на понравившееся",
    pickImage: "Пожалуйста, выберите изображение.",
    imgTooLarge: "Изображение должно быть меньше 5 МБ.",
    likeStyle: "Мне нравится этот стиль, хочу что-то похожее.",
    portfolio: "Портфолио",
  },
  de: {
    online: "Online",
    newChat: "Neuer Chat",
    assistant: "Assistent",
    here: "Ich bin hier, um zu helfen.",
    suggested: "Vorschlag",
    you: "Sie",
    apptOk: "Termin bestätigt",
    imgWillSend: "Bild wird gesendet",
    attachImg: "Bild anhängen",
    sendMsg: "Nachricht schreiben...",
    sendHint: "Enter zum Senden · Shift+Enter für neue Zeile",
    loading: "Lädt...",
    igFail: "Bilder konnten nicht geladen werden. Besuchen Sie Instagram direkt.",
    tapLiked: "Tippen Sie auf eines, das Ihnen gefällt",
    pickImage: "Bitte wählen Sie ein Bild aus.",
    imgTooLarge: "Das Bild muss unter 5 MB sein.",
    likeStyle: "Mir gefällt dieser Stil, ich möchte etwas Ähnliches.",
    portfolio: "Portfolio",
  },
};

export default function ChatWidget({
  businessSlug,
  lang = "tr",
}: {
  businessSlug: string;
  lang?: Lang;
}) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string | undefined>();
  const [welcomeInfo, setWelcomeInfo] = useState<WelcomeInfo | null>(null);
  const [appointmentCreated, setAppointmentCreated] = useState(false);
  const [activeLang, setActiveLang] = useState<Lang>(lang);
  const [imagePreview, setImagePreview] = useState<string | null>(null);
  const [imageSendData, setImageSendData] = useState<string | null>(null);
  const [showPortfolio, setShowPortfolio] = useState(false);
  const [portfolioPosts, setPortfolioPosts] = useState<PortfolioPost[]>([]);
  const [portfolioLoading, setPortfolioLoading] = useState(false);
  const [showScrollDown, setShowScrollDown] = useState(false);
  const [theme, setTheme] = useState<"dark" | "light">("dark");

  // Load persisted theme preference
  useEffect(() => {
    try {
      const saved = localStorage.getItem("chat-theme");
      if (saved === "light" || saved === "dark") setTheme(saved);
    } catch {}
  }, []);

  useEffect(() => {
    try {
      localStorage.setItem("chat-theme", theme);
    } catch {}
  }, [theme]);

  const fileInputRef = useRef<HTMLInputElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const scrollRef = useRef<HTMLDivElement>(null);
  const bottomRef = useRef<HTMLDivElement>(null);

  // Load welcome
  useEffect(() => {
    api.getWelcome(businessSlug, activeLang).then((info) => {
      setWelcomeInfo(info);
      setMessages([{ role: "assistant", content: info.welcome_message }]);
    });
  }, [businessSlug, activeLang]);

  // Auto-scroll
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  // Textarea auto-grow
  useEffect(() => {
    const el = textareaRef.current;
    if (!el) return;
    el.style.height = "0px";
    el.style.height = Math.min(el.scrollHeight, 200) + "px";
  }, [input]);

  // Scroll-down indicator
  const onScroll = useCallback(() => {
    const el = scrollRef.current;
    if (!el) return;
    const near = el.scrollHeight - el.scrollTop - el.clientHeight < 120;
    setShowScrollDown(!near);
  }, []);

  const sectorEmoji: Record<string, string> = {
    tattoo: "✦",
    doctor: "✚",
    beauty: "❀",
    general: "◇",
  };

  const sendMessage = async (override?: string) => {
    const text = (override ?? input).trim();
    if (!text || loading) return;

    const igMatch = text.match(INSTAGRAM_RE);
    const instagramUrl = igMatch ? igMatch[0] : undefined;
    const currentImageBase64 = imageSendData || undefined;
    const currentImageUrl = !currentImageBase64 ? instagramUrl : undefined;
    const currentPreview = imagePreview;

    setMessages((prev) => [
      ...prev,
      { role: "user", content: text, imagePreview: currentPreview || undefined },
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
        toast.success(
          activeLang === "tr"
            ? "Randevunuz oluşturuldu! 🎉"
            : "Appointment created! 🎉",
        );
      }
    } catch {
      toast.error(
        activeLang === "tr"
          ? "Bir hata oluştu, lütfen tekrar deneyin."
          : "Something went wrong, please try again.",
      );
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content:
            activeLang === "tr"
              ? "Üzgünüm, bir hata oluştu. Lütfen tekrar deneyin."
              : "Sorry, an error occurred. Please try again.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const newConversation = () => {
    setSessionId(undefined);
    setAppointmentCreated(false);
    setImagePreview(null);
    setImageSendData(null);
    setInput("");
    if (welcomeInfo) {
      setMessages([{ role: "assistant", content: welcomeInfo.welcome_message }]);
    } else {
      setMessages([]);
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
      toast.error(
        activeLang === "tr" ? "Portfolyo yüklenemedi." : "Portfolio unavailable.",
      );
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
        (prev) => prev || T[activeLang].likeStyle,
      );
    }
    setShowPortfolio(false);
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    if (!file.type.startsWith("image/")) {
      toast.error(T[activeLang].pickImage);
      return;
    }
    if (file.size > 5 * 1024 * 1024) {
      toast.error(T[activeLang].imgTooLarge);
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

  const personaInitial = welcomeInfo
    ? sectorEmoji[welcomeInfo.sector] ?? welcomeInfo.persona_name.charAt(0)
    : "✦";

  const isEmptyState = messages.length <= 1 && !loading;

  return (
    <div data-chat-theme={theme} className="flex flex-col h-full bg-cyber-bg text-cyber-ink">
      {/* ============ HEADER ============ */}
      <header className="sticky top-0 z-20 bg-cyber-bg/85 backdrop-blur-cyber border-b border-cyber-rule">
        <div className="max-w-3xl mx-auto px-4 sm:px-6 h-14 flex items-center gap-3">
          <div className="w-8 h-8 rounded-full bg-cyber-emerald/15 border border-cyber-emerald/30 flex items-center justify-center text-cyber-emerald text-[14px] font-serif shrink-0">
            {personaInitial}
          </div>
          <div className="min-w-0 flex-1">
            <p className="font-serif font-light text-[15px] leading-tight text-cyber-ink truncate">
              {welcomeInfo?.persona_name ?? "Asistan"}
            </p>
            <p className="cyber-label text-[9px] mt-0.5 truncate">
              {welcomeInfo?.business_name ?? ""}
              <span className="ml-2 inline-flex items-center gap-1 text-cyber-emerald normal-case tracking-normal">
                <span className="w-1 h-1 rounded-full bg-cyber-emerald animate-pulse" />
                {T[activeLang].online}
              </span>
            </p>
          </div>

          {/* Actions */}
          <div className="flex items-center gap-1.5">
            <button
              onClick={newConversation}
              title={T[activeLang].newChat}
              className="hidden sm:flex items-center gap-1.5 px-3 h-8 rounded-full border border-cyber-rule text-cyber-ink/70 hover:text-cyber-ink hover:border-cyber-emerald/40 transition-all duration-500 ease-cyber text-[12px] font-light"
            >
              <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 4v16m8-8H4" />
              </svg>
              {T[activeLang].newChat}
            </button>
            <button
              onClick={newConversation}
              title={T[activeLang].newChat}
              className="sm:hidden w-8 h-8 flex items-center justify-center rounded-full border border-cyber-rule text-cyber-ink/70 hover:text-cyber-ink"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 4v16m8-8H4" />
              </svg>
            </button>

            {welcomeInfo?.instagram_handle && (
              <button
                onClick={openPortfolio}
                title="Portfolyo"
                className="w-8 h-8 flex items-center justify-center rounded-full border border-cyber-rule text-cyber-ink/70 hover:text-cyber-emerald hover:border-cyber-emerald/40 transition-all duration-500 ease-cyber"
              >
                <svg className="w-3.5 h-3.5" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zm0 5.838c-3.403 0-6.162 2.759-6.162 6.162s2.759 6.163 6.162 6.163 6.162-2.759 6.162-6.163c0-3.403-2.759-6.162-6.162-6.162zm0 10.162c-2.209 0-4-1.79-4-4 0-2.209 1.791-4 4-4s4 1.791 4 4c0 2.21-1.791 4-4 4zm6.406-11.845c-.796 0-1.441.645-1.441 1.44s.645 1.44 1.441 1.44c.795 0 1.439-.645 1.439-1.44s-.644-1.44-1.439-1.44z" />
                </svg>
              </button>
            )}

            {/* Theme toggle */}
            <button
              onClick={() => setTheme((t) => (t === "dark" ? "light" : "dark"))}
              title={theme === "dark" ? "Light mode" : "Dark mode"}
              aria-label="Toggle theme"
              className="w-8 h-8 flex items-center justify-center rounded-full border border-cyber-rule text-cyber-ink/70 hover:text-cyber-emerald hover:border-cyber-emerald/40 transition-all duration-500 ease-cyber"
            >
              {theme === "dark" ? (
                <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <circle cx="12" cy="12" r="4" strokeWidth={1.5} />
                  <path strokeLinecap="round" strokeWidth={1.5} d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M4.93 19.07l1.41-1.41M17.66 6.34l1.41-1.41" />
                </svg>
              ) : (
                <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M21 12.79A9 9 0 1111.21 3 7 7 0 0021 12.79z" />
                </svg>
              )}
            </button>

            {/* Lang toggle */}
            <div className="flex bg-cyber-glass border border-cyber-rule rounded-full p-0.5 text-[10px] font-grotesk uppercase tracking-[0.15em]">
              {(['tr', 'en', 'ru', 'de'] as const).map((l) => (
                <button
                  key={l}
                  onClick={() => {
                    if (l !== activeLang) {
                      setActiveLang(l);
                      setSessionId(undefined);
                    }
                  }}
                  className={`px-2.5 py-1 rounded-full transition-colors duration-500 ease-cyber ${
                    activeLang === l
                      ? "bg-cyber-emerald/15 text-cyber-emerald"
                      : "text-cyber-ink/45 hover:text-cyber-ink"
                  }`}
                >
                  {l}
                </button>
              ))}
            </div>
          </div>
        </div>
      </header>

      {/* ============ MESSAGES SCROLL AREA ============ */}
      <div
        ref={scrollRef}
        onScroll={onScroll}
        className="flex-1 overflow-y-auto relative"
      >
        {/* Empty state */}
        {isEmptyState ? (
          <div className="min-h-full flex items-center justify-center px-4 py-12">
            <div className="w-full max-w-2xl text-center">
              <div className="mx-auto w-16 h-16 rounded-full bg-cyber-emerald/15 border border-cyber-emerald/30 flex items-center justify-center text-cyber-emerald text-[26px] font-serif mb-6">
                {personaInitial}
              </div>
              <h1 className="font-serif font-light text-[28px] sm:text-[34px] leading-tight tracking-[-0.022em] text-cyber-ink mb-2">
                {welcomeInfo?.persona_name ?? "Asistan"}
                <span className="italic text-cyber-emerald">.</span>
              </h1>
              <p className="text-[14px] text-cyber-ink/55 font-light max-w-md mx-auto mb-10">
                {messages[0]?.content ?? T[activeLang].here}
              </p>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5 text-left">
                {SUGGESTIONS[activeLang].map((s) => (
                  <button
                    key={s}
                    onClick={() => sendMessage(s)}
                    disabled={loading || appointmentCreated}
                    className="group px-4 py-3 rounded-2xl border border-cyber-rule bg-cyber-glass hover:border-cyber-emerald/40 hover:bg-cyber-emerald/[0.04] transition-all duration-500 ease-cyber text-[13px] text-cyber-ink/75 font-light disabled:opacity-40 disabled:hover:border-cyber-rule"
                  >
                    <span className="cyber-label text-[8px] text-cyber-emerald/70 block mb-1 group-hover:text-cyber-emerald transition-colors">
                      {T[activeLang].suggested}
                    </span>
                    {s}
                  </button>
                ))}
              </div>
            </div>
          </div>
        ) : (
          <div className="max-w-3xl mx-auto px-3 sm:px-6 py-6 space-y-5">
            {messages.map((msg, i) => (
              <div key={i} className="flex items-start gap-3">
                {/* Avatar */}
                <div className="w-8 h-8 shrink-0 rounded-full flex items-center justify-center text-[12px] font-serif border mt-0.5">
                  {msg.role === "assistant" ? (
                    <span className="w-full h-full rounded-full bg-cyber-emerald/15 border-cyber-emerald/30 text-cyber-emerald flex items-center justify-center border">
                      {personaInitial}
                    </span>
                  ) : (
                    <span className="w-full h-full rounded-full bg-cyber-glass border-cyber-rule text-cyber-ink/70 flex items-center justify-center border">
                      <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                      </svg>
                    </span>
                  )}
                </div>

                <div className="flex-1 min-w-0 pt-1">
                  <p className="cyber-label text-[9px] mb-1.5 text-cyber-ink/40">
                    {msg.role === "assistant"
                      ? welcomeInfo?.persona_name ?? T[activeLang].assistant
                      : T[activeLang].you}
                  </p>
                  {msg.imagePreview && msg.role === "user" && (
                    <img
                      src={msg.imagePreview}
                      alt="paylaşılan görsel"
                      className="max-w-[220px] max-h-[220px] rounded-2xl object-cover border border-cyber-rule mb-2"
                    />
                  )}
                  <MessageBubble role={msg.role} content={msg.content} />
                </div>
              </div>
            ))}

            {loading && (
              <div className="flex items-start gap-3">
                <div className="w-8 h-8 shrink-0 rounded-full bg-cyber-emerald/15 border border-cyber-emerald/30 text-cyber-emerald flex items-center justify-center text-[12px] font-serif mt-0.5">
                  {personaInitial}
                </div>
                <div className="flex-1 pt-1">
                  <p className="cyber-label text-[9px] mb-1.5 text-cyber-ink/40">
                    {welcomeInfo?.persona_name ?? "Asistan"}
                  </p>
                  <div className="cyber-typing inline-flex items-center gap-1 px-1 py-2">
                    <span /> <span /> <span />
                  </div>
                </div>
              </div>
            )}

            <div ref={bottomRef} />
          </div>
        )}

        {/* Scroll-to-bottom button */}
        {showScrollDown && (
          <button
            onClick={() => bottomRef.current?.scrollIntoView({ behavior: "smooth" })}
            className="absolute bottom-4 left-1/2 -translate-x-1/2 w-9 h-9 rounded-full bg-cyber-bg/90 backdrop-blur-cyber border border-cyber-rule text-cyber-ink/70 hover:text-cyber-emerald hover:border-cyber-emerald/40 flex items-center justify-center transition-all duration-500 ease-cyber shadow-lg"
            aria-label="Scroll to bottom"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M19 14l-7 7m0 0l-7-7m7 7V3" />
            </svg>
          </button>
        )}
      </div>

      {/* Appointment success banner */}
      {appointmentCreated && (
        <div className="bg-cyber-emerald/[0.06] border-t border-cyber-emerald/20 px-4 py-2.5 text-center text-[12px] text-cyber-emerald font-grotesk uppercase tracking-[0.2em]">
          {T[activeLang].apptOk}
        </div>
      )}

      {/* ============ INPUT BAR ============ */}
      <div className="border-t border-cyber-rule bg-cyber-bg/85 backdrop-blur-cyber">
        <div className="max-w-3xl mx-auto px-3 sm:px-6 py-3 sm:py-4">
          {imagePreview && (
            <div className="flex items-center gap-2 mb-2.5">
              <div className="relative">
                <img
                  src={imagePreview}
                  alt="önizleme"
                  className="h-14 w-14 rounded-xl object-cover border border-cyber-rule"
                />
                <button
                  onClick={() => {
                    setImagePreview(null);
                    setImageSendData(null);
                  }}
                  className="absolute -top-1.5 -right-1.5 w-5 h-5 bg-cyber-ink text-cyber-bg rounded-full text-[11px] flex items-center justify-center hover:bg-cyber-emerald hover:text-cyber-bg transition-colors"
                >
                  ×
                </button>
              </div>
              <span className="cyber-label text-[9px]">
                {T[activeLang].imgWillSend}
              </span>
            </div>
          )}

          <div className="relative flex items-end gap-2 bg-cyber-glass border border-cyber-rule rounded-3xl px-2 py-2 focus-within:border-cyber-emerald/40 focus-within:bg-cyber-emerald/[0.03] transition-all duration-500 ease-cyber">
            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              className="hidden"
              onChange={handleFileChange}
            />
            <button
              onClick={() => fileInputRef.current?.click()}
              disabled={loading || appointmentCreated}
              title={T[activeLang].attachImg}
              className="shrink-0 w-9 h-9 flex items-center justify-center rounded-full text-cyber-ink/55 hover:text-cyber-emerald hover:bg-cyber-emerald/10 transition-all duration-500 ease-cyber disabled:opacity-30"
            >
              <svg className="w-[18px] h-[18px]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M21.44 11.05l-9.19 9.19a6 6 0 01-8.49-8.49l9.19-9.19a4 4 0 015.66 5.66l-9.2 9.19a2 2 0 01-2.83-2.83l8.49-8.48" />
              </svg>
            </button>

            <textarea
              ref={textareaRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder={T[activeLang].sendMsg}
              rows={1}
              disabled={loading || appointmentCreated}
              className="flex-1 resize-none bg-transparent border-0 outline-none px-1 py-2 text-[14px] leading-relaxed text-cyber-ink placeholder-cyber-ink/35 font-light max-h-[200px]"
            />

            <button
              onClick={() => sendMessage()}
              disabled={loading || (!input.trim() && !imageSendData) || appointmentCreated}
              className="shrink-0 w-9 h-9 flex items-center justify-center rounded-full bg-cyber-emerald text-cyber-bg hover:bg-cyber-emerald/90 disabled:bg-cyber-glass disabled:text-cyber-ink/30 disabled:border disabled:border-cyber-rule transition-all duration-500 ease-cyber shadow-cyber-emerald disabled:shadow-none"
              aria-label="Send"
            >
              {loading ? (
                <svg className="w-3.5 h-3.5 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <circle cx="12" cy="12" r="9" strokeWidth={2} strokeDasharray="40 60" />
                </svg>
              ) : (
                <svg className="w-[16px] h-[16px]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 12l14-7-4 14-3-6-7-1z" />
                </svg>
              )}
            </button>
          </div>

          <p className="text-[10px] text-cyber-ink/35 text-center mt-2 font-light">
            {T[activeLang].sendHint}
            <span className="mx-1.5 text-cyber-ink/20">·</span>
            AssistantAI
          </p>
        </div>
      </div>

      {/* ============ PORTFOLIO OVERLAY ============ */}
      {showPortfolio && (
        <div className="absolute inset-0 z-30 bg-cyber-bg flex flex-col">
          <div className="flex items-center justify-between px-5 py-4 border-b border-cyber-rule">
            <div>
              <p className="font-serif font-light text-[18px] text-cyber-ink leading-tight">
                {T[activeLang].portfolio}
              </p>
              {welcomeInfo?.instagram_handle && (
                <a
                  href={`https://www.instagram.com/${welcomeInfo.instagram_handle}/`}
                  target="_blank"
                  rel="noreferrer"
                  className="cyber-label text-[9px] text-cyber-emerald hover:text-cyber-emerald/80 transition-colors"
                >
                  @{welcomeInfo.instagram_handle}
                </a>
              )}
            </div>
            <button
              onClick={() => setShowPortfolio(false)}
              className="w-8 h-8 rounded-full border border-cyber-rule text-cyber-ink/70 hover:text-cyber-ink hover:border-cyber-emerald/40 flex items-center justify-center text-lg leading-none transition-all duration-500 ease-cyber"
            >
              ×
            </button>
          </div>
          <div className="flex-1 overflow-y-auto p-3 bg-cyber-bg">
            {portfolioLoading ? (
              <div className="flex items-center justify-center h-full text-cyber-ink/55 text-[13px] font-light">
                {T[activeLang].loading}
              </div>
            ) : portfolioPosts.length === 0 ? (
              <div className="flex flex-col items-center justify-center h-full gap-3 text-center px-6">
                <p className="text-cyber-ink/55 text-[13px] font-light">
                  {T[activeLang].igFail}
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
              <div className="max-w-3xl mx-auto">
                <p className="cyber-label text-[9px] mb-2 px-1">
                  {T[activeLang].tapLiked}
                </p>
                <div className="grid grid-cols-3 gap-1.5">
                  {portfolioPosts.map((post, i) => (
                    <button
                      key={i}
                      onClick={() => handlePortfolioImageClick(post)}
                      className="aspect-square bg-cyber-glass border border-cyber-rule rounded-lg overflow-hidden hover:border-cyber-emerald/40 hover:opacity-90 transition-all duration-500 ease-cyber"
                    >
                      {post.thumbnail ? (
                        <img
                          src={post.thumbnail}
                          alt={`post ${i + 1}`}
                          className="w-full h-full object-cover"
                        />
                      ) : (
                        <div className="w-full h-full flex items-center justify-center text-cyber-ink/40 text-[10px]">
                          {post.shortcode ?? "—"}
                        </div>
                      )}
                    </button>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
