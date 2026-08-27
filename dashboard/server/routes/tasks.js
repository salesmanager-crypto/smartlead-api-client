import { Router } from "express";
import { store } from "../data/store.js";

export const router = Router();

router.patch("/tasks/:id", (req, res) => {
  const task = store.tasks.find((t) => t.id === req.params.id);
  if (!task) return res.status(404).json({ error: "Task not found" });
  const patch = req.body || {};
  Object.assign(task, patch);
  if (patch.status === "Done" && !task.completedAt) task.completedAt = new Date().toISOString();
  if (patch.status && patch.status !== "Done") {
    task.completedAt = null;
    task.isArchived = false;
  }
  res.json({ ...task });
});

router.post("/tasks", (req, res) => {
  const body = req.body || {};
  const task = {
    id: `task_${Date.now()}`,
    status: "To Do",
    priority: "Medium",
    category: "Smartlead",
    dueDate: new Date(Date.now() + 3 * 86400000).toISOString().slice(0, 10),
    completedAt: null,
    isArchived: false,
    description: "",
    ...body,
  };
  store.tasks.unshift(task);
  res.status(201).json(task);
});
