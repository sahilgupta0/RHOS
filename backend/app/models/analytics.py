"""
RHOS Analytics Models.

Data models for analytics aggregation and dashboard statistics.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class DashboardStats(BaseModel):
    """Dashboard summary statistics."""

    total_patients: int = 0
    patients_today: int = 0
    patients_this_week: int = 0
    high_priority_today: int = 0
    consultations_today: int = 0
    consultations_this_week: int = 0
    follow_ups_pending: int = 0
    referrals_this_month: int = 0


class DiseaseDistribution(BaseModel):
    """Disease distribution data point."""

    condition: str
    count: int
    percentage: float = 0.0


class PatientTrend(BaseModel):
    """Daily patient trend data point."""

    date: str
    count: int
    high_priority: int = 0


class VillageStats(BaseModel):
    """Village-level statistics."""

    village_id: str
    village_name: str
    total_patients: int = 0
    active_cases: int = 0
    high_priority: int = 0
    last_visit_date: str = ""


class MedicineUsage(BaseModel):
    """Medicine usage statistics."""

    medicine_name: str
    generic_name: str = ""
    times_prescribed: int = 0
    category: str = ""


class AnalyticsResponse(BaseModel):
    """Complete analytics response."""

    dashboard_stats: DashboardStats = Field(default_factory=DashboardStats)
    disease_distribution: list[DiseaseDistribution] = Field(default_factory=list)
    patient_trends: list[PatientTrend] = Field(default_factory=list)
    village_stats: list[VillageStats] = Field(default_factory=list)
    medicine_usage: list[MedicineUsage] = Field(default_factory=list)
    top_symptoms: list[dict[str, int]] = Field(default_factory=list)
