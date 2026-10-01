import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: ["class"],
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "#07080B", // Obsidian Black
        foreground: "#EDEDED",
        surface: {
          DEFAULT: "#12141A",
          muted: "#181B23",
          border: "#232733",
          hover: "#2A2F3E",
        },
        gold: {
          DEFAULT: "#C9A96E", // Champagne Gold Accent
          light: "#E2C799",
          dark: "#A6864C",
          glow: "rgba(201, 169, 110, 0.25)",
        },
        ice: {
          DEFAULT: "#7CC4FF", // Electric Ice-Blue Secondary
          muted: "#3E75A6",
          glow: "rgba(124, 196, 255, 0.25)",
        },
        coral: {
          DEFAULT: "#FF5A5F", // Alert Coral
          dark: "#B82F34",
          glow: "rgba(255, 90, 95, 0.25)",
        },
        emerald: {
          DEFAULT: "#3DDC97", // Healthy Emerald
          dark: "#1B8C5C",
          glow: "rgba(61, 220, 151, 0.25)",
        },
      },
      fontFamily: {
        sans: ["var(--font-inter)", "sans-serif"],
        serif: ["var(--font-serif)", "serif"],
        mono: ["var(--font-mono)", "monospace"],
      },
      boxShadow: {
        'gold-glow': '0 0 25px -5px rgba(201, 169, 110, 0.3)',
        'coral-glow': '0 0 25px -5px rgba(255, 90, 95, 0.4)',
        'emerald-glow': '0 0 25px -5px rgba(61, 220, 151, 0.3)',
        'ice-glow': '0 0 25px -5px rgba(124, 196, 255, 0.3)',
      },
      animation: {
        'pulse-slow': 'pulse 4s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'spin-slow': 'spin 20s linear infinite',
      },
      transitionTimingFunction: {
        'orbit-bezier': 'cubic-bezier(0.22, 1, 0.36, 1)',
      }
    },
  },
  plugins: [require("tailwindcss-animate")],
};

export default config;
