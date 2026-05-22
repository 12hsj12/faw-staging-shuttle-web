import { useEffect, useState } from "react";
import { Bar, BarChart, CartesianGrid, Legend, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

import { api } from "../api/client";
import ChartCard from "../components/ChartCard";
import LaneCard from "../components/LaneCard";
import MetricCard from "../components/MetricCard";
import type { ComparisonResponse, OptimizationResult } from "../types/logistics";

const defaultParams = {
  population_size: 50,
  generations: 100,
  crossover_rate: 0.8,
  mutation_rate: 0.1,
  elite_size: 2,
  lane_capacity: 8,
};

export default function StagingOptimization() {
  const [algorithm, setAlgorithm] = useState<"baseline" | "genetic">("genetic");
  const [params, setParams] = useState(defaultParams);
  const [result, setResult] = useState<OptimizationResult | null>(null);
  const [comparison, setComparison] = useState<ComparisonResponse | null>(null);
  const [running, setRunning] = useState(false);

  useEffect(() => {
    api.getComparison().then((res) => {
      setComparison(res);
      setResult(res.genetic);
    });
  }, []);

  const runOptimization = async () => {
    setRunning(true);
    try {
      const next = algorithm === "baseline" ? await api.runBaseline() : await api.runGenetic(params);
      setResult(next);
      const latestComparison = await api.getComparison();
      setComparison(latestComparison);
    } finally {
      setRunning(false);
    }
  };

  const updateParam = (key: keyof typeof defaultParams, value: number) => {
    setParams((current) => ({ ...current, [key]: value }));
  };

  const compareChart = comparison?.rows.map((row) => ({
    metric: row.metric.replace("数量", "").replace("次数", ""),
    基线算法: row.baseline,
    遗传算法: row.genetic,
  })) ?? [];

  return (
    <div className="page">
      <div className="page-title">
        <h1>备车优化</h1>
        <p>选择基线规则算法或遗传算法，生成每条备车道的车辆分配与道内排序。</p>
      </div>

      <section className="control-panel">
        <div className="segmented">
          <button className={algorithm === "baseline" ? "active" : ""} onClick={() => setAlgorithm("baseline")}>
            基线规则算法
          </button>
          <button className={algorithm === "genetic" ? "active" : ""} onClick={() => setAlgorithm("genetic")}>
            遗传算法
          </button>
        </div>
        <div className="param-grid">
          {Object.entries(params).map(([key, value]) => (
            <label key={key}>
              <span>{paramLabel(key)}</span>
              <input
                type="number"
                step={key.includes("rate") ? 0.05 : 1}
                value={value}
                disabled={algorithm === "baseline"}
                onChange={(event) => updateParam(key as keyof typeof defaultParams, Number(event.target.value))}
              />
            </label>
          ))}
        </div>
        <button className="primary-action" onClick={runOptimization} disabled={running}>
          {running ? "正在运行..." : "运行备车优化"}
        </button>
      </section>

      {result && (
        <>
          <div className="metric-grid compact">
            <MetricCard title="已分配整车" value={result.metrics.assigned_count} unit="辆" tone="green" />
            <MetricCard title="未分配整车" value={result.metrics.unassigned_count} unit="辆" tone="amber" />
            <MetricCard title="已使用备车道" value={result.metrics.used_lane_count} unit="条" />
            <MetricCard title="平均利用率" value={`${Math.round(result.metrics.average_utilization * 100)}%`} />
            <MetricCard title="同目的地集中度" value={`${Math.round(result.metrics.destination_concentration * 100)}%`} />
            <MetricCard title="FIFO 违背" value={result.metrics.fifo_violations} unit="次" tone="red" />
            <MetricCard title="综合惩罚值" value={result.metrics.total_penalty} tone="amber" />
            <MetricCard title="最优适应度" value={result.metrics.best_fitness} />
          </div>

          <div className="chart-grid">
            <ChartCard title="算法收敛曲线">
              <ResponsiveContainer width="100%" height={260}>
                <LineChart data={result.convergence ?? result.metrics.convergence}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="generation" />
                  <YAxis />
                  <Tooltip />
                  <Line dataKey="best_fitness" name="最优适应度" stroke="#d97706" dot={false} />
                </LineChart>
              </ResponsiveContainer>
            </ChartCard>
            <ChartCard title="基线算法 vs 遗传算法对比">
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

          <section className="panel">
            <h2>备车道分配与排序结果</h2>
            <div className="lane-grid">
              {result.lanes.map((lane) => (
                <LaneCard key={lane.lane_id} lane={lane} />
              ))}
            </div>
          </section>
        </>
      )}
    </div>
  );
}

function paramLabel(key: string) {
  const labels: Record<string, string> = {
    population_size: "种群规模",
    generations: "迭代次数",
    crossover_rate: "交叉概率",
    mutation_rate: "变异概率",
    elite_size: "精英保留",
    lane_capacity: "备车道容量",
  };
  return labels[key] ?? key;
}
