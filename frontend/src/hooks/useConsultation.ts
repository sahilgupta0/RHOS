import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { consultationApi } from "../api";
import type { ConsultationChatRequest, TriageRequest, MedicineCheckRequest } from "../types";

export function useConsultations(params?: { limit?: number; patient_id?: string }) {
  return useQuery({
    queryKey: ["consultations", params],
    queryFn: () => consultationApi.list(params),
  });
}

export function useStartConsultation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: { patient_id: string; chief_complaint?: string }) =>
      consultationApi.start(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["consultations"] });
    },
  });
}

export function useConsultationChat() {
  return useMutation({
    mutationFn: (data: ConsultationChatRequest) => consultationApi.chat(data),
  });
}

export function useTriage() {
  return useMutation({
    mutationFn: (data: TriageRequest) => consultationApi.triage(data),
  });
}

export function useMedicineCheck() {
  return useMutation({
    mutationFn: (data: MedicineCheckRequest) => consultationApi.medicineCheck(data),
  });
}

export function useConsultationSummary() {
  return useMutation({
    mutationFn: (consultationId: string) => consultationApi.summary(consultationId),
  });
}
