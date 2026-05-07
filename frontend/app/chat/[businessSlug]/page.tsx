import ChatWidget from "@/components/chat/ChatWidget";

interface Props {
  params: { businessSlug: string };
  searchParams: { lang?: string };
}

export default function ChatPage({ params, searchParams }: Props) {
  const lang = (searchParams.lang === "en" ? "en" : "tr") as "tr" | "en";

  return (
    <div className="min-h-screen bg-gradient-to-br from-brand-50 to-purple-50 flex items-center justify-center p-4">
      <div className="w-full max-w-lg h-[680px]">
        <ChatWidget businessSlug={params.businessSlug} lang={lang} />
      </div>
    </div>
  );
}
