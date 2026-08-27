import RGL, { WidthProvider } from "react-grid-layout";
import { useDashboard } from "../context/DashboardContext.jsx";
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

export default function GridDashboard() {
  const { layout, setLayout } = useDashboard();

  return (
    <GridLayout
      className="mx-5 my-4 md:mx-8"
      layout={layout}
      cols={12}
      rowHeight={28}
      margin={[16, 16]}
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
