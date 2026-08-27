export default function CardShell({ id, title, icon, headerRight, children, bodyClassName = "" }) {
  return (
    <section
      id={`card-${id}`}
      className="flex h-full flex-col overflow-hidden rounded-2xl border border-line/20 bg-white shadow-card dark:border-slate-800/60 dark:bg-slate-900 dark:shadow-card-dark"
    >
      <header className="card-grab-handle flex shrink-0 items-center justify-between gap-2 border-b border-line/15 px-6 py-4 dark:border-slate-800/60">
        <div className="flex min-w-0 items-center gap-2">
          {icon && <span aria-hidden>{icon}</span>}
          <h2 className="truncate text-sm font-semibold uppercase tracking-wide text-charcoal/80 dark:text-slate-50">
            {title}
          </h2>
        </div>
        <div className="flex shrink-0 items-center gap-2" onMouseDown={(e) => e.stopPropagation()}>
          {headerRight}
        </div>
      </header>
      <div className={`thin-scroll min-h-0 flex-1 overflow-auto p-6 ${bodyClassName}`}>{children}</div>
    </section>
  );
}
