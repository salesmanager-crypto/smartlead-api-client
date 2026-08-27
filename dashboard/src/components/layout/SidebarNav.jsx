import { useDashboard } from "../../context/DashboardContext.jsx";

const NAV_ITEMS = [
  { id: "outreach", label: "Outreach", icon: "📨" },
  { id: "pipeline", label: "Pipeline", icon: "📊" },
  { id: "tasks", label: "Tasks", icon: "✅" },
  { id: "seo", label: "SEO & Infra", icon: "🌐" },
  { id: "automation-log", label: "Automations", icon: "⚙️" },
];

function scrollToCard(id) {
  document.getElementById(`card-${id}`)?.scrollIntoView({ behavior: "smooth", block: "start" });
}

export default function SidebarNav() {
  const { resetDashboardLayout, setProfileOpen } = useDashboard();

  return (
    <aside className="sticky top-0 hidden h-screen w-16 shrink-0 flex-col items-center justify-between border-r border-line/20 bg-white py-4 md:flex dark:bg-white/[0.03]">
      <div className="flex flex-col items-center gap-6">
        <div
          className="flex h-9 w-9 items-center justify-center rounded-lg bg-charcoal text-sm font-extrabold text-white dark:bg-signal"
          title="Albert Scott"
        >
          AS
        </div>
        <nav className="flex flex-col items-center gap-4">
          {NAV_ITEMS.map((item) => (
            <button
              key={item.id}
              onClick={() => scrollToCard(item.id)}
              title={item.label}
              className="press focus-ring flex h-10 w-10 items-center justify-center rounded-lg text-lg text-charcoal/60 transition-colors hover:bg-mist hover:text-signal dark:text-mist/60 dark:hover:bg-white/10"
            >
              <span aria-hidden>{item.icon}</span>
              <span className="sr-only">{item.label}</span>
            </button>
          ))}
        </nav>
      </div>

      <div className="flex flex-col items-center gap-3">
        <button
          onClick={resetDashboardLayout}
          title="Reset default dashboard layout"
          className="press focus-ring flex h-10 w-10 items-center justify-center rounded-lg text-lg text-charcoal/50 transition-colors hover:bg-mist hover:text-signal dark:text-mist/50 dark:hover:bg-white/10"
        >
          ↺
        </button>
        <button
          onClick={() => setProfileOpen(true)}
          title="Profile & settings"
          className="press focus-ring flex h-10 w-10 items-center justify-center rounded-lg text-lg text-charcoal/50 transition-colors hover:bg-mist hover:text-signal dark:text-mist/50 dark:hover:bg-white/10"
        >
          ⚙️
        </button>
      </div>
    </aside>
  );
}
