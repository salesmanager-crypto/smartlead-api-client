import { motion } from "framer-motion";

// Two/three-way switch with a sliding active-pill background (shared-element
// transition via layoutId — ui-ux-pro-max: shared-element-transition / spring-physics)
// instead of the pill just appearing on the new option.
export default function SegmentedToggle({ id, options, value, onChange, size = "sm" }) {
  const pad = size === "sm" ? "px-2 py-1" : "px-2.5 py-1";
  return (
    <div role="tablist" className="flex items-center gap-1 rounded-lg bg-mist p-0.5 text-xs font-semibold dark:bg-white/10">
      {options.map((opt) => {
        const active = opt.value === value;
        return (
          <button
            key={opt.value}
            role="tab"
            aria-selected={active}
            onClick={() => onChange(opt.value)}
            className={`focus-ring relative rounded-md ${pad} transition-colors ${active ? "text-charcoal dark:text-mist" : "text-charcoal/60 hover:text-charcoal dark:text-mist/60 dark:hover:text-mist"}`}
          >
            {active && (
              <motion.span
                layoutId={`segpill-${id}`}
                transition={{ type: "spring", stiffness: 500, damping: 34 }}
                className="absolute inset-0 rounded-md bg-white shadow-sm dark:bg-charcoal"
              />
            )}
            <span className="relative">{opt.label}</span>
          </button>
        );
      })}
    </div>
  );
}
