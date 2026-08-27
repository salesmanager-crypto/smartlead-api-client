import { useEffect, useState } from "react";

/** True below the `md` breakpoint (768px) — used to swap the draggable grid for a
 * plain stacked layout on phones. Drag-to-rearrange is a desktop power-user feature;
 * react-grid-layout's fixed 12-column math (even with WidthProvider) produces
 * unusably narrow columns on a phone-width viewport, so mobile gets a simpler,
 * always-readable single column instead of a squeezed grid. */
export function useIsMobile(breakpoint = 768) {
  const [isMobile, setIsMobile] = useState(
    () => typeof window !== "undefined" && window.innerWidth < breakpoint
  );

  useEffect(() => {
    const mql = window.matchMedia(`(max-width: ${breakpoint - 1}px)`);
    const onChange = () => setIsMobile(mql.matches);
    onChange();
    mql.addEventListener("change", onChange);
    return () => mql.removeEventListener("change", onChange);
  }, [breakpoint]);

  return isMobile;
}
