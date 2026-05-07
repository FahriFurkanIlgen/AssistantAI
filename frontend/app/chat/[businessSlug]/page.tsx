import ChatWidget from "@/components/chat/ChatWidget";

interface Props {
  params: Promise<{ businessSlug: string }>;
  searchParams: Promise<{ lang?: string }>;
}

export default async function ChatPage({ params, searchParams }: Props) {
  const { businessSlug } = await params;
  const { lang: langParam } = await searchParams;
  const lang = (langParam === "en" ? "en" : "tr") as "tr" | "en";

  return (
    <div className="min-h-screen bg-apple-gray flex items-center justify-center p-4">
      <div className="w-full max-w-lg h-[680px]">
        <ChatWidget businessSlug={businessSlug} lang={lang} />
      </div>
    </div>
  );
}
