import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";

// Mock AuthContext useAuth
vi.mock("../../context/AuthContext", () => {
  return {
    useAuth: () => ({
      user: { name: "Dr. Verma", role: "doctor" },
      logout: vi.fn(),
      login: vi.fn(),
      loading: false,
      isLoading: false,
      isAuthenticated: true,
    }),
  };
});

// Mock ThemeContext useTheme
vi.mock("../../context/ThemeContext", () => {
  return {
    useTheme: () => ({
      theme: "light",
      toggleTheme: vi.fn(),
    }),
  };
});

// Import components
import EmptyState from "../common/EmptyState";
import LoadingSpinner from "../common/LoadingSpinner";
import SearchBar from "../common/SearchBar";
import SafetyDisclaimer from "../common/SafetyDisclaimer";
import ProtectedRoute from "../common/ProtectedRoute";
import PageHeader from "../layout/PageHeader";
import AppLayout from "../layout/AppLayout";
import Sidebar from "../layout/Sidebar";
import Topbar from "../layout/Topbar";
import ConsultationCard from "../cards/ConsultationCard";
import PatientCard from "../cards/PatientCard";
import StatsCard from "../cards/StatsCard";
import Breadcrumb from "../navigation/Breadcrumb";
import NavItem from "../navigation/NavItem";
import AllergyBadges from "../patient/AllergyBadges";
import MedicalHistory from "../patient/MedicalHistory";
import MedicationList from "../patient/MedicationList";
import PatientHeader from "../patient/PatientHeader";
import VitalsDisplay from "../patient/VitalsDisplay";
import Timeline from "../timeline/Timeline";
import TimelineItem from "../timeline/TimelineItem";
import PatientForm from "../forms/PatientForm";
import ConsultationForm from "../forms/ConsultationForm";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: false,
    },
  },
});

const wrapper = ({ children }: { children: React.ReactNode }) => (
  <QueryClientProvider client={queryClient}>
    <MemoryRouter>{children}</MemoryRouter>
  </QueryClientProvider>
);

