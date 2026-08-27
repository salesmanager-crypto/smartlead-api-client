/** Albert Scott brand tokens — sourced from the Albert Scott v1.2 theme
 * (assets/Albert_Scott_Master_Template_v1.pptx): black/charcoal for authority,
 * light grey for clarity, white for information, hot magenta as the single key
 * signal color, and four division colors used only for classification. */
export default {
  darkMode: "class",
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#000000",
        charcoal: "#0D0D0D",
        mist: "#F2F2F2",
        paper: "#F9FAFB",
        canvas: "#0F172A",
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
        sans: ["Montserrat", "ui-sans-serif", "system-ui", "sans-serif"],
      },
      boxShadow: {
        card: "0 1px 2px 0 rgb(0 0 0 / 0.04), 0 1px 3px 0 rgb(0 0 0 / 0.06)",
        "card-dark": "0 1px 2px 0 rgb(0 0 0 / 0.4), 0 4px 16px -4px rgb(0 0 0 / 0.5)",
      },
    },
  },
  plugins: [],
};
