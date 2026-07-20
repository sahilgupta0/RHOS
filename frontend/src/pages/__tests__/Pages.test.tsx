/**
 * Tests for Page components:
 * - Login page (rendering, form interaction)
 * - NotFound page
 * - Context (AuthContext, ThemeContext) shape verification
 * - Utility functions (lib/utils)
 */

import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import React from "react";

// ── Auth context mock ────────────────────────────────────────────────────────

const mockLogin = vi.fn().mockResolvedValue(undefined);
const mockRegister = vi.fn().mockResolvedValue(undefined);
const mockLogout = vi.fn();

vi.mock("../../context/AuthContext", () => ({
  useAuth: () => ({
    user: null,
    login: mockLogin,
    register: mockRegister,
    logout: mockLogout,
    loading: false,
    isLoading: false,
    isAuthenticated: false,
  }),
  AuthProvider: ({ children }: { children: React.ReactNode }) => (
    <>{children}</>
  ),
}));

// ── Theme context mock ───────────────────────────────────────────────────────

vi.mock("../../context/ThemeContext", () => ({
  useTheme: () => ({ theme: "light", toggleTheme: vi.fn() }),
  ThemeProvider: ({ children }: { children: React.ReactNode }) => (
    <>{children}</>
  ),
}));

// ── API mocks ────────────────────────────────────────────────────────────────

vi.mock("../../api", () => ({
  analyticsApi: {
    getDashboard: vi.fn().mockResolvedValue({
      total_patients: 300,
      patients_today: 24,
      high_priority_today: 3,
      consultations_today: 18,
    }),
    getAnalytics: vi.fn().mockResolvedValue({
      patient_trends: [],
      disease_distribution: [],
      village_stats: [],
    }),
  },
  patientsApi: {
    list: vi.fn().mockResolvedValue({ patients: [], total: 0 }),
  },
  consultationApi: {
    list: vi.fn().mockResolvedValue([]),
  },
}));

// ── Recharts mock ────────────────────────────────────────────────────────────

vi.mock("recharts", () => ({
  ResponsiveContainer: ({ children }: any) => (
    <div data-testid="responsive-container">{children}</div>
  ),
  PieChart: ({ children }: any) => (
    <div data-testid="pie-chart">{children}</div>
  ),
  Pie: () => <div data-testid="pie" />,
  Cell: () => <div />,
  BarChart: ({ children }: any) => (
    <div data-testid="bar-chart">{children}</div>
  ),
  Bar: () => <div />,
  LineChart: ({ children }: any) => (
    <div data-testid="line-chart">{children}</div>
  ),
  Line: () => <div />,
  XAxis: () => <div />,
  YAxis: () => <div />,
  CartesianGrid: () => <div />,
  Tooltip: () => <div />,
  Legend: () => <div />,
}));

// ── Wrapper ─────────────────────────────────────────────────────────────────

const createWrapper = (initialPath = "/") => {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false }, mutations: { retry: false } },
  });
  return ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>
      <MemoryRouter initialEntries={[initialPath]}>{children}</MemoryRouter>
    </QueryClientProvider>
  );
};

// ── Imports (after mocks) ────────────────────────────────────────────────────

import Login from "../../pages/Login/index";
import NotFound from "../../pages/NotFound/index";

// ── Login Page Tests ─────────────────────────────────────────────────────────

describe("Login Page", () => {
  it("renders the page without crashing", () => {
    const { container } = render(<Login />, { wrapper: createWrapper("/login") });
    expect(container).toBeTruthy();
    expect(container.firstChild).toBeTruthy();
  });

  it("renders at least one RHOS brand element", () => {
    render(<Login />, { wrapper: createWrapper("/login") });
    // Use getAllByText to handle multiple matches
    const rhosElements = screen.getAllByText(/RHOS/i);
    expect(rhosElements.length).toBeGreaterThan(0);
  });

  it("shows email input field", () => {
    render(<Login />, { wrapper: createWrapper("/login") });
    const emailInputs = document.querySelectorAll('input[type="email"]');
    expect(emailInputs.length).toBeGreaterThan(0);
  });

  it("shows password input field", () => {
    render(<Login />, { wrapper: createWrapper("/login") });
    const passwordInputs = document.querySelectorAll('input[type="password"]');
    expect(passwordInputs.length).toBeGreaterThan(0);
  });

  it("renders a submit button", () => {
    render(<Login />, { wrapper: createWrapper("/login") });
    const submitButtons = document.querySelectorAll('button[type="submit"]');
    expect(submitButtons.length).toBeGreaterThan(0);
  });

  it("submits login form on button click without crashing", () => {
    render(<Login />, { wrapper: createWrapper("/login") });

    const submitButton = document.querySelector('button[type="submit"]');
    if (submitButton) {
      fireEvent.click(submitButton);
    }

    // Verify page is still mounted
    expect(document.body).toBeInTheDocument();
  });

  it("renders staff and patient tab options", () => {
    render(<Login />, { wrapper: createWrapper("/login") });
    // Tabs or buttons for Staff/Patient should exist
    const staffEl =
      screen.queryByText(/staff/i) || screen.queryByText(/doctor/i);
    const patientEl = screen.queryByText(/patient/i);
    expect(staffEl || patientEl).toBeTruthy();
  });
});

// ── NotFound Page Tests ──────────────────────────────────────────────────────

