interface MetricCardProps {
  title: string;
  value: string | number;
  unit?: string;
  tone?: "blue" | "green" | "amber" | "red";
}

export default function MetricCard({ title, value, unit, tone = "blue" }: MetricCardProps) {
  return (
    <div className={`metric-card metric-${tone}`}>
      <span>{title}</span>
      <strong>
        {value}
        {unit && <em>{unit}</em>}
      </strong>
    </div>
  );
}
