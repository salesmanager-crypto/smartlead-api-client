import { NavLink } from "react-router-dom";
import { useDashboard } from "../../context/DashboardContext.jsx";

// Route-based navigation — every item is a real URL, not a scroll anchor, so the
// sidebar, browser back/forward, and deep links all agree on where you are.
const NAV_ITEMS = [
  { to: "/dashboard", label: "Overview", icon: "🏠" },
  { to: "/inbox", label: "Inbox", icon: "📨" },
  { to: "/pipeline", label: "Pipeline", icon: "📊" },
  { to: "/tasks", label: "Tasks", icon: "✅" },
  { to: "/seo", label: "SEO & Infra", icon: "🌐" },
];

export default function SidebarNav() {
  const { resetDashboardLayout, setProfileOpen } = useDashboard();

  return (
    <aside className="sticky top-0 hidden h-screen w-16 shrink-0 flex-col items-center justify-between border-r border-line/20 bg-white py-4 md:flex dark:bg-slate-950">
      <div className="flex flex-col items-center gap-6">
        <NavLink
          to="/dashboard"
          className="flex h-9 w-9 items-center justify-center rounded-lg bg-charcoal text-sm font-extrabold text-white dark:bg-signal"
          title="Albert Scott — Overview"
        >
          AS
        </NavLink>
        <nav className="flex flex-col items-center gap-4">
          {NAV_ITEMS.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              title={item.label}
              className={({ isActive }) =>
                `press focus-ring flex h-10 w-10 items-center justify-center rounded-lg text-lg transition-colors ${
                  isActive
                    ? "bg-mist text-signal dark:bg-slate-800/70 dark:text-signal"
                    : "text-charcoal/60 hover:bg-mist hover:text-signal dark:text-slate-400 dark:hover:bg-slate-800/60"
                }`
              }
            >
              <span aria-hidden>{item.icon}</span>
              <span className="sr-only">{item.label}</span>
            </NavLink>
          ))}
        </nav>
      </div>

      <div className="flex flex-col items-center gap-3">
        <button
          onClick={resetDashboardLayout}
          title="Reset default dashboard layout"
          className="press focus-ring flex h-10 w-10 items-center justify-center rounded-lg text-lg text-charcoal/50 transition-colors hover:bg-mist hover:text-signal dark:text-slate-400 dark:hover:bg-slate-800/60"
        >
          ↺
        </button>
        <button
          onClick={() => setProfileOpen(true)}
          title="Profile & settings"
          className="press focus-ring flex h-10 w-10 items-center justify-center rounded-lg text-lg text-charcoal/50 transition-colors hover:bg-mist hover:text-signal dark:text-slate-400 dark:hover:bg-slate-800/60"
        >
          ⚙️
        </button>
      </div>
    </aside>
  );
}
