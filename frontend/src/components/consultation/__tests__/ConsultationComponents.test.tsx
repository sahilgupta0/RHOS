import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";

import AgentProgress from "../AgentProgress";
import ImageUpload from "../ImageUpload";
import PatientSummary from "../PatientSummary";

describe("Consultation-Specific Components Rendering Tests", () => {
  const mockPatient = {
    id: "p001",
    name: "Dinesh Sharma",
    age: 45,
    gender: "Male" as const,
    phone: "+91-9876543210",
    blood_group: "O+" as const,
    village_id: "v001",
    asha_worker_id: "asha-001",
    is_active: true,
    vitals: { bp_sys: 120, bp_dia: 80, pulse: 72, temperature: 98.6 },
    created_at: "2026-07-19T10:00:00Z",
    updated_at: "2026-07-19T10:00:00Z",
  };

  it("renders AgentProgress stages successfully", () => {
    const mockAgents = [
      { name: "Patient Intake", status: "completed" as const, description: "Extracting symptoms" },
      { name: "Medical History", status: "running" as const, description: "Loading history" },
      { name: "Triage Decision", status: "idle" as const },
    ];

    render(<AgentProgress agents={mockAgents} />);
    expect(screen.getByText("Patient Intake")).toBeInTheDocument();
    expect(screen.getByText("Extracting symptoms")).toBeInTheDocument();
    expect(screen.getByText("Medical History")).toBeInTheDocument();
    expect(screen.getByText("Triage Decision")).toBeInTheDocument();
  });

  it("renders ImageUpload dropzone and triggers selection", () => {
    const onUploadMock = vi.fn();
    const { container } = render(<ImageUpload onUpload={onUploadMock} />);

    expect(screen.getByText(/Clinical photo/i)).toBeInTheDocument();
    expect(screen.getByText(/drag and drop/i)).toBeInTheDocument();

    const file = new File(["dummy content"], "xray.png", { type: "image/png" });
    const input = container.querySelector('input[type="file"]') as HTMLInputElement;

    // Trigger file select change
    fireEvent.change(input, { target: { files: [file] } });
    expect(onUploadMock).toHaveBeenCalledWith(file);
  });

  it("renders PatientSummary clinical reports successfully", () => {
    render(<PatientSummary patient={mockPatient} chiefComplaint="Fever and cough" />);
    expect(screen.getByText("Dinesh Sharma")).toBeInTheDocument();
    expect(screen.getByText("Fever and cough")).toBeInTheDocument();
    expect(screen.getByText("45 yrs • Male • Blood: O+")).toBeInTheDocument();
  });
});
