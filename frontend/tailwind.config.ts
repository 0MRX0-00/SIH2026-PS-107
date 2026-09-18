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
        bis: {
          navy: "#0a2540",
          blue: "#1e3a8a",
          lightBlue: "#e0f2fe",
          saffron: "#f59e0b",
          saffronDark: "#d97706",
          slate: "#334155",
          grayBg: "#f8fafc",
          border: "#e2e8f0"
        }
      },
      fontFamily: {
        sans: ["Inter", "-apple-system", "BlinkMacSystemFont", "Segoe UI", "Roboto", "sans-serif"],
      },
    },
  },
  plugins: [],
};
export default config;
