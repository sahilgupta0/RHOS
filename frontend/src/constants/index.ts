export const API_ROUTES = {
  LOGIN: "/auth/login",
  REGISTER: "/auth/register",
  USER_PROFILE: "/auth/me",
  PATIENTS: "/patients",
  PATIENT_DETAIL: (id: string) => `/patient/${id}`,
  PATIENT_HISTORY: (id: string) => `/patient/history/${id}`,
  CONSULATION_START: "/consultation/start",
  CONSULATION_CHAT: "/consultation/chat",
  CONSULATION_UPLOAD: "/consultation/upload",
  CONSULTATIONS: "/consultations",
  TRIAGE: "/triage",
  MEDICINE_CHECK: "/medicine/check",
  SUMMARY: "/summary",
  SPEECH_TO_TEXT: "/speech-to-text",
  TEXT_TO_SPEECH: "/text-to-speech",
  UPLOAD: "/upload",
  HEALTH: "/health",
};

export const TRIAGE_PRIORITIES = {
  LOW: {
    label: "Low",
    color: "bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400",
    dot: "bg-emerald-500",
  },
  MEDIUM: {
    label: "Medium",
    color: "bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400",
    dot: "bg-amber-500",
  },
  HIGH: {
    label: "High",
    color: "bg-rose-100 text-rose-700 dark:bg-rose-900/30 dark:text-rose-400",
    dot: "bg-rose-500",
  },
};

export const BLOOD_GROUPS = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"] as const;

export const GENDERS = ["Male", "Female", "Other"] as const;

export const THEME_MODES = {
  LIGHT: "light",
  DARK: "dark",
  SYSTEM: "system",
} as const;
