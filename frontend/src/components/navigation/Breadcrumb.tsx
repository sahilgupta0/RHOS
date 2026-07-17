import { Link } from "react-router-dom";
import { ChevronRight, Home } from "lucide-react";
import { cn } from "../../lib/utils";

interface BreadcrumbItem {
  label: string;
  path?: string;
}

interface BreadcrumbProps {
  items: BreadcrumbItem[];
  className?: string;
}

export default function Breadcrumb({ items, className }: BreadcrumbProps) {
  return (
    <nav className={cn("flex items-center gap-1.5 text-xs text-[hsl(var(--muted-foreground))]", className)}>
      <Link
        to="/dashboard"
        className="flex items-center gap-1 hover:text-[hsl(var(--foreground))] transition-colors"
      >
        <Home className="h-3.5 w-3.5" />
      </Link>

      {items.map((item, index) => {
        const isLast = index === items.length - 1;

        return (
          <div key={index} className="flex items-center gap-1.5">
            <ChevronRight className="h-3.5 w-3.5 shrink-0" />
            {item.path && !isLast ? (
              <Link
                to={item.path}
                className="hover:text-[hsl(var(--foreground))] transition-colors"
              >
                {item.label}
              </Link>
            ) : (
              <span className="font-medium text-[hsl(var(--foreground))] truncate max-w-[160px]">
                {item.label}
              </span>
            )}
          </div>
        );
      })}
    </nav>
  );
}
