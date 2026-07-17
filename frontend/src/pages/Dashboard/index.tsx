import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { analyticsApi } from "../../api";
import { cn, getTriageColor, getTriageDotColor } from "../../lib/utils";
import {
  Users,
  AlertTriangle,
  ArrowUpRight,
  Stethoscope,
  Clock,
  TrendingUp,
  MessageSquare,
} from "lucide-react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from "recharts";
import type { DashboardStats } from "../../types";

const CHART_COLORS = ["#3b82f6", "#10b981", "#f59e0b", "#ef4444", "#8b5cf6", "#ec4899", "#06b6d4", "#84cc16"];

// Mock data for when API is unavailable
const mockStats: DashboardStats = {
  total_patients: 300,
  patients_today: 24,
  patients_this_week: 142,
  high_priority_today: 3,
  consultations_today: 18,
  consultations_this_week: 98,
  follow_ups_pending: 15,
  referrals_this_month: 8,
};

const mockTrends = Array.from({ length: 14 }, (_, i) => ({
  date: new Date(Date.now() - (13 - i) * 86400000).toLocaleDateString("en-IN", { month: "short", day: "numeric" }),
  count: Math.floor(Math.random() * 20) + 15,
  high_priority: Math.floor(Math.random() * 5),
}));

const mockDiseases = [
  { condition: "Hypertension", count: 45, percentage: 15 },
  { condition: "Type 2 Diabetes", count: 38, percentage: 12.7 },
  { condition: "ARI", count: 32, percentage: 10.7 },
  { condition: "Malaria", count: 28, percentage: 9.3 },
  { condition: "Dengue", count: 22, percentage: 7.3 },
  { condition: "TB", count: 18, percentage: 6.0 },
];

const recentPatients = [
  { id: "P001", name: "Ramesh Kumar", age: 45, complaint: "Chest pain, breathlessness", priority: "HIGH", time: "10:30 AM" },
  { id: "P002", name: "Sunita Devi", age: 32, complaint: "Fever, cough for 3 days", priority: "MEDIUM", time: "10:15 AM" },
  { id: "P003", name: "Mohan Lal", age: 68, complaint: "Follow-up: Diabetes check", priority: "LOW", time: "9:45 AM" },
  { id: "P004", name: "Geeta Bai", age: 28, complaint: "Skin rash, itching", priority: "LOW", time: "9:30 AM" },
  { id: "P005", name: "Raju Singh", age: 55, complaint: "Severe headache, vomiting", priority: "HIGH", time: "9:00 AM" },
];

