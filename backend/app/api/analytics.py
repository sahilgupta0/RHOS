"""
RHOS Analytics Endpoints.

Dashboard stats and analytics data.
"""

from __future__ import annotations

from fastapi import APIRouter, Query

from app.dependencies import CurrentUser
from app.models.analytics import AnalyticsResponse, DashboardStats
from app.services.analytics import AnalyticsService

router = APIRouter()

analytics_service = AnalyticsService()


@router.get("/dashboard", response_model=DashboardStats)
async def get_dashboard(current_user: CurrentUser):
    """Get dashboard summary statistics."""
    return await analytics_service.get_dashboard()


@router.get("/analytics", response_model=AnalyticsResponse)
async def get_analytics(
    current_user: CurrentUser,
    days: int = Query(14, ge=1, le=90, description="Number of days for trend data"),
):
    """Get complete analytics data for charts and reports."""
    return await analytics_service.get_analytics(days=days)
