import { Phone, MapPin, Droplets } from "lucide-react";

import { getInitials } from "../../lib/utils";
import type { Patient } from "../../types";

interface PatientHeaderProps {
  patient: Patient;
}

export default function PatientHeader({ patient }: PatientHeaderProps) {
  return (
    <div className="flex flex-col md:flex-row gap-4 items-start md:items-center justify-between rounded-2xl bg-gradient-primary p-6 text-white shadow-md">
      <div className="flex items-center gap-4">
        <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-white/20 text-2xl font-bold backdrop-blur shadow-sm shrink-0">
          {getInitials(patient.name)}
        </div>
        <div>
          <h1 className="text-2xl font-bold tracking-tight">{patient.name}</h1>
          <div className="flex flex-wrap items-center gap-x-3 gap-y-1 text-sm opacity-90 mt-1">
            <span>{patient.age} yrs</span>
            <span>•</span>
            <span>{patient.gender}</span>
            {patient.blood_group && (
              <>
                <span>•</span>
                <span className="flex items-center gap-0.5">
                  <Droplets className="h-4 w-4 text-rose-300" />
                  Blood: {patient.blood_group}
                </span>
              </>
            )}
          </div>
        </div>
      </div>

      <div className="flex flex-wrap gap-x-4 gap-y-2 text-sm opacity-90 border-t border-white/10 md:border-t-0 pt-3 md:pt-0 w-full md:w-auto">
        {patient.phone && (
          <span className="flex items-center gap-1.5">
            <Phone className="h-4 w-4" />
            {patient.phone}
          </span>
        )}
        {patient.village_name && (
          <span className="flex items-center gap-1.5">
            <MapPin className="h-4 w-4" />
            {patient.village_name}, {patient.district || "Sikar"}
          </span>
        )}
      </div>
    </div>
  );
}
