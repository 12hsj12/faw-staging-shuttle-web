import type { ReactNode } from "react";

interface ChartCardProps {
  title: string;
  children: ReactNode;
}

export default function ChartCard({ title, children }: ChartCardProps) {
  return (
    <section className="chart-card">
      <h3>{title}</h3>
      <div className="chart-body">{children}</div>
    </section>
  );
}
