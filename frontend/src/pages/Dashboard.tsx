import { useEffect, useMemo, useState } from "react";
import { Bar, BarChart, CartesianGrid, Legend, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

import { api } from "../api/client";
import ChartCard from "../components/ChartCard";
import MetricCard from "../components/MetricCard";
import type { CarOrder, ComparisonResponse } from "../types/logistics";

export default function Dashboard() {
  const [comparison, setComparison] = useState<ComparisonResponse | null>(null);
  const [cars, setCars] = useState<CarOrder[]>([]);

  useEffect(() => {
    api.getComparison().then(setComparison);
    api.getCars().then((res) => setCars(res.data));
  }, []);

  const destinationData = useMemo(() => {
    const countMap = cars.reduce<Record<string, number>>((acc, car) => {
      acc[car.destination] = (acc[car.destination] ?? 0) + 1;
      return acc;
    }, {});
    return Object.entries(countMap).map(([destination, count]) => ({ destination, count }));
  }, [cars]);

  if (!comparison) return <div className="loading">正在加载首页指标...</div>;

  const metrics = comparison.genetic.metrics;
  const compareChart = comparison.rows.map((row) => ({
    metric: row.metric.replace("数量", "").replace("次数", ""),
    基线算法: row.baseline,
    遗传算法: row.genetic,
  }));

  return (
    <div className="page">
      <div className="page-title">
        <h1>首页仪表盘</h1>
        <p>展示模拟整车出库备车场景下的算法结果、利用率和遗传算法收敛情况。</p>
      </div>

      <div className="metric-grid">
        <MetricCard title="待出库整车数量" value={metrics.total_cars} unit="辆" />
        <MetricCard title="已分配整车数量" value={metrics.assigned_count} unit="辆" tone="green" />
        <MetricCard title="未分配整车数量" value={metrics.unassigned_count} unit="辆" tone="amber" />
        <MetricCard title="已使用备车道" value={metrics.used_lane_count} unit="条" />
        <MetricCard title="平均利用率" value={`${Math.round(metrics.average_utilization * 100)}%`} tone="green" />
        <MetricCard title="同目的地集中度" value={`${Math.round(metrics.destination_concentration * 100)}%`} />
        <MetricCard title="同方向集中度" value={`${Math.round(metrics.direction_concentration * 100)}%`} />
        <MetricCard title="FIFO 违背次数" value={metrics.fifo_violations} unit="次" tone="red" />
        <MetricCard title="遗传算法最优适应度" value={metrics.best_fitness} tone="amber" />
      </div>

      <div className="chart-grid">
        <ChartCard title="备车道利用率">
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={comparison.lane_utilization}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="lane_id" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="vehicle_count" name="车辆数" fill="#2563eb" />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>
        <ChartCard title="各目的地车辆数量分布">
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={destinationData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="destination" interval={0} angle={-35} textAnchor="end" height={72} />
              <YAxis />
              <Tooltip />
              <Bar dataKey="count" name="车辆数" fill="#0f766e" />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>
        <ChartCard title="遗传算法收敛曲线">
          <ResponsiveContainer width="100%" height={260}>
            <LineChart data={comparison.genetic.convergence}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="generation" />
              <YAxis />
              <Tooltip />
              <Line dataKey="best_fitness" name="最优适应度" stroke="#d97706" dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </ChartCard>
        <ChartCard title="基线算法 vs 遗传算法指标对比">
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={compareChart}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="metric" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="基线算法" fill="#64748b" />
              <Bar dataKey="遗传算法" fill="#16a34a" />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>
      </div>
    </div>
  );
}