describe("General UI Components Rendering Tests", () => {
  const mockPatient = {
    id: "p001",
    name: "Dinesh Sharma",
    age: 45,
    gender: "Male",
    phone: "+91-9876543210",
    blood_group: "O+",
    village_id: "v001",
    asha_worker_id: "asha-001",
    is_active: true,
    vitals: {
      bp_systolic: 120,
      bp_diastolic: 80,
      heart_rate: 72,
      spo2: 98,
      temperature: 98.6,
    },
    created_at: "2026-07-19T10:00:00Z",
    updated_at: "2026-07-19T10:00:00Z",
  };

  const mockConsultation = {
    id: "c001",
    patient_id: "p001",
    patient_name: "Dinesh Sharma",
    doctor_id: "d001",
    doctor_name: "Dr. Verma",
    chief_complaint: "Fever and cough",
    language: "en",
    status: "active" as const,
    conversation_history: [],
    created_at: "2026-07-19T10:00:00Z",
    updated_at: "2026-07-19T10:00:00Z",
  };

  it("renders EmptyState successfully", () => {
    render(<EmptyState title="No Records" description="No patient found" />);
    expect(screen.getByText("No Records")).toBeInTheDocument();
    expect(screen.getByText("No patient found")).toBeInTheDocument();
  });

  it("renders LoadingSpinner successfully", () => {
    const { container } = render(<LoadingSpinner />);
    expect(container.querySelector("svg")).toBeInTheDocument();
  });

  it("renders SearchBar successfully", () => {
    render(<SearchBar onSearch={() => {}} placeholder="Search patients..." />);
    expect(screen.getByPlaceholderText("Search patients...")).toBeInTheDocument();
  });

  it("renders SafetyDisclaimer successfully", () => {
    render(<SafetyDisclaimer />);
    expect(screen.getByText(/AI-assisted/i)).toBeInTheDocument();
  });

  it("renders PageHeader successfully", () => {
    render(<PageHeader title="Patient Dashboard" description="Manage your cases" />);
    expect(screen.getByText("Patient Dashboard")).toBeInTheDocument();
    expect(screen.getByText("Manage your cases")).toBeInTheDocument();
  });

  it("renders StatsCard successfully", () => {
    render(<StatsCard label="Total Consults" value={42} trend="This week" icon={() => <span>Icon</span>} />);
    expect(screen.getByText("Total Consults")).toBeInTheDocument();
    expect(screen.getByText("42")).toBeInTheDocument();
    expect(screen.getByText("This week")).toBeInTheDocument();
  });

  it("renders PatientCard successfully", () => {
    render(<PatientCard patient={mockPatient} />, { wrapper });
    expect(screen.getByText("Dinesh Sharma")).toBeInTheDocument();
    expect(screen.getByText("45 yrs • Male")).toBeInTheDocument();
  });

  it("renders ConsultationCard successfully", () => {
    render(<ConsultationCard consultation={mockConsultation} onClick={() => {}} />, { wrapper });
    expect(screen.getByText("Dinesh Sharma")).toBeInTheDocument();
    expect(screen.getByText("Fever and cough")).toBeInTheDocument();
  });

  it("renders Breadcrumb successfully", () => {
    render(
      <Breadcrumb
        items={[
          { label: "Dashboard", path: "/" },
          { label: "Patients", path: "/patients" },
        ]}
      />,
      { wrapper }
    );
    expect(screen.getByText("Dashboard")).toBeInTheDocument();
    expect(screen.getByText("Patients")).toBeInTheDocument();
  });

  it("renders NavItem successfully", () => {
    render(
      <NavItem path="/dashboard" label="Dashboard Link" icon={() => <span>Icon</span>} />,
      { wrapper }
    );
    expect(screen.getByText("Dashboard Link")).toBeInTheDocument();
  });

  it("renders AllergyBadges successfully", () => {
    const mockAllergies = [
      { id: "a1", allergen: "Dust", severity: "moderate" as const },
      { id: "a2", allergen: "Peanuts", severity: "severe" as const },
    ];
    render(<AllergyBadges allergies={mockAllergies} />);
    expect(screen.getByText("Dust")).toBeInTheDocument();
    expect(screen.getByText("Peanuts")).toBeInTheDocument();
  });

  it("renders MedicalHistory successfully", () => {
    const mockHistory = [
      { id: "h1", condition: "Hypertension", status: "active", diagnosed_date: "1 Jan 2024" },
    ];
    render(<MedicalHistory history={mockHistory} />);
    expect(screen.getByText("Hypertension")).toBeInTheDocument();
    expect(screen.getByText(/Diagnosed:\s*1 Jan 2024/i)).toBeInTheDocument();
  });

  it("renders MedicationList successfully", () => {
    const mockMeds = [
      { id: "m1", name: "Aspirin", dosage: "75mg", frequency: "Once daily" },
    ];
    render(<MedicationList medications={mockMeds} />);
    expect(screen.getByText("Aspirin")).toBeInTheDocument();
    expect(screen.getByText(/75mg\s*•\s*Once daily/i)).toBeInTheDocument();
  });

  it("renders PatientHeader successfully", () => {
    render(<PatientHeader patient={mockPatient} />);
    expect(screen.getByText("Dinesh Sharma")).toBeInTheDocument();
    expect(screen.getByText(/Blood:\s*O\+/i)).toBeInTheDocument();
  });

  it("renders VitalsDisplay successfully", () => {
    render(<VitalsDisplay vitals={mockPatient.vitals} />);
    expect(screen.getByText("120/80")).toBeInTheDocument();
    expect(screen.getByText("mmHg")).toBeInTheDocument();
    expect(screen.getByText("72")).toBeInTheDocument();
    expect(screen.getByText("bpm")).toBeInTheDocument();
    expect(screen.getByText("98%")).toBeInTheDocument();
  });

  it("renders Timeline and TimelineItem successfully", () => {
    render(
      <Timeline>
        <TimelineItem title="Consultation Started" date="2026-07-19" description="With Dr. Verma" isLast={true} />
      </Timeline>
    );
    expect(screen.getByText("Consultation Started")).toBeInTheDocument();
    expect(screen.getByText("2026-07-19")).toBeInTheDocument();
    expect(screen.getByText("With Dr. Verma")).toBeInTheDocument();
  });

  it("renders PatientForm successfully", () => {
    const { container } = render(<PatientForm onSubmit={() => {}} onCancel={() => {}} />);
    expect(container.querySelector('input[name="name"]')).toBeInTheDocument();
    expect(container.querySelector('select[name="blood_group"]')).toBeInTheDocument();
    expect(container.querySelector('button[type="submit"]')).toBeInTheDocument();
  });

  it("renders ConsultationForm successfully", () => {
    const { container } = render(<ConsultationForm patients={[mockPatient]} onSubmit={() => {}} onCancel={() => {}} />);
    expect(container.querySelector('input[name="patient_id"]')).toBeInTheDocument();
    expect(container.querySelector('textarea[name="chief_complaint"]')).toBeInTheDocument();
    expect(container.querySelector('button[type="submit"]')).toBeInTheDocument();
  });

  it("renders Sidebar layout successfully", () => {
    render(<Sidebar />, { wrapper });
    expect(screen.getByText(/RHOS/i)).toBeInTheDocument();
  });

  it("renders Topbar layout successfully", () => {
    render(<Topbar onMenuToggle={vi.fn()} />, { wrapper });
    expect(screen.getByPlaceholderText("Search patients, records...")).toBeInTheDocument();
    expect(screen.getByText("Dr. Verma")).toBeInTheDocument();
  });

  it("renders AppLayout successfully", () => {
    render(<AppLayout />, { wrapper });
    expect(screen.getByText(/RHOS/i)).toBeInTheDocument();
    expect(screen.getByPlaceholderText("Search patients, records...")).toBeInTheDocument();
  });

  it("renders ProtectedRoute successfully", () => {
    render(
      <ProtectedRoute>
        <div>Protected Content</div>
      </ProtectedRoute>,
      { wrapper }
    );
    expect(screen.getByText("Protected Content")).toBeInTheDocument();
  });
});
