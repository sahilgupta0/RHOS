import { AlertTriangle, Shield } from "lucide-react";
import { cn } from "../../lib/utils";

interface SafetyDisclaimerProps {
  className?: string;
  variant?: "warning" | "info";
}

export default function SafetyDisclaimer({ className, variant = "info" }: SafetyDisclaimerProps) {
  if (variant === "warning") {
    return (
      <div
        className={cn(
          "flex items-start gap-2.5 rounded-xl border border-amber-200 bg-amber-50 p-4 text-amber-800 dark:border-amber-900/30 dark:bg-amber-950/10 dark:text-amber-400",
          className
        )}
      >
        <AlertTriangle className="h-5 w-5 shrink-0 text-amber-500" />
        <div className="text-xs leading-relaxed">
          <p className="font-semibold">Clinical Decision Support Notice</p>
          <p className="mt-1 opacity-90">
            RHOS is a decision support tool — NOT an AI doctor. All generated medical plans, triages, and
            medication reviews are advisory. Final clinical decisions and prescriptions must be confirmed by
            qualified medical professionals.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div
      className={cn(
        "flex items-center gap-1.5 text-[10px] text-[hsl(var(--muted-foreground))] opacity-80",
        className
      )}
    >
      <Shield className="h-3 w-3 shrink-0 text-[hsl(var(--primary))]" />
      <span>AI-assisted decision support. Doctor review required.</span>
    </div>
  );
}
