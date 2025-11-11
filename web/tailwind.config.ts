import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        heading: ["var(--font-instrument-serif)", "serif"],
        sans: ["var(--font-monument)", "sans-serif"],
      },
      colors: {
        golden: {
          light: "#F5E6D3",
          DEFAULT: "#D4AF37",
          dark: "#B8941F",
        },
        background: {
          primary: "#FFFFFF",
          secondary: "#FAFAF9",
        },
        text: {
          primary: "#1A1A1A",
          secondary: "#737373",
        },
        border: {
          DEFAULT: "#E5E5E5",
        },
      },
      borderRadius: {
        none: "0",
      },
    },
  },
  plugins: [],
};
export default config;
