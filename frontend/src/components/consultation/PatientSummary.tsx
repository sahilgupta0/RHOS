import { cn } from "../../lib/utils";

import type { Patient } from "../../types";

interface PatientSummaryProps {
  patient?: Patient | null;
  chiefComplaint?: string;
  className?: string;
}

export default function PatientSummary({ patient, chiefComplaint, className }: PatientSummaryProps) {
  if (!patient) return null;

  return (
    <div className={cn("rounded-2xl border border-[hsl(var(--border))] bg-[hsl(var(--card))] p-5 shadow-sm space-y-4", className)}>
      <h3 className="text-sm font-semibold tracking-tight">Active Consultation</h3>

      {/* Demographics */}
      <div className="flex items-center gap-3">
        <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-primary text-xs font-bold text-white">
          {patient.name.split(" ").map(n => n[0]).join("")}
        </div>
        <div>
          <h4 className="text-xs font-bold">{patient.name}</h4>
          <p className="text-[10px] text-[hsl(var(--muted-foreground))]">
            {patient.age} yrs • {patient.gender} • Blood: {patient.blood_group || "N/A"}
          </p>
        </div>
      </div>

      {/* Vitals summary */}
      <div className="border-t border-[hsl(var(--border))] pt-3 space-y-2">
        <h4 className="text-[10px] font-bold uppercase tracking-wider text-[hsl(var(--muted-foreground))]">Current Session Vitals</h4>
        <div className="grid grid-cols-2 gap-2 text-xs">
          <div className="rounded-lg bg-[hsl(var(--muted))] p-2">
            <span className="text-[10px] text-[hsl(var(--muted-foreground))]">BP</span>
            <p className="font-semibold mt-0.5">120/80</p>
          </div>
          <div className="rounded-lg bg-[hsl(var(--muted))] p-2">
            <span className="text-[10px] text-[hsl(var(--muted-foreground))]">SpO₂</span>
            <p className="font-semibold mt-0.5 text-emerald-600 dark:text-emerald-400">98%</p>
          </div>
        </div>
      </div>

      {/* Chief complaint */}
      {chiefComplaint && (
        <div className="border-t border-[hsl(var(--border))] pt-3">
          <h4 className="text-[10px] font-bold uppercase tracking-wider text-[hsl(var(--muted-foreground))]">Chief Complaint</h4>
          <p className="text-xs mt-1 leading-relaxed italic">{chiefComplaint}</p>
        </div>
      )}
    </div>
  );
}
