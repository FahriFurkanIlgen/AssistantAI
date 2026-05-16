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
    <div className="h-screen w-screen bg-cyber-bg overflow-hidden">
      <ChatWidget businessSlug={businessSlug} lang={lang} />
    </div>
  );
}
