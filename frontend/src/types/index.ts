/**
 * RHOS TypeScript Type Definitions.
 *
 * Matches backend Pydantic schemas.
 */

// ── Enums ───────────────────────────────────────────────────────────────────

export type TriagePriority = "LOW" | "MEDIUM" | "HIGH";
export type Gender = "Male" | "Female" | "Other";
export type BloodGroup = "A+" | "A-" | "B+" | "B-" | "AB+" | "AB-" | "O+" | "O-";
export type UserRole = "doctor" | "nurse" | "asha_worker" | "admin" | "patient";
export type AppointmentStatus = "scheduled" | "completed" | "cancelled" | "no-show";
export type ConsultationStatus = "active" | "completed" | "cancelled";

// ── User & Auth ─────────────────────────────────────────────────────────────

export interface User {
  id: string;
  email: string;
  name: string;
  role: UserRole;
  phone?: string;
  hospital_name?: string;
  avatar_url?: string;
  is_active?: boolean;
  patient_id?: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  name: string;
  role?: UserRole;
  phone?: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User | null;
}

// ── Patient ─────────────────────────────────────────────────────────────────

export interface Patient {
  id: string;
  name: string;
  age: number;
  gender: Gender;
  date_of_birth?: string;
  blood_group?: BloodGroup;
  phone?: string;
  address?: string;
  village_id?: string;
  village_name?: string;
  district?: string;
  asha_worker_id?: string;
  is_active?: boolean;
  created_at?: string;
}

export interface PatientListResponse {
  patients: Patient[];
  total: number;
  page: number;
  page_size: number;
}

// ── Medical History ─────────────────────────────────────────────────────────

export interface MedicalHistory {
  id: string;
  patient_id: string;
  condition: string;
  diagnosed_date?: string;
  status: "active" | "resolved" | "chronic" | "managed";
  treating_doctor?: string;
  notes?: string;
}

export interface Vital {
  id: string;
  patient_id: string;
  visit_id?: string;
  recorded_at: string;
  bp_systolic?: number;
  bp_diastolic?: number;
  heart_rate?: number;
  temperature?: number;
  spo2?: number;
  weight?: number;
  height?: number;
}

export interface Allergy {
  id: string;
  patient_id: string;
  allergen: string;
  severity: "mild" | "moderate" | "severe";
  reaction?: string;
}

// ── Consultation ────────────────────────────────────────────────────────────

export interface Consultation {
  id: string;
  patient_id: string;
  patient_name?: string;
  doctor_name?: string;
  chief_complaint?: string;
  triage_priority?: TriagePriority;
  triage_reasoning?: string;
  conversation_history?: { role: string; content: string }[];
  status: ConsultationStatus;
  clinical_summary?: string;
  follow_up_plan?: string;
  duration?: string;
  created_at?: string;
}

export interface ConsultationChatRequest {
  consultation_id: string;
  message: string;
  language?: string;
}

export interface ConsultationChatResponse {
  consultation_id: string;
  agent_response: string;
  symptoms_extracted?: Record<string, unknown>[];
  triage_priority?: TriagePriority;
  triage_reasoning?: string;
  history_summary?: string;
  clinical_summary?: string;
  medication_checks?: Record<string, unknown>[];
  follow_up_plan?: string;
  ready_to_submit?: boolean;
  agent_pipeline_status?: Record<string, string>;
}

// ── Triage ──────────────────────────────────────────────────────────────────

export interface TriageRequest {
  patient_id: string;
  symptoms: string[];
  vitals?: Record<string, unknown>;
  medical_history?: string[];
  age?: number;
  gender?: string;
}

export interface TriageResponse {
  priority: TriagePriority;
  reasoning: string;
  confidence: number;
  recommendations: string[];
  disclaimer: string;
}

// ── Medicine ────────────────────────────────────────────────────────────────

export interface MedicineCheckRequest {
  medications: string[];
  patient_id?: string;
  allergies?: string[];
  current_medications?: string[];
  age?: number;
  conditions?: string[];
}

export interface MedicineCheckResponse {
  interactions: Record<string, unknown>[];
  allergy_warnings: Record<string, unknown>[];
  warnings: string[];
  alternatives: Record<string, unknown>[];
  safe_to_prescribe: boolean;
  disclaimer: string;
}

// ── Analytics ───────────────────────────────────────────────────────────────

export interface DashboardStats {
  total_patients: number;
  patients_today: number;
  patients_this_week: number;
  high_priority_today: number;
  consultations_today: number;
  consultations_this_week: number;
  follow_ups_pending: number;
  referrals_this_month: number;
}

export interface DiseaseDistribution {
  condition: string;
  count: number;
  percentage: number;
}

export interface PatientTrend {
  date: string;
  count: number;
  high_priority: number;
}

export interface VillageStats {
  village_id: string;
  village_name: string;
  total_patients: number;
  active_cases: number;
  high_priority: number;
}

export interface AnalyticsData {
  dashboard_stats: DashboardStats;
  disease_distribution: DiseaseDistribution[];
  patient_trends: PatientTrend[];
  village_stats: VillageStats[];
}

// ── Health ──────────────────────────────────────────────────────────────────

export interface HealthResponse {
  status: string;
  version: string;
  firebase_connected: boolean;
  gemini_configured: boolean;
}

// ── Chat Message ────────────────────────────────────────────────────────────

export interface ChatMessage {
  id: string;
  role: "patient" | "assistant" | "system";
  content: string;
  timestamp: Date;
  agentName?: string;
  isLoading?: boolean;
}

// ── Navigation ──────────────────────────────────────────────────────────────

export interface NavItem {
  label: string;
  path: string;
  icon: string;
  badge?: number;
}