export default function Dashboard() {
  const { data: analyticsData } = useQuery({
    queryKey: ["analytics"],
    queryFn: () => analyticsApi.getAnalytics(14),
    retry: false,
  });

  const stats = analyticsData?.dashboard_stats || mockStats;
  const trends = analyticsData?.patient_trends?.map(t => ({
    ...t,
    date: new Date(t.date).toLocaleDateString("en-IN", { month: "short", day: "numeric" }),
  })) || mockTrends;
  const diseases = analyticsData?.disease_distribution || mockDiseases;

  const statCards = [
    { label: "Patients Today", value: stats.patients_today, icon: Users, color: "text-blue-600 dark:text-blue-400", bg: "bg-blue-50 dark:bg-blue-900/20", trend: "+12%" },
    { label: "High Priority", value: stats.high_priority_today, icon: AlertTriangle, color: "text-rose-600 dark:text-rose-400", bg: "bg-rose-50 dark:bg-rose-900/20", trend: "" },
    { label: "Consultations", value: stats.consultations_today, icon: Stethoscope, color: "text-emerald-600 dark:text-emerald-400", bg: "bg-emerald-50 dark:bg-emerald-900/20", trend: "+8%" },
    { label: "Follow-ups Pending", value: stats.follow_ups_pending, icon: Clock, color: "text-amber-600 dark:text-amber-400", bg: "bg-amber-50 dark:bg-amber-900/20", trend: "" },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold">Dashboard</h1>
          <p className="text-sm text-[hsl(var(--muted-foreground))]">
            Overview of today's activity • {new Date().toLocaleDateString("en-IN", { weekday: "long", year: "numeric", month: "long", day: "numeric" })}
          </p>
        </div>
        <Link
          to="/consultation"
          className="flex items-center gap-2 rounded-xl bg-gradient-primary px-5 py-2.5 text-sm font-medium text-white shadow-lg shadow-blue-500/25 transition-all hover:shadow-xl"
        >
          <MessageSquare className="h-4 w-4" />
          New Consultation
        </Link>
      </div>

      {/* Stats cards */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {statCards.map((card) => (
          <div
            key={card.label}
            className="rounded-2xl border border-[hsl(var(--border))] bg-[hsl(var(--card))] p-5 transition-all hover:shadow-lg card-hover"
          >
            <div className="flex items-center justify-between">
              <div className={cn("rounded-xl p-2.5", card.bg)}>
                <card.icon className={cn("h-5 w-5", card.color)} />
              </div>
              {card.trend && (
                <span className="flex items-center gap-0.5 text-xs font-medium text-emerald-600">
                  <TrendingUp className="h-3 w-3" />
                  {card.trend}
                </span>
              )}
            </div>
            <p className="mt-3 text-2xl font-bold">{card.value}</p>
            <p className="text-sm text-[hsl(var(--muted-foreground))]">{card.label}</p>
          </div>
        ))}
      </div>

      {/* Charts row */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        {/* Patient trends chart */}
        <div className="lg:col-span-2 rounded-2xl border border-[hsl(var(--border))] bg-[hsl(var(--card))] p-5">
          <h3 className="text-lg font-semibold mb-4">Patient Trends (14 Days)</h3>
          <ResponsiveContainer width="100%" height={280}>
            <LineChart data={trends}>
              <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
              <XAxis dataKey="date" tick={{ fontSize: 11 }} stroke="hsl(var(--muted-foreground))" />
              <YAxis tick={{ fontSize: 11 }} stroke="hsl(var(--muted-foreground))" />
              <Tooltip
                contentStyle={{
                  backgroundColor: "hsl(var(--card))",
                  border: "1px solid hsl(var(--border))",
                  borderRadius: "12px",
                  fontSize: "12px",
                }}
              />
              <Line type="monotone" dataKey="count" stroke="#3b82f6" strokeWidth={2.5} dot={false} name="Patients" />
              <Line type="monotone" dataKey="high_priority" stroke="#ef4444" strokeWidth={2} dot={false} name="High Priority" />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Disease distribution */}
        <div className="rounded-2xl border border-[hsl(var(--border))] bg-[hsl(var(--card))] p-5">
          <h3 className="text-lg font-semibold mb-4">Top Conditions</h3>
          <ResponsiveContainer width="100%" height={200}>
            <PieChart>
              <Pie data={diseases.slice(0, 6)} dataKey="count" nameKey="condition" cx="50%" cy="50%" outerRadius={80} innerRadius={40}>
                {diseases.slice(0, 6).map((_, i) => (
                  <Cell key={i} fill={CHART_COLORS[i % CHART_COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
          <div className="mt-2 space-y-1.5">
            {diseases.slice(0, 4).map((d, i) => (
              <div key={d.condition} className="flex items-center justify-between text-xs">
                <div className="flex items-center gap-2">
                  <div className="h-2.5 w-2.5 rounded-full" style={{ backgroundColor: CHART_COLORS[i] }} />
                  <span className="text-[hsl(var(--muted-foreground))]">{d.condition}</span>
                </div>
                <span className="font-medium">{d.count}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Patient Queue */}
      <div className="rounded-2xl border border-[hsl(var(--border))] bg-[hsl(var(--card))]">
        <div className="flex items-center justify-between border-b border-[hsl(var(--border))] p-5">
          <h3 className="text-lg font-semibold">Patient Queue</h3>
          <span className="text-sm text-[hsl(var(--muted-foreground))]">{recentPatients.length} waiting</span>
        </div>
        <div className="divide-y divide-[hsl(var(--border))]">
          {recentPatients.map((patient) => (
            <Link
              key={patient.id}
              to={`/patient/${patient.id}`}
              className="flex items-center justify-between p-4 hover:bg-[hsl(var(--accent))] transition-colors"
            >
              <div className="flex items-center gap-3">
                <div className={cn("h-2.5 w-2.5 rounded-full", getTriageDotColor(patient.priority))} />
                <div>
                  <p className="text-sm font-medium">{patient.name}</p>
                  <p className="text-xs text-[hsl(var(--muted-foreground))]">{patient.complaint}</p>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <span className={cn("rounded-full px-2.5 py-0.5 text-[10px] font-semibold uppercase", getTriageColor(patient.priority))}>
                  {patient.priority}
                </span>
                <span className="text-xs text-[hsl(var(--muted-foreground))]">{patient.time}</span>
                <ArrowUpRight className="h-4 w-4 text-[hsl(var(--muted-foreground))]" />
              </div>
            </Link>
          ))}
        </div>
      </div>
    </div>
  );
}
