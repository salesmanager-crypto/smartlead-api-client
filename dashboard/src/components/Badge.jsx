// Hollow, low-opacity status badges — tinted background + hairline border + a
// muted-but-legible text color, instead of solid saturated color blocks
// ("anti-childish" palette subtraction: ui-ux-pro-max Style Specification Override).
const PALETTE = {
  green: "border-emerald-500/20 bg-emerald-500/10 text-emerald-700 dark:text-emerald-400",
  red: "border-red-500/20 bg-red-500/10 text-red-700 dark:text-red-400",
  yellow: "border-amber-500/20 bg-amber-500/10 text-amber-700 dark:text-amber-400",
  gray: "border-transparent bg-slate-500/10 text-slate-600 dark:bg-slate-500/10 dark:text-slate-500",
  blue: "border-sky-500/20 bg-sky-500/10 text-sky-700 dark:text-sky-400",
  pink: "border-pink-500/20 bg-pink-500/10 text-pink-700 dark:text-pink-400",
};

const DOT_PALETTE = {
  green: "bg-emerald-500",
  red: "bg-red-500",
  yellow: "bg-amber-500",
  gray: "bg-slate-500",
  blue: "bg-sky-500",
  pink: "bg-pink-500",
};

export default function Badge({ children, color = "gray", dot = false }) {
  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-md border px-2 py-0.5 text-xs font-medium ${PALETTE[color] || PALETTE.gray}`}
    >
      {dot && <span className={`h-1.5 w-1.5 shrink-0 rounded-full ${DOT_PALETTE[color] || DOT_PALETTE.gray}`} aria-hidden />}
      {children}
    </span>
  );
}

const TAG_DOT = {
  green: "bg-emerald-500",
  red: "bg-red-500",
  yellow: "bg-amber-500",
  gray: "bg-slate-400 dark:bg-slate-600",
  blue: "bg-sky-500",
  pink: "bg-pink-500",
};

/** Microscopic lowercase status tag — no pill/border, just a tiny dot + muted
 * text. Used where a full Badge would be too loud (dense Kanban/list rows). */
export function MicroTag({ children, color, className = "" }) {
  return (
    <span className={`inline-flex items-center gap-1 text-[10px] font-medium lowercase tracking-wide text-charcoal/50 dark:text-slate-500 ${className}`}>
      {color && <span className={`h-1.5 w-1.5 shrink-0 rounded-full ${TAG_DOT[color] || TAG_DOT.gray}`} aria-hidden />}
      {children}
    </span>
  );
}
