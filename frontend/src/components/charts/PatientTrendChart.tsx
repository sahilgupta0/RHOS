import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from "recharts";
import type { PatientTrend } from "../../types";

interface PatientTrendChartProps {
  data: PatientTrend[];
  height?: number;
}

export default function PatientTrendChart({ data, height = 300 }: PatientTrendChartProps) {
  return (
    <div className="w-full">
      <ResponsiveContainer width="100%" height={height}>
        <LineChart data={data} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
          <XAxis
            dataKey="date"
            tick={{ fontSize: 10 }}
            stroke="hsl(var(--muted-foreground))"
          />
          <YAxis
            tick={{ fontSize: 11 }}
            stroke="hsl(var(--muted-foreground))"
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
          <Line
            type="monotone"
            dataKey="count"
            stroke="#3b82f6"
            strokeWidth={2.5}
            activeDot={{ r: 6 }}
            name="Daily Patients"
          />
          <Line
            type="monotone"
            dataKey="high_priority"
            stroke="#ef4444"
            strokeWidth={2}
            name="High Priority"
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
