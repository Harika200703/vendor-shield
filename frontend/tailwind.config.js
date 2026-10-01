/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],

  theme: {
    extend: {
      colors: {
        navy: {
          950: "#07111F",
          900: "#0B1728",
          800: "#102238",
          700: "#16304D",
        },

        brand: {
          50: "#EFF6FF",
          100: "#DBEAFE",
          200: "#BFDBFE",
          300: "#93C5FD",
          400: "#60A5FA",
          500: "#3B82F6",
          600: "#2563EB",
          700: "#1D4ED8",
          800: "#1E40AF",
        },

        risk: {
          low: "#16A34A",
          medium: "#D97706",
          high: "#EA580C",
          critical: "#DC2626",
        },
      },

      boxShadow: {
        card: "0 8px 30px rgba(15, 23, 42, 0.06)",
        soft: "0 4px 20px rgba(15, 23, 42, 0.05)",
      },

      borderRadius: {
        xl2: "1rem",
      },
    },
  },

  plugins: [],
};