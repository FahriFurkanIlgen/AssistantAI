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
        // Relate design system — canonical tokens
        relate: {
          canvas:   "#fcfcfc",
          wash:     "#f0f4fe",
          card:     "#ffffff",
          ink:      "#020520",
          graphite: "#14141e",
          slate:    "#374151",
          ash:      "#696a72",
          fog:      "#95959b",
          steel:    "#6b7280",
          border:   "#e8eaf0",
          rule:     "#cfcfcf",
          signal:   "#145aff",
          glow:     "#b6cbfd",
          fade:     "#3b82f6",
          fadeDeep: "#145aff",
          emerald:  "#16ca2e",
          coral:    "#f26052",
          azure:    "#0099ff",
          amber:    "#ffa64d",
          action:   "#0f1f3d",
        },
        brand: {
          50:  "#f0f4fe",
          100: "#dfe7fd",
          500: "#145aff",
          600: "#145aff",
          700: "#0f1f3d",
          900: "#020520",
        },
        // Legacy apple-* names re-mapped to Relate tokens so existing pages
        // pick up the new palette without rewrites.
        apple: {
          black:    "#020520",
          gray:     "#f0f4fe",
          ink:      "#14141e",
          secondary:"#696a72",
          border:   "#e8eaf0",
          border2:  "#cfcfcf",
          utility:  "#374151",
          blue:     "#145aff",
          blueLink: "#145aff",
          blueDark: "#3b82f6",
          graphite: "#14141e",
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
      },
      backgroundImage: {
        "relate-fade": "linear-gradient(rgb(59,130,246) 0%, rgb(20,90,255) 100%)",
        "relate-hero":
          "radial-gradient(60% 70% at 50% 30%, rgba(182,203,253,0.55) 0%, rgba(240,244,254,0.6) 45%, rgba(252,252,252,0) 80%)",
      },
      maxWidth: {
        relate: "1200px",
      },
    },
  },
  plugins: [],
};
