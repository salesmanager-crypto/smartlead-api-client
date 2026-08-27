import { useMemo, useState } from "react";
import CardShell from "./CardShell.jsx";
import Badge from "../Badge.jsx";
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
        className={`block w-full truncate text-left text-sm font-medium hover:text-signal ${
          task.status === "Done" ? "text-charcoal/40 line-through dark:text-mist/40" : ""
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
      onBlur={() => {
        setEditing(false);
        if (value.trim() && value !== task.title) onCommit({ title: value.trim() });
      }}
      onKeyDown={(e) => {
        if (e.key === "Enter") e.currentTarget.blur();
        if (e.key === "Escape") setEditing(false);
      }}
      className="w-full rounded-md border border-signal/50 bg-white px-1.5 py-0.5 text-sm outline-none dark:bg-canvas"
    />
  );
}

function TaskMeta({ task, isOverdueTask }) {
  return (
    <div className="mt-1.5 flex flex-wrap items-center gap-1.5">
      <Badge color={PRIORITY_COLOR[task.priority]}>{task.priority}</Badge>
      <Badge color={CATEGORY_COLOR[task.category]}>{task.category}</Badge>
      <span className={`text-[11px] ${isOverdueTask ? "font-semibold text-signal" : "text-charcoal/45 dark:text-mist/45"}`}>
        {isOverdueTask ? "Overdue · " : "Due "}
        {task.dueDate}
      </span>
    </div>
  );
}

function KanbanBoard({ tasks, onUpdate }) {
  const [dragId, setDragId] = useState(null);

  return (
    <div className="grid h-full grid-cols-1 gap-3 sm:grid-cols-3">
      {COLUMNS.map((col) => {
        const items = tasks.filter((t) => t.status === col);
        return (
          <div
            key={col}
            onDragOver={(e) => e.preventDefault()}
            onDrop={() => {
              if (dragId) onUpdate(dragId, { status: col });
              setDragId(null);
            }}
            className="flex min-h-[10rem] flex-col rounded-xl bg-mist/50 p-2 dark:bg-white/[0.04]"
          >
            <p className="mb-2 flex items-center justify-between px-1 text-xs font-bold uppercase tracking-wide text-charcoal/50 dark:text-mist/50">
              {col} <span>{items.length}</span>
            </p>
            <div className="flex flex-1 flex-col gap-2">
              {items.map((task) => (
                <div
                  key={task.id}
                  draggable
                  onDragStart={() => setDragId(task.id)}
                  className="cursor-grab rounded-lg border border-line/15 bg-white p-2.5 shadow-sm active:cursor-grabbing dark:border-white/10 dark:bg-white/[0.06]"
                >
                  <EditableTitle task={task} onCommit={(patch) => onUpdate(task.id, patch)} />
                  <TaskMeta task={task} isOverdueTask={isOverdue(task)} />
                </div>
              ))}
              {items.length === 0 && <p className="px-1 text-xs text-charcoal/35 dark:text-mist/35">Drop tasks here</p>}
            </div>
          </div>
        );
      })}
    </div>
  );
}

function ListView({ tasks, onUpdate }) {
  return (
    <div className="overflow-hidden rounded-xl border border-line/15 dark:border-white/10">
      <table className="w-full text-sm">
        <thead className="bg-mist/60 text-left text-[11px] uppercase tracking-wide text-charcoal/50 dark:bg-white/[0.06] dark:text-mist/50">
          <tr>
            <th className="px-3 py-2 font-semibold">Task</th>
            <th className="px-3 py-2 font-semibold">Status</th>
            <th className="px-3 py-2 font-semibold">Priority</th>
            <th className="px-3 py-2 font-semibold">Category</th>
            <th className="px-3 py-2 font-semibold">Due</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-line/10 dark:divide-white/5">
          {tasks.map((task) => (
            <tr key={task.id} className={isOverdue(task) ? "bg-signal/5" : ""}>
              <td className="px-3 py-2">
                <EditableTitle task={task} onCommit={(patch) => onUpdate(task.id, patch)} />
              </td>
              <td className="px-3 py-2">
                <select
                  value={task.status}
                  onChange={(e) => onUpdate(task.id, { status: e.target.value })}
                  className="rounded-md border border-line/25 bg-transparent px-1.5 py-0.5 text-xs dark:border-white/15"
                >
                  {COLUMNS.map((c) => (
                    <option key={c} value={c}>
                      {c}
                    </option>
                  ))}
                </select>
              </td>
              <td className="px-3 py-2">
                <Badge color={PRIORITY_COLOR[task.priority]}>{task.priority}</Badge>
              </td>
              <td className="px-3 py-2">
                <Badge color={CATEGORY_COLOR[task.category]}>{task.category}</Badge>
              </td>
              <td className={`px-3 py-2 text-xs ${isOverdue(task) ? "font-semibold text-signal" : ""}`}>{task.dueDate}</td>
            </tr>
          ))}
        </tbody>
      </table>
      {tasks.length === 0 && <p className="p-4 text-center text-xs text-charcoal/40 dark:text-mist/40">Nothing here.</p>}
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
        <div className="flex items-center gap-1 rounded-lg bg-mist p-0.5 text-xs font-semibold dark:bg-white/10">
          <button
            onClick={() => setShowArchived(false)}
            className={`rounded-md px-2 py-1 ${!showArchived ? "bg-white shadow-sm dark:bg-charcoal" : "opacity-60"}`}
          >
            Active
          </button>
          <button
            onClick={() => setShowArchived(true)}
            className={`rounded-md px-2 py-1 ${showArchived ? "bg-white shadow-sm dark:bg-charcoal" : "opacity-60"}`}
          >
            Archived
          </button>
        </div>
      }
    >
      <div className="flex h-full flex-col gap-3">
        {!showArchived && (
          <div className="flex flex-wrap items-center gap-2">
            <div className="flex items-center gap-1 rounded-lg bg-mist p-0.5 text-xs font-semibold dark:bg-white/10">
              <button
                onClick={() => setTaskView("kanban")}
                className={`rounded-md px-2.5 py-1 ${taskView === "kanban" ? "bg-white shadow-sm dark:bg-charcoal" : "opacity-60"}`}
              >
                Kanban
              </button>
              <button
                onClick={() => setTaskView("list")}
                className={`rounded-md px-2.5 py-1 ${taskView === "list" ? "bg-white shadow-sm dark:bg-charcoal" : "opacity-60"}`}
              >
                List
              </button>
            </div>

            <select
              value={taskFilters.priority}
              onChange={(e) => setTaskFilters((f) => ({ ...f, priority: e.target.value }))}
              className="rounded-md border border-line/25 bg-transparent px-2 py-1 text-xs dark:border-white/15"
            >
              <option>All</option>
              {TASK_PRIORITIES.map((p) => (
                <option key={p}>{p}</option>
              ))}
            </select>
            <select
              value={taskFilters.category}
              onChange={(e) => setTaskFilters((f) => ({ ...f, category: e.target.value }))}
              className="rounded-md border border-line/25 bg-transparent px-2 py-1 text-xs dark:border-white/15"
            >
              <option>All</option>
              {TASK_CATEGORIES.map((c) => (
                <option key={c}>{c}</option>
              ))}
            </select>
            <select
              value={taskFilters.dueDate}
              onChange={(e) => setTaskFilters((f) => ({ ...f, dueDate: e.target.value }))}
              className="rounded-md border border-line/25 bg-transparent px-2 py-1 text-xs dark:border-white/15"
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
                className="w-36 rounded-md border border-line/25 bg-transparent px-2 py-1 text-xs outline-none focus:border-signal dark:border-white/15"
              />
              <button type="submit" className="rounded-md bg-signal px-2 py-1 text-xs font-semibold text-white">
                Add
              </button>
            </form>
          </div>
        )}

        <div className="min-h-0 flex-1 overflow-auto">
          {showArchived ? (
            <ListView tasks={filtered} onUpdate={updateTask} />
          ) : taskView === "kanban" ? (
            <KanbanBoard tasks={filtered} onUpdate={updateTask} />
          ) : (
            <ListView tasks={filtered} onUpdate={updateTask} />
          )}
        </div>
      </div>
    </CardShell>
  );
}
