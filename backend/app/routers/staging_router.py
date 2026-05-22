from typing import Literal

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.algorithms.baseline_staging import run_baseline_staging
from app.algorithms.genetic_staging import run_genetic_staging
from app.services.data_loader import load_cars, load_lanes
from app.services.metrics_service import lane_utilization_rows


router = APIRouter(prefix="/api/staging", tags=["staging"])


class GeneticRequest(BaseModel):
    population_size: int = Field(default=50, ge=10, le=200)
    generations: int = Field(default=100, ge=10, le=500)
    crossover_rate: float = Field(default=0.8, ge=0, le=1)
    mutation_rate: float = Field(default=0.1, ge=0, le=1)
    elite_size: int = Field(default=2, ge=1, le=10)
    lane_capacity: int = Field(default=8, ge=1, le=20)


def _comparison_rows(baseline: dict, genetic: dict) -> list[dict]:
    metric_map = [
        ("used_lane_count", "已使用备车道数量", "条"),
        ("average_utilization", "平均利用率", ""),
        ("destination_concentration", "同目的地集中度", ""),
        ("direction_concentration", "同方向集中度", ""),
        ("fifo_violations", "FIFO 违背次数", "次"),
        ("unassigned_count", "未分配车辆数", "辆"),
        ("total_penalty", "综合惩罚值", "分"),
    ]
    return [
        {
            "metric": label,
            "unit": unit,
            "baseline": baseline["metrics"][key],
            "genetic": genetic["metrics"][key],
        }
        for key, label, unit in metric_map
    ]


@router.post("/baseline")
def baseline() -> dict:
    cars = load_cars()
    lanes = load_lanes()
    result = run_baseline_staging(cars, lanes)
    result["lane_utilization"] = lane_utilization_rows(result["lanes"])
    return result


@router.post("/genetic")
def genetic(request: GeneticRequest) -> dict:
    cars = load_cars()
    lanes = load_lanes()
    result = run_genetic_staging(
        cars,
        lanes,
        population_size=request.population_size,
        generations=request.generations,
        crossover_rate=request.crossover_rate,
        mutation_rate=request.mutation_rate,
        elite_size=request.elite_size,
        lane_capacity=request.lane_capacity,
    )
    result["lane_utilization"] = lane_utilization_rows(result["lanes"], request.lane_capacity)
    return result


@router.get("/comparison")
def comparison(default_algorithm: Literal["genetic"] = "genetic") -> dict:
    cars = load_cars()
    lanes = load_lanes()
    baseline_result = run_baseline_staging(cars, lanes)
    genetic_result = run_genetic_staging(cars, lanes)
    return {
        "baseline": baseline_result,
        "genetic": genetic_result,
        "rows": _comparison_rows(baseline_result, genetic_result),
        "lane_utilization": lane_utilization_rows(genetic_result["lanes"]),
        "default_algorithm": default_algorithm,
    }
