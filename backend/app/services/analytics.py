"""
RHOS Analytics Service.

Business logic for analytics aggregation and dashboard data.
"""

from __future__ import annotations

import logging
from typing import Any

from app.models.analytics import (AnalyticsResponse, DashboardStats,
                                  DiseaseDistribution, PatientTrend,
                                  VillageStats)
from app.repositories.analytics_repository import AnalyticsRepository

logger = logging.getLogger(__name__)


class AnalyticsService:
    """Service for analytics and dashboard data."""

    def __init__(self):
        self.repo = AnalyticsRepository()

    async def get_dashboard(self) -> DashboardStats:
        """Get dashboard summary statistics."""
        stats = await self.repo.get_dashboard_stats()
        return DashboardStats(**stats)

    async def get_analytics(self, days: int = 14) -> AnalyticsResponse:
        """Get complete analytics data."""
        dashboard_stats = await self.repo.get_dashboard_stats()
        disease_dist = await self.repo.get_disease_distribution()
        patient_trends = await self.repo.get_patient_trends(days=days)
        village_stats = await self.repo.get_village_stats()

        return AnalyticsResponse(
            dashboard_stats=DashboardStats(**dashboard_stats),
            disease_distribution=[DiseaseDistribution(**d) for d in disease_dist],
            patient_trends=[PatientTrend(**t) for t in patient_trends],
            village_stats=[VillageStats(**v) for v in village_stats],
        )
