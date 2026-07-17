import { cn } from "../../lib/utils";

interface TimelineProps {
  children: React.ReactNode;
  className?: string;
}

export default function Timeline({ children, className }: TimelineProps) {
  return (
    <div className={cn("relative border-l border-[hsl(var(--border))] ml-3 space-y-6", className)}>
      {children}
    </div>
  );
}
