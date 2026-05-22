import { BarChart3, Database, FileText, LayoutDashboard, Route, Shuffle } from "lucide-react";
import { useState } from "react";

import Dashboard from "./pages/Dashboard";
import DataManagement from "./pages/DataManagement";
import ProjectInfo from "./pages/ProjectInfo";
import ShuttlePlaceholder from "./pages/ShuttlePlaceholder";
import StagingOptimization from "./pages/StagingOptimization";

type PageKey = "dashboard" | "data" | "optimization" | "shuttle" | "info";

const navItems = [
  { key: "dashboard", label: "首页仪表盘", icon: LayoutDashboard },
  { key: "data", label: "数据管理", icon: Database },
  { key: "optimization", label: "备车优化", icon: Shuffle },
  { key: "shuttle", label: "短驳仿真占位", icon: Route },
  { key: "info", label: "项目说明", icon: FileText },
] as const;

export default function App() {
  const [page, setPage] = useState<PageKey>("dashboard");

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <BarChart3 size={28} />
          <div>
            <strong>一汽绿运</strong>
            <span>备车优化展示平台</span>
          </div>
        </div>
        <nav>
          {navItems.map((item) => {
            const Icon = item.icon;
            return (
              <button
                key={item.key}
                className={page === item.key ? "active" : ""}
                onClick={() => setPage(item.key as PageKey)}
                title={item.label}
              >
                <Icon size={18} />
                <span>{item.label}</span>
              </button>
            );
          })}
        </nav>
      </aside>
      <main>
        {page === "dashboard" && <Dashboard />}
        {page === "data" && <DataManagement />}
        {page === "optimization" && <StagingOptimization />}
        {page === "shuttle" && <ShuttlePlaceholder />}
        {page === "info" && <ProjectInfo />}
      </main>
    </div>
  );
}
