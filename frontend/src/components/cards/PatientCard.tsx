import { Link } from "react-router-dom";
import { cn, getInitials } from "../../lib/utils";
import { MapPin, Phone, ArrowRight } from "lucide-react";
import type { Patient } from "../../types";

interface PatientCardProps {
  patient: Patient;
  className?: string;
}

export default function PatientCard({ patient, className }: PatientCardProps) {
  return (
    <div
      className={cn(
        "rounded-2xl border border-[hsl(var(--border))] bg-[hsl(var(--card))] p-5 shadow-sm transition-all hover:shadow-md flex flex-col justify-between",
        className
      )}
    >
      <div className="flex items-start gap-3">
        <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-gradient-primary text-xs font-bold text-white shadow-sm">
          {getInitials(patient.name)}
        </div>
        <div className="min-w-0">
          <h4 className="font-semibold text-sm truncate">{patient.name}</h4>
          <p className="text-xs text-[hsl(var(--muted-foreground))] mt-0.5">
            {patient.age} yrs • {patient.gender}
          </p>
        </div>
      </div>

      <div className="mt-4 space-y-2 border-t border-[hsl(var(--border))] pt-3 text-xs text-[hsl(var(--muted-foreground))]">
        {patient.phone && (
          <div className="flex items-center gap-1.5">
            <Phone className="h-3.5 w-3.5" />
            <span>{patient.phone}</span>
          </div>
        )}
        {patient.village_name && (
          <div className="flex items-center gap-1.5">
            <MapPin className="h-3.5 w-3.5" />
            <span className="truncate">{patient.village_name}</span>
          </div>
        )}
      </div>

      <Link
        to={`/patient/${patient.id}`}
        className="mt-4 flex items-center justify-center gap-1 rounded-xl bg-[hsl(var(--muted))] py-2 text-xs font-medium text-[hsl(var(--foreground))] hover:bg-[hsl(var(--primary))]/10 hover:text-[hsl(var(--primary))] transition-all"
      >
        View Profile
        <ArrowRight className="h-3.5 w-3.5" />
      </Link>
    </div>
  );
}
