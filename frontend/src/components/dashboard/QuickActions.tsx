import { Link } from "react-router-dom";
import { cn } from "../../lib/utils";
import { Plus, Users, ShieldAlert, Map } from "lucide-react";


interface ActionItem {
  label: string;
  description: string;
  icon: any;
  path: string;
  color: string;
  bg: string;
}

const actions: ActionItem[] = [
  {
    label: "Start Intake",
    description: "Launch new AI agent consultation session",
    icon: Plus,
    path: "/consultation",
    color: "text-blue-600 dark:text-blue-400",
    bg: "bg-blue-50 dark:bg-blue-900/20",
  },
  {
    label: "Register Patient",
    description: "Create a new demographic file card",
    icon: Users,
    path: "/patients",
    color: "text-emerald-600 dark:text-emerald-400",
    bg: "bg-emerald-50 dark:bg-emerald-900/20",
  },
  {
    label: "Triage Alert Room",
    description: "Track active warning logs",
    icon: ShieldAlert,
    path: "/dashboard",
    color: "text-rose-600 dark:text-rose-400",
    bg: "bg-rose-50 dark:bg-rose-900/20",
  },
  {
    label: "Referrals Mapping",
    description: "Lookup nearby clinics/hospitals",
    icon: Map,
    path: "/analytics",
    color: "text-violet-600 dark:text-violet-400",
    bg: "bg-violet-50 dark:bg-violet-900/20",
  },
];

interface QuickActionsProps {
  className?: string;
}

export default function QuickActions({ className }: QuickActionsProps) {
  return (
    <div className={cn("grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4", className)}>
      {actions.map((act) => (
        <Link
          key={act.label}
          to={act.path}
          className="flex items-start gap-4 rounded-2xl border border-[hsl(var(--border))] bg-[hsl(var(--card))] p-5 shadow-sm hover:shadow-md hover:-translate-y-0.5 transition-all card-hover"
        >
          <div className={cn("rounded-xl p-2.5 shrink-0", act.bg)}>
            <act.icon className={cn("h-5 w-5", act.color)} />
          </div>
          <div className="min-w-0">
            <h4 className="font-semibold text-sm">{act.label}</h4>
            <p className="text-xs text-[hsl(var(--muted-foreground))] mt-1 leading-normal">
              {act.description}
            </p>
          </div>
        </Link>
      ))}
    </div>
  );
}
