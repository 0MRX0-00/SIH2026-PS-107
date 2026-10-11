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
        gov: {
          navy: "#071324",
          navySecondary: "#152E4D",
          navyLight: "#1E3A8A",
          saffron: "#D97706",
          saffronBright: "#F59E0B",
          saffronSoft: "#FEF3C7",
          bg: "#F8FAFC",
          card: "#FFFFFF",
          textPrimary: "#0F172A",
          textSecondary: "#64748B",
          textMuted: "#94A3B8",
          success: "#059669",
          successSoft: "#D1FAE5",
          danger: "#DC2626",
          dangerSoft: "#FEE2E2",
          border: "#E2E8F0",
          borderLight: "#F1F5F9",
        },
        bis: {
          navy: "#071324",
          secondaryNavy: "#152E4D",
          blue: "#1e3a8a",
          lightBlue: "#e0f2fe",
          saffron: "#d97706",
          saffronDark: "#b45309",
          saffronBright: "#f59e0b",
          slate: "#334155",
          grayBg: "#f8fafc",
          border: "#e2e8f0"
        }
      },
      fontFamily: {
        sans: ["Inter", "-apple-system", "BlinkMacSystemFont", "Segoe UI", "Roboto", "sans-serif"],
      },
      boxShadow: {
        card: "0 1px 3px 0 rgba(15, 23, 42, 0.05), 0 1px 2px -1px rgba(15, 23, 42, 0.05)",
        cardHover: "0 10px 15px -3px rgba(15, 23, 42, 0.08), 0 4px 6px -4px rgba(15, 23, 42, 0.04)",
        dropdown: "0 10px 25px -5px rgba(7, 19, 36, 0.15), 0 8px 10px -6px rgba(7, 19, 36, 0.1)",
      }
    },
  },
  plugins: [],
};
export default config;
