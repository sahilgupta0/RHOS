/**
 * Tests for the API client module (api/index.ts) and API client base (api/client.ts).
 * Uses vi.mock for axios to avoid real HTTP calls.
 */

import { describe, it, expect, vi, beforeEach } from "vitest";

// Mock axios entirely before importing api modules
vi.mock("axios", () => {
  const mockAxiosInstance = {
    post: vi.fn(),
    get: vi.fn(),
    put: vi.fn(),
    delete: vi.fn(),
    interceptors: {
      request: { use: vi.fn() },
      response: { use: vi.fn() },
    },
    defaults: { headers: {} },
  };

  return {
    default: {
      create: vi.fn(() => mockAxiosInstance),
      ...mockAxiosInstance,
    },
  };
});

import axios from "axios";

// ── Mock axios instance setup ─────────────────────────────────────────────────

const mockAxios = axios.create() as any;

beforeEach(() => {
  vi.clearAllMocks();
});

// ── Test authApi structure ───────────────────────────────────────────────────

describe("authApi", () => {
  it("authApi.login calls post with /auth/login", async () => {
    mockAxios.post.mockResolvedValueOnce({
      data: { access_token: "tok", user: { email: "a@b.com" } },
    });

    const { authApi } = await import("../../api/index");
    const result = await authApi.login({
      email: "a@b.com",
      password: "pass",
    });

    expect(mockAxios.post).toHaveBeenCalledWith("/auth/login", {
      email: "a@b.com",
      password: "pass",
    });
    expect(result.access_token).toBe("tok");
  });

  it("authApi.register calls post with /auth/register", async () => {
    mockAxios.post.mockResolvedValueOnce({
      data: { access_token: "reg-tok", user: { email: "new@b.com" } },
    });

    const { authApi } = await import("../../api/index");
    await authApi.register({
      email: "new@b.com",
      password: "pass",
      name: "New User",
      role: "nurse",
      phone: "+91-1234567890",
    });

    expect(mockAxios.post).toHaveBeenCalledWith(
      "/auth/register",
      expect.objectContaining({ email: "new@b.com" })
    );
  });

  it("authApi.getMe calls get with /auth/me", async () => {
    mockAxios.get.mockResolvedValueOnce({
      data: { id: "u1", email: "me@b.com", role: "doctor" },
    });

    const { authApi } = await import("../../api/index");
    const result = await authApi.getMe();

    expect(mockAxios.get).toHaveBeenCalledWith("/auth/me");
    expect(result.role).toBe("doctor");
  });
});

// ── Test patientsApi structure ───────────────────────────────────────────────

describe("patientsApi", () => {
  it("patientsApi.list calls get /patients", async () => {
    mockAxios.get.mockResolvedValueOnce({
      data: { patients: [], total: 0 },
    });

    const { patientsApi } = await import("../../api/index");
    await patientsApi.list();

    expect(mockAxios.get).toHaveBeenCalledWith(
      "/patients",
      expect.any(Object)
    );
  });

  it("patientsApi.getById calls get /patient/:id", async () => {
    mockAxios.get.mockResolvedValueOnce({ data: { id: "p001" } });

    const { patientsApi } = await import("../../api/index");
    await patientsApi.getById("p001");

    expect(mockAxios.get).toHaveBeenCalledWith("/patient/p001");
  });

  it("patientsApi.create calls post /patient", async () => {
    mockAxios.post.mockResolvedValueOnce({ data: { id: "p002" } });

    const { patientsApi } = await import("../../api/index");
    await patientsApi.create({ name: "Sita" });

    expect(mockAxios.post).toHaveBeenCalledWith(
      "/patient",
      expect.objectContaining({ name: "Sita" })
    );
  });

  it("patientsApi.update calls put /patient/:id", async () => {
    mockAxios.put.mockResolvedValueOnce({ data: { id: "p001" } });

    const { patientsApi } = await import("../../api/index");
    await patientsApi.update("p001", { phone: "+91-1111111111" });

    expect(mockAxios.put).toHaveBeenCalledWith(
      "/patient/p001",
      expect.objectContaining({ phone: "+91-1111111111" })
    );
  });

  it("patientsApi.getHistory calls get /patient/history/:id", async () => {
    mockAxios.get.mockResolvedValueOnce({ data: { history: [] } });

    const { patientsApi } = await import("../../api/index");
    await patientsApi.getHistory("p001");

    expect(mockAxios.get).toHaveBeenCalledWith("/patient/history/p001");
  });
});

