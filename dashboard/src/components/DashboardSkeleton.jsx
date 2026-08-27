// Shown during the initial fetch instead of a blank/frozen screen (ui-ux-pro-max:
// Loading Indicators — "Stable skeleton ... with aria-busy", never a blank screen).
// Shaped like the real grid so there's no layout shift once data arrives.
function Block({ className = "" }) {
  return <div className={`animate-pulse rounded-2xl border border-line/20 bg-white dark:border-slate-800/60 dark:bg-slate-900 ${className}`} />;
}

export default function DashboardSkeleton() {
  return (
    <div aria-busy="true" role="status" className="mx-5 my-4 md:mx-8">
      <span className="sr-only">Loading Growth Ops dashboard data…</span>
      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <Block className="h-[19rem]" />
        <Block className="h-[19rem]" />
        <Block className="h-[24rem]" />
        <Block className="h-[24rem]" />
      </div>
      <Block className="mt-4 h-64" />
    </div>
  );
}
