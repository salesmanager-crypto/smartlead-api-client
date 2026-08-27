import Header from "./components/layout/Header.jsx";
import SidebarNav from "./components/layout/SidebarNav.jsx";
import AlertBanner from "./components/layout/AlertBanner.jsx";
import GridDashboard from "./components/GridDashboard.jsx";
import AutomationLogTable from "./components/automation/AutomationLogTable.jsx";
import SidebarDrawer from "./components/SidebarDrawer.jsx";
import ProfileModal from "./components/ProfileModal.jsx";
import { useDashboard } from "./context/DashboardContext.jsx";

export default function App() {
  const { loading, error, snapshot } = useDashboard();

  return (
    <div className="flex min-h-screen bg-paper dark:bg-canvas">
      <SidebarNav />
      <div className="min-w-0 flex-1">
        <Header />
        <AlertBanner />

        {loading && !snapshot ? (
          <div className="flex h-64 items-center justify-center text-sm text-charcoal/50 dark:text-mist/50">
            Loading Growth Ops data…
          </div>
        ) : (
          <>
            <GridDashboard />
            <AutomationLogTable />
          </>
        )}

        {error && (
          <p className="mx-5 mb-6 text-xs text-signal md:mx-8">
            {error} — showing last known data / local fallback.
          </p>
        )}
      </div>

      <SidebarDrawer />
      <ProfileModal />
    </div>
  );
}
