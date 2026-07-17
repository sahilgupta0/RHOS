/**
 * RHOS API Service Modules.
 */

import apiClient from "./client";
import type {
  AuthResponse,
  LoginRequest,
  RegisterRequest,
  User,
  Patient,
  PatientListResponse,
  Consultation,
  ConsultationChatRequest,
  ConsultationChatResponse,
  TriageRequest,
  TriageResponse,
  MedicineCheckRequest,
  MedicineCheckResponse,
  DashboardStats,
  AnalyticsData,
  HealthResponse,
} from "../types";

// ── Auth API ────────────────────────────────────────────────────────────────

export const authApi = {
  login: (data: LoginRequest) =>
    apiClient.post<AuthResponse>("/auth/login", data).then((r) => r.data),

  register: (data: RegisterRequest) =>
    apiClient.post<AuthResponse>("/auth/register", data).then((r) => r.data),

  getMe: () =>
    apiClient.get<User>("/auth/me").then((r) => r.data),
};

// ── Patients API ────────────────────────────────────────────────────────────

export const patientsApi = {
  list: (params?: { search?: string; page?: number; page_size?: number; village_id?: string }) =>
    apiClient.get<PatientListResponse>("/patients", { params }).then((r) => r.data),

  getById: (id: string) =>
    apiClient.get<Patient>(`/patient/${id}`).then((r) => r.data),

  getHistory: (id: string) =>
    apiClient.get(`/patient/history/${id}`).then((r) => r.data),

  create: (data: Partial<Patient>) =>
    apiClient.post<Patient>("/patient", data).then((r) => r.data),

  update: (id: string, data: Partial<Patient>) =>
    apiClient.put<Patient>(`/patient/${id}`, data).then((r) => r.data),
};

// ── Consultation API ────────────────────────────────────────────────────────

export const consultationApi = {
  start: (data: { patient_id: string; chief_complaint?: string }) =>
    apiClient.post<Consultation>("/consultation/start", data).then((r) => r.data),

  chat: (data: ConsultationChatRequest) =>
    apiClient.post<ConsultationChatResponse>("/consultation/chat", data).then((r) => r.data),

  submit: (consultationId: string) =>
    apiClient.post<ConsultationChatResponse>("/consultation/submit", { consultation_id: consultationId }).then((r) => r.data),

  uploadImage: (consultationId: string, file: File) => {
    const formData = new FormData();
    formData.append("consultation_id", consultationId);
    formData.append("file", file);
    return apiClient.post("/consultation/upload", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    }).then((r) => r.data);
  },

  getById: (id: string) =>
    apiClient.get<Consultation>(`/consultation/${id}`).then((r) => r.data),

  clearChat: (id: string) =>
    apiClient.post<Consultation>(`/consultation/${id}/clear`).then((r) => r.data),

  list: (params?: { limit?: number; patient_id?: string }) =>
    apiClient.get<Consultation[]>("/consultations", { params }).then((r) => r.data),

  triage: (data: TriageRequest) =>
    apiClient.post<TriageResponse>("/triage", data).then((r) => r.data),

  medicineCheck: (data: MedicineCheckRequest) =>
    apiClient.post<MedicineCheckResponse>("/medicine/check", data).then((r) => r.data),

  summary: (consultationId: string) =>
    apiClient.post("/summary", { consultation_id: consultationId }).then((r) => r.data),
};


// ── Analytics API ───────────────────────────────────────────────────────────

export const analyticsApi = {
  getDashboard: () =>
    apiClient.get<DashboardStats>("/dashboard").then((r) => r.data),

  getAnalytics: (days?: number) =>
    apiClient.get<AnalyticsData>("/analytics", { params: { days } }).then((r) => r.data),
};

// ── Health API ──────────────────────────────────────────────────────────────

export const healthApi = {
  check: () =>
    apiClient.get<HealthResponse>("/health").then((r) => r.data),
};

// ── Upload API ──────────────────────────────────────────────────────────────

export const uploadApi = {
  upload: (file: File) => {
    const formData = new FormData();
    formData.append("file", file);
    return apiClient.post("/upload", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    }).then((r) => r.data);
  },
};
