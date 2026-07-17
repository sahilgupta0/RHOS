import { Link } from "react-router-dom";
import { cn, formatDate, getTriageColor } from "../../lib/utils";
import { MessageSquare, Calendar, ChevronRight } from "lucide-react";
import type { Consultation } from "../../types";

interface RecentConsultationsProps {
  consultations: Consultation[];
  className?: string;
}

export default function RecentConsultations({ consultations, className }: RecentConsultationsProps) {
  return (
    <div className={cn("rounded-2xl border border-[hsl(var(--border))] bg-[hsl(var(--card))] shadow-sm", className)}>
      <div className="flex items-center justify-between border-b border-[hsl(var(--border))] p-5">
        <h3 className="text-base font-semibold tracking-tight">Recent Sessions</h3>
        <Link
          to="/consultation"
          className="text-xs font-semibold text-[hsl(var(--primary))] hover:underline"
        >
          View all
        </Link>
      </div>

      {consultations.length === 0 ? (
        <div className="flex flex-col items-center justify-center p-8 text-center text-[hsl(var(--muted-foreground))]">
          <MessageSquare className="h-8 w-8 opacity-40 mb-2" />
          <p className="text-xs">No recent sessions found</p>
        </div>
      ) : (
        <div className="divide-y divide-[hsl(var(--border))]">
          {consultations.slice(0, 5).map((session) => (
            <div
              key={session.id}
              className="flex items-center justify-between p-4 hover:bg-[hsl(var(--accent))] transition-all group"
            >
              <div className="min-w-0 flex-1">
                <div className="flex items-center gap-2">
                  <p className="text-sm font-semibold truncate text-[hsl(var(--foreground))]">
                    {session.patient_name || "Unknown Patient"}
                  </p>
                  {session.triage_priority && (
                    <span className={cn("rounded-full px-2 py-0.5 text-[9px] font-bold uppercase tracking-wider", getTriageColor(session.triage_priority))}>
                      {session.triage_priority}
                    </span>
                  )}
                </div>
                <p className="text-xs text-[hsl(var(--muted-foreground))] mt-0.5 truncate max-w-[280px]">
                  {session.chief_complaint || "General checkup"}
                </p>
              </div>

              <div className="flex items-center gap-3 shrink-0 ml-4">
                {session.created_at && (
                  <span className="text-xs text-[hsl(var(--muted-foreground))] flex items-center gap-1">
                    <Calendar className="h-3.5 w-3.5" />
                    {formatDate(session.created_at)}
                  </span>
                )}
                <Link
                  to={`/consultation/${session.id}`}
                  className="rounded-lg p-1.5 hover:bg-[hsl(var(--border))] text-[hsl(var(--muted-foreground))] hover:text-[hsl(var(--foreground))] transition-all"
                >
                  <ChevronRight className="h-4 w-4" />
                </Link>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
