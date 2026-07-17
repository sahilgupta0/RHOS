import { cn, getTriageColor } from "../../lib/utils";
import type { TriagePriority } from "../../types";

interface PriorityBadgeProps {
  priority?: TriagePriority | string | null;
  className?: string;
}

export default function PriorityBadge({ priority, className }: PriorityBadgeProps) {
  if (!priority) return null;

  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 rounded-full px-2.5 py-0.5 text-xs font-semibold uppercase tracking-wider",
        getTriageColor(priority),
        className
      )}
    >
      {priority}
    </span>
  );
}
