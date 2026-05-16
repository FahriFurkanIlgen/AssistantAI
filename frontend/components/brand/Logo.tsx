import Link from "next/link";
import { clsx } from "clsx";
import type { CSSProperties } from "react";

/** AssistantAI marka logosu — emerald üçgen + iç beyaz A + beyaz nokta. */
export function LogoMark({
  className,
  style,
  title = "AssistantAI",
}: {
  className?: string;
  style?: CSSProperties;
  title?: string;
}) {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 512 512"
      role="img"
      aria-label={title}
      className={className}
      style={style}
    >
      <path
        d="M256 56 L460 416 L52 416 Z"
        fill="#22c55e"
        stroke="#22c55e"
        strokeWidth={52}
        strokeLinejoin="round"
        strokeLinecap="round"
      />
      <path
        d="M240 188 L320 344 L172 344 Z"
        fill="#ffffff"
        stroke="#ffffff"
        strokeWidth={22}
        strokeLinejoin="round"
        strokeLinecap="round"
      />
      <circle cx={368} cy={340} r={44} fill="#ffffff" />
    </svg>
  );
}

/**
 * Marka kilidi: mark + wordmark.
 * `size`: mark yüksekliği px (wordmark da orantılı).
 */
export function LogoLockup({
  size = 32,
  href,
  wordmark = true,
  className,
}: {
  size?: number;
  href?: string;
  wordmark?: boolean;
  className?: string;
}) {
  const wordSize = Math.round(size * 0.58);
  const content = (
    <span className={clsx("inline-flex items-center gap-2.5", className)}>
      <LogoMark style={{ width: size, height: size }} className="shrink-0" />
      {wordmark && (
        <span
          className="font-serif font-normal tracking-tight text-cyber-ink leading-none"
          style={{ fontSize: wordSize }}
        >
          assistant<span className="text-cyber-emerald">AI</span>
        </span>
      )}
    </span>
  );

  if (href) {
    return (
      <Link href={href} aria-label="AssistantAI ana sayfa">
        {content}
      </Link>
    );
  }
  return content;
}
