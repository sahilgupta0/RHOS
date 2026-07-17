import { CheckCircle2, Circle, Loader2 } from "lucide-react";
import { cn } from "../../lib/utils";

interface Agent {
  name: string;
  status: "idle" | "running" | "completed" | "failed" | "optional";
  description?: string;
}

interface AgentProgressProps {
  agents: Agent[];
  className?: string;
}

export default function AgentProgress({ agents, className }: AgentProgressProps) {
  return (
    <div className={cn("rounded-2xl border border-[hsl(var(--border))] bg-[hsl(var(--card))] p-5 shadow-sm", className)}>
      <h3 className="text-sm font-semibold mb-4 tracking-tight">AI Orchestration Pipeline</h3>
      <div className="space-y-4">
        {agents.map((agent) => {
          const isRunning = agent.status === "running";
          const isCompleted = agent.status === "completed";
          const isFailed = agent.status === "failed";
          const isOptional = agent.status === "optional";

          return (
            <div key={agent.name} className="flex items-start gap-3">
              <div className="mt-0.5 shrink-0">
                {isRunning ? (
                  <Loader2 className="h-4 w-4 animate-spin text-[hsl(var(--primary))]" />
                ) : isCompleted ? (
                  <CheckCircle2 className="h-4 w-4 text-emerald-500" />
                ) : isFailed ? (
                  <div className="h-4 w-4 rounded-full bg-rose-500/10 flex items-center justify-center text-rose-500 font-bold text-[10px]">!</div>
                ) : isOptional ? (
                  <Circle className="h-4 w-4 text-slate-300 dark:text-slate-700 stroke-dashed" />
                ) : (
                  <Circle className="h-4 w-4 text-slate-300 dark:text-slate-700" />
                )}
              </div>
              <div className="min-w-0">
                <p
                  className={cn(
                    "text-xs font-medium",
                    isRunning && "text-[hsl(var(--primary))]",
                    isCompleted && "text-emerald-700 dark:text-emerald-400"
                  )}
                >
                  {agent.name}
                </p>
                {agent.description && (
                  <p className="text-[10px] text-[hsl(var(--muted-foreground))] mt-0.5 truncate">
                    {agent.description}
                  </p>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
