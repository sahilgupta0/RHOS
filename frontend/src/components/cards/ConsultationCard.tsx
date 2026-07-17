import { Link } from "react-router-dom";
import { cn, formatDate } from "../../lib/utils";
import { MessageSquare, Calendar, User, ArrowUpRight } from "lucide-react";
import PriorityBadge from "../common/PriorityBadge";
import type { Consultation } from "../../types";

interface ConsultationCardProps {
  consultation: Consultation;
  className?: string;
}

export default function ConsultationCard({ consultation, className }: ConsultationCardProps) {
  return (
    <div
      className={cn(
        "rounded-2xl border border-[hsl(var(--border))] bg-[hsl(var(--card))] p-5 shadow-sm transition-all hover:shadow-md",
        className
      )}
    >
      <div className="flex items-start justify-between gap-2">
        <div className="flex items-center gap-2">
          <MessageSquare className="h-4 w-4 text-[hsl(var(--primary))]" />
          <span className="text-xs font-semibold text-[hsl(var(--muted-foreground))]">Consultation</span>
        </div>
        <PriorityBadge priority={consultation.triage_priority} />
      </div>

      <h4 className="mt-3 font-semibold text-sm truncate">
        {consultation.chief_complaint || "Routine Checkup"}
      </h4>

      <div className="mt-4 flex items-center justify-between border-t border-[hsl(var(--border))] pt-3 text-xs text-[hsl(var(--muted-foreground))]">
        <div className="flex items-center gap-1.5 min-w-0">
          <User className="h-3.5 w-3.5 shrink-0" />
          <span className="truncate">{consultation.patient_name || "Unknown Patient"}</span>
        </div>
        {consultation.created_at && (
          <div className="flex items-center gap-1 shrink-0">
            <Calendar className="h-3.5 w-3.5" />
            <span>{formatDate(consultation.created_at)}</span>
          </div>
        )}
      </div>

      <Link
        to={`/consultation/${consultation.id}`}
        className="mt-4 flex items-center justify-center gap-1.5 rounded-xl bg-[hsl(var(--primary))] py-2 text-xs font-medium text-white shadow-sm hover:shadow-md transition-all bg-gradient-primary"
      >
        Resume Session
        <ArrowUpRight className="h-3.5 w-3.5" />
      </Link>
    </div>
  );
}
