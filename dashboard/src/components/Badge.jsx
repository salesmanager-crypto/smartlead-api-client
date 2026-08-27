const PALETTE = {
  green: "bg-emerald-500/15 text-emerald-700 dark:text-emerald-400",
  red: "bg-signal/15 text-signal-deep dark:text-signal",
  yellow: "bg-division-retail/20 text-charcoal dark:text-division-retail",
  gray: "bg-line/20 text-charcoal/60 dark:bg-white/10 dark:text-mist/60",
  blue: "bg-division-listing/20 text-sky-800 dark:text-division-listing",
  pink: "bg-division-logistics/25 text-charcoal dark:text-division-logistics",
};

export default function Badge({ children, color = "gray", dot = false }) {
  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full px-2.5 py-0.5 text-xs font-semibold ${PALETTE[color] || PALETTE.gray}`}
    >
      {dot && <span className="h-1.5 w-1.5 rounded-full bg-current" aria-hidden />}
      {children}
    </span>
  );
}
