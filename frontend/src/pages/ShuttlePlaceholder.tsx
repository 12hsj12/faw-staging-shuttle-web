export default function ShuttlePlaceholder() {
  return (
    <div className="page">
      <div className="page-title">
        <h1>短驳仿真与方案选型</h1>
        <p>该页面仅保留案例 16 的研究方法说明，不展示任何虚构仿真结果。</p>
      </div>
      <section className="panel readable">
        <p>
          本模块对应案例 16：整车售前短驳运输“零公里”方案选型。原比赛方案中曾基于 TruckSim
          对不同路况、车型、天气下的短驳方案进行仿真对比，并结合成本、效率、安全等指标进行方案选型。
          当前 Web Demo 聚焦备车优化算法与系统展示，因原始 TruckSim 仿真文件缺失，本模块暂不展示具体仿真结果，
          仅保留方法说明与后续扩展入口。
        </p>
      </section>
      <div className="placeholder-grid">
        {[
          ["原 TruckSim 仿真", "暂未接入"],
          ["路况维度", "预留"],
          ["车型维度", "预留"],
          ["天气维度", "预留"],
          ["方案选型结果", "预留"],
        ].map(([title, status]) => (
          <article className="placeholder-item" key={title}>
            <span>{title}</span>
            <strong>{status}</strong>
          </article>
        ))}
      </div>
    </div>
  );
}
