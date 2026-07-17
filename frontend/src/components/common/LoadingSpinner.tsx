import { Loader2 } from "lucide-react";
import { cn } from "../../lib/utils";

interface LoadingSpinnerProps {
  className?: string;
  size?: number;
}

export default function LoadingSpinner({ className, size = 32 }: LoadingSpinnerProps) {
  return (
    <div className={cn("flex items-center justify-center p-4", className)}>
      <Loader2
        className="animate-spin text-[hsl(var(--primary))]"
        size={size}
      />
    </div>
  );
}
