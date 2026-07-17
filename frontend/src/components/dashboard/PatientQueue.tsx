import { Link } from "react-router-dom";
import { cn, getTriageColor, getTriageDotColor } from "../../lib/utils";
import { ArrowUpRight, Clock, Users } from "lucide-react";


interface QueuePatient {
  id: string;
  name: string;
  age: number;
  complaint: string;
  priority: string;
  time: string;
}

interface PatientQueueProps {
  patients: QueuePatient[];
  className?: string;
}

export default function PatientQueue({ patients, className }: PatientQueueProps) {
  return (
    <div className={cn("rounded-2xl border border-[hsl(var(--border))] bg-[hsl(var(--card))] shadow-sm", className)}>
      <div className="flex items-center justify-between border-b border-[hsl(var(--border))] p-5">
        <div className="flex items-center gap-2">
          <Clock className="h-5 w-5 text-[hsl(var(--primary))]" />
          <h3 className="text-base font-semibold tracking-tight">ASHA Priority Queue</h3>
        </div>
        <span className="text-xs font-semibold text-[hsl(var(--muted-foreground))] px-2 py-0.5 rounded-full bg-[hsl(var(--muted))]">
          {patients.length} waiting
        </span>
      </div>

      {patients.length === 0 ? (
        <div className="flex flex-col items-center justify-center p-8 text-center text-[hsl(var(--muted-foreground))]">
          <Users className="h-8 w-8 opacity-40 mb-2" />
          <p className="text-xs">No patients currently in the queue</p>
        </div>
      ) : (
        <div className="divide-y divide-[hsl(var(--border))]">
          {patients.map((patient) => (
            <Link
              key={patient.id}
              to={`/patient/${patient.id}`}
              className="flex items-center justify-between p-4 hover:bg-[hsl(var(--accent))] transition-colors group"
            >
              <div className="flex items-center gap-3 min-w-0">
                <div className={cn("h-2.5 w-2.5 rounded-full shrink-0", getTriageDotColor(patient.priority))} />
                <div className="min-w-0">
                  <p className="text-sm font-semibold truncate group-hover:text-[hsl(var(--primary))] transition-colors">
                    {patient.name}
                  </p>
                  <p className="text-xs text-[hsl(var(--muted-foreground))] mt-0.5 truncate max-w-[200px]">
                    {patient.complaint}
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-3 shrink-0 ml-3">
                <span className={cn("rounded-full px-2.5 py-0.5 text-[10px] font-bold uppercase tracking-wider", getTriageColor(patient.priority))}>
                  {patient.priority}
                </span>
                <span className="text-xs text-[hsl(var(--muted-foreground))]">{patient.time}</span>
                <ArrowUpRight className="h-4 w-4 text-[hsl(var(--muted-foreground))] group-hover:text-[hsl(var(--foreground))] transition-colors" />
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
