import GridDashboard from "../components/GridDashboard.jsx";
import AutomationLogTable from "../components/automation/AutomationLogTable.jsx";

// The Executive Overview Matrix — the draggable/resizable card grid plus a
// capped preview of the automation log. Every card here is a click-through link
// wrapper into its dedicated full-page workspace (see each card component).
export default function DashboardPage() {
  return (
    <>
      <GridDashboard />
      <AutomationLogTable />
    </>
  );
}
