import { useParams, Link } from "react-router-dom";
import { useState, useEffect } from "react";
import { cn, getTriageColor, formatDate } from "../../lib/utils";
import {
  ArrowLeft,
  Phone,
  MapPin,
  Heart,
  Activity,
  Thermometer,
  Wind,
  AlertTriangle,
  FileText,
  Calendar,
} from "lucide-react";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";
import { patientsApi, consultationApi } from "../../api";
import LoadingSpinner from "../../components/common/LoadingSpinner";
import { useAuth } from "../../context/AuthContext";

export default function PatientDetails() {
  const { id } = useParams();
  const { user } = useAuth();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [data, setData] = useState<{
    patient: any;
    medical_history: any[];
    vitals: any[];
    allergies: any[];
  } | null>(null);
  const [consultations, setConsultations] = useState<any[]>([]);

  useEffect(() => {
    if (!id) return;
    const fetchData = async () => {
      try {
        setLoading(true);
        const historyRes = await patientsApi.getHistory(id);
        setData(historyRes);
        try {
          const consultationsRes = await consultationApi.list({ patient_id: id });
          setConsultations(consultationsRes);
        } catch (cErr) {
          console.error("Error loading consultations:", cErr);
        }
      } catch (err: any) {
        setError(err.response?.data?.detail || "Failed to load patient history");
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [id]);

  if (loading) {
    return (
      <div className="flex h-64 items-center justify-center">
        <LoadingSpinner />
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="rounded-2xl border border-rose-200 bg-rose-50 p-6 text-rose-700 dark:bg-rose-900/10 dark:text-rose-400">
        <h3 className="font-semibold">Error Loading Patient Data</h3>
        <p className="text-sm mt-1">{error || "Patient not found"}</p>
        <Link to="/dashboard" className="mt-4 inline-block text-sm font-semibold underline">
          Go back to dashboard
        </Link>
      </div>
    );
  }

  const patient = data.patient;
  const history = data.medical_history || [];
  const allergies = data.allergies || [];
  const vitalsList = data.vitals || [];

  // Default vitals if none recorded
  const latestVitals = vitalsList.length > 0 ? vitalsList[0] : {
    bp_systolic: 120,
    bp_diastolic: 80,
    heart_rate: 72,
    spo2: 98,
    temperature: 37.0
  };

  // Convert temperature to Fahrenheit if in Celsius range (e.g. 35-42)
  const formatTemp = (celsius: any) => {
    const val = Number(celsius);
    if (isNaN(val)) return "98.6";
    if (val < 45) {
      return ((val * 9) / 5 + 32).toFixed(1);
    }
    return val.toFixed(1);
  };

  // Prepare chart data (needs chronological order)
  const chartData = [...vitalsList]
    .reverse()
    .map((v: any) => ({
      date: new Date(v.recorded_at || v.created_at || Date.now()).toLocaleDateString("en-IN", { month: "short", day: "numeric" }),
      bp_systolic: Number(v.bp_systolic),
      bp_diastolic: Number(v.bp_diastolic),
      heart_rate: Number(v.heart_rate),
      spo2: Number(v.spo2),
    }));

  return (
    <div className="space-y-6">
      {/* Back + Header */}
      <div>
        {user?.role !== "patient" && (
          <Link to="/dashboard" className="mb-3 inline-flex items-center gap-1 text-sm text-[hsl(var(--muted-foreground))] hover:text-[hsl(var(--foreground))] transition-colors">
            <ArrowLeft className="h-4 w-4" /> Back to Dashboard
          </Link>
        )}

        <div className="flex flex-col md:flex-row gap-4 items-start md:items-center justify-between rounded-2xl bg-gradient-primary p-6 text-white">
          <div className="flex items-center gap-4">
            <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-white/20 text-2xl font-bold backdrop-blur">
              {patient.name.split(" ").map((n: string) => n[0]).join("")}
            </div>
            <div>
              <h1 className="text-2xl font-bold">{patient.name}</h1>
              <p className="text-sm opacity-80">
                {patient.age} yrs • {patient.gender} • {patient.blood_group || "Unknown Blood"} • ID: {patient.id}
              </p>
            </div>
          </div>
          <div className="flex flex-wrap gap-3 text-sm opacity-90">
            {patient.phone && <span className="flex items-center gap-1"><Phone className="h-4 w-4" />{patient.phone}</span>}
            <span className="flex items-center gap-1"><MapPin className="h-4 w-4" />{patient.village_name || "Unknown Village"}, {patient.district || "Rajasthan"}</span>
          </div>
        </div>
      </div>

      {/* Current Vitals */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        {[
          { label: "Blood Pressure", value: `${latestVitals.bp_systolic}/${latestVitals.bp_diastolic}`, unit: "mmHg", icon: Heart, color: "text-rose-500" },
          { label: "Heart Rate", value: String(latestVitals.heart_rate), unit: "bpm", icon: Activity, color: "text-blue-500" },
          { label: "SpO₂", value: `${latestVitals.spo2}%`, unit: "", icon: Wind, color: "text-emerald-500" },
          { label: "Temperature", value: formatTemp(latestVitals.temperature), unit: "°F", icon: Thermometer, color: "text-amber-500" },
        ].map((v) => (
          <div key={v.label} className="rounded-2xl border border-[hsl(var(--border))] bg-[hsl(var(--card))] p-4">
            <v.icon className={cn("h-5 w-5 mb-2", v.color)} />
            <p className="text-2xl font-bold">{v.value}<span className="text-xs font-normal text-[hsl(var(--muted-foreground))] ml-1">{v.unit}</span></p>
            <p className="text-xs text-[hsl(var(--muted-foreground))]">{v.label}</p>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Vitals Chart */}
        <div className="lg:col-span-2 rounded-2xl border border-[hsl(var(--border))] bg-[hsl(var(--card))] p-5">
          <h3 className="text-lg font-semibold mb-4">Vitals Trend</h3>
          {chartData.length > 0 ? (
            <ResponsiveContainer width="100%" height={250}>
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                <XAxis dataKey="date" tick={{ fontSize: 11 }} stroke="hsl(var(--muted-foreground))" />
                <YAxis tick={{ fontSize: 11 }} stroke="hsl(var(--muted-foreground))" />
                <Tooltip contentStyle={{ backgroundColor: "hsl(var(--card))", border: "1px solid hsl(var(--border))", borderRadius: "12px", fontSize: "12px" }} />
                <Line type="monotone" dataKey="bp_systolic" stroke="#ef4444" strokeWidth={2} dot={false} name="Systolic" />
                <Line type="monotone" dataKey="bp_diastolic" stroke="#f97316" strokeWidth={2} dot={false} name="Diastolic" />
                <Line type="monotone" dataKey="heart_rate" stroke="#3b82f6" strokeWidth={2} dot={false} name="Heart Rate" />
              </LineChart>
            </ResponsiveContainer>
          ) : (
            <div className="flex h-[250px] items-center justify-center text-sm text-[hsl(var(--muted-foreground))]">
              No vitals history recorded.
            </div>
          )}
        </div>

        {/* Allergies */}
        <div className="rounded-2xl border border-[hsl(var(--border))] bg-[hsl(var(--card))] p-5">
          <h3 className="text-lg font-semibold mb-3 flex items-center gap-2">
            <AlertTriangle className="h-5 w-5 text-rose-500" /> Allergies
          </h3>
          <div className="space-y-2">
            {allergies.length > 0 ? (
              allergies.map((a: any) => (
                <div key={a.id} className="rounded-xl bg-rose-50 dark:bg-rose-900/10 border border-rose-200 dark:border-rose-800 p-3">
                  <p className="font-semibold text-sm text-rose-700 dark:text-rose-400">{a.allergen}</p>
                  <p className="text-xs text-rose-600 dark:text-rose-400/70">{a.reaction} • {a.severity}</p>
                </div>
              ))
            ) : (
              <p className="text-sm text-[hsl(var(--muted-foreground))]">No known allergies.</p>
            )}
          </div>
        </div>
      </div>

      {/* Medical History + Visit Timeline */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Medical History */}
        <div className="rounded-2xl border border-[hsl(var(--border))] bg-[hsl(var(--card))] p-5">
          <h3 className="text-lg font-semibold mb-3 flex items-center gap-2">
            <FileText className="h-5 w-5 text-blue-500" /> Medical History
          </h3>
          <div className="space-y-3">
            {history.length > 0 ? (
              history.map((h: any) => (
                <div key={h.id} className="rounded-xl border border-[hsl(var(--border))] p-3">
                  <div className="flex items-center justify-between">
                    <p className="font-medium text-sm">{h.condition}</p>
                    <span className={cn(
                      "rounded-full px-2 py-0.5 text-[10px] font-semibold capitalize",
                      h.status === "chronic" ? "bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400" :
                      h.status === "resolved" ? "bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400" :
                      "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400"
                    )}>
                      {h.status}
                    </span>
                  </div>
                  <p className="text-xs text-[hsl(var(--muted-foreground))] mt-1">{h.notes}</p>
                  <p className="text-[10px] text-[hsl(var(--muted-foreground))] mt-1">Diagnosed: {formatDate(h.diagnosed_date)}</p>
                </div>
              ))
            ) : (
              <p className="text-sm text-[hsl(var(--muted-foreground))]">No past medical history recorded.</p>
            )}
          </div>
        </div>

        {/* Recent Consultations/Visits */}
        <div className="rounded-2xl border border-[hsl(var(--border))] bg-[hsl(var(--card))] p-5">
          <h3 className="text-lg font-semibold mb-3 flex items-center gap-2">
            <Calendar className="h-5 w-5 text-violet-500" /> Recent Consultations
          </h3>
          <div className="space-y-4">
            {consultations.length > 0 ? (
              consultations.map((c: any, i: number) => (
                <div key={c.id || i} className="flex gap-3 pb-2 border-b border-[hsl(var(--border))] last:border-0 last:pb-0">
                  <div className="flex flex-col items-center">
                    <div className={cn("h-3 w-3 rounded-full ring-4 ring-[hsl(var(--card))]",
                      c.triage_priority === "HIGH" ? "bg-rose-500" :
                      c.triage_priority === "MEDIUM" ? "bg-amber-500" : "bg-emerald-500"
                    )} />
                  </div>
                  <div className="flex-1 pb-2">
                    <div className="flex items-center justify-between">
                      <p className="text-sm font-medium">{c.chief_complaint || "Routine Consultation"}</p>
                      <span className={cn("rounded-full px-2 py-0.5 text-[10px] font-semibold", getTriageColor(c.triage_priority || "LOW"))}>
                        {c.triage_priority || "LOW"}
                      </span>
                    </div>
                    <p className="text-xs text-[hsl(var(--muted-foreground))] mt-1">
                      Doctor: {c.doctor_name || "Unknown Doctor"}
                    </p>
                    {c.clinical_summary && (
                      <p className="text-xs text-[hsl(var(--muted-foreground))] mt-1 line-clamp-2 bg-[hsl(var(--muted))]/30 p-2 rounded-lg">
                        {c.clinical_summary}
                      </p>
                    )}
                    <div className="flex items-center gap-2 mt-1">
                      <span className="text-[10px] text-[hsl(var(--muted-foreground))]">{formatDate(c.created_at)}</span>
                      <span className="text-[10px] text-[hsl(var(--muted-foreground))] capitalize">{c.status}</span>
                    </div>
                  </div>
                </div>
              ))
            ) : (
              <p className="text-sm text-[hsl(var(--muted-foreground))]">No recent consultations found.</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