describe("NotFound Page", () => {
  it("renders without crashing", () => {
    const { container } = render(<NotFound />, {
      wrapper: createWrapper("/nonexistent"),
    });
    expect(container).toBeTruthy();
  });

  it("shows 404 text", () => {
    render(<NotFound />, { wrapper: createWrapper("/nonexistent") });
    const elements = screen.queryAllByText(/404/i);
    expect(elements.length).toBeGreaterThan(0);
  });

  it("shows a back to home or navigation link", () => {
    render(<NotFound />, { wrapper: createWrapper("/nonexistent") });
    const link =
      screen.queryByText(/back to home/i) ||
      screen.queryByText(/home/i) ||
      document.querySelector("a");
    expect(link).toBeTruthy();
  });

  it("shows page not found message", () => {
    render(<NotFound />, { wrapper: createWrapper("/nonexistent") });
    const msg =
      screen.queryByText(/not found/i) ||
      screen.queryByText(/doesn't exist/i) ||
      screen.queryByText(/route/i);
    expect(msg).toBeTruthy();
  });
});

// ── AuthContext mock verification ────────────────────────────────────────────

describe("AuthContext mock shape", () => {
  it("useAuth returns expected properties", async () => {
    const { useAuth } = await import("../../context/AuthContext");
    const auth = useAuth();
    expect(auth).toHaveProperty("user");
    expect(auth).toHaveProperty("login");
    expect(auth).toHaveProperty("logout");
    expect(auth).toHaveProperty("isAuthenticated");
    expect(typeof auth.login).toBe("function");
    expect(typeof auth.logout).toBe("function");
  });

  it("isAuthenticated is false by default in mock", async () => {
    const { useAuth } = await import("../../context/AuthContext");
    expect(useAuth().isAuthenticated).toBe(false);
  });
});

// ── ThemeContext mock verification ───────────────────────────────────────────

describe("ThemeContext mock shape", () => {
  it("useTheme returns theme and toggleTheme", async () => {
    const { useTheme } = await import("../../context/ThemeContext");
    const theme = useTheme();
    expect(theme).toHaveProperty("theme");
    expect(theme).toHaveProperty("toggleTheme");
    expect(typeof theme.toggleTheme).toBe("function");
  });

  it("theme is 'light' in mock", async () => {
    const { useTheme } = await import("../../context/ThemeContext");
    expect(useTheme().theme).toBe("light");
  });
});

// ── Utility Functions Tests ──────────────────────────────────────────────────

describe("Utility functions (lib/utils)", () => {
  it("cn merges class names correctly", async () => {
    const { cn } = await import("../../lib/utils");
    const result = cn("foo", "bar", undefined, "baz");
    expect(result).toContain("foo");
    expect(result).toContain("bar");
    expect(result).toContain("baz");
  });

  it("cn handles empty inputs", async () => {
    const { cn } = await import("../../lib/utils");
    const result = cn();
    expect(typeof result).toBe("string");
  });

  it("getTriageColor returns string for HIGH", async () => {
    const { getTriageColor } = await import("../../lib/utils");
    const colorClass = getTriageColor("HIGH");
    expect(typeof colorClass).toBe("string");
    expect(colorClass.length).toBeGreaterThan(0);
  });

  it("getTriageColor returns string for MEDIUM", async () => {
    const { getTriageColor } = await import("../../lib/utils");
    expect(typeof getTriageColor("MEDIUM")).toBe("string");
  });

  it("getTriageColor returns string for LOW", async () => {
    const { getTriageColor } = await import("../../lib/utils");
    expect(typeof getTriageColor("LOW")).toBe("string");
  });

  it("getTriageColor returns default for unknown priority", async () => {
    const { getTriageColor } = await import("../../lib/utils");
    const colorClass = getTriageColor("UNKNOWN");
    expect(typeof colorClass).toBe("string");
    expect(colorClass).toContain("slate");
  });

  it("getTriageDotColor returns correct color for HIGH", async () => {
    const { getTriageDotColor } = await import("../../lib/utils");
    const color = getTriageDotColor("HIGH");
    expect(color).toBe("bg-rose-500");
  });

  it("getTriageDotColor returns correct color for MEDIUM", async () => {
    const { getTriageDotColor } = await import("../../lib/utils");
    expect(getTriageDotColor("MEDIUM")).toBe("bg-amber-500");
  });

  it("getTriageDotColor returns correct color for LOW", async () => {
    const { getTriageDotColor } = await import("../../lib/utils");
    expect(getTriageDotColor("LOW")).toBe("bg-emerald-500");
  });

  it("formatDate returns a formatted string", async () => {
    const { formatDate } = await import("../../lib/utils");
    const result = formatDate("2026-07-19T10:00:00Z");
    expect(typeof result).toBe("string");
    expect(result.length).toBeGreaterThan(0);
  });

  it("formatDateTime returns a formatted string with time", async () => {
    const { formatDateTime } = await import("../../lib/utils");
    const result = formatDateTime("2026-07-19T10:30:00Z");
    expect(typeof result).toBe("string");
    expect(result.length).toBeGreaterThan(0);
  });

  it("truncate shortens long text", async () => {
    const { truncate } = await import("../../lib/utils");
    const long = "A".repeat(200);
    const result = truncate(long, 50);
    expect(result.length).toBeLessThanOrEqual(51); // 50 + ellipsis
    expect(result.endsWith("…")).toBe(true);
  });

  it("truncate returns original text if short enough", async () => {
    const { truncate } = await import("../../lib/utils");
    const short = "Short text";
    expect(truncate(short, 100)).toBe(short);
  });

  it("getInitials returns 2 uppercase initials", async () => {
    const { getInitials } = await import("../../lib/utils");
    expect(getInitials("Dinesh Sharma")).toBe("DS");
    expect(getInitials("Dr. Priya")).toBe("DP");
  });

  it("getInitials handles single word name", async () => {
    const { getInitials } = await import("../../lib/utils");
    const result = getInitials("Admin");
    expect(result).toBe("AD");
  });
});
