import { useEffect, useState } from "react";

import { api } from "../api/client";
import DataTable from "../components/DataTable";
import type { CarOrder, StagingLane } from "../types/logistics";

export default function DataManagement() {
  const [cars, setCars] = useState<CarOrder[]>([]);
  const [lanes, setLanes] = useState<StagingLane[]>([]);

  useEffect(() => {
    api.getCars().then((res) => setCars(res.data));
    api.getLanes().then((res) => setLanes(res.data));
  }, []);

  return (
    <div className="page">
      <div className="page-title">
        <h1>数据管理</h1>
        <p>展示用于 Demo 的模拟整车数据和备车道数据，所有数据均非真实企业数据。</p>
      </div>
      <section className="panel">
        <h2>整车出库模拟数据</h2>
        <DataTable
          data={cars as unknown as Record<string, unknown>[]}
          maxRows={18}
          columns={[
            { key: "car_id", title: "整车编号" },
            { key: "model_type", title: "车型" },
            { key: "color", title: "颜色" },
            { key: "offline_time", title: "下线时间" },
            { key: "outbound_time", title: "计划出库时间" },
            { key: "destination", title: "目的地" },
            { key: "direction", title: "方向" },
            { key: "priority", title: "优先级" },
          ]}
        />
      </section>
      <section className="panel">
        <h2>备车道模拟数据</h2>
        <DataTable
          data={lanes as unknown as Record<string, unknown>[]}
          columns={[
            { key: "lane_id", title: "备车道编号" },
            { key: "capacity", title: "容量" },
            { key: "lane_status", title: "状态" },
          ]}
        />
      </section>
    </div>
  );
}
