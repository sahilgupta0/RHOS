import { useAuth } from "../../context/AuthContext";
import { useTheme } from "../../context/ThemeContext";
import { cn, getInitials } from "../../lib/utils";
import { Moon, Sun, Monitor, Bell, Shield, User, Palette } from "lucide-react";

export default function Settings() {
  const { user } = useAuth();
  const { theme, setTheme } = useTheme();

  const themeOptions = [
    { value: "light" as const, label: "Light", icon: Sun },
    { value: "dark" as const, label: "Dark", icon: Moon },
    { value: "system" as const, label: "System", icon: Monitor },
  ];

  return (
    <div className="space-y-6 max-w-3xl">
      <div>
        <h1 className="text-2xl font-bold">Settings</h1>
        <p className="text-sm text-[hsl(var(--muted-foreground))]">Manage your profile and preferences</p>
      </div>

      {/* Profile */}
      <div className="rounded-2xl border border-[hsl(var(--border))] bg-[hsl(var(--card))] p-6">
        <div className="flex items-center gap-2 mb-4">
          <User className="h-5 w-5 text-blue-500" />
          <h3 className="text-lg font-semibold">Profile</h3>
        </div>
        <div className="flex items-center gap-4">
          <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-gradient-primary text-xl font-bold text-white">
            {user ? getInitials(user.name) : "U"}
          </div>
          <div>
            <p className="text-lg font-semibold">{user?.name || "User"}</p>
            <p className="text-sm text-[hsl(var(--muted-foreground))]">{user?.email}</p>
            <p className="text-xs text-[hsl(var(--muted-foreground))] capitalize mt-0.5">{user?.role} • {user?.hospital_name || "PHC Khandela"}</p>
          </div>
        </div>
      </div>

      {/* Theme */}
      <div className="rounded-2xl border border-[hsl(var(--border))] bg-[hsl(var(--card))] p-6">
        <div className="flex items-center gap-2 mb-4">
          <Palette className="h-5 w-5 text-violet-500" />
          <h3 className="text-lg font-semibold">Appearance</h3>
        </div>
        <div className="grid grid-cols-3 gap-3">
          {themeOptions.map((opt) => (
            <button
              key={opt.value}
              onClick={() => setTheme(opt.value)}
              className={cn(
                "flex flex-col items-center gap-2 rounded-xl border-2 p-4 transition-all",
                theme === opt.value
                  ? "border-[hsl(var(--primary))] bg-[hsl(var(--primary))]/5"
                  : "border-[hsl(var(--border))] hover:border-[hsl(var(--primary))]/50"
              )}
            >
              <opt.icon className={cn("h-6 w-6", theme === opt.value ? "text-[hsl(var(--primary))]" : "text-[hsl(var(--muted-foreground))]")} />
              <span className="text-sm font-medium">{opt.label}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Notifications */}
      <div className="rounded-2xl border border-[hsl(var(--border))] bg-[hsl(var(--card))] p-6">
        <div className="flex items-center gap-2 mb-4">
          <Bell className="h-5 w-5 text-amber-500" />
          <h3 className="text-lg font-semibold">Notifications</h3>
        </div>
        <div className="space-y-3">
          {[
            { label: "High priority alerts", description: "Get notified for HIGH priority triage cases", defaultOn: true },
            { label: "Follow-up reminders", description: "Reminders for patient follow-ups", defaultOn: true },
            { label: "System updates", description: "News about RHOS features and updates", defaultOn: false },
          ].map((item) => (
            <div key={item.label} className="flex items-center justify-between rounded-xl border border-[hsl(var(--border))] p-3">
              <div>
                <p className="text-sm font-medium">{item.label}</p>
                <p className="text-xs text-[hsl(var(--muted-foreground))]">{item.description}</p>
              </div>
              <button className={cn(
                "relative h-6 w-11 rounded-full transition-colors",
                item.defaultOn ? "bg-[hsl(var(--primary))]" : "bg-[hsl(var(--muted))]"
              )}>
                <span className={cn(
                  "absolute top-0.5 h-5 w-5 rounded-full bg-white shadow transition-transform",
                  item.defaultOn ? "left-5.5 translate-x-0" : "left-0.5"
                )} />
              </button>
            </div>
          ))}
        </div>
      </div>

      {/* Safety */}
      <div className="rounded-2xl border border-amber-200 dark:border-amber-800 bg-amber-50 dark:bg-amber-900/10 p-6">
        <div className="flex items-center gap-2 mb-2">
          <Shield className="h-5 w-5 text-amber-600 dark:text-amber-400" />
          <h3 className="text-lg font-semibold text-amber-700 dark:text-amber-400">Safety & Compliance</h3>
        </div>
        <p className="text-sm text-amber-600 dark:text-amber-400/80 leading-relaxed">
          RHOS is a Clinical Decision Support System (CDSS). All AI-generated outputs — including
          triage classifications, medication checks, clinical summaries, and follow-up plans —
          are advisory only and require review and approval by a qualified healthcare professional
          before any clinical action is taken.
        </p>
      </div>
    </div>
  );
}
