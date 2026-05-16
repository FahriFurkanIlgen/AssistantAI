import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { Toaster } from "react-hot-toast";
import QueryProvider from "@/components/providers/QueryProvider";

const inter = Inter({
  subsets: ["latin"],
  weight: ["300", "400", "500", "600", "700"],
  display: "swap",
});

export const metadata: Metadata = {
  title: "AssistantAI – Akıllı Randevu Sistemi",
  description:
    "Yapay zeka destekli randevu yönetim sistemi. Dövme stüdyoları, klinikler, güzellik merkezleri ve daha fazlası için.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="tr">
      <body className={`${inter.className} antialiased bg-relate-canvas text-relate-graphite`}>
        <QueryProvider>
          {children}
          <Toaster
            position="top-right"
            toastOptions={{
              duration: 4000,
            }}
          />
        </QueryProvider>
      </body>
    </html>
  );
}
