import { useEffect, useRef, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { useDashboard } from "../context/DashboardContext.jsx";
import { TIMEZONES } from "../lib/time.js";

export default function ProfileModal() {
  const { profile, setProfile, profileOpen, setProfileOpen, resetDashboardLayout } = useDashboard();
  const [form, setForm] = useState(profile);
  const fileRef = useRef(null);

  // Re-sync the draft whenever the modal opens (AnimatePresence keeps this component
  // mounted through its close animation, so it can no longer rely on unmount/remount
  // to reset stale form state the way an early `return null` did).
  useEffect(() => {
    if (profileOpen) setForm(profile);
  }, [profileOpen, profile]);

  const onAvatarPick = (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = () => setForm((f) => ({ ...f, avatar: reader.result }));
    reader.readAsDataURL(file);
  };

  const save = () => {
    setProfile(form);
    setProfileOpen(false);
  };

  return (
    <AnimatePresence>
      {profileOpen && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0, transition: { duration: 0.15, ease: "easeIn" } }}
          transition={{ duration: 0.2, ease: "easeOut" }}
          className="fixed inset-0 z-[60] flex items-center justify-center bg-charcoal/40 p-4"
          onClick={() => setProfileOpen(false)}
        >
          <motion.div
            initial={{ opacity: 0, scale: 0.96, y: 8 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.97, y: 4, transition: { duration: 0.15, ease: "easeIn" } }}
            transition={{ type: "spring", stiffness: 420, damping: 32 }}
            onClick={(e) => e.stopPropagation()}
            className="w-full max-w-md rounded-2xl border border-line/20 bg-white p-6 shadow-2xl dark:border-white/10 dark:bg-canvas"
          >
        <h2 className="mb-4 text-lg font-bold">Profile & Settings</h2>

        <div className="mb-5 flex items-center gap-4">
          <button
            onClick={() => fileRef.current?.click()}
            className="press focus-ring flex h-16 w-16 items-center justify-center overflow-hidden rounded-full bg-mist text-xl font-bold text-charcoal/60 transition-colors hover:bg-line/30 dark:bg-white/10 dark:text-mist/60 dark:hover:bg-white/20"
          >
            {form.avatar ? <img src={form.avatar} alt="" className="h-16 w-16 object-cover" /> : "＋"}
          </button>
          <div>
            <button
              onClick={() => fileRef.current?.click()}
              className="focus-ring rounded text-sm font-semibold text-signal transition-colors hover:text-signal-deep"
            >
              Upload avatar
            </button>
            <input ref={fileRef} type="file" accept="image/*" className="hidden" onChange={onAvatarPick} />
            <p className="text-xs text-charcoal/45 dark:text-mist/45">PNG or JPG</p>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-3">
          <label className="text-sm">
            <span className="mb-1 block text-xs font-semibold text-charcoal/60 dark:text-mist/60">First name</span>
            <input
              value={form.firstName}
              onChange={(e) => setForm((f) => ({ ...f, firstName: e.target.value }))}
              className="focus-ring w-full rounded-lg border border-line/25 bg-transparent px-2.5 py-1.5 transition-colors focus:border-signal dark:border-white/15"
            />
          </label>
          <label className="text-sm">
            <span className="mb-1 block text-xs font-semibold text-charcoal/60 dark:text-mist/60">Last name</span>
            <input
              value={form.lastName}
              onChange={(e) => setForm((f) => ({ ...f, lastName: e.target.value }))}
              className="focus-ring w-full rounded-lg border border-line/25 bg-transparent px-2.5 py-1.5 transition-colors focus:border-signal dark:border-white/15"
            />
          </label>
        </div>

        <label className="mt-3 block text-sm">
          <span className="mb-1 block text-xs font-semibold text-charcoal/60 dark:text-mist/60">Email</span>
          <input
            type="email"
            value={form.email}
            onChange={(e) => setForm((f) => ({ ...f, email: e.target.value }))}
            className="focus-ring w-full rounded-lg border border-line/25 bg-transparent px-2.5 py-1.5 transition-colors focus:border-signal dark:border-white/15"
          />
        </label>

        <label className="mt-3 block text-sm">
          <span className="mb-1 block text-xs font-semibold text-charcoal/60 dark:text-mist/60">
            Timezone <span className="font-normal text-charcoal/40 dark:text-mist/40">(drives your greeting)</span>
          </span>
          <select
            value={form.timezone}
            onChange={(e) => setForm((f) => ({ ...f, timezone: e.target.value }))}
            className="focus-ring w-full rounded-lg border border-line/25 bg-transparent px-2.5 py-1.5 transition-colors focus:border-signal dark:border-white/15"
          >
            {TIMEZONES.map((tz) => (
              <option key={tz} value={tz}>
                {tz}
              </option>
            ))}
          </select>
        </label>

        <div className="mt-5 flex items-center justify-between border-t border-line/15 pt-4 dark:border-white/10">
          <button
            onClick={() => {
              if (confirm("Reset the dashboard layout to defaults?")) resetDashboardLayout();
            }}
            className="focus-ring rounded text-xs font-semibold text-charcoal/50 transition-colors hover:text-signal dark:text-mist/50"
          >
            Reset Default Dashboard Layout
          </button>
          <div className="flex gap-2">
            <button
              onClick={() => setProfileOpen(false)}
              className="press focus-ring rounded-lg border border-line/25 px-3 py-1.5 text-sm font-semibold transition-colors hover:bg-mist dark:border-white/15 dark:hover:bg-white/10"
            >
              Cancel
            </button>
            <button
              onClick={save}
              className="press focus-ring rounded-lg bg-signal px-3 py-1.5 text-sm font-semibold text-white transition-opacity hover:opacity-90"
            >
              Save
            </button>
          </div>
        </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
