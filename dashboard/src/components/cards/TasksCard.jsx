import { useNavigate } from "react-router-dom";
import CardShell from "./CardShell.jsx";
import TasksBoard from "../tasks/TasksBoard.jsx";

// Overview version of the board — full Kanban/List interactivity stays available
// at a glance (drag, ▲▼ move, quick filters, quick-add), but clicking a task's
// title deep-links to the dedicated Advanced Task Center instead of editing in
// place, per the click-through overview-card pattern.
export default function TasksCard() {
  const navigate = useNavigate();
  return (
    <CardShell id="tasks" title="Task Management" icon="✅" openTo="/tasks">
      <TasksBoard onNavigate={(task) => navigate(`/tasks?task=${task.id}`)} />
    </CardShell>
  );
}
