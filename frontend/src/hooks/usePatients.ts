import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { patientsApi } from "../api";
import type { Patient } from "../types";

export function usePatients(filters?: { search?: string; page?: number; page_size?: number; village_id?: string }) {
  return useQuery({
    queryKey: ["patients", filters],
    queryFn: () => patientsApi.list(filters),
  });
}

export function usePatient(id: string) {
  return useQuery({
    queryKey: ["patient", id],
    queryFn: () => patientsApi.getById(id),
    enabled: !!id,
  });
}

export function usePatientHistory(id: string) {
  return useQuery({
    queryKey: ["patientHistory", id],
    queryFn: () => patientsApi.getHistory(id),
    enabled: !!id,
  });
}

export function useCreatePatient() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: Partial<Patient>) => patientsApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["patients"] });
    },
  });
}

export function useUpdatePatient(id: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: Partial<Patient>) => patientsApi.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["patient", id] });
      queryClient.invalidateQueries({ queryKey: ["patients"] });
    },
  });
}
