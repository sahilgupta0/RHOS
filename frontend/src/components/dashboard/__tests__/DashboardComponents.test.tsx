import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";

import RecentConsultations from "../RecentConsultations";
import PatientQueue from "../PatientQueue";
import QuickActions from "../QuickActions";

describe("Dashboard Components Rendering Tests", () => {
  const mockConsultations = [
    {
      id: "c001",
      patient_id: "p001",
      patient_name: "Dinesh Sharma",
      doctor_id: "d001",
      doctor_name: "Dr. Verma",
      chief_complaint: "Severe coughing",
      language: "en",
      status: "active" as const,
      triage_priority: "HIGH" as const,
      created_at: "2026-07-19T10:00:00Z",
      updated_at: "2026-07-19T10:00:00Z",
      conversation_history: [],
    },
  ];

  const mockQueue = [
    {
      id: "p001",
      name: "Sita Devi",
      age: 38,
      complaint: "High fever",
      priority: "HIGH",
      time: "10 mins",
    },
  ];

  it("renders RecentConsultations successfully with data", () => {
    render(
      <MemoryRouter>
        <RecentConsultations consultations={mockConsultations} />
      </MemoryRouter>
    );

    expect(screen.getByText("Recent Sessions")).toBeInTheDocument();
    expect(screen.getByText("Dinesh Sharma")).toBeInTheDocument();
    expect(screen.getByText("Severe coughing")).toBeInTheDocument();
    expect(screen.getByText("HIGH")).toBeInTheDocument();
  });

  it("renders RecentConsultations empty state", () => {
    render(
      <MemoryRouter>
        <RecentConsultations consultations={[]} />
      </MemoryRouter>
    );

    expect(screen.getByText("No recent sessions found")).toBeInTheDocument();
  });

  it("renders PatientQueue successfully with patients", () => {
    render(
      <MemoryRouter>
        <PatientQueue patients={mockQueue} />
      </MemoryRouter>
    );

    expect(screen.getByText("ASHA Priority Queue")).toBeInTheDocument();
    expect(screen.getByText("1 waiting")).toBeInTheDocument();
    expect(screen.getByText("Sita Devi")).toBeInTheDocument();
    expect(screen.getByText("High fever")).toBeInTheDocument();
  });

  it("renders PatientQueue empty state", () => {
    render(
      <MemoryRouter>
        <PatientQueue patients={[]} />
      </MemoryRouter>
    );

    expect(screen.getByText("No patients currently in the queue")).toBeInTheDocument();
  });

  it("renders QuickActions successfully", () => {
    render(
      <MemoryRouter>
        <QuickActions />
      </MemoryRouter>
    );

    expect(screen.getByText("Start Intake")).toBeInTheDocument();
    expect(screen.getByText("Register Patient")).toBeInTheDocument();
    expect(screen.getByText("Triage Alert Room")).toBeInTheDocument();
    expect(screen.getByText("Referrals Mapping")).toBeInTheDocument();
  });
});
