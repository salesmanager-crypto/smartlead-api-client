import { useMemo, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import CardShell from "./CardShell.jsx";
import { MicroTag } from "../Badge.jsx";
import SegmentedToggle from "../SegmentedToggle.jsx";
import { useDashboard } from "../../context/DashboardContext.jsx";
import { TASK_CATEGORIES, TASK_PRIORITIES } from "../../lib/mockData.js";

const COLUMNS = ["To Do", "In Progress", "Done"];
const PRIORITY_COLOR = { High: "red", Medium: "yellow", Low: "gray" };
const CATEGORY_COLOR = { Smartlead: "blue", Pipedrive: "pink", Heyreach: "green", SEO: "yellow", Infrastructure: "gray" };

const todayStr = () => new Date().toISOString().slice(0, 10);

function isOverdue(task) {
  return task.status !== "Done" && task.dueDate < todayStr();
}

function matchesDueFilter(task, filter) {
  if (filter === "All") return true;
  const today = todayStr();
  if (filter === "Overdue") return isOverdue(task);
  if (filter === "Today") return task.dueDate === today;
  if (filter === "This week") {
    const weekOut = new Date(Date.now() + 7 * 86400000).toISOString().slice(0, 10);
    return task.dueDate >= today && task.dueDate <= weekOut;
  }
  return true;
}

function EditableTitle({ task, onCommit }) {
  const [editing, setEditing] = useState(false);
  const [value, setValue] = useState(task.title);

  if (!editing) {
    return (
      <button
        onClick={() => {
          setValue(task.title);
          setEditing(true);
        }}
        className={`focus-ring block w-full truncate rounded text-left text-sm font-medium transition-colors hover:text-signal ${
          task.status === "Done" ? "text-charcoal/40 line-through dark:text-slate-500" : ""
        }`}
        title="Click to edit"
      >
        {task.title}
      </button>
    );
  }
  return (
    <input
      autoFocus
      value={value}
      onChange={(e) => setValue(e.target.value)}
      onFocus={(e) => e.currentTarget.select()}
      onBlur={() => {
        setEditing(false);
        if (value.trim() && value !== task.title) onCommit({ title: value.trim() });
      }}
      onKeyDown={(e) => {
        if (e.key === "Enter") e.currentTarget.blur();
        if (e.key === "Escape") setEditing(false);
      }}
      className="focus-ring w-full rounded-md border border-signal/50 bg-white px-1.5 py-0.5 text-sm transition-shadow dark:bg-slate-900"
    />
  );
}

function TaskMeta({ task, isOverdueTask }) {
  return (
    <div className="mt-1.5 flex flex-wrap items-center gap-x-2.5 gap-y-1">
      <MicroTag color={PRIORITY_COLOR[task.priority]}>{task.priority}</MicroTag>
      <MicroTag color={CATEGORY_COLOR[task.category]}>{task.category}</MicroTag>
      <span className={`text-[10px] lowercase tracking-wide ${isOverdueTask ? "font-medium text-signal" : "text-charcoal/45 dark:text-slate-500"}`}>
        {isOverdueTask ? "overdue · " : "due "}
        {task.dueDate}
      </span>
    </div>
  );
}

function KanbanCard({ task, onUpdate, onDragStart, onDragEnd, dragging }) {
  const colIndex = COLUMNS.indexOf(task.status);
  return (
    <motion.div
      layout
      layoutId={task.id}
      initial={{ opacity: 0, scale: 0.96 }}
      animate={{ opacity: dragging ? 0.4 : 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.96 }}
      transition={{ type: "spring", stiffness: 500, damping: 36 }}
      draggable
      onDragStart={onDragStart}
      onDragEnd={onDragEnd}
      className="group cursor-grab rounded-lg border border-line/15 bg-white p-2.5 shadow-sm transition-colors duration-200 hover:border-line/40 active:cursor-grabbing dark:border-slate-800/60 dark:bg-slate-900 dark:hover:border-slate-700"
    >
      <div className="flex items-start gap-1.5">
        <div className="min-w-0 flex-1">
          <EditableTitle task={task} onCommit={(patch) => onUpdate(task.id, patch)} />
          <TaskMeta task={task} isOverdueTask={isOverdue(task)} />
        </div>
        {/* Single-pointer / keyboard alternative to dragging (WCAG 2.2 SC 2.5.7) —
         * dragging is never the only way to move a card between columns. */}
        <div className="flex shrink-0 flex-col gap-0.5 opacity-0 transition-opacity group-hover:opacity-100 group-focus-within:opacity-100">
          <button
            disabled={colIndex === 0}
            onClick={() => onUpdate(task.id, { status: COLUMNS[colIndex - 1] })}
            aria-label={`Move "${task.title}" to ${COLUMNS[colIndex - 1] || "previous column"}`}
            title={`Move to ${COLUMNS[colIndex - 1] || "—"}`}
            className="press focus-ring rounded text-charcoal/40 transition-colors hover:text-signal disabled:pointer-events-none disabled:opacity-0 dark:text-slate-500"
          >
            ▲
          </button>
          <button
            disabled={colIndex === COLUMNS.length - 1}
            onClick={() => onUpdate(task.id, { status: COLUMNS[colIndex + 1] })}
            aria-label={`Move "${task.title}" to ${COLUMNS[colIndex + 1] || "next column"}`}
            title={`Move to ${COLUMNS[colIndex + 1] || "—"}`}
            className="press focus-ring rounded text-charcoal/40 transition-colors hover:text-signal disabled:pointer-events-none disabled:opacity-0 dark:text-slate-500"
          >
            ▼
          </button>
        </div>
      </div>
    </motion.div>
  );
}

function KanbanBoard({ tasks, onUpdate }) {
  const [dragId, setDragId] = useState(null);
  const [overCol, setOverCol] = useState(null);

  return (
    <div className="grid h-full grid-cols-1 gap-3 sm:grid-cols-3">
      {COLUMNS.map((col) => {
        const items = tasks.filter((t) => t.status === col);
        const isOver = overCol === col && dragId;
        return (
          <div
            key={col}
            onDragOver={(e) => {
              e.preventDefault();
              if (overCol !== col) setOverCol(col);
            }}
            onDragLeave={() => setOverCol((c) => (c === col ? null : c))}
            onDrop={() => {
              if (dragId) onUpdate(dragId, { status: col });
              setDragId(null);
              setOverCol(null);
            }}
            className={`flex min-h-[10rem] flex-col rounded-lg border p-2 transition-colors duration-150 ${
              isOver
                ? "border-signal/40 bg-signal/10 ring-2 ring-signal/40"
                : "border-transparent bg-mist/40 dark:border-slate-800/40 dark:bg-transparent"
            }`}
          >
            <p className="mb-2 flex items-center justify-between px-1 text-xs font-semibold uppercase tracking-wide text-charcoal/50 dark:text-slate-400">
              {col} <span>{items.length}</span>
            </p>
            <div className="flex flex-1 flex-col gap-2">
              <AnimatePresence initial={false}>
                {items.map((task) => (
                  <KanbanCard
                    key={task.id}
                    task={task}
                    onUpdate={onUpdate}
                    dragging={dragId === task.id}
                    onDragStart={() => setDragId(task.id)}
                    onDragEnd={() => {
                      setDragId(null);
                      setOverCol(null);
                    }}
                  />
                ))}
              </AnimatePresence>
              {items.length === 0 && <p className="px-1 text-xs text-charcoal/35 dark:text-slate-500">Drop tasks here</p>}
            </div>
          </div>
        );
      })}
    </div>
  );
}

function ListView({ tasks, onUpdate }) {
  return (
    <div className="overflow-hidden rounded-xl border border-line/15 dark:border-slate-800/60">
      <table className="w-full text-sm">
        <thead className="bg-mist/60 text-left text-[11px] uppercase tracking-wide text-charcoal/50 dark:bg-slate-800/50 dark:text-slate-400">
          <tr>
            <th className="px-3 py-2 font-semibold">Task</th>
            <th className="px-3 py-2 font-semibold">Status</th>
            <th className="px-3 py-2 font-semibold">Priority</th>
            <th className="px-3 py-2 font-semibold">Category</th>
            <th className="px-3 py-2 font-semibold">Due</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-line/10 dark:divide-slate-800/60">
          {tasks.map((task) => (
            <tr key={task.id} className={`transition-colors hover:bg-mist/40 dark:hover:bg-slate-800/40 ${isOverdue(task) ? "bg-signal/5" : ""}`}>
              <td className="px-3 py-2">
                <EditableTitle task={task} onCommit={(patch) => onUpdate(task.id, patch)} />
              </td>
              <td className="px-3 py-2">
                <select
                  value={task.status}
                  onChange={(e) => onUpdate(task.id, { status: e.target.value })}
                  className="focus-ring rounded-md border border-line/25 bg-transparent px-1.5 py-0.5 text-xs transition-colors dark:border-slate-700/60"
                >
                  {COLUMNS.map((c) => (
                    <option key={c} value={c}>
                      {c}
                    </option>
                  ))}
                </select>
              </td>
              <td className="px-3 py-2">
                <MicroTag color={PRIORITY_COLOR[task.priority]}>{task.priority}</MicroTag>
              </td>
              <td className="px-3 py-2">
                <MicroTag color={CATEGORY_COLOR[task.category]}>{task.category}</MicroTag>
              </td>
              <td className={`px-3 py-2 text-xs ${isOverdue(task) ? "font-semibold text-signal" : ""}`}>{task.dueDate}</td>
            </tr>
          ))}
        </tbody>
      </table>
      {tasks.length === 0 && <p className="p-4 text-center text-xs text-charcoal/40 dark:text-slate-500">Nothing here.</p>}
    </div>
  );
}

export default function TasksCard() {
  const { snapshot, taskView, setTaskView, taskFilters, setTaskFilters, showArchived, setShowArchived, updateTask, createTask } =
    useDashboard();
  const [newTitle, setNewTitle] = useState("");

  const filtered = useMemo(() => {
    if (!snapshot) return [];
    return snapshot.tasks.filter((t) => {
      if (showArchived) return t.isArchived;
      if (t.isArchived) return false;
      if (taskFilters.priority !== "All" && t.priority !== taskFilters.priority) return false;
      if (taskFilters.category !== "All" && t.category !== taskFilters.category) return false;
      if (!matchesDueFilter(t, taskFilters.dueDate)) return false;
      return true;
    });
  }, [snapshot, taskFilters, showArchived]);

  if (!snapshot) return <CardShell id="tasks" title="Task Management">Loading…</CardShell>;

  return (
    <CardShell
      id="tasks"
      title="Task Management"
      icon="✅"
      headerRight={
        <SegmentedToggle
          id="tasks-archive"
          value={showArchived ? "archived" : "active"}
          onChange={(v) => setShowArchived(v === "archived")}
          options={[
            { value: "active", label: "Active" },
            { value: "archived", label: "Archived" },
          ]}
        />
      }
    >
      <div className="flex h-full flex-col gap-3">
        {!showArchived && (
          <div className="flex flex-wrap items-center gap-2">
            <SegmentedToggle
              id="tasks-view"
              value={taskView}
              onChange={setTaskView}
              options={[
                { value: "kanban", label: "Kanban" },
                { value: "list", label: "List" },
              ]}
            />

            <select
              value={taskFilters.priority}
              onChange={(e) => setTaskFilters((f) => ({ ...f, priority: e.target.value }))}
              className="focus-ring rounded-md border border-line/25 bg-transparent px-2 py-1 text-xs transition-colors dark:border-slate-700/60"
            >
              <option>All</option>
              {TASK_PRIORITIES.map((p) => (
                <option key={p}>{p}</option>
              ))}
            </select>
            <select
              value={taskFilters.category}
              onChange={(e) => setTaskFilters((f) => ({ ...f, category: e.target.value }))}
              className="focus-ring rounded-md border border-line/25 bg-transparent px-2 py-1 text-xs transition-colors dark:border-slate-700/60"
            >
              <option>All</option>
              {TASK_CATEGORIES.map((c) => (
                <option key={c}>{c}</option>
              ))}
            </select>
            <select
              value={taskFilters.dueDate}
              onChange={(e) => setTaskFilters((f) => ({ ...f, dueDate: e.target.value }))}
              className="focus-ring rounded-md border border-line/25 bg-transparent px-2 py-1 text-xs transition-colors dark:border-slate-700/60"
            >
              {["All", "Overdue", "Today", "This week"].map((d) => (
                <option key={d}>{d}</option>
              ))}
            </select>

            <form
              className="ml-auto flex items-center gap-1"
              onSubmit={(e) => {
                e.preventDefault();
                if (!newTitle.trim()) return;
                createTask({ title: newTitle.trim() });
                setNewTitle("");
              }}
            >
              <input
                value={newTitle}
                onChange={(e) => setNewTitle(e.target.value)}
                placeholder="Quick add task…"
                className="focus-ring w-36 rounded-md border border-line/25 bg-transparent px-2 py-1 text-xs transition-colors focus:border-signal dark:border-slate-700/60"
              />
              <button type="submit" className="press focus-ring rounded-md bg-signal px-2 py-1 text-xs font-semibold text-white transition-opacity hover:opacity-90">
                Add
              </button>
            </form>
          </div>
        )}

        <div className="min-h-0 flex-1 overflow-auto">
          <AnimatePresence mode="wait" initial={false}>
            {showArchived ? (
              <motion.div key="archived" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} transition={{ duration: 0.15 }}>
                <ListView tasks={filtered} onUpdate={updateTask} />
              </motion.div>
            ) : taskView === "kanban" ? (
              <motion.div key="kanban" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} transition={{ duration: 0.15 }} className="h-full">
                <KanbanBoard tasks={filtered} onUpdate={updateTask} />
              </motion.div>
            ) : (
              <motion.div key="list" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} transition={{ duration: 0.15 }}>
                <ListView tasks={filtered} onUpdate={updateTask} />
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </CardShell>
  );
}
