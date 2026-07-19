import { describe, it, expect, vi } from "vitest";
import { render } from "@testing-library/react";

// Mock Recharts to avoid jsdom layout dimensions / ResizeObserver issues
vi.mock("recharts", () => {
  return {
    ResponsiveContainer: ({ children }: any) => <div data-testid="responsive-container">{children}</div>,
    PieChart: ({ children }: any) => <div data-testid="pie-chart">{children}</div>,
    Pie: ({ children }: any) => <div data-testid="pie">{children}</div>,
    Cell: () => <div data-testid="cell" />,
    BarChart: ({ children }: any) => <div data-testid="bar-chart">{children}</div>,
    Bar: () => <div data-testid="bar" />,
    LineChart: ({ children }: any) => <div data-testid="line-chart">{children}</div>,
    Line: () => <div data-testid="line" />,
    XAxis: () => <div data-testid="x-axis" />,
    YAxis: () => <div data-testid="y-axis" />,
    CartesianGrid: () => <div data-testid="cartesian-grid" />,
    Tooltip: () => <div data-testid="tooltip" />,
    Legend: () => <div data-testid="legend" />,
  };
});

import DiseasePieChart from "../charts/DiseasePieChart";
import PatientTrendChart from "../charts/PatientTrendChart";
import VillageBarChart from "../charts/VillageBarChart";
import VitalsChart from "../charts/VitalsChart";

describe("Charts Component Rendering Tests", () => {
  it("renders DiseasePieChart successfully", () => {
    const mockData = [{ condition: "Fever", count: 10, percentage: 50 }];
    const { getByTestId } = render(<DiseasePieChart data={mockData} />);
    expect(getByTestId("pie-chart")).toBeInTheDocument();
  });

  it("renders PatientTrendChart successfully", () => {
    const mockData = [{ date: "2026-07-19", count: 5, high_priority: 1 }];
    const { getByTestId } = render(<PatientTrendChart data={mockData} />);
    expect(getByTestId("line-chart")).toBeInTheDocument();
  });

  it("renders VillageBarChart successfully", () => {
    const mockData = [{ village_name: "A", total_patients: 5, active_cases: 2 }];
    const { getByTestId } = render(<VillageBarChart data={mockData} />);
    expect(getByTestId("bar-chart")).toBeInTheDocument();
  });

  it("renders VitalsChart successfully", () => {
    const mockHistory = [
      {
        id: "v1",
        patient_id: "p1",
        bp_systolic: 120,
        bp_diastolic: 80,
        heart_rate: 72,
        temperature: 98.6,
        spo2: 98,
        recorded_at: "2026-07-19T10:00:00Z",
      },
    ];
    const { getByTestId } = render(<VitalsChart data={mockHistory} />);
    expect(getByTestId("line-chart")).toBeInTheDocument();
  });
});
