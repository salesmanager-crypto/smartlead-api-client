import RGL, { WidthProvider } from "react-grid-layout";
import { useDashboard } from "../context/DashboardContext.jsx";
import { useIsMobile } from "../hooks/useIsMobile.js";
import OutreachPerformanceCard from "./cards/OutreachPerformanceCard.jsx";
import PipelineCard from "./cards/PipelineCard.jsx";
import TasksCard from "./cards/TasksCard.jsx";
import SeoHealthCard from "./cards/SeoHealthCard.jsx";

const GridLayout = WidthProvider(RGL);

const CARDS = {
  outreach: OutreachPerformanceCard,
  pipeline: PipelineCard,
  tasks: TasksCard,
  seo: SeoHealthCard,
};

// Fixed pixel heights below md — react-grid-layout's row-height math no longer
// applies once cards stop being draggable, so each card just needs enough room to
// show its content without an awkward internal scrollbar.
const MOBILE_HEIGHT = { outreach: 320, pipeline: 300, tasks: 520, seo: 480 };

export default function GridDashboard() {
  const { layout, setLayout } = useDashboard();
  const isMobile = useIsMobile();

  if (isMobile) {
    // Plain stacked column, ordered the same way the grid would compact them
    // (top-to-bottom, left-to-right) — no drag, no column math, always legible.
    const ordered = [...layout].sort((a, b) => a.y - b.y || a.x - b.x);
    return (
      <div className="mx-4 my-3 flex flex-col gap-3">
        {ordered.map((item) => {
          const Card = CARDS[item.i];
          return (
            <div key={item.i} style={{ height: MOBILE_HEIGHT[item.i] || 360 }}>
              <Card />
            </div>
          );
        })}
      </div>
    );
  }

  return (
    <GridLayout
      className="mx-4 my-3 md:mx-6"
      layout={layout}
      cols={12}
      rowHeight={26}
      margin={[12, 12]}
      draggableHandle=".card-grab-handle"
      onLayoutChange={(next) => setLayout(next)}
      compactType="vertical"
      preventCollision={false}
    >
      {layout.map((item) => {
        const Card = CARDS[item.i];
        return (
          <div key={item.i}>
            <Card />
          </div>
        );
      })}
    </GridLayout>
  );
}
