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
        // Apple design tokens
        brand: {
          50:  "#e8f1fd",
          100: "#cce0fb",
          500: "#0071e3",
          600: "#0071e3",
          700: "#0066cc",
          900: "#004499",
        },
        apple: {
          black:    "#000000",
          gray:     "#f5f5f7",
          ink:      "#1d1d1f",
          secondary:"#6e6e73",
          border:   "#d2d2d7",
          border2:  "#86868b",
          utility:  "#424245",
          blue:     "#0071e3",
          blueLink: "#0066cc",
          blueDark: "#2997ff",
          graphite: "#272729",
        },
      },
      fontFamily: {
        sans: [
          "SF Pro Text",
          "SF Pro Icons",
          "Inter",
          "Helvetica Neue",
          "Helvetica",
          "Arial",
          "sans-serif",
        ],
        display: [
          "SF Pro Display",
          "SF Pro Icons",
          "Inter Tight",
          "Helvetica Neue",
          "Helvetica",
          "Arial",
          "sans-serif",
        ],
      },
      letterSpacing: {
        tighter2: "-0.028em",
        tighter3: "-0.374px",
      },
      borderRadius: {
        apple: "18px",
        "apple-lg": "28px",
        "apple-xl": "36px",
        pill: "9999px",
      },
    },
  },
  plugins: [],
};
