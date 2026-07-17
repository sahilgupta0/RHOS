import { cn } from "../../lib/utils";

interface TimelineItemProps {
  title: string;
  description: React.ReactNode | string;
  date: string;
  dotColor?: string;
  badge?: React.ReactNode;
  className?: string;
}

export default function TimelineItem({
  title,
  description,
  date,
  dotColor = "bg-[hsl(var(--primary))]",
  badge,
  className,
}: TimelineItemProps) {
  return (
    <div className={cn("relative pl-6 group", className)}>
      {/* Circle dot */}
      <div
        className={cn(
          "absolute -left-[6.5px] top-1.5 h-3.5 w-3.5 rounded-full border-4 border-[hsl(var(--background))] transition-transform group-hover:scale-110 shadow-sm",
          dotColor
        )}
      />

      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-1">
        <h4 className="font-semibold text-sm text-[hsl(var(--foreground))]">{title}</h4>
        <span className="text-[10px] font-semibold text-[hsl(var(--muted-foreground))]">{date}</span>
      </div>

      <div className="text-xs text-[hsl(var(--muted-foreground))] mt-1 leading-relaxed">
        {description}
      </div>

      {badge && <div className="mt-2">{badge}</div>}
    </div>
  );
}
