/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./lib/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        // Relate palette tokens — REMAPPED to Cyber Serif (dark/emerald).
        // Original Relate values preserved as comments for easy revert.
        relate: {
          canvas:   "#050505",   // was #fcfcfc
          wash:     "#0a0a0a",   // was #f0f4fe
          card:     "rgba(255,255,255,0.02)", // was #ffffff
          ink:      "#ebebeb",   // was #020520
          graphite: "#ebebeb",   // was #14141e
          slate:    "rgba(235,235,235,0.70)", // was #374151
          ash:      "rgba(235,235,235,0.55)", // was #696a72
          fog:      "rgba(235,235,235,0.40)", // was #95959b
          steel:    "rgba(235,235,235,0.50)", // was #6b7280
          border:   "rgba(255,255,255,0.08)", // was #e8eaf0
          rule:     "rgba(255,255,255,0.12)", // was #cfcfcf
          signal:   "#10b981",   // was #145aff (emerald accent)
          glow:     "#10b981",
          fade:     "#10b981",
          fadeDeep: "#10b981",
          emerald:  "#10b981",
          coral:    "#f26052",
          azure:    "#10b981",
          amber:    "#ffa64d",
          action:   "#ebebeb",   // was #0f1f3d
        },
        // Cyber Serif (dark) — opt-in via `.dark-cyber` wrapper or
        // `bg-cyber-bg` / `text-cyber-ink` utilities. Coexists with Relate.
        cyber: {
          bg:        "#050505",
          surface:   "#0a0a0a",
          ink:       "#ebebeb",
          mute:      "rgba(235,235,235,0.60)",
          dim:       "rgba(235,235,235,0.50)",
          faint:     "rgba(235,235,235,0.30)",
          rule:      "rgba(255,255,255,0.08)",
          ruleSoft:  "rgba(255,255,255,0.05)",
          glass:     "rgba(255,255,255,0.02)",
          emerald:   "#10b981",
          emeraldDim:"rgba(16,185,129,0.20)",
        },
        brand: {
          50:  "#f0f4fe",
          100: "#dfe7fd",
          500: "#145aff",
          600: "#145aff",
          700: "#0f1f3d",
          900: "#020520",
        },
        // Legacy apple-* names — also remapped to Cyber Serif tones.
        apple: {
          black:    "#050505",
          gray:     "#0a0a0a",
          ink:      "#ebebeb",
          secondary:"rgba(235,235,235,0.55)",
          border:   "rgba(255,255,255,0.08)",
          border2:  "rgba(255,255,255,0.12)",
          utility:  "rgba(235,235,235,0.70)",
          blue:     "#10b981",
          blueLink: "#10b981",
          blueDark: "#10b981",
          graphite: "#ebebeb",
        },
      },
      fontFamily: {
        sans: [
          "Inter",
          "ui-sans-serif",
          "system-ui",
          "-apple-system",
          "BlinkMacSystemFont",
          "Segoe UI",
          "Roboto",
          "sans-serif",
        ],
        display: [
          "Inter",
          "ui-sans-serif",
          "system-ui",
          "-apple-system",
          "BlinkMacSystemFont",
          "Segoe UI",
          "Roboto",
          "sans-serif",
        ],
        mono: [
          "Roboto Mono",
          "ui-monospace",
          "SFMono-Regular",
          "Menlo",
          "Monaco",
          "Consolas",
          "monospace",
        ],
        // Cyber Serif theme fonts
        serif: [
          "var(--font-newsreader)",
          "Newsreader",
          "ui-serif",
          "Georgia",
          "Cambria",
          "serif",
        ],
        grotesk: [
          "var(--font-space-grotesk)",
          "Space Grotesk",
          "ui-sans-serif",
          "system-ui",
          "sans-serif",
        ],
      },
      letterSpacing: {
        tighter2: "-0.028em",
        tighter3: "-0.038em",
        display:  "-0.0269em",
      },
      borderRadius: {
        apple:      "8px",
        "apple-lg": "40px",
        "apple-xl": "40px",
        relate:     "8px",
        "relate-lg":"40px",
        pill:       "9999px",
      },
      boxShadow: {
        "relate-sm":   "rgba(0, 0, 0, 0.10) 0px 0px 4px -2px",
        "relate-md":   "rgba(0, 0, 0, 0.25) 0px 0px 4px -2px",
        "relate-xl":   "rgba(20, 90, 255, 0.10) 0px 0px 50px -28px, rgba(0, 0, 0, 0.18) 0px 0px 3px -1px",
        "relate-glow": "rgba(20, 90, 255, 0.10) 0px 0px 100px -28px",
        "relate-feature":
          "rgba(0,0,0,0.082) 0px 0.36px 1.81px -1.42px, rgba(0,0,0,0.07) 0px 1.37px 6.87px -2.83px, rgba(0,0,0,0.016) 0px 6px 30px -4.25px",
        // Cyber Serif glows
        "cyber-emerald": "0 0 30px rgba(16,185,129,0.35)",
        "cyber-white":   "0 0 30px rgba(255,255,255,0.30)",
      },
      backgroundImage: {
        "relate-fade": "linear-gradient(rgb(59,130,246) 0%, rgb(20,90,255) 100%)",
        "relate-hero":
          "radial-gradient(60% 70% at 50% 30%, rgba(182,203,253,0.55) 0%, rgba(240,244,254,0.6) 45%, rgba(252,252,252,0) 80%)",
        // Cyber Serif radial glows
        "cyber-emerald-glow":
          "radial-gradient(60% 60% at 50% 50%, rgba(16,185,129,0.18) 0%, rgba(5,5,5,0) 70%)",
        "cyber-grid":
          "linear-gradient(rgba(255,255,255,0.04) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.04) 1px, transparent 1px)",
      },
      transitionTimingFunction: {
        cyber: "cubic-bezier(0.16, 1, 0.3, 1)",
      },
      backdropBlur: {
        cyber: "12px",
      },
      maxWidth: {
        relate: "1200px",
      },
    },
  },
  plugins: [],
};