// ── Test consultationApi structure ───────────────────────────────────────────

describe("consultationApi", () => {
  it("consultationApi.start calls post /consultation/start", async () => {
    mockAxios.post.mockResolvedValueOnce({ data: { id: "c001" } });

    const { consultationApi } = await import("../../api/index");
    await consultationApi.start({ patient_id: "p001" });

    expect(mockAxios.post).toHaveBeenCalledWith(
      "/consultation/start",
      expect.objectContaining({ patient_id: "p001" })
    );
  });

  it("consultationApi.chat calls post /consultation/chat", async () => {
    mockAxios.post.mockResolvedValueOnce({
      data: { consultation_id: "c001", agent_response: "test" },
    });

    const { consultationApi } = await import("../../api/index");
    await consultationApi.chat({ consultation_id: "c001", message: "hello" });

    expect(mockAxios.post).toHaveBeenCalledWith(
      "/consultation/chat",
      expect.objectContaining({ consultation_id: "c001" })
    );
  });

  it("consultationApi.submit calls post /consultation/submit", async () => {
    mockAxios.post.mockResolvedValueOnce({
      data: { consultation_id: "c001" },
    });

    const { consultationApi } = await import("../../api/index");
    await consultationApi.submit("c001");

    expect(mockAxios.post).toHaveBeenCalledWith(
      "/consultation/submit",
      expect.objectContaining({ consultation_id: "c001" })
    );
  });

  it("consultationApi.triage calls post /triage", async () => {
    mockAxios.post.mockResolvedValueOnce({
      data: { priority: "HIGH", reasoning: "test" },
    });

    const { consultationApi } = await import("../../api/index");
    await consultationApi.triage({
      patient_id: "p001",
      symptoms: ["fever"],
      vitals: {},
      medical_history: [],
    });

    expect(mockAxios.post).toHaveBeenCalledWith(
      "/triage",
      expect.any(Object)
    );
  });

  it("consultationApi.list calls get /consultations", async () => {
    mockAxios.get.mockResolvedValueOnce({ data: [] });

    const { consultationApi } = await import("../../api/index");
    await consultationApi.list();

    expect(mockAxios.get).toHaveBeenCalledWith(
      "/consultations",
      expect.any(Object)
    );
  });

  it("consultationApi.getById calls get /consultation/:id", async () => {
    mockAxios.get.mockResolvedValueOnce({ data: { id: "c001" } });

    const { consultationApi } = await import("../../api/index");
    await consultationApi.getById("c001");

    expect(mockAxios.get).toHaveBeenCalledWith("/consultation/c001");
  });

  it("consultationApi.summary calls post /summary", async () => {
    mockAxios.post.mockResolvedValueOnce({
      data: { summary: "Patient summary" },
    });

    const { consultationApi } = await import("../../api/index");
    await consultationApi.summary("c001");

    expect(mockAxios.post).toHaveBeenCalledWith(
      "/summary",
      expect.objectContaining({ consultation_id: "c001" })
    );
  });
});

// ── Test analyticsApi structure ──────────────────────────────────────────────

describe("analyticsApi", () => {
  it("analyticsApi.getDashboard calls get /dashboard", async () => {
    mockAxios.get.mockResolvedValueOnce({
      data: { total_patients: 10 },
    });

    const { analyticsApi } = await import("../../api/index");
    await analyticsApi.getDashboard();

    expect(mockAxios.get).toHaveBeenCalledWith("/dashboard");
  });

  it("analyticsApi.getAnalytics calls get /analytics with days param", async () => {
    mockAxios.get.mockResolvedValueOnce({ data: {} });

    const { analyticsApi } = await import("../../api/index");
    await analyticsApi.getAnalytics(30);

    expect(mockAxios.get).toHaveBeenCalledWith(
      "/analytics",
      expect.objectContaining({ params: { days: 30 } })
    );
  });
});

// ── Test healthApi structure ─────────────────────────────────────────────────

describe("healthApi", () => {
  it("healthApi.check calls get /health", async () => {
    mockAxios.get.mockResolvedValueOnce({ data: { status: "healthy" } });

    const { healthApi } = await import("../../api/index");
    const result = await healthApi.check();

    expect(mockAxios.get).toHaveBeenCalledWith("/health");
    expect(result.status).toBe("healthy");
  });
});
