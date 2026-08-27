/** Enterprise Growth Ops theme (dark-slate minimalist, per the "Style Specification
 * Override" pass) layered onto the Albert Scott brand base: deep monochrome slate
 * surfaces with a single restrained accent (hot magenta, "#E51958") reserved for
 * primary actions/CTAs — the one place the brand rule "magenta only for the key
 * signal" and the enterprise "anti-childish" mandate agree. Everything else (status,
 * severity, category) now reads through standard muted Tailwind semantic hues
 * (emerald/red/amber/sky/slate) instead of saturated brand tints. */
export default {
  darkMode: "class",
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#000000",
        charcoal: "#0F172A", // slate-900 — light-mode ink / dark-on-light chip text
        mist: "#F8FAFC", // slate-50 — light-mode subtle surface / dark-mode primary text
        paper: "#F9FAFB",
        canvas: "#020617", // slate-950 — global dark canvas (flush chrome only; see slate-900 for elevated surfaces)
        signal: {
          DEFAULT: "#E51958",
          deep: "#AC1342",
        },
        division: {
          listing: "#7EC1EE",
          marketing: "#AC1342",
          retail: "#C9A600",
          logistics: "#F5A3BC",
        },
        line: "#A6A6A6",
      },
      fontFamily: {
        sans: ["Inter", "Geist Sans", "ui-sans-serif", "system-ui", "sans-serif"],
      },
      boxShadow: {
        card: "0 1px 2px 0 rgb(0 0 0 / 0.04), 0 1px 3px 0 rgb(0 0 0 / 0.06)",
        "card-dark": "0 1px 2px 0 rgb(0 0 0 / 0.5), 0 12px 32px -12px rgb(0 0 0 / 0.65)",
      },
    },
  },
  plugins: [],
};
