import { useNavigate } from "react-router-dom";

export default function CardShell({ id, title, icon, headerRight, children, bodyClassName = "", openTo, openLabel = "Open ↗" }) {
  const navigate = useNavigate();
  return (
    <section
      id={`card-${id}`}
      className="flex h-full flex-col overflow-hidden rounded-2xl border border-line/20 bg-white shadow-card dark:border-slate-800/60 dark:bg-slate-900 dark:shadow-card-dark"
    >
      <header className="card-grab-handle flex shrink-0 items-center justify-between gap-2 border-b border-line/15 px-4 py-3 dark:border-slate-800/60">
        <div className="flex min-w-0 items-center gap-2">
          {icon && <span aria-hidden>{icon}</span>}
          <h2 className="truncate text-sm font-semibold uppercase tracking-wide text-charcoal/80 dark:text-slate-50">
            {title}
          </h2>
        </div>
        <div className="flex shrink-0 items-center gap-2" onMouseDown={(e) => e.stopPropagation()}>
          {headerRight}
          {openTo && (
            <button
              onClick={() => navigate(openTo)}
              className="press focus-ring rounded-md px-1.5 py-1 text-[11px] font-semibold text-charcoal/45 transition-colors hover:bg-mist hover:text-signal dark:text-slate-500 dark:hover:bg-slate-800/60 dark:hover:text-signal"
            >
              {openLabel}
            </button>
          )}
        </div>
      </header>
      <div className={`thin-scroll min-h-0 flex-1 overflow-auto p-4 ${bodyClassName}`}>{children}</div>
    </section>
  );
}
