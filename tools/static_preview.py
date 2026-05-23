from __future__ import annotations

import csv
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "backend" / "app" / "data"
OUTPUT_DIR = ROOT / "preview"
OUTPUT_FILE = OUTPUT_DIR / "index.html"
LANE_CAPACITY = 8


def read_csv(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8-sig", newline="") as file:
        return list(csv.DictReader(file))


def parse_time(value: str) -> datetime:
    return datetime.strptime(value, "%Y-%m-%d %H:%M")


def build_baseline(cars: list[dict], lanes: list[dict]) -> list[dict]:
    sorted_cars = sorted(cars, key=lambda car: (parse_time(car["outbound_time"]), car["destination"], car["direction"]))
    grouped: list[dict] = []
    buckets: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for car in sorted_cars:
        buckets[(car["destination"], car["direction"])].append(car)
    for _, bucket in buckets.items():
        grouped.extend(bucket)

    result = []
    cursor = 0
    for lane in lanes:
        chunk = grouped[cursor : cursor + LANE_CAPACITY]
        cursor += LANE_CAPACITY
        result.append({**lane, "cars": chunk})
    return result


def purity(values: list[str]) -> float:
    if not values:
        return 0
    counter = Counter(values)
    return max(counter.values()) / len(values)


def fifo_violations(lanes: list[dict]) -> int:
    count = 0
    for lane in lanes:
        times = [parse_time(car["outbound_time"]) for car in lane["cars"]]
        for i in range(len(times)):
            for j in range(i + 1, len(times)):
                if times[i] > times[j]:
                    count += 1
    return count


def metrics(cars: list[dict], lanes: list[dict]) -> dict:
    used = [lane for lane in lanes if lane["cars"]]
    assigned = sum(len(lane["cars"]) for lane in lanes)
    dest = [purity([car["destination"] for car in lane["cars"]]) for lane in used]
    direction = [purity([car["direction"] for car in lane["cars"]]) for lane in used]
    return {
        "total": len(cars),
        "assigned": assigned,
        "unassigned": len(cars) - assigned,
        "used_lanes": len(used),
        "avg_util": assigned / (len(used) * LANE_CAPACITY) if used else 0,
        "dest_conc": sum(dest) / len(dest) if dest else 0,
        "dir_conc": sum(direction) / len(direction) if direction else 0,
        "fifo": fifo_violations(lanes),
    }


def bar_rows(items: list[tuple[str, int]], color: str) -> str:
    max_value = max([value for _, value in items] or [1])
    rows = []
    for label, value in items:
        width = int(value / max_value * 100)
        rows.append(
            f'<div class="bar-row"><span>{label}</span><div><i style="width:{width}%;background:{color}"></i></div><b>{value}</b></div>'
        )
    return "\n".join(rows)


def lane_cards(lanes: list[dict]) -> str:
    cards = []
    for lane in lanes:
        cars = lane["cars"]
        car_items = "".join(
            f"<li><strong>{index}. {car['car_id']}</strong><span>{car['destination']} · {car['direction']} · {car['model_type']}</span></li>"
            for index, car in enumerate(cars, start=1)
        )
        util = int(len(cars) / LANE_CAPACITY * 100)
        cards.append(
            f"""
            <article class="lane">
              <header><strong>{lane['lane_id']}</strong><span>{len(cars)}/{LANE_CAPACITY} 辆</span></header>
              <div class="progress"><i style="width:{util}%"></i></div>
              <ol>{car_items}</ol>
            </article>
            """
        )
    return "\n".join(cards)


def main() -> None:
    cars = read_csv(DATA_DIR / "car_orders.csv")
    lanes = read_csv(DATA_DIR / "staging_lanes.csv")
    baseline_lanes = build_baseline(cars, lanes)
    stat = metrics(cars, baseline_lanes)
    destination_counts = Counter(car["destination"] for car in cars)
    lane_counts = [(lane["lane_id"], len(lane["cars"])) for lane in baseline_lanes]

    OUTPUT_DIR.mkdir(exist_ok=True)
    OUTPUT_FILE.write_text(
        f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>一汽绿运 Web 预览</title>
  <style>
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; font-family: "Microsoft YaHei", Arial, sans-serif; background: #f3f6fb; color: #172033; }}
    .shell {{ display: grid; grid-template-columns: 240px 1fr; min-height: 100vh; }}
    aside {{ background: #172033; color: white; padding: 24px 18px; }}
    aside strong {{ display: block; font-size: 22px; margin-bottom: 6px; }}
    aside span {{ color: #b8c4d8; }}
    nav {{ display: grid; gap: 8px; margin-top: 28px; }}
    nav a {{ color: #dbeafe; text-decoration: none; padding: 12px; border-radius: 8px; background: rgba(255,255,255,.08); }}
    main {{ padding: 28px; display: grid; gap: 20px; }}
    h1 {{ margin: 0; font-size: 28px; }}
    .muted {{ color: #64748b; margin-top: 8px; }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 14px; }}
    .card, .panel {{ background: white; border: 1px solid #dbe3ef; border-radius: 8px; padding: 18px; }}
    .card span {{ color: #64748b; font-size: 13px; }}
    .card b {{ display: block; font-size: 26px; margin-top: 8px; }}
    .charts {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(360px, 1fr)); gap: 18px; }}
    .bar-row {{ display: grid; grid-template-columns: 88px 1fr 36px; gap: 10px; align-items: center; margin: 10px 0; font-size: 14px; }}
    .bar-row div {{ height: 12px; background: #e2e8f0; border-radius: 99px; overflow: hidden; }}
    .bar-row i {{ display: block; height: 100%; }}
    .lanes {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 14px; }}
    .lane {{ border: 1px solid #dbe3ef; border-radius: 8px; padding: 14px; background: #fff; }}
    .lane header {{ display: flex; justify-content: space-between; }}
    .progress {{ height: 8px; background: #e2e8f0; border-radius: 99px; overflow: hidden; margin: 12px 0; }}
    .progress i {{ display: block; height: 100%; background: #16a34a; }}
    li {{ margin: 8px 0; }}
    li span {{ display: block; color: #64748b; font-size: 13px; }}
    @media (max-width: 820px) {{ .shell {{ grid-template-columns: 1fr; }} }}
  </style>
</head>
<body>
  <div class="shell">
    <aside>
      <strong>一汽绿运</strong>
      <span>备车优化展示平台</span>
      <nav>
        <a href="#dashboard">首页仪表盘</a>
        <a href="#lanes">备车道分配</a>
        <a href="#shuttle">短驳占位说明</a>
      </nav>
    </aside>
    <main>
      <section id="dashboard">
        <h1>自动验收预览</h1>
        <p class="muted">当前页由项目 CSV 模拟数据生成，用于在依赖安装受限时快速呈现 Web 端结果。</p>
      </section>
      <section class="grid">
        <div class="card"><span>待出库整车数量</span><b>{stat['total']} 辆</b></div>
        <div class="card"><span>已分配整车数量</span><b>{stat['assigned']} 辆</b></div>
        <div class="card"><span>未分配整车数量</span><b>{stat['unassigned']} 辆</b></div>
        <div class="card"><span>已使用备车道</span><b>{stat['used_lanes']} 条</b></div>
        <div class="card"><span>平均利用率</span><b>{stat['avg_util']:.0%}</b></div>
        <div class="card"><span>同目的地集中度</span><b>{stat['dest_conc']:.0%}</b></div>
        <div class="card"><span>同方向集中度</span><b>{stat['dir_conc']:.0%}</b></div>
        <div class="card"><span>FIFO 违背次数</span><b>{stat['fifo']} 次</b></div>
      </section>
      <section class="charts">
        <div class="panel"><h2>备车道利用率</h2>{bar_rows(lane_counts, "#2563eb")}</div>
        <div class="panel"><h2>目的地车辆数量分布</h2>{bar_rows(destination_counts.most_common(), "#0f766e")}</div>
      </section>
      <section class="panel" id="lanes">
        <h2>基线规则算法备车道分配与排序</h2>
        <div class="lanes">{lane_cards(baseline_lanes)}</div>
      </section>
      <section class="panel" id="shuttle">
        <h2>短驳仿真与方案选型</h2>
        <p>本模块对应案例 16。原比赛方案中曾基于 TruckSim 对不同路况、车型、天气下的短驳方案进行仿真对比。当前版本因原始 TruckSim 文件缺失，不展示具体仿真结果，仅保留方法说明与后续扩展入口。</p>
      </section>
    </main>
  </div>
</body>
</html>""",
        encoding="utf-8",
    )
    print(OUTPUT_FILE)


if __name__ == "__main__":
    main()
