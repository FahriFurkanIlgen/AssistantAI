"use client";
import { useEffect, useState, useRef } from "react";
import { api } from "@/lib/api";
import MessageBubble from "./MessageBubble";
import toast from "react-hot-toast";

interface Message {
  role: "user" | "assistant";
  content: string;
}

interface WelcomeInfo {
  business_name: string;
  persona_name: string;
  welcome_message: string;
  sector: string;
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
  const bottomRef = useRef<HTMLDivElement>(null);

  // Load welcome message
  useEffect(() => {
    api.getWelcome(businessSlug, lang).then((info) => {
      setWelcomeInfo(info);
      setMessages([{ role: "assistant", content: info.welcome_message }]);
    });
  }, [businessSlug, lang]);

  // Auto-scroll
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const sendMessage = async () => {
    const text = input.trim();
    if (!text || loading) return;

    setMessages((prev) => [...prev, { role: "user", content: text }]);
    setInput("");
    setLoading(true);

    try {
      const data = await api.sendMessage(businessSlug, text, sessionId, lang);
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
    <div className="flex flex-col h-full bg-white rounded-2xl shadow-xl overflow-hidden border border-gray-200">
      {/* Header */}
      <div className="bg-gradient-to-r from-brand-600 to-purple-700 px-5 py-4 text-white">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-white/20 rounded-full flex items-center justify-center text-xl">
            {welcomeInfo ? (sectorEmoji[welcomeInfo.sector] ?? "🤖") : "🤖"}
          </div>
          <div>
            <p className="font-semibold text-base leading-tight">
              {welcomeInfo?.persona_name ?? "Asistan"}
            </p>
            <p className="text-xs text-purple-200">
              {welcomeInfo?.business_name ?? ""}
            </p>
          </div>
          <div className="ml-auto flex items-center gap-1.5">
            <span className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
            <span className="text-xs text-purple-200">Çevrimiçi</span>
          </div>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-4 py-4 space-y-3 bg-gray-50">
        {messages.map((msg, i) => (
          <MessageBubble key={i} role={msg.role} content={msg.content} />
        ))}
        {loading && (
          <div className="flex justify-start">
            <div className="bg-white border border-gray-200 rounded-2xl rounded-tl-sm px-4 py-3 shadow-sm">
              <div className="flex gap-1 items-center h-5">
                <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce [animation-delay:0ms]" />
                <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce [animation-delay:150ms]" />
                <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce [animation-delay:300ms]" />
              </div>
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* Appointment success banner */}
      {appointmentCreated && (
        <div className="bg-green-50 border-t border-green-200 px-4 py-3 text-center text-sm text-green-700 font-medium">
          ✅ Randevunuz başarıyla oluşturuldu!
        </div>
      )}

      {/* Input */}
      <div className="px-4 py-3 bg-white border-t border-gray-200">
        <div className="flex gap-2 items-end">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={
              lang === "tr" ? "Mesajınızı yazın..." : "Type your message..."
            }
            rows={1}
            disabled={loading || appointmentCreated}
            className="flex-1 resize-none input-field py-2.5 max-h-28 leading-snug"
          />
          <button
            onClick={sendMessage}
            disabled={loading || !input.trim() || appointmentCreated}
            className="btn-primary px-4 py-2.5 rounded-xl shrink-0"
          >
            <svg
              className="w-5 h-5"
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
        <p className="text-xs text-gray-400 text-center mt-2">
          Powered by AssistantAI · GPT-4o
        </p>
      </div>
    </div>
  );
}
