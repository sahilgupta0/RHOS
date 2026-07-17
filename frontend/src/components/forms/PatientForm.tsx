import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { Loader2 } from "lucide-react";
import { BLOOD_GROUPS, GENDERS } from "../../constants";

const patientSchema = z.object({
  name: z.string().min(2, "Name must be at least 2 characters"),
  age: z.number().min(0, "Age cannot be negative").max(120, "Invalid age"),
  gender: z.enum(["Male", "Female", "Other"]),
  blood_group: z.enum(["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]).optional(),
  phone: z.string().regex(/^\+91-\d{10}$/, "Format must be +91-XXXXXXXXXX"),
  address: z.string().min(5, "Address must be at least 5 characters"),
  village_name: z.string().min(2, "Village name is required"),
  emergency_contact: z.string().optional(),
});

type PatientFormValues = z.infer<typeof patientSchema>;

interface PatientFormProps {
  onSubmit: (data: PatientFormValues) => void;
  initialValues?: Partial<PatientFormValues>;
  isLoading?: boolean;
}

export default function PatientForm({ onSubmit, initialValues, isLoading = false }: PatientFormProps) {
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<PatientFormValues>({
    resolver: zodResolver(patientSchema),
    defaultValues: {
      name: "",
      age: 30,
      gender: "Male",
      phone: "+91-",
      address: "",
      village_name: "",
      ...initialValues,
    },
  });

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4 max-w-lg">
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-xs font-semibold mb-1.5 uppercase tracking-wide">Full Name</label>
          <input
            type="text"
            {...register("name")}
            className="w-full rounded-xl border border-[hsl(var(--border))] bg-[hsl(var(--background))] px-3.5 py-2 text-sm outline-none focus:ring-2 focus:ring-[hsl(var(--ring))]/50"
            placeholder="John Doe"
            disabled={isLoading}
          />
          {errors.name && <p className="text-xs text-rose-500 mt-1">{errors.name.message}</p>}
        </div>

        <div>
          <label className="block text-xs font-semibold mb-1.5 uppercase tracking-wide">Age</label>
          <input
            type="number"
            {...register("age", { valueAsNumber: true })}
            className="w-full rounded-xl border border-[hsl(var(--border))] bg-[hsl(var(--background))] px-3.5 py-2 text-sm outline-none focus:ring-2 focus:ring-[hsl(var(--ring))]/50"
            disabled={isLoading}
          />
          {errors.age && <p className="text-xs text-rose-500 mt-1">{errors.age.message}</p>}
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-xs font-semibold mb-1.5 uppercase tracking-wide">Gender</label>
          <select
            {...register("gender")}
            className="w-full rounded-xl border border-[hsl(var(--border))] bg-[hsl(var(--background))] px-3.5 py-2 text-sm outline-none focus:ring-2 focus:ring-[hsl(var(--ring))]/50"
            disabled={isLoading}
          >
            {GENDERS.map((g) => (
              <option key={g} value={g}>
                {g}
              </option>
            ))}
          </select>
          {errors.gender && <p className="text-xs text-rose-500 mt-1">{errors.gender.message}</p>}
        </div>

        <div>
          <label className="block text-xs font-semibold mb-1.5 uppercase tracking-wide">Blood Group</label>
          <select
            {...register("blood_group")}
            className="w-full rounded-xl border border-[hsl(var(--border))] bg-[hsl(var(--background))] px-3.5 py-2 text-sm outline-none focus:ring-2 focus:ring-[hsl(var(--ring))]/50"
            disabled={isLoading}
          >
            <option value="">Select blood type</option>
            {BLOOD_GROUPS.map((bg) => (
              <option key={bg} value={bg}>
                {bg}
              </option>
            ))}
          </select>
        </div>
      </div>

      <div>
        <label className="block text-xs font-semibold mb-1.5 uppercase tracking-wide">Phone Number</label>
        <input
          type="text"
          {...register("phone")}
          className="w-full rounded-xl border border-[hsl(var(--border))] bg-[hsl(var(--background))] px-3.5 py-2 text-sm outline-none focus:ring-2 focus:ring-[hsl(var(--ring))]/50"
          placeholder="+91-9876543210"
          disabled={isLoading}
        />
        {errors.phone && <p className="text-xs text-rose-500 mt-1">{errors.phone.message}</p>}
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-xs font-semibold mb-1.5 uppercase tracking-wide">Village</label>
          <input
            type="text"
            {...register("village_name")}
            className="w-full rounded-xl border border-[hsl(var(--border))] bg-[hsl(var(--background))] px-3.5 py-2 text-sm outline-none focus:ring-2 focus:ring-[hsl(var(--ring))]/50"
            placeholder="Khandela"
            disabled={isLoading}
          />
          {errors.village_name && <p className="text-xs text-rose-500 mt-1">{errors.village_name.message}</p>}
        </div>

        <div>
          <label className="block text-xs font-semibold mb-1.5 uppercase tracking-wide">Emergency Contact</label>
          <input
            type="text"
            {...register("emergency_contact")}
            className="w-full rounded-xl border border-[hsl(var(--border))] bg-[hsl(var(--background))] px-3.5 py-2 text-sm outline-none focus:ring-2 focus:ring-[hsl(var(--ring))]/50"
            placeholder="+91-XXXXXXXXXX"
            disabled={isLoading}
          />
        </div>
      </div>

      <div>
        <label className="block text-xs font-semibold mb-1.5 uppercase tracking-wide">Address</label>
        <textarea
          {...register("address")}
          rows={2}
          className="w-full rounded-xl border border-[hsl(var(--border))] bg-[hsl(var(--background))] px-3.5 py-2 text-sm outline-none focus:ring-2 focus:ring-[hsl(var(--ring))]/50 resize-none"
          placeholder="Detailed home address details..."
          disabled={isLoading}
        />
        {errors.address && <p className="text-xs text-rose-500 mt-1">{errors.address.message}</p>}
      </div>

      <button
        type="submit"
        disabled={isLoading}
        className="w-full rounded-xl bg-gradient-primary py-3 text-sm font-semibold text-white shadow-md hover:shadow-lg transition-all flex items-center justify-center gap-1.5"
      >
        {isLoading && <Loader2 className="h-4 w-4 animate-spin" />}
        Save Patient Card
      </button>
    </form>
  );
}
