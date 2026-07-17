import { NavLink } from "react-router-dom";
import { cn } from "../../lib/utils";
import { useAuth } from "../../context/AuthContext";
import {
  LayoutDashboard,
  MessageSquare,
  BarChart3,
  Settings,
  ChevronLeft,
  Activity,
  Stethoscope,
  Clock,
  FileText,
} from "lucide-react";

interface SidebarProps {
  collapsed: boolean;
  onToggle: () => void;
}

export default function Sidebar({ collapsed, onToggle }: SidebarProps) {
  const { user } = useAuth();

  const navItems = user?.role === "patient" ? [
    { label: "Diagnosis", path: "/consultation", icon: MessageSquare },
    { label: "Report", path: `/patient/${user.patient_id || "P001"}`, icon: FileText },
    { label: "Reminder", path: "/reminders", icon: Clock },
    { label: "Profile", path: "/settings", icon: Settings },
  ] : [
    { label: "Dashboard", path: "/dashboard", icon: LayoutDashboard },
    { label: "Consultation", path: "/consultation", icon: MessageSquare },
    { label: "Analytics", path: "/analytics", icon: BarChart3 },
    { label: "Settings", path: "/settings", icon: Settings },
  ];

  return (
    <aside
      className={cn(
        "flex flex-col border-r border-[hsl(var(--sidebar-border))] bg-[hsl(var(--sidebar-bg))] transition-all duration-300",
        collapsed ? "w-[72px]" : "w-[260px]"
      )}
    >
      {/* Logo */}
      <div className="flex h-16 items-center gap-3 border-b border-[hsl(var(--sidebar-border))] px-4">
        <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-gradient-primary text-white shadow-md">
          <Stethoscope className="h-5 w-5" />
        </div>
        {!collapsed && (
          <div className="overflow-hidden">
            <h1 className="text-lg font-bold text-gradient">RHOS</h1>
            <p className="text-[10px] text-[hsl(var(--muted-foreground))] truncate">Rural Health OS</p>
          </div>
        )}
      </div>

      {/* Navigation */}
      <nav className="flex-1 space-y-1 p-3">
        {navItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) =>
              cn(
                "flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition-all duration-200",
                isActive
                  ? "bg-[hsl(var(--sidebar-active))/0.1] text-[hsl(var(--sidebar-active))] shadow-sm"
                  : "text-[hsl(var(--muted-foreground))] hover:bg-[hsl(var(--accent))] hover:text-[hsl(var(--accent-foreground))]",
                collapsed && "justify-center px-2"
              )
            }
          >
            <item.icon className="h-5 w-5 shrink-0" />
            {!collapsed && <span>{item.label}</span>}
          </NavLink>
        ))}
      </nav>

      {/* Health indicator */}
      <div className="border-t border-[hsl(var(--sidebar-border))] p-3">
        <div
          className={cn(
            "flex items-center gap-2 rounded-xl bg-emerald-50 px-3 py-2 dark:bg-emerald-900/20",
            collapsed && "justify-center px-2"
          )}
        >
          <Activity className="h-4 w-4 text-emerald-600 dark:text-emerald-400 animate-pulse-soft" />
          {!collapsed && (
            <span className="text-xs font-medium text-emerald-700 dark:text-emerald-400">
              System Active
            </span>
          )}
        </div>
      </div>

      {/* Collapse button */}
      <button
        onClick={onToggle}
        className="flex h-10 items-center justify-center border-t border-[hsl(var(--sidebar-border))] text-[hsl(var(--muted-foreground))] hover:bg-[hsl(var(--accent))] transition-colors"
      >
        <ChevronLeft className={cn("h-4 w-4 transition-transform", collapsed && "rotate-180")} />
      </button>
    </aside>
  );
}
