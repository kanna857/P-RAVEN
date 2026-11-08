/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: ["class"],
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        raven: {
          navy: "#101B2B",
          navyDark: "#0B121D",
          navyLight: "#18263A",
          offwhite: "#F6F5F1",
          paper: "#FAFAF7",
          graphite: "#242C35",
          graphiteLight: "#333D48",
          teal: "#2A8C85",
          tealLight: "#38B2A9",
          tealMuted: "rgba(42, 140, 133, 0.15)",
          amber: "#C89448",
          amberMuted: "rgba(200, 148, 72, 0.15)",
          crimson: "#A63D40",
          crimsonMuted: "rgba(166, 61, 64, 0.15)",
          border: "#1E2C3D",
          borderLight: "#E5E3DC"
        }
      },
      fontFamily: {
        sans: ["Inter", "-apple-system", "BlinkMacSystemFont", "Segoe UI", "sans-serif"],
        serif: ["Newsreader", "Georgia", "serif"],
        mono: ["JetBrains Mono", "Menlo", "Courier New", "monospace"]
      }
    },
  },
  plugins: [],
}
