import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import { loadJSON, saveJSON, clearKey } from "../lib/storage.js";
import * as api from "../lib/api.js";

const DashboardContext = createContext(null);

export const DEFAULT_LAYOUT = [
  { i: "outreach", x: 0, y: 0, w: 6, h: 9, minW: 4, minH: 6 },
  { i: "pipeline", x: 6, y: 0, w: 6, h: 9, minW: 4, minH: 6 },
  { i: "tasks", x: 0, y: 9, w: 7, h: 11, minW: 4, minH: 7 },
  { i: "seo", x: 7, y: 9, w: 5, h: 11, minW: 3, minH: 6 },
];

const DEFAULT_PROFILE = {
  firstName: "Yoni",
  lastName: "Lebovits",
  email: "yoni@albertscott.com",
  avatar: null,
  timezone: Intl.DateTimeFormat().resolvedOptions().timeZone || "America/New_York",
};

const POLL_MS = 60000;

export function DashboardProvider({ children }) {
  const [profile, setProfile] = useState(() => loadJSON("profile", DEFAULT_PROFILE));
  const [layout, setLayout] = useState(() => loadJSON("layout", DEFAULT_LAYOUT));
  const [snapshot, setSnapshot] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const [drawer, setDrawer] = useState({ open: false, context: null, data: null, widthPct: 34 });
  const [profileOpen, setProfileOpen] = useState(false);

  const [taskView, setTaskView] = useState(() => loadJSON("taskView", "kanban"));
  const [taskFilters, setTaskFilters] = useState({ priority: "All", category: "All", dueDate: "All" });
  const [showArchived, setShowArchived] = useState(false);

  const refresh = useCallback(async () => {
    try {
      const data = await api.getSnapshot();
      setSnapshot(data);
      setError(null);
    } catch (e) {
      setError(e.message || "Failed to load dashboard data");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    refresh();
    const id = setInterval(refresh, POLL_MS);
    return () => clearInterval(id);
  }, [refresh]);

  useEffect(() => saveJSON("profile", profile), [profile]);
  useEffect(() => saveJSON("layout", layout), [layout]);
  useEffect(() => saveJSON("taskView", taskView), [taskView]);

  const openDrawer = useCallback((context, data, widthPct = 34) => {
    setDrawer({ open: true, context, data, widthPct });
  }, []);
  const closeDrawer = useCallback(() => setDrawer((d) => ({ ...d, open: false })), []);
  const setDrawerWidth = useCallback((widthPct) => {
    setDrawer((d) => ({ ...d, widthPct: Math.min(60, Math.max(30, widthPct)) }));
  }, []);

  // ---- mutation actions (optimistic where cheap to do so) ------------------

  const reRunAutomations = useCallback(async (ids) => {
    const updated = await api.reRunAutomations(ids);
    setSnapshot((s) => {
      if (!s) return s;
      const byId = new Map(updated.map((r) => [r.id, r]));
      return { ...s, automationLog: s.automationLog.map((r) => byId.get(r.id) || r) };
    });
    return updated;
  }, []);

  const setDomainCooldown = useCallback(async (domainId, cooldown) => {
    const updated = await api.setDomainCooldown(domainId, cooldown);
    setSnapshot((s) => (s ? { ...s, domains: s.domains.map((d) => (d.id === domainId ? updated : d)) } : s));
    return updated;
  }, []);

  const sendQuickReply = useCallback((payload) => api.sendQuickReply(payload), []);

  const updateTask = useCallback(async (id, patch) => {
    setSnapshot((s) => (s ? { ...s, tasks: s.tasks.map((t) => (t.id === id ? { ...t, ...patch } : t)) } : s));
    const updated = await api.updateTask(id, patch);
    setSnapshot((s) => (s ? { ...s, tasks: s.tasks.map((t) => (t.id === id ? updated : t)) } : s));
    return updated;
  }, []);

  const createTask = useCallback(async (task) => {
    const created = await api.createTask(task);
    setSnapshot((s) => (s ? { ...s, tasks: [created, ...s.tasks] } : s));
    return created;
  }, []);

  const muteAlert = useCallback(async (id) => {
    setSnapshot((s) => (s ? { ...s, alerts: s.alerts.filter((a) => a.id !== id) } : s));
    await api.muteAlert(id);
  }, []);

  const resetDashboardLayout = useCallback(async () => {
    await api.resetLayout();
    setLayout(DEFAULT_LAYOUT);
    clearKey("layout");
  }, []);

  const value = useMemo(
    () => ({
      profile,
      setProfile,
      layout,
      setLayout,
      snapshot,
      loading,
      error,
      refresh,
      drawer,
      openDrawer,
      closeDrawer,
      setDrawerWidth,
      profileOpen,
      setProfileOpen,
      taskView,
      setTaskView,
      taskFilters,
      setTaskFilters,
      showArchived,
      setShowArchived,
      reRunAutomations,
      setDomainCooldown,
      sendQuickReply,
      updateTask,
      createTask,
      muteAlert,
      resetDashboardLayout,
    }),
    [
      profile,
      layout,
      snapshot,
      loading,
      error,
      refresh,
      drawer,
      openDrawer,
      closeDrawer,
      setDrawerWidth,
      profileOpen,
      taskView,
      taskFilters,
      showArchived,
      reRunAutomations,
      setDomainCooldown,
      sendQuickReply,
      updateTask,
      createTask,
      muteAlert,
      resetDashboardLayout,
    ]
  );

  return <DashboardContext.Provider value={value}>{children}</DashboardContext.Provider>;
}

export function useDashboard() {
  const ctx = useContext(DashboardContext);
  if (!ctx) throw new Error("useDashboard must be used within DashboardProvider");
  return ctx;
}
