import { useQuery } from "@tanstack/react-query";
import { useAuth } from "../../context/AuthContext";
import { consultationApi } from "../../api";
import {
  Calendar,
  AlertTriangle,
  HeartPulse,
  UserCheck,
  Clock,
  Activity,
  ArrowRight,
} from "lucide-react";
import LoadingSpinner from "../../components/common/LoadingSpinner";


export default function RemindersPage() {
  const { user } = useAuth();
  const patientId = user?.patient_id || "P001";

  const { data: consultations, isLoading } = useQuery({
    queryKey: ["consultations", { patient_id: patientId }],
    queryFn: () => consultationApi.list({ patient_id: patientId, limit: 1 }),
  });

  if (isLoading) {
    return (
      <div className="flex h-[50vh] items-center justify-center">
        <LoadingSpinner />
      </div>
    );
  }

  const latestConsultation = consultations?.[0];

  // Default reminders structure in case consultation has not run yet
  const defaultReminders = {
    followUpDate: "As advised by your physician, or if symptoms worsen.",
    monitoring: [
      "Record your blood pressure twice daily (morning and evening).",
      "Monitor your temperature if you feel warm.",
      "Keep track of any new or changing symptoms.",
    ],
    warningSigns: [
      "Difficulty breathing or chest tightness.",
      "Persistent high fever above 101°F that does not respond to paracetamol.",
      "Severe or worsening pain.",
      "Dizziness, confusion, or extreme weakness.",
    ],
    lifestyle: [
      "Drink at least 2-3 liters of clean, boiled water daily.",
      "Ensure adequate physical rest (7-8 hours of sleep).",
      "Eat light, home-cooked meals. Avoid spicy or fried food.",
    ],
    ashaTasks: [
      "Weekly visit to check vital signs.",
      "Verify adherence to prescribed medication schedule.",
      "Assist in booking next clinical appointment if needed.",
    ],
  };

  // Attempt to parse followup plan details from latest consultation if available
  let reminders = defaultReminders;
  if (latestConsultation?.follow_up_plan) {
    try {
      // If the plan is structured as a JSON string
      const parsed = JSON.parse(latestConsultation.follow_up_plan);
      reminders = {
        followUpDate: parsed.follow_up_date || defaultReminders.followUpDate,
        monitoring: parsed.monitoring_instructions || defaultReminders.monitoring,
        warningSigns: parsed.warning_signs || defaultReminders.warningSigns,
        lifestyle: parsed.lifestyle_recommendations || defaultReminders.lifestyle,
        ashaTasks: parsed.asha_worker_tasks || defaultReminders.ashaTasks,
      };
    } catch {
      // If it is just free text description, put it in monitoring
      reminders = {
        ...defaultReminders,
        followUpDate: latestConsultation.duration || defaultReminders.followUpDate,
        monitoring: [latestConsultation.follow_up_plan],
      };
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold">Health Reminders</h1>
        <p className="text-sm text-[hsl(var(--muted-foreground))]">
          Your personalized care plan, warning signs, and follow-up schedule
        </p>
      </div>

      {/* Follow-up Timeline */}
      <div className="relative overflow-hidden rounded-3xl bg-gradient-to-r from-blue-500 to-cyan-500 p-6 text-white shadow-xl shadow-blue-500/20">
        <div className="absolute right-0 top-0 -mr-6 -mt-6 h-32 w-32 rounded-full bg-white/10 blur-2xl" />
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="flex items-center gap-4">
            <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-white/20 backdrop-blur">
              <Calendar className="h-6 w-6" />
            </div>
            <div>
              <p className="text-xs uppercase tracking-wider text-blue-100 font-semibold">Next Follow-up Recommendation</p>
              <h2 className="text-xl font-bold mt-0.5">{reminders.followUpDate}</h2>
            </div>
          </div>
          <div className="flex items-center gap-1.5 self-start sm:self-auto rounded-full bg-white/20 px-3.5 py-1.5 text-xs font-semibold backdrop-blur">
            <Clock className="h-4 w-4" /> Active Care Plan
          </div>
        </div>
      </div>

      {/* Warning Signs (Critical Section) */}
      <div className="rounded-3xl border border-rose-100 bg-rose-50/30 p-6 dark:border-rose-900/20 dark:bg-rose-950/10">
        <div className="flex items-start gap-4">
          <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-2xl bg-rose-100 text-rose-600 dark:bg-rose-900/30 dark:text-rose-400">
            <AlertTriangle className="h-6 w-6" />
          </div>
          <div className="space-y-3 flex-1">
            <div>
              <h3 className="text-lg font-semibold text-rose-900 dark:text-rose-400">Warning Signs (Red Flags)</h3>
              <p className="text-xs text-rose-700/80 dark:text-rose-400/60 mt-0.5">
                If you experience any of these symptoms, please return to the health center or contact emergency services immediately
              </p>
            </div>
            <ul className="grid grid-cols-1 md:grid-cols-2 gap-2 text-sm text-rose-800 dark:text-rose-400/80">
              {reminders.warningSigns.map((sign, index) => (
                <li key={index} className="flex items-start gap-2 bg-white/60 dark:bg-rose-950/20 rounded-xl p-3 border border-rose-100/50 dark:border-rose-900/10">
                  <ArrowRight className="h-4 w-4 text-rose-500 mt-0.5 shrink-0" />
                  <span>{sign}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>

      {/* Main Grid: Monitoring, Lifestyle, ASHA */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Home Monitoring */}
        <div className="rounded-3xl border border-[hsl(var(--border))] bg-[hsl(var(--card))] p-6 card-hover">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-blue-50 text-blue-600 dark:bg-blue-900/20 dark:text-blue-400 mb-4">
            <Activity className="h-5 w-5" />
          </div>
          <h3 className="text-base font-semibold mb-1.5">Home Monitoring</h3>
          <p className="text-xs text-[hsl(var(--muted-foreground))] mb-4">Steps to monitor your condition at home</p>
          <ul className="space-y-3 text-sm">
            {reminders.monitoring.map((item, index) => (
              <li key={index} className="flex gap-2.5 items-start">
                <span className="flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-blue-50 text-[10px] font-bold text-blue-600 dark:bg-blue-900/20 dark:text-blue-400">
                  {index + 1}
                </span>
                <span className="text-[hsl(var(--foreground))]">{item}</span>
              </li>
            ))}
          </ul>
        </div>

        {/* Lifestyle & Diet */}
        <div className="rounded-3xl border border-[hsl(var(--border))] bg-[hsl(var(--card))] p-6 card-hover">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-emerald-50 text-emerald-600 dark:bg-emerald-900/20 dark:text-emerald-400 mb-4">
            <HeartPulse className="h-5 w-5" />
          </div>
          <h3 className="text-base font-semibold mb-1.5">Lifestyle & Diet</h3>
          <p className="text-xs text-[hsl(var(--muted-foreground))] mb-4">Health and nutritional habits recommended for you</p>
          <ul className="space-y-3 text-sm">
            {reminders.lifestyle.map((item, index) => (
              <li key={index} className="flex gap-2.5 items-start">
                <span className="flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-emerald-50 text-[10px] font-bold text-emerald-600 dark:bg-emerald-900/20 dark:text-emerald-400">
                  {index + 1}
                </span>
                <span className="text-[hsl(var(--foreground))]">{item}</span>
              </li>
            ))}
          </ul>
        </div>

        {/* ASHA Coordinator visits */}
        <div className="rounded-3xl border border-[hsl(var(--border))] bg-[hsl(var(--card))] p-6 card-hover">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-purple-50 text-purple-600 dark:bg-purple-900/20 dark:text-purple-400 mb-4">
            <UserCheck className="h-5 w-5" />
          </div>
          <h3 className="text-base font-semibold mb-1.5">ASHA Support</h3>
          <p className="text-xs text-[hsl(var(--muted-foreground))] mb-4">Tasks coordinated with your community ASHA health worker</p>
          <ul className="space-y-3 text-sm">
            {reminders.ashaTasks.map((item, index) => (
              <li key={index} className="flex gap-2.5 items-start">
                <span className="flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-purple-50 text-[10px] font-bold text-purple-600 dark:bg-purple-900/20 dark:text-purple-400">
                  {index + 1}
                </span>
                <span className="text-[hsl(var(--foreground))]">{item}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
}
