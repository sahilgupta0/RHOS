import { Stethoscope } from "lucide-react";
import { cn } from "../../lib/utils";

interface EmptyStateProps {
  title?: string;
  description?: string;
  icon?: any;
  className?: string;
}

export default function EmptyState({
  title = "No data available",
  description = "There are no records to display at this time.",
  icon: Icon = Stethoscope,
  className,
}: EmptyStateProps) {
  return (
    <div
      className={cn(
        "flex flex-col items-center justify-center rounded-2xl border border-dashed border-[hsl(var(--border))] p-8 text-center",
        className
      )}
    >
      <div className="flex h-12 w-12 items-center justify-center rounded-full bg-[hsl(var(--muted))] text-[hsl(var(--muted-foreground))]">
        <Icon className="h-6 w-6" />
      </div>
      <h3 className="mt-4 text-sm font-semibold">{title}</h3>
      <p className="mt-1 text-xs text-[hsl(var(--muted-foreground))] max-w-xs">{description}</p>
    </div>
  );
}
