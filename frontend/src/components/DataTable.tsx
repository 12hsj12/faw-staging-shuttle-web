interface Column<T> {
  key: keyof T | string;
  title: string;
  render?: (row: T) => string | number;
}

interface DataTableProps<T> {
  columns: Column<T>[];
  data: T[];
  maxRows?: number;
}

export default function DataTable<T extends Record<string, unknown>>({
  columns,
  data,
  maxRows = 12,
}: DataTableProps<T>) {
  const visibleData = data.slice(0, maxRows);
  return (
    <div className="table-wrap">
      <table>
        <thead>
          <tr>
            {columns.map((column) => (
              <th key={String(column.key)}>{column.title}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {visibleData.map((row, index) => (
            <tr key={String(row.car_id ?? row.lane_id ?? index)}>
              {columns.map((column) => (
                <td key={String(column.key)}>
                  {column.render ? column.render(row) : String(row[column.key] ?? "")}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
      {data.length > maxRows && <div className="table-note">仅展示前 {maxRows} 条，共 {data.length} 条。</div>}
    </div>
  );
}
