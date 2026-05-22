import { useEffect, useState } from "react";

import { api } from "../api/client";

export default function ProjectInfo() {
  const [info, setInfo] = useState<Record<string, unknown> | null>(null);

  useEffect(() => {
    api.getProjectInfo().then(setInfo);
  }, []);

  return (
    <div className="page">
      <div className="page-title">
        <h1>项目说明</h1>
        <p>用于简历展示和面试讲解的项目背景、建模思路与边界说明。</p>
      </div>
      <section className="panel readable">
        <h2>项目来源</h2>
        <p>{String(info?.source ?? "长春国际汽车城&一汽物流杯第八届全国大学生物流设计大赛案例文件。")}</p>
        <h2>案例 14 与案例 16 的关系</h2>
        <p>
          案例 14 聚焦整车库内管理与出库备车，当前系统将其抽象为备车道分配与车辆排序问题。
          案例 16 聚焦整车售前短驳运输“零公里”方案选型，当前版本只保留方法入口。
        </p>
        <h2>为什么重点做备车</h2>
        <p>
          备车问题可以用模拟数据、可解释规则算法和遗传算法完整呈现，从业务约束、算法建模到 Web
          结果展示都适合简历和面试讲解。TruckSim 原始文件缺失，因此不复现短驳仿真。
        </p>
        <h2>遗传算法建模思路</h2>
        <p>
          系统使用车辆 ID 的排列作为染色体，按顺序每 8 辆解码为一个备车组，再分配到备车道。适应度函数综合目的地集中度、
          方向集中度、FIFO 违背、备车道利用率、未分配车辆和车型混合惩罚，惩罚值越低代表方案越优。
        </p>
        <h2>后续扩展方向</h2>
        <ul>
          <li>使用更丰富的车型装载规则和轿运车顺序约束。</li>
          <li>引入多目标优化算法，对效率、集中度和 FIFO 进行 Pareto 对比。</li>
          <li>若找回原 TruckSim 文件，仅接入真实仿真结果，不编造数据。</li>
        </ul>
      </section>
    </div>
  );
}
