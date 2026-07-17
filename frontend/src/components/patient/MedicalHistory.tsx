import { cn, formatDate } from "../../lib/utils";
import { FileText, Calendar } from "lucide-react";

import type { MedicalHistory as HistoryItem } from "../../types";

interface MedicalHistoryProps {
  history: HistoryItem[];
  className?: string;
}

export default function MedicalHistory({ history, className }: MedicalHistoryProps) {
  return (
    <div className={cn("rounded-2xl border border-[hsl(var(--border))] bg-[hsl(var(--card))] p-5 shadow-sm", className)}>
      <div className="flex items-center gap-2 mb-4">
        <FileText className="h-5 w-5 text-blue-500" />
        <h3 className="text-base font-semibold tracking-tight">Chronic & Medical Conditions</h3>
      </div>

      {history.length === 0 ? (
        <div className="text-center p-6 text-xs text-[hsl(var(--muted-foreground))]">
          No medical history records found.
        </div>
      ) : (
        <div className="space-y-3">
          {history.map((item) => (
            <div key={item.id} className="rounded-xl border border-[hsl(var(--border))] p-3.5 hover:bg-[hsl(var(--muted))]/30 transition-colors">
              <div className="flex items-center justify-between">
                <p className="font-semibold text-sm">{item.condition}</p>
                <span
                  className={cn(
                    "rounded-full px-2.5 py-0.5 text-[10px] font-bold uppercase tracking-wider",
                    item.status === "chronic"
                      ? "bg-amber-100 text-amber-700 dark:bg-amber-950/20 dark:text-amber-400"
                      : item.status === "resolved"
                      ? "bg-emerald-100 text-emerald-700 dark:bg-emerald-950/20 dark:text-emerald-400"
                      : "bg-blue-100 text-blue-700 dark:bg-blue-950/20 dark:text-blue-400"
                  )}
                >
                  {item.status}
                </span>
              </div>
              {item.notes && (
                <p className="text-xs text-[hsl(var(--muted-foreground))] mt-2 leading-relaxed">
                  {item.notes}
                </p>
              )}
              {item.diagnosed_date && (
                <div className="flex items-center gap-1 mt-2 text-[10px] text-[hsl(var(--muted-foreground))] font-medium">
                  <Calendar className="h-3 w-3" />
                  <span>Diagnosed: {formatDate(item.diagnosed_date)}</span>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
