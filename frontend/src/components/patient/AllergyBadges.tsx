import { AlertTriangle } from "lucide-react";
import { cn } from "../../lib/utils";
import type { Allergy } from "../../types";

interface AllergyBadgesProps {
  allergies: Allergy[];
  className?: string;
}

export default function AllergyBadges({ allergies, className }: AllergyBadgesProps) {
  return (
    <div className={cn("rounded-2xl border border-[hsl(var(--border))] bg-[hsl(var(--card))] p-5 shadow-sm", className)}>
      <div className="flex items-center gap-2 mb-4">
        <AlertTriangle className="h-5 w-5 text-rose-500" />
        <h3 className="text-base font-semibold tracking-tight">Drug & Food Allergies</h3>
      </div>

      {allergies.length === 0 ? (
        <div className="text-center p-6 text-xs text-[hsl(var(--muted-foreground))]">
          No known allergies reported.
        </div>
      ) : (
        <div className="flex flex-wrap gap-2">
          {allergies.map((allergy) => {
            const isSevere = allergy.severity === "severe";
            const isModerate = allergy.severity === "moderate";

            return (
              <span
                key={allergy.id}
                className={cn(
                  "inline-flex items-center gap-1.5 rounded-xl border px-3 py-1.5 text-xs font-semibold shadow-sm transition-all",
                  isSevere
                    ? "border-rose-200 bg-rose-50 text-rose-700 dark:border-rose-950/20 dark:bg-rose-950/10 dark:text-rose-400"
                    : isModerate
                    ? "border-amber-200 bg-amber-50 text-amber-700 dark:border-amber-950/20 dark:bg-amber-950/10 dark:text-amber-400"
                    : "border-slate-200 bg-slate-50 text-slate-700 dark:border-slate-800 dark:bg-slate-900/30 dark:text-slate-400"
                )}
                title={allergy.reaction ? `Reaction: ${allergy.reaction}` : undefined}
              >
                <div
                  className={cn(
                    "h-2 w-2 rounded-full",
                    isSevere ? "bg-rose-500 animate-pulse" : isModerate ? "bg-amber-500" : "bg-slate-400"
                  )}
                />
                <span>{allergy.allergen}</span>
                {allergy.reaction && (
                  <span className="text-[10px] opacity-75 font-normal">({allergy.reaction})</span>
                )}
              </span>
            );
          })}
        </div>
      )}
    </div>
  );
}
