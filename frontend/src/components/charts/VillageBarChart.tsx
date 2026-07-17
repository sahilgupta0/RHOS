import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from "recharts";
import type { VillageStats } from "../../types";

interface VillageBarChartProps {
  data: VillageStats[];
  height?: number;
}

export default function VillageBarChart({ data, height = 300 }: VillageBarChartProps) {
  return (
    <div className="w-full">
      <ResponsiveContainer width="100%" height={height}>
        <BarChart
          data={data}
          layout="vertical"
          margin={{ top: 10, right: 10, left: -20, bottom: 5 }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
          <XAxis
            type="number"
            tick={{ fontSize: 10 }}
            stroke="hsl(var(--muted-foreground))"
          />
          <YAxis
            dataKey="village_name"
            type="category"
            tick={{ fontSize: 10 }}
            stroke="hsl(var(--muted-foreground))"
            width={90}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: "hsl(var(--card))",
              border: "1px solid hsl(var(--border))",
              borderRadius: "12px",
              fontSize: "12px",
            }}
          />
          <Legend wrapperStyle={{ fontSize: "11px", marginTop: "10px" }} />
          <Bar
            dataKey="total_patients"
            fill="#3b82f6"
            name="Total Patients"
            radius={[0, 4, 4, 0]}
          />
          <Bar
            dataKey="active_cases"
            fill="#f59e0b"
            name="Active Cases"
            radius={[0, 4, 4, 0]}
          />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
