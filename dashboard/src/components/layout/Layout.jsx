import { Outlet } from "react-router-dom";
import Header from "./Header.jsx";
import SidebarNav from "./SidebarNav.jsx";
import AlertBanner from "./AlertBanner.jsx";
import SidebarDrawer from "../SidebarDrawer.jsx";
import ProfileModal from "../ProfileModal.jsx";
import DashboardSkeleton from "../DashboardSkeleton.jsx";
import { useDashboard } from "../../context/DashboardContext.jsx";

// The persistent chrome around every route: nav, header, alert banner, and —
// critically — the resizable SidebarDrawer and ProfileModal, rendered once here
// (not per-page) so they stay the global "third layer" available from any page
// without remounting on navigation. Profile/theme/layout state lives in the
// Provider tree above the Router (see main.jsx), so it survives route changes too.
export default function Layout() {
  const { loading, error, snapshot } = useDashboard();

  return (
    <div className="flex min-h-screen bg-paper dark:bg-canvas">
      <SidebarNav />
      <div className="min-w-0 flex-1">
        <Header />
        <AlertBanner />

        {loading && !snapshot ? <DashboardSkeleton /> : <Outlet />}

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
