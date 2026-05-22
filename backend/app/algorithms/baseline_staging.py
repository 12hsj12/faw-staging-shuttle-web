from __future__ import annotations

import pandas as pd

from app.services.metrics_service import calculate_metrics


def _format_car(car: dict, sequence: int) -> dict:
    return {
        "sequence": sequence,
        "car_id": car["car_id"],
        "model_type": car["model_type"],
        "color": car["color"],
        "offline_time": car["offline_time"].strftime("%Y-%m-%d %H:%M"),
        "outbound_time": car["outbound_time"].strftime("%Y-%m-%d %H:%M"),
        "destination": car["destination"],
        "direction": car["direction"],
        "priority": int(car["priority"]),
    }


def run_baseline_staging(
    cars_df: pd.DataFrame,
    lanes_df: pd.DataFrame,
    lane_capacity: int = 8,
) -> dict:
    """按出库时间、目的地和方向分组的可解释基线算法。"""
    sorted_cars = cars_df.sort_values(["outbound_time", "destination", "direction", "priority"])
    grouped_cars: list[dict] = []

    for _, group in sorted_cars.groupby(["destination", "direction"], sort=False):
        grouped_cars.extend(group.to_dict(orient="records"))

    lanes = []
    cursor = 0
    lane_records = lanes_df.to_dict(orient="records")

    for lane in lane_records:
        chunk = grouped_cars[cursor : cursor + lane_capacity]
        cursor += lane_capacity
        lanes.append(
            {
                "lane_id": lane["lane_id"],
                "capacity": int(lane["capacity"]),
                "lane_status": lane["lane_status"],
                "cars": [_format_car(car, idx + 1) for idx, car in enumerate(chunk)],
            }
        )

    metrics = calculate_metrics(lanes, len(cars_df), len(lanes_df), lane_capacity)
    return {
        "algorithm": "baseline",
        "algorithm_name": "基线规则算法",
        "description": "按计划出库时间排序，再按目的地与运输方向分组，每 8 辆依次分配到可用备车道。",
        "lanes": lanes,
        "unassigned_cars": [
            _format_car(car, idx + 1)
            for idx, car in enumerate(grouped_cars[cursor:])
        ],
        "metrics": metrics,
    }
