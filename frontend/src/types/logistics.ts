export interface CarOrder {
  sequence?: number;
  car_id: string;
  model_type: string;
  color: string;
  offline_time: string;
  outbound_time: string;
  destination: string;
  direction: string;
  priority: number;
}

export interface StagingLane {
  lane_id: string;
  capacity: number;
  lane_status: string;
  cars?: CarOrder[];
}

export interface Metrics {
  total_cars: number;
  assigned_count: number;
  unassigned_count: number;
  used_lane_count: number;
  total_lane_count: number;
  average_utilization: number;
  destination_concentration: number;
  direction_concentration: number;
  fifo_violations: number;
  total_penalty: number;
  best_fitness: number;
  convergence: ConvergencePoint[];
}

export interface ConvergencePoint {
  generation: number;
  best_fitness: number;
}

export interface OptimizationResult {
  algorithm: "baseline" | "genetic";
  algorithm_name: string;
  description: string;
  lanes: StagingLane[];
  unassigned_cars: CarOrder[];
  metrics: Metrics;
  best_fitness?: number;
  convergence?: ConvergencePoint[];
  lane_utilization?: LaneUtilization[];
  parameters?: Record<string, number>;
}

export interface LaneUtilization {
  lane_id: string;
  vehicle_count: number;
  capacity: number;
  utilization: number;
}

export interface ComparisonRow {
  metric: string;
  unit: string;
  baseline: number;
  genetic: number;
}

export interface ComparisonResponse {
  baseline: OptimizationResult;
  genetic: OptimizationResult;
  rows: ComparisonRow[];
  lane_utilization: LaneUtilization[];
}
