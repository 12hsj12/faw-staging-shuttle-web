from __future__ import annotations

import random
from typing import Any

import numpy as np
import pandas as pd

from app.algorithms.baseline_staging import _format_car
from app.services.metrics_service import calculate_lane_penalties, calculate_metrics


WEIGHTS = {
    "destination_penalty": 2.0,
    "direction_penalty": 1.5,
    "fifo_penalty": 3.0,
    "utilization_penalty": 1.0,
    "unassigned_penalty": 50.0,
    "model_mix_penalty": 1.0,
}


def _decode_chromosome(
    chromosome: list[str],
    cars_by_id: dict[str, dict],
    lanes_df: pd.DataFrame,
    lane_capacity: int,
) -> tuple[list[dict], list[dict]]:
    lanes = []
    lane_records = lanes_df.to_dict(orient="records")
    max_assignable = len(lane_records) * lane_capacity
    assigned_ids = chromosome[:max_assignable]
    unassigned_ids = chromosome[max_assignable:]

    for lane_index, lane in enumerate(lane_records):
        start = lane_index * lane_capacity
        chunk_ids = assigned_ids[start : start + lane_capacity]
        cars = [cars_by_id[car_id] for car_id in chunk_ids]
        lanes.append(
            {
                "lane_id": lane["lane_id"],
                "capacity": int(lane["capacity"]),
                "lane_status": lane["lane_status"],
                "cars": [_format_car(car, idx + 1) for idx, car in enumerate(cars)],
            }
        )

    unassigned = [_format_car(cars_by_id[car_id], idx + 1) for idx, car_id in enumerate(unassigned_ids)]
    return lanes, unassigned


def _fitness(
    chromosome: list[str],
    cars_by_id: dict[str, dict],
    lanes_df: pd.DataFrame,
    lane_capacity: int,
) -> float:
    lanes, unassigned = _decode_chromosome(chromosome, cars_by_id, lanes_df, lane_capacity)
    penalties = calculate_lane_penalties(lanes, lane_capacity)

    # destination_penalty：同一备车道内目的地越分散，惩罚越高。
    # direction_penalty：同一备车道内运输方向越分散，惩罚越高。
    # fifo_penalty：计划出库时间更早的车辆被排在后面时，产生先进先出违背惩罚。
    # utilization_penalty：备车道未装满时产生惩罚，体现 8 辆一组的组织要求。
    # unassigned_penalty：可用备车道不足导致车辆无法分配时，产生较高惩罚。
    # model_mix_penalty：车型组合过于分散时，装载匹配复杂度更高，因此增加惩罚。
    return (
        penalties["destination_penalty"] * WEIGHTS["destination_penalty"]
        + penalties["direction_penalty"] * WEIGHTS["direction_penalty"]
        + penalties["fifo_penalty"] * WEIGHTS["fifo_penalty"]
        + penalties["utilization_penalty"] * WEIGHTS["utilization_penalty"]
        + len(unassigned) * WEIGHTS["unassigned_penalty"]
        + penalties["model_mix_penalty"] * WEIGHTS["model_mix_penalty"]
    )


def _ordered_crossover(parent_a: list[str], parent_b: list[str]) -> list[str]:
    size = len(parent_a)
    left, right = sorted(random.sample(range(size), 2))
    child = [None] * size
    child[left:right] = parent_a[left:right]
    fill_values = [gene for gene in parent_b if gene not in child]
    fill_index = 0
    for idx in range(size):
        if child[idx] is None:
            child[idx] = fill_values[fill_index]
            fill_index += 1
    return child


def _mutate(chromosome: list[str], mutation_rate: float) -> list[str]:
    mutated = chromosome[:]
    if random.random() < mutation_rate:
        i, j = random.sample(range(len(mutated)), 2)
        mutated[i], mutated[j] = mutated[j], mutated[i]
    return mutated


def _tournament_select(population: list[list[str]], scores: list[float], k: int = 3) -> list[str]:
    candidates = random.sample(list(zip(population, scores)), min(k, len(population)))
    return min(candidates, key=lambda item: item[1])[0][:]


def run_genetic_staging(
    cars_df: pd.DataFrame,
    lanes_df: pd.DataFrame,
    population_size: int = 50,
    generations: int = 100,
    crossover_rate: float = 0.8,
    mutation_rate: float = 0.1,
    elite_size: int = 2,
    lane_capacity: int = 8,
    seed: int = 42,
) -> dict[str, Any]:
    random.seed(seed)
    np.random.seed(seed)

    car_ids = cars_df["car_id"].tolist()
    cars_by_id = {row["car_id"]: row for row in cars_df.to_dict(orient="records")}
    population = [random.sample(car_ids, len(car_ids)) for _ in range(population_size)]
    convergence: list[dict] = []

    best_chromosome = population[0]
    best_score = float("inf")

    for generation in range(1, generations + 1):
        scores = [_fitness(chromosome, cars_by_id, lanes_df, lane_capacity) for chromosome in population]
        ranked = sorted(zip(population, scores), key=lambda item: item[1])

        if ranked[0][1] < best_score:
            best_chromosome = ranked[0][0][:]
            best_score = ranked[0][1]

        convergence.append({"generation": generation, "best_fitness": round(best_score, 2)})

        next_population = [chromosome[:] for chromosome, _ in ranked[:elite_size]]
        while len(next_population) < population_size:
            parent_a = _tournament_select(population, scores)
            parent_b = _tournament_select(population, scores)
            child = (
                _ordered_crossover(parent_a, parent_b)
                if random.random() < crossover_rate
                else parent_a[:]
            )
            next_population.append(_mutate(child, mutation_rate))

        population = next_population

    lanes, unassigned = _decode_chromosome(best_chromosome, cars_by_id, lanes_df, lane_capacity)
    metrics = calculate_metrics(
        lanes,
        len(cars_df),
        len(lanes_df),
        lane_capacity,
        best_fitness=best_score,
        convergence=convergence,
    )

    return {
        "algorithm": "genetic",
        "algorithm_name": "遗传算法",
        "description": "采用车辆 ID 排列编码，通过选择、交叉、变异和精英保留搜索备车道分配与排序方案。",
        "lanes": lanes,
        "unassigned_cars": unassigned,
        "metrics": metrics,
        "best_fitness": round(best_score, 2),
        "convergence": convergence,
        "parameters": {
            "population_size": population_size,
            "generations": generations,
            "crossover_rate": crossover_rate,
            "mutation_rate": mutation_rate,
            "elite_size": elite_size,
            "lane_capacity": lane_capacity,
            "seed": seed,
        },
    }
