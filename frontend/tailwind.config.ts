import type { Config } from "tailwindcss";

// Paleta conforme briefing: fundo escuro opcional, preto/cinza/branco,
// azul como cor de destaque única. Sem rosa, sem excesso de cores.
export default {
  darkMode: "class",
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        background: {
          DEFAULT: "#0B0F19",
          surface: "#131826",
          elevated: "#1B2233",
        },
        border: "#242C3D",
        foreground: {
          DEFAULT: "#F5F7FA",
          muted: "#9AA4B2",
        },
        accent: {
          DEFAULT: "#3B82F6",
          hover: "#2563EB",
          muted: "#1E3A8A",
        },
        success: "#22C55E",
        warning: "#F59E0B",
        danger: "#EF4444",
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
      },
      borderRadius: {
        xl: "1rem",
        "2xl": "1.25rem",
      },
    },
  },
  plugins: [],
} satisfies Config;
