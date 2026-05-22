import type { StagingLane } from "../types/logistics";

export default function LaneCard({ lane }: { lane: StagingLane }) {
  const count = lane.cars?.length ?? 0;
  const utilization = Math.round((count / lane.capacity) * 100);

  return (
    <article className="lane-card">
      <header>
        <div>
          <strong>{lane.lane_id}</strong>
          <span>{count}/{lane.capacity} 辆</span>
        </div>
        <em>{utilization}%</em>
      </header>
      <div className="lane-progress">
        <span style={{ width: `${utilization}%` }} />
      </div>
      <ol>
        {(lane.cars ?? []).map((car) => (
          <li key={car.car_id}>
            <span>{car.sequence}. {car.car_id}</span>
            <small>{car.destination} · {car.direction} · {car.model_type}</small>
          </li>
        ))}
      </ol>
    </article>
  );
}
