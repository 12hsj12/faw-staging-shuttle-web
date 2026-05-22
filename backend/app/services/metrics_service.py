from __future__ import annotations

from collections import Counter
from datetime import datetime
from typing import Any


def _parse_time(value: str) -> datetime:
    return datetime.strptime(str(value), "%Y-%m-%d %H:%M")


def _lane_purity(values: list[str]) -> float:
    if not values:
        return 0.0
    counter = Counter(values)
    return max(counter.values()) / len(values)


def calculate_lane_penalties(lanes: list[dict], lane_capacity: int = 8) -> dict[str, float]:
    destination_penalty = 0.0
    direction_penalty = 0.0
    fifo_penalty = 0.0
    utilization_penalty = 0.0
    model_mix_penalty = 0.0

    for lane in lanes:
        cars = lane.get("cars", [])
        if not cars:
            continue

        # 目的地越分散，惩罚越高。
        destinations = [car["destination"] for car in cars]
        destination_penalty += max(0, len(set(destinations)) - 1) * 8

        # 运输方向越分散，惩罚越高。
        directions = [car["direction"] for car in cars]
        direction_penalty += max(0, len(set(directions)) - 1) * 5

        # 出库时间更早的车辆如果排在更晚位置，视为 FIFO 违背。
        outbound_times = [_parse_time(car["outbound_time"]) for car in cars]
        for i in range(len(outbound_times)):
            for j in range(i + 1, len(outbound_times)):
                if outbound_times[i] > outbound_times[j]:
                    fifo_penalty += 1

        # 备车道未装满会降低 8 辆一组的装车组织效率。
        utilization_penalty += abs(lane_capacity - len(cars))

        # 同一备车道车型过于分散时，认为装载匹配复杂度更高。
        models = [car["model_type"] for car in cars]
        model_mix_penalty += max(0, len(set(models)) - 3) * 3

    return {
        "destination_penalty": destination_penalty,
        "direction_penalty": direction_penalty,
        "fifo_penalty": fifo_penalty,
        "utilization_penalty": utilization_penalty,
        "model_mix_penalty": model_mix_penalty,
    }


def calculate_metrics(
    lanes: list[dict],
    total_cars: int,
    total_lanes: int,
    lane_capacity: int = 8,
    best_fitness: float | None = None,
    convergence: list[dict] | None = None,
) -> dict[str, Any]:
    assigned_count = sum(len(lane.get("cars", [])) for lane in lanes)
    used_lanes = [lane for lane in lanes if lane.get("cars")]
    unassigned_count = max(0, total_cars - assigned_count)
    avg_utilization = (
        assigned_count / (len(used_lanes) * lane_capacity) if used_lanes else 0.0
    )

    destination_purity = [
        _lane_purity([car["destination"] for car in lane.get("cars", [])])
        for lane in used_lanes
    ]
    direction_purity = [
        _lane_purity([car["direction"] for car in lane.get("cars", [])])
        for lane in used_lanes
    ]

    penalties = calculate_lane_penalties(lanes, lane_capacity)
    unassigned_penalty = unassigned_count * 50
    total_penalty = (
        penalties["destination_penalty"] * 2
        + penalties["direction_penalty"] * 1.5
        + penalties["fifo_penalty"] * 3
        + penalties["utilization_penalty"] * 1
        + unassigned_penalty
        + penalties["model_mix_penalty"] * 1
    )

    return {
        "total_cars": total_cars,
        "assigned_count": assigned_count,
        "unassigned_count": unassigned_count,
        "used_lane_count": len(used_lanes),
        "total_lane_count": total_lanes,
        "average_utilization": round(avg_utilization, 4),
        "destination_concentration": round(sum(destination_purity) / len(destination_purity), 4)
        if destination_purity
        else 0,
        "direction_concentration": round(sum(direction_purity) / len(direction_purity), 4)
        if direction_purity
        else 0,
        "fifo_violations": int(penalties["fifo_penalty"]),
        "unassigned_penalty": unassigned_penalty,
        "total_penalty": round(total_penalty, 2),
        "best_fitness": round(best_fitness, 2) if best_fitness is not None else round(total_penalty, 2),
        "convergence": convergence or [],
    }


def lane_utilization_rows(lanes: list[dict], lane_capacity: int = 8) -> list[dict]:
    return [
        {
            "lane_id": lane["lane_id"],
            "vehicle_count": len(lane.get("cars", [])),
            "capacity": lane.get("capacity", lane_capacity),
            "utilization": round(len(lane.get("cars", [])) / lane.get("capacity", lane_capacity), 4),
        }
        for lane in lanes
    ]
