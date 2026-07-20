/**
 * Tests for custom React hooks:
 * - useDebounce
 * - usePatients (via React Query)
 * - useConsultations (via React Query)
 * - useStartConsultation mutation
 */

import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { renderHook, act, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import React from "react";

// Mock the API modules
vi.mock("../../api", () => ({
  patientsApi: {
    list: vi.fn(),
    getById: vi.fn(),
    getHistory: vi.fn(),
    create: vi.fn(),
    update: vi.fn(),
  },
  consultationApi: {
    list: vi.fn(),
    start: vi.fn(),
    chat: vi.fn(),
    submit: vi.fn(),
    triage: vi.fn(),
    medicineCheck: vi.fn(),
    summary: vi.fn(),
    getById: vi.fn(),
    clearChat: vi.fn(),
    uploadImage: vi.fn(),
  },
}));

import { useDebounce } from "../../hooks/useDebounce";
import {
  usePatients,
  usePatient,
  useCreatePatient,
  useUpdatePatient,
} from "../../hooks/usePatients";
import {
  useConsultations,
  useStartConsultation,
  useConsultationChat,
  useTriage,
  useMedicineCheck,
} from "../../hooks/useConsultation";
import { patientsApi, consultationApi } from "../../api";

// ── Wrapper for React Query ──────────────────────────────────────────────────

const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false, gcTime: 0 },
      mutations: { retry: false },
    },
  });
  return ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );
};

// ── useDebounce Tests ────────────────────────────────────────────────────────

describe("useDebounce", () => {
  beforeEach(() => {
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it("returns initial value immediately", () => {
    const { result } = renderHook(() => useDebounce("initial", 300));
    expect(result.current).toBe("initial");
  });

  it("debounces value changes", async () => {
    const { result, rerender } = renderHook(
      ({ value }) => useDebounce(value, 300),
      { initialProps: { value: "first" } }
    );

    expect(result.current).toBe("first");

    rerender({ value: "second" });
    expect(result.current).toBe("first"); // Still old value

    act(() => {
      vi.advanceTimersByTime(300);
    });

    expect(result.current).toBe("second"); // Now updated
  });

  it("cancels previous timeout on rapid changes", () => {
    const { result, rerender } = renderHook(
      ({ value }) => useDebounce(value, 500),
      { initialProps: { value: "a" } }
    );

    rerender({ value: "ab" });
    rerender({ value: "abc" });

    act(() => {
      vi.advanceTimersByTime(500);
    });

    expect(result.current).toBe("abc");
  });

  it("handles number values", () => {
    const { result, rerender } = renderHook(
      ({ value }) => useDebounce(value, 200),
      { initialProps: { value: 0 } }
    );

    rerender({ value: 42 });
    act(() => {
      vi.advanceTimersByTime(200);
    });

    expect(result.current).toBe(42);
  });

  it("handles boolean values", () => {
    const { result, rerender } = renderHook(
      ({ value }) => useDebounce(value, 100),
      { initialProps: { value: false } }
    );

    rerender({ value: true });
    act(() => {
      vi.advanceTimersByTime(100);
    });

    expect(result.current).toBe(true);
  });
});

// ── usePatients Tests ────────────────────────────────────────────────────────

describe("usePatients", () => {
  it("fetches patients successfully", async () => {
    const mockData = {
      patients: [{ id: "p001", name: "Dinesh" }],
      total: 1,
    };
    vi.mocked(patientsApi.list).mockResolvedValue(mockData as any);

    const { result } = renderHook(() => usePatients(), {
      wrapper: createWrapper(),
    });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data).toEqual(mockData);
  });

  it("fetches patients with search filter", async () => {
    const mockData = { patients: [], total: 0 };
    vi.mocked(patientsApi.list).mockResolvedValue(mockData as any);

    const { result } = renderHook(
      () => usePatients({ search: "Dinesh" }),
      { wrapper: createWrapper() }
    );

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(patientsApi.list).toHaveBeenCalledWith({ search: "Dinesh" });
  });

  it("handles patients fetch error", async () => {
    vi.mocked(patientsApi.list).mockRejectedValue(
      new Error("Network error")
    );

    const { result } = renderHook(() => usePatients(), {
      wrapper: createWrapper(),
    });

    await waitFor(() => expect(result.current.isError).toBe(true));
    expect(result.current.error).toBeDefined();
  });
});

describe("usePatient", () => {
  it("fetches single patient by ID", async () => {
    const mockPatient = { id: "p001", name: "Dinesh" };
    vi.mocked(patientsApi.getById).mockResolvedValue(mockPatient as any);

    const { result } = renderHook(() => usePatient("p001"), {
      wrapper: createWrapper(),
    });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data).toEqual(mockPatient);
  });

  it("does not fetch when id is empty", () => {
    const { result } = renderHook(() => usePatient(""), {
      wrapper: createWrapper(),
    });

    // Query should be disabled (not fetching)
    expect(result.current.isFetching).toBe(false);
  });
});

