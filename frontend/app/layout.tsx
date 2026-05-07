import type { Metadata } from "next";
import "./globals.css";
import { Toaster } from "react-hot-toast";
import QueryProvider from "@/components/providers/QueryProvider";

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
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link
          href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap"
          rel="stylesheet"
        />
      </head>
      <body className="font-sans antialiased bg-gray-50 text-gray-900">
        <QueryProvider>
          {children}
          <Toaster
            position="top-right"
            toastOptions={{
              duration: 4000,
              style: { fontFamily: "Inter, sans-serif" },
            }}
          />
        </QueryProvider>
      </body>
    </html>
  );
}
