import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./src/**/*.{ts,tsx}"],
  prefix: "of-",
  corePlugins: {
    preflight: false,
  },
  theme: {
    extend: {
      colors: {
        canvas: "#090B14",
        panel: "#11162B",
        surface: "#171E37",
        "surface-strong": "#20294B",
        border: "rgba(255,255,255,0.08)",
        text: "#F7F8FC",
        muted: "#B8C1DA",
        subtle: "#8E9AC0",
        accent: "#8B5CF6",
        "accent-2": "#A855F7",
        "accent-soft": "#C4B5FD",
      },
      boxShadow: {
        panel: "0 24px 56px rgba(6, 9, 24, 0.42)",
        glow: "0 18px 34px rgba(76, 34, 176, 0.34)",
      },
      borderRadius: {
        xl2: "24px",
      },
    },
  },
  plugins: [],
};

export default config;
