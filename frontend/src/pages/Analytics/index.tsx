import { useQuery } from "@tanstack/react-query";
import { analyticsApi } from "../../api";
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, BarChart, Bar,
} from "recharts";
import { TrendingUp, Users, MapPin, Pill } from "lucide-react";

const CHART_COLORS = ["#3b82f6", "#10b981", "#f59e0b", "#ef4444", "#8b5cf6", "#ec4899", "#06b6d4", "#84cc16"];

// Mock data
const mockTrends = Array.from({ length: 30 }, (_, i) => ({
  date: new Date(Date.now() - (29 - i) * 86400000).toLocaleDateString("en-IN", { month: "short", day: "numeric" }),
  count: Math.floor(Math.random() * 25) + 10,
  high_priority: Math.floor(Math.random() * 5),
}));

const mockDiseases = [
  { condition: "Hypertension", count: 45, percentage: 15 },
  { condition: "Type 2 Diabetes", count: 38, percentage: 12.7 },
  { condition: "ARI", count: 32, percentage: 10.7 },
  { condition: "Malaria", count: 28, percentage: 9.3 },
  { condition: "Dengue", count: 22, percentage: 7.3 },
  { condition: "TB", count: 18, percentage: 6.0 },
  { condition: "Anemia", count: 16, percentage: 5.3 },
  { condition: "Gastroenteritis", count: 14, percentage: 4.7 },
];

const mockVillages = [
  { village_name: "Khandela", total_patients: 45, active_cases: 3, high_priority: 1 },
  { village_name: "Ringus", total_patients: 38, active_cases: 2, high_priority: 0 },
  { village_name: "Neem Ka Thana", total_patients: 32, active_cases: 4, high_priority: 2 },
  { village_name: "Sri Madhopur", total_patients: 28, active_cases: 1, high_priority: 0 },
  { village_name: "Chomu", total_patients: 42, active_cases: 5, high_priority: 1 },
  { village_name: "Phulera", total_patients: 22, active_cases: 2, high_priority: 1 },
];

const mockMedicines = [
  { name: "Paracetamol", count: 89 },
  { name: "Metformin", count: 72 },
  { name: "Amlodipine", count: 65 },
  { name: "Amoxicillin", count: 58 },
  { name: "Omeprazole", count: 45 },
  { name: "Atorvastatin", count: 38 },
];

export default function Analytics() {
  const { data } = useQuery({
    queryKey: ["analytics", 30],
    queryFn: () => analyticsApi.getAnalytics(30),
    retry: false,
  });

  const trends = data?.patient_trends?.map(t => ({
    ...t,
    date: new Date(t.date).toLocaleDateString("en-IN", { month: "short", day: "numeric" }),
  })) || mockTrends;
  const diseases = data?.disease_distribution || mockDiseases;
  const villages = data?.village_stats || mockVillages;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Analytics</h1>
        <p className="text-sm text-[hsl(var(--muted-foreground))]">
          Healthcare metrics and insights across the service area
        </p>
      </div>

      {/* Patient Trends — Full Width */}
      <div className="rounded-2xl border border-[hsl(var(--border))] bg-[hsl(var(--card))] p-5">
        <div className="flex items-center gap-2 mb-4">
          <TrendingUp className="h-5 w-5 text-blue-500" />
          <h3 className="text-lg font-semibold">Patient Trends (30 Days)</h3>
        </div>
        <ResponsiveContainer width="100%" height={320}>
          <LineChart data={trends}>
            <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
            <XAxis dataKey="date" tick={{ fontSize: 10 }} stroke="hsl(var(--muted-foreground))" interval={2} />
            <YAxis tick={{ fontSize: 11 }} stroke="hsl(var(--muted-foreground))" />
            <Tooltip contentStyle={{ backgroundColor: "hsl(var(--card))", border: "1px solid hsl(var(--border))", borderRadius: "12px", fontSize: "12px" }} />
            <Line type="monotone" dataKey="count" stroke="#3b82f6" strokeWidth={2.5} dot={false} name="Total Patients" />
            <Line type="monotone" dataKey="high_priority" stroke="#ef4444" strokeWidth={2} dot={false} name="High Priority" />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Disease + Village Stats */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Disease Distribution */}
        <div className="rounded-2xl border border-[hsl(var(--border))] bg-[hsl(var(--card))] p-5">
          <div className="flex items-center gap-2 mb-4">
            <Users className="h-5 w-5 text-emerald-500" />
            <h3 className="text-lg font-semibold">Disease Distribution</h3>
          </div>
          <div className="flex flex-col md:flex-row items-center gap-4">
            <ResponsiveContainer width="100%" height={240}>
              <PieChart>
                <Pie data={diseases} dataKey="count" nameKey="condition" cx="50%" cy="50%" outerRadius={90} innerRadius={50}>
                  {diseases.map((_, i) => (
                    <Cell key={i} fill={CHART_COLORS[i % CHART_COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="mt-4 grid grid-cols-2 gap-2">
            {diseases.map((d, i) => (
              <div key={d.condition} className="flex items-center gap-2 text-xs">
                <div className="h-2.5 w-2.5 rounded-full shrink-0" style={{ backgroundColor: CHART_COLORS[i % CHART_COLORS.length] }} />
                <span className="text-[hsl(var(--muted-foreground))] truncate">{d.condition}</span>
                <span className="font-medium ml-auto">{d.percentage}%</span>
              </div>
            ))}
          </div>
        </div>

        {/* Village Statistics */}
        <div className="rounded-2xl border border-[hsl(var(--border))] bg-[hsl(var(--card))] p-5">
          <div className="flex items-center gap-2 mb-4">
            <MapPin className="h-5 w-5 text-violet-500" />
            <h3 className="text-lg font-semibold">Village Statistics</h3>
          </div>
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={villages} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
              <XAxis type="number" tick={{ fontSize: 11 }} stroke="hsl(var(--muted-foreground))" />
              <YAxis dataKey="village_name" type="category" tick={{ fontSize: 11 }} stroke="hsl(var(--muted-foreground))" width={100} />
              <Tooltip contentStyle={{ backgroundColor: "hsl(var(--card))", border: "1px solid hsl(var(--border))", borderRadius: "12px", fontSize: "12px" }} />
              <Bar dataKey="total_patients" fill="#3b82f6" radius={[0, 6, 6, 0]} name="Total" />
              <Bar dataKey="active_cases" fill="#f59e0b" radius={[0, 6, 6, 0]} name="Active" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Medicine Usage */}
      <div className="rounded-2xl border border-[hsl(var(--border))] bg-[hsl(var(--card))] p-5">
        <div className="flex items-center gap-2 mb-4">
          <Pill className="h-5 w-5 text-amber-500" />
          <h3 className="text-lg font-semibold">Most Prescribed Medicines</h3>
        </div>
        <ResponsiveContainer width="100%" height={260}>
          <BarChart data={mockMedicines}>
            <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
            <XAxis dataKey="name" tick={{ fontSize: 11 }} stroke="hsl(var(--muted-foreground))" />
            <YAxis tick={{ fontSize: 11 }} stroke="hsl(var(--muted-foreground))" />
            <Tooltip contentStyle={{ backgroundColor: "hsl(var(--card))", border: "1px solid hsl(var(--border))", borderRadius: "12px", fontSize: "12px" }} />
            <Bar dataKey="count" fill="#8b5cf6" radius={[6, 6, 0, 0]} name="Times Prescribed" />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
