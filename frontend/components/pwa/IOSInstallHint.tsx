"use client";

/**
 * IOSInstallHint
 *
 * iOS Safari doesn't fire `beforeinstallprompt`, so users have to manually
 * use Share → "Add to Home Screen". This shows a subtle, dismissible hint
 * on iOS devices when the page is not already running standalone.
 */

import { useEffect, useState } from "react";

const STORAGE_KEY = "ios-install-hint-dismissed";

function isIOS(): boolean {
  if (typeof navigator === "undefined") return false;
  const ua = navigator.userAgent;
  const isiPhoneOrPad = /iPhone|iPad|iPod/.test(ua);
  // iPadOS 13+ identifies as Mac with touch.
  const isiPadOS =
    /Macintosh/.test(ua) &&
    typeof navigator.maxTouchPoints === "number" &&
    navigator.maxTouchPoints > 1;
  return isiPhoneOrPad || isiPadOS;
}

function isStandalone(): boolean {
  if (typeof window === "undefined") return false;
  // iOS-specific:
  const nav = navigator as Navigator & { standalone?: boolean };
  if (nav.standalone) return true;
  return window.matchMedia?.("(display-mode: standalone)").matches ?? false;
}

export default function IOSInstallHint() {
  const [show, setShow] = useState(false);

  useEffect(() => {
    if (!isIOS()) return;
    if (isStandalone()) return;
    try {
      if (localStorage.getItem(STORAGE_KEY)) return;
    } catch {}
    // Tiny delay so it doesn't flash on first paint.
    const t = setTimeout(() => setShow(true), 1500);
    return () => clearTimeout(t);
  }, []);

  const dismiss = () => {
    try {
      localStorage.setItem(STORAGE_KEY, "1");
    } catch {}
    setShow(false);
  };

  if (!show) return null;

  return (
    <div className="fixed bottom-4 left-4 right-4 z-50 max-w-md mx-auto rounded-2xl border border-relate-border bg-white shadow-relate-sm px-4 py-3 flex items-start gap-3">
      <div className="w-8 h-8 rounded-xl bg-relate-signal/10 text-relate-signal flex items-center justify-center shrink-0">
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.8} d="M12 4v12m0 0l-4-4m4 4l4-4M4 20h16" />
        </svg>
      </div>
      <div className="flex-1 min-w-0 text-[13px] leading-snug text-relate-graphite">
        <p className="font-medium text-relate-ink mb-0.5">Ana Ekrana Ekle</p>
        <p>
          Safari'de <span className="font-medium">Paylaş</span> butonuna dokunun,
          ardından <span className="font-medium">"Ana Ekrana Ekle"</span> seçeneğini seçin.
        </p>
      </div>
      <button
        onClick={dismiss}
        aria-label="Kapat"
        className="w-7 h-7 flex items-center justify-center rounded-full text-relate-graphite/60 hover:text-relate-ink hover:bg-relate-wash transition-colors"
      >
        <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 6l12 12M6 18L18 6" />
        </svg>
      </button>
    </div>
  );
}
