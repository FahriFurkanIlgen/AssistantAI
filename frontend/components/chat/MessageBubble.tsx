import clsx from "clsx";

interface Props {
  role: "user" | "assistant";
  content: string;
}

export default function MessageBubble({ role, content }: Props) {
  const isUser = role === "user";

  return (
    <div
      className={clsx(
        "text-[14px] leading-[1.65] font-light whitespace-pre-wrap break-words",
        isUser
          ? "text-cyber-ink/90"
          : "text-cyber-ink/85",
      )}
    >
      {content}
    </div>
  );
}
