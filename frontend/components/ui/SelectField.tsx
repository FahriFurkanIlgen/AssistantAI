"use client";

import { useEffect, useRef, useState } from "react";

interface Option {
  value: string | number;
  label: string;
}

interface SelectFieldProps {
  label?: string;
  value: string | number;
  options: Option[];
  onChange: (val: string) => void;
  className?: string;
  /** Extra classes on the trigger button */
  triggerClassName?: string;
}

export function SelectField({
  label,
  value,
  options,
  onChange,
  className,
  triggerClassName,
}: SelectFieldProps) {
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);
  const selected = options.find((o) => String(o.value) === String(value));

  useEffect(() => {
    function handleClick(e: MouseEvent) {
      if (ref.current && !ref.current.contains(e.target as Node)) {
        setOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClick);
    return () => document.removeEventListener("mousedown", handleClick);
  }, []);

  return (
    <div className={className}>
      {label && (
        <label className="block text-[12px] text-relate-graphite mb-1">
          {label}
        </label>
      )}
      <div ref={ref} className="relative">
        <button
          type="button"
          onClick={() => setOpen((p) => !p)}
          className={`input-field w-full text-left flex items-center justify-between gap-2 ${triggerClassName ?? ""}`}
        >
          <span className="truncate">{selected?.label ?? "—"}</span>
          <svg
            className={`w-4 h-4 shrink-0 text-relate-graphite transition-transform ${open ? "rotate-180" : ""}`}
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            strokeWidth={2}
          >
            <path strokeLinecap="round" strokeLinejoin="round" d="M19 9l-7 7-7-7" />
          </svg>
        </button>

        {open && (
          <ul
            className="absolute z-[9999] mt-1 w-full rounded-xl border border-relate-border overflow-hidden max-h-60 overflow-y-auto"
            style={{ backgroundColor: "#0a0a0a", boxShadow: "0 8px 32px rgba(0,0,0,0.6)" }}
          >
            {options.map((o) => (
              <li key={o.value}>
                <button
                  type="button"
                  onClick={() => {
                    onChange(String(o.value));
                    setOpen(false);
                  }}
                  className={`w-full text-left px-3 py-2.5 text-[13px] transition-colors ${
                    String(o.value) === String(value)
                      ? "text-relate-signal font-medium"
                      : "text-relate-ink hover:text-relate-ink"
                  }`}
                  style={
                    String(o.value) === String(value)
                      ? { backgroundColor: "rgba(16,185,129,0.12)" }
                      : undefined
                  }
                  onMouseEnter={(e) => {
                    if (String(o.value) !== String(value)) {
                      (e.currentTarget as HTMLButtonElement).style.backgroundColor =
                        "rgba(255,255,255,0.06)";
                    }
                  }}
                  onMouseLeave={(e) => {
                    if (String(o.value) !== String(value)) {
                      (e.currentTarget as HTMLButtonElement).style.backgroundColor = "";
                    }
                  }}
                >
                  {o.label}
                </button>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}
