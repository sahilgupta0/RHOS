import { cn } from "../../lib/utils";

interface StatsCardProps {
  label: string;
  value: string | number;
  icon: any;
  trend?: string;
  trendType?: "up" | "down" | "neutral";
  color?: string;
  bg?: string;
  className?: string;
}

export default function StatsCard({
  label,
  value,
  icon: Icon,
  trend,
  trendType = "up",
  color = "text-[hsl(var(--primary))]",
  bg = "bg-[hsl(var(--primary))]/10",
  className,
}: StatsCardProps) {
  return (
    <div
      className={cn(
        "rounded-2xl border border-[hsl(var(--border))] bg-[hsl(var(--card))] p-5 shadow-sm transition-all card-hover",
        className
      )}
    >
      <div className="flex items-center justify-between">
        <div className={cn("rounded-xl p-2.5", bg)}>
          <Icon className={cn("h-5 w-5", color)} />
        </div>
        {trend && (
          <span
            className={cn(
              "text-xs font-semibold px-2 py-0.5 rounded-full",
              trendType === "up"
                ? "bg-emerald-50 text-emerald-700 dark:bg-emerald-950/20 dark:text-emerald-400"
                : trendType === "down"
                ? "bg-rose-50 text-rose-700 dark:bg-rose-950/20 dark:text-rose-400"
                : "bg-slate-50 text-slate-700 dark:bg-slate-900/20 dark:text-slate-400"
            )}
          >
            {trend}
          </span>
        )}
      </div>
      <p className="mt-4 text-2xl font-bold tracking-tight">{value}</p>
      <p className="text-xs text-[hsl(var(--muted-foreground))] mt-1">{label}</p>
    </div>
  );
}
