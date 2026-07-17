import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { Loader2, MessageSquare } from "lucide-react";

const consultationSchema = z.object({
  patient_id: z.string().min(1, "Patient ID selection is required"),
  chief_complaint: z.string().min(5, "Chief complaint must be at least 5 characters"),
});

type ConsultationFormValues = z.infer<typeof consultationSchema>;

interface ConsultationFormProps {
  onSubmit: (data: ConsultationFormValues) => void;
  patientId?: string;
  isLoading?: boolean;
}

export default function ConsultationForm({ onSubmit, patientId = "", isLoading = false }: ConsultationFormProps) {
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<ConsultationFormValues>({
    resolver: zodResolver(consultationSchema),
    defaultValues: {
      patient_id: patientId,
      chief_complaint: "",
    },
  });

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4 max-w-md">
      <div>
        <label className="block text-xs font-semibold mb-1.5 uppercase tracking-wide">Patient ID</label>
        <input
          type="text"
          {...register("patient_id")}
          className="w-full rounded-xl border border-[hsl(var(--border))] bg-[hsl(var(--background))] px-3.5 py-2 text-sm outline-none focus:ring-2 focus:ring-[hsl(var(--ring))]/50"
          placeholder="e.g. P001"
          disabled={isLoading || !!patientId}
        />
        {errors.patient_id && <p className="text-xs text-rose-500 mt-1">{errors.patient_id.message}</p>}
      </div>

      <div>
        <label className="block text-xs font-semibold mb-1.5 uppercase tracking-wide">Chief Complaint</label>
        <textarea
          {...register("chief_complaint")}
          rows={3}
          className="w-full rounded-xl border border-[hsl(var(--border))] bg-[hsl(var(--background))] px-3.5 py-2 text-sm outline-none focus:ring-2 focus:ring-[hsl(var(--ring))]/50 resize-none"
          placeholder="Describe symptoms, duration, and pain levels..."
          disabled={isLoading}
        />
        {errors.chief_complaint && <p className="text-xs text-rose-500 mt-1">{errors.chief_complaint.message}</p>}
      </div>

      <button
        type="submit"
        disabled={isLoading}
        className="w-full rounded-xl bg-gradient-primary py-3 text-sm font-semibold text-white shadow-md hover:shadow-lg transition-all flex items-center justify-center gap-1.5 bg-gradient-primary"
      >
        {isLoading ? (
          <Loader2 className="h-4 w-4 animate-spin" />
        ) : (
          <MessageSquare className="h-4 w-4" />
        )}
        Start Consultation Session
      </button>
    </form>
  );
}
