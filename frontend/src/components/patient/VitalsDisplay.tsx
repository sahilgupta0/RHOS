import { Heart, Activity, Wind, Thermometer } from "lucide-react";

import { cn } from "../../lib/utils";
import type { Vital } from "../../types";

interface VitalsDisplayProps {
  vitals?: Vital | null;
  className?: string;
}

export default function VitalsDisplay({ vitals, className }: VitalsDisplayProps) {
  if (!vitals) {
    return (
      <div className={cn("rounded-2xl border border-dashed border-[hsl(var(--border))] bg-[hsl(var(--card))] p-6 text-center text-xs text-[hsl(var(--muted-foreground))]", className)}>
        No vital measurements recorded.
      </div>
    );
  }

  const cards = [
    {
      label: "Blood Pressure",
      value: vitals.bp_systolic && vitals.bp_diastolic ? `${vitals.bp_systolic}/${vitals.bp_diastolic}` : "N/A",
      unit: "mmHg",
      icon: Heart,
      color: "text-rose-500",
      bg: "bg-rose-50 dark:bg-rose-950/20",
    },
    {
      label: "Heart Rate",
      value: vitals.heart_rate || "N/A",
      unit: "bpm",
      icon: Activity,
      color: "text-blue-500",
      bg: "bg-blue-50 dark:bg-blue-950/20",
    },
    {
      label: "Oxygen (SpO₂)",
      value: vitals.spo2 ? `${vitals.spo2}%` : "N/A",
      unit: "",
      icon: Wind,
      color: "text-emerald-500",
      bg: "bg-emerald-50 dark:bg-emerald-950/20",
    },
    {
      label: "Temperature",
      value: vitals.temperature || "N/A",
      unit: "°C",
      icon: Thermometer,
      color: "text-amber-500",
      bg: "bg-amber-50 dark:bg-amber-950/20",
    },
  ];

  return (
    <div className={cn("grid grid-cols-2 md:grid-cols-4 gap-4", className)}>
      {cards.map((c) => (
        <div key={c.label} className="rounded-2xl border border-[hsl(var(--border))] bg-[hsl(var(--card))] p-4 shadow-sm">
          <div className="flex items-center justify-between mb-3">
            <span className="text-[10px] font-bold text-[hsl(var(--muted-foreground))] uppercase tracking-wider">{c.label}</span>
            <div className={cn("rounded-lg p-1.5", c.bg)}>
              <c.icon className={cn("h-4 w-4", c.color)} />
            </div>
          </div>
          <p className="text-xl font-bold tracking-tight">
            {c.value}
            {c.value !== "N/A" && c.unit && (
              <span className="text-xs font-normal text-[hsl(var(--muted-foreground))] ml-1">{c.unit}</span>
            )}
          </p>
        </div>
      ))}
    </div>
  );
}
