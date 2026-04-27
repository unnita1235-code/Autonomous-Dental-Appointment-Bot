import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}"
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: "#1A6B8A",
          hover: "#155a75",
          light: "#e8f4f8"
        },
        accent: {
          DEFAULT: "#2EC4B6",
          hover: "#25a99c"
        },
        surface: "#F7FAFC",
        success: "#38A169",
        warning: "#DD6B20",
        error: "#E53E3E",
        muted: "#718096"
      },
      fontFamily: {
        heading: ["'Instrument Sans'", "sans-serif"],
        body: ["'DM Sans'", "sans-serif"]
      },
      keyframes: {
        "typing-dot": {
          "0%, 80%, 100%": { opacity: "0.3", transform: "translateY(0)" },
          "40%": { opacity: "1", transform: "translateY(-2px)" }
        }
      },
      animation: {
        "typing-dot": "typing-dot 1.2s infinite ease-in-out"
      }
    }
  },
  plugins: []
};

export default config;