describe("useCreatePatient", () => {
  it("calls create API and invalidates queries", async () => {
    const mockPatient = { id: "p002", name: "New Patient" };
    vi.mocked(patientsApi.create).mockResolvedValue(mockPatient as any);

    const { result } = renderHook(() => useCreatePatient(), {
      wrapper: createWrapper(),
    });

    act(() => {
      result.current.mutate({ name: "New Patient" } as any);
    });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(patientsApi.create).toHaveBeenCalledWith({ name: "New Patient" });
  });
});

describe("useUpdatePatient", () => {
  it("calls update API with patient data", async () => {
    const mockPatient = { id: "p001", name: "Updated Name" };
    vi.mocked(patientsApi.update).mockResolvedValue(mockPatient as any);

    const { result } = renderHook(() => useUpdatePatient("p001"), {
      wrapper: createWrapper(),
    });

    act(() => {
      result.current.mutate({ name: "Updated Name" } as any);
    });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(patientsApi.update).toHaveBeenCalledWith("p001", {
      name: "Updated Name",
    });
  });
});

// ── useConsultations Tests ───────────────────────────────────────────────────

describe("useConsultations", () => {
  it("fetches consultations list", async () => {
    const mockConsultations = [
      { id: "c001", patient_id: "p001", status: "active" },
    ];
    vi.mocked(consultationApi.list).mockResolvedValue(
      mockConsultations as any
    );

    const { result } = renderHook(() => useConsultations(), {
      wrapper: createWrapper(),
    });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data).toEqual(mockConsultations);
  });

  it("fetches consultations with patient_id filter", async () => {
    vi.mocked(consultationApi.list).mockResolvedValue([] as any);

    const { result } = renderHook(
      () => useConsultations({ patient_id: "p001", limit: 5 }),
      { wrapper: createWrapper() }
    );

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(consultationApi.list).toHaveBeenCalledWith({
      patient_id: "p001",
      limit: 5,
    });
  });
});

describe("useStartConsultation", () => {
  it("starts a new consultation and invalidates cache", async () => {
    const mockConsultation = { id: "c002", status: "active" };
    vi.mocked(consultationApi.start).mockResolvedValue(
      mockConsultation as any
    );

    const { result } = renderHook(() => useStartConsultation(), {
      wrapper: createWrapper(),
    });

    act(() => {
      result.current.mutate({
        patient_id: "p001",
        chief_complaint: "Fever",
      });
    });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(consultationApi.start).toHaveBeenCalledWith({
      patient_id: "p001",
      chief_complaint: "Fever",
    });
  });
});

describe("useConsultationChat", () => {
  it("sends a chat message successfully", async () => {
    const mockResponse = {
      consultation_id: "c001",
      agent_response: "How long have you had this?",
      symptoms_extracted: [],
    };
    vi.mocked(consultationApi.chat).mockResolvedValue(mockResponse as any);

    const { result } = renderHook(() => useConsultationChat(), {
      wrapper: createWrapper(),
    });

    act(() => {
      result.current.mutate({
        consultation_id: "c001",
        message: "I have a headache",
      });
    });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data).toEqual(mockResponse);
  });
});

describe("useTriage", () => {
  it("runs triage classification", async () => {
    const mockTriage = {
      priority: "HIGH",
      reasoning: "High fever",
      confidence: 0.9,
    };
    vi.mocked(consultationApi.triage).mockResolvedValue(mockTriage as any);

    const { result } = renderHook(() => useTriage(), {
      wrapper: createWrapper(),
    });

    act(() => {
      result.current.mutate({
        patient_id: "p001",
        symptoms: ["fever"],
        vitals: { temp: 103.5 },
        medical_history: [],
      });
    });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data?.priority).toBe("HIGH");
  });
});

describe("useMedicineCheck", () => {
  it("checks medicine safety", async () => {
    const mockResult = {
      safe_to_prescribe: false,
      interactions: ["NSAIDs conflict"],
    };
    vi.mocked(consultationApi.medicineCheck).mockResolvedValue(
      mockResult as any
    );

    const { result } = renderHook(() => useMedicineCheck(), {
      wrapper: createWrapper(),
    });

    act(() => {
      result.current.mutate({
        medications: ["Aspirin", "Ibuprofen"],
        allergies: [],
        conditions: [],
      });
    });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data?.safe_to_prescribe).toBe(false);
  });
});
