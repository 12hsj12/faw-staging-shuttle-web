import type { CarOrder, ComparisonResponse, OptimizationResult, StagingLane } from "../types/logistics";

const API_BASE = import.meta.env.VITE_API_BASE ?? "http://127.0.0.1:8000";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!response.ok) {
    throw new Error(`请求失败：${response.status}`);
  }
  return response.json();
}

export const api = {
  getCars: async () => request<{ data: CarOrder[]; total: number; note: string }>("/api/cars"),
  getLanes: async () => request<{ data: StagingLane[]; total: number; note: string }>("/api/staging-lanes"),
  runBaseline: async () =>
    request<OptimizationResult>("/api/staging/baseline", { method: "POST" }),
  runGenetic: async (params: Record<string, number>) =>
    request<OptimizationResult>("/api/staging/genetic", {
      method: "POST",
      body: JSON.stringify(params),
    }),
  getComparison: async () => request<ComparisonResponse>("/api/staging/comparison"),
  getProjectInfo: async () => request<Record<string, unknown>>("/api/project-info"),
};
