import { NavLink } from "react-router-dom";
import { cn } from "../../lib/utils";

interface NavItemProps {
  label: string;
  path: string;
  icon: any;
  collapsed?: boolean;
  badge?: number;
}

export default function NavItem({
  label,
  path,
  icon: Icon,
  collapsed = false,
  badge,
}: NavItemProps) {
  return (
    <NavLink
      to={path}
      className={({ isActive }) =>
        cn(
          "flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition-all duration-200 relative group",
          isActive
            ? "bg-[hsl(var(--primary))]/10 text-[hsl(var(--primary))] shadow-sm font-semibold"
            : "text-[hsl(var(--muted-foreground))] hover:bg-[hsl(var(--accent))] hover:text-[hsl(var(--accent-foreground))]",
          collapsed && "justify-center px-2"
        )
      }
    >
      <Icon className="h-5 w-5 shrink-0" />

      {!collapsed && (
        <span className="truncate">{label}</span>
      )}

      {!collapsed && badge !== undefined && badge > 0 && (
        <span className="ml-auto flex h-5 w-5 items-center justify-center rounded-full bg-rose-500 text-[10px] font-bold text-white">
          {badge}
        </span>
      )}

      {collapsed && (
        <div className="absolute left-full ml-3 rounded-md bg-[hsl(var(--foreground))] text-[hsl(var(--background))] px-2 py-1 text-xs opacity-0 pointer-events-none group-hover:opacity-100 transition-opacity whitespace-nowrap z-50">
          {label}
        </div>
      )}
    </NavLink>
  );
}
