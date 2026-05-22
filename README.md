# 一汽绿运：备车优化与短驳方案展示平台

本项目是一个用于简历展示和面试讲解的 B/S 架构 Web Demo，英文名为 **FAW Staging & Shuttle Web Platform**。项目来源于“长春国际汽车城&一汽物流杯”第八届全国大学生物流设计大赛案例文件，当前重构版本重点实现案例 14 的整车出库备车优化，并为案例 16 的短驳仿真保留占位说明页面。

> 重要说明：本项目所有 CSV 数据均为模拟数据，不是企业真实业务数据；当前版本没有复现 TruckSim，也没有编造任何短驳仿真结果。

## 项目背景

整车从主机厂下线后进入物流园，出库前需要根据计划出库时间、目的地、运输方向、车型和备车道容量进行备车。备车方案会影响后续装车效率、先进先出执行情况、同方向车辆集中程度和备车道利用率。

原比赛方案还包含案例 16：整车售前短驳运输“零公里”方案选型，当时曾基于 TruckSim 对不同路况、车型和天气进行仿真对比。由于当前已找不到原始 TruckSim 文件，本项目只保留“短驳仿真与方案选型”页面入口和方法说明，不展示具体仿真数据。

## 当前项目重点

- 用模拟数据展示整车出库备车场景；
- 实现基线规则算法；
- 实现遗传算法求解备车道分配与排序；
- 展示遗传算法收敛曲线；
- 展示基线算法与遗传算法对比指标；
- 用 React 前端呈现 Dashboard、数据管理、备车优化、短驳占位和项目说明页面。

## 技术栈

- 前端：React、Vite、TypeScript、Recharts、lucide-react；
- 后端：Python、FastAPI、Pandas、NumPy；
- 数据：CSV 模拟数据；
- 算法：基线规则算法、遗传算法。

## 项目结构

```text
faw-staging-shuttle-web/
  README.md
  AGENTS.md
  docs/
    problem_brief.md
    reference/
      物流设计大赛案例文件.pdf
  backend/
    requirements.txt
    app/
      main.py
      routers/
      services/
      algorithms/
      data/
        car_orders.csv
        staging_lanes.csv
  frontend/
    package.json
    index.html
    src/
      api/
      components/
      pages/
      types/
```

## 数据说明

`backend/app/data/car_orders.csv` 包含 72 条模拟整车数据，字段包括整车编号、车型、颜色、下线时间、计划出库时间、目的地、运输方向和优先级。

`backend/app/data/staging_lanes.csv` 包含 12 条模拟备车道数据，每条备车道容量默认为 8。

这些数据仅用于展示算法流程和 Web 页面效果，不代表一汽物流或任何企业的真实运营数据。

## 算法说明

基线规则算法：

1. 按 `outbound_time` 从早到晚排序；
2. 按 `destination` 和 `direction` 分组；
3. 每 8 辆切分为一个备车组；
4. 依次分配到可用备车道；
5. 输出每条备车道内车辆排序。

遗传算法：

1. 使用车辆 ID 排列作为染色体；
2. 按染色体顺序每 8 辆解码为一个备车组；
3. 依次分配到备车道；
4. 适应度函数采用惩罚项越小越好的设计；
5. 惩罚项包括目的地分散惩罚、方向分散惩罚、FIFO 违背惩罚、利用率惩罚、未分配惩罚和车型混合惩罚；
6. 使用选择、交叉、变异和精英保留迭代搜索较优方案。

默认参数：

```text
population_size = 50
generations = 100
crossover_rate = 0.8
mutation_rate = 0.1
elite_size = 2
lane_capacity = 8
```

## 后端 API

```text
GET  /api/health
GET  /api/cars
GET  /api/staging-lanes
POST /api/staging/baseline
POST /api/staging/genetic
GET  /api/staging/comparison
GET  /api/project-info
```

`/api/staging/baseline` 返回基线算法备车结果、指标统计和算法说明。

