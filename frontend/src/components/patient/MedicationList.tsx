import { Pill } from "lucide-react";

import { cn } from "../../lib/utils";

interface Medication {
  name: string;
  dosage: string;
  frequency: string;
  status: "active" | "discontinued" | "completed";
}

interface MedicationListProps {
  medications: Medication[];
  className?: string;
}

export default function MedicationList({ medications, className }: MedicationListProps) {
  return (
    <div className={cn("rounded-2xl border border-[hsl(var(--border))] bg-[hsl(var(--card))] p-5 shadow-sm", className)}>
      <div className="flex items-center gap-2 mb-4">
        <Pill className="h-5 w-5 text-emerald-500" />
        <h3 className="text-base font-semibold tracking-tight">Active Medications</h3>
      </div>

      {medications.length === 0 ? (
        <div className="text-center p-6 text-xs text-[hsl(var(--muted-foreground))]">
          No current medications prescribed.
        </div>
      ) : (
        <div className="space-y-2.5">
          {medications.map((med, i) => (
            <div key={i} className="flex items-center justify-between border border-[hsl(var(--border))] rounded-xl p-3">
              <div className="flex items-start gap-3">
                <div className="rounded-lg bg-emerald-50 dark:bg-emerald-950/20 p-2 text-emerald-600 dark:text-emerald-400 shrink-0">
                  <Pill className="h-4 w-4" />
                </div>
                <div>
                  <p className="text-sm font-semibold">{med.name}</p>
                  <p className="text-xs text-[hsl(var(--muted-foreground))] mt-0.5">
                    {med.dosage} • {med.frequency}
                  </p>
                </div>
              </div>
              <span className={cn(
                "rounded-full px-2 py-0.5 text-[9px] font-bold uppercase tracking-wider",
                med.status === "active"
                  ? "bg-emerald-50 text-emerald-700 dark:bg-emerald-950/20 dark:text-emerald-400"
                  : "bg-slate-100 text-slate-700 dark:bg-slate-900/20 dark:text-slate-400"
              )}>
                {med.status}
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
