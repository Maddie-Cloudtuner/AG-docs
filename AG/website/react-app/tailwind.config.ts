import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        // "Clear Skies" Palette - Professional & Approachable
        background: "#0F172A", // Slate 900 - Softer than black
        surface: {
          DEFAULT: "#1E293B", // Slate 800
          hover: "#334155",   // Slate 700
        },
        border: "rgba(255, 255, 255, 0.1)",

        // Brand Colors
        primary: {
          DEFAULT: "#3B82F6", // Blue 500 - Trust
          hover: "#2563EB",   // Blue 600
          light: "#60A5FA",   // Blue 400
        },
        secondary: {
          DEFAULT: "#10B981", // Emerald 500 - Savings/Sustainability
        },
        accent: {
          DEFAULT: "#F59E0B", // Amber 500 - Attention
        },

        // Text
        muted: "#94A3B8", // Slate 400
      },
      fontFamily: {
        sans: ["var(--font-inter)"],
        heading: ["var(--font-jakarta)"],
      },
      backgroundImage: {
        "gradient-subtle": "linear-gradient(to bottom right, #0F172A, #1E293B)",
        "gradient-primary": "linear-gradient(to right, #3B82F6, #60A5FA)",
      },
    },
  },
  plugins: [],
};
export default config;