`/api/staging/genetic` 支持传入遗传算法参数，返回最优分配方案、指标统计、最优适应度、收敛曲线和参数配置。

`/api/staging/comparison` 返回基线算法与遗传算法在备车道数量、平均利用率、集中度、FIFO 违背次数、未分配车辆数和综合惩罚值上的对比。

## 前端页面

- 首页仪表盘：展示核心指标、备车道利用率、目的地分布、收敛曲线和算法对比；
- 数据管理：展示模拟整车数据和备车道数据；
- 备车优化：选择算法、设置遗传算法参数、运行优化、查看备车道分配与排序；
- 短驳仿真与方案选型：保留案例 16 方法说明，不展示假数据；
- 项目说明：展示项目来源、案例关系、建模思路和后续扩展方向。

## 运行方式

后端：

```powershell
cd E:\workworkwork\faw-staging-shuttle-web
python -m pip install -r backend\requirements.txt
$env:PYTHONPATH="E:\workworkwork\faw-staging-shuttle-web\backend"
uvicorn app.main:app --app-dir backend --reload
```

前端：

```powershell
cd E:\workworkwork\faw-staging-shuttle-web\frontend
npm install
npm run dev
```

浏览器访问：

```text
http://localhost:5173
```

如需修改后端地址，可在前端设置环境变量：

```text
VITE_API_BASE=http://127.0.0.1:8000
```

## 当前局限

- 数据为模拟数据，未接入真实 VWMS/TMS；
- 车型装载匹配规则做了简化，没有复现真实轿运车装载约束；
- 遗传算法为 MVP 版本，未加入局部搜索、多目标 Pareto 或自适应参数；
- 短驳 TruckSim 原始仿真文件缺失，因此只保留占位页面；
- 未实现登录权限、数据库持久化、Docker 或微服务。

## 后续扩展方向

- 引入更细的车型尺寸、轿运车层位和装车顺序约束；
- 用脱敏业务数据校准权重；
- 增加多目标遗传算法、禁忌搜索或模拟退火对比；
- 增加方案导出和算法参数实验记录；
- 若找回 TruckSim 原始文件，再接入真实仿真结果，不编造数据。

## 简历项目描述

一汽物流“备车 + 短驳”调度优化 Web 平台：

- 面向整车物流园出库场景，抽象备车道分配与排序问题，综合先进先出、同目的地/同方向、8 辆一组和备车道容量等约束，设计遗传算法生成备车方案。
- 构建基线规则算法与遗传算法对比实验，输出备车道利用率、同向集中度、FIFO 违背次数、未分配车辆数和综合惩罚值等指标，并展示遗传算法收敛曲线。
- 使用 FastAPI + React 搭建 B/S 架构 Web Demo，实现整车数据管理、备车优化计算、结果可视化和短驳仿真占位说明。

## 面试讲解话术

这个项目来源于全国大学生物流设计大赛的一汽物流案例。原赛题包含多个方向，我们当时节选了案例 14 和案例 16。案例 14 我主要聚焦备车问题，也就是整车出库前如何按照目的地、方向、先进先出和轿运车装载规则，将待出库车辆分配到备车道并确定排序。

备车问题本质上是一个带业务约束的组合优化问题。我在项目中将车辆序列作为遗传算法染色体，通过解码得到不同备车道的车辆分组与排序，再基于同目的地集中度、同方向集中度、FIFO 违背次数、备车道利用率和未分配车辆数设计适应度函数。为了便于对比，我还实现了一个按出库时间和目的地方向分组的基线规则算法。

案例 16 是短驳问题，我们当时使用 TruckSim 做过不同路况、不同车型、不同天气下的仿真对比，用于方案选型。但由于原始仿真文件目前找不到，所以这次 Web 重构没有编造仿真结果，而是在前端保留了短驳仿真占位页面，说明该模块的研究方法和后续扩展方向。
