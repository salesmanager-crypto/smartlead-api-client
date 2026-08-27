import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import { MotionConfig } from "framer-motion";
import Layout from "./components/layout/Layout.jsx";
import DashboardPage from "./pages/DashboardPage.jsx";
import InboxPage from "./pages/InboxPage.jsx";
import PipelinePage from "./pages/PipelinePage.jsx";
import TasksPage from "./pages/TasksPage.jsx";
import SeoPage from "./pages/SeoPage.jsx";

// Client-side routing schema (React Router — this is a Vite SPA, not Next.js):
// /dashboard is the Executive Overview Matrix, and /inbox, /pipeline, /tasks, /seo
// are dedicated full-page workspaces the overview cards deep-link into. Layout
// (header/nav/alerts/drawer/modal) is rendered once and wraps every route via
// <Outlet/>, so it never remounts on navigation.
export default function App() {
  return (
    // reducedMotion="user" makes every Framer Motion animation in the tree honor
    // prefers-reduced-motion automatically (plain Tailwind transitions are handled
    // separately in index.css).
    <MotionConfig reducedMotion="user">
      <BrowserRouter>
        <Routes>
          <Route element={<Layout />}>
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
            <Route path="/dashboard" element={<DashboardPage />} />
            <Route path="/inbox" element={<InboxPage />} />
            <Route path="/pipeline" element={<PipelinePage />} />
            <Route path="/tasks" element={<TasksPage />} />
            <Route path="/seo" element={<SeoPage />} />
            <Route path="*" element={<Navigate to="/dashboard" replace />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </MotionConfig>
  );
}
