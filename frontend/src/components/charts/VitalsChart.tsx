import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from "recharts";
import type { Vital } from "../../types";

interface VitalsChartProps {
  data: Vital[];
  height?: number;
}

export default function VitalsChart({ data, height = 280 }: VitalsChartProps) {
  // Sort data chronologically for plotting
  const chartData = [...data].sort(
    (a, b) => new Date(a.recorded_at).getTime() - new Date(b.recorded_at).getTime()
  ).map((v) => ({
    ...v,
    date: new Date(v.recorded_at).toLocaleDateString("en-IN", { month: "short", day: "numeric" }),
  }));

  return (
    <div className="w-full">
      <ResponsiveContainer width="100%" height={height}>
        <LineChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
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
            dataKey="bp_systolic"
            stroke="#ef4444"
            strokeWidth={2}
            name="BP Systolic"
            connectNulls
          />
          <Line
            type="monotone"
            dataKey="bp_diastolic"
            stroke="#f97316"
            strokeWidth={2}
            name="BP Diastolic"
            connectNulls
          />
          <Line
            type="monotone"
            dataKey="heart_rate"
            stroke="#3b82f6"
            strokeWidth={2}
            name="Heart Rate"
            connectNulls
          />
          <Line
            type="monotone"
            dataKey="spo2"
            stroke="#10b981"
            strokeWidth={2}
            name="SpO₂"
            connectNulls
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
