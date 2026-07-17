import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer } from "recharts";

import type { DiseaseDistribution } from "../../types";

const COLORS = ["#3b82f6", "#10b981", "#f59e0b", "#ef4444", "#8b5cf6", "#ec4899", "#06b6d4", "#84cc16"];

interface DiseasePieChartProps {
  data: DiseaseDistribution[];
  height?: number;
}

export default function DiseasePieChart({ data, height = 260 }: DiseasePieChartProps) {
  return (
    <div className="w-full flex flex-col items-center">
      <ResponsiveContainer width="100%" height={height}>
        <PieChart>
          <Pie
            data={data}
            cx="50%"
            cy="50%"
            innerRadius={60}
            outerRadius={90}
            paddingAngle={3}
            dataKey="count"
            nameKey="condition"
          >
            {data.map((_, index) => (
              <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
            ))}
          </Pie>
          <Tooltip
            contentStyle={{
              backgroundColor: "hsl(var(--card))",
              border: "1px solid hsl(var(--border))",
              borderRadius: "12px",
              fontSize: "12px",
            }}
          />
        </PieChart>
      </ResponsiveContainer>
      <div className="mt-4 grid grid-cols-2 gap-x-6 gap-y-1.5 w-full px-4">
        {data.slice(0, 8).map((entry, index) => (
          <div key={entry.condition} className="flex items-center gap-2 text-xs">
            <div
              className="h-3 w-3 rounded-full shrink-0"
              style={{ backgroundColor: COLORS[index % COLORS.length] }}
            />
            <span className="text-[hsl(var(--muted-foreground))] truncate max-w-[120px]">
              {entry.condition}
            </span>
            <span className="font-semibold ml-auto">{entry.count}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
