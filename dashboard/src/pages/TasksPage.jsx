import { useSearchParams } from "react-router-dom";
import TasksBoard from "../components/tasks/TasksBoard.jsx";
import { useDashboard } from "../context/DashboardContext.jsx";

// Dedicated Advanced Task Center — the same full-bleed Kanban/List board and
// 1-week auto-archive engine as the overview card, just without the CardShell
// height constraint and with room to breathe. No onNavigate is passed to
// TasksBoard here, so title-click goes back to editing in place — deep
// interaction belongs on this page, not the glance-view overview.
export default function TasksPage() {
  const { snapshot } = useDashboard();
  const [searchParams] = useSearchParams();
  const highlightedId = searchParams.get("task");

  if (!snapshot) return <div className="mx-4 my-4 text-sm text-charcoal/40 dark:text-slate-500 md:mx-6">Loading…</div>;

  return (
    <div className="mx-4 my-4 md:mx-6">
      <header className="mb-4">
        <h1 className="text-lg font-semibold tracking-tight">Advanced Task Center</h1>
        <p className="text-xs text-charcoal/50 dark:text-slate-500">
          {snapshot.tasks.filter((t) => !t.isArchived).length} active tasks · auto-archives 1 week after completion
        </p>
      </header>

      <div
        className="rounded-2xl border border-line/20 bg-white p-4 shadow-card dark:border-slate-800/60 dark:bg-slate-900 dark:shadow-card-dark md:p-5"
        style={{ minHeight: "calc(100vh - 220px)" }}
      >
        <TasksBoard highlightedId={highlightedId} />
      </div>
    </div>
  );
}
